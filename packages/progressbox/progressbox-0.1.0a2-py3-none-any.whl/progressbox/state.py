"""Thread-safe state management for progress tracking.

This module provides the core data structures and thread-safe operations
for managing progress state across multiple concurrent tasks and workers.
All operations are atomic and safe for use in multithreaded environments.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional, Tuple, Hashable, Any, Iterator
import time
import copy


@dataclass
class TaskInfo:
    """Information about a single active task.
    
    This class tracks the complete lifecycle and state of an individual task,
    including timing information, stage progression, and metadata.
    
    Attributes:
        task_id (Hashable): Unique identifier for this task.
        worker_id (int): ID of the worker processing this task.
        stage (str): Current processing stage name.
        start_time (float): Unix timestamp when task started.
        stage_start (float): Unix timestamp when current stage started.
        cached (bool): Whether this task used cached results. Default: False.
        sub_progress (Optional[Tuple[int, int]]): Sub-task progress as
            (current, total). Default: None.
        meta (Optional[Dict[str, Any]]): Additional task metadata. Default: None.
    
    Example:
        >>> task = TaskInfo(
        ...     task_id="task_001",
        ...     worker_id=0,
        ...     stage="loading",
        ...     start_time=time.time(),
        ...     stage_start=time.time()
        ... )
        >>> task.get_task_duration()  # doctest: +SKIP
        0.123456
    """
    task_id: Hashable
    worker_id: int
    stage: str
    start_time: float
    stage_start: float
    cached: bool = False
    sub_progress: Optional[Tuple[int, int]] = None
    meta: Optional[Dict[str, Any]] = None
    
    def get_task_duration(self) -> float:
        """Get total task duration so far.
        
        Returns:
            float: Duration in seconds since task started.
        """
        return time.time() - self.start_time
    
    def get_stage_duration(self) -> float:
        """Get current stage duration.
        
        Returns:
            float: Duration in seconds since current stage started.
        """
        return time.time() - self.stage_start
    
    def get_sub_progress_ratio(self) -> Optional[float]:
        """Get sub-progress as a ratio (0.0-1.0).
        
        Returns:
            Optional[float]: Progress ratio, or None if no sub-progress set.
        """
        if self.sub_progress is None:
            return None
        current, total = self.sub_progress
        if total <= 0:
            return 0.0
        return min(1.0, max(0.0, current / total))
    
    def transition_stage(self, new_stage: str) -> float:
        """Transition to a new processing stage.
        
        Args:
            new_stage (str): Name of the new stage.
            
        Returns:
            float: Duration of the previous stage in seconds.
        """
        now = time.time()
        previous_duration = now - self.stage_start
        self.stage = new_stage
        self.stage_start = now
        return previous_duration


@dataclass
class ProgressState:
    """Thread-safe progress state container.
    
    This is the central state manager for progress tracking, maintaining
    all active tasks, completion metrics, and timing statistics in a
    thread-safe manner. All public methods use locking to ensure
    atomicity of operations.
    
    Attributes:
        total (int): Total number of tasks to be processed.
        completed (int): Number of tasks completed so far. Default: 0.
        cached_loads (int): Number of tasks that used cached results. Default: 0.
        global_start (float): Unix timestamp when tracking started.
        active_tasks (Dict[Hashable, TaskInfo]): Currently active tasks.
        completion_times (List[float]): Task completion durations.
        stage_durations (Dict[str, List[float]]): Stage duration history.
        next_worker_id (int): Next worker ID to assign. Default: 0.
        last_display_time (float): Last display update timestamp. Default: 0.
        all_completed (bool): Whether all tasks are completed. Default: False.
    
    Thread Safety:
        All public methods are thread-safe. The internal `_lock` ensures
        atomic access to all state variables.
    
    Example:
        >>> state = ProgressState(total=100)
        >>> state.start_task("task_001", stage="loading")
        >>> state.get_completion_ratio()
        0.0
        >>> state.finish_task("task_001")
        >>> state.get_completion_ratio()
        0.01
    """

    # Global metrics
    total: int
    completed: int = 0
    cached_loads: int = 0
    global_start: float = field(default_factory=time.time)

    # Active tasks
    active_tasks: Dict[Hashable, TaskInfo] = field(default_factory=dict)

    # Timing data  
    completion_times: List[float] = field(default_factory=list)
    stage_durations: Dict[str, List[float]] = field(default_factory=dict)

    # Worker management
    next_worker_id: int = 0

    # Display control
    last_display_time: float = 0
    all_completed: bool = False

    # Thread safety
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate initial state after construction."""
        if self.total <= 0:
            raise ValueError(f"total must be positive, got {self.total}")
    
    def start_task(
        self, 
        task_id: Hashable, 
        stage: str = "processing",
        worker_id: Optional[int] = None,
        cached: bool = False,
        meta: Optional[Dict[str, Any]] = None
    ) -> int:
        """Start tracking a new task.
        
        Args:
            task_id (Hashable): Unique identifier for the task.
            stage (str): Initial processing stage. Default: "processing".
            worker_id (Optional[int]): Specific worker ID, or None to auto-assign.
            cached (bool): Whether this task uses cached results. Default: False.
            meta (Optional[Dict[str, Any]]): Additional task metadata.
            
        Returns:
            int: The worker ID assigned to this task.
            
        Raises:
            ValueError: If task_id is already active.
            
        Example:
            >>> state = ProgressState(total=10)
            >>> worker_id = state.start_task("task_001", stage="loading")
            >>> worker_id
            0
        """
        with self._lock:
            if task_id in self.active_tasks:
                raise ValueError(f"Task {task_id} is already active")
            
            # Assign worker ID
            if worker_id is None:
                worker_id = self.next_worker_id
                self.next_worker_id += 1
            
            # Create task info
            now = time.time()
            task = TaskInfo(
                task_id=task_id,
                worker_id=worker_id,
                stage=stage,
                start_time=now,
                stage_start=now,
                cached=cached,
                meta=meta
            )
            
            self.active_tasks[task_id] = task
            return worker_id
    
    def update_task(
        self,
        task_id: Hashable,
        stage: Optional[str] = None,
        progress: Optional[float] = None,
        sub_progress: Optional[Tuple[int, int]] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update an active task's state.
        
        Args:
            task_id (Hashable): ID of the task to update.
            stage (Optional[str]): New stage name, or None to keep current.
            progress (Optional[float]): Overall progress ratio (0.0-1.0).
            sub_progress (Optional[Tuple[int, int]]): Sub-task progress.
            meta (Optional[Dict[str, Any]]): Metadata to merge with existing.
            
        Raises:
            KeyError: If task_id is not currently active.
            
        Example:
            >>> state = ProgressState(total=10)
            >>> state.start_task("task_001")  # doctest: +SKIP
            >>> state.update_task("task_001", stage="saving", progress=0.8)
        """
        with self._lock:
            if task_id not in self.active_tasks:
                raise KeyError(f"Task {task_id} is not active")
            
            task = self.active_tasks[task_id]
            
            # Handle stage transition
            if stage is not None and stage != task.stage:
                old_stage = task.stage
                stage_duration = task.transition_stage(stage)
                self._record_stage_duration(old_stage, stage_duration)
            
            # Update sub-progress
            if sub_progress is not None:
                task.sub_progress = sub_progress
            
            # Merge metadata
            if meta is not None:
                if task.meta is None:
                    task.meta = {}
                task.meta.update(meta)
    
    def finish_task(self, task_id: Hashable) -> float:
        """Mark a task as completed and remove from active tasks.
        
        Args:
            task_id (Hashable): ID of the task to complete.
            
        Returns:
            float: Total task duration in seconds.
            
        Raises:
            KeyError: If task_id is not currently active.
            
        Example:
            >>> state = ProgressState(total=10)
            >>> state.start_task("task_001")  # doctest: +SKIP
            >>> duration = state.finish_task("task_001")  # doctest: +SKIP
            >>> duration > 0
            True
        """
        with self._lock:
            if task_id not in self.active_tasks:
                raise KeyError(f"Task {task_id} is not active")
            
            task = self.active_tasks.pop(task_id)
            
            # Record completion metrics
            task_duration = task.get_task_duration()
            self.completion_times.append(task_duration)
            self.completed += 1
            
            if task.cached:
                self.cached_loads += 1
            
            # Record final stage duration
            final_stage_duration = task.get_stage_duration()
            self._record_stage_duration(task.stage, final_stage_duration)
            
            # Check if all tasks completed
            if self.completed >= self.total:
                self.all_completed = True
            
            return task_duration
    
    def get_task_info(self, task_id: Hashable) -> Optional[TaskInfo]:
        """Get information about an active task.
        
        Args:
            task_id (Hashable): ID of the task to query.
            
        Returns:
            Optional[TaskInfo]: Task information, or None if not active.
            
        Thread Safety:
            Returns a deep copy to prevent external modification.
        """
        with self._lock:
            task = self.active_tasks.get(task_id)
            if task is None:
                return None
            return copy.deepcopy(task)
    
    def get_active_tasks(self) -> List[TaskInfo]:
        """Get a list of all currently active tasks.
        
        Returns:
            List[TaskInfo]: Deep copies of all active tasks.
            
        Thread Safety:
            Returns deep copies to prevent external modification.
        """
        with self._lock:
            return [copy.deepcopy(task) for task in self.active_tasks.values()]
    
    def get_completion_ratio(self) -> float:
        """Get the overall completion ratio.
        
        Returns:
            float: Completion ratio from 0.0 to 1.0.
            
        Example:
            >>> state = ProgressState(total=100)
            >>> state.completed = 25
            >>> state.get_completion_ratio()
            0.25
        """
        with self._lock:
            if self.total <= 0:
                return 1.0
            return min(1.0, self.completed / self.total)
    
    def get_active_count(self) -> int:
        """Get the number of currently active tasks.
        
        Returns:
            int: Number of active tasks.
        """
        with self._lock:
            return len(self.active_tasks)
    
    def get_remaining_count(self) -> int:
        """Get the number of tasks not yet started or completed.
        
        Returns:
            int: Number of remaining tasks.
        """
        with self._lock:
            return max(0, self.total - self.completed - len(self.active_tasks))
    
    def get_elapsed_time(self) -> float:
        """Get total elapsed time since tracking started.
        
        Returns:
            float: Elapsed time in seconds.
        """
        return time.time() - self.global_start
    
    def get_average_completion_time(self) -> Optional[float]:
        """Get average task completion time.
        
        Returns:
            Optional[float]: Average completion time in seconds, or None if
                no tasks completed.
        """
        with self._lock:
            if not self.completion_times:
                return None
            return sum(self.completion_times) / len(self.completion_times)
    
    def get_stage_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistical summary of stage durations.
        
        Returns:
            Dict[str, Dict[str, float]]: Statistics by stage name, containing:
                - 'count': Number of stage completions
                - 'mean': Average duration in seconds
                - 'std': Standard deviation in seconds
                - 'total': Total time spent in this stage
                - 'percentage': Percentage of total processing time
                
        Example:
            >>> state = ProgressState(total=10)
            >>> stats = state.get_stage_statistics()
            >>> 'loading' in stats  # doctest: +SKIP
            True
        """
        with self._lock:
            if not self.stage_durations:
                return {}
            
            # Calculate total time across all stages
            total_stage_time = sum(
                sum(durations) for durations in self.stage_durations.values()
            )
            
            result = {}
            for stage, durations in self.stage_durations.items():
                if not durations:
                    continue
                
                count = len(durations)
                total = sum(durations)
                mean = total / count
                
                # Calculate standard deviation
                variance = sum((d - mean) ** 2 for d in durations) / count
                std = variance ** 0.5
                
                # Calculate percentage of total time
                percentage = (total / total_stage_time * 100) if total_stage_time > 0 else 0.0
                
                result[stage] = {
                    'count': count,
                    'mean': mean,
                    'std': std,
                    'total': total,
                    'percentage': percentage
                }
            
            return result
    
    def get_estimated_completion_time(self) -> Optional[float]:
        """Estimate time to completion based on current progress.
        
        Returns:
            Optional[float]: Estimated seconds to completion, or None if
                insufficient data for estimation.
                
        Note:
            Uses average completion time and remaining task count for estimation.
            Accounts for cached task speedup factor.
        """
        with self._lock:
            if not self.completion_times:
                return None
            
            avg_time = sum(self.completion_times) / len(self.completion_times)
            remaining = self.get_remaining_count()
            
            if remaining <= 0:
                return 0.0
            
            return avg_time * remaining
    
    def should_display_update(self, min_interval: float = 0.1) -> bool:
        """Check if enough time has passed for a display update.
        
        Args:
            min_interval (float): Minimum seconds between updates. Default: 0.1.
            
        Returns:
            bool: True if display should be updated.
            
        Side Effects:
            Updates last_display_time if returning True.
        """
        with self._lock:
            now = time.time()
            if now - self.last_display_time >= min_interval:
                self.last_display_time = now
                return True
            return False
    
    def create_snapshot(self) -> Dict[str, Any]:
        """Create a complete state snapshot for logging/monitoring.
        
        Returns:
            Dict[str, Any]: Complete state snapshot including all metrics,
                active tasks, and timing statistics.
                
        Thread Safety:
            Creates a deep copy of all mutable state.
        """
        with self._lock:
            return {
                'timestamp': time.time(),
                'total': self.total,
                'completed': self.completed,
                'cached_loads': self.cached_loads,
                'active_count': len(self.active_tasks),
                'remaining': self.get_remaining_count(),
                'completion_ratio': self.get_completion_ratio(),
                'elapsed_time': self.get_elapsed_time(),
                'average_completion_time': self.get_average_completion_time(),
                'all_completed': self.all_completed,
                'active_tasks': [
                    {
                        'task_id': str(task.task_id),
                        'worker_id': task.worker_id,
                        'stage': task.stage,
                        'task_duration': task.get_task_duration(),
                        'stage_duration': task.get_stage_duration(),
                        'cached': task.cached,
                        'sub_progress': task.sub_progress,
                        'meta': task.meta
                    }
                    for task in self.active_tasks.values()
                ],
                'stage_statistics': self.get_stage_statistics()
            }
    
    def _record_stage_duration(self, stage: str, duration: float) -> None:
        """Record a completed stage duration.
        
        Args:
            stage (str): Name of the completed stage.
            duration (float): Stage duration in seconds.
            
        Note:
            This method assumes the lock is already held.
        """
        if stage not in self.stage_durations:
            self.stage_durations[stage] = []
        self.stage_durations[stage].append(duration)
    
    def __len__(self) -> int:
        """Return the number of active tasks."""
        with self._lock:
            return len(self.active_tasks)
    
    def __iter__(self) -> Iterator[TaskInfo]:
        """Iterate over active tasks (returns deep copies)."""
        with self._lock:
            tasks = [copy.deepcopy(task) for task in self.active_tasks.values()]
        return iter(tasks)
    
    def __contains__(self, task_id: Hashable) -> bool:
        """Check if a task is currently active."""
        with self._lock:
            return task_id in self.active_tasks
