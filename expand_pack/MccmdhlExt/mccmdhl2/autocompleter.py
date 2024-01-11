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

"""The auto-completer."""

from typing import (
    TYPE_CHECKING, Optional, List, Dict, Tuple,
    Union, Any, Callable, NewType
)
import json

from .reader import CharLocation
if TYPE_CHECKING:
    from .marker import Marker, AutoCompletingMark
    from .translator import Translator

__all__ = [
    "IdTable", "AutoCompleter",
    "Suggestion", "IdSuggestion", "HandledSuggestion",
    "RULEW_FAILED", "RULEW_STR_FIND", "RULEW_ID_NOTABLE", "RULEW_SPACE",
    "RULEW_OTHER", "str_find_rule"
]

RuleWeight = NewType("RuleWeight", int)
RULEW_SPACE = RuleWeight(15000)
RULEW_OTHER = RuleWeight(11000)
RULEW_STR_FIND = RuleWeight(10000)
RULEW_ID_NOTABLE = RuleWeight(1000)
RULEW_FAILED = RuleWeight(-1)

def str_find_rule(text: str, w: RuleWeight = RULEW_STR_FIND) \
        -> Callable[[str], RuleWeight]:
    def _res(pattern: str):
        f = text.find(pattern)
        if f == -1:
            return RULEW_FAILED
        else:
            return RuleWeight(w - f)
    return _res

class IdTable:
    def __init__(self, json: Dict[str, Dict[str, Union[str, None]]]):
        self.map = json

    def dump(self, path: str, **kwds):
        with open(path, "w", **kwds) as file:
            json.dump(self.map, file)

    @classmethod
    def from_json(cls, path: str, **kwds):
        with open(path, "r", **kwds) as file:
            j = json.load(file)
        return cls(j)

    @classmethod
    def merge_from(cls, *tables: "IdTable"):
        res = {}
        for table in tables:
            for key, subtable in table.map.items():
                if key in res:
                    res[key].update(subtable)
                else:
                    res[key] = subtable
        return cls(res)

    @classmethod
    def empty_table(cls):
        return cls({})

Refactor = Union[None, Callable[["HandledSuggestion"], None]]

class Suggestion:
    def __init__(self, name: str, writes: str,
                 match_rule: Callable[[str], RuleWeight],
                 note: Union[str, None] = None,
                 name_kwds: Dict[str, Any] = {},
                 refactor: Refactor = None):
        self.name = name
        self.note = note
        self.match_rule = match_rule
        assert writes
        self.writes = writes
        self.name_kwds = name_kwds
        self.refactor = refactor

    def __repr__(self):
        return "<Suggestion %r note=%r>" % (self.name, self.note)

    def translate(self, translator: "Translator") -> "HandledSuggestion":
        return HandledSuggestion(
            name=translator.get(self.name).format(**self.name_kwds),
            writes=self.writes,
            note=translator.get(self.note) if self.note else None,
            match_rule=self.match_rule,
            refactor=self.refactor
        )

    def set_refactor(self, refactor: Refactor):
        assert self.refactor is None
        self.refactor = refactor

class IdSuggestion:
    def __init__(self, name: str, note: Union[str, None] = None):
        self.name = name
        self.note = note
        self.refactor = None

    def resolve(self, id_table: IdTable) \
            -> List[Union[Suggestion, "HandledSuggestion"]]:
        res = []
        d = id_table.map.get(self.name)
        if d:
            for id_, note in d.items():
                if note is None:
                    note = self.note
                res.append(HandledSuggestion(
                    name=id_, writes=id_, note=note,
                    match_rule=str_find_rule(id_),
                    refactor=self.refactor
                ))
        else:
            res.append(Suggestion(
                name="autocomp.no_idtable." + self.name,
                writes="minecraft:",
                note="autocomp.no_idtable._hint",
                match_rule=lambda s: RULEW_ID_NOTABLE,
                refactor=self.refactor
            ))
        return res

    def set_refactor(self, refactor: Refactor):
        assert self.refactor is None
        self.refactor = refactor

class HandledSuggestion:
    def __init__(self, name: str, writes: str, note: Union[str, None],
                 match_rule: Callable[[str], RuleWeight],
                 refactor: Refactor = None):
        self.name = name
        self.note = note
        self.writes = writes
        self.match_rule = match_rule
        self.overwrite = None
        if refactor is not None:
            refactor(self)

    def __repr__(self):
        return "<HandledSuggestion %s>" % self.resolve()

    def resolve(self):
        res = self.name
        if self.note:
            res += " - " + self.note
        return res

    def set_overwrite_range(self, begin: "CharLocation", end: "CharLocation"):
        self.overwrite = (begin, end)

    def get_overwrite_range(self) -> Tuple["CharLocation", "CharLocation"]:
        # The range of overwriting
        # e.g. 'elp' -> HandledSuggestion(name="'help'", writes="help",
        #     note="xxxxx") overwrite=(<Ln 1 Col 1>, <Ln 1 Col 3>)
        # So that when you use the suggestion it would be 'help'
        # instead of 'elphelp'.
        if self.overwrite:
            return self.overwrite
        else:
            raise ValueError("Range not set yet")

class AutoCompletingUnit:
    def __init__(self,
        argument_end: bool,
        info: List[Tuple[
            Callable[[], List[Union[Suggestion, IdSuggestion]]],  # suggest
            bool,  # is_close
            bool,  # is_arg_end
        ]],
    ):
        self.argument_end = argument_end
        assert not (any(t[2] for t in info) and argument_end)
        self.info = info

class AutoCompleter:
    def __init__(self, marker: "Marker", id_table: Optional[IdTable] = None):
        self.marker = marker
        self.reader = marker.reader
        if not id_table:
            self.id_table = IdTable.empty_table()
        else:
            self.id_table = id_table

    def _inner_suggest(self, location: CharLocation, translator: "Translator",
                       mark: "AutoCompletingMark") -> List[HandledSuggestion]:
        # e.g. 'scoreboard playe' ->
        #   `unit` is `AutoCompletingUnit.from_node(Keyword("scoreboard"))`
        unit = mark.get_unit()
        # e.g. 'scoreboard playe' -> `text_between` = ' playe'
        text_between = self.reader.get_slice(mark.end, location)
        # `already_typed`: User typed content for this suggesting
        # argument.
        # `is_cursor_close`: Whether suggesting argument appears
        # directly after `node`.
        # e.g. 'scoreboard playe' ->
        #   `already_typed` = 'playe', `is_cursor_close` = False
        if not text_between:
            is_cursor_close = True
            already_typed = ""
        else:
            is_cursor_close = not self.reader.is_terminating_char(
                text_between[0])
            already_typed = text_between.strip()

        # Filter suggestions
        res1: List[Union[Suggestion, HandledSuggestion]] = []
        res1_extra: List[HandledSuggestion] = []
        def _expand(suggs: List[Union[Suggestion, IdSuggestion]]) \
                -> List[Union[Suggestion, HandledSuggestion]]:
            # Expand `IdSuggestion`s.
            res = []
            for sugg in suggs:
                if isinstance(sugg, IdSuggestion):
                    res.extend(sugg.resolve(self.id_table))
                else:
                    res.append(sugg)
            return res
        if is_cursor_close:
            # Cursor is next to `node` (e.g. '@e[x')
            # Part1. Suggestions from `node`
            # For instance, '=' for '@e[x'
            have_hidden_sugg = False
            for suggest, is_close, is_arg_end in unit.info:
                for sugg in _expand(suggest()):
                    if (unit.argument_end or is_arg_end):
                        if (self.reader.is_terminating_char(sugg.writes[0])
                            or is_close):
                            # OK if next argument starts with
                            # terminating char or is a close branch
                            res1.append(sugg)
                        else:
                            have_hidden_sugg = True
                    else:
                        # OK if the node does not require argument
                        # end before next argument.
                        res1.append(sugg)
            if have_hidden_sugg:
                res1.insert(0, Suggestion(
                    name="autocomp.space", writes=" ", note="note._space",
                    match_rule=lambda s: RULEW_FAILED if s else RULEW_SPACE
                ))
            # Part2. Suggestions from `node`'s parent
            # For instance, 'rx', 'rxm' for '@e[x'. On this condition,
            # we "assume" that Keyword("x") failed here and `node` is
            # Char("["), and we run this whole suggest algorithm again.
            # This is triggered only when cursor is at the end of `mark`.
            if not text_between:
                prev_mark = self.marker.previous_ac_mark(mark)
                # Previous mark must be in same line.
                if prev_mark and prev_mark.begin.line == mark.begin.line:
                    res1_extra = self._inner_suggest(
                        location, translator, prev_mark
                    )
        else:
            # Cursor is away from `node` (e.g. '@e[x ' and
            # 'scoreboard pl')
            for suggest, is_close, is_arg_end in unit.info:
                if not is_close:
                    res1.extend(_expand(suggest()))

        # Convert all `Suggestion`s to `HandledSuggestion`
        def _conv(s: Union[Suggestion, HandledSuggestion]) \
                -> HandledSuggestion:
            if isinstance(s, Suggestion):
                return s.translate(translator)
            return s
        res2: Tuple[HandledSuggestion] = tuple(map(_conv, res1))

        # Filter the available suggestions according to existing user
        # input (`already_typed`) for suggesting argument.
        #  - Associate `Suggestions` with the match result
        found = tuple(sugg.match_rule(already_typed) for sugg in res2)
        sugg2find = zip(res2, found)
        #  - Throw away suggestions that failed the find test
        sugg2find = filter(lambda arg: arg[1] != RULEW_FAILED, sugg2find)
        #  - Sort according to the place `already_typed` occurs
        sugg2find = sorted(sugg2find, key=lambda arg: arg[1], reverse=True)
        #  - Un-associate match results
        res3: List[HandledSuggestion] = [arg[0] for arg in sugg2find]

        # Calculate overwrite range
        # We want to keep the spaces (e.g. in 'help  s' only 's' need
        # to be replaced).
        _L = len(text_between)
        lspace = _L - len(text_between.lstrip())
        rspace = _L - len(text_between.rstrip())
        overw_begin = mark.end.offset(lspace)
        overw_end = location.offset(-rspace)
        overw_text = self.reader.get_slice(overw_begin, overw_end)

        # Translate and overwrite range
        res4 = []
        for sugg in res3:
            sugg.set_overwrite_range(begin=overw_begin, end=overw_end)
            if overw_text != sugg.writes:
                # If user has written the text we suggests, don't give
                # that hint.
                # XXX This relies on `writes`, which does not make
                # sense (e.g. "1.0" won't match `Float`'s suggestion
                # which is "0.0".)
                res4.append(sugg)
        res4.extend(res1_extra)
        return res4

    def suggest(self, location: CharLocation, translator: "Translator") \
            -> List[HandledSuggestion]:
        # General idea of auto completer:
        #  We first find the `Mark` where the cursor is, then
        #  `mark.owner` is the `Node` that wrote this `Mark` and
        #  its branches should be the text that can go after here.
        mark = self.marker.enclosed_ac_mark(location)
        if mark is None:
            return []
        else:
            return self._inner_suggest(location, translator, mark)
