# -*- coding: utf-8 -*-
"""
Text Deduplicator and Keyword Merger Module
Handles:
1. Deduplication of text from multiple extraction sources to avoid double-counting keywords
2. Merging keyword counts by taking MAX from each source (not SUM) to ensure accuracy
"""

import re
from typing import List, Tuple, Dict
from app.utils.logger import setup_logger
from app.core.text_processor import get_text_processor

logger = setup_logger("TextDeduplicator")


def analyze_and_merge_keyword_counts(analyzer, text_parts: List[str], keywords_map: Dict[str, int]) -> Tuple[Dict[str, int], Dict[int, int]]:
    """
    Analyze keywords in each text source SEPARATELY, then merge by taking MAX for each keyword.
    
    This ensures:
    - No double-counting: We take MAX, not SUM, so duplicate content doesn't inflate counts
    - Accurate counting: We use the BEST result from any source
    - Complete coverage: If one source finds a keyword another missed, we still capture it
    
    Example:
    - PyMuPDF found: {"quản lý rủi ro": 5, "ngân hàng": 10}
    - PyPDF2 found: {"quản lý rủi ro": 6, "ngân hàng": 8}
    - EasyOCR found: {"quản lý rủi ro": 4, "mobile banking": 3}
    
    Result: {"quản lý rủi ro": 6, "ngân hàng": 10, "mobile banking": 3}
    (Takes MAX for each keyword)
    
    Args:
        analyzer: KeywordAnalyzer instance
        text_parts: List of text strings from different extraction methods
        keywords_map: {keyword: group_id}
        
    Returns:
        (merged_keyword_counts, merged_group_counts)
    """
    if not text_parts or not keywords_map:
        return {}, {}
    
    # Filter valid text parts
    valid_parts = [t for t in text_parts if t and len(t.strip()) > 50]
    
    if not valid_parts:
        return {}, {}
    
    # Analyze each source separately
    all_keyword_counts = []
    source_names = ["Source_1", "Source_2", "Source_3", "Source_4"]  # Generic names
    
    logger.info(f"Analyzing {len(valid_parts)} text sources separately for accurate keyword counting...")
    
    for idx, text in enumerate(valid_parts):
        kw_counts, _ = analyzer.analyze(text, keywords_map)
        all_keyword_counts.append(kw_counts)
        
        total_kw = sum(kw_counts.values())
        source_name = source_names[idx] if idx < len(source_names) else f"Source_{idx+1}"
        logger.debug(f"{source_name}: {total_kw} total keywords, {len(kw_counts)} unique keywords, {len(text):,} chars")
    
    # Merge by taking MAX for each keyword
    merged_keyword_counts = {}
    keyword_source_info = {}  # Track which source provided the max count
    
    for idx, kw_counts in enumerate(all_keyword_counts):
        for keyword, count in kw_counts.items():
            current_max = merged_keyword_counts.get(keyword, 0)
            if count > current_max:
                merged_keyword_counts[keyword] = count
                keyword_source_info[keyword] = idx
    
    # Calculate group counts from merged keyword counts
    merged_group_counts = {}
    for keyword, count in merged_keyword_counts.items():
        group_id = keywords_map.get(keyword, 0)
        merged_group_counts[group_id] = merged_group_counts.get(group_id, 0) + count
    
    # Log summary
    total_merged = sum(merged_keyword_counts.values())
    total_raw = sum(sum(kw.values()) for kw in all_keyword_counts)
    
    logger.info(f"Merged keyword counts: {len(merged_keyword_counts)} unique keywords, {total_merged} total occurrences")
    logger.info(f"  (Raw sum from all sources: {total_raw} - using MAX prevented {total_raw - total_merged} duplicate counts)")
    
    return merged_keyword_counts, merged_group_counts


class TextDeduplicator:
    """
    Deduplicates text from multiple extraction sources while preserving unique content.
    Strategy: Remove exact duplicates and highly similar text segments.
    """
    
    def __init__(self):
        self.processor = get_text_processor()
        self._whitespace_pattern = re.compile(r'\s+')
    
    def normalize_for_comparison(self, text: str) -> str:
        """
        Normalize text for comparison (remove extra whitespace, lowercase).
        This helps identify duplicates even with minor formatting differences.
        """
        if not text:
            return ""
        # Normalize whitespace
        normalized = self._whitespace_pattern.sub(' ', text.strip())
        # Lowercase for comparison
        normalized = normalized.lower()
        return normalized
    
    def deduplicate_text_sources(self, text_parts: List[str]) -> str:
        """
        Deduplicate text from multiple extraction sources.
        
        Strategy:
        1. Use the longest text as base (most complete)
        2. For each additional source, only add content that's significantly different
        3. Compare normalized text to identify duplicates
        
        Args:
            text_parts: List of text strings from different extraction methods
            
        Returns:
            Deduplicated text string
        """
        if not text_parts:
            return ""
        
        if len(text_parts) == 1:
            return text_parts[0]
        
        # Filter out empty or very short texts
        valid_parts = [t for t in text_parts if t and len(t.strip()) > 50]
        
        if not valid_parts:
            return ""
        
        if len(valid_parts) == 1:
            return valid_parts[0]
        
        # Sort by length (longest first) - longest is likely most complete
        valid_parts.sort(key=lambda x: len(x), reverse=True)
        base_text = valid_parts[0]
        base_normalized = self.normalize_for_comparison(base_text)
        
        # Split base text into sentences/paragraphs for comparison
        base_segments = self._split_into_segments(base_text)
        base_segments_normalized = [self.normalize_for_comparison(s) for s in base_segments]
        
        # Build deduplicated text
        deduplicated_text = base_text
        deduplicated_segments_normalized = set(base_segments_normalized)
        
        # Process additional sources
        for additional_text in valid_parts[1:]:
            additional_normalized = self.normalize_for_comparison(additional_text)
            additional_segments = self._split_into_segments(additional_text)
            
            # Find unique segments from additional source
            unique_segments = []
            for segment in additional_segments:
                segment_normalized = self.normalize_for_comparison(segment)
                
                # Check if this segment is significantly different from base
                is_duplicate = False
                for base_seg_norm in deduplicated_segments_normalized:
                    # Check for high similarity (80%+ overlap)
                    similarity = self._calculate_similarity(segment_normalized, base_seg_norm)
                    if similarity > 0.8:
                        is_duplicate = True
                        break
                
                if not is_duplicate and segment_normalized:
                    unique_segments.append(segment)
                    deduplicated_segments_normalized.add(segment_normalized)
            
            # Add unique segments to deduplicated text
            if unique_segments:
                unique_text = "\n".join(unique_segments)
                deduplicated_text += "\n" + unique_text
                logger.debug(f"Added {len(unique_segments)} unique segments from additional source ({len(unique_text)} chars)")
        
        logger.info(f"Deduplicated {len(valid_parts)} text sources: {sum(len(t) for t in valid_parts):,} chars -> {len(deduplicated_text):,} chars")
        
        return deduplicated_text
    
    def _split_into_segments(self, text: str) -> List[str]:
        """
        Split text into segments (sentences/paragraphs) for comparison.
        """
        # Split by double newlines (paragraphs) first
        paragraphs = text.split('\n\n')
        
        # If no paragraphs, split by single newlines
        if len(paragraphs) == 1:
            paragraphs = text.split('\n')
        
        # Further split long paragraphs into sentences
        segments = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Split by sentence endings
            sentences = re.split(r'[.!?]\s+', para)
            for sent in sentences:
                sent = sent.strip()
                if sent and len(sent) > 20:  # Only keep meaningful sentences
                    segments.append(sent)
        
        return segments
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two normalized text strings.
        Returns a value between 0.0 (completely different) and 1.0 (identical).
        """
        if not text1 or not text2:
            return 0.0
        
        # Exact match
        if text1 == text2:
            return 1.0
        
        # Calculate word overlap
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity (intersection over union)
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        similarity = intersection / union
        return similarity


def deduplicate_text_sources(text_parts: List[str]) -> str:
    """
    Convenience function to deduplicate text from multiple sources.
    """
    deduplicator = TextDeduplicator()
    return deduplicator.deduplicate_text_sources(text_parts)
