# Jebasa Quick Start Guide

This guide will get you up and running with Jebasa in just a few minutes!

## Installation

```bash
pip install jebasa
```

For development installation:
```bash
git clone https://github.com/yourusername/jebasa.git
cd jebasa
pip install -e .[dev]
```

## Basic Usage

### 1. Prepare Your Files

Create this directory structure:
```
your_project/
├── input/
│   ├── audio/          # Your Japanese audiobook files (MP3, M4A, etc.)
│   └── text/           # Your Japanese text files (TXT, XHTML from EPUB)
└── output/             # Where results will be saved
```

### 2. Quick Start with CLI

Run the complete pipeline:
```bash
jebasa run --input-dir ./input --output-dir ./output
```

That's it! Jebasa will:
1. Convert your audio to 16kHz mono WAV format
2. Process your Japanese text (extract furigana, normalize)
3. Create a pronunciation dictionary
4. Run Montreal Forced Aligner
5. Generate synchronized SRT subtitles

### 3. Step-by-Step Control

For more control, run each step individually:

```bash
# 1. Prepare audio
jebasa prepare-audio --input-dir ./input/audio --output-dir ./work/audio

# 2. Prepare text
jebasa prepare-text --input-dir ./input/text --output-dir ./work/text

# 3. Create pronunciation dictionary
jebasa create-dictionary --input-dir ./work/text --output-dir ./work/dictionary

# 4. Run alignment
jebasa align --corpus-dir ./work --dictionary ./work/dictionary/dict.txt --output-dir ./work/alignment

# 5. Generate subtitles
jebasa generate-subtitles --alignment-dir ./work/alignment --text-dir ./work/text --output-dir ./output
```

## Configuration

### Basic Configuration

Create a `config.yaml` file:

```yaml
audio:
  sample_rate: 16000
  
text:
  extract_furigana: true
  normalize_text: true
  
mfa:
  acoustic_model: japanese_mfa
  num_jobs: 4
  
subtitles:
  max_line_length: 42
  max_lines: 2
  min_duration: 1.0
  max_duration: 7.0
```

Use it:
```bash
jebasa run --config config.yaml --input-dir ./input --output-dir ./output
```

### Advanced Configuration

For more control, use Python:

```python
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig

config = JebasaConfig()

# Audio settings
config.audio.sample_rate = 22050
config.audio.ffmpeg_options = {"acodec": "pcm_s16le"}

# Text processing
config.text.tokenizer = "mecab"
config.text.min_chapter_length = 200

# MFA settings
config.mfa.beam = 150
config.mfa.retry_beam = 500
config.mfa.num_jobs = 8

# Subtitle settings
config.subtitles.max_line_length = 35  # Shorter for Japanese
config.subtitles.gap_filling = True

# Paths
config.paths.input_dir = "./my_book"
config.paths.output_dir = "./results"

# Run pipeline
pipeline = JebasaPipeline(config)
results = pipeline.run_all()
```

## Example with Real Data

### Sample Japanese Text

Create `input/text/chapter1.txt`:
```
第一章　冬の訪れ

冬の訪れは静かだった。街並みに雪が降り積もり、人々の足取りも重くなる。

「今年の冬は例年より寒いね」

田中さんが呟いた。彼の息は白く凍り、窓ガラスに小さな模様を描いていた。
```

### Sample Audio

Place your Japanese audiobook files in `input/audio/`:
- `chapter1.mp3`
- `chapter2.m4a`
- etc.

### Run the Pipeline

```bash
# Quick method
jebasa run --input-dir ./input --output-dir ./output

# Or with custom config
jebasa run --config my_config.yaml --input-dir ./input --output-dir ./output --verbose
```

### Results

You'll get:
- `output/subtitles/chapter1.srt` - Synchronized subtitles
- `output/subtitles/chapter1.vtt` - WebVTT format
- `output/subtitles/chapter1.txt` - Plain transcript
- `work/` directory with intermediate files

## Japanese-Specific Features

### Furigana Support

Jebasa automatically extracts furigana (ruby annotations) from your text:

```html
<ruby>漢字<rt>かんじ</rt></ruby>
```

### Text Normalization

Converts between full-width and half-width characters:
- １２３ → 123
- ａｂｃ → abc
- ア → あ (optional)

### MeCab Tokenization

Uses MeCab for accurate Japanese morphological analysis:
- 私は学生です → 私/は/学生/です
- Handles complex grammar patterns

## Troubleshooting

### Common Issues

1. **Audio format not supported**
   - Convert to MP3, M4A, WAV, or FLAC
   - Use `jebasa info audio_file.mp3` to check format

2. **Text encoding issues**
   - Ensure files are UTF-8 encoded
   - Use `file -i text_file.txt` to check encoding

3. **MFA alignment fails**
   - Check audio quality (noise, music)
   - Verify text matches audio content
   - Try different beam settings

4. **Japanese text not processing**
   - Install MeCab: `pip install mecab-python3`
   - Install unidic: `pip install unidic-lite`

### Debug Mode

Run with debug information:
```bash
jebasa run --debug --verbose --input-dir ./input --output-dir ./output
```

## Next Steps

- Check out the [examples](examples/) directory for complete workflows
- Read the [API documentation](api-reference.md) for advanced usage
- See [troubleshooting](troubleshooting.md) for common issues
- Contribute to the project on [GitHub](https://github.com/yourusername/jebasa)

## Example Files

This directory contains:
- `sample_chapter1.txt` - Sample Japanese text
- `sample_book.xhtml` - Sample XHTML with furigana
- `complete_workflow.py` - Complete Python example
- `step_by_step_example.py` - Step-by-step Python example

Run the examples:
```bash
python examples/complete_workflow.py
python examples/step_by_step_example.py
```

Happy subtitling! 🎌