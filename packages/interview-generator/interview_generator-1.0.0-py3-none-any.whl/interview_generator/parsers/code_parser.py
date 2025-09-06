"""
Core AST parsing functionality for Python code analysis.
"""

import ast
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from ..models.analysis_models import (
    AnalysisResult,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    VariableInfo,
    ComplexityMetrics,
    PatternInfo,
    BusinessContext
)
from ..models.config_models import Config
from ..utils.file_discovery import FileDiscovery


logger = logging.getLogger(__name__)


class CodeParsingError(Exception):
    """Base exception for code parsing errors."""
    pass


class PythonSyntaxError(CodeParsingError):
    """Raised when Python code has syntax errors."""
    pass


class EncodingError(CodeParsingError):
    """Raised when file encoding cannot be determined."""
    pass


class CodeParser:
    """Parser for extracting information from Python code using AST."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the code parser.
        
        Args:
            config: Configuration object for parser settings
        """
        self.config = config
        self.file_discovery = FileDiscovery(config=config)
    
    def parse_file(self, file_path: Path) -> AnalysisResult:
        """
        Parse a Python file and extract code information.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            AnalysisResult containing extracted information
            
        Raises:
            CodeParsingError: If file cannot be parsed
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        logger.info(f"Parsing file: {file_path}")
        
        # Validate file
        try:
            self.file_discovery.is_valid_python_file(file_path)
        except Exception as e:
            logger.error(f"Invalid Python file {file_path}: {e}")
            return AnalysisResult(
                file_path=str(file_path),
                functions=[], classes=[], imports=[], variables=[],
                complexity_metrics=ComplexityMetrics(0, 0, 0, []),
                patterns=[], context=BusinessContext("", "", [], {}),
                success=False, errors=[f"Invalid Python file: {e}"], warnings=[]
            )
        
        # Read file content
        try:
            content = self.file_discovery._read_file_content(file_path)
        except Exception as e:
            logger.error(f"Cannot read file {file_path}: {e}")
            return AnalysisResult(
                file_path=str(file_path),
                functions=[], classes=[], imports=[], variables=[],
                complexity_metrics=ComplexityMetrics(0, 0, 0, []),
                patterns=[], context=BusinessContext("", "", [], {}),
                success=False, errors=[f"Cannot read file: {e}"], warnings=[]
            )
        
        # Parse the code
        return self.parse_code(content, str(file_path))
    
    def parse_code(self, code: str, filename: str = "<string>") -> AnalysisResult:
        """
        Parse Python code string and extract information.
        
        Args:
            code: Python code as string
            filename: Name of the file (for error reporting)
            
        Returns:
            AnalysisResult containing extracted information
            
        Raises:
            PythonSyntaxError: If code has syntax errors
        """
        logger.debug(f"Parsing code from {filename}")
        
        # Parse code into AST
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            logger.error(f"Syntax error in {filename}: {e}")
            return AnalysisResult(
                file_path=filename,
                functions=[], classes=[], imports=[], variables=[],
                complexity_metrics=ComplexityMetrics(0, 0, 0, []),
                patterns=[], context=BusinessContext("", "", [], {}),
                success=False, errors=[f"Syntax error: {e}"], warnings=[]
            )
        
        # Extract information from AST
        try:
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            imports = self._extract_imports(tree)
            variables = self._extract_variables(tree)
            
            # Create placeholder objects for now (will be implemented in later tasks)
            complexity_metrics = ComplexityMetrics(
                cyclomatic_complexity=0,
                nesting_depth=0,
                function_length=0,
                code_smells=[]
            )
            
            patterns = []  # Will be populated by pattern detector
            
            context = BusinessContext(
                purpose="",
                domain="",
                key_operations=[],
                data_flow={}
            )
            
            result = AnalysisResult(
                file_path=filename,
                functions=functions,
                classes=classes,
                imports=imports,
                variables=variables,
                complexity_metrics=complexity_metrics,
                patterns=patterns,
                context=context,
                success=True,
                errors=[],
                warnings=[]
            )
            
            logger.info(f"Successfully parsed {filename}: "
                       f"{len(functions)} functions, {len(classes)} classes, "
                       f"{len(imports)} imports, {len(variables)} variables")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting information from {filename}: {e}")
            return AnalysisResult(
                file_path=filename,
                functions=[], classes=[], imports=[], variables=[],
                complexity_metrics=ComplexityMetrics(0, 0, 0, []),
                patterns=[], context=BusinessContext("", "", [], {}),
                success=False, errors=[f"Failed to extract information: {e}"], warnings=[]
            )
    
    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        """
        Extract function information from AST.
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            List of FunctionInfo objects
        """
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    func_info = self._parse_function_node(node)
                    functions.append(func_info)
                except Exception as e:
                    logger.warning(f"Error parsing function {getattr(node, 'name', 'unknown')}: {e}")
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        """
        Extract class information from AST.
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            List of ClassInfo objects
        """
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                try:
                    class_info = self._parse_class_node(node)
                    classes.append(class_info)
                except Exception as e:
                    logger.warning(f"Error parsing class {getattr(node, 'name', 'unknown')}: {e}")
        
        return classes
    
    def _extract_imports(self, tree: ast.AST) -> List[ImportInfo]:
        """
        Extract import information from AST.
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            List of ImportInfo objects
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                try:
                    for alias in node.names:
                        import_info = ImportInfo(
                            module=alias.name,
                            names=[alias.name],
                            alias=alias.asname,
                            line_number=node.lineno
                        )
                        imports.append(import_info)
                except Exception as e:
                    logger.warning(f"Error parsing import: {e}")
            
            elif isinstance(node, ast.ImportFrom):
                try:
                    module_name = node.module or ""
                    names = []
                    
                    for alias in node.names:
                        names.append(alias.name)
                    
                    import_info = ImportInfo(
                        module=module_name,
                        names=names,
                        alias=None,  # ImportFrom doesn't have module alias
                        line_number=node.lineno
                    )
                    imports.append(import_info)
                except Exception as e:
                    logger.warning(f"Error parsing from import: {e}")
        
        return imports
    
    def _extract_variables(self, tree: ast.AST) -> List[VariableInfo]:
        """
        Extract variable information from AST.
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            List of VariableInfo objects
        """
        variables = []
        
        # Track scope context
        scope_stack = ['global']
        
        class VariableVisitor(ast.NodeVisitor):
            def __init__(self, parser):
                self.parser = parser
                self.variables = []
            
            def visit_FunctionDef(self, node):
                scope_stack.append(f'function:{node.name}')
                self.generic_visit(node)
                scope_stack.pop()
            
            def visit_AsyncFunctionDef(self, node):
                scope_stack.append(f'async_function:{node.name}')
                self.generic_visit(node)
                scope_stack.pop()
            
            def visit_ClassDef(self, node):
                scope_stack.append(f'class:{node.name}')
                self.generic_visit(node)
                scope_stack.pop()
            
            def visit_Assign(self, node):
                try:
                    current_scope = scope_stack[-1] if scope_stack else 'global'
                    
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_info = VariableInfo(
                                name=target.id,
                                value_type=self.parser._get_value_type(node.value),
                                line_number=node.lineno,
                                scope=current_scope
                            )
                            self.variables.append(var_info)
                        elif isinstance(target, ast.Tuple):
                            # Handle tuple unpacking: a, b = 1, 2
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    var_info = VariableInfo(
                                        name=elt.id,
                                        value_type="tuple_element",
                                        line_number=node.lineno,
                                        scope=current_scope
                                    )
                                    self.variables.append(var_info)
                except Exception as e:
                    logger.debug(f"Error parsing assignment: {e}")
                
                self.generic_visit(node)
            
            def visit_AnnAssign(self, node):
                try:
                    if isinstance(node.target, ast.Name):
                        current_scope = scope_stack[-1] if scope_stack else 'global'
                        
                        var_info = VariableInfo(
                            name=node.target.id,
                            value_type=self.parser._get_type_annotation(node.annotation),
                            line_number=node.lineno,
                            scope=current_scope
                        )
                        self.variables.append(var_info)
                except Exception as e:
                    logger.debug(f"Error parsing annotated assignment: {e}")
                
                self.generic_visit(node)
        
        visitor = VariableVisitor(self)
        visitor.visit(tree)
        
        return visitor.variables
    
    def _parse_function_node(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> FunctionInfo:
        """
        Parse a function AST node into FunctionInfo.
        
        Args:
            node: Function AST node
            
        Returns:
            FunctionInfo object
        """
        name = node.name
        parameters = self._extract_parameters(node)
        return_annotation = self._get_type_annotation(node.returns) if node.returns else None
        docstring = self._get_docstring(node)
        line_number = node.lineno
        
        return FunctionInfo(
            name=name,
            parameters=parameters,
            return_annotation=return_annotation,
            docstring=docstring,
            line_number=line_number,
            complexity_score=0  # Will be calculated by complexity analyzer
        )
    
    def _parse_class_node(self, node: ast.ClassDef) -> ClassInfo:
        """
        Parse a class AST node into ClassInfo.
        
        Args:
            node: Class AST node
            
        Returns:
            ClassInfo object
        """
        name = node.name
        docstring = self._get_docstring(node)
        line_number = node.lineno
        
        # Extract inheritance
        inheritance = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                inheritance.append(base.id)
            elif isinstance(base, ast.Attribute):
                inheritance.append(self._get_attribute_name(base))
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    method_info = self._parse_function_node(item)
                    methods.append(method_info)
                except Exception as e:
                    logger.warning(f"Error parsing method {item.name}: {e}")
        
        return ClassInfo(
            name=name,
            methods=methods,
            inheritance=inheritance,
            docstring=docstring,
            line_number=line_number
        )
    
    def _extract_parameters(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> List[str]:
        """
        Extract parameter information from function node.
        
        Args:
            func_node: Function AST node
            
        Returns:
            List of parameter strings with type annotations and defaults
        """
        parameters = []
        args = func_node.args
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            param_str = arg.arg
            
            # Add type annotation if present
            if arg.annotation:
                type_str = self._get_type_annotation(arg.annotation)
                if type_str:
                    param_str += f": {type_str}"
            
            # Add default value if present
            defaults_offset = len(args.args) - len(args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                default_value = self._get_default_value(args.defaults[default_idx])
                param_str += f" = {default_value}"
            
            parameters.append(param_str)
        
        # *args parameter
        if args.vararg:
            vararg_str = f"*{args.vararg.arg}"
            if args.vararg.annotation:
                type_str = self._get_type_annotation(args.vararg.annotation)
                if type_str:
                    vararg_str += f": {type_str}"
            parameters.append(vararg_str)
        
        # Keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            param_str = arg.arg
            
            if arg.annotation:
                type_str = self._get_type_annotation(arg.annotation)
                if type_str:
                    param_str += f": {type_str}"
            
            # Keyword-only defaults
            if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
                default_value = self._get_default_value(args.kw_defaults[i])
                param_str += f" = {default_value}"
            
            parameters.append(param_str)
        
        # **kwargs parameter
        if args.kwarg:
            kwarg_str = f"**{args.kwarg.arg}"
            if args.kwarg.annotation:
                type_str = self._get_type_annotation(args.kwarg.annotation)
                if type_str:
                    kwarg_str += f": {type_str}"
            parameters.append(kwarg_str)
        
        return parameters
    
    def _get_docstring(self, node: ast.AST) -> Optional[str]:
        """
        Extract docstring from AST node.
        
        Args:
            node: AST node to extract docstring from
            
        Returns:
            Docstring text or None
        """
        if not hasattr(node, 'body') or not node.body:
            return None
        
        first_stmt = node.body[0]
        if (isinstance(first_stmt, ast.Expr) and 
            isinstance(first_stmt.value, ast.Constant) and 
            isinstance(first_stmt.value.value, str)):
            return first_stmt.value.value
        
        return None
    
    def _get_type_annotation(self, annotation: ast.AST) -> Optional[str]:
        """
        Convert AST type annotation to string.
        
        Args:
            annotation: AST annotation node
            
        Returns:
            String representation of type annotation
        """
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Constant):
                return repr(annotation.value)
            elif isinstance(annotation, ast.Attribute):
                return self._get_attribute_name(annotation)
            elif isinstance(annotation, ast.Subscript):
                value = self._get_type_annotation(annotation.value)
                if isinstance(annotation.slice, ast.Tuple):
                    # Handle multiple type parameters like Dict[str, int]
                    elements = [self._get_type_annotation(elt) for elt in annotation.slice.elts]
                    slice_val = ', '.join(filter(None, elements))
                else:
                    slice_val = self._get_type_annotation(annotation.slice)
                return f"{value}[{slice_val}]"
            elif isinstance(annotation, ast.Tuple):
                elements = [self._get_type_annotation(elt) for elt in annotation.elts]
                return f"({', '.join(filter(None, elements))})"
            elif isinstance(annotation, ast.List):
                elements = [self._get_type_annotation(elt) for elt in annotation.elts]
                return f"[{', '.join(filter(None, elements))}]"
            else:
                # Fallback: try to unparse the annotation
                return ast.unparse(annotation)
        except Exception:
            return None
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """
        Get full attribute name (e.g., 'typing.Optional').
        
        Args:
            node: Attribute AST node
            
        Returns:
            Full attribute name
        """
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        else:
            return node.attr
    
    def _get_default_value(self, node: ast.AST) -> str:
        """
        Get string representation of default value.
        
        Args:
            node: AST node representing default value
            
        Returns:
            String representation of default value
        """
        try:
            if isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return self._get_attribute_name(node)
            else:
                return ast.unparse(node)
        except Exception:
            return "..."
    
    def _get_value_type(self, node: ast.AST) -> Optional[str]:
        """
        Determine the type of a value from AST node.
        
        Args:
            node: AST node representing a value
            
        Returns:
            String representation of value type
        """
        try:
            if isinstance(node, ast.Constant):
                return type(node.value).__name__
            elif isinstance(node, ast.Name):
                return "variable"
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    return f"call:{node.func.id}"
                else:
                    return "call"
            elif isinstance(node, ast.List):
                return "list"
            elif isinstance(node, ast.Dict):
                return "dict"
            elif isinstance(node, ast.Tuple):
                return "tuple"
            elif isinstance(node, ast.Set):
                return "set"
            elif isinstance(node, ast.ListComp):
                return "list_comprehension"
            elif isinstance(node, ast.DictComp):
                return "dict_comprehension"
            elif isinstance(node, ast.SetComp):
                return "set_comprehension"
            elif isinstance(node, ast.GeneratorExp):
                return "generator"
            else:
                return "expression"
        except Exception:
            return None