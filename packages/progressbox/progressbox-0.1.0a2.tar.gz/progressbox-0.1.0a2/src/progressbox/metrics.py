"""Metrics calculation engines for progress monitoring.

This module provides production-ready metrics calculation components for the 
ProgressBox library:

1. WelfordAccumulator: Online calculation of mean, variance, and other statistics
   using Welford's numerically stable algorithm. Supports merging accumulators
   and tracking min/max values.

2. EWMA: Exponentially Weighted Moving Average with confidence intervals.
   Provides smooth estimates of time-varying signals with configurable smoothing
   factors and weighted updates.

3. MetricsEngine: Comprehensive metrics engine that combines both Welford and
   EWMA for stage timing analysis, ETA calculations, throughput metrics, and
   cache speed adjustments.

4. Helper functions: Time formatting, ETA calculations, and throughput calculations.

All classes are designed for numerical stability, production reliability, and
comprehensive documentation with type hints throughout.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Tuple, Any, Union
import math
import time
from collections import defaultdict

class WelfordAccumulator:
    """Online calculation of mean and variance using Welford's algorithm.
    
    This accumulator provides numerically stable calculation of statistics
    for a stream of values without storing all values in memory.
    
    Attributes:
        n: Number of values processed
        mean: Current mean value
        M2: Sum of squared differences from mean (internal)
        min_val: Minimum value seen
        max_val: Maximum value seen
    """

    def __init__(self) -> None:
        """Initialize empty accumulator."""
        self.n: int = 0
        self.mean: float = 0.0
        self.M2: float = 0.0
        self.min_val: Optional[float] = None
        self.max_val: Optional[float] = None

    def update(self, x: float) -> None:
        """Add a new value to the accumulator.
        
        Args:
            x: New value to add
        """
        self.n += 1
        
        # Update min/max
        if self.min_val is None or x < self.min_val:
            self.min_val = x
        if self.max_val is None or x > self.max_val:
            self.max_val = x
        
        # Welford's algorithm for mean and variance
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2

    def reset(self) -> None:
        """Reset accumulator to initial state."""
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0
        self.min_val = None
        self.max_val = None

    def merge(self, other: 'WelfordAccumulator') -> 'WelfordAccumulator':
        """Merge another accumulator into this one.
        
        Args:
            other: Another WelfordAccumulator to merge
            
        Returns:
            New WelfordAccumulator with combined statistics
        """
        if other.n == 0:
            # Return copy of self
            result = WelfordAccumulator()
            result.n = self.n
            result.mean = self.mean
            result.M2 = self.M2
            result.min_val = self.min_val
            result.max_val = self.max_val
            return result
        
        if self.n == 0:
            # Return copy of other
            result = WelfordAccumulator()
            result.n = other.n
            result.mean = other.mean
            result.M2 = other.M2
            result.min_val = other.min_val
            result.max_val = other.max_val
            return result
        
        # Merge two non-empty accumulators
        result = WelfordAccumulator()
        result.n = self.n + other.n
        
        # Combined mean
        delta = other.mean - self.mean
        result.mean = self.mean + delta * other.n / result.n
        
        # Combined variance (Chan's formula)
        result.M2 = self.M2 + other.M2 + delta * delta * self.n * other.n / result.n
        
        # Combined min/max
        if self.min_val is not None and other.min_val is not None:
            result.min_val = min(self.min_val, other.min_val)
        elif self.min_val is not None:
            result.min_val = self.min_val
        elif other.min_val is not None:
            result.min_val = other.min_val
            
        if self.max_val is not None and other.max_val is not None:
            result.max_val = max(self.max_val, other.max_val)
        elif self.max_val is not None:
            result.max_val = self.max_val
        elif other.max_val is not None:
            result.max_val = other.max_val
        
        return result

    @property
    def count(self) -> int:
        """Number of values processed."""
        return self.n

    @property
    def minimum(self) -> Optional[float]:
        """Minimum value seen, or None if no values."""
        return self.min_val

    @property
    def maximum(self) -> Optional[float]:
        """Maximum value seen, or None if no values."""
        return self.max_val

    @property
    def variance(self) -> float:
        """Calculate sample variance."""
        if self.n < 2:
            return 0.0
        return self.M2 / (self.n - 1)  # Sample variance (Bessel's correction)

    @property
    def population_variance(self) -> float:
        """Calculate population variance."""
        return self.M2 / self.n if self.n > 0 else 0.0

    @property
    def std(self) -> float:
        """Calculate sample standard deviation."""
        return math.sqrt(self.variance)

    @property
    def population_std(self) -> float:
        """Calculate population standard deviation."""
        return math.sqrt(self.population_variance)

class EWMA:
    """Exponentially weighted moving average with confidence intervals.
    
    Provides smooth estimates of time-varying signals with configurable
    smoothing factor and confidence interval calculations.
    
    Attributes:
        alpha: Smoothing factor (0 < alpha <= 1)
        value: Current EWMA value
        variance: Estimated variance for confidence intervals
        n: Number of updates (for initialization)
    """

    def __init__(self, alpha: float = 0.2) -> None:
        """Initialize EWMA.
        
        Args:
            alpha: Smoothing factor. Higher values = more responsive.
                  Typical range: 0.1 (smooth) to 0.3 (responsive)
        
        Raises:
            ValueError: If alpha is not in (0, 1] range
        """
        if not (0 < alpha <= 1):
            raise ValueError(f"Alpha must be in (0, 1], got {alpha}")
        
        self.alpha: float = alpha
        self.value: Optional[float] = None
        self.variance: Optional[float] = None
        self.n: int = 0

    def update(self, x: float, weight: float = 1.0) -> float:
        """Update EWMA with new value.
        
        Args:
            x: New observation
            weight: Relative weight of this observation (default 1.0)
                   Higher weights make this observation more influential
        
        Returns:
            Updated EWMA value
        """
        self.n += 1
        effective_alpha = self.alpha * weight
        
        if self.value is None:
            # First observation
            self.value = x
            self.variance = 0.0
        else:
            # Update value
            old_value = self.value
            self.value = effective_alpha * x + (1 - effective_alpha) * old_value
            
            # Update variance estimate for confidence intervals
            # Using exponential smoothing on squared deviations
            deviation = x - old_value
            if self.variance is None:
                self.variance = deviation * deviation
            else:
                self.variance = effective_alpha * deviation * deviation + (1 - effective_alpha) * self.variance
        
        return self.value

    def weighted_update(self, x: float, weight: float) -> float:
        """Update with explicit weight (alias for update with weight).
        
        Args:
            x: New observation
            weight: Weight for this observation
            
        Returns:
            Updated EWMA value
        """
        return self.update(x, weight)

    def reset(self) -> None:
        """Reset EWMA to initial state."""
        self.value = None
        self.variance = None
        self.n = 0

    def get(self) -> Optional[float]:
        """Get current EWMA value.
        
        Returns:
            Current EWMA value, or None if no updates
        """
        return self.value

    def confidence_interval(self, confidence: float = 0.95) -> Optional[Tuple[float, float]]:
        """Calculate confidence interval for current estimate.
        
        Args:
            confidence: Confidence level (e.g., 0.95 for 95%)
            
        Returns:
            (lower_bound, upper_bound) tuple, or None if insufficient data
        """
        if self.value is None or self.variance is None or self.n < 2:
            return None
        
        # Use normal approximation with estimated standard error
        std_error = math.sqrt(self.variance)
        
        # Z-score for desired confidence level
        z_score = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }.get(confidence)
        
        if z_score is None:
            # Fallback for arbitrary confidence levels
            # Approximate using inverse normal distribution
            if confidence == 0.68:
                z_score = 1.0
            elif confidence < 0.5:
                z_score = 0.0
            elif confidence > 0.999:
                z_score = 3.0
            else:
                # Linear approximation for intermediate values
                z_score = 1.96 * (confidence - 0.5) / 0.45
        
        margin = z_score * std_error
        return (self.value - margin, self.value + margin)

    @property
    def is_initialized(self) -> bool:
        """Whether EWMA has been initialized with at least one value."""
        return self.value is not None

    @property
    def count(self) -> int:
        """Number of updates processed."""
        return self.n


class MetricsEngine:
    """Comprehensive metrics engine for progress monitoring.
    
    Manages stage timing statistics, ETA calculations, throughput metrics,
    and cache speed adjustments for progress tracking systems.
    
    Attributes:
        stage_accumulators: Welford accumulators per stage
        eta_estimator: EWMA for ETA smoothing
        throughput_estimator: EWMA for throughput smoothing
        cache_speed_factor: Speed multiplier for cached operations
        start_time: Global start timestamp
    """

    def __init__(
        self, 
        ewma_alpha: float = 0.2, 
        cache_speed_factor: float = 0.8
    ) -> None:
        """Initialize metrics engine.
        
        Args:
            ewma_alpha: Smoothing factor for ETA and throughput estimates
            cache_speed_factor: Speed multiplier for cached tasks (0-1)
                               0.8 means cached tasks are 20% faster
        """
        self.stage_accumulators: Dict[str, WelfordAccumulator] = defaultdict(WelfordAccumulator)
        self.eta_estimator = EWMA(alpha=ewma_alpha)
        self.throughput_estimator = EWMA(alpha=ewma_alpha)
        
        self.cache_speed_factor = cache_speed_factor
        self.start_time = time.time()
        
        # Tracking variables
        self.completed_count = 0
        self.cached_count = 0
        self.last_completion_time: Optional[float] = None
        
        # For throughput calculation
        self._completion_times: List[float] = []
        self._throughput_window = 60.0  # 1 minute window for throughput

    def record_stage_time(self, stage: str, duration: float, cached: bool = False) -> None:
        """Record timing for a stage completion.
        
        Args:
            stage: Stage name
            duration: Time taken in seconds
            cached: Whether this was a cached/fast operation
        """
        # Adjust duration for cache speed
        if cached:
            # If cached operations are faster, record the "equivalent" uncached time
            # This helps with ETA calculations that mix cached and uncached tasks
            adjusted_duration = duration / self.cache_speed_factor
        else:
            adjusted_duration = duration
        
        self.stage_accumulators[stage].update(adjusted_duration)
    
    def record_stage_duration(self, stage: str, duration: float, cached: bool = False) -> None:
        """Alias for record_stage_time for backwards compatibility.
        
        Args:
            stage: Stage name
            duration: Time taken in seconds
            cached: Whether this was a cached/fast operation
        """
        self.record_stage_time(stage, duration, cached)

    def record_task_completion(self, total_time: float, cached: bool = False) -> None:
        """Record a completed task for ETA and throughput calculations.
        
        Args:
            total_time: Total time for the task in seconds
            cached: Whether this was a cached operation
        """
        current_time = time.time()
        
        self.completed_count += 1
        if cached:
            self.cached_count += 1
        
        # Update ETA estimator
        weight = self.cache_speed_factor if cached else 1.0
        self.eta_estimator.weighted_update(total_time, weight)
        
        # Update throughput calculation
        self._completion_times.append(current_time)
        
        # Clean old completion times (keep only recent window)
        cutoff_time = current_time - self._throughput_window
        self._completion_times = [t for t in self._completion_times if t >= cutoff_time]
        
        # Update throughput estimator
        if len(self._completion_times) >= 2:
            # Calculate current throughput (tasks per minute)
            time_span = self._completion_times[-1] - self._completion_times[0]
            if time_span > 0:
                current_throughput = (len(self._completion_times) - 1) / time_span * 60
                self.throughput_estimator.update(current_throughput)
        
        self.last_completion_time = current_time

    def calculate_eta(self, completed_or_remaining: int, total: Optional[int] = None, cache_ratio: float = 0.0) -> Union[Optional[float], Tuple[Optional[float], str]]:
        """Calculate estimated time to completion.
        
        Can be called in two ways:
        1. calculate_eta(remaining_tasks, cache_ratio=0.0) -> float
        2. calculate_eta(completed, total, cache_ratio=0.0) -> (seconds, string)
        
        Args:
            completed_or_remaining: Either remaining tasks (if total is None) or completed count
            total: If provided, treat first arg as completed count
            cache_ratio: Fraction of remaining tasks expected to be cached (0-1)
            
        Returns:
            ETA in seconds, or tuple of (seconds, string) if total provided
        """
        if total is not None:
            # Called as (completed, total, cache_ratio)
            completed = completed_or_remaining
            remaining_tasks = total - completed
        else:
            # Called as (remaining_tasks, cache_ratio)
            remaining_tasks = completed_or_remaining
        
        if not self.eta_estimator.is_initialized or remaining_tasks <= 0:
            if total is not None:
                return (None, "N/A")
            return None
        
        avg_time_per_task = self.eta_estimator.get()
        if avg_time_per_task is None or avg_time_per_task <= 0:
            if total is not None:
                return (None, "N/A")
            return None
        
        # Adjust for expected cache ratio
        # If cache_ratio=0.3, then 30% of tasks will be faster
        effective_time_per_task = (
            avg_time_per_task * self.cache_speed_factor * cache_ratio +
            avg_time_per_task * (1 - cache_ratio)
        )
        
        eta_seconds = remaining_tasks * effective_time_per_task
        
        if total is not None:
            # Return tuple format expected by test
            eta_str = format_time(eta_seconds)
            return (eta_seconds, eta_str)
        
        return eta_seconds

    def calculate_throughput(self) -> Optional[float]:
        """Calculate current throughput in tasks per minute.
        
        Returns:
            Tasks per minute, or None if insufficient data
        """
        if self.throughput_estimator.is_initialized:
            return self.throughput_estimator.get()
        
        # Fallback: simple calculation
        if len(self._completion_times) >= 2:
            time_span = self._completion_times[-1] - self._completion_times[0]
            if time_span > 0:
                return (len(self._completion_times) - 1) / time_span * 60
        
        return None

    def get_stage_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary statistics for all stages.
        
        Returns:
            Dictionary mapping stage names to their statistics:
            {
                'stage_name': {
                    'count': int,
                    'mean': float,
                    'std': float,
                    'min': float,
                    'max': float,
                    'total_time': float
                }
            }
        """
        summary = {}
        
        total_time_all_stages = sum(
            acc.mean * acc.count 
            for acc in self.stage_accumulators.values()
            if acc.count > 0
        )
        
        for stage, acc in self.stage_accumulators.items():
            if acc.count > 0:
                stage_total_time = acc.mean * acc.count
                percentage = (stage_total_time / total_time_all_stages * 100) if total_time_all_stages > 0 else 0.0
                
                summary[stage] = {
                    'count': acc.count,
                    'mean': acc.mean,
                    'std': acc.std,
                    'min': acc.minimum,
                    'max': acc.maximum,
                    'total_time': stage_total_time,
                    'percentage': percentage
                }
        
        return summary

    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall timing and performance statistics.
        
        Returns:
            Dictionary with overall statistics
        """
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        throughput = self.calculate_throughput()
        avg_task_time = self.eta_estimator.get()
        
        return {
            'elapsed_time': elapsed,
            'completed_count': self.completed_count,
            'cached_count': self.cached_count,
            'cache_percentage': (self.cached_count / self.completed_count * 100) if self.completed_count > 0 else 0.0,
            'throughput_per_minute': throughput,
            'average_task_time': avg_task_time,
            'eta_confidence_interval': self.eta_estimator.confidence_interval() if self.eta_estimator.is_initialized else None
        }

    def reset(self) -> None:
        """Reset all metrics to initial state."""
        self.stage_accumulators.clear()
        self.eta_estimator.reset()
        self.throughput_estimator.reset()
        
        self.start_time = time.time()
        self.completed_count = 0
        self.cached_count = 0
        self.last_completion_time = None
        self._completion_times.clear()


# Helper functions

def format_time(seconds: float) -> str:
    """Format time duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "2m 15s", "1h 30m", "45.2s"
        
    Examples:
        >>> format_time(75.3)
        '1m 15s'
        >>> format_time(3665)
        '1h 1m 5s'
        >>> format_time(42.7)
        '42.7s'
    """
    if seconds < 0:
        return "0s"
    
    if seconds < 60:
        if seconds < 10:
            return f"{seconds:.1f}s"
        else:
            return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes < 60:
        if remaining_seconds == 0:
            return f"{minutes}m"
        else:
            return f"{minutes}m {remaining_seconds}s"
    
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    
    if hours < 24:
        if remaining_minutes == 0 and remaining_seconds == 0:
            return f"{hours}h"
        elif remaining_seconds == 0:
            return f"{hours}h {remaining_minutes}m"
        else:
            return f"{hours}h {remaining_minutes}m {remaining_seconds}s"
    
    days = int(hours // 24)
    remaining_hours = int(hours % 24)
    
    if remaining_hours == 0 and remaining_minutes == 0 and remaining_seconds == 0:
        return f"{days}d"
    elif remaining_minutes == 0 and remaining_seconds == 0:
        return f"{days}d {remaining_hours}h"
    else:
        return f"{days}d {remaining_hours}h {remaining_minutes}m"


def calculate_eta(
    remaining_tasks: int,
    avg_time_per_task: float,
    cache_ratio: float = 0.0,
    cache_speed_factor: float = 0.8
) -> float:
    """Calculate estimated time to completion with cache adjustment.
    
    Args:
        remaining_tasks: Number of tasks left
        avg_time_per_task: Average time per task in seconds
        cache_ratio: Expected fraction of remaining tasks that will be cached
        cache_speed_factor: Speed multiplier for cached tasks
        
    Returns:
        ETA in seconds
        
    Example:
        >>> # 100 remaining tasks, 10s avg, 20% cached, cached 2x faster
        >>> eta = calculate_eta(100, 10.0, 0.2, 0.5)
        >>> eta  # 80*10 + 20*5 = 900 seconds
        900.0
    """
    if remaining_tasks <= 0 or avg_time_per_task <= 0:
        return 0.0
    
    cached_tasks = remaining_tasks * cache_ratio
    uncached_tasks = remaining_tasks * (1 - cache_ratio)
    
    cached_time = cached_tasks * avg_time_per_task * cache_speed_factor
    uncached_time = uncached_tasks * avg_time_per_task
    
    return cached_time + uncached_time


def calculate_throughput(
    completed_count: int,
    elapsed_time: float,
    unit: str = "minute"
) -> float:
    """Calculate throughput (tasks per time unit).
    
    Args:
        completed_count: Number of completed tasks
        elapsed_time: Time elapsed in seconds
        unit: Time unit ("second", "minute", "hour")
        
    Returns:
        Tasks per time unit
        
    Raises:
        ValueError: If unit is not recognized
        
    Example:
        >>> throughput = calculate_throughput(120, 600, "minute")
        >>> throughput  # 120 tasks in 10 minutes = 12 tasks/min
        12.0
    """
    if elapsed_time <= 0 or completed_count <= 0:
        return 0.0
    
    tasks_per_second = completed_count / elapsed_time
    
    if unit == "second":
        return tasks_per_second
    elif unit == "minute":
        return tasks_per_second * 60
    elif unit == "hour":
        return tasks_per_second * 3600
    else:
        raise ValueError(f"Unknown unit '{unit}'. Use 'second', 'minute', or 'hour'")
