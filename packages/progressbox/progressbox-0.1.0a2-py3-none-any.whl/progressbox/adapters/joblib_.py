"""
Joblib integration for ProgressBox.

This module provides seamless integration between joblib.Parallel and ProgressBox
for progress tracking in parallel computations.

Components:
-----------
1. joblib_progress() - Main function for easy parallel execution with progress
2. ProgressParallel - Subclass of joblib.Parallel with progress infrastructure  
3. with_progress - Decorator for adding progress to existing parallel functions

Usage Examples:
--------------

Basic usage (automatic progress tracking):
>>> from progressbox.adapters import joblib_progress
>>> 
>>> def process_item(item):
>>>     # Your processing logic here
>>>     return item * 2
>>> 
>>> results = joblib_progress(
>>>     items=range(100),
>>>     func=process_item,
>>>     n_jobs=4
>>> )

Advanced usage with progress stages:
>>> def process_with_stages(item, reporter):
>>>     reporter.task_start(item)
>>>     reporter.task_update(item, stage="loading", progress=0.2)
>>>     # ... do loading work ...
>>>     reporter.task_update(item, stage="processing", progress=0.8)
>>>     # ... do processing work ...
>>>     reporter.task_finish(item)
>>>     return result
>>> 
>>> results = joblib_progress(
>>>     items=range(50),
>>>     func=process_with_stages,
>>>     n_jobs=6,
>>>     stages=["loading", "processing", "saving"]
>>> )

Decorator pattern:
>>> @with_progress(total=100, n_workers=4)
>>> def parallel_job(items, func):
>>>     return Parallel(n_jobs=4)(delayed(func)(i) for i in items)
>>> 
>>> results = parallel_job(range(100), process_item)

Notes:
------
- Use backend="threading" for better reliability with progress tracking
- The loky backend may have issues with multiprocessing Queue serialization
- Consumer threads use timeouts to prevent hanging on cleanup
"""
from __future__ import annotations
from typing import Callable, Iterable, Any, Optional, List, Union
from multiprocessing import Queue
from joblib import Parallel, delayed
import threading
import functools
import inspect
from progressbox import Progress, Config, Reporter
from progressbox.ipc import consume


def joblib_progress(
    items: Iterable,
    func: Callable,
    n_jobs: int = 6,
    config: Optional[Config] = None,
    backend: str = "loky",
    **joblib_kwargs
) -> List[Any]:
    """
    Execute func on items in parallel with progress tracking.

    This function provides seamless integration with joblib.Parallel while
    automatically injecting progress reporting capabilities into user functions.

    Parameters
    ----------
    items : Iterable
        Items to process
    func : Callable
        Function to apply to each item. The function signature can be:
        - func(item) -> result
        - func(item, reporter) -> result  (if it accepts a Reporter)
    n_jobs : int, default=6
        Number of parallel jobs
    config : Config, optional
        Progress configuration. If None, will create default config.
    backend : str, default="loky"
        Joblib backend to use ("loky", "threading", "multiprocessing")
    **joblib_kwargs
        Additional arguments for joblib.Parallel

    Returns
    -------
    List[Any]
        Results from parallel execution

    Example
    -------
    >>> def process_item(item, reporter):
    ...     reporter.task_start(item, cached=False)
    ...     # Do work...
    ...     reporter.task_finish(item)
    ...     return item * 2
    >>> 
    >>> results = joblib_progress(
    ...     items=range(100),
    ...     func=process_item,
    ...     n_jobs=4,
    ...     stages=["loading", "processing", "saving"]
    ... )
    """
    # Convert items to list to get length
    items_list = list(items)
    
    # Handle empty input
    if not items_list:
        return []
    
    # Handle single item (bypass parallel execution)
    if len(items_list) == 1:
        return [func(items_list[0])]
    
    # Create config if not provided
    if config is None:
        config = Config(total=len(items_list), n_workers=n_jobs)
    
    # Setup IPC components
    queue = Queue()
    progress = Progress(config)
    reporter = Reporter(queue)
    
    # Start consumer thread
    consumer = threading.Thread(
        target=consume,
        args=(queue, progress),
        kwargs={'manage_progress': True},  # Let consume manage progress start/close
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
        
    except Exception as e:
        # Re-raise the exception after cleanup
        raise e
        
    finally:
        # Always clean up, regardless of success or failure
        try:
            # Signal completion
            reporter.done()
            # Wait for consumer with timeout to prevent hanging
            consumer.join(timeout=3.0)
            
            # If consumer is still alive, it might be stuck - log warning
            if consumer.is_alive():
                import warnings
                warnings.warn("Progress consumer thread did not finish cleanly", RuntimeWarning)
        except Exception:
            # Ignore cleanup errors to avoid masking original exceptions
            pass


class ProgressParallel(Parallel):
    """
    A subclass of joblib.Parallel that sets up progress tracking infrastructure.
    
    This class sets up the progress tracking components (queue, progress display, consumer)
    but requires that your functions explicitly use the Reporter for progress tracking.
    This approach is more reliable than trying to automatically wrap all functions.
    
    Parameters
    ----------
    config : Config, optional
        ProgressBox configuration
    auto_track : bool, default=True
        Whether to set up progress tracking (should be True)
    **parallel_kwargs
        Arguments passed to joblib.Parallel
        
    Example
    -------
    >>> def process_item(item, reporter):  # Function must accept reporter
    ...     reporter.task_start(item)
    ...     # Do work...
    ...     reporter.task_finish(item)
    ...     return item * 2
    >>> 
    >>> config = Config(total=100, n_workers=4)
    >>> parallel = ProgressParallel(config=config, n_jobs=4)
    >>> reporter = parallel.get_reporter()
    >>> results = parallel(delayed(process_item)(i, reporter) for i in range(100))
    
    Note
    ----
    For automatic progress tracking without Reporter injection, use joblib_progress() instead.
    """
    
    def __init__(self, config: Optional[Config] = None, auto_track: bool = True, **parallel_kwargs):
        super().__init__(**parallel_kwargs)
        self.config = config
        self.auto_track = auto_track
        self._queue = None
        self._progress = None
        self._reporter = None
        self._consumer_thread = None
        
    def __call__(self, iterable):
        """Execute the parallel computation with progress tracking."""
        if not self.auto_track:
            return super().__call__(iterable)
            
        # Convert to list to count items
        delayed_funcs = list(iterable)
        
        # Handle empty input
        if not delayed_funcs:
            return []
            
        # Create config if needed
        if self.config is None:
            self.config = Config(total=len(delayed_funcs), n_workers=self.n_jobs or 1)
        
        # Setup progress tracking
        self._setup_progress_tracking()
        
        try:
            # For ProgressParallel, we'll use a simpler approach
            # Just execute the original delayed functions and let them report progress themselves
            # This is simpler and more reliable than trying to wrap them
            
            # Execute with parent Parallel
            results = super().__call__(delayed_funcs)
            
            return results
            
        finally:
            self._cleanup_progress_tracking()
    
    def get_reporter(self) -> Optional[Reporter]:
        """Get the Reporter instance for use in worker functions.
        
        Returns
        -------
        Optional[Reporter]
            Reporter instance if progress tracking is set up, None otherwise.
            
        Example
        -------
        >>> parallel = ProgressParallel(config=config, n_jobs=4)
        >>> reporter = parallel.get_reporter()
        >>> # Use reporter in your worker functions
        """
        return self._reporter
    
    def _setup_progress_tracking(self):
        """Setup the progress tracking components."""
        self._queue = Queue()
        self._progress = Progress(self.config)
        self._reporter = Reporter(self._queue)
        
        # Start consumer thread
        self._consumer_thread = threading.Thread(
            target=consume,
            args=(self._queue, self._progress),
            kwargs={'manage_progress': True},  # Let consume manage progress start/close
            daemon=True
        )
        self._consumer_thread.start()
    
    def _cleanup_progress_tracking(self):
        """Clean up progress tracking components."""
        try:
            if self._reporter:
                self._reporter.done()
            if self._consumer_thread:
                self._consumer_thread.join(timeout=3.0)
                if self._consumer_thread.is_alive():
                    import warnings
                    warnings.warn("ProgressParallel consumer thread did not finish cleanly", RuntimeWarning)
        except Exception:
            # Ignore cleanup errors
            pass
    


def with_progress(
    total: Optional[int] = None,
    n_workers: int = 6, 
    stages: Optional[List[str]] = None,
    **config_kwargs
):
    """
    Decorator to add progress tracking to parallel execution functions.
    
    This decorator wraps functions that use joblib.Parallel internally,
    automatically setting up progress tracking.
    
    Parameters
    ----------
    total : int, optional
        Total number of items to process. If None, will try to infer.
    n_workers : int, default=6
        Number of workers for display purposes
    stages : List[str], optional
        List of stage names for progress tracking
    **config_kwargs
        Additional configuration parameters for Config
    
    Example
    -------
    >>> @with_progress(total=100, n_workers=4)
    ... def parallel_job(items, func):
    ...     return Parallel(n_jobs=4)(delayed(func)(i) for i in items)
    >>> 
    >>> results = parallel_job(range(100), lambda x: x**2)
    """
    def decorator(parallel_func: Callable) -> Callable:
        @functools.wraps(parallel_func)
        def wrapper(*args, **kwargs):
            # Try to infer total if not provided
            inferred_total = total
            if inferred_total is None:
                # Look for common parameter names that might contain items
                sig = inspect.signature(parallel_func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                for param_name in ['items', 'data', 'values', 'tasks']:
                    if param_name in bound_args.arguments:
                        try:
                            inferred_total = len(list(bound_args.arguments[param_name]))
                            break
                        except (TypeError, AttributeError):
                            continue
                
                if inferred_total is None:
                    inferred_total = 100  # Default fallback
            
            # Create config
            config_params = {
                'total': inferred_total,
                'n_workers': n_workers,
                **config_kwargs
            }
            config = Config(**config_params)
            
            # Setup progress tracking
            queue = Queue()
            progress = Progress(config)
            reporter = Reporter(queue)
            
            # Start consumer
            consumer = threading.Thread(
                target=consume,
                args=(queue, progress),
                kwargs={'manage_progress': True},  # Let consume manage progress start/close
                daemon=True
            )
            consumer.start()
            
            try:
                # Inject reporter into kwargs if the function accepts it
                if 'reporter' in inspect.signature(parallel_func).parameters:
                    kwargs['reporter'] = reporter
                
                # Call the original function
                result = parallel_func(*args, **kwargs)
                
                return result
                
            finally:
                # Cleanup with timeout
                try:
                    reporter.done()
                    consumer.join(timeout=3.0)
                    if consumer.is_alive():
                        import warnings
                        warnings.warn("with_progress consumer thread did not finish cleanly", RuntimeWarning)
                except Exception:
                    pass
        
        return wrapper
    return decorator


def _wrap_function_with_reporter(func: Callable, reporter: Reporter) -> Callable:
    """
    Wrap a user function to inject Reporter if the function accepts it.
    
    This function inspects the user's function signature and determines
    whether it expects a Reporter parameter. If so, it injects it.
    
    Parameters
    ----------
    func : Callable
        User function to wrap
    reporter : Reporter
        Reporter instance to inject
        
    Returns
    -------
    Callable
        Wrapped function that handles reporter injection
    """
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    
    # Check if function expects a reporter parameter
    expects_reporter = (
        'reporter' in param_names or 
        len(param_names) >= 2  # Assume second param might be reporter
    )
    
    if expects_reporter and len(param_names) >= 2:
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
