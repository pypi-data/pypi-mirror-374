"""Configuration management for Jebasa."""

from pathlib import Path
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
import yaml


class AudioConfig(BaseModel):
    """Audio processing configuration."""
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    format: str = Field(default="wav", description="Audio format")
    ffmpeg_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional FFmpeg options"
    )


class TextConfig(BaseModel):
    """Text processing configuration."""
    tokenizer: str = Field(default="mecab", description="Japanese tokenizer to use")
    normalize_text: bool = Field(default=True, description="Normalize full/half-width characters")
    extract_furigana: bool = Field(default=True, description="Extract furigana annotations")
    min_chapter_length: int = Field(default=100, description="Minimum chapter length in characters")


class MFAConfig(BaseModel):
    """Montreal Forced Aligner configuration."""
    acoustic_model: str = Field(default="japanese_mfa", description="MFA acoustic model")
    beam: int = Field(default=100, description="Beam search width")
    retry_beam: int = Field(default=400, description="Retry beam search width")
    num_jobs: int = Field(default=4, description="Number of parallel jobs")
    single_speaker: bool = Field(default=True, description="Optimize for single speaker")
    textgrid_cleanup: bool = Field(default=True, description="Clean up TextGrid output")


class SubtitleConfig(BaseModel):
    """Subtitle generation configuration - simplified to match original script."""
    # No configurable settings - uses hardcoded values from original tg2srt_final_v3.py
    # Key hardcoded values from original script:
    # - seconds_to_move = 0.3 (gap adjustment)
    # - 2.0 seconds per unaligned sentence
    # - 0.1 seconds minimum gap threshold
    # - No line length limits (full sentences)


class PathConfig(BaseModel):
    """Path configuration."""
    input_dir: Path = Field(default=Path("input"), description="Base input directory")
    output_dir: Path = Field(default=Path("output"), description="Base output directory")
    temp_dir: Path = Field(default=Path("temp"), description="Temporary directory")
    
    # Stage-specific directories (relative to output_dir if not absolute)
    audio_dir: Optional[Path] = Field(default=None, description="Prepared audio files directory")
    text_dir: Optional[Path] = Field(default=None, description="Processed text files directory")
    dictionary_dir: Optional[Path] = Field(default=None, description="Dictionary files directory")
    alignment_dir: Optional[Path] = Field(default=None, description="MFA alignment results directory")
    subtitle_dir: Optional[Path] = Field(default=None, description="Generated subtitle files directory")
    
    @validator('*', pre=True)
    def convert_to_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    def get_stage_dir(self, stage: str, base_config: "JebasaConfig") -> Path:
        """Get the appropriate directory for a pipeline stage."""
        stage_dirs = {
            'audio': self.audio_dir,
            'text': self.text_dir,
            'dictionary': self.dictionary_dir,
            'alignment': self.alignment_dir,
            'subtitle': self.subtitle_dir
        }
        
        # If stage-specific directory is configured, use it
        if stage_dirs[stage]:
            # Make absolute if relative
            if not stage_dirs[stage].is_absolute():
                return base_config.paths.output_dir / stage_dirs[stage]
            return stage_dirs[stage]
        
        # Default to standard subdirectories under output_dir
        defaults = {
            'audio': 'processed/audio',
            'text': 'processed/text', 
            'dictionary': 'dictionaries',
            'alignment': 'aligned',
            'subtitle': 'subtitles'
        }
        
        return base_config.paths.output_dir / defaults[stage]


class JebasaConfig(BaseModel):
    """Main Jebasa configuration."""
    audio: AudioConfig = Field(default_factory=AudioConfig)
    text: TextConfig = Field(default_factory=TextConfig)
    mfa: MFAConfig = Field(default_factory=MFAConfig)
    subtitles: SubtitleConfig = Field(default_factory=SubtitleConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    verbose: bool = Field(default=False, description="Enable verbose output")
    debug: bool = Field(default=False, description="Enable debug mode")

    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "JebasaConfig":
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    def to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and handle Path objects
        config_dict = self.model_dump()
        
        # Convert Path objects to strings for YAML serialization
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, Path):
                return str(obj)
            else:
                return obj
        
        config_dict = convert_paths(config_dict)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
    
    def ensure_directories(self) -> None:
        """Ensure all configured directories exist."""
        for path_attr in ['input_dir', 'output_dir', 'temp_dir']:
            path = getattr(self.paths, path_attr)
            path.mkdir(parents=True, exist_ok=True)


def get_config(
    config_file: Optional[Path] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> JebasaConfig:
    """Get configuration with optional file and overrides."""
    if config_file and config_file.exists():
        config = JebasaConfig.from_file(config_file)
    else:
        config = JebasaConfig()
    
    if overrides:
        config = config.copy(update=overrides)
    
    config.ensure_directories()
    return config