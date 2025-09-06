"""JSON output formatter for interview questions."""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from ...models.question_models import (
    Question, QuestionGenerationResult, QuestionCategory, DifficultyLevel
)
from ...models.context_models import CodeContext


logger = logging.getLogger(__name__)


class JSONFormatter:
    """Formats interview questions and results as JSON."""
    
    def __init__(self, pretty_print: bool = True, include_metadata: bool = True):
        """
        Initialize JSON formatter.
        
        Args:
            pretty_print: Whether to format JSON with indentation
            include_metadata: Whether to include generation metadata
        """
        self.pretty_print = pretty_print
        self.include_metadata = include_metadata
        self.indent = 2 if pretty_print else None
    
    def format_question(self, question: Question) -> Dict[str, Any]:
        """
        Format a single question as JSON-serializable dictionary.
        
        Args:
            question: Question to format
            
        Returns:
            Dictionary representation of the question
        """
        try:
            # Convert question to dictionary
            question_dict = {
                "id": question.id,
                "category": question.category.value,
                "difficulty": question.difficulty.value,
                "title": getattr(question, 'title', ''),
                "question_text": question.question_text,
                "code_snippet": question.code_snippet,
                "expected_answer": question.expected_answer,
                "sample_answer": getattr(question, 'sample_answer', ''),
                "hints": question.hints,
                "context_references": question.context_references,
                "created_at": question.created_at.isoformat() if question.created_at else None
            }
            
            # Add optional fields if they exist
            if hasattr(question, 'learning_objectives'):
                question_dict["learning_objectives"] = question.learning_objectives
            
            if hasattr(question, 'prerequisite_knowledge'):
                question_dict["prerequisite_knowledge"] = question.prerequisite_knowledge
            
            if hasattr(question, 'follow_up_questions'):
                question_dict["follow_up_questions"] = question.follow_up_questions
            
            if hasattr(question, 'time_estimate_minutes'):
                question_dict["time_estimate_minutes"] = question.time_estimate_minutes
            
            if hasattr(question, 'tags'):
                question_dict["tags"] = question.tags
            
            if hasattr(question, 'multiple_choice_options'):
                question_dict["multiple_choice_options"] = [
                    {
                        "id": opt.id,
                        "text": opt.text,
                        "is_correct": opt.is_correct,
                        "explanation": opt.explanation
                    } for opt in question.multiple_choice_options
                ] if question.multiple_choice_options else []
            
            # Include metadata if requested
            if self.include_metadata and question.metadata:
                question_dict["metadata"] = question.metadata
            
            return question_dict
            
        except Exception as e:
            logger.error(f"Error formatting question {question.id}: {e}")
            return {
                "id": question.id,
                "error": f"Failed to format question: {str(e)}"
            }
    
    def format_question_list(self, questions: List[Question]) -> List[Dict[str, Any]]:
        """
        Format a list of questions.
        
        Args:
            questions: List of questions to format
            
        Returns:
            List of formatted question dictionaries
        """
        return [self.format_question(q) for q in questions]
    
    def format_generation_result(self, result: QuestionGenerationResult,
                               include_stats: bool = True) -> Dict[str, Any]:
        """
        Format a complete question generation result.
        
        Args:
            result: Generation result to format
            include_stats: Whether to include generation statistics
            
        Returns:
            Formatted result dictionary
        """
        try:
            formatted_result = {
                "success": result.success,
                "questions": self.format_question_list(result.questions),
                "total_questions": len(result.questions),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            # Add error information if present
            if result.errors:
                formatted_result["errors"] = result.errors
            
            if result.warnings:
                formatted_result["warnings"] = result.warnings
            
            # Add statistics if requested
            if include_stats:
                stats = {
                    "processing_time_seconds": result.processing_time,
                    "api_calls_made": result.api_calls_made,
                    "tokens_used": result.tokens_used
                }
                
                # Add cost estimate if available
                if hasattr(result, 'cost_estimate'):
                    stats["estimated_cost_usd"] = result.cost_estimate
                
                formatted_result["statistics"] = stats
            
            # Add question distribution analysis
            if result.questions:
                formatted_result["analysis"] = self._analyze_question_distribution(result.questions)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error formatting generation result: {e}")
            return {
                "success": False,
                "error": f"Failed to format result: {str(e)}",
                "generation_timestamp": datetime.now().isoformat()
            }
    
    def format_with_context(self, result: QuestionGenerationResult,
                          context: Optional[CodeContext] = None,
                          source_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Format result with additional context information.
        
        Args:
            result: Generation result
            context: Code context used for generation
            source_code: Original source code
            
        Returns:
            Enhanced formatted result
        """
        formatted_result = self.format_generation_result(result)
        
        # Add context information
        if context:
            formatted_result["code_analysis"] = {
                "domain": context.business_context.domain_type.value,
                "business_purpose": context.business_context.business_purpose,
                "overall_quality_score": context.overall_quality_score,
                "maintainability_score": getattr(context, 'maintainability_score', 0.0),
                "testability_score": getattr(context, 'testability_score', 0.0),
                "function_count": len(context.function_contexts),
                "class_count": len(context.class_contexts),
                "documentation_quality": context.documentation_context.docstring_quality
            }
        
        # Add source code if provided and not too large
        if source_code and len(source_code) < 10000:  # Limit to 10KB
            formatted_result["source_code"] = source_code
        elif source_code:
            formatted_result["source_code_info"] = {
                "length_characters": len(source_code),
                "length_lines": source_code.count('\n') + 1,
                "note": "Source code omitted due to size (>10KB)"
            }
        
        return formatted_result
    
    def to_json_string(self, data: Dict[str, Any]) -> str:
        """
        Convert dictionary to JSON string.
        
        Args:
            data: Data to serialize
            
        Returns:
            JSON string
        """
        try:
            return json.dumps(
                data,
                indent=self.indent,
                ensure_ascii=False,
                separators=(',', ': ') if self.pretty_print else (',', ':')
            )
        except Exception as e:
            logger.error(f"Error serializing to JSON: {e}")
            return json.dumps({
                "error": f"JSON serialization failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    def _analyze_question_distribution(self, questions: List[Question]) -> Dict[str, Any]:
        """Analyze the distribution of questions by category and difficulty."""
        category_counts = {}
        difficulty_counts = {}
        
        for question in questions:
            # Count categories
            cat_key = question.category.value
            category_counts[cat_key] = category_counts.get(cat_key, 0) + 1
            
            # Count difficulties
            diff_key = question.difficulty.value
            difficulty_counts[diff_key] = difficulty_counts.get(diff_key, 0) + 1
        
        # Calculate percentages
        total = len(questions)
        category_percentages = {k: (v / total) * 100 for k, v in category_counts.items()}
        difficulty_percentages = {k: (v / total) * 100 for k, v in difficulty_counts.items()}
        
        return {
            "category_distribution": {
                "counts": category_counts,
                "percentages": category_percentages
            },
            "difficulty_distribution": {
                "counts": difficulty_counts,
                "percentages": difficulty_percentages
            },
            "average_time_estimate": self._calculate_average_time(questions),
            "has_hints": sum(1 for q in questions if q.hints),
            "has_code_snippets": sum(1 for q in questions if q.code_snippet)
        }
    
    def _calculate_average_time(self, questions: List[Question]) -> float:
        """Calculate average time estimate for questions."""
        time_estimates = []
        for question in questions:
            if hasattr(question, 'time_estimate_minutes') and question.time_estimate_minutes:
                time_estimates.append(question.time_estimate_minutes)
        
        return sum(time_estimates) / len(time_estimates) if time_estimates else 0.0
    
    def create_schema(self) -> Dict[str, Any]:
        """
        Create JSON schema for the output format.
        
        Returns:
            JSON schema dictionary
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Interview Questions Generation Result",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "category": {"type": "string", "enum": [cat.value for cat in QuestionCategory]},
                            "difficulty": {"type": "string", "enum": [diff.value for diff in DifficultyLevel]},
                            "title": {"type": "string"},
                            "question_text": {"type": "string"},
                            "code_snippet": {"type": "string"},
                            "expected_answer": {"type": "string"},
                            "sample_answer": {"type": "string"},
                            "hints": {"type": "array", "items": {"type": "string"}},
                            "context_references": {"type": "array", "items": {"type": "string"}},
                            "learning_objectives": {"type": "array", "items": {"type": "string"}},
                            "prerequisite_knowledge": {"type": "array", "items": {"type": "string"}},
                            "follow_up_questions": {"type": "array", "items": {"type": "string"}},
                            "time_estimate_minutes": {"type": "number"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                            "created_at": {"type": "string", "format": "date-time"},
                            "metadata": {"type": "object"}
                        },
                        "required": ["id", "category", "difficulty", "question_text"]
                    }
                },
                "total_questions": {"type": "integer"},
                "generation_timestamp": {"type": "string", "format": "date-time"},
                "errors": {"type": "array", "items": {"type": "string"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "statistics": {
                    "type": "object",
                    "properties": {
                        "processing_time_seconds": {"type": "number"},
                        "api_calls_made": {"type": "integer"},
                        "tokens_used": {"type": "integer"},
                        "estimated_cost_usd": {"type": "number"}
                    }
                },
                "analysis": {
                    "type": "object",
                    "properties": {
                        "category_distribution": {"type": "object"},
                        "difficulty_distribution": {"type": "object"},
                        "average_time_estimate": {"type": "number"},
                        "has_hints": {"type": "integer"},
                        "has_code_snippets": {"type": "integer"}
                    }
                }
            },
            "required": ["success", "questions", "total_questions", "generation_timestamp"]
        }