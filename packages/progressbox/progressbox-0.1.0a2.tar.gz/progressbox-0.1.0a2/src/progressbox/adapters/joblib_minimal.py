"""Minimal joblib integration for testing."""
from __future__ import annotations
from typing import Callable, Iterable, Any, List
from joblib import Parallel, delayed
import inspect


def joblib_progress_minimal(
    items: Iterable,
    func: Callable,
    n_jobs: int = 6,
    backend: str = "threading",
    **joblib_kwargs
) -> List[Any]:
    """
    Execute func on items in parallel (minimal version for testing).
    
    This version just wraps joblib without any progress display.
    Used to verify that our function wrapping logic works.
    """
    # Convert items to list
    items_list = list(items)
    
    # Handle edge cases
    if not items_list:
        return []
    
    if len(items_list) == 1:
        return [func(items_list[0])]
    
    # Create a minimal mock reporter for testing
    class MockReporter:
        def task_start(self, task_id, **kwargs):
            print(f"Starting task {task_id}")
            
        def task_update(self, task_id, **kwargs):
            print(f"Updating task {task_id}: {kwargs}")
            
        def task_finish(self, task_id):
            print(f"Finished task {task_id}")
            
        def task_error(self, task_id, error_msg):
            print(f"Error in task {task_id}: {error_msg}")
    
    mock_reporter = MockReporter()
    
    # Wrap the user function
    wrapped_func = _wrap_function_with_reporter(func, mock_reporter)
    
    # Run parallel execution
    results = Parallel(n_jobs=n_jobs, backend=backend, **joblib_kwargs)(
        delayed(wrapped_func)(item, item_index) for item_index, item in enumerate(items_list)
    )
    
    return results


def _wrap_function_with_reporter(func: Callable, reporter) -> Callable:
    """Wrap a user function to inject Reporter if the function accepts it."""
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    
    # Check if function expects a reporter parameter
    if 'reporter' in param_names:
        # Function has named 'reporter' parameter
        def wrapper_named_reporter(item, item_index):
            return func(item, reporter=reporter)
        return wrapper_named_reporter
    
    elif len(param_names) >= 2:
        # Function expects reporter as second parameter
        def wrapper_with_reporter(item, item_index):
            return func(item, reporter)
        return wrapper_with_reporter
    
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