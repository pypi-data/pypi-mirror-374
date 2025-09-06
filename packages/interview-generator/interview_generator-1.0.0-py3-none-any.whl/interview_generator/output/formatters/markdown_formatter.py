"""Markdown output formatter for interview questions."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from textwrap import dedent, fill

from ...models.question_models import (
    Question, QuestionGenerationResult, QuestionCategory, DifficultyLevel
)
from ...models.context_models import CodeContext


logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Formats interview questions and results as Markdown."""
    
    def __init__(self, include_toc: bool = True, include_metadata: bool = True,
                 style: str = "interview"):
        """
        Initialize Markdown formatter.
        
        Args:
            include_toc: Whether to include table of contents
            include_metadata: Whether to include generation metadata
            style: Output style ("interview", "study_guide", "compact")
        """
        self.include_toc = include_toc
        self.include_metadata = include_metadata
        self.style = style
        
        # Style configurations
        self.styles = {
            "interview": {
                "question_header": "##",
                "include_hints": True,
                "include_answers": True,
                "code_language": "python",
                "show_difficulty": True
            },
            "study_guide": {
                "question_header": "###",
                "include_hints": True,
                "include_answers": True,
                "code_language": "python",
                "show_difficulty": True,
                "include_learning_objectives": True
            },
            "compact": {
                "question_header": "##",
                "include_hints": False,
                "include_answers": False,
                "code_language": "python",
                "show_difficulty": False
            }
        }
        
        self.config = self.styles.get(style, self.styles["interview"])
    
    def format_question(self, question: Question, question_number: int = 1) -> str:
        """
        Format a single question as Markdown.
        
        Args:
            question: Question to format
            question_number: Question number for display
            
        Returns:
            Markdown formatted question
        """
        try:
            lines = []
            
            # Question header
            header_level = self.config["question_header"]
            title = getattr(question, 'title', f"Question {question_number}")
            
            if self.config["show_difficulty"]:
                difficulty_badge = self._get_difficulty_badge(question.difficulty)
                lines.append(f"{header_level} {title} {difficulty_badge}")
            else:
                lines.append(f"{header_level} {title}")
            
            lines.append("")
            
            # Category and metadata
            category_badge = self._get_category_badge(question.category)
            lines.append(f"**Category:** {category_badge}")
            
            if hasattr(question, 'time_estimate_minutes') and question.time_estimate_minutes:
                lines.append(f"**Estimated Time:** {question.time_estimate_minutes} minutes")
            
            lines.append("")
            
            # Question text
            lines.append("### Question")
            lines.append("")
            lines.append(question.question_text)
            lines.append("")
            
            # Code snippet
            if question.code_snippet and question.code_snippet.strip():
                lines.append("### Code")
                lines.append("")
                lines.append(f"```{self.config['code_language']}")
                lines.append(question.code_snippet.strip())
                lines.append("```")
                lines.append("")
            
            # Learning objectives (study guide style)
            if (self.config.get("include_learning_objectives") and 
                hasattr(question, 'learning_objectives') and question.learning_objectives):
                lines.append("### Learning Objectives")
                lines.append("")
                for objective in question.learning_objectives:
                    lines.append(f"- {objective}")
                lines.append("")
            
            # Prerequisites
            if (hasattr(question, 'prerequisite_knowledge') and 
                question.prerequisite_knowledge):
                lines.append("### Prerequisites")
                lines.append("")
                for prereq in question.prerequisite_knowledge:
                    lines.append(f"- {prereq}")
                lines.append("")
            
            # Hints (collapsible)
            if self.config["include_hints"] and question.hints:
                lines.append("### Hints")
                lines.append("")
                for i, hint in enumerate(question.hints, 1):
                    if hasattr(hint, 'text'):  # QuestionHint object
                        hint_text = hint.text
                        if hasattr(hint, 'reveals_concept') and hint.reveals_concept:
                            hint_text += f" *(Concept: {hint.reveals_concept})*"
                    else:  # String hint
                        hint_text = hint
                    
                    lines.append(f"<details>")
                    lines.append(f"<summary>Hint {i}</summary>")
                    lines.append("")
                    lines.append(hint_text)
                    lines.append("")
                    lines.append("</details>")
                    lines.append("")
            
            # Expected answer
            if self.config["include_answers"] and question.expected_answer:
                lines.append("### Expected Answer")
                lines.append("")
                lines.append("<details>")
                lines.append("<summary>Click to reveal answer</summary>")
                lines.append("")
                lines.append(question.expected_answer)
                lines.append("")
                lines.append("</details>")
                lines.append("")
            
            # Sample answer (if different from expected)
            if (self.config["include_answers"] and 
                hasattr(question, 'sample_answer') and question.sample_answer and
                question.sample_answer != question.expected_answer):
                lines.append("### Sample Answer")
                lines.append("")
                lines.append("<details>")
                lines.append("<summary>Click to reveal sample answer</summary>")
                lines.append("")
                lines.append(question.sample_answer)
                lines.append("")
                lines.append("</details>")
                lines.append("")
            
            # Follow-up questions
            if (hasattr(question, 'follow_up_questions') and 
                question.follow_up_questions):
                lines.append("### Follow-up Questions")
                lines.append("")
                for follow_up in question.follow_up_questions:
                    lines.append(f"- {follow_up}")
                lines.append("")
            
            # Tags
            if hasattr(question, 'tags') and question.tags:
                tag_badges = [f"`{tag}`" for tag in question.tags]
                lines.append(f"**Tags:** {' '.join(tag_badges)}")
                lines.append("")
            
            # Separator
            lines.append("---")
            lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting question {question.id}: {e}")
            return f"## Error formatting question {question.id}\n\n{str(e)}\n\n---\n\n"
    
    def format_question_list(self, questions: List[Question]) -> str:
        """
        Format a list of questions as Markdown.
        
        Args:
            questions: List of questions to format
            
        Returns:
            Markdown formatted questions
        """
        if not questions:
            return "No questions generated.\n"
        
        formatted_questions = []
        for i, question in enumerate(questions, 1):
            formatted_questions.append(self.format_question(question, i))
        
        return "\n".join(formatted_questions)
    
    def format_generation_result(self, result: QuestionGenerationResult,
                               title: str = "Interview Questions") -> str:
        """
        Format a complete question generation result as Markdown.
        
        Args:
            result: Generation result to format
            title: Document title
            
        Returns:
            Complete Markdown document
        """
        try:
            lines = []
            
            # Document title
            lines.append(f"# {title}")
            lines.append("")
            lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")
            lines.append("")
            
            # Generation summary
            if result.success:
                lines.append(f"✅ Successfully generated **{len(result.questions)}** questions")
            else:
                lines.append(f"❌ Generation failed")
            
            if result.warnings:
                lines.append(f"⚠️  {len(result.warnings)} warnings")
            
            if result.errors:
                lines.append(f"🚫 {len(result.errors)} errors")
            
            lines.append("")
            
            # Statistics
            if self.include_metadata:
                lines.extend(self._format_statistics(result))
            
            # Table of contents
            if self.include_toc and result.questions:
                lines.extend(self._generate_toc(result.questions))
            
            # Questions by category
            if result.questions:
                lines.extend(self._format_questions_by_category(result.questions))
            
            # Errors and warnings
            if result.errors or result.warnings:
                lines.extend(self._format_issues(result.errors, result.warnings))
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting generation result: {e}")
            return f"# Error\n\nFailed to format generation result: {str(e)}\n"
    
    def format_with_context(self, result: QuestionGenerationResult,
                          context: Optional[CodeContext] = None,
                          source_code: Optional[str] = None,
                          title: str = "Code Analysis & Interview Questions") -> str:
        """
        Format result with additional context information.
        
        Args:
            result: Generation result
            context: Code context used for generation
            source_code: Original source code
            title: Document title
            
        Returns:
            Enhanced Markdown document
        """
        lines = []
        
        # Document header
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")
        lines.append("")
        
        # Code analysis summary
        if context:
            lines.extend(self._format_code_analysis(context))
        
        # Source code (if provided and reasonable size)
        if source_code and len(source_code) < 5000:  # Limit to 5KB for readability
            lines.append("## Source Code")
            lines.append("")
            lines.append("```python")
            lines.append(source_code.strip())
            lines.append("```")
            lines.append("")
        elif source_code:
            lines.append("## Source Code")
            lines.append("")
            lines.append(f"*Source code omitted for brevity ({len(source_code)} characters, "
                        f"{source_code.count(chr(10)) + 1} lines)*")
            lines.append("")
        
        # Questions section
        questions_md = self.format_generation_result(result, "Generated Questions")
        # Remove the title from the questions section since we have our own
        questions_lines = questions_md.split('\n')
        if questions_lines and questions_lines[0].startswith('# '):
            questions_lines = questions_lines[3:]  # Skip title and empty lines
        
        lines.extend(questions_lines)
        
        return "\n".join(lines)
    
    def _get_difficulty_badge(self, difficulty: DifficultyLevel) -> str:
        """Get a colored badge for difficulty level."""
        badges = {
            DifficultyLevel.BEGINNER: "![Beginner](https://img.shields.io/badge/Difficulty-Beginner-green)",
            DifficultyLevel.INTERMEDIATE: "![Intermediate](https://img.shields.io/badge/Difficulty-Intermediate-yellow)",
            DifficultyLevel.ADVANCED: "![Advanced](https://img.shields.io/badge/Difficulty-Advanced-orange)",
            DifficultyLevel.EXPERT: "![Expert](https://img.shields.io/badge/Difficulty-Expert-red)"
        }
        return badges.get(difficulty, f"`{difficulty.value}`")
    
    def _get_category_badge(self, category: QuestionCategory) -> str:
        """Get a badge for question category."""
        badges = {
            QuestionCategory.COMPREHENSION: "![Comprehension](https://img.shields.io/badge/Category-Comprehension-blue)",
            QuestionCategory.DEBUGGING: "![Debugging](https://img.shields.io/badge/Category-Debugging-red)",
            QuestionCategory.OPTIMIZATION: "![Optimization](https://img.shields.io/badge/Category-Optimization-purple)",
            QuestionCategory.DESIGN: "![Design](https://img.shields.io/badge/Category-Design-teal)",
            QuestionCategory.EDGE_CASES: "![Edge Cases](https://img.shields.io/badge/Category-Edge_Cases-orange)"
        }
        return badges.get(category, f"`{category.value}`")
    
    def _format_statistics(self, result: QuestionGenerationResult) -> List[str]:
        """Format generation statistics."""
        lines = ["## Generation Statistics", ""]
        
        # Basic stats
        lines.append(f"- **Total Questions:** {len(result.questions)}")
        lines.append(f"- **Processing Time:** {result.processing_time:.2f} seconds")
        lines.append(f"- **API Calls Made:** {result.api_calls_made}")
        lines.append(f"- **Tokens Used:** {result.tokens_used}")
        
        if hasattr(result, 'cost_estimate'):
            lines.append(f"- **Estimated Cost:** ${result.cost_estimate:.4f}")
        
        lines.append("")
        
        # Question distribution
        if result.questions:
            category_counts = {}
            difficulty_counts = {}
            
            for question in result.questions:
                cat = question.category.value
                diff = question.difficulty.value
                category_counts[cat] = category_counts.get(cat, 0) + 1
                difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            
            lines.append("### Question Distribution")
            lines.append("")
            lines.append("**By Category:**")
            for category, count in sorted(category_counts.items()):
                percentage = (count / len(result.questions)) * 100
                lines.append(f"- {category.title()}: {count} ({percentage:.1f}%)")
            
            lines.append("")
            lines.append("**By Difficulty:**")
            for difficulty, count in sorted(difficulty_counts.items()):
                percentage = (count / len(result.questions)) * 100
                lines.append(f"- {difficulty.title()}: {count} ({percentage:.1f}%)")
            
            lines.append("")
        
        return lines
    
    def _generate_toc(self, questions: List[Question]) -> List[str]:
        """Generate table of contents."""
        lines = ["## Table of Contents", ""]
        
        # Group by category
        category_groups = {}
        for i, question in enumerate(questions, 1):
            category = question.category.value
            if category not in category_groups:
                category_groups[category] = []
            
            title = getattr(question, 'title', f"Question {i}")
            category_groups[category].append((i, title))
        
        for category, question_list in sorted(category_groups.items()):
            lines.append(f"### {category.title()}")
            for num, title in question_list:
                # Create anchor link (simplified)
                anchor = title.lower().replace(' ', '-').replace('?', '').replace('!', '')
                lines.append(f"{num}. [{title}](#{anchor})")
            lines.append("")
        
        return lines
    
    def _format_questions_by_category(self, questions: List[Question]) -> List[str]:
        """Format questions grouped by category."""
        lines = []
        
        # Group questions by category
        category_groups = {}
        for question in questions:
            category = question.category
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(question)
        
        # Format each category
        for category in sorted(category_groups.keys(), key=lambda x: x.value):
            category_questions = category_groups[category]
            
            lines.append(f"## {category.value.title()} Questions")
            lines.append("")
            
            question_number = 1
            for question in category_questions:
                lines.append(self.format_question(question, question_number))
                question_number += 1
        
        return lines
    
    def _format_issues(self, errors: List[str], warnings: List[str]) -> List[str]:
        """Format errors and warnings."""
        lines = []
        
        if errors:
            lines.append("## Errors")
            lines.append("")
            for error in errors:
                lines.append(f"🚫 {error}")
            lines.append("")
        
        if warnings:
            lines.append("## Warnings")
            lines.append("")
            for warning in warnings:
                lines.append(f"⚠️  {warning}")
            lines.append("")
        
        return lines
    
    def _format_code_analysis(self, context: CodeContext) -> List[str]:
        """Format code analysis summary."""
        lines = ["## Code Analysis Summary", ""]
        
        # Basic info
        lines.append(f"- **Domain:** {context.business_context.domain_type.value}")
        lines.append(f"- **Purpose:** {context.business_context.business_purpose}")
        lines.append(f"- **Overall Quality:** {context.overall_quality_score:.2f}/1.0")
        
        if hasattr(context, 'maintainability_score'):
            lines.append(f"- **Maintainability:** {context.maintainability_score:.2f}/1.0")
        
        if hasattr(context, 'testability_score'):
            lines.append(f"- **Testability:** {context.testability_score:.2f}/1.0")
        
        lines.append(f"- **Functions Analyzed:** {len(context.function_contexts)}")
        lines.append(f"- **Classes Analyzed:** {len(context.class_contexts)}")
        lines.append(f"- **Documentation Quality:** {context.documentation_context.docstring_quality}")
        lines.append("")
        
        # Key findings
        if context.business_context.workflow_patterns:
            lines.append("### Key Patterns Detected")
            for pattern in context.business_context.workflow_patterns:
                lines.append(f"- {pattern.value if hasattr(pattern, 'value') else pattern}")
            lines.append("")
        
        return lines