# Jebasa Documentation

Welcome to the Jebasa documentation! Jebasa (Japanese ebook audio subtitle aligner) is a Python package that creates synchronized subtitles from Japanese audiobooks and EPUB files using forced alignment.

## What is Jebasa?

Jebasa addresses the unique challenges of aligning Japanese audio with text by:

- **Handling furigana annotations** - Extracts and processes ruby annotations for accurate pronunciation
- **Japanese tokenization** - Uses MeCab for proper word boundary detection
- **Text normalization** - Converts between full-width and half-width characters
- **Forced alignment** - Uses Montreal Forced Aligner for precise timing
- **Subtitle generation** - Creates properly formatted SRT files with optimal timing

## Quick Links

- [Installation Guide](installation.md) - Get started with Jebasa
- [User Guide](user-guide.md) - Learn how to use Jebasa effectively
- [API Reference](api-reference.md) - Detailed documentation of all classes and functions
- [Examples](examples.md) - Common use cases and workflows
- [Troubleshooting](troubleshooting.md) - Solutions to common problems

## Key Features

### 🎵 Audio Processing
- Convert audio files to alignment-ready format (16kHz, mono, WAV)
- Support for multiple formats: MP3, M4A, WAV, FLAC, AAC
- Audio quality validation and normalization

### 📖 Text Processing  
- Extract text from EPUB, XHTML, HTML, and plain text files
- Handle furigana (ruby) annotations for pronunciation guidance
- Japanese text normalization and tokenization
- Chapter validation and alignment

### 🗣️ Dictionary Management
- Create custom pronunciation dictionaries from furigana
- Combine with base MFA dictionaries
- Support for manual review and correction

### ⚖️ Forced Alignment
- Use Montreal Forced Aligner for precise audio-text alignment
- Optimized parameters for Japanese single-speaker audio
- Parallel processing support for faster alignment

### 📝 Subtitle Generation
- Convert alignment results to SRT format
- Intelligent sentence segmentation for Japanese
- Proportional gap-filling for unaligned segments
- Customizable subtitle formatting

## Installation

```bash
pip install jebasa
```

See the [Installation Guide](installation.md) for detailed setup instructions.

## Basic Usage

```python
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig

# Create configuration
config = JebasaConfig()
config.paths.input_dir = "./my_book"
config.paths.output_dir = "./output"

# Run complete pipeline
pipeline = JebasaPipeline(config)
results = pipeline.run_all()

print(f"Generated {len(results)} subtitle files")
```

Or use the command line:

```bash
jebasa run --input-dir ./my_book --output-dir ./output
```

## Architecture

Jebasa follows a modular architecture with five main stages:

1. **Audio Preparation** - Convert and validate audio files
2. **Text Processing** - Extract and process text with furigana support  
3. **Dictionary Creation** - Generate pronunciation dictionaries
4. **Forced Alignment** - Align audio with text using MFA
5. **Subtitle Generation** - Create final SRT files

Each stage can be run independently or as part of the complete pipeline.

## Next Steps

- Read the [Installation Guide](installation.md) to get started
- Follow the [User Guide](user-guide.md) for detailed usage instructions
- Check out [Examples](examples.md) for common workflows
- Browse the [API Reference](api-reference.md) for technical details