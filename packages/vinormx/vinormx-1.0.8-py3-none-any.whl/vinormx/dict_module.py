"""
Dict Module - Dictionary Management for Vietnamese Text Normalization

This module handles loading and managing dictionary data from various sources.
It provides a flexible system for loading different types of dictionaries
used in Vietnamese text normalization.
"""

import os
from typing import Dict, List, Optional, Union
from pathlib import Path


class DictLoader:
    """Loads and manages dictionary data from files"""
    
    def __init__(self, dict_dir: Optional[str] = None):
        """
        Initialize DictLoader
        
        Args:
            dict_dir: Directory containing dictionary files. If None, uses default structure.
        """
        if dict_dir is None:
            # Default to dictionaries subdirectory
            self.dict_dir = Path(__file__).parent / "dictionaries"
        else:
            self.dict_dir = Path(dict_dir)
        
        self._loaded_dicts = {}
    
    def load_dict_file(self, filename: str, delimiter: str = "#") -> Dict[str, str]:
        """
        Load a dictionary file with key-value pairs
        
        Args:
            filename: Name of the dictionary file
            delimiter: Delimiter used to separate key and value (default: "#")
            
        Returns:
            Dictionary mapping keys to values
        """
        file_path = self.dict_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dictionary file not found: {file_path}")
        
        result = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Split by delimiter
                    parts = line.split(delimiter, 1)
                    if len(parts) != 2:
                        print(f"Warning: Invalid format in {filename} line {line_num}: {line}")
                        continue
                    
                    key, value = parts[0].strip(), parts[1].strip()
                    if key and value:
                        result[key] = value
        
        except Exception as e:
            raise IOError(f"Error loading dictionary file {filename}: {e}")
        
        return result
    
    def load_number_dict(self) -> Dict[str, str]:
        """Load number dictionary"""
        return self.load_dict_file("number_dict.txt")
    
    def load_month_dict(self) -> Dict[str, str]:
        """Load month dictionary"""
        return self.load_dict_file("month_dict.txt")
    
    def load_abbreviation_dict(self) -> Dict[str, str]:
        """Load abbreviation dictionary"""
        return self.load_dict_file("abbreviation_dict.txt")
    
    def load_special_chars_dict(self) -> Dict[str, str]:
        """Load special characters dictionary"""
        return self.load_dict_file("special_chars_dict.txt")
    
    def load_letter_sound_dict(self) -> Dict[str, str]:
        """Load letter sound dictionary"""
        return self.load_dict_file("letter_sound_dict.txt")
    
    def load_currency_dict(self) -> Dict[str, str]:
        """Load currency dictionary"""
        return self.load_dict_file("currency_dict.txt")
    
    def load_unit_dict(self) -> Dict[str, str]:
        """Load unit dictionary"""
        return self.load_dict_file("unit_dict.txt")
    
    def load_acronyms_dict(self) -> Dict[str, str]:
        """Load comprehensive acronyms dictionary"""
        return self.load_dict_file("acronyms_dict.txt")
    
    def load_teencode_dict(self) -> Dict[str, str]:
        """Load teencode dictionary"""
        return self.load_dict_file("teencode_dict.txt")
    
    def load_base_unit_dict(self) -> Dict[str, str]:
        """Load base unit dictionary"""
        return self.load_dict_file("base_unit_dict.txt")
    
    def load_letter_sound_vn_dict(self) -> Dict[str, str]:
        """Load Vietnamese letter sound dictionary"""
        return self.load_dict_file("letter_sound_vn_dict.txt")
    
    def load_symbol_dict(self) -> Dict[str, str]:
        """Load symbol dictionary"""
        return self.load_dict_file("symbol_dict.txt")
    
    def load_prefix_unit_dict(self) -> Dict[str, str]:
        """Load prefix unit dictionary"""
        return self.load_dict_file("prefix_unit_dict.txt")
    
    def get_dict(self, dict_name: str) -> Dict[str, str]:
        """
        Get a dictionary by name, loading it if not already loaded
        
        Args:
            dict_name: Name of the dictionary to get
            
        Returns:
            Dictionary data
        """
        if dict_name not in self._loaded_dicts:
            # Map dictionary names to loading methods
            dict_loaders = {
                'number': self.load_number_dict,
                'month': self.load_month_dict,
                'abbreviation': self.load_abbreviation_dict,
                'special_chars': self.load_special_chars_dict,
                'letter_sound': self.load_letter_sound_dict,
                'currency': self.load_currency_dict,
                'unit': self.load_unit_dict,
                'acronyms': self.load_acronyms_dict,
                'teencode': self.load_teencode_dict,
                'base_unit': self.load_base_unit_dict,
                'letter_sound_vn': self.load_letter_sound_vn_dict,
                'symbol': self.load_symbol_dict,
                'prefix_unit': self.load_prefix_unit_dict,
            }
            
            if dict_name not in dict_loaders:
                raise ValueError(f"Unknown dictionary: {dict_name}")
            
            self._loaded_dicts[dict_name] = dict_loaders[dict_name]()
        
        return self._loaded_dicts[dict_name]
    
    def reload_dict(self, dict_name: str) -> Dict[str, str]:
        """
        Reload a dictionary from file
        
        Args:
            dict_name: Name of the dictionary to reload
            
        Returns:
            Reloaded dictionary data
        """
        if dict_name in self._loaded_dicts:
            del self._loaded_dicts[dict_name]
        
        return self.get_dict(dict_name)
    
    def list_available_dicts(self) -> List[str]:
        """List all available dictionary files in the directory"""
        dict_files = []
        for file_path in self.dict_dir.glob("*.txt"):
            dict_files.append(file_path.stem)
        return sorted(dict_files)


class DictManager:
    """High-level dictionary management with caching and validation"""
    
    def __init__(self, dict_dir: Optional[str] = None):
        """
        Initialize DictManager
        
        Args:
            dict_dir: Directory containing dictionary files
        """
        self.loader = DictLoader(dict_dir)
        self._cache = {}
        self._validation_rules = {}
    
    def get_number_dict(self) -> Dict[str, str]:
        """Get number dictionary with validation"""
        return self._get_validated_dict('number', self._validate_number_dict)
    
    def get_month_dict(self) -> Dict[str, str]:
        """Get month dictionary with validation"""
        return self._get_validated_dict('month', self._validate_month_dict)
    
    def get_abbreviation_dict(self) -> Dict[str, str]:
        """Get abbreviation dictionary with validation"""
        return self._get_validated_dict('abbreviation', self._validate_abbreviation_dict)
    
    def get_special_chars_dict(self) -> Dict[str, str]:
        """Get special characters dictionary with validation"""
        return self._get_validated_dict('special_chars', self._validate_special_chars_dict)
    
    def get_letter_sound_dict(self) -> Dict[str, str]:
        """Get letter sound dictionary with validation"""
        return self._get_validated_dict('letter_sound', self._validate_letter_sound_dict)
    
    def get_acronyms_dict(self) -> Dict[str, str]:
        """Get comprehensive acronyms dictionary with validation"""
        return self._get_validated_dict('acronyms', self._validate_acronyms_dict)
    
    def get_teencode_dict(self) -> Dict[str, str]:
        """Get teencode dictionary with validation"""
        return self._get_validated_dict('teencode', self._validate_teencode_dict)
    
    def get_base_unit_dict(self) -> Dict[str, str]:
        """Get base unit dictionary with validation"""
        return self._get_validated_dict('base_unit', self._validate_base_unit_dict)
    
    def get_letter_sound_vn_dict(self) -> Dict[str, str]:
        """Get Vietnamese letter sound dictionary with validation"""
        return self._get_validated_dict('letter_sound_vn', self._validate_letter_sound_vn_dict)
    
    def get_symbol_dict(self) -> Dict[str, str]:
        """Get symbol dictionary with validation"""
        return self._get_validated_dict('symbol', self._validate_symbol_dict)
    
    def get_prefix_unit_dict(self) -> Dict[str, str]:
        """Get prefix unit dictionary with validation"""
        return self._get_validated_dict('prefix_unit', self._validate_prefix_unit_dict)
    
    def _get_validated_dict(self, dict_name: str, validator) -> Dict[str, str]:
        """Get dictionary with validation"""
        if dict_name not in self._cache:
            dict_data = self.loader.get_dict(dict_name)
            if validator:
                dict_data = validator(dict_data)
            self._cache[dict_name] = dict_data
        
        return self._cache[dict_name]
    
    def _validate_number_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate number dictionary"""
        # Ensure all keys are numeric strings
        validated = {}
        for key, value in data.items():
            if key.isdigit() or key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                validated[key] = value
            else:
                print(f"Warning: Non-numeric key in number dict: {key}")
        return validated
    
    def _validate_month_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate month dictionary"""
        # Ensure all keys are valid month numbers
        validated = {}
        valid_months = [str(i) for i in range(1, 13)] + [f"{i:02d}" for i in range(1, 13)]
        
        for key, value in data.items():
            if key in valid_months:
                validated[key] = value
            else:
                print(f"Warning: Invalid month key: {key}")
        return validated
    
    def _validate_abbreviation_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate abbreviation dictionary"""
        # Basic validation - ensure keys and values are non-empty
        validated = {}
        for key, value in data.items():
            if key.strip() and value.strip():
                validated[key.strip()] = value.strip()
        return validated
    
    def _validate_special_chars_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate special characters dictionary"""
        # Basic validation - ensure single character keys
        validated = {}
        for key, value in data.items():
            if len(key) == 1 and value.strip():
                validated[key] = value.strip()
        return validated
    
    def _validate_letter_sound_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate letter sound dictionary"""
        # Basic validation - ensure single character keys
        validated = {}
        for key, value in data.items():
            if len(key) == 1 and value.strip():
                validated[key] = value.strip()
        return validated
    
    def _validate_acronyms_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate acronyms dictionary"""
        # Basic validation - ensure keys and values are non-empty
        validated = {}
        for key, value in data.items():
            if key.strip() and value.strip():
                validated[key.strip()] = value.strip()
        return validated
    
    def _validate_teencode_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate teencode dictionary"""
        # Basic validation - ensure keys and values are non-empty
        validated = {}
        for key, value in data.items():
            if key.strip() and value.strip():
                validated[key.strip()] = value.strip()
        return validated
    
    def _validate_base_unit_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate base unit dictionary"""
        # Basic validation - ensure keys and values are non-empty
        validated = {}
        for key, value in data.items():
            if key.strip() and value.strip():
                validated[key.strip()] = value.strip()
        return validated
    
    def _validate_letter_sound_vn_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate Vietnamese letter sound dictionary"""
        # Basic validation - ensure keys and values are non-empty
        validated = {}
        for key, value in data.items():
            if key.strip() and value.strip():
                validated[key.strip()] = value.strip()
        return validated
    
    def _validate_symbol_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate symbol dictionary"""
        # Basic validation - ensure keys and values are non-empty
        validated = {}
        for key, value in data.items():
            if key.strip() and value.strip():
                validated[key.strip()] = value.strip()
        return validated
    
    def _validate_prefix_unit_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """Validate prefix unit dictionary"""
        # Basic validation - ensure keys and values are non-empty
        validated = {}
        for key, value in data.items():
            if key.strip() and value.strip():
                validated[key.strip()] = value.strip()
        return validated
    
    def clear_cache(self):
        """Clear all cached dictionaries"""
        self._cache.clear()
    
    def reload_all(self):
        """Reload all dictionaries"""
        self.clear_cache()
        # Preload common dictionaries
        self.get_number_dict()
        self.get_month_dict()
        self.get_abbreviation_dict()
        self.get_special_chars_dict()


# Convenience function for backward compatibility
def load_dict_file(filename: str, delimiter: str = "#", dict_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Load a dictionary file (convenience function)
    
    Args:
        filename: Name of the dictionary file
        delimiter: Delimiter used to separate key and value
        dict_dir: Directory containing dictionary files
        
    Returns:
        Dictionary mapping keys to values
    """
    loader = DictLoader(dict_dir)
    return loader.load_dict_file(filename, delimiter)
