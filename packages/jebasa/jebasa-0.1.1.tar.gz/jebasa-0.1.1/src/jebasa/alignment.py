"""Alignment functionality for Jebasa using Montreal Forced Aligner."""

import subprocess
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import time

from jebasa.config import MFAConfig
from jebasa.exceptions import AlignmentError
from jebasa.utils import get_audio_files, format_duration

logger = logging.getLogger(__name__)


class AlignmentRunner:
    """Handle forced alignment using Montreal Forced Aligner."""
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.acoustic_model = config.acoustic_model
        self.beam = config.beam
        self.retry_beam = config.retry_beam
        self.num_jobs = config.num_jobs
        self.single_speaker = config.single_speaker
        self.textgrid_cleanup = config.textgrid_cleanup
    
    def run_alignment(
        self, 
        corpus_dir: Path, 
        dictionary_file: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """Run forced alignment on corpus directory."""
        corpus_dir = Path(corpus_dir)
        
        if output_dir is None:
            output_dir = corpus_dir / "alignment_output"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate inputs
        self._validate_corpus(corpus_dir)
        
        if dictionary_file:
            dictionary_file = Path(dictionary_file)
            self._validate_dictionary(dictionary_file)
        
        # Prepare MFA command
        cmd = self._build_mfa_command(corpus_dir, dictionary_file, output_dir)
        
        # Run alignment
        logger.info(f"Starting MFA alignment with {self.num_jobs} jobs")
        logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            result = self._run_mfa_command(cmd)
            
            if result['success']:
                logger.info("MFA alignment completed successfully")
                alignment_results = self._collect_alignment_results(output_dir)
                
                if progress_callback:
                    progress_callback(alignment_results)
                
                return alignment_results
            else:
                raise AlignmentError(f"MFA alignment failed: {result['error']}")
        
        except Exception as e:
            raise AlignmentError(f"Alignment failed: {e}")
    
    def _validate_corpus(self, corpus_dir: Path) -> None:
        """Validate corpus directory structure."""
        if not corpus_dir.exists():
            raise AlignmentError(f"Corpus directory does not exist: {corpus_dir}")
        
        # Look for audio files
        audio_files = get_audio_files(corpus_dir)
        if not audio_files:
            raise AlignmentError(f"No audio files found in {corpus_dir}")
        
        # Look for text files
        text_files = list(corpus_dir.glob("*.txt"))
        if not text_files:
            raise AlignmentError(f"No text files found in {corpus_dir}")
        
        # Check for matching pairs
        audio_stems = {f.stem for f in audio_files}
        text_stems = {f.stem for f in text_files}
        
        matched_files = audio_stems.intersection(text_stems)
        if not matched_files:
            raise AlignmentError("No matching audio-text pairs found")
        
        logger.info(f"Found {len(matched_files)} audio-text pairs for alignment")
    
    def _validate_dictionary(self, dictionary_file: Path) -> None:
        """Validate dictionary file."""
        if not dictionary_file.exists():
            raise AlignmentError(f"Dictionary file does not exist: {dictionary_file}")
        
        if dictionary_file.stat().st_size == 0:
            raise AlignmentError(f"Dictionary file is empty: {dictionary_file}")
        
        # Basic format check
        try:
            with open(dictionary_file, 'r', encoding='utf-8') as f:
                first_few_lines = [f.readline().strip() for _ in range(5)]
                valid_lines = [line for line in first_few_lines if line and '\t' in line]
                
                if len(valid_lines) < 3:
                    logger.warning(f"Dictionary file may have format issues: {dictionary_file}")
        except Exception as e:
            raise AlignmentError(f"Failed to read dictionary file: {e}")
    
    def _build_mfa_command(
        self, 
        corpus_dir: Path, 
        dictionary_file: Optional[Path], 
        output_dir: Path
    ) -> List[str]:
        """Build MFA command with appropriate parameters."""
        cmd = [
            "mfa", "align",
            "--verbose",
            f"--beam", str(self.beam),
            f"--retry_beam", str(self.retry_beam),
            f"--num-jobs", str(self.num_jobs),
            "--clean"  # Clean temporary files
        ]
        
        # Add single speaker optimization
        if self.single_speaker:
            cmd.append("--single_speaker")
        
        # Add textgrid cleanup
        if self.textgrid_cleanup:
            cmd.append("--textgrid_cleanup")
        
        # Add acoustic model
        cmd.extend(["--acoustic_model", self.acoustic_model])
        
        # Add dictionary if provided
        if dictionary_file:
            cmd.extend(["--dictionary", str(dictionary_file)])
        
        # Add corpus and output directories
        cmd.extend([
            str(corpus_dir),
            str(output_dir)
        ])
        
        return cmd
    
    def _run_mfa_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Execute MFA command and handle results."""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=3600  # 1 hour timeout
            )
            
            elapsed_time = time.time() - start_time
            
            # Check if alignment was successful
            success = result.returncode == 0
            
            if success:
                logger.info(f"MFA alignment completed in {format_duration(elapsed_time)}")
            else:
                logger.error(f"MFA alignment failed with return code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
            
            return {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'elapsed_time': elapsed_time
            }
        
        except subprocess.TimeoutExpired:
            raise AlignmentError("MFA alignment timed out after 1 hour")
        except FileNotFoundError:
            raise AlignmentError("MFA command not found. Please install Montreal Forced Aligner.")
        except Exception as e:
            raise AlignmentError(f"Failed to run MFA command: {e}")
    
    def _collect_alignment_results(self, output_dir: Path) -> List[Dict[str, Any]]:
        """Collect and analyze alignment results."""
        results = []
        
        # Find TextGrid files
        textgrid_files = list(output_dir.glob("*.TextGrid"))
        
        if not textgrid_files:
            logger.warning("No TextGrid files found in output directory")
            return results
        
        for textgrid_file in textgrid_files:
            try:
                result = self._analyze_textgrid(textgrid_file)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to analyze {textgrid_file}: {e}")
                results.append({
                    'file': textgrid_file,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate overall statistics
        successful_alignments = sum(1 for r in results if r.get('success', False))
        total_files = len(results)
        
        logger.info(f"Alignment results: {successful_alignments}/{total_files} files aligned successfully")
        
        return results
    
    def _analyze_textgrid(self, textgrid_file: Path) -> Dict[str, Any]:
        """Analyze individual TextGrid file."""
        try:
            # Import textgrid library
            import textgrid
            
            # Load TextGrid
            tg = textgrid.TextGrid.fromFile(str(textgrid_file))
            
            # Analyze alignment quality
            alignment_info = self._extract_alignment_info(tg)
            
            return {
                'file': textgrid_file,
                'success': True,
                'tier_count': len(tg.tiers),
                'alignment_info': alignment_info,
                'file_size': textgrid_file.stat().st_size
            }
            
        except Exception as e:
            return {
                'file': textgrid_file,
                'success': False,
                'error': str(e)
            }
    
    def _extract_alignment_info(self, textgrid) -> Dict[str, Any]:
        """Extract alignment information from TextGrid."""
        info = {
            'total_segments': 0,
            'aligned_segments': 0,
            'unaligned_segments': 0,
            'total_duration': 0.0,
            'alignment_coverage': 0.0
        }
        
        try:
            for tier in textgrid.tiers:
                if hasattr(tier, 'intervals'):
                    for interval in tier.intervals:
                        info['total_segments'] += 1
                        
                        if interval.mark and interval.mark.strip():
                            info['aligned_segments'] += 1
                        else:
                            info['unaligned_segments'] += 1
                        
                        info['total_duration'] += interval.duration()
            
            # Calculate alignment coverage
            if info['total_segments'] > 0:
                info['alignment_coverage'] = info['aligned_segments'] / info['total_segments']
            
        except Exception as e:
            logger.warning(f"Failed to extract alignment info: {e}")
        
        return info
    
    def validate_alignment_quality(self, textgrid_file: Path) -> Dict[str, Any]:
        """Validate alignment quality of a TextGrid file."""
        try:
            result = self._analyze_textgrid(textgrid_file)
            
            if not result['success']:
                return {
                    'valid': False,
                    'quality_score': 0.0,
                    'issues': ['Failed to analyze file'],
                    'recommendations': ['Check file format and content']
                }
            
            alignment_info = result['alignment_info']
            quality_score = self._calculate_quality_score(alignment_info)
            issues = self._identify_quality_issues(alignment_info)
            recommendations = self._generate_recommendations(issues)
            
            return {
                'valid': True,
                'quality_score': quality_score,
                'alignment_coverage': alignment_info.get('alignment_coverage', 0.0),
                'issues': issues,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'valid': False,
                'quality_score': 0.0,
                'issues': [f'Analysis failed: {e}'],
                'recommendations': ['Check file and try again']
            }
    
    def _calculate_quality_score(self, alignment_info: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-1)."""
        score = 1.0
        
        # Alignment coverage
        coverage = alignment_info.get('alignment_coverage', 0.0)
        if coverage < 0.8:
            score *= coverage  # Heavy penalty for low coverage
        
        # Unaligned segments ratio
        total_segments = alignment_info.get('total_segments', 0)
        unaligned_segments = alignment_info.get('unaligned_segments', 0)
        
        if total_segments > 0:
            unaligned_ratio = unaligned_segments / total_segments
            if unaligned_ratio > 0.3:
                score *= (1.0 - unaligned_ratio)
        
        return max(0.0, min(1.0, score))
    
    def _identify_quality_issues(self, alignment_info: Dict[str, Any]) -> List[str]:
        """Identify specific quality issues."""
        issues = []
        
        coverage = alignment_info.get('alignment_coverage', 0.0)
        if coverage < 0.7:
            issues.append(f"Low alignment coverage: {coverage:.1%}")
        
        unaligned_ratio = 0.0
        total_segments = alignment_info.get('total_segments', 0)
        unaligned_segments = alignment_info.get('unaligned_segments', 0)
        
        if total_segments > 0:
            unaligned_ratio = unaligned_segments / total_segments
            if unaligned_ratio > 0.3:
                issues.append(f"High unaligned segment ratio: {unaligned_ratio:.1%}")
        
        if alignment_info.get('total_segments', 0) < 10:
            issues.append("Very few alignment segments")
        
        return issues
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            if "Low alignment coverage" in issue:
                recommendations.extend([
                    "Check audio quality and noise levels",
                    "Verify text matches audio content",
                    "Consider adjusting MFA beam parameters",
                    "Review pronunciation dictionary coverage"
                ])
            
            elif "High unaligned segment ratio" in issue:
                recommendations.extend([
                    "Check for silent segments in audio",
                    "Verify text segmentation",
                    "Consider using gap-filling in subtitle generation"
                ])
            
            elif "Very few alignment segments" in issue:
                recommendations.extend([
                    "Check audio duration and quality",
                    "Verify text file is not empty",
                    "Check for proper audio-text correspondence"
                ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def optimize_alignment_parameters(self, test_corpus: Path) -> Dict[str, Any]:
        """Optimize alignment parameters for specific corpus."""
        logger.info("Optimizing alignment parameters")
        
        # Test different beam parameters
        beam_options = [50, 100, 150, 200]
        retry_beam_options = [200, 400, 600, 800]
        
        best_params = None
        best_score = 0.0
        
        for beam in beam_options:
            for retry_beam in retry_beam_options:
                if retry_beam <= beam:
                    continue
                
                # Create temporary config
                temp_config = MFAConfig(
                    beam=beam,
                    retry_beam=retry_beam,
                    num_jobs=2,  # Use fewer jobs for testing
                    acoustic_model=self.acoustic_model,
                    single_speaker=self.single_speaker,
                    textgrid_cleanup=self.textgrid_cleanup
                )
                
                temp_runner = AlignmentRunner(temp_config)
                
                try:
                    # Run alignment on subset
                    results = temp_runner.run_alignment(
                        test_corpus,
                        output_dir=Path(f"temp_alignment_test_{beam}_{retry_beam}")
                    )
                    
                    # Calculate average quality score
                    quality_scores = []
                    for result in results:
                        if result.get('success'):
                            textgrid_file = result['file']
                            quality_info = temp_runner.validate_alignment_quality(textgrid_file)
                            quality_scores.append(quality_info['quality_score'])
                    
                    if quality_scores:
                        avg_score = sum(quality_scores) / len(quality_scores)
                        logger.info(f"Beam {beam}, Retry {retry_beam}: Avg score {avg_score:.3f}")
                        
                        if avg_score > best_score:
                            best_score = avg_score
                            best_params = {'beam': beam, 'retry_beam': retry_beam}
                
                except Exception as e:
                    logger.warning(f"Parameter test failed for beam={beam}, retry={retry_beam}: {e}")
        
        # Clean up temporary directories
        import shutil
        for temp_dir in Path('.').glob('temp_alignment_test_*'):
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        if best_params:
            logger.info(f"Optimal parameters: beam={best_params['beam']}, retry_beam={best_params['retry_beam']}")
            return {
                'optimal_beam': best_params['beam'],
                'optimal_retry_beam': best_params['retry_beam'],
                'best_score': best_score
            }
        else:
            logger.warning("Parameter optimization failed, using defaults")
            return {
                'optimal_beam': self.beam,
                'optimal_retry_beam': self.retry_beam,
                'best_score': 0.0
            }