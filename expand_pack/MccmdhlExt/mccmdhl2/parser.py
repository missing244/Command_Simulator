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

"""The core parser that resolves the nodes and use the nodes to parse
a source command.
"""

from typing import (
    TYPE_CHECKING, List, Tuple, Type, TypeVar, Any,
    Optional, Callable, Generic, Union
)
from enum import Enum
from abc import ABCMeta, abstractmethod

from .ctxutils import ExitStack
from .reader import Reader, ReaderError
if TYPE_CHECKING:
    from .reader import CharLocation
    from .autocompleter import Suggestion, IdSuggestion
    from .marker import Marker
    from .translator import Translator

__all__ = [
    "Font",
    "Node", "Finish", "Empty", "CompressedNode", "SubparsingNode",
    "BaseError", "SyntaxError_", "SemanticError",
    "ArgParseFailure", "ExpectationFailure"
]

class Font(Enum):
    numeric = 1  # Literal integer, float, boolean, etc.
    string = 2  # String and namespaced ID
    keyword = 3  # Options and keywords
    position = 4  # Positions in the world
    command = 5  # Name of command
    meta = 6  # Special characters
    scoreboard = 7  # Scoreboard objectives
    tag = 8  # Tag names
    target = 9  # Player name & selector variable
    comment = 10  # Comments
    rotation = 11  # Rotation
    molang_class = 12  # "qeury" in Molang "query."
    molang_keyword = 13  # "return" in Molang

# --- INTERNAL EXCEPTIONS ---

class ArgParseFailure(Exception):
    def __init__(self, message: str, **kwds):
        self.message = message
        self.kwds = kwds

class ExpectationFailure(ArgParseFailure):
    def __init__(self, needs: str, **kwds):
        super().__init__("error.syntax.expect." + needs, **kwds)

# --- USERSIDE EXCEPTIONS ---

class BaseError(Exception):
    def __init__(self, message: str, **kwds):
        self.message = message
        self.kwds = kwds

    def resolve(self, translator: "Translator"):
        return translator.get(self.message).format(**self.kwds)

class ExpectationError(BaseError):
    def __init__(self, message: str, **kwds):
        super().__init__(message, **kwds)
        self.messages = [message]
        self.kwdss = [kwds]

    def merge(self, other: "ExpectationError"):
        self.messages.append(other.message)
        self.kwdss.extend(other.kwdss)

    def resolve(self, translator: "Translator"):
        return translator.get("error.syntax.expect._root").format(
            content=translator.get("error.syntax.expect._separator").join(
                translator.get(msg).format(**kwds)
                for msg, kwds in zip(self.messages, self.kwdss)
            )
        )

class SyntaxError_(BaseError):
    """Syntax error raised by `Parser`."""
    def __init__(self, location: "CharLocation",
                 suberrs: List[ArgParseFailure]):
        super().__init__("error.syntax._root")
        self.location = location
        def _trans(err: ArgParseFailure) -> BaseError:
            if isinstance(err, ExpectationFailure):
                cls = ExpectationError
            else:
                cls = BaseError
            return cls(err.message, **err.kwds)
        pass1: List[BaseError] = list(map(_trans, suberrs))
        self.suberrs: List[BaseError] = []
        # Merge `ExpectationError`s
        exp_err = None
        for suberr in pass1:
            if isinstance(suberr, ExpectationError):
                if exp_err is None:
                    exp_err = suberr
                else:
                    exp_err.merge(suberr)
            else:
                self.suberrs.append(suberr)
        if exp_err is not None:
            self.suberrs.append(exp_err)

    def resolve(self, translator: "Translator") -> str:
        self.kwds["col"] = self.location.column
        self.kwds["ln"] = self.location.line
        self.kwds["suberrs"] = (
            translator.get("error.syntax._separator").join(
                err.resolve(translator) for err in self.suberrs
            )
        )
        return super().resolve(translator)

class SemanticError(BaseError):
    """Error raised by checkers (See `Node.checker`).
    These errors are bound to a `Mark`, so its location is the range
    of the `Mark`.
    """
    def set_range(self, begin: "CharLocation", end: "CharLocation"):
        self.range = (begin, end)

    def resolve(self, translator: "Translator") -> str:
        if not hasattr(self, "range"):
            raise ValueError("Range not set yet")
        return translator.get("error.semantic._root").format(
            ln1=self.range[0].line, col1=self.range[0].column,
            ln2=self.range[1].line, col2=self.range[1].column,
            message=super().resolve(translator)
        )

# --- VERSION ---
MCVersion = Tuple[int, ...]
class VersionFilter(metaclass=ABCMeta):
    @abstractmethod
    def validate(self, version: MCVersion) -> bool:
        pass

class _AllVersion(VersionFilter):
    def validate(self, version: MCVersion) -> bool:
        return True

class VersionAnd(VersionFilter):
    def __init__(self, *filters: VersionFilter):
        self.filters = filters

    def validate(self, version: MCVersion) -> bool:
        return all(f.validate(version) for f in self.filters)

# --- NODE ---

_PT = TypeVar("_PT")  # Parse result type

class Node(Generic[_PT]):
    argument_end: bool = True  # Whether argument terminator is required
    default_font: Union[None, Font] = None  # Default color font
    default_note: Union[None, str] = None  # Default auto-completion note
    do_ac_mark: bool = True  # Whether to leave `AutoCompletingMark`

    def __init__(self):
        self.branches: List[Node] = []
        # Each corresponding to a branch in `self.branches`:
        self.branch_versions: List[VersionFilter] = []
        # Branches that goes directly after `self` (no space between):
        self.close_branches = []
        # Branches that does not go directly after `self`
        # (terminator required):
        self.arg_end_branches = []
        self.checkers = []
        self.note_ = self.default_note  # Auto complete note
        self.font_ = self.default_font  # Font for colorizer
        self.frozen = False
        self.expanded_branch_info = []

    def branch(self, node: "Node",
               is_close: bool = False, require_arg_end: bool = False,
               version: VersionFilter = _AllVersion()):
        if self.frozen:
            raise ValueError("frozen node")
        self.branches.append(node)
        self.branch_versions.append(version)
        if is_close:
            # This branch must come with `self` directly,
            # without spaces between.
            assert not isinstance(self, Empty), \
                       "Unknown behavior for branch of Empty to use is_close"
            self.close_branches.append(node)
        if require_arg_end:
            # This branch must have a argument terminator before it.
            # This is an exception option for `self` whose
            # `argument_end` is False.
            assert not self.argument_end
            assert not isinstance(self, Empty), \
                       "Empty nodes are supposed to consume NO char"
            self.arg_end_branches.append(node)
        return self

    def finish(self, cls: Optional[Type["Finish"]] = None):
        if cls is None:
            cls = Finish
        return self.branch(cls())

    def note(self, note: Union[str, None]):
        if self.note_ is not None:
            raise ValueError("note set already")
        self.note_ = note
        return self

    def font(self, font: Font):
        self.font_ = font
        return self

    def checker(self, checker: Callable[[_PT], Any]):
        self.checkers.append(checker)
        return self

    def _parse(self, reader: Reader) -> _PT:
        raise NotImplementedError("should be implemented by subclass")

    def _suggest(self) -> List[Union["Suggestion", "IdSuggestion"]]:
        return []

    def _inner_freeze(self) -> List["Node"]:
        self.frozen = True
        try_freeze = []
        # `res`: node, version, is_close, is_arg_end
        res = self.expanded_branch_info
        def _handle_empty(bbranch_: Node,
                version_: VersionFilter, vfilter_: VersionFilter):
            res.append((bbranch_, VersionAnd(version_, vfilter_),
                        is_close, is_arg_end))
        for branch, vfilter in zip(self.branches, self.branch_versions):
            is_close = branch in self.close_branches
            is_arg_end = branch in self.arg_end_branches
            if isinstance(branch, Empty):
                if not branch.frozen:
                    s = branch._inner_freeze()
                    try_freeze.extend(s)
                for bbranch, version, _, _ in branch.expanded_branch_info:
                    _handle_empty(bbranch, version, vfilter)
            else:
                try_freeze.append(branch)
                res.append((branch, vfilter, is_close, is_arg_end))
        if not self.expanded_branch_info and not isinstance(self, Finish):
            raise ValueError("No branch for %r!" % self)
        return try_freeze

    def freeze(self):
        nodes = [self]
        tmp_nodes = []
        while nodes:
            for node in nodes:
                if not node.frozen:
                    tmp_nodes.extend(node._inner_freeze())
            nodes = tmp_nodes
            tmp_nodes = []

    def parse(self, marker: "Marker"):
        if not self.frozen:
            raise ValueError("`freeze` the node before parsing")
        reader = marker.reader
        node = self
        is_close, is_arg_end = False, False
        prev_node = None
        prev_state = reader.state_save()
        info_idx = 0
        info = []
        info_len = 0
        failures = []
        got_terminator_failure = False
        while True:
            is_terminator_failure = False
            try:
                # Content between `self` and child
                if prev_node:  # root node does not need this
                    if ((prev_node.argument_end and not is_close)
                        or is_arg_end):
                        try:
                            reader.argument_finish()
                        except ReaderError:
                            is_terminator_failure = True
                            raise ExpectationFailure("terminator")
                    if not is_close:
                        reader.skip_spaces()
                # Enter context here since we don't want spaces
                # between to be included.
                with ExitStack() as stack:
                    if node.do_ac_mark or (not prev_node):
                        # Do ac mark when option is True OR this node
                        # is the root. (There must be some mark
                        # marking the root for autocompleter.)
                        stack.enter_context(
                            marker.add_ac_mark(node=node))
                    if node.font_ is not None:
                        stack.enter_context(
                            marker.add_font_mark(font=node.font_))
                    if node.checkers:
                        callback = stack.enter_context(
                            marker.add_checker_mark(node.checkers))
                    else:
                        callback = None
                    # The child itself
                    if isinstance(node, SubparsingNode):
                        parse_res = node._parse(marker)
                    else:
                        parse_res = node._parse(reader)
            except ArgParseFailure as err:
                # We only keep 1 terminator expectation failure, since
                # every branch may raise it. Or you'll get "expecting a
                # terminator like space or a terminator like space or
                # ..." by writing "execute if score a b matches ..1a"
                if (not is_terminator_failure or not got_terminator_failure):
                    failures.append(err)
                if is_terminator_failure:
                    got_terminator_failure = True
                reader.state_jump(prev_state)
                info_idx += 1
                if info_idx >= info_len:
                    raise SyntaxError_(reader.get_location(), failures)
                else:
                    node, is_close, is_arg_end = info[info_idx]
            else:
                if callback:  # type: ignore
                    callback(parse_res)  # type: ignore
                if isinstance(node, Finish):
                    break
                info = node.get_info_v(marker.version)
                info_len = len(info)
                failures.clear()
                info_idx = 0
                prev_state = reader.state_save()
                prev_node = node
                node, is_close, is_arg_end = info[0]
                got_terminator_failure = False

    def suggest(self) -> List[Union["IdSuggestion", "Suggestion"]]:
        res = self._suggest()
        for s in res:
            if s.note is None:
                s.note = self.note_
        return res

    def get_info_v(self, version: MCVersion) \
            -> List[Tuple["Node", bool, bool]]:
        if not self.frozen:
            raise ValueError("`freeze` node before getting info")
        res = []
        for br, vfilter, is_close, is_arg_end in self.expanded_branch_info:
            if vfilter.validate(version):
                res.append((br, is_close, is_arg_end))
        if not res:
            raise ValueError("node %r has no branch in version %s"
                             % (self, version))
        return res

class Finish(Node):
    argument_end = False
    do_ac_mark = False

    def _parse(self, reader: Reader):
        pass

class Empty(Node):
    argument_end = False
    do_ac_mark = False

    def _parse(self, reader: Reader):
        pass

    def note(self, note: Union[str, None]):
        for branch in self.branches:
            branch.note(note)
        return self

class CompressedNode(Empty):
    def __init__(self):
        super().__init__()
        self.end = Empty()
        old_branch = self.branch
        def new_branch(*args, **kwds):
            return super(CompressedNode, self).branch(*args, **kwds)
        self.branch = new_branch
        self._tree()
        self.branch = old_branch

    def branch(self, node: Node, *args, **kwds):
        self.end.branch(node, *args, **kwds)
        return self

    def font(self, font: "Font"):
        # NOTE Use this carefully!
        # We only colorize the direct branches here!
        for branch in self.branches:
            branch.font(font)
        return self

    def _tree(self):
        raise NotImplementedError("should be implemented by subclass")

class SubparsingNode(Node):
    do_ac_mark = False
    default_font = None

    def _parse(self, marker: "Marker"):
        raise NotImplementedError("should be implemented by subclass")
