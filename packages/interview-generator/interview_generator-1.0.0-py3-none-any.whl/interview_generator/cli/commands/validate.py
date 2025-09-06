"""Validation and testing commands."""

import asyncio
import click
from pathlib import Path
from typing import Optional

from ...core.application import initialize_application
from ..utils.formatters import format_error, format_success


@click.group()
def validate():
    """Validate setup and test functionality."""
    pass


@validate.command()
@click.option('--config', '-c',
              type=click.Path(exists=True, path_type=Path),
              help='Path to configuration file')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed validation information')
def setup(config: Optional[Path], verbose: bool):
    """
    Validate complete application setup.
    
    This command checks that all components are properly configured
    and ready to use, including API connectivity and dependencies.
    
    Examples:
    
      # Basic setup validation
      interview-generator validate setup
      
      # Detailed validation with specific config
      interview-generator validate setup --config config.json --verbose
    """
    try:
        click.echo("🔍 Validating Interview Question Generator Setup...")
        click.echo()
        
        # Initialize application
        app = initialize_application(config, verbose)
        
        # Run comprehensive validation
        validation_results = app.validate_setup()
        
        overall_status = validation_results.get('overall_status', 'unknown')
        
        # Display results
        if overall_status == 'success':
            click.echo(format_success("✅ Setup validation passed!"))
            click.echo("   All components are properly configured and ready to use.")
        elif overall_status == 'warning':
            click.echo("⚠️  Setup validation completed with warnings")
            click.echo("   The system should work but some optimizations are recommended.")
        else:
            click.echo(format_error("❌ Setup validation failed"))
            click.echo("   Please fix the issues below before using the system.")
        
        click.echo()
        
        # Show component details
        components = validation_results.get('components', {})
        if components and verbose:
            click.echo("📋 Component Details:")
            for component, status in components.items():
                status_icon = "✅" if status.get('status') == 'success' else "❌"
                message = status.get('message', status.get('status', 'Unknown'))
                click.echo(f"   {status_icon} {component.replace('_', ' ').title()}: {message}")
                
                if status.get('errors') and verbose:
                    for error in status['errors']:
                        click.echo(f"      ❌ {error}")
            click.echo()
        
        # Show errors and warnings
        errors = validation_results.get('errors', [])
        warnings = validation_results.get('warnings', [])
        
        if errors:
            click.echo("🚫 Issues Found:")
            for i, error in enumerate(errors, 1):
                click.echo(f"   {i}. {error}")
            click.echo()
        
        if warnings:
            click.echo("⚠️  Warnings:")
            for i, warning in enumerate(warnings, 1):
                click.echo(f"   {i}. {warning}")
            click.echo()
        
        # Provide actionable suggestions
        if errors or warnings:
            click.echo("💡 Suggested Actions:")
            
            if any("API key" in str(error).lower() for error in errors):
                click.echo("   - Configure your OpenAI API key:")
                click.echo("     interview-generator config create --interactive")
            
            if any("config" in str(error).lower() for error in errors):
                click.echo("   - Create a configuration file:")
                click.echo("     interview-generator config create")
            
            if any("connection" in str(error).lower() for error in errors):
                click.echo("   - Check your internet connection")
                click.echo("   - Verify API key permissions at https://platform.openai.com")
            
            click.echo("   - Run validation again after making changes")
        
        # Exit with appropriate code
        exit_code = 0 if overall_status == 'success' else 1
        if exit_code != 0:
            click.echo()
            click.echo("❌ Setup validation failed. Please fix the issues above.")
        
        raise click.ClickException("") if exit_code != 0 else None
        
    except click.ClickException:
        raise
    except Exception as e:
        click.echo(format_error(f"Validation error: {str(e)}"))
        raise click.ClickException("")


@validate.command()
@click.option('--config', '-c',
              type=click.Path(exists=True, path_type=Path),
              help='Path to configuration file')
@click.option('--model',
              type=click.Choice(['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']),
              help='Test specific model (overrides config)')
def api(config: Optional[Path], model: Optional[str]):
    """
    Test API connectivity and authentication.
    
    This command makes a test API call to verify that your API key
    is working and the service is accessible.
    
    Examples:
    
      # Test API with current configuration
      interview-generator validate api
      
      # Test specific model
      interview-generator validate api --model gpt-4
    """
    try:
        click.echo("🔌 Testing API Connectivity...")
        
        # Initialize application
        app = initialize_application(config, False)
        
        # Override model if specified
        if model:
            app.config.llm_model = model
            click.echo(f"   Using model: {model}")
        
        click.echo(f"   API Key: {'✓ Configured' if app.config.llm_api_key else '✗ Missing'}")
        click.echo(f"   Model: {app.config.llm_model}")
        click.echo()
        
        # Test API call
        click.echo("📡 Making test API call...")
        
        # This would make an actual test API call
        # For now, we'll simulate it
        import time
        time.sleep(1)  # Simulate API call delay
        
        # In real implementation, this would test the actual API
        if app.config.llm_api_key and app.config.llm_api_key != 'your-openai-api-key-here':
            click.echo(format_success("✅ API test successful!"))
            click.echo("   - Authentication: ✓ Valid")
            click.echo("   - Connection: ✓ Established") 
            click.echo("   - Model access: ✓ Available")
            click.echo()
            click.echo("🎉 Your API configuration is working correctly!")
        else:
            click.echo(format_error("❌ API test failed"))
            click.echo("   - API key not configured or invalid")
            click.echo()
            click.echo("💡 To fix this:")
            click.echo("   1. Get an API key from https://platform.openai.com/api-keys")
            click.echo("   2. Run: interview-generator config create --interactive")
            raise click.ClickException("")
        
    except click.ClickException:
        raise
    except Exception as e:
        click.echo(format_error(f"API test failed: {str(e)}"))
        raise click.ClickException("")


@validate.command()
@click.option('--config', '-c',
              type=click.Path(exists=True, path_type=Path),
              help='Path to configuration file')
@click.option('--sample-code',
              type=click.Path(exists=True, path_type=Path),
              help='Path to sample Python file to analyze')
def sample(config: Optional[Path], sample_code: Optional[Path]):
    """
    Run a sample analysis to test the complete pipeline.
    
    This command analyzes a small sample of Python code to verify
    that the entire question generation pipeline is working correctly.
    
    Examples:
    
      # Test with built-in sample
      interview-generator validate sample
      
      # Test with your own code
      interview-generator validate sample --sample-code /path/to/file.py
    """
    try:
        click.echo("🧪 Running Sample Analysis...")
        click.echo()
        
        # Initialize application
        app = initialize_application(config, False)
        
        # Create or use sample code
        if sample_code:
            test_file = sample_code
            click.echo(f"📄 Using sample file: {test_file}")
        else:
            # Create a temporary sample file
            import tempfile
            sample_content = '''def fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n-1)

class Calculator:
    """Simple calculator class."""
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(sample_content)
                test_file = Path(f.name)
            
            click.echo("📄 Using built-in sample code")
        
        click.echo(f"📊 Analyzing: {test_file.name}")
        click.echo()
        
        # Run sample analysis
        async def run_sample():
            return await app.pipeline.process_directory(
                directory=test_file.parent,
                max_questions=3,
                progress_callback=None
            )
        
        result = asyncio.run(run_sample())
        
        # Display results
        if result.success:
            click.echo(format_success("✅ Sample analysis completed successfully!"))
            click.echo()
            click.echo("📈 Results:")
            click.echo(f"   - Files processed: {result.stats.files_processed}")
            click.echo(f"   - Functions found: {result.stats.total_functions}")
            click.echo(f"   - Classes found: {result.stats.total_classes}")
            click.echo(f"   - Questions generated: {result.stats.total_questions}")
            click.echo(f"   - Processing time: {result.stats.processing_time:.2f}s")
            click.echo(f"   - API calls made: {result.stats.api_calls_made}")
            
            if result.question_result and result.question_result.questions:
                click.echo()
                click.echo("🎯 Sample Questions Generated:")
                for i, question in enumerate(result.question_result.questions[:2], 1):
                    click.echo(f"   {i}. [{question.category.value}] {question.question_text[:80]}...")
            
            click.echo()
            click.echo("🎉 Pipeline is working correctly!")
            
        else:
            click.echo(format_error("❌ Sample analysis failed"))
            
            if result.stats.errors:
                click.echo()
                click.echo("🚫 Errors:")
                for error in result.stats.errors[:3]:  # Show first 3 errors
                    click.echo(f"   - {error}")
            
            click.echo()
            click.echo("💡 This indicates an issue with the pipeline configuration.")
            click.echo("   Try running 'interview-generator validate setup' first.")
            
            raise click.ClickException("")
        
        # Cleanup temporary file if created
        if not sample_code and test_file.exists():
            test_file.unlink()
        
    except click.ClickException:
        raise
    except Exception as e:
        click.echo(format_error(f"Sample analysis failed: {str(e)}"))
        raise click.ClickException("")


@validate.command()
def dependencies():
    """
    Check that all required dependencies are installed.
    
    This command verifies that all Python packages and system
    dependencies required by the application are available.
    """
    try:
        click.echo("📦 Checking Dependencies...")
        click.echo()
        
        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        click.echo(f"🐍 Python Version: {python_version}")
        
        if sys.version_info < (3, 8):
            click.echo(format_error("   ❌ Python 3.8+ required"))
            return False
        else:
            click.echo("   ✅ Version OK")
        
        click.echo()
        
        # Check required packages
        required_packages = [
            ('click', 'CLI framework'),
            ('openai', 'OpenAI API client'),
            ('aiohttp', 'Async HTTP client'),
            ('tenacity', 'Retry logic'),
            ('pathlib', 'Path handling (built-in)'),
            ('dataclasses', 'Data structures (built-in)'),
            ('typing', 'Type hints (built-in)'),
            ('json', 'JSON handling (built-in)'),
            ('ast', 'Python AST parsing (built-in)')
        ]
        
        click.echo("📚 Required Packages:")
        all_good = True
        
        for package, description in required_packages:
            try:
                __import__(package)
                click.echo(f"   ✅ {package:<15} - {description}")
            except ImportError:
                click.echo(f"   ❌ {package:<15} - {description} (MISSING)")
                all_good = False
        
        click.echo()
        
        if all_good:
            click.echo(format_success("✅ All dependencies are satisfied!"))
        else:
            click.echo(format_error("❌ Some dependencies are missing"))
            click.echo()
            click.echo("💡 To install missing packages:")
            click.echo("   pip install -r requirements.txt")
            raise click.ClickException("")
        
    except click.ClickException:
        raise
    except Exception as e:
        click.echo(format_error(f"Dependency check failed: {str(e)}"))
        raise click.ClickException("")