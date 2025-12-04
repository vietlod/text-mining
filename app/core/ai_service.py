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
    """
    
    def __init__(self):
        self.model = None
        self.init_error = None
        
        logger.info(f"Initializing GeminiService...")
        logger.info(f"API Key present: {bool(GEMINI_API_KEY)}")
        logger.info(f"API Key length: {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0}")
        
        if not GEMINI_API_KEY:
            self.init_error = "GEMINI_API_KEY not found"
            logger.error(self.init_error)
            return

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
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
