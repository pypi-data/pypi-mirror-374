#!/usr/bin/env python3
"""
Complete Jebasa workflow example

This example demonstrates the full pipeline from raw Japanese audio/text files
to synchronized subtitle generation.
"""

import logging
from pathlib import Path
from jebasa import JebasaPipeline
from jebasa.config import JebasaConfig
from jebasa.cli import setup_logging

def main():
    # Set up logging
    setup_logging(verbose=True, debug=False)
    
    # Create configuration
    config = JebasaConfig()
    
    # Configure paths (using example directory structure)
    config.paths.input_dir = Path("./examples/input")
    config.paths.output_dir = Path("./examples/output")
    config.paths.work_dir = Path("./examples/work")
    config.paths.mfa_dir = Path("./examples/mfa")
    
    # Customize settings for this example
    config.audio.sample_rate = 16000
    config.mfa.num_jobs = 2  # Use fewer jobs for example
    config.subtitles.max_line_length = 35  # Shorter lines for Japanese text
    
    # Ensure directories exist
    config.paths.input_dir.mkdir(parents=True, exist_ok=True)
    config.paths.output_dir.mkdir(parents=True, exist_ok=True)
    config.paths.work_dir.mkdir(parents=True, exist_ok=True)
    config.paths.mfa_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎌 Starting Jebasa Japanese Audio-Text Alignment Pipeline")
    print(f"📁 Input directory: {config.paths.input_dir}")
    print(f"📁 Output directory: {config.paths.output_dir}")
    
    # Create the pipeline
    pipeline = JebasaPipeline(config)
    
    try:
        # Run the complete pipeline
        print("\n🔄 Running complete pipeline...")
        results = pipeline.run_all()
        
        # Display results
        print("\n✅ Pipeline completed successfully!")
        print(f"📊 Generated {len(results)} subtitle files:")
        
        for filename, result in results.items():
            print(f"  📄 {filename}")
            if 'subtitle_file' in result:
                print(f"     Subtitle: {result['subtitle_file']}")
            if 'duration' in result:
                print(f"     Duration: {result['duration']:.1f}s")
            if 'segments' in result:
                print(f"     Segments: {result['segments']}")
        
        # Show configuration used
        print(f"\n⚙️  Configuration saved to: {config.paths.output_dir}/config.yaml")
        config.to_file(config.paths.output_dir / "config.yaml")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())