"""Main analyze command for processing code and generating questions."""

import asyncio
import click
from pathlib import Path
from typing import List, Optional

from ...models.question_models import QuestionCategory, DifficultyLevel
from ...core.application import initialize_application
from ..utils.validators import validate_directory, validate_output_path, validate_categories, validate_difficulties
from ..utils.formatters import format_results, format_error, format_progress
from ..utils.progress import ProgressDisplay


@click.command()
@click.argument('directory', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o',
              type=click.Path(path_type=Path),
              help='Output file or directory path')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'markdown', 'both', 'structured']),
              default='json',
              help='Output format')
@click.option('--categories', '-c',
              multiple=True,
              type=click.Choice([cat.value for cat in QuestionCategory]),
              help='Question categories to generate (can be used multiple times)')
@click.option('--difficulty', '-d',
              multiple=True,
              type=click.Choice([level.value for level in DifficultyLevel]),
              help='Difficulty levels to include (can be used multiple times)')
@click.option('--max-questions', '-n',
              type=click.IntRange(1, 50),
              default=10,
              help='Maximum number of questions to generate')
@click.option('--config', '-cfg',
              type=click.Path(exists=True, path_type=Path),
              help='Path to configuration file')
@click.option('--dry-run',
              is_flag=True,
              help='Show what would be analyzed without making API calls')
@click.option('--quiet', '-q',
              is_flag=True,
              help='Suppress progress output')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose output')
@click.pass_context
def analyze(ctx, directory: Path, output: Optional[Path], output_format: str,
           categories: tuple, difficulty: tuple, max_questions: int,
           config: Optional[Path], dry_run: bool, quiet: bool, verbose: bool):
    """
    Analyze Python code and generate interview questions.
    
    DIRECTORY: Path to the directory containing Python files to analyze.
    
    Examples:
    
      # Basic analysis with JSON output
      interview-generator analyze /path/to/code
      
      # Generate specific question types
      interview-generator analyze /path/to/code -c comprehension -c debugging
      
      # Export to structured format with reports
      interview-generator analyze /path/to/code -f structured -o ./results
      
      # Advanced filtering
      interview-generator analyze /path/to/code \\
        --categories comprehension debugging optimization \\
        --difficulty intermediate advanced \\
        --max-questions 15 \\
        --output questions.json
    """
    try:
        # Validate inputs
        if not validate_directory(directory):
            click.echo(format_error(f"Invalid directory: {directory}"), err=True)
            ctx.exit(1)
        
        if output and not validate_output_path(output, output_format):
            click.echo(format_error(f"Invalid output path: {output}"), err=True)
            ctx.exit(1)
        
        # Convert categories and difficulties
        selected_categories = None
        if categories:
            selected_categories = validate_categories(list(categories))
            if not selected_categories:
                click.echo(format_error("Invalid categories specified"), err=True)
                ctx.exit(1)
        
        selected_difficulties = None
        if difficulty:
            selected_difficulties = validate_difficulties(list(difficulty))
            if not selected_difficulties:
                click.echo(format_error("Invalid difficulty levels specified"), err=True)
                ctx.exit(1)
        
        # Initialize application
        if not quiet:
            click.echo("🚀 Initializing Interview Question Generator...")
        
        app = initialize_application(config, verbose)
        
        # Show configuration info if verbose
        if verbose:
            config_info = app.get_config_info()
            click.echo(f"📋 Configuration: {config_info['config_path']}")
            click.echo(f"🤖 LLM Model: {config_info['llm_model']}")
            click.echo(f"🔑 API Key: {'✓ Configured' if config_info['api_key_configured'] else '✗ Missing'}")
        
        # Dry run mode
        if dry_run:
            _perform_dry_run(directory, selected_categories, selected_difficulties, max_questions)
            return
        
        # Run the analysis
        result = asyncio.run(_run_analysis(
            app, directory, selected_categories, selected_difficulties,
            max_questions, output, output_format, quiet
        ))
        
        # Display results
        if not quiet:
            click.echo(format_results(result))
        
        # Exit with appropriate code
        ctx.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        click.echo("\n⚠️  Analysis cancelled by user", err=True)
        ctx.exit(130)
    except Exception as e:
        click.echo(format_error(f"Analysis failed: {str(e)}"), err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)


async def _run_analysis(app, directory: Path, categories: Optional[List[QuestionCategory]],
                       difficulties: Optional[List[DifficultyLevel]], max_questions: int,
                       output: Optional[Path], output_format: str, quiet: bool):
    """Run the complete analysis pipeline."""
    
    progress_display = None
    if not quiet:
        progress_display = ProgressDisplay()
        progress_display.start("Starting analysis...")
    
    def progress_callback(message: str, progress: float):
        if progress_display:
            progress_display.update(message, progress)
    
    try:
        # Run pipeline
        result = await app.pipeline.process_directory(
            directory=directory,
            categories=categories,
            difficulties=difficulties,
            max_questions=max_questions,
            output_path=output,
            output_format=output_format,
            progress_callback=progress_callback if not quiet else None
        )
        
        if progress_display:
            if result.success:
                progress_display.complete("✅ Analysis completed successfully!")
            else:
                progress_display.fail("❌ Analysis failed")
        
        return result
        
    finally:
        if progress_display:
            progress_display.stop()
        
        # Cleanup
        await app.shutdown()


def _perform_dry_run(directory: Path, categories: Optional[List[QuestionCategory]],
                    difficulties: Optional[List[DifficultyLevel]], max_questions: int):
    """Perform a dry run showing what would be analyzed."""
    
    click.echo("🔍 Dry Run Mode - No API calls will be made")
    click.echo("=" * 50)
    
    # Show what would be analyzed
    from ...utils.file_discovery import FileDiscovery
    
    file_discovery = FileDiscovery()
    python_files = file_discovery.find_python_files(directory)
    
    click.echo(f"📁 Directory: {directory}")
    click.echo(f"📄 Python files found: {len(python_files)}")
    
    if len(python_files) <= 10:
        for file_path in python_files:
            click.echo(f"   - {file_path.relative_to(directory)}")
    else:
        for file_path in python_files[:5]:
            click.echo(f"   - {file_path.relative_to(directory)}")
        click.echo(f"   ... and {len(python_files) - 5} more files")
    
    click.echo()
    click.echo("🎯 Question Generation Plan:")
    click.echo(f"   - Categories: {[cat.value for cat in categories] if categories else 'All available'}")
    click.echo(f"   - Difficulties: {[diff.value for diff in difficulties] if difficulties else 'All levels'}")
    click.echo(f"   - Max questions: {max_questions}")
    
    click.echo()
    click.echo("📊 Estimated Processing:")
    
    # Estimate processing time and API calls
    estimated_api_calls = len(python_files) * (len(categories) if categories else 5)
    estimated_time = estimated_api_calls * 2  # ~2 seconds per API call
    
    click.echo(f"   - Estimated API calls: {estimated_api_calls}")
    click.echo(f"   - Estimated time: {estimated_time // 60}m {estimated_time % 60}s")
    click.echo(f"   - Estimated tokens: {estimated_api_calls * 200}")
    
    click.echo()
    click.echo("💡 To run the actual analysis, remove the --dry-run flag")


# Add command aliases and shortcuts
@click.command(name='quick')
@click.argument('directory', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path))
@click.pass_context
def quick_analyze(ctx, directory: Path, output: Optional[Path]):
    """Quick analysis with default settings (alias for common use case)."""
    ctx.invoke(analyze, 
               directory=directory,
               output=output,
               output_format='json',
               categories=(),
               difficulty=(),
               max_questions=5,
               config=None,
               dry_run=False,
               quiet=False,
               verbose=False)