"""Main question generation orchestrator."""

import logging
import asyncio
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field

from ..models.context_models import CodeContext
from ..models.question_models import (
    Question, QuestionCategory, DifficultyLevel, 
    QuestionGenerationRequest, QuestionGenerationResult
)
from ..models.config_models import Config
from ..llm.llm_integration import LLMIntegration
from .question_categorizer import QuestionCategorizer, CategorizationResult
from .question_validator import QuestionValidator, ValidationResult


logger = logging.getLogger(__name__)


@dataclass
class GenerationPlan:
    """Plan for generating questions based on categorization analysis."""
    categories_to_generate: List[Tuple[QuestionCategory, int]]  # (category, count)
    difficulties_to_generate: List[Tuple[DifficultyLevel, float]]  # (difficulty, percentage)
    total_questions: int
    reasoning: str


@dataclass
class GenerationStats:
    """Statistics from question generation process."""
    total_requested: int = 0
    total_generated: int = 0
    total_validated: int = 0
    total_accepted: int = 0
    generation_time: float = 0.0
    validation_time: float = 0.0
    api_calls_made: int = 0
    tokens_used: int = 0
    average_quality_score: float = 0.0
    category_breakdown: Dict[str, int] = field(default_factory=dict)
    difficulty_breakdown: Dict[str, int] = field(default_factory=dict)


class QuestionGenerator:
    """Main orchestrator for generating interview questions from code analysis."""
    
    def __init__(self, config: Config):
        """
        Initialize the question generator.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.categorizer = QuestionCategorizer(config)
        self.validator = QuestionValidator()
        self.llm_integration = None  # Will be initialized when needed
        
        # Generation settings
        self.max_retries = 3
        self.quality_threshold = 0.6
        self.max_generation_attempts = 10
        
        logger.info("QuestionGenerator initialized")
    
    async def generate_questions(self, context: CodeContext, source_code: str,
                               max_questions: int = 10,
                               categories: Optional[List[QuestionCategory]] = None,
                               difficulties: Optional[List[DifficultyLevel]] = None,
                               custom_instructions: Optional[str] = None,
                               progress_callback=None) -> QuestionGenerationResult:
        """
        Generate interview questions based on code context.
        
        Args:
            context: Extracted code context
            source_code: Original source code
            max_questions: Maximum number of questions to generate
            categories: Specific categories to focus on (optional)
            difficulties: Specific difficulty levels to focus on (optional)
            custom_instructions: Additional instructions for question generation
            
        Returns:
            QuestionGenerationResult with generated and validated questions
        """
        start_time = time.time()
        stats = GenerationStats()
        
        try:
            logger.info(f"Starting question generation for {max_questions} questions")
            
            # Initialize LLM integration
            if not self.llm_integration:
                self.llm_integration = LLMIntegration(self.config)
            
            # Step 1: Analyze and categorize
            if progress_callback:
                progress_callback("Analyzing code for question categories...", 0.61)
            
            categorization = self.categorizer.analyze_and_recommend(context, max_questions)
            logger.info(f"Categorization complete: {len(categorization.recommended_categories)} categories")
            
            # Step 2: Create generation plan
            if progress_callback:
                progress_callback("Creating question generation plan...", 0.62)
            
            generation_plan = self._create_generation_plan(
                categorization, max_questions, categories, difficulties
            )
            logger.info(f"Generation plan: {generation_plan.total_questions} questions across "
                       f"{len(generation_plan.categories_to_generate)} categories")
            
            # Step 3: Generate questions
            if progress_callback:
                progress_callback("Beginning question generation...", 0.63)
            
            generated_questions, generation_stats = await self._generate_questions_from_plan(
                context, source_code, generation_plan, custom_instructions, progress_callback
            )
            
            # Step 4: Validate questions
            if progress_callback:
                progress_callback("Validating generated questions...", 0.91)
            
            validation_start = time.time()
            validated_questions = self._validate_and_filter_questions(
                generated_questions, context
            )
            validation_time = time.time() - validation_start
            
            # Step 5: Compile results
            total_time = time.time() - start_time
            
            # Update stats
            stats.total_requested = generation_plan.total_questions
            stats.total_generated = len(generated_questions)
            stats.total_validated = len(validated_questions)
            stats.total_accepted = len(validated_questions)
            stats.generation_time = generation_stats.get('generation_time', 0.0)
            stats.validation_time = validation_time
            stats.api_calls_made = generation_stats.get('api_calls', 0)
            stats.tokens_used = generation_stats.get('tokens_used', 0)
            
            # Calculate quality metrics
            if validated_questions:
                quality_scores = [q.metadata.get('quality_score', 0.0) for q in validated_questions]
                stats.average_quality_score = sum(quality_scores) / len(quality_scores)
                
                # Category and difficulty breakdown
                for question in validated_questions:
                    cat_key = question.category.value
                    diff_key = question.difficulty.value
                    stats.category_breakdown[cat_key] = stats.category_breakdown.get(cat_key, 0) + 1
                    stats.difficulty_breakdown[diff_key] = stats.difficulty_breakdown.get(diff_key, 0) + 1
            
            # Create result
            result = QuestionGenerationResult(
                success=len(validated_questions) > 0,
                questions=validated_questions,
                errors=[],
                warnings=[],
                processing_time=total_time,
                api_calls_made=stats.api_calls_made,
                tokens_used=stats.tokens_used
            )
            
            # Add warnings if generation was incomplete
            if len(validated_questions) < max_questions:
                result.warnings.append(
                    f"Generated {len(validated_questions)} questions instead of requested {max_questions}"
                )
            
            if stats.average_quality_score < self.quality_threshold:
                result.warnings.append(
                    f"Average quality score ({stats.average_quality_score:.2f}) below threshold"
                )
            
            logger.info(f"Question generation complete: {len(validated_questions)} questions "
                       f"in {total_time:.2f}s (avg quality: {stats.average_quality_score:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in question generation: {e}")
            return QuestionGenerationResult(
                success=False,
                questions=[],
                errors=[f"Question generation failed: {str(e)}"],
                processing_time=time.time() - start_time
            )
    
    def _create_generation_plan(self, categorization: CategorizationResult,
                              max_questions: int,
                              preferred_categories: Optional[List[QuestionCategory]] = None,
                              preferred_difficulties: Optional[List[DifficultyLevel]] = None) -> GenerationPlan:
        """Create a plan for question generation based on categorization results."""
        
        # Determine categories to generate
        if preferred_categories:
            # Use user-specified categories
            categories_to_generate = [(cat, 2) for cat in preferred_categories]
        else:
            # Use categorization recommendations
            categories_to_generate = []
            for rec in categorization.recommended_categories:
                if rec.confidence > 0.3:  # Only include confident recommendations
                    count = min(rec.suggested_count, max_questions // len(categorization.recommended_categories) + 1)
                    categories_to_generate.append((rec.category, count))
        
        # Ensure we don't exceed max_questions
        total_planned = sum(count for _, count in categories_to_generate)
        if total_planned > max_questions:
            # Scale down proportionally
            scale_factor = max_questions / total_planned
            categories_to_generate = [
                (cat, max(1, int(count * scale_factor))) 
                for cat, count in categories_to_generate
            ]
        
        # Determine difficulty distribution
        if preferred_difficulties:
            # Use user-specified difficulties
            difficulties_to_generate = [(diff, 1.0 / len(preferred_difficulties)) 
                                      for diff in preferred_difficulties]
        else:
            # Use categorization recommendations
            difficulties_to_generate = [
                (rec.difficulty, rec.suggested_percentage)
                for rec in categorization.recommended_difficulties
                if rec.confidence > 0.3
            ]
        
        # Ensure percentages sum to 1.0
        total_percentage = sum(pct for _, pct in difficulties_to_generate)
        if total_percentage > 0:
            difficulties_to_generate = [
                (diff, pct / total_percentage) 
                for diff, pct in difficulties_to_generate
            ]
        else:
            # Default distribution
            difficulties_to_generate = [
                (DifficultyLevel.INTERMEDIATE, 0.6),
                (DifficultyLevel.BEGINNER, 0.4)
            ]
        
        final_total = sum(count for _, count in categories_to_generate)
        
        return GenerationPlan(
            categories_to_generate=categories_to_generate,
            difficulties_to_generate=difficulties_to_generate,
            total_questions=final_total,
            reasoning=categorization.reasoning_summary
        )
    
    async def _generate_questions_from_plan(self, context: CodeContext, source_code: str,
                                          plan: GenerationPlan, 
                                          custom_instructions: Optional[str] = None,
                                          progress_callback=None) -> Tuple[List[Question], Dict[str, Any]]:
        """Generate questions according to the generation plan."""
        all_questions = []
        total_api_calls = 0
        total_tokens = 0
        generation_start = time.time()
        generated_count = 0  # Track progress
        
        # Initial progress update
        if progress_callback:
            progress_callback("Starting question generation...", 0.6)
        
        # Create difficulty distribution for each category
        difficulty_distribution = {diff: pct for diff, pct in plan.difficulties_to_generate}
        
        for category, target_count in plan.categories_to_generate:
            logger.info(f"Generating {target_count} questions for category: {category.value}")
            
            # Update progress at start of each category
            if progress_callback:
                base_progress = 0.6
                progress_range = 0.3
                completion_ratio = generated_count / plan.total_questions if plan.total_questions > 0 else 0.0
                current_overall_progress = base_progress + (progress_range * completion_ratio)
                progress_callback(f"Starting {category.value} questions...", current_overall_progress)
            
            # Distribute questions across difficulty levels for this category
            category_questions = []
            remaining_count = target_count
            
            for difficulty, percentage in plan.difficulties_to_generate:
                if remaining_count <= 0:
                    break
                
                # Calculate how many questions of this difficulty to generate
                difficulty_count = max(1, int(target_count * percentage))
                difficulty_count = min(difficulty_count, remaining_count)
                
                if difficulty_count > 0:
                    # Update progress before starting generation
                    if progress_callback:
                        base_progress = 0.6
                        progress_range = 0.3
                        completion_ratio = generated_count / plan.total_questions if plan.total_questions > 0 else 0.0
                        current_overall_progress = base_progress + (progress_range * completion_ratio)
                        progress_callback(f"Generating {category.value} questions...", current_overall_progress)
                    
                    # Generate questions for this category/difficulty combination
                    questions, api_calls, tokens = await self._generate_category_difficulty_questions(
                        context, source_code, category, difficulty, difficulty_count, custom_instructions, progress_callback
                    )
                    
                    category_questions.extend(questions)
                    total_api_calls += api_calls
                    total_tokens += tokens
                    remaining_count -= len(questions)
                    
                    # Update progress after each batch
                    generated_count += len(questions)
                    if progress_callback:
                        # Generation happens between 60% and 90%
                        base_progress = 0.6
                        progress_range = 0.3
                        
                        completion_ratio = generated_count / plan.total_questions if plan.total_questions > 0 else 1.0
                        current_overall_progress = base_progress + (progress_range * completion_ratio)
                        
                        progress_callback(f"Generated {generated_count}/{plan.total_questions} questions...", current_overall_progress)
                        # Small delay to ensure progress display updates
                        await asyncio.sleep(0.1)
            
            all_questions.extend(category_questions)
            logger.info(f"Generated {len(category_questions)} questions for {category.value}")
        
        generation_time = time.time() - generation_start
        
        stats = {
            'generation_time': generation_time,
            'api_calls': total_api_calls,
            'tokens_used': total_tokens
        }
        
        return all_questions, stats
    
    async def _generate_category_difficulty_questions(self, context: CodeContext, source_code: str,
                                                    category: QuestionCategory, difficulty: DifficultyLevel,
                                                    count: int, custom_instructions: Optional[str] = None,
                                                    progress_callback=None) -> Tuple[List[Question], int, int]:
        """Generate questions for a specific category and difficulty level."""
        questions = []
        api_calls = 0
        tokens_used = 0
        
        for attempt in range(min(count * 2, self.max_generation_attempts)):  # Allow some retries
            if len(questions) >= count:
                break
            
            try:
                # Create generation request
                request = QuestionGenerationRequest(
                    categories=[category],
                    difficulty_levels=[difficulty],
                    max_questions_per_category=1,
                    include_hints=True,
                    include_context_references=True,
                    custom_instructions=custom_instructions
                )
                
                # Generate question using LLM
                result = await self.llm_integration.generate_questions(context, source_code, request)
                
                if result.success and result.questions:
                    questions.extend(result.questions)
                    api_calls += result.api_calls_made
                    tokens_used += result.tokens_used
                else:
                    logger.warning(f"Failed to generate {category.value} {difficulty.value} question: {result.errors}")
                
            except Exception as e:
                logger.error(f"Error generating {category.value} {difficulty.value} question: {e}")
                continue
        
        # Return only the requested count
        return questions[:count], api_calls, tokens_used
    
    def _validate_and_filter_questions(self, questions: List[Question], 
                                     context: CodeContext) -> List[Question]:
        """Validate questions and filter out low-quality ones."""
        if not questions:
            return []
        
        logger.info(f"Validating {len(questions)} generated questions")
        
        # Validate individual questions
        validation_results = self.validator.validate_question_set(questions, context)
        
        # Filter questions based on validation results
        validated_questions = []
        for question in questions:
            result = validation_results.get(question.id)
            if result and result.is_valid and result.quality_score >= self.quality_threshold:
                # Add quality score to metadata
                question.metadata['quality_score'] = result.quality_score
                question.metadata['validation_issues'] = len(result.issues)
                validated_questions.append(question)
            else:
                logger.debug(f"Rejected question {question.id}: "
                           f"valid={result.is_valid if result else False}, "
                           f"quality={result.quality_score if result else 0.0}")
        
        logger.info(f"Validated {len(validated_questions)} out of {len(questions)} questions")
        
        # Sort by quality score (highest first)
        validated_questions.sort(key=lambda q: q.metadata.get('quality_score', 0.0), reverse=True)
        
        return validated_questions
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about the question generation process."""
        stats = {
            'config': {
                'max_questions_per_category': self.config.max_questions_per_category,
                'quality_threshold': self.quality_threshold,
                'max_retries': self.max_retries
            }
        }
        
        if self.llm_integration:
            stats['llm_stats'] = self.llm_integration.get_usage_stats()
        
        return stats
    
    async def close(self):
        """Clean up resources."""
        if self.llm_integration:
            await self.llm_integration.close()
    
    # Convenience methods for specific use cases
    
    async def generate_comprehension_questions(self, context: CodeContext, source_code: str,
                                             count: int = 3) -> QuestionGenerationResult:
        """Generate only comprehension questions."""
        return await self.generate_questions(
            context, source_code, 
            max_questions=count,
            categories=[QuestionCategory.COMPREHENSION]
        )
    
    async def generate_debugging_questions(self, context: CodeContext, source_code: str,
                                         count: int = 2) -> QuestionGenerationResult:
        """Generate only debugging questions."""
        return await self.generate_questions(
            context, source_code,
            max_questions=count,
            categories=[QuestionCategory.DEBUGGING]
        )
    
    async def generate_optimization_questions(self, context: CodeContext, source_code: str,
                                            count: int = 2) -> QuestionGenerationResult:
        """Generate only optimization questions."""
        return await self.generate_questions(
            context, source_code,
            max_questions=count,
            categories=[QuestionCategory.OPTIMIZATION]
        )
    
    async def generate_design_questions(self, context: CodeContext, source_code: str,
                                       count: int = 2) -> QuestionGenerationResult:
        """Generate only design questions."""
        return await self.generate_questions(
            context, source_code,
            max_questions=count,
            categories=[QuestionCategory.DESIGN]
        )
    
    async def generate_balanced_question_set(self, context: CodeContext, source_code: str,
                                           total_questions: int = 10) -> QuestionGenerationResult:
        """Generate a balanced set of questions across all relevant categories."""
        # Let the categorizer determine the best distribution
        return await self.generate_questions(context, source_code, max_questions=total_questions)