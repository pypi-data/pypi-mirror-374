# Jebasa (Japanese ebook audio subtitle aligner)

[![PyPI version](https://badge.fury.io/py/jebasa.svg)](https://badge.fury.io/py/jebasa)
[![Python Support](https://img.shields.io/pypi/pyversions/jebasa.svg)](https://pypi.org/project/jebasa/)
[![Tests](https://github.com/OCboy5/jebasa/workflows/CI/badge.svg)](https://github.com/OCboy5/jebasa/actions)
[![codecov](https://codecov.io/gh/yourusername/jebasa/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/jebasa)

**Jebasa** is a Python package that creates synchronized subtitles from Japanese audiobooks and EPUB files using forced alignment. It handles Japanese-specific challenges like furigana annotations and morphological analysis to produce high-quality subtitle files.

## Features

- 🎵 **Audio Processing**: Convert and prepare audio files for alignment
- 📖 **Text Extraction**: Process EPUB and text files with furigana support
- 🗣️ **Dictionary Creation**: Generate custom pronunciation dictionaries
- ⚖️ **Forced Alignment**: Use Montreal Forced Aligner for precise timing
- 📝 **Subtitle Generation**: Create properly timed SRT files
- 🔄 **Complete Pipeline**: Run all stages automatically or individually
- 🇯🇵 **Japanese Optimized**: Handles furigana, tokenization, and text normalization

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- Montreal Forced Aligner (for alignment)

### Install Jebasa

```bash
pip install jebasa
```

### Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
pip install montreal-forced-aligner
mfa model download acoustic japanese_mfa
```

#### macOS
```bash
brew install ffmpeg
pip install montreal-forced-aligner
mfa model download acoustic japanese_mfa
```

#### Windows
```bash
choco install ffmpeg
pip install montreal-forced-aligner
mfa model download acoustic japanese_mfa
```

## Quick Start

### Basic Usage

```bash
# Run complete pipeline
jebasa run --input-dir ./my_book --output-dir ./output

# Or run individual stages
jebasa prepare-audio --input-dir ./my_book/audio --output-dir ./processed
jebasa prepare-text --input-dir ./my_book/text --output-dir ./processed
jebasa create-dictionary --input-dir ./processed --output-dir ./dictionaries
jebasa align --corpus-dir ./processed --dictionary ./dictionaries/custom.dict --output-dir ./aligned
jebasa generate-subtitles --alignment-dir ./aligned --text-dir ./processed --output-dir ./subtitles
```

### Python API

```python
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig

# Create configuration
config = JebasaConfig()
config.paths.input_dir = "./my_book"
config.paths.output_dir = "./output"

# Run pipeline
pipeline = JebasaPipeline(config)
results = pipeline.run_all()

print(f"Generated {len(results)} subtitle files")
```

## Input Requirements

### Audio Files
- Formats: MP3, M4A, WAV, FLAC, AAC
- Will be converted to 16kHz mono WAV for alignment
- Quality: Clear speech with minimal background noise

### Text Files
- Formats: EPUB, XHTML, HTML, TXT
- Japanese text with optional furigana (ruby) annotations
- Should correspond to audio content

## Configuration

Jebasa can be configured via command-line options, configuration files, or environment variables.

### Configuration File

Create a `jebasa.yaml` file:

```yaml
audio:
  sample_rate: 16000
  channels: 1
  format: wav

text:
  tokenizer: mecab
  normalize_text: true
  extract_furigana: true

mfa:
  acoustic_model: japanese_mfa
  beam: 100
  retry_beam: 400
  num_jobs: 4

subtitles:
  max_line_length: 42
  max_lines: 2
  min_duration: 1.0
  max_duration: 7.0

paths:
  input_dir: ./input
  output_dir: ./output
  temp_dir: ./temp
```

### Command Line Options

```bash
jebasa run --help
jebasa prepare-audio --help
jebasa prepare-text --help
jebasa create-dictionary --help
jebasa align --help
jebasa generate-subtitles --help
```

## Examples

### Example 1: Basic Audiobook Processing

```bash
# Organize your files
mkdir my_book/{audio,text}
cp audiobook.mp3 my_book/audio/
cp book.epub my_book/text/

# Run complete pipeline
jebasa run --input-dir ./my_book --output-dir ./output

# Find your subtitles
ls output/srt/
```

### Example 2: Custom Quality Settings

```bash
# High-quality alignment with more beam search
jebasa align \
  --corpus-dir ./processed \
  --dictionary ./dictionaries/custom.dict \
  --output-dir ./aligned \
  --beam 200 \
  --retry-beam 600 \
  --num-jobs 8
```

### Example 3: Processing with Configuration File

```bash
# Create configuration file
cat > jebasa.yaml << EOF
audio:
  sample_rate: 22050
  ffmpeg_options:
    acodec: pcm_s16le

text:
  min_chapter_length: 500

mfa:
  num_jobs: 8
  beam: 150
EOF

# Use configuration file
jebasa run --config jebasa.yaml --input-dir ./my_book
```

## Advanced Usage

### Custom Audio Processing

```python
from jebasa.audio import AudioProcessor
from jebasa.config import AudioConfig

config = AudioConfig(
    sample_rate=22050,
    channels=1,
    format="wav",
    ffmpeg_options={"acodec": "pcm_s16le"}
)

processor = AudioProcessor(config)
processed_files = processor.process_audio_files(
    input_dir="./audio",
    output_dir="./processed"
)
```

### Custom Text Processing

```python
from jebasa.text import TextProcessor
from jebasa.config import TextConfig

config = TextConfig(
    tokenizer="mecab",
    normalize_text=True,
    extract_furigana=True
)

processor = TextProcessor(config)
processed_files = processor.process_text_files(
    input_dir="./text",
    output_dir="./processed"
)
```

### Pipeline Stages

```python
from jebasa.pipeline import JebasaPipeline
from jebasa.config import JebasaConfig

config = JebasaConfig()
pipeline = JebasaPipeline(config)

# Run individual stages
audio_files = pipeline.prepare_audio()
text_files = pipeline.prepare_text()
dictionary = pipeline.create_dictionary()
alignments = pipeline.run_alignment()
subtitles = pipeline.generate_subtitles()
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```
   Error: FFmpeg not found. Please install FFmpeg.
   ```
   Solution: Install FFmpeg using your system's package manager.

2. **MFA model not found**
   ```
   Error: Acoustic model 'japanese_mfa' not found
   ```
   Solution: Download the model with `mfa model download acoustic japanese_mfa`

3. **Poor alignment quality**
   - Check audio quality (clear speech, minimal noise)
   - Verify text matches audio content
   - Try adjusting beam search parameters
   - Check pronunciation dictionary coverage

4. **Memory issues during alignment**
   - Reduce `--num-jobs` parameter
   - Process files in smaller batches
   - Ensure sufficient RAM (8GB+ recommended)

### Getting Help

- Check the [documentation](https://jebasa.readthedocs.io)
- Report issues on [GitHub](https://github.com/OCboy5/jebasa/issues)
- Join our [discussion forum](https://github.com/OCboy5/jebasa/discussions)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/) for alignment
- [fugashi](https://github.com/polm/fugashi) for Japanese tokenization
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML/XML parsing

## Citation

If you use Jebasa in your research, please cite:

```bibtex
@software{jebasa,
  title={Jebasa: Japanese ebook audio subtitle aligner},
  author={Your Name},
  year={2024},
  url={https://github.com/OCboy5/jebasa}
}
```
