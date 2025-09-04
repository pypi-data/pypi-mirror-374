"""
Configuration Module for Vietnamese Text Normalization

This module provides configuration management for the Vietnamese text normalization system.
It supports loading configurations from files, presets, and programmatic configuration.
"""

import json
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path


class ConfigManager:
    """Manages configuration for Vietnamese text normalization"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize ConfigManager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self._config = self._load_default_config()
        
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'normalization': {
                'convert_numbers': True,
                'expand_abbreviations': True,
                'convert_special_chars': True,
                'spell_unknown_words': True,
                'apply_regex_rules': True,
                'normalize_dates': True,
                'normalize_phone_numbers': True,
                'normalize_measurements': True,
                'clean_whitespace': True,
                'preserve_case': False
            },
            'dictionaries': {
                'dict_dir': None,
                'auto_reload': False,
                'cache_enabled': True
            },
            'regex_rules': {
                'custom_rules': [],
                'rule_files': [],
                'priority_order': ['date', 'phone', 'measurement', 'custom']
            },
            'output': {
                'encoding': 'utf-8',
                'line_ending': '\\n',
                'include_metadata': False
            }
        }
    
    def load_from_file(self, filepath: str):
        """
        Load configuration from file
        
        Args:
            filepath: Path to configuration file
        """
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
            elif file_path.suffix.lower() in ['.yml', '.yaml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_path.suffix}")
            
            # Merge with existing config
            self._merge_config(file_config)
            
        except Exception as e:
            raise IOError(f"Error loading configuration from {filepath}: {e}")
    
    def save_to_file(self, filepath: str, format: str = 'json'):
        """
        Save configuration to file
        
        Args:
            filepath: Path to save configuration
            format: File format ('json' or 'yaml')
        """
        file_path = Path(filepath)
        
        try:
            if format.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            elif format.lower() in ['yml', 'yaml']:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            raise IOError(f"Error saving configuration to {filepath}: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing config"""
        def deep_merge(base: Dict, update: Dict) -> Dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base
        
        self._config = deep_merge(self._config, new_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by key
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]):
        """
        Update multiple configuration values
        
        Args:
            updates: Dictionary of updates
        """
        self._merge_config(updates)
    
    def get_normalization_config(self) -> Dict[str, Any]:
        """Get normalization-specific configuration"""
        return self.get('normalization', {})
    
    def get_dictionary_config(self) -> Dict[str, Any]:
        """Get dictionary-specific configuration"""
        return self.get('dictionaries', {})
    
    def get_regex_config(self) -> Dict[str, Any]:
        """Get regex rules configuration"""
        return self.get('regex_rules', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output-specific configuration"""
        return self.get('output', {})
    
    def add_custom_rule(self, name: str, pattern: str, replacement: str, 
                       flags: int = 0, priority: int = 0):
        """
        Add a custom regex rule to configuration
        
        Args:
            name: Rule name
            pattern: Regex pattern
            replacement: Replacement text or function name
            flags: Regex flags
            priority: Rule priority
        """
        custom_rules = self.get('regex_rules.custom_rules', [])
        custom_rules.append({
            'name': name,
            'pattern': pattern,
            'replacement': replacement,
            'flags': flags,
            'priority': priority
        })
        self.set('regex_rules.custom_rules', custom_rules)
    
    def add_rule_file(self, filepath: str, priority: int = 0):
        """
        Add a rule file to configuration
        
        Args:
            filepath: Path to rule file
            priority: Priority for rules in this file
        """
        rule_files = self.get('regex_rules.rule_files', [])
        rule_files.append({
            'filepath': filepath,
            'priority': priority
        })
        self.set('regex_rules.rule_files', rule_files)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration"""
        return self._config.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = self._load_default_config()


class PresetManager:
    """Manages configuration presets"""
    
    def __init__(self):
        """Initialize PresetManager"""
        self._presets = self._load_default_presets()
    
    def _load_default_presets(self) -> Dict[str, Dict[str, Any]]:
        """Load default presets"""
        return {
            'basic': {
                'normalization': {
                    'convert_numbers': True,
                    'expand_abbreviations': True,
                    'convert_special_chars': True,
                    'spell_unknown_words': False,
                    'apply_regex_rules': True,
                    'clean_whitespace': True
                }
            },
            'advanced': {
                'normalization': {
                    'convert_numbers': True,
                    'expand_abbreviations': True,
                    'convert_special_chars': True,
                    'spell_unknown_words': True,
                    'apply_regex_rules': True,
                    'normalize_dates': True,
                    'normalize_phone_numbers': True,
                    'normalize_measurements': True,
                    'clean_whitespace': True,
                    'preserve_case': False
                },
                'dictionaries': {
                    'auto_reload': True,
                    'cache_enabled': True
                }
            },
            'minimal': {
                'normalization': {
                    'convert_numbers': True,
                    'expand_abbreviations': False,
                    'convert_special_chars': False,
                    'spell_unknown_words': False,
                    'apply_regex_rules': False,
                    'clean_whitespace': True
                }
            },
            'tts_optimized': {
                'normalization': {
                    'convert_numbers': True,
                    'expand_abbreviations': True,
                    'convert_special_chars': True,
                    'spell_unknown_words': True,
                    'apply_regex_rules': True,
                    'normalize_dates': True,
                    'normalize_phone_numbers': True,
                    'normalize_measurements': True,
                    'clean_whitespace': True,
                    'preserve_case': False
                },
                'output': {
                    'include_metadata': True
                }
            }
        }
    
    def get_preset(self, name: str) -> Dict[str, Any]:
        """
        Get configuration preset by name
        
        Args:
            name: Preset name
            
        Returns:
            Configuration dictionary
        """
        if name not in self._presets:
            raise ValueError(f"Unknown preset: {name}. Available presets: {list(self._presets.keys())}")
        
        return self._presets[name].copy()
    
    def list_presets(self) -> List[str]:
        """List available presets"""
        return list(self._presets.keys())
    
    def add_preset(self, name: str, config: Dict[str, Any]):
        """
        Add a custom preset
        
        Args:
            name: Preset name
            config: Configuration dictionary
        """
        self._presets[name] = config.copy()
    
    def remove_preset(self, name: str):
        """
        Remove a preset
        
        Args:
            name: Preset name
        """
        if name in self._presets:
            del self._presets[name]
        else:
            raise ValueError(f"Preset not found: {name}")


# Global instances
_config_manager = ConfigManager()
_preset_manager = PresetManager()


def get_config_manager() -> ConfigManager:
    """Get global configuration manager"""
    return _config_manager


def get_preset_manager() -> PresetManager:
    """Get global preset manager"""
    return _preset_manager


def load_config_from_preset(preset_name: str) -> Dict[str, Any]:
    """
    Load configuration from preset
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        Configuration dictionary
    """
    return _preset_manager.get_preset(preset_name)


def create_config_from_preset(preset_name: str, **overrides) -> ConfigManager:
    """
    Create a ConfigManager from a preset with optional overrides
    
    Args:
        preset_name: Name of the preset
        **overrides: Configuration overrides
        
    Returns:
        Configured ConfigManager instance
    """
    config = ConfigManager()
    preset_config = _preset_manager.get_preset(preset_name)
    config.update(preset_config)
    config.update(overrides)
    return config
