# Examples and Tutorials

This page provides practical examples and tutorials for using Jebasa effectively.

## Basic Examples

### Example 1: Simple Audiobook Processing

Process a complete Japanese audiobook with EPUB text:

```bash
# Create project structure
mkdir my_book/{audio,text,output}
cp audiobook.mp3 my_book/audio/
cp book.epub my_book/text/

# Run complete pipeline
jebasa run --input-dir ./my_book --output-dir ./my_book/output

# Check results
ls my_book/output/srt/
```

### Example 2: Step-by-Step Processing

Run each pipeline stage individually for more control:

```bash
# 1. Prepare audio files
jebasa prepare-audio \
  --input-dir ./my_book/audio \
  --output-dir ./my_book/processed/audio

# 2. Prepare text files  
jebasa prepare-text \
  --input-dir ./my_book/text \
  --output-dir ./my_book/processed/text

# 3. Create pronunciation dictionary
jebasa create-dictionary \
  --input-dir ./my_book/processed/text \
  --output-dir ./my_book/dictionaries

# 4. Run alignment
jebasa align \
  --corpus-dir ./my_book/processed \
  --dictionary ./my_book/dictionaries/combined.dict \
  --output-dir ./my_book/aligned

# 5. Generate subtitles
jebasa generate-subtitles \
  --alignment-dir ./my_book/aligned \
  --text-dir ./my_book/processed/text \
  --output-dir ./my_book/output/srt
```

### Example 3: Multiple Audio Files

Handle audiobooks split into multiple files:

```bash
# Audio files: chapter_01.mp3, chapter_02.mp3, etc.
# Text files: chapter_01.txt, chapter_02.txt, etc.

jebasa run --input-dir ./multi_chapter_book --output-dir ./output

# Jebasa will automatically match chapters by filename
```

## Advanced Examples

### Example 4: Custom Configuration

Use a configuration file for complex settings:

```yaml
# config.yaml
audio:
  sample_rate: 22050
  channels: 1
  format: wav
  ffmpeg_options:
    acodec: pcm_s16le

text:
  tokenizer: mecab
  normalize_text: true
  extract_furigana: true
  min_chapter_length: 500

mfa:
  acoustic_model: japanese_mfa
  beam: 150
  retry_beam: 600
  num_jobs: 8
  single_speaker: true
  textgrid_cleanup: true

subtitles:
  max_line_length: 35
  max_lines: 2
  min_duration: 0.8
  max_duration: 6.0
  gap_filling: true

paths:
  input_dir: ./input
  output_dir: ./output
  temp_dir: ./temp
```

Use the configuration:

```bash
jebasa run --config config.yaml --input-dir ./my_book
```

### Example 5: Python API Usage

```python
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig
from jebasa.audio import AudioProcessor
from jebasa.text import TextProcessor

# Method 1: Complete pipeline
config = JebasaConfig()
config.paths.input_dir = "./my_book"
config.paths.output_dir = "./output"
config.mfa.num_jobs = 8

pipeline = JebasaPipeline(config)
results = pipeline.run_all()

print(f"Generated {len(results)} subtitle files")

# Method 2: Individual components
audio_processor = AudioProcessor(config.audio)
audio_files = audio_processor.process_audio_files(
    input_dir="./my_book/audio",
    output_dir="./processed/audio"
)

text_processor = TextProcessor(config.text)
text_files = text_processor.process_text_files(
    input_dir="./my_book/text", 
    output_dir="./processed/text"
)
```

### Example 6: Audio Quality Check

Validate audio files before processing:

```bash
# Check individual file
jebasa info ./my_book/audio/chapter_01.mp3

# Check all audio files in directory
for file in ./my_book/audio/*.mp3; do
    echo "Checking: $file"
    jebasa info "$file"
done
```

### Example 7: Custom Audio Processing

```python
from jebasa.audio import AudioProcessor
from jebasa.config import AudioConfig

# Custom audio configuration
config = AudioConfig(
    sample_rate=22050,  # Higher quality
    channels=1,
    format="wav",
    ffmpeg_options={
        "acodec": "pcm_s16le",
        "ar": "22050",
        "ac": "1"
    }
)

processor = AudioProcessor(config)

# Process with custom settings
processed_files = processor.process_audio_files(
    input_dir="./high_quality_audio",
    output_dir="./processed_hq"
)

# Merge multiple audio files
files_to_merge = [
    Path("./part1.mp3"),
    Path("./part2.mp3"),
    Path("./part3.mp3")
]

merged_file = processor.merge_audio_files(
    files=files_to_merge,
    output_file=Path("./merged.mp3"),
    crossfade=1000  # 1 second crossfade
)
```

### Example 8: Text Processing with Furigana

```python
from jebasa.text import TextProcessor
from jebasa.config import TextConfig

config = TextConfig(
    tokenizer="mecab",
    normalize_text=True,
    extract_furigana=True,
    min_chapter_length=100
)

processor = TextProcessor(config)

# Process EPUB with furigana
results = processor.process_text_files(
    input_dir="./epub_files",
    output_dir="./processed_text"
)

# Check furigana extraction
for tokenized_file, info in results:
    if info['furigana_found']:
        print(f"Found furigana in {info['original_file']}")
        print(f"Chapters: {info['chapter_count']}")
        print(f"Text length: {info['text_length']} characters")
```

### Example 9: Batch Processing Multiple Books

```bash
#!/bin/bash
# batch_process.sh

BOOKS_DIR="./books"
OUTPUT_BASE="./output"

for book_dir in "$BOOKS_DIR"/*/; do
    book_name=$(basename "$book_dir")
    echo "Processing: $book_name"
    
    jebasa run \
        --input-dir "$book_dir" \
        --output-dir "$OUTPUT_BASE/$book_name" \
        --verbose
    
    echo "Completed: $book_name"
    echo "---"
done
```

### Example 10: Error Handling and Logging

```python
import logging
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig
from jebasa.exceptions import JebasaError

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_book(book_dir, output_dir):
    try:
        config = JebasaConfig()
        config.paths.input_dir = book_dir
        config.paths.output_dir = output_dir
        config.verbose = True
        
        pipeline = JebasaPipeline(config)
        
        # Run with error handling
        results = pipeline.run_all()
        
        logger.info(f"Successfully processed {book_dir}")
        return results
        
    except JebasaError as e:
        logger.error(f"Jebasa processing failed: {e}")
        # Handle specific errors
        if "AudioProcessingError" in str(e):
            logger.error("Check audio file format and quality")
        elif "TextProcessingError" in str(e):
            logger.error("Check text file encoding and format")
        elif "AlignmentError" in str(e):
            logger.error("Check MFA installation and models")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

# Use the function
try:
    results = process_book("./my_book", "./output")
    print(f"Generated {len(results)} files")
except JebasaError as e:
    print(f"Processing failed: {e}")
```

## Tutorial: Creating a Complete Audiobook Subtitle Project

### Step 1: Project Setup

```bash
# Create project structure
mkdir japanese_audiobook_project
cd japanese_audiobook_project
mkdir -p {input/{audio,text},output,configs,logs}
```

### Step 2: Organize Your Files

```
input/
├── audio/
│   ├── chapter_01.mp3
│   ├── chapter_02.mp3
│   └── chapter_03.mp3
└── text/
    └── novel.epub
```

### Step 3: Create Configuration

```yaml
# configs/project.yaml
audio:
  sample_rate: 16000
  channels: 1
  format: wav

text:
  tokenizer: mecab
  normalize_text: true
  extract_furigana: true
  min_chapter_length: 200

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

### Step 4: Process with Logging

```bash
# Run with verbose logging
jebasa run \
  --config configs/project.yaml \
  --verbose \
  2>> logs/processing.log

# Monitor progress
tail -f logs/processing.log
```

### Step 5: Quality Check

```bash
# Check generated subtitles
jebasa info output/srt/chapter_01.srt

# Validate alignment quality
python validate_alignment.py output/aligned/
```

### Step 6: Final Review

```bash
# List all generated files
find output -type f -name "*.srt" | sort

# Check subtitle timing
head -20 output/srt/chapter_01.srt
```

## Performance Tips

### For Large Files

```python
# Process in batches
from jebasa.pipeline import JebasaPipeline

config = JebasaConfig()
config.mfa.num_jobs = 8  # Use more CPU cores
config.mfa.beam = 150    # Higher quality alignment

pipeline = JebasaPipeline(config)

# Process files one at a time
for chapter in chapters:
    result = pipeline.process_single_chapter(chapter)
    # Save intermediate results
```

### Memory Optimization

```yaml
# config.yaml
mfa:
  num_jobs: 2  # Reduce parallel jobs
  beam: 80     # Lower beam search
  
audio:
  sample_rate: 16000  # Don't use higher than necessary
```

### Speed Optimization

```bash
# Fast processing (lower quality)
jebasa align \
  --corpus-dir ./processed \
  --dictionary ./dictionaries/custom.dict \
  --output-dir ./aligned \
  --beam 50 \
  --retry-beam 200 \
  --num-jobs $(nproc)  # Use all CPU cores
```

## Common Workflows

### Workflow 1: Research Project

```bash
# Process multiple books for linguistic research
for book in research_corpus/*/; do
    jebasa run \
        --input-dir "$book" \
        --output-dir "./research_output/$(basename "$book")" \
        --config research_config.yaml
done
```

### Workflow 2: Language Learning App

```python
# Generate subtitles for language learning app
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig

def generate_learning_subtitles(audio_file, text_file, output_dir):
    """Generate subtitles optimized for language learning."""
    config = JebasaConfig()
    
    # Shorter subtitles for learning
    config.subtitles.max_line_length = 30
    config.subtitles.max_lines = 2
    config.subtitles.min_duration = 2.0  # Longer display time
    
    # High precision alignment
    config.mfa.beam = 200
    config.mfa.retry_beam = 800
    
    pipeline = JebasaPipeline(config)
    
    # Process single file pair
    return pipeline.process_pair(audio_file, text_file, output_dir)
```

### Workflow 3: Audiobook Production

```bash
# High-quality production workflow
jebasa prepare-audio --input-dir ./audio --output-dir ./processed/audio
jebasa prepare-text --input-dir ./text --output-dir ./processed/text  
jebasa create-dictionary --input-dir ./processed/text --output-dir ./dictionaries --review

# Manual review of dictionary
echo "Review dictionary entries in: ./dictionaries/review.txt"
read -p "Press enter after review..."

jebasa align \
    --corpus-dir ./processed \
    --dictionary ./dictionaries/combined.dict \
    --output-dir ./aligned \
    --beam 200 \
    --retry-beam 800 \
    --num-jobs 8

jebasa generate-subtitles \
    --alignment-dir ./aligned \
    --text-dir ./processed/text \
    --output-dir ./final_subtitles \
    --max-line-length 35
```

These examples should help you get started with Jebasa and show you how to handle various use cases from simple processing to complex workflows. Remember to adjust parameters based on your specific needs and always validate your results!