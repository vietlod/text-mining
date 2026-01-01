import os
import fitz  # PyMuPDF
import PyPDF2
import cv2
import numpy as np
import easyocr
import docx
import re
from bs4 import BeautifulSoup
from app.utils.logger import setup_logger
from app.config import OCR_ENABLED, OCR_LANGUAGES, OCR_GPU
from app.core.text_processor import get_text_processor
from app.core.analyzer import KeywordAnalyzer
from app.core.ai_service import GeminiService
from app.core.text_deduplicator import deduplicate_text_sources, analyze_and_merge_keyword_counts

logger = setup_logger("Extractor")

class TextExtractor:
    def __init__(self):
        self.ocr_reader = None
        self.processor = get_text_processor()
        self.analyzer = KeywordAnalyzer()
        self.ai_service = GeminiService()
        
        if OCR_ENABLED:
            try:
                logger.info("Initializing EasyOCR...")
                self.ocr_reader = easyocr.Reader(OCR_LANGUAGES, gpu=OCR_GPU, verbose=False)
                logger.info("EasyOCR initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")

    def normalize_text(self, text):
        return self.processor.normalize_text(text)

    def extract_from_file(self, file_path, keywords_map=None, force_ai=False, progress_callback=None):
        """
        Returns: (text, token_usage)
        """
        ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Extracting text from {file_path} ({ext}) [AI: {force_ai}]")
        
        if ext == '.pdf':
            return self.extract_pdf_aggressive(file_path, keywords_map, force_ai, progress_callback)
        elif ext == '.docx':
            return self.extract_docx(file_path), 0
        elif ext == '.txt':
            return self.extract_txt(file_path), 0
        elif ext in ['.html', '.htm']:
            return self.extract_html(file_path), 0
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return self.extract_image(file_path) # extract_image now needs to return tokens
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return "", 0

    def extract_pdf_aggressive(self, path, keywords_map, force_ai=False, progress_callback=None):
        """
        Aggressive PDF extraction pipeline.
        
        Args:
            path: Path to PDF
            keywords_map: Keywords to search for
            force_ai: If True, skip local extraction and use AI
            progress_callback: Optional callback for page progress (only used with force_ai)
        
        Returns: (text, token_usage)
        """
        text_parts = []
        total_tokens = 0
        
        # If Force AI is enabled, skip straight to Gemini
        if force_ai and self.ai_service.model:
            logger.info("Force AI enabled. Skipping local extraction.")
            # Pass keywords_map to allow real-time counting
            return self.extract_pdf_ai(path, keywords_map, progress_callback)

        # 1. PyMuPDF
        try:
            doc = fitz.open(path)
            t1 = ""
            total_pages = len(doc)
            cumulative_counts = {}
            total_keywords = 0
            
            for i, page in enumerate(doc):
                page_text = page.get_text()
                t1 += page_text + "\n"
                
                # Update progress without analyzing each page (too slow and inaccurate)
                # Analysis will be done on combined text later
                if progress_callback:
                    # Simple progress update without keyword analysis per page
                    progress_callback(i + 1, total_pages, 0, 0, {})
            
            doc.close()
            if len(self.normalize_text(t1)) > 50:
                text_parts.append(t1)
        except Exception as e:
            logger.error(f"PyMuPDF failed: {e}")

        # 2. PyPDF2
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                t2 = ""
                for page in reader.pages:
                    t2 += (page.extract_text() or "") + "\n"
                if len(self.normalize_text(t2)) > 50:
                    text_parts.append(t2)
        except Exception as e:
            logger.error(f"PyPDF2 failed: {e}")

        # Analyze keywords by taking MAX count from each source to avoid double-counting
        # Strategy: Analyze each source separately, then take MAX for each keyword
        # This ensures:
        # - No double-counting from duplicate content between sources
        # - Accurate counting by using the BEST result from any source
        # - Complete coverage (if one source finds a keyword another missed, we capture it)
        
        # Get combined text for quality check (use longest source)
        initial_text = max(text_parts, key=len) if text_parts else ""
        
        # Quality Check
        should_ocr = False
        use_ai = False
        reason = ""
        
        normalized = self.normalize_text(initial_text)
        text_len = len(normalized)
        
        # Analyze keywords by taking MAX from each source
        kw_count = 0
        cumulative_counts = {}
        if keywords_map and text_parts:
            # Use MAX strategy: analyze each source separately, take MAX for each keyword
            kw_res, group_res = analyze_and_merge_keyword_counts(self.analyzer, text_parts, keywords_map)
            kw_count = sum(kw_res.values())
            cumulative_counts = kw_res
            
            logger.info(f"Keyword analysis using MAX strategy: {kw_count} total keywords from {len(text_parts)} sources")
            
            # Update progress with final keyword counts if callback provided
            if progress_callback:
                # Estimate total pages (from PyMuPDF extraction)
                try:
                    doc = fitz.open(path)
                    total_pages = len(doc)
                    doc.close()
                    progress_callback(total_pages, total_pages, 0, kw_count, cumulative_counts)
                except:
                    pass

        # Decision Logic
        # Priority: keyword count > text length > Vietnamese ratio
        if text_len < 100:
            should_ocr = True
            reason = "Text too short"
        elif keywords_map and kw_count == 0:
            should_ocr = True
            use_ai = True # If no keywords found even after text extraction, try AI
            reason = "No keywords found"
        elif text_len < 200000 and text_len > 100:
             # Only check Vietnamese ratio for medium-length text
             # For very long text, rely on keyword count instead
             words = normalized.split()
             if words:
                 vn_vocab = ['ngan', 'hang', 'tai', 'chinh', 'dich', 'vu']
                 vn_count = sum(1 for w in words if any(v in w for v in vn_vocab))
                 vn_ratio = vn_count / len(words) if words else 0
                 
                 if vn_ratio < 0.05:
                     should_ocr = True
                     reason = "Low Vietnamese content"
        # For very long text (>200K), trust the extraction methods
        # Don't trigger OCR based on Vietnamese ratio (may be inaccurate)
        
        # Execute OCR / AI
        if should_ocr:
            logger.info(f"Triggering Enhanced Extraction: {reason}")
            
            # Try Local OCR first
            if self.ocr_reader:
                ocr_text = self.extract_pdf_ocr(path)
                if len(self.normalize_text(ocr_text)) > 100:
                    # Add OCR text to parts (preserve all sources)
                    text_parts.append(ocr_text)
                    
                    # Re-check keywords after OCR using MAX strategy
                    if keywords_map:
                        # Use MAX strategy: analyze each source separately, take MAX for each keyword
                        kw_res_ocr, _ = analyze_and_merge_keyword_counts(self.analyzer, text_parts, keywords_map)
                        if sum(kw_res_ocr.values()) > 0:
                            use_ai = False # OCR worked, no need for AI
                            logger.info(f"After OCR: {sum(kw_res_ocr.values())} keywords found using MAX strategy")
            
            # If still no good results, use Gemini
            if use_ai and self.ai_service.model:
                logger.info("Local OCR insufficient. Engaging Gemini AI...")
                ai_text, ai_tokens = self.extract_pdf_ai(path)
                total_tokens += ai_tokens
                if ai_text:
                    text_parts.append(ai_text)

        # Final text combination
        # Note: Keyword counts are already calculated using MAX strategy above
        # For the returned text, we use the longest source as it's likely most complete
        # The MAX strategy ensures keywords are counted correctly even if text has duplicates
        if len(text_parts) > 1:
            # Use longest text as base (most complete) for further processing
            # Keyword counts are already accurate from MAX strategy
            final_text = max(text_parts, key=len)
            
            # Add any unique content from other sources that might have keywords not in longest
            for other_text in text_parts:
                if other_text != final_text and len(other_text.strip()) > 50:
                    # Only add if significantly different
                    if len(other_text) > len(final_text) * 0.1:  # At least 10% of main text
                        # Check if this source has unique content
                        # For simplicity, append to ensure all keywords can be found if needed later
                        pass  # MAX strategy already handles keyword counting correctly
            
            logger.info(f"Final text: {len(final_text):,} chars (longest of {len(text_parts)} sources)")
        else:
            final_text = text_parts[0] if text_parts else ""
            logger.info(f"Final text: {len(final_text):,} chars (single source)")
        
        return final_text, total_tokens

    def _merge_text_sources(self, text_parts):
        """
        Intelligently merge text from multiple sources, avoiding duplicates and optimizing for keyword extraction.
        
        Strategy:
        1. If only one source, return it
        2. If multiple sources, prioritize by quality and merge intelligently
        3. Remove obvious duplicates while preserving unique content
        
        Args:
            text_parts: List of text strings from different extraction methods
            
        Returns:
            Merged text string optimized for keyword extraction
        """
        if not text_parts:
            return ""
        
        if len(text_parts) == 1:
            return text_parts[0]
        
        # Filter out empty or very short texts
        valid_parts = [t for t in text_parts if t and len(self.normalize_text(t)) > 50]
        
        if not valid_parts:
            return ""
        
        if len(valid_parts) == 1:
            return valid_parts[0]
        
        # Strategy: Use the longest text as base, then supplement with unique content from others
        # This avoids duplicate keywords while maximizing coverage
        valid_parts.sort(key=lambda x: len(self.normalize_text(x)), reverse=True)
        base_text = valid_parts[0]
        base_normalized = self.normalize_text(base_text)
        
        # For additional sources, only add content that's significantly different
        # (to avoid duplicate keywords from same content extracted differently)
        merged_text = base_text
        merged_normalized = base_normalized
        
        for additional_text in valid_parts[1:]:
            additional_normalized = self.normalize_text(additional_text)
            
            # Calculate overlap ratio
            base_words = set(base_normalized.split())
            additional_words = set(additional_normalized.split())
            
            if len(base_words) == 0:
                # Base is empty, use additional
                merged_text = additional_text
                merged_normalized = additional_normalized
                base_normalized = additional_normalized
                base_words = additional_words
                continue
            
            overlap = len(base_words & additional_words)
            overlap_ratio = overlap / len(additional_words) if additional_words else 0
            
            # Only merge if overlap is less than 80% (significant new content)
            if overlap_ratio < 0.8:
                # Add unique content from additional source
                unique_words = additional_words - base_words
                if len(unique_words) > len(additional_words) * 0.2:  # At least 20% unique
                    # Append additional text (it has significant unique content)
                    merged_text += "\n" + additional_text
                    merged_normalized = self.normalize_text(merged_text)
                    base_normalized = merged_normalized
                    base_words = set(merged_normalized.split())
        
        logger.info(f"Merged {len(text_parts)} text sources: {len(base_text):,} -> {len(merged_text):,} chars")
        return merged_text

    def extract_pdf_ocr(self, path, max_pages=None):
        """
        Extract text from PDF using Local OCR (EasyOCR).
        
        Optimized to ensure all pages are processed correctly and text quality is maintained.
        Uses incremental text building to avoid memory issues with very long documents.
        
        Args:
            path: Path to PDF file
            max_pages: Maximum pages to process. If None, processes all pages.
                      Default None to ensure all keywords are extracted.
        
        Returns:
            Extracted text string
        """
        text = ""  # Build text incrementally to avoid memory issues
        pages_processed = 0
        pages_failed = 0
        pages_with_text = 0
        
        try:
            doc = fitz.open(path)
            total_pages = len(doc)
            
            # Process all pages by default to avoid missing keywords
            # Only limit if explicitly set (for very large documents)
            pages_to_process = min(max_pages, total_pages) if max_pages else total_pages
            
            logger.info(f"OCR processing {pages_to_process}/{total_pages} pages from {path}")
            
            for i, page in enumerate(doc):
                if max_pages and i >= max_pages:
                    break
                    
                try:
                    # Render page with good quality (2x for better OCR accuracy)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    
                    # Preprocess for better OCR quality
                    processed = self.preprocess_image(img_bgr)
                    
                    # OCR with paragraph mode for better text structure
                    results = self.ocr_reader.readtext(processed, detail=0, paragraph=True)
                    page_text = " ".join(results).strip()
                    
                    if page_text and len(page_text) > 10:  # Only add if meaningful text
                        # Append page text immediately to avoid memory buildup
                        text += page_text + "\n"
                        pages_with_text += 1
                    
                    pages_processed += 1
                    
                    # Log progress every 10 pages
                    if (i + 1) % 10 == 0:
                        logger.info(f"OCR processed {i + 1}/{pages_to_process} pages ({pages_with_text} with text, {pages_failed} failed, {len(text):,} chars)")
                        
                except Exception as e:
                    pages_failed += 1
                    logger.warning(f"OCR failed for page {i + 1}: {e}")
                    # Continue processing other pages - don't give up
                    continue
                    
            doc.close()
            
            logger.info(f"OCR complete: {len(text):,} chars extracted from {pages_processed} pages ({pages_with_text} with text, {pages_failed} failed)")
            
            if pages_failed > 0:
                logger.warning(f"⚠️ {pages_failed} pages failed OCR - may affect keyword extraction")
            
            if pages_with_text == 0:
                logger.warning(f"⚠️ No text extracted from any page - OCR may have failed completely")
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return text

    def extract_pdf_ai(self, path, keywords_map=None, progress_callback=None):
        """
        Extract text from PDF using Gemini AI with smart optimization.
        
        Strategy:
        1. First, try to read PDF directly (if supported by Gemini)
        2. Assess quality of extracted text
        3. Only use Vision API (page-by-page image processing) if quality is poor (< 50)
        
        This optimizes token usage and processing speed.
        """
        text = ""
        tokens = 0
        total_keywords_found = 0
        cumulative_keyword_counts = {}
        
        try:
            doc = fitz.open(path)
            total_pages = len(doc)
            doc.close()
            
            logger.info(f"Extracting {total_pages} pages with AI (optimized mode)...")
            
            # Step 1: Try direct PDF reading first
            if progress_callback:
                progress_callback(0, total_pages, 0, 0, {})
            
            logger.info("Attempting direct PDF extraction (optimized)...")
            direct_text, direct_tokens, quality_score = self.ai_service.extract_text_from_pdf_direct(path)
            tokens += direct_tokens
            
            # Step 2: Assess quality and completeness
            quality_threshold = 50  # Use Vision API if quality < 50
            
            # Check if direct extraction got sufficient text
            # Estimate: PDF should have at least 1000 chars per page on average
            # If direct extraction is much shorter, it may be incomplete
            estimated_min_length = total_pages * 1000
            is_complete = len(direct_text) >= estimated_min_length * 0.5  # At least 50% of estimated
            
            # Also check if we got reasonable keyword count (if keywords_map provided)
            # If direct extraction has very few keywords compared to expected, it's likely incomplete
            has_sufficient_keywords = True
            baseline_keyword_count = None
            
            if keywords_map and direct_text:
                kw_counts_check, _ = self.analyzer.analyze(direct_text, keywords_map)
                kw_count_check = sum(kw_counts_check.values())
                
                # Get baseline from local extraction for comparison
                # This helps detect if AI extraction is missing content
                try:
                    # Quick local extraction to get baseline
                    doc_baseline = fitz.open(path)
                    baseline_text = ""
                    for page in doc_baseline:
                        baseline_text += page.get_text() + "\n"
                    doc_baseline.close()
                    
                    if baseline_text:
                        baseline_kw, _ = self.analyzer.analyze(baseline_text, keywords_map)
                        baseline_keyword_count = sum(baseline_kw.values())
                        
                        # AI models with semantic understanding should extract AT LEAST as many keywords as Local OCR
                        # Local OCR uses simple text extraction, while AI can understand context, synonyms, and variations
                        # If AI has fewer keywords than baseline, it's likely incomplete or not leveraging its full capabilities
                        # Target: AI should have ≥ 100% of baseline keywords (ideally more due to semantic understanding)
                        if baseline_keyword_count > 0:
                            keyword_ratio = kw_count_check / baseline_keyword_count
                            if keyword_ratio < 1.0:  # AI should have at least 100% of baseline
                                has_sufficient_keywords = False
                                logger.warning(f"Direct extraction has {kw_count_check} keywords vs baseline {baseline_keyword_count} ({keyword_ratio:.1%}) - AI should extract ≥100% due to semantic understanding. Falling back to Vision API...")
                            elif keyword_ratio >= 1.0:
                                logger.info(f"✅ Direct extraction has {kw_count_check} keywords vs baseline {baseline_keyword_count} ({keyword_ratio:.1%}) - AI leveraging semantic understanding effectively")
                except Exception as e:
                    logger.debug(f"Could not get baseline for comparison: {e}")
                
                # Fallback: If we have many pages but very few keywords, likely incomplete
                if has_sufficient_keywords and total_pages > 10 and kw_count_check < 5:
                    has_sufficient_keywords = False
                    logger.warning(f"Direct extraction has only {kw_count_check} keywords for {total_pages} pages - likely incomplete")
            
            if quality_score >= quality_threshold and len(direct_text) > 100 and is_complete and has_sufficient_keywords:
                # Good quality and complete, use direct extraction
                logger.info(f"✅ Direct extraction successful: quality={quality_score}/100, {len(direct_text):,} chars (estimated min: {estimated_min_length:,})")
                text = direct_text
                
                # Count keywords
                if keywords_map:
                    kw_counts, _ = self.analyzer.analyze(text, keywords_map)
                    total_keywords_found = sum(kw_counts.values())
                    cumulative_keyword_counts = kw_counts
                    
                    if progress_callback:
                        progress_callback(total_pages, total_pages, tokens, total_keywords_found, cumulative_keyword_counts)
                
                logger.info(f"AI extraction complete (direct): {len(text)} chars, {tokens} tokens, {total_keywords_found} keywords")
                return text, tokens
            else:
                # Quality insufficient OR text incomplete OR insufficient keywords - use Vision API
                if not is_complete:
                    logger.warning(f"⚠️ Direct extraction incomplete ({len(direct_text):,} chars, expected ~{estimated_min_length:,}). Using Vision API for complete extraction...")
                elif not has_sufficient_keywords:
                    logger.warning(f"⚠️ Direct extraction has insufficient keywords. Using Vision API for complete extraction...")
                else:
                    logger.info(f"⚠️ Direct extraction quality insufficient ({quality_score}/100). Using Vision API...")
                
                # Don't use incomplete direct text - start fresh with Vision API
                # This ensures we get complete extraction from all pages
                text = ""
                cumulative_keyword_counts = {}
                total_keywords_found = 0
                
                # Update progress to show we're starting Vision API
                if progress_callback:
                    progress_callback(0, total_pages, tokens, 0, {})
            
            # Step 3: Process ALL pages with Vision API for complete extraction
            # This ensures we get all text and keywords, even if direct extraction failed
            logger.info(f"Starting Vision API processing for {total_pages} pages...")
            doc = fitz.open(path)
            
            for i, page in enumerate(doc):
                current_page = i + 1
                
                # Call progress callback BEFORE processing page (to show we're starting)
                if progress_callback:
                    progress_callback(current_page, total_pages, tokens, total_keywords_found, cumulative_keyword_counts)
                
                pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                img_bytes = pix.tobytes("png")
                
                page_text, page_tokens = self.ai_service.extract_text_from_pdf_page(img_bytes)
                tokens += page_tokens
                if page_text:
                    text += page_text + "\n"
                    
                    # Real-time keyword counting for this page
                    if keywords_map:
                        page_counts, _ = self.analyzer.analyze(page_text, keywords_map)
                        page_kw_sum = sum(page_counts.values())
                        total_keywords_found += page_kw_sum
                        
                        # Update cumulative counts
                        for k, v in page_counts.items():
                            cumulative_keyword_counts[k] = cumulative_keyword_counts.get(k, 0) + v
                
                # Update progress with new counts AFTER processing page
                if progress_callback:
                    progress_callback(current_page, total_pages, tokens, total_keywords_found, cumulative_keyword_counts)
                
                # Log progress every 5 pages for better visibility
                if current_page % 5 == 0:
                    logger.info(f"Vision API: {current_page}/{total_pages} pages, {tokens:,} tokens, {total_keywords_found} keywords, {len(text):,} chars")
                
                # Log progress every 10 pages
                if current_page % 10 == 0:
                    logger.info(f"Vision API: {current_page}/{total_pages} pages, {tokens} tokens, {total_keywords_found} keywords")
            
            doc.close()
            logger.info(f"AI extraction complete (Vision API): {total_pages} pages, {len(text)} chars, {tokens} tokens, {total_keywords_found} keywords")
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
        return text, tokens

    def preprocess_image(self, img):
        # Advanced preprocessing from fin_v3.txt
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        return enhanced

    def extract_docx(self, path):
        try:
            doc = docx.Document(path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""

    def extract_txt(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"TXT extraction failed: {e}")
            return ""

    def extract_html(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"HTML extraction failed: {e}")
            return ""

    def extract_image(self, path):
        text = ""
        tokens = 0
        
        # Try Local OCR first
        if self.ocr_reader:
            try:
                img = cv2.imread(path)
                processed = self.preprocess_image(img)
                results = self.ocr_reader.readtext(processed, detail=0, paragraph=True)
                text = " ".join(results)
            except Exception as e:
                logger.error(f"Image extraction failed: {e}")
        
        # If local OCR fails or returns empty, try AI
        if not text and self.ai_service.model:
             try:
                 with open(path, "rb") as f:
                     img_data = f.read()
                 text, tokens = self.ai_service.extract_text_from_image(img_data)
             except Exception as e:
                 logger.error(f"AI Image extraction failed: {e}")
                 
        return text, tokens
