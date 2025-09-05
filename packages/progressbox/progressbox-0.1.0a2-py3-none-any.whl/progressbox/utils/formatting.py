"""Formatting utilities for progress displays."""
import math
from typing import Union, Optional, Tuple

from .width import get_display_width, align_left, align_right, truncate_to_width


def format_duration(seconds: float, precision: int = 1) -> str:
    """Format time duration in human-readable form.
    
    Args:
        seconds: Duration in seconds
        precision: Decimal places for seconds (when showing seconds)
        
    Returns:
        Formatted duration string
        
    Examples:
        >>> format_duration(45.2)
        '45.2s'
        >>> format_duration(135)
        '2m 15s'
        >>> format_duration(3675)
        '1h 1m 15s'
        >>> format_duration(86400)
        '1d 0h 0m'
    """
    if seconds < 0:
        return "0s"
    
    if seconds == 0:
        return "0s"
    
    # Handle very small durations
    if seconds < 1:
        if seconds < 0.001:
            return f"{seconds*1000000:.0f}\u03bcs"  # microseconds
        elif seconds < 1:
            return f"{seconds*1000:.0f}ms"  # milliseconds
    
    # Convert to integer seconds for calculations
    total_seconds = int(seconds)
    fractional_seconds = seconds - total_seconds
    
    # Calculate time components
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    remaining_seconds = total_seconds % 60
    
    # Add fractional part back to seconds
    if fractional_seconds > 0 and days == 0 and hours == 0:
        remaining_seconds += fractional_seconds
    
    parts = []
    
    # Add days if present
    if days > 0:
        parts.append(f"{days}d")
    
    # Add hours if present or if days are present
    if hours > 0 or (days > 0):
        parts.append(f"{hours}h")
    
    # Add minutes if present or if hours/days are present
    if minutes > 0 or (hours > 0 or days > 0):
        parts.append(f"{minutes}m")
    
    # Add seconds
    if days == 0 and hours == 0 and fractional_seconds > 0:
        # Show fractional seconds only for durations < 1 hour
        parts.append(f"{remaining_seconds:.{precision}f}s")
    elif days == 0 and hours == 0 and minutes == 0:
        # For very short durations, always show seconds
        parts.append(f"{remaining_seconds:.{precision}f}s")
    elif remaining_seconds > 0 or not parts:
        # Show integer seconds
        parts.append(f"{int(remaining_seconds)}s")
    
    return " ".join(parts)


def format_percentage(value: float, total: Optional[float] = None, 
                     decimals: int = 1, show_sign: bool = False) -> str:
    """Format percentage with configurable decimal places.
    
    Args:
        value: Current value
        total: Total value (if None, value is assumed to be 0-1 range)
        decimals: Number of decimal places to show
        show_sign: Whether to show + for positive percentages
        
    Returns:
        Formatted percentage string
        
    Examples:
        >>> format_percentage(0.5)
        '50.0%'
        >>> format_percentage(50, 100, decimals=0)
        '50%'
        >>> format_percentage(1.234, decimals=2)
        '123.40%'
        >>> format_percentage(0.1, show_sign=True)
        '+10.0%'
    """
    if total is not None and total != 0:
        percentage = (value / total) * 100
    else:
        percentage = value * 100
    
    # Handle edge cases
    if math.isnan(percentage):
        return "nan%"
    elif math.isinf(percentage):
        return "inf%" if percentage > 0 else "-inf%"
    
    # Clamp to reasonable range for display
    if percentage > 9999:
        percentage = 9999
    elif percentage < -9999:
        percentage = -9999
    
    # Format with specified decimals
    if decimals == 0:
        formatted = f"{percentage:.0f}"
    else:
        formatted = f"{percentage:.{decimals}f}"
    
    # Add sign if requested
    if show_sign and percentage > 0:
        formatted = "+" + formatted
    
    return formatted + "%"


def format_file_size(size_bytes: int, binary: bool = True, decimals: int = 1) -> str:
    """Format file size in human-readable form.
    
    Args:
        size_bytes: Size in bytes
        binary: Use binary (1024) or decimal (1000) units
        decimals: Number of decimal places to show
        
    Returns:
        Formatted file size string
        
    Examples:
        >>> format_file_size(1024)
        '1.0 KiB'
        >>> format_file_size(1000, binary=False)
        '1.0 KB'
        >>> format_file_size(1536, decimals=0)
        '2 KiB'
    """
    if size_bytes < 0:
        return "0 B"
    
    if size_bytes == 0:
        return "0 B"
    
    # Choose unit base and suffixes
    if binary:
        base = 1024
        suffixes = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    else:
        base = 1000
        suffixes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    
    # Calculate the appropriate unit
    if size_bytes < base:
        return f"{size_bytes} B"
    
    # Find the largest unit that results in a value >= 1
    unit_index = min(int(math.log(size_bytes) / math.log(base)), len(suffixes) - 1)
    
    # Calculate the value in the chosen unit
    value = size_bytes / (base ** unit_index)
    suffix = suffixes[unit_index]
    
    # Format with specified decimals
    if decimals == 0:
        return f"{value:.0f} {suffix}"
    else:
        return f"{value:.{decimals}f} {suffix}"


def format_rate(value: float, unit: str = "it", decimals: int = 1) -> str:
    """Format processing rate (items per second).
    
    Args:
        value: Rate in items per second
        unit: Unit name (e.g., "it", "files", "MB")
        decimals: Number of decimal places to show
        
    Returns:
        Formatted rate string
        
    Examples:
        >>> format_rate(123.4)
        '123.4it/s'
        >>> format_rate(1.23, "MB", 2)
        '1.23MB/s'
        >>> format_rate(1234, decimals=0)
        '1234it/s'
    """
    if math.isnan(value) or math.isinf(value) or value < 0:
        return f"0{unit}/s"
    
    # Format with specified decimals
    if decimals == 0:
        return f"{value:.0f}{unit}/s"
    else:
        return f"{value:.{decimals}f}{unit}/s"


def build_progress_bar(progress: float, width: int, 
                      filled_char: str = "\u2588", empty_char: str = "\u2591",
                      partial_chars: Optional[str] = None) -> str:
    """Build a progress bar with configurable characters.
    
    Args:
        progress: Progress ratio (0.0 to 1.0)
        width: Width of the progress bar in characters
        filled_char: Character for filled portions
        empty_char: Character for empty portions
        partial_chars: String of characters for partial progress (e.g., "\u258f\u258e\u258d\u258c\u258b\u258a\u2589")
        
    Returns:
        Progress bar string
        
    Examples:
        >>> build_progress_bar(0.5, 10)
        '\u2588\u2588\u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591'
        >>> build_progress_bar(0.33, 10, '=', '-')
        '===-------'
        >>> build_progress_bar(0.75, 8, filled_char='#', empty_char=' ')
        '######  '
    """
    if width <= 0:
        return ""
    
    # Clamp progress to valid range
    progress = max(0.0, min(1.0, progress))
    
    # Calculate filled portion
    filled_width = progress * width
    filled_chars = int(filled_width)
    
    # Handle partial character if supported
    if partial_chars and filled_chars < width:
        remaining = filled_width - filled_chars
        partial_index = int(remaining * len(partial_chars))
        
        if partial_index > 0 and partial_index <= len(partial_chars):
            partial_char = partial_chars[partial_index - 1]
            bar = filled_char * filled_chars + partial_char
            empty_chars = width - filled_chars - 1
        else:
            bar = filled_char * filled_chars
            empty_chars = width - filled_chars
    else:
        bar = filled_char * filled_chars
        empty_chars = width - filled_chars
    
    # Add empty portion
    bar += empty_char * empty_chars
    
    return bar


def format_eta(remaining_seconds: float) -> str:
    """Format estimated time of arrival/completion.
    
    Args:
        remaining_seconds: Estimated seconds remaining
        
    Returns:
        Formatted ETA string
        
    Examples:
        >>> format_eta(65)
        '1m 5s'
        >>> format_eta(float('inf'))
        '--:--'
        >>> format_eta(3600)
        '1h 0m'
    """
    if math.isnan(remaining_seconds) or math.isinf(remaining_seconds) or remaining_seconds < 0:
        return "--:--"
    
    return format_duration(remaining_seconds, precision=0)


def build_status_line(current: int, total: Optional[int] = None,
                     rate: Optional[float] = None, elapsed: Optional[float] = None,
                     eta: Optional[float] = None, prefix: str = "",
                     unit: str = "it", width: Optional[int] = None) -> str:
    """Build a complete status line for progress display.
    
    Args:
        current: Current progress count
        total: Total count (None for indeterminate)
        rate: Processing rate (items per second)
        elapsed: Elapsed time in seconds
        eta: Estimated time remaining in seconds
        prefix: Prefix text to show before progress
        unit: Unit name for items
        width: Maximum width for the status line
        
    Returns:
        Formatted status line
        
    Examples:
        >>> build_status_line(50, 100, 2.5, 20.0, 20.0, "Processing")
        'Processing: 50/100 (50.0%) [2.5it/s, 20.0s elapsed, 20s remaining]'
    """
    parts = []
    
    # Add prefix if provided
    if prefix:
        parts.append(prefix + ":")
    
    # Progress count
    if total is not None:
        parts.append(f"{current}/{total}")
        # Percentage
        if total > 0:
            pct = format_percentage(current, total, decimals=1)
            parts.append(f"({pct})")
    else:
        parts.append(f"{current}")
    
    # Build the info section
    info_parts = []
    
    if rate is not None:
        info_parts.append(format_rate(rate, unit))
    
    if elapsed is not None:
        info_parts.append(f"{format_duration(elapsed)} elapsed")
    
    if eta is not None and not math.isinf(eta):
        info_parts.append(f"{format_eta(eta)} remaining")
    
    if info_parts:
        parts.append(f"[{', '.join(info_parts)}]")
    
    status_line = " ".join(parts)
    
    # Truncate if width specified
    if width is not None and width > 0:
        status_line = truncate_to_width(status_line, width)
    
    return status_line


def build_full_progress_display(current: int, total: Optional[int] = None,
                               progress_bar_width: int = 20,
                               rate: Optional[float] = None,
                               elapsed: Optional[float] = None,
                               eta: Optional[float] = None,
                               prefix: str = "", unit: str = "it",
                               bar_format: Optional[str] = None) -> str:
    """Build a complete progress display with bar and status.
    
    Args:
        current: Current progress count
        total: Total count (None for indeterminate)
        progress_bar_width: Width of the progress bar
        rate: Processing rate (items per second)
        elapsed: Elapsed time in seconds
        eta: Estimated time remaining in seconds
        prefix: Prefix text to show
        unit: Unit name for items
        bar_format: Custom format string (not implemented in this basic version)
        
    Returns:
        Complete progress display string
        
    Examples:
        >>> build_full_progress_display(50, 100, 10, 2.5, 20.0, 20.0, "Processing")
        'Processing:  50% [\u2588\u2588\u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591] 50/100 [2.5it/s, 20.0s elapsed, 20s remaining]'
    """
    parts = []
    
    # Add prefix if provided
    if prefix:
        parts.append(prefix + ":")
    
    # Progress percentage (if total known)
    if total is not None and total > 0:
        pct = format_percentage(current, total, decimals=0)
        parts.append(f"{pct:>4}")
    
    # Progress bar
    if total is not None and total > 0:
        progress_ratio = current / total
        bar = build_progress_bar(progress_ratio, progress_bar_width)
        parts.append(f"[{bar}]")
    else:
        # Indeterminate progress bar (could be animated)
        bar = build_progress_bar(0.0, progress_bar_width, empty_char="\u2591")
        parts.append(f"[{bar}]")
    
    # Progress count
    if total is not None:
        parts.append(f"{current}/{total}")
    else:
        parts.append(f"{current}")
    
    # Build the info section
    info_parts = []
    
    if rate is not None:
        info_parts.append(format_rate(rate, unit))
    
    if elapsed is not None:
        info_parts.append(f"{format_duration(elapsed)} elapsed")
    
    if eta is not None and not math.isinf(eta):
        info_parts.append(f"{format_eta(eta)} remaining")
    
    if info_parts:
        parts.append(f"[{', '.join(info_parts)}]")
    
    return " ".join(parts)


# Utility functions for special formatting cases

def format_scientific(value: float, decimals: int = 2) -> str:
    """Format number in scientific notation.
    
    Args:
        value: Number to format
        decimals: Decimal places for mantissa
        
    Returns:
        Scientific notation string
        
    Examples:
        >>> format_scientific(1234.5)
        '1.23e+03'
        >>> format_scientific(0.00123, 1)
        '1.2e-03'
    """
    if math.isnan(value):
        return "nan"
    elif math.isinf(value):
        return "inf" if value > 0 else "-inf"
    
    return f"{value:.{decimals}e}"


def format_compact_number(value: Union[int, float], decimals: int = 1) -> str:
    """Format large numbers in compact form (K, M, B, etc.).
    
    Args:
        value: Number to format
        decimals: Decimal places to show
        
    Returns:
        Compact number string
        
    Examples:
        >>> format_compact_number(1500)
        '1.5K'
        >>> format_compact_number(2500000)
        '2.5M'
        >>> format_compact_number(1234567890)
        '1.2B'
    """
    if abs(value) < 1000:
        if isinstance(value, int):
            return str(value)
        else:
            return f"{value:.{decimals}f}".rstrip('0').rstrip('.')
    
    suffixes = ['', 'K', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    magnitude = int(math.log10(abs(value)) // 3)
    magnitude = min(magnitude, len(suffixes) - 1)
    
    scaled = value / (1000 ** magnitude)
    suffix = suffixes[magnitude]
    
    if decimals == 0:
        return f"{scaled:.0f}{suffix}"
    else:
        formatted = f"{scaled:.{decimals}f}".rstrip('0').rstrip('.')
        return f"{formatted}{suffix}"