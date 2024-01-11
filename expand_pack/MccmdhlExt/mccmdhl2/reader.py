# `mccmdhl2` - Minecraft Bedrock command parser and autocompleter.
# Copyright (C) 2023  CBerJun<cberjun@163.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Basic stuffs for reading a command."""

from typing import NewType, Union, Match, Pattern
from functools import total_ordering
import re

__all__ = [
    "Reader", "ReaderError", "CharLocation",
    "TERMINATORS", "DIGITS", "SIGNS"
]

_TERMINATOR_STR = " ,@~^/$&\"'!#%+*=[{]}\\|<>`\n"
_TERMINATOR_RE = r' ,@~\^/\$&"!#%\+\*=\[\{\]\}\\\|<>`\n' + "'"

TERMINATORS = frozenset(_TERMINATOR_STR)
DIGITS = frozenset("0123456789")
SIGNS = frozenset("+-")

PAT_INT = re.compile(r"[+-]?\d+")
PAT_WORD = re.compile(r".*?(?=[%s])" % _TERMINATOR_RE)
PAT_TILLEOF = re.compile(r".*$")
PAT_FLOAT = re.compile(r"[+-]?\d+(\.(\d+)?)?")
PAT_FLOAT_NOINT = re.compile(r"[+-]?\.\d+")
PAT_TILLEOL = re.compile(r".*?(?=\n)")

class ReaderError(Exception):
    pass

@total_ordering
class CharLocation:
    def __init__(self, line: int, column: int, pointer: int):
        self.line = line
        self.column = column
        self.pointer = pointer

    def __repr__(self):
        return "<Ln %d Col %d>" % (self.line, self.column)

    def __lt__(self, other: "CharLocation"):
        return self.pointer < other.pointer

    def __eq__(self, other: "CharLocation"):
        return self.pointer == other.pointer

    def offset(self, offset: int = 1) -> "CharLocation":
        return CharLocation(
            line=self.line, column=self.column + offset,
            pointer=self.pointer + offset
        )

ReaderState = NewType("ReaderState", CharLocation)
ReaderChar = Union[str, None]

class Reader:
    def __init__(self, src: str):
        self.src = src
        self.SRC_LEN = len(src)
        self.prev_char = None
        self.pointer = 0
        self.current_line = 1
        self.current_column = 1

    def next(self) -> ReaderChar:
        """Read and consume the next character."""
        if self._is_file_finish():
            res = None
        else:
            res = self.src[self.pointer]
        self.prev_char = res
        if self.pointer <= self.SRC_LEN:
            # We also push pointer when file finished ONCE (`<=`
            # not `<`), this char is End of File (`None`).
            self.current_column += 1
            if self.is_line_end(res):
                self.current_column = 1
                self.current_line += 1
            self.pointer += 1
        return res

    def read(self, regex: Pattern) -> Match:
        """Read and consume the text that matches given `regex`.
        NOTE The given `regex` cannot allow any `\n` read.
        Returns the match object or raises a `ReaderError` when failed.
        """
        m = regex.match(self.src, pos=self.pointer)
        if m is None:
            raise ReaderError
        length = m.end() - self.pointer
        self.pointer += length
        assert "\n" not in m.group()
        # This relies on the fact that no `\n` is skipped:
        self.current_column += length
        return m

    def peek(self):
        """Get the next character."""
        if not self._is_file_finish():
            return self.src[self.pointer]
        else:
            return None

    def read_word(self) -> str:
        try:
            m = self.read(PAT_WORD)
        except ReaderError:
            # Because no terminator presents, and end of file should
            # be the terminator
            m = self.read(PAT_TILLEOF)
        return m.group()

    def read_int(self) -> int:
        m = self.read(PAT_INT)
        x = int(m.group())
        if not -2**32 <= x <= 2**32-1:
            raise ReaderError
        return x

    def read_float(self, no_int_part_ok: bool = False) -> float:
        try:
            m = self.read(PAT_FLOAT)
        except ReaderError:
            if not no_int_part_ok:
                raise
            m = self.read(PAT_FLOAT_NOINT)
        return float(m.group())

    def argument_finish(self):
        if not self.is_terminating_char(self.peek()):
            raise ReaderError

    def _is_file_finish(self) -> bool:
        return self.pointer >= self.SRC_LEN

    def is_finish(self) -> bool:
        # We want End Of File to be read.
        return self.pointer > self.SRC_LEN

    @staticmethod
    def is_line_end(char: ReaderChar) -> bool:
        return char == "\n" or char is None

    @staticmethod
    def is_terminating_char(char: ReaderChar) -> bool:
        return char in TERMINATORS or char is None

    def skip_spaces(self):
        while self.peek() == " ":
            self.next()

    def read_until_eol(self) -> str:
        """Read until End Of Line.
        Return content read. "\n" is not consumed."""
        try:
            m = self.read(PAT_TILLEOL)
        except ReaderError:
            # No \n found, then EOF must indicate end of line
            m = self.read(PAT_TILLEOF)
        return m.group()

    def skip_current_line(self):
        self.read_until_eol()
        self.next()  # "\n"

    def get_location(self) -> CharLocation:
        return CharLocation(
            self.current_line, self.current_column, self.pointer)

    def linecol_to_location(self, line: int, column: int) -> CharLocation:
        m = re.match(r"((?:.*\n){%d})(.*)" % (line - 1), self.src)
        if m is None:
            raise ValueError("Invalid line %d" % line)
        R, L = m.groups()
        # `R`: All chars before `line` (including \n)
        # `L`: Chars on line `line`
        if column - 1 > len(L):
            raise ValueError("Invalid column %d" % column)
        return CharLocation(line, column, column - 1 + len(R))

    def get_slice(self, begin: CharLocation, end: CharLocation) -> str:
        return self.src[begin.pointer:end.pointer]

    def state_save(self) -> ReaderState:
        return ReaderState(self.get_location())

    def state_jump(self, state: ReaderState):
        self.current_line = state.line
        self.current_column = state.column
        self.pointer = state.pointer
        if self.pointer == 0 or self._is_file_finish():
            self.current_char = None
        else:
            self.current_char = self.src[self.pointer - 1]
