"""Tests for configuration management."""

import pytest
from pathlib import Path
import tempfile
import yaml

from jebasa.config import JebasaConfig, get_config
from jebasa.exceptions import ConfigurationError


class TestJebasaConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = JebasaConfig()
        
        # Check audio defaults
        assert config.audio.sample_rate == 16000
        assert config.audio.channels == 1
        assert config.audio.format == "wav"
        
        # Check text defaults
        assert config.text.tokenizer == "mecab"
        assert config.text.normalize_text is True
        assert config.text.extract_furigana is True
        
        # Check MFA defaults
        assert config.mfa.acoustic_model == "japanese_mfa"
        assert config.mfa.beam == 100
        assert config.mfa.retry_beam == 400
        assert config.mfa.num_jobs == 4
        
        # Check paths
        assert config.paths.input_dir == Path("input")
        assert config.paths.output_dir == Path("output")
    
    def test_config_from_file(self):
        """Test loading configuration from file."""
        config_data = {
            'audio': {
                'sample_rate': 22050,
                'channels': 2
            },
            'text': {
                'tokenizer': 'janome',
                'normalize_text': False
            },
            'mfa': {
                'beam': 150,
                'num_jobs': 8
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file = Path(f.name)
        
        try:
            config = JebasaConfig.from_file(config_file)
            
            assert config.audio.sample_rate == 22050
            assert config.audio.channels == 2
            assert config.text.tokenizer == 'janome'
            assert config.text.normalize_text is False
            assert config.mfa.beam == 150
            assert config.mfa.num_jobs == 8
            
        finally:
            config_file.unlink()
    
    def test_config_to_file(self):
        """Test saving configuration to file."""
        config = JebasaConfig()
        config.audio.sample_rate = 48000
        config.mfa.num_jobs = 16
        
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = Path(f.name)
        
        try:
            config.to_file(config_file)
            
            # Read back and verify
            loaded_config = JebasaConfig.from_file(config_file)
            assert loaded_config.audio.sample_rate == 48000
            assert loaded_config.mfa.num_jobs == 16
            
        finally:
            config_file.unlink()
    
    def test_get_config_with_overrides(self):
        """Test configuration with overrides."""
        overrides = {
            'audio': {'sample_rate': 44100},
            'mfa': {'beam': 200}
        }
        
        config = get_config(overrides=overrides)
        
        assert config.audio.sample_rate == 44100
        assert config.mfa.beam == 200
        # Other values should remain defaults
        assert config.audio.channels == 1
        assert config.mfa.retry_beam == 400
    
    def test_ensure_directories(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            config = JebasaConfig()
            config.paths.input_dir = temp_path / "test_input"
            config.paths.output_dir = temp_path / "test_output"
            
            config.ensure_directories()
            
            assert config.paths.input_dir.exists()
            assert config.paths.output_dir.exists()
    
    def test_invalid_config_file(self):
        """Test handling of invalid config file."""
        with pytest.raises(FileNotFoundError):
            JebasaConfig.from_file("nonexistent.yaml")
    
    def test_invalid_audio_config(self):
        """Test invalid audio configuration values."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            config_data = {'audio': {'sample_rate': -1000}}
            JebasaConfig(**config_data)
    
    def test_path_conversion(self):
        """Test automatic path conversion."""
        config_data = {
            'paths': {
                'input_dir': 'custom_input',
                'output_dir': 'custom_output'
            }
        }
        
        config = JebasaConfig(**config_data)
        
        assert isinstance(config.paths.input_dir, Path)
        assert isinstance(config.paths.output_dir, Path)
        assert config.paths.input_dir == Path('custom_input')
        assert config.paths.output_dir == Path('custom_output')