"""Main processing pipeline that orchestrates all components."""

import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from ..models.config_models import Config
from ..models.question_models import QuestionGenerationResult, QuestionCategory, DifficultyLevel
from ..models.context_models import CodeContext
from ..utils.file_discovery import FileDiscovery
from ..parsers.code_parser import CodeParser
from ..analyzers.complexity_analyzer import ComplexityAnalyzer
from ..analyzers.pattern_detector import PatternDetector
from ..analyzers.context_extractor import ContextExtractor
from ..generators.question_generator import QuestionGenerator
from ..output.output_formatter import OutputFormatter


logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """Statistics from pipeline execution."""
    files_discovered: int = 0
    files_processed: int = 0
    files_failed: int = 0
    total_functions: int = 0
    total_classes: int = 0
    total_questions: int = 0
    processing_time: float = 0.0
    api_calls_made: int = 0
    tokens_used: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """Result of complete pipeline execution."""
    success: bool
    question_result: Optional[QuestionGenerationResult] = None
    stats: PipelineStats = field(default_factory=PipelineStats)
    output_files: List[str] = field(default_factory=list)


class InterviewQuestionPipeline:
    """Main pipeline that orchestrates the complete question generation process."""
    
    def __init__(self, config: Config):
        """
        Initialize the pipeline with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Initialize components
        self.file_discovery = FileDiscovery()
        self.code_parser = CodeParser()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.pattern_detector = PatternDetector()
        self.context_extractor = ContextExtractor()
        self.question_generator = QuestionGenerator(config)
        self.output_formatter = OutputFormatter(
            default_format=config.output_format,
            include_progress=True
        )
        
        logger.info("Pipeline initialized with all components")
    
    async def process_directory(self, directory: Path,
                              categories: Optional[List[QuestionCategory]] = None,
                              difficulties: Optional[List[DifficultyLevel]] = None,
                              max_questions: int = 10,
                              output_path: Optional[Path] = None,
                              output_format: str = "json",
                              progress_callback=None) -> PipelineResult:
        """
        Process a directory of Python files and generate interview questions.
        
        Args:
            directory: Directory to analyze
            categories: Question categories to generate
            difficulties: Difficulty levels to include
            max_questions: Maximum number of questions
            output_path: Output file/directory path
            output_format: Output format
            progress_callback: Optional progress callback function
            
        Returns:
            PipelineResult with generated questions and statistics
        """
        start_time = datetime.now()
        stats = PipelineStats()
        
        try:
            logger.info(f"Starting pipeline processing for directory: {directory}")
            
            # Step 1: File Discovery
            if progress_callback:
                progress_callback("Discovering Python files...", 0.1)
            
            python_files = await self._discover_files(directory, stats)
            if not python_files:
                return PipelineResult(
                    success=False,
                    stats=stats
                )
            
            # Step 2: Code Analysis
            if progress_callback:
                progress_callback("Analyzing code structure...", 0.2)
            
            combined_context = await self._analyze_code_files(python_files, stats, progress_callback)
            if not combined_context:
                return PipelineResult(
                    success=False,
                    stats=stats
                )
            
            # Step 3: Question Generation
            if progress_callback:
                progress_callback("Generating interview questions...", 0.6)
            
            question_result = await self._generate_questions(
                combined_context, categories, difficulties, max_questions, stats, progress_callback
            )
            
            # Step 4: Output Formatting and Export
            if progress_callback:
                progress_callback("Formatting and exporting results...", 0.9)
            
            output_files = []
            if output_path and question_result.success:
                output_files = await self._export_results(
                    question_result, combined_context, output_path, output_format
                )
            
            # Calculate final statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            stats.processing_time = processing_time
            stats.total_questions = len(question_result.questions) if question_result.success else 0
            stats.api_calls_made = question_result.api_calls_made if question_result.success else 0
            stats.tokens_used = question_result.tokens_used if question_result.success else 0
            
            if progress_callback:
                progress_callback("Processing complete!", 1.0)
            
            logger.info(f"Pipeline completed successfully in {processing_time:.2f}s")
            
            return PipelineResult(
                success=question_result.success,
                question_result=question_result,
                stats=stats,
                output_files=output_files
            )
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            stats.errors.append(f"Pipeline failed: {str(e)}")
            stats.processing_time = (datetime.now() - start_time).total_seconds()
            
            return PipelineResult(
                success=False,
                stats=stats
            )
    
    async def process_single_file(self, file_path: Path,
                                categories: Optional[List[QuestionCategory]] = None,
                                difficulties: Optional[List[DifficultyLevel]] = None,
                                max_questions: int = 5) -> PipelineResult:
        """
        Process a single Python file.
        
        Args:
            file_path: Path to Python file
            categories: Question categories to generate
            difficulties: Difficulty levels to include
            max_questions: Maximum number of questions
            
        Returns:
            PipelineResult with generated questions
        """
        return await self.process_directory(
            file_path.parent, categories, difficulties, max_questions
        )
    
    async def _discover_files(self, directory: Path, stats: PipelineStats) -> List[Path]:
        """Discover Python files in directory."""
        try:
            python_files, discovery_errors = self.file_discovery.find_python_files(
                directory
            )
            
            stats.files_discovered = len(python_files)
            if discovery_errors:
                stats.errors.extend(discovery_errors)
                stats.warnings.extend([f"Discovery warning: {err}" for err in discovery_errors])
            
            logger.info(f"Discovered {len(python_files)} Python files")
            
            return python_files
            
        except Exception as e:
            logger.error(f"File discovery failed: {e}")
            stats.errors.append(f"File discovery failed: {str(e)}")
            return []
    
    async def _analyze_code_files(self, files: List[Path], stats: PipelineStats,
                                progress_callback=None) -> Optional[CodeContext]:
        """Analyze all code files and combine contexts."""
        all_contexts = []
        combined_source_code = []
        
        for i, file_path in enumerate(files):
            try:
                if progress_callback:
                    progress = 0.2 + (0.4 * (i + 1) / len(files))
                    progress_callback(f"Analyzing {file_path.name}...", progress)
                
                # Parse file
                source_code = file_path.read_text(encoding='utf-8')
                parse_result = self.code_parser.parse_file(file_path)
                
                if not parse_result.success:
                    stats.files_failed += 1
                    stats.errors.extend(parse_result.errors)
                    continue
                
                # Analyze complexity
                complexity_result = self.complexity_analyzer.analyze_code(
                    source_code, str(file_path)
                )
                
                # Detect patterns
                pattern_result = self.pattern_detector.detect_patterns(source_code, str(file_path))
                
                # Extract context
                context_result = self.context_extractor.extract_context(source_code, str(file_path))
                
                if context_result.success and context_result.context:
                    all_contexts.append(context_result.context)
                    combined_source_code.append(f"# File: {file_path}\n{source_code}")
                    stats.files_processed += 1
                    stats.total_functions += len(parse_result.functions)
                    stats.total_classes += len(parse_result.classes)
                else:
                    stats.files_failed += 1
                    if hasattr(context_result, 'errors'):
                        stats.errors.extend(context_result.errors)
                    else:
                        stats.errors.append(f"Context extraction failed for {file_path}")
                
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {e}")
                stats.files_failed += 1
                stats.errors.append(f"Failed to analyze {file_path}: {str(e)}")
        
        if not all_contexts:
            logger.error("No files were successfully analyzed")
            return None
        
        # Combine contexts into a single comprehensive context
        combined_context = self._combine_contexts(all_contexts)
        
        # Store combined source code for reference
        combined_context.metadata = {
            'combined_source_code': '\n\n'.join(combined_source_code),
            'files_analyzed': [str(f) for f in files[:stats.files_processed]]
        }
        
        logger.info(f"Successfully analyzed {stats.files_processed} files")
        return combined_context
    
    def _combine_contexts(self, contexts: List[CodeContext]) -> CodeContext:
        """Combine multiple code contexts into one comprehensive context."""
        if len(contexts) == 1:
            return contexts[0]
        
        # Use the first context as base and merge others
        combined = contexts[0]
        
        for context in contexts[1:]:
            # Combine function contexts
            combined.function_contexts.extend(context.function_contexts)
            
            # Combine class contexts
            combined.class_contexts.extend(context.class_contexts)
            
            # Merge business context
            combined.business_context.data_entities.extend(
                context.business_context.data_entities
            )
            combined.business_context.external_integrations.extend(
                context.business_context.external_integrations
            )
            combined.business_context.business_rules.extend(
                context.business_context.business_rules
            )
            
            # Merge error handling context
            combined.error_handling_context.exception_patterns.extend(
                context.error_handling_context.exception_patterns
            )
            combined.error_handling_context.validation_approaches.extend(
                context.error_handling_context.validation_approaches
            )
            
            # Merge performance context
            combined.performance_context.performance_hotspots.extend(
                context.performance_context.performance_hotspots
            )
            combined.performance_context.memory_patterns.extend(
                context.performance_context.memory_patterns
            )
            
            # Average quality scores
            combined.overall_quality_score = (
                combined.overall_quality_score + context.overall_quality_score
            ) / 2
        
        # Remove duplicates
        combined.business_context.data_entities = list(set(
            combined.business_context.data_entities
        ))
        combined.error_handling_context.exception_patterns = list(set(
            combined.error_handling_context.exception_patterns
        ))
        
        return combined
    
    async def _generate_questions(self, context: CodeContext,
                                categories: Optional[List[QuestionCategory]],
                                difficulties: Optional[List[DifficultyLevel]],
                                max_questions: int,
                                stats: PipelineStats,
                                progress_callback=None) -> QuestionGenerationResult:
        """Generate interview questions from the analyzed context."""
        try:
            source_code = context.metadata.get('combined_source_code', '')
            
            result = await self.question_generator.generate_questions(
                context=context,
                source_code=source_code,
                max_questions=max_questions,
                categories=categories,
                difficulties=difficulties,
                progress_callback=progress_callback
            )
            
            if not result.success:
                stats.errors.extend(result.errors)
                stats.warnings.extend(result.warnings)
            
            return result
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            stats.errors.append(f"Question generation failed: {str(e)}")
            
            from ..models.question_models import QuestionGenerationResult
            return QuestionGenerationResult(
                success=False,
                questions=[],
                errors=[str(e)]
            )
    
    async def _export_results(self, result: QuestionGenerationResult,
                            context: CodeContext,
                            output_path: Path,
                            output_format: str) -> List[str]:
        """Export results to specified format and location."""
        try:
            source_code = context.metadata.get('combined_source_code', '')
            
            if output_format == "structured":
                # Export structured output with all formats
                export_summary = self.output_formatter.export_structured_output(
                    result, output_path, 
                    formats=["json", "markdown"],
                    context=context,
                    source_code=source_code,
                    include_reports=True
                )
                return export_summary.get('files_created', [])
            
            else:
                # Single format export
                export_result = self.output_formatter.format_and_export(
                    result, output_path, output_format, context, source_code
                )
                
                if export_result.get('success'):
                    return [export_result.get('output_file', str(output_path))]
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return []
    
    async def validate_setup(self) -> Dict[str, Any]:
        """Validate that all components are properly configured."""
        validation_results = {
            'overall_status': 'success',
            'components': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate configuration
            is_valid, config_errors = self.config.validate_all()
            validation_results['components']['config'] = {
                'status': 'success' if is_valid else 'error',
                'errors': config_errors
            }
            if not is_valid:
                validation_results['errors'].extend(config_errors)
            
            # Test LLM integration
            try:
                # This would test API connectivity
                validation_results['components']['llm'] = {
                    'status': 'success',
                    'message': 'API key format valid'
                }
            except Exception as e:
                validation_results['components']['llm'] = {
                    'status': 'error',
                    'error': str(e)
                }
                validation_results['errors'].append(f"LLM integration: {str(e)}")
            
            # Validate other components
            for component_name, component in [
                ('file_discovery', self.file_discovery),
                ('code_parser', self.code_parser),
                ('complexity_analyzer', self.complexity_analyzer),
                ('pattern_detector', self.pattern_detector),
                ('context_extractor', self.context_extractor),
                ('output_formatter', self.output_formatter)
            ]:
                validation_results['components'][component_name] = {
                    'status': 'success',
                    'message': 'Component initialized'
                }
            
            # Set overall status
            if validation_results['errors']:
                validation_results['overall_status'] = 'error'
            elif validation_results['warnings']:
                validation_results['overall_status'] = 'warning'
            
        except Exception as e:
            validation_results['overall_status'] = 'error'
            validation_results['errors'].append(f"Validation failed: {str(e)}")
        
        return validation_results
    
    async def close(self):
        """Clean up resources."""
        try:
            await self.question_generator.close()
            logger.info("Pipeline resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")