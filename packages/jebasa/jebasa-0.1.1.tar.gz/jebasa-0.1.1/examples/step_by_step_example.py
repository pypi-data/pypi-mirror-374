#!/usr/bin/env python3
"""
Step-by-step Jebasa example

This example shows how to use each stage of the pipeline individually,
useful for debugging and understanding the process.
"""

import logging
from pathlib import Path
from jebasa.audio import AudioProcessor
from jebasa.text import TextProcessor
from jebasa.dictionary import DictionaryCreator
from jebasa.alignment import AlignmentRunner
from jebasa.subtitles import SubtitleGenerator
from jebasa.config import AudioConfig, TextConfig, MFAConfig, SubtitleConfig
from jebasa.cli import setup_logging

def step_1_prepare_audio():
    """Step 1: Prepare audio files for alignment"""
    print("\n🎵 Step 1: Preparing audio files...")
    
    config = AudioConfig()
    processor = AudioProcessor(config)
    
    # Process all audio files in input directory
    input_dir = Path("./examples/input/audio")
    output_dir = Path("./examples/work/audio")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_files = processor.process_audio_files(input_dir, output_dir)
    
    print(f"✅ Processed {len(processed_files)} audio files:")
    for original, processed in processed_files:
        print(f"  🎧 {original.name} → {processed.name}")
        
        # Show audio info
        info = processor.get_audio_info(processed)
        print(f"     Format: {info['format']}, Duration: {info['duration']:.1f}s, "
              f"Sample rate: {info['sample_rate']}Hz")
    
    return processed_files

def step_2_prepare_text():
    """Step 2: Prepare text files for alignment"""
    print("\n📖 Step 2: Preparing text files...")
    
    config = TextConfig(
        tokenizer="mecab",
        normalize_text=True,
        extract_furigana=True,
        min_chapter_length=50
    )
    processor = TextProcessor(config)
    
    # Process all text files in input directory
    input_dir = Path("./examples/input/text")
    output_dir = Path("./examples/work/text")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_files = processor.process_text_files(input_dir, output_dir)
    
    print(f"✅ Processed {len(processed_files)} text files:")
    for processed_file, info in processed_files:
        print(f"  📄 {processed_file.name}")
        print(f"     Chapters: {info['chapters']}, Total words: {info['words']}")
        if info['furigana_extracted']:
            print(f"     Furigana: {info['furigana_words']} words with readings")
    
    return processed_files

def step_3_create_dictionary(processed_text_files):
    """Step 3: Create pronunciation dictionary"""
    print("\n📚 Step 3: Creating pronunciation dictionary...")
    
    config = MFAConfig()
    creator = DictionaryCreator(config)
    
    # Create dictionary from processed text files
    input_dir = Path("./examples/work/text")
    output_dir = Path("./examples/work/dictionary")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    dict_results = creator.create_dictionary(input_dir, output_dir, review_file=True)
    
    print(f"✅ Dictionary created:")
    print(f"  📖 Dictionary file: {dict_results['dictionary_file']}")
    print(f"  🔤 Total entries: {dict_results['total_entries']}")
    print(f"  ✨ Custom entries: {dict_results['custom_entries']}")
    print(f"  👀 Review file: {dict_results['review_file']}")
    
    # Validate dictionary
    validation = creator.validate_dictionary(dict_results['dictionary_file'])
    print(f"  ✅ Validation: {validation['status']}")
    if validation['warnings']:
        print(f"  ⚠️  Warnings: {len(validation['warnings'])}")
    
    return dict_results

def step_4_run_alignment(dictionary_file):
    """Step 4: Run forced alignment"""
    print("\n🎯 Step 4: Running forced alignment...")
    
    config = MFAConfig(
        acoustic_model="japanese_mfa",
        beam=100,
        retry_beam=400,
        num_jobs=2,
        single_speaker=True
    )
    runner = AlignmentRunner(config)
    
    # Run alignment
    corpus_dir = Path("./examples/work")
    output_dir = Path("./examples/work/alignment")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    alignment_results = runner.run_alignment(corpus_dir, dictionary_file, output_dir)
    
    print(f"✅ Alignment completed:")
    for result in alignment_results:
        print(f"  📊 {result['file']}")
        print(f"     Status: {result['status']}")
        print(f"     Aligned words: {result['aligned_words']}")
        print(f"     Duration: {result['duration']:.1f}s")
        if result['quality_score']:
            print(f"     Quality: {result['quality_score']:.2f}")
    
    return alignment_results

def step_5_generate_subtitles():
    """Step 5: Generate subtitle files"""
    print("\n🎬 Step 5: Generating subtitles...")
    
    config = SubtitleConfig(
        max_line_length=35,
        max_lines=2,
        min_duration=1.0,
        max_duration=6.0,
        gap_filling=True
    )
    generator = SubtitleGenerator(config)
    
    # Generate subtitles
    alignment_dir = Path("./examples/work/alignment")
    text_dir = Path("./examples/work/text")
    output_dir = Path("./examples/output/subtitles")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    subtitle_results = generator.generate_subtitles(alignment_dir, text_dir, output_dir)
    
    print(f"✅ Subtitles generated:")
    for subtitle_file, info in subtitle_results:
        print(f"  📝 {subtitle_file.name}")
        print(f"     Segments: {info['segments']}")
        print(f"     Duration: {info['duration']:.1f}s")
        print(f"     Avg segment: {info['avg_segment_duration']:.1f}s")
        
        # Convert to other formats
        conversions = generator.convert_to_other_formats(subtitle_file, output_dir)
        print(f"     Formats: {', '.join(conversions.keys())}")
    
    return subtitle_results

def main():
    """Run the complete step-by-step example"""
    setup_logging(verbose=True, debug=False)
    
    print("🎌 Jebasa Step-by-Step Example")
    print("=" * 40)
    
    try:
        # Step 1: Prepare audio
        audio_files = step_1_prepare_audio()
        
        # Step 2: Prepare text
        text_files = step_2_prepare_text()
        
        # Step 3: Create dictionary
        dict_results = step_3_create_dictionary(text_files)
        
        # Step 4: Run alignment
        alignment_results = step_4_run_alignment(dict_results['dictionary_file'])
        
        # Step 5: Generate subtitles
        subtitle_results = step_5_generate_subtitles()
        
        print("\n" + "=" * 40)
        print("✅ All steps completed successfully!")
        print(f"🎬 Generated {len(subtitle_results)} subtitle files")
        print(f"📁 Output directory: ./examples/output/")
        
    except Exception as e:
        print(f"\n❌ Error in workflow: {e}")
        logging.error(f"Workflow failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())