"""
Pattern detection and algorithm identification for Python code.
"""

import ast
import logging
import re
from typing import List, Optional, Set, Dict, Any
from pathlib import Path

from ..models.analysis_models import PatternInfo, AlgorithmInfo
from ..models.config_models import Config


logger = logging.getLogger(__name__)


class PatternDetectionError(Exception):
    """Base exception for pattern detection errors."""
    pass


class PatternDetector:
    """Detector for design patterns, algorithms, and Python idioms."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the pattern detector.
        
        Args:
            config: Configuration object for detector settings
        """
        self.config = config
        
        # Pattern detection confidence thresholds
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
    
    def detect_patterns(self, code: str, filename: str = "<string>") -> List[PatternInfo]:
        """
        Detect design patterns in code.
        
        Args:
            code: Python source code
            filename: Name of the file (for error reporting)
            
        Returns:
            List of detected design patterns
        """
        logger.debug(f"Detecting patterns in {filename}")
        
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            raise PatternDetectionError(f"Syntax error in {filename}: {e}")
        
        patterns = []
        
        # Detect design patterns
        patterns.extend(self.detect_singleton_pattern(tree))
        patterns.extend(self.detect_factory_pattern(tree))
        patterns.extend(self.detect_observer_pattern(tree))
        patterns.extend(self.detect_decorator_pattern(tree))
        patterns.extend(self.detect_strategy_pattern(tree))
        patterns.extend(self.detect_builder_pattern(tree))
        patterns.extend(self.detect_command_pattern(tree))
        patterns.extend(self.detect_template_method_pattern(tree))
        
        return patterns
    
    def detect_algorithms(self, code: str, filename: str = "<string>") -> List[AlgorithmInfo]:
        """
        Detect algorithms in code.
        
        Args:
            code: Python source code
            filename: Name of the file (for error reporting)
            
        Returns:
            List of detected algorithms
        """
        logger.debug(f"Detecting algorithms in {filename}")
        
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            raise PatternDetectionError(f"Syntax error in {filename}: {e}")
        
        algorithms = []
        
        # Detect algorithms
        algorithms.extend(self.detect_sorting_algorithms(tree))
        algorithms.extend(self.detect_searching_algorithms(tree))
        algorithms.extend(self.detect_data_processing_patterns(tree))
        
        return algorithms
    
    def detect_python_idioms(self, code: str, filename: str = "<string>") -> List[PatternInfo]:
        """
        Detect Python idioms and best practices.
        
        Args:
            code: Python source code
            filename: Name of the file (for error reporting)
            
        Returns:
            List of detected Python idioms
        """
        logger.debug(f"Detecting Python idioms in {filename}")
        
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            raise PatternDetectionError(f"Syntax error in {filename}: {e}")
        
        idioms = []
        
        # Detect Python idioms
        idioms.extend(self.detect_list_comprehensions(tree))
        idioms.extend(self.detect_context_managers(tree))
        idioms.extend(self.detect_generators(tree))
        idioms.extend(self.detect_decorators(tree))
        idioms.extend(self.detect_duck_typing(tree))
        idioms.extend(self.detect_eafp_pattern(tree))
        idioms.extend(self.detect_property_usage(tree))
        
        return idioms
    
    # Design Pattern Detection Methods
    
    def detect_singleton_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Singleton pattern by looking for:
        - Class with __new__ method that controls instance creation
        - Class variable to store single instance
        - Logic to return existing instance
        """
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_new_method = False
                has_instance_var = False
                has_singleton_logic = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__new__":
                        has_new_method = True
                        has_singleton_logic = self._has_singleton_logic(item)
                    
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if (isinstance(target, ast.Name) and 
                                ('instance' in target.id.lower() or 
                                 target.id.startswith('_'))):
                                has_instance_var = True
                
                if has_new_method and has_singleton_logic:
                    confidence = 0.9 if has_instance_var else 0.7
                    patterns.append(PatternInfo(
                        pattern_name="Singleton",
                        confidence=confidence,
                        description=f"Class {node.name} implements Singleton pattern",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_factory_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Factory pattern by looking for:
        - Methods that create and return objects based on parameters
        - Class methods or static methods that act as factories
        - Functions with names like create_*, make_*, build_*
        """
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for factory method names
                factory_keywords = ['create', 'make', 'build', 'get', 'factory', 'new']
                has_factory_name = any(keyword in node.name.lower() for keyword in factory_keywords)
                
                if has_factory_name and self._has_conditional_object_creation(node):
                    patterns.append(PatternInfo(
                        pattern_name="Factory Method",
                        confidence=0.8,
                        description=f"Function {node.name} appears to be a factory method",
                        line_numbers=[node.lineno]
                    ))
                
                # Check for static/class methods that create objects
                elif self._is_static_or_class_method(node) and self._creates_objects(node):
                    patterns.append(PatternInfo(
                        pattern_name="Factory Method",
                        confidence=0.7,
                        description=f"Method {node.name} acts as a factory method",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_observer_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Observer pattern by looking for:
        - Classes with observer/listener lists
        - Methods like add_observer, remove_observer, notify
        - Event handling mechanisms
        """
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                observer_methods = []
                has_observer_list = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_name = item.name.lower()
                        observer_keywords = ['observer', 'listener', 'notify', 'subscribe', 
                                           'unsubscribe', 'attach', 'detach', 'update']
                        if any(keyword in method_name for keyword in observer_keywords):
                            observer_methods.append(item.name)
                        
                        # Also check for observer list assignments within methods (like __init__)
                        for subnode in ast.walk(item):
                            if isinstance(subnode, ast.Assign):
                                for target in subnode.targets:
                                    if (isinstance(target, ast.Attribute) and
                                        any(keyword in target.attr.lower() for keyword in 
                                            ['observer', 'listener', 'subscriber', 'callback'])):
                                        has_observer_list = True
                    
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if (isinstance(target, ast.Name) and
                                any(keyword in target.id.lower() for keyword in 
                                    ['observer', 'listener', 'subscriber', 'callback'])):
                                has_observer_list = True
                
                if len(observer_methods) >= 2 and has_observer_list:
                    patterns.append(PatternInfo(
                        pattern_name="Observer",
                        confidence=0.8,
                        description=f"Class {node.name} implements Observer pattern",
                        line_numbers=[node.lineno]
                    ))
                elif len(observer_methods) >= 3:  # Strong indication even without explicit list
                    patterns.append(PatternInfo(
                        pattern_name="Observer",
                        confidence=0.6,
                        description=f"Class {node.name} likely implements Observer pattern",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_decorator_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Decorator pattern (not Python decorators, but the design pattern).
        """
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_component_ref = False
                has_delegation = False
                
                # Look for component reference and delegation
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if (isinstance(target, ast.Name) and 
                                'component' in target.id.lower()):
                                has_component_ref = True
                    
                    elif isinstance(item, ast.FunctionDef):
                        # Look for method delegation
                        if self._has_method_delegation(item):
                            has_delegation = True
                
                if has_component_ref and has_delegation:
                    patterns.append(PatternInfo(
                        pattern_name="Decorator Pattern",
                        confidence=0.7,
                        description=f"Class {node.name} implements Decorator pattern",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_strategy_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Strategy pattern by looking for:
        - Classes with interchangeable algorithm implementations
        - Strategy interface or abstract base class
        - Context class that uses strategies
        """
        patterns = []
        
        strategy_classes = []
        context_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for strategy classes (similar interface)
                if self._looks_like_strategy_class(node):
                    strategy_classes.append(node)
                
                # Look for context classes (uses strategies)
                elif self._looks_like_context_class(node):
                    context_classes.append(node)
        
        # If we have multiple strategy classes and a context, it's likely Strategy pattern
        if len(strategy_classes) >= 2 and context_classes:
            for context in context_classes:
                patterns.append(PatternInfo(
                    pattern_name="Strategy",
                    confidence=0.8,
                    description=f"Strategy pattern with context class {context.name}",
                    line_numbers=[context.lineno]
                ))
        
        return patterns
    
    def detect_builder_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Builder pattern by looking for:
        - Classes with fluent interface (method chaining)
        - Methods that return self
        - Final build() method
        """
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                chaining_methods = 0
                has_build_method = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.lower() in ['build', 'create', 'construct']:
                            has_build_method = True
                        elif self._returns_self(item):
                            chaining_methods += 1
                
                if chaining_methods >= 2 and has_build_method:
                    patterns.append(PatternInfo(
                        pattern_name="Builder",
                        confidence=0.8,
                        description=f"Class {node.name} implements Builder pattern",
                        line_numbers=[node.lineno]
                    ))
                elif chaining_methods >= 3:  # Strong indication even without explicit build
                    patterns.append(PatternInfo(
                        pattern_name="Builder",
                        confidence=0.6,
                        description=f"Class {node.name} likely implements Builder pattern",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_command_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Command pattern by looking for:
        - Classes with execute() method
        - Command interface or base class
        - Invoker that calls execute()
        """
        patterns = []
        
        command_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_execute = False
                has_undo = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.lower() in ['execute', 'run', 'do', 'call']:
                            has_execute = True
                        elif item.name.lower() in ['undo', 'reverse', 'rollback']:
                            has_undo = True
                
                if has_execute:
                    confidence = 0.8 if has_undo else 0.6
                    command_classes.append((node, confidence))
        
        # If we have multiple command classes, it's likely Command pattern
        if len(command_classes) >= 2:
            for node, confidence in command_classes:
                patterns.append(PatternInfo(
                    pattern_name="Command",
                    confidence=confidence,
                    description=f"Class {node.name} implements Command pattern",
                    line_numbers=[node.lineno]
                ))
        
        return patterns
    
    def detect_template_method_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """
        Detect Template Method pattern by looking for:
        - Abstract base class with template method
        - Template method calling abstract methods
        - Concrete classes implementing abstract methods
        """
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_template_method = False
                has_abstract_methods = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Look for methods that call other methods (template)
                        if self._calls_multiple_methods(item):
                            has_template_method = True
                        
                        # Look for abstract methods (raise NotImplementedError)
                        if self._is_abstract_method(item):
                            has_abstract_methods = True
                
                if has_template_method and has_abstract_methods:
                    patterns.append(PatternInfo(
                        pattern_name="Template Method",
                        confidence=0.7,
                        description=f"Class {node.name} implements Template Method pattern",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    # Algorithm Detection Methods
    
    def detect_sorting_algorithms(self, tree: ast.AST) -> List[AlgorithmInfo]:
        """Detect sorting algorithms by analyzing loop patterns and comparisons."""
        algorithms = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Bubble Sort: nested loops with adjacent element swapping
                if self._has_bubble_sort_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Bubble Sort",
                        algorithm_type="sorting",
                        confidence=0.9,
                        description="Bubble sort implementation with nested loops",
                        line_numbers=[node.lineno],
                        time_complexity="O(n²)",
                        space_complexity="O(1)",
                        implementation_notes=["Uses nested loops", "Swaps adjacent elements"]
                    ))
                
                # Quick Sort: recursive partitioning
                elif self._has_quicksort_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Quick Sort",
                        algorithm_type="sorting",
                        confidence=0.8,
                        description="Quick sort implementation with partitioning",
                        line_numbers=[node.lineno],
                        time_complexity="O(n log n) average, O(n²) worst",
                        space_complexity="O(log n)",
                        implementation_notes=["Divide and conquer", "In-place partitioning"]
                    ))
                
                # Merge Sort: divide and conquer with merging
                elif self._has_mergesort_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Merge Sort",
                        algorithm_type="sorting",
                        confidence=0.8,
                        description="Merge sort implementation with divide and conquer",
                        line_numbers=[node.lineno],
                        time_complexity="O(n log n)",
                        space_complexity="O(n)",
                        implementation_notes=["Stable sort", "Requires additional space"]
                    ))
                
                # Insertion Sort: inserting elements in sorted position
                elif self._has_insertion_sort_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Insertion Sort",
                        algorithm_type="sorting",
                        confidence=0.8,
                        description="Insertion sort implementation",
                        line_numbers=[node.lineno],
                        time_complexity="O(n²) worst, O(n) best",
                        space_complexity="O(1)",
                        implementation_notes=["Efficient for small datasets", "Adaptive"]
                    ))
        
        return algorithms
    
    def detect_searching_algorithms(self, tree: ast.AST) -> List[AlgorithmInfo]:
        """Detect searching algorithms by analyzing search patterns."""
        algorithms = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Binary Search: divide and conquer on sorted data
                if self._has_binary_search_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Binary Search",
                        algorithm_type="searching",
                        confidence=0.9,
                        description="Binary search implementation",
                        line_numbers=[node.lineno],
                        time_complexity="O(log n)",
                        space_complexity="O(1)",
                        implementation_notes=["Requires sorted data", "Divide and conquer"]
                    ))
                
                # Linear Search: sequential scanning
                elif self._has_linear_search_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Linear Search",
                        algorithm_type="searching",
                        confidence=0.8,
                        description="Linear search implementation",
                        line_numbers=[node.lineno],
                        time_complexity="O(n)",
                        space_complexity="O(1)",
                        implementation_notes=["Sequential scan", "Works on unsorted data"]
                    ))
        
        return algorithms
    
    def detect_data_processing_patterns(self, tree: ast.AST) -> List[AlgorithmInfo]:
        """Detect data processing patterns and algorithms."""
        algorithms = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Map-Reduce pattern
                if self._has_map_reduce_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Map-Reduce",
                        algorithm_type="data_processing",
                        confidence=0.7,
                        description="Map-reduce data processing pattern",
                        line_numbers=[node.lineno],
                        time_complexity="O(n)",
                        space_complexity="O(n)",
                        implementation_notes=["Functional programming style", "Parallel processing friendly"]
                    ))
                
                # Filter-Transform pattern
                elif self._has_filter_transform_pattern(node):
                    algorithms.append(AlgorithmInfo(
                        algorithm_name="Filter-Transform",
                        algorithm_type="data_processing",
                        confidence=0.7,
                        description="Filter and transform data processing pattern",
                        line_numbers=[node.lineno],
                        time_complexity="O(n)",
                        space_complexity="O(n)",
                        implementation_notes=["Pipeline processing", "Functional style"]
                    ))
        
        return algorithms
    
    # Python Idiom Detection Methods
    
    def detect_list_comprehensions(self, tree: ast.AST) -> List[PatternInfo]:
        """Detect list comprehensions and their complexity."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                complexity = self._analyze_comprehension_complexity(node)
                patterns.append(PatternInfo(
                    pattern_name="List Comprehension",
                    confidence=1.0,
                    description=f"List comprehension ({complexity})",
                    line_numbers=[node.lineno]
                ))
            
            elif isinstance(node, ast.DictComp):
                complexity = self._analyze_comprehension_complexity(node)
                patterns.append(PatternInfo(
                    pattern_name="Dict Comprehension",
                    confidence=1.0,
                    description=f"Dictionary comprehension ({complexity})",
                    line_numbers=[node.lineno]
                ))
            
            elif isinstance(node, ast.SetComp):
                complexity = self._analyze_comprehension_complexity(node)
                patterns.append(PatternInfo(
                    pattern_name="Set Comprehension",
                    confidence=1.0,
                    description=f"Set comprehension ({complexity})",
                    line_numbers=[node.lineno]
                ))
        
        return patterns
    
    def detect_context_managers(self, tree: ast.AST) -> List[PatternInfo]:
        """Detect context manager usage and custom implementations."""
        patterns = []
        
        for node in ast.walk(tree):
            # with statements
            if isinstance(node, ast.With):
                context_type = "single" if len(node.items) == 1 else "multiple"
                patterns.append(PatternInfo(
                    pattern_name="Context Manager Usage",
                    confidence=1.0,
                    description=f"Using context manager with 'with' statement ({context_type})",
                    line_numbers=[node.lineno]
                ))
            
            # Custom context manager classes
            elif isinstance(node, ast.ClassDef):
                has_enter = False
                has_exit = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name == "__enter__":
                            has_enter = True
                        elif item.name == "__exit__":
                            has_exit = True
                
                if has_enter and has_exit:
                    patterns.append(PatternInfo(
                        pattern_name="Custom Context Manager",
                        confidence=0.9,
                        description=f"Class {node.name} implements context manager protocol",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_generators(self, tree: ast.AST) -> List[PatternInfo]:
        """Detect generator functions and expressions."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for yield statements
                has_yield = any(isinstance(n, (ast.Yield, ast.YieldFrom)) 
                              for n in ast.walk(node))
                
                if has_yield:
                    patterns.append(PatternInfo(
                        pattern_name="Generator Function",
                        confidence=1.0,
                        description=f"Function {node.name} is a generator",
                        line_numbers=[node.lineno]
                    ))
            
            elif isinstance(node, ast.GeneratorExp):
                patterns.append(PatternInfo(
                    pattern_name="Generator Expression",
                    confidence=1.0,
                    description="Generator expression for lazy evaluation",
                    line_numbers=[node.lineno]
                ))
        
        return patterns
    
    def detect_decorators(self, tree: ast.AST) -> List[PatternInfo]:
        """Detect decorator usage and custom decorator implementations."""
        patterns = []
        
        for node in ast.walk(tree):
            # Detect decorator usage
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.decorator_list:
                decorator_names = []
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorator_names.append(decorator.id)
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        decorator_names.append(decorator.func.id)
                
                patterns.append(PatternInfo(
                    pattern_name="Decorator Usage",
                    confidence=1.0,
                    description=f"Using decorators: {', '.join(decorator_names)}",
                    line_numbers=[node.lineno]
                ))
            
            # Detect custom decorator implementations
            elif isinstance(node, ast.FunctionDef):
                if self._is_decorator_function(node):
                    patterns.append(PatternInfo(
                        pattern_name="Custom Decorator",
                        confidence=0.8,
                        description=f"Function {node.name} appears to be a decorator",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_duck_typing(self, tree: ast.AST) -> List[PatternInfo]:
        """Detect duck typing patterns."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for hasattr() calls
                has_hasattr = any(
                    isinstance(n, ast.Call) and 
                    isinstance(n.func, ast.Name) and 
                    n.func.id == 'hasattr'
                    for n in ast.walk(node)
                )
                
                # Look for try/except with AttributeError
                has_attribute_error_handling = any(
                    isinstance(n, ast.ExceptHandler) and
                    isinstance(n.type, ast.Name) and
                    n.type.id == 'AttributeError'
                    for n in ast.walk(node)
                )
                
                if has_hasattr or has_attribute_error_handling:
                    patterns.append(PatternInfo(
                        pattern_name="Duck Typing",
                        confidence=0.7,
                        description=f"Function {node.name} uses duck typing",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_eafp_pattern(self, tree: ast.AST) -> List[PatternInfo]:
        """Detect EAFP (Easier to Ask for Forgiveness than Permission) pattern."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # EAFP typically has try/except without explicit condition checking
                has_specific_exception = any(
                    isinstance(handler.type, ast.Name) and
                    handler.type.id in ['KeyError', 'AttributeError', 'IndexError', 'TypeError']
                    for handler in node.handlers
                    if handler.type
                )
                
                if has_specific_exception:
                    patterns.append(PatternInfo(
                        pattern_name="EAFP Pattern",
                        confidence=0.6,
                        description="Using EAFP (try/except) instead of LBYL",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    def detect_property_usage(self, tree: ast.AST) -> List[PatternInfo]:
        """Detect property decorator usage."""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_property = any(
                    isinstance(decorator, ast.Name) and decorator.id == 'property'
                    for decorator in node.decorator_list
                )
                
                if has_property:
                    patterns.append(PatternInfo(
                        pattern_name="Property Usage",
                        confidence=1.0,
                        description=f"Method {node.name} uses @property decorator",
                        line_numbers=[node.lineno]
                    ))
        
        return patterns
    
    # Helper Methods for Pattern Recognition
    
    def _has_singleton_logic(self, new_method: ast.FunctionDef) -> bool:
        """Check if __new__ method implements singleton logic."""
        has_instance_check = False
        has_conditional_creation = False
        
        for node in ast.walk(new_method):
            if isinstance(node, ast.If):
                has_conditional_creation = True
            elif isinstance(node, ast.Attribute) and 'instance' in str(node.attr).lower():
                has_instance_check = True
        
        return has_instance_check and has_conditional_creation
    
    def _has_conditional_object_creation(self, func_node: ast.FunctionDef) -> bool:
        """Check if function creates different objects based on conditions."""
        has_conditional = False
        has_object_creation = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                has_conditional = True
            elif isinstance(node, ast.Call):
                # Look for class instantiation
                if isinstance(node.func, ast.Name) and node.func.id[0].isupper():
                    has_object_creation = True
        
        return has_conditional and has_object_creation
    
    def _is_static_or_class_method(self, func_node: ast.FunctionDef) -> bool:
        """Check if function is decorated with @staticmethod or @classmethod."""
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in ['staticmethod', 'classmethod']:
                return True
        return False
    
    def _creates_objects(self, func_node: ast.FunctionDef) -> bool:
        """Check if function creates and returns objects."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
                return True
        return False
    
    def _has_method_delegation(self, method_node: ast.FunctionDef) -> bool:
        """Check if method delegates to another object's method."""
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                return True
        return False
    
    def _looks_like_strategy_class(self, class_node: ast.ClassDef) -> bool:
        """Check if class looks like a strategy implementation."""
        # Look for common strategy method names
        strategy_methods = ['execute', 'run', 'process', 'handle', 'calculate']
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                if any(method in item.name.lower() for method in strategy_methods):
                    return True
        return False
    
    def _looks_like_context_class(self, class_node: ast.ClassDef) -> bool:
        """Check if class looks like a context that uses strategies."""
        has_strategy_ref = False
        has_strategy_usage = False
        
        for item in class_node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and 'strategy' in target.id.lower():
                        has_strategy_ref = True
            
            elif isinstance(item, ast.FunctionDef):
                # Look for strategy method calls
                for node in ast.walk(item):
                    if (isinstance(node, ast.Call) and 
                        isinstance(node.func, ast.Attribute) and
                        'strategy' in str(node.func.attr).lower()):
                        has_strategy_usage = True
        
        return has_strategy_ref or has_strategy_usage
    
    def _returns_self(self, method_node: ast.FunctionDef) -> bool:
        """Check if method returns self (for method chaining)."""
        for node in ast.walk(method_node):
            if (isinstance(node, ast.Return) and 
                isinstance(node.value, ast.Name) and 
                node.value.id == 'self'):
                return True
        return False
    
    def _calls_multiple_methods(self, method_node: ast.FunctionDef) -> bool:
        """Check if method calls multiple other methods."""
        method_calls = 0
        for node in ast.walk(method_node):
            if (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'self'):
                method_calls += 1
        
        return method_calls >= 2
    
    def _is_abstract_method(self, method_node: ast.FunctionDef) -> bool:
        """Check if method is abstract (raises NotImplementedError)."""
        for node in ast.walk(method_node):
            if (isinstance(node, ast.Raise) and
                isinstance(node.exc, ast.Call) and
                isinstance(node.exc.func, ast.Name) and
                node.exc.func.id == 'NotImplementedError'):
                return True
        return False
    
    # Algorithm Pattern Recognition Helpers
    
    def _has_bubble_sort_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements bubble sort pattern."""
        nested_loops = 0
        has_swap = False
        has_comparison = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                nested_loops += 1
            elif isinstance(node, ast.Assign):
                # Look for swapping pattern: a, b = b, a
                if (isinstance(node.value, ast.Tuple) and 
                    len(node.value.elts) == 2 and
                    len(node.targets) == 1 and
                    isinstance(node.targets[0], ast.Tuple)):
                    has_swap = True
            elif isinstance(node, ast.Compare):
                has_comparison = True
        
        return nested_loops >= 2 and has_swap and has_comparison
    
    def _has_quicksort_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements quicksort pattern."""
        has_recursion = False
        has_partitioning = False
        
        # Check for recursive calls
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == func_node.name):
                    has_recursion = True
        
        # Look for partitioning logic (pivot selection and list comprehensions)
        func_body_str = ast.unparse(func_node) if hasattr(ast, 'unparse') else str(func_node)
        if 'pivot' in func_body_str.lower():
            has_partitioning = True
        
        # Also check for list comprehensions that partition data
        list_comps = 0
        for node in ast.walk(func_node):
            if isinstance(node, ast.ListComp):
                list_comps += 1
        
        if list_comps >= 2:  # Typically left and right partitions
            has_partitioning = True
        
        return has_recursion and has_partitioning
    
    def _has_mergesort_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements mergesort pattern."""
        has_recursion = False
        has_merge_logic = False
        
        # Check for recursive calls
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == func_node.name):
                    has_recursion = True
                elif (isinstance(node.func, ast.Name) and 
                      'merge' in node.func.id.lower()):
                    has_merge_logic = True
        
        # Look for merge logic in function body
        func_body_str = ast.unparse(func_node) if hasattr(ast, 'unparse') else str(func_node)
        if 'merge' in func_body_str.lower():
            has_merge_logic = True
        
        # Check for array slicing (typical in merge sort)
        has_slicing = False
        for node in ast.walk(func_node):
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Slice):
                    has_slicing = True
        
        return has_recursion and (has_merge_logic or has_slicing)
    
    def _has_insertion_sort_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements insertion sort pattern."""
        has_outer_loop = False
        has_inner_loop = False
        has_insertion = False
        
        loop_count = 0
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                loop_count += 1
            elif isinstance(node, ast.While):
                has_inner_loop = True
            elif isinstance(node, ast.Assign):
                # Look for element insertion/shifting
                has_insertion = True
        
        return loop_count >= 1 and (has_inner_loop or loop_count >= 2) and has_insertion
    
    def _has_binary_search_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements binary search pattern."""
        has_while_loop = False
        has_midpoint = False
        has_comparison = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.While):
                has_while_loop = True
            elif isinstance(node, ast.Assign):
                # Look for midpoint calculation
                if isinstance(node.value, ast.BinOp):
                    if isinstance(node.value.op, (ast.FloorDiv, ast.Div)):
                        has_midpoint = True
            elif isinstance(node, ast.Compare):
                has_comparison = True
        
        return has_while_loop and has_midpoint and has_comparison
    
    def _has_linear_search_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements linear search pattern."""
        has_loop = False
        has_comparison = False
        has_return_in_loop = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                has_loop = True
                # Check if there's a return statement inside the loop
                for child in ast.walk(node):
                    if isinstance(child, ast.Return):
                        has_return_in_loop = True
                    elif isinstance(child, ast.Compare):
                        has_comparison = True
        
        return has_loop and has_comparison and has_return_in_loop
    
    def _has_map_reduce_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements map-reduce pattern."""
        has_map = False
        has_reduce = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['map', 'filter']:
                    has_map = True
                elif node.func.id in ['reduce', 'sum', 'min', 'max']:
                    has_reduce = True
        
        return has_map and has_reduce
    
    def _has_filter_transform_pattern(self, func_node: ast.FunctionDef) -> bool:
        """Check if function implements filter-transform pattern."""
        has_filter = False
        has_transform = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.ListComp):
                # List comprehension with condition is filter-transform
                if any(node.generators[0].ifs):
                    has_filter = True
                has_transform = True
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'filter':
                    has_filter = True
                elif node.func.id == 'map':
                    has_transform = True
        
        return has_filter and has_transform
    
    def _analyze_comprehension_complexity(self, comp_node) -> str:
        """Analyze the complexity of a comprehension."""
        if hasattr(comp_node, 'generators'):
            generators = comp_node.generators
            
            if len(generators) > 1:
                return "nested"
            elif generators[0].ifs:
                return "filtered"
            else:
                return "simple"
        
        return "simple"    

    def _is_decorator_function(self, func_node: ast.FunctionDef) -> bool:
        """Check if function is likely a decorator."""
        # Look for nested function definition
        has_nested_function = False
        returns_function = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.FunctionDef) and node != func_node:
                has_nested_function = True
            elif isinstance(node, ast.Return):
                if isinstance(node.value, ast.Name):
                    # Returning a function name
                    returns_function = True
        
        return has_nested_function and returns_function