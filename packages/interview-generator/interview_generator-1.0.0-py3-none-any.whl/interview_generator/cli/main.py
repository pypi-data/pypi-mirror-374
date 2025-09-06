"""
Main CLI entry point for the interview generator.
"""

import click
import sys
from pathlib import Path

from .commands.analyze import analyze, quick_analyze
from .commands.config import config
from .commands.validate import validate


# Version information
__version__ = "1.0.0"


@click.group()
@click.version_option(version=__version__, prog_name="interview-generator")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """
    🎯 Interview Question Generator
    
    Generate contextual interview questions from Python code analysis.
    
    This tool analyzes Python codebases and automatically generates relevant
    technical interview questions based on the code structure, patterns, and
    business logic found in the files.
    
    Examples:
    
      # Quick analysis with default settings
      interview-generator analyze /path/to/code
      
      # Generate specific question types
      interview-generator analyze /path/to/code -c comprehension -c debugging
      
      # Create configuration file
      interview-generator config create --interactive
      
      # Validate setup
      interview-generator validate setup
    
    For more help on specific commands, use:
      interview-generator COMMAND --help
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


# Add commands to the main CLI group
cli.add_command(analyze)
cli.add_command(config)
cli.add_command(validate)

# Add quick analyze as a top-level command for convenience
cli.add_command(quick_analyze)


@cli.command()
def version():
    """Show version information."""
    click.echo(f"Interview Question Generator v{__version__}")
    click.echo("🎯 Generate contextual interview questions from Python code")
    click.echo()
    click.echo("Components:")
    click.echo("  • Code Analysis Engine")
    click.echo("  • Pattern Detection System") 
    click.echo("  • LLM Integration Layer")
    click.echo("  • Question Generation Pipeline")
    click.echo("  • Multi-format Output System")


@cli.command()
def info():
    """Show system information and diagnostics."""
    import sys
    import platform
    from datetime import datetime
    
    click.echo("🔍 System Information")
    click.echo("=" * 30)
    click.echo(f"Version: {__version__}")
    click.echo(f"Python: {sys.version.split()[0]}")
    click.echo(f"Platform: {platform.system()} {platform.release()}")
    click.echo(f"Architecture: {platform.machine()}")
    click.echo(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo()
    
    # Check key dependencies
    click.echo("📦 Dependencies:")
    dependencies = [
        ('click', 'CLI framework'),
        ('openai', 'OpenAI API client'),
        ('aiohttp', 'Async HTTP client'),
        ('tenacity', 'Retry logic')
    ]
    
    for package, description in dependencies:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            click.echo(f"  ✅ {package} {version} - {description}")
        except ImportError:
            click.echo(f"  ❌ {package} - {description} (missing)")
    
    click.echo()
    click.echo("💡 For detailed validation, run:")
    click.echo("   interview-generator validate setup")


@cli.command()
@click.option('--format', 'output_format', 
              type=click.Choice(['text', 'json']),
              default='text',
              help='Output format')
def examples(output_format):
    """Show usage examples and common workflows."""
    
    if output_format == 'json':
        import json
        examples_data = {
            "basic_usage": [
                "interview-generator analyze /path/to/code",
                "interview-generator analyze /path/to/code --output questions.json"
            ],
            "filtering": [
                "interview-generator analyze /path/to/code -c comprehension -c debugging",
                "interview-generator analyze /path/to/code -d intermediate -d advanced"
            ],
            "configuration": [
                "interview-generator config create --interactive",
                "interview-generator config validate"
            ],
            "validation": [
                "interview-generator validate setup",
                "interview-generator validate api"
            ]
        }
        click.echo(json.dumps(examples_data, indent=2))
        return
    
    # Text format
    click.echo("📚 Usage Examples")
    click.echo("=" * 20)
    click.echo()
    
    click.echo("🚀 Getting Started:")
    click.echo("  # Set up configuration")
    click.echo("  interview-generator config create --interactive")
    click.echo()
    click.echo("  # Validate setup")
    click.echo("  interview-generator validate setup")
    click.echo()
    click.echo("  # Quick analysis")
    click.echo("  interview-generator analyze /path/to/your/code")
    click.echo()
    
    click.echo("🎯 Basic Analysis:")
    click.echo("  # Analyze directory with default settings")
    click.echo("  interview-generator analyze /path/to/code")
    click.echo()
    click.echo("  # Save to specific file")
    click.echo("  interview-generator analyze /path/to/code --output questions.json")
    click.echo()
    click.echo("  # Use different output format")
    click.echo("  interview-generator analyze /path/to/code --format markdown")
    click.echo()
    
    click.echo("🔍 Filtering Options:")
    click.echo("  # Generate specific question categories")
    click.echo("  interview-generator analyze /path/to/code \\")
    click.echo("    --categories comprehension debugging optimization")
    click.echo()
    click.echo("  # Filter by difficulty level")
    click.echo("  interview-generator analyze /path/to/code \\")
    click.echo("    --difficulty intermediate advanced")
    click.echo()
    click.echo("  # Limit number of questions")
    click.echo("  interview-generator analyze /path/to/code --max-questions 15")
    click.echo()
    
    click.echo("📊 Advanced Usage:")
    click.echo("  # Structured export with reports")
    click.echo("  interview-generator analyze /path/to/code \\")
    click.echo("    --format structured --output ./results")
    click.echo()
    click.echo("  # Dry run to preview analysis")
    click.echo("  interview-generator analyze /path/to/code --dry-run")
    click.echo()
    click.echo("  # Use custom configuration")
    click.echo("  interview-generator analyze /path/to/code \\")
    click.echo("    --config /path/to/config.json")
    click.echo()
    
    click.echo("⚙️  Configuration Management:")
    click.echo("  # Create interactive configuration")
    click.echo("  interview-generator config create --interactive")
    click.echo()
    click.echo("  # Validate configuration")
    click.echo("  interview-generator config validate")
    click.echo()
    click.echo("  # Show current settings")
    click.echo("  interview-generator config show")
    click.echo()
    
    click.echo("🔧 Validation and Testing:")
    click.echo("  # Check complete setup")
    click.echo("  interview-generator validate setup")
    click.echo()
    click.echo("  # Test API connectivity")
    click.echo("  interview-generator validate api")
    click.echo()
    click.echo("  # Run sample analysis")
    click.echo("  interview-generator validate sample")
    click.echo()
    
    click.echo("💡 Tips:")
    click.echo("  • Use --verbose for detailed output")
    click.echo("  • Use --quiet to suppress progress indicators")
    click.echo("  • Use --dry-run to preview without API calls")
    click.echo("  • Check 'interview-generator COMMAND --help' for command-specific options")


def main():
    """Main entry point for the CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⚠️  Operation cancelled by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()