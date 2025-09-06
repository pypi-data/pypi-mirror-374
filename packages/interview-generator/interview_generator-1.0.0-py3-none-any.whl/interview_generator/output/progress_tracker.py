"""Progress tracking for long-running operations."""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class ProgressStatus(Enum):
    """Status of a progress tracking operation."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class ProgressStep:
    """Represents a step in a multi-step process."""
    name: str
    description: str
    weight: float = 1.0  # Relative weight for progress calculation
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class ProgressState:
    """Current state of progress tracking."""
    current_step: int = 0
    total_steps: int = 0
    current_step_progress: float = 0.0  # 0.0 to 1.0
    overall_progress: float = 0.0  # 0.0 to 1.0
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    current_operation: str = ""
    steps: List[ProgressStep] = field(default_factory=list)


class ProgressTracker:
    """Tracks progress for long-running operations with callbacks and display options."""
    
    def __init__(self, show_progress_bar: bool = True, update_interval: float = 0.5):
        """
        Initialize progress tracker.
        
        Args:
            show_progress_bar: Whether to display progress bar in console
            update_interval: How often to update display (seconds)
        """
        self.show_progress_bar = show_progress_bar
        self.update_interval = update_interval
        
        self.state = ProgressState()
        self.callbacks: List[Callable[[ProgressState], None]] = []
        self.lock = threading.Lock()
        self.cancelled = False
        self.paused = False
        
        # Display state
        self._last_display_time = 0
        self._display_thread: Optional[threading.Thread] = None
        self._stop_display = False
    
    def initialize(self, steps: List[str], step_descriptions: Optional[List[str]] = None,
                  step_weights: Optional[List[float]] = None) -> None:
        """
        Initialize progress tracking with steps.
        
        Args:
            steps: List of step names
            step_descriptions: Optional descriptions for each step
            step_weights: Optional weights for each step (for progress calculation)
        """
        with self.lock:
            self.state.steps = []
            self.state.total_steps = len(steps)
            self.state.current_step = 0
            self.state.overall_progress = 0.0
            self.state.status = ProgressStatus.NOT_STARTED
            
            # Create step objects
            for i, step_name in enumerate(steps):
                description = step_descriptions[i] if step_descriptions else step_name
                weight = step_weights[i] if step_weights else 1.0
                
                step = ProgressStep(
                    name=step_name,
                    description=description,
                    weight=weight
                )
                self.state.steps.append(step)
    
    def start(self, operation_name: str = "Processing") -> None:
        """Start progress tracking."""
        with self.lock:
            self.state.status = ProgressStatus.IN_PROGRESS
            self.state.start_time = datetime.now()
            self.state.current_operation = operation_name
            self.cancelled = False
            self.paused = False
        
        # Start display thread if needed
        if self.show_progress_bar:
            self._start_display_thread()
        
        self._notify_callbacks()
        logger.info(f"Started progress tracking for: {operation_name}")
    
    def update_step(self, step_index: int, progress: float = 0.0,
                   status: Optional[ProgressStatus] = None,
                   message: Optional[str] = None) -> None:
        """
        Update progress for a specific step.
        
        Args:
            step_index: Index of the step to update
            progress: Progress within the step (0.0 to 1.0)
            status: Optional status update
            message: Optional status message
        """
        with self.lock:
            if 0 <= step_index < len(self.state.steps):
                step = self.state.steps[step_index]
                
                # Update step status
                if status:
                    if status == ProgressStatus.IN_PROGRESS and not step.start_time:
                        step.start_time = datetime.now()
                    elif status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED]:
                        step.end_time = datetime.now()
                    
                    step.status = status
                
                # Update current step tracking
                if step_index >= self.state.current_step:
                    self.state.current_step = step_index
                    self.state.current_step_progress = max(0.0, min(1.0, progress))
                
                # Update overall progress
                self._calculate_overall_progress()
                
                # Update current operation message
                if message:
                    self.state.current_operation = message
        
        self._notify_callbacks()
    
    def advance_step(self, message: Optional[str] = None) -> None:
        """Advance to the next step."""
        with self.lock:
            if self.state.current_step < len(self.state.steps):
                # Mark current step as completed
                if self.state.current_step < len(self.state.steps):
                    current_step = self.state.steps[self.state.current_step]
                    current_step.status = ProgressStatus.COMPLETED
                    current_step.end_time = datetime.now()
                
                # Move to next step
                self.state.current_step += 1
                self.state.current_step_progress = 0.0
                
                # Start next step if it exists
                if self.state.current_step < len(self.state.steps):
                    next_step = self.state.steps[self.state.current_step]
                    next_step.status = ProgressStatus.IN_PROGRESS
                    next_step.start_time = datetime.now()
                    
                    if message:
                        self.state.current_operation = message
                    else:
                        self.state.current_operation = next_step.description
                
                self._calculate_overall_progress()
        
        self._notify_callbacks()
    
    def complete(self, message: str = "Completed") -> None:
        """Mark the entire operation as completed."""
        with self.lock:
            # Mark all remaining steps as completed
            for step in self.state.steps[self.state.current_step:]:
                if step.status == ProgressStatus.NOT_STARTED:
                    step.status = ProgressStatus.COMPLETED
                    step.start_time = step.start_time or datetime.now()
                    step.end_time = datetime.now()
            
            self.state.status = ProgressStatus.COMPLETED
            self.state.overall_progress = 1.0
            self.state.current_operation = message
        
        self._stop_display_thread()
        self._notify_callbacks()
        logger.info("Progress tracking completed")
    
    def fail(self, error_message: str) -> None:
        """Mark the operation as failed."""
        with self.lock:
            self.state.status = ProgressStatus.FAILED
            self.state.current_operation = f"Failed: {error_message}"
            
            # Mark current step as failed
            if self.state.current_step < len(self.state.steps):
                current_step = self.state.steps[self.state.current_step]
                current_step.status = ProgressStatus.FAILED
                current_step.error_message = error_message
                current_step.end_time = datetime.now()
        
        self._stop_display_thread()
        self._notify_callbacks()
        logger.error(f"Progress tracking failed: {error_message}")
    
    def cancel(self) -> None:
        """Cancel the operation."""
        with self.lock:
            self.cancelled = True
            self.state.status = ProgressStatus.CANCELLED
            self.state.current_operation = "Cancelled"
        
        self._stop_display_thread()
        self._notify_callbacks()
        logger.info("Progress tracking cancelled")
    
    def pause(self) -> None:
        """Pause the operation."""
        with self.lock:
            self.paused = True
            self.state.status = ProgressStatus.PAUSED
        
        self._notify_callbacks()
        logger.info("Progress tracking paused")
    
    def resume(self) -> None:
        """Resume the operation."""
        with self.lock:
            if self.paused:
                self.paused = False
                self.state.status = ProgressStatus.IN_PROGRESS
        
        self._notify_callbacks()
        logger.info("Progress tracking resumed")
    
    def add_callback(self, callback: Callable[[ProgressState], None]) -> None:
        """Add a callback to be called on progress updates."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[ProgressState], None]) -> None:
        """Remove a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_state(self) -> ProgressState:
        """Get current progress state."""
        with self.lock:
            # Create a copy to avoid threading issues
            return ProgressState(
                current_step=self.state.current_step,
                total_steps=self.state.total_steps,
                current_step_progress=self.state.current_step_progress,
                overall_progress=self.state.overall_progress,
                status=self.state.status,
                start_time=self.state.start_time,
                estimated_completion=self.state.estimated_completion,
                current_operation=self.state.current_operation,
                steps=self.state.steps.copy()
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the progress tracking."""
        state = self.get_state()
        
        summary = {
            'status': state.status.value,
            'overall_progress': state.overall_progress,
            'current_step': state.current_step + 1 if state.current_step < state.total_steps else state.total_steps,
            'total_steps': state.total_steps,
            'current_operation': state.current_operation
        }
        
        if state.start_time:
            elapsed = datetime.now() - state.start_time
            summary['elapsed_time'] = str(elapsed).split('.')[0]  # Remove microseconds
            
            if state.overall_progress > 0 and state.status == ProgressStatus.IN_PROGRESS:
                estimated_total = elapsed / state.overall_progress
                remaining = estimated_total - elapsed
                summary['estimated_remaining'] = str(remaining).split('.')[0]
        
        return summary
    
    def _calculate_overall_progress(self) -> None:
        """Calculate overall progress based on step weights and completion."""
        if not self.state.steps:
            self.state.overall_progress = 0.0
            return
        
        total_weight = sum(step.weight for step in self.state.steps)
        completed_weight = 0.0
        
        for i, step in enumerate(self.state.steps):
            if step.status == ProgressStatus.COMPLETED:
                completed_weight += step.weight
            elif i == self.state.current_step and step.status == ProgressStatus.IN_PROGRESS:
                completed_weight += step.weight * self.state.current_step_progress
        
        self.state.overall_progress = completed_weight / total_weight if total_weight > 0 else 0.0
        
        # Update estimated completion time
        if self.state.start_time and self.state.overall_progress > 0:
            elapsed = datetime.now() - self.state.start_time
            estimated_total = elapsed / self.state.overall_progress
            self.state.estimated_completion = self.state.start_time + estimated_total
    
    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks."""
        state = self.get_state()
        for callback in self.callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def _start_display_thread(self) -> None:
        """Start the display thread for console progress bar."""
        if self._display_thread and self._display_thread.is_alive():
            return
        
        self._stop_display = False
        self._display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self._display_thread.start()
    
    def _stop_display_thread(self) -> None:
        """Stop the display thread."""
        self._stop_display = True
        if self._display_thread and self._display_thread.is_alive():
            self._display_thread.join(timeout=1.0)
    
    def _display_loop(self) -> None:
        """Main loop for console display."""
        while not self._stop_display:
            current_time = time.time()
            if current_time - self._last_display_time >= self.update_interval:
                self._update_display()
                self._last_display_time = current_time
            
            time.sleep(0.1)  # Small sleep to prevent busy waiting
    
    def _update_display(self) -> None:
        """Update console display."""
        try:
            state = self.get_state()
            
            # Create progress bar
            bar_width = 40
            filled = int(bar_width * state.overall_progress)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Format percentage
            percentage = state.overall_progress * 100
            
            # Format step info
            step_info = f"Step {state.current_step + 1}/{state.total_steps}" if state.total_steps > 0 else ""
            
            # Format time info
            time_info = ""
            if state.start_time:
                elapsed = datetime.now() - state.start_time
                elapsed_str = str(elapsed).split('.')[0]
                time_info = f" | {elapsed_str}"
                
                if state.estimated_completion and state.status == ProgressStatus.IN_PROGRESS:
                    remaining = state.estimated_completion - datetime.now()
                    if remaining.total_seconds() > 0:
                        remaining_str = str(remaining).split('.')[0]
                        time_info += f" | ETA: {remaining_str}"
            
            # Create display line
            display_line = f"\r[{bar}] {percentage:5.1f}% | {step_info} | {state.current_operation}{time_info}"
            
            # Print with carriage return to overwrite previous line
            print(display_line, end='', flush=True)
            
            # Print newline if completed or failed
            if state.status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.CANCELLED]:
                print()  # New line to preserve final status
                
        except Exception as e:
            logger.error(f"Error updating progress display: {e}")


class SimpleProgressTracker:
    """Simplified progress tracker for basic use cases."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize simple progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the operation
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1, message: Optional[str] = None) -> None:
        """Update progress."""
        self.current = min(self.current + increment, self.total)
        
        if message:
            current_desc = message
        else:
            current_desc = self.description
        
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        
        # Simple progress bar
        bar_width = 30
        filled = int(bar_width * (self.current / self.total)) if self.total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        
        print(f"\r[{bar}] {percentage:5.1f}% | {self.current}/{self.total} | {current_desc}", 
              end='', flush=True)
        
        if self.current >= self.total:
            elapsed = datetime.now() - self.start_time
            print(f"\nCompleted in {elapsed}")
    
    def finish(self, message: str = "Completed") -> None:
        """Mark as finished."""
        self.current = self.total
        elapsed = datetime.now() - self.start_time
        print(f"\n{message} in {elapsed}")


# Convenience functions for common use cases

def track_progress(items, description: str = "Processing", 
                  callback: Optional[Callable] = None):
    """
    Context manager for tracking progress over an iterable.
    
    Args:
        items: Iterable to process
        description: Description of the operation
        callback: Optional callback for each item
    """
    class ProgressContext:
        def __init__(self, items, description, callback):
            self.items = list(items)
            self.description = description
            self.callback = callback
            self.tracker = SimpleProgressTracker(len(self.items), description)
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                self.tracker.finish()
            else:
                print(f"\nFailed: {exc_val}")
        
        def __iter__(self):
            for item in self.items:
                yield item
                if self.callback:
                    self.callback(item)
                self.tracker.update()
    
    return ProgressContext(items, description, callback)