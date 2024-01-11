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

"""Node definition of Minecraft command arguments and the tree
definition.
"""

from typing import (
    Dict, List, Callable, Optional, Any, TypeVar, Union,
    TYPE_CHECKING
)
import itertools
import json
import re

from .parser import (
    Node, Empty, Finish, CompressedNode, SubparsingNode,
    ArgParseFailure, ExpectationFailure,
    BaseError, SemanticError, SyntaxError_,
    Font, VersionFilter
)
from .reader import Reader, ReaderError, DIGITS, TERMINATORS, SIGNS
from .autocompleter import (
    Suggestion, IdSuggestion,
    str_find_rule, RULEW_OTHER, RULEW_FAILED, RULEW_STR_FIND, RuleWeight
)
from .marker import FontMark, AutoCompletingMark, CheckerMark, Marker
if TYPE_CHECKING:
    from .reader import CharLocation
    from .parser import MCVersion
    from .translator import Translator
    from .autocompleter import IdTable, HandledSuggestion

NAMESPACEDID = frozenset("0123456789:._-abcdefghijklmnopqrstuvwxyz")

# Test result in MCBE 1.20.0
PAT_ILLEGAL_WORD = re.compile(
    r"""
    (
      [+-]?\d+
      (
        (\.\..*)  # anything starting with "1.." is invalid
        |
        (\.\d*)  # floating number is invalid
      )?  # integer is invalid
    )
    |
    (\.\.[+-]?\d+)  # "..1" is invalid while "..1a" is OK
    """,
    flags=re.VERBOSE
)

def char_check_rule(checker: Callable[[str], bool]):
    def _rule(s: str):
        if all(map(checker, s)):
            return RULEW_OTHER
        else:
            return RULEW_FAILED
    return _rule
def char_rule(char: str):
    def _rule(s: str):
        if (not s) or (s == char):
            return RULEW_OTHER
        return RULEW_FAILED
    return _rule

class VersionGe(VersionFilter):
    def __init__(self, version: "MCVersion"):
        self.version = version

    def validate(self, version: "MCVersion") -> bool:
        return version >= self.version

class VersionLt(VersionFilter):
    def __init__(self, version: "MCVersion"):
        self.version = version

    def validate(self, version: "MCVersion") -> bool:
        return version < self.version

def re_word(pat: str, **kwds):
    return re.compile(r'(\b|\s+)(%s)(\b|\s+)' % pat, **kwds)

def dict_getter(d: dict, *path: List[str]):
    try:
        for s in itertools.chain(*path):
            d = d[s]
    except KeyError:
        return None
    return d

# Use these CAREFULLY:
def _end_subparse(node: Node):
    finish = Finish()
    if isinstance(node, CompressedNode):
        # Walk through whole tree to find `node.end`
        node.end.branch(finish)
        walked = []
        def _walk(n: Node):
            walked.append(n)
            for branch in n.branches:
                if branch is node.end:
                    n.close_branches.append(branch)
                elif branch not in walked:
                    _walk(branch)
        _walk(node)
    else:
        node.branch(finish, is_close=True)
def _node_subparse(self: SubparsingNode, node: Node, marker: "Marker"):
    reader = marker.reader
    tree = Empty().branch(node)
    tree.freeze()
    tree.parse(marker)
    pos = reader.get_location()
    # XXX Since the `node`'s branch is just `Finish()`, no hint
    # will be given after this. We need to override that finish
    # node using `self`'s branches.
    if not isinstance(node, SubparsingNode):
        orig = marker.ac_marks[-1]
        marker.ac_marks[-1] = AutoCompletingMark.from_node(
            orig.begin, orig.end, self, marker.version
        )
    else:
        marker.ac_marks.append(AutoCompletingMark.from_node(
            pos.offset(-1), pos, self, marker.version
        ))

class Char(Node):
    argument_end = False

    def __init__(self, char: str):
        super().__init__()
        self.char = char

    def _parse(self, reader: Reader):
        if reader.peek() == self.char:
            reader.next()
        else:
            raise ExpectationFailure("char", char=self.char)

    def _suggest(self):
        return [Suggestion(
            name="autocomp.char",
            writes=self.char,
            name_kwds={"char": self.char},
            match_rule=char_rule(self.char)
        )]

INF = float("inf")

class Numeric(Node):
    default_font = Font.numeric

    def _parse(self, reader: Reader) -> float:
        raise NotImplementedError

    def ranged(self, min=-INF, max=INF):
        def _checker(res: float):
            if not min <= res <= max:
                raise SemanticError("error.semantic.number.out_of_range",
                                    min=min, max=max)
        return self.checker(_checker)

    def none_of(self, *numbers: float):
        def _checker(res: float):
            if res in numbers:
                raise SemanticError("error.semantic.number.cant_be", num=res)
        return self.checker(_checker)

    def one_of(self, *numbers: float):
        def _checker(res: float):
            if res not in numbers:
                raise SemanticError("error.semantic.number.must_be",
                                    nums=numbers)
        return self.checker(_checker)

class Integer(Numeric):
    def _parse(self, reader: Reader):
        try:
            res = reader.read_int()
        except ReaderError:
            raise ExpectationFailure("int")
        else:
            return res

    def _suggest(self):
        return [Suggestion(
            name="autocomp.integer", writes="0",
            match_rule=char_check_rule(
                lambda char: char in DIGITS or char in SIGNS
            )
        )]

class Float(Numeric):
    def _parse(self, reader: Reader):
        try:
            res = reader.read_float()
        except ReaderError:
            raise ExpectationFailure("float")
        else:
            return res

    def _suggest(self):
        return [Suggestion(
            name="autocomp.float", writes="0.0",
            match_rule=char_check_rule(
                lambda char: char in DIGITS or char in SIGNS or char == "."
            )
        )]

class Word(Node):
    default_font = Font.string

    def _parse(self, reader: Reader):
        word = reader.read_word()
        if not word:
            raise ExpectationFailure("word")
        if PAT_ILLEGAL_WORD.fullmatch(word):
            raise ArgParseFailure("error.syntax.illegal_word")
        return word

    @classmethod
    def _suggest(cls):
        return [Suggestion(
            name="autocomp.word", writes="word",
            match_rule=char_check_rule(
                lambda char: char not in TERMINATORS
            )
        )]

class Boolean(Word):
    default_font = Font.numeric

    def _parse(self, reader: Reader):
        word = reader.read_word()
        if word != "true" and word != "false":
            raise ExpectationFailure("bool")
        return word

    def _suggest(self):
        return [
            Suggestion(
                name="autocomp.true", writes="true",
                match_rule=str_find_rule("true")
            ),
            Suggestion(
                name="autocomp.false", writes="false",
                match_rule=str_find_rule("false")
            )
        ]

class NamespacedId(Word):
    def __init__(self, id_type: str):
        self.id_type = id_type
        super().__init__()

    def _parse(self, reader: Reader):
        word = super()._parse(reader)
        for char in word:
            if char not in NAMESPACEDID:
                raise ArgParseFailure("error.syntax.id_invalid", char=char)
        return word

    def _suggest(self):
        return [IdSuggestion(self.id_type)]

class QuotedString(SubparsingNode):
    argument_end = False
    default_font = Font.string

    def _parse(self, marker: "Marker"):
        reader = marker.reader
        pos_begin = reader.get_location()
        with marker.add_font_mark(Font.meta):  # type: ignore # Opening '"'
            if reader.next() != '"':
                raise ExpectationFailure("quoted_str")
        chars = []
        pos0 = reader.get_location()
        char = reader.next()
        while True:
            if char == '"' or reader.is_line_end(char):
                break
            if char == "\\":
                f = True
                char2 = reader.next()
                if char2 == "\\":
                    chars.append("\\")
                elif char2 == '"':
                    chars.append('"')
                else:
                    f = False
                    chars.append(char)
                    chars.append(char2)
                if f:
                    marker.font_marks.append(FontMark(
                        pos0, reader.get_location(), Font.meta
                    ))  # Escape
            else:
                chars.append(char)
            pos0 = reader.get_location()
            char = reader.next()
        if char != '"':
            raise ArgParseFailure("error.syntax.unclosed_str")
        pos_end = reader.get_location()
        marker.font_marks.append(FontMark(
            pos_end.offset(-1), pos_end, Font.meta
        ))  # Closing '"'
        marker.ac_marks.append(AutoCompletingMark.from_node(
            pos_begin, pos_end, self, marker.version
        ))
        return "".join(chars)

    @staticmethod
    def _rule(s: str):
        if not s:
            return RULEW_OTHER
        elif s[0] == '"':
            return RULEW_OTHER
        else:
            return RULEW_FAILED

    @classmethod
    def _suggest(cls):
        return [Suggestion(
            name="autocomp.quoted_string", writes='"string"',
            match_rule=cls._rule
        )]

class String(CompressedNode):
    def _tree(self):
        self._word_part = Word()
        self._qstr_part = QuotedString()
        (self
          .branch(
            self._word_part
              .branch(self.end)
          )
          .branch(
            self._qstr_part
              .branch(self.end)
          )
        )

class IdEntity(NamespacedId):
    def __init__(self):
        super().__init__("entity")
class IdItem(NamespacedId):
    def __init__(self):
        super().__init__("item")
class IdBlock(NamespacedId):
    def __init__(self):
        super().__init__("block")
class _StringOverrideSuggest(String):
    def __init__(self, suggest):
        super().__init__()
        self._word_part._suggest = suggest
        self._qstr_part._suggest = lambda: []
class IdFamily(_StringOverrideSuggest):
    def __init__(self):
        super().__init__(lambda: [IdSuggestion("family")])
class IdEntitySlot(Word):
    def _suggest(self):
        return [IdSuggestion("entity_slot")]
class IdBlockSlot(Word):
    def _suggest(self):
        return [IdSuggestion("block_slot")]
class IdDamageType(NamespacedId):
    def __init__(self):
        super().__init__("damage")
class IdEffect(NamespacedId):
    def __init__(self):
        super().__init__("effect")
class IdEnchantment(NamespacedId):
    def __init__(self):
        super().__init__("enchantment")
class IdEntityEvent(_StringOverrideSuggest):
    def __init__(self):
        super().__init__(lambda: [IdSuggestion("entity_event")])
class IdFog(NamespacedId):
    def __init__(self):
        super().__init__("fog")
class GameRule(Word):
    def _suggest(self):
        return [IdSuggestion("game_rule")]
class IdPermission(Word):
    def _suggest(self):
        return [IdSuggestion("permission")]
class IdStructure(Word):
    def _suggest(self):
        return [IdSuggestion("structure")]
class IdBiome(NamespacedId):
    def __init__(self):
        super().__init__("biome")
class IdMobEvent(NamespacedId):
    def __init__(self):
        super().__init__("mob_event")
class IdMusic(Word):
    def _suggest(self):
        return [IdSuggestion("music")]
class IdSound(Word):
    def _suggest(self):
        return [IdSuggestion("sound")]
class IdLootTable(_StringOverrideSuggest):
    def __init__(self):
        super().__init__(lambda: [IdSuggestion("loot_table")])
class IdAnimationRef(_StringOverrideSuggest):
    def __init__(self):
        super().__init__(lambda: [IdSuggestion("animation_ref")])
class IdRPACState(_StringOverrideSuggest):
    def __init__(self):
        super().__init__(lambda: [IdSuggestion("rpac_state")])
class IdRPAC(_StringOverrideSuggest):
    def __init__(self):
        super().__init__(lambda: [IdSuggestion("rpac")])
class IdRecipe(_StringOverrideSuggest):
    def __init__(self):
        super().__init__(lambda: [IdSuggestion("recipe")])
class IdCameraPreset(NamespacedId):
    def __init__(self):
        super().__init__("camera_preset")
class IdEaseType(Word):
    def _suggest(self):
        return [IdSuggestion("ease_type")]
class IdAbility(Word):
    def _suggest(self):
        return [IdSuggestion("ability")]
class IdParticle(NamespacedId):
    def __init__(self):
        super().__init__("particle")

def ItemData(is_test: bool):
    return (Integer()
      .ranged(min=-1 if is_test else 0, max=32767)
      .note("note._item_data")
    )

class EntitySlot(CompressedNode):
    def _tree(self):
        (self
          .branch(
            IdEntitySlot()
              .branch(
                Integer()
                  .note("note._slot_number")
                  .branch(self.end)
              )
          )
        )

class BlockSlot(CompressedNode):
    def _tree(self):
        (self
          .branch(
            IdBlockSlot()
              .branch(
                Integer()
                  .note("note._slot_number")
                  .branch(self.end)
              )
          )
        )

_PT = TypeVar("_PT")

def ResultTracked(node: Node[_PT], callback: Callable[[_PT], Any]):
    """Call `callback` when `node` successfully parsed."""
    orig = node._parse
    def _new_parse(reader):
        v = orig(reader)
        callback(v)
        return v
    node._parse = _new_parse
    return node

class _DynamicIdSuggestion(IdSuggestion):
    def __init__(self, path: List[str],
        orig_suggest: Callable[[], List[Union[Suggestion, IdSuggestion]]],
        map_handler: Callable[[Union[dict, list]],
                              Union[List[str], Dict[str, str]]],
        note: Union[str, None] = None
    ):
        super().__init__(path[0], note)
        self.__path = path
        self.__orig_suggest = orig_suggest
        self.__map_handler = map_handler

    def resolve(self, id_table: "IdTable") \
            -> List[Union[Suggestion, "HandledSuggestion"]]:
        val = id_table.map
        try:
            for k in self.__path:
                if not isinstance(val, dict):
                    raise TypeError
                val = val[k]
        except (KeyError, TypeError):
            res = []
            for s in self.__orig_suggest():
                if isinstance(s, Suggestion):
                    s.note = "autocomp.dynamic_id_fails"
                    res.append(s)
                elif isinstance(s, IdSuggestion):
                    res.extend(s.resolve(id_table))
            return res
        else:
            assert isinstance(val, (list, dict))
            val = self.__map_handler(val)
            if isinstance(val, list):
                val = dict.fromkeys(val)
            def _map(arg):
                sv = str(arg[0])
                return Suggestion(
                    name=sv, writes=sv, note=arg[1] if arg[1] else self.note,
                    match_rule=str_find_rule(sv)
                )
            return list(map(_map, val.items()))

def DynamicId(node: Node, path_getter: Callable[[], List[str]],
              map_handler: Callable[[Union[dict, list]],
                                    Union[List[str], Dict[str, str]]]
                         = lambda d: d):
    """Return the `node` that use suggestions from `IdTable`s, but
    the ID is dynamic (related to context). `path_getter` should return
    the path to values in `IdTable`, like
    `["block_state", "bamboo", "str", "leaves"]`.
    """
    orig_suggest = node._suggest
    def _new_suggest():
        return [_DynamicIdSuggestion(
            path_getter(), orig_suggest, map_handler)]
    node._suggest = _new_suggest  # type: ignore
    return node

class BlockSpec(CompressedNode):
    class _BlockStatePair(CompressedNode):
        def __init__(self, parent_path: Callable[[], List[str]]):
            self.__parent_path = parent_path
            super().__init__()

        def _tree(self):
            self.__key = None
            def _set_key(value: str):
                self.__key = value
            def _get_vpath(type_: str):
                def _res():
                    assert self.__key is not None
                    l = self.__parent_path()
                    l.append(type_)
                    l.append(self.__key)
                    return l
                return _res
            def _kmap_handler(map_):
                # `map_` is supposed to be `Dict[str, Dict[str, List[Any]]]`
                # e.g. {"int": {"foo_state": [0, 1, 2, 3]}}
                res: List[str] = []
                for k in ("int", "bool", "str"):
                    if k in map_:
                        res.extend(['"%s"' % s for s in map_[k].keys()])
                return res
            _value = (Empty()
              .branch(
                DynamicId(QuotedString(), _get_vpath("str"))
                  .note("note._block_state.value")
                  .branch(self.end)
              )
              .branch(
                DynamicId(Integer(), _get_vpath("int"))
                  .note("note._block_state.value")
                  .branch(self.end)
              )
              .branch(
                DynamicId(Boolean(), _get_vpath("bool"))
                  .note("note._block_state.value")
                  .branch(self.end)
              )
            )
            (self
              .branch(
                DynamicId(
                    ResultTracked(QuotedString(), _set_key),
                    self.__parent_path, _kmap_handler
                )
                  .note("note._block_state.key")
                  .branch(
                    Char(":")
                      .branch(_value),
                    version=VersionLt((1, 20, 10))
                  )
                  .branch(
                    Char("=")
                      .branch(_value),
                    version=VersionGe((1, 20, 10))
                  )
              )
            )

    def __init__(self, bs_optional: Optional[Node] = None):
        """bs_optional: allow omitting block state and just write
        this node after block ID. This only matters <1.19.80,
        since any id can omit block state >=1.19.80.
        """
        self.__bs_node = bs_optional
        super().__init__()

    def _tree(self):
        self.__block_id = None
        def _set_block_id(value: str):
            if value.startswith("minecraft:"):
                value = value[10:]
            self.__block_id = value
        def _get_path():
            return ["block_state", self.__block_id]
        root = ResultTracked(IdBlock(), _set_block_id)
        (self
          .branch(
            root
              # Block data (deprecated since 1.19.70)
              .branch(
                Integer()
                  .note("note._block_data")
                  .branch(self.end),
                version=VersionLt((1, 19, 70))
              )
              # Block state
              .branch(
                Series(
                  begin=Char("[")
                    .note("note._block_state.begin"),
                  end=Char("]")
                    .note("note._block_state.end"),
                  separator=Char(",")
                    .note("note._block_state.separator"),
                  content=self._BlockStatePair(_get_path),
                  empty_ok=True
                )
                  .branch(self.end)
              )
              # Above 1.19.80, Block state can be omitted
              .branch(self.end, version=VersionGe((1, 19, 80)))
          )
        )
        if self.__bs_node:
            root.branch(self.__bs_node,
                        # Without version filter, there may be 2
                        # "(Line Finish)" hints when version >=
                        # 1.19.80.
                        version=VersionLt((1, 19, 80)))

class Keyword(Node):
    default_font = Font.keyword

    def __init__(self, word: str):
        super().__init__()
        self.word = word

    def _parse(self, reader: Reader):
        if reader.read_word() != self.word:
            raise ExpectationFailure("keyword", keyword=self.word)

    def _suggest(self):
        return [Suggestion(
            name="autocomp.keyword",
            writes=self.word,
            name_kwds={"keyword": self.word},
            match_rule=str_find_rule(self.word)
        )]

class Enumerate(Node):
    default_font = Font.keyword

    def __init__(self, *options: str, note_table: Dict[str, str] = {}):
        super().__init__()
        self.options = options
        self.note_table = note_table

    def _parse(self, reader: Reader):
        word = reader.read_word()
        if word not in self.options:
            raise ExpectationFailure("enum", options=self.options)
        return word

    def _suggest(self):
        return [
            Suggestion(
                name="autocomp.option",
                writes=word,
                note=self.note_table.get(word),
                name_kwds={"option": word},
                match_rule=str_find_rule(word)
            )
            for word in self.options
        ]

def NotedEnumerate(*options: str, note_template: str):
    note_table = {}
    for o in options:
        note_table[o] = note_template % o
    return Enumerate(*options, note_table=note_table)

class Invertable(CompressedNode):
    def __init__(self, node: Node):
        self.node = node
        super().__init__()

    def _tree(self):
        self.node.branch(self.end)
        (self
          .branch(
            self.node
          )
          .branch(
            Char("!")
              .note("note._invert")
              .font(Font.meta)
              .branch(
                self.node
              )
          )
        )

class Chars(Node):
    """Multiple characters.
    `Chars("!=")` <==> `Char("!").branch(Char("="), is_close=True)`.
    In auto-completion "!=" will be treated as a single suggestion,
    but not first "!" then "=".
    """
    argument_end = False
    default_font = Font.meta

    def __init__(self, chars: str):
        super().__init__()
        self.chars = chars

    def _parse(self, reader: Reader):
        for char in self.chars:
            if reader.next() != char:
                raise ExpectationFailure("chars", chars=self.chars)

    def _suggest(self):
        return [Suggestion(
            name="autocomp.chars",
            writes=self.chars,
            name_kwds={"chars": self.chars},
            match_rule=str_find_rule(self.chars)
        )]

class CharsEnumerate(CompressedNode):
    def __init__(self, *strings: str, note_template: Optional[str] = None):
        self.strings = strings
        self.note_template = note_template
        super().__init__()

    def _tree(self):
        for chars in self.strings:
            self.branch(
              Chars(chars)
                .note(self.note_template % chars
                      if self.note_template else None)
                .branch(self.end)
            )

class IntegerNoEnd(Integer):
    """An integer that does not require argument terminator."""
    argument_end = False

class _RawIntRange(CompressedNode):
    """Un-invertable integer range."""
    def _tree(self):
        (self
          .branch(
            IntegerNoEnd()
            # If we use regular `Integer` here, there must be space
            # between integer and "..".
              .branch(
                Chars("..")
                  .note("note._int_range")
                  .branch(self.end)
                  .branch(
                    Integer()
                      .branch(self.end)
                  )
              )
              .branch(
                # Since we used `IntegerNoEnd` above, when there is
                # actually no ".." after integer, the terminator
                # should come back.
                  self.end, require_arg_end=True
              )
          )
          .branch(
            Chars("..")
              .note("note._int_range")
              .branch(
                Integer()
                  .branch(self.end)
              )
          )
        )

def IntRange():
    return Invertable(_RawIntRange())

class BareText(Node):
    default_font = Font.string

    def __init__(self, empty_ok: bool):
        super().__init__()
        self.__empty_ok = empty_ok

    def _parse(self, reader: Reader):
        s = reader.read_until_eol()
        if not s and not self.__empty_ok:
            raise ExpectationFailure("bare_text")
        return s

    def _suggest(self):
        return [Suggestion(
            name="autocomp.bare_text", writes="text",
            match_rule=lambda s: RULEW_OTHER
        )]

class OffsetFloat(Node):
    default_font = Font.position

    def _parse(self, reader: Reader):
        try:
            res = reader.read_float(no_int_part_ok=True)
        except ReaderError:
            raise ExpectationFailure("offset_float")
        else:
            return res

    def _suggest(self):
        return [Suggestion(
            name="autocomp.offset_float", writes="0",
            match_rule=char_check_rule(
                lambda char: char in DIGITS or char in SIGNS or char == "."
            )
        )]

class Pos(CompressedNode):
    def __init__(self, type_: str):
        self._type = type_
        super().__init__()

    def _tree(self):
        (self
          .branch(
            Float()
              .font(Font.position)
              .note("note._pos.absolute." + self._type)
              .branch(self.end)
          )
          .branch(
            Char("~")
              .font(Font.position)
              .note("note._pos.relative." + self._type)
              .branch(
                OffsetFloat()
                  .font(Font.position)
                  .note("note._pos.float_offset")
                  .branch(self.end),
                is_close=True
              )
              .branch(self.end)
          )
        )

class LocalPos(CompressedNode):
    def __init__(self, type_: str):
        self._type = type_
        super().__init__()

    def _tree(self):
        (self
          .branch(
            Char("^")
              .font(Font.position)
              .note("note._pos.local." + self._type)
              .branch(
                OffsetFloat()
                  .font(Font.position)
                  .note("note._pos.float_offset")
                  .branch(self.end),
                is_close=True
              )
              .branch(self.end)
          )
        )

class Pos3D(CompressedNode):
    def _tree(self):
        for cls in (Pos, LocalPos):
            (self
              .branch(
                cls("x")
                  .branch(
                    cls("y")
                      .branch(
                        cls("z")
                          .branch(self.end)
                      )
                  )
              )
            )

class Rotation(CompressedNode):
    def __init__(self, type_: str):
        self._type = type_
        super().__init__()

    def _tree(self):
        (self
          .branch(
            Float()
              .font(Font.rotation)
              .note("note._rot.absolute." + self._type)
              .branch(self.end)
          )
          .branch(
            Char("~")
              .font(Font.rotation)
              .note("note._rot.relative." + self._type)
              .branch(
                OffsetFloat()
                  .font(Font.rotation)
                  .note("note._rot.float_offset")
                  .branch(self.end),
                is_close=True
              )
              .branch(self.end)
          )
        )

class YawPitch(CompressedNode):
    def _tree(self):
        (self
          .branch(
            Rotation("x")
              .branch(
                Rotation("y")
                  .branch(self.end)
              )
          )
        )

class GameMode(CompressedNode):
    def __init__(self, allow_5: bool, allow_legacy_6=False):
        self.allow_5 = allow_5
        self.allow_legacy_6 = allow_legacy_6
        super().__init__()

    def _note_table(self) -> Dict[str, str]:
        res: Dict[str, str] = {}
        for mode in ("spectator", "adventure", "creative",
                     "survival", "default"):
            res[mode] = "note._gamemode." + mode
        res["s"] = res["survival"]
        res["c"] = res["creative"]
        res["d"] = res["default"]
        res["a"] = res["adventure"]
        return res

    def _allow_ids(self) -> List[int]:
        res = [0, 1, 2]
        if self.allow_5:
            res.append(5)
        return res

    def _tree(self):
        int_ids = self._allow_ids()
        legacy_ids = int_ids.copy()
        if self.allow_legacy_6:
            legacy_ids.append(6)
        (self
          .branch(
            Enumerate("spectator", "adventure", "survival", "creative",
                      "default", "s", "c", "a", "d",
                      note_table=self._note_table())
              .branch(self.end)
          )
          .branch(
            Integer()
              .one_of(*int_ids)
              .font(Font.keyword)
              .note("note._gamemode._number")
              .branch(self.end),
            version=VersionGe((1, 19, 30))
          )
          .branch(
            Integer()
              .one_of(*legacy_ids)
              .font(Font.keyword)
              .note("note._gamemode._number")
              .branch(self.end),
            version=VersionLt((1, 19, 30))
          )
        )

def PermissionState(note: Optional[str] = None):
    note_map = {"enabled": "note._states.enabled",
                "disabled": "note._states.disabled"}
    if note is not None:
        note_map["enabled"] = note_map["disabled"] = note
    return (Enumerate("enabled", "disabled", note_table=note_map)
      .font(Font.numeric)
    )

class Series(CompressedNode):
    def __init__(self, begin: Node, content: Node,
                       separator: Node, end: Node,
                       empty_ok: bool):
        self.begin = begin
        self.content = content
        self.separator = separator
        self.end_ = end
        self.empty_ok = empty_ok
        super().__init__()

    def _tree(self):
        self.end_.branch(self.end)
        self.branch(
          self.begin
            .branch(
              self.content
                .branch(
                  self.separator
                    .branch(self.content)
                )
                .branch(
                  self.end_
                )
            )
        )
        if self.empty_ok:
            self.begin.branch(
              self.end_
            )

class KeywordCaseInsensitive(Keyword):
    def _parse(self, reader: Reader):
        if reader.read_word().lower() != self.word:
            raise ExpectationFailure("keyword", keyword=self.word)

    def _rule(self, pattern: str):
        f = self.word.find(pattern.lower())
        if f == -1:
            return RULEW_FAILED
        else:
            return RuleWeight(RULEW_STR_FIND - f)

    def _suggest(self):
        res = super()._suggest()
        for r in res:
            r.match_rule = self._rule
        return res

class SelectorArg(CompressedNode):
    class _HasItem(CompressedNode):
        def _hasitem_object(self):
            return Series(
              begin=Char("{")
                .note("note._selector.complex.hasitem.begin.object"),
              end=Char("}")
                .note("note._selector.complex.hasitem.end.object"),
              separator=Char(",")
                .note("note._selector.complex.hasitem.separator.object"),
              content=self._HasItemArg(),
              empty_ok=False
            )

        def _tree(self):
            (self
              .branch(
                self._hasitem_object()
                  .branch(self.end)
              )
              .branch(
                Series(
                  begin=Char("[")
                    .note("note._selector.complex.hasitem.begin.array"),
                  end=Char("]")
                    .note("note._selector.complex.hasitem.end.array"),
                  separator=Char(",")
                    .note("note._selector.complex.hasitem.separator.array"),
                  content=self._hasitem_object(),
                  empty_ok=False
                )
                  .branch(self.end)
              )
            )

        class _HasItemArg(CompressedNode):
            def _tree(self):
                for arg, node in (
                    ("item", IdItem()),
                    ("data", ItemData(is_test=True)),
                    ("quantity", IntRange()),
                    ("location", IdEntitySlot()),
                    ("slot", IntRange())
                ):
                    self.branch(
                      Keyword(arg)
                        .note("note._selector.complex.hasitem." + arg)
                        .branch(
                          Char("=")
                            .note("note._selector.complex.hasitem.equals")
                            .branch(
                              node
                                .branch(self.end)
                            )
                        )
                    )

    class _RawTag(CompressedNode):
        def _tree(self):
            (self
              .branch(
                String()
                .font(Font.tag)
                .note("note._selector.complex.tag")
                .branch(self.end)
              )
              .branch(
                # Yep, @e[tag=] is legal and it selects entities
                # without any tag.
                self.end
              )
            )

    class _ScoresArg(CompressedNode):
        def _tree(self):
            (self
              .branch(
                String()
                .note("note._scoreboard")
                .font(Font.scoreboard)
                .branch(
                  Char("=")
                    .branch(
                      IntRange()
                        .branch(self.end)
                    )
                )
              )
            )

    class _HasPermissionArg(CompressedNode):
        def _tree(self):
            (self
              .branch(
                IdPermission()
                  .branch(
                    Char("=")
                      .branch(
                        PermissionState()
                          .branch(self.end)
                      )
                  )
              )
            )

    @staticmethod
    def _XRotation():
        return (Float()
          .note("note._rot.absolute.x")
          .font(Font.rotation)
          .ranged(min=-90, max=90)
        )
    @staticmethod
    def _YRotation():
        return (Float()
          .note("note._rot.absolute.y")
          .font(Font.rotation)
          .ranged(min=-180, max=180)
        )

    def _tree(self):
        def _handle(arg: str, node: Node, kwds: Dict[str, Any] = {}):
            self.branch(
              KeywordCaseInsensitive(arg)
                .note("note._selector.complex.arg_names." + arg)
                .branch(
                  Char("=")
                    .note("note._selector.complex.equals")
                    .branch(
                      node
                        .branch(self.end)
                    )
                ),
              **kwds
            )
        for args in (
            ("r", Float().ranged(min=0)),
            ("rm", Float().ranged(min=0)),
            ("dx", Float()),
            ("dy", Float()),
            ("dz", Float()),
            ("x", Pos("x")),
            ("y", Pos("y")),
            ("z", Pos("z")),
            ("scores", Series(
              begin=Char("{")
                .note("note._selector.complex.scores.begin"),
              end=Char("}")
                .note("note._selector.complex.scores.end"),
              separator=Char(",")
                .note("note._selector.complex.scores.separator"),
              content=self._ScoresArg(),
              empty_ok=False
            )),
            ("tag", Invertable(self._RawTag())),
            ("name", Invertable(String())),
            ("type", Invertable(IdEntity())),
            ("family", Invertable(IdFamily())),
            ("rx", self._XRotation()),
            ("rxm", self._XRotation()),
            ("ry", self._YRotation()),
            ("rym", self._YRotation()),
            ("hasitem", self._HasItem()),
            ("l", Integer().ranged(min=0)),
            ("lm", Integer().ranged(min=0)),
            ("m", GameMode(allow_5=False)),
            ("c", Integer().none_of(0)),
            ("haspermission", Series(
              begin=Char("{")
                .note("note._selector.complex.haspermission.begin"),
              end=Char("}")
                .note("note._selector.complex.haspermission.end"),
              separator=Char(",")
                .note("note._selector.complex.haspermission.separator"),
              content=self._HasPermissionArg(),
              empty_ok=False
            ), {"version": VersionGe((1, 19, 80))}),
        ):
            _handle(*args)  # type: ignore

class Selector(CompressedNode):
    def __init__(self, note: Optional[str] = None):
        if note is None:
            self.__note_name = "note._selector.player_name"
            self.__note_filter = "note._selector.complex.root"
        else:
            self.__note_name = self.__note_filter = note
        super().__init__()

    def _tree(self):
        (self
          .branch(
            String()
              .font(Font.target)
              .note(self.__note_name)
              .branch(self.end)
          )
          .branch(
            Char("@")
              .font(Font.target)
              .note(self.__note_filter)
              .branch(
                NotedEnumerate("a", "e", "r", "p", "s", "initiator",
                               note_template="note._selector.complex.vars.%s")
                  .font(Font.target)
                  .branch(
                    Series(
                      begin=Char("[")
                        .note("note._selector.complex.begin"),
                      end=Char("]")
                        .note("note._selector.complex.end"),
                      separator=Char(",")
                        .note("note._selector.complex.separator"),
                      content=SelectorArg(),
                      empty_ok=False
                    )
                      .branch(self.end)
                  )
                  .branch(self.end),
                is_close=True
              )
          )
        )

class Wildcard(CompressedNode):
    def __init__(self, node: Node, wildcard_note: str = "note._wildcard"):
        self.node = node
        self.wildcard_note = wildcard_note
        super().__init__()

    def _tree(self):
        (self
          .branch(
            self.node
              .branch(self.end)
          )
          .branch(
            Char("*")
              .note(self.wildcard_note)
              .font(Font.meta)
              .branch(self.end)
          )
        )

class Swizzle(Node):
    default_font = Font.keyword

    def _parse(self, reader: Reader):
        word = reader.read_word()
        wordset = set(word)
        if not (word
                and wordset.issubset({"x", "y", "z"})
                and len(wordset) == len(word)):
            raise ExpectationFailure("swizzle")
        return wordset

    def _suggest(self):
        return [
            Suggestion(
                name="autocomp.swizzle", writes=word, note=None,
                name_kwds={"swizzle": word},
                match_rule=str_find_rule(word)
            )
            for word in ("x", "y", "z", "xy", "yz", "xz", "xyz")
        ]

class ScoreSpec(CompressedNode):
    def __init__(self, wildcard_ok=True):
        self.__wildcard = wildcard_ok
        super().__init__()

    def _tree(self):
        sel = Selector()
        if self.__wildcard:
            sel = Wildcard(sel, wildcard_note="note._wildcard_score_holder")
        (self
          .branch(
            sel
              .branch(
                String()
                  .font(Font.scoreboard)
                  .note("note._scoreboard")
                  .branch(self.end)
              )
          )
        )

class RegexNode(SubparsingNode):
    """Use Regular Expression to generate font marks (i.e. highlight)
    the argument.
    """
    RE_DEFS = ()

    def _re_parse(self, marker: "Marker"):
        raise NotImplementedError("should be implemented by subclass")

    def _parse(self, marker: "Marker"):
        # Parsing
        reader = marker.reader
        pos_begin = reader.get_location()
        self._re_parse(marker)
        pos_end = reader.get_location()
        string = reader.get_slice(pos_begin, pos_end)
        # Marking
        for regex, font in self.RE_DEFS:  # type: ignore
            for m in re.finditer(regex, string):
                start, end = m.span()
                marker.font_marks.append(FontMark(
                    pos_begin.offset(start), pos_begin.offset(end), font
                ))

class _RawtextTranslate(RegexNode):
    default_font = Font.string
    RE_DEFS = (
        (re.compile(r"%%[s1-9]"), Font.meta),
    )

    def _re_parse(self, marker: "Marker"):
        with marker.add_ac_mark(node=self):  # type: ignore
            marker.reader.read_until_eol()

class JsonStrSemanticError(SemanticError):
    def __init__(self, suberr: BaseError):
        super().__init__("error.semantic.json_str")
        self.__suberr = suberr

    def resolve(self, translator: "Translator"):
        self.kwds["suberr"] = self.__suberr.resolve(translator)
        return super().resolve(translator)

class _JsonString(SubparsingNode):
    argument_end = False

    ESCAPES = {
        "t": "\t", "n": "\n",
        "b": "\b", "f": "\f", "r": "\r",
        '"': '"', "\\": "\\"
    }
    HEX = frozenset("0123456789abcdefABCDEF")

    def __init__(self, definition: dict = {},
                       path: List[str] = [],
                       name: Union[str, None] = None,
                       ac_node: Optional[Node] = None):
        super().__init__()
        self.__difinition = definition
        self.__path = path
        self.__name = name
        self.__tree = None
        self.__done_tree = False
        if ac_node is None:
            self.__ac_node = self
        else:
            self.__ac_node = ac_node

    def __get_tree(self) -> Union[None, Node]:
        """Get the tree that parses the content in the string."""
        if self.__done_tree:
            return self.__tree
        if self.__name is None:
            # When this string is a JSON key in a JSON object
            o = dict_getter(self.__difinition, self.__path)
            if o:
                keys = set()
                for k in o:
                    if k.startswith("!"):
                        i = k.rfind("@")
                        if i == -1:
                            continue
                        k = k[1:i]
                        keys.add(k)
                if keys:
                    self.__tree = NotedEnumerate(*keys,
                        note_template="note._json.{}._keys.%s"
                                      .format(".".join(self.__path)))
                else:
                    self.__tree = None
        else:
            # When this string is a JSON value
            lib = dict_getter(self.__difinition,
                self.__path, ["%s@string" % self.__name, "#lib"])
            if lib is None:
                self.__tree = None
            elif lib == "wildcard_selector":
                self.__tree = Wildcard(Selector())
            elif lib == "lock_mode":
                self.__tree = NotedEnumerate(
                    "lock_in_inventory", "lock_in_slot",
                    note_template="note._json._libs.lock.%s"
                )
            elif lib == "block":
                self.__tree = IdBlock()
            elif lib == "scoreboard":
                self.__tree = BareText(empty_ok=False).font(Font.scoreboard)
            elif lib == "translate":
                self.__tree = _RawtextTranslate()
            else:
                raise ValueError("Invalid lib %r" % lib)
        return self.__tree

    def _parse(self, marker: Marker):
        reader = marker.reader
        # Parsing
        pos_begin = reader.get_location()
        if reader.next() != '"':
            raise ExpectationFailure("quoted_str")
        chars = []
        col_map = []
        i = 0
        while True:
            char = reader.next()
            if char == '"' or reader.is_line_end(char):
                col_map.append(i)
                break
            if char == "\\":
                char2 = reader.next()
                esc = self.ESCAPES.get(char2)  # type: ignore
                if esc:
                    chars.append(esc)
                    col_map.append(i)
                    col_map.append(i)
                    i += 1
                    continue
                if char2 == "u":
                    hex_ = []
                    for _ in range(4):
                        c = reader.next()
                        if c not in self.HEX:
                            raise ArgParseFailure(
                                "error.syntax.json_str_u_escape")
                        hex_.append(c)
                    for _ in range(6):
                        col_map.append(i)
                    chars.append(chr(int("".join(hex_), base=16)))
                    i += 1
                    continue
                chars.append("\\")
                col_map.append(i)
                if char2 is not None:
                    chars.append(char2)
                    col_map.append(i + 1)
                    i += 1
                i += 1
                continue
            chars.append(char)
            col_map.append(i)
            i += 1
        if char != '"':
            raise ArgParseFailure("error.syntax.unclosed_str")
        pos_end = reader.get_location()
        string = "".join(chars)
        # Marking
        p1, p2 = pos_begin.offset(1), pos_end.offset(-1)
        marker.font_marks.append(FontMark(pos_begin, p1, Font.meta))
        marker.font_marks.append(FontMark(p2, pos_end, Font.meta))
        marker.ac_marks.append(AutoCompletingMark.from_node(
            p2, pos_end, self.__ac_node, version=marker.version
        ))  # Leave body part of string for sub-node
        tree = self.__get_tree()
        if tree is not None:
            def _conv_loc(loc: "CharLocation"):
                return p1.offset(col_map.index(loc.column - 1))
            def _get_loc(m):
                return (_conv_loc(m.begin), _conv_loc(m.end))
            submarker = Marker(Reader(string), version=marker.version)
            tree2 = Empty().branch(tree.finish(EOL))
            tree2.freeze()
            try:
                tree2.parse(submarker)
                submarker.trigger_checkers()
            except BaseError as err:
                # Fix error location and re-raise the error in the
                # checker.
                if isinstance(err, SyntaxError_):
                    err_range = (_conv_loc(err.location), p2)
                elif isinstance(err, SemanticError):
                    err_range = (
                        _conv_loc(err.range[0]), _conv_loc(err.range[1])
                    )
                else:
                    raise TypeError("Unexpected error type %r" % type(err))
                err_save = err
                def _raise(res):
                    raise JsonStrSemanticError(err_save)
                checker_mark = CheckerMark(*err_range, [_raise])
                checker_mark.set_result(None)
                marker.checker_marks.append(checker_mark)
            else:
                for mark in submarker.font_marks:
                    marker.font_marks.append(
                        FontMark(*_get_loc(mark), mark.font)
                    )
                for mark in submarker.ac_marks:
                    marker.ac_marks.append(
                        AutoCompletingMark(*_get_loc(mark), mark.get_unit)
                    )
        else:  # No information for parsing the string
            marker.font_marks.append(FontMark(p1, p2, Font.string))
        return string

    def _suggest(self):
        tree = self.__get_tree()
        if tree is None:
            return []
        res = tree._suggest()
        def _ref(s: "HandledSuggestion"):
            s.name = json.dumps(s.name)
            s.writes = json.dumps(s.writes)
            s.match_rule = str_find_rule(s.writes)
        for s in res:
            s.set_refactor(_ref)
        return res

class _JsonKeyValPair(CompressedNode):
    def __init__(self, definition: dict, path: List[str]):
        self.__definition = definition
        self.__path = path
        super().__init__()

    def _tree(self):
        __key = None
        def _set_key(v: str):
            nonlocal __key
            __key = v
        def _get_key():
            assert __key is not None
            return "!" + __key
        (self
          .branch(
            ResultTracked(
              _JsonString(self.__definition, self.__path), _set_key
            )
              .branch(
                Char(":")
                  .branch(
                    Json(self.__definition, _get_key, self.__path)
                      .branch(self.end)
                  )
              )
          )
        )

class Json(SubparsingNode):
    WHITESPACES = frozenset(" \t\r\n")

    def __init__(self, definition: dict = {},
                       name: Union[str, Callable[[], str]] = "",
                       path: List[str] = []):
        super().__init__()
        self.__difinition = definition
        self.__path = path
        if isinstance(name, str):
            self.__get_name = lambda: name
        else:
            self.__get_name = name

    def __skip_spaces(self):
        while self.reader.peek() in self.WHITESPACES:
            self.reader.next()

    def __parse_node(self, node: Node):
        # Since we do `_end_subparse(node)` directly, node should be
        # a single node and should not be a embedded tree.
        _end_subparse(node)
        return _node_subparse(self, node, self.marker)

    def __float(self):
        # Exponent is deprecated in Minecraft
        # and `0` prefix is allowed
        self.__parse_node(Float())

    def __string(self):
        self.__parse_node(_JsonString(
            self.__difinition, self.__path, self.__name, ac_node=self
        ))

    def __object(self):
        p = self.__path.copy()
        p.append("%s@object" % self.__name)
        o = dict_getter(self.__difinition, p, ["#redirect"])
        if not (o is None or isinstance(o, list)):
            raise ValueError("#redirect should be an array of string")
        path = o if o is not None else p
        tree = Series(
          begin=Char("{"),
          end=Char("}"),
          separator=Char(","),
          content=_JsonKeyValPair(self.__difinition, path),
          empty_ok=True
        )
        self.__parse_node(tree)

    def __array(self):
        p = self.__path.copy()
        p.append("%s@array" % self.__name)
        o = dict_getter(self.__difinition, p, ["#redirect"])
        if not (o is None or isinstance(o, list)):
            raise ValueError("#redirect should be an array of string")
        path = o if o is not None else p
        tree = Series(
          begin=Char("["),
          end=Char("]"),
          separator=Char(","),
          content=Json(self.__difinition, "#value", path),
          empty_ok=True
        )
        self.__parse_node(tree)

    def __boolean(self):
        self.__parse_node(Boolean())

    def _parse(self, marker: "Marker"):
        self.marker = marker
        self.reader = marker.reader
        self.__name = self.__get_name()
        self.__skip_spaces()
        char = self.reader.peek()
        if char in DIGITS or char == "-":
            self.__float()
        elif char == '"':
            self.__string()
        elif char == "{":
            self.__object()
        elif char == "[":
            self.__array()
        elif char == "t" or char == "f":
            self.__boolean()
        else:
            raise ExpectationFailure("json")

    def _suggest(self):
        o = dict_getter(self.__difinition, self.__path)
        types = []
        if o:
            for k in o:
                i = k.rfind("@")
                if i == -1:
                    continue
                if k[:i] == self.__name:
                    types.append(k[i+1:])
        res = [
            Suggestion(
                name="autocomp.char", name_kwds={"char": "{"},
                writes="{", match_rule=char_rule("{"),
                note="note._json._suggested" if "object" in types else None),
            Suggestion(
                name="autocomp.char", name_kwds={"char": "["},
                writes="[", match_rule=char_rule("["),
                note="note._json._suggested" if "array" in types else None),
            Suggestion(
                name="autocomp.true", writes="true",
                match_rule=str_find_rule("true", RULEW_OTHER),
                note="note._json._suggested" if "boolean" in types else None),
            Suggestion(
                name="autocomp.false", writes="false",
                match_rule=str_find_rule("false", RULEW_OTHER),
                note="note._json._suggested" if "boolean" in types else None),
            Suggestion(
                name="autocomp.quoted_string", writes='"',
                match_rule=char_rule('"'),
                note="note._json._suggested" if "string" in types else None),
            # `null` is deprecated in Minecraft
            Suggestion(
                name="autocomp.float", writes="0.0",
                match_rule=char_check_rule(
                    lambda char: char in DIGITS or char == "-"
                                 or char == "."
                                 # JSON does not allow + prefix
                ),
                note="note._json._suggested" if "number" in types else None)
        ]
        res.sort(key=lambda s: s.note is None)
        return res

def ItemComponents():
    return Json(
        {
            "$item_components@object": {
                "!minecraft:can_place_on@object": {
                    "!blocks@array": {
                        "#value@string": {
                            "#lib": "block"
                        }
                    }
                },
                "!minecraft:can_destroy@object": {
                    "!blocks@array": {
                        "#value@string": {
                            "#lib": "block"
                        }
                    }
                },
                "!minecraft:item_lock@object": {
                    "!mode@string": {
                        "#lib": "lock_mode"
                    }
                },
                "!minecraft:keep_on_death@object": {}
            }
        },
        name="$item_components"
    )

def RawText():
    return Json(
    {
        "$rawtext@object": {
            "!rawtext@array": {
                "#value@object": {
                    "!text@string": {},
                    "!translate@string": {
                        "#lib": "translate"
                    },
                    "!with@array": {
                        "#value@string": {}
                    },
                    "!with@object": {
                        "#redirect": ["$rawtext@object"]
                    },
                    "!score@object": {
                        "!objective@string": {
                            "#lib": "scoreboard"
                        },
                        "!name@string": {
                            "#lib": "wildcard_selector"
                        }
                    },
                    "!selector@string": {
                        "#lib": "wildcard_selector"
                    }
                }
            }
        }
    },
        name="$rawtext"
    )

class Molang(RegexNode):
    RE_DEFS = (
        (re_word(r"return|this|loop|for_each|break|continue",
                 flags=re.IGNORECASE),
         Font.molang_keyword),
        (re.compile(
            r"\b(q(uery)?|v(ariable)?|math|t(emp)?|c(ontext)?"
            r")(?=\s*\.)",
            flags=re.IGNORECASE),
         Font.molang_class),
        (re.compile(r'^"|"$'), Font.meta),  # Quoted string
        (re.compile(r"'[^']*'"), Font.string),
        (re_word(r"->|==|>=|<=|>|<|!=|=|!|&&|\|\||\+|-|\*|/|;|\?\?|\?|:|\."),
         Font.meta),  # Operators
        (re.compile(r'(?<=^")!'), Font.meta),  # Unary special case
        (re_word(r"\d+(\.(\d+)?)?"), Font.numeric),
    )

    def _re_parse(self, marker: "Marker"):
        tree = String()
        tree._qstr_part.close_branches.append(tree.end)
        tree._word_part.close_branches.append(tree.end)
        tree.note(self.note_)
        submarker = Marker(marker.reader, version=marker.version)
        _end_subparse(tree)
        _node_subparse(self, tree, submarker)
        submarker.font_marks.clear()  # Override font marks
        submarker.merge_to(marker)

    def _suggest(self):
        return Word._suggest() + QuotedString._suggest()

class CircleOrArea(CompressedNode):
    def _tree(self):
        (self
          .branch(
            Keyword("circle")
              .note("note._circle.root")
              .branch(
                Pos3D()
                  .branch(
                    Integer()
                      .note("note._circle.radius")
                      .ranged(min=0)
                      .branch(self.end)
                  )
              )
          )
          .branch(
            Pos3D()
              .branch(
                Pos3D()
                  .branch(self.end)
              )
          )
        )

class FacingOrYXRot(CompressedNode):
    def __init__(self, xrot_optional: Optional[Node] = None,
                 facing_kwds: Dict[str, Any] = {}):
        self.__xrot_branch = xrot_optional
        self.__facing_kwds = facing_kwds
        super().__init__()

    def _tree(self):
        yrot = Rotation("y")
        (self
          .branch(
            Keyword("facing")
              .note("note._facing")
              .branch(
                Pos3D()
                  .branch(self.end)
              )
              .branch(
                Selector()
                  .branch(self.end)
              ),
            **self.__facing_kwds
          )
          .branch(
            yrot
              .branch(
                Rotation("x")
                  .branch(self.end)
              )
          )
        )
        if self.__xrot_branch is not None:
            yrot.branch(self.__xrot_branch)

class EOL(Finish):
    # End Of Line
    def _parse(self, reader: Reader):
        if reader.is_line_end(reader.peek()):
            reader.next()
        else:
            raise ArgParseFailure("error.syntax.too_many_args")

    @staticmethod
    def _rule(s: str):
        if not s:
            return RULEW_OTHER
        else:
            return RULEW_FAILED

    def _suggest(self):
        return [Suggestion(
            name="autocomp.eol", writes="\n",
            match_rule=self._rule
        )]

def CommandName(name: str, *alias: str):
    if not alias:
        n = Keyword(name)
    else:
        n = Enumerate(name, *alias)
    return (n
      .font(Font.command)
      .note("note.%s.root" % name)
    )

def Command():
    command_root = Empty()

    # Common
    _spawnevt_nametag = (
      Wildcard(IdEntityEvent(), wildcard_note="note._wildcard_entity_event")
        .branch(
          String()
            .note("note._name_tag")
            .finish(EOL)
        )
        .finish(EOL)
    )
    _optional_selector_end = (Empty()
      .branch(
        Selector()
          .finish(EOL)
      )
      .finish(EOL)
    )

    _camera_color = (Keyword("color")
      .note("note.camera.fade.color.root")
      .branch(
        Float()
          .note("note.camera.fade.color.r")
          .ranged(min=0, max=1)
          .branch(
            Float()
              .note("note.camera.fade.color.g")
              .ranged(min=0, max=1)
              .branch(
                Float()
                  .note("note.camera.fade.color.b")
                  .ranged(min=0, max=1)
                  .finish(EOL)
              )
          ),
        version=VersionLt((1, 20, 10))
      )
      .branch(
        Integer()
          .note("note.camera.fade.color.r")
          .ranged(min=0, max=255)
          .branch(
            Integer()
              .note("note.camera.fade.color.g")
              .ranged(min=0, max=255)
              .branch(
                Integer()
                  .note("note.camera.fade.color.b")
                  .ranged(min=0, max=255)
                  .finish(EOL)
              )
          ),
        version=VersionGe((1, 20, 10))
      )
    )
    _camera_rot = (Empty()
      .branch(
        Keyword("rot")
          .note("note.camera.set.rot")
          .branch(
            YawPitch()
              .finish(EOL)
          )
      )
      .branch(
        Keyword("facing")
          .note("note._facing")
          .branch(
            Selector()
              .finish(EOL)
          )
          .branch(
            Pos3D()
              .finish(EOL)
          ),
        version=VersionGe((1, 20, 10))
      )
    )
    _camera_set_end = (Empty()
      .branch(
        Keyword("default")
          .note("note.camera.set.default")
          .finish(EOL)
      )
      .branch(
        Keyword("pos")
          .note("note.camera.set.pos")
          .branch(
            Pos3D()
              .branch(_camera_rot)
              .finish(EOL)
          )
      )
      .branch(_camera_rot)
      .finish(EOL)
    )

    def _difficulty() -> Dict[str, str]:
        res: Dict[str, str] = {}
        for diff in ("peaceful", "easy", "normal", "hard"):
            res[diff] = "note.difficulty.diffs." + diff
        res["p"] = res["peaceful"]
        res["e"] = res["easy"]
        res["n"] = res["normal"]
        res["h"] = res["hard"]
        return res

    _enchant = (Empty()
      .branch(
        Integer()
          .note("note.enchant.level")
          .ranged(min=1)
          .finish(EOL)
      )
      .finish(EOL)
    )

    def _ExecuteSubcmd(word: str):
        return Keyword(word).note("note.execute.subcmds." + word)
    _execute = Empty()
    _execute_cond = (Empty()
      .branch(
        Keyword("block")
          .note("note.execute.tests.block")
          .branch(
            Pos3D()
              .branch(
                BlockSpec(bs_optional=_execute)
                  .branch(_execute)
                  .finish(EOL)
              )
          )
      )
      .branch(
        Keyword("blocks")
          .note("note.execute.tests.blocks")
          .branch(
            Pos3D().branch(Pos3D().branch(Pos3D()
              .branch(
                NotedEnumerate("all", "masked",
                    note_template="note._blocks_scan_mode.%s")
                  .branch(_execute)
                  .finish(EOL)
              )
            ))
          )
      )
      .branch(
        Keyword("entity")
          .note("note.execute.tests.entity")
          .branch(
            Selector()
              .branch(_execute)
              .finish(EOL)
          )
      )
      .branch(
        Keyword("score")
          .note("note.execute.tests.score.root")
          .branch(
            ScoreSpec(wildcard_ok=False)
              .branch(
                Keyword("matches")
                  .note("note.execute.tests.score.matches")
                  .branch(
                    IntRange()
                      .branch(_execute)
                      .finish(EOL)
                  )
              )
              .branch(
                CharsEnumerate("=", "<=", ">=", "<", ">",
                    note_template="note.execute.tests.score.compare_ops.%s")
                  .branch(
                    ScoreSpec(wildcard_ok=False)
                      .branch(_execute)
                      .finish(EOL)
                  )
              )
          )
      )
    )
    (_execute
      .branch(
        _ExecuteSubcmd("align")
          .branch(
            Swizzle()
              .branch(_execute)
          )
      )
      .branch(
        _ExecuteSubcmd("anchored")
          .branch(
            NotedEnumerate("eyes", "feet",
                           note_template="note.execute.anchors.%s")
              .branch(_execute)
          )
      )
      .branch(
        _ExecuteSubcmd("as")
          .branch(
            Selector()
              .branch(_execute)
          )
      )
      .branch(
        _ExecuteSubcmd("at")
          .branch(
            Selector()
              .branch(_execute)
          )
      )
      .branch(
        _ExecuteSubcmd("facing")
          .branch(
            Pos3D()
              .branch(_execute)
          )
          .branch(
            Keyword("entity")
              .note("note.execute.entity_variant")
              .branch(
                Selector()
                  .branch(
                    NotedEnumerate("eyes", "feet",
                                   note_template="note.execute.anchors.%s")
                      .branch(_execute)
                  )
              )
          )
      )
      .branch(
        _ExecuteSubcmd("in")
          .branch(
            NotedEnumerate("overworld", "nether", "the_end",
                           note_template="note.execute.dims.%s")
              .branch(_execute)
          )
      )
      .branch(
        _ExecuteSubcmd("positioned")
          .branch(
            Pos3D()
              .branch(_execute)
          )
          .branch(
            Keyword("as")
              .note("note.execute.entity_variant")
              .branch(
                Selector()
                  .branch(_execute)
              )
          )
      )
      .branch(
        _ExecuteSubcmd("rotated")
          .branch(
            YawPitch()
              .branch(_execute)
          )
          .branch(
            Keyword("as")
              .note("note.execute.entity_variant")
              .branch(
                Selector()
                  .branch(_execute)
              )
          )
      )
      .branch(
        _ExecuteSubcmd("if")
          .branch(_execute_cond)
      )
      .branch(
        _ExecuteSubcmd("unless")
          .branch(_execute_cond)
      )
      .branch(
        _ExecuteSubcmd("run")
          .branch(command_root)
      )
    )

    _gametest_runset_end = (Empty()
      .branch(
        String()
          .note("note.gametest.runset.tag")
          .branch(
            Integer()
              .note("note.gametest.rotation")
              .ranged(min=0, max=3)
              .finish(EOL)
          )
          .finish(EOL)
      )
      .branch(
        EOL()
          .note("note.gametest.runset.default")
      )
    )

    _loot_tool = (Empty()
      .branch(
        NotedEnumerate("mainhand", "offhand",
                       note_template="note.loot.origin.tools.%s")
          .finish(EOL)
      )
      .branch(
        IdItem()
          .finish(EOL)
      )
    )
    _loot_origin = (Empty()
      .branch(
        Keyword("kill")
          .note("note.loot.origin.kill")
          .branch(
            Selector()
              .branch(_loot_tool)
              .finish(EOL)
          )
      )
      .branch(
        Keyword("loot")
          .note("note.loot.origin.loot")
          .branch(
            IdLootTable()
              .branch(_loot_tool)
              .finish(EOL)
          )
      )
    )

    _replaceitem_end = (IdItem()
      .branch(
        Integer()
          .note("note.replaceitem.amount")
          .ranged(min=1, max=64)
          .branch(
            ItemData(is_test=False)
              .branch(
                ItemComponents()
                  .finish(EOL)
              )
              .finish(EOL)
          )
          .finish(EOL)
      )
      .finish(EOL)
    )
    _replaceitem = (Empty()
      .branch(
        NotedEnumerate("destroy", "keep",
                       note_template="note.replaceitem.modes.%s")
          .branch(_replaceitem_end)
      )
      .branch(_replaceitem_end)
    )

    _structure_load_end = (Boolean()
      .note("note.structure.include_entity")
      .branch(
        Boolean()
          .note("note.structure.include_block")
          .branch(
            Boolean()
              .note("note.structure.load.water_logged")
              .branch(
                Float()
                  .note("note.structure.load.integrity")
                  .ranged(min=0, max=100)
                  .branch(
                    String()
                      .note("note.structure.load.seed")
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
              .finish(EOL)
          )
          .finish(EOL)
      )
      .finish(EOL)
    )

    _tp_pos_end = (Boolean()
      .note("note.teleport.check_for_blocks")
      .finish(EOL)
    )
    _tp_pos = (Pos3D()
      .branch(
        FacingOrYXRot(xrot_optional=EOL())
          .branch(_tp_pos_end)
          .finish(EOL)
      )
      .branch(_tp_pos_end)
      .finish(EOL)
    )

    _tickingarea_preload_end = (Empty()
      .branch(
        Boolean()
          .note("note.tickingarea.set_preload")
          .finish(EOL)
      )
      .branch(
        EOL()
          .note("note.tickingarea.preload.query")
      )
    )

    def _title_command(name: str, text_node: Node):
        return (CommandName(name)
          .branch(
            Selector()
              .branch(
                NotedEnumerate("title", "subtitle", "actionbar",
                    note_template="note.title.%s")
                  .branch(
                    text_node
                      .finish(EOL)
                  )
              )
              .branch(
                Keyword("clear")
                  .note("note.title.clear")
                  .finish(EOL)
              )
              .branch(
                Keyword("times")
                  .note("note.title.times.root")
                  .branch(
                    Integer()
                      .note("note.title.times.fade_in")
                      .ranged(min=0)
                      .branch(
                        Integer()
                          .note("note.title.times.hold")
                          .ranged(min=0)
                          .branch(
                            Integer()
                              .note("note.title.times.fade_out")
                              .ranged(min=0)
                              .finish(EOL)
                          )
                      )
                  )
              )
              .branch(
                Keyword("reset")
                  .note("note.title.reset")
                  .finish(EOL)
              )
          )
        )

    return (command_root
      .branch(
        CommandName("help", "?")
          .branch(
            Integer()
              .note("note.help.on.page")
              .finish(EOL)
          )
          .branch(
            Word()
              .note("note.help.on.command")
              .finish(EOL)
          )
          .branch(
            EOL()
              .note("note.help.on.page_1")
          )
      )
      .branch(
        CommandName("ability")
          .branch(
            Selector()
              .branch(
                IdAbility()
                  .branch(
                    Boolean()
                      .note("note.ability.set")
                      .finish(EOL)
                  )
                  .branch(
                    EOL()
                      .note("note.ability.query.ability")
                  )
              )
              .branch(
                EOL()
                  .note("note.ability.query.unknown")
              )
          )
      )
      .branch(
        CommandName("alwaysday", "daylock")
          .branch(
            Boolean()
              .note("note.alwaysday.set")
              .finish(EOL)
          )
          .branch(
            EOL()
              .note("note.alwaysday.lock")
          )
      )
      .branch(
        CommandName("camera")
          .branch(
            Selector()
              .branch(
                Keyword("clear")
                  .note("note.camera.clear")
                  .finish(EOL)
              )
              .branch(
                Keyword("fade")
                  .note("note.camera.fade.root")
                  .branch(_camera_color)
                  .branch(
                    Keyword("time")
                      .note("note.camera.fade.time.root")
                      .branch(
                        Float()
                          .note("note.camera.fade.time.in")
                          .ranged(min=0)
                          .branch(
                            Float()
                              .note("note.camera.fade.time.hold")
                              .ranged(min=0)
                              .branch(
                                Float()
                                  .ranged(min=0)
                                  .note("note.camera.fade.time.out")
                                  .branch(_camera_color)
                                  .finish(EOL)
                              )
                          )
                      ),
                    version=VersionLt((1, 20, 10))
                  )
                  .branch(
                    Keyword("time")
                      .note("note.camera.fade.time.root")
                      .branch(
                        Float()
                          .note("note.camera.fade.time.in")
                          .ranged(min=0, max=10)
                          .branch(
                            Float()
                              .note("note.camera.fade.time.hold")
                              .ranged(min=0, max=10)
                              .branch(
                                Float()
                                  .note("note.camera.fade.time.out")
                                  .ranged(min=0, max=10)
                                  .branch(_camera_color)
                                  .finish(EOL)
                              )
                          )
                      ),
                    version=VersionGe((1, 20, 10))
                  )
                  .finish(EOL)
              )
              .branch(
                Keyword("set")
                  .note("note.camera.set.root")
                  .branch(
                    IdCameraPreset()
                      .branch(
                        Keyword("ease")
                          .note("note.camera.set.ease.root")
                          .branch(
                            Float()
                              .note("note.camera.set.ease.time")
                              .ranged(min=0)
                              .branch(
                                IdEaseType()
                                  .branch(_camera_set_end)
                              )
                          )
                      )
                      .branch(_camera_set_end)
                  )
              )
          ),
        version=VersionGe((1, 20, 0))
      )
      .branch(
        CommandName("camerashake")
          .branch(
            Keyword("add")
              .note("note.camerashake.add.root")
              .branch(
                Selector()
                  .branch(
                    Float()
                      .note("note.camerashake.add.intensity")
                      .ranged(min=0, max=4)
                      .branch(
                        Float()
                          .note("note.camerashake.add.seconds")
                          .ranged(min=0)
                          .branch(
                            NotedEnumerate("positional", "rotational",
                                note_template="note.camerashake.add.types.%s")
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("stop")
              .note("note.camerashake.stop")
              .branch(
                Selector()
                  .finish(EOL)
              )
              .finish(EOL)
          )
      )
      .branch(
        CommandName("clear")
          .branch(
            Selector()
              .branch(
                IdItem()
                  .branch(
                    ItemData(is_test=True)
                      .branch(
                        Integer()
                          .note("note.clear.max_count")
                          .ranged(min=-1)
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
              .finish(EOL)
          )
          .finish(EOL)
      )
      .branch(
        CommandName("clearspawnpoint")
          .branch(_optional_selector_end)
      )
      .branch(
        CommandName("clone")
          .branch(
            Pos3D().branch(Pos3D().branch(Pos3D()
              .branch(
                NotedEnumerate("masked", "replace",
                               note_template="note.clone.masks.%s")
                  .branch(
                    NotedEnumerate("force", "move", "normal",
                                   note_template="note.clone.clones.%s")
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
              .branch(
                Keyword("filtered")
                  .note("note.clone.filtered")
                  .branch(
                    NotedEnumerate("force", "move", "normal",
                                   note_template="note.clone.clones.%s")
                      .branch(
                        BlockSpec()
                          .finish(EOL)
                      )
                  )
              )
              .finish(EOL)
            ))
          )
      )
      .branch(
        CommandName("wsserver", "connect")
          .branch(
            Keyword("out")
              .note("note.wsserver.out")
              .finish(EOL)
          )
          .branch(
            BareText(empty_ok=False)
              .note("note.wsserver.address")
              .finish(EOL)
          )
      )
      .branch(
        CommandName("damage")
          .branch(
            Selector()
              .branch(
                Integer()
                  .note("note.damage.amount")
                  .branch(
                    IdDamageType()
                      .branch(
                        Keyword("entity")
                          .note("note.damage.damager")
                          .branch(
                            Selector()
                              .finish(EOL)
                          )
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("deop")
          .branch(
            Selector()
              .finish(EOL)
          )
      )
      .branch(
        CommandName("dialogue")
          .branch(
            Keyword("open")
              .note("note.dialogue.modes.open")
              .branch(
                Selector("note.dialogue.npc")
                  .branch(
                    Selector("note.dialogue.player")
                      .branch(
                        String()
                          .note("note.dialogue.scene")
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
              )
          )
          .branch(
            Keyword("change")
              .note("note.dialogue.modes.change")
              .branch(
                Selector("note.dialogue.npc")
                  .branch(
                    String()
                      .note("note.dialogue.scene")
                      .branch(
                        Selector("note.dialogue.player")
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
              )
          )
      )
      .branch(
        CommandName("difficulty")
          .branch(
            Integer()
              .one_of(0, 1, 2, 3)
              .font(Font.keyword)
              .note("note.difficulty.int")
              .finish(EOL)
          )
          .branch(
            Enumerate("peaceful", "easy", "normal", "hard",
                      "p", "e", "n", "h",
                      note_table=_difficulty())
              .finish(EOL)
          )
      )
      .branch(
        CommandName("effect")
          .branch(
            Selector()
              .branch(
                Keyword("clear")
                  .note("note.effect.clear")
                  .finish(EOL)
              )
              .branch(
                IdEffect()
                  .branch(
                    Integer()
                      .note("note.effect.seconds")
                      .ranged(min=0)
                      .branch(
                        Integer()
                          .note("note.effect.amplifier")
                          .ranged(min=0, max=255)
                          .branch(
                            Boolean()
                              .note("note.effect.hide_particles")
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("enchant")
          .branch(
            Selector()
              .branch(
                Integer()
                  .note("note.enchant.int_id")
                  .branch(_enchant)
              )
              .branch(
                IdEnchantment()
                  .branch(_enchant)
              )
          )
      )
      .branch(
        CommandName("event")
          .branch(
            Keyword("entity")
              .branch(
                Selector()
                  .branch(
                    IdEntityEvent()
                      .finish(EOL)
                  )
              )
          )
      )
      .branch(
        CommandName("execute")
          .branch(
            _execute,
            version=VersionGe((1, 19, 50))
          )
          .branch(
            Selector()
              .branch(
                Pos3D()
                  .branch(
                    command_root
                  )
                  .branch(
                    Keyword("detect")
                      .note("note.execute.old.detect")
                      .branch(
                        Pos3D()
                          .branch(
                            IdBlock()
                              .branch(
                                Integer()
                                  .note("note._block_data")
                                  .branch(
                                    command_root
                                  )
                              )
                          )
                      )
                  )
              ),
            version=VersionLt((1, 19, 50))
          )
      )
      .branch(
        CommandName("fill")
          .branch(
            Pos3D()
              .branch(
                Pos3D()
                  .branch(
                    BlockSpec(bs_optional=EOL())
                      .branch(
                        Keyword("replace")
                          .note("note.fill.modes.replace.root")
                          .branch(
                            BlockSpec(bs_optional=EOL())
                              .finish(EOL)
                          )
                          .branch(
                            EOL()
                              .note("note.fill.modes.replace.all")
                          )
                      )
                      .branch(
                        NotedEnumerate("destroy", "hollow", "keep", "outline",
                                       note_template="note.fill.modes.%s")
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
              )
          )
      )
      .branch(
        CommandName("fog")
          .branch(
            Selector()
              .branch(
                Keyword("push")
                  .note("note.fog.modes.push")
                  .branch(
                    IdFog()
                      .branch(
                        String()
                          .note("note.fog.user_provided_name")
                          .finish(EOL)
                      )
                  )
              )
              .branch(
                NotedEnumerate("pop", "remove",
                               note_template="note.fog.modes.%s")
                  .branch(
                    String()
                      .note("note.fog.user_provided_name")
                      .finish(EOL)
                  )
              )
          )
      )
      .branch(
        CommandName("function")
          .branch(
            BareText(empty_ok=False)
              .note("note.function.path")
              .finish(EOL)
          )
      )
      .branch(
        CommandName("gamemode")
          .branch(
            GameMode(allow_5=True, allow_legacy_6=True)
              .branch(_optional_selector_end)
          )
      )
      .branch(
        CommandName("gamerule")
          .branch(
            GameRule()
              .branch(
                Integer()
                  .note("note.gamerule.value")
                  .finish(EOL)
              )
              .branch(
                Boolean()
                  .note("note.gamerule.value")
                  .finish(EOL)
              )
              .branch(
                EOL()
                  .note("note.gamerule.query")
              )
          )
      )
      .branch(
        CommandName("gametest")
          .branch(
            Keyword("runthis")
              .note("note.gametest.runthis")
              .finish(EOL)
          )
          .branch(
            Keyword("run")
              .note("note.gametest.run")
              .branch(
                String()
                  .note("note.gametest.test_name")
                  .branch(
                    Boolean()
                      .note("note.gametest.stop_on_failure")
                      .branch(
                        Integer()
                          .note("note.gametest.repeat")
                          .ranged(min=1)
                          .branch(
                            Integer()
                              .note("note.gametest.rotation")
                              .ranged(min=0, max=3)
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                  )
                  .branch(
                    Integer()
                      .note("note.gametest.rotation")
                      .ranged(min=0, max=3)
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("runthese")
              .note("note.gametest.runthis")
              .finish(EOL)
          )
          .branch(
            Keyword("runset")
              .note("note.gametest.runset.root_regular")
              .branch(_gametest_runset_end)
          )
          .branch(
            Keyword("runsetuntilfail")
              .note("note.gametest.runset.root_untilfail")
              .branch(_gametest_runset_end),
            version=VersionGe((1, 19, 80))
          )
          .branch(
            Keyword("clearall")
              .note("note.gametest.clearall")
              .finish(EOL)
          )
          .branch(
            Keyword("stopall")
              .note("note.gametest.stopall")
              .finish(EOL),
            version=VersionGe((1, 19, 80))
          )
          .branch(
            Keyword("create")
              .note("note.gametest.create.root")
              .branch(
                String()
                  .note("note.gametest.test_name")
                  .branch(
                    Integer()
                      .note("note.gametest.create.len_x")
                      .ranged(min=1, max=48)
                      .branch(
                        Integer()
                          .note("note.gametest.create.len_y")
                          .ranged(min=1, max=48)
                          .branch(
                            Integer()
                              .note("note.gametest.create.len_z")
                              .ranged(min=1, max=48)
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("pos")
              .note("note.gametest.pos")
              .finish(EOL)
          )
      )
      .branch(
        CommandName("give")
          .branch(
            Selector()
              .branch(
                IdItem()
                  .branch(
                    Integer()
                      .ranged(min=1, max=32767)
                      .note("note.give.amount")
                      .branch(
                        ItemData(is_test=False)
                          .branch(
                            ItemComponents()
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("immutableworld")
          .branch(
            Boolean()
              .note("note.immutableworld.set")
              .finish(EOL)
          )
          .branch(
            EOL()
              .note("note.immutableworld.query")
          )
      )
      .branch(
        CommandName("inputpermission")
          .branch(
            Keyword("query")
              .note("note.inputpermission.query.root")
              .branch(
                Selector()
                  .branch(
                    IdPermission()
                      .branch(
                        PermissionState(
                          note="note.inputpermission.query.equal"
                        )
                          .finish(EOL)
                      )
                      .branch(
                        EOL()
                          .note("note.inputpermission.query.normal")
                      )
                  )
              )
          )
          .branch(
            Keyword("set")
              .note("note.inputpermission.set")
              .branch(
                Selector()
                  .branch(
                    IdPermission()
                      .branch(
                        PermissionState()
                          .finish(EOL)
                      )
                  )
              )
          ),
        version=VersionGe((1, 19, 80))
      )
      .branch(
        CommandName("kick")
          .branch(
            Selector("note.kick.target")
              .branch(
                BareText(empty_ok=True)
                  .note("note.kick.reason")
                  .finish(EOL)
              )
              .finish(EOL)  # For autocompletion
          )
      )
      .branch(
        CommandName("kill")
          .branch(_optional_selector_end)
      )
      .branch(
        CommandName("list")
          .finish(EOL)
      )
      .branch(
        CommandName("locate")
          .branch(
            Keyword("biome")
              .note("note.locate.biome")
              .branch(
                IdBiome()
                  .finish(EOL)
              ),
            version=VersionGe((1, 19, 10))
          )
          .branch(
            Keyword("structure")
              .note("note.locate.structure.root")
              .branch(
                IdStructure()
                  .branch(
                    Boolean()
                      .note("note.locate.structure.new_chunks")
                      .finish(EOL)
                  )
                  .finish(EOL)
              ),
            version=VersionGe((1, 19, 10))
          )
          .branch(
            IdStructure()
              .branch(
                Boolean()
                  .note("note.locate.structure.new_chunks")
                  .finish(EOL)
              )
              .finish(EOL),
            version=VersionLt((1, 19, 30))
          )
      )
      .branch(
        CommandName("loot")
          .branch(
            Keyword("give")
              .note("note.loot.give")
              .branch(
                Selector()
                  .branch(_loot_origin)
              )
          )
          .branch(
            Keyword("insert")
              .note("note.loot.insert")
              .branch(
                Pos3D()
                  .branch(_loot_origin)
              )
          )
          .branch(
            Keyword("spawn")
              .note("note.loot.spawn")
              .branch(
                Pos3D()
                  .branch(_loot_origin)
              )
          )
          .branch(
            Keyword("replace")
              .note("note.loot.replace.root")
              .branch(
                Keyword("entity")
                  .note("note.loot.replace.entity")
                  .branch(
                    Selector()
                      .branch(
                        EntitySlot()
                          .branch(
                            Integer()
                              .note("note.loot.replace.slot_count")
                              .branch(_loot_origin)
                          )
                          .branch(_loot_origin)
                      )
                  )
              )
              .branch(
                Keyword("block")
                  .note("note.loot.replace.block")
                  .branch(
                    Pos3D()
                      .branch(
                        BlockSlot()
                          .branch(
                            Integer()
                              .note("note.loot.replace.slot_count")
                              .branch(_loot_origin)
                          )
                          .branch(_loot_origin)
                      )
                  ),
                version=VersionGe((1, 19, 40))
              ),
            version=VersionGe((1, 19, 0))
          )
      )
      .branch(
        CommandName("me")
          .branch(
            BareText(empty_ok=True)
              .finish(EOL)
          )
      )
      .branch(
        CommandName("mobevent")
          .branch(
            Keyword("events_enabled")
              .note("note.mobevent.events_enabled")
              .branch(
                Boolean()
                  .note("note.mobevent.value")
                  .finish(EOL)
              )
              .branch(
                EOL()
                  .note("note.mobevent.query")
              )
          )
          .branch(
            IdMobEvent()
              .branch(
                Boolean()
                  .note("note.mobevent.value")
                  .finish(EOL)
              )
              .branch(
                EOL()
                  .note("note.mobevent.query")
              )
          )
      )
      .branch(
        CommandName("tell", "msg", "w")
          .branch(
            Selector()
              .branch(
                BareText(empty_ok=True)
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("music")
          .branch(
            NotedEnumerate("play", "queue",
                           note_template="note.music.modes.%s")
              .branch(
                IdMusic()
                  .branch(
                    Float()
                      .note("note.music.volume")
                      .ranged(min=0, max=1)
                      .branch(
                        Float()
                          .note("note.music.fade_in")
                          .ranged(min=0, max=10)
                          .branch(
                            NotedEnumerate("play_once", "loop",
                                note_template="note.music.loop_modes.%s")
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("stop")
              .note("note.music.modes.stop")
              .branch(
                Float()
                  .note("note.music.fade_out")
                  .ranged(min=0, max=10)
                  .finish(EOL)
              )
              .finish(EOL)
          )
          .branch(
            Keyword("volume")
              .note("note.music.modes.volume")
              .branch(
                Float()
                  .note("note.music.volume")
                  .ranged(min=0, max=1)
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("op")
          .branch(
            Selector()
              .finish(EOL)
          )
      )
      .branch(
        CommandName("particle")
          .branch(
            IdParticle()
              .branch(
                Pos3D()
                  .finish(EOL)
              )
              .finish(EOL)
          )
      )
      .branch(
        CommandName("playanimation")
          .branch(
            Selector()
              .branch(
                IdAnimationRef()
                  .branch(
                    IdRPACState()
                      .branch(
                        Float()
                          .note("note.playanimation.blend")
                          .ranged(min=0)
                          .branch(
                            Molang()
                              .note("note.playanimation.stop_exp")
                              .branch(
                                IdRPAC()
                                  .finish(EOL)
                              )
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("playsound")
          .branch(
            IdSound()
              .branch(
                Selector()
                  .branch(
                    Pos3D()
                      .branch(
                        Float()
                          .note("note.playsound.volume")
                          .ranged(min=0)
                          .branch(
                            Float()
                              .note("note.playsound.pitch")
                              .ranged(min=0, max=256)
                              .branch(
                                Float()
                                  .note("note.playsound.min_volume")
                                  .ranged(min=0, max=1)
                                  .finish(EOL)
                              )
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
              .finish(EOL)
          )
      )
      .branch(
        CommandName("recipe")
          .branch(
            Selector()
              .branch(
                Keyword("give")
                  .note("note.recipe.give")
                  .branch(
                    Wildcard(IdRecipe(), wildcard_note="note.recipe.wildcard")
                      .finish(EOL)
                  )
              )
              .branch(
                Keyword("take")
                  .note("note.recipe.take")
                  .branch(
                    Wildcard(IdRecipe(), wildcard_note="note.recipe.wildcard")
                      .finish(EOL)
                  )
              ),
            version=VersionLt((1, 20, 20))
          )
          .branch(
            Keyword("give")
              .note("note.recipe.give")
              .branch(
                Selector()
                  .branch(
                    Wildcard(IdRecipe(), wildcard_note="note.recipe.wildcard")
                      .finish(EOL)
                  )
              ),
            version=VersionGe((1, 20, 20))
          )
          .branch(
            Keyword("take")
              .note("note.recipe.take")
              .branch(
                Selector()
                  .branch(
                    Wildcard(IdRecipe(), wildcard_note="note.recipe.wildcard")
                      .finish(EOL)
                  )
              ),
            version=VersionGe((1, 20, 20))
          ),
        version=VersionGe((1, 20, 10))
      )
      .branch(
        CommandName("reload")
          .finish(EOL)
      )
      .branch(
        CommandName("replaceitem")
          .branch(
            Keyword("entity")
              .note("note.replaceitem.entity")
              .branch(
                Selector()
                  .branch(
                    EntitySlot()
                      .branch(_replaceitem)
                  )
              )
          )
          .branch(
            Keyword("block")
              .note("note.replaceitem.block")
              .branch(
                Pos3D()
                  .branch(
                    BlockSlot()
                      .branch(_replaceitem)
                  )
              )
          )
      )
      .branch(
        CommandName("ride")
          .branch(
            Selector()
              .branch(
                Keyword("start_riding")
                  .note("note.ride.mount")
                  .branch(
                    Selector()
                      .branch(
                        NotedEnumerate("teleport_rider", "teleport_ride",
                                       note_template="note.ride.tp_modes.%s")
                          .branch(
                            NotedEnumerate("if_group_fits", "until_full",
                                note_template="note.ride.fill_modes.%s")
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
              )
              .branch(
                Keyword("stop_riding")
                  .note("note.ride.dismount")
                  .finish(EOL)
              )
              .branch(
                Keyword("evict_riders")
                  .note("note.ride.dismount_rider")
                  .finish(EOL)
              )
              .branch(
                Keyword("summon_rider")
                  .note("note.ride.summon_rider")
                  .branch(
                    IdEntity()
                      .branch(_spawnevt_nametag)
                      .finish(EOL)
                  )
              )
              .branch(
                Keyword("summon_ride")
                  .note("note.ride.summon_ride")
                  .branch(
                    IdEntity()
                      .branch(
                        NotedEnumerate(
                            "skip_riders", "no_ride_change", "reassign_rides",
                            note_template="note.ride.ride_modes.%s"
                        )
                          .branch(_spawnevt_nametag)
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
              )
          )
      )
      .branch(
        CommandName("say")
          .branch(
            BareText(empty_ok=True)
              .finish(EOL)
          )
      )
      .branch(
        CommandName("schedule")
          .branch(
            Keyword("on_area_loaded")
              .note("note.schedule.area.root")
              .branch(
                Keyword("add")
                  .branch(
                    CircleOrArea()
                      .branch(
                        BareText(empty_ok=False)
                          .note("note.schedule.function")
                          .finish(EOL)
                      )
                  )
                  .branch(
                    Keyword("tickingarea")
                      .note("note.schedule.area.tickingarea")
                      .branch(
                        String()
                          .note("note._tickingarea")
                          .branch(
                            BareText(empty_ok=False)
                              .note("note.schedule.function")
                              .finish(EOL)
                          )
                      )
                  )
              )
          )
      )
      .branch(
        CommandName("scoreboard")
          .branch(
            Keyword("players")
              .note("note.scoreboard.players.root")
              .branch(
                Keyword("set")
                  .note("note.scoreboard.players.set")
                  .branch(
                    ScoreSpec()
                      .branch(
                        Integer()
                          .finish(EOL)
                      )
                  )
              )
              .branch(
                Keyword("add")
                  .note("note.scoreboard.players.add")
                  .branch(
                    ScoreSpec()
                      .branch(
                        Integer()
                          .finish(EOL)
                      )
                  )
              )
              .branch(
                Keyword("remove")
                  .note("note.scoreboard.players.remove")
                  .branch(
                    ScoreSpec()
                      .branch(
                        Integer()
                          .finish(EOL)
                      )
                  )
              )
              .branch(
                Keyword("random")
                  .note("note.scoreboard.players.random.root")
                  .branch(
                    ScoreSpec()
                      .branch(
                        Integer()
                          .note("note.scoreboard.players.random.min")
                          .branch(
                            Integer()
                              .note("note.scoreboard.players.random.max")
                              .finish(EOL)
                          )
                      )
                  )
              )
              .branch(
                Keyword("reset")
                  .note("note.scoreboard.players.reset.root")
                  .branch(
                    Wildcard(Selector())
                      .branch(
                        String()
                          .font(Font.scoreboard)
                          .note("note._scoreboard")
                          .finish(EOL)
                      )
                      .branch(
                        EOL()
                          .note("note.scoreboard.players.reset.all")
                      )
                  )
              )
              .branch(
                Keyword("test")
                  .note("note.scoreboard.players.test.root")
                  .branch(
                    ScoreSpec()
                      .branch(
                        Wildcard(
                          Integer()
                            .note("note.scoreboard.players.test.min"),
                          wildcard_note=
                            "note.scoreboard.players.test.wildcard.min"
                        )
                          .branch(
                            Wildcard(
                              Integer()
                                .note("note.scoreboard.players.test.max"),
                              wildcard_note=
                                "note.scoreboard.players.test.wildcard.max"
                            )
                              .finish(EOL)
                          )
                          .branch(
                            EOL()
                              .note("note.scoreboard.players.test.no_max")
                          )
                      )
                  )
              )
              .branch(
                Keyword("operation")
                  .note("note.scoreboard.players.operation.root")
                  .branch(
                    ScoreSpec()
                      .branch(
                        CharsEnumerate("=", "+=", "-=", "*=", "/=",
                                       "%=", "><", "<", ">",
                           note_template="note.scoreboard.players."
                                         "operation.operators.%s")
                          .branch(
                            ScoreSpec()
                              .finish(EOL)
                          )
                      )
                  )
              )
              .branch(
                Keyword("list")
                  .note("note.scoreboard.players.list.root")
                  .branch(
                    Wildcard(Selector())
                      .branch(
                        EOL()
                          .note("note.scoreboard.players.list.scores")
                      )
                  )
                  .branch(
                    EOL()
                      .note("note.scoreboard.players.list.tracking")
                  )
              )
          )
          .branch(
            Keyword("objectives")
              .note("note.scoreboard.objectives.root")
              .branch(
                Keyword("add")
                  .note("note.scoreboard.objectives.add.root")
                  .branch(
                    String()
                      .font(Font.scoreboard)
                      .note("note._scoreboard")
                      .branch(
                        Keyword("dummy")
                          .branch(
                            String()
                              .note("note.scoreboard.objectives.add.display")
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                  )
              )
              .branch(
                Keyword("remove")
                  .note("note.scoreboard.objectives.remove")
                  .branch(
                    String()
                      .font(Font.scoreboard)
                      .note("note._scoreboard")
                      .finish(EOL)
                  )
              )
              .branch(
                Keyword("setdisplay")
                  .note("note.scoreboard.objectives.setdisplay.root")
                  .branch(
                    NotedEnumerate("sidebar", "list",
                        note_template="note.scoreboard.objectives."
                                      "setdisplay.slots.%s")
                      .branch(
                        String()
                          .font(Font.scoreboard)
                          .note("note._scoreboard")
                          .branch(
                            NotedEnumerate("ascending", "descending",
                                note_template="note.scoreboard.objectives."
                                              "setdisplay.sort.%s")
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .branch(
                        EOL()
                          .note("note.scoreboard.objectives.setdisplay.clear")
                      )
                  )
                  .branch(
                    Keyword("belowname")
                      .note("note.scoreboard.objectives."
                            "setdisplay.slots.belowname")
                      .branch(
                        String()
                          .font(Font.scoreboard)
                          .note("note._scoreboard")
                          .finish(EOL)
                      )
                      .branch(
                        EOL()
                          .note("note.scoreboard.objectives.setdisplay.clear")
                      )
                  )
              )
              .branch(
                Keyword("list")
                  .note("note.scoreboard.objectives.list")
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("script")
          .branch(
            Keyword("debugger")
              .note("note.script.debugger.root")
              .branch(
                Keyword("close")
                  .note("note.script.debugger.close")
                  .finish(EOL)
              )
              .branch(
                Keyword("connect")
                  .note("note.script.debugger.connect")
                  .branch(
                    String()
                      .note("note.script.debugger.host")
                      .branch(
                        Integer()
                          .ranged(min=0, max=65535)
                          .note("note.script.debugger.port")
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
              .branch(
                Keyword("listen")
                  .note("note.script.debugger.listen")
                  .branch(
                    Integer()
                      .ranged(min=0, max=65535)
                      .note("note.script.debugger.port")
                      .finish(EOL)
                  )
              )
          )
          .branch(
            Keyword("profiler")
              .note("note.script.profiler.root")
              .branch(
                Keyword("start")
                  .note("note.script.profiler.start")
                  .finish(EOL)
              )
              .branch(
                Keyword("stop")
                  .note("note.script.profiler.stop")
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("watchdog")
              .note("note.script.watchdog.root")
              .branch(
                Keyword("exportstats")
                  .note("note.script.watchdog.exportstats")
                  .finish(EOL)
              ),
            version=VersionGe((1, 19, 30))
          )
      )
      .branch(
        CommandName("scriptevent")
          .branch(
            String()
              .note("note.scriptevent.id")
              .branch(
                BareText(empty_ok=True)
                  .note("note.scriptevent.message")
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("setblock")
          .branch(
            Pos3D()
              .branch(
                BlockSpec(bs_optional=EOL())
                  .branch(
                    NotedEnumerate("destroy", "keep", "replace",
                                   note_template="note.setblock.modes.%s")
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("setmaxplayers")
          .branch(
            Integer()
              .note("note.setmaxplayers.value")
              .ranged(min=1)
              .finish(EOL)
          )
      )
      .branch(
        CommandName("setworldspawn")
          .branch(
            Pos3D()
              .finish(EOL)
          )
          .branch(
            EOL()
              .note("note.setworldspawn.here")
          )
      )
      .branch(
        CommandName("spawnpoint")
          .branch(
            Selector()
              .branch(
                Pos3D()
                  .finish(EOL)
              )
              .branch(
                EOL()
                  .note("note.spawnpoint.here")
              )
          )
          .finish(EOL)
      )
      .branch(
        CommandName("spreadplayers")
          .branch(
            Pos("x")
              .branch(
                Pos("z")
                  .branch(
                    Float()
                      .note("note.spreadplayers.distance")
                      .ranged(min=0)
                      .branch(
                        Float()
                          .note("note.spreadplayers.max_range")
                          .ranged(min=1)
                          .branch(
                            Selector()
                              .finish(EOL)
                          )
                      )
                  )
              )
          )
      )
      .branch(
        CommandName("stopsound")
          .branch(
            Selector()
              .branch(
                IdSound()
                  .finish(EOL)
              )
              .finish(EOL)
          )
      )
      .branch(
        CommandName("structure")
          .branch(
            Keyword("save")
              .note("note.structure.save.root")
              .branch(
                String()
                  .note("note.structure.name")
                  .branch(
                    Pos3D()
                      .branch(
                        Pos3D()
                          .branch(
                            Boolean()
                              .note("note.structure.include_entity")
                              .branch(
                                NotedEnumerate("disk", "memory",
                                    note_template="note.structure.save."
                                                  "modes.%s")
                                  .branch(
                                    Boolean()
                                      .note("note.structure.include_block")
                                      .finish(EOL)
                                  )
                                  .finish(EOL)
                              )
                              .finish(EOL)
                          )
                          .branch(
                            NotedEnumerate("disk", "memory",
                                note_template="note.structure.save.modes.%s")
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                  )
              )
          )
          .branch(
            Keyword("load")
              .note("note.structure.load.root")
              .branch(
                String()
                  .note("note.structure.name")
                  .branch(
                    Pos3D()
                      .branch(
                        NotedEnumerate("0_degrees", "90_degrees",
                                       "180_degrees", "270_degrees",
                            note_template="note.structure.load.rotations.%s")
                          .branch(
                            NotedEnumerate("x", "z", "xz", "none",
                                note_template="note.structure.load.flip.%s")
                              .branch(_structure_load_end)
                              .branch(
                                NotedEnumerate("block_by_block",
                                               "layer_by_layer",
                                    note_template="note.structure.load."
                                                  "anims.%s")
                                  .branch(
                                    Float()
                                      .note("note.structure.load.anim_sec")
                                      .ranged(min=0)
                                      .branch(_structure_load_end)
                                      .finish(EOL)
                                  )
                                  .finish(EOL)
                              )
                              .finish(EOL)
                          )
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
              )
          )
          .branch(
            Keyword("delete")
              .note("note.structure.delete")
              .branch(
                String()
                  .note("note.structure.name")
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("summon")
          .branch(
            IdEntity()
              .branch(
                Pos3D()
                  .branch(
                    FacingOrYXRot(
                        xrot_optional=EOL(),
                        facing_kwds={"version": VersionGe((1, 19, 80))}
                    )
                      .branch(_spawnevt_nametag)
                      .finish(EOL),
                    version=VersionGe((1, 19, 70))
                  )
                  .branch(_spawnevt_nametag, version=VersionLt((1, 19, 70)))
                  .finish(EOL)
              )
              .branch(
                String()
                  .note("note._name_tag")
                  .branch(
                    Pos3D()
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
              .finish(EOL)
          )
      )
      .branch(
        CommandName("tag")
          .branch(
            Wildcard(Selector(), wildcard_note="note.tag.wildcard_target")
              .branch(
                Keyword("add")
                  .note("note.tag.add")
                  .branch(
                    String()
                      .note("note.tag.tag")
                      .font(Font.tag)
                      .finish(EOL)
                  )
              )
              .branch(
                Keyword("remove")
                  .note("note.tag.remove")
                  .branch(
                    String()
                      .note("note.tag.tag")
                      .font(Font.tag)
                      .finish(EOL)
                  )
              )
              .branch(
                Keyword("list")
                  .note("note.tag.list")
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("teleport", "tp")
          .branch(
            Selector()
              .branch(_tp_pos)
              .branch(
                Selector()
                  .branch(
                    Boolean()
                      .note("note.teleport.check_for_blocks")
                      .branch(
                        EOL()
                          .note("note.teleport.to_entity")
                      )
                  )
                  .branch(
                    EOL()
                      .note("note.teleport.to_entity")
                  )
              )
              .branch(
                EOL()
                  .note("note.teleport.self2entity")
              )
          )
          .branch(_tp_pos)
      )
      .branch(
        CommandName("tellraw")
          .branch(
            Selector()
              .branch(
                RawText()
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("testfor")
          .branch(
            Selector()
              .finish(EOL)
          )
      )
      .branch(
        CommandName("testforblock")
          .branch(
            Pos3D()
              .branch(
                BlockSpec(bs_optional=EOL())
                  .finish(EOL)
              )
          )
      )
      .branch(
        CommandName("testforblocks")
          .branch(
            Pos3D().branch(Pos3D().branch(Pos3D()
              .branch(
                NotedEnumerate("all", "masked",
                    note_template="note._blocks_scan_mode.%s")
                  .finish(EOL)
              )
              .finish(EOL)
            ))
          )
      )
      .branch(
        CommandName("tickingarea")
          .branch(
            Keyword("add")
              .note("note.tickingarea.add")
              .branch(
                CircleOrArea()
                  .branch(
                    String()
                      .note("note._tickingarea")
                      .branch(
                        Boolean()
                          .note("note.tickingarea.set_preload")
                          .finish(EOL)
                      )
                      .finish(EOL)
                  )
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("remove")
              .note("note.tickingarea.remove")
              .branch(
                Pos3D()
                  .finish(EOL)
              )
              .branch(
                String()
                  .note("note._tickingarea")
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("remove_all")
              .note("note.tickingarea.remove_all")
              .finish(EOL)
          )
          .branch(
            Keyword("list")
              .note("note.tickingarea.list.root")
              .branch(
                Keyword("all-dimensions")
                  .note("note.tickingarea.list.all_dims")
                  .finish(EOL)
              )
              .branch(
                EOL()
                  .note("note.tickingarea.list.cur_dim")
              )
          )
          .branch(
            Keyword("preload")
              .note("note.tickingarea.preload.root")
              .branch(
                Pos3D()
                  .branch(_tickingarea_preload_end)
              )
              .branch(
                String()
                  .note("note._tickingarea")
                  .branch(_tickingarea_preload_end)
              )
          )
      )
      .branch(
        CommandName("time")
          .branch(
            Keyword("add")
              .note("note.time.add")
              .branch(
                Integer()
                  .note("note.time.amount")
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("query")
              .note("note.time.query.root")
              .branch(
                NotedEnumerate("daytime", "gametime", "day",
                    note_template="note.time.query.types.%s")
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("set")
              .note("note.time.set.root")
              .branch(
                Integer()
                  .note("note.time.amount")
                  .finish(EOL)
              )
              .branch(
                NotedEnumerate("day", "night", "noon", "midnight",
                               "sunrise", "sunset",
                    note_template="note.time.set.alias.%s")
                  .finish(EOL)
              )
          )
      )
      .branch(_title_command("title", BareText(empty_ok=True)))
      .branch(_title_command("titleraw", RawText()))
      .branch(
        CommandName("toggledownfall")
          .finish(EOL)
      )
      .branch(
        CommandName("volumearea")
          .branch(
            Keyword("add")
              .note("note.volumearea.add.root")
              .branch(
                String()
                  .note("note.volumearea.add.id")
                  .branch(
                    Pos3D()
                      .branch(
                        Pos3D()
                          .branch(
                            String()
                              .note("note.volumearea.name")
                              .finish(EOL)
                          )
                      )
                  )
              )
          )
          .branch(
            Keyword("remove")
              .note("note.volumearea.remove")
              .branch(
                Pos3D()
                  .finish(EOL)
              )
              .branch(
                String()
                  .note("note.volumearea.name")
                  .finish(EOL)
              )
          )
          .branch(
            Keyword("remove_all")
              .note("note.volumearea.remove_all")
              .finish(EOL)
          )
          .branch(
            Keyword("list")
              .note("note.volumearea.list.root")
              .branch(
                Keyword("all-dimensions")
                  .note("note.volumearea.list.all_dims")
                  .finish(EOL)
              )
              .branch(
                EOL()
                  .note("note.volumearea.list.cur_dim")
              )
          )
      )
      .branch(
        CommandName("worldbuilder", "wb")
          .finish(EOL)
      )
      .branch(
        CommandName("weather")
          .branch(
            NotedEnumerate("clear", "rain", "thunder",
                note_template="note.weather.set.weathers.%s")
              .branch(
                Integer()
                  .note("note.weather.set.duration")
                  .ranged(min=0, max=1000000)
                  .finish(EOL)
              )
              .finish(EOL)
          )
          .branch(
            Keyword("query")
              .note("note.weather.query")
              .finish(EOL)
          )
      )
      .branch(
        CommandName("xp")
          .branch(
            Integer()
              .note("note.xp.amount")
              .branch(
                KeywordCaseInsensitive("l")
                  .note("note.xp.level")
                  .font(Font.meta)
                  .branch(_optional_selector_end),
                is_close=True
              )
              .branch(_optional_selector_end)
          )
      )
    )

def MCFuncLine():
    return (Empty()
      .branch(
        Command()
      )
      .branch(
        EOL()
          .note("note._empty_line")
      )
      .branch(
        Char("#")
          .font(Font.comment)
          .note("note._comment")
          .branch(
            BareText(empty_ok=True)
              .font(Font.comment)
              .finish(EOL)
          )
      )
    )
