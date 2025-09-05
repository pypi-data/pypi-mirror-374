from __future__ import annotations

"""Spinner frame presets for terminal UIs.

Note: Not all terminals render every Unicode glyph identically. Keep a few
ASCII-friendly presets as well. You can trim this list later.
"""

# Braille-style spinner (smooth, compact, good Unicode support in modern terminals)
BRAILLE_SPINNER_FRAMES: list[str] = [
    "⣷",
    "⣯",
    "⣟",
    "⡿",
    "⢿",
    "⣻",
    "⣽",
    "⣾",
]

# ASCII pipes
PIPE_SPINNER_FRAMES: list[str] = ["|", "/", "-", "\\"]

# Dashes (line)
LINE_SPINNER_FRAMES: list[str] = ["-", "\\", "|", "/"]

# Dots (growing)
DOTS_FRAMES: list[str] = ["․  ", "․․ ", "․․․", "   "]
DOTS_BOUNCE_FRAMES: list[str] = [".  ", ".. ", "...", " ..", "  .", "   "]

# Ellipsis variants
ELLIPSIS_FRAMES: list[str] = ["", ".", "..", "..."]

# Arrows
ARROW_FRAMES: list[str] = ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]
ARROW_THIN_FRAMES: list[str] = ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"]

# Quadrants
QUADRANT_FRAMES: list[str] = ["▖", "▘", "▝", "▗"]

# Block shades
BLOCK_SHADES_FRAMES: list[str] = ["░", "▒", "▓", "█", "▓", "▒"]

# Growing bar (horizontal)
BAR_FRAMES: list[str] = [
    "▁",
    "▂",
    "▃",
    "▄",
    "▅",
    "▆",
    "▇",
    "█",
    "▇",
    "▆",
    "▅",
    "▄",
    "▃",
    "▂",
]

# Vertical growth
GROW_VERTICAL_FRAMES: list[str] = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

# Classic circle
CLASSIC_CIRCLE_FRAMES: list[str] = ["◴", "◷", "◶", "◵"]

# Bouncing ball
BOUNCE_FRAMES: list[str] = [
    "⠁",
    "⠂",
    "⠄",
    "⡀",
    "⢀",
    "⠠",
    "⠐",
    "⠈",
]

# Simple toggles
TOGGLE_FRAMES: list[str] = ["⊶", "⊷"]
TOGGLE_SQUARE_FRAMES: list[str] = ["▮", "▯"]

# Clock
CLOCK_FRAMES: list[str] = [
    "🕛",
    "🕐",
    "🕑",
    "🕒",
    "🕓",
    "🕔",
    "🕕",
    "🕖",
    "🕗",
    "🕘",
    "🕙",
    "🕚",
]

# Triangle
TRIANGLE_FRAMES: list[str] = ["◢", "◣", "◤", "◥"]

# Squares
SQUARE_FRAMES: list[str] = ["▖", "▘", "▝", "▗"]

# Circle dots
CIRCLE_QUADRANT_FRAMES: list[str] = [
    "◐",
    "◓",
    "◑",
    "◒",
]

# Dot pulse
DOT_PULSE_FRAMES: list[str] = ["∙    ", "∙∙   ", "∙∙∙  ", "∙∙∙∙ ", "∙∙∙∙∙", "     "]

# Simple ASCII triangle wave
ASCII_WAVE_FRAMES: list[str] = ["_", "-", "^", "-", "_"]

# Default spinner exported for convenience
DEFAULT_SPINNER_FRAMES: list[str] = BRAILLE_SPINNER_FRAMES

# Registry of presets by name (feel free to prune later)
SPINNER_PRESETS: dict[str, list[str]] = {
    "default": DEFAULT_SPINNER_FRAMES,
    "braille": BRAILLE_SPINNER_FRAMES,
    "pipe": PIPE_SPINNER_FRAMES,
    "line": LINE_SPINNER_FRAMES,
    "dots": DOTS_FRAMES,
    "dots_bounce": DOTS_BOUNCE_FRAMES,
    "ellipsis": ELLIPSIS_FRAMES,
    "arrow": ARROW_FRAMES,
    "arrow_thin": ARROW_THIN_FRAMES,
    "quadrant": QUADRANT_FRAMES,
    "block_shades": BLOCK_SHADES_FRAMES,
    "bar": BAR_FRAMES,
    "grow_vertical": GROW_VERTICAL_FRAMES,
    "circle": CLASSIC_CIRCLE_FRAMES,
    "bounce": BOUNCE_FRAMES,
    "toggle": TOGGLE_FRAMES,
    "toggle_square": TOGGLE_SQUARE_FRAMES,
    "clock": CLOCK_FRAMES,
    "triangle": TRIANGLE_FRAMES,
    "square": SQUARE_FRAMES,
    "circle_dots": CIRCLE_QUADRANT_FRAMES,
    "dot_pulse": DOT_PULSE_FRAMES,
    "ascii_wave": ASCII_WAVE_FRAMES,
}

__all__ = [
    # core
    "DEFAULT_SPINNER_FRAMES",
    # presets
    "BRAILLE_SPINNER_FRAMES",
    "PIPE_SPINNER_FRAMES",
    "LINE_SPINNER_FRAMES",
    "DOTS_FRAMES",
    "DOTS_BOUNCE_FRAMES",
    "ELLIPSIS_FRAMES",
    "ARROW_FRAMES",
    "ARROW_THIN_FRAMES",
    "QUADRANT_FRAMES",
    "BLOCK_SHADES_FRAMES",
    "BAR_FRAMES",
    "GROW_VERTICAL_FRAMES",
    "CLASSIC_CIRCLE_FRAMES",
    "BOUNCE_FRAMES",
    "TOGGLE_FRAMES",
    "TOGGLE_SQUARE_FRAMES",
    "CLOCK_FRAMES",
    "TRIANGLE_FRAMES",
    "SQUARE_FRAMES",
    "CIRCLE_DOTS_FRAMES",
    "DOT_PULSE_FRAMES",
    "ASCII_WAVE_FRAMES",
    # registry
    "SPINNER_PRESETS",
]
