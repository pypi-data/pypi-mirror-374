"""
File discovery utilities for finding Python files.
"""

import ast
import fnmatch
import logging
import os
from pathlib import Path
from typing import List, Tuple, Iterator, Optional, Set
import chardet

from ..models.config_models import Config


logger = logging.getLogger(__name__)


class FileDiscoveryError(Exception):
    """Base exception for file discovery errors."""
    pass


class DirectoryAccessError(FileDiscoveryError):
    """Raised when directory cannot be accessed."""
    pass


class FileValidationError(FileDiscoveryError):
    """Raised when file validation fails."""
    pass


class FileDiscovery:
    """Utility for discovering Python files in directories."""
    
    # Default patterns to exclude
    DEFAULT_EXCLUDE_PATTERNS = [
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        "venv",
        ".venv",
        "env",
        ".env",
        "node_modules",
        ".tox",
        "build",
        "dist",
        "*.egg-info",
        ".mypy_cache",
        ".coverage",
        "htmlcov"
    ]
    
    # File size limits (in bytes)
    MIN_FILE_SIZE = 1  # At least 1 byte
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None, config: Optional[Config] = None):
        """
        Initialize file discovery.
        
        Args:
            exclude_patterns: Patterns to exclude from discovery
            config: Configuration object for additional settings
        """
        self.exclude_patterns = exclude_patterns or self.DEFAULT_EXCLUDE_PATTERNS.copy()
        self.config = config
        self._visited_dirs: Set[Path] = set()  # For symlink loop detection
    
    def find_python_files(self, directory_path: Path) -> Tuple[List[Path], List[str]]:
        """
        Recursively find Python files in a directory.
        
        Args:
            directory_path: Directory to search
            
        Returns:
            Tuple of (list of valid Python file paths, list of error messages)
        """
        if not isinstance(directory_path, Path):
            directory_path = Path(directory_path)
        
        errors = []
        python_files = []
        
        # Validate directory exists and is accessible
        try:
            if not directory_path.exists():
                raise DirectoryAccessError(f"Directory does not exist: {directory_path}")
            
            if not directory_path.is_dir():
                raise DirectoryAccessError(f"Path is not a directory: {directory_path}")
            
            if not os.access(directory_path, os.R_OK):
                raise DirectoryAccessError(f"Directory is not readable: {directory_path}")
        
        except DirectoryAccessError as e:
            errors.append(str(e))
            return [], errors
        
        # Walk directory tree and collect Python files
        try:
            for file_path in self._walk_directory(directory_path):
                try:
                    if self.is_valid_python_file(file_path):
                        python_files.append(file_path)
                except FileValidationError as e:
                    logger.debug(f"Skipping file {file_path}: {e}")
                    # Don't add to errors - these are expected (binary files, etc.)
                except Exception as e:
                    error_msg = f"Error validating file {file_path}: {e}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
        
        except Exception as e:
            error_msg = f"Error walking directory {directory_path}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        # Sort files for consistent output
        python_files.sort()
        
        logger.info(f"Found {len(python_files)} Python files in {directory_path}")
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during discovery")
        
        return python_files, errors
    
    def is_valid_python_file(self, file_path: Path) -> bool:
        """
        Check if a file is a valid Python file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if valid Python file
            
        Raises:
            FileValidationError: If file is invalid for expected reasons
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        # Check file extension
        if file_path.suffix.lower() != '.py':
            raise FileValidationError(f"Not a Python file: {file_path.suffix}")
        
        # Check file exists and is readable
        if not file_path.exists():
            raise FileValidationError("File does not exist")
        
        if not file_path.is_file():
            raise FileValidationError("Path is not a file")
        
        if not os.access(file_path, os.R_OK):
            raise FileValidationError("File is not readable")
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size < self.MIN_FILE_SIZE:
                raise FileValidationError("File is empty")
            
            if file_size > self.MAX_FILE_SIZE:
                raise FileValidationError(f"File too large: {file_size} bytes")
        
        except OSError as e:
            raise FileValidationError(f"Cannot access file stats: {e}")
        
        # Check file content and syntax
        try:
            content = self._read_file_content(file_path)
            if not content.strip():
                raise FileValidationError("File contains only whitespace")
            
            # Basic Python syntax validation
            try:
                ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                raise FileValidationError(f"Python syntax error: {e}")
        
        except UnicodeDecodeError as e:
            raise FileValidationError(f"File encoding error: {e}")
        except Exception as e:
            raise FileValidationError(f"Error reading file content: {e}")
        
        return True
    
    def filter_files(self, files: List[Path]) -> List[Path]:
        """
        Filter files based on exclude patterns.
        
        Args:
            files: List of files to filter
            
        Returns:
            Filtered list of files
        """
        filtered_files = []
        
        for file_path in files:
            if not self._matches_exclude_pattern(file_path):
                filtered_files.append(file_path)
            else:
                logger.debug(f"Excluding file due to pattern match: {file_path}")
        
        return filtered_files
    
    def _walk_directory(self, directory_path: Path) -> Iterator[Path]:
        """
        Walk directory tree recursively, yielding Python files.
        
        Args:
            directory_path: Directory to walk
            
        Yields:
            Path objects for potential Python files
        """
        # Symlink loop detection
        try:
            real_path = directory_path.resolve()
            if real_path in self._visited_dirs:
                logger.warning(f"Symlink loop detected, skipping: {directory_path}")
                return
            self._visited_dirs.add(real_path)
        except OSError:
            logger.warning(f"Cannot resolve path, skipping: {directory_path}")
            return
        
        try:
            # Use scandir for better performance
            with os.scandir(directory_path) as entries:
                for entry in entries:
                    entry_path = Path(entry.path)
                    
                    # Skip if matches exclude pattern
                    if self._matches_exclude_pattern(entry_path):
                        logger.debug(f"Excluding due to pattern: {entry_path}")
                        continue
                    
                    try:
                        if entry.is_file():
                            # Check if it's a Python file by extension
                            if entry_path.suffix.lower() == '.py':
                                yield entry_path
                        
                        elif entry.is_dir():
                            # Recursively walk subdirectories
                            yield from self._walk_directory(entry_path)
                    
                    except OSError as e:
                        logger.warning(f"Cannot access {entry_path}: {e}")
                        continue
        
        except PermissionError:
            logger.warning(f"Permission denied accessing directory: {directory_path}")
        except OSError as e:
            logger.warning(f"Error accessing directory {directory_path}: {e}")
        finally:
            # Remove from visited set when done with this directory
            self._visited_dirs.discard(real_path)
    
    def _matches_exclude_pattern(self, file_path: Path) -> bool:
        """
        Check if a file path matches any exclude pattern.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if path should be excluded
        """
        path_str = str(file_path)
        path_parts = file_path.parts
        
        for pattern in self.exclude_patterns:
            # Direct filename match
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
            
            # Full path match
            if fnmatch.fnmatch(path_str, pattern):
                return True
            
            # Directory name match in path
            if pattern in path_parts:
                return True
            
            # Pattern with path separators
            if '/' in pattern or '\\' in pattern:
                # Convert pattern to use current OS path separator
                normalized_pattern = pattern.replace('/', os.sep).replace('\\', os.sep)
                if fnmatch.fnmatch(path_str, f"*{normalized_pattern}*"):
                    return True
        
        return False
    
    def _read_file_content(self, file_path: Path) -> str:
        """
        Read file content with encoding detection.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string
            
        Raises:
            UnicodeDecodeError: If file cannot be decoded
        """
        # Try UTF-8 first (most common)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            pass
        
        # Try to detect encoding
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            
            if encoding and detected.get('confidence', 0) > 0.7:
                return raw_data.decode(encoding)
        
        except Exception:
            pass
        
        # Fallback to latin-1 (can decode any byte sequence)
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                # Check if it looks like text
                if '\x00' in content:  # Binary file indicator
                    raise UnicodeDecodeError('binary', b'', 0, 1, 'Binary file detected')
                return content
        except Exception:
            pass
        
        raise UnicodeDecodeError('unknown', b'', 0, 1, 'Cannot decode file')
    
    def find_all_python_files_with_details(self, directory_path: Path) -> dict:
        """
        Find all Python files with detailed information about valid/invalid files.
        
        Args:
            directory_path: Directory to search
            
        Returns:
            Dictionary with detailed file information
        """
        if not isinstance(directory_path, Path):
            directory_path = Path(directory_path)
        
        result = {
            'valid_files': [],
            'invalid_files': [],
            'excluded_files': [],
            'errors': []
        }
        
        # Validate directory exists and is accessible
        try:
            if not directory_path.exists():
                raise DirectoryAccessError(f"Directory does not exist: {directory_path}")
            
            if not directory_path.is_dir():
                raise DirectoryAccessError(f"Path is not a directory: {directory_path}")
            
            if not os.access(directory_path, os.R_OK):
                raise DirectoryAccessError(f"Directory is not readable: {directory_path}")
        
        except DirectoryAccessError as e:
            result['errors'].append(str(e))
            return result
        
        # Walk directory tree and collect all Python files
        try:
            for file_path in self._walk_directory(directory_path):
                try:
                    if self.is_valid_python_file(file_path):
                        result['valid_files'].append(file_path)
                except FileValidationError as e:
                    result['invalid_files'].append({
                        'file': file_path,
                        'reason': str(e)
                    })
                except Exception as e:
                    result['errors'].append(f"Error validating file {file_path}: {e}")
        
        except Exception as e:
            result['errors'].append(f"Error walking directory {directory_path}: {e}")
        
        # Also find files that were excluded by patterns
        try:
            all_py_files = list(directory_path.rglob("*.py"))
            found_files = set(result['valid_files'] + [item['file'] for item in result['invalid_files']])
            
            for py_file in all_py_files:
                if py_file not in found_files:
                    if self._matches_exclude_pattern(py_file):
                        result['excluded_files'].append({
                            'file': py_file,
                            'reason': 'Matches exclude pattern'
                        })
        except Exception as e:
            result['errors'].append(f"Error finding excluded files: {e}")
        
        # Sort all lists
        result['valid_files'].sort()
        result['invalid_files'].sort(key=lambda x: x['file'])
        result['excluded_files'].sort(key=lambda x: x['file'])
        
        return result
    
    def get_statistics(self, directory_path: Path) -> dict:
        """
        Get statistics about the file discovery process.
        
        Args:
            directory_path: Directory that was analyzed
            
        Returns:
            Dictionary with statistics
        """
        python_files, errors = self.find_python_files(directory_path)
        
        return {
            'total_python_files': len(python_files),
            'errors_encountered': len(errors),
            'exclude_patterns_used': len(self.exclude_patterns),
            'directory_analyzed': str(directory_path),
            'largest_file': max((f.stat().st_size for f in python_files), default=0),
            'smallest_file': min((f.stat().st_size for f in python_files), default=0),
            'total_size': sum(f.stat().st_size for f in python_files)
        }