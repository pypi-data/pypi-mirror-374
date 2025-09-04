"""
Vietnamese Text Normalization Package

This package provides modular Vietnamese text normalization capabilities
with support for numbers, abbreviations, special characters, and regex rules.
"""

from vinormx_refactored import (
    VietnameseNormalizer,
    AdvancedVietnameseNormalizer,
    TTSnorm,
    create_normalizer,
    PRESETS
)

from dict_module import DictManager, DictLoader
from mapping_module import MappingManager
from regex_rule_module import RegexRuleManager

__version__ = "2.0.0"
__author__ = "Vietnamese Text Normalization Team"

# Backward compatibility
def normalize_vietnamese_text(text: str, **kwargs) -> str:
    """
    Normalize Vietnamese text (backward compatibility function)
    
    Args:
        text: Input text to normalize
        **kwargs: Configuration options
        
    Returns:
        Normalized text
    """
    return TTSnorm(text, **kwargs)

# Export main classes and functions
__all__ = [
    'VietnameseNormalizer',
    'AdvancedVietnameseNormalizer', 
    'TTSnorm',
    'create_normalizer',
    'PRESETS',
    'DictManager',
    'DictLoader',
    'MappingManager',
    'RegexRuleManager',
    'normalize_vietnamese_text'
]
