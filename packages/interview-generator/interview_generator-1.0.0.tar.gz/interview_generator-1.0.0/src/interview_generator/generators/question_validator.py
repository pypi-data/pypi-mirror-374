"""Question validation logic to ensure quality and relevance."""

import logging
import re
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field

from ..models.question_models import Question, QuestionCategory, DifficultyLevel
from ..models.context_models import CodeContext


logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a validation issue with a question."""
    severity: str  # "error", "warning", "info"
    category: str  # "content", "structure", "relevance", "quality"
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of question validation."""
    is_valid: bool
    quality_score: float  # 0.0 to 1.0
    issues: List[ValidationIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class QuestionValidator:
    """Validates interview questions for quality, relevance, and completeness."""
    
    def __init__(self):
        """Initialize the validator."""
        # Quality thresholds
        self.min_quality_score = 0.6
        self.min_question_length = 20
        self.max_question_length = 500
        self.min_answer_length = 10
        
        # Common quality indicators
        self.quality_keywords = {
            'positive': [
                'analyze', 'explain', 'describe', 'identify', 'compare', 'evaluate',
                'implement', 'optimize', 'debug', 'refactor', 'design', 'consider'
            ],
            'negative': [
                'simply', 'just', 'obviously', 'clearly', 'easy', 'hard', 'difficult'
            ]
        }
        
        # Relevance keywords by category
        self.category_keywords = {
            QuestionCategory.COMPREHENSION: [
                'understand', 'purpose', 'function', 'works', 'does', 'logic', 'flow'
            ],
            QuestionCategory.DEBUGGING: [
                'bug', 'error', 'issue', 'problem', 'fix', 'debug', 'wrong', 'fail'
            ],
            QuestionCategory.OPTIMIZATION: [
                'optimize', 'performance', 'efficient', 'faster', 'memory', 'speed', 'improve'
            ],
            QuestionCategory.DESIGN: [
                'design', 'pattern', 'architecture', 'structure', 'organize', 'refactor'
            ],
            QuestionCategory.EDGE_CASES: [
                'edge', 'boundary', 'corner', 'exception', 'invalid', 'unexpected', 'handle'
            ]
        }
    
    def validate_question(self, question: Question, context: Optional[CodeContext] = None) -> ValidationResult:
        """
        Validate a single question for quality and relevance.
        
        Args:
            question: Question to validate
            context: Optional code context for relevance checking
            
        Returns:
            ValidationResult with validation details
        """
        issues = []
        quality_scores = []
        
        # Validate structure
        structure_score, structure_issues = self._validate_structure(question)
        issues.extend(structure_issues)
        quality_scores.append(structure_score)
        
        # Validate content quality
        content_score, content_issues = self._validate_content_quality(question)
        issues.extend(content_issues)
        quality_scores.append(content_score)
        
        # Validate relevance to category
        relevance_score, relevance_issues = self._validate_category_relevance(question)
        issues.extend(relevance_issues)
        quality_scores.append(relevance_score)
        
        # Validate difficulty appropriateness
        difficulty_score, difficulty_issues = self._validate_difficulty_level(question)
        issues.extend(difficulty_issues)
        quality_scores.append(difficulty_score)
        
        # Validate code relevance if context provided
        if context:
            code_relevance_score, code_issues = self._validate_code_relevance(question, context)
            issues.extend(code_issues)
            quality_scores.append(code_relevance_score)
        
        # Calculate overall quality score
        overall_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Determine if valid
        error_count = len([i for i in issues if i.severity == "error"])
        is_valid = error_count == 0 and overall_score >= self.min_quality_score
        
        # Generate suggestions
        suggestions = self._generate_suggestions(question, issues, overall_score)
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=overall_score,
            issues=issues,
            suggestions=suggestions
        )
    
    def validate_question_set(self, questions: List[Question], 
                            context: Optional[CodeContext] = None) -> Dict[str, ValidationResult]:
        """
        Validate a set of questions and check for duplicates/overlap.
        
        Args:
            questions: List of questions to validate
            context: Optional code context
            
        Returns:
            Dictionary mapping question IDs to validation results
        """
        results = {}
        
        # Validate individual questions
        for question in questions:
            results[question.id] = self.validate_question(question, context)
        
        # Check for duplicates and overlap
        self._check_question_overlap(questions, results)
        
        # Check category distribution
        self._validate_category_distribution(questions, results)
        
        # Check difficulty distribution
        self._validate_difficulty_distribution(questions, results)
        
        return results
    
    def _validate_structure(self, question: Question) -> Tuple[float, List[ValidationIssue]]:
        """Validate question structure and required fields."""
        issues = []
        score = 1.0
        
        # Check required fields
        if not question.question_text or len(question.question_text.strip()) == 0:
            issues.append(ValidationIssue(
                severity="error",
                category="structure",
                message="Question text is empty",
                suggestion="Provide a clear, specific question"
            ))
            score -= 0.5
        
        if not question.expected_answer or len(question.expected_answer.strip()) == 0:
            issues.append(ValidationIssue(
                severity="error",
                category="structure",
                message="Expected answer is empty",
                suggestion="Provide guidance on what a good answer should include"
            ))
            score -= 0.3
        
        # Check question length
        if question.question_text:
            if len(question.question_text) < self.min_question_length:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="structure",
                    message="Question text is very short",
                    suggestion="Provide more context and detail in the question"
                ))
                score -= 0.1
            elif len(question.question_text) > self.max_question_length:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="structure",
                    message="Question text is very long",
                    suggestion="Consider breaking into multiple questions or simplifying"
                ))
                score -= 0.1
        
        # Check answer length
        if question.expected_answer and len(question.expected_answer) < self.min_answer_length:
            issues.append(ValidationIssue(
                severity="warning",
                category="structure",
                message="Expected answer is very short",
                suggestion="Provide more detailed guidance for the expected answer"
            ))
            score -= 0.1
        
        # Check for hints if they should be present
        if not question.hints:
            issues.append(ValidationIssue(
                severity="info",
                category="structure",
                message="No hints provided",
                suggestion="Consider adding hints to help candidates"
            ))
        
        return max(0.0, score), issues
    
    def _validate_content_quality(self, question: Question) -> Tuple[float, List[ValidationIssue]]:
        """Validate the quality of question content."""
        issues = []
        score = 1.0
        
        question_text = question.question_text.lower() if question.question_text else ""
        
        # Check for positive quality indicators
        positive_count = sum(1 for keyword in self.quality_keywords['positive'] 
                           if keyword in question_text)
        if positive_count == 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="quality",
                message="Question lacks action-oriented language",
                suggestion="Use verbs like 'analyze', 'explain', 'identify' to make questions more engaging"
            ))
            score -= 0.2
        
        # Check for negative quality indicators
        negative_count = sum(1 for keyword in self.quality_keywords['negative'] 
                           if keyword in question_text)
        if negative_count > 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="quality",
                message="Question contains subjective language",
                suggestion="Avoid words like 'obviously', 'simply', 'easy' that may be subjective"
            ))
            score -= 0.1 * negative_count
        
        # Check for question marks
        if question.question_text and '?' not in question.question_text:
            issues.append(ValidationIssue(
                severity="info",
                category="quality",
                message="Question doesn't end with a question mark",
                suggestion="Consider rephrasing as a direct question"
            ))
        
        # Check for code references
        if question.code_snippet and question.code_snippet.strip():
            if 'code' not in question_text and 'function' not in question_text:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="quality",
                    message="Question doesn't reference the provided code",
                    suggestion="Explicitly reference the code snippet in the question"
                ))
                score -= 0.2
        
        return max(0.0, score), issues
    
    def _validate_category_relevance(self, question: Question) -> Tuple[float, List[ValidationIssue]]:
        """Validate that question content matches its category."""
        issues = []
        score = 1.0
        
        if not question.question_text:
            return 0.0, issues
        
        question_text = question.question_text.lower()
        category_keywords = self.category_keywords.get(question.category, [])
        
        # Check for category-relevant keywords
        relevant_keywords = [kw for kw in category_keywords if kw in question_text]
        
        if not relevant_keywords:
            issues.append(ValidationIssue(
                severity="warning",
                category="relevance",
                message=f"Question doesn't clearly relate to {question.category.value} category",
                suggestion=f"Include keywords like: {', '.join(category_keywords[:3])}"
            ))
            score -= 0.3
        
        # Category-specific validation
        if question.category == QuestionCategory.DEBUGGING:
            if not any(word in question_text for word in ['bug', 'error', 'issue', 'problem', 'fix']):
                issues.append(ValidationIssue(
                    severity="warning",
                    category="relevance",
                    message="Debugging question should mention bugs, errors, or issues",
                    suggestion="Frame the question around identifying or fixing problems"
                ))
                score -= 0.2
        
        elif question.category == QuestionCategory.OPTIMIZATION:
            if not any(word in question_text for word in ['performance', 'optimize', 'efficient', 'improve']):
                issues.append(ValidationIssue(
                    severity="warning",
                    category="relevance",
                    message="Optimization question should focus on performance improvements",
                    suggestion="Ask about making the code faster, more efficient, or using less memory"
                ))
                score -= 0.2
        
        return max(0.0, score), issues
    
    def _validate_difficulty_level(self, question: Question) -> Tuple[float, List[ValidationIssue]]:
        """Validate that question difficulty matches its assigned level."""
        issues = []
        score = 1.0
        
        if not question.question_text:
            return 0.0, issues
        
        question_text = question.question_text.lower()
        
        # Difficulty indicators
        beginner_indicators = ['what', 'basic', 'simple', 'identify', 'list']
        intermediate_indicators = ['how', 'why', 'explain', 'analyze', 'compare']
        advanced_indicators = ['evaluate', 'design', 'optimize', 'refactor', 'architect']
        expert_indicators = ['synthesize', 'create', 'innovate', 'trade-offs', 'scalability']
        
        # Count indicators for each level
        beginner_count = sum(1 for ind in beginner_indicators if ind in question_text)
        intermediate_count = sum(1 for ind in intermediate_indicators if ind in question_text)
        advanced_count = sum(1 for ind in advanced_indicators if ind in question_text)
        expert_count = sum(1 for ind in expert_indicators if ind in question_text)
        
        # Check alignment with assigned difficulty
        if question.difficulty == DifficultyLevel.BEGINNER:
            if beginner_count == 0 and intermediate_count > 0:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="difficulty",
                    message="Question seems too complex for beginner level",
                    suggestion="Use simpler language and focus on basic concepts"
                ))
                score -= 0.2
        
        elif question.difficulty == DifficultyLevel.EXPERT:
            if expert_count == 0 and advanced_count == 0:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="difficulty",
                    message="Question may be too simple for expert level",
                    suggestion="Focus on complex trade-offs, design decisions, or advanced concepts"
                ))
                score -= 0.2
        
        return max(0.0, score), issues
    
    def _validate_code_relevance(self, question: Question, context: CodeContext) -> Tuple[float, List[ValidationIssue]]:
        """Validate that question is relevant to the provided code context."""
        issues = []
        score = 1.0
        
        if not question.question_text:
            return 0.0, issues
        
        question_text = question.question_text.lower()
        
        # Check if question mentions domain-specific concepts
        domain_keywords = {
            'web': ['http', 'request', 'response', 'api', 'endpoint', 'server'],
            'data': ['data', 'process', 'transform', 'analyze', 'dataset'],
            'ml': ['model', 'train', 'predict', 'algorithm', 'machine learning'],
            'finance': ['transaction', 'account', 'payment', 'financial'],
            'system': ['system', 'process', 'resource', 'performance']
        }
        
        domain = context.business_context.domain_type.value
        relevant_keywords = domain_keywords.get(domain, [])
        
        if relevant_keywords:
            domain_relevance = any(kw in question_text for kw in relevant_keywords)
            if not domain_relevance and domain != 'unknown':
                issues.append(ValidationIssue(
                    severity="info",
                    category="relevance",
                    message=f"Question could be more specific to {domain} domain",
                    suggestion=f"Consider mentioning {domain}-specific concepts"
                ))
                score -= 0.1
        
        # Check if question references specific functions or classes
        function_names = [f.function_name.lower() for f in context.function_contexts]
        class_names = [c.class_name.lower() for c in context.class_contexts]
        
        mentions_specific_code = any(name in question_text for name in function_names + class_names)
        if not mentions_specific_code and (function_names or class_names):
            issues.append(ValidationIssue(
                severity="info",
                category="relevance",
                message="Question could reference specific functions or classes",
                suggestion="Make the question more specific to the actual code"
            ))
            score -= 0.1
        
        return max(0.0, score), issues
    
    def _check_question_overlap(self, questions: List[Question], 
                              results: Dict[str, ValidationResult]) -> None:
        """Check for duplicate or overlapping questions."""
        question_texts = [q.question_text.lower() for q in questions if q.question_text]
        
        for i, question in enumerate(questions):
            if not question.question_text:
                continue
                
            current_text = question.question_text.lower()
            
            # Check for exact duplicates
            for j, other_text in enumerate(question_texts):
                if i != j and current_text == other_text:
                    results[question.id].issues.append(ValidationIssue(
                        severity="error",
                        category="content",
                        message="Duplicate question detected",
                        suggestion="Remove or rephrase duplicate questions"
                    ))
                    results[question.id].is_valid = False
            
            # Check for high similarity (simple word overlap check)
            for j, other_question in enumerate(questions):
                if i != j and other_question.question_text:
                    similarity = self._calculate_text_similarity(
                        current_text, other_question.question_text.lower()
                    )
                    if similarity > 0.8:
                        results[question.id].issues.append(ValidationIssue(
                            severity="warning",
                            category="content",
                            message="Very similar question detected",
                            suggestion="Consider making questions more distinct"
                        ))
    
    def _validate_category_distribution(self, questions: List[Question],
                                      results: Dict[str, ValidationResult]) -> None:
        """Validate the distribution of question categories."""
        category_counts = {}
        for question in questions:
            category_counts[question.category] = category_counts.get(question.category, 0) + 1
        
        # Check if there's good category diversity
        if len(category_counts) == 1 and len(questions) > 3:
            for question in questions:
                results[question.id].issues.append(ValidationIssue(
                    severity="info",
                    category="distribution",
                    message="All questions are in the same category",
                    suggestion="Consider adding questions from different categories for variety"
                ))
    
    def _validate_difficulty_distribution(self, questions: List[Question],
                                        results: Dict[str, ValidationResult]) -> None:
        """Validate the distribution of difficulty levels."""
        difficulty_counts = {}
        for question in questions:
            difficulty_counts[question.difficulty] = difficulty_counts.get(question.difficulty, 0) + 1
        
        # Check for reasonable difficulty progression
        if len(questions) > 2 and len(difficulty_counts) == 1:
            for question in questions:
                results[question.id].issues.append(ValidationIssue(
                    severity="info",
                    category="distribution",
                    message="All questions have the same difficulty level",
                    suggestion="Consider varying difficulty levels for better assessment"
                ))
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity based on word overlap."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_suggestions(self, question: Question, issues: List[ValidationIssue],
                            quality_score: float) -> List[str]:
        """Generate improvement suggestions based on validation results."""
        suggestions = []
        
        # Extract suggestions from issues
        for issue in issues:
            if issue.suggestion and issue.suggestion not in suggestions:
                suggestions.append(issue.suggestion)
        
        # Add general suggestions based on quality score
        if quality_score < 0.7:
            suggestions.append("Consider revising the question for better clarity and specificity")
        
        if quality_score < 0.5:
            suggestions.append("Question needs significant improvement before use")
        
        return suggestions