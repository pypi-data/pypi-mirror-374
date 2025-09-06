"""Generate comprehensive analysis and summary reports."""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

from ..models.question_models import (
    Question, QuestionGenerationResult, QuestionCategory, DifficultyLevel
)
from ..models.context_models import CodeContext


logger = logging.getLogger(__name__)


@dataclass
class ReportStats:
    """Statistics for report generation."""
    total_questions: int = 0
    category_distribution: Dict[str, int] = field(default_factory=dict)
    difficulty_distribution: Dict[str, int] = field(default_factory=dict)
    average_time_estimate: float = 0.0
    total_time_estimate: int = 0
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    generation_metrics: Dict[str, Any] = field(default_factory=dict)


class ReportGenerator:
    """Generates comprehensive analysis and summary reports."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.report_timestamp = datetime.now()
    
    def generate_summary_report(self, result: QuestionGenerationResult,
                              context: Optional[CodeContext] = None,
                              include_recommendations: bool = True) -> str:
        """
        Generate a comprehensive summary report.
        
        Args:
            result: Question generation result
            context: Optional code context for enhanced analysis
            include_recommendations: Whether to include recommendations
            
        Returns:
            Formatted summary report
        """
        try:
            lines = []
            
            # Report header
            lines.extend(self._generate_header())
            
            # Executive summary
            lines.extend(self._generate_executive_summary(result, context))
            
            # Detailed statistics
            lines.extend(self._generate_detailed_stats(result))
            
            # Code analysis summary (if context provided)
            if context:
                lines.extend(self._analyze_business_context(context.business_context))
            
            # Question quality analysis
            lines.extend(self._generate_quality_analysis(result))
            
            # Performance metrics
            lines.extend(self._generate_performance_metrics(result))
            
            # Recommendations (if requested)
            if include_recommendations:
                lines.extend(self._generate_recommendations(result, context))
            
            # Footer
            lines.extend(self._generate_footer())
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return f"Error generating report: {str(e)}"
    
    def generate_analysis_report(self, context: CodeContext) -> str:
        """
        Generate a detailed code analysis report.
        
        Args:
            context: Code context to analyze
            
        Returns:
            Formatted analysis report
        """
        try:
            lines = []
            
            # Header
            lines.append("=" * 60)
            lines.append("CODE ANALYSIS REPORT")
            lines.append("=" * 60)
            lines.append(f"Generated: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            
            # Business context
            lines.extend(self._analyze_business_context(context.business_context))
            
            # Technical analysis
            lines.extend(self._analyze_technical_aspects(context))
            
            # Quality assessment
            lines.extend(self._analyze_quality_metrics(context))
            
            # Complexity analysis
            lines.extend(self._analyze_complexity(context))
            
            # Documentation analysis
            lines.extend(self._analyze_documentation(context.documentation_context))
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
            return f"Error generating analysis report: {str(e)}"
    
    def generate_performance_report(self, result: QuestionGenerationResult) -> str:
        """
        Generate a performance analysis report.
        
        Args:
            result: Question generation result
            
        Returns:
            Performance report
        """
        try:
            lines = []
            
            lines.append("=" * 50)
            lines.append("PERFORMANCE ANALYSIS REPORT")
            lines.append("=" * 50)
            lines.append(f"Generated: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            
            # Generation performance
            lines.append("GENERATION PERFORMANCE")
            lines.append("-" * 25)
            lines.append(f"Total Processing Time: {result.processing_time:.2f} seconds")
            lines.append(f"Questions Generated: {len(result.questions)}")
            
            if result.processing_time > 0:
                rate = len(result.questions) / result.processing_time
                lines.append(f"Generation Rate: {rate:.2f} questions/second")
            
            lines.append(f"API Calls Made: {result.api_calls_made}")
            lines.append(f"Tokens Used: {result.tokens_used}")
            
            if hasattr(result, 'cost_estimate'):
                lines.append(f"Estimated Cost: ${result.cost_estimate:.4f}")
                
                if result.tokens_used > 0:
                    cost_per_token = result.cost_estimate / result.tokens_used
                    lines.append(f"Cost per Token: ${cost_per_token:.6f}")
            
            lines.append("")
            
            # Efficiency metrics
            if result.api_calls_made > 0:
                lines.append("EFFICIENCY METRICS")
                lines.append("-" * 20)
                
                questions_per_call = len(result.questions) / result.api_calls_made
                lines.append(f"Questions per API Call: {questions_per_call:.2f}")
                
                if result.tokens_used > 0:
                    tokens_per_call = result.tokens_used / result.api_calls_made
                    lines.append(f"Average Tokens per Call: {tokens_per_call:.1f}")
                
                lines.append("")
            
            # Performance recommendations
            lines.extend(self._generate_performance_recommendations(result))
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return f"Error generating performance report: {str(e)}"
    
    def calculate_report_stats(self, result: QuestionGenerationResult) -> ReportStats:
        """Calculate comprehensive statistics for reporting."""
        stats = ReportStats()
        
        if not result.questions:
            return stats
        
        # Basic counts
        stats.total_questions = len(result.questions)
        
        # Category distribution
        for question in result.questions:
            category = question.category.value
            stats.category_distribution[category] = stats.category_distribution.get(category, 0) + 1
        
        # Difficulty distribution
        for question in result.questions:
            difficulty = question.difficulty.value
            stats.difficulty_distribution[difficulty] = stats.difficulty_distribution.get(difficulty, 0) + 1
        
        # Time estimates
        time_estimates = []
        for question in result.questions:
            if hasattr(question, 'time_estimate_minutes') and question.time_estimate_minutes:
                time_estimates.append(question.time_estimate_minutes)
        
        if time_estimates:
            stats.average_time_estimate = sum(time_estimates) / len(time_estimates)
            stats.total_time_estimate = sum(time_estimates)
        
        # Quality metrics
        quality_scores = []
        for question in result.questions:
            if 'quality_score' in question.metadata:
                quality_scores.append(question.metadata['quality_score'])
        
        if quality_scores:
            stats.quality_metrics = {
                'average': sum(quality_scores) / len(quality_scores),
                'min': min(quality_scores),
                'max': max(quality_scores),
                'count': len(quality_scores)
            }
        
        # Generation metrics
        stats.generation_metrics = {
            'processing_time': result.processing_time,
            'api_calls': result.api_calls_made,
            'tokens_used': result.tokens_used,
            'success_rate': 1.0 if result.success else 0.0
        }
        
        return stats
    
    def _generate_header(self) -> List[str]:
        """Generate report header."""
        return [
            "=" * 70,
            "INTERVIEW QUESTIONS GENERATION REPORT",
            "=" * 70,
            f"Generated: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Report Version: 1.0",
            ""
        ]
    
    def _generate_executive_summary(self, result: QuestionGenerationResult,
                                  context: Optional[CodeContext]) -> List[str]:
        """Generate executive summary section."""
        lines = ["EXECUTIVE SUMMARY", "-" * 20, ""]
        
        # Success status
        if result.success:
            lines.append(f"✓ Successfully generated {len(result.questions)} interview questions")
        else:
            lines.append(f"✗ Generation failed with {len(result.errors)} errors")
        
        # Key metrics
        if result.questions:
            stats = self.calculate_report_stats(result)
            
            lines.append(f"• Processing completed in {result.processing_time:.2f} seconds")
            lines.append(f"• Average question quality: {stats.quality_metrics.get('average', 0):.2f}/1.0")
            lines.append(f"• Estimated interview time: {stats.total_time_estimate} minutes")
            
            # Most common category
            if stats.category_distribution:
                top_category = max(stats.category_distribution.items(), key=lambda x: x[1])
                lines.append(f"• Primary focus area: {top_category[0]} ({top_category[1]} questions)")
        
        # Context summary
        if context:
            lines.append(f"• Code domain: {context.business_context.domain_type.value}")
            lines.append(f"• Overall code quality: {context.overall_quality_score:.2f}/1.0")
        
        lines.append("")
        return lines
    
    def _generate_detailed_stats(self, result: QuestionGenerationResult) -> List[str]:
        """Generate detailed statistics section."""
        lines = ["DETAILED STATISTICS", "-" * 20, ""]
        
        if not result.questions:
            lines.append("No questions were generated.")
            lines.append("")
            return lines
        
        stats = self.calculate_report_stats(result)
        
        # Question distribution
        lines.append("Question Distribution by Category:")
        for category, count in sorted(stats.category_distribution.items()):
            percentage = (count / stats.total_questions) * 100
            bar = self._create_ascii_bar(percentage, 20)
            lines.append(f"  {category:15} {count:2d} ({percentage:5.1f}%) {bar}")
        
        lines.append("")
        lines.append("Question Distribution by Difficulty:")
        for difficulty, count in sorted(stats.difficulty_distribution.items()):
            percentage = (count / stats.total_questions) * 100
            bar = self._create_ascii_bar(percentage, 20)
            lines.append(f"  {difficulty:15} {count:2d} ({percentage:5.1f}%) {bar}")
        
        lines.append("")
        return lines
    
    def _generate_quality_analysis(self, result: QuestionGenerationResult) -> List[str]:
        """Generate quality analysis section."""
        lines = ["QUALITY ANALYSIS", "-" * 16, ""]
        
        if not result.questions:
            lines.append("No questions to analyze.")
            lines.append("")
            return lines
        
        # Quality metrics
        quality_scores = []
        validation_issues = []
        
        for question in result.questions:
            if 'quality_score' in question.metadata:
                quality_scores.append(question.metadata['quality_score'])
            if 'validation_issues' in question.metadata:
                validation_issues.append(question.metadata['validation_issues'])
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            min_quality = min(quality_scores)
            max_quality = max(quality_scores)
            
            lines.append(f"Average Quality Score: {avg_quality:.2f}/1.0")
            lines.append(f"Quality Range: {min_quality:.2f} - {max_quality:.2f}")
            
            # Quality distribution
            high_quality = sum(1 for score in quality_scores if score >= 0.8)
            medium_quality = sum(1 for score in quality_scores if 0.6 <= score < 0.8)
            low_quality = sum(1 for score in quality_scores if score < 0.6)
            
            lines.append(f"High Quality (≥0.8): {high_quality} questions")
            lines.append(f"Medium Quality (0.6-0.8): {medium_quality} questions")
            lines.append(f"Low Quality (<0.6): {low_quality} questions")
        
        # Content analysis
        has_hints = sum(1 for q in result.questions if q.hints)
        has_code = sum(1 for q in result.questions if q.code_snippet)
        
        lines.append(f"Questions with hints: {has_hints}/{len(result.questions)}")
        lines.append(f"Questions with code: {has_code}/{len(result.questions)}")
        
        lines.append("")
        return lines
    
    def _generate_performance_metrics(self, result: QuestionGenerationResult) -> List[str]:
        """Generate performance metrics section."""
        lines = ["PERFORMANCE METRICS", "-" * 19, ""]
        
        lines.append(f"Total Processing Time: {result.processing_time:.2f} seconds")
        lines.append(f"API Calls Made: {result.api_calls_made}")
        lines.append(f"Tokens Consumed: {result.tokens_used:,}")
        
        if hasattr(result, 'cost_estimate'):
            lines.append(f"Estimated Cost: ${result.cost_estimate:.4f}")
        
        # Efficiency calculations
        if result.processing_time > 0:
            rate = len(result.questions) / result.processing_time
            lines.append(f"Generation Rate: {rate:.2f} questions/second")
        
        if result.api_calls_made > 0:
            efficiency = len(result.questions) / result.api_calls_made
            lines.append(f"Questions per API Call: {efficiency:.2f}")
        
        lines.append("")
        return lines
    
    def _generate_recommendations(self, result: QuestionGenerationResult,
                                context: Optional[CodeContext]) -> List[str]:
        """Generate recommendations section."""
        lines = ["RECOMMENDATIONS", "-" * 15, ""]
        
        recommendations = []
        
        # Quality-based recommendations
        if result.questions:
            stats = self.calculate_report_stats(result)
            avg_quality = stats.quality_metrics.get('average', 0)
            
            if avg_quality < 0.7:
                recommendations.append("• Consider refining prompts to improve question quality")
            
            if stats.total_time_estimate > 120:  # More than 2 hours
                recommendations.append("• Consider breaking questions into multiple interview sessions")
            
            # Category balance
            if len(stats.category_distribution) < 3:
                recommendations.append("• Add more question categories for comprehensive assessment")
            
            # Difficulty balance
            difficulty_counts = list(stats.difficulty_distribution.values())
            if max(difficulty_counts) > len(result.questions) * 0.7:
                recommendations.append("• Balance difficulty levels for better candidate assessment")
        
        # Performance recommendations
        if result.processing_time > 30:  # More than 30 seconds
            recommendations.append("• Consider optimizing generation process for better performance")
        
        if result.api_calls_made > len(result.questions) * 2:
            recommendations.append("• Optimize API usage to reduce costs and improve efficiency")
        
        # Context-based recommendations
        if context:
            if context.overall_quality_score < 0.6:
                recommendations.append("• Focus on code quality questions due to low code quality score")
            
            if len(context.function_contexts) > 10:
                recommendations.append("• Consider focusing on specific functions for targeted assessment")
        
        # Default recommendations if none generated
        if not recommendations:
            recommendations = [
                "• Questions appear well-balanced and comprehensive",
                "• Consider customizing based on specific interview requirements",
                "• Review generated questions for relevance to your specific context"
            ]
        
        lines.extend(recommendations)
        lines.append("")
        return lines
    
    def _generate_footer(self) -> List[str]:
        """Generate report footer."""
        return [
            "=" * 70,
            "End of Report",
            f"Generated by Interview Question Generator v1.0",
            f"Report completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70
        ]
    
    def _create_ascii_bar(self, percentage: float, width: int = 20) -> str:
        """Create ASCII progress bar."""
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _analyze_business_context(self, business_context) -> List[str]:
        """Analyze business context."""
        lines = ["BUSINESS CONTEXT ANALYSIS", "-" * 25, ""]
        
        lines.append(f"Domain Type: {business_context.domain_type.value}")
        lines.append(f"Business Purpose: {business_context.business_purpose}")
        lines.append(f"Confidence Score: {business_context.confidence_score:.2f}/1.0")
        
        if business_context.workflow_patterns:
            lines.append("Workflow Patterns:")
            for pattern in business_context.workflow_patterns:
                pattern_name = pattern.value if hasattr(pattern, 'value') else str(pattern)
                lines.append(f"  • {pattern_name}")
        
        if business_context.data_entities:
            lines.append(f"Data Entities: {', '.join(business_context.data_entities)}")
        
        lines.append("")
        return lines
    
    def _analyze_technical_aspects(self, context: CodeContext) -> List[str]:
        """Analyze technical aspects."""
        lines = ["TECHNICAL ANALYSIS", "-" * 18, ""]
        
        lines.append(f"Functions Analyzed: {len(context.function_contexts)}")
        lines.append(f"Classes Analyzed: {len(context.class_contexts)}")
        
        # Complexity analysis
        if context.function_contexts:
            complexity_levels = [f.complexity_level for f in context.function_contexts]
            high_complexity = sum(1 for level in complexity_levels if level in ['high', 'very_high'])
            lines.append(f"High Complexity Functions: {high_complexity}/{len(context.function_contexts)}")
        
        lines.append("")
        return lines
    
    def _analyze_quality_metrics(self, context: CodeContext) -> List[str]:
        """Analyze quality metrics."""
        lines = ["QUALITY METRICS", "-" * 15, ""]
        
        lines.append(f"Overall Quality Score: {context.overall_quality_score:.2f}/1.0")
        
        if hasattr(context, 'maintainability_score'):
            lines.append(f"Maintainability Score: {context.maintainability_score:.2f}/1.0")
        
        if hasattr(context, 'testability_score'):
            lines.append(f"Testability Score: {context.testability_score:.2f}/1.0")
        
        lines.append("")
        return lines
    
    def _analyze_complexity(self, context: CodeContext) -> List[str]:
        """Analyze code complexity."""
        lines = ["COMPLEXITY ANALYSIS", "-" * 19, ""]
        
        if context.function_contexts:
            complexity_distribution = {}
            for func in context.function_contexts:
                level = func.complexity_level
                complexity_distribution[level] = complexity_distribution.get(level, 0) + 1
            
            lines.append("Function Complexity Distribution:")
            for level, count in sorted(complexity_distribution.items()):
                lines.append(f"  {level}: {count} functions")
        
        lines.append("")
        return lines
    
    def _analyze_documentation(self, doc_context) -> List[str]:
        """Analyze documentation quality."""
        lines = ["DOCUMENTATION ANALYSIS", "-" * 22, ""]
        
        lines.append(f"Docstring Coverage: {doc_context.docstring_coverage:.1%}")
        lines.append(f"Documentation Quality: {doc_context.docstring_quality}")
        lines.append(f"Type Hint Coverage: {doc_context.type_hint_coverage:.1%}")
        
        if doc_context.todo_items:
            lines.append(f"TODO Items Found: {len(doc_context.todo_items)}")
        
        if doc_context.fixme_items:
            lines.append(f"FIXME Items Found: {len(doc_context.fixme_items)}")
        
        lines.append("")
        return lines
    
    def _generate_performance_recommendations(self, result: QuestionGenerationResult) -> List[str]:
        """Generate performance-specific recommendations."""
        lines = ["PERFORMANCE RECOMMENDATIONS", "-" * 27, ""]
        
        recommendations = []
        
        # Processing time recommendations
        if result.processing_time > 60:
            recommendations.append("• Consider reducing the number of questions for faster processing")
        elif result.processing_time < 5:
            recommendations.append("• Processing time is excellent - consider generating more questions")
        
        # API efficiency recommendations
        if result.api_calls_made > 0:
            efficiency = len(result.questions) / result.api_calls_made
            if efficiency < 0.5:
                recommendations.append("• Low API efficiency - consider batch processing or prompt optimization")
            elif efficiency > 1.5:
                recommendations.append("• Excellent API efficiency - current approach is well-optimized")
        
        # Token usage recommendations
        if result.tokens_used > 10000:
            recommendations.append("• High token usage - consider shorter prompts or fewer questions")
        
        if not recommendations:
            recommendations.append("• Performance metrics are within acceptable ranges")
        
        lines.extend(recommendations)
        lines.append("")
        return lines