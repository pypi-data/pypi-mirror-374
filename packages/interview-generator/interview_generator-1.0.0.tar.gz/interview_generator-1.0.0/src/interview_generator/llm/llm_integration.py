"""LLM integration for generating interview questions."""

import json
import logging
import time
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..models.config_models import Config
from ..models.context_models import CodeContext
from ..models.question_models import (
    Question, QuestionCategory, DifficultyLevel, 
    QuestionGenerationRequest, QuestionGenerationResult
)
from .prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class LLMIntegrationError(Exception):
    """Base exception for LLM integration errors."""
    pass


class APIRateLimitError(LLMIntegrationError):
    """Raised when API rate limit is exceeded."""
    pass


class APIAuthenticationError(LLMIntegrationError):
    """Raised when API authentication fails."""
    pass


class LLMIntegration:
    """Handles integration with LLM services for question generation."""
    
    def __init__(self, config: Config):
        """
        Initialize LLM integration.
        
        Args:
            config: Configuration object with LLM settings
        """
        self.config = config
        self.client = None
        self._setup_client()
        self._request_count = 0
        self._last_request_time = 0.0
        
    def _setup_client(self):
        """Set up the OpenAI client."""
        try:
            self.client = OpenAI(
                api_key=self.config.llm_api_key,
                base_url=self.config.llm_base_url,
                timeout=self.config.llm_timeout
            )
            
            # Test the API key with a simple request
            self._validate_api_key()
            
        except Exception as e:
            logger.error(f"Failed to setup OpenAI client: {e}")
            raise LLMIntegrationError(f"Failed to setup LLM client: {e}")
    
    def _validate_api_key(self):
        """Validate the API key by making a test request."""
        try:
            # Make a minimal request to validate the key
            response = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1
            )
            logger.info("API key validation successful")
        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                logger.error(f"API authentication failed: {e}")
                raise APIAuthenticationError(f"Invalid API key: {e}")
            else:
                logger.warning(f"API key validation failed, but continuing: {e}")
    
    async def generate_questions(self, context: CodeContext, code: str, 
                               request: QuestionGenerationRequest) -> QuestionGenerationResult:
        """
        Generate interview questions based on code context.
        
        Args:
            context: Extracted code context
            code: Original source code
            request: Question generation request parameters
            
        Returns:
            QuestionGenerationResult with generated questions
        """
        start_time = time.time()
        result = QuestionGenerationResult(success=True)
        
        try:
            logger.info(f"Generating questions for {len(request.categories)} categories")
            
            # Generate questions for each category and difficulty combination
            tasks = []
            for category in request.categories:
                for difficulty in request.difficulty_levels:
                    for i in range(request.max_questions_per_category):
                        task = self._generate_single_question(
                            context, code, category, difficulty, request
                        )
                        tasks.append(task)
            
            # Execute all generation tasks concurrently
            question_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for question_result in question_results:
                if isinstance(question_result, Exception):
                    error_msg = f"Question generation failed: {question_result}"
                    logger.error(error_msg)
                    result.errors.append(error_msg)
                elif question_result:
                    result.questions.append(question_result)
                    result.api_calls_made += 1
            
            result.processing_time = time.time() - start_time
            
            if not result.questions and result.errors:
                result.success = False
            
            logger.info(f"Generated {len(result.questions)} questions in {result.processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            result.success = False
            result.errors.append(f"Generation failed: {e}")
            result.processing_time = time.time() - start_time
        
        return result
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((Exception,))  # Will be more specific based on actual exceptions
    )
    async def _generate_single_question(self, context: CodeContext, code: str,
                                      category: QuestionCategory, difficulty: DifficultyLevel,
                                      request: QuestionGenerationRequest) -> Optional[Question]:
        """
        Generate a single question for a specific category and difficulty.
        
        Args:
            context: Code context
            code: Source code
            category: Question category
            difficulty: Difficulty level
            request: Generation request parameters
            
        Returns:
            Generated Question or None if failed
        """
        try:
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Create prompt
            prompt = PromptTemplates.create_prompt(category, difficulty, context, code)
            
            # Add custom instructions if provided
            if request.custom_instructions:
                prompt += f"\\n\\nAdditional Instructions: {request.custom_instructions}"
            
            logger.debug(f"Generating {category.value} question at {difficulty.value} level")
            
            # Make API call
            response = await self._make_api_call(prompt)
            
            # Parse response
            question = self._parse_question_response(response, category, difficulty, context)
            
            if question:
                logger.debug(f"Successfully generated {category.value} question")
                return question
            else:
                logger.warning(f"Failed to parse question response for {category.value}")
                return None
                
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str:
                logger.warning(f"Rate limit exceeded: {e}")
                raise APIRateLimitError(f"Rate limit exceeded: {e}")
            elif "authentication" in error_str or "api key" in error_str:
                logger.error(f"Authentication error: {e}")
                raise APIAuthenticationError(f"Authentication failed: {e}")
            else:
                logger.error(f"Failed to generate {category.value} question: {e}")
                return None
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting based on configuration."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        # Calculate minimum time between requests
        min_interval = 60.0 / self.config.llm_requests_per_minute
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    async def _make_api_call(self, prompt: str) -> Dict[str, Any]:
        """
        Make an API call to the LLM service.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            API response dictionary
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.config.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert technical interviewer creating high-quality interview questions. Always respond with valid JSON."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=self.config.llm_max_tokens,
                    temperature=self.config.llm_temperature
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise
    
    def _parse_question_response(self, response: Dict[str, Any], category: QuestionCategory,
                               difficulty: DifficultyLevel, context: CodeContext) -> Optional[Question]:
        """
        Parse the LLM response into a Question object.
        
        Args:
            response: API response
            category: Question category
            difficulty: Difficulty level
            context: Code context for metadata
            
        Returns:
            Parsed Question or None if parsing failed
        """
        try:
            # Extract content from response
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                question_data = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON from the content
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    question_data = json.loads(json_content)
                else:
                    logger.error(f"Could not parse JSON from response: {content}")
                    return None
            
            # Validate required fields
            required_fields = ['question_text', 'code_snippet', 'expected_answer']
            for field in required_fields:
                if field not in question_data:
                    logger.error(f"Missing required field '{field}' in response")
                    return None
            
            # Create Question object
            question = Question.create(
                category=category,
                difficulty=difficulty,
                question_text=question_data['question_text'],
                code_snippet=question_data['code_snippet'],
                expected_answer=question_data['expected_answer'],
                hints=question_data.get('hints', []),
                context_references=[
                    f"Domain: {context.business_context.domain_type.value}",
                    f"Purpose: {context.business_context.business_purpose}",
                    f"Quality Score: {context.overall_quality_score:.2f}"
                ],
                metadata={
                    'model_used': self.config.llm_model,
                    'tokens_used': response.usage.total_tokens if response.usage else 0,
                    'generation_time': time.time(),
                    'context_confidence': context.business_context.confidence_score
                }
            )
            
            return question
            
        except Exception as e:
            logger.error(f"Failed to parse question response: {e}")
            return None
    
    # Convenience methods for specific question types
    
    async def generate_comprehension_questions(self, context: CodeContext, code: str,
                                             difficulty_levels: List[DifficultyLevel],
                                             max_questions: int = 3) -> QuestionGenerationResult:
        """Generate comprehension questions."""
        request = QuestionGenerationRequest(
            categories=[QuestionCategory.COMPREHENSION],
            difficulty_levels=difficulty_levels,
            max_questions_per_category=max_questions
        )
        return await self.generate_questions(context, code, request)
    
    async def generate_debugging_questions(self, context: CodeContext, code: str,
                                         difficulty_levels: List[DifficultyLevel],
                                         max_questions: int = 3) -> QuestionGenerationResult:
        """Generate debugging questions."""
        request = QuestionGenerationRequest(
            categories=[QuestionCategory.DEBUGGING],
            difficulty_levels=difficulty_levels,
            max_questions_per_category=max_questions
        )
        return await self.generate_questions(context, code, request)
    
    async def generate_optimization_questions(self, context: CodeContext, code: str,
                                            difficulty_levels: List[DifficultyLevel],
                                            max_questions: int = 3) -> QuestionGenerationResult:
        """Generate optimization questions."""
        request = QuestionGenerationRequest(
            categories=[QuestionCategory.OPTIMIZATION],
            difficulty_levels=difficulty_levels,
            max_questions_per_category=max_questions
        )
        return await self.generate_questions(context, code, request)
    
    async def generate_design_questions(self, context: CodeContext, code: str,
                                       difficulty_levels: List[DifficultyLevel],
                                       max_questions: int = 3) -> QuestionGenerationResult:
        """Generate design questions."""
        request = QuestionGenerationRequest(
            categories=[QuestionCategory.DESIGN],
            difficulty_levels=difficulty_levels,
            max_questions_per_category=max_questions
        )
        return await self.generate_questions(context, code, request)
    
    async def generate_edge_case_questions(self, context: CodeContext, code: str,
                                         difficulty_levels: List[DifficultyLevel],
                                         max_questions: int = 3) -> QuestionGenerationResult:
        """Generate edge case questions."""
        request = QuestionGenerationRequest(
            categories=[QuestionCategory.EDGE_CASES],
            difficulty_levels=difficulty_levels,
            max_questions_per_category=max_questions
        )
        return await self.generate_questions(context, code, request)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'total_requests': self._request_count,
            'last_request_time': self._last_request_time,
            'configured_rate_limit': self.config.llm_requests_per_minute,
            'model': self.config.llm_model
        }