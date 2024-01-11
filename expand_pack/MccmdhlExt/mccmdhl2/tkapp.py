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

"""A high-level use of the parser -- a tkinter `Text` widget where
Minecraft commands can be input and highlighted, which has a pop-up
window showing error messages and auto-completing hints.
"""

from typing import (
    List, Tuple, Dict, Any, Optional, TYPE_CHECKING
)
import tkinter
from tkinter.font import Font as TkFont
# To track the insert and delete of a `Text` widget:
from idlelib.redirector import WidgetRedirector

from mccmdhl2 import MCCmdParser, Font, BaseError, SyntaxError_, SemanticError
if TYPE_CHECKING:
    from mccmdhl2.autocompleter import HandledSuggestion
    from mccmdhl2.parser import MCVersion
    from mccmdhl2.reader import CharLocation

__all__ = ["MCCmdText"]

def charloc_to_index(location: "CharLocation") -> str:
    return "%d.%d" % (location.line, location.column - 1)

class Popup:
    """The pop-up window used by `MCCmdText`."""
    KEYPRESS_EVENT = "<Key>"
    POPUP_HIDE_EVENT = "<FocusOut>"
    TEXT_TRY_HIDE_EVENT = "<FocusOut>"
    TEXT_HIDE_EVENT = "<Button-1>"
    LISTBOX_CONFIRM_EVENT = "<B1-Double-ButtonRelease>"

    POPUP_HIDE_KEYS = ("Escape",)

    LABEL_WRAPLENGTH = 400
    ERRMSG_MAX_LENGTH = 100  # Chars

    def __init__(self, text: "MCCmdText"):
        self.text = text
        self.FONT = self.text.cget("font")
        # Toplevel is the pop-up window:
        self.toplevel = None
        # Label shows error messages:
        self.label = None
        # Listbox that contains suggestions:
        self.listbox = None
        # and its scrollbar:
        self.scrollbar = None
        # Current suggestions:
        self.suggestions: List["HandledSuggestion"] = []
        # and its length (update with it)
        self.SUGG_LEN = 0

    def create(self):
        """Create the pop-up window, without positioning it to the
        correct place.
        """
        if self.toplevel is not None:
            return
        # Create widget
        self.toplevel = tkinter.Toplevel(self.text)
        self.toplevel.wm_overrideredirect(True)  # No border
        self.scrollbar = tkinter.Scrollbar(
            self.toplevel, orient=tkinter.VERTICAL)
        self.listbox = tkinter.Listbox(self.toplevel,
            yscrollcommand=self.scrollbar.set,
            exportselection=False,
            font=self.FONT)
        self.scrollbar.config(command=self.listbox.yview)
        self.label = tkinter.Label(self.toplevel,
            font=self.FONT,
            wraplength=self.LABEL_WRAPLENGTH)
        self.toplevel.lift()
        # Pack widgets
        self.label.pack(side="top")
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        # Bind events
        self.id_hidep = self.toplevel.bind(
            self.POPUP_HIDE_EVENT, self.on_hide)
        self.id_hidet = self.text.bind(
            self.TEXT_HIDE_EVENT, self.on_hide, "+")
        self.id_tryhide = self.text.bind(
            self.TEXT_TRY_HIDE_EVENT, self.on_try_hide)
        self.id_keyp = self.toplevel.bind(
            self.KEYPRESS_EVENT, self.on_toplevel_key)
        self.id_keyt = self.text.bind(
            self.KEYPRESS_EVENT, self.on_text_key)
        self.id_lb = self.listbox.bind(
            self.LISTBOX_CONFIRM_EVENT, self.on_listbox_confirm)

    def _get_listbox_selection(self) -> int:
        assert self.listbox
        sel = self.listbox.curselection()
        if not sel:
            return -1
        return int(sel[0])

    def update_position(self):
        """Position the window on the cursor."""
        if self.toplevel is None:
            return
        self.text.see("insert")
        bb = self.text.bbox(self.text.index("insert"))
        assert bb is not None
        x, y, dx, dy = bb
        pop_width = self.toplevel.winfo_width()
        pop_height = self.toplevel.winfo_height()
        text_width = self.text.winfo_width()
        text_height = self.text.winfo_height()
        new_x = (self.text.winfo_rootx()
                 + min(x, max(0, text_width - pop_width)))
        new_y = self.text.winfo_rooty() + y
        if (text_height - (y + dy) >= pop_height  # enough height below
            or y < pop_height):  # not enough height above
            # Place pop-up below current line
            new_y += dy
        else:
            # Place pop-up above current line
            new_y -= pop_height
        self.toplevel.wm_geometry("+%d+%d" % (new_x, new_y))

    def destroy(self):
        """Destroy pop-up window."""
        if self.toplevel is None:
            return
        assert self.scrollbar
        assert self.listbox
        assert self.label
        # Re-focus on `Text`
        self.text.focus_set()
        # Unbind events
        self.toplevel.unbind(self.POPUP_HIDE_EVENT, self.id_hidep)
        self.text.unbind(self.TEXT_TRY_HIDE_EVENT, self.id_tryhide)
        self.text.unbind(self.TEXT_HIDE_EVENT, self.id_hidet)
        self.text.unbind(self.KEYPRESS_EVENT, self.id_keyt)
        self.listbox.unbind(self.LISTBOX_CONFIRM_EVENT, self.id_lb)
        # Destroy
        self.scrollbar.destroy()
        self.listbox.destroy()
        self.label.destroy()
        self.toplevel.destroy()
        self.scrollbar = self.listbox = self.label = self.toplevel = None

    def update_content(self,
               suggestions: List["HandledSuggestion"],
               error: str = ""):
        """Show the pop-up & update content on it."""
        if not self.toplevel:
            self.create()
        assert self.toplevel
        assert self.listbox
        assert self.label
        self.suggestions = suggestions
        self.SUGG_LEN = len(self.suggestions)
        self.listbox.delete(0, "end")
        for suggestion in suggestions:
            self.listbox.insert("end", suggestion.resolve())
        if suggestions:
            # Select the first option by default
            self.listbox.select_set(0)
        # Trim error if it's too long
        if len(error) >= self.ERRMSG_MAX_LENGTH:
            error = error[:self.ERRMSG_MAX_LENGTH-3] + "..."
        self.label.config(text=error)
        # Update position
        # We update position after the listbox and label are updated
        # because positioning needs correct toplevel size, if we
        # update position first the window size will be the wrong one
        # (the old one when last time we update the content).
        # Also we call `self.toplevel.update_idletasks()` to update
        # window to make sure we get correct size info.
        # Using `self.toplevel.update()` also updates size info, but it
        # causes toplevel to handle some events too early and in very
        # few conditions make the Python call stack overflow.
        self.toplevel.update_idletasks()
        self.update_position()

    def complete(self) -> bool:
        """Use the user selected completion.
        Return True, if succeeded; False if not.
        """
        if not self.listbox:
            return False
        cursel = self._get_listbox_selection()
        if cursel == -1:
            return False
        suggestion = self.suggestions[cursel]
        l1, l2 = suggestion.get_overwrite_range()
        i1 = self.text._charloc_to_index(l1)
        i2 = self.text._charloc_to_index(l2)
        self.text.delete(i1, i2)
        self.text.insert(i1, suggestion.writes)
        return True

    def _focus_back(self):
        """Give back focus to `Text`, without hiding pop-up window."""
        self.text.focus_set()
        # Giving back focus to `Text` will trigger `<FocusOut>` for
        # the toplevel, so we unbind this event temporarily.
        if not self.toplevel:
            return
        self.toplevel.unbind(self.POPUP_HIDE_EVENT, self.id_hidep)
        self.toplevel.update()  # Trigger event immediately
        self.id_hidep = self.toplevel.bind(
            self.POPUP_HIDE_EVENT, self.on_hide)
        # After text gain focus, toplevel would go under it, so:
        self.toplevel.lift()

    def on_try_hide(self, event: tkinter.Event):
        """Tkinter callback: When text receive FocusOut."""
        if self.toplevel is None:
            return
        # We want to hide popup only if the whole application does not
        # have focus. Now we only know text does not, but not the other
        # parts of the application (e.g. popup), so we use `focus_get`
        # to check.
        self.text.update()  # make sure focus is updated
        if not self.text.focus_get():
            self.destroy()

    def on_hide(self, event: tkinter.Event):
        """Tkinter callback: When toplevel should be hidden."""
        self.destroy()

    def _common_keys(self, keysym: str):
        """Handle common key press (Whenever it's toplevel or text
        to receive this event).
        If failed to handle, raise `ValueError`
        """
        if keysym == "Tab" or keysym == "Return":
            succeeded = self.complete()
            return "break" if succeeded else None
        elif keysym in self.POPUP_HIDE_KEYS:
            self.destroy()
            return "break"
        else:
            raise ValueError

    def on_text_key(self, event: tkinter.Event):
        """Tkinter callback: When `Text` receive on key press."""
        if not self.listbox:
            return None
        keysym = event.keysym
        try:
            res = self._common_keys(keysym)
        except ValueError:
            res = "break"
            if keysym in ("Up", "Down", "Home", "End"):
                cur = self._get_listbox_selection()
                if keysym == "Up":
                    new = max(0, cur - 1)
                elif keysym == "Down":
                    new = min(self.SUGG_LEN - 1, cur + 1)
                elif keysym == "Home":
                    new = 0
                else:
                    assert keysym == "End"
                    new = self.SUGG_LEN - 1
                self.listbox.select_clear(cur)
                self.listbox.select_set(new)
                self.listbox.see(new)
            else:
                res = None
        # When returning None, `Text` will handle this key.
        return res

    def on_toplevel_key(self, event: tkinter.Event):
        """Tkinter callback: When `Toplevel` receive any key press."""
        if not self.toplevel:
            return
        keysym = event.keysym
        try:
            res = self._common_keys(keysym)
        except ValueError:
            # Try insert this character
            char = event.char
            if keysym == "BackSpace":
                self.text.delete("insert-1c")
                res = "break"
            elif len(char) != 1:
                res = None
            else:
                p = ord(char)
                if (10 <= p <= 13  # Line break
                    or 32 <= p <= 126  # ASCII printable
                    or 161 <= p <= 255):  # Extended ASCII
                    self.text.insert("insert", char)
                    res = "break"
                else:
                    res = None
            # We should give back focus when user types
            self._focus_back()
        return res

    def on_listbox_confirm(self, event: tkinter.Event):
        """Tkinter callback: On suggestion taken."""
        self.complete()
        self._focus_back()  # Give back focus

class MCCmdText(tkinter.Text):
    """A Tkinter `Text` widget where you can input Minecraft commands
    and get error messages, auto-completion and highlighting.
    """
    ERROR_TKTAG = "mccmdhl2E"
    FONT_TKTAG_PREFIX = "mccmdhl2F"

    def __init__(self, *args,
                 mc_version: "MCVersion" = (1, 19, 80),
                 parser_kwds: Dict[str, Any] = {},
                 suggest_kwds: Dict[str, Any] = {},
                 **kwds):
        super().__init__(*args, **kwds)
        self.BASE_FONT = TkFont(font=self.cget("font"))
        self.version = mc_version
        self.parser_kwds = parser_kwds
        self.suggest_kwds = suggest_kwds
        self.popup = Popup(self)
        # Overwrite insert and delete
        self.redirector = WidgetRedirector(self)
        self.original_ins = self.redirector.register(
            "insert", self.new_insert)
        self.original_del = self.redirector.register(
            "delete", self.new_delete)
        # Create color font
        # NOTE:
        #  1. If you wish to change `FONT2FORMAT`, please call `update_font`
        #  after changing it;
        #  2. If you wish to override "font" attribute of these format, please
        #  use a copy of `self.BASE_FONT` and then `config` it. `font_italic`
        #  below is a good example.
        ## Italic and bold font
        font_italic = self.BASE_FONT.copy()
        font_italic.config(slant="italic")
        ## Define font
        self.FONT2FORMAT = {
            Font.comment: {"foreground": "DeepSkyBlue"},
            Font.command: {"foreground": "Green"},
            Font.keyword: {"foreground": "DarkOrange"},
            Font.numeric: {"foreground": "LimeGreen"},
            Font.string: {"foreground": "DimGray"},
            Font.target: {"foreground": "DarkViolet"},
            Font.scoreboard: {"foreground": "DarkBlue", "font": font_italic},
            Font.tag: {"foreground": "Blue", "font": font_italic},
            Font.position: {"foreground": "DarkTurquoise"},
            Font.rotation: {"foreground": "LightSkyBlue"},
            Font.meta: {"foreground": "Teal"},
            Font.molang_class: {"foreground": "MediumBlue"},
            Font.molang_keyword: {"foreground": "Purple"}
        }
        self.FONT_ERROR = {"background": "Pink"}
        self.update_font()
        # Initial update
        self.update_text(1, popup=False)

    @staticmethod
    def linecol_from_index(index: str) -> Tuple[int, int]:
        """Get line number & column from tkinter index."""
        l = index.split(".")
        assert len(l) == 2
        return int(l[0]), int(l[1])

    @staticmethod
    def line_from_index(index: str) -> int:
        """Get line number from `Text` widget index "X.X"."""
        return int(index.partition(".")[0])

    def _charloc_to_index(self, location: "CharLocation") -> str:
        return "%d.%d" % (location.line + self.line_diff,
                          location.column - 1)
        # Tkinter count from column 0 while we are counting from 1
        # Using "-1c" to handle this can cause strange problem

    def update_font(self):
        """Register color tags to widget."""
        for font, tkopt in self.FONT2FORMAT.items():
            self.tag_config(self.font_to_tag(font), **tkopt)
        self.tag_config(self.ERROR_TKTAG, **self.FONT_ERROR)

    def set_version(self, version: "MCVersion"):
        """Update engine version."""
        self.version = version
        self.update_text(1, popup=False)

    def font_to_tag(self, font: Font) -> str:
        """Convert `Font` to tkinter tag."""
        return self.FONT_TKTAG_PREFIX + font.name

    def new_insert(self, index: str, chars: str, tags=None):
        index = self.index(index)
        self.original_ins(index, chars, tags)
        # We update in group of lines
        line_count = chars.count("\n")
        line_start = self.line_from_index(index)
        line_end = line_start + line_count
        self.update_text(line_start, line_end)

    def new_delete(self, index1: str, index2: Optional[str] = None):
        index1 = self.index(index1)
        if index2 is not None:
            index2 = self.index(index2)
        self.original_del(index1, index2)
        # We update in group of lines
        line_start = self.line_from_index(index1)
        if index2 is None:
            line_end = line_start
        else:
            line_end = self.line_from_index(index2)
        self.update_text(line_start, line_end)

    def update_text(self, line_start: int, line_end: Optional[int] = None,
                    popup: bool = True):
        """Recolorize the text from `line_start` to `line_end`.
        When `line_end` is None, the end will be the end of file.
        """
        # Get parser
        index1 = "%s.0" % line_start
        if line_end is None:
            index2 = self.index("end")
            line_end = self.line_from_index(index2)
        else:
            index2 = "%s.end" % line_end
        src = self.get(index1, index2)
        self.line_diff = line_start - 1
        self.parser = MCCmdParser(src, version=self.version,
                                  **self.parser_kwds)
        # Remove old error tags
        self.tag_remove(self.ERROR_TKTAG, index1, index2)
        # Parse & write errors
        cursor_line_tk, cursor_column_tk = self.linecol_from_index(
            self.index("insert"))
        i = line_start
        error_message = None
        while not self.parser.is_finish():
            try:
                self.parser.parse_line()
            except BaseError as err:
                if isinstance(err, SyntaxError_):
                    idx1 = "%s.%s" % (i, err.location.column - 1)
                    idx2 = "%s.end" % i
                elif isinstance(err, SemanticError):
                    idx1 = "%s.%s" % (i, err.range[0].column - 1)
                    idx2 = "%s.%s" % (i, err.range[1].column - 1)
                else:
                    raise ValueError("Unexpected error %r" % err)
                self.tag_add(self.ERROR_TKTAG, idx1, idx2)
                if i == cursor_line_tk:
                    error_message = self.parser.resolve_error(err)
            i += 1
        if error_message is None:
            error_message = self.parser.translator.get("tkapp.no_error")
        # Get cursor location (if cursor is in the range of update)
        cursor_line = cursor_line_tk - self.line_diff
        cursor_column = cursor_column_tk + 1
        if not 1 <= cursor_line <= line_end - line_start + 1:
            cursor_line = None  # cursor out of update range
        # Update pop-up
        if cursor_line is None:
            self.popup.destroy()
        elif popup:
            suggestions = self.parser.suggest(
                cursor_line, cursor_column, **self.suggest_kwds
            )
            self.popup.update_content(suggestions, error_message)
        # Remove old font tags
        for font in self.FONT2FORMAT:
            self.tag_remove(self.font_to_tag(font), index1, index2)
        # Update font tags
        for mark in self.parser.get_font_marks():
            # NOTE tkinter counts column from 0, rather than 1
            self.tag_add(
                self.font_to_tag(mark.font),
                self._charloc_to_index(mark.begin),
                self._charloc_to_index(mark.end)
            )
