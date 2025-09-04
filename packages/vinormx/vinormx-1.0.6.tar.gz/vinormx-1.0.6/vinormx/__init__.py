"""
Vietnamese Text Normalization - Optimized Version

This is an optimized version of the Vietnamese text normalization system
that uses a modular architecture with separate modules for dictionaries,
mappings, and regex rules. This version includes performance optimizations
for maximum speed and efficiency.

The optimized version maintains backward compatibility with the original API.
"""

import re
import time
from functools import lru_cache
from typing import Optional, Dict, List, Any, Set
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
from collections import OrderedDict

from .dict_module import DictManager
from .mapping_module import MappingManager
from .regex_rule_module import RegexRuleManager
from .config_module import ConfigManager


class VietnameseNormalizer:
    """
    Optimized Vietnamese Text Normalizer with Performance Enhancements
    
    This class provides Vietnamese text normalization using a modular architecture
    with advanced performance optimizations including caching, parallel processing,
    and smart text chunking for maximum speed and efficiency.
    """
    
    def __init__(self, 
                 dict_dir: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None,
                 enable_caching: bool = True,
                 cache_size: int = 2000,
                 chunk_size: int = 1500,
                 max_workers: int = 4,
                 enable_pattern_filtering: bool = True,
                 enable_parallel_processing: bool = True):
        """
        Initialize Optimized VietnameseNormalizer
        
        Args:
            dict_dir: Directory containing dictionary files
            config: Configuration dictionary for customizing behavior
            enable_caching: Enable advanced LRU caching
            cache_size: Maximum cache size for LRU cache
            chunk_size: Maximum chunk size for text processing
            max_workers: Maximum number of worker threads
            enable_pattern_filtering: Enable pattern pre-filtering
            enable_parallel_processing: Enable parallel processing for chunks
        """
        # Initialize managers
        self.dict_manager = DictManager(dict_dir)
        self.mapping_manager = MappingManager(self.dict_manager)
        self.regex_manager = RegexRuleManager(self.mapping_manager.number_mapper)
        
        # Configuration
        self.config = config or self._get_default_config()
        
        # Performance settings
        self.enable_caching = enable_caching
        self.cache_size = cache_size
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.enable_pattern_filtering = enable_pattern_filtering
        self.enable_parallel_processing = enable_parallel_processing
        
        # Pre-compile frequently used regex patterns with optimization
        self._precompile_patterns()
        
        # Initialize advanced caching
        if self.enable_caching:
            self._cache = OrderedDict()  # LRU cache with ordered dict
            self._cache_lock = threading.RLock()  # Reentrant lock for better performance
        
        # Pattern filtering for faster processing
        if self.enable_pattern_filtering:
            self._pattern_indicators = self._build_pattern_indicators()
        
        # Performance metrics
        self._stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'pattern_filter_hits': 0,
            'pattern_filter_misses': 0,
            'chunk_processing_count': 0,
            'parallel_processing_count': 0
        }
        self._stats_lock = threading.RLock()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'convert_numbers': True,
            'expand_abbreviations': True,
            'convert_special_chars': True,
            'spell_unknown_words': True,
            'normalize_dates': True,
            'normalize_times': True,
            'normalize_emails': True,
            'normalize_phones': True,
            'normalize_urls': True,
            'normalize_currency': True,
            'normalize_measurements': True
        }
    
    def _precompile_patterns(self):
        """Pre-compile frequently used regex patterns with optimization"""
        # Compile patterns with re.UNICODE for better performance
        self._compiled_patterns = {
            'whitespace': re.compile(r'\s+', re.UNICODE),
            'punctuation': re.compile(r'[.,!?;:]+', re.UNICODE),
            'numbers': re.compile(r'\d+', re.UNICODE),
            'dates': re.compile(r'\d{1,2}/\d{1,2}/\d{4}', re.UNICODE),
            'times': re.compile(r'\d{1,2}:\d{2}', re.UNICODE),
            'emails': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.UNICODE),
            'phones': re.compile(r'0\d{9,10}', re.UNICODE),
            'urls': re.compile(r'https?://[^\s]+', re.UNICODE),
            'currency': re.compile(r'\d+(?:,\d{3})*(?:\.\d+)?\s*(?:VND|USD|EUR)', re.UNICODE),
            'measurements': re.compile(r'\d+(?:\.\d+)?\s*(?:km|m|cm|mm|kg|g|ml|l)', re.UNICODE),
        }
    
    def _build_pattern_indicators(self) -> Set[str]:
        """Build pattern indicators for fast pre-filtering"""
        indicators = set()
        
        # Add common patterns that indicate specific processing needs
        indicators.update(['@', '://', 'www.', '.com', '.vn', '.org'])
        indicators.update(['VND', 'USD', 'EUR', 'km', 'm', 'cm', 'mm', 'kg', 'g'])
        indicators.update(['ANTQ', 'VNPT', 'FPT', 'Viettel', 'Mobifone'])
        indicators.update(['ngày', 'tháng', 'năm', 'giờ', 'phút'])
        
        # Add number patterns to ensure numbers are always processed
        indicators.update(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        
        return indicators
    
    def _should_process_text(self, text: str) -> bool:
        """Quick check if text needs processing based on pattern indicators"""
        if not self.enable_pattern_filtering:
            return True
        
        text_lower = text.lower()
        for indicator in self._pattern_indicators:
            if indicator.lower() in text_lower:
                self._stats['pattern_filter_hits'] += 1
                return True
        
        self._stats['pattern_filter_misses'] += 1
        return False
    
    def _get_cache_key(self, text: str, options: Dict[str, Any]) -> str:
        """Generate optimized cache key"""
        # Use hash of text + options for faster key generation
        key_data = f"{text}|{hash(frozenset(options.items()))}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Get result from cache with LRU optimization"""
        if not self.enable_caching:
            return None
        
        with self._cache_lock:
            if cache_key in self._cache:
                # Move to end (most recently used)
                result = self._cache.pop(cache_key)
                self._cache[cache_key] = result
                self._stats['cache_hits'] += 1
                return result
            else:
                self._stats['cache_misses'] += 1
                return None
    
    def _set_cache(self, cache_key: str, result: str):
        """Set result in cache with LRU eviction"""
        if not self.enable_caching:
            return
        
        with self._cache_lock:
            # Remove oldest if cache is full
            if len(self._cache) >= self.cache_size:
                self._cache.popitem(last=False)  # Remove oldest
            
            self._cache[cache_key] = result
    
    def _smart_chunk_text(self, text: str) -> List[str]:
        """Smart text chunking with overlap handling for better context preservation"""
        if len(text) <= self.chunk_size:
            return [text]
        
        # Split by sentences first for better context
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        overlap_size = min(100, self.chunk_size // 10)  # 10% overlap or 100 chars max
        
        for i, sentence in enumerate(sentences):
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + "."
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap from previous
                if chunks and overlap_size > 0:
                    prev_chunk = chunks[-1]
                    overlap = prev_chunk[-overlap_size:] if len(prev_chunk) > overlap_size else prev_chunk
                    current_chunk = overlap + " " + sentence + "."
                else:
                    current_chunk = sentence + "."
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _process_chunk_optimized(self, chunk: str, options: Dict[str, Any]) -> str:
        """Ultra-optimized chunk processing"""
        # Quick pattern filtering
        if not self._should_process_text(chunk):
            return chunk
        
        # Apply mapping transformations with early exit for simple cases
        if len(chunk) < 50 and not any(char.isdigit() for char in chunk):
            # Simple text without numbers, skip heavy processing
            result = self.mapping_manager.normalize_text(
                chunk,
                convert_numbers=False,
                expand_abbreviations=options.get('expand_abbreviations', True),
                convert_special_chars=options.get('convert_special_chars', True),
                spell_unknown_words=False
            )
        else:
            # Full processing for complex text or text with numbers
            result = self.mapping_manager.normalize_text(
                chunk,
                convert_numbers=options.get('convert_numbers', True),
                expand_abbreviations=options.get('expand_abbreviations', True),
                convert_special_chars=options.get('convert_special_chars', True),
                spell_unknown_words=options.get('spell_unknown_words', True)
            )
        
        # Apply regex rules
        result = self.regex_manager.apply_all_rules(result)
        
        # Convert to lowercase to match original behavior
        result = result.lower()
        
        return result
    
    def _process_chunks_parallel_optimized(self, chunks: List[str], options: Dict[str, Any]) -> List[str]:
        """Ultra-optimized parallel chunk processing"""
        if len(chunks) == 1:
            return [self._process_chunk_optimized(chunks[0], options)]
        
        # Use thread pool with optimized settings
        results = []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(chunks))) as executor:
            futures = [executor.submit(self._process_chunk_optimized, chunk, options) for chunk in chunks]
            results = [future.result() for future in futures]
        
        return results
    
    def normalize(self, 
                  text: str,
                  convert_numbers: Optional[bool] = None,
                  expand_abbreviations: Optional[bool] = None,
                  convert_special_chars: Optional[bool] = None,
                  spell_unknown_words: Optional[bool] = None,
                  normalize_dates: Optional[bool] = None,
                  normalize_times: Optional[bool] = None,
                  normalize_emails: Optional[bool] = None,
                  normalize_phones: Optional[bool] = None,
                  normalize_urls: Optional[bool] = None,
                  normalize_currency: Optional[bool] = None,
                  normalize_measurements: Optional[bool] = None,
                  use_chunking: bool = True,
                  use_parallel: bool = True) -> str:
        """
        Optimized Vietnamese text normalization with performance enhancements
        
        Args:
            text: Input text to normalize
            convert_numbers: Convert numbers to words (overrides config)
            expand_abbreviations: Expand abbreviations (overrides config)
            convert_special_chars: Convert special characters (overrides config)
            spell_unknown_words: Spell out unknown words (overrides config)
            normalize_dates: Normalize dates (overrides config)
            normalize_times: Normalize times (overrides config)
            normalize_emails: Normalize emails (overrides config)
            normalize_phones: Normalize phone numbers (overrides config)
            normalize_urls: Normalize URLs (overrides config)
            normalize_currency: Normalize currency (overrides config)
            normalize_measurements: Normalize measurements (overrides config)
            use_chunking: Use smart text chunking for long texts
            use_parallel: Use parallel processing for chunks
            
        Returns:
            Normalized text
        """
        if not text or not text.strip():
            return text
        
        start_time = time.time()
        
        # Use provided parameters or fall back to config
        convert_numbers = convert_numbers if convert_numbers is not None else self.config['convert_numbers']
        expand_abbreviations = expand_abbreviations if expand_abbreviations is not None else self.config['expand_abbreviations']
        convert_special_chars = convert_special_chars if convert_special_chars is not None else self.config['convert_special_chars']
        spell_unknown_words = spell_unknown_words if spell_unknown_words is not None else self.config['spell_unknown_words']
        
        # Create options dictionary
        options = {
            'convert_numbers': convert_numbers,
            'expand_abbreviations': expand_abbreviations,
            'convert_special_chars': convert_special_chars,
            'spell_unknown_words': spell_unknown_words
        }
        
        # Check cache first
        if self.enable_caching:
            cache_key = self._get_cache_key(text, options)
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
        
        # Process text with smart chunking
        if use_chunking and len(text) > self.chunk_size:
            chunks = self._smart_chunk_text(text)
            self._stats['chunk_processing_count'] += 1
            
            if use_parallel and self.enable_parallel_processing and len(chunks) > 1:
                processed_chunks = self._process_chunks_parallel_optimized(chunks, options)
                self._stats['parallel_processing_count'] += 1
            else:
                processed_chunks = [self._process_chunk_optimized(chunk, options) for chunk in chunks]
            
            result = " ".join(processed_chunks)
        else:
            # Process normally with optimization
            result = self._process_chunk_optimized(text, options)
        
        # Cache result
        if self.enable_caching:
            self._set_cache(cache_key, result)
        
        # Update statistics
        end_time = time.time()
        with self._stats_lock:
            self._stats['total_processed'] += 1
            self._stats['total_time'] += (end_time - start_time)
        
        return result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self._stats_lock:
            stats = self._stats.copy()
        
        if stats['total_processed'] > 0:
            stats['avg_time_per_text'] = stats['total_time'] / stats['total_processed']
            stats['texts_per_second'] = stats['total_processed'] / stats['total_time'] if stats['total_time'] > 0 else 0
        else:
            stats['avg_time_per_text'] = 0
            stats['texts_per_second'] = 0
        
        if self.enable_caching:
            total_cache_requests = stats['cache_hits'] + stats['cache_misses']
            stats['cache_hit_rate'] = stats['cache_hits'] / total_cache_requests if total_cache_requests > 0 else 0
        else:
            stats['cache_hit_rate'] = 0
        
        if self.enable_pattern_filtering:
            total_filter_requests = stats['pattern_filter_hits'] + stats['pattern_filter_misses']
            stats['pattern_filter_hit_rate'] = stats['pattern_filter_hits'] / total_filter_requests if total_filter_requests > 0 else 0
        else:
            stats['pattern_filter_hit_rate'] = 0
        
        # Additional metrics
        if stats['total_processed'] > 0:
            stats['chunk_processing_rate'] = stats['chunk_processing_count'] / stats['total_processed']
            stats['parallel_processing_rate'] = stats['parallel_processing_count'] / stats['total_processed']
        else:
            stats['chunk_processing_rate'] = 0
            stats['parallel_processing_rate'] = 0
        
        return stats
    
    def clear_cache(self):
        """Clear the cache"""
        if self.enable_caching:
            with self._cache_lock:
                self._cache.clear()
    
    def reset_stats(self):
        """Reset performance statistics"""
        with self._stats_lock:
            self._stats = {
                'total_processed': 0,
                'total_time': 0.0,
                'cache_hits': 0,
                'cache_misses': 0,
                'pattern_filter_hits': 0,
                'pattern_filter_misses': 0,
                'chunk_processing_count': 0,
                'parallel_processing_count': 0
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        if not self.enable_caching:
            return {'enabled': False}
        
        with self._cache_lock:
            return {
                'enabled': True,
                'size': len(self._cache),
                'max_size': self.cache_size,
                'utilization': len(self._cache) / self.cache_size
            }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, **kwargs):
        """Update configuration"""
        self.config.update(kwargs)
    
    def get_dict_info(self) -> Dict[str, Any]:
        """Get dictionary information"""
        return self.dict_manager.get_dict_info()
    
    def get_regex_info(self) -> Dict[str, Any]:
        """Get regex rule information"""
        return self.regex_manager.get_rule_info()
    
    # Backward compatibility methods
    def normalize_with_metadata(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Normalize text and return metadata about the process
        
        Args:
            text: Input text to normalize
            **kwargs: Additional options
            
        Returns:
            Dictionary with normalized text and metadata
        """
        start_time = time.time()
        
        normalized = self.normalize(text, **kwargs)
        
        processing_time = time.time() - start_time
        
        return {
            'original_text': text,
            'normalized_text': normalized,
            'processing_time': processing_time,
            'text_length': len(text),
            'normalized_length': len(normalized),
            'config_used': {**self.config, **kwargs}
        }
    
    def batch_normalize(self, texts: List[str], **kwargs) -> List[str]:
        """
        Normalize multiple texts in batch
        
        Args:
            texts: List of texts to normalize
            **kwargs: Additional options
            
        Returns:
            List of normalized texts
        """
        return [self.normalize(text, **kwargs) for text in texts]
    
    def add_custom_rule(self, name: str, pattern: str, replacement: str):
        """
        Add a custom regex rule
        
        Args:
            name: Name of the rule
            pattern: Regex pattern
            replacement: Replacement string
        """
        self.regex_manager.add_custom_rule(name, pattern, replacement)


# Global normalizer instance for backward compatibility
_normalizer = None

def get_normalizer() -> VietnameseNormalizer:
    """Get the global normalizer instance"""
    global _normalizer
    if _normalizer is None:
        _normalizer = VietnameseNormalizer()
    return _normalizer

def TTSnorm(text: str, **kwargs) -> str:
    """
    Main function for Vietnamese text normalization (backward compatibility)
    
    Args:
        text: Input text to normalize
        **kwargs: Additional options
        
    Returns:
        Normalized text
    """
    normalizer = get_normalizer()
    return normalizer.normalize(text, **kwargs)

def create_normalizer(preset: str = 'basic', **kwargs) -> VietnameseNormalizer:
    """
    Create a normalizer with a preset configuration
    
    Args:
        preset: Preset name ('basic', 'advanced', 'minimal', 'tts_optimized')
        **kwargs: Additional configuration options
        
    Returns:
        Configured VietnameseNormalizer instance
    """
    from .config_module import create_normalizer as _create_normalizer
    return _create_normalizer(preset, **kwargs)

# Export main classes and functions
__all__ = [
    'VietnameseNormalizer',
    'TTSnorm', 
    'create_normalizer',
    'get_normalizer'
]