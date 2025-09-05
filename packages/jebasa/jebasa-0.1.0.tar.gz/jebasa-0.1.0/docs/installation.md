# Installation Guide

This guide will walk you through installing Jebasa and its dependencies.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 8GB+ RAM recommended for alignment
- **Storage**: 2GB+ free space for models and temporary files

## Installation Steps

### Step 1: Install Python

Make sure you have Python 3.8+ installed:

```bash
python --version
# Should show Python 3.8.x or higher
```

If you need to install Python, download it from [python.org](https://www.python.org/downloads/).

### Step 2: Install System Dependencies

#### FFmpeg (Required for Audio Processing)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

#### MeCab (Required for Japanese Tokenization)

**Ubuntu/Debian:**
```bash
sudo apt install mecab mecab-ipadic-utf8 libmecab-dev
```

**macOS:**
```bash
brew install mecab mecab-ipadic
```

**Windows:**
Download and install from [MeCab website](https://taku910.github.io/mecab/).

### Step 3: Install Jebasa

#### From PyPI (Recommended)

```bash
pip install jebasa
```

#### From Source

```bash
git clone https://github.com/yourusername/jebasa.git
cd jebasa
pip install -e .
```

#### Development Installation

For development work:

```bash
git clone https://github.com/yourusername/jebasa.git
cd jebasa
pip install -e .[dev]
```

### Step 4: Install Montreal Forced Aligner

Jebasa uses Montreal Forced Aligner (MFA) for audio-text alignment:

```bash
pip install montreal-forced-aligner
```

### Step 5: Download Japanese Models

Download the required Japanese models for MFA:

```bash
# Download acoustic model
mfa model download acoustic japanese_mfa

# Download Japanese dictionary (optional, Jebasa creates custom ones)
mfa model download dictionary japanese_mfa
```

### Step 6: Verify Installation

Test your installation:

```bash
jebasa --version
jebasa --help

# Test with sample files (if available)
jebasa info sample_audio.mp3
```

## Virtual Environment (Recommended)

Using a virtual environment is recommended to avoid conflicts:

```bash
# Create virtual environment
python -m venv jebasa_env

# Activate it
source jebasa_env/bin/activate  # Linux/macOS
# or
jebasa_env\Scripts\activate  # Windows

# Install Jebasa
pip install jebasa
```

## Docker Installation (Alternative)

For a containerized setup:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install jebasa montreal-forced-aligner

WORKDIR /app

CMD ["jebasa", "--help"]
```

Build and run:

```bash
docker build -t jebasa .
docker run -it --rm -v $(pwd):/app jebasa
```

## Troubleshooting Installation

### FFmpeg Not Found

```
Error: FFmpeg not found. Please install FFmpeg.
```

**Solution:** Ensure FFmpeg is installed and in your PATH:

```bash
ffmpeg -version
```

### MeCab Import Error

```
ImportError: Cannot find MeCab
```

**Solution:** Install MeCab and verify installation:

```bash
python -c "import fugashi; print(fugashi.Tagger().parse('テスト'))"
```

### MFA Model Download Fails

```
Error: Failed to download model
```

**Solution:** Download models manually:

```bash
# Check available models
mfa model download acoustic --help

# Download specific model
mfa model download acoustic japanese_mfa
```

### Permission Errors

```
PermissionError: [Errno 13] Permission denied
```

**Solution:** Use virtual environment or install with user flag:

```bash
pip install --user jebasa
```

### Memory Issues

```
MemoryError: Unable to allocate array
```

**Solution:** Ensure sufficient RAM (8GB+ recommended) and close other applications.

## Next Steps

- Read the [User Guide](user-guide.md) to learn how to use Jebasa
- Check out [Examples](examples.md) for common workflows
- See [Configuration](configuration.md) for advanced setup options

## Getting Help

If you encounter installation issues:

1. Check the [Troubleshooting](troubleshooting.md) guide
2. Search [existing issues](https://github.com/yourusername/jebasa/issues)
3. Create a new issue with:
   - Your operating system and version
   - Python version
   - Complete error message
   - Installation method used