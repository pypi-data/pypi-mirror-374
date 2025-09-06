"""Subtitle generation functionality for Jebasa."""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import textgrid
from datetime import timedelta

from jebasa.config import SubtitleConfig
from jebasa.exceptions import SubtitleGenerationError
from jebasa.utils import format_duration, chunk_text, safe_filename

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """Generate SRT subtitle files from alignment results."""
    
    def __init__(self, config: SubtitleConfig):
        self.config = config
        self.max_line_length = config.max_line_length
        self.max_lines = config.max_lines
        self.min_duration = config.min_duration
        self.max_duration = config.max_duration
        self.gap_filling = config.gap_filling
    
    def generate_subtitles(
        self,
        alignment_dir: Path,
        text_dir: Path,
        output_dir: Path,
        progress_callback: Optional[callable] = None
    ) -> List[Tuple[Path, Dict[str, Any]]]:
        """Generate SRT subtitles from alignment results."""
        alignment_dir = Path(alignment_dir)
        text_dir = Path(text_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find TextGrid files
        textgrid_files = list(alignment_dir.glob("*.TextGrid"))
        
        if not textgrid_files:
            raise SubtitleGenerationError(f"No TextGrid files found in {alignment_dir}")
        
        generated_files = []
        
        for textgrid_file in textgrid_files:
            try:
                # Find corresponding text file
                text_file = self._find_text_file(textgrid_file, text_dir)
                
                # Generate subtitle
                subtitle_file = self._generate_single_subtitle(
                    textgrid_file, text_file, output_dir
                )
                
                info = self._get_subtitle_info(subtitle_file)
                generated_files.append((subtitle_file, info))
                
                if progress_callback:
                    progress_callback(textgrid_file, subtitle_file)
                
                logger.info(f"Generated subtitle: {subtitle_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to generate subtitle for {textgrid_file}: {e}")
                raise SubtitleGenerationError(f"Subtitle generation failed for {textgrid_file}: {e}")
        
        return generated_files
    
    def _find_text_file(self, textgrid_file: Path, text_dir: Path) -> Optional[Path]:
        """Find corresponding text file for TextGrid."""
        base_name = textgrid_file.stem
        
        # Try different naming patterns
        patterns = [
            f"{base_name}_clean.txt",
            f"{base_name}.txt",
            f"{base_name}_mfa.txt",
            f"{base_name}_original.txt"
        ]
        
        for pattern in patterns:
            text_file = text_dir / pattern
            if text_file.exists():
                return text_file
        
        # Try without suffixes
        for suffix in ['_clean', '_mfa', '_aligned', '']:
            clean_name = base_name.replace(suffix, '')
            for pattern in [f"{clean_name}.txt", f"{clean_name}_clean.txt"]:
                text_file = text_dir / pattern
                if text_file.exists():
                    return text_file
        
        logger.warning(f"No text file found for {textgrid_file}")
        return None
    
    def _generate_single_subtitle(
        self, 
        textgrid_file: Path, 
        text_file: Optional[Path], 
        output_dir: Path
    ) -> Path:
        """Generate subtitle for single TextGrid file."""
        try:
            # Load TextGrid
            tg = textgrid.TextGrid.fromFile(str(textgrid_file))
            
            # Extract alignment segments
            segments = self._extract_segments(tg)
            
            # Load original text if available
            original_text = ""
            if text_file:
                original_text = text_file.read_text(encoding='utf-8')
            
            # Process segments
            processed_segments = self._process_segments(segments, original_text)
            
            # Apply gap filling if enabled
            if self.gap_filling:
                processed_segments = self._fill_gaps(processed_segments)
            
            # Generate SRT content
            srt_content = self._generate_srt_content(processed_segments)
            
            # Save SRT file
            output_file = output_dir / f"{textgrid_file.stem}.srt"
            output_file.write_text(srt_content, encoding='utf-8')
            
            return output_file
            
        except Exception as e:
            raise SubtitleGenerationError(f"Failed to generate subtitle for {textgrid_file}: {e}")
    
    def _extract_segments(self, textgrid) -> List[Dict[str, Any]]:
        """Extract alignment segments from TextGrid."""
        segments = []
        
        try:
            # Look for word or phone tiers
            target_tiers = []
            for tier in textgrid.tiers:
                if 'word' in tier.name.lower() or 'phone' in tier.name.lower():
                    target_tiers.append(tier)
            
            # If no specific tiers found, use all tiers
            if not target_tiers:
                target_tiers = textgrid.tiers
            
            for tier in target_tiers:
                if hasattr(tier, 'intervals'):
                    for interval in tier.intervals:
                        if interval.mark and interval.mark.strip():
                            segments.append({
                                'start': interval.minTime,
                                'end': interval.maxTime,
                                'text': interval.mark.strip(),
                                'tier': tier.name
                            })
        
        except Exception as e:
            logger.warning(f"Failed to extract segments from TextGrid: {e}")
        
        return segments
    
    def _process_segments(
        self, 
        segments: List[Dict[str, Any]], 
        original_text: str
    ) -> List[Dict[str, Any]]:
        """Process alignment segments for subtitle generation."""
        if not segments:
            return []
        
        processed = []
        
        # Group segments into sentences
        sentences = self._group_into_sentences(segments)
        
        for sentence in sentences:
            # Calculate sentence timing
            start_time = sentence[0]['start']
            end_time = sentence[-1]['end']
            duration = end_time - start_time
            
            # Combine text
            combined_text = self._combine_sentence_text(sentence)
            
            # Apply subtitle formatting
            formatted_text = self._format_subtitle_text(combined_text)
            
            # Validate duration
            if duration < self.min_duration:
                logger.debug(f"Skipping short sentence: {duration:.2f}s")
                continue
            
            if duration > self.max_duration:
                # Split long sentences
                split_sentences = self._split_long_sentence(sentence)
                for split_sentence in split_sentences:
                    processed.extend(self._process_segments(split_sentence, original_text))
                continue
            
            processed.append({
                'start': start_time,
                'end': end_time,
                'duration': duration,
                'text': formatted_text,
                'original_segments': len(sentence)
            })
        
        return processed
    
    def _group_into_sentences(self, segments: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group segments into sentences based on Japanese punctuation."""
        sentences = []
        current_sentence = []
        
        sentence_endings = ['。', '！', '？', '!', '?', '．']
        
        for segment in segments:
            current_sentence.append(segment)
            
            # Check for sentence ending
            text = segment['text']
            if any(ending in text for ending in sentence_endings):
                sentences.append(current_sentence)
                current_sentence = []
        
        # Add remaining segments
        if current_sentence:
            sentences.append(current_sentence)
        
        return sentences
    
    def _combine_sentence_text(self, sentence: List[Dict[str, Any]]) -> str:
        """Combine text from sentence segments."""
        texts = []
        
        for segment in sentence:
            text = segment['text']
            
            # Clean up text
            text = text.strip()
            
            # Handle common formatting issues
            text = re.sub(r'\s+', ' ', text)
            
            if text:
                texts.append(text)
        
        return ' '.join(texts)
    
    def _format_subtitle_text(self, text: str) -> str:
        """Format text for subtitle display."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle Japanese punctuation
        text = text.replace('。', '.')
        text = text.replace('、', ',')
        text = text.replace('！', '!')
        text = text.replace('？', '?')
        
        # Split into lines if too long
        if len(text) > self.max_line_length * self.max_lines:
            lines = chunk_text(text, self.max_line_length, self.max_lines)
            text = '\n'.join(lines)
        elif len(text) > self.max_line_length:
            # Simple line break
            mid_point = len(text) // 2
            # Find good break point (space or punctuation)
            break_point = mid_point
            for i in range(mid_point - 10, mid_point + 10):
                if 0 <= i < len(text) and text[i] in ' 、。！？,.':
                    break_point = i + 1
                    break
            
            text = text[:break_point].strip() + '\n' + text[break_point:].strip()
        
        return text
    
    def _split_long_sentence(
        self, 
        sentence: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Split long sentence into shorter parts."""
        # Calculate target split points
        total_duration = sentence[-1]['end'] - sentence[0]['start']
        num_parts = int(total_duration / self.max_duration) + 1
        
        # Split segments evenly
        segments_per_part = len(sentence) // num_parts
        if segments_per_part < 1:
            segments_per_part = 1
        
        split_sentences = []
        for i in range(0, len(sentence), segments_per_part):
            split_sentences.append(sentence[i:i + segments_per_part])
        
        return split_sentences
    
    def _fill_gaps(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fill gaps between aligned segments."""
        if not segments:
            return segments
        
        filled_segments = []
        
        for i in range(len(segments)):
            current = segments[i]
            filled_segments.append(current)
            
            # Check for gap with next segment
            if i < len(segments) - 1:
                next_segment = segments[i + 1]
                gap_start = current['end']
                gap_end = next_segment['start']
                gap_duration = gap_end - gap_start
                
                # Fill significant gaps (0.5s or more)
                if gap_duration >= 0.5:
                    # Calculate proportional text for gap
                    gap_text = self._generate_gap_text(current, next_segment, gap_duration)
                    
                    if gap_text:
                        filled_segments.append({
                            'start': gap_start,
                            'end': gap_end,
                            'duration': gap_duration,
                            'text': gap_text,
                            'is_gap_fill': True
                        })
        
        return filled_segments
    
    def _generate_gap_text(
        self, 
        previous: Dict[str, Any], 
        next_segment: Dict[str, Any], 
        gap_duration: float
    ) -> str:
        """Generate text for gap between segments."""
        # Simple implementation - could be enhanced with more sophisticated logic
        
        # If gap is very short, just extend previous/next
        if gap_duration < 1.0:
            return ""
        
        # For longer gaps, could use silence marker or context
        return "..."
    
    def _generate_srt_content(self, segments: List[Dict[str, Any]]) -> str:
        """Generate SRT format content from segments."""
        srt_lines = []
        
        for i, segment in enumerate(segments):
            # SRT subtitle number
            srt_lines.append(str(i + 1))
            
            # Time range
            start_time = self._format_srt_time(segment['start'])
            end_time = self._format_srt_time(segment['end'])
            srt_lines.append(f"{start_time} --> {end_time}")
            
            # Text content
            text = segment['text']
            if text.strip():
                srt_lines.append(text)
            
            # Empty line between subtitles
            srt_lines.append("")
        
        return '\n'.join(srt_lines)
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format time in SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        milliseconds = int((secs % 1) * 1000)
        secs = int(secs)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _get_subtitle_info(self, subtitle_file: Path) -> Dict[str, Any]:
        """Get information about generated subtitle file."""
        try:
            content = subtitle_file.read_text(encoding='utf-8')
            lines = content.strip().split('\n')
            
            # Count subtitles (look for time codes)
            subtitle_count = 0
            total_duration = 0.0
            
            for i, line in enumerate(lines):
                if '-->' in line:
                    subtitle_count += 1
                    # Parse time to calculate duration
                    try:
                        times = line.split('-->')
                        if len(times) == 2:
                            start_time = self._parse_srt_time(times[0].strip())
                            end_time = self._parse_srt_time(times[1].strip())
                            total_duration = max(total_duration, end_time)
                    except ValueError:
                        pass
            
            return {
                'filename': subtitle_file.name,
                'subtitle_count': subtitle_count,
                'total_duration': total_duration,
                'file_size': subtitle_file.stat().st_size,
                'avg_subtitle_duration': total_duration / subtitle_count if subtitle_count > 0 else 0
            }
            
        except Exception as e:
            logger.warning(f"Failed to get subtitle info for {subtitle_file}: {e}")
            return {'filename': subtitle_file.name, 'error': str(e)}
    
    def _parse_srt_time(self, time_str: str) -> float:
        """Parse SRT time format to seconds."""
        try:
            # Handle format: HH:MM:SS,mmm or HH:MM:SS.mmm
            time_str = time_str.strip()
            if ',' in time_str:
                time_part, ms_part = time_str.split(',')
            elif '.' in time_str:
                time_part, ms_part = time_str.split('.')
            else:
                time_part = time_str
                ms_part = '000'
            
            # Parse time part
            if ':' in time_part:
                parts = time_part.split(':')
                if len(parts) == 3:
                    hours, minutes, seconds = parts
                    total_seconds = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
                elif len(parts) == 2:
                    minutes, seconds = parts
                    total_seconds = float(minutes) * 60 + float(seconds)
                else:
                    total_seconds = float(parts[0])
            else:
                total_seconds = float(time_part)
            
            # Add milliseconds
            milliseconds = float(ms_part) / 1000.0
            return total_seconds + milliseconds
            
        except ValueError as e:
            raise ValueError(f"Invalid SRT time format: {time_str}") from e
    
    def validate_subtitle_file(self, subtitle_file: Path) -> Dict[str, Any]:
        """Validate SRT subtitle file format and content."""
        try:
            content = subtitle_file.read_text(encoding='utf-8')
            lines = content.strip().split('\n')
            
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'subtitle_count': 0,
                'timing_issues': 0,
                'formatting_issues': 0
            }
            
            expected_subtitle_num = 1
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines
                if not line:
                    i += 1
                    continue
                
                # Check subtitle number
                try:
                    subtitle_num = int(line)
                    if subtitle_num != expected_subtitle_num:
                        validation_results['warnings'].append(
                            f"Subtitle number mismatch at line {i+1}: expected {expected_subtitle_num}, got {subtitle_num}"
                        )
                    expected_subtitle_num += 1
                except ValueError:
                    validation_results['errors'].append(f"Invalid subtitle number at line {i+1}: '{line}'")
                    validation_results['valid'] = False
                
                i += 1
                if i >= len(lines):
                    break
                
                # Check time code
                time_line = lines[i].strip()
                if '-->' not in time_line:
                    validation_results['errors'].append(f"Missing time code at line {i+1}: '{time_line}'")
                    validation_results['valid'] = False
                else:
                    # Validate time format
                    try:
                        times = time_line.split('-->')
                        if len(times) != 2:
                            validation_results['errors'].append(f"Invalid time code format at line {i+1}: '{time_line}'")
                            validation_results['valid'] = False
                        else:
                            start_time = self._parse_srt_time(times[0].strip())
                            end_time = self._parse_srt_time(times[1].strip())
                            
                            if start_time >= end_time:
                                validation_results['errors'].append(f"Invalid time range at line {i+1}: start {start_time} >= end {end_time}")
                                validation_results['valid'] = False
                            elif end_time - start_time > 10.0:  # Very long subtitle
                                validation_results['warnings'].append(f"Very long subtitle duration at line {i+1}: {end_time - start_time:.1f}s")
                                
                    except ValueError as e:
                        validation_results['errors'].append(f"Invalid time format at line {i+1}: {e}")
                        validation_results['valid'] = False
                
                i += 1
                
                # Check text content (skip empty lines)
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1
                
                if not text_lines:
                    validation_results['warnings'].append(f"Empty subtitle text for subtitle {subtitle_num}")
                else:
                    validation_results['subtitle_count'] += 1
                    
                    # Check text length
                    text_content = ' '.join(text_lines)
                    if len(text_content) > 100:  # Very long subtitle
                        validation_results['warnings'].append(f"Very long subtitle text for subtitle {subtitle_num}: {len(text_content)} characters")
                
                # Skip empty line after subtitle
                if i < len(lines) and not lines[i].strip():
                    i += 1
            
            # Final checks
            if validation_results['subtitle_count'] == 0:
                validation_results['errors'].append("No valid subtitles found")
                validation_results['valid'] = False
            
            return validation_results
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation failed: {e}"],
                'warnings': [],
                'subtitle_count': 0,
                'timing_issues': 0,
                'formatting_issues': 0
            }
    
    def convert_to_other_formats(self, srt_file: Path, output_dir: Path) -> Dict[str, Path]:
        """Convert SRT to other subtitle formats."""
        converted_files = {}
        
        try:
            # Convert to VTT (WebVTT)
            vtt_file = self._convert_srt_to_vtt(srt_file, output_dir)
            if vtt_file:
                converted_files['vtt'] = vtt_file
            
            # Convert to TTML (Timed Text)
            ttml_file = self._convert_srt_to_ttml(srt_file, output_dir)
            if ttml_file:
                converted_files['ttml'] = ttml_file
            
            # Convert to plain text transcript
            transcript_file = self._convert_srt_to_transcript(srt_file, output_dir)
            if transcript_file:
                converted_files['transcript'] = transcript_file
            
            return converted_files
            
        except Exception as e:
            logger.warning(f"Format conversion failed: {e}")
            return {}
    
    def _convert_srt_to_vtt(self, srt_file: Path, output_dir: Path) -> Optional[Path]:
        """Convert SRT to WebVTT format."""
        try:
            content = srt_file.read_text(encoding='utf-8')
            
            # Convert time format and add WebVTT header
            vtt_content = "WEBVTT\n\n"
            
            lines = content.strip().split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                # Skip subtitle numbers
                if line.isdigit():
                    i += 1
                    continue
                
                # Convert time line
                if '-->' in line:
                    # Convert comma to dot for milliseconds
                    vtt_line = line.replace(',', '.')
                    vtt_content += vtt_line + '\n'
                    i += 1
                    continue
                
                # Copy text lines
                if line:
                    vtt_content += line + '\n'
                
                i += 1
            
            # Add final newline
            vtt_content += '\n'
            
            output_file = output_dir / f"{srt_file.stem}.vtt"
            output_file.write_text(vtt_content, encoding='utf-8')
            
            return output_file
            
        except Exception as e:
            logger.warning(f"SRT to VTT conversion failed: {e}")
            return None
    
    def _convert_srt_to_ttml(self, srt_file: Path, output_dir: Path) -> Optional[Path]:
        """Convert SRT to TTML format."""
        try:
            content = srt_file.read_text(encoding='utf-8')
            
            # Basic TTML structure
            ttml_content = """?xml version="1.0" encoding="UTF-8"?>
<ttm xmlns="http://www.w3.org/ns/ttml" xml:lang="ja">
<head>
    <metadata>
        <ttm:title>{title}</ttm:title>
    </metadata>
</head>
<body>
    <div>
""".format(title=srt_file.stem)
            
            lines = content.strip().split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                if not line or line.isdigit():
                    i += 1
                    continue
                
                if '-->' in line:
                    # Parse time
                    times = line.split('-->')
                    start_time = times[0].strip().replace(',', '.')
                    end_time = times[1].strip().replace(',', '.')
                    
                    # Get text
                    text_lines = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                        text_lines.append(lines[i].strip())
                        i += 1
                    
                    if text_lines:
                        text_content = ' '.join(text_lines)
                        text_content = text_content.replace('\n', '\u003cbr/\u003e')
                        
                        ttml_content += f'        \u003cp begin="{start_time}" end="{end_time}"\u003e{text_content}\u003c/p\u003e\n'
                    
                    continue
                
                i += 1
            
            ttml_content += """    \u003c/div>
\u003c/body>
\u003c/ttm>"""
            
            output_file = output_dir / f"{srt_file.stem}.ttml"
            output_file.write_text(ttml_content, encoding='utf-8')
            
            return output_file
            
        except Exception as e:
            logger.warning(f"SRT to TTML conversion failed: {e}")
            return None
    
    def _convert_srt_to_transcript(self, srt_file: Path, output_dir: Path) -> Optional[Path]:
        """Convert SRT to plain text transcript."""
        try:
            content = srt_file.read_text(encoding='utf-8')
            
            transcript_lines = []
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Skip subtitle numbers, time codes, and empty lines
                if (not line or 
                    line.isdigit() or 
                    '-->' in line or 
                    line.startswith('WEBVTT')):
                    continue
                
                transcript_lines.append(line)
            
            transcript_content = ' '.join(transcript_lines)
            transcript_content = re.sub(r'\s+', ' ', transcript_content).strip()
            
            output_file = output_dir / f"{srt_file.stem}_transcript.txt"
            output_file.write_text(transcript_content, encoding='utf-8')
            
            return output_file
            
        except Exception as e:
            logger.warning(f"SRT to transcript conversion failed: {e}")
            return None