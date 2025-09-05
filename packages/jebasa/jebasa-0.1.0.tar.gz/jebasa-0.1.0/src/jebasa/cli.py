"""Command-line interface for Jebasa."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from jebasa import __version__
from jebasa.config import get_config, JebasaConfig
from jebasa.exceptions import JebasaError
from jebasa.pipeline import JebasaPipeline
from jebasa.utils import setup_logging

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def main(ctx: click.Context, config: Optional[Path], verbose: bool, debug: bool) -> None:
    """Jebasa: Japanese ebook audio subtitle aligner.
    
    Create synchronized subtitles from Japanese audiobooks and EPUB files
    using Montreal Forced Aligner (MFA).
    """
    setup_logging(verbose=verbose, debug=debug)
    
    # Store config in context for subcommands
    ctx.ensure_object(dict)
    try:
        ctx.obj['config'] = get_config(config)
        ctx.obj['verbose'] = verbose
        ctx.obj['debug'] = debug
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option(
    "--input-dir", "-i",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Input directory containing audio and text files"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for generated files"
)
@click.option(
    "--audio-format",
    type=click.Choice(["wav", "mp3", "flac"]),
    default="wav",
    help="Output audio format"
)
@click.option(
    "--sample-rate",
    type=int,
    default=16000,
    help="Audio sample rate in Hz"
)
@click.pass_context
def prepare_audio(
    ctx: click.Context,
    input_dir: Optional[Path],
    output_dir: Optional[Path],
    audio_format: str,
    sample_rate: int
) -> None:
    """Prepare audio files for alignment.
    
    Converts audio files to the format required by MFA (16kHz, mono, WAV).
    """
    config = ctx.obj['config']
    
    # Override config with CLI options
    if input_dir:
        config.paths.input_dir = input_dir
    if output_dir:
        config.paths.output_dir = output_dir
    if audio_format:
        config.audio.format = audio_format
    if sample_rate:
        config.audio.sample_rate = sample_rate
    
    try:
        pipeline = JebasaPipeline(config)
        
        with console.status("[bold green]Preparing audio files..."):
            processed_files = pipeline.prepare_audio()
        
        console.print(f"[green]✓[/green] Processed {len(processed_files)} audio files")
        
        # Show summary table
        table = Table(title="Audio Processing Summary")
        table.add_column("Original File", style="cyan")
        table.add_column("Processed File", style="green")
        table.add_column("Duration", style="yellow")
        
        for orig, proc in processed_files:
            table.add_row(str(orig.name), str(proc.name), "processed")
        
        console.print(table)
        
    except JebasaError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--input-dir", "-i",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Input directory containing text files"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for processed text files"
)
@click.option(
    "--tokenizer",
    type=click.Choice(["mecab", "janome"]),
    default="mecab",
    help="Japanese tokenizer to use"
)
@click.option(
    "--extract-furigana/--no-extract-furigana",
    default=True,
    help="Extract furigana annotations"
)
@click.pass_context
def prepare_text(
    ctx: click.Context,
    input_dir: Optional[Path],
    output_dir: Optional[Path],
    tokenizer: str,
    extract_furigana: bool
) -> None:
    """Prepare text files for alignment.
    
    Extracts and processes text from EPUB/XHTML files, handles furigana annotations,
    and creates tokenized text suitable for MFA alignment.
    """
    config = ctx.obj['config']
    
    # Override config with CLI options
    if input_dir:
        config.paths.input_dir = input_dir
    if output_dir:
        config.paths.output_dir = output_dir
    if tokenizer:
        config.text.tokenizer = tokenizer
    config.text.extract_furigana = extract_furigana
    
    try:
        pipeline = JebasaPipeline(config)
        
        with console.status("[bold green]Preparing text files..."):
            processed_files = pipeline.prepare_text()
        
        console.print(f"[green]✓[/green] Processed {len(processed_files)} text files")
        
        # Show furigana extraction summary
        if extract_furigana:
            furigana_count = sum(1 for _, info in processed_files if info.get('furigana_found'))
            console.print(f"[blue]ℹ[/blue] Found furigana in {furigana_count} files")
        
    except JebasaError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--input-dir", "-i",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Input directory containing processed text files"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for dictionary files"
)
@click.option(
    "--review/--no-review",
    default=True,
    help="Generate review file for manual verification"
)
@click.pass_context
def create_dictionary(
    ctx: click.Context,
    input_dir: Optional[Path],
    output_dir: Optional[Path],
    review: bool
) -> None:
    """Create pronunciation dictionary for MFA.
    
    Generates custom pronunciation dictionary from furigana annotations and
    combines with base MFA dictionary.
    """
    config = ctx.obj['config']
    
    # Override config with CLI options
    if input_dir:
        config.paths.input_dir = input_dir
    if output_dir:
        config.paths.output_dir = output_dir
    
    try:
        pipeline = JebasaPipeline(config)
        
        with console.status("[bold green]Creating pronunciation dictionary..."):
            dict_info = pipeline.create_dictionary(review_file=review)
        
        console.print(f"[green]✓[/green] Dictionary created: {dict_info['dictionary_file']}")
        console.print(f"[blue]ℹ[/blue] Total entries: {dict_info['total_entries']}")
        console.print(f"[blue]ℹ[/blue] Custom entries: {dict_info['custom_entries']}")
        
        if review and dict_info.get('review_entries'):
            console.print(f"[yellow]⚠[/yellow] {len(dict_info['review_entries'])} entries need review")
            console.print(f"Review file: {dict_info['review_file']}")
        
    except JebasaError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--corpus-dir", "-c",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing audio-text pairs for alignment"
)
@click.option(
    "--dictionary",
    type=click.Path(exists=True, path_type=Path),
    help="Pronunciation dictionary file"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for alignment results"
)
@click.option(
    "--num-jobs", "-j",
    type=int,
    default=4,
    help="Number of parallel jobs"
)
@click.pass_context
def align(
    ctx: click.Context,
    corpus_dir: Optional[Path],
    dictionary: Optional[Path],
    output_dir: Optional[Path],
    num_jobs: int
) -> None:
    """Run Montreal Forced Aligner.
    
    Performs forced alignment between audio and text files using MFA.
    """
    config = ctx.obj['config']
    
    # Override config with CLI options
    if corpus_dir:
        config.paths.input_dir = corpus_dir
    if output_dir:
        config.paths.output_dir = output_dir
    if num_jobs:
        config.mfa.num_jobs = num_jobs
    
    try:
        pipeline = JebasaPipeline(config)
        
        with console.status("[bold green]Running forced alignment..."):
            alignment_results = pipeline.run_alignment(dictionary)
        
        console.print(f"[green]✓[/green] Alignment completed")
        console.print(f"[blue]ℹ[/blue] Aligned files: {len(alignment_results)}")
        
        # Show alignment statistics
        successful = sum(1 for r in alignment_results if r.get('success', False))
        failed = len(alignment_results) - successful
        
        if failed > 0:
            console.print(f"[yellow]⚠[/yellow] {failed} files failed alignment")
        
        console.print(f"[green]✓[/green] {successful} files aligned successfully")
        
    except JebasaError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--alignment-dir", "-a",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing TextGrid alignment files"
)
@click.option(
    "--text-dir", "-t",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing original text files"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for SRT files"
)
@click.option(
    "--max-line-length",
    type=int,
    default=42,
    help="Maximum characters per subtitle line"
)
@click.pass_context
def generate_subtitles(
    ctx: click.Context,
    alignment_dir: Optional[Path],
    text_dir: Optional[Path],
    output_dir: Optional[Path],
    max_line_length: int
) -> None:
    """Generate SRT subtitle files.
    
    Converts MFA TextGrid output to SRT format with proper timing and text formatting.
    """
    config = ctx.obj['config']
    
    # Override config with CLI options
    if alignment_dir:
        config.paths.input_dir = alignment_dir
    if text_dir:
        config.paths.temp_dir = text_dir  # Store text dir in temp for this command
    if output_dir:
        config.paths.output_dir = output_dir
    if max_line_length:
        config.subtitles.max_line_length = max_line_length
    
    try:
        pipeline = JebasaPipeline(config)
        
        with console.status("[bold green]Generating subtitle files..."):
            subtitle_files = pipeline.generate_subtitles()
        
        console.print(f"[green]✓[/green] Generated {len(subtitle_files)} subtitle files")
        
        # Show subtitle statistics
        total_subtitles = sum(info['subtitle_count'] for _, info in subtitle_files)
        console.print(f"[blue]ℹ[/blue] Total subtitles created: {total_subtitles}")
        
    except JebasaError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--input-dir", "-i",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Input directory containing audio and text files"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(path_type=Path),
    help="Output directory for all generated files"
)
@click.option(
    "--skip-preparation",
    is_flag=True,
    help="Skip audio/text preparation (use pre-processed files)"
)
@click.pass_context
def run(
    ctx: click.Context,
    input_dir: Optional[Path],
    output_dir: Optional[Path],
    skip_preparation: bool
) -> None:
    """Run complete alignment pipeline.
    
    Executes all stages: audio preparation, text processing, dictionary creation,
    alignment, and subtitle generation.
    """
    config = ctx.obj['config']
    
    # Override config with CLI options
    if input_dir:
        config.paths.input_dir = input_dir
    if output_dir:
        config.paths.output_dir = output_dir
    
    try:
        pipeline = JebasaPipeline(config)
        
        with console.status("[bold green]Running complete pipeline..."):
            results = pipeline.run_all(skip_preparation=skip_preparation)
        
        console.print(f"[green]✓[/green] Pipeline completed successfully!")
        
        # Show final summary
        table = Table(title="Pipeline Results")
        table.add_column("Stage", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Files Processed", style="yellow")
        
        for stage, info in results.items():
            status = "✓ Completed" if info['success'] else "✗ Failed"
            count = info.get('file_count', 0)
            table.add_row(stage.replace('_', ' ').title(), status, str(count))
        
        console.print(table)
        
        # Show output location
        console.print(f"\n[blue]ℹ[/blue] Output files saved to: {config.paths.output_dir}")
        
    except JebasaError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def info(ctx: click.Context, audio_file: Path) -> None:
    """Show information about an audio file."""
    from jebasa.audio import AudioProcessor
    
    config = ctx.obj['config']
    
    try:
        processor = AudioProcessor(config.audio)
        info = processor.get_audio_info(audio_file)
        
        table = Table(title=f"Audio File Information: {audio_file.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in info.items():
            if key == 'duration':
                value = f"{value:.2f} seconds"
            elif key == 'sample_rate':
                value = f"{value} Hz"
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)
        
        # Validate quality
        is_valid = processor.validate_audio_quality(audio_file)
        if is_valid:
            console.print("[green]✓ Audio file meets alignment requirements[/green]")
        else:
            console.print("[yellow]⚠ Audio file may have quality issues[/yellow]")
        
    except JebasaError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Show current configuration."""
    config = ctx.obj['config']
    
    table = Table(title="Jebasa Configuration")
    table.add_column("Section", style="cyan")
    table.add_column("Setting", style="yellow")
    table.add_column("Value", style="green")
    
    # Audio config
    for key, value in config.audio.dict().items():
        table.add_row("Audio", key.replace('_', ' ').title(), str(value))
    
    # Text config
    for key, value in config.text.dict().items():
        table.add_row("Text", key.replace('_', ' ').title(), str(value))
    
    # MFA config
    for key, value in config.mfa.dict().items():
        table.add_row("MFA", key.replace('_', ' ').title(), str(value))
    
    # Subtitle config
    for key, value in config.subtitles.dict().items():
        table.add_row("Subtitles", key.replace('_', ' ').title(), str(value))
    
    # Path config
    for key, value in config.paths.dict().items():
        table.add_row("Paths", key.replace('_', ' ').title(), str(value))
    
    console.print(table)


if __name__ == "__main__":
    main()