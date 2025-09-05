"""Audio processing functionality for Jebasa."""

import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydub import AudioSegment
from rich.progress import Progress

from jebasa.config import AudioConfig
from jebasa.exceptions import AudioProcessingError
from jebasa.utils import (
    get_audio_files, 
    validate_audio_file, 
    create_progress_bar,
    format_duration
)

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handle audio file processing for alignment pipeline."""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.sample_rate = config.sample_rate
        self.channels = config.channels
        self.format = config.format
        self.ffmpeg_options = config.ffmpeg_options
    
    def process_audio_files(
        self, 
        input_dir: Path, 
        output_dir: Path,
        progress_callback: Optional[callable] = None
    ) -> List[Path]:
        """Process all audio files in input directory."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_files = get_audio_files(input_dir)
        if not audio_files:
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        processed_files = []
        
        with Progress() as progress:
            task = progress.add_task("Processing audio files...", total=len(audio_files))
            
            for audio_file in audio_files:
                try:
                    output_file = self._process_single_audio(audio_file, output_dir)
                    processed_files.append(output_file)
                    
                    if progress_callback:
                        progress_callback(audio_file, output_file)
                    
                    progress.advance(task)
                    
                except Exception as e:
                    logger.error(f"Failed to process {audio_file}: {e}")
                    raise AudioProcessingError(f"Audio processing failed for {audio_file}: {e}")
        
        return processed_files
    
    def _process_single_audio(self, input_file: Path, output_dir: Path) -> Path:
        """Process a single audio file."""
        if not validate_audio_file(input_file):
            raise AudioProcessingError(f"Unsupported audio format: {input_file.suffix}")
        
        # Generate output filename
        output_filename = f"{input_file.stem}.{self.format}"
        output_file = output_dir / output_filename
        
        # Load audio file
        try:
            audio = AudioSegment.from_file(str(input_file))
        except Exception as e:
            raise AudioProcessingError(f"Failed to load audio file {input_file}: {e}")
        
        # Apply processing
        processed_audio = self._apply_audio_processing(audio)
        
        # Export processed audio
        try:
            processed_audio.export(
                str(output_file),
                format=self.format,
                parameters=self._get_ffmpeg_parameters()
            )
        except Exception as e:
            raise AudioProcessingError(f"Failed to export audio to {output_file}: {e}")
        
        # Log processing info
        original_duration = len(audio) / 1000.0  # Convert to seconds
        processed_duration = len(processed_audio) / 1000.0
        
        logger.info(
            f"Processed {input_file.name}: "
            f"{format_duration(original_duration)} -> "
            f"{format_duration(processed_duration)} "
            f"({self.sample_rate}Hz, {self.channels}ch)"
        )
        
        return output_file
    
    def _apply_audio_processing(self, audio: AudioSegment) -> AudioSegment:
        """Apply audio processing steps."""
        # Set channels
        if audio.channels != self.channels:
            audio = audio.set_channels(self.channels)
            logger.debug(f"Set channels to {self.channels}")
        
        # Set frame rate
        if audio.frame_rate != self.sample_rate:
            audio = audio.set_frame_rate(self.sample_rate)
            logger.debug(f"Set sample rate to {self.sample_rate}Hz")
        
        # Normalize audio
        audio = audio.normalize()
        logger.debug("Normalized audio")
        
        return audio
    
    def _get_ffmpeg_parameters(self) -> List[str]:
        """Get FFmpeg parameters for export."""
        params = []
        
        # Add custom FFmpeg options
        for key, value in self.ffmpeg_options.items():
            params.extend([f"-{key}", str(value)])
        
        return params
    
    def merge_audio_files(
        self, 
        files: List[Path], 
        output_file: Path,
        crossfade: int = 0
    ) -> Path:
        """Merge multiple audio files into one."""
        if not files:
            raise AudioProcessingError("No files to merge")
        
        # Load all audio files
        segments = []
        for file in files:
            try:
                segment = AudioSegment.from_file(str(file))
                segments.append(segment)
            except Exception as e:
                raise AudioProcessingError(f"Failed to load {file}: {e}")
        
        # Merge segments
        merged = segments[0]
        for segment in segments[1:]:
            if crossfade > 0:
                merged = merged.append(segment, crossfade=crossfade)
            else:
                merged = merged + segment
        
        # Export merged audio
        try:
            merged.export(str(output_file), format=self.format)
        except Exception as e:
            raise AudioProcessingError(f"Failed to export merged audio: {e}")
        
        total_duration = len(merged) / 1000.0
        logger.info(f"Merged {len(files)} files into {output_file.name} ({format_duration(total_duration)})")
        
        return output_file
    
    def split_audio_by_duration(
        self, 
        input_file: Path, 
        segment_duration: float,
        output_dir: Path
    ) -> List[Path]:
        """Split audio file into segments of specified duration."""
        try:
            audio = AudioSegment.from_file(str(input_file))
        except Exception as e:
            raise AudioProcessingError(f"Failed to load audio file: {e}")
        
        total_duration = len(audio) / 1000.0  # seconds
        segment_duration_ms = int(segment_duration * 1000)
        
        segments = []
        for i, start_ms in enumerate(range(0, len(audio), segment_duration_ms)):
            end_ms = min(start_ms + segment_duration_ms, len(audio))
            segment = audio[start_ms:end_ms]
            
            output_file = output_dir / f"{input_file.stem}_{i:03d}.{self.format}"
            
            try:
                segment.export(str(output_file), format=self.format)
                segments.append(output_file)
            except Exception as e:
                raise AudioProcessingError(f"Failed to export segment {i}: {e}")
        
        logger.info(f"Split {input_file.name} into {len(segments)} segments of ~{segment_duration}s each")
        
        return segments
    
    def get_audio_info(self, audio_file: Path) -> Dict[str, Any]:
        """Get information about an audio file."""
        try:
            audio = AudioSegment.from_file(str(audio_file))
        except Exception as e:
            raise AudioProcessingError(f"Failed to load audio file: {e}")
        
        return {
            'filename': audio_file.name,
            'duration': len(audio) / 1000.0,
            'sample_rate': audio.frame_rate,
            'channels': audio.channels,
            'sample_width': audio.sample_width,
            'frame_count': len(audio.get_array_of_samples())
        }
    
    def validate_audio_quality(self, audio_file: Path) -> bool:
        """Validate that audio file meets alignment requirements."""
        try:
            info = self.get_audio_info(audio_file)
        except AudioProcessingError:
            return False
        
        # Check duration (should be reasonable for alignment)
        if info['duration'] < 1.0:
            logger.warning(f"Audio too short: {info['duration']}s")
            return False
        
        # Check sample rate
        if info['sample_rate'] < 8000:
            logger.warning(f"Sample rate too low: {info['sample_rate']}Hz")
            return False
        
        # Check for silence (basic check)
        try:
            audio = AudioSegment.from_file(str(audio_file))
            if audio.dBFS < -60:  # Very quiet
                logger.warning(f"Audio appears to be mostly silent: {audio.dBFS}dBFS")
                return False
        except Exception:
            return False
        
        return True
    
    def convert_with_ffmpeg(
        self, 
        input_file: Path, 
        output_file: Path,
        additional_options: Optional[List[str]] = None
    ) -> bool:
        """Convert audio using FFmpeg directly."""
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-ar', str(self.sample_rate),
            '-ac', str(self.channels),
            '-y'  # Overwrite output
        ]
        
        if additional_options:
            cmd.extend(additional_options)
        
        cmd.append(str(output_file))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"FFmpeg conversion successful: {input_file} -> {output_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {e.stderr}")
            raise AudioProcessingError(f"FFmpeg conversion failed: {e.stderr}")
        except FileNotFoundError:
            raise AudioProcessingError("FFmpeg not found. Please install FFmpeg.")