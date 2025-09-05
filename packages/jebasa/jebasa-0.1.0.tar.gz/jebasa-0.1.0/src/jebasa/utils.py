"""Utility functions for Jebasa."""

import re
import logging
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, TaskID


console = Console()


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Set up logging with rich formatting."""
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


def normalize_filename(filename: str) -> str:
    """Normalize filename by removing special characters and converting to lowercase."""
    # Remove file extension
    name = Path(filename).stem
    
    # Replace Japanese separators and special characters
    name = re.sub(r'[・]', '_', name)
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    
    return name.lower()


def get_audio_files(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]:
    """Get all audio files from directory."""
    if extensions is None:
        extensions = ['.mp3', '.m4a', '.wav', '.flac', '.aac']
    
    files = []
    for ext in extensions:
        files.extend(directory.glob(f'*{ext}'))
        files.extend(directory.glob(f'*{ext.upper()}'))
    
    return sorted(files)


def get_text_files(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]:
    """Get all text files from directory."""
    if extensions is None:
        extensions = ['.txt', '.html', '.xhtml', '.xml']
    
    files = []
    for ext in extensions:
        files.extend(directory.glob(f'*{ext}'))
        files.extend(directory.glob(f'*{ext.upper()}'))
    
    return sorted(files)


def get_epub_files(directory: Path) -> List[Path]:
    """Get all EPUB files from directory."""
    files = list(directory.glob('*.epub')) + list(directory.glob('*.EPUB'))
    return sorted(files)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS.sss format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{secs:06.3f}"


def parse_duration(duration_str: str) -> float:
    """Parse duration string to seconds."""
    parts = duration_str.split(':')
    
    if len(parts) == 3:  # HH:MM:SS.sss
        hours, minutes, seconds = parts
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    elif len(parts) == 2:  # MM:SS.sss
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    else:  # SS.sss
        return float(parts[0])


def create_progress_bar(description: str, total: int) -> tuple[Progress, TaskID]:
    """Create a rich progress bar."""
    progress = Progress(
        "[progress.description]{task.description}",
        "[progress.percentage]{task.percentage:3.0f}%",
        "[progress.bar]",
        "[progress.completed]/{task.total}",
        "[progress.elapsed]",
        console=console,
    )
    
    task = progress.add_task(description, total=total)
    return progress, task


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing problematic characters."""
    # Replace spaces and special characters
    safe = re.sub(r'[^\w\s-]', '', filename)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe.strip('_')


def chunk_text(text: str, max_length: int = 42, max_lines: int = 2) -> List[str]:
    """Chunk text into subtitle-friendly lines."""
    if len(text) <= max_length:
        return [text]
    
    # Split by punctuation first
    sentences = re.split(r'[。！？.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    lines = []
    current_line = ""
    
    for sentence in sentences:
        if len(current_line + sentence) <= max_length:
            current_line += sentence
        else:
            if current_line:
                lines.append(current_line)
            current_line = sentence
            
            if len(lines) >= max_lines:
                break
    
    if current_line and len(lines) < max_lines:
        lines.append(current_line)
    
    return lines


def validate_audio_file(file_path: Path) -> bool:
    """Validate that file is a supported audio format."""
    supported_extensions = {'.mp3', '.m4a', '.wav', '.flac', '.aac'}
    return file_path.suffix.lower() in supported_extensions


def validate_text_file(file_path: Path) -> bool:
    """Validate that file is a supported text format."""
    supported_extensions = {'.txt', '.html', '.xhtml', '.xml', '.epub'}
    return file_path.suffix.lower() in supported_extensions


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists and return Path object."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_directory(path: Union[str, Path], keep_files: Optional[List[str]] = None) -> None:
    """Clean directory contents, optionally keeping specified files."""
    path = Path(path)
    if not path.exists():
        return
    
    keep_files = keep_files or []
    
    for item in path.iterdir():
        if item.name in keep_files:
            continue
            
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil
            shutil.rmtree(item)


def get_file_stem(file_path: Path) -> str:
    """Get file stem (name without extension and numbering)."""
    stem = file_path.stem
    
    # Remove common numbering patterns
    stem = re.sub(r'_\d+$', '', stem)  # _01, _02, etc.
    stem = re.sub(r'\d+$', '', stem)   # 01, 02, etc.
    
    return stem.strip('_')


def find_matching_files(
    audio_files: List[Path], 
    text_files: List[Path]
) -> Dict[str, Dict[str, Path]]:
    """Find matching audio and text files based on filenames."""
    matches = {}
    
    audio_stems = {get_file_stem(f): f for f in audio_files}
    text_stems = {get_file_stem(f): f for f in text_files}
    
    for stem, audio_file in audio_stems.items():
        if stem in text_stems:
            matches[stem] = {
                'audio': audio_file,
                'text': text_stems[stem]
            }
    
    return matches