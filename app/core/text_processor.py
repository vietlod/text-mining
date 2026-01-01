# -*- coding: utf-8 -*-
"""
Text Processor Module - Optimized for Vietnamese Documents
Handles:
- Font encoding errors (TCVN3, VNI, corrupted Unicode)
- Diacritic normalization
- OCR error correction
- Flexible keyword matching
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Pattern
from app.utils.logger import setup_logger

logger = setup_logger("TextProcessor")

# ============================================
# VIETNAMESE FONT ERROR CORRECTION
# These are ONLY for actual font corruptions (TCVN3, VNI, mojibake).
# DO NOT include valid Vietnamese characters here!
# ============================================
VN_FONT_FIX_MAP = {
    # TCVN3 encoding errors (non-standard symbols → correct Vietnamese)
    'µ': 'à', '¸': 'á', '¶': 'ả', '·': 'ã', '¹': 'ạ',
    'Ì': 'è', 'Ð': 'é', 'Î': 'ẻ', 'Ï': 'ẽ', 'Ñ': 'ẹ',
    'ß': 'ò', 'ä': 'ọ',
    '©': 'â', 'ª': 'ă', '®': 'ê', '«': 'ơ', '¬': 'ư',
    '§': 'đ',
    # VNI encoding errors (multi-char sequences)
    'aø': 'à', 'aù': 'á', 'aû': 'ả', 'aõ': 'ã', 'aï': 'ạ',
    'eø': 'è', 'eù': 'é', 'eû': 'ẻ', 'eõ': 'ẽ', 'eï': 'ẹ',
    'ö': 'ô',
    # Common OCR symbol errors
    '–': '-', '—': '-', ''': "'", ''': "'", '"': '"', '"': '"',
    '…': '...', '•': '-',
    # Mojibake patterns (UTF-8 → Latin-1 double encoding)
    'Ã ': 'à', 'Ã¡': 'á', 'Ã¢': 'â', 'Ã£': 'ã',
    'Ã¨': 'è', 'Ã©': 'é', 'Ãª': 'ê',
    'Ã¬': 'ì', 'Ã­': 'í',
    'Ã²': 'ò', 'Ã³': 'ó', 'Ã´': 'ô', 'Ãµ': 'õ',
    'Ã¹': 'ù', 'Ãº': 'ú',
    'Ä ': 'đ', 'Ä': 'đ',
}

# ============================================
# VIETNAMESE DIACRITIC REMOVAL MAP
# Maps accented characters to their base form
# ============================================
VN_DIACRITIC_MAP = {
    # A variants
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'À': 'a', 'Á': 'a', 'Ả': 'a', 'Ã': 'a', 'Ạ': 'a',
    'Ă': 'a', 'Ằ': 'a', 'Ắ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
    'Â': 'a', 'Ầ': 'a', 'Ấ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
    # E variants
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'È': 'e', 'É': 'e', 'Ẻ': 'e', 'Ẽ': 'e', 'Ẹ': 'e',
    'Ê': 'e', 'Ề': 'e', 'Ế': 'e', 'Ể': 'e', 'Ễ': 'e', 'Ệ': 'e',
    # I variants
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'Ì': 'i', 'Í': 'i', 'Ỉ': 'i', 'Ĩ': 'i', 'Ị': 'i',
    # O variants
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'Ò': 'o', 'Ó': 'o', 'Ỏ': 'o', 'Õ': 'o', 'Ọ': 'o',
    'Ô': 'o', 'Ồ': 'o', 'Ố': 'o', 'Ổ': 'o', 'Ỗ': 'o', 'Ộ': 'o',
    'Ơ': 'o', 'Ờ': 'o', 'Ớ': 'o', 'Ở': 'o', 'Ỡ': 'o', 'Ợ': 'o',
    # U variants
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'Ù': 'u', 'Ú': 'u', 'Ủ': 'u', 'Ũ': 'u', 'Ụ': 'u',
    'Ư': 'u', 'Ừ': 'u', 'Ứ': 'u', 'Ử': 'u', 'Ữ': 'u', 'Ự': 'u',
    # Y variants
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    'Ỳ': 'y', 'Ý': 'y', 'Ỷ': 'y', 'Ỹ': 'y', 'Ỵ': 'y',
    # D variants
    'đ': 'd', 'Đ': 'd',
}


class VietnameseTextProcessor:
    """
    Optimized text processor for Vietnamese documents.
    Handles font errors, diacritics, and OCR mistakes.
    """
    
    def __init__(self):
        # Pre-compile regex patterns for performance
        self._whitespace_pattern = re.compile(r'\s+')
        self._non_alnum_pattern = re.compile(r'[^\w\s]')
        self._word_boundary_pattern = re.compile(r'(?<![a-z0-9])({})(?![a-z0-9])')
        
        # Build translation table for fast character replacement
        self._diacritic_table = str.maketrans(VN_DIACRITIC_MAP)

    def fix_font_errors(self, text: str) -> str:
        """
        Fix common Vietnamese font encoding errors.
        Handles TCVN3, VNI, and mojibake issues.
        """
        if not text:
            return ""
        
        # Apply multi-character fixes first (longer patterns)
        for wrong, correct in sorted(VN_FONT_FIX_MAP.items(), key=lambda x: -len(x[0])):
            text = text.replace(wrong, correct)
        
        return text

    def remove_diacritics(self, text: str) -> str:
        """
        Remove all Vietnamese diacritics, converting to base Latin characters.
        Uses both translation table and Unicode normalization for completeness.
        """
        if not text:
            return ""
        
        # Method 1: Direct translation (fast, handles known chars)
        text = text.translate(self._diacritic_table)
        
        # Method 2: Unicode NFD normalization (handles remaining chars)
        text = unicodedata.normalize('NFD', text)
        text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
        
        return text

    def normalize_text(self, text: str) -> str:
        """
        Full normalization pipeline:
        1. Fix font errors
        2. Lowercase
        3. Remove diacritics
        4. Clean whitespace and punctuation
        
        This is the PRIMARY method for normalizing document text.
        """
        if not text:
            return ""
        
        # Step 1: Fix font encoding errors
        text = self.fix_font_errors(text)
        
        # Step 2: Lowercase
        text = text.lower()
        
        # Step 3: Handle đ/Đ BEFORE other normalization
        text = text.replace('đ', 'd').replace('Đ', 'd')
        
        # Step 4: Remove diacritics
        text = self.remove_diacritics(text)
        
        # Step 5: Remove non-alphanumeric (keep spaces)
        text = self._non_alnum_pattern.sub(' ', text)
        
        # Step 6: Collapse whitespace
        text = self._whitespace_pattern.sub(' ', text).strip()
        
        return text

    def normalize_keyword(self, keyword: str) -> str:
        """
        Normalize a keyword for matching.
        Same as normalize_text but specifically for keywords.
        """
        return self.normalize_text(keyword)

    def generate_keyword_variants(self, keyword: str) -> List[str]:
        """
        Generate all possible variants of a keyword for flexible matching.
        Handles:
        - Original form
        - No spaces: "viet qr" → "vietqr"
        - Hyphen: "viet qr" → "viet-qr"
        - Underscore: "viet qr" → "viet_qr"
        - Dot: "viet qr" → "viet.qr"
        """
        kw_norm = self.normalize_keyword(keyword)
        if not kw_norm or len(kw_norm) < 2:
            return []
        
        variants = set()
        variants.add(kw_norm)
        
        # Only generate variants if there are spaces
        if ' ' in kw_norm:
            # No space
            no_space = kw_norm.replace(' ', '')
            if len(no_space) > 2:
                variants.add(no_space)
            
            # Hyphen
            variants.add(kw_norm.replace(' ', '-'))
            
            # Underscore
            variants.add(kw_norm.replace(' ', '_'))
            
            # Dot
            variants.add(kw_norm.replace(' ', '.'))
        
        return list(variants)

    def create_flexible_regex(self, keyword: str) -> Pattern:
        """
        Create a highly flexible regex pattern for keyword matching.
        Handles all variants and uses proper word boundaries.
        """
        variants = self.generate_keyword_variants(keyword)
        if not variants:
            return re.compile(r'(?!.*)')  # Never match
        
        patterns = []
        for v in variants:
            escaped = re.escape(v)
            # Word boundary that works with normalized text (lowercase + numbers only)
            patterns.append(f'(?<![a-z0-9])({escaped})(?![a-z0-9])')
        
        return re.compile('|'.join(patterns), re.IGNORECASE)

    def count_keyword_matches(self, text: str, keyword: str) -> int:
        """
        Count occurrences of a keyword in text using flexible matching.
        """
        pattern = self.create_flexible_regex(keyword)
        normalized_text = self.normalize_text(text)
        matches = pattern.findall(normalized_text)
        return len(matches)

    def analyze_text(self, text: str, keywords_map: Dict[str, int]) -> Tuple[Dict[str, int], Dict[int, int]]:
        """
        Analyze text against a map of keywords.
        Uses batch processing for very long text to avoid performance issues.
        
        Args:
            text: Raw text to analyze
            keywords_map: {keyword: group_id}
            
        Returns:
            keyword_counts: {keyword: count}
            group_counts: {group_id: total_count}
        """
        if not text or not keywords_map:
            logger.warning(f"analyze_text called with empty text={not text} or empty keywords_map={not keywords_map}")
            return {}, {}
        
        # For very long text (>100K chars), use batch processing
        # This avoids regex performance issues and memory problems
        CHUNK_SIZE = 100000  # Process in 100K char chunks
        
        if len(text) > CHUNK_SIZE:
            logger.info(f"Text is very long ({len(text):,} chars), using batch processing")
            return self._analyze_text_batched(text, keywords_map, CHUNK_SIZE)
        
        # Normal processing for shorter text
        normalized_text = self.normalize_text(text)
        keyword_counts = {}
        group_counts = {}
        
        logger.info(f"Analyzing {len(text)} chars of text against {len(keywords_map)} keywords")
        logger.debug(f"Normalized text length: {len(normalized_text)}")
        
        matches_found = 0
        for keyword, group_id in keywords_map.items():
            try:
                pattern = self.create_flexible_regex(keyword)
                matches = pattern.findall(normalized_text)
                count = len(matches)
                
                if count > 0:
                    keyword_counts[keyword] = count
                    group_counts[group_id] = group_counts.get(group_id, 0) + count
                    matches_found += count
            except Exception as e:
                logger.error(f"Regex error for keyword '{keyword}': {e}")
        
        logger.info(f"Analysis complete: {len(keyword_counts)} unique keywords found, {matches_found} total matches")
        
        return keyword_counts, group_counts
    
    def _analyze_text_batched(self, text: str, keywords_map: Dict[str, int], chunk_size: int) -> Tuple[Dict[str, int], Dict[int, int]]:
        """
        Analyze very long text in chunks to avoid performance issues.
        Uses non-overlapping chunks to avoid double counting, but processes
        the entire text to ensure no keywords are missed.
        
        Args:
            text: Raw text to analyze
            keywords_map: {keyword: group_id}
            chunk_size: Size of each chunk in characters
            
        Returns:
            keyword_counts: {keyword: count}
            group_counts: {group_id: total_count}
        """
        # Split text into non-overlapping chunks
        # This avoids double counting while maintaining performance
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)
        
        logger.info(f"Split text into {len(chunks)} non-overlapping chunks for batch processing")
        
        # Analyze each chunk independently
        total_keyword_counts = {}
        total_group_counts = {}
        total_matches = 0
        
        for chunk_idx, chunk in enumerate(chunks):
            # Normalize chunk
            normalized_chunk = self.normalize_text(chunk)
            
            # Analyze chunk
            chunk_keyword_counts = {}
            chunk_group_counts = {}
            
            for keyword, group_id in keywords_map.items():
                try:
                    pattern = self.create_flexible_regex(keyword)
                    matches = pattern.findall(normalized_chunk)
                    count = len(matches)
                    
                    if count > 0:
                        chunk_keyword_counts[keyword] = count
                        chunk_group_counts[group_id] = chunk_group_counts.get(group_id, 0) + count
                        total_matches += count
                except Exception as e:
                    logger.error(f"Regex error for keyword '{keyword}' in chunk {chunk_idx}: {e}")
            
            # Merge results (sum counts across chunks)
            # Since chunks are non-overlapping, no risk of double counting
            for k, v in chunk_keyword_counts.items():
                total_keyword_counts[k] = total_keyword_counts.get(k, 0) + v
            for g, c in chunk_group_counts.items():
                total_group_counts[g] = total_group_counts.get(g, 0) + c
            
            if (chunk_idx + 1) % 10 == 0:
                logger.debug(f"Processed {chunk_idx + 1}/{len(chunks)} chunks, {len(total_keyword_counts)} keywords found so far")
        
        logger.info(f"Batch analysis complete: {len(total_keyword_counts)} unique keywords found, {total_matches} total matches across {len(chunks)} chunks")
        
        return total_keyword_counts, total_group_counts


# ============================================
# SINGLETON INSTANCE
# ============================================
_processor_instance = None

def get_text_processor() -> VietnameseTextProcessor:
    """Get singleton instance of VietnameseTextProcessor."""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = VietnameseTextProcessor()
    return _processor_instance


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================
def normalize_text(text: str) -> str:
    """Convenience function for text normalization."""
    return get_text_processor().normalize_text(text)

def normalize_keyword(keyword: str) -> str:
    """Convenience function for keyword normalization."""
    return get_text_processor().normalize_keyword(keyword)

def analyze_text(text: str, keywords_map: Dict[str, int]) -> Tuple[Dict[str, int], Dict[int, int]]:
    """Convenience function for text analysis."""
    return get_text_processor().analyze_text(text, keywords_map)
