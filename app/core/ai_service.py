import google.generativeai as genai
import json
import re
import traceback
from app.config import GEMINI_API_KEY
from app.utils.logger import setup_logger

logger = setup_logger("AIService")


class GeminiService:
    """
    Advanced AI Service using Google Gemini.

    Supports both user-specific API keys and fallback to config API key.
    """

    def __init__(self, api_key=None):
        """
        Initialize Gemini Service.

        Args:
            api_key: Optional user-specific API key. If None, uses config API key.
        """
        self.model = None
        self.init_error = None
        self.api_key = api_key or GEMINI_API_KEY

        logger.info(f"Initializing GeminiService...")
        logger.info(f"Using user-specific API key: {bool(api_key)}")
        logger.info(f"API Key present: {bool(self.api_key)}")
        logger.info(f"API Key length: {len(self.api_key) if self.api_key else 0}")

        if not self.api_key:
            self.init_error = "GEMINI_API_KEY not found. Please configure your API key in Settings."
            logger.error(self.init_error)
            return

        try:
            genai.configure(api_key=self.api_key)
            
            # List of models to try in order of preference
            models_to_try = [
                'gemini-2.5-flash',
                'gemini-2.0-flash-exp',
                'gemini-1.5-flash',
                'gemini-1.5-flash-001',
                'gemini-1.5-flash-latest',
                'gemini-1.5-pro',
                'gemini-1.5-pro-001',
                'gemini-pro'
            ]
            
            self.model = None
            self.model_name = None
            
            logger.info("Attempting to connect to Gemini models...")
            
            for model_name in models_to_try:
                try:
                    logger.info(f"Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    # Test generation
                    response = model.generate_content("Test")
                    if response:
                        self.model = model
                        self.model_name = model_name
                        logger.info(f"✅ Successfully connected to: {model_name}")
                        break
                except Exception as e:
                    logger.warning(f"Failed to connect to {model_name}: {e}")
            
            if not self.model:
                # If all fail, list available models for debugging
                try:
                    logger.info("Listing available models...")
                    for m in genai.list_models():
                        logger.info(f"Available: {m.name} | Supported methods: {m.supported_generation_methods}")
                except Exception as e:
                    logger.error(f"Failed to list models: {e}")
                    
                raise Exception("No suitable Gemini model found. Check logs for available models.")
                
        except Exception as e:
            self.init_error = str(e)
            self.model = None
            logger.error(f"Gemini init FAILED: {e}")
            logger.error(traceback.format_exc())

    def get_status(self):
        """Return current status for debugging."""
        if self.model:
            return f"✅ Gemini OK ({self.model_name})"
        else:
            return f"❌ Error: {self.init_error}"

    def extract_text_from_image(self, image_data, mime_type='image/jpeg'):
        """Extract text from image using Gemini Vision with enhanced Vietnamese OCR."""
        logger.info(f"extract_text_from_image called, image size: {len(image_data)} bytes")
        
        if not self.model:
            logger.error(f"Model not available: {self.init_error}")
            return "", 0

        try:
            # Enhanced prompt for better Vietnamese text extraction
            prompt = """Extract ALL text from this document image.
            
            CRITICAL:
            - Preserve Vietnamese diacritics exactly (ă, â, đ, ê, ô, ơ, ư, etc.)
            - Maintain original formatting and line breaks
            - Include ALL numbers, tables, and headers
            - Return ONLY the extracted text, no explanations
            """

            logger.info("Sending image to Gemini...")
            response = self.model.generate_content([
                prompt,
                {"mime_type": mime_type, "data": image_data}
            ])
            
            text = response.text if response and response.text else ""
            tokens = 0
            
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens = getattr(response.usage_metadata, 'total_token_count', 0)
            
            logger.info(f"Gemini returned: {len(text)} chars, {tokens} tokens")
            return text, tokens
            
        except Exception as e:
            logger.error(f"extract_text_from_image FAILED: {e}")
            logger.error(traceback.format_exc())
            return "", 0

    def extract_text_from_pdf_page(self, image_data):
        """Extract text from a PDF page image."""
        return self.extract_text_from_image(image_data, mime_type='image/png')

    def extract_text_from_pdf_direct(self, pdf_path):
        """
        Extract text from PDF by uploading directly to Gemini (if supported).
        This is more efficient than converting to images.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            (text, tokens, quality_score)
            quality_score: 0-100, higher = better quality
        """
        if not self.model:
            logger.error(f"Model not available: {self.init_error}")
            return "", 0, 0
        
        try:
            import fitz
            import os
            
            # Check if file exists
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return "", 0, 0
            
            file_size = os.path.getsize(pdf_path)
            logger.info(f"Attempting direct PDF upload: {pdf_path} ({file_size:,} bytes)")
            
            # Try to upload PDF directly to Gemini
            # Note: Gemini 1.5+ supports PDF uploads
            try:
                # Check if upload_file is available
                if not hasattr(genai, 'upload_file'):
                    raise AttributeError("genai.upload_file not available in this version")
                
                # Upload file to Gemini
                uploaded_file = genai.upload_file(path=pdf_path)
                logger.info(f"PDF uploaded successfully: {uploaded_file.uri}")
                
                # Extract text with quality assessment prompt
                # CRITICAL: Request COMPLETE, EXHAUSTIVE extraction - no summarization, no omissions
                # AI models have semantic understanding and context awareness, so they should extract MORE keywords than simple text extraction
                prompt = """You are extracting text from a PDF document for keyword analysis using advanced AI capabilities. 

IMPORTANT: You have semantic understanding and context awareness that simple text extraction methods (like PyMuPDF, PyPDF2, OCR) lack. 
These simple methods only extract raw text without understanding meaning. You should:
1. Extract EVERY SINGLE WORD, EVERY NUMBER, EVERY SYMBOL from EVERY PAGE (same as simple extraction)
2. PLUS leverage your AI capabilities to capture MORE comprehensive content:
   - Synonyms and variations that simple extraction might miss
   - Contextual meanings and related terms
   - Acronyms and abbreviations in context (e.g., "NH" = "ngân hàng")
   - Technical terms and domain-specific vocabulary
   - Implicit references and related concepts

This is CRITICAL - you must extract EVERYTHING:

MANDATORY EXTRACTION RULES (NO EXCEPTIONS):
1. Extract text from ALL pages sequentially (page 1, 2, 3... to the last page)
2. Do NOT skip any pages, sections, paragraphs, sentences, or words
3. Do NOT summarize, paraphrase, or condense any content
4. Do NOT omit headers, footers, tables, captions, or any text elements
5. Extract EVERY occurrence of text, even if it appears multiple times
6. Preserve Vietnamese diacritics EXACTLY (ă, â, đ, ê, ô, ơ, ư, etc.) - do not modify
7. Maintain original line breaks and formatting structure
8. Include ALL numbers, dates, percentages, and numerical data
9. Extract text from tables cell-by-cell, row-by-row
10. Include ALL text from appendices, references, and supplementary materials

WHAT TO EXTRACT:
- Main body text (every paragraph, every sentence)
- Headers and subheaders (all levels)
- Table content (every cell, every row)
- Figure captions and image descriptions
- Footnotes and endnotes
- Page numbers and headers/footers
- Lists and bullet points (every item)
- Any text in sidebars, boxes, or callouts
- References and bibliography entries

WHAT NOT TO DO:
- DO NOT summarize paragraphs into shorter versions
- DO NOT skip "less important" sections
- DO NOT combine similar content
- DO NOT omit repetitive text
- DO NOT truncate long sections
- DO NOT interpret or rephrase content

LEVERAGE YOUR AI CAPABILITIES:
- Use semantic understanding to identify related terms and concepts
- Recognize synonyms, variations, and contextual meanings
- Understand domain-specific terminology and technical jargon
- Identify acronyms and abbreviations in context
- Capture implicit references and related concepts

Remember: Simple text extraction methods (like PyMuPDF, PyPDF2) only extract raw text. 
You have the advantage of understanding context, so you should extract MORE comprehensive content than simple extraction methods.

After extraction, assess the quality on a scale of 0-100 where:
- 90-100: Excellent quality, ALL text clearly readable, COMPLETE extraction from ALL pages
- 70-89: Good quality, most text readable with minor issues
- 50-69: Medium quality, some text unclear or missing
- 30-49: Poor quality, significant text missing or unreadable
- 0-29: Very poor quality, most text unreadable

Format your response EXACTLY as:
QUALITY_SCORE: [number]
TEXT:
[complete extracted text from all pages here - NO SUMMARIES, NO OMISSIONS]
"""
                
                logger.info("Sending PDF to Gemini for direct extraction...")
                response = self.model.generate_content([
                    prompt,
                    uploaded_file
                ])
                
                text = response.text if response and response.text else ""
                tokens = 0
                
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    tokens = getattr(response.usage_metadata, 'total_token_count', 0)
                
                # Parse quality score from response
                quality_score = 50  # Default medium quality
                if "QUALITY_SCORE:" in text:
                    try:
                        quality_line = [line for line in text.split('\n') if 'QUALITY_SCORE:' in line][0]
                        quality_score = int(re.search(r'\d+', quality_line).group())
                        # Remove quality score line from text
                        text = '\n'.join([line for line in text.split('\n') if 'QUALITY_SCORE:' not in line])
                        text = text.replace('TEXT:', '').strip()
                    except:
                        pass
                
                logger.info(f"Direct PDF extraction: {len(text)} chars, quality={quality_score}, {tokens} tokens")
                
                # Clean up uploaded file
                try:
                    genai.delete_file(uploaded_file.name)
                except:
                    pass
                
                return text, tokens, quality_score
                
            except Exception as upload_error:
                logger.warning(f"Direct PDF upload not supported or failed: {upload_error}")
                logger.info("Falling back to text extraction from PDF structure...")
                
                # Fallback: Extract text using PyMuPDF and send to Gemini for analysis
                doc = fitz.open(pdf_path)
                extracted_text = ""
                for page in doc:
                    extracted_text += page.get_text() + "\n"
                doc.close()
                
                if len(extracted_text.strip()) < 100:
                    # Very little text extracted, quality is poor
                    return extracted_text, 0, 20
                
                # Assess quality by sending extracted text to Gemini
                quality_prompt = f"""Assess the quality of this extracted PDF text on a scale of 0-100.

Text sample (first 2000 chars):
{extracted_text[:2000]}

Consider:
- Completeness: Are there missing sections?
- Readability: Is the text clear and well-formatted?
- Vietnamese content: Are diacritics preserved?

Respond with ONLY a number 0-100 representing quality score."""

                try:
                    quality_response = self.model.generate_content(quality_prompt)
                    quality_text = quality_response.text.strip()
                    quality_score = int(re.search(r'\d+', quality_text).group()) if re.search(r'\d+', quality_text) else 50
                except:
                    quality_score = 50
                
                tokens = 0
                if hasattr(quality_response, 'usage_metadata') and quality_response.usage_metadata:
                    tokens = getattr(quality_response.usage_metadata, 'total_token_count', 0)
                
                logger.info(f"Text extraction quality assessment: {quality_score}/100, {tokens} tokens")
                return extracted_text, tokens, quality_score
                
        except Exception as e:
            logger.error(f"extract_text_from_pdf_direct FAILED: {e}")
            logger.error(traceback.format_exc())
            return "", 0, 0

    def search_keywords_in_image(self, image_data, keywords: list, mime_type='image/png', semantic_threshold=85):
        """Search for keywords in a document image with semantic matching."""
        logger.info(f"search_keywords_in_image called, {len(keywords)} keywords, threshold={semantic_threshold}%, image size: {len(image_data)} bytes")
        
        if not self.model:
            logger.error(f"Model not available: {self.init_error}")
            return {}, 0
            
        if not keywords:
            logger.warning("No keywords provided")
            return {}, 0

        try:
            keywords_str = ", ".join([f'"{k}"' for k in keywords[:30]])
            
            # Enhanced prompt with configurable semantic matching threshold
            prompt = f"""You are analyzing a Vietnamese business/financial document for keywords. Count occurrences of the following keywords:

Keywords: {keywords_str}

CRITICAL MATCHING RULES:
1. **Exact Match**: Count exact keyword occurrences (ignore case, ignore Vietnamese diacritics)
2. **Semantic Match (≥{semantic_threshold}% similarity)**: Also count semantically similar phrases:
   - "phân tích dữ liệu" ≈ "phân tích số liệu", "data analytics"  
   - "quản lý rủi ro" ≈ "quản trị rủi ro", "kiểm soát rủi ro"
   - "ngân hàng" ≈ "NH", "bank", "banking"
   - "trí tuệ nhân tạo" ≈ "AI", "artificial intelligence"

3. **Context Understanding**:
   - Distinguish "Apple" (company) vs "táo" (fruit)
   - Match acronyms: "NH" = "ngân hàng", "TMĐT" = "thương mại điện tử"

4. **Vietnamese Variations**:
   - "dữ liệu" = "số liệu" = "data"
   - "chuyển đổi số" = "số hóa" = "digitalization"

RESPONSE FORMAT (CRITICAL - MUST FOLLOW EXACTLY):
- Return ONLY a raw JSON object (no ```json or ``` markdown)
- Each key is a keyword, each value is an INTEGER count
- Example: {{"phân tích dữ liệu": 3, "quản lý rủi ro": 1, "AI": 0}}
- DO NOT use nested objects like {{"keyword": {{"exact": 1, "similar": 2}}}}
- ONLY return keywords that appear in the document (count > 0)

JSON Output:"""

            logger.info("Sending keyword search to Gemini...")
            response = self.model.generate_content([
                prompt,
                {"mime_type": mime_type, "data": image_data}
            ])
            
            tokens = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens = getattr(response.usage_metadata, 'total_token_count', 0)
            
            if not response or not response.text:
                logger.warning("Empty response from Gemini")
                return {}, tokens
            
            text = response.text.strip()
            logger.info(f"Gemini keyword response: {text[:200]}")
            
            result = self._parse_json_response(text)
            # Normalize to ensure all values are integers (handles nested dicts)
            result = self._normalize_keyword_counts(result)
            logger.info(f"Parsed and normalized keywords: {len(result)} keywords, total: {sum(result.values())}")
            return result, tokens
            
        except Exception as e:
            logger.error(f"search_keywords_in_image FAILED: {e}")
            logger.error(traceback.format_exc())
            return {}, 0

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from response with multiple fallback methods."""
        # Method 1: Direct parse
        try:
            return json.loads(text)
        except:
            pass
        
        # Method 2: Extract from markdown code block
        if '```' in text:
            try:
                match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except:
                pass
        
        # Method 3: Find any JSON object
        try:
            match = re.search(r'\{[^{}]*\}', text)
            if match:
                return json.loads(match.group())
        except:
            pass
        
        logger.warning(f"Could not parse JSON: {text[:100]}")
        return {}
    
    def _normalize_keyword_counts(self, raw_result: dict) -> dict:
        """
        Normalize keyword counts to ensure all values are integers.
        Handles cases where Gemini returns nested dicts like:
        {"keyword": {"keyword": 0, "similar_term": 0}} instead of {"keyword": 0}
        """
        normalized = {}
        for key, value in raw_result.items():
            if isinstance(value, int):
                normalized[key] = value
            elif isinstance(value, float):
                normalized[key] = int(value)
            elif isinstance(value, dict):
                # Sum all integer values in nested dict
                total = 0
                for v in value.values():
                    if isinstance(v, (int, float)):
                        total += int(v)
                normalized[key] = total
                logger.debug(f"Normalized nested dict for '{key}': {value} -> {total}")
            elif isinstance(value, str):
                try:
                    normalized[key] = int(value)
                except ValueError:
                    normalized[key] = 0
            else:
                normalized[key] = 0
                logger.warning(f"Unknown type for '{key}': {type(value)}")
        return normalized

    def generate_insights(self, keyword_counts: dict, group_counts: dict, filenames: list):
        """Generate insights from keyword data."""
        logger.info(f"generate_insights called: {len(keyword_counts)} keywords")
        
        if not self.model:
            return f"❌ Gemini chưa sẵn sàng: {self.init_error}", 0

        try:
            top_kw = sorted(keyword_counts.items(), key=lambda x: -x[1])[:10] if keyword_counts else []
            kw_text = "\n".join([f"- {k}: {v}" for k, v in top_kw]) if top_kw else "Không có"
            
            prompt = f"""Phân tích ngắn gọn dữ liệu keyword:
            
Số file: {len(filenames)}
Tổng keywords: {sum(keyword_counts.values()) if keyword_counts else 0}
Top keywords:
{kw_text}

Viết 3 bullet points nhận xét bằng tiếng Việt."""

            logger.info("Generating insights...")
            response = self.model.generate_content(prompt)
            
            tokens = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens = getattr(response.usage_metadata, 'total_token_count', 0)
            
            result = response.text.strip() if response and response.text else "Không có kết quả"
            logger.info(f"Insights generated: {len(result)} chars, {tokens} tokens")
            return result, tokens
            
        except Exception as e:
            logger.error(f"generate_insights FAILED: {e}")
            return f"❌ Lỗi: {e}", 0
