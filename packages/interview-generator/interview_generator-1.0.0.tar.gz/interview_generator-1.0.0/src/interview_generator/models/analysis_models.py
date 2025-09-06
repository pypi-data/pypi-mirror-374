"""
Data models for code analysis results.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class FunctionInfo:
    """Information about a function extracted from code analysis."""
    name: str
    parameters: List[str]
    return_annotation: Optional[str]
    docstring: Optional[str]
    line_number: int
    complexity_score: int = 0


@dataclass
class ClassInfo:
    """Information about a class extracted from code analysis."""
    name: str
    methods: List[FunctionInfo]
    inheritance: List[str]
    docstring: Optional[str]
    line_number: int


@dataclass
class ImportInfo:
    """Information about imports in the analyzed code."""
    module: str
    names: List[str]
    alias: Optional[str]
    line_number: int


@dataclass
class VariableInfo:
    """Information about variable assignments."""
    name: str
    value_type: Optional[str]
    line_number: int
    scope: str  # 'global', 'local', 'class'


@dataclass
class ComplexityMetrics:
    """Code complexity measurements."""
    cyclomatic_complexity: int
    nesting_depth: int
    function_length: int
    code_smells: List[str]
    
    # Additional metrics
    parameter_count: int = 0
    local_variable_count: int = 0
    return_statement_count: int = 0
    magic_number_count: int = 0
    
    # Complexity ratings
    complexity_rating: str = "low"  # low, medium, high, very_high
    maintainability_index: float = 100.0  # 0-100 scale


@dataclass
class PatternInfo:
    """Information about detected design patterns."""
    pattern_name: str
    confidence: float
    description: str
    line_numbers: List[int]


@dataclass
class AlgorithmInfo:
    """Information about detected algorithms."""
    algorithm_name: str
    algorithm_type: str  # "sorting", "searching", "data_processing"
    confidence: float
    description: str
    line_numbers: List[int]
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    implementation_notes: List[str] = field(default_factory=list)


@dataclass
class BusinessContext:
    """Business logic context extracted from code."""
    purpose: str
    domain: str
    key_operations: List[str]
    data_flow: Dict[str, Any]


@dataclass
class AnalysisResult:
    """Complete analysis result for a Python file."""
    file_path: str
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[ImportInfo]
    variables: List[VariableInfo]
    complexity_metrics: ComplexityMetrics
    patterns: List[PatternInfo]
    context: BusinessContext
    success: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)