"""Display width calculations using wcwidth with robust fallbacks."""
import re
import unicodedata
from functools import lru_cache
from typing import List, Optional, Union

try:
    from wcwidth import wcswidth, wcwidth
except ImportError:
    # Fallback implementation when wcwidth not installed
    def wcwidth(char: str) -> Optional[int]:
        """Fallback wcwidth implementation."""
        if not char:
            return 0
        
        # ASCII characters (except control chars) are width 1
        if 32 <= ord(char) <= 126:
            return 1
        
        # Control characters are width 0
        if ord(char) < 32 or ord(char) == 127:
            return 0
            
        # Check for zero-width characters
        category = unicodedata.category(char)
        if category in ('Mn', 'Me', 'Cf'):  # Mark, Enclosing, Format
            return 0
        
        # Wide East Asian characters
        east_asian_width = unicodedata.east_asian_width(char)
        if east_asian_width in ('F', 'W'):  # Fullwidth, Wide
            return 2
            
        # Default to 1 for most characters
        return 1
    
    def wcswidth(s: str) -> Optional[int]:
        """Fallback wcswidth implementation."""
        if not s:
            return 0
        
        total_width = 0
        for char in s:
            char_width = wcwidth(char)
            if char_width is None:
                return None
            total_width += char_width
        return total_width


# ANSI escape sequence pattern for stripping color codes
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


@lru_cache(maxsize=8192)
def get_display_width(s: str) -> int:
    """Get display width of string, cached and robust.
    
    Args:
        s: Input string that may contain ANSI escape sequences
        
    Returns:
        Display width of the string
        
    Examples:
        >>> get_display_width("hello")
        5
        >>> get_display_width("こんにちは")  # Japanese
        10
        >>> get_display_width("\x1b[31mred\x1b[0m")  # ANSI colored
        3
        >>> get_display_width("café")  # Accented characters
        4
    """
    if not s:
        return 0
    
    # Strip ANSI escape sequences first
    clean_s = ANSI_ESCAPE.sub('', s)
    
    # Use wcwidth if available
    width = wcswidth(clean_s)
    if width is not None:
        return max(0, width)  # Ensure non-negative
    
    # Fallback: count visible characters, handling some Unicode
    visible_chars = 0
    for char in clean_s:
        if char == '\t':
            visible_chars += 8  # Standard tab width
        elif ord(char) >= 32:  # Printable character
            visible_chars += 1
    
    return visible_chars


def truncate_to_width(text: str, max_width: int, ellipsis: str = "…") -> str:
    """Safely truncate text to fit within max_width.
    
    Args:
        text: Text to truncate
        max_width: Maximum display width allowed
        ellipsis: String to append when truncating
        
    Returns:
        Truncated text that fits within max_width
        
    Examples:
        >>> truncate_to_width("Hello World", 8)
        'Hello W…'
        >>> truncate_to_width("こんにちは", 6)
        'こん…'
        >>> truncate_to_width("short", 10)
        'short'
    """
    if max_width <= 0:
        return ""
    
    current_width = get_display_width(text)
    if current_width <= max_width:
        return text
    
    ellipsis_width = get_display_width(ellipsis)
    if ellipsis_width >= max_width:
        # Ellipsis too long, just truncate without it
        return _truncate_by_width(text, max_width)
    
    target_width = max_width - ellipsis_width
    truncated = _truncate_by_width(text, target_width)
    return truncated + ellipsis


def _truncate_by_width(text: str, max_width: int) -> str:
    """Helper to truncate text to exact width without ellipsis."""
    if max_width <= 0:
        return ""
    
    # Strip ANSI codes for width calculation but preserve for output
    clean_text = ANSI_ESCAPE.sub('', text)
    
    result = ""
    current_width = 0
    
    # Track position in original text (with ANSI codes)
    orig_pos = 0
    clean_pos = 0
    
    while clean_pos < len(clean_text) and current_width < max_width:
        # Find the next character in the clean text
        clean_char = clean_text[clean_pos]
        
        # Calculate width of this character
        char_width = wcwidth(clean_char) if 'wcwidth' in globals() else 1
        if char_width is None:
            char_width = 0
        
        # Check if adding this character would exceed max_width
        if current_width + char_width > max_width:
            break
        
        # Find this character in the original text (handling ANSI codes)
        while orig_pos < len(text):
            if ANSI_ESCAPE.match(text[orig_pos:]):
                # Skip ANSI sequence
                match = ANSI_ESCAPE.match(text[orig_pos:])
                if match:
                    result += match.group()
                    orig_pos += match.end()
                    continue
            
            if text[orig_pos] == clean_char:
                result += text[orig_pos]
                orig_pos += 1
                break
            orig_pos += 1
        
        current_width += char_width
        clean_pos += 1
    
    return result


def align_left(text: str, width: int, fill_char: str = " ") -> str:
    """Left-align text to exact width.
    
    Args:
        text: Text to align
        width: Target width
        fill_char: Character to use for padding
        
    Returns:
        Left-aligned text padded to exact width
        
    Examples:
        >>> align_left("hello", 10)
        'hello     '
        >>> align_left("café", 8, ".")
        'café....'
    """
    if width <= 0:
        return ""
    
    current_width = get_display_width(text)
    if current_width >= width:
        return truncate_to_width(text, width, "")
    
    padding_needed = width - current_width
    return text + (fill_char * padding_needed)


def align_right(text: str, width: int, fill_char: str = " ") -> str:
    """Right-align text to exact width.
    
    Args:
        text: Text to align
        width: Target width
        fill_char: Character to use for padding
        
    Returns:
        Right-aligned text padded to exact width
        
    Examples:
        >>> align_right("hello", 10)
        '     hello'
        >>> align_right("café", 8, ".")
        '....café'
    """
    if width <= 0:
        return ""
    
    current_width = get_display_width(text)
    if current_width >= width:
        return truncate_to_width(text, width, "")
    
    padding_needed = width - current_width
    return (fill_char * padding_needed) + text


def align_center(text: str, width: int, fill_char: str = " ") -> str:
    """Center-align text to exact width.
    
    Args:
        text: Text to align
        width: Target width
        fill_char: Character to use for padding
        
    Returns:
        Center-aligned text padded to exact width
        
    Examples:
        >>> align_center("hello", 10)
        '  hello   '
        >>> align_center("café", 9, ".")
        '..café...'
    """
    if width <= 0:
        return ""
    
    current_width = get_display_width(text)
    if current_width >= width:
        return truncate_to_width(text, width, "")
    
    padding_needed = width - current_width
    left_padding = padding_needed // 2
    right_padding = padding_needed - left_padding
    
    return (fill_char * left_padding) + text + (fill_char * right_padding)


def pad_multiline(lines: List[str], width: int, align: str = "left", fill_char: str = " ") -> List[str]:
    """Pad multiple lines to consistent width.
    
    Args:
        lines: List of text lines
        width: Target width for all lines
        align: Alignment ('left', 'right', 'center')
        fill_char: Character to use for padding
        
    Returns:
        List of lines all padded to exact width
        
    Examples:
        >>> pad_multiline(["short", "longer line"], 12)
        ['short       ', 'longer line ']
        >>> pad_multiline(["a", "bb"], 5, align="center")
        ['  a  ', ' bb  ']
    """
    align_func = {
        "left": align_left,
        "right": align_right,
        "center": align_center
    }.get(align, align_left)
    
    return [align_func(line, width, fill_char) for line in lines]


def wrap_to_width(text: str, width: int, break_long_words: bool = True) -> List[str]:
    """Wrap text to fit within specified width.
    
    Args:
        text: Text to wrap
        width: Maximum width per line
        break_long_words: Whether to break words longer than width
        
    Returns:
        List of lines that fit within width
        
    Examples:
        >>> wrap_to_width("Hello world from Python", 12)
        ['Hello world', 'from Python']
        >>> wrap_to_width("verylongword", 6)
        ['verylo', 'ngword']
    """
    if width <= 0:
        return []
    
    if not text:
        return [""]
    
    words = text.split()
    if not words:
        return [""]
    
    lines = []
    current_line = ""
    
    for word in words:
        word_width = get_display_width(word)
        current_line_width = get_display_width(current_line)
        
        # Check if adding this word (plus space) would exceed width
        space_width = 1 if current_line else 0
        if current_line_width + space_width + word_width <= width:
            # Word fits on current line
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            # Word doesn't fit
            if current_line:
                lines.append(current_line)
                current_line = ""
            
            # Handle long words
            if word_width > width and break_long_words:
                # Break the word across lines
                while word_width > width:
                    partial = truncate_to_width(word, width, "")
                    lines.append(partial)
                    # Remove the part we used
                    word = word[len(partial):]
                    word_width = get_display_width(word)
                
                if word:  # Remaining part
                    current_line = word
            else:
                # Add word as-is (might exceed width if break_long_words=False)
                current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


# Legacy function for backwards compatibility
def pad_to_width(text: str, width: int) -> str:
    """Pad text to exact display width (legacy function).
    
    This is kept for backwards compatibility. Use align_left() for new code.
    """
    return align_left(text, width)
