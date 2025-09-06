"""File export functionality for saving formatted output."""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json
import zipfile

from ..models.question_models import QuestionGenerationResult


logger = logging.getLogger(__name__)


class FileExportError(Exception):
    """Exception raised for file export errors."""
    pass


class FileExporter:
    """Handles exporting formatted content to files with various options."""
    
    def __init__(self, backup_existing: bool = True, create_directories: bool = True):
        """
        Initialize file exporter.
        
        Args:
            backup_existing: Whether to backup existing files before overwriting
            create_directories: Whether to create directories if they don't exist
        """
        self.backup_existing = backup_existing
        self.create_directories = create_directories
        self.export_timestamp = datetime.now()
    
    def export_to_file(self, content: str, file_path: Union[str, Path],
                      encoding: str = 'utf-8', overwrite: bool = False) -> bool:
        """
        Export content to a single file.
        
        Args:
            content: Content to write
            file_path: Path to write to
            encoding: File encoding
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            # Create directories if needed
            if self.create_directories:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and handle accordingly
            if file_path.exists():
                if not overwrite:
                    logger.warning(f"File {file_path} already exists and overwrite=False")
                    return False
                
                if self.backup_existing:
                    self._backup_file(file_path)
            
            # Write content
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"Successfully exported content to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to file {file_path}: {e}")
            raise FileExportError(f"Failed to export to {file_path}: {str(e)}")
    
    def export_multiple_formats(self, content_dict: Dict[str, str],
                               base_path: Union[str, Path],
                               filename_base: str = "interview_questions") -> Dict[str, bool]:
        """
        Export content in multiple formats to separate files.
        
        Args:
            content_dict: Dictionary mapping format names to content
            base_path: Base directory path
            filename_base: Base filename (without extension)
            
        Returns:
            Dictionary mapping format names to success status
        """
        results = {}
        base_path = Path(base_path)
        
        # Create base directory
        if self.create_directories:
            base_path.mkdir(parents=True, exist_ok=True)
        
        # Export each format
        for format_name, content in content_dict.items():
            try:
                # Determine file extension
                extension = self._get_extension_for_format(format_name)
                filename = f"{filename_base}.{extension}"
                file_path = base_path / filename
                
                success = self.export_to_file(content, file_path, overwrite=True)
                results[format_name] = success
                
            except Exception as e:
                logger.error(f"Error exporting {format_name} format: {e}")
                results[format_name] = False
        
        return results
    
    def export_structured_output(self, result: QuestionGenerationResult,
                                output_dir: Union[str, Path],
                                formats: List[str] = None,
                                include_metadata: bool = True) -> Dict[str, Any]:
        """
        Export generation result in a structured directory format.
        
        Args:
            result: Question generation result
            output_dir: Output directory
            formats: List of formats to export ('json', 'markdown', 'txt')
            include_metadata: Whether to include metadata files
            
        Returns:
            Export summary with file paths and status
        """
        if formats is None:
            formats = ['json', 'markdown']
        
        output_dir = Path(output_dir)
        timestamp = self.export_timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Create structured directory
        export_dir = output_dir / f"interview_questions_{timestamp}"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        export_summary = {
            'export_directory': str(export_dir),
            'timestamp': timestamp,
            'formats_exported': [],
            'files_created': [],
            'errors': []
        }
        
        try:
            # Import formatters here to avoid circular imports
            from .formatters.json_formatter import JSONFormatter
            from .formatters.markdown_formatter import MarkdownFormatter
            
            # Export in requested formats
            if 'json' in formats:
                try:
                    json_formatter = JSONFormatter(pretty_print=True)
                    json_content = json_formatter.to_json_string(
                        json_formatter.format_generation_result(result)
                    )
                    json_file = export_dir / "questions.json"
                    self.export_to_file(json_content, json_file, overwrite=True)
                    export_summary['formats_exported'].append('json')
                    export_summary['files_created'].append(str(json_file))
                except Exception as e:
                    export_summary['errors'].append(f"JSON export failed: {str(e)}")
            
            if 'markdown' in formats:
                try:
                    md_formatter = MarkdownFormatter(include_toc=True)
                    md_content = md_formatter.format_generation_result(result)
                    md_file = export_dir / "questions.md"
                    self.export_to_file(md_content, md_file, overwrite=True)
                    export_summary['formats_exported'].append('markdown')
                    export_summary['files_created'].append(str(md_file))
                except Exception as e:
                    export_summary['errors'].append(f"Markdown export failed: {str(e)}")
            
            if 'txt' in formats:
                try:
                    # Simple text format
                    txt_content = self._format_as_text(result)
                    txt_file = export_dir / "questions.txt"
                    self.export_to_file(txt_content, txt_file, overwrite=True)
                    export_summary['formats_exported'].append('txt')
                    export_summary['files_created'].append(str(txt_file))
                except Exception as e:
                    export_summary['errors'].append(f"Text export failed: {str(e)}")
            
            # Export metadata if requested
            if include_metadata:
                try:
                    metadata = self._create_metadata(result)
                    metadata_file = export_dir / "metadata.json"
                    self.export_to_file(json.dumps(metadata, indent=2), metadata_file, overwrite=True)
                    export_summary['files_created'].append(str(metadata_file))
                except Exception as e:
                    export_summary['errors'].append(f"Metadata export failed: {str(e)}")
            
            # Create README
            try:
                readme_content = self._create_readme(result, export_summary)
                readme_file = export_dir / "README.md"
                self.export_to_file(readme_content, readme_file, overwrite=True)
                export_summary['files_created'].append(str(readme_file))
            except Exception as e:
                export_summary['errors'].append(f"README creation failed: {str(e)}")
            
            logger.info(f"Structured export completed to {export_dir}")
            
        except Exception as e:
            logger.error(f"Error in structured export: {e}")
            export_summary['errors'].append(f"Structured export failed: {str(e)}")
        
        return export_summary
    
    def create_archive(self, source_dir: Union[str, Path],
                      archive_path: Union[str, Path] = None,
                      format: str = 'zip') -> Optional[Path]:
        """
        Create an archive of the exported files.
        
        Args:
            source_dir: Directory to archive
            archive_path: Path for the archive file
            format: Archive format ('zip', 'tar', 'tar.gz')
            
        Returns:
            Path to created archive or None if failed
        """
        try:
            source_dir = Path(source_dir)
            
            if archive_path is None:
                archive_path = source_dir.parent / f"{source_dir.name}.{format}"
            else:
                archive_path = Path(archive_path)
            
            if format == 'zip':
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in source_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_dir)
                            zipf.write(file_path, arcname)
            
            elif format in ['tar', 'tar.gz']:
                import tarfile
                mode = 'w:gz' if format == 'tar.gz' else 'w'
                with tarfile.open(archive_path, mode) as tar:
                    tar.add(source_dir, arcname=source_dir.name)
            
            else:
                raise FileExportError(f"Unsupported archive format: {format}")
            
            logger.info(f"Created archive: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            return None
    
    def export_with_templates(self, result: QuestionGenerationResult,
                            template_dir: Union[str, Path],
                            output_dir: Union[str, Path]) -> Dict[str, Any]:
        """
        Export using custom templates.
        
        Args:
            result: Question generation result
            template_dir: Directory containing templates
            output_dir: Output directory
            
        Returns:
            Export summary
        """
        # This would be implemented for custom template support
        # For now, return a placeholder
        return {
            'status': 'not_implemented',
            'message': 'Template-based export not yet implemented'
        }
    
    def _backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a backup of an existing file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.warning(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def _get_extension_for_format(self, format_name: str) -> str:
        """Get file extension for format name."""
        extensions = {
            'json': 'json',
            'markdown': 'md',
            'text': 'txt',
            'html': 'html',
            'csv': 'csv',
            'xml': 'xml'
        }
        return extensions.get(format_name.lower(), 'txt')
    
    def _format_as_text(self, result: QuestionGenerationResult) -> str:
        """Format result as plain text."""
        lines = []
        
        lines.append("INTERVIEW QUESTIONS")
        lines.append("=" * 50)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Questions: {len(result.questions)}")
        lines.append("")
        
        for i, question in enumerate(result.questions, 1):
            lines.append(f"QUESTION {i}")
            lines.append("-" * 20)
            lines.append(f"Category: {question.category.value}")
            lines.append(f"Difficulty: {question.difficulty.value}")
            lines.append("")
            lines.append("Question:")
            lines.append(question.question_text)
            lines.append("")
            
            if question.code_snippet:
                lines.append("Code:")
                lines.append(question.code_snippet)
                lines.append("")
            
            if question.expected_answer:
                lines.append("Expected Answer:")
                lines.append(question.expected_answer)
                lines.append("")
            
            if question.hints:
                lines.append("Hints:")
                for j, hint in enumerate(question.hints, 1):
                    hint_text = hint.text if hasattr(hint, 'text') else hint
                    lines.append(f"  {j}. {hint_text}")
                lines.append("")
            
            lines.append("=" * 50)
            lines.append("")
        
        return "\n".join(lines)
    
    def _create_metadata(self, result: QuestionGenerationResult) -> Dict[str, Any]:
        """Create metadata for the export."""
        return {
            'export_info': {
                'timestamp': self.export_timestamp.isoformat(),
                'generator_version': '1.0',
                'export_format_version': '1.0'
            },
            'generation_stats': {
                'total_questions': len(result.questions),
                'success': result.success,
                'processing_time': result.processing_time,
                'api_calls_made': result.api_calls_made,
                'tokens_used': result.tokens_used
            },
            'question_distribution': self._analyze_distribution(result.questions),
            'errors': result.errors,
            'warnings': result.warnings
        }
    
    def _analyze_distribution(self, questions) -> Dict[str, Any]:
        """Analyze question distribution for metadata."""
        if not questions:
            return {}
        
        category_counts = {}
        difficulty_counts = {}
        
        for question in questions:
            cat = question.category.value
            diff = question.difficulty.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        return {
            'by_category': category_counts,
            'by_difficulty': difficulty_counts
        }
    
    def _create_readme(self, result: QuestionGenerationResult,
                      export_summary: Dict[str, Any]) -> str:
        """Create README content for the export."""
        lines = [
            "# Interview Questions Export",
            "",
            f"Generated on: {self.export_timestamp.strftime('%Y-%m-%d at %H:%M:%S')}",
            f"Total Questions: {len(result.questions)}",
            "",
            "## Files in this Export",
            ""
        ]
        
        for file_path in export_summary.get('files_created', []):
            filename = Path(file_path).name
            lines.append(f"- `{filename}` - {self._describe_file(filename)}")
        
        lines.extend([
            "",
            "## Question Distribution",
            ""
        ])
        
        if result.questions:
            # Category distribution
            category_counts = {}
            for question in result.questions:
                cat = question.category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            lines.append("### By Category")
            for category, count in sorted(category_counts.items()):
                lines.append(f"- {category.title()}: {count} questions")
            
            # Difficulty distribution
            difficulty_counts = {}
            for question in result.questions:
                diff = question.difficulty.value
                difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            
            lines.append("")
            lines.append("### By Difficulty")
            for difficulty, count in sorted(difficulty_counts.items()):
                lines.append(f"- {difficulty.title()}: {count} questions")
        
        lines.extend([
            "",
            "## Usage",
            "",
            "- Open `questions.md` for a formatted view of all questions",
            "- Use `questions.json` for programmatic access to the data",
            "- Check `metadata.json` for generation statistics and details",
            "",
            "---",
            "*Generated by Interview Question Generator v1.0*"
        ])
        
        return "\n".join(lines)
    
    def _describe_file(self, filename: str) -> str:
        """Provide description for a file based on its name."""
        descriptions = {
            'questions.json': 'Questions in JSON format',
            'questions.md': 'Questions in Markdown format',
            'questions.txt': 'Questions in plain text format',
            'metadata.json': 'Generation metadata and statistics',
            'README.md': 'This documentation file'
        }
        return descriptions.get(filename, 'Generated file')