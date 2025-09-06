"""Text processing functionality for Jebasa."""

import re
import logging
import zipfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

from bs4 import BeautifulSoup, NavigableString
import fugashi

from jebasa.config import TextConfig
from jebasa.exceptions import TextProcessingError, FileFormatError
from jebasa.utils import get_text_files, get_epub_files, safe_filename

logger = logging.getLogger(__name__)


class TextProcessor:
    """Handle text file processing for alignment pipeline."""
    
    def __init__(self, config: TextConfig):
        self.config = config
        self.tokenizer = None
        self._setup_tokenizer()
    
    def _setup_tokenizer(self) -> None:
        """Set up the Japanese tokenizer."""
        try:
            if self.config.tokenizer == "mecab":
                self.tokenizer = fugashi.Tagger()
            else:
                raise TextProcessingError(f"Unsupported tokenizer: {self.config.tokenizer}")
        except Exception as e:
            raise TextProcessingError(f"Failed to initialize tokenizer: {e}")
    
    def process_text_files(
        self, 
        input_dir: Path, 
        output_dir: Path,
        progress_callback: Optional[callable] = None
    ) -> List[Tuple[Path, Dict[str, Any]]]:
        """Process all text files in input directory."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all text and EPUB files
        text_files = get_text_files(input_dir)
        epub_files = get_epub_files(input_dir)
        all_files = text_files + epub_files
        
        if not all_files:
            raise TextProcessingError(f"No text files found in {input_dir}")
        
        processed_files = []
        
        for file_path in all_files:
            try:
                result = self._process_single_file(file_path, output_dir)
                processed_files.append(result)
                
                if progress_callback:
                    progress_callback(file_path, result[0])
                
                logger.info(f"Processed text file: {file_path.name}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                raise TextProcessingError(f"Text processing failed for {file_path}: {e}")
        
        return processed_files
    
    def _process_single_file(self, input_file: Path, output_dir: Path) -> Tuple[Path, Dict[str, Any]]:
        """Process a single text file."""
        if input_file.suffix.lower() == '.epub':
            return self._process_epub_file(input_file, output_dir)
        else:
            return self._process_text_file(input_file, output_dir)
    
    def _process_epub_file(self, epub_file: Path, output_dir: Path) -> Tuple[Path, Dict[str, Any]]:
        """Process EPUB file."""
        try:
            # Extract EPUB contents
            extracted_dir = output_dir / f"{epub_file.stem}_extracted"
            extracted_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(epub_file, 'r') as zip_ref:
                zip_ref.extractall(extracted_dir)
            
            # Find XHTML files
            xhtml_files = list(extracted_dir.rglob('*.xhtml')) + list(extracted_dir.rglob('*.html'))
            
            if not xhtml_files:
                raise FileFormatError(f"No XHTML files found in EPUB: {epub_file}")
            
            # Process XHTML files
            all_text = []
            furigana_maps = []
            
            for xhtml_file in sorted(xhtml_files):
                text, furigana = self._extract_text_from_xhtml(xhtml_file)
                if text.strip():
                    all_text.append(text)
                    furigana_maps.extend(furigana)
            
            combined_text = '\n'.join(all_text)
            
            # Create output files
            base_name = safe_filename(epub_file.stem)
            
            # Clean text file (without furigana)
            clean_file = output_dir / f"{base_name}_clean.txt"
            clean_file.write_text(combined_text, encoding='utf-8')
            
            # Tokenized text file for MFA
            tokenized_file = output_dir / f"{base_name}_mfa.txt"
            tokenized_text = self._tokenize_text_for_mfa(combined_text)
            tokenized_file.write_text(tokenized_text, encoding='utf-8')
            
            # Furigana mapping file
            furigana_file = output_dir / f"{base_name}_furigana.txt"
            if furigana_maps:
                self._save_furigana_map(furigana_maps, furigana_file)
            
            info = {
                'original_file': epub_file,
                'clean_file': clean_file,
                'tokenized_file': tokenized_file,
                'furigana_file': furigana_file if furigana_maps else None,
                'furigana_found': len(furigana_maps) > 0,
                'chapter_count': len(xhtml_files),
                'text_length': len(combined_text)
            }
            
            return tokenized_file, info
            
        except Exception as e:
            raise TextProcessingError(f"Failed to process EPUB file {epub_file}: {e}")
    
    def _process_text_file(self, text_file: Path, output_dir: Path) -> Tuple[Path, Dict[str, Any]]:
        """Process plain text file."""
        try:
            text = text_file.read_text(encoding='utf-8')
            
            # Normalize text if configured
            if self.config.normalize_text:
                text = self._normalize_text(text)
            
            # Create output files
            base_name = safe_filename(text_file.stem)
            
            # Clean text file
            clean_file = output_dir / f"{base_name}_clean.txt"
            clean_file.write_text(text, encoding='utf-8')
            
            # Tokenized text file for MFA
            tokenized_file = output_dir / f"{base_name}_mfa.txt"
            tokenized_text = self._tokenize_text_for_mfa(text)
            tokenized_file.write_text(tokenized_text, encoding='utf-8')
            
            info = {
                'original_file': text_file,
                'clean_file': clean_file,
                'tokenized_file': tokenized_file,
                'furigana_found': False,
                'text_length': len(text)
            }
            
            return tokenized_file, info
            
        except Exception as e:
            raise TextProcessingError(f"Failed to process text file {text_file}: {e}")
    
    def _extract_text_from_xhtml(self, xhtml_file: Path) -> Tuple[str, List[Dict[str, str]]]:
        """Extract text and furigana from XHTML file."""
        try:
            content = xhtml_file.read_text(encoding='utf-8')
            soup = BeautifulSoup(content, 'lxml-xml')
            
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
            
            furigana_map = []
            text_parts = []
            
            # Process ruby annotations
            for ruby in soup.find_all('ruby'):
                self._process_ruby_element(ruby, furigana_map)
            
            # Extract text
            text_content = soup.get_text()
            
            # Clean up whitespace
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return text_content, furigana_map
            
        except Exception as e:
            logger.warning(f"Failed to extract text from {xhtml_file}: {e}")
            return "", []
    
    def _process_ruby_element(self, ruby_element, furigana_map: List[Dict[str, str]]) -> None:
        """Process ruby element and extract furigana."""
        try:
            # Get the base text (rb element)
            rb = ruby_element.find('rb')
            if not rb:
                return
            
            base_text = rb.get_text().strip()
            
            # Get the furigana (rt element)
            rt = ruby_element.find('rt')
            if not rt:
                return
            
            furigana = rt.get_text().strip()
            
            # Get context (surrounding text)
            context = self._get_ruby_context(ruby_element)
            
            furigana_map.append({
                'base_text': base_text,
                'furigana': furigana,
                'context': context,
                'position': len(furigana_map)
            })
            
            # Replace ruby with just the base text
            ruby_element.replace_with(base_text)
            
        except Exception as e:
            logger.warning(f"Failed to process ruby element: {e}")
    
    def _get_ruby_context(self, ruby_element, context_size: int = 20) -> str:
        """Get context around ruby element."""
        try:
            # Get parent element text
            parent_text = ruby_element.parent.get_text()
            
            # Find ruby text position
            ruby_text = ruby_element.get_text()
            pos = parent_text.find(ruby_text)
            
            if pos >= 0:
                start = max(0, pos - context_size)
                end = min(len(parent_text), pos + len(ruby_text) + context_size)
                return parent_text[start:end]
            
            return ""
            
        except Exception:
            return ""
    
    def _normalize_text(self, text: str) -> str:
        """Normalize Japanese text."""
        # Convert full-width characters to half-width
        text = self._full_width_to_half_width(text)
        
        # Normalize punctuation
        text = re.sub(r'[。！？]', '.', text)
        text = re.sub(r'[、]', ',', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _full_width_to_half_width(self, text: str) -> str:
        """Convert full-width characters to half-width."""
        result = ""
        for char in text:
            code = ord(char)
            # Full-width alphabet
            if 0xFF01 <= code <= 0xFF5E:
                result += chr(code - 0xFEE0)
            # Full-width space
            elif code == 0x3000:
                result += ' '
            else:
                result += char
        return result
    
    def _tokenize_text_for_mfa(self, text: str) -> str:
        """Tokenize text for MFA alignment."""
        if not self.tokenizer:
            raise TextProcessingError("Tokenizer not initialized")
        
        try:
            tokens = []
            for word in self.tokenizer(text):
                tokens.append(word.surface)
            
            return ' '.join(tokens)
            
        except Exception as e:
            raise TextProcessingError(f"Tokenization failed: {e}")
    
    def _save_furigana_map(self, furigana_map: List[Dict[str, str]], output_file: Path) -> None:
        """Save furigana mapping to file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for entry in furigana_map:
                    f.write(f"{entry['base_text']}\t{entry['furigana']}\t{entry['context']}\n")
        except Exception as e:
            logger.warning(f"Failed to save furigana map: {e}")
    
    def validate_chapter_alignment(self, audio_files: List[Path], text_files: List[Path]) -> Dict[str, Any]:
        """Validate that chapters align between audio and text files."""
        # Extract chapter numbers from filenames
        audio_chapters = {}
        text_chapters = {}
        
        for audio_file in audio_files:
            chapter_num = self._extract_chapter_number(audio_file.stem)
            if chapter_num is not None:
                audio_chapters[chapter_num] = audio_file
        
        for text_file in text_files:
            chapter_num = self._extract_chapter_number(text_file.stem)
            if chapter_num is not None:
                text_chapters[chapter_num] = text_file
        
        # Find matches and mismatches
        audio_chapter_nums = set(audio_chapters.keys())
        text_chapter_nums = set(text_chapters.keys())
        
        matched_chapters = audio_chapter_nums.intersection(text_chapter_nums)
        audio_only = audio_chapter_nums - text_chapter_nums
        text_only = text_chapter_nums - audio_chapter_nums
        
        return {
            'total_audio_chapters': len(audio_chapters),
            'total_text_chapters': len(text_chapters),
            'matched_chapters': len(matched_chapters),
            'audio_only_chapters': len(audio_only),
            'text_only_chapters': len(text_only),
            'missing_audio_chapters': sorted(text_only),
            'missing_text_chapters': sorted(audio_only),
            'matches': [(audio_chapters[num], text_chapters[num]) for num in sorted(matched_chapters)]
        }
    
    def _extract_chapter_number(self, filename: str) -> Optional[int]:
        """Extract chapter number from filename."""
        # Look for patterns like "chapter_01", "ch01", "01", etc.
        patterns = [
            r'ch(?:apter)?[_\s]*0*(\d+)',
            r'(?<!\d)0*(\d+)(?!\d)',
            r'第\s*0*(\d+)\s*章'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def get_text_statistics(self, text_file: Path) -> Dict[str, Any]:
        """Get statistics about a text file."""
        try:
            text = text_file.read_text(encoding='utf-8')
            
            # Basic statistics
            char_count = len(text)
            word_count = len(text.split())
            
            # Japanese-specific statistics
            japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
            
            # Tokenization
            if self.tokenizer:
                tokens = [word.surface for word in self.tokenizer(text)]
                token_count = len(tokens)
            else:
                token_count = 0
            
            return {
                'filename': text_file.name,
                'character_count': char_count,
                'word_count': word_count,
                'japanese_character_count': japanese_chars,
                'token_count': token_count,
                'estimated_duration': japanese_chars * 0.1  # Rough estimate: 0.1s per char
            }
            
        except Exception as e:
            logger.warning(f"Failed to get statistics for {text_file}: {e}")
            return {}