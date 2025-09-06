"""Data models for interview questions."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid
from datetime import datetime


class QuestionCategory(Enum):
    """Categories of interview questions."""
    COMPREHENSION = "comprehension"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    DESIGN = "design"
    EDGE_CASES = "edge_cases"


class DifficultyLevel(Enum):
    """Difficulty levels for questions."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Question:
    """Represents a single interview question."""
    id: str
    category: QuestionCategory
    difficulty: DifficultyLevel
    question_text: str
    code_snippet: str
    expected_answer: str
    hints: List[str] = field(default_factory=list)
    context_references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, category: QuestionCategory, difficulty: DifficultyLevel,
               question_text: str, code_snippet: str, expected_answer: str,
               hints: Optional[List[str]] = None, 
               context_references: Optional[List[str]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> 'Question':
        """Create a new question with auto-generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            category=category,
            difficulty=difficulty,
            question_text=question_text,
            code_snippet=code_snippet,
            expected_answer=expected_answer,
            hints=hints or [],
            context_references=context_references or [],
            metadata=metadata or {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary format."""
        return {
            "id": self.id,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "question_text": self.question_text,
            "code_snippet": self.code_snippet,
            "expected_answer": self.expected_answer,
            "hints": self.hints,
            "context_references": self.context_references,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """Create question from dictionary format."""
        return cls(
            id=data["id"],
            category=QuestionCategory(data["category"]),
            difficulty=DifficultyLevel(data["difficulty"]),
            question_text=data["question_text"],
            code_snippet=data["code_snippet"],
            expected_answer=data["expected_answer"],
            hints=data.get("hints", []),
            context_references=data.get("context_references", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        )


@dataclass
class QuestionGenerationRequest:
    """Request for generating questions."""
    categories: List[QuestionCategory]
    difficulty_levels: List[DifficultyLevel]
    max_questions_per_category: int = 3
    include_hints: bool = True
    include_context_references: bool = True
    custom_instructions: Optional[str] = None


@dataclass
class QuestionGenerationResult:
    """Result of question generation process."""
    success: bool
    questions: List[Question] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    api_calls_made: int = 0
    tokens_used: int = 0
    
    def get_questions_by_category(self) -> Dict[QuestionCategory, List[Question]]:
        """Group questions by category."""
        result = {}
        for question in self.questions:
            if question.category not in result:
                result[question.category] = []
            result[question.category].append(question)
        return result
    
    def get_questions_by_difficulty(self) -> Dict[DifficultyLevel, List[Question]]:
        """Group questions by difficulty level."""
        result = {}
        for question in self.questions:
            if question.difficulty not in result:
                result[question.difficulty] = []
            result[question.difficulty].append(question)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "success": self.success,
            "questions": [q.to_dict() for q in self.questions],
            "errors": self.errors,
            "warnings": self.warnings,
            "processing_time": self.processing_time,
            "api_calls_made": self.api_calls_made,
            "tokens_used": self.tokens_used,
            "summary": {
                "total_questions": len(self.questions),
                "questions_by_category": {
                    cat.value: len(questions) 
                    for cat, questions in self.get_questions_by_category().items()
                },
                "questions_by_difficulty": {
                    diff.value: len(questions) 
                    for diff, questions in self.get_questions_by_difficulty().items()
                }
            }
        }