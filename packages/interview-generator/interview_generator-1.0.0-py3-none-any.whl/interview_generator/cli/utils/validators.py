"""Input validation utilities for CLI."""

from pathlib import Path
from typing import List, Optional

from ...models.question_models import QuestionCategory, DifficultyLevel


def validate_directory(directory: Path) -> bool:
    """
    Validate that directory exists and contains Python files.
    
    Args:
        directory: Directory path to validate
        
    Returns:
        True if directory is valid
    """
    if not directory.exists():
        return False
    
    if not directory.is_dir():
        return False
    
    # Check if directory contains any Python files (recursively)
    python_files = list(directory.rglob("*.py"))
    return len(python_files) > 0


def validate_output_path(output_path: Path, output_format: str) -> bool:
    """
    Validate output path based on format.
    
    Args:
        output_path: Output path to validate
        output_format: Expected output format
        
    Returns:
        True if output path is valid
    """
    try:
        # Check if parent directory exists or can be created
        parent = output_path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError):
                return False
        
        # For structured format, path should be a directory
        if output_format == "structured":
            return True  # Directory will be created
        
        # For file formats, check if we can write to the location
        try:
            # Test write access
            test_file = parent / f".test_write_{output_path.name}"
            test_file.touch()
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False
    
    except Exception:
        return False


def validate_categories(categories: List[str]) -> Optional[List[QuestionCategory]]:
    """
    Validate and convert category strings to QuestionCategory enums.
    
    Args:
        categories: List of category strings
        
    Returns:
        List of QuestionCategory enums or None if invalid
    """
    try:
        result = []
        valid_categories = {cat.value: cat for cat in QuestionCategory}
        
        for category in categories:
            if category not in valid_categories:
                return None
            result.append(valid_categories[category])
        
        return result
    
    except Exception:
        return None


def validate_difficulties(difficulties: List[str]) -> Optional[List[DifficultyLevel]]:
    """
    Validate and convert difficulty strings to DifficultyLevel enums.
    
    Args:
        difficulties: List of difficulty strings
        
    Returns:
        List of DifficultyLevel enums or None if invalid
    """
    try:
        result = []
        valid_difficulties = {level.value: level for level in DifficultyLevel}
        
        for difficulty in difficulties:
            if difficulty not in valid_difficulties:
                return None
            result.append(valid_difficulties[difficulty])
        
        return result
    
    except Exception:
        return None


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is required"
    
    if api_key in ["your-openai-api-key-here", "sk-placeholder"]:
        return False, "Please replace the placeholder API key with your actual OpenAI API key"
    
    # Basic OpenAI API key format validation
    if not api_key.startswith("sk-"):
        return False, "OpenAI API key should start with 'sk-'"
    
    if len(api_key) < 20:
        return False, "API key appears to be too short"
    
    return True, ""


def validate_max_questions(max_questions: int) -> bool:
    """
    Validate maximum questions parameter.
    
    Args:
        max_questions: Maximum questions value
        
    Returns:
        True if valid
    """
    return 1 <= max_questions <= 50


def validate_file_patterns(patterns: List[str]) -> bool:
    """
    Validate file exclusion patterns.
    
    Args:
        patterns: List of file patterns
        
    Returns:
        True if patterns are valid
    """
    try:
        import fnmatch
        
        # Test each pattern with a sample filename
        test_filename = "test_file.py"
        
        for pattern in patterns:
            try:
                fnmatch.fnmatch(test_filename, pattern)
            except Exception:
                return False
        
        return True
    
    except Exception:
        return False


def suggest_fixes_for_directory(directory: Path) -> List[str]:
    """
    Suggest fixes for directory validation issues.
    
    Args:
        directory: Directory that failed validation
        
    Returns:
        List of suggested fixes
    """
    suggestions = []
    
    if not directory.exists():
        suggestions.append(f"Directory does not exist: {directory}")
        suggestions.append("Check the path and ensure the directory exists")
    elif not directory.is_dir():
        suggestions.append(f"Path is not a directory: {directory}")
        suggestions.append("Provide a directory path, not a file path")
    else:
        # Check for Python files
        python_files = list(directory.rglob("*.py"))
        if not python_files:
            suggestions.append("No Python files found in directory")
            suggestions.append("Ensure the directory contains .py files")
            
            # Check for common issues
            if list(directory.glob("*")):
                suggestions.append("Directory is not empty - files may have different extensions")
            else:
                suggestions.append("Directory is empty")
    
    return suggestions


def suggest_fixes_for_output(output_path: Path, output_format: str) -> List[str]:
    """
    Suggest fixes for output path validation issues.
    
    Args:
        output_path: Output path that failed validation
        output_format: Output format
        
    Returns:
        List of suggested fixes
    """
    suggestions = []
    
    try:
        parent = output_path.parent
        
        if not parent.exists():
            suggestions.append(f"Parent directory does not exist: {parent}")
            suggestions.append("Create the parent directory or choose a different path")
        
        # Check write permissions
        import os
        if parent.exists() and not os.access(parent, os.W_OK):
            suggestions.append("No write permission to parent directory")
            suggestions.append("Choose a directory where you have write permissions")
        
        # Format-specific suggestions
        if output_format == "structured":
            suggestions.append("For structured format, provide a directory path")
            suggestions.append("The system will create subdirectories as needed")
        else:
            # Suggest appropriate file extensions
            extensions = {
                "json": ".json",
                "markdown": ".md",
                "both": " (directory for multiple files)"
            }
            
            ext = extensions.get(output_format, "")
            if ext and not str(output_path).endswith(ext.split()[0]):
                suggestions.append(f"Consider using {ext} extension for {output_format} format")
    
    except Exception:
        suggestions.append("Unable to validate output path")
        suggestions.append("Check path format and permissions")
    
    return suggestions