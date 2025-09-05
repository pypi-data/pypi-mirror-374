#!/usr/bin/env python3
"""
Text processing utilities.
"""

import re
from typing import Optional

from wcwidth import wcswidth


def trace_log(message: str, enabled: bool) -> None:
    """
    Print trace message if tracing is enabled.

    Args:
        message: Message to log
        enabled: Whether tracing is enabled
    """
    if enabled:
        print(message)


def str_display_width(text: str) -> int:
    """
    Get the display width of a string, handling Unicode characters.

    Args:
        text: Text to measure

    Returns:
        Display width in terminal columns
    """
    if not text:
        return 0

    width = wcswidth(text)
    return width if width is not None and width >= 0 else len(text)


def truncate_str_by_width(text: str, max_width: int) -> str:
    """
    Truncate string to fit within specified display width.

    Args:
        text: Text to truncate
        max_width: Maximum display width

    Returns:
        Truncated text
    """
    if not text or max_width <= 0:
        return ""

    if str_display_width(text) <= max_width:
        return text

    # Binary search for the right length
    left, right = 0, len(text)
    result = ""

    while left <= right:
        mid = (left + right) // 2
        substring = text[:mid]
        width = str_display_width(substring)

        if width <= max_width:
            result = substring
            left = mid + 1
        else:
            right = mid - 1

    return result


def format_reading_time(minutes: float) -> str:
    """
    Format reading time in a human-readable format.

    Args:
        minutes: Reading time in minutes

    Returns:
        Formatted time string
    """
    if minutes < 1:
        return "< 1 min"
    elif minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = int(minutes // 60)
        remaining_mins = int(minutes % 60)
        if remaining_mins == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_mins}m"


def clean_text_for_display(text: str) -> str:
    """
    Clean text for display by normalizing whitespace and removing control characters.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs to single space
    # Multiple newlines to double
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()


def clean_text_for_tts(text: str) -> str:
    """
    Clean text specifically for TTS processing.

    Args:
        text: Raw text

    Returns:
        Text suitable for TTS
    """
    if not text:
        return ""

    # Remove image references and other non-readable elements
    text = re.sub(r"\[Image[^\]]*\]", "", text)
    text = re.sub(r"\[.*?Content\]", "", text)  # [Unsupported Content]

    # Clean up markdown-style formatting
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # **bold** -> text
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # *italic* -> text
    text = re.sub(r"_{2,}", "", text)  # Remove underlines

    # Clean up excessive punctuation
    text = re.sub(r"[.]{3,}", "...", text)  # Multiple dots
    text = re.sub(r"[-]{3,}", "---", text)  # Multiple dashes

    # Normalize whitespace
    text = clean_text_for_display(text)

    # Add pauses for better TTS flow
    # Pause after sentences at line end
    text = re.sub(r"([.!?])\s*\n\s*", r"\1\n\n", text)
    text = re.sub(r":\s*\n", ":\n\n", text)  # Pause after colons

    return text


def extract_title_from_text(text: str, max_length: int = 50) -> str:
    """
    Extract a suitable title from text content.

    Args:
        text: Text content
        max_length: Maximum title length

    Returns:
        Extracted title
    """
    if not text:
        return "Untitled"

    lines = text.strip().split("\n")

    # Look for the first non-empty line as title
    for line in lines:
        line = line.strip()
        if line:
            # Clean up the title
            title = re.sub(r"[#*_`]", "", line)  # Remove markdown
            title = title.strip()

            if title:
                return truncate_str_by_width(title, max_length)

    return "Untitled"


def word_wrap(text: str, width: int, indent: int = 0) -> list[str]:
    """
    Wrap text to specified width with optional indentation.

    Args:
        text: Text to wrap
        width: Maximum line width
        indent: Indentation for wrapped lines

    Returns:
        List of wrapped lines
    """
    if not text or width <= 0:
        return []

    words = text.split()
    lines: list[str] = []
    current_line: list[str] = []
    current_length = 0
    indent_str = " " * indent

    for word in words:
        word_length = str_display_width(word)

        # Check if word fits on current line
        spaces_needed = len(current_line)  # spaces between words
        line_indent = indent if lines else 0  # first line might not be indented

        if current_length + spaces_needed + word_length + line_indent <= width:
            current_line.append(word)
            current_length += word_length
        else:
            # Finish current line and start new one
            if current_line:
                prefix = indent_str if lines else ""  # indent continuation lines
                lines.append(prefix + " ".join(current_line))

            # Handle very long words
            if word_length > width - indent:
                # Split the word
                while word:
                    max_chars = width - indent
                    if len(word) <= max_chars:
                        current_line = [word]
                        current_length = word_length
                        break
                    else:
                        # Find good break point
                        break_point = max_chars
                        lines.append(indent_str + word[:break_point])
                        word = word[break_point:]

                current_line = []
                current_length = 0
            else:
                current_line = [word]
                current_length = word_length

    # Add final line
    if current_line:
        prefix = indent_str if lines else ""
        lines.append(prefix + " ".join(current_line))

    return lines


def normalize_chapter_title(title: str) -> str:
    """
    Normalize chapter title for consistent display.

    Args:
        title: Raw chapter title

    Returns:
        Normalized title
    """
    if not title:
        return "Untitled Chapter"

    # Remove excessive whitespace
    title = " ".join(title.split())

    # Remove common prefixes that might be redundant
    title = re.sub(r"^(Chapter\s+\d+[:\-\s]*)", "", title, flags=re.IGNORECASE)
    # Remove Chinese chapter prefixes (e.g., "第1章", "第2节")
    title = re.sub(r"^(第\s*\d+\s*[章节][:\-\s]*)", "", title)

    # Clean up remaining text
    title = title.strip(" :-")

    return title if title else "Untitled Chapter"


def extract_reading_level(text: str) -> dict[str, float | int | str]:
    """
    Estimate reading level and complexity of text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with reading statistics
    """
    if not text:
        return {
            "words": 0,
            "sentences": 0,
            "avg_word_length": 0,
            "complexity": "unknown",
        }

    # Count words and sentences
    words = len(text.split())
    sentences = len(re.findall(r"[.!?]+", text))

    if words == 0:
        return {
            "words": 0,
            "sentences": 0,
            "avg_word_length": 0,
            "complexity": "unknown",
        }

    # Calculate average word length
    word_lengths = [len(word.strip(".,!?;:")) for word in text.split()]
    avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0

    # Simple complexity estimation
    if sentences == 0:
        words_per_sentence = 0
    else:
        words_per_sentence = words / sentences

    # Rough complexity categories
    if avg_word_length < 4 and words_per_sentence < 15:
        complexity = "easy"
    elif avg_word_length < 6 and words_per_sentence < 20:
        complexity = "medium"
    else:
        complexity = "hard"

    return {
        "words": words,
        "sentences": sentences,
        "avg_word_length": float(round(avg_word_length, 1)),
        "words_per_sentence": float(round(words_per_sentence, 1)),
        "complexity": complexity,
    }
