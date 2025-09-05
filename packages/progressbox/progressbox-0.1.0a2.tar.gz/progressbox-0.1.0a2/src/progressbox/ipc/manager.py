"""IPC Manager for handling multiprocessing progress tracking."""
from __future__ import annotations
from multiprocessing import Queue
import threading
from typing import Optional
from progressbox.core import Progress
from progressbox.config import Config
from progressbox.ipc.queue import consume
from progressbox.ipc.reporter import Reporter


class Manager:
    """Manages the IPC system for multiprocessing progress tracking.
    
    This class coordinates a multiprocessing Queue, Progress instance, 
    and consumer thread to provide a complete IPC solution for tracking
    progress across multiple worker processes.
    
    The Manager handles the lifecycle of the consumer thread and provides
    clean startup/shutdown semantics.
    
    Example:
        >>> config = Config(total=100, n_workers=4)
        >>> manager = Manager(config)
        >>> manager.start()
        >>> reporter = manager.get_reporter()
        >>> # Use reporter in worker processes...
        >>> manager.stop()
        >>> manager.wait()
    """
    
    def __init__(self, config: Config, *, refresh_hz: Optional[float] = None):
        """Initialize the IPC Manager.
        
        Args:
            config (Config): ProgressBox configuration.
            refresh_hz (Optional[float]): Consumer refresh rate in Hz.
                If None, uses config.refresh_hz. Default: None.
        """
        self.config = config
        self.refresh_hz = refresh_hz or config.refresh_hz
        
        # Core components
        self.queue: Queue = Queue()
        self.progress: Progress = Progress(config)
        self.reporter: Reporter = Reporter(self.queue)
        
        # Thread management
        self.consumer_thread: Optional[threading.Thread] = None
        self._running = False
        self._started = False
        
    def start(self) -> None:
        """Start the consumer thread and progress display.
        
        This method is idempotent - calling it multiple times has no effect
        after the first call.
        
        Raises:
            RuntimeError: If the manager has already been stopped.
        """
        if self._started:
            return
            
        if self.consumer_thread is not None and not self.consumer_thread.is_alive():
            raise RuntimeError("Manager has been stopped and cannot be restarted")
        
        self._running = True
        self._started = True
        
        # Start the progress display first
        try:
            self.progress.start()
        except Exception as e:
            # If display start fails, continue without display
            import logging
            logging.warning(f"Failed to start progress display: {e}")
        
        # Start the consumer thread (not daemon so we can join it properly)
        # Note: manage_progress=False since we manually manage progress lifecycle
        self.consumer_thread = threading.Thread(
            target=consume,
            args=(self.queue, self.progress, self.refresh_hz),
            kwargs={'manage_progress': False},
            daemon=False,
            name="ProgressBox-Consumer"
        )
        self.consumer_thread.start()
    
    def stop(self, *, timeout: Optional[float] = 5.0) -> None:
        """Signal the consumer thread to stop.
        
        Sends a "done" event to the queue to trigger graceful shutdown
        of the consumer loop.
        
        Args:
            timeout (Optional[float]): Maximum time to wait for thread to stop.
                If None, wait indefinitely. Default: 5.0 seconds.
                
        Note:
            This method is non-blocking. Use wait() to ensure the thread
            has actually terminated.
        """
        if not self._started or not self._running:
            return
            
        self._running = False
        
        # Send done signal to consumer
        try:
            self.reporter.done()
        except Exception:
            # Queue might be full or closed, that's ok
            pass
    
    def wait(self, *, timeout: Optional[float] = 5.0) -> bool:
        """Wait for the consumer thread to finish.
        
        Args:
            timeout (Optional[float]): Maximum time to wait in seconds.
                If None, wait indefinitely. Default: 5.0 seconds.
                
        Returns:
            bool: True if thread finished within timeout, False if timeout occurred.
        """
        if self.consumer_thread is None or not self._started:
            return True
            
        self.consumer_thread.join(timeout=timeout)
        return not self.consumer_thread.is_alive()
    
    def get_reporter(self) -> Reporter:
        """Get the Reporter instance for use in worker processes.
        
        Returns:
            Reporter: Reporter instance that can be pickled and sent to workers.
            
        Note:
            The returned Reporter is safe to use across process boundaries
            and can be pickled for use with joblib or multiprocessing.Pool.
        """
        return self.reporter
    
    def is_running(self) -> bool:
        """Check if the manager is currently running.
        
        Returns:
            bool: True if the consumer thread is active.
        """
        return (
            self._running and 
            self.consumer_thread is not None and 
            self.consumer_thread.is_alive()
        )
    
    def __enter__(self):
        """Context manager entry - start the manager."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop and wait for cleanup."""
        self.stop()
        self.wait()
        # Close the progress display
        try:
            self.progress.close()
        except Exception as e:
            import logging
            logging.warning(f"Failed to close progress display: {e}")
    
    def __del__(self):
        """Destructor - ensure clean shutdown."""
        try:
            if self._running:
                self.stop()
                # Don't wait in destructor as it might block
        except Exception:
            # Ignore exceptions during cleanup
            pass