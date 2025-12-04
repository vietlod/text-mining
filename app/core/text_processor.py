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
        
        normalized_text = self.normalize_text(text)
        keyword_counts = {}
        group_counts = {}
        
        logger.info(f"Analyzing {len(text)} chars of text against {len(keywords_map)} keywords")
        logger.info(f"Normalized text length: {len(normalized_text)}")
        logger.info(f"Normalized text sample: {normalized_text[:100]}...")
        
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
        if len(keyword_counts) == 0:
            logger.warning("NO KEYWORDS MATCHED! Checking first 5 keywords...")
            sample_kws = list(keywords_map.keys())[:5]
            for kw in sample_kws:
                norm_kw = self.normalize_keyword(kw)
                logger.warning(f"  Test keyword: '{kw}' -> normalized: '{norm_kw}'")
                if norm_kw in normalized_text:
                    logger.warning(f"    ✓ Found in text (simple search)!")
                else:
                    logger.warning(f"    ✗ Not found even with simple search")
        
        return keyword_counts, group_counts


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
