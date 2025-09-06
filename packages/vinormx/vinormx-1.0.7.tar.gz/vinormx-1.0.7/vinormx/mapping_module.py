"""
Mapping Module - Text Mapping and Transformation for Vietnamese Text Normalization

This module handles various types of text mappings including numbers, abbreviations,
special characters, and other transformations used in Vietnamese text normalization.
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from .dict_module import DictManager


class NumberMapper:
    """Handles number to text conversion"""
    
    def __init__(self, dict_manager: Optional[DictManager] = None):
        """
        Initialize NumberMapper
        
        Args:
            dict_manager: Dictionary manager instance
        """
        self.dict_manager = dict_manager or DictManager()
        self._number_dict = None
        self._month_dict = None
    
    def _get_number_dict(self) -> Dict[str, str]:
        """Get number dictionary"""
        if self._number_dict is None:
            self._number_dict = self.dict_manager.get_number_dict()
        return self._number_dict
    
    def _get_month_dict(self) -> Dict[str, str]:
        """Get month dictionary"""
        if self._month_dict is None:
            self._month_dict = self.dict_manager.get_month_dict()
        return self._month_dict
    
    def convert_number_to_words(self, num_str: str) -> str:
        """
        Convert number string to Vietnamese words
        
        Args:
            num_str: Number as string
            
        Returns:
            Vietnamese text representation
        """
        if not num_str.isdigit():
            return num_str
        
        num = int(num_str)
        number_dict = self._get_number_dict()
        
        if num == 0:
            return "không"
        
        if str(num) in number_dict:
            return number_dict[str(num)]
        
        return self._convert_large_number(num)
    
    def _convert_large_number(self, num: int) -> str:
        """Convert large numbers to Vietnamese words"""
        number_dict = self._get_number_dict()
        result = []
        
        # Handle millions
        if num >= 1000000:
            millions = num // 1000000
            result.append(self._convert_hundreds(millions))
            result.append("triệu")
            num %= 1000000
        
        # Handle thousands
        if num >= 1000:
            thousands = num // 1000
            result.append(self._convert_hundreds(thousands))
            result.append("nghìn")
            num %= 1000
            
            # If we have thousands but no hundreds, add "không trăm"
            if num < 100 and num > 0:
                result.append("không trăm")
        
        # Handle hundreds
        if num >= 100:
            hundreds = num // 100
            result.append(number_dict[str(hundreds)])
            result.append("trăm")
            num %= 100
        
        # Handle tens and units
        if num > 0:
            if num < 10:
                result.append(number_dict[str(num)])
            elif num < 20:
                if num == 15:
                    result.append("mười lăm")
                else:
                    result.append("mười " + number_dict[str(num % 10)])
            else:
                tens = num // 10
                units = num % 10
                result.append(number_dict[str(tens)])
                result.append("mươi")
                if units > 0:
                    if units == 5:
                        result.append("lăm")
                    else:
                        result.append(number_dict[str(units)])
        
        return " ".join(result)
    
    def _convert_hundreds(self, num: int) -> str:
        """Convert hundreds to Vietnamese words"""
        number_dict = self._get_number_dict()
        
        if num == 0:
            return ""
        if num < 10:
            return number_dict[str(num)]
        if num < 100:
            tens = num // 10
            units = num % 10
            result = number_dict[str(tens)] + " mươi"
            if units > 0:
                if units == 5:
                    result += " lăm"
                else:
                    result += " " + number_dict[str(units)]
            return result
        else:
            hundreds = num // 100
            remainder = num % 100
            result = number_dict[str(hundreds)] + " trăm"
            if remainder > 0:
                result += " " + self._convert_hundreds(remainder)
            return result
    
    def convert_year_to_words(self, year_str: str) -> str:
        """Convert year to Vietnamese words"""
        year = int(year_str)
        number_dict = self._get_number_dict()
        
        if year < 1000:
            return self.convert_number_to_words(year_str)
        
        thousands = year // 1000
        hundreds = (year % 1000) // 100
        tens = (year % 100) // 10
        units = year % 10
        
        result = []
        
        if thousands > 0:
            result.append(number_dict[str(thousands)])
            result.append("nghìn")
        
        if hundreds > 0:
            result.append(number_dict[str(hundreds)])
            result.append("trăm")
        elif year % 1000 >= 10:
            result.append("không trăm")
        
        if tens > 0:
            if tens == 1:
                result.append("mười")
            else:
                result.append(number_dict[str(tens)])
                result.append("mươi")
        elif units > 0 and (hundreds > 0 or thousands > 0):
            result.append("không")
        
        if units > 0:
            if tens == 1 and units == 5:
                result.append("lăm")
            else:
                result.append(number_dict[str(units)])
        
        return " ".join(result)
    
    def convert_month_to_words(self, month_str: str) -> str:
        """Convert month number to Vietnamese words"""
        month_dict = self._get_month_dict()
        return month_dict.get(month_str, self.convert_number_to_words(month_str))


class AbbreviationMapper:
    """Handles abbreviation expansion"""
    
    def __init__(self, dict_manager: Optional[DictManager] = None):
        """
        Initialize AbbreviationMapper
        
        Args:
            dict_manager: Dictionary manager instance
        """
        self.dict_manager = dict_manager or DictManager()
        self._abbreviation_dict = None
    
    def _get_abbreviation_dict(self) -> Dict[str, str]:
        """Get comprehensive abbreviation dictionary (includes acronyms)"""
        if self._abbreviation_dict is None:
            # Combine both abbreviation and acronyms dictionaries
            abbrev_dict = self.dict_manager.get_abbreviation_dict()
            acronyms_dict = self.dict_manager.get_acronyms_dict()
            self._abbreviation_dict = {**abbrev_dict, **acronyms_dict}
        return self._abbreviation_dict
    
    def expand_abbreviations(self, text: str) -> str:
        """
        Expand abbreviations in text
        
        Args:
            text: Input text
            
        Returns:
            Text with abbreviations expanded
        """
        abbreviation_dict = self._get_abbreviation_dict()
        
        for abbr, full in abbreviation_dict.items():
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, full, text, flags=re.IGNORECASE)
        
        return text


class SpecialCharMapper:
    """Handles special character conversion"""
    
    def __init__(self, dict_manager: Optional[DictManager] = None):
        """
        Initialize SpecialCharMapper
        
        Args:
            dict_manager: Dictionary manager instance
        """
        self.dict_manager = dict_manager or DictManager()
        self._special_chars_dict = None
    
    def _get_special_chars_dict(self) -> Dict[str, str]:
        """Get special characters dictionary"""
        if self._special_chars_dict is None:
            self._special_chars_dict = self.dict_manager.get_special_chars_dict()
        return self._special_chars_dict
    
    def convert_special_chars(self, text: str) -> str:
        """
        Convert special characters to Vietnamese words
        
        Args:
            text: Input text
            
        Returns:
            Text with special characters converted
        """
        # Handle special cases first
        text = re.sub(r'covid-19', 'covid mười chín', text, flags=re.IGNORECASE)
        
        special_chars_dict = self._get_special_chars_dict()
        
        for char, word in special_chars_dict.items():
            text = text.replace(char, f" {word} ")
        
        return text


class PunctuationMapper:
    """Maps punctuation to Vietnamese format"""
    
    def __init__(self):
        pass
    
    def normalize_punctuation(self, text: str, keep_punct: bool = False) -> str:
        """
        Normalize punctuation to Vietnamese format
        
        Args:
            text: Input text
            keep_punct: Whether to keep original punctuation
            
        Returns:
            Text with normalized punctuation
        """
        if keep_punct:
            return text
            
        # Replace punctuation with periods and commas, adding spaces
        text = re.sub(r'[.!?]+', ' .', text)
        text = re.sub(r'[,;:]+', ' ,', text)
        text = re.sub(r'[()[\]{}]+', '', text)
        text = re.sub(r'["\'""`''""]+', '', text)
        text = re.sub(r'[-–—]+', ' ', text)  # Remove dashes
        
        return text


class LetterSoundMapper:
    """Handles letter sound conversion for spelling out words"""
    
    def __init__(self, dict_manager: Optional[DictManager] = None):
        """
        Initialize LetterSoundMapper
        
        Args:
            dict_manager: Dictionary manager instance
        """
        self.dict_manager = dict_manager or DictManager()
        self._letter_sound_dict = None
    
    def _get_letter_sound_dict(self) -> Dict[str, str]:
        """Get letter sound dictionary"""
        if self._letter_sound_dict is None:
            self._letter_sound_dict = self.dict_manager.get_letter_sound_dict()
        return self._letter_sound_dict
    
    def spell_char(self, char: str) -> str:
        """
        Convert single character to its sound
        
        Args:
            char: Single character
            
        Returns:
            Sound representation of the character
        """
        letter_sound_dict = self._get_letter_sound_dict()
        return letter_sound_dict.get(char.lower(), char)
    
    def spell_word(self, word: str) -> str:
        """
        Spell out a word character by character
        
        Args:
            word: Word to spell out
            
        Returns:
            Spelled out word
        """
        return " ".join([self.spell_char(c) for c in word.lower()])
    
    def is_consonant_only(self, word: str) -> bool:
        """
        Check if word contains only consonants
        
        Args:
            word: Word to check
            
        Returns:
            True if word contains only consonants
        """
        vowels = 'aeiouy'  # Include 'y' as a vowel in Vietnamese
        return not any(c.lower() in vowels for c in word)


class MappingManager:
    """High-level mapping management"""
    
    def __init__(self, dict_manager: Optional[DictManager] = None):
        """
        Initialize MappingManager
        
        Args:
            dict_manager: Dictionary manager instance
        """
        self.dict_manager = dict_manager or DictManager()
        self.number_mapper = NumberMapper(self.dict_manager)
        self.abbreviation_mapper = AbbreviationMapper(self.dict_manager)
        self.special_char_mapper = SpecialCharMapper(self.dict_manager)
        self.letter_sound_mapper = LetterSoundMapper(self.dict_manager)
        self.punctuation_mapper = PunctuationMapper()
    
    def normalize_text(self, text: str, 
                      convert_numbers: bool = True,
                      expand_abbreviations: bool = True,
                      convert_special_chars: bool = True,
                      spell_unknown_words: bool = True) -> str:
        """
        Normalize text using all available mappings
        
        Args:
            text: Input text
            convert_numbers: Whether to convert numbers to words
            expand_abbreviations: Whether to expand abbreviations
            convert_special_chars: Whether to convert special characters
            spell_unknown_words: Whether to spell out unknown words
            
        Returns:
            Normalized text
        """
        result = text
        
        if convert_special_chars:
            result = self.special_char_mapper.convert_special_chars(result)
        
        if expand_abbreviations:
            result = self.abbreviation_mapper.expand_abbreviations(result)
        
        if convert_numbers:
            result = self._convert_numbers_in_text(result)
        
        if spell_unknown_words:
            result = self._spell_unknown_words(result)
        
        # Normalize punctuation (always apply this step)
        result = self.punctuation_mapper.normalize_punctuation(result, keep_punct=False)
        
        return result
    
    def _convert_numbers_in_text(self, text: str) -> str:
        """Convert numbers in text to words"""
        # Handle decimal numbers
        decimal_pattern = r'\b(\d+)[,.](\d+)\b'
        
        def replace_decimal(match):
            integer_part = match.group(1)
            decimal_part = match.group(2)
            
            integer_word = self.number_mapper.convert_number_to_words(integer_part)
            decimal_word = " ".join([self.number_mapper.convert_number_to_words(d) for d in decimal_part])
            
            return f"{integer_word} phẩy {decimal_word}"
        
        text = re.sub(decimal_pattern, replace_decimal, text)
        
        # Handle whole numbers, but exclude date patterns
        # Exclude numbers that are part of date patterns (dd/mm/yyyy or mm/yyyy)
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2}/\d{4}\b'
        
        # Find all date patterns and protect them
        date_matches = list(re.finditer(date_pattern, text))
        protected_text = text
        replacements = {}
        
        for i, match in enumerate(date_matches):
            placeholder = f"__DATE_PLACEHOLDER_{i}__"
            replacements[placeholder] = match.group(0)
            protected_text = protected_text.replace(match.group(0), placeholder, 1)
        
        # Convert remaining numbers
        number_pattern = r'\b\d+\b'
        
        def replace_number(match):
            return self.number_mapper.convert_number_to_words(match.group(0))
        
        protected_text = re.sub(number_pattern, replace_number, protected_text)
        
        # Restore date patterns
        for placeholder, original in replacements.items():
            protected_text = protected_text.replace(placeholder, original)
        
        return protected_text
    
    def _spell_unknown_words(self, text: str) -> str:
        """Spell out unknown words"""
        words = text.split()
        result = []
        
        for word in words:
            if self._has_vietnamese_chars(word):
                result.append(word)
            elif word.isalpha() and self.letter_sound_mapper.is_consonant_only(word):
                spelled = self.letter_sound_mapper.spell_word(word)
                result.append(spelled)
            else:
                result.append(word)
        
        return " ".join(result)
    
    def _has_vietnamese_chars(self, text: str) -> bool:
        """Check if text contains Vietnamese characters"""
        vietnamese_chars = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
        vietnamese_chars += vietnamese_chars.upper()
        
        return any(c in vietnamese_chars for c in text)
