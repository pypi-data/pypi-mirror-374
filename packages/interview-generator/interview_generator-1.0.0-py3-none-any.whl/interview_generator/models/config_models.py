"""
Configuration data models.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from .question_models import QuestionCategory, DifficultyLevel


@dataclass
class Config:
    """Application configuration settings."""
    llm_api_key: str
    llm_model: str = "gpt-3.5-turbo"
    llm_max_tokens: int = 1500
    llm_temperature: float = 0.7
    llm_requests_per_minute: int = 60
    llm_max_retries: int = 3
    llm_retry_delay: float = 1.0
    llm_timeout: int = 30
    llm_base_url: Optional[str] = None
    question_categories: List[QuestionCategory] = field(default_factory=lambda: list(QuestionCategory))
    difficulty_levels: List[DifficultyLevel] = field(default_factory=lambda: list(DifficultyLevel))
    output_format: str = "json"
    max_questions_per_category: int = 5
    exclude_patterns: List[str] = field(default_factory=lambda: ["__pycache__", ".git", "*.pyc", "*.pyo"])
    include_docstrings: bool = True
    min_function_length: int = 3
    max_complexity_threshold: int = 10
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """
        Validate the API key format and content.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.llm_api_key:
            return False, "API key is required"
        
        if self.llm_api_key in ["your-openai-api-key-here", "sk-placeholder"]:
            return False, "Please replace the placeholder API key with your actual OpenAI API key"
        
        # Basic OpenAI API key format validation
        if not self.llm_api_key.startswith("sk-"):
            return False, "OpenAI API key should start with 'sk-'"
        
        if len(self.llm_api_key) < 20:
            return False, "API key appears to be too short"
        
        return True, ""
    
    def validate_categories(self) -> Tuple[bool, str]:
        """
        Validate question categories.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.question_categories:
            return False, "At least one question category must be specified"
        
        valid_categories = set(QuestionCategory)
        for category in self.question_categories:
            if category not in valid_categories:
                return False, f"Invalid question category: {category}"
        
        return True, ""
    
    def validate_difficulty_levels(self) -> Tuple[bool, str]:
        """
        Validate difficulty levels.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.difficulty_levels:
            return False, "At least one difficulty level must be specified"
        
        valid_levels = set(DifficultyLevel)
        for level in self.difficulty_levels:
            if level not in valid_levels:
                return False, f"Invalid difficulty level: {level}"
        
        return True, ""
    
    def validate_output_format(self) -> Tuple[bool, str]:
        """
        Validate output format.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_formats = {"json", "markdown"}
        if self.output_format not in valid_formats:
            return False, f"Output format must be one of: {', '.join(valid_formats)}"
        
        return True, ""
    
    def validate_numeric_fields(self) -> Tuple[bool, str]:
        """
        Validate numeric configuration fields.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.max_questions_per_category < 1:
            return False, "max_questions_per_category must be at least 1"
        
        if self.max_questions_per_category > 50:
            return False, "max_questions_per_category should not exceed 50"
        
        if self.min_function_length < 1:
            return False, "min_function_length must be at least 1"
        
        if self.max_complexity_threshold < 1:
            return False, "max_complexity_threshold must be at least 1"
        
        return True, ""
    
    def validate_all(self) -> Tuple[bool, List[str]]:
        """
        Validate all configuration fields.
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Validate each field
        validations = [
            self.validate_api_key(),
            self.validate_categories(),
            self.validate_difficulty_levels(),
            self.validate_output_format(),
            self.validate_numeric_fields()
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Create Config from dictionary with type conversion.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            Config instance
        """
        # Convert string enum values back to enum objects
        categories = []
        if "question_categories" in data:
            for cat_str in data["question_categories"]:
                try:
                    categories.append(QuestionCategory(cat_str))
                except ValueError:
                    # Skip invalid categories, will be caught in validation
                    pass
        
        levels = []
        if "difficulty_levels" in data:
            for level_str in data["difficulty_levels"]:
                try:
                    levels.append(DifficultyLevel(level_str))
                except ValueError:
                    # Skip invalid levels, will be caught in validation
                    pass
        
        return cls(
            llm_api_key=data.get("llm_api_key", ""),
            llm_model=data.get("llm_model", "gpt-3.5-turbo"),
            question_categories=categories or list(QuestionCategory),
            difficulty_levels=levels or list(DifficultyLevel),
            output_format=data.get("output_format", "json"),
            max_questions_per_category=data.get("max_questions_per_category", 5),
            exclude_patterns=data.get("exclude_patterns", ["__pycache__", ".git", "*.pyc", "*.pyo"]),
            include_docstrings=data.get("include_docstrings", True),
            min_function_length=data.get("min_function_length", 3),
            max_complexity_threshold=data.get("max_complexity_threshold", 10)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            "llm_api_key": self.llm_api_key,
            "llm_model": self.llm_model,
            "question_categories": [cat.value for cat in self.question_categories],
            "difficulty_levels": [level.value for level in self.difficulty_levels],
            "output_format": self.output_format,
            "max_questions_per_category": self.max_questions_per_category,
            "exclude_patterns": self.exclude_patterns,
            "include_docstrings": self.include_docstrings,
            "min_function_length": self.min_function_length,
            "max_complexity_threshold": self.max_complexity_threshold
        }