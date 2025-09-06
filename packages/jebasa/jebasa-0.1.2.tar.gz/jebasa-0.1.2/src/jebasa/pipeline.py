"""Main pipeline orchestration for Jebasa."""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json

from jebasa.config import JebasaConfig
from jebasa.exceptions import JebasaError, AudioProcessingError, TextProcessingError, AlignmentError, SubtitleGenerationError
from jebasa.audio import AudioProcessor
from jebasa.text import TextProcessor
from jebasa.dictionary import DictionaryCreator
from jebasa.alignment import AlignmentRunner
from jebasa.subtitles import SubtitleGenerator
from jebasa.utils import (
    get_audio_files, get_text_files, get_epub_files, 
    find_matching_files, setup_logging, ensure_directory
)

logger = logging.getLogger(__name__)


class JebasaPipeline:
    """Main pipeline for Japanese audio-text alignment."""
    
    def __init__(self, config: JebasaConfig):
        self.config = config
        self.audio_processor = AudioProcessor(config.audio)
        self.text_processor = TextProcessor(config.text)
        self.dictionary_creator = DictionaryCreator(config.mfa)
        self.alignment_runner = AlignmentRunner(config.mfa)
        self.subtitle_generator = SubtitleGenerator(config.subtitles)
        
        # Create output directories
        self._setup_directories()
    
    def _setup_directories(self) -> None:
        """Set up necessary directories."""
        self.config.paths.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.paths.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create stage directories
        self.config.paths.get_stage_dir('audio', self.config).mkdir(parents=True, exist_ok=True)
        self.config.paths.get_stage_dir('text', self.config).mkdir(parents=True, exist_ok=True)
        self.config.paths.get_stage_dir('dictionary', self.config).mkdir(parents=True, exist_ok=True)
        self.config.paths.get_stage_dir('alignment', self.config).mkdir(parents=True, exist_ok=True)
        self.config.paths.get_stage_dir('subtitle', self.config).mkdir(parents=True, exist_ok=True)
    
    def run_all(self, skip_preparation: bool = False) -> Dict[str, Dict[str, Any]]:
        """Run complete alignment pipeline."""
        results = {}
        start_time = datetime.now()
        
        logger.info("Starting complete Jebasa pipeline")
        
        try:
            # Stage 1: Audio preparation
            if not skip_preparation:
                logger.info("Stage 1: Audio preparation")
                audio_results = self.prepare_audio()
                results['audio_preparation'] = {
                    'success': True,
                    'file_count': len(audio_results),
                    'results': audio_results
                }
            else:
                logger.info("Skipping audio preparation")
                results['audio_preparation'] = {'success': True, 'skipped': True}
            
            # Stage 2: Text preparation
            if not skip_preparation:
                logger.info("Stage 2: Text preparation")
                text_results = self.prepare_text()
                results['text_preparation'] = {
                    'success': True,
                    'file_count': len(text_results),
                    'results': text_results
                }
            else:
                logger.info("Skipping text preparation")
                results['text_preparation'] = {'success': True, 'skipped': True}
            
            # Stage 3: Dictionary creation
            logger.info("Stage 3: Dictionary creation")
            dict_results = self.create_dictionary()
            results['dictionary_creation'] = {
                'success': True,
                'total_entries': dict_results['total_entries'],
                'custom_entries': dict_results['custom_entries'],
                'results': dict_results
            }
            
            # Stage 4: Alignment
            logger.info("Stage 4: Forced alignment")
            alignment_results = self.run_alignment()
            successful_alignments = sum(1 for r in alignment_results if r.get('success', False))
            results['alignment'] = {
                'success': True,
                'file_count': len(alignment_results),
                'successful_count': successful_alignments,
                'results': alignment_results
            }
            
            # Stage 5: Subtitle generation
            logger.info("Stage 5: Subtitle generation")
            subtitle_results = self.generate_subtitles()
            total_subtitles = sum(info['subtitle_count'] for _, info in subtitle_results)
            results['subtitle_generation'] = {
                'success': True,
                'file_count': len(subtitle_results),
                'total_subtitles': total_subtitles,
                'results': subtitle_results
            }
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Pipeline completed in {duration:.1f} seconds")
            logger.info(f"Generated {len(subtitle_results)} subtitle files with {total_subtitles} total subtitles")
            
            # Save pipeline report
            self._save_pipeline_report(results, duration)
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results['pipeline_error'] = {
                'success': False,
                'error': str(e),
                'duration': duration
            }
            
            raise JebasaError(f"Pipeline failed: {e}")
    
    def prepare_audio(self) -> List[Tuple[Path, Path]]:
        """Prepare audio files for alignment."""
        # Use the configured audio stage directory, or fall back to legacy paths
        if hasattr(self.config.paths, 'audio_dir') and self.config.paths.audio_dir:
            output_audio_dir = self.config.paths.audio_dir
        else:
            output_audio_dir = self.config.paths.get_stage_dir('audio', self.config)
        
        # Determine input directory
        input_audio_dir = self.config.paths.input_dir / "audio"
        if not input_audio_dir.exists():
            # Try input directory directly
            input_audio_dir = self.config.paths.input_dir
        
        logger.info(f"Preparing audio files from {input_audio_dir} to {output_audio_dir}")
        
        try:
            processed_files = self.audio_processor.process_audio_files(
                input_audio_dir,
                output_audio_dir
            )
            
            # Return list of (original, processed) tuples
            result_pairs = []
            for processed_file in processed_files:
                # Find original file
                original_matches = list(input_audio_dir.glob(f"{processed_file.stem}.*"))
                
                if original_matches:
                    result_pairs.append((original_matches[0], processed_file))
                else:
                    result_pairs.append((processed_file, processed_file))
            
            logger.info(f"Processed {len(result_pairs)} audio files")
            return result_pairs
            
        except Exception as e:
            raise AudioProcessingError(f"Audio preparation failed: {e}")
    
    def prepare_text(self) -> List[Tuple[Path, Dict[str, Any]]]:
        """Prepare text files for alignment."""
        # Use the configured text stage directory, or fall back to legacy paths
        if hasattr(self.config.paths, 'text_dir') and self.config.paths.text_dir:
            output_text_dir = self.config.paths.text_dir
        else:
            output_text_dir = self.config.paths.get_stage_dir('text', self.config)
        
        # Determine input directory
        input_text_dir = self.config.paths.input_dir / "text"
        if not input_text_dir.exists():
            # Try input directory directly
            input_text_dir = self.config.paths.input_dir
        
        logger.info(f"Preparing text files from {input_text_dir} to {output_text_dir}")
        
        try:
            processed_files = self.text_processor.process_text_files(
                input_text_dir,
                output_text_dir
            )
            
            logger.info(f"Processed {len(processed_files)} text files")
            return processed_files
            
        except Exception as e:
            raise TextProcessingError(f"Text preparation failed: {e}")
    
    def create_dictionary(self, review_file: bool = True) -> Dict[str, Any]:
        """Create pronunciation dictionary."""
        # Use the configured dictionary stage directory, or fall back to legacy paths
        if hasattr(self.config.paths, 'dictionary_dir') and self.config.paths.dictionary_dir:
            dict_output_dir = self.config.paths.dictionary_dir
        else:
            dict_output_dir = self.config.paths.get_stage_dir('dictionary', self.config)
        
        # Use text directory from previous stage
        if hasattr(self.config.paths, 'text_dir') and self.config.paths.text_dir:
            text_output_dir = self.config.paths.text_dir
        else:
            text_output_dir = self.config.paths.get_stage_dir('text', self.config)
        
        logger.info(f"Creating pronunciation dictionary from {text_output_dir} to {dict_output_dir}")
        
        try:
            dict_results = self.dictionary_creator.create_dictionary(
                text_output_dir,
                dict_output_dir,
                review_file=review_file
            )
            
            logger.info(f"Dictionary created with {dict_results['total_entries']} total entries")
            if dict_results['custom_entries'] > 0:
                logger.info(f"Added {dict_results['custom_entries']} custom entries from furigana")
            
            return dict_results
            
        except Exception as e:
            raise JebasaError(f"Dictionary creation failed: {e}")
    
    def run_alignment(self, dictionary_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Run forced alignment."""
        # Use the configured alignment stage directory, or fall back to legacy paths
        if hasattr(self.config.paths, 'alignment_dir') and self.config.paths.alignment_dir:
            alignment_output_dir = self.config.paths.alignment_dir
        else:
            alignment_output_dir = self.config.paths.get_stage_dir('alignment', self.config)
        
        # Use audio directory as corpus input
        if hasattr(self.config.paths, 'audio_dir') and self.config.paths.audio_dir:
            corpus_dir = self.config.paths.audio_dir
        else:
            corpus_dir = self.config.paths.get_stage_dir('audio', self.config)
        
        # Use custom dictionary if available
        if dictionary_file is None:
            if hasattr(self.config.paths, 'dictionary_dir') and self.config.paths.dictionary_dir:
                dict_dir = self.config.paths.dictionary_dir
            else:
                dict_dir = self.config.paths.get_stage_dir('dictionary', self.config)
            
            dict_file = dict_dir / "combined_mfa_dictionary.dict"
            if dict_file.exists():
                dictionary_file = dict_file
        
        logger.info(f"Running forced alignment from {corpus_dir} to {alignment_output_dir}")
        
        try:
            alignment_results = self.alignment_runner.run_alignment(
                corpus_dir,
                dictionary_file,
                alignment_output_dir
            )
            
            logger.info(f"Alignment completed: {len(alignment_results)} files processed")
            return alignment_results
            
        except Exception as e:
            raise AlignmentError(f"Alignment failed: {e}")
    
    def generate_subtitles(self) -> List[Tuple[Path, Dict[str, Any]]]:
        """Generate subtitle files."""
        # Use the configured subtitle stage directory, or fall back to legacy paths
        if hasattr(self.config.paths, 'subtitle_dir') and self.config.paths.subtitle_dir:
            subtitle_output_dir = self.config.paths.subtitle_dir
        else:
            subtitle_output_dir = self.config.paths.get_stage_dir('subtitle', self.config)
        
        # Use alignment directory from previous stage
        if hasattr(self.config.paths, 'alignment_dir') and self.config.paths.alignment_dir:
            alignment_dir = self.config.paths.alignment_dir
        else:
            alignment_dir = self.config.paths.get_stage_dir('alignment', self.config)
        
        # Use text directory from previous stage
        if hasattr(self.config.paths, 'text_dir') and self.config.paths.text_dir:
            text_dir = self.config.paths.text_dir
        else:
            text_dir = self.config.paths.get_stage_dir('text', self.config)
        
        logger.info(f"Generating subtitle files from {alignment_dir} and {text_dir} to {subtitle_output_dir}")
        
        try:
            subtitle_results = self.subtitle_generator.generate_subtitles(
                alignment_dir,
                text_dir,
                subtitle_output_dir
            )
            
            total_subtitles = sum(info['subtitle_count'] for _, info in subtitle_results)
            logger.info(f"Generated {len(subtitle_results)} subtitle files with {total_subtitles} total subtitles")
            
            return subtitle_results
            
        except Exception as e:
            raise SubtitleGenerationError(f"Subtitle generation failed: {e}")
    
    def process_single_file(
        self, 
        audio_file: Path, 
        text_file: Path, 
        output_dir: Path
    ) -> Dict[str, Any]:
        """Process a single audio-text file pair."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Processing single file pair: {audio_file.name} + {text_file.name}")
        
        try:
            # Prepare audio
            audio_output_dir = output_dir / "audio"
            processed_audio = self.audio_processor.process_audio_files(
                audio_file.parent,
                audio_output_dir
            )
            
            # Prepare text
            text_output_dir = output_dir / "text"
            processed_text = self.text_processor.process_text_files(
                text_file.parent,
                text_output_dir
            )
            
            # Create dictionary
            dict_output_dir = output_dir / "dictionaries"
            dict_results = self.dictionary_creator.create_dictionary(
                text_output_dir,
                dict_output_dir
            )
            
            # Run alignment
            alignment_output_dir = output_dir / "aligned"
            alignment_results = self.alignment_runner.run_alignment(
                output_dir,
                dict_results['dictionary_file'],
                alignment_output_dir
            )
            
            # Generate subtitles
            subtitle_output_dir = output_dir / "srt"
            subtitle_results = self.subtitle_generator.generate_subtitles(
                alignment_output_dir,
                text_output_dir,
                subtitle_output_dir
            )
            
            return {
                'success': True,
                'audio_file': audio_file,
                'text_file': text_file,
                'output_dir': output_dir,
                'subtitle_file': subtitle_results[0][0] if subtitle_results else None,
                'subtitle_info': subtitle_results[0][1] if subtitle_results else None
            }
            
        except Exception as e:
            logger.error(f"Single file processing failed: {e}")
            return {
                'success': False,
                'audio_file': audio_file,
                'text_file': text_file,
                'error': str(e)
            }
    
    def validate_inputs(self) -> Dict[str, Any]:
        """Validate input files and configuration."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'audio_files': [],
            'text_files': [],
            'matched_pairs': []
        }
        
        try:
            # Check input directory
            if not self.config.paths.input_dir.exists():
                validation_results['errors'].append(f"Input directory does not exist: {self.config.paths.input_dir}")
                validation_results['valid'] = False
                return validation_results
            
            # Find audio files
            audio_dir = self.config.paths.input_dir / "audio"
            if not audio_dir.exists():
                audio_dir = self.config.paths.input_dir
            
            audio_files = get_audio_files(audio_dir)
            validation_results['audio_files'] = audio_files
            
            if not audio_files:
                validation_results['warnings'].append(f"No audio files found in {audio_dir}")
            
            # Find text files
            text_dir = self.config.paths.input_dir / "text"
            if not text_dir.exists():
                text_dir = self.config.paths.input_dir
            
            text_files = get_text_files(text_dir) + get_epub_files(text_dir)
            validation_results['text_files'] = text_files
            
            if not text_files:
                validation_results['warnings'].append(f"No text files found in {text_dir}")
            
            # Check for matching pairs
            if audio_files and text_files:
                matched_pairs = find_matching_files(audio_files, text_files)
                validation_results['matched_pairs'] = matched_pairs
                
                if not matched_pairs:
                    validation_results['warnings'].append("No matching audio-text pairs found by filename")
            
            # Validate audio files
            for audio_file in audio_files:
                try:
                    info = self.audio_processor.get_audio_info(audio_file)
                    if info['duration'] < 1.0:
                        validation_results['warnings'].append(f"Audio file very short: {audio_file.name} ({info['duration']:.1f}s)")
                    if info['sample_rate'] < 8000:
                        validation_results['warnings'].append(f"Audio file low sample rate: {audio_file.name} ({info['sample_rate']}Hz)")
                except Exception as e:
                    validation_results['warnings'].append(f"Could not validate audio file {audio_file.name}: {e}")
            
            # Validate text files
            for text_file in text_files:
                try:
                    content = text_file.read_text(encoding='utf-8')
                    if len(content) < 10:
                        validation_results['warnings'].append(f"Text file very short: {text_file.name}")
                except Exception as e:
                    validation_results['warnings'].append(f"Could not read text file {text_file.name}: {e}")
            
            # Check system dependencies
            import shutil
            if not shutil.which('ffmpeg'):
                validation_results['errors'].append("FFmpeg not found in PATH")
                validation_results['valid'] = False
            
            if not shutil.which('mfa'):
                validation_results['errors'].append("MFA (Montreal Forced Aligner) not found in PATH")
                validation_results['valid'] = False
            
            return validation_results
            
        except Exception as e:
            validation_results['errors'].append(f"Validation failed: {e}")
            validation_results['valid'] = False
            return validation_results
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and file counts."""
        status = {
            'input_files': {
                'audio': len(get_audio_files(self.config.paths.input_dir)),
                'text': len(get_text_files(self.config.paths.input_dir) + get_epub_files(self.config.paths.input_dir))
            },
            'output_files': {
                'audio': len(get_audio_files(self.config.paths.output_dir / "audio")),
                'text': len(get_text_files(self.config.paths.output_dir / "text")),
                'dictionaries': len(list((self.config.paths.output_dir / "dictionaries").glob("*.dict"))),
                'aligned': len(list((self.config.paths.output_dir / "aligned").glob("*.TextGrid"))),
                'subtitles': len(list((self.config.paths.output_dir / "srt").glob("*.srt")))
            },
            'config': self.config.model_dump()
        }
        
        return status
    
    def _save_pipeline_report(self, results: Dict[str, Any], duration: float) -> None:
        """Save detailed pipeline report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'config': self.config.model_dump(),
            'results': results,
            'status': self.get_pipeline_status()
        }
        
        report_file = self.config.paths.output_dir / "pipeline_report.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Pipeline report saved: {report_file}")
        except Exception as e:
            logger.warning(f"Failed to save pipeline report: {e}")
    
    def clean_output(self, keep_subtitles: bool = True) -> None:
        """Clean output directory, optionally keeping final subtitles."""
        import shutil
        
        logger.info("Cleaning output directory")
        
        try:
            if keep_subtitles:
                # Keep only subtitle files
                subtitle_dir = self.config.paths.output_dir / "srt"
                if subtitle_dir.exists():
                    # Create clean directory
                    clean_dir = self.config.paths.output_dir / "final"
                    clean_dir.mkdir(exist_ok=True)
                    
                    # Copy subtitle files
                    for srt_file in subtitle_dir.glob("*.srt"):
                        shutil.copy2(srt_file, clean_dir)
                    
                    # Remove everything else
                    for item in self.config.paths.output_dir.iterdir():
                        if item.name != "final":
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                    
                    # Move final files back
                    for item in clean_dir.iterdir():
                        shutil.move(str(item), str(self.config.paths.output_dir))
                    
                    clean_dir.rmdir()
            else:
                # Remove everything
                for item in self.config.paths.output_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            
            logger.info("Output directory cleaned")
            
        except Exception as e:
            logger.warning(f"Failed to clean output directory: {e}")