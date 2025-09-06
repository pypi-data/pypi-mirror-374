"""
Context extraction system for analyzing business logic and semantic meaning in Python code.
"""

import ast
import re
import logging
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
from collections import defaultdict, Counter

from ..models.context_models import (
    BusinessContext, ErrorHandlingContext, PerformanceContext, DocumentationContext,
    SecurityContext, IntegrationContext, ArchitecturalContext, FunctionContext, ClassContext,
    CodeContext, ContextExtractionResult, DomainType, WorkflowPattern, ErrorHandlingStrategy,
    PerformancePattern
)
from ..models.config_models import Config


logger = logging.getLogger(__name__)


class ContextExtractionError(Exception):
    """Base exception for context extraction errors."""
    pass


class ContextExtractor:
    """Extracts business context and semantic meaning from Python code."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the context extractor.
        
        Args:
            config: Configuration object for extractor settings
        """
        self.config = config
        
        # Domain keywords for classification
        self.domain_keywords = {
            DomainType.WEB: ['flask', 'django', 'fastapi', 'request', 'response', 'http', 'url', 'route', 'endpoint'],
            DomainType.DATA: ['pandas', 'numpy', 'dataframe', 'csv', 'json', 'etl', 'transform', 'pipeline'],
            DomainType.ML: ['sklearn', 'tensorflow', 'pytorch', 'model', 'train', 'predict', 'feature', 'dataset'],
            DomainType.FINANCE: ['payment', 'transaction', 'account', 'balance', 'currency', 'price', 'order'],
            DomainType.GAMING: ['player', 'game', 'score', 'level', 'character', 'inventory', 'quest'],
            DomainType.SYSTEM: ['process', 'thread', 'memory', 'cpu', 'disk', 'network', 'system', 'os'],
            DomainType.API: ['api', 'endpoint', 'rest', 'graphql', 'service', 'client', 'server'],
            DomainType.CLI: ['argparse', 'click', 'command', 'argument', 'option', 'cli', 'terminal']
        }
        
        # Business entity patterns
        self.entity_patterns = [
            r'\\b(user|customer|client|account|profile)\\b',
            r'\\b(product|item|inventory|catalog)\\b',
            r'\\b(order|purchase|transaction|payment)\\b',
            r'\\b(document|file|record|data)\\b',
            r'\\b(message|notification|alert|email)\\b',
            r'\\b(report|analytics|metrics|stats)\\b',
            r'\\b(config|setting|preference|option)\\b'
        ]
        
        # Performance-critical patterns
        self.performance_patterns = {
            'loops': [r'for\\s+\\w+\\s+in', r'while\\s+'],
            'recursion': [r'def\\s+\\w+.*:\\s*.*\\1\\('],
            'io_operations': [r'open\\(', r'\\.read\\(', r'\\.write\\(', r'requests\\.'],
            'database': [r'\\.execute\\(', r'\\.query\\(', r'SELECT', r'INSERT', r'UPDATE'],
            'caching': [r'cache', r'memoize', r'@lru_cache'],
            'async': [r'async\\s+def', r'await\\s+', r'asyncio']
        }
    
    def extract_context(self, code: str, filename: str = "<string>") -> ContextExtractionResult:
        """
        Extract complete context from Python code.
        
        Args:
            code: Python source code
            filename: Name of the file (for error reporting)
            
        Returns:
            ContextExtractionResult with extracted context
        """
        start_time = time.time()
        
        try:
            logger.debug(f"Extracting context from {filename}")
            
            # Parse the code
            tree = ast.parse(code, filename=filename)
            
            # Extract different types of context
            business_context = self.analyze_business_logic(tree, code)
            error_handling_context = self.analyze_error_handling(tree, code)
            performance_context = self.analyze_performance(tree, code)
            documentation_context = self.analyze_documentation(tree, code)
            security_context = self.analyze_security_patterns(tree, code)
            integration_context = self.analyze_integrations(tree, code)
            
            # Extract function and class contexts
            function_contexts = self.extract_function_contexts(tree, code)
            class_contexts = self.extract_class_contexts(tree, code)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                business_context, error_handling_context, performance_context,
                documentation_context, security_context, integration_context
            )
            
            # Create complete context
            context = CodeContext(
                business_context=business_context,
                error_handling_context=error_handling_context,
                performance_context=performance_context,
                documentation_context=documentation_context,
                security_context=security_context,
                integration_context=integration_context,
                function_contexts=function_contexts,
                class_contexts=class_contexts,
                overall_quality_score=overall_confidence,
                maintainability_score=self._calculate_maintainability_score(documentation_context, function_contexts),
                testability_score=self._calculate_testability_score(function_contexts, error_handling_context)
            )
            
            return ContextExtractionResult(
                success=True,
                context=context,
                processing_time=time.time() - start_time,
                lines_analyzed=len(code.splitlines()),
                functions_analyzed=len(function_contexts),
                classes_analyzed=len(class_contexts)
            )
            
        except SyntaxError as e:
            logger.error(f"Syntax error in {filename}: {e}")
            return ContextExtractionResult(
                success=False,
                errors=[f"Syntax error: {e}"],
                processing_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error extracting context from {filename}: {e}")
            return ContextExtractionResult(
                success=False,
                errors=[f"Context extraction error: {e}"],
                processing_time=time.time() - start_time
            )
    
    def analyze_business_logic(self, tree: ast.AST, code: str) -> BusinessContext:
        """
        Analyze business logic and purpose from code structure and naming.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            BusinessContext with extracted business information
        """
        # Detect domain type
        domain_type = self._detect_domain_type(tree, code)
        
        # Extract business purpose from various sources
        business_purpose = self._extract_business_purpose(tree, code)
        
        # Identify workflow patterns
        workflow_patterns = self._identify_workflow_patterns(tree, code)
        
        # Extract data entities
        data_entities = self._extract_data_entities(tree, code)
        
        # Identify external integrations
        external_integrations = self._identify_external_integrations(tree, code)
        
        # Extract configuration patterns
        configuration_patterns = self._extract_configuration_patterns(tree, code)
        
        # Identify user interactions
        user_interactions = self._identify_user_interactions(tree, code)
        
        # Extract business rules
        business_rules = self._extract_business_rules(tree, code)
        
        # Identify data transformations
        data_transformations = self._identify_data_transformations(tree, code)
        
        # Calculate confidence score
        confidence_score = self._calculate_business_confidence(
            domain_type, business_purpose, workflow_patterns, data_entities
        )
        
        return BusinessContext(
            domain_type=domain_type,
            business_purpose=business_purpose,
            workflow_patterns=workflow_patterns,
            data_entities=data_entities,
            external_integrations=external_integrations,
            configuration_patterns=configuration_patterns,
            user_interactions=user_interactions,
            business_rules=business_rules,
            data_transformations=data_transformations,
            confidence_score=confidence_score
        )
    
    def analyze_error_handling(self, tree: ast.AST, code: str) -> ErrorHandlingContext:
        """
        Analyze error handling patterns and strategies.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            ErrorHandlingContext with error handling analysis
        """
        exception_patterns = []
        recovery_strategies = []
        validation_approaches = []
        logging_patterns = []
        defensive_patterns = []
        exception_hierarchy = []
        
        # Analyze try/except blocks
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Extract exception types
                for handler in node.handlers:
                    if handler.type:
                        if isinstance(handler.type, ast.Name):
                            exception_patterns.append(handler.type.id)
                        elif isinstance(handler.type, ast.Tuple):
                            for exc in handler.type.elts:
                                if isinstance(exc, ast.Name):
                                    exception_patterns.append(exc.id)
                
                # Analyze recovery strategies in except blocks
                for handler in node.handlers:
                    handler_code = ast.unparse(handler) if hasattr(ast, 'unparse') else str(handler)
                    
                    if 'retry' in handler_code.lower() or 'sleep' in handler_code.lower():
                        recovery_strategies.append(ErrorHandlingStrategy.RETRY_WITH_BACKOFF)
                    elif 'fallback' in handler_code.lower() or 'default' in handler_code.lower():
                        recovery_strategies.append(ErrorHandlingStrategy.FALLBACK)
                    elif 'log' in handler_code.lower():
                        recovery_strategies.append(ErrorHandlingStrategy.LOGGING_ONLY)
                    elif 'pass' in handler_code or 'continue' in handler_code:
                        recovery_strategies.append(ErrorHandlingStrategy.SILENT_FAILURE)
                    else:
                        recovery_strategies.append(ErrorHandlingStrategy.GRACEFUL_DEGRADATION)
        
        # Analyze validation patterns
        validation_approaches = self._extract_validation_patterns(tree, code)
        
        # Analyze logging patterns
        logging_patterns = self._extract_logging_patterns(tree, code)
        
        # Analyze defensive programming patterns
        defensive_patterns = self._extract_defensive_patterns(tree, code)
        
        # Determine error propagation strategy
        error_propagation = self._analyze_error_propagation(tree, code)
        
        # Calculate error handling coverage
        error_handling_coverage = self._calculate_error_handling_coverage(tree)
        
        return ErrorHandlingContext(
            exception_patterns=list(set(exception_patterns)),
            recovery_strategies=list(set(recovery_strategies)),
            validation_approaches=validation_approaches,
            logging_patterns=logging_patterns,
            defensive_patterns=defensive_patterns,
            error_propagation=error_propagation,
            exception_hierarchy=exception_hierarchy,
            error_handling_coverage=error_handling_coverage
        )
    
    def analyze_performance(self, tree: ast.AST, code: str) -> PerformanceContext:
        """
        Analyze performance considerations and optimization patterns.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            PerformanceContext with performance analysis
        """
        performance_hotspots = []
        memory_patterns = []
        io_operations = []
        optimization_patterns = []
        scalability_considerations = []
        resource_usage = {}
        complexity_hotspots = []
        concurrency_patterns = []
        
        # Identify performance hotspots
        performance_hotspots = self._identify_performance_hotspots(tree, code)
        
        # Analyze memory usage patterns
        memory_patterns = self._analyze_memory_patterns(tree, code)
        
        # Identify I/O operations
        io_operations = self._identify_io_operations(tree, code)
        
        # Detect optimization patterns
        optimization_patterns = self._detect_optimization_patterns(tree, code)
        
        # Analyze scalability considerations
        scalability_considerations = self._analyze_scalability(tree, code)
        
        # Analyze resource usage
        resource_usage = self._analyze_resource_usage(tree, code)
        
        # Identify complexity hotspots
        complexity_hotspots = self._identify_complexity_hotspots(tree, code)
        
        # Detect concurrency patterns
        concurrency_patterns = self._detect_concurrency_patterns(tree, code)
        
        return PerformanceContext(
            performance_hotspots=performance_hotspots,
            memory_patterns=memory_patterns,
            io_operations=io_operations,
            optimization_patterns=optimization_patterns,
            scalability_considerations=scalability_considerations,
            resource_usage=resource_usage,
            complexity_hotspots=complexity_hotspots,
            concurrency_patterns=concurrency_patterns
        )
    
    def analyze_documentation(self, tree: ast.AST, code: str) -> DocumentationContext:
        """
        Analyze documentation quality and extract context from docstrings and comments.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            DocumentationContext with documentation analysis
        """
        docstrings = []
        inline_comments = []
        todo_items = []
        fixme_items = []
        examples_in_docs = []
        api_documentation = []
        
        # Extract docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append(docstring)
                    
                    # Look for examples in docstrings
                    if 'example' in docstring.lower() or '>>>' in docstring:
                        examples_in_docs.append(f"{node.name if hasattr(node, 'name') else 'module'}: {docstring[:100]}...")
        
        # Extract inline comments
        lines = code.split('\\n')
        for i, line in enumerate(lines):
            if '#' in line:
                comment = line[line.index('#'):].strip()
                inline_comments.append(f"Line {i+1}: {comment}")
                
                # Look for TODO/FIXME items
                if 'todo' in comment.lower():
                    todo_items.append(f"Line {i+1}: {comment}")
                elif 'fixme' in comment.lower() or 'hack' in comment.lower():
                    fixme_items.append(f"Line {i+1}: {comment}")
        
        # Calculate docstring coverage
        total_functions_classes = len([n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))])
        docstring_coverage = len(docstrings) / max(total_functions_classes, 1)
        
        # Determine documentation style
        documentation_style = self._determine_documentation_style(docstrings)
        
        # Assess docstring quality
        docstring_quality = self._assess_docstring_quality(docstrings)
        
        # Calculate type hint coverage
        type_hint_coverage = self._calculate_type_hint_coverage(tree)
        
        # Extract API documentation
        api_documentation = self._extract_api_documentation(tree, docstrings)
        
        return DocumentationContext(
            docstring_coverage=docstring_coverage,
            docstring_quality=docstring_quality,
            documentation_style=documentation_style,
            inline_comments=inline_comments[:10],  # Limit to first 10
            todo_items=todo_items,
            fixme_items=fixme_items,
            examples_in_docs=examples_in_docs,
            type_hint_coverage=type_hint_coverage,
            api_documentation=api_documentation
        )
    
    def analyze_security_patterns(self, tree: ast.AST, code: str) -> SecurityContext:
        """
        Analyze security patterns and potential vulnerabilities.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            SecurityContext with security analysis
        """
        authentication_patterns = []
        authorization_patterns = []
        input_validation = []
        data_sanitization = []
        encryption_usage = []
        security_vulnerabilities = []
        secure_coding_practices = []
        compliance_patterns = []
        
        # Analyze authentication patterns
        authentication_patterns = self._detect_authentication_patterns(tree, code)
        
        # Analyze authorization patterns
        authorization_patterns = self._detect_authorization_patterns(tree, code)
        
        # Analyze input validation
        input_validation = self._analyze_input_validation(tree, code)
        
        # Analyze data sanitization
        data_sanitization = self._analyze_data_sanitization(tree, code)
        
        # Detect encryption usage
        encryption_usage = self._detect_encryption_usage(tree, code)
        
        # Identify potential security vulnerabilities
        security_vulnerabilities = self._identify_security_vulnerabilities(tree, code)
        
        # Detect secure coding practices
        secure_coding_practices = self._detect_secure_coding_practices(tree, code)
        
        # Analyze compliance patterns
        compliance_patterns = self._analyze_compliance_patterns(tree, code)
        
        return SecurityContext(
            authentication_patterns=authentication_patterns,
            authorization_patterns=authorization_patterns,
            input_validation=input_validation,
            data_sanitization=data_sanitization,
            encryption_usage=encryption_usage,
            security_vulnerabilities=security_vulnerabilities,
            secure_coding_practices=secure_coding_practices,
            compliance_patterns=compliance_patterns
        )
    
    def analyze_integrations(self, tree: ast.AST, code: str) -> IntegrationContext:
        """
        Analyze external integrations and dependencies.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            IntegrationContext with integration analysis
        """
        database_integrations = []
        api_integrations = []
        message_queue_patterns = []
        file_system_operations = []
        network_operations = []
        third_party_libraries = []
        configuration_sources = []
        deployment_patterns = []
        
        # Analyze imports for third-party libraries
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        third_party_libraries.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    third_party_libraries.append(node.module)
        
        # Analyze database integrations
        database_integrations = self._analyze_database_integrations(tree, code, third_party_libraries)
        
        # Analyze API integrations
        api_integrations = self._analyze_api_integrations(tree, code, third_party_libraries)
        
        # Analyze message queue patterns
        message_queue_patterns = self._analyze_message_queue_patterns(tree, code, third_party_libraries)
        
        # Analyze file system operations
        file_system_operations = self._analyze_file_system_operations(tree, code)
        
        # Analyze network operations
        network_operations = self._analyze_network_operations(tree, code)
        
        # Analyze configuration sources
        configuration_sources = self._analyze_configuration_sources(tree, code)
        
        # Analyze deployment patterns
        deployment_patterns = self._analyze_deployment_patterns(tree, code)
        
        return IntegrationContext(
            database_integrations=database_integrations,
            api_integrations=api_integrations,
            message_queue_patterns=message_queue_patterns,
            file_system_operations=file_system_operations,
            network_operations=network_operations,
            third_party_libraries=list(set(third_party_libraries))[:20],  # Limit to 20
            configuration_sources=configuration_sources,
            deployment_patterns=deployment_patterns
        )
    
    def extract_function_contexts(self, tree: ast.AST, code: str) -> List[FunctionContext]:
        """
        Extract context for individual functions.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            List of FunctionContext objects
        """
        function_contexts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                context = self._analyze_function_context(node, code)
                function_contexts.append(context)
        
        return function_contexts
    
    def extract_class_contexts(self, tree: ast.AST, code: str) -> List[ClassContext]:
        """
        Extract context for individual classes.
        
        Args:
            tree: AST of the code
            code: Raw source code
            
        Returns:
            List of ClassContext objects
        """
        class_contexts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                context = self._analyze_class_context(node, code)
                class_contexts.append(context)
        
        return class_contexts    
 
    # Helper Methods for Business Logic Analysis
    
    def _detect_domain_type(self, tree: ast.AST, code: str) -> DomainType:
        """Detect the domain type based on imports, function names, and keywords."""
        code_lower = code.lower()
        
        # Count domain-specific keywords
        domain_scores = defaultdict(int)
        
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                domain_scores[domain] += code_lower.count(keyword)
        
        # Also check imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.lower()
                        for domain, keywords in self.domain_keywords.items():
                            if any(keyword in module_name for keyword in keywords):
                                domain_scores[domain] += 2
                elif isinstance(node, ast.ImportFrom) and node.module:
                    module_name = node.module.lower()
                    for domain, keywords in self.domain_keywords.items():
                        if any(keyword in module_name for keyword in keywords):
                            domain_scores[domain] += 2
        
        # Return the domain with the highest score
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        return DomainType.UNKNOWN
    
    def _extract_business_purpose(self, tree: ast.AST, code: str) -> str:
        """Extract business purpose from module docstring, class names, and function names."""
        # Try module docstring first
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            # Extract first sentence as purpose
            sentences = module_docstring.split('.')
            if sentences:
                return sentences[0].strip()
        
        # Analyze class and function names for business purpose
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                names.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                names.append(node.name)
        
        # Look for common business patterns in names
        if names:
            name_text = ' '.join(names).lower()
            if 'user' in name_text or 'customer' in name_text:
                return "User management and customer operations"
            elif 'order' in name_text or 'payment' in name_text:
                return "Order processing and payment handling"
            elif 'data' in name_text or 'process' in name_text:
                return "Data processing and transformation"
            elif 'api' in name_text or 'service' in name_text:
                return "API service and endpoint management"
            elif 'auth' in name_text or 'login' in name_text:
                return "Authentication and authorization system"
        
        return "General purpose application logic"
    
    def _identify_workflow_patterns(self, tree: ast.AST, code: str) -> List[WorkflowPattern]:
        """Identify workflow patterns from code structure."""
        patterns = []
        code_lower = code.lower()
        
        # Check for CRUD operations
        crud_keywords = ['create', 'read', 'update', 'delete', 'get', 'post', 'put', 'patch']
        if sum(1 for keyword in crud_keywords if keyword in code_lower) >= 3:
            patterns.append(WorkflowPattern.CRUD)
        
        # Check for ETL patterns
        etl_keywords = ['extract', 'transform', 'load', 'pipeline', 'process']
        if sum(1 for keyword in etl_keywords if keyword in code_lower) >= 2:
            patterns.append(WorkflowPattern.ETL)
        
        # Check for MVC patterns
        mvc_keywords = ['model', 'view', 'controller', 'template', 'render']
        if sum(1 for keyword in mvc_keywords if keyword in code_lower) >= 2:
            patterns.append(WorkflowPattern.MVC)
        
        # Check for event-driven patterns
        event_keywords = ['event', 'listener', 'handler', 'callback', 'trigger']
        if sum(1 for keyword in event_keywords if keyword in code_lower) >= 2:
            patterns.append(WorkflowPattern.EVENT_DRIVEN)
        
        return patterns
    
    # Placeholder methods for all the helper functions
    # These would be implemented with actual analysis logic
    
    def _extract_data_entities(self, tree: ast.AST, code: str) -> List[str]:
        """Extract data entities from class names and variable names."""
        entities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                entities.append(node.name)
        return entities
    
    def _identify_external_integrations(self, tree: ast.AST, code: str) -> List[str]:
        """Identify external service integrations."""
        integrations = []
        # Simple implementation - check for common integration libraries
        if 'requests' in code.lower():
            integrations.append("HTTP API integration")
        if 'boto3' in code.lower():
            integrations.append("AWS integration")
        return integrations
    
    def _extract_configuration_patterns(self, tree: ast.AST, code: str) -> List[str]:
        """Extract configuration management patterns."""
        patterns = []
        if 'os.environ' in code or 'getenv' in code:
            patterns.append("Environment variables")
        if 'config' in code.lower():
            patterns.append("Configuration files")
        return patterns
    
    def _identify_user_interactions(self, tree: ast.AST, code: str) -> List[str]:
        """Identify user interaction patterns."""
        interactions = []
        if 'input(' in code:
            interactions.append("Console input")
        if 'print(' in code:
            interactions.append("Console output")
        return interactions
    
    def _extract_business_rules(self, tree: ast.AST, code: str) -> List[str]:
        """Extract business rules from conditional logic."""
        rules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Simple extraction of business rules
                rules.append("Conditional business logic detected")
                break
        return rules
    
    def _identify_data_transformations(self, tree: ast.AST, code: str) -> List[str]:
        """Identify data transformation patterns."""
        transformations = []
        if any(keyword in code.lower() for keyword in ['map', 'filter', 'transform']):
            transformations.append("Data transformation operations")
        return transformations
    
    def _calculate_business_confidence(self, domain_type: DomainType, business_purpose: str, 
                                     workflow_patterns: List[WorkflowPattern], data_entities: List[str]) -> float:
        """Calculate confidence score for business context analysis."""
        score = 0.0
        if domain_type != DomainType.UNKNOWN:
            score += 0.3
        if business_purpose != "General purpose application logic":
            score += 0.3
        score += min(0.2, len(workflow_patterns) * 0.1)
        score += min(0.2, len(data_entities) * 0.05)
        return min(1.0, score)
    
    # Placeholder implementations for all other helper methods
    def _extract_validation_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Input validation detected"] if 'validate' in code.lower() else []
    
    def _extract_logging_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Logging detected"] if any(x in code.lower() for x in ['log', 'print']) else []
    
    def _extract_defensive_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Defensive programming detected"] if 'isinstance' in code else []
    
    def _analyze_error_propagation(self, tree: ast.AST, code: str) -> str:
        return "explicit_raise" if 'raise' in code else "unknown"
    
    def _calculate_error_handling_coverage(self, tree: ast.AST) -> float:
        try_blocks = len([n for n in ast.walk(tree) if isinstance(n, ast.Try)])
        functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        return try_blocks / max(functions, 1)
    
    def _identify_performance_hotspots(self, tree: ast.AST, code: str) -> List[str]:
        hotspots = []
        nested_loops = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                nested_loops += 1
        if nested_loops > 2:
            hotspots.append("Nested loops detected")
        return hotspots
    
    def _analyze_memory_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Large data structures"] if any(x in code for x in ['list(', 'dict(']) else []
    
    def _identify_io_operations(self, tree: ast.AST, code: str) -> List[str]:
        operations = []
        if 'open(' in code:
            operations.append("File I/O")
        if 'requests.' in code:
            operations.append("Network I/O")
        return operations
    
    def _detect_optimization_patterns(self, tree: ast.AST, code: str) -> List[PerformancePattern]:
        patterns = []
        if 'cache' in code.lower():
            patterns.append(PerformancePattern.CACHING)
        if 'async' in code.lower():
            patterns.append(PerformancePattern.ASYNC_PROCESSING)
        return patterns
    
    def _analyze_scalability(self, tree: ast.AST, code: str) -> List[str]:
        return ["Scalability considerations needed"] if len(code) > 1000 else []
    
    def _analyze_resource_usage(self, tree: ast.AST, code: str) -> Dict[str, str]:
        return {"memory": "moderate", "cpu": "low"}
    
    def _identify_complexity_hotspots(self, tree: ast.AST, code: str) -> List[str]:
        return ["High complexity function"] if len([n for n in ast.walk(tree) if isinstance(n, ast.If)]) > 5 else []
    
    def _detect_concurrency_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Async/await pattern"] if 'async' in code else []
    
    def _determine_documentation_style(self, docstrings: List[str]) -> str:
        if not docstrings:
            return "none"
        
        # Check all docstrings for style indicators
        all_docstrings = ' '.join(docstrings).lower()
        
        if 'args:' in all_docstrings and 'returns:' in all_docstrings:
            return "google"
        elif 'parameters' in all_docstrings and '----------' in all_docstrings:
            return "numpy"
        elif ':param' in all_docstrings and ':return' in all_docstrings:
            return "sphinx"
        elif any(keyword in all_docstrings for keyword in ['args:', 'returns:', 'raises:']):
            return "google"
        return "custom"
    
    def _assess_docstring_quality(self, docstrings: List[str]) -> str:
        if not docstrings:
            return "none"
        avg_length = sum(len(d) for d in docstrings) / len(docstrings)
        if avg_length > 200:
            return "excellent"
        elif avg_length > 100:
            return "good"
        elif avg_length > 50:
            return "fair"
        return "poor"
    
    def _calculate_type_hint_coverage(self, tree: ast.AST) -> float:
        functions_with_hints = 0
        total_functions = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    functions_with_hints += 1
        return functions_with_hints / max(total_functions, 1)
    
    def _extract_api_documentation(self, tree: ast.AST, docstrings: List[str]) -> List[str]:
        return ["API documentation found"] if any('api' in d.lower() for d in docstrings) else []
    
    # Security analysis helper methods
    def _detect_authentication_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Authentication logic"] if any(x in code.lower() for x in ['auth', 'login', 'password']) else []
    
    def _detect_authorization_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Authorization logic"] if any(x in code.lower() for x in ['permission', 'role', 'access']) else []
    
    def _analyze_input_validation(self, tree: ast.AST, code: str) -> List[str]:
        return ["Input validation"] if 'validate' in code.lower() else []
    
    def _analyze_data_sanitization(self, tree: ast.AST, code: str) -> List[str]:
        return ["Data sanitization"] if 'sanitize' in code.lower() else []
    
    def _detect_encryption_usage(self, tree: ast.AST, code: str) -> List[str]:
        return ["Encryption usage"] if any(x in code.lower() for x in ['encrypt', 'hash', 'crypto']) else []
    
    def _identify_security_vulnerabilities(self, tree: ast.AST, code: str) -> List[str]:
        vulnerabilities = []
        if 'eval(' in code:
            vulnerabilities.append("Potential code injection via eval()")
        return vulnerabilities
    
    def _detect_secure_coding_practices(self, tree: ast.AST, code: str) -> List[str]:
        return ["Secure coding practices"] if 'secure' in code.lower() else []
    
    def _analyze_compliance_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Compliance patterns"] if 'compliance' in code.lower() else []
    
    # Integration analysis helper methods
    def _analyze_database_integrations(self, tree: ast.AST, code: str, libraries: List[str]) -> List[str]:
        db_integrations = []
        db_libraries = ['sqlite3', 'psycopg2', 'pymongo', 'sqlalchemy']
        for lib in libraries:
            if any(db_lib in lib.lower() for db_lib in db_libraries):
                db_integrations.append(f"Database integration: {lib}")
        return db_integrations
    
    def _analyze_api_integrations(self, tree: ast.AST, code: str, libraries: List[str]) -> List[str]:
        api_integrations = []
        if 'requests' in libraries:
            api_integrations.append("HTTP API integration")
        return api_integrations
    
    def _analyze_message_queue_patterns(self, tree: ast.AST, code: str, libraries: List[str]) -> List[str]:
        return ["Message queue integration"] if any('queue' in lib.lower() for lib in libraries) else []
    
    def _analyze_file_system_operations(self, tree: ast.AST, code: str) -> List[str]:
        return ["File system operations"] if 'open(' in code else []
    
    def _analyze_network_operations(self, tree: ast.AST, code: str) -> List[str]:
        return ["Network operations"] if 'socket' in code.lower() else []
    
    def _analyze_configuration_sources(self, tree: ast.AST, code: str) -> List[str]:
        return ["Configuration management"] if 'config' in code.lower() else []
    
    def _analyze_deployment_patterns(self, tree: ast.AST, code: str) -> List[str]:
        return ["Deployment patterns"] if 'deploy' in code.lower() else []
    
    def _analyze_function_context(self, node: ast.FunctionDef, code: str) -> FunctionContext:
        """Analyze context for a single function."""
        function_name = node.name
        
        # Extract business purpose from docstring or name
        docstring = ast.get_docstring(node)
        if docstring:
            business_purpose = docstring.split('.')[0].strip()
        else:
            business_purpose = f"Function: {function_name}"
        
        # Extract type information
        input_types = []
        output_types = []
        
        for arg in node.args.args:
            if arg.annotation:
                input_types.append(ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation))
        
        if node.returns:
            output_types.append(ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns))
        
        # Analyze complexity
        complexity_indicators = len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While))])
        if complexity_indicators > 10:
            complexity_level = "very_high"
        elif complexity_indicators > 5:
            complexity_level = "high"
        elif complexity_indicators > 2:
            complexity_level = "medium"
        else:
            complexity_level = "low"
        
        return FunctionContext(
            function_name=function_name,
            business_purpose=business_purpose,
            input_types=input_types,
            output_types=output_types,
            complexity_level=complexity_level
        )
    
    def _analyze_class_context(self, node: ast.ClassDef, code: str) -> ClassContext:
        """Analyze context for a single class."""
        class_name = node.name
        
        # Extract business purpose from docstring or name
        docstring = ast.get_docstring(node)
        if docstring:
            business_purpose = docstring.split('.')[0].strip()
        else:
            business_purpose = f"Class: {class_name}"
        
        # Analyze inheritance
        inheritance_hierarchy = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                inheritance_hierarchy.append(base.id)
        
        # Analyze methods
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        responsibilities = [f"Method: {method}" for method in methods[:5]]  # Limit to 5
        
        return ClassContext(
            class_name=class_name,
            business_purpose=business_purpose,
            inheritance_hierarchy=inheritance_hierarchy,
            responsibilities=responsibilities
        )
    
    def _calculate_overall_confidence(self, business_context: BusinessContext, 
                                    error_handling_context: ErrorHandlingContext,
                                    performance_context: PerformanceContext,
                                    documentation_context: DocumentationContext,
                                    security_context: SecurityContext,
                                    integration_context: IntegrationContext) -> float:
        """Calculate overall confidence score for context extraction."""
        scores = [
            business_context.confidence_score,
            error_handling_context.error_handling_coverage,
            len(performance_context.optimization_patterns) / 5,  # Normalize to 0-1
            documentation_context.docstring_coverage,
            len(security_context.authentication_patterns) / 3,  # Normalize to 0-1
            len(integration_context.third_party_libraries) / 10  # Normalize to 0-1
        ]
        
        return sum(scores) / len(scores)
    
    def _calculate_maintainability_score(self, documentation_context: DocumentationContext, 
                                       function_contexts: List[FunctionContext]) -> float:
        """Calculate maintainability score."""
        doc_score = documentation_context.docstring_coverage
        complexity_score = 1.0 - (sum(1 for f in function_contexts if f.complexity_level in ["high", "very_high"]) / max(len(function_contexts), 1))
        return (doc_score + complexity_score) / 2
    
    def _calculate_testability_score(self, function_contexts: List[FunctionContext], 
                                   error_handling_context: ErrorHandlingContext) -> float:
        """Calculate testability score."""
        # Simple heuristic: functions with clear inputs/outputs and error handling are more testable
        testable_functions = sum(1 for f in function_contexts if f.input_types and f.output_types)
        function_score = testable_functions / max(len(function_contexts), 1)
        error_score = error_handling_context.error_handling_coverage
        return (function_score + error_score) / 2