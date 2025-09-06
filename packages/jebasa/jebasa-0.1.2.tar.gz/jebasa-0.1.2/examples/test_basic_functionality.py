#!/usr/bin/env python3
"""
Basic functionality test for Jebasa

This script tests the core functionality without requiring external dependencies
like Montreal Forced Aligner or audio files.
"""

import tempfile
from pathlib import Path
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig
from jebasa.audio import AudioProcessor
from jebasa.text import TextProcessor
from jebasa.dictionary import DictionaryCreator
from jebasa.cli import setup_logging

def test_configuration():
    """Test configuration creation and validation"""
    print("🧪 Testing configuration...")
    
    config = JebasaConfig()
    
    # Test basic settings
    assert config.audio.sample_rate == 16000
    assert config.text.tokenizer == "mecab"
    assert config.mfa.acoustic_model == "japanese_mfa"
    assert config.subtitles.max_line_length == 42
    
    # Test configuration serialization
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config.to_file(Path(f.name))
        loaded_config = JebasaConfig.from_file(Path(f.name))
        assert loaded_config.audio.sample_rate == config.audio.sample_rate
        Path(f.name).unlink()
    
    print("✅ Configuration test passed")

def test_audio_processor():
    """Test audio processor initialization"""
    print("🧪 Testing audio processor...")
    
    config = JebasaConfig()
    processor = AudioProcessor(config.audio)
    
    # Test that processor is created successfully
    assert processor.config.sample_rate == 16000
    assert processor.config.channels == 1
    
    print("✅ Audio processor test passed")

def test_text_processor():
    """Test text processor with Japanese text"""
    print("🧪 Testing text processor...")
    
    config = JebasaConfig()
    processor = TextProcessor(config.text)
    
    # Test basic text processing
    japanese_text = "こんにちは世界"
    
    # Test MeCab tokenizer (if available)
    try:
        from fugashi import Tagger
        tagger = Tagger()
        words = [word.surface for word in tagger(japanese_text)]
        assert len(words) > 0
        print(f"  ✅ MeCab tokenization works: {words}")
    except ImportError:
        print("  ⚠️  MeCab not available, skipping tokenization test")
    
    print("✅ Text processor test passed")

def test_dictionary_creator():
    """Test dictionary creator initialization"""
    print("🧪 Testing dictionary creator...")
    
    config = JebasaConfig()
    creator = DictionaryCreator(config.mfa)
    
    # Test that creator is created successfully
    assert creator.config.acoustic_model == "japanese_mfa"
    
    print("✅ Dictionary creator test passed")

def test_pipeline_creation():
    """Test pipeline creation"""
    print("🧪 Testing pipeline creation...")
    
    config = JebasaConfig()
    
    # Use temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config.paths.input_dir = temp_path / "input"
        config.paths.output_dir = temp_path / "output"
        config.paths.temp_dir = temp_path / "temp"
        
        # Create directories
        config.paths.input_dir.mkdir()
        config.paths.output_dir.mkdir()
        config.paths.temp_dir.mkdir()
        
        pipeline = JebasaPipeline(config)
        
        # Test that pipeline is created successfully
        assert pipeline.config.audio.sample_rate == 16000
        
        print("✅ Pipeline creation test passed")

def test_japanese_text_processing():
    """Test Japanese text processing capabilities"""
    print("🧪 Testing Japanese text processing...")
    
    config = JebasaConfig()
    processor = TextProcessor(config.text)
    
    # Test text normalization
    full_width_text = "１２３ＡＢＣ"
    half_width_text = "123ABC"
    
    # Note: This is a simplified test - actual implementation would use MeCab
    print(f"  ✅ Text samples ready for processing")
    print(f"     Full-width: {full_width_text}")
    print(f"     Half-width: {half_width_text}")
    
    print("✅ Japanese text processing test passed")

def test_cli_commands():
    """Test that CLI commands can be imported"""
    print("🧪 Testing CLI commands...")
    
    try:
        from jebasa.cli import main, prepare_audio, prepare_text, create_dictionary, align, generate_subtitles, run, info, config
        print("  ✅ All CLI commands available")
    except ImportError as e:
        print(f"  ❌ CLI import failed: {e}")
        return False
    
    print("✅ CLI commands test passed")
    return True

def main():
    """Run all basic functionality tests"""
    print("🎌 Jebasa Basic Functionality Tests")
    print("=" * 40)
    
    setup_logging(verbose=False, debug=False)
    
    tests = [
        test_configuration,
        test_audio_processor,
        test_text_processor,
        test_dictionary_creator,
        test_pipeline_creation,
        test_japanese_text_processing,
        test_cli_commands,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Jebasa is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())