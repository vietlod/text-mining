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
                
                # Incremental analysis for Bubble Chart (Local OCR)
                if progress_callback and keywords_map:
                    page_counts, _ = self.analyzer.analyze(page_text, keywords_map)
                    page_kw_sum = sum(page_counts.values())
                    total_keywords += page_kw_sum
                    
                    for k, v in page_counts.items():
                        cumulative_counts[k] = cumulative_counts.get(k, 0) + v
                    
                    # Update progress (every page or every 10 pages for speed?)
                    # For Local OCR, it's fast, so maybe every page is fine, 
                    # but for very large docs, it might slow down.
                    # Let's do every page for smooth animation.
                    progress_callback(i + 1, total_pages, 0, total_keywords, cumulative_counts)
            
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

        initial_text = "\n".join(text_parts)
        
        # Quality Check
        should_ocr = False
        use_ai = False
        reason = ""
        
        normalized = self.normalize_text(initial_text)
        text_len = len(normalized)
        
        # Check keywords
        kw_count = 0
        if keywords_map:
            kw_res, _ = self.analyzer.analyze(initial_text, keywords_map)
            kw_count = sum(kw_res.values())

        # Decision Logic
        if text_len < 100:
            should_ocr = True
            reason = "Text too short"
        elif keywords_map and kw_count == 0:
            should_ocr = True
            use_ai = True # If no keywords found even after text extraction, try AI
            reason = "No keywords found"
        elif text_len < 200000:
             words = normalized.split()
             vn_vocab = ['ngan', 'hang', 'tai', 'chinh', 'dich', 'vu']
             vn_count = sum(1 for w in words if any(v in w for v in vn_vocab))
             vn_ratio = vn_count / len(words) if words else 0
             
             if vn_ratio < 0.05:
                 should_ocr = True
                 reason = "Low Vietnamese content"
        
        # Execute OCR / AI
        if should_ocr:
            logger.info(f"Triggering Enhanced Extraction: {reason}")
            
            # Try Local OCR first
            if self.ocr_reader:
                ocr_text = self.extract_pdf_ocr(path)
                if len(self.normalize_text(ocr_text)) > 100:
                    text_parts.append(ocr_text)
                    
                    # Re-check keywords after OCR
                    if keywords_map:
                        kw_res_ocr, _ = self.analyzer.analyze(ocr_text, keywords_map)
                        if sum(kw_res_ocr.values()) > 0:
                            use_ai = False # OCR worked, no need for AI
            
            # If still no good results, use Gemini
            if use_ai and self.ai_service.model:
                logger.info("Local OCR insufficient. Engaging Gemini AI...")
                ai_text, ai_tokens = self.extract_pdf_ai(path)
                total_tokens += ai_tokens
                if ai_text:
                    text_parts.append(ai_text)

        return "\n".join(text_parts), total_tokens

    def extract_pdf_ocr(self, path):
        text = ""
        try:
            doc = fitz.open(path)
            max_pages = 10 # Limit for local OCR speed
            for i, page in enumerate(doc):
                if i >= max_pages: break
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                processed = self.preprocess_image(img_bgr)
                results = self.ocr_reader.readtext(processed, detail=0, paragraph=True)
                text += " ".join(results) + "\n"
            doc.close()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
        return text

    def extract_pdf_ai(self, path, keywords_map=None, progress_callback=None):
        """
        Extract text from PDF using Gemini Vision for each page.
        Processes ALL pages of the document - no page limit.
        """
        text = ""
        tokens = 0
        total_keywords_found = 0
        cumulative_keyword_counts = {}
        
        try:
            doc = fitz.open(path)
            total_pages = len(doc)
            logger.info(f"Extracting {total_pages} pages with AI...")
            
            for i, page in enumerate(doc):
                current_page = i + 1
                
                # Call progress callback if provided (initial call for page start)
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
                        # We count keywords in this page's text
                        # Note: This is an approximation as it doesn't handle keywords split across pages
                        # but it's good enough for real-time progress
                        page_counts, _ = self.analyzer.analyze(page_text, keywords_map)
                        total_keywords_found += sum(page_counts.values())
                        
                        # Update cumulative counts
                        for k, v in page_counts.items():
                            cumulative_keyword_counts[k] = cumulative_keyword_counts.get(k, 0) + v
                
                # Update progress with new counts
                if progress_callback:
                    progress_callback(current_page, total_pages, tokens, total_keywords_found, cumulative_keyword_counts)
                
                # Log progress every 10 pages
                if current_page % 10 == 0:
                    logger.info(f"Processed {current_page}/{total_pages} pages, {tokens} tokens used")
            
            doc.close()
            logger.info(f"AI extraction complete: {total_pages} pages, {len(text)} chars, {tokens} tokens")
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
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
