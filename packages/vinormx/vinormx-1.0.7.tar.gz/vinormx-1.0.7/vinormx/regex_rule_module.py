"""
RegexRule Module - Regex Pattern Management for Vietnamese Text Normalization

This module handles complex regex patterns and rules for text normalization,
including date patterns, phone numbers, measurements, and other structured text.
"""

import re
import os
from typing import Dict, List, Optional, Tuple, Callable, Any
from pathlib import Path


class RegexRule:
    """Represents a single regex rule with pattern and replacement function"""
    
    def __init__(self, name: str, pattern: str, replacement: Callable[[re.Match], str], 
                 flags: int = 0, priority: int = 0):
        """
        Initialize RegexRule
        
        Args:
            name: Name of the rule
            pattern: Regex pattern
            replacement: Function to generate replacement text
            flags: Regex flags
            priority: Rule priority (higher = applied first)
        """
        self.name = name
        self.pattern = pattern
        self.replacement = replacement
        self.flags = flags
        self.priority = priority
        self._compiled_pattern = None
    
    def compile(self):
        """Compile the regex pattern"""
        if self._compiled_pattern is None:
            self._compiled_pattern = re.compile(self.pattern, self.flags)
    
    def apply(self, text: str) -> str:
        """
        Apply the rule to text
        
        Args:
            text: Input text
            
        Returns:
            Text with rule applied
        """
        if self._compiled_pattern is None:
            self.compile()
        
        return self._compiled_pattern.sub(self.replacement, text)


class DateRuleManager:
    """Manages date-related regex rules"""
    
    def __init__(self, number_mapper=None):
        """
        Initialize DateRuleManager
        
        Args:
            number_mapper: Number mapper instance for converting numbers to words
        """
        self.number_mapper = number_mapper
        self._rules = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize date-related rules"""
        # Rule 1: Full date format (dd/mm/yyyy)
        def replace_full_date(match):
            day, month, year = match.groups()
            
            # Check if "ngày" already exists before the date
            start_pos = match.start()
            before_text = match.string[:start_pos]
            has_ngay_before = before_text.rstrip().endswith('ngày')
            
            day_word = self.number_mapper.convert_number_to_words(day) if self.number_mapper else day
            month_word = "tháng " + (self.number_mapper.convert_month_to_words(month) if self.number_mapper else month)
            year_word = "năm " + (self.number_mapper.convert_year_to_words(year) if self.number_mapper else year)
            
            if has_ngay_before:
                return f"{day_word} {month_word} {year_word}"
            else:
                return f"ngày {day_word} {month_word} {year_word}"
        
        self._rules.append(RegexRule(
            "full_date",
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            replace_full_date,
            priority=100
        ))
        
        # Rule 2: Month/Year format (mm/yyyy)
        def replace_month_year(match):
            month, year = match.groups()
            
            # Check if "tháng" already exists before the date
            start_pos = match.start()
            before_text = match.string[:start_pos]
            has_thang_before = before_text.rstrip().endswith('tháng')
            
            month_word = self.number_mapper.convert_month_to_words(month) if self.number_mapper else month
            year_word = "năm " + (self.number_mapper.convert_year_to_words(year) if self.number_mapper else year)
            
            if has_thang_before:
                return f"{month_word} {year_word}"
            else:
                return f"tháng {month_word} {year_word}"
        
        self._rules.append(RegexRule(
            "month_year",
            r'(\d{1,2})/(\d{4})',
            replace_month_year,
            priority=90
        ))
    
    def apply_rules(self, text: str) -> str:
        """
        Apply all date rules to text
        
        Args:
            text: Input text
            
        Returns:
            Text with date rules applied
        """
        result = text
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self._rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            result = rule.apply(result)
        
        return result


class PhoneNumberRuleManager:
    """Manages phone number regex rules"""
    
    def __init__(self):
        """Initialize PhoneNumberRuleManager"""
        self._rules = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize phone number rules"""
        def replace_phone(match):
            phone = match.group(0)
            # Convert each digit to its word form
            words = []
            for digit in phone:
                if digit.isdigit():
                    words.append(self._digit_to_word(digit))
                else:
                    words.append(digit)
            return " ".join(words)
        
        # Vietnamese phone number patterns
        patterns = [
            r'\b0\d{9,10}\b',  # Mobile numbers
            r'\b0\d{2,3}-\d{7,8}\b',  # Landline with area code
            r'\b\+84\d{9,10}\b',  # International format
        ]
        
        for i, pattern in enumerate(patterns):
            self._rules.append(RegexRule(
                f"phone_{i}",
                pattern,
                replace_phone,
                priority=50
            ))
    
    def _digit_to_word(self, digit: str) -> str:
        """Convert single digit to Vietnamese word"""
        digit_words = {
            '0': 'không', '1': 'một', '2': 'hai', '3': 'ba', '4': 'bốn',
            '5': 'năm', '6': 'sáu', '7': 'bảy', '8': 'tám', '9': 'chín'
        }
        return digit_words.get(digit, digit)
    
    def apply_rules(self, text: str) -> str:
        """Apply phone number rules to text"""
        result = text
        for rule in self._rules:
            result = rule.apply(result)
        return result


class MeasurementRuleManager:
    """Manages measurement unit regex rules"""
    
    def __init__(self):
        """Initialize MeasurementRuleManager"""
        self._rules = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize measurement rules"""
        def replace_measurement(match):
            number, unit = match.groups()
            number_word = self._number_to_word(number)
            unit_word = self._unit_to_word(unit)
            return f"{number_word} {unit_word}"
        
        # Common measurement patterns
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*°C', 'độ xê'),
            (r'(\d+(?:\.\d+)?)\s*°F', 'độ ép'),
            (r'(\d+(?:\.\d+)?)\s*%', 'phần trăm'),
            (r'(\d+(?:\.\d+)?)\s*kg', 'ki lô gam'),
            (r'(\d+(?:\.\d+)?)\s*g', 'gam'),
            (r'(\d+(?:\.\d+)?)\s*km', 'ki lô mét'),
            (r'(\d+(?:\.\d+)?)\s*m', 'mét'),
            (r'(\d+(?:\.\d+)?)\s*cm', 'xen ti mét'),
            (r'(\d+(?:\.\d+)?)\s*mm', 'mi li mét'),
        ]
        
        for i, (pattern, unit_word) in enumerate(patterns):
            def make_replacer(unit):
                def replace_measurement(match):
                    number = match.group(1)
                    number_word = self._number_to_word(number)
                    return f"{number_word} {unit}"
                return replace_measurement
            
            self._rules.append(RegexRule(
                f"measurement_{i}",
                pattern,
                make_replacer(unit_word),
                priority=60
            ))
    
    def _number_to_word(self, number: str) -> str:
        """Convert number to Vietnamese word"""
        # Simple implementation - can be enhanced
        try:
            num = float(number)
            if num == int(num):
                return self._int_to_word(int(num))
            else:
                # Handle decimal
                integer_part = int(num)
                decimal_part = str(num).split('.')[1]
                return f"{self._int_to_word(integer_part)} phẩy {self._int_to_word(int(decimal_part))}"
        except:
            return number
    
    def _int_to_word(self, num: int) -> str:
        """Convert integer to Vietnamese word"""
        if num == 0:
            return "không"
        elif num < 10:
            return ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"][num]
        elif num < 20:
            return f"mười {self._int_to_word(num - 10)}"
        elif num < 100:
            tens = num // 10
            units = num % 10
            if units == 0:
                return f"{self._int_to_word(tens)} mười"
            else:
                return f"{self._int_to_word(tens)} mười {self._int_to_word(units)}"
        else:
            return str(num)  # Fallback for large numbers
    
    def _unit_to_word(self, unit: str) -> str:
        """Convert unit to Vietnamese word"""
        unit_map = {
            '°C': 'độ xê',
            '°F': 'độ ép',
            '%': 'phần trăm',
            'kg': 'ki lô gam',
            'g': 'gam',
            'km': 'ki lô mét',
            'm': 'mét',
            'cm': 'xen ti mét',
            'mm': 'mi li mét',
        }
        return unit_map.get(unit, unit)
    
    def apply_rules(self, text: str) -> str:
        """Apply measurement rules to text"""
        result = text
        for rule in self._rules:
            result = rule.apply(result)
        return result


class RegexRuleManager:
    """High-level regex rule management"""
    
    def __init__(self, number_mapper=None, regex_rule_dir=None):
        """
        Initialize RegexRuleManager
        
        Args:
            number_mapper: Number mapper instance
            regex_rule_dir: Directory containing regex rule files
        """
        self.number_mapper = number_mapper
        self.regex_rule_dir = regex_rule_dir or Path(__file__).parent / "RegexRule"
        self.date_manager = DateRuleManager(number_mapper)
        self.phone_manager = PhoneNumberRuleManager()
        self.measurement_manager = MeasurementRuleManager()
        self._custom_rules = []
        self._file_rules = []
        
        # Load comprehensive regex rules from files
        self._load_comprehensive_rules()
    
    def add_custom_rule(self, name: str, pattern: str, replacement: Callable[[re.Match], str], 
                       flags: int = 0, priority: int = 0):
        """
        Add a custom regex rule
        
        Args:
            name: Name of the rule
            pattern: Regex pattern
            replacement: Replacement function
            flags: Regex flags
            priority: Rule priority
        """
        rule = RegexRule(name, pattern, replacement, flags, priority)
        self._custom_rules.append(rule)
    
    def load_rules_from_file(self, filepath: str, priority: int = 0):
        """
        Load regex rules from file
        
        Args:
            filepath: Path to rules file
            priority: Priority for loaded rules
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Expected format: pattern|replacement_function_name
                    parts = line.split('|', 1)
                    if len(parts) != 2:
                        print(f"Warning: Invalid rule format in {filepath} line {line_num}: {line}")
                        continue
                    
                    pattern, func_name = parts
                    
                    # Create replacement function
                    def make_replacer(name):
                        def replacement(match):
                            # This is a placeholder - in practice, you'd have a registry of functions
                            return f"[{name}]"
                        return replacement
                    
                    rule = RegexRule(f"file_rule_{line_num}", pattern, make_replacer(func_name), priority=priority)
                    self._custom_rules.append(rule)
        
        except Exception as e:
            print(f"Error loading rules from {filepath}: {e}")
    
    def _load_comprehensive_rules(self):
        """Load comprehensive regex rules from RegexRule folder"""
        if not self.regex_rule_dir.exists():
            print(f"RegexRule directory not found: {self.regex_rule_dir}")
            return
        
        # Define rule priorities (higher number = higher priority)
        rule_priorities = {
            'Date_1.txt': 100,
            'Date_2.txt': 100,
            'Date_3.txt': 100,
            'Date_From_To_1.txt': 100,
            'Date_From_To_2.txt': 100,
            'PhoneNumber.txt': 90,
            'Email.txt': 80,
            'Website.txt': 80,
            'Time.txt': 70,
            'NormalNumber.txt': 60,
            'Measurement.txt': 50,
            'Measurement_1.txt': 50,
            'Month.txt': 40,
            'RomanNumber.txt': 30,
            'Street.txt': 20,
            'Office.txt': 20,
            'PoliticalDivision.txt': 20,
            'FootballOther.txt': 10,
            'FootballUnder.txt': 10,
            'Codenumber.txt': 5,
        }
        
        # Load rules from each file
        for rule_file in self.regex_rule_dir.glob("*.txt"):
            if rule_file.name in rule_priorities:
                priority = rule_priorities[rule_file.name]
                self._load_rules_from_file(rule_file, priority)
    
    def _load_rules_from_file(self, filepath: Path, priority: int = 0):
        """Load regex rules from a specific file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Test if the regex pattern is valid
                try:
                    re.compile(line, re.IGNORECASE)
                except re.error as regex_error:
                    print(f"Warning: Invalid regex pattern in {filepath.name} line {line_num}: {line}")
                    print(f"Error: {regex_error}")
                    continue
                
                # Create a simple replacement function that preserves the match
                def make_replacer():
                    def replacer(match):
                        # For now, just return the original match
                        # This can be enhanced later with specific replacement logic
                        return match.group(0)
                    return replacer
                
                rule = RegexRule(
                    f"{filepath.stem}_{line_num}",
                    line,
                    make_replacer(),
                    flags=re.IGNORECASE,
                    priority=priority
                )
                self._file_rules.append(rule)
        
        except Exception as e:
            print(f"Error loading rules from {filepath}: {e}")
    
    def apply_all_rules(self, text: str) -> str:
        """
        Apply all rules to text
        
        Args:
            text: Input text
            
        Returns:
            Text with all rules applied
        """
        result = text
        
        # Apply specialized rule managers
        result = self.date_manager.apply_rules(result)
        result = self.phone_manager.apply_rules(result)
        result = self.measurement_manager.apply_rules(result)
        
        # Apply file rules (comprehensive regex patterns)
        sorted_file_rules = sorted(self._file_rules, key=lambda r: r.priority, reverse=True)
        for rule in sorted_file_rules:
            result = rule.apply(result)
        
        # Apply custom rules
        sorted_custom_rules = sorted(self._custom_rules, key=lambda r: r.priority, reverse=True)
        for rule in sorted_custom_rules:
            result = rule.apply(result)
        
        return result
    
    def get_rule_count(self) -> int:
        """Get total number of rules"""
        return (len(self.date_manager._rules) + 
                len(self.phone_manager._rules) + 
                len(self.measurement_manager._rules) + 
                len(self._file_rules) +
                len(self._custom_rules))
    
    def list_rules(self) -> List[str]:
        """List all rule names"""
        rules = []
        rules.extend([rule.name for rule in self.date_manager._rules])
        rules.extend([rule.name for rule in self.phone_manager._rules])
        rules.extend([rule.name for rule in self.measurement_manager._rules])
        rules.extend([rule.name for rule in self._file_rules])
        rules.extend([rule.name for rule in self._custom_rules])
        return rules
