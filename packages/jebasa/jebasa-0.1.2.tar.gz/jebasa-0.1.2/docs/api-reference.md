# API Reference

This page provides detailed documentation of all classes and functions in the Jebasa package.

## Core Classes

### JebasaPipeline

The main pipeline class that orchestrates the entire alignment process.

```python
from jebasa.pipeline import JebasaPipeline
from jebasa.config import JebasaConfig

config = JebasaConfig()
pipeline = JebasaPipeline(config)
results = pipeline.run_all()
```

#### Methods

##### `run_all(skip_preparation: bool = False) -> Dict[str, Dict[str, Any]]`

Run the complete alignment pipeline.

**Parameters:**
- `skip_preparation` (bool): Skip audio/text preparation if files are already processed

**Returns:**
Dictionary containing results from each pipeline stage

##### `prepare_audio() -> List[Tuple[Path, Path]]`

Prepare audio files for alignment.

**Returns:**
List of tuples containing (original_file, processed_file) pairs

##### `prepare_text() -> List[Tuple[Path, Dict[str, Any]]]`

Prepare text files for alignment.

**Returns:**
List of tuples containing (processed_file, info_dict) pairs

##### `create_dictionary(review_file: bool = True) -> Dict[str, Any]`

Create pronunciation dictionary from furigana annotations.

**Parameters:**
- `review_file` (bool): Generate review file for manual verification

**Returns:**
Dictionary containing dictionary creation results

##### `run_alignment(dictionary_file: Optional[Path] = None) -> List[Dict[str, Any]]`

Run forced alignment using Montreal Forced Aligner.

**Parameters:**
- `dictionary_file` (Path, optional): Custom dictionary file to use

**Returns:**
List of alignment results

##### `generate_subtitles() -> List[Tuple[Path, Dict[str, Any]]]`

Generate SRT subtitle files from alignment results.

**Returns:**
List of tuples containing (subtitle_file, info_dict) pairs

### Configuration Classes

#### JebasaConfig

Main configuration class for the pipeline.

```python
from jebasa.config import JebasaConfig

config = JebasaConfig()
config.audio.sample_rate = 22050
config.mfa.num_jobs = 8
```

**Attributes:**
- `audio` (AudioConfig): Audio processing configuration
- `text` (TextConfig): Text processing configuration  
- `mfa` (MFAConfig): Montreal Forced Aligner configuration
- `subtitles` (SubtitleConfig): Subtitle generation configuration
- `paths` (PathConfig): Directory path configuration

#### AudioConfig

Configuration for audio processing.

```python
from jebasa.config import AudioConfig

audio_config = AudioConfig(
    sample_rate=16000,
    channels=1,
    format="wav",
    ffmpeg_options={"acodec": "pcm_s16le"}
)
```

**Attributes:**
- `sample_rate` (int): Audio sample rate in Hz (default: 16000)
- `channels` (int): Number of audio channels (default: 1)
- `format` (str): Output audio format (default: "wav")
- `ffmpeg_options` (dict): Additional FFmpeg options

#### TextConfig

Configuration for text processing.

```python
from jebasa.config import TextConfig

text_config = TextConfig(
    tokenizer="mecab",
    normalize_text=True,
    extract_furigana=True,
    min_chapter_length=100
)
```

**Attributes:**
- `tokenizer` (str): Japanese tokenizer to use (default: "mecab")
- `normalize_text` (bool): Normalize full/half-width characters (default: True)
- `extract_furigana` (bool): Extract furigana annotations (default: True)
- `min_chapter_length` (int): Minimum chapter length in characters (default: 100)

#### MFAConfig

Configuration for Montreal Forced Aligner.

```python
from jebasa.config import MFAConfig

mfa_config = MFAConfig(
    acoustic_model="japanese_mfa",
    beam=100,
    retry_beam=400,
    num_jobs=4,
    single_speaker=True,
    textgrid_cleanup=True
)
```

**Attributes:**
- `acoustic_model` (str): MFA acoustic model (default: "japanese_mfa")
- `beam` (int): Beam search width (default: 100)
- `retry_beam` (int): Retry beam search width (default: 400)
- `num_jobs` (int): Number of parallel jobs (default: 4)
- `single_speaker` (bool): Optimize for single speaker (default: True)
- `textgrid_cleanup` (bool): Clean up TextGrid output (default: True)

#### SubtitleConfig

Configuration for subtitle generation.

```python
from jebasa.config import SubtitleConfig

subtitle_config = SubtitleConfig(
    max_line_length=42,
    max_lines=2,
    min_duration=1.0,
    max_duration=7.0,
    gap_filling=True
)
```

**Attributes:**
- `max_line_length` (int): Maximum characters per line (default: 42)
- `max_lines` (int): Maximum lines per subtitle (default: 2)
- `min_duration` (float): Minimum subtitle duration in seconds (default: 1.0)
- `max_duration` (float): Maximum subtitle duration in seconds (default: 7.0)
- `gap_filling` (bool): Fill gaps between aligned segments (default: True)

## Processing Classes

### AudioProcessor

Handles audio file processing for alignment.

```python
from jebasa.audio import AudioProcessor
from jebasa.config import AudioConfig

config = AudioConfig()
processor = AudioProcessor(config)
processed_files = processor.process_audio_files("input", "output")
```

#### Methods

##### `process_audio_files(input_dir: Path, output_dir: Path) -> List[Path]`

Process all audio files in input directory.

##### `get_audio_info(audio_file: Path) -> Dict[str, Any]`

Get information about an audio file.

**Returns:**
Dictionary containing duration, sample_rate, channels, etc.

##### `validate_audio_quality(audio_file: Path) -> bool`

Validate that audio file meets alignment requirements.

### TextProcessor

Handles text file processing with Japanese-specific features.

```python
from jebasa.text import TextProcessor
from jebasa.config import TextConfig

config = TextConfig()
processor = TextProcessor(config)
processed_files = processor.process_text_files("input", "output")
```

#### Methods

##### `process_text_files(input_dir: Path, output_dir: Path) -> List[Tuple[Path, Dict[str, Any]]]`

Process all text files in input directory.

##### `validate_chapter_alignment(audio_files: List[Path], text_files: List[Path]) -> Dict[str, Any]`

Validate that chapters align between audio and text files.

### DictionaryCreator

Creates pronunciation dictionaries from furigana annotations.

```python
from jebasa.dictionary import DictionaryCreator
from jebasa.config import MFAConfig

config = MFAConfig()
creator = DictionaryCreator(config)
dict_results = creator.create_dictionary("input", "output")
```

#### Methods

##### `create_dictionary(input_dir: Path, output_dir: Path, review_file: bool = True) -> Dict[str, Any]`

Create pronunciation dictionary from processed text files.

##### `validate_dictionary(dictionary_file: Path) -> Dict[str, Any]`

Validate dictionary file format and content.

### AlignmentRunner

Runs forced alignment using Montreal Forced Aligner.

```python
from jebasa.alignment import AlignmentRunner
from jebasa.config import MFAConfig

config = MFAConfig()
runner = AlignmentRunner(config)
alignment_results = runner.run_alignment("corpus", "dictionary", "output")
```

#### Methods

##### `run_alignment(corpus_dir: Path, dictionary_file: Path, output_dir: Path) -> List[Dict[str, Any]]`

Run forced alignment on corpus directory.

##### `validate_alignment_quality(textgrid_file: Path) -> Dict[str, Any]`

Validate alignment quality of a TextGrid file.

### SubtitleGenerator

Generates SRT subtitle files from alignment results.

```python
from jebasa.subtitles import SubtitleGenerator
from jebasa.config import SubtitleConfig

config = SubtitleConfig()
generator = SubtitleGenerator(config)
subtitle_results = generator.generate_subtitles("aligned", "text", "output")
```

#### Methods

##### `generate_subtitles(alignment_dir: Path, text_dir: Path, output_dir: Path) -> List[Tuple[Path, Dict[str, Any]]]`

Generate SRT subtitles from alignment results.

##### `validate_subtitle_file(subtitle_file: Path) -> Dict[str, Any]`

Validate SRT subtitle file format and content.

##### `convert_to_other_formats(srt_file: Path, output_dir: Path) -> Dict[str, Path]`

Convert SRT to other subtitle formats (VTT, TTML, transcript).

## Utility Functions

### Configuration Functions

#### `get_config(config_file: Optional[Path] = None, overrides: Optional[Dict[str, Any]] = None) -> JebasaConfig`

Get configuration with optional file and overrides.

### File Functions

#### `get_audio_files(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]`

Get all audio files from directory.

#### `get_text_files(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]`

Get all text files from directory.

#### `get_epub_files(directory: Path) -> List[Path]`

Get all EPUB files from directory.

#### `find_matching_files(audio_files: List[Path], text_files: List[Path]) -> Dict[str, Dict[str, Path]]`

Find matching audio and text files based on filenames.

### Time Functions

#### `format_duration(seconds: float) -> str`

Format duration in seconds to HH:MM:SS.sss format.

#### `parse_duration(duration_str: str) -> float`

Parse duration string to seconds.

### Logging Functions

#### `setup_logging(verbose: bool = False, debug: bool = False) -> None`

Set up logging with rich formatting.

## Exception Classes

All exceptions inherit from `JebasaError`:

- `AudioProcessingError`: Audio processing failures
- `TextProcessingError`: Text processing failures
- `AlignmentError`: MFA alignment failures
- `DictionaryError`: Dictionary creation failures
- `SubtitleGenerationError`: Subtitle generation failures
- `ConfigurationError`: Configuration errors
- `ValidationError`: Input validation failures
- `FileFormatError`: Unsupported file format errors

## CLI Functions

### Main CLI

The main CLI entry point is `jebasa.cli:main` which provides subcommands for each pipeline stage:

- `jebasa prepare-audio`: Prepare audio files
- `jebasa prepare-text`: Prepare text files
- `jebasa create-dictionary`: Create pronunciation dictionary
- `jebasa align`: Run forced alignment
- `jebasa generate-subtitles`: Generate subtitle files
- `jebasa run`: Run complete pipeline
- `jebasa info`: Show audio file information
- `jebasa config`: Show current configuration

## Examples

### Basic Pipeline Usage

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

### Custom Processing

```python
from jebasa.audio import AudioProcessor
from jebasa.config import AudioConfig

# Custom audio processing
config = AudioConfig(sample_rate=22050)
processor = AudioProcessor(config)
processed_files = processor.process_audio_files("input", "output")

# Get audio info
info = processor.get_audio_info("audio.mp3")
print(f"Duration: {info['duration']}s, Sample rate: {info['sample_rate']}Hz")
```

### Configuration Management

```python
from jebasa.config import JebasaConfig, get_config

# Load from file
config = JebasaConfig.from_file("config.yaml")

# Create with overrides
config = get_config(overrides={
    'audio': {'sample_rate': 44100},
    'mfa': {'num_jobs': 8}
})

# Save configuration
config.to_file("output_config.yaml")
```

For more examples, see the [Examples](examples.md) documentation page."}