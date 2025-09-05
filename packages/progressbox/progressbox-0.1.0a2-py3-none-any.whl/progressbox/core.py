"""Main Progress tracker class."""
from __future__ import annotations
import sys
import time
import threading
import logging
from typing import Optional, Dict, Any, Hashable
from progressbox.config import Config
from progressbox.state import ProgressState
from progressbox.metrics import MetricsEngine
from progressbox.render.ascii import ASCIIRenderer
from progressbox.utils.terminal import is_jupyter, is_tty

# Configure logging
logger = logging.getLogger(__name__)


class Progress:
    """Main progress tracker class with thread-safe rendering and metrics.
    
    This class provides stage-aware progress tracking with real-time display
    updates, metrics calculation, and support for both terminal and Jupyter
    notebook environments.
    
    Features:
    - Thread-safe task tracking and updates
    - Real-time rendering in background thread
    - Automatic terminal/Jupyter detection
    - Stage timing and throughput metrics
    - Graceful error handling and cleanup
    - Snapshot/logging callbacks
    
    Example:
        >>> config = Config(total=100, n_workers=4)
        >>> with Progress(config) as progress:
        ...     for i in range(100):
        ...         progress.task_start(f"task_{i}", stage="processing")
        ...         # ... do work ...
        ...         progress.task_finish(f"task_{i}")
    """

    def __init__(self, config: Config):
        """Initialize with configuration.
        
        Args:
            config: Configuration object with display and behavior settings.
        """
        self.config = config
        self.state = ProgressState(total=config.total)
        self.metrics = MetricsEngine(
            ewma_alpha=config.ewma_alpha,
            cache_speed_factor=config.cache_speed_factor
        )
        
        # Initialize renderer based on environment and config
        self.renderer = ASCIIRenderer(config)
        
        # Thread management
        self._render_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        # Display state
        self._display_handle = None
        self._is_started = False
        self._is_closed = False
        self._last_render_time = 0.0
        self._last_snapshot_time = time.time()
        self._last_heartbeat_time = time.time()
        
        # Environment detection
        self._is_jupyter = is_jupyter()
        self._is_tty = is_tty()
        self._is_vscode = self._detect_vscode()
        
        # Initialize display handle for Jupyter if detected
        if self._is_jupyter:
            self._init_jupyter_display()
    
    def _detect_vscode(self) -> bool:
        """Detect if running in VS Code terminal."""
        import os
        return (
            os.environ.get('TERM_PROGRAM') == 'vscode' or
            os.environ.get('VSCODE_INJECTION') == '1' or
            'Code' in os.environ.get('TERMINAL_EMULATOR', '')
        )

    def _init_jupyter_display(self) -> None:
        """Initialize Jupyter display handle if available."""
        try:
            from IPython.display import display, HTML
            # Create initial empty display
            self._display_handle = display(HTML(""), display_id=True)
        except ImportError:
            logger.debug("IPython not available for Jupyter display")
            self._display_handle = None

    # Simple API methods - thread-safe task tracking
    def task_start(
        self,
        task_id: Hashable,
        *,
        worker: Optional[int] = None,
        cached: bool = False,
        meta: Optional[Dict[str, Any]] = None
    ) -> None:
        """Start tracking a task.
        
        Args:
            task_id: Unique identifier for the task.
            worker: Optional worker ID, will be auto-assigned if None.
            cached: Whether this task uses cached results.
            meta: Additional task metadata.
            
        Thread Safety:
            This method is thread-safe and can be called from multiple workers.
        """
        if self._is_closed:
            return
            
        try:
            assigned_worker = self.state.start_task(
                task_id=task_id,
                stage="starting",
                worker_id=worker,
                cached=cached,
                meta=meta
            )
            logger.debug(f"Started task {task_id} on worker {assigned_worker}")
        except Exception as e:
            if not self.config.fail_safe:
                raise
            logger.error(f"Failed to start task {task_id}: {e}")

    def task_update(
        self,
        task_id: Hashable,
        *,
        stage: Optional[str] = None,
        progress: Optional[float] = None,
        sub_progress: Optional[tuple[int, int]] = None
    ) -> None:
        """Update task state.
        
        Args:
            task_id: ID of the task to update.
            stage: New stage name, triggers timing if changed.
            progress: Overall progress ratio (0.0-1.0).
            sub_progress: Sub-task progress as (current, total).
            
        Thread Safety:
            This method is thread-safe and can be called from multiple workers.
        """
        if self._is_closed:
            return
            
        try:
            self.state.update_task(
                task_id=task_id,
                stage=stage,
                progress=progress,
                sub_progress=sub_progress
            )
            logger.debug(f"Updated task {task_id} - stage: {stage}, progress: {progress}")
        except KeyError:
            if not self.config.fail_safe:
                raise
            logger.warning(f"Attempted to update unknown task: {task_id}")
        except Exception as e:
            if not self.config.fail_safe:
                raise
            logger.error(f"Failed to update task {task_id}: {e}")

    def task_finish(self, task_id: Hashable) -> None:
        """Mark task as complete.
        
        Args:
            task_id: ID of the task to complete.
            
        Thread Safety:
            This method is thread-safe and can be called from multiple workers.
        """
        if self._is_closed:
            return
            
        try:
            # Get task info before finishing for metrics
            task_info = self.state.get_task_info(task_id)
            if task_info is None:
                if not self.config.fail_safe:
                    raise KeyError(f"Task {task_id} is not active")
                logger.warning(f"Attempted to finish unknown task: {task_id}")
                return
            
            # Finish task and get duration
            duration = self.state.finish_task(task_id)
            
            # Record metrics
            self.metrics.record_task_completion(duration, task_info.cached)
            
            # Record stage timing if we have stage info
            if hasattr(task_info, 'stage') and task_info.stage:
                stage_duration = task_info.get_stage_duration()
                self.metrics.record_stage_time(task_info.stage, stage_duration, task_info.cached)
            
            logger.debug(f"Finished task {task_id} in {duration:.3f}s")
        except KeyError:
            if not self.config.fail_safe:
                raise
            logger.warning(f"Attempted to finish unknown task: {task_id}")
        except Exception as e:
            if not self.config.fail_safe:
                raise
            logger.error(f"Failed to finish task {task_id}: {e}")

    # Rich API methods (aliases for convenience)
    def stage_transition(self, task_id: Hashable, stage: str) -> None:
        """Transition task to a new stage (alias for task_update).
        
        Args:
            task_id: ID of the task to update.
            stage: New stage name.
        """
        self.task_update(task_id, stage=stage)

    def stage_progress(self, task_id: Hashable, progress: float) -> None:
        """Update task progress (alias for task_update).
        
        Args:
            task_id: ID of the task to update.
            progress: Progress ratio (0.0-1.0).
        """
        self.task_update(task_id, progress=progress)

    def task_complete(self, task_id: Hashable) -> None:
        """Mark task complete (alias for task_finish).
        
        Args:
            task_id: ID of the task to complete.
        """
        self.task_finish(task_id)

    # Control methods
    def start(self) -> None:
        """Start the rendering loop.
        
        Initializes the renderer and starts the background rendering thread.
        Safe to call multiple times - subsequent calls are no-ops.
        """
        with self._lock:
            if self._is_started or self._is_closed:
                return
                
            try:
                # Initialize renderer
                self.renderer.start()
                
                # Skip rendering thread if disabled (for tests) or in headless mode
                if self.config.disable_threading:
                    self._is_started = True
                    logger.debug("Progress renderer started (threading disabled)")
                    return
                    
                # Skip rendering thread in headless non-TTY environments (like tests)
                # unless explicitly configured to run
                if not self._is_tty and self.config.headless_ok:
                    # In headless mode, we can skip the rendering thread
                    # unless user wants logging/snapshots
                    if not (self.config.on_snapshot or self.config.log_interval_s > 0):
                        self._is_started = True
                        logger.debug("Progress renderer started (headless mode, no thread)")
                        return
                
                # Start rendering thread with daemon mode for clean shutdown
                self._render_thread = threading.Thread(
                    target=self._render_loop,
                    name="ProgressBox-Renderer",
                    daemon=True
                )
                self._render_thread.start()
                
                self._is_started = True
                logger.debug("Progress renderer started")
            except Exception as e:
                if not self.config.fail_safe:
                    raise
                logger.error(f"Failed to start renderer: {e}")

    def stop(self) -> None:
        """Stop rendering but keep state.
        
        Stops the background rendering thread while preserving all state.
        The renderer can be restarted with start().
        """
        with self._lock:
            if self._is_closed:
                return
            
            # Even if _is_started is False, we still need to join the thread if it exists
            # because the render loop might have just finished but thread is still running
                
            try:
                # Signal stop to render thread
                self._stop_event.set()
                
                # Wait for thread to finish (longer timeout for cleaner shutdown)
                if self._render_thread and self._render_thread.is_alive():
                    self._render_thread.join(timeout=1.0)
                    
                    # If thread still alive after timeout, it's a daemon so let it go
                    if self._render_thread.is_alive():
                        logger.debug("Render thread still alive after timeout (daemon mode)")
                
                self._is_started = False
                self._stop_event.clear()
                logger.debug("Progress renderer stopped")
            except Exception as e:
                if not self.config.fail_safe:
                    raise
                logger.error(f"Error stopping renderer: {e}")

    def close(self) -> None:
        """Clean shutdown with final display.
        
        Stops rendering, displays final results, and performs cleanup.
        After calling close(), the Progress instance should not be reused.
        """
        if self._is_closed:
            return
            
        try:
            # Stop rendering thread if it exists - stop() has its own locking
            if self._render_thread is not None:
                self.stop()
            
            # Render final display only if we have a TTY or are in Jupyter
            if self._is_tty or self._is_jupyter:
                # For VS Code, show final progress then complete message
                if self._is_vscode:
                    # First show final progress state
                    self._render_once(force=True)
                    # Add newline to ensure cursor moves down properly
                    print()  # Move to next line for clean prompt return
                else:
                    self._render_once(force=True)
                    sys.stdout.write('\033[0m')  # Reset terminal attributes
                    print()  # This ensures command prompt appears below
                
                sys.stdout.flush()  # Force flush to ensure prompt returns
            
            # Call completion callback if configured
            if self.config.on_complete:
                try:
                    final_snapshot = self.state.create_snapshot()
                    final_snapshot['metrics'] = self.metrics.get_overall_stats()
                    self.config.on_complete(final_snapshot)
                except Exception as e:
                    logger.error(f"Error in completion callback: {e}")
            
            # Cleanup renderer
            self.renderer.close()
            
            self._is_closed = True
            logger.debug("Progress tracker closed")
        except Exception as e:
            if not self.config.fail_safe:
                raise
            logger.error(f"Error during close: {e}")

    def tick(self) -> None:
        """Force a render update.
        
        Manually triggers a display update, bypassing normal throttling.
        Useful for ensuring display is current before long-running operations.
        """
        if not self._is_closed:
            self._render_once(force=True)

    # Context manager implementation
    def __enter__(self):
        """Context manager entry - starts rendering."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures clean shutdown."""
        self.close()

    # Rendering loop and display management
    def _render_loop(self) -> None:
        """Background rendering loop with throttling and error handling."""
        refresh_interval = 1.0 / self.config.get_effective_refresh_rate()
        
        while not self._stop_event.is_set():
            try:
                # Render if enough time has passed
                self._render_once()
                
                # Handle periodic callbacks
                self._handle_periodic_callbacks()
                
                # Check if all tasks are complete
                if self.state.completed >= self.state.total:
                    # All tasks done - render one final time and exit
                    self._render_once(force=True)
                    logger.debug("All tasks complete, stopping render loop")
                    # No lock needed here - render loop is the only one setting this
                    self._is_started = False  # Mark as stopped
                    break
                
                # Sleep until next render cycle
                # Use wait() properly - it returns True if event is set
                if self._stop_event.wait(refresh_interval):
                    break  # Event was set, exit immediately
                
            except Exception as e:
                if not self.config.fail_safe:
                    raise
                logger.error(f"Error in render loop: {e}")
                # Continue rendering despite errors
                if self._stop_event.wait(refresh_interval):
                    break  # Event was set, exit immediately

    def _render_once(self, force: bool = False) -> None:
        """Perform a single render update with throttling.
        
        Args:
            force: If True, bypass throttling and always render.
        """
        current_time = time.time()
        
        # Check if we should render (throttling)
        if not force and not self.state.should_display_update(self.config.display_interval):
            return
        
        try:
            # Generate display content
            display_content = self.renderer.render(self.state, self.config)
            
            # Output based on environment
            if self._is_jupyter and self._display_handle:
                self._update_jupyter_display(display_content)
            elif self._is_tty:
                self._update_terminal_display(display_content)
            # In headless mode, we skip display updates unless logging is enabled
            
            self._last_render_time = current_time
            
        except Exception as e:
            if not self.config.fail_safe:
                raise
            logger.error(f"Render error: {e}")

    def _update_jupyter_display(self, content: str) -> None:
        """Update Jupyter notebook display."""
        try:
            from IPython.display import HTML
            # Wrap in <pre> for monospace formatting
            html_content = f"<pre style='font-family: monospace;'>{content}</pre>"
            self._display_handle.update(HTML(html_content))
        except ImportError:
            # Fallback to print if IPython not available
            print(content)

    def _update_terminal_display(self, content: str) -> None:
        """Update terminal display with proper cursor management."""
        
        # For non-interactive terminals, just print
        if not sys.stdout.isatty():
            print(content)
            return
            
        lines = content.split('\n')
        
        # Standard terminal handling for good terminals
        if hasattr(self, '_last_line_count') and self._last_line_count > 0:
            try:
                # Move cursor up to start of previous display
                sys.stdout.write(f'\033[{self._last_line_count}A')
                # Clear from cursor to end of screen
                sys.stdout.write('\033[0J')
            except (IOError, OSError):
                print(content)
                return
        else:
            # First render - ensure cursor is at column 0
            # Just move to beginning of line without clearing
            sys.stdout.write('\r')
        
        # Write new content normally
        sys.stdout.write(content)
        sys.stdout.flush()
        
        # Remember line count for next clear
        self._last_line_count = len(lines)

    def _handle_periodic_callbacks(self) -> None:
        """Handle snapshot callbacks and heartbeat logging."""
        current_time = time.time()
        
        # Handle snapshot callback
        if (self.config.on_snapshot and 
            self.config.snapshot_interval_s > 0 and
            current_time - self._last_snapshot_time >= self.config.snapshot_interval_s):
            
            try:
                snapshot = self.state.create_snapshot()
                snapshot['metrics'] = self.metrics.get_overall_stats()
                self.config.on_snapshot(snapshot)
                self._last_snapshot_time = current_time
            except Exception as e:
                if not self.config.fail_safe:
                    raise
                logger.error(f"Snapshot callback error: {e}")
        
        # Handle heartbeat logging
        if (self.config.log_interval_s > 0 and
            current_time - self._last_heartbeat_time >= self.config.log_interval_s):
            
            try:
                completion_ratio = self.state.get_completion_ratio()
                active_count = self.state.get_active_count()
                remaining = self.state.get_remaining_count()
                
                eta = self.metrics.calculate_eta(remaining)
                eta_str = f" ETA: {self._format_eta(eta)}" if eta else ""
                
                logger.info(
                    f"Progress: {completion_ratio*100:.1f}% "
                    f"({self.state.completed}/{self.state.total}) "
                    f"Active: {active_count}, Remaining: {remaining}{eta_str}"
                )
                self._last_heartbeat_time = current_time
            except Exception as e:
                if not self.config.fail_safe:
                    raise
                logger.error(f"Heartbeat logging error: {e}")

    def _format_eta(self, eta_seconds: Optional[float]) -> str:
        """Format ETA for logging."""
        if eta_seconds is None:
            return "unknown"
        
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            return f"{eta_seconds/60:.0f}m"
        else:
            hours = eta_seconds // 3600
            minutes = (eta_seconds % 3600) // 60
            return f"{hours:.0f}h {minutes:.0f}m"
