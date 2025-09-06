"""
Output formatting for interview questions.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from ..models.question_models import QuestionGenerationResult, Question
from ..models.context_models import CodeContext
from .formatters.json_formatter import JSONFormatter
from .formatters.markdown_formatter import MarkdownFormatter
from .report_generator import ReportGenerator
from .file_exporter import FileExporter
from .progress_tracker import ProgressTracker, ProgressStatus


logger = logging.getLogger(__name__)


class OutputFormatterError(Exception):
    """Exception raised for output formatting errors."""
    pass


class OutputFormatter:
    """Main orchestrator for formatting and exporting interview questions."""
    
    def __init__(self, default_format: str = "json", include_progress: bool = True):
        """
        Initialize the output formatter.
        
        Args:
            default_format: Default output format ("json", "markdown", "both")
            include_progress: Whether to show progress indicators
        """
        self.default_format = default_format
        self.include_progress = include_progress
        
        # Initialize formatters
        self.json_formatter = JSONFormatter(pretty_print=True, include_metadata=True)
        self.markdown_formatter = MarkdownFormatter(include_toc=True, include_metadata=True)
        self.report_generator = ReportGenerator()
        self.file_exporter = FileExporter(backup_existing=True, create_directories=True)
        
        # Progress tracking
        self.progress_tracker = ProgressTracker(show_progress_bar=include_progress)
        
        logger.info(f"OutputFormatter initialized with default format: {default_format}")
    
    def format_as_json(self, result: QuestionGenerationResult,
                      context: Optional[CodeContext] = None,
                      source_code: Optional[str] = None,
                      include_context: bool = False) -> str:
        """
        Format questions as JSON.
        
        Args:
            result: Question generation result
            context: Optional code context
            source_code: Optional source code
            include_context: Whether to include context information
            
        Returns:
            JSON formatted string
        """
        try:
            if include_context and context:
                formatted_data = self.json_formatter.format_with_context(
                    result, context, source_code
                )
            else:
                formatted_data = self.json_formatter.format_generation_result(result)
            
            return self.json_formatter.to_json_string(formatted_data)
            
        except Exception as e:
            logger.error(f"Error formatting as JSON: {e}")
            raise OutputFormatterError(f"JSON formatting failed: {str(e)}")
    
    def format_as_markdown(self, result: QuestionGenerationResult,
                          context: Optional[CodeContext] = None,
                          source_code: Optional[str] = None,
                          title: str = "Interview Questions",
                          style: str = "interview") -> str:
        """
        Format questions as Markdown.
        
        Args:
            result: Question generation result
            context: Optional code context
            source_code: Optional source code
            title: Document title
            style: Markdown style ("interview", "study_guide", "compact")
            
        Returns:
            Markdown formatted string
        """
        try:
            # Create formatter with specified style
            formatter = MarkdownFormatter(
                include_toc=True,
                include_metadata=True,
                style=style
            )
            
            if context:
                return formatter.format_with_context(result, context, source_code, title)
            else:
                return formatter.format_generation_result(result, title)
                
        except Exception as e:
            logger.error(f"Error formatting as Markdown: {e}")
            raise OutputFormatterError(f"Markdown formatting failed: {str(e)}")
    
    def create_summary_report(self, result: QuestionGenerationResult,
                            context: Optional[CodeContext] = None,
                            include_recommendations: bool = True) -> str:
        """
        Create a comprehensive summary report.
        
        Args:
            result: Question generation result
            context: Optional code context
            include_recommendations: Whether to include recommendations
            
        Returns:
            Summary report string
        """
        try:
            return self.report_generator.generate_summary_report(
                result, context, include_recommendations
            )
        except Exception as e:
            logger.error(f"Error creating summary report: {e}")
            raise OutputFormatterError(f"Summary report generation failed: {str(e)}")
    
    def create_analysis_report(self, context: CodeContext) -> str:
        """
        Create a detailed code analysis report.
        
        Args:
            context: Code context to analyze
            
        Returns:
            Analysis report string
        """
        try:
            return self.report_generator.generate_analysis_report(context)
        except Exception as e:
            logger.error(f"Error creating analysis report: {e}")
            raise OutputFormatterError(f"Analysis report generation failed: {str(e)}")
    
    def create_performance_report(self, result: QuestionGenerationResult) -> str:
        """
        Create a performance analysis report.
        
        Args:
            result: Question generation result
            
        Returns:
            Performance report string
        """
        try:
            return self.report_generator.generate_performance_report(result)
        except Exception as e:
            logger.error(f"Error creating performance report: {e}")
            raise OutputFormatterError(f"Performance report generation failed: {str(e)}")
    
    def export_to_file(self, content: str, file_path: Union[str, Path],
                      encoding: str = 'utf-8', overwrite: bool = False) -> bool:
        """
        Export content to a file.
        
        Args:
            content: Content to write
            file_path: Path to write to
            encoding: File encoding
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if successful
        """
        try:
            return self.file_exporter.export_to_file(
                content, file_path, encoding, overwrite
            )
        except Exception as e:
            logger.error(f"Error exporting to file: {e}")
            raise OutputFormatterError(f"File export failed: {str(e)}")
    
    def export_multiple_formats(self, result: QuestionGenerationResult,
                               output_dir: Union[str, Path],
                               formats: List[str] = None,
                               context: Optional[CodeContext] = None,
                               source_code: Optional[str] = None,
                               filename_base: str = "interview_questions") -> Dict[str, Any]:
        """
        Export result in multiple formats.
        
        Args:
            result: Question generation result
            output_dir: Output directory
            formats: List of formats to export
            context: Optional code context
            source_code: Optional source code
            filename_base: Base filename
            
        Returns:
            Export summary
        """
        if formats is None:
            formats = ["json", "markdown"]
        
        try:
            # Initialize progress tracking
            if self.include_progress:
                steps = [f"Formatting as {fmt}" for fmt in formats] + ["Exporting files"]
                self.progress_tracker.initialize(steps)
                self.progress_tracker.start("Exporting multiple formats")
            
            content_dict = {}
            
            # Format in each requested format
            for i, format_name in enumerate(formats):
                if self.include_progress:
                    self.progress_tracker.update_step(
                        i, 0.0, ProgressStatus.IN_PROGRESS, f"Formatting as {format_name}"
                    )
                
                if format_name.lower() == "json":
                    content_dict["json"] = self.format_as_json(result, context, source_code, True)
                elif format_name.lower() == "markdown":
                    content_dict["markdown"] = self.format_as_markdown(result, context, source_code)
                elif format_name.lower() == "summary":
                    content_dict["summary"] = self.create_summary_report(result, context)
                elif format_name.lower() == "performance":
                    content_dict["performance"] = self.create_performance_report(result)
                
                if self.include_progress:
                    self.progress_tracker.update_step(i, 1.0, ProgressStatus.COMPLETED)
            
            # Export files
            if self.include_progress:
                self.progress_tracker.update_step(
                    len(formats), 0.0, ProgressStatus.IN_PROGRESS, "Exporting files"
                )
            
            export_results = self.file_exporter.export_multiple_formats(
                content_dict, output_dir, filename_base
            )
            
            if self.include_progress:
                self.progress_tracker.update_step(len(formats), 1.0, ProgressStatus.COMPLETED)
                self.progress_tracker.complete("Export completed")
            
            return {
                "success": True,
                "formats_exported": list(content_dict.keys()),
                "export_results": export_results,
                "output_directory": str(output_dir)
            }
            
        except Exception as e:
            if self.include_progress:
                self.progress_tracker.fail(str(e))
            logger.error(f"Error in multiple format export: {e}")
            raise OutputFormatterError(f"Multiple format export failed: {str(e)}")
    
    def export_structured_output(self, result: QuestionGenerationResult,
                                output_dir: Union[str, Path],
                                formats: List[str] = None,
                                context: Optional[CodeContext] = None,
                                source_code: Optional[str] = None,
                                include_reports: bool = True) -> Dict[str, Any]:
        """
        Export result in a structured directory format with reports.
        
        Args:
            result: Question generation result
            output_dir: Output directory
            formats: List of formats to export
            context: Optional code context
            source_code: Optional source code
            include_reports: Whether to include analysis reports
            
        Returns:
            Export summary
        """
        if formats is None:
            formats = ["json", "markdown"]
        
        try:
            # Initialize progress tracking
            total_steps = len(formats) + (3 if include_reports else 1)  # +1 for structured export, +2 for reports
            if self.include_progress:
                steps = [f"Format {fmt}" for fmt in formats]
                if include_reports:
                    steps.extend(["Generate summary report", "Generate performance report"])
                steps.append("Create structured export")
                
                self.progress_tracker.initialize(steps)
                self.progress_tracker.start("Creating structured export")
            
            # Use file exporter's structured export
            export_summary = self.file_exporter.export_structured_output(
                result, output_dir, formats, include_metadata=True
            )
            
            # Add reports if requested
            if include_reports and export_summary.get('export_directory'):
                export_dir = Path(export_summary['export_directory'])
                
                try:
                    # Summary report
                    if self.include_progress:
                        step_idx = len(formats)
                        self.progress_tracker.update_step(
                            step_idx, 0.0, ProgressStatus.IN_PROGRESS, "Generating summary report"
                        )
                    
                    summary_report = self.create_summary_report(result, context)
                    summary_file = export_dir / "summary_report.txt"
                    self.export_to_file(summary_report, summary_file, overwrite=True)
                    export_summary['files_created'].append(str(summary_file))
                    
                    if self.include_progress:
                        self.progress_tracker.update_step(step_idx, 1.0, ProgressStatus.COMPLETED)
                    
                    # Performance report
                    if self.include_progress:
                        step_idx = len(formats) + 1
                        self.progress_tracker.update_step(
                            step_idx, 0.0, ProgressStatus.IN_PROGRESS, "Generating performance report"
                        )
                    
                    perf_report = self.create_performance_report(result)
                    perf_file = export_dir / "performance_report.txt"
                    self.export_to_file(perf_report, perf_file, overwrite=True)
                    export_summary['files_created'].append(str(perf_file))
                    
                    if self.include_progress:
                        self.progress_tracker.update_step(step_idx, 1.0, ProgressStatus.COMPLETED)
                    
                except Exception as e:
                    export_summary['errors'].append(f"Report generation failed: {str(e)}")
            
            if self.include_progress:
                self.progress_tracker.complete("Structured export completed")
            
            return export_summary
            
        except Exception as e:
            if self.include_progress:
                self.progress_tracker.fail(str(e))
            logger.error(f"Error in structured export: {e}")
            raise OutputFormatterError(f"Structured export failed: {str(e)}")
    
    def format_and_export(self, result: QuestionGenerationResult,
                         output_path: Union[str, Path],
                         format_type: str = None,
                         context: Optional[CodeContext] = None,
                         source_code: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Format and export in one operation.
        
        Args:
            result: Question generation result
            output_path: Output file or directory path
            format_type: Format type (defaults to self.default_format)
            context: Optional code context
            source_code: Optional source code
            **kwargs: Additional formatting options
            
        Returns:
            Export summary
        """
        format_type = format_type or self.default_format
        output_path = Path(output_path)
        
        try:
            if format_type == "both" or format_type == "multiple":
                # Export multiple formats to directory
                return self.export_multiple_formats(
                    result, output_path, ["json", "markdown"], context, source_code
                )
            
            elif format_type == "structured":
                # Export structured output
                return self.export_structured_output(
                    result, output_path, ["json", "markdown"], context, source_code
                )
            
            else:
                # Single format export
                if format_type == "json":
                    content = self.format_as_json(result, context, source_code, True)
                    if not output_path.suffix:
                        output_path = output_path.with_suffix('.json')
                
                elif format_type == "markdown":
                    content = self.format_as_markdown(result, context, source_code)
                    if not output_path.suffix:
                        output_path = output_path.with_suffix('.md')
                
                elif format_type == "summary":
                    content = self.create_summary_report(result, context)
                    if not output_path.suffix:
                        output_path = output_path.with_suffix('.txt')
                
                else:
                    raise OutputFormatterError(f"Unsupported format type: {format_type}")
                
                success = self.export_to_file(content, output_path, overwrite=True)
                
                return {
                    "success": success,
                    "format": format_type,
                    "output_file": str(output_path),
                    "file_size": len(content)
                }
        
        except Exception as e:
            logger.error(f"Error in format_and_export: {e}")
            raise OutputFormatterError(f"Format and export failed: {str(e)}")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats."""
        return ["json", "markdown", "summary", "performance", "both", "multiple", "structured"]
    
    def validate_format(self, format_type: str) -> bool:
        """Validate if format type is supported."""
        return format_type.lower() in self.get_supported_formats()
    
    def get_format_info(self) -> Dict[str, str]:
        """Get information about supported formats."""
        return {
            "json": "Structured JSON format with full metadata",
            "markdown": "Human-readable Markdown format with formatting",
            "summary": "Text summary report with statistics and analysis",
            "performance": "Performance analysis report",
            "both": "Both JSON and Markdown formats",
            "multiple": "Multiple formats in separate files",
            "structured": "Complete structured export with all formats and reports"
        }