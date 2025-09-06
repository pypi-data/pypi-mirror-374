"""Main application orchestrator."""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from ..models.config_models import Config
from ..utils.config_manager import ConfigManager
from .pipeline import InterviewQuestionPipeline


logger = logging.getLogger(__name__)


class Application:
    """Main application class that orchestrates the entire system."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the application.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config: Optional[Config] = None
        self.config_manager = ConfigManager()
        self.pipeline: Optional[InterviewQuestionPipeline] = None
        
        # Setup logging
        self._setup_logging()
    
    def initialize(self, verbose: bool = False) -> bool:
        """
        Initialize the application with configuration.
        
        Args:
            verbose: Enable verbose logging
            
        Returns:
            True if initialization successful
        """
        try:
            # Adjust logging level
            if verbose:
                logging.getLogger().setLevel(logging.DEBUG)
                logger.debug("Verbose logging enabled")
            
            # Load configuration
            if self.config_path and self.config_path.exists():
                logger.info(f"Loading configuration from {self.config_path}")
                self.config = self.config_manager.load_config(self.config_path)
            else:
                # This is the corrected logic: search for the config if no path is given
                logger.info("No specific config path provided, searching default locations...")
                self.config = self.config_manager.find_and_load_config()
            
            # Validate configuration
            is_valid, errors = self.config.validate_all()
            if not is_valid:
                logger.error("Configuration validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False
            
            # Initialize pipeline
            self.pipeline = InterviewQuestionPipeline(self.config)
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Application initialization failed: {e}")
            return False
    
    def create_default_config(self, output_path: Path, interactive: bool = False) -> bool:
        """
        Create a default configuration file.
        
        Args:
            output_path: Path where to save the config
            interactive: Whether to prompt for values interactively
            
        Returns:
            True if config created successfully
        """
        try:
            if interactive:
                config = self._create_interactive_config()
            else:
                config = self.config_manager.create_default_config()
            
            success = self.config_manager.save_config(config, output_path)
            
            if success:
                logger.info(f"Configuration saved to {output_path}")
                return True
            else:
                logger.error("Failed to save configuration")
                return False
                
        except Exception as e:
            logger.error(f"Error creating configuration: {e}")
            return False
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate the complete application setup.
        
        Returns:
            Validation results dictionary
        """
        if not self.pipeline:
            return {
                'overall_status': 'error',
                'errors': ['Application not initialized']
            }
        
        try:
            import asyncio
            return asyncio.run(self.pipeline.validate_setup())
        except Exception as e:
            return {
                'overall_status': 'error',
                'errors': [f'Validation failed: {str(e)}']
            }
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about current configuration."""
        if not self.config:
            return {'status': 'not_loaded'}
        
        return {
            'status': 'loaded',
            'config_path': str(self.config_path) if self.config_path else 'default',
            'llm_model': self.config.llm_model,
            'output_format': self.config.output_format,
            'max_questions_per_category': self.config.max_questions_per_category,
            'question_categories': [cat.value for cat in self.config.question_categories],
            'difficulty_levels': [level.value for level in self.config.difficulty_levels],
            'api_key_configured': bool(self.config.llm_api_key and 
                                     self.config.llm_api_key != 'your-openai-api-key-here')
        }
    
    def _setup_logging(self):
        """Setup application logging."""
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Set specific logger levels
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
        
        logger.info("Logging configured")
    
    def _create_interactive_config(self) -> Config:
        """Create configuration interactively by prompting user."""
        import click
        
        click.echo("Creating interactive configuration...")
        click.echo("Press Enter to use default values shown in brackets.")
        click.echo()
        
        # Get API key
        api_key = click.prompt(
            "OpenAI API Key",
            type=str,
            hide_input=True,
            confirmation_prompt=True
        )
        
        # Get model
        model = click.prompt(
            "LLM Model",
            default="gpt-3.5-turbo",
            type=click.Choice(['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'])
        )
        
        # Get output format
        output_format = click.prompt(
            "Default output format",
            default="json",
            type=click.Choice(['json', 'markdown', 'both'])
        )
        
        # Get max questions
        max_questions = click.prompt(
            "Maximum questions per category",
            default=5,
            type=click.IntRange(1, 20)
        )
        
        # Create config
        config = self.config_manager.create_default_config()
        config.llm_api_key = api_key
        config.llm_model = model
        config.output_format = output_format
        config.max_questions_per_category = max_questions
        
        click.echo()
        click.echo("Configuration created successfully!")
        
        return config
    
    async def shutdown(self):
        """Shutdown the application gracefully."""
        try:
            if self.pipeline:
                await self.pipeline.close()
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global application instance
app_instance: Optional[Application] = None


def get_application(config_path: Optional[Path] = None) -> Application:
    """Get or create the global application instance."""
    global app_instance
    
    if app_instance is None:
        app_instance = Application(config_path)
    
    return app_instance


def initialize_application(config_path: Optional[Path] = None, 
                         verbose: bool = False) -> Application:
    """Initialize and return the application instance."""
    app = get_application(config_path)
    
    if not app.initialize(verbose):
        logger.error("Failed to initialize application")
        sys.exit(1)
    
    return app