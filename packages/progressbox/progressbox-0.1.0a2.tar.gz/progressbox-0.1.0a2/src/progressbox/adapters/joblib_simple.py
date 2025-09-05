"""Simplified joblib integration for ProgressBox."""
from __future__ import annotations
from typing import Callable, Iterable, Any, Optional, List
from multiprocessing import Queue
from joblib import Parallel, delayed
import threading
import inspect
from progressbox import Progress, Config, Reporter
from progressbox.ipc import consume


def joblib_progress_simple(
    items: Iterable,
    func: Callable,
    n_jobs: int = 6,
    config: Optional[Config] = None,
    backend: str = "threading",  # Default to threading for reliability
    **joblib_kwargs
) -> List[Any]:
    """
    Execute func on items in parallel with progress tracking.
    
    Simplified version that manages progress display manually.
    """
    # Convert items to list to get length
    items_list = list(items)
    
    # Handle edge cases
    if not items_list:
        return []
    
    if len(items_list) == 1:
        return [func(items_list[0])]
    
    # Create config if not provided
    if config is None:
        config = Config(
            total=len(items_list), 
            n_workers=n_jobs,
            headless_ok=True,
            fail_safe=True
        )
    
    # Setup IPC components
    queue = Queue()
    progress = Progress(config)
    reporter = Reporter(queue)
    
    # Start progress display manually
    progress.start()
    
    # Start consumer thread without managing progress
    consumer = threading.Thread(
        target=consume,
        args=(queue, progress),
        kwargs={'manage_progress': False},  # We manage it ourselves
        daemon=True
    )
    consumer.start()
    
    # Wrap the user function to inject reporter if needed
    wrapped_func = _wrap_function_with_reporter(func, reporter)
    
    try:
        # Run parallel execution
        results = Parallel(n_jobs=n_jobs, backend=backend, **joblib_kwargs)(
            delayed(wrapped_func)(item, item_index) for item_index, item in enumerate(items_list)
        )
        
        return results
        
    finally:
        # Clean shutdown
        try:
            reporter.done()
            consumer.join(timeout=2.0)
        except:
            pass
        
        try:
            progress.close()
        except:
            pass


def _wrap_function_with_reporter(func: Callable, reporter: Reporter) -> Callable:
    """Wrap a user function to inject Reporter if the function accepts it."""
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    
    # Check if function expects a reporter parameter
    expects_reporter = (
        'reporter' in param_names or 
        len(param_names) >= 2
    )
    
    if expects_reporter and len(param_names) >= 2 and 'reporter' not in param_names:
        # Function expects reporter as second parameter
        def wrapper_with_reporter(item, item_index):
            return func(item, reporter)
        return wrapper_with_reporter
    
    elif 'reporter' in param_names:
        # Function has named 'reporter' parameter
        def wrapper_named_reporter(item, item_index):
            return func(item, reporter=reporter)
        return wrapper_named_reporter
    
    else:
        # Function doesn't expect reporter, use auto-tracking
        def wrapper_auto_track(item, item_index):
            reporter.task_start(item_index)
            try:
                result = func(item)
                reporter.task_finish(item_index)
                return result
            except Exception as e:
                reporter.task_error(item_index, str(e))
                raise
        return wrapper_auto_track