from __future__ import annotations


class WithIndentation:
    _indentation: int = 0
    _indent_string: str = "  "

    def indentation_up(self, number: int = 1) -> None:
        self._indentation += number

    def indentation_down(self, number: int = 1) -> None:
        self._indentation -= number

    @property
    def indentation(self) -> int:
        return self._indentation
