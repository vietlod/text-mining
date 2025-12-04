import re
from collections import defaultdict
from app.utils.logger import setup_logger
from app.core.text_processor import get_text_processor

logger = setup_logger("Analyzer")


class KeywordAnalyzer:
    """
    Keyword analyzer using optimized VietnameseTextProcessor.
    """
    
    def __init__(self):
        self.processor = get_text_processor()

    def normalize_text(self, text: str) -> str:
        """Delegate to text processor for consistent normalization."""
        return self.processor.normalize_text(text)

    def create_flexible_regex(self, keyword: str) -> re.Pattern:
        """Delegate to text processor for regex creation."""
        return self.processor.create_flexible_regex(keyword)

    def analyze(self, text: str, keywords_map: dict) -> tuple:
        """
        Analyze text against a map of keywords.
        
        Args:
            text: Raw text to analyze
            keywords_map: {keyword: group_id}
            
        Returns:
            keyword_counts: {keyword: count}
            group_counts: {group_id: count}
        """
        return self.processor.analyze_text(text, keywords_map)
