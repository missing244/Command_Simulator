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

from typing import (
    TYPE_CHECKING, List, Any,
    Callable, Union, Generic, TypeVar
)

from .ctxutils import contextmanager
from .parser import Font, SemanticError
from .autocompleter import AutoCompletingUnit
if TYPE_CHECKING:
    from .reader import Reader, CharLocation
    from .parser import Node, MCVersion

__all__ = [
    "Marker",
    "FontMark", "CheckerMark", "AutoCompletingMark",
]

class FontMark:
    """For colorizer to highlight code."""
    def __init__(self, begin: "CharLocation", end: "CharLocation",
                 font: Font):
        self.begin = begin
        self.end = end
        self.font = font

    def __repr__(self):
        return "<FontMark %s~%s %s>" % (self.begin, self.end, self.font.name)

_PT = TypeVar("_PT")

class CheckerMark(Generic[_PT]):
    """For generating semantic errors."""
    def __init__(
        self, begin: "CharLocation", end: "CharLocation",
        checkers: List[Callable[[_PT], Any]]
    ):
        self.begin = begin
        self.end = end
        self.checkers = checkers
        self.did_checker_run = False

    def __repr__(self):
        return "<CheckerMark %s~%s with %d checkers>" % (
            self.begin, self.end, len(self.checkers)
        )

    def set_result(self, result: _PT):
        self.result = result

    def trigger_checkers(self):
        assert hasattr(self, "result")
        self.did_checker_run = True
        for checker in self.checkers:
            try:
                checker(self.result)
            except SemanticError as err:
                err.set_range(self.begin, self.end)
                raise

class AutoCompletingMark:
    """For autocompleter to know which range of text is corresponding
    to an argument (`AutoCompletingUnit`)"""
    def __init__(self, begin: "CharLocation", end: "CharLocation",
                 unit_getter: Callable[[], AutoCompletingUnit]):
        self.begin = begin
        self.end = end
        self.get_unit = unit_getter

    def __repr__(self):
        return "<AutoCompletingMark begin=%s end=%s br=%s>" % (self.begin, self.end, self.get_unit().branches)

    def get_unit(self):
        raise NotImplementedError

    def covers(self, location: "CharLocation"):
        return self.begin < location <= self.end

    @classmethod
    def from_unit(cls, begin: "CharLocation", end: "CharLocation",
                  unit: AutoCompletingUnit):
        return cls(begin, end, lambda: unit)

    @classmethod
    def from_node(cls, begin: "CharLocation", end: "CharLocation",
                  node: "Node", version: "MCVersion"):
        # Calculating unit from node for every marks takes VERY LONG
        # time, so we store units as function.
        def _unit_getter():
            info = node.get_info_v(version)
            return AutoCompletingUnit(
                node.argument_end,
                list((node.suggest, is_c, is_a)
                     for node, is_c, is_a in info)
            )
        return cls(begin, end, _unit_getter)

class Marker:
    def __init__(self, reader: "Reader", version: "MCVersion"):
        self.reader = reader
        self.version = version
        self.font_marks = []
        self.checker_marks = []
        self.ac_marks = []

    @contextmanager
    def add_font_mark(self, font: Font):
        begin = self.reader.get_location()
        yield
        end = self.reader.get_location()
        mark = FontMark(begin, end, font)
        self.font_marks.append(mark)

    @contextmanager
    def add_checker_mark(self, checkers: List[Callable[[Any], Any]]):
        begin = self.reader.get_location()
        yield lambda res: mark.set_result(res)
        end = self.reader.get_location()
        mark = CheckerMark(begin, end, checkers)
        self.checker_marks.append(mark)

    @contextmanager
    def add_ac_mark(self, node: "Node"):
        begin = self.reader.get_location()
        yield
        end = self.reader.get_location()
        mark = AutoCompletingMark.from_node(begin, end, node, self.version)
        self.ac_marks.append(mark)

    def merge_to(self, other: "Marker"):
        other.ac_marks.extend(self.ac_marks)
        other.font_marks.extend(self.font_marks)
        other.checker_marks.extend(self.checker_marks)

    def enclosed_ac_mark(self, location: "CharLocation") \
            -> Union[AutoCompletingMark, None]:
        # XXX Special case: Line begin, return root node of the line
        if location.column == 1:
            for mark in self.ac_marks:
                if mark.begin == location:
                    assert mark.end == location
                    return mark
            raise ValueError("Invalid location")

        # Normal case:
        #  When a `Mark` covers this `location`, return it
        #  When no `Mark` covers it, return the mark before `location`
        prev_mark = None
        for mark in self.ac_marks:
            if mark.covers(location):
                return mark
            if mark.begin >= location:
                return prev_mark
            prev_mark = mark
        else:
            # Return last mark if all marks have been passed
            return prev_mark

    def previous_ac_mark(self, mark: AutoCompletingMark) \
            -> Union[AutoCompletingMark, None]:
        i = self.ac_marks.index(mark)
        if i >= 1:
            return self.ac_marks[i-1]
        else:
            return None

    def trigger_checkers(self):
        for mark in self.checker_marks:
            if not mark.did_checker_run:
                mark.trigger_checkers()
