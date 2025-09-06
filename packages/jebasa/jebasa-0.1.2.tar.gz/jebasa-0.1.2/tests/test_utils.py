"""Tests for utility functions."""

import pytest
from pathlib import Path
import tempfile

from jebasa.utils import (
    normalize_filename, get_audio_files, get_text_files, 
    format_duration, parse_duration, safe_filename, chunk_text,
    validate_audio_file, validate_text_file, find_matching_files
)


class TestUtils:
    """Test utility functions."""
    
    def test_normalize_filename(self):
        """Test filename normalization."""
        assert normalize_filename("テスト・ファイル.mp3") == "テスト_ファイル"
        assert normalize_filename("test file!.wav") == "test_file"
        assert normalize_filename("chapter_01") == "chapter_01"
        assert normalize_filename("01_test") == "01_test"
    
    def test_format_duration(self):
        """Test duration formatting."""
        assert format_duration(3661.5) == "01:01:01.500"
        assert format_duration(125.25) == "02:05.250"
        assert format_duration(45.123) == "00:45.123"
    
    def test_parse_duration(self):
        """Test duration parsing."""
        assert parse_duration("01:01:01.500") == 3661.5
        assert parse_duration("02:05.250") == 125.25
        assert parse_duration("45.123") == 45.123
    
    def test_safe_filename(self):
        """Test safe filename generation."""
        assert safe_filename("test file!@#") == "test_file"
        assert safe_filename("日本語ファイル") == "日本語ファイル"
        assert safe_filename("file   with   spaces") == "file_with_spaces"
    
    def test_chunk_text(self):
        """Test text chunking for subtitles."""
        # Short text
        assert chunk_text("Short text") == ["Short text"]
        
        # Long text that needs splitting
        long_text = "This is a very long text that needs to be split into multiple lines for subtitle display"
        chunks = chunk_text(long_text, max_length=20, max_lines=2)
        assert len(chunks) <= 2
        assert all(len(chunk) <= 20 for chunk in chunks)
    
    def test_validate_audio_file(self):
        """Test audio file validation."""
        assert validate_audio_file(Path("test.mp3")) is True
        assert validate_audio_file(Path("test.wav")) is True
        assert validate_audio_file(Path("test.m4a")) is True
        assert validate_audio_file(Path("test.txt")) is False
        assert validate_audio_file(Path("test")) is False
    
    def test_validate_text_file(self):
        """Test text file validation."""
        assert validate_text_file(Path("test.txt")) is True
        assert validate_text_file(Path("test.html")) is True
        assert validate_text_file(Path("test.xhtml")) is True
        assert validate_text_file(Path("test.epub")) is True
        assert validate_text_file(Path("test.mp3")) is False
    
    def test_get_audio_files(self):
        """Test audio file discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test audio files
            (temp_path / "test1.mp3").touch()
            (temp_path / "test2.wav").touch()
            (temp_path / "test3.m4a").touch()
            (temp_path / "readme.txt").touch()  # Should be ignored
            
            audio_files = get_audio_files(temp_path)
            
            assert len(audio_files) == 3
            assert all(f.suffix in ['.mp3', '.wav', '.m4a'] for f in audio_files)
    
    def test_get_text_files(self):
        """Test text file discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test text files
            (temp_path / "test1.txt").touch()
            (temp_path / "test2.html").touch()
            (temp_path / "test3.xhtml").touch()
            (temp_path / "audio.mp3").touch()  # Should be ignored
            
            text_files = get_text_files(temp_path)
            
            assert len(text_files) == 3
            assert all(f.suffix in ['.txt', '.html', '.xhtml'] for f in text_files)
    
    def test_find_matching_files(self):
        """Test finding matching audio and text files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create matching files
            (temp_path / "chapter_01.mp3").touch()
            (temp_path / "chapter_01.txt").touch()
            (temp_path / "chapter_02.mp3").touch()
            (temp_path / "chapter_02.txt").touch()
            (temp_path / "chapter_03.mp3").touch()  # No matching text
            (temp_path / "chapter_04.txt").touch()  # No matching audio
            
            audio_files = get_audio_files(temp_path)
            text_files = get_text_files(temp_path)
            
            matches = find_matching_files(audio_files, text_files)
            
            assert len(matches) == 2  # chapter_01 and chapter_02
            assert 'chapter_01' in matches
            assert 'chapter_02' in matches
            assert 'chapter_03' not in matches
            assert 'chapter_04' not in matches
    
    def test_full_width_to_half_width(self):
        """Test full-width to half-width character conversion."""
        # This would be tested if the function was exposed
        # For now, it's an internal implementation detail
        pass