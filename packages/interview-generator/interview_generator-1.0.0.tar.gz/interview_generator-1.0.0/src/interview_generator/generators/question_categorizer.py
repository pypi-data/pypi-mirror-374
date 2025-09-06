"""Question categorization logic based on code analysis."""

import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field

from ..models.context_models import (
    CodeContext, DomainType, WorkflowPattern, ErrorHandlingStrategy, 
    PerformancePattern, FunctionContext, ClassContext
)
from ..models.question_models import QuestionCategory, DifficultyLevel
from ..models.config_models import Config


logger = logging.getLogger(__name__)


@dataclass
class CategoryRecommendation:
    """Recommendation for question categories based on code analysis."""
    category: QuestionCategory
    confidence: float  # 0.0 to 1.0
    reasoning: str
    suggested_count: int = 1
    priority: int = 1  # 1 = high, 2 = medium, 3 = low


@dataclass
class DifficultyRecommendation:
    """Recommendation for difficulty levels based on code complexity."""
    difficulty: DifficultyLevel
    confidence: float
    reasoning: str
    suggested_percentage: float = 0.25  # What percentage of questions should be this difficulty


@dataclass
class CategorizationResult:
    """Result of question categorization analysis."""
    recommended_categories: List[CategoryRecommendation] = field(default_factory=list)
    recommended_difficulties: List[DifficultyRecommendation] = field(default_factory=list)
    total_recommended_questions: int = 0
    analysis_confidence: float = 0.0
    reasoning_summary: str = ""


class QuestionCategorizer:
    """Analyzes code context to recommend appropriate question categories and difficulties."""
    
    def __init__(self, config: Config):
        """
        Initialize the categorizer.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Category weights based on code characteristics
        self.category_weights = {
            QuestionCategory.COMPREHENSION: 1.0,  # Always relevant
            QuestionCategory.DEBUGGING: 0.0,
            QuestionCategory.OPTIMIZATION: 0.0,
            QuestionCategory.DESIGN: 0.0,
            QuestionCategory.EDGE_CASES: 0.0
        }
        
        # Difficulty thresholds
        self.complexity_thresholds = {
            'low': (0.0, 0.3),
            'medium': (0.3, 0.7),
            'high': (0.7, 0.9),
            'very_high': (0.9, 1.0)
        }
    
    def analyze_and_recommend(self, context: CodeContext, 
                            max_questions: int = 10) -> CategorizationResult:
        """
        Analyze code context and recommend question categories and difficulties.
        
        Args:
            context: Extracted code context
            max_questions: Maximum number of questions to recommend
            
        Returns:
            CategorizationResult with recommendations
        """
        logger.info("Analyzing code context for question categorization")
        
        try:
            # Analyze categories
            category_recommendations = self._analyze_categories(context)
            
            # Analyze difficulties
            difficulty_recommendations = self._analyze_difficulties(context)
            
            # Calculate total questions and distribution
            total_questions = min(max_questions, len(category_recommendations) * 2)
            
            # Create result
            result = CategorizationResult(
                recommended_categories=category_recommendations,
                recommended_difficulties=difficulty_recommendations,
                total_recommended_questions=total_questions,
                analysis_confidence=self._calculate_overall_confidence(context),
                reasoning_summary=self._generate_reasoning_summary(
                    category_recommendations, difficulty_recommendations
                )
            )
            
            logger.info(f"Recommended {len(category_recommendations)} categories "
                       f"and {len(difficulty_recommendations)} difficulty levels")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in categorization analysis: {e}")
            # Return default recommendations
            return self._get_default_recommendations(max_questions)
    
    def _analyze_categories(self, context: CodeContext) -> List[CategoryRecommendation]:
        """Analyze code context to recommend question categories."""
        recommendations = []
        
        # Always include comprehension questions
        recommendations.append(CategoryRecommendation(
            category=QuestionCategory.COMPREHENSION,
            confidence=1.0,
            reasoning="Comprehension questions are always valuable for understanding code structure and purpose",
            suggested_count=2,
            priority=1
        ))
        
        # Analyze for debugging questions
        debug_score = self._calculate_debugging_relevance(context)
        if debug_score > 0.3:
            recommendations.append(CategoryRecommendation(
                category=QuestionCategory.DEBUGGING,
                confidence=debug_score,
                reasoning=self._get_debugging_reasoning(context),
                suggested_count=1 if debug_score < 0.7 else 2,
                priority=1 if debug_score > 0.7 else 2
            ))
        
        # Analyze for optimization questions
        optimization_score = self._calculate_optimization_relevance(context)
        if optimization_score > 0.3:
            recommendations.append(CategoryRecommendation(
                category=QuestionCategory.OPTIMIZATION,
                confidence=optimization_score,
                reasoning=self._get_optimization_reasoning(context),
                suggested_count=1 if optimization_score < 0.7 else 2,
                priority=1 if optimization_score > 0.7 else 2
            ))
        
        # Analyze for design questions
        design_score = self._calculate_design_relevance(context)
        if design_score > 0.3:
            recommendations.append(CategoryRecommendation(
                category=QuestionCategory.DESIGN,
                confidence=design_score,
                reasoning=self._get_design_reasoning(context),
                suggested_count=1 if design_score < 0.7 else 2,
                priority=1 if design_score > 0.7 else 2
            ))
        
        # Analyze for edge cases questions
        edge_cases_score = self._calculate_edge_cases_relevance(context)
        if edge_cases_score > 0.3:
            recommendations.append(CategoryRecommendation(
                category=QuestionCategory.EDGE_CASES,
                confidence=edge_cases_score,
                reasoning=self._get_edge_cases_reasoning(context),
                suggested_count=1,
                priority=2 if edge_cases_score > 0.6 else 3
            ))
        
        # Sort by priority and confidence
        recommendations.sort(key=lambda x: (x.priority, -x.confidence))
        
        return recommendations
    
    def _analyze_difficulties(self, context: CodeContext) -> List[DifficultyRecommendation]:
        """Analyze code complexity to recommend difficulty levels."""
        recommendations = []
        
        # Calculate overall complexity score
        complexity_score = self._calculate_complexity_score(context)
        
        # Determine difficulty distribution based on complexity
        if complexity_score < 0.3:
            # Simple code - focus on beginner/intermediate
            recommendations.extend([
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.BEGINNER,
                    confidence=0.8,
                    reasoning="Code has low complexity, suitable for beginner-level questions",
                    suggested_percentage=0.5
                ),
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    confidence=0.7,
                    reasoning="Some intermediate concepts present",
                    suggested_percentage=0.4
                ),
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.ADVANCED,
                    confidence=0.3,
                    reasoning="Limited advanced concepts",
                    suggested_percentage=0.1
                )
            ])
        elif complexity_score < 0.7:
            # Medium complexity - balanced distribution
            recommendations.extend([
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.BEGINNER,
                    confidence=0.6,
                    reasoning="Basic concepts still relevant",
                    suggested_percentage=0.3
                ),
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    confidence=0.9,
                    reasoning="Code complexity well-suited for intermediate questions",
                    suggested_percentage=0.5
                ),
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.ADVANCED,
                    confidence=0.7,
                    reasoning="Advanced patterns and complexity present",
                    suggested_percentage=0.2
                )
            ])
        else:
            # High complexity - focus on intermediate/advanced
            recommendations.extend([
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    confidence=0.7,
                    reasoning="Complex code requires solid intermediate understanding",
                    suggested_percentage=0.4
                ),
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.ADVANCED,
                    confidence=0.9,
                    reasoning="High complexity code ideal for advanced questions",
                    suggested_percentage=0.4
                ),
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.EXPERT,
                    confidence=0.6,
                    reasoning="Very complex patterns suitable for expert-level analysis",
                    suggested_percentage=0.2
                )
            ])
        
        return recommendations
    
    def _calculate_debugging_relevance(self, context: CodeContext) -> float:
        """Calculate relevance score for debugging questions."""
        score = 0.0
        
        # Check error handling patterns
        error_context = context.error_handling_context
        if error_context.exception_patterns:
            score += 0.3
        if error_context.recovery_strategies:
            score += 0.2
        if error_context.validation_approaches:
            score += 0.2
        
        # Check for complex functions that might have bugs
        complex_functions = [f for f in context.function_contexts 
                           if f.complexity_level in ['high', 'very_high']]
        if complex_functions:
            score += min(0.3, len(complex_functions) * 0.1)
        
        return min(1.0, score)
    
    def _calculate_optimization_relevance(self, context: CodeContext) -> float:
        """Calculate relevance score for optimization questions."""
        score = 0.0
        
        # Check performance context
        perf_context = context.performance_context
        if perf_context.performance_hotspots:
            score += 0.4
        if perf_context.optimization_patterns:
            score += 0.3
        if perf_context.memory_patterns:
            score += 0.2
        if perf_context.io_operations:
            score += 0.2
        
        # Check for loops and recursive functions
        for func in context.function_contexts:
            if 'loop' in func.performance_characteristics:
                score += 0.1
            if 'recursive' in func.performance_characteristics:
                score += 0.2
        
        return min(1.0, score)
    
    def _calculate_design_relevance(self, context: CodeContext) -> float:
        """Calculate relevance score for design questions."""
        score = 0.0
        
        # Check for classes and design patterns
        if context.class_contexts:
            score += 0.3
            
            # Check for design patterns
            for class_ctx in context.class_contexts:
                if class_ctx.design_patterns:
                    score += 0.2
                if class_ctx.inheritance_hierarchy:
                    score += 0.1
        
        # Check architectural patterns
        if hasattr(context, 'integration_context') and context.integration_context:
            if context.integration_context.api_integrations:
                score += 0.2
            if context.integration_context.database_integrations:
                score += 0.2
        
        # Check business context complexity
        if len(context.business_context.workflow_patterns) > 1:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_edge_cases_relevance(self, context: CodeContext) -> float:
        """Calculate relevance score for edge cases questions."""
        score = 0.0
        
        # Check for input validation
        if hasattr(context, 'security_context') and context.security_context:
            if context.security_context.input_validation:
                score += 0.3
        
        # Check for error conditions in functions
        for func in context.function_contexts:
            if func.error_conditions:
                score += 0.1
        
        # Check for business rules that might have edge cases
        if context.business_context.business_rules:
            score += 0.2
        
        # Check for complex conditional logic
        complex_functions = [f for f in context.function_contexts 
                           if f.complexity_level in ['high', 'very_high']]
        if complex_functions:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_complexity_score(self, context: CodeContext) -> float:
        """Calculate overall complexity score of the code."""
        scores = []
        
        # Function complexity
        if context.function_contexts:
            complexity_levels = {'low': 0.2, 'medium': 0.5, 'high': 0.8, 'very_high': 1.0}
            func_scores = [complexity_levels.get(f.complexity_level, 0.2) 
                          for f in context.function_contexts]
            scores.append(sum(func_scores) / len(func_scores))
        
        # Class complexity
        if context.class_contexts:
            scores.append(min(1.0, len(context.class_contexts) * 0.2))
        
        # Overall quality scores
        if hasattr(context, 'overall_quality_score'):
            # Invert quality score - lower quality = higher complexity for questions
            scores.append(1.0 - context.overall_quality_score)
        
        # Business context complexity
        workflow_complexity = min(1.0, len(context.business_context.workflow_patterns) * 0.2)
        scores.append(workflow_complexity)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_overall_confidence(self, context: CodeContext) -> float:
        """Calculate overall confidence in the analysis."""
        confidence_factors = []
        
        # Business context confidence
        if hasattr(context.business_context, 'confidence_score'):
            confidence_factors.append(context.business_context.confidence_score)
        
        # Documentation quality affects confidence
        doc_quality_map = {'excellent': 1.0, 'good': 0.8, 'fair': 0.6, 'poor': 0.4, 'none': 0.2}
        doc_confidence = doc_quality_map.get(context.documentation_context.docstring_quality, 0.5)
        confidence_factors.append(doc_confidence)
        
        # Amount of context data affects confidence
        context_richness = min(1.0, (len(context.function_contexts) + len(context.class_contexts)) * 0.1)
        confidence_factors.append(context_richness)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.7
    
    def _get_debugging_reasoning(self, context: CodeContext) -> str:
        """Generate reasoning for debugging question recommendation."""
        reasons = []
        
        if context.error_handling_context.exception_patterns:
            reasons.append("code contains exception handling patterns")
        if context.error_handling_context.validation_approaches:
            reasons.append("input validation logic present")
        
        complex_functions = [f for f in context.function_contexts 
                           if f.complexity_level in ['high', 'very_high']]
        if complex_functions:
            reasons.append(f"{len(complex_functions)} complex functions that may contain bugs")
        
        return "Code has " + ", ".join(reasons) if reasons else "potential debugging scenarios identified"
    
    def _get_optimization_reasoning(self, context: CodeContext) -> str:
        """Generate reasoning for optimization question recommendation."""
        reasons = []
        
        if context.performance_context.performance_hotspots:
            reasons.append("performance hotspots identified")
        if context.performance_context.io_operations:
            reasons.append("I/O operations present")
        if context.performance_context.memory_patterns:
            reasons.append("memory usage patterns detected")
        
        return "Code has " + ", ".join(reasons) if reasons else "optimization opportunities identified"
    
    def _get_design_reasoning(self, context: CodeContext) -> str:
        """Generate reasoning for design question recommendation."""
        reasons = []
        
        if context.class_contexts:
            reasons.append(f"{len(context.class_contexts)} classes with design patterns")
        if len(context.business_context.workflow_patterns) > 1:
            reasons.append("multiple workflow patterns")
        
        return "Code has " + ", ".join(reasons) if reasons else "design patterns and architecture worth discussing"
    
    def _get_edge_cases_reasoning(self, context: CodeContext) -> str:
        """Generate reasoning for edge cases question recommendation."""
        reasons = []
        
        if hasattr(context, 'security_context') and context.security_context:
            if context.security_context.input_validation:
                reasons.append("input validation logic")
        
        if context.business_context.business_rules:
            reasons.append("business rules with potential edge cases")
        
        return "Code has " + ", ".join(reasons) if reasons else "potential edge cases and boundary conditions"
    
    def _generate_reasoning_summary(self, categories: List[CategoryRecommendation],
                                  difficulties: List[DifficultyRecommendation]) -> str:
        """Generate a summary of the categorization reasoning."""
        summary_parts = []
        
        # Summarize categories
        high_confidence_cats = [c for c in categories if c.confidence > 0.7]
        if high_confidence_cats:
            cat_names = [c.category.value for c in high_confidence_cats]
            summary_parts.append(f"High confidence in {', '.join(cat_names)} questions")
        
        # Summarize difficulty
        primary_difficulty = max(difficulties, key=lambda x: x.confidence) if difficulties else None
        if primary_difficulty:
            summary_parts.append(f"Primary difficulty level: {primary_difficulty.difficulty.value}")
        
        return ". ".join(summary_parts) if summary_parts else "Standard question distribution recommended"
    
    def _get_default_recommendations(self, max_questions: int) -> CategorizationResult:
        """Get default recommendations when analysis fails."""
        return CategorizationResult(
            recommended_categories=[
                CategoryRecommendation(
                    category=QuestionCategory.COMPREHENSION,
                    confidence=0.8,
                    reasoning="Default comprehension questions",
                    suggested_count=2,
                    priority=1
                ),
                CategoryRecommendation(
                    category=QuestionCategory.DEBUGGING,
                    confidence=0.5,
                    reasoning="Default debugging scenarios",
                    suggested_count=1,
                    priority=2
                )
            ],
            recommended_difficulties=[
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    confidence=0.7,
                    reasoning="Default intermediate level",
                    suggested_percentage=0.6
                ),
                DifficultyRecommendation(
                    difficulty=DifficultyLevel.BEGINNER,
                    confidence=0.6,
                    reasoning="Default beginner level",
                    suggested_percentage=0.4
                )
            ],
            total_recommended_questions=min(max_questions, 5),
            analysis_confidence=0.5,
            reasoning_summary="Default recommendations due to analysis limitations"
        )