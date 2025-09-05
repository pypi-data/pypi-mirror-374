"""Worker-side progress reporter."""
from __future__ import annotations
from multiprocessing import Queue
from typing import Optional, Dict, Any, Hashable
from progressbox.events import ProgressEvent

class Reporter:
    """Worker-side progress reporter for multiprocessing.
    
    This class provides a thread-safe, picklable interface for workers
    to report progress events back to the main process via a multiprocessing Queue.
    
    The Reporter is designed to work with joblib's loky backend and native
    multiprocessing.Pool, handling serialization gracefully across process boundaries.
    """

    def __init__(self, queue: Queue):
        """Initialize with multiprocessing queue.
        
        Args:
            queue (Queue): Multiprocessing queue for sending events to main process.
            
        Raises:
            TypeError: If queue is not a multiprocessing Queue.
        """
        if not hasattr(queue, 'put') or not hasattr(queue, 'get'):
            raise TypeError("queue must be a multiprocessing Queue-like object")
        self.queue = queue

    def task_start(
        self,
        task_id: Hashable,
        *,
        worker: Optional[int] = None,
        cached: bool = False,
        meta: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send task start event.
        
        Args:
            task_id (Hashable): Unique identifier for the task.
            worker (Optional[int]): Worker ID, if known.
            cached (bool): Whether this task used cached results. Default: False.
            meta (Optional[Dict[str, Any]]): Additional task metadata.
            
        Raises:
            ValueError: If task_id is None.
        """
        if task_id is None:
            raise ValueError("task_id cannot be None for task events")
        
        event = ProgressEvent(
            type="start",
            task_id=task_id,
            worker_id=worker,
            cached=cached,
            meta=meta
        )
        try:
            self.queue.put(event)
        except Exception:
            # Fail gracefully - don't crash the worker process
            pass

    def task_update(
        self,
        task_id: Hashable,
        *,
        stage: Optional[str] = None,
        progress: Optional[float] = None,
        sub_progress: Optional[tuple[int, int]] = None
    ) -> None:
        """Send task update event.
        
        Args:
            task_id (Hashable): Unique identifier for the task.
            stage (Optional[str]): Current processing stage name.
            progress (Optional[float]): Overall progress ratio (0.0-1.0).
            sub_progress (Optional[tuple[int, int]]): Sub-task progress (current, total).
            
        Raises:
            ValueError: If task_id is None or progress is out of range.
        """
        if task_id is None:
            raise ValueError("task_id cannot be None for task events")
        
        if progress is not None:
            if not isinstance(progress, (int, float)):
                raise ValueError("progress must be a number")
            if not (0.0 <= progress <= 1.0):
                raise ValueError(f"progress must be between 0.0 and 1.0, got {progress}")
        
        if sub_progress is not None:
            if not isinstance(sub_progress, (tuple, list)) or len(sub_progress) != 2:
                raise ValueError("sub_progress must be a 2-tuple (current, total)")
            current, total = sub_progress
            if not isinstance(current, int) or not isinstance(total, int):
                raise ValueError("sub_progress values must be integers")
            if current < 0 or total < 0:
                raise ValueError("sub_progress values must be non-negative")
            if current > total:
                raise ValueError("sub_progress current cannot exceed total")
        
        event = ProgressEvent(
            type="update",
            task_id=task_id,
            stage=stage,
            progress=progress,
            sub_progress=sub_progress
        )
        try:
            self.queue.put(event)
        except Exception:
            # Fail gracefully - don't crash the worker process
            pass

    def task_finish(self, task_id: Hashable) -> None:
        """Send task finish event.
        
        Args:
            task_id (Hashable): Unique identifier for the task.
            
        Raises:
            ValueError: If task_id is None.
        """
        if task_id is None:
            raise ValueError("task_id cannot be None for task events")
        
        event = ProgressEvent(type="finish", task_id=task_id)
        try:
            self.queue.put(event)
        except Exception:
            # Fail gracefully - don't crash the worker process
            pass

    def task_error(self, task_id: Hashable, error_msg: str) -> None:
        """Send task error event.
        
        Args:
            task_id (Hashable): Unique identifier for the task.
            error_msg (str): Error message describing what went wrong.
            
        Raises:
            ValueError: If task_id is None.
        """
        if task_id is None:
            raise ValueError("task_id cannot be None for task events")
        
        event = ProgressEvent(type="error", task_id=task_id, error_msg=error_msg)
        try:
            self.queue.put(event)
        except Exception:
            # Fail gracefully - don't crash the worker process
            pass

    def done(self) -> None:
        """Signal that all tasks are complete.
        
        This should be called once all workers have finished processing
        to signal the consumer thread to shut down gracefully.
        """
        event = ProgressEvent(type="done", task_id=None)
        try:
            self.queue.put(event)
        except Exception:
            # Fail gracefully - don't crash the worker process
            pass

    def __getstate__(self):
        """Support for pickling - return state for serialization."""
        return {'queue': self.queue}
    
    def __setstate__(self, state):
        """Support for unpickling - restore state after deserialization."""
        self.queue = state['queue']
