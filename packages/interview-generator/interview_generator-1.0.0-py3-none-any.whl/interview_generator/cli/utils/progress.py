"""Progress display utilities for CLI."""

import threading
import time
from typing import Optional


class ProgressDisplay:
    """Simple progress display for CLI operations."""
    
    def __init__(self, show_spinner: bool = True):
        """
        Initialize progress display.
        
        Args:
            show_spinner: Whether to show animated spinner
        """
        self.show_spinner = show_spinner
        self.current_message = ""
        self.current_progress = 0.0
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Spinner characters
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0
    
    def start(self, message: str = "Processing..."):
        """Start the progress display."""
        self.current_message = message
        self.current_progress = 0.0
        self.is_running = True
        self.stop_event.clear()
        
        if self.show_spinner:
            self.thread = threading.Thread(target=self._spinner_loop, daemon=True)
            self.thread.start()
        else:
            print(f"🔄 {message}")
    
    def update(self, message: str, progress: float = None):
        """Update the progress display."""
        self.current_message = message
        if progress is not None:
            self.current_progress = max(0.0, min(1.0, progress))
        
        if not self.show_spinner:
            if progress is not None:
                percentage = int(self.current_progress * 100)
                print(f"🔄 {message} ({percentage}%)")
            else:
                print(f"🔄 {message}")
    
    def complete(self, message: str = "Completed!"):
        """Mark progress as complete."""
        self.stop()
        print(f"✅ {message}")
    
    def fail(self, message: str = "Failed!"):
        """Mark progress as failed."""
        self.stop()
        print(f"❌ {message}")
    
    def stop(self):
        """Stop the progress display."""
        self.is_running = False
        self.stop_event.set()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Clear the current line if spinner was running
        if self.show_spinner:
            print("\r" + " " * 80 + "\r", end="", flush=True)
    
    def _spinner_loop(self):
        """Main loop for spinner animation."""
        while self.is_running and not self.stop_event.is_set():
            spinner_char = self.spinner_chars[self.spinner_index]
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            
            # Create progress bar if progress is available
            if self.current_progress > 0:
                percentage = int(self.current_progress * 100)
                bar_length = 20
                filled = int(bar_length * self.current_progress)
                bar = "█" * filled + "░" * (bar_length - filled)
                display_text = f"\r{spinner_char} {self.current_message} [{bar}] {percentage}%"
            else:
                display_text = f"\r{spinner_char} {self.current_message}"
            
            print(display_text, end="", flush=True)
            
            # Wait for next update or stop signal
            if self.stop_event.wait(0.1):
                break


class SimpleProgressBar:
    """Simple progress bar without threading."""
    
    def __init__(self, total: int, width: int = 40):
        """
        Initialize progress bar.
        
        Args:
            total: Total number of items
            width: Width of progress bar in characters
        """
        self.total = total
        self.width = width
        self.current = 0
        self.start_time = time.time()
    
    def update(self, increment: int = 1, message: str = ""):
        """Update progress bar."""
        self.current = min(self.current + increment, self.total)
        
        # Calculate progress
        progress = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * progress)
        bar = "█" * filled + "░" * (self.width - filled)
        
        # Calculate percentage and ETA
        percentage = int(progress * 100)
        elapsed = time.time() - self.start_time
        
        if progress > 0 and self.current < self.total:
            eta = (elapsed / progress) * (1 - progress)
            eta_str = f" ETA: {int(eta)}s"
        else:
            eta_str = ""
        
        # Format display
        display = f"\r[{bar}] {percentage:3d}% ({self.current}/{self.total}){eta_str}"
        if message:
            display += f" - {message}"
        
        print(display, end="", flush=True)
        
        # Print newline when complete
        if self.current >= self.total:
            elapsed_str = f"{elapsed:.1f}s"
            print(f"\nCompleted in {elapsed_str}")
    
    def finish(self, message: str = "Done"):
        """Finish the progress bar."""
        self.current = self.total
        self.update(0, message)


def show_progress_for_items(items, description: str = "Processing"):
    """
    Context manager for showing progress over an iterable.
    
    Args:
        items: Iterable to process
        description: Description of the operation
    
    Usage:
        with show_progress_for_items(files, "Analyzing files") as progress:
            for item in progress:
                # Process item
                pass
    """
    class ProgressContext:
        def __init__(self, items, description):
            self.items = list(items)
            self.description = description
            self.progress_bar = SimpleProgressBar(len(self.items))
            self.index = 0
        
        def __enter__(self):
            print(f"🔄 {self.description}...")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                self.progress_bar.finish("Completed")
            else:
                print(f"\n❌ Failed: {exc_val}")
        
        def __iter__(self):
            for item in self.items:
                yield item
                self.index += 1
                self.progress_bar.update(1, f"Item {self.index}")
    
    return ProgressContext(items, description)


def format_progress_message(current: int, total: int, message: str = "") -> str:
    """Format a progress message."""
    percentage = int((current / total) * 100) if total > 0 else 0
    base_msg = f"({current}/{total}) {percentage}%"
    
    if message:
        return f"{base_msg} - {message}"
    return base_msg


def create_progress_callback(display: ProgressDisplay):
    """Create a progress callback function for use with pipeline."""
    def callback(message: str, progress: float):
        display.update(message, progress)
    
    return callback