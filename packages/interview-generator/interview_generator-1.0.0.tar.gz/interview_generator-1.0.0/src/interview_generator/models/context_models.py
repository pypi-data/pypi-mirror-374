"""
Data models for context extraction results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class DomainType(Enum):
    """Common software domain types."""
    WEB = "web"
    DATA = "data"
    ML = "machine_learning"
    FINANCE = "finance"
    GAMING = "gaming"
    SYSTEM = "system"
    API = "api"
    CLI = "cli"
    LIBRARY = "library"
    UNKNOWN = "unknown"


class WorkflowPattern(Enum):
    """Common workflow patterns."""
    CRUD = "crud"
    ETL = "etl"
    MVC = "mvc"
    PIPELINE = "pipeline"
    EVENT_DRIVEN = "event_driven"
    BATCH_PROCESSING = "batch_processing"
    STREAM_PROCESSING = "stream_processing"
    API_GATEWAY = "api_gateway"
    MICROSERVICE = "microservice"
    MONOLITH = "monolith"


class ErrorHandlingStrategy(Enum):
    """Error handling strategies."""
    FAIL_FAST = "fail_fast"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK = "fallback"
    LOGGING_ONLY = "logging_only"
    SILENT_FAILURE = "silent_failure"


class PerformancePattern(Enum):
    """Performance optimization patterns."""
    CACHING = "caching"
    LAZY_LOADING = "lazy_loading"
    MEMOIZATION = "memoization"
    POOLING = "pooling"
    BATCHING = "batching"
    ASYNC_PROCESSING = "async_processing"
    STREAMING = "streaming"
    PAGINATION = "pagination"


@dataclass
class BusinessContext:
    """Context about the business logic and purpose of code."""
    domain_type: DomainType
    business_purpose: str
    workflow_patterns: List[WorkflowPattern] = field(default_factory=list)
    data_entities: List[str] = field(default_factory=list)
    external_integrations: List[str] = field(default_factory=list)
    configuration_patterns: List[str] = field(default_factory=list)
    user_interactions: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    data_transformations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class ErrorHandlingContext:
    """Context about error handling patterns and strategies."""
    exception_patterns: List[str] = field(default_factory=list)
    recovery_strategies: List[ErrorHandlingStrategy] = field(default_factory=list)
    validation_approaches: List[str] = field(default_factory=list)
    logging_patterns: List[str] = field(default_factory=list)
    defensive_patterns: List[str] = field(default_factory=list)
    error_propagation: str = ""
    exception_hierarchy: List[str] = field(default_factory=list)
    error_handling_coverage: float = 0.0


@dataclass
class PerformanceContext:
    """Context about performance considerations and optimizations."""
    performance_hotspots: List[str] = field(default_factory=list)
    memory_patterns: List[str] = field(default_factory=list)
    io_operations: List[str] = field(default_factory=list)
    optimization_patterns: List[PerformancePattern] = field(default_factory=list)
    scalability_considerations: List[str] = field(default_factory=list)
    resource_usage: Dict[str, str] = field(default_factory=dict)
    complexity_hotspots: List[str] = field(default_factory=list)
    concurrency_patterns: List[str] = field(default_factory=list)


@dataclass
class DocumentationContext:
    """Context extracted from documentation and comments."""
    docstring_coverage: float = 0.0
    docstring_quality: str = "unknown"  # "excellent", "good", "fair", "poor", "none"
    documentation_style: str = "unknown"  # "google", "numpy", "sphinx", "custom", "none"
    inline_comments: List[str] = field(default_factory=list)
    todo_items: List[str] = field(default_factory=list)
    fixme_items: List[str] = field(default_factory=list)
    examples_in_docs: List[str] = field(default_factory=list)
    type_hint_coverage: float = 0.0
    api_documentation: List[str] = field(default_factory=list)


@dataclass
class FunctionContext:
    """Context specific to a function."""
    function_name: str
    business_purpose: str
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    complexity_level: str = "unknown"  # "low", "medium", "high", "very_high"
    error_conditions: List[str] = field(default_factory=list)
    performance_characteristics: List[str] = field(default_factory=list)
    usage_patterns: List[str] = field(default_factory=list)


@dataclass
class ClassContext:
    """Context specific to a class."""
    class_name: str
    business_purpose: str
    design_patterns: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    collaborations: List[str] = field(default_factory=list)
    inheritance_hierarchy: List[str] = field(default_factory=list)
    interface_contracts: List[str] = field(default_factory=list)
    state_management: List[str] = field(default_factory=list)
    lifecycle_methods: List[str] = field(default_factory=list)
    encapsulation_level: str = "unknown"  # "high", "medium", "low"


@dataclass
class SecurityContext:
    """Context about security considerations."""
    authentication_patterns: List[str] = field(default_factory=list)
    authorization_patterns: List[str] = field(default_factory=list)
    input_validation: List[str] = field(default_factory=list)
    data_sanitization: List[str] = field(default_factory=list)
    encryption_usage: List[str] = field(default_factory=list)
    security_vulnerabilities: List[str] = field(default_factory=list)
    secure_coding_practices: List[str] = field(default_factory=list)
    compliance_patterns: List[str] = field(default_factory=list)


@dataclass
class IntegrationContext:
    """Context about external integrations and dependencies."""
    database_integrations: List[str] = field(default_factory=list)
    api_integrations: List[str] = field(default_factory=list)
    message_queue_patterns: List[str] = field(default_factory=list)
    file_system_operations: List[str] = field(default_factory=list)
    network_operations: List[str] = field(default_factory=list)
    third_party_libraries: List[str] = field(default_factory=list)
    configuration_sources: List[str] = field(default_factory=list)
    deployment_patterns: List[str] = field(default_factory=list)


@dataclass
class CodeContext:
    """Comprehensive context extracted from code analysis."""
    business_context: BusinessContext
    error_handling_context: ErrorHandlingContext
    performance_context: PerformanceContext
    documentation_context: DocumentationContext
    security_context: Optional[SecurityContext] = None
    integration_context: Optional[IntegrationContext] = None
    function_contexts: List[FunctionContext] = field(default_factory=list)
    class_contexts: List[ClassContext] = field(default_factory=list)
    overall_quality_score: float = 0.0
    maintainability_score: float = 0.0
    testability_score: float = 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the extracted context."""
        return {
            "domain": self.business_context.domain_type.value,
            "purpose": self.business_context.business_purpose,
            "workflow_patterns": [p.value for p in self.business_context.workflow_patterns],
            "error_handling_strategies": [s.value for s in self.error_handling_context.recovery_strategies],
            "performance_patterns": [p.value for p in self.performance_context.optimization_patterns],
            "documentation_quality": self.documentation_context.docstring_quality,
            "function_count": len(self.function_contexts),
            "class_count": len(self.class_contexts),
            "overall_quality": self.overall_quality_score
        }


@dataclass
class ArchitecturalContext:
    """Context about architectural patterns and design decisions."""
    architectural_patterns: List[str] = field(default_factory=list)
    layer_separation: List[str] = field(default_factory=list)
    dependency_injection: List[str] = field(default_factory=list)
    service_patterns: List[str] = field(default_factory=list)
    data_access_patterns: List[str] = field(default_factory=list)
    messaging_patterns: List[str] = field(default_factory=list)
    configuration_management: List[str] = field(default_factory=list)
    deployment_patterns: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ContextExtractionResult:
    """Result of context extraction process."""
    success: bool
    context: Optional[CodeContext] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    lines_analyzed: int = 0
    functions_analyzed: int = 0
    classes_analyzed: int = 0