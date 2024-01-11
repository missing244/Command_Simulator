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

"""`mccmdhl2` - The Minecraft Bedrock Edition command parser.
Command system of Minecraft Bedrock Edition version 1.19.0+ is
supported.  Friendly messages are given when failed to parse.
Autocompleter can give you suggestions on what to type next and
explain meanings of different choices.
"""

from typing import (
    Optional as _Optional, List as _List,
    TYPE_CHECKING as _TYPE_CHECKING
)

from .reader import *
from .marker import *
from .parser import *
from .translator import *
from .nodes import Command, MCFuncLine
from .autocompleter import *
if _TYPE_CHECKING:
    from .parser import MCVersion

_DEFAULT_TREE = None

def get_default_tree() -> Node:
    """Load and get the default tree used by parser."""
    global _DEFAULT_TREE
    if _DEFAULT_TREE is None:
        _DEFAULT_TREE = MCFuncLine()
    return _DEFAULT_TREE

def load_resources():
    """(Re)Load default `IdTable` & `Translator`."""
    global BASE_ID_TABLE, BASE_TRANSLATOR
    import os
    mccmdhl2 = os.path.realpath(os.path.dirname(__file__))
    res_path = os.path.join(mccmdhl2, "res")
    table_path = os.path.join(res_path, "id_table.json")
    if os.path.exists(table_path):
        BASE_ID_TABLE = IdTable.from_json(table_path)
    else:
        BASE_ID_TABLE = IdTable.empty_table()
    translation_path = os.path.join(res_path, "translation.json")
    if os.path.exists(translation_path):
        BASE_TRANSLATOR = Translator.from_json(translation_path)
    else:
        BASE_TRANSLATOR = Translator.empty_translation()

load_resources()

class MCCmdParser:
    def __init__(self, src: str,
                 tree: _Optional[Node] = None,
                 version: "MCVersion" = (1, 19, 80),
                 translator: _Optional[Translator] = None):
        if tree is None:
            self.tree = get_default_tree()
        else:
            self.tree = tree
        if not isinstance(self.tree, Empty):
            # Make sure there's an empty root node for autocompleter
            self.tree = Empty().branch(self.tree)
        if not self.tree.frozen:
            self.tree.freeze()
        if translator is None:
            self.translator = BASE_TRANSLATOR
        else:
            self.translator = Translator.merge_from(
                BASE_TRANSLATOR, translator
            )
        self.reader = Reader(src)
        self.marker = Marker(self.reader, version)
        self.has_parsed = False

    def parse_line(self):
        """Parse 1 line of source. `BaseError` is thrown when
        any error occurs. The error message can be resolved using
        `resolve_error` method.
        After parsing, the color information are of `FontMark` type
        and can be obtained using `get_font_marks` method.
        """
        assert not self.has_parsed, "Repeat parsing"
        if self.reader.is_finish():
            self.has_parsed = True
            return
        try:
            self.tree.parse(self.marker)
        except SyntaxError_:
            # When failed to parse, we still didn't finish this line
            # yet, so skip it here
            self.reader.skip_current_line()
            raise
        # Trigger checkers (raises `SemanticError`)
        self.marker.trigger_checkers()

    def is_finish(self) -> bool:
        """Return whether we have finished parsing."""
        return self.has_parsed

    def suggest(self, line: int, column: int,
                id_table: _Optional[IdTable] = None) \
            -> _List[HandledSuggestion]:
        """Predict and give suggestions on what to type next after
        location specified by `line` and `column`.
        """
        if not self.has_parsed:
            raise RuntimeError("Source must be parsed completely before "
                "suggesting")
        if id_table:
            table = IdTable.merge_from(id_table, BASE_ID_TABLE)
        else:
            table = BASE_ID_TABLE
        location = self.reader.linecol_to_location(line, column)
        autocomp = AutoCompleter(self.marker, table)
        return autocomp.suggest(location, self.translator)

    def get_font_marks(self) -> _List[FontMark]:
        """Get `Mark`s (tokens)."""
        if not self.has_parsed:
            raise RuntimeError("Source must be parsed completely before "
                "producing marks")
        return self.marker.font_marks

    def resolve_error(self, err: BaseError) -> str:
        """Return string form of `BaseError`"""
        return err.resolve(self.translator)
