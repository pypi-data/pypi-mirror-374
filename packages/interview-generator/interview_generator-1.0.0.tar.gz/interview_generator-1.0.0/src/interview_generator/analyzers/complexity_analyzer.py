"""
Complexity analysis engine for Python code.
"""

import ast
import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from ..models.analysis_models import ComplexityMetrics, FunctionInfo
from ..models.config_models import Config


logger = logging.getLogger(__name__)


class ComplexityAnalysisError(Exception):
    """Base exception for complexity analysis errors."""
    pass


class ComplexityAnalyzer:
    """Analyzer for measuring code complexity and detecting code smells."""
    
    # Complexity thresholds
    COMPLEXITY_THRESHOLDS = {
        'low': (1, 5),
        'medium': (6, 10),
        'high': (11, 15),
        'very_high': (16, float('inf'))
    }
    
    NESTING_THRESHOLDS = {
        'good': (1, 2),
        'acceptable': (3, 4),
        'too_deep': (5, float('inf'))
    }
    
    LENGTH_THRESHOLDS = {
        'good': (1, 20),
        'acceptable': (21, 50),
        'long': (51, 100),
        'too_long': (101, float('inf'))
    }
    
    # Code smell thresholds
    MAX_PARAMETERS = 5
    MAX_FUNCTION_LENGTH = 50
    MAX_COMPLEXITY = 10
    MAX_NESTING_DEPTH = 4
    MAX_LOCAL_VARIABLES = 15
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the complexity analyzer.
        
        Args:
            config: Configuration object for analyzer settings
        """
        self.config = config
    
    def analyze_function(self, func_node: ast.FunctionDef, code: str, 
                        func_info: Optional[FunctionInfo] = None) -> ComplexityMetrics:
        """
        Analyze complexity of a single function.
        
        Args:
            func_node: AST node of the function
            code: Source code containing the function
            func_info: Optional FunctionInfo object with additional context
            
        Returns:
            ComplexityMetrics object with analysis results
        """
        logger.debug(f"Analyzing complexity for function: {func_node.name}")
        
        try:
            # Calculate core metrics
            cyclomatic_complexity = self.calculate_cyclomatic_complexity(func_node)
            nesting_depth = self.calculate_nesting_depth(func_node)
            function_length = self.calculate_function_length(func_node, code)
            
            # Detect code smells
            code_smells = self.detect_code_smells(func_node, code)
            
            # Calculate additional metrics
            parameter_count = self._count_parameters(func_node)
            local_variable_count = self._count_local_variables(func_node)
            return_statement_count = self._count_return_statements(func_node)
            magic_number_count = len(self._find_magic_numbers(func_node))
            
            # Determine complexity rating
            complexity_rating = self._get_complexity_rating(cyclomatic_complexity)
            
            # Calculate maintainability index (simplified version)
            maintainability_index = self._calculate_maintainability_index(
                cyclomatic_complexity, function_length, len(code_smells)
            )
            
            return ComplexityMetrics(
                cyclomatic_complexity=cyclomatic_complexity,
                nesting_depth=nesting_depth,
                function_length=function_length,
                code_smells=code_smells,
                parameter_count=parameter_count,
                local_variable_count=local_variable_count,
                return_statement_count=return_statement_count,
                magic_number_count=magic_number_count,
                complexity_rating=complexity_rating,
                maintainability_index=maintainability_index
            )
            
        except Exception as e:
            logger.error(f"Error analyzing function {func_node.name}: {e}")
            raise ComplexityAnalysisError(f"Failed to analyze function {func_node.name}: {e}")
    
    def analyze_code(self, code: str, filename: str = "<string>") -> Dict[str, ComplexityMetrics]:
        """
        Analyze complexity of all functions in code.
        
        Args:
            code: Python source code
            filename: Name of the file (for error reporting)
            
        Returns:
            Dictionary mapping function names to ComplexityMetrics
        """
        logger.debug(f"Analyzing complexity for code in {filename}")
        
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            raise ComplexityAnalysisError(f"Syntax error in {filename}: {e}")
        
        results = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    metrics = self.analyze_function(node, code)
                    results[node.name] = metrics
                except Exception as e:
                    logger.warning(f"Error analyzing function {node.name}: {e}")
        
        return results
    
    def calculate_cyclomatic_complexity(self, func_node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity using decision point counting.
        
        Complexity = 1 + number of decision points
        
        Decision points include:
        - if/elif statements
        - while/for loops  
        - try/except blocks (each except clause)
        - boolean operators (and/or)
        - ternary operators
        - match/case statements (Python 3.10+)
        - comprehensions with conditions
        
        Args:
            func_node: Function AST node
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        # Track processed if statements to avoid double counting elif chains
        processed_ifs = set()
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.If) and id(node) not in processed_ifs:
                complexity += 1
                processed_ifs.add(id(node))
                
                # Count elif clauses in the chain
                current = node
                while hasattr(current, 'orelse') and len(current.orelse) == 1:
                    if isinstance(current.orelse[0], ast.If):
                        complexity += 1
                        current = current.orelse[0]
                        processed_ifs.add(id(current))  # Mark as processed
                    else:
                        break
            
            elif isinstance(node, (ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            
            elif isinstance(node, ast.BoolOp):
                # and/or operators add complexity
                complexity += len(node.values) - 1
            
            elif isinstance(node, ast.IfExp):  # Ternary operator
                complexity += 1
            
            elif hasattr(ast, 'Match') and isinstance(node, ast.Match):
                # Python 3.10+ match statement
                complexity += len(node.cases)
            
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                # Comprehensions with conditions
                for generator in node.generators:
                    complexity += len(generator.ifs)
        
        return complexity
    
    def calculate_nesting_depth(self, func_node: ast.FunctionDef) -> int:
        """
        Calculate maximum nesting depth of control structures.
        
        Args:
            func_node: Function AST node
            
        Returns:
            Maximum nesting depth
        """
        def measure_depth(node: ast.AST, current_depth: int = 0) -> int:
            max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                child_depth = current_depth
                
                # Increment depth for nesting structures
                if isinstance(child, (
                    ast.If, ast.While, ast.For, ast.AsyncFor,
                    ast.Try, ast.With, ast.AsyncWith,
                    ast.FunctionDef, ast.AsyncFunctionDef,
                    ast.ClassDef
                )):
                    child_depth += 1
                
                # Handle match statements if available (Python 3.10+)
                elif hasattr(ast, 'Match') and isinstance(child, ast.Match):
                    child_depth += 1
                
                # Recursively measure child depth
                nested_depth = measure_depth(child, child_depth)
                max_depth = max(max_depth, nested_depth)
            
            return max_depth
        
        return measure_depth(func_node)
    
    def calculate_function_length(self, func_node: ast.FunctionDef, code: str) -> int:
        """
        Calculate function length in lines of code (excluding comments and blank lines).
        
        Args:
            func_node: Function AST node
            code: Source code containing the function
            
        Returns:
            Number of code lines in the function
        """
        lines = code.split('\n')
        start_line = func_node.lineno - 1  # Convert to 0-based indexing
        
        # Find end line by looking at the last statement in the function
        end_line = start_line + 1
        if func_node.body:
            last_stmt = func_node.body[-1]
            end_line = getattr(last_stmt, 'end_lineno', last_stmt.lineno)
            if end_line is None:
                end_line = last_stmt.lineno
        
        # Count non-empty, non-comment lines
        code_lines = 0
        for i in range(start_line, min(end_line, len(lines))):
            if i < len(lines):
                line = lines[i].strip()
                if line and not line.startswith('#'):
                    code_lines += 1
        
        return code_lines
    
    def detect_code_smells(self, func_node: ast.FunctionDef, code: str) -> List[str]:
        """
        Detect various code smells in the function.
        
        Args:
            func_node: Function AST node
            code: Source code containing the function
            
        Returns:
            List of detected code smells
        """
        smells = []
        
        # Long parameter list
        param_count = self._count_parameters(func_node)
        if param_count > self.MAX_PARAMETERS:
            smells.append(f"Long parameter list ({param_count} parameters)")
        
        # Missing docstring
        if not self._has_docstring(func_node):
            smells.append("Missing docstring")
        
        # High complexity
        complexity = self.calculate_cyclomatic_complexity(func_node)
        if complexity > self.MAX_COMPLEXITY:
            smells.append(f"High cyclomatic complexity ({complexity})")
        
        # Deep nesting
        nesting = self.calculate_nesting_depth(func_node)
        if nesting > self.MAX_NESTING_DEPTH:
            smells.append(f"Deep nesting ({nesting} levels)")
        
        # Long function
        length = self.calculate_function_length(func_node, code)
        if length > self.MAX_FUNCTION_LENGTH:
            smells.append(f"Long function ({length} lines)")
        
        # Too many local variables
        local_vars = self._count_local_variables(func_node)
        if local_vars > self.MAX_LOCAL_VARIABLES:
            smells.append(f"Too many local variables ({local_vars})")
        
        # Magic numbers
        magic_numbers = self._find_magic_numbers(func_node)
        if magic_numbers:
            smells.append(f"Magic numbers: {magic_numbers}")
        
        # Empty exception handling
        if self._has_empty_except(func_node):
            smells.append("Empty exception handling")
        
        # Broad exception catching
        if self._has_broad_except(func_node):
            smells.append("Broad exception catching")
        
        # Multiple return statements
        return_count = self._count_return_statements(func_node)
        if return_count > 5:
            smells.append(f"Too many return statements ({return_count})")
        
        # Inconsistent naming
        naming_issues = self._check_naming_consistency(func_node)
        if naming_issues:
            smells.extend(naming_issues)
        
        return smells
    
    def _count_parameters(self, func_node: ast.FunctionDef) -> int:
        """Count total number of parameters including *args and **kwargs."""
        count = len(func_node.args.args)
        if func_node.args.vararg:
            count += 1
        if func_node.args.kwarg:
            count += 1
        count += len(func_node.args.kwonlyargs)
        return count
    
    def _count_local_variables(self, func_node: ast.FunctionDef) -> int:
        """Count local variable assignments in the function."""
        variables = set()
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                variables.add(elt.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                variables.add(node.target.id)
        
        return len(variables)
    
    def _count_return_statements(self, func_node: ast.FunctionDef) -> int:
        """Count return statements in the function."""
        return sum(1 for node in ast.walk(func_node) if isinstance(node, ast.Return))
    
    def _find_magic_numbers(self, func_node: ast.FunctionDef) -> List[int]:
        """Find magic numbers (hardcoded numeric literals) in the function."""
        magic_numbers = []
        
        # Common non-magic numbers
        non_magic = {0, 1, -1, 2, 10, 100, 1000}
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in non_magic and abs(node.value) > 1:
                    magic_numbers.append(node.value)
        
        return list(set(magic_numbers))  # Remove duplicates
    
    def _has_docstring(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has a docstring."""
        if not func_node.body:
            return False
        
        first_stmt = func_node.body[0]
        return (isinstance(first_stmt, ast.Expr) and 
                isinstance(first_stmt.value, ast.Constant) and 
                isinstance(first_stmt.value.value, str))
    
    def _has_empty_except(self, func_node: ast.FunctionDef) -> bool:
        """Check for empty exception handlers."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.ExceptHandler):
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Pass)):
                    return True
        return False
    
    def _has_broad_except(self, func_node: ast.FunctionDef) -> bool:
        """Check for broad exception catching."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:  # bare except:
                    return True
                elif (isinstance(node.type, ast.Name) and 
                      node.type.id in ['Exception', 'BaseException']):
                    return True
        return False
    
    def _check_naming_consistency(self, func_node: ast.FunctionDef) -> List[str]:
        """Check for naming consistency issues."""
        issues = []
        variable_names = []
        
        # Collect variable names
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                variable_names.append(node.id)
        
        # Check for mixed naming conventions
        snake_case_pattern = re.compile(r'^[a-z_][a-z0-9_]*$')
        camel_case_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
        
        snake_case_vars = [name for name in variable_names if snake_case_pattern.match(name)]
        camel_case_vars = [name for name in variable_names if camel_case_pattern.match(name)]
        
        if snake_case_vars and camel_case_vars:
            issues.append("Mixed naming conventions (snake_case and camelCase)")
        
        return issues
    
    def _get_complexity_rating(self, complexity: int) -> str:
        """Get complexity rating based on cyclomatic complexity."""
        for rating, (min_val, max_val) in self.COMPLEXITY_THRESHOLDS.items():
            if min_val <= complexity <= max_val:
                return rating
        return "very_high"
    
    def _calculate_maintainability_index(self, complexity: int, length: int, 
                                       smell_count: int) -> float:
        """
        Calculate a simplified maintainability index.
        
        Higher values indicate better maintainability (0-100 scale).
        """
        # Simplified formula based on complexity, length, and code smells
        base_score = 100.0
        
        # Penalize high complexity
        complexity_penalty = max(0, (complexity - 5) * 5)
        
        # Penalize long functions
        length_penalty = max(0, (length - 20) * 1)
        
        # Penalize code smells
        smell_penalty = smell_count * 10
        
        score = base_score - complexity_penalty - length_penalty - smell_penalty
        return max(0.0, min(100.0, score))
    
    def get_complexity_summary(self, metrics: ComplexityMetrics) -> Dict[str, str]:
        """
        Get a human-readable summary of complexity metrics.
        
        Args:
            metrics: ComplexityMetrics object
            
        Returns:
            Dictionary with summary information
        """
        return {
            'complexity_level': metrics.complexity_rating,
            'maintainability': 'high' if metrics.maintainability_index > 70 else 
                             'medium' if metrics.maintainability_index > 40 else 'low',
            'nesting_assessment': 'good' if metrics.nesting_depth <= 2 else
                                'acceptable' if metrics.nesting_depth <= 4 else 'too_deep',
            'length_assessment': 'good' if metrics.function_length <= 20 else
                               'acceptable' if metrics.function_length <= 50 else 'too_long',
            'smell_count': len(metrics.code_smells),
            'overall_quality': self._assess_overall_quality(metrics)
        }
    
    def _assess_overall_quality(self, metrics: ComplexityMetrics) -> str:
        """Assess overall code quality based on all metrics."""
        score = 0
        
        # Complexity score
        if metrics.cyclomatic_complexity <= 5:
            score += 3
        elif metrics.cyclomatic_complexity <= 10:
            score += 2
        elif metrics.cyclomatic_complexity <= 15:
            score += 1
        
        # Nesting score
        if metrics.nesting_depth <= 2:
            score += 2
        elif metrics.nesting_depth <= 4:
            score += 1
        
        # Length score
        if metrics.function_length <= 20:
            score += 2
        elif metrics.function_length <= 50:
            score += 1
        
        # Code smell penalty
        score -= min(len(metrics.code_smells), 3)
        
        if score >= 6:
            return "excellent"
        elif score >= 4:
            return "good"
        elif score >= 2:
            return "fair"
        else:
            return "poor"