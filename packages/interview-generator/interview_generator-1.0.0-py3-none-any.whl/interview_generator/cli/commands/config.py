"""Configuration management commands."""

import click
from pathlib import Path
from typing import Optional

from ...core.application import get_application
from ..utils.formatters import format_error, format_success, format_config_info


@click.group()
def config():
    """Manage configuration settings."""
    pass


@config.command()
@click.option('--output', '-o',
              type=click.Path(path_type=Path),
              default=Path.cwd() / 'config.json',
              help='Output path for configuration file')
@click.option('--interactive', '-i',
              is_flag=True,
              help='Create configuration interactively')
@click.option('--force',
              is_flag=True,
              help='Overwrite existing configuration file')
def create(output: Path, interactive: bool, force: bool):
    """
    Create a new configuration file.
    
    Examples:
    
      # Create default configuration
      interview-generator config create
      
      # Create with interactive prompts
      interview-generator config create --interactive
      
      # Save to specific location
      interview-generator config create -o /path/to/config.json
    """
    try:
        # Check if file exists
        if output.exists() and not force:
            click.echo(format_error(f"Configuration file already exists: {output}"))
            click.echo("Use --force to overwrite or choose a different path")
            return
        
        # Create configuration
        app = get_application()
        success = app.create_default_config(output, interactive)
        
        if success:
            click.echo(format_success(f"Configuration created: {output}"))
            
            if interactive:
                click.echo("\n💡 Your configuration has been saved with your API key.")
                click.echo("   Keep this file secure and don't commit it to version control.")
            else:
                click.echo("\n⚠️  Remember to set your OpenAI API key in the configuration file:")
                click.echo(f"   Edit {output} and replace 'your-openai-api-key-here' with your actual API key")
            
            click.echo(f"\n📖 To use this configuration:")
            click.echo(f"   interview-generator analyze /path/to/code --config {output}")
        else:
            click.echo(format_error("Failed to create configuration file"))
            
    except Exception as e:
        click.echo(format_error(f"Error creating configuration: {str(e)}"))


@config.command()
@click.option('--config', '-c',
              type=click.Path(exists=True, path_type=Path),
              help='Path to configuration file to validate')
def validate(config: Optional[Path]):
    """
    Validate configuration settings.
    
    Examples:
    
      # Validate default configuration
      interview-generator config validate
      
      # Validate specific configuration file
      interview-generator config validate --config /path/to/config.json
    """
    try:
        app = get_application(config)
        
        if not app.initialize(verbose=False):
            click.echo(format_error("Configuration validation failed"))
            return
        
        # Run validation
        validation_results = app.validate_setup()
        
        click.echo("🔍 Configuration Validation Results")
        click.echo("=" * 40)
        
        overall_status = validation_results.get('overall_status', 'unknown')
        
        if overall_status == 'success':
            click.echo(format_success("✅ All validations passed"))
        elif overall_status == 'warning':
            click.echo("⚠️  Validation completed with warnings")
        else:
            click.echo(format_error("❌ Validation failed"))
        
        # Show component status
        components = validation_results.get('components', {})
        if components:
            click.echo("\n📋 Component Status:")
            for component, status in components.items():
                status_icon = "✅" if status.get('status') == 'success' else "❌"
                click.echo(f"   {status_icon} {component}: {status.get('message', status.get('status'))}")
                
                if status.get('errors'):
                    for error in status['errors']:
                        click.echo(f"      ❌ {error}")
        
        # Show errors and warnings
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        if errors:
            click.echo("\n🚫 Errors:")
            for error in errors:
                click.echo(f"   - {error}")
        
        if warnings:
            click.echo("\n⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"   - {warning}")
        
        # Provide suggestions
        if errors:
            click.echo("\n💡 Suggestions:")
            if any("API key" in error for error in errors):
                click.echo("   - Set your OpenAI API key in the configuration file")
                click.echo("   - Get an API key from: https://platform.openai.com/api-keys")
            
            if any("configuration" in error.lower() for error in errors):
                click.echo("   - Run 'interview-generator config create --interactive' to create a new configuration")
        
    except Exception as e:
        click.echo(format_error(f"Validation error: {str(e)}"))


@config.command()
@click.option('--config', '-c',
              type=click.Path(exists=True, path_type=Path),
              help='Path to configuration file to show')
@click.option('--show-secrets',
              is_flag=True,
              help='Show sensitive values (API keys) - use with caution')
def show(config: Optional[Path], show_secrets: bool):
    """
    Display current configuration settings.
    
    Examples:
    
      # Show current configuration
      interview-generator config show
      
      # Show specific configuration file
      interview-generator config show --config /path/to/config.json
      
      # Show including sensitive values (be careful!)
      interview-generator config show --show-secrets
    """
    try:
        app = get_application(config)
        
        if not app.initialize(verbose=False):
            click.echo(format_error("Failed to load configuration"))
            return
        
        config_info = app.get_config_info()
        
        click.echo("📋 Current Configuration")
        click.echo("=" * 30)
        
        click.echo(format_config_info(config_info, show_secrets))
        
        if not show_secrets and config_info.get('api_key_configured'):
            click.echo("\n🔒 API key is configured but hidden for security")
            click.echo("   Use --show-secrets to display sensitive values")
        
    except Exception as e:
        click.echo(format_error(f"Error displaying configuration: {str(e)}"))


@config.command()
@click.option('--config', '-c',
              type=click.Path(exists=True, path_type=Path),
              help='Path to configuration file to edit')
def edit(config: Optional[Path]):
    """
    Open configuration file in default editor.
    
    Examples:
    
      # Edit default configuration
      interview-generator config edit
      
      # Edit specific configuration file
      interview-generator config edit --config /path/to/config.json
    """
    try:
        import os
        import subprocess
        
        # Determine config file path
        if config:
            config_path = config
        else:
            config_path = Path.cwd() / 'config.json'
            if not config_path.exists():
                click.echo(format_error(f"Configuration file not found: {config_path}"))
                click.echo("Run 'interview-generator config create' first")
                return
        
        # Try to open with default editor
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(config_path))
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(config_path)])
            else:
                # Fallback to environment editor
                editor = os.environ.get('EDITOR', 'nano')
                subprocess.call([editor, str(config_path)])
            
            click.echo(f"📝 Opening configuration file: {config_path}")
            
        except Exception:
            # If opening fails, just show the path
            click.echo(f"📝 Configuration file location: {config_path}")
            click.echo("Please open this file in your preferred text editor")
        
    except Exception as e:
        click.echo(format_error(f"Error opening configuration: {str(e)}"))


@config.command()
def template():
    """
    Show configuration file template with all available options.
    
    This displays a complete configuration template that you can copy
    and customize for your needs.
    """
    template_content = '''{
  "llm_api_key": "your-openai-api-key-here",
  "llm_model": "gpt-3.5-turbo",
  "llm_max_tokens": 1500,
  "llm_temperature": 0.7,
  "llm_requests_per_minute": 60,
  "llm_max_retries": 3,
  "llm_retry_delay": 1.0,
  "llm_timeout": 30,
  "question_categories": [
    "comprehension",
    "debugging", 
    "optimization",
    "design",
    "edge_cases"
  ],
  "difficulty_levels": [
    "beginner",
    "intermediate", 
    "advanced",
    "expert"
  ],
  "output_format": "json",
  "max_questions_per_category": 5,
  "exclude_patterns": [
    "__pycache__",
    ".git",
    "*.pyc",
    "*.pyo"
  ],
  "include_docstrings": true,
  "min_function_length": 3,
  "max_complexity_threshold": 10
}'''
    
    click.echo("📄 Configuration Template")
    click.echo("=" * 25)
    click.echo(template_content)
    click.echo()
    click.echo("💡 To use this template:")
    click.echo("   1. Copy the content above to a file (e.g., config.json)")
    click.echo("   2. Replace 'your-openai-api-key-here' with your actual API key")
    click.echo("   3. Customize other settings as needed")
    click.echo("   4. Use with: interview-generator analyze /path/to/code --config config.json")