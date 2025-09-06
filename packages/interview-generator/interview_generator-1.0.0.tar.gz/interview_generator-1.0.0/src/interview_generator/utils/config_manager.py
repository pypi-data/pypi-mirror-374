"""
Configuration management utilities.
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Tuple

from ..models.config_models import Config
from ..models.question_models import QuestionCategory, DifficultyLevel


logger = logging.getLogger(__name__)


class ConfigManager:
    """Manager for application configuration."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.default_config_locations = [
            Path("config/config.json"),
            Path.home() / ".interview-gen" / "config.json",
            Path("config/default_config.json")
        ]
    
    def load_config(self, config_path: Path) -> Config:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = Config.from_dict(data)
            
            # Validate the loaded configuration
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                logger.warning(f"Configuration validation errors: {'; '.join(errors)}")
                # Merge with defaults to fix missing/invalid fields
                config = self._merge_with_defaults(config, data)
            
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    def find_and_load_config(self) -> Config:
        """
        Find and load configuration from default locations.
        
        Returns:
            Loaded configuration or default configuration if none found
        """
        for config_path in self.default_config_locations:
            if config_path.exists():
                try:
                    logger.info(f"Loading configuration from: {config_path}")
                    return self.load_config(config_path)
                except (FileNotFoundError, ValueError) as e:
                    logger.warning(f"Failed to load config from {config_path}: {e}")
                    continue
        
        logger.info("No valid configuration file found, using defaults")
        return self.create_default_config()
    
    def create_default_config(self) -> Config:
        """
        Create a default configuration.
        
        Returns:
            Default configuration
        """
        return Config(
            llm_api_key="your-openai-api-key-here",
            llm_model="gpt-3.5-turbo",
            question_categories=list(QuestionCategory),
            difficulty_levels=list(DifficultyLevel),
            output_format="json",
            max_questions_per_category=5,
            exclude_patterns=[
                "__pycache__",
                ".git",
                "*.pyc",
                "*.pyo",
                ".pytest_cache",
                "node_modules",
                ".venv",
                "venv"
            ],
            include_docstrings=True,
            min_function_length=3,
            max_complexity_threshold=10
        )
    
    def validate_config(self, config: Config) -> Tuple[bool, List[str]]:
        """
        Validate configuration settings.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        return config.validate_all()
    
    def save_config(self, config: Config, config_path: Path) -> None:
        """
        Save configuration to a file.
        
        Args:
            config: Configuration to save
            config_path: Path to save to
            
        Raises:
            OSError: If file cannot be written
        """
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to: {config_path}")
            
        except Exception as e:
            raise OSError(f"Failed to save configuration to {config_path}: {e}")
    
    def create_config_file(self, config_path: Path) -> None:
        """
        Create a new configuration file with default settings.
        
        Args:
            config_path: Path where to create the config file
        """
        default_config = self.create_default_config()
        self.save_config(default_config, config_path)
        
        logger.info(f"Created default configuration file at: {config_path}")
        logger.info("Please edit the configuration file and add your OpenAI API key")
    
    def _merge_with_defaults(self, config: Config, original_data: dict) -> Config:
        """
        Merge configuration with defaults to fix missing or invalid fields.
        
        Args:
            config: Current configuration
            original_data: Original data from config file
            
        Returns:
            Merged configuration with defaults for invalid fields
        """
        default_config = self.create_default_config()
        
        # Check each field and use default if current value is invalid
        merged_data = original_data.copy()
        
        # Validate and fix API key
        is_valid, _ = config.validate_api_key()
        if not is_valid:
            merged_data["llm_api_key"] = default_config.llm_api_key
            logger.warning("Using default API key placeholder")
        
        # Validate and fix categories
        is_valid, _ = config.validate_categories()
        if not is_valid:
            merged_data["question_categories"] = [cat.value for cat in default_config.question_categories]
            logger.warning("Using default question categories")
        
        # Validate and fix difficulty levels
        is_valid, _ = config.validate_difficulty_levels()
        if not is_valid:
            merged_data["difficulty_levels"] = [level.value for level in default_config.difficulty_levels]
            logger.warning("Using default difficulty levels")
        
        # Validate and fix output format
        is_valid, _ = config.validate_output_format()
        if not is_valid:
            merged_data["output_format"] = default_config.output_format
            logger.warning("Using default output format")
        
        # Validate and fix numeric fields
        is_valid, _ = config.validate_numeric_fields()
        if not is_valid:
            merged_data["max_questions_per_category"] = default_config.max_questions_per_category
            merged_data["min_function_length"] = default_config.min_function_length
            merged_data["max_complexity_threshold"] = default_config.max_complexity_threshold
            logger.warning("Using default numeric field values")
        
        return Config.from_dict(merged_data)