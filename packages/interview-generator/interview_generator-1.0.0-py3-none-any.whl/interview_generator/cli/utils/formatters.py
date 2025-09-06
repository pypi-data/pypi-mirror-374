"""Output formatting utilities for CLI."""

import click
from typing import Dict, Any, List
from datetime import datetime

from ...core.pipeline import PipelineResult


def format_error(message: str) -> str:
    """Format error message with styling."""
    return click.style(f"❌ {message}", fg='red', bold=True)


def format_success(message: str) -> str:
    """Format success message with styling."""
    return click.style(f"✅ {message}", fg='green', bold=True)


def format_warning(message: str) -> str:
    """Format warning message with styling."""
    return click.style(f"⚠️  {message}", fg='yellow', bold=True)


def format_info(message: str) -> str:
    """Format info message with styling."""
    return click.style(f"ℹ️  {message}", fg='blue')


def format_progress(message: str, progress: float = None) -> str:
    """Format progress message with optional progress indicator."""
    if progress is not None:
        percentage = int(progress * 100)
        bar_length = 20
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"🔄 {message} [{bar}] {percentage}%"
    else:
        return f"🔄 {message}"


def format_results(result: PipelineResult) -> str:
    """Format pipeline results for display."""
    lines = []
    
    # Header
    lines.append("=" * 60)
    lines.append("📊 ANALYSIS RESULTS")
    lines.append("=" * 60)
    
    # Overall status
    if result.success:
        lines.append(format_success("Analysis completed successfully!"))
    else:
        lines.append(format_error("Analysis failed"))
    
    lines.append("")
    
    # Statistics
    stats = result.stats
    lines.append("📈 Processing Statistics:")
    lines.append(f"   Files discovered: {stats.files_discovered}")
    lines.append(f"   Files processed: {stats.files_processed}")
    
    if stats.files_failed > 0:
        lines.append(f"   Files failed: {click.style(str(stats.files_failed), fg='red')}")
    
    lines.append(f"   Functions analyzed: {stats.total_functions}")
    lines.append(f"   Classes analyzed: {stats.total_classes}")
    lines.append(f"   Processing time: {stats.processing_time:.2f}s")
    
    if result.success and result.question_result:
        lines.append("")
        lines.append("🎯 Question Generation:")
        lines.append(f"   Questions generated: {stats.total_questions}")
        lines.append(f"   API calls made: {stats.api_calls_made}")
        lines.append(f"   Tokens used: {stats.tokens_used:,}")
        
        # Question breakdown by category
        if result.question_result.questions:
            category_counts = {}
            difficulty_counts = {}
            
            for question in result.question_result.questions:
                cat = question.category.value
                diff = question.difficulty.value
                category_counts[cat] = category_counts.get(cat, 0) + 1
                difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            
            if category_counts:
                lines.append("")
                lines.append("📋 Question Categories:")
                for category, count in sorted(category_counts.items()):
                    lines.append(f"   {category.title()}: {count}")
            
            if difficulty_counts:
                lines.append("")
                lines.append("🎚️  Difficulty Levels:")
                for difficulty, count in sorted(difficulty_counts.items()):
                    lines.append(f"   {difficulty.title()}: {count}")
    
    # Output files
    if result.output_files:
        lines.append("")
        lines.append("📁 Output Files:")
        for file_path in result.output_files:
            lines.append(f"   📄 {file_path}")
    
    # Errors and warnings
    if stats.errors:
        lines.append("")
        lines.append(format_warning(f"Errors ({len(stats.errors)}):"))
        for error in stats.errors[:5]:  # Show first 5 errors
            lines.append(f"   • {error}")
        if len(stats.errors) > 5:
            lines.append(f"   ... and {len(stats.errors) - 5} more errors")
    
    if stats.warnings:
        lines.append("")
        lines.append(format_info(f"Warnings ({len(stats.warnings)}):"))
        for warning in stats.warnings[:3]:  # Show first 3 warnings
            lines.append(f"   • {warning}")
        if len(stats.warnings) > 3:
            lines.append(f"   ... and {len(stats.warnings) - 3} more warnings")
    
    # Performance summary
    if result.success and stats.files_processed > 0:
        lines.append("")
        lines.append("⚡ Performance Summary:")
        
        files_per_second = stats.files_processed / stats.processing_time if stats.processing_time > 0 else 0
        lines.append(f"   Processing rate: {files_per_second:.1f} files/second")
        
        if stats.api_calls_made > 0:
            questions_per_call = stats.total_questions / stats.api_calls_made
            lines.append(f"   Questions per API call: {questions_per_call:.1f}")
        
        if stats.tokens_used > 0 and stats.processing_time > 0:
            tokens_per_second = stats.tokens_used / stats.processing_time
            lines.append(f"   Token processing rate: {tokens_per_second:.0f} tokens/second")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_config_info(config_info: Dict[str, Any], show_secrets: bool = False) -> str:
    """Format configuration information for display."""
    lines = []
    
    # Basic info
    lines.append(f"📍 Config Source: {config_info.get('config_path', 'default')}")
    lines.append(f"🤖 LLM Model: {config_info.get('llm_model', 'unknown')}")
    lines.append(f"📄 Output Format: {config_info.get('output_format', 'unknown')}")
    lines.append(f"🔢 Max Questions/Category: {config_info.get('max_questions_per_category', 'unknown')}")
    
    # API key status
    api_configured = config_info.get('api_key_configured', False)
    if show_secrets and 'llm_api_key' in config_info:
        lines.append(f"🔑 API Key: {config_info['llm_api_key']}")
    else:
        status = "✅ Configured" if api_configured else "❌ Not configured"
        lines.append(f"🔑 API Key: {status}")
    
    # Categories
    categories = config_info.get('question_categories', [])
    if categories:
        lines.append(f"📋 Categories: {', '.join(categories)}")
    
    # Difficulty levels
    difficulties = config_info.get('difficulty_levels', [])
    if difficulties:
        lines.append(f"🎚️  Difficulties: {', '.join(difficulties)}")
    
    return "\n".join(lines)


def format_validation_results(results: Dict[str, Any]) -> str:
    """Format validation results for display."""
    lines = []
    
    overall_status = results.get('overall_status', 'unknown')
    
    # Status header
    if overall_status == 'success':
        lines.append(format_success("All validations passed"))
    elif overall_status == 'warning':
        lines.append(format_warning("Validation completed with warnings"))
    else:
        lines.append(format_error("Validation failed"))
    
    # Component details
    components = results.get('components', {})
    if components:
        lines.append("")
        lines.append("Component Status:")
        
        for component, status in components.items():
            component_name = component.replace('_', ' ').title()
            status_value = status.get('status', 'unknown')
            
            if status_value == 'success':
                icon = "✅"
            elif status_value == 'warning':
                icon = "⚠️"
            else:
                icon = "❌"
            
            message = status.get('message', status_value)
            lines.append(f"  {icon} {component_name}: {message}")
    
    # Errors and warnings
    errors = results.get('errors', [])
    warnings = results.get('warnings', [])
    
    if errors:
        lines.append("")
        lines.append("Errors:")
        for error in errors:
            lines.append(f"  ❌ {error}")
    
    if warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in warnings:
            lines.append(f"  ⚠️  {warning}")
    
    return "\n".join(lines)


def format_file_list(files: List[str], max_display: int = 10) -> str:
    """Format a list of files for display."""
    lines = []
    
    if not files:
        return "No files found"
    
    lines.append(f"Found {len(files)} files:")
    
    for i, file_path in enumerate(files):
        if i >= max_display:
            lines.append(f"  ... and {len(files) - max_display} more files")
            break
        lines.append(f"  📄 {file_path}")
    
    return "\n".join(lines)


def format_table(headers: List[str], rows: List[List[str]], 
                title: str = None) -> str:
    """Format data as a simple table."""
    if not rows:
        return "No data to display"
    
    lines = []
    
    if title:
        lines.append(title)
        lines.append("=" * len(title))
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format header
    header_line = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Format rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(row_line)
    
    return "\n".join(lines)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def truncate_text(text: str, max_length: int = 80) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_timestamp(timestamp: datetime = None) -> str:
    """Format timestamp for display."""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")