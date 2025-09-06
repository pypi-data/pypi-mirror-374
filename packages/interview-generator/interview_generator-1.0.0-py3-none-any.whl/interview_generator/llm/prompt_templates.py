"""Prompt templates for LLM question generation."""

from typing import Dict, Any
from ..models.context_models import CodeContext
from ..models.question_models import QuestionCategory, DifficultyLevel


class PromptTemplates:
    """Collection of prompt templates for different question categories."""
    
    BASE_CONTEXT_TEMPLATE = """
Code Analysis Context:
- Domain: {domain}
- Business Purpose: {purpose}
- Workflow Patterns: {workflow_patterns}
- Data Entities: {data_entities}
- Error Handling Coverage: {error_handling_coverage:.1%}
- Documentation Quality: {documentation_quality}
- Overall Quality Score: {overall_quality:.2f}

Function Contexts:
{function_contexts}

Class Contexts:
{class_contexts}
"""
    
    COMPREHENSION_TEMPLATE = """
You are an expert technical interviewer creating code comprehension questions.

{context}

Code to Analyze:
```python
{code}
```

Create a {difficulty} level comprehension question that tests understanding of:
- What the code does and its purpose
- How the code works and its logic flow
- The business context and domain knowledge
- Key algorithms or patterns used

Requirements:
- Generate exactly ONE question
- Question should be clear and specific
- Include the code snippet in your response
- Provide a comprehensive expected answer
- Add 2-3 helpful hints for the interviewer

Format your response as JSON:
{{
    "question_text": "Your question here",
    "code_snippet": "The relevant code snippet",
    "expected_answer": "Detailed expected answer",
    "hints": ["Hint 1", "Hint 2", "Hint 3"]
}}
"""
    
    DEBUGGING_TEMPLATE = """
You are an expert technical interviewer creating debugging questions.

{context}

Code to Analyze:
```python
{code}
```

Create a {difficulty} level debugging question by either:
1. Introducing a realistic bug into the code
2. Asking about potential issues or edge cases
3. Testing knowledge of common pitfalls

Focus on:
- Logic errors, off-by-one errors, or incorrect conditions
- Exception handling issues
- Performance problems or memory leaks
- Concurrency issues if applicable
- Input validation problems

Requirements:
- Generate exactly ONE question
- If introducing a bug, make it realistic and subtle
- Provide clear explanation of the issue
- Include debugging steps in the expected answer

Format your response as JSON:
{{
    "question_text": "Your debugging question here",
    "code_snippet": "Code with bug or code to analyze for issues",
    "expected_answer": "Explanation of the bug/issue and how to fix it",
    "hints": ["Debugging hint 1", "Debugging hint 2", "Debugging hint 3"]
}}
"""
    
    OPTIMIZATION_TEMPLATE = """
You are an expert technical interviewer creating performance optimization questions.

{context}

Code to Analyze:
```python
{code}
```

Performance Context:
- Performance Hotspots: {performance_hotspots}
- I/O Operations: {io_operations}
- Optimization Patterns: {optimization_patterns}
- Complexity Hotspots: {complexity_hotspots}

Create a {difficulty} level optimization question focusing on:
- Time complexity improvements
- Space complexity optimizations
- I/O efficiency
- Caching strategies
- Algorithm improvements
- Memory usage optimization

Requirements:
- Generate exactly ONE question
- Focus on realistic performance improvements
- Consider the existing optimization patterns
- Provide specific optimization techniques in the answer

Format your response as JSON:
{{
    "question_text": "Your optimization question here",
    "code_snippet": "Code to optimize",
    "expected_answer": "Detailed optimization approach with improved code if applicable",
    "hints": ["Optimization hint 1", "Optimization hint 2", "Optimization hint 3"]
}}
"""
    
    DESIGN_TEMPLATE = """
You are an expert technical interviewer creating software design questions.

{context}

Code to Analyze:
```python
{code}
```

Architectural Context:
- Design Patterns: {design_patterns}
- Responsibilities: {responsibilities}
- Integration Patterns: {integration_patterns}

Create a {difficulty} level design question focusing on:
- Code structure and organization
- Design patterns and their application
- SOLID principles
- Refactoring opportunities
- Architecture improvements
- Separation of concerns

Requirements:
- Generate exactly ONE question
- Focus on design principles and patterns
- Consider maintainability and extensibility
- Provide design alternatives in the answer

Format your response as JSON:
{{
    "question_text": "Your design question here",
    "code_snippet": "Code to analyze or refactor",
    "expected_answer": "Design analysis and improvement suggestions",
    "hints": ["Design hint 1", "Design hint 2", "Design hint 3"]
}}
"""
    
    EDGE_CASES_TEMPLATE = """
You are an expert technical interviewer creating edge case and error handling questions.

{context}

Code to Analyze:
```python
{code}
```

Error Handling Context:
- Exception Patterns: {exception_patterns}
- Recovery Strategies: {recovery_strategies}
- Validation Approaches: {validation_approaches}
- Security Vulnerabilities: {security_vulnerabilities}

Create a {difficulty} level edge case question focusing on:
- Boundary conditions and limits
- Invalid input handling
- Error scenarios and recovery
- Security considerations
- Resource exhaustion scenarios
- Concurrent access issues

Requirements:
- Generate exactly ONE question
- Focus on realistic edge cases
- Consider security implications
- Provide comprehensive error handling in the answer

Format your response as JSON:
{{
    "question_text": "Your edge case question here",
    "code_snippet": "Code to analyze for edge cases",
    "expected_answer": "Analysis of edge cases and proper handling approaches",
    "hints": ["Edge case hint 1", "Edge case hint 2", "Edge case hint 3"]
}}
"""
    
    @classmethod
    def get_template(cls, category: QuestionCategory) -> str:
        """Get the appropriate template for a question category."""
        templates = {
            QuestionCategory.COMPREHENSION: cls.COMPREHENSION_TEMPLATE,
            QuestionCategory.DEBUGGING: cls.DEBUGGING_TEMPLATE,
            QuestionCategory.OPTIMIZATION: cls.OPTIMIZATION_TEMPLATE,
            QuestionCategory.DESIGN: cls.DESIGN_TEMPLATE,
            QuestionCategory.EDGE_CASES: cls.EDGE_CASES_TEMPLATE
        }
        return templates.get(category, cls.COMPREHENSION_TEMPLATE)
    
    @classmethod
    def format_context(cls, context: CodeContext) -> str:
        """Format code context for inclusion in prompts."""
        function_contexts = "\\n".join([
            f"- {func.function_name}: {func.business_purpose} (Complexity: {func.complexity_level})"
            for func in context.function_contexts[:5]  # Limit to first 5
        ]) or "No functions analyzed"
        
        class_contexts = "\\n".join([
            f"- {cls_ctx.class_name}: {cls_ctx.business_purpose}"
            for cls_ctx in context.class_contexts[:5]  # Limit to first 5
        ]) or "No classes analyzed"
        
        return cls.BASE_CONTEXT_TEMPLATE.format(
            domain=context.business_context.domain_type.value,
            purpose=context.business_context.business_purpose,
            workflow_patterns=", ".join([p.value for p in context.business_context.workflow_patterns]) or "None identified",
            data_entities=", ".join(context.business_context.data_entities[:5]) or "None identified",
            error_handling_coverage=context.error_handling_context.error_handling_coverage,
            documentation_quality=context.documentation_context.docstring_quality,
            overall_quality=context.overall_quality_score,
            function_contexts=function_contexts,
            class_contexts=class_contexts
        )
    
    @classmethod
    def create_prompt(cls, category: QuestionCategory, difficulty: DifficultyLevel,
                     context: CodeContext, code: str) -> str:
        """Create a complete prompt for question generation."""
        template = cls.get_template(category)
        formatted_context = cls.format_context(context)
        
        # Category-specific context formatting
        if category == QuestionCategory.OPTIMIZATION:
            return template.format(
                context=formatted_context,
                code=code,
                difficulty=difficulty.value,
                performance_hotspots=", ".join(context.performance_context.performance_hotspots) or "None identified",
                io_operations=", ".join(context.performance_context.io_operations) or "None identified",
                optimization_patterns=", ".join([p.value for p in context.performance_context.optimization_patterns]) or "None identified",
                complexity_hotspots=", ".join(context.performance_context.complexity_hotspots) or "None identified"
            )
        elif category == QuestionCategory.DESIGN:
            design_patterns = []
            responsibilities = []
            for class_ctx in context.class_contexts:
                design_patterns.extend(class_ctx.design_patterns)
                responsibilities.extend(class_ctx.responsibilities)
            
            return template.format(
                context=formatted_context,
                code=code,
                difficulty=difficulty.value,
                design_patterns=", ".join(design_patterns[:5]) or "None identified",
                responsibilities=", ".join(responsibilities[:5]) or "None identified",
                integration_patterns=", ".join(context.integration_context.api_integrations if context.integration_context else []) or "None identified"
            )
        elif category == QuestionCategory.EDGE_CASES:
            return template.format(
                context=formatted_context,
                code=code,
                difficulty=difficulty.value,
                exception_patterns=", ".join(context.error_handling_context.exception_patterns) or "None identified",
                recovery_strategies=", ".join([s.value for s in context.error_handling_context.recovery_strategies]) or "None identified",
                validation_approaches=", ".join(context.error_handling_context.validation_approaches) or "None identified",
                security_vulnerabilities=", ".join(context.security_context.security_vulnerabilities if context.security_context else []) or "None identified"
            )
        else:
            # Default formatting for COMPREHENSION and DEBUGGING
            return template.format(
                context=formatted_context,
                code=code,
                difficulty=difficulty.value
            )