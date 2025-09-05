"""Dictionary creation functionality for Jebasa."""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import defaultdict

from jebasa.config import MFAConfig
from jebasa.exceptions import DictionaryError
from jebasa.utils import safe_filename

logger = logging.getLogger(__name__)


class DictionaryCreator:
    """Handle pronunciation dictionary creation for MFA."""
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.acoustic_model = config.acoustic_model
        
        # Kana to IPA mapping (simplified)
        self.kana_to_ipa = self._load_kana_ipa_mapping()
        
        # Common pronunciation exceptions
        self.pronunciation_exceptions = self._load_pronunciation_exceptions()
    
    def create_dictionary(
        self, 
        input_dir: Path, 
        output_dir: Path,
        review_file: bool = True,
        auto_approve_threshold: float = 0.9
    ) -> Dict[str, Any]:
        """Create pronunciation dictionary from processed text files."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find furigana files
        furigana_files = list(input_dir.glob("*_furigana.txt"))
        
        if not furigana_files:
            logger.warning("No furigana files found, creating basic dictionary")
            return self._create_basic_dictionary(output_dir)
        
        # Extract custom pronunciations from furigana
        custom_entries = self._extract_furigana_entries(furigana_files)
        
        # Load base MFA dictionary
        base_dict = self._load_base_dictionary()
        
        # Combine dictionaries
        combined_dict = self._combine_dictionaries(base_dict, custom_entries)
        
        # Generate review file if requested
        review_entries = []
        if review_file:
            review_entries = self._generate_review_entries(custom_entries, auto_approve_threshold)
        
        # Save dictionaries
        output_files = self._save_dictionaries(combined_dict, custom_entries, review_entries, output_dir)
        
        # Return summary
        return {
            'dictionary_file': output_files['combined'],
            'custom_dict_file': output_files['custom'],
            'review_file': output_files.get('review'),
            'total_entries': len(combined_dict),
            'custom_entries': len(custom_entries),
            'review_entries': len(review_entries),
            'auto_approved': len([e for e in review_entries if e['auto_approved']])
        }
    
    def _extract_furigana_entries(self, furigana_files: List[Path]) -> Dict[str, str]:
        """Extract pronunciation entries from furigana files."""
        custom_entries = {}
        
        for furigana_file in furigana_files:
            try:
                with open(furigana_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            base_text = parts[0].strip()
                            furigana = parts[1].strip()
                            context = parts[2].strip() if len(parts) > 2 else ""
                            
                            # Convert to IPA
                            pronunciation = self._furigana_to_ipa(furigana)
                            
                            if pronunciation:
                                custom_entries[base_text] = {
                                    'pronunciation': pronunciation,
                                    'furigana': furigana,
                                    'context': context,
                                    'confidence': self._calculate_confidence(base_text, furigana, context)
                                }
            
            except Exception as e:
                logger.warning(f"Failed to process furigana file {furigana_file}: {e}")
        
        return custom_entries
    
    def _furigana_to_ipa(self, furigana: str) -> str:
        """Convert furigana to IPA notation."""
        try:
            # Simple kana to IPA conversion
            # This is a simplified implementation
            ipa_parts = []
            
            for char in furigana:
                if char in self.kana_to_ipa:
                    ipa_parts.append(self.kana_to_ipa[char])
                else:
                    # Handle unknown characters
                    ipa_parts.append(char)
            
            return ' '.join(ipa_parts)
        
        except Exception as e:
            logger.warning(f"Failed to convert furigana '{furigana}' to IPA: {e}")
            return ""
    
    def _calculate_confidence(self, base_text: str, furigana: str, context: str) -> float:
        """Calculate confidence score for pronunciation entry."""
        confidence = 1.0
        
        # Reduce confidence for very short words
        if len(base_text) <= 1:
            confidence *= 0.8
        
        # Reduce confidence for very long furigana
        if len(furigana) > len(base_text) * 3:
            confidence *= 0.7
        
        # Check for common pronunciation patterns
        if self._is_common_pronunciation(base_text, furigana):
            confidence *= 1.2  # Boost confidence
        
        # Check against known exceptions
        if base_text in self.pronunciation_exceptions:
            expected_furigana = self.pronunciation_exceptions[base_text]
            if furigana != expected_furigana:
                confidence *= 0.5  # Significant reduction
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _is_common_pronunciation(self, base_text: str, furigana: str) -> bool:
        """Check if this is a common/expected pronunciation pattern."""
        # Common kanji readings
        common_patterns = {
            '日': ['にち', 'じつ', 'ひ', 'か'],
            '本': ['ほん', 'もと'],
            '人': ['にん', 'じん', 'ひと'],
            '月': ['がつ', 'げつ', 'つき'],
        }
        
        for char, valid_readings in common_patterns.items():
            if char in base_text and furigana in valid_readings:
                return True
        
        return False
    
    def _load_base_dictionary(self) -> Dict[str, str]:
        """Load base MFA dictionary."""
        # This would typically load the standard Japanese MFA dictionary
        # For now, return an empty dict - in practice, this would load
        # the japanese_mfa dictionary
        return {}
    
    def _combine_dictionaries(
        self, 
        base_dict: Dict[str, str], 
        custom_entries: Dict[str, Dict[str, Any]]
    ) -> Dict[str, str]:
        """Combine base and custom dictionaries."""
        combined = base_dict.copy()
        
        for word, entry in custom_entries.items():
            combined[word] = entry['pronunciation']
        
        return combined
    
    def _generate_review_entries(
        self, 
        custom_entries: Dict[str, Dict[str, Any]], 
        auto_approve_threshold: float
    ) -> List[Dict[str, Any]]:
        """Generate review entries for manual verification."""
        review_entries = []
        
        for word, entry in custom_entries.items():
            if entry['confidence'] < auto_approve_threshold:
                review_entries.append({
                    'word': word,
                    'pronunciation': entry['pronunciation'],
                    'furigana': entry['furigana'],
                    'context': entry['context'],
                    'confidence': entry['confidence'],
                    'auto_approved': False,
                    'notes': self._generate_review_notes(word, entry)
                })
            else:
                review_entries.append({
                    'word': word,
                    'pronunciation': entry['pronunciation'],
                    'furigana': entry['furigana'],
                    'context': entry['context'],
                    'confidence': entry['confidence'],
                    'auto_approved': True,
                    'notes': 'Auto-approved due to high confidence'
                })
        
        return review_entries
    
    def _generate_review_notes(self, word: str, entry: Dict[str, Any]) -> str:
        """Generate notes for manual review."""
        notes = []
        
        if entry['confidence'] < 0.5:
            notes.append("Low confidence - verify pronunciation")
        
        if len(word) > 5 and len(entry['furigana']) > len(word) * 2:
            notes.append("Unusually long furigana for word length")
        
        if word in self.pronunciation_exceptions:
            notes.append(f"Known exception - expected: {self.pronunciation_exceptions[word]}")
        
        return "; ".join(notes) if notes else "Review recommended"
    
    def _save_dictionaries(
        self, 
        combined_dict: Dict[str, str],
        custom_entries: Dict[str, Dict[str, Any]], 
        review_entries: List[Dict[str, Any]],
        output_dir: Path
    ) -> Dict[str, Path]:
        """Save all dictionary files."""
        output_files = {}
        
        # Save combined dictionary
        combined_file = output_dir / "combined_mfa_dictionary.dict"
        self._save_mfa_dictionary(combined_dict, combined_file)
        output_files['combined'] = combined_file
        
        # Save custom dictionary
        custom_dict = {word: entry['pronunciation'] for word, entry in custom_entries.items()}
        custom_file = output_dir / "custom_dictionary.dict"
        self._save_mfa_dictionary(custom_dict, custom_file)
        output_files['custom'] = custom_file
        
        # Save review file if there are entries to review
        if review_entries:
            review_file = output_dir / "dictionary_review.txt"
            self._save_review_file(review_entries, review_file)
            output_files['review'] = review_file
        
        return output_files
    
    def _save_mfa_dictionary(self, dictionary: Dict[str, str], output_file: Path) -> None:
        """Save dictionary in MFA format."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for word, pronunciation in sorted(dictionary.items()):
                    f.write(f"{word}\t{pronunciation}\n")
            
            logger.info(f"Saved MFA dictionary: {output_file}")
            
        except Exception as e:
            raise DictionaryError(f"Failed to save dictionary {output_file}: {e}")
    
    def _save_review_file(self, review_entries: List[Dict[str, Any]], output_file: Path) -> None:
        """Save review file for manual verification."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Dictionary Review File\n")
                f.write("# Please review entries marked for manual verification\n")
                f.write("# Format: WORD\tPRONUNCIATION\tFURIGANA\tCONFIDENCE\tNOTES\n\n")
                
                for entry in review_entries:
                    if not entry['auto_approved']:
                        f.write(f"{entry['word']}\t")
                        f.write(f"{entry['pronunciation']}\t")
                        f.write(f"{entry['furigana']}\t")
                        f.write(f"{entry['confidence']:.2f}\t")
                        f.write(f"{entry['notes']}\n")
            
            logger.info(f"Saved review file: {output_file}")
            
        except Exception as e:
            raise DictionaryError(f"Failed to save review file {output_file}: {e}")
    
    def _create_basic_dictionary(self, output_dir: Path) -> Dict[str, Any]:
        """Create a basic dictionary without furigana."""
        # Load base dictionary only
        base_dict = self._load_base_dictionary()
        
        output_file = output_dir / "basic_dictionary.dict"
        self._save_mfa_dictionary(base_dict, output_file)
        
        return {
            'dictionary_file': output_file,
            'custom_dict_file': None,
            'review_file': None,
            'total_entries': len(base_dict),
            'custom_entries': 0,
            'review_entries': 0,
            'auto_approved': 0
        }
    
    def _load_kana_ipa_mapping(self) -> Dict[str, str]:
        """Load kana to IPA mapping."""
        # Simplified mapping - in practice, this would be more comprehensive
        return {
            # Hiragana
            'あ': 'a', 'い': 'i', 'う': 'ɯ', 'え': 'e', 'お': 'o',
            'か': 'ka', 'き': 'ki', 'く': 'kɯ', 'け': 'ke', 'こ': 'ko',
            'さ': 'sa', 'し': 'ɕi', 'す': 'sɯ', 'せ': 'se', 'そ': 'so',
            'た': 'ta', 'ち': 'tɕi', 'つ': 'tsɯ', 'て': 'te', 'と': 'to',
            'な': 'na', 'に': 'ɲi', 'ぬ': 'nɯ', 'ね': 'ne', 'の': 'no',
            'は': 'ha', 'ひ': 'çi', 'ふ': 'ɸɯ', 'へ': 'he', 'ほ': 'ho',
            'ま': 'ma', 'み': 'mi', 'む': 'mɯ', 'め': 'me', 'も': 'mo',
            'や': 'ja', 'ゆ': 'jɯ', 'よ': 'jo',
            'ら': 'ɾa', 'り': 'ɾi', 'る': 'ɾɯ', 'れ': 'ɾe', 'ろ': 'ɾo',
            'わ': 'wa', 'を': 'o', 'ん': 'ɴ',
            
            # Katakana
            'ア': 'a', 'イ': 'i', 'ウ': 'ɯ', 'エ': 'e', 'オ': 'o',
            'カ': 'ka', 'キ': 'ki', 'ク': 'kɯ', 'ケ': 'ke', 'コ': 'ko',
            'サ': 'sa', 'シ': 'ɕi', 'ス': 'sɯ', 'セ': 'se', 'ソ': 'so',
            'タ': 'ta', 'チ': 'tɕi', 'ツ': 'tsɯ', 'テ': 'te', 'ト': 'to',
            'ナ': 'na', 'ニ': 'ɲi', 'ヌ': 'nɯ', 'ネ': 'ne', 'ノ': 'no',
            'ハ': 'ha', 'ヒ': 'çi', 'フ': 'ɸɯ', 'ヘ': 'he', 'ホ': 'ho',
            'マ': 'ma', 'ミ': 'mi', 'ム': 'mɯ', 'メ': 'me', 'モ': 'mo',
            'ヤ': 'ja', 'ユ': 'jɯ', 'ヨ': 'jo',
            'ラ': 'ɾa', 'リ': 'ɾi', 'ル': 'ɾɯ', 'レ': 'ɾe', 'ロ': 'ɾo',
            'ワ': 'wa', 'ヲ': 'o', 'ン': 'ɴ',
        }
    
    def _load_pronunciation_exceptions(self) -> Dict[str, str]:
        """Load common pronunciation exceptions."""
        return {
            '今日': 'きょう',
            '明日': 'あした',
            '昨日': 'きのう',
            '大人': 'おとな',
            '仲間': 'なかま',
        }
    
    def load_reviewed_dictionary(self, review_file: Path) -> Dict[str, str]:
        """Load manually reviewed dictionary entries."""
        reviewed_entries = {}
        
        try:
            with open(review_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        word = parts[0].strip()
                        pronunciation = parts[1].strip()
                        
                        if word and pronunciation:
                            reviewed_entries[word] = pronunciation
            
            logger.info(f"Loaded {len(reviewed_entries)} reviewed entries from {review_file}")
            return reviewed_entries
            
        except Exception as e:
            raise DictionaryError(f"Failed to load review file {review_file}: {e}")
    
    def validate_dictionary(self, dictionary_file: Path) -> Dict[str, Any]:
        """Validate dictionary file format and content."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'entry_count': 0,
            'unique_words': set(),
            'duplicate_words': set()
        }
        
        try:
            with open(dictionary_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('\t')
                    
                    if len(parts) < 2:
                        validation_results['errors'].append(f"Line {line_num}: Insufficient columns")
                        validation_results['valid'] = False
                        continue
                    
                    word = parts[0].strip()
                    pronunciation = parts[1].strip()
                    
                    if not word:
                        validation_results['errors'].append(f"Line {line_num}: Empty word")
                        validation_results['valid'] = False
                        continue
                    
                    if not pronunciation:
                        validation_results['errors'].append(f"Line {line_num}: Empty pronunciation")
                        validation_results['valid'] = False
                        continue
                    
                    # Check for duplicates
                    if word in validation_results['unique_words']:
                        validation_results['duplicate_words'].add(word)
                        validation_results['warnings'].append(f"Line {line_num}: Duplicate word '{word}'")
                    else:
                        validation_results['unique_words'].add(word)
                    
                    validation_results['entry_count'] += 1
        
        except Exception as e:
            validation_results['errors'].append(f"File error: {e}")
            validation_results['valid'] = False
        
        validation_results['unique_words'] = len(validation_results['unique_words'])
        validation_results['duplicate_words'] = len(validation_results['duplicate_words'])
        
        return validation_results