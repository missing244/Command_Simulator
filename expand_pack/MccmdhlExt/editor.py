"""Editor of Minecraft Command Highlighter for Command Simulator."""

import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import mccmdhl2
import mccmdhl2.tkapp
from tkinter.simpledialog import _QueryString

try:
    import jnius
except ImportError:
    jnius = None

from constants import DIR

DEFAULT_WRAP = tkinter.NONE
DEFAULT_VERSION = (1, 20, 20)
FILEDIALOG_OPTIONS = {
    "defaultextension": ".mcfunction",
    "filetypes": (
        ("MC行为包函数", ".mcfunction"),
        ("文本文件", ".txt"),
        ("所有文件", ".*")
    ),
    "initialdir": os.path.join(os.getcwd(), "save_world")
}

def _load_resources():
    global TRANSLATOR, ID_TABLE
    res = os.path.join(DIR, "res")
    trans = os.path.join(res, "translation.json")
    if os.path.exists(trans):
        TRANSLATOR = mccmdhl2.Translator.from_json(trans, encoding="utf-8")
    else:
        TRANSLATOR = mccmdhl2.Translator.empty_translation()
    idt = os.path.join(res, "id_table.json")
    if os.path.exists(idt):
        ID_TABLE = mccmdhl2.IdTable.from_json(idt, encoding="utf-8")
    else:
        ID_TABLE = mccmdhl2.IdTable.empty_table()
_load_resources()
del _load_resources

class FileError(Exception):
    pass

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except:
        raise FileError

def write_file(path, content):
    try:
        with open(path, "w", encoding="utf-8") as file:
            return file.write(content)
    except:
        raise FileError

class AskFileNameDialog(_QueryString):
    @staticmethod
    def __char_windows(char: str):
        # NTFS, exFAT standard preserved characters
        return ("\x00" <= char <= "\x1F") or (char in '\x7F"*/:<>?\\|')
    @staticmethod
    def __char_android(char: str):
        return char in "\x00/\\"

    def __init__(self, *args, cmdsim_mainwin, **kwds):
        self.__cmdsim_mainwin = cmdsim_mainwin
        super().__init__(*args, **kwds)

    def body(self, master):
        super().body(master)
        self.entry.bind("<FocusIn>", lambda evt:
                        self.__cmdsim_mainwin.set_focus_input(evt))

    def validate(self):
        ok = super().validate()
        if not ok:
            return 0
        func = (self.__char_windows
                if self.__cmdsim_mainwin.platform == "windows"
                else self.__char_android)
        if any(func(char) for char in self.result):
            tkinter.messagebox.showwarning(
                "非法文件名", "文件名包含特殊字符",
                parent = self
            )
            self.result = None
            return 0
        return 1

class MCCmdText_(mccmdhl2.tkapp.MCCmdText):
    def __init__(self, cmdsim_mainwin, *args, **kwds):
        super().__init__(*args, **kwds)
        self.bind("<FocusIn>", lambda evt:
                  cmdsim_mainwin.set_focus_input(evt), "+")

    def unbind(self, *args, **kwds):
        return

class EditorFile:
    # One file
    MAX_ERRMSG_LEN = 120
    MAX_ERRMSG_COL = 34
    __initialized = False

    @classmethod
    def class_init(cls, ad_python_activity):
        if cls.__initialized:
            return
        cls.__initialized = True
        cls.ad_python_activity = ad_python_activity
        if cls.ad_python_activity is not None:
            assert jnius
            resources = cls.ad_python_activity.getContext().getResources()
            display = resources.getDisplayAdjustments().getConfiguration()
            ox, oy = display.screenWidthDp, display.screenHeightDp
            convert = resources.getDisplayMetrics().density
            cls.ad_screen_size = (ox * convert, oy * convert)
            android_context = jnius.autoclass('android.content.Context')
            cls.ad_input_service = (
                cls.ad_python_activity.mActivity.getSystemService(
                    android_context.INPUT_METHOD_SERVICE)
            )
            cls.ad_keyevent = jnius.autoclass("android.view.KeyEvent")

    def ad_send_key(self, keycode):
        event_down = self.ad_keyevent(self.ad_keyevent.ACTION_DOWN, keycode)
        event_up = self.ad_keyevent(self.ad_keyevent.ACTION_UP, keycode)
        self.ad_python_activity.mActivity.dispatchKeyEvent(event_down)
        self.ad_python_activity.mActivity.dispatchKeyEvent(event_up)

    def __init__(self, master_widget, packcls):
        self.packcls = packcls
        self.master = master_widget
        self.cmdsim_mainwin = packcls.main_win
        self._IS_MOBILE = self.cmdsim_mainwin.platform != "windows"
        self.version = DEFAULT_VERSION
        self.file_path = None # File path (if exists)
        self.file_saved = False # Whether file is saved
        # Create widgets
        text_scroll_bar_y = tkinter.Scrollbar(self.master)
        text_scroll_bar_x = tkinter.Scrollbar(
            self.master, orient=tkinter.HORIZONTAL
        )
        self.text = MCCmdText_(
            self.cmdsim_mainwin,
            # Master
            self.master,
            # Parsing settings
            mc_version=self.version,
            parser_kwds={"translator": TRANSLATOR},
            suggest_kwds={"id_table": ID_TABLE},
            # UI settings
            font=("Courier", 7 if self._IS_MOBILE else 11),
            height=38 if self._IS_MOBILE else 28,
            width=40 if self._IS_MOBILE else 30,
            undo=True, wrap=DEFAULT_WRAP,
            yscrollcommand=text_scroll_bar_y.set,
            xscrollcommand=text_scroll_bar_x.set
        )
        text_scroll_bar_y.config(command=self.text.yview)
        text_scroll_bar_x.config(command=self.text.xview)
        self.status_bar = tkinter.Label(self.master)
        # Grid widgets
        self.text.grid(
            row=0, column=0, columnspan=2, sticky=tkinter.W, padx=(5, 0)
        )
        text_scroll_bar_y.grid(row=0, column=2, sticky=tkinter.N+tkinter.S)
        text_scroll_bar_x.grid(
            row=1, column=0, columnspan=2, sticky=tkinter.W+tkinter.E
        )
        self.status_bar.grid(row=2, column=0, sticky=tkinter.W)
        # We need to know whether a file is changed, so we tweak insert
        # and delete a little bit
        def _on_modify(func):
            def _wrapped(*args, **kw):
                if self.file_saved:
                    self.file_saved = False
                    self.packcls.update_file_menu()
                func(*args, **kw)
            return _wrapped
        self.text.new_insert = _on_modify(self.text.new_insert)
        self.text.new_delete = _on_modify(self.text.new_delete)
        self.text.redirector.register("insert", self.text.new_insert)
        self.text.redirector.register("delete", self.text.new_delete)
        # Status bar
        self.text.event_add("<<update-status>>",
                            "<KeyRelease>", "<ButtonRelease>")
        self.text.bind("<<update-status>>", lambda evt: self.update_status())
        self.update_status()
        # Extra modification to `mccmdhl2`
        ## `focus_get` does not work on Android, so `on_try_hide` is invalid
        if self._IS_MOBILE:
            self.text.popup.on_try_hide = lambda event: None
        ## popup does not adjust its width automatically on Android
            self.text.popup.LABEL_WRAPLENGTH = 600
            original_create = self.text.popup.create
            def _new_create():
                original_create()
                self.text.popup.listbox.configure(width=30)
            self.text.popup.create = _new_create
        ## fix: completing cannot trigger autoscroll on Android
        if self.ad_python_activity is not None:
            original_complete = self.text.popup.complete
            def _new_complete():
                ok = original_complete()
                if ok:
                    # Force soft keyboard to auto-scroll
                    self.ad_send_key(self.ad_keyevent.KEYCODE_DPAD_LEFT)
                    self.ad_send_key(self.ad_keyevent.KEYCODE_DPAD_RIGHT)
                return ok
            self.text.popup.complete = _new_complete
        ## make sure soft keyboard does not cover popup
        def _new_update_pos():
            this = self.text.popup
            if this.toplevel is None:
                return
            this.text.see("insert")
            bb = this.text.bbox(this.text.index("insert"))
            assert bb is not None
            x, y, dx, dy = bb
            pop_width = this.toplevel.winfo_width()
            pop_height = this.toplevel.winfo_height()
            text_width = this.text.winfo_width()
            origin_x = this.text.winfo_rootx()
            origin_y = this.text.winfo_rooty()
            if self.ad_python_activity is None:  # Windows
                bottom_y = this.text.winfo_screenheight()
            else:  # Android
                soft_kb_height = self.ad_input_service \
                    .getInputMethodWindowVisibleHeight()
                screen_height = self.ad_screen_size[1]
                bottom_y = screen_height - soft_kb_height
            new_x = (origin_x + min(x, max(0, text_width - pop_width)))
            new_y = y_abs = origin_y + y
            if (# enough height below: (till top of keyboard (android)
                # or bottom of screen)
                bottom_y - (y_abs + dy) >= pop_height
                # not enough height above: (till top of screen)
                or y_abs < pop_height
            ):
                # Place pop-up below current line
                new_y += dy
            else:
                # Place pop-up above current line
                new_y -= pop_height
            this.toplevel.wm_geometry("+%d+%d" % (new_x, new_y))
        self.text.popup.update_position = _new_update_pos

    @classmethod
    def from_file(cls, file_path, master_widget, cmdsim_mainwin):
        # Open a file
        inst = cls(master_widget, cmdsim_mainwin)
        inst.text.insert("insert", read_file(file_path))
        # `insert` will show popup
        inst.text.popup.destroy()
        inst.file_saved = True
        inst.file_path = file_path
        inst.update_status()
        return inst

    def update_status(self):
        # Update position "Ln: x, Col: x"
        pos = self.text.index("insert")
        if not pos:
            ln, col = "?", "?"
        else:
            ln, col = pos.split(".")
            col = str(int(col) + 1)
        self.status_bar.config(text="Ln: %s, Col: %s" % (ln, col))

    def _get_content(self):
        t = self.text.get("1.0", "end")
        # Tkinter adds one "\n" to text
        if t.endswith("\n"):
            t = t[:-1]
        return t

    def hide_popup(self):
        self.text.popup.destroy()

    def edit_undo(self):
        self.text.edit_undo()
    def edit_redo(self):
        self.text.edit_redo()

    def _get_copy_pos(self):
        if not self.text.get("sel.first", "sel.last"):
            # no selection -> select the whole line
            lineno = self.text.line_from_index(self.text.index("insert"))
            return "%d.0" % lineno, "%d.end" % lineno
        return "sel.first", "sel.last"
    def edit_copy(self):
        self.text.clipboard_clear()
        self.text.clipboard_append(self.text.get(*self._get_copy_pos()))
    def edit_paste(self):
        try:
            content = self.text.selection_get(selection="CLIPBOARD")
        except tkinter.TclError:
            return
        # Insert the text on clipboard
        self.text.insert("insert", content)
        # Also remove the selected text. Since we override the default
        # delete command (See main.pack_class.on_function_pressed),
        # this must be handled by ourselves
        try:
            self.text.original_del("sel.first", "sel.last")
        except tkinter.TclError:
            pass
    def edit_cut(self):
        pos = self._get_copy_pos()
        self.edit_copy()
        self.text.delete(*pos)

    def file_close(self):
        # Close this file; return whether succeeded
        if self.file_saved:
            return True
        response = tkinter.messagebox.askyesnocancel("关闭文件", "是否要保存文件?")
        if response is True: # close if saved successfully
            self.file_save()
            return self.file_saved
        elif response is None:
            return False
        elif response is False:
            return True
    def file_save(self):
        # Save this file
        if self.file_path is None:
            # No path given -> Save as a new one
            return self.file_save_as()
        write_file(self.file_path, self._get_content())
        self.file_saved = True
        return True
    def file_save_as(self):
        # Save this file to another path
        if self._IS_MOBILE:
            d = AskFileNameDialog(title="另存为", prompt="保存文件名:",
                                  cmdsim_mainwin=self.cmdsim_mainwin)
            res = d.result
            if res is None:
                return False
            file_path = tkinter.filedialog.asksaveasfilename(
                initialfile=res, **FILEDIALOG_OPTIONS)
        else:
            file_path = tkinter.filedialog.asksaveasfilename(
                **FILEDIALOG_OPTIONS)
        if file_path:
            write_file(file_path, self._get_content())
            self.file_path = file_path
            self.file_saved = True
            return True
        return False

    def update_version(self, version: tuple):
        self.version = version
        self.text.set_version(version)

    def _parse_source(self, src: str):
        parser = mccmdhl2.MCCmdParser(src, version=self.version)
        while not parser.is_finish():
            try:
                parser.parse_line()
            except mccmdhl2.SyntaxError_ as err:
                yield err.location
            except mccmdhl2.SemanticError as err:
                yield err.range[0]
            else:
                yield None
    def find_error_down(self, line: int, column: int):
        # type: (int, int) -> mccmdhl2.CharLocation | None
        src = self._get_content()
        lines = src.split("\n")
        cur_line = lines[line - 1]
        def _return(ln: int, col: int):
            reader = mccmdhl2.Reader(src)
            return reader.linecol_to_location(ln, col)
        # Current line
        curline_loc = None
        for loc in self._parse_source(cur_line):
            curline_loc = loc
            break  # current line is only 1 line
        if curline_loc is not None:
            curline_loc = _return(line, curline_loc.column)
            if curline_loc.column > column:
                return curline_loc
        # Below
        below = "\n".join(lines[line:])
        for loc in self._parse_source(below):
            if loc is not None:
                return _return(loc.line + line, loc.column)
        # Above
        above = "\n".join(lines[:line - 1])
        for loc in self._parse_source(above):
            if loc is not None:
                return loc
        # Finally check current line again
        if curline_loc is not None:
            return curline_loc
        # No error
        return None
    def find_error_up(self, line: int, column: int):
        # type: (int, int) -> mccmdhl2.CharLocation | None
        src = self._get_content()
        lines = src.split("\n")
        cur_line = lines[line - 1]
        def _return(ln: int, col: int):
            reader = mccmdhl2.Reader(src)
            return reader.linecol_to_location(ln, col)
        # Current line
        curline_loc = None
        for loc in self._parse_source(cur_line):
            curline_loc = loc
            break  # current line is only 1 line
        if curline_loc is not None:
            curline_loc = _return(line, curline_loc.column)
            if curline_loc.column < column:
                return curline_loc
        # Above
        above = "\n".join(lines[:line - 1])
        for loc in self._parse_source(above):
            if loc is not None:
                return loc
        # Below
        below = "\n".join(lines[line:])
        for loc in self._parse_source(below):
            if loc is not None:
                return _return(loc.line + line, loc.column)
        # Finally check current line again
        if curline_loc is not None:
            return curline_loc
        # No error
        return None
