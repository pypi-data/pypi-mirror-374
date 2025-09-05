"""Tests for utility functions."""
try:
    import pytest
except ImportError:
    pytest = None
import math
from progressbox.utils.width import (
    get_display_width, truncate_to_width, align_left, align_right, align_center,
    pad_multiline, wrap_to_width, _truncate_by_width
)
from progressbox.utils.terminal import (
    get_terminal_width, get_terminal_height, is_tty, is_jupyter,
    supports_color, get_color_support, is_windows_terminal, get_terminal_info
)
from progressbox.utils.formatting import (
    format_duration, format_percentage, format_file_size, format_rate,
    build_progress_bar, format_eta, build_status_line, build_full_progress_display,
    format_scientific, format_compact_number
)


class TestWidthUtilities:
    """Test width calculation and text manipulation utilities."""
    
    def test_get_display_width_basic(self):
        """Test basic display width calculation."""
        assert get_display_width("hello") == 5
        assert get_display_width("") == 0
        assert get_display_width("a") == 1
        
    def test_get_display_width_unicode(self):
        """Test display width with Unicode characters."""
        assert get_display_width("café") == 4
        assert get_display_width("naïve") == 5
        # CJK characters should be width 2
        assert get_display_width("中文") == 4
        assert get_display_width("こんにちは") == 10
        
    def test_get_display_width_emoji(self):
        """Test display width with emoji."""
        # Emoji are typically width 2
        assert get_display_width("🎉") == 2
        assert get_display_width("🎉🎈") == 4
        
    def test_get_display_width_ansi(self):
        """Test display width with ANSI escape sequences."""
        assert get_display_width("\033[31mred\033[0m") == 3
        assert get_display_width("\033[1m\033[31mBold Red\033[0m") == 8
        
    def test_truncate_to_width_basic(self):
        """Test basic text truncation."""
        assert truncate_to_width("hello", 3) == "he…"
        assert truncate_to_width("hello", 5) == "hello"
        assert truncate_to_width("hello", 10) == "hello"
        assert truncate_to_width("hello", 0) == ""
        
    def test_truncate_to_width_unicode(self):
        """Test truncation with Unicode characters."""
        assert truncate_to_width("café", 3) == "ca…"
        assert truncate_to_width("中文测试", 5) == "中文…"
        
    def test_truncate_to_width_edge_cases(self):
        """Test truncation edge cases."""
        assert truncate_to_width("", 5) == ""
        assert truncate_to_width("a", 1) == "a"
        # Ellipsis too long for width
        assert truncate_to_width("hello", 1) == "h"
        
    def test_align_functions(self):
        """Test text alignment functions."""
        assert align_left("test", 8) == "test    "
        assert align_right("test", 8) == "    test"
        assert align_center("test", 8) == "  test  "
        assert align_center("test", 9) == "  test   "
        
    def test_align_with_fill_char(self):
        """Test alignment with custom fill character."""
        assert align_left("test", 8, ".") == "test...."
        assert align_right("test", 8, "-") == "----test"
        assert align_center("test", 8, "*") == "**test**"
        
    def test_align_truncation(self):
        """Test alignment when text is too long."""
        assert align_left("verylongtext", 5) == "veryl"
        assert align_right("verylongtext", 5) == "veryl"
        assert align_center("verylongtext", 5) == "veryl"
        
    def test_pad_multiline(self):
        """Test multiline padding."""
        lines = ["short", "longer line"]
        result = pad_multiline(lines, 12)
        assert result == ["short       ", "longer line "]
        
        result = pad_multiline(["a", "bb"], 5, align="center")
        assert result == ["  a  ", " bb  "]
        
    def test_wrap_to_width(self):
        """Test text wrapping."""
        result = wrap_to_width("Hello world from Python", 12)
        assert result == ["Hello world", "from Python"]
        
        result = wrap_to_width("verylongword", 6)
        assert result == ["verylo", "ngword"]
        
        result = wrap_to_width("", 10)
        assert result == [""]
        
    def test_wrap_to_width_no_break(self):
        """Test text wrapping without breaking words."""
        result = wrap_to_width("verylongword", 6, break_long_words=False)
        assert result == ["verylongword"]


class TestTerminalUtilities:
    """Test terminal detection utilities."""
    
    def test_get_terminal_width(self):
        """Test terminal width detection."""
        width = get_terminal_width()
        assert isinstance(width, int)
        assert width > 0  # Should return at least the default value
        
    def test_get_terminal_height(self):
        """Test terminal height detection."""
        height = get_terminal_height()
        assert isinstance(height, int)
        assert height > 0  # Should return at least the default value
        
    def test_is_tty(self):
        """Test TTY detection."""
        result = is_tty()
        assert isinstance(result, bool)
        
    def test_is_jupyter(self):
        """Test Jupyter detection."""
        result = is_jupyter()
        assert isinstance(result, bool)
        
    def test_supports_color(self):
        """Test color support detection."""
        result = supports_color()
        assert isinstance(result, bool)
        
    def test_get_color_support(self):
        """Test color support level detection."""
        result = get_color_support()
        assert result in ['none', 'basic', '256', 'truecolor']
        
    def test_is_windows_terminal(self):
        """Test Windows Terminal detection."""
        result = is_windows_terminal()
        assert isinstance(result, bool)
        
    def test_get_terminal_info(self):
        """Test comprehensive terminal info."""
        info = get_terminal_info()
        assert isinstance(info, dict)
        required_keys = [
            'width', 'height', 'is_tty', 'is_jupyter',
            'supports_color', 'color_support', 'is_windows_terminal',
            'term', 'colorterm', 'platform'
        ]
        for key in required_keys:
            assert key in info


class TestFormattingUtilities:
    """Test formatting utility functions."""
    
    def test_format_duration_seconds(self):
        """Test duration formatting for seconds."""
        assert format_duration(0) == "0s"
        assert format_duration(1.5) == "1.5s"
        assert format_duration(45.2) == "45.2s"
        
    def test_format_duration_minutes(self):
        """Test duration formatting for minutes."""
        assert format_duration(60) == "1m 0s"
        assert format_duration(135) == "2m 15s"
        assert format_duration(90.5) == "1m 30.5s"
        
    def test_format_duration_hours(self):
        """Test duration formatting for hours."""
        assert format_duration(3600) == "1h 0m 0s"
        assert format_duration(3675) == "1h 1m 15s"
        assert format_duration(7200.0) == "2h 0m 0s"
        
    def test_format_duration_days(self):
        """Test duration formatting for days."""
        assert format_duration(86400) == "1d 0h 0m"
        assert format_duration(90000) == "1d 1h 0m"
        
    def test_format_duration_edge_cases(self):
        """Test duration formatting edge cases."""
        assert format_duration(-1) == "0s"
        assert format_duration(0.0001) == "0.1ms"
        assert format_duration(0.000001) == "1μs"
        
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(0.5) == "50.0%"
        assert format_percentage(50, 100, decimals=0) == "50%"
        assert format_percentage(1.234, decimals=2) == "123.40%"
        assert format_percentage(0.1, show_sign=True) == "+10.0%"
        
    def test_format_percentage_edge_cases(self):
        """Test percentage formatting edge cases."""
        assert format_percentage(float('nan')) == "nan%"
        assert format_percentage(float('inf')) == "inf%"
        assert format_percentage(float('-inf')) == "-inf%"
        
    def test_format_file_size_binary(self):
        """Test file size formatting with binary units."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KiB"
        assert format_file_size(1048576) == "1.0 MiB"
        assert format_file_size(1536, decimals=0) == "2 KiB"
        
    def test_format_file_size_decimal(self):
        """Test file size formatting with decimal units."""
        assert format_file_size(1000, binary=False) == "1.0 KB"
        assert format_file_size(1000000, binary=False) == "1.0 MB"
        
    def test_format_rate(self):
        """Test rate formatting."""
        assert format_rate(123.4) == "123.4it/s"
        assert format_rate(1.23, "MB", 2) == "1.23MB/s"
        assert format_rate(1234, decimals=0) == "1234it/s"
        
    def test_format_rate_edge_cases(self):
        """Test rate formatting edge cases."""
        assert format_rate(float('nan')) == "0it/s"
        assert format_rate(float('inf')) == "0it/s"
        assert format_rate(-1) == "0it/s"
        
    def test_build_progress_bar(self):
        """Test progress bar building."""
        assert build_progress_bar(0.5, 10) == "█████░░░░░"
        assert build_progress_bar(0.0, 5) == "░░░░░"
        assert build_progress_bar(1.0, 5) == "█████"
        assert build_progress_bar(0.75, 4) == "███░"
        
    def test_build_progress_bar_custom_chars(self):
        """Test progress bar with custom characters."""
        assert build_progress_bar(0.5, 6, '=', '-') == "===---"
        assert build_progress_bar(0.33, 6, '#', ' ') == "##    "
        
    def test_build_progress_bar_edge_cases(self):
        """Test progress bar edge cases."""
        assert build_progress_bar(0.5, 0) == ""
        assert build_progress_bar(-0.1, 5) == "░░░░░"
        assert build_progress_bar(1.5, 5) == "█████"
        
    def test_format_eta(self):
        """Test ETA formatting."""
        assert format_eta(65) == "1m 5s"
        assert format_eta(float('inf')) == "--:--"
        assert format_eta(3600) == "1h 0m"
        assert format_eta(-1) == "--:--"
        
    def test_build_status_line(self):
        """Test status line building."""
        result = build_status_line(50, 100, 2.5, 20.0, 20.0, "Processing")
        assert "Processing:" in result
        assert "50/100" in result
        assert "50.0%" in result
        assert "2.5it/s" in result
        
    def test_build_status_line_indeterminate(self):
        """Test status line for indeterminate progress."""
        result = build_status_line(42, None, 1.2, 35.0, None, "Loading")
        assert "Loading:" in result
        assert "42" in result
        assert "1.2it/s" in result
        assert "/" not in result  # No total
        
    def test_build_full_progress_display(self):
        """Test full progress display building."""
        result = build_full_progress_display(50, 100, 20, 2.5, 20.0, 20.0, "Processing")
        assert "Processing:" in result
        assert "50%" in result
        assert "50/100" in result
        assert "█" in result or "░" in result  # Progress bar characters
        
    def test_format_scientific(self):
        """Test scientific notation formatting."""
        assert format_scientific(1234.5) == "1.23e+03"
        assert format_scientific(0.00123, 1) == "1.2e-03"
        assert format_scientific(float('nan')) == "nan"
        assert format_scientific(float('inf')) == "inf"
        
    def test_format_compact_number(self):
        """Test compact number formatting."""
        assert format_compact_number(1500) == "1.5K"
        assert format_compact_number(2500000) == "2.5M"
        assert format_compact_number(1234567890) == "1.2B"
        assert format_compact_number(999) == "999"
        assert format_compact_number(1000) == "1K"


# Integration tests
class TestIntegration:
    """Integration tests combining multiple utilities."""
    
    def test_unicode_handling_integration(self):
        """Test Unicode handling across all utilities."""
        unicode_text = "café 中文 🎉"
        
        # Width calculation
        width = get_display_width(unicode_text)
        assert width > len(unicode_text)  # Should account for wide characters
        
        # Truncation
        truncated = truncate_to_width(unicode_text, 8)
        assert get_display_width(truncated) <= 8
        
        # Alignment
        aligned = align_center(unicode_text, 20)
        assert get_display_width(aligned) == 20
        
    def test_ansi_handling_integration(self):
        """Test ANSI sequence handling across utilities."""
        ansi_text = "\033[31mred text\033[0m"
        
        # Should strip ANSI for width calculation
        width = get_display_width(ansi_text)
        assert width == 8  # "red text" length
        
        # Truncation should preserve ANSI codes when possible
        truncated = truncate_to_width(ansi_text, 6)
        assert "\033[31m" in truncated  # Should preserve color code
        
    def test_progress_display_realistic(self):
        """Test realistic progress display scenarios."""
        # Fast progress
        fast_display = build_full_progress_display(
            current=950, total=1000, progress_bar_width=30,
            rate=125.5, elapsed=7.6, eta=0.4, prefix="Fast Task"
        )
        assert "95%" in fast_display
        assert "125.5it/s" in fast_display
        
        # Slow progress  
        slow_display = build_full_progress_display(
            current=23, total=100, progress_bar_width=20,
            rate=0.3, elapsed=76.7, eta=256.7, prefix="Slow Task"
        )
        assert "23%" in slow_display
        assert "0.3it/s" in slow_display


if __name__ == "__main__":
    # Run a few quick tests if executed directly
    print("Running basic smoke tests...")
    
    # Test width utilities
    assert get_display_width("hello") == 5
    assert truncate_to_width("Hello World", 8) == "Hello W…"
    print("✓ Width utilities working")
    
    # Test terminal utilities
    assert isinstance(get_terminal_width(), int)
    assert isinstance(supports_color(), bool)
    print("✓ Terminal utilities working")
    
    # Test formatting utilities
    assert format_duration(135) == "2m 15s"
    assert "█" in build_progress_bar(0.7, 10) or "░" in build_progress_bar(0.7, 10)
    print("✓ Formatting utilities working")
    
    print("All smoke tests passed!")