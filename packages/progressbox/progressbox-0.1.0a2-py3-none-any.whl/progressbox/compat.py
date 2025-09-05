"""Simple backwards compatibility layer - pure state tracking."""
import warnings
import time
from typing import Optional, Tuple

# Global flag to track if deprecation warning has been shown
_deprecation_warning_shown = False


class VLFProgressTracker:
    """
    Drop-in replacement for the original VLFProgressTracker.
    
    This version provides pure state tracking without using ProgressBox internals
    to ensure maximum compatibility and no hanging issues.
    
    .. deprecated:: 0.3.0
       Use progressbox.Progress instead. See migration guide at:
       https://github.com/your-repo/progressbox#migration-from-vlfprogresstracker
    """

    def __init__(self, total_gains: int, n_workers: int = 6, window_info: str = ""):
        # Show deprecation warning only once per session
        global _deprecation_warning_shown
        if not _deprecation_warning_shown:
            warnings.warn(
                "\n" + "="*70 + "\n"
                "VLFProgressTracker is deprecated and will be removed in v1.0.0\n"
                "\n"
                "Please migrate to the new ProgressBox API:\n"
                "\n"
                "  OLD (VLFProgressTracker):\n"
                "    tracker = VLFProgressTracker(total_gains=20, n_workers=6)\n"
                "    tracker.update(7.5, 'filtering', cached=False, sub_progress=(100, 1000))\n"
                "    tracker.final_display()\n"
                "\n"
                "  NEW (ProgressBox):\n"
                "    from progressbox import Progress, Config\n"
                "    config = Config(total=20, n_workers=6)\n"
                "    with Progress(config) as progress:\n"
                "        progress.task_start('task_7.5', cached=False)\n"
                "        progress.task_update('task_7.5', stage='filtering', sub_progress=(100, 1000))\n"
                "        progress.task_finish('task_7.5')\n"
                "\n"
                "Migration guide: https://github.com/your-repo/progressbox#migration\n"
                + "="*70,
                DeprecationWarning,
                stacklevel=2
            )
            _deprecation_warning_shown = True
        
        # Store original parameters for compatibility
        self.total = total_gains
        self.n_workers = n_workers
        self.window_info = window_info
        
        # Compatibility state tracking (like original)
        self.completed = 0
        self.cached_loads = 0
        self.global_start = time.time()
        self.all_completed = False
        
        # Stage timing tracking (like original)
        self.completion_times = []
        self.stage_durations = {}
        
        # Track current task states for compatibility
        self._active_tasks = {}  # gain -> task_info
        self._next_worker_id = 0
        
        # Display management (like original)
        self._last_display_time = 0
        self._display_interval = 0.1  # 100ms throttle like original

    def update(self, gain: float, stage: str, cached: bool = False, sub_progress: Optional[Tuple[int, int]] = None):
        """
        Compatibility wrapper for update method.
        
        Maps the original VLFProgressTracker.update() API to state tracking.
        
        Args:
            gain: Gain value (used as task_id)
            stage: Processing stage name
            cached: Whether this is a cached result
            sub_progress: Optional tuple of (current, total) for sub-progress
        """
        if stage == 'starting':
            # Starting a new task
            worker_id = self._next_worker_id % self.n_workers
            self._next_worker_id += 1
            
            self._active_tasks[gain] = {
                'worker_id': worker_id,
                'start_time': time.time(),
                'stage': 'starting',
                'stage_start': time.time(),
                'cached': cached
            }
            
            # Transition to first real stage (usually 'loading')
            self._active_tasks[gain]['stage'] = 'loading'
            self._active_tasks[gain]['stage_start'] = time.time()
            
        elif stage == 'completed':
            # Task completion
            if gain in self._active_tasks:
                task_info = self._active_tasks[gain]
                
                # Record stage duration if not starting
                if task_info['stage'] != 'starting':
                    duration = time.time() - task_info['stage_start']
                    if task_info['stage'] not in self.stage_durations:
                        self.stage_durations[task_info['stage']] = []
                    self.stage_durations[task_info['stage']].append(duration)
                
                # Record total completion time
                total_time = time.time() - task_info['start_time']
                self.completion_times.append(total_time)
                
                # Update cached count
                if task_info.get('cached', False):
                    self.cached_loads += 1
                
                # Update completion tracking
                del self._active_tasks[gain]
                self.completed += 1
                
                # Check if all completed
                if self.completed >= self.total:
                    self.all_completed = True
            else:
                # Fallback for tasks not properly tracked
                self.completed += 1
                
        else:
            # Stage update or sub-progress update
            if gain in self._active_tasks:
                task_info = self._active_tasks[gain]
                
                # Check if this is just a sub-progress update
                if sub_progress is not None and stage == task_info['stage']:
                    # Just update sub-progress, don't change stage
                    pass  # We don't need to store sub_progress for compatibility
                else:
                    # This is a real stage change
                    # Record previous stage duration if not starting
                    if task_info['stage'] != 'starting':
                        duration = time.time() - task_info['stage_start']
                        if task_info['stage'] not in self.stage_durations:
                            self.stage_durations[task_info['stage']] = []
                        self.stage_durations[task_info['stage']].append(duration)
                    
                    # Update to new stage
                    task_info['stage'] = stage
                    task_info['stage_start'] = time.time()
            else:
                # Task not tracked - create it on the fly (for robustness)
                worker_id = self._next_worker_id % self.n_workers
                self._next_worker_id += 1
                
                self._active_tasks[gain] = {
                    'worker_id': worker_id,
                    'start_time': time.time(),
                    'stage': stage,
                    'stage_start': time.time(),
                    'cached': cached
                }
        
        # Trigger display update with throttling (like original)
        self._maybe_display_update()

    def final_display(self):
        """
        Compatibility wrapper for final_display.
        
        Forces a final display showing 100% completion.
        """
        # Force completion state for final display
        self.all_completed = True
        
        # Clear any remaining active tasks
        self._active_tasks.clear()
        
        # Print final summary
        print(f"\rFinal: {self.completed}/{self.total} tasks completed (100.0%)")
        print(f"Cached operations: {self.cached_loads}")
        if self.completion_times:
            avg_time = sum(self.completion_times) / len(self.completion_times)
            print(f"Average time per task: {avg_time:.2f}s")
        
        # Show stage analysis if we have data
        if self.stage_durations:
            print("\nStage Analysis:")
            for stage_name, times in self.stage_durations.items():
                if times:
                    avg_time = sum(times) / len(times)
                    print(f"  {stage_name}: {avg_time:.2f}s avg ({len(times)} samples)")
    
    def _maybe_display_update(self):
        """Update display with throttling like the original VLFProgressTracker."""
        current_time = time.time()
        if current_time - self._last_display_time >= self._display_interval:
            # Simple progress update
            percentage = (self.completed / self.total) * 100 if self.total > 0 else 0
            active_tasks = len(self._active_tasks)
            elapsed = current_time - self.global_start
            
            # Calculate ETA if we have some completions
            eta_str = "calculating..."
            if len(self.completion_times) >= 2:
                avg_time = sum(self.completion_times) / len(self.completion_times)
                remaining = self.total - self.completed
                eta_seconds = remaining * avg_time
                if eta_seconds < 60:
                    eta_str = f"{eta_seconds:.0f}s"
                else:
                    eta_str = f"{eta_seconds/60:.0f}m"
            
            print(f"\rProgress: {self.completed}/{self.total} ({percentage:.1f}%) - Active: {active_tasks} - ETA: {eta_str} - Elapsed: {elapsed:.1f}s", end="", flush=True)
            self._last_display_time = current_time