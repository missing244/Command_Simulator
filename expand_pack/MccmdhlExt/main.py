"""Minecraft BE Command Syntax Hightlight Extension for Command Simulator."""

import sys
import os
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))

import json
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
from typing import Optional

from main_source.main_window.constant import PythonActivity

from editor import (
    EditorFile, FileError,
    DEFAULT_WRAP, DEFAULT_VERSION, FILEDIALOG_OPTIONS
)
from palette import PaletteWindow
from constants import *

WELCOME_HINT = """V2.0.7 By CBerJun
新用户一定要看看“面板”里的帮助哦~

还没有打开文件呢~"""

def alert(msg: str):
    tkinter.messagebox.showinfo("错误", msg)

def log(msg: str):
    pass

def _throws_FileError(func):
    def _wrapped(self, *args, **kw):
        try:
            func(self, *args, **kw)
        except FileError:
            alert("文件读取/写入错误")
    return _wrapped

def _pos_str2int(pos: str):
    """convert Tk text position "lineno.col" to (lineno, col) used
    by `mccmdhl2`.
    """
    ln, col = pos.split(".")
    return int(ln), int(col) + 1

class Config:
    def __init__(self, path: str, default_map: dict):
        self.map = default_map
        flag = False
        if os.path.exists(path) and os.path.isfile(path):
            with open(path, "r") as file:
                m = json.load(file)
            if isinstance(m, dict):
                self.map.update(m)
            else:
                flag = True
        else:
            flag = True
        if flag:
            with open(path, "w") as file:
                json.dump(default_map, file)
        self.path = path

    def set(self, name: str, value):
        self.map[name] = value
        with open(self.path, "w") as file:
            json.dump(self.map, file)

    def get(self, name: str):
        return self.map[name]

class pack_class:
    def init(self, main_win, frame: tkinter.Frame):
        self.main_win = main_win
        self.editor_frame = None # The Frame to contain the current editor
        self.editors = [] # All editors
        self.current_editor: EditorFile = None # The current showing editor
        self.function_mode = False # whether Function button is pressed
        self.name2editor = {} # str(Name on Combobox): EditorFile pairs
        self._func_bind_id = None # See `self.on_function_pressed`
        self._palette = None # See `self.on_palette_pressed`

        self.window = self.main_win.window
        self.PLATFORM = self.main_win.platform
        self.root = frame
        self.root.focus_set()
        self._bind_hotkeys(self.root)

        EditorFile.class_init(PythonActivity)

        BUTTON_WIDTH = 4 if self.PLATFORM == "windows" else 2
        frame_top = tkinter.Frame(self.root)
        self.button_func = tkinter.Button(
            frame_top, text="功能", width=BUTTON_WIDTH,
            command=self.on_function_pressed, **BUTTON_FONT
        ) # The Function button
        button_help = tkinter.Button(
            frame_top, text="面板", width=BUTTON_WIDTH,
            command=self.on_palette_pressed, **BUTTON_FONT
        )
        button_find_error = tkinter.Button(
            frame_top, text="查错", width=BUTTON_WIDTH,
            command=self.on_find_error_pressed, **BUTTON_FONT
        )
        self.menu_files = tkinter.ttk.Combobox(frame_top, state="readonly")
        self.menu_files.bind("<<ComboboxSelected>>", self.on_file_change)
        self.button_func.grid(row=0, column=0, padx=(5, 0))
        button_help.grid(row=0, column=1)
        button_find_error.grid(row=0, column=2, padx=(0, 10))
        self.menu_files.grid(row=0, column=3)

        frame_top.grid(row=0, column=0, sticky=tkinter.EW)

        ## Settings
        self.config = Config(
            os.path.join(DIR, "res", "config.json"),
            default_map={
                "wrap_mode": DEFAULT_WRAP,
                "version": list(DEFAULT_VERSION)
            })
        # Current wrap mode index in `ALL_WRAPS`
        self.wrap_mode = ALL_WRAPS.index(self.config.get("wrap_mode"))
        # Version index in `ALL_VERSIONS`
        self.version = ALL_VERSIONS.index(tuple(self.config.get("version")))

        ## Create Welcome page
        FG = "DimGray"
        self.WELCOME_FRAME = tkinter.Frame(self.root)
        title = tkinter.Label(
            self.WELCOME_FRAME, text="指令编辑器",
            font=("Arial", 22), fg=FG
        )
        hint = tkinter.Label(
            self.WELCOME_FRAME, text=WELCOME_HINT, fg=FG, justify=tkinter.LEFT
        )

        frame_options = tkinter.Frame(self.WELCOME_FRAME)
        bt_open = tkinter.Button(
            frame_options, text="打开",
            command=self.file_open, **BUTTON_FONT
        )
        bt_new = tkinter.Button(
            frame_options, text="新建", command=self.file_new, **BUTTON_FONT
        )
        lab_open = tkinter.Label(frame_options, text="功能/Ctrl + O", fg=FG)
        lab_new = tkinter.Label(frame_options, text="功能/Ctrl + N", fg=FG)
        bt_open.grid(row=0, column=0)
        lab_open.grid(row=0, column=1, padx=10)
        bt_new.grid(row=1, column=0, pady=5)
        lab_new.grid(row=1, column=1, padx=10, pady=5)

        title.grid(row=0, column=0, sticky=tkinter.W, pady=(30, 15))
        hint.grid(row=1, column=0, sticky=tkinter.W)
        frame_options.grid(row=2, column=0, sticky=tkinter.W, pady=30)
        ## Show Welcome page
        self.show_welcome()

    def exit_method(self):
        if self.current_editor:
            self.current_editor.hide_popup()

    def _bind_hotkeys(self, widget):
        # Bind hot keys to `widget`
        # In our code, every Text widget for every file and the `root`
        # Frame are bound with this method
        ## global operations
        def _bind(key, func):
            def _cb(event):
                func()
                return "break"
            widget.bind(key, _cb)
        for key, func in (
            ("<Control-n>", self.file_new),
            ("<Control-o>", self.file_open),
            ("<Control-Shift-L>", self.switch_text_wrap),
        ):
            _bind(key, func)
        ## editor operations (Only works when ther is an editor)
        def _editor_bind(key, func):
            def _callback(event):
                if self.current_editor:
                    func()
                return "break"
            widget.bind(key, _callback)
        for key, func in (
            # Control-z/v is auto bound by Tcl
            # Control-c/x is bound by Tcl, but our implementation copies
            # the whole line when no character is selected
            ("<Control-c>", lambda: self.current_editor.edit_copy()),
            ("<Control-x>", lambda: self.current_editor.edit_cut()),
            ("<Control-Shift-Z>", lambda: self.current_editor.edit_redo()),
            ("<Control-s>", self.file_save),
            ("<Control-Shift-S>", self.file_save_as),
            ("<Control-w>", self.file_close),
            ("<Control-i>", self.file_info),
            ("<Control-j>", self.find_error_down),
            ("<Control-Shift-J>", self.find_error_up),
        ):
            _editor_bind(key, func)

    def _grid_editor_frame(self, **kwargs):
        self.editor_frame.grid(row=1, column=0, **kwargs)

    def _prepare_editor_frame(self):
        # Create a frame for a new editor and show it
        if self.editor_frame is not None:
            self.editor_frame.grid_forget()
        self.editor_frame = tkinter.Frame(self.root)
        self._grid_editor_frame()

    def _set_current_editor(self, editor: Optional[EditorFile]):
        if self.current_editor:
            self.current_editor.hide_popup()
        self.current_editor = editor

    def _new_current_editor(self, editor: EditorFile):
        # Set up a newly created editor
        # Register
        self._set_current_editor(editor)
        self.editors.append(editor)
        self.update_all_settings(editor)
        # Focus
        editor.text.focus_set()
        # Key Binds
        self._bind_hotkeys(editor.text)
        # Update menu
        self.update_file_menu()

    def show_welcome(self):
        # Welcome page is only available when no editor exists
        assert not self.editors
        if self.editor_frame:
            self.editor_frame.destroy()
        self.editor_frame = self.WELCOME_FRAME
        self._set_current_editor(None)
        self.menu_files.set("欢迎!")
        self._grid_editor_frame(padx=70)

    def _disable_function(self):
        # Do cleanups after user use any Function
        self.function_mode = False
        self.button_func.config(background=BG_UNPRESSED, text="功能")
        if self.current_editor:
            text = self.current_editor.text
            text.redirector.register("insert", text.new_insert)
            text.redirector.register("delete", text.new_delete)
        if self._func_bind_id:
            self.root.unbind("<Key>", self._func_bind_id)
            self._func_bind_id = None

    def on_function_pressed(self):
        # Callback when user press Function button
        self.function_mode = not self.function_mode
        if not self.function_mode:
            # cancel if user press the button again
            self._disable_function()
        else:
            self.button_func.config(background=BG_PRESSED, text="~功能~")
            if self.current_editor: # if some editor is working
                # Override `text_insert`: when user `input` some text,
                # send the keys to `_handle_function_key`
                def _new_insert(index: str, chars: str, tags=None):
                    self._handle_function_key(chars)
                # Tcl actually does 2 things when user press a key
                # while some text is selected:
                #  1. delete("sel.first", "sel.last")
                #  2. insert("insert", the_key)
                # However, we don't want the text to be deleted when
                # using Function, so we also override delete here
                def _new_delete(index1, index2 = None):
                    pass
                self.current_editor.text.redirector.register(
                    "insert", _new_insert
                )
                self.current_editor.text.redirector.register(
                    "delete", _new_delete
                )
            else: # if no editor is working
                # Just listen to keys
                def _callback(event):
                    self._handle_function_key(event.char)
                self.root.focus_set()
                self._func_bind_id = self.root.bind("<Key>", _callback)

    @_throws_FileError
    def _handle_function_key(self, char: str):
        # Handle the key press after user pressed Function
        self._disable_function()
        if char == "o":
            self.file_open()
        elif char == "n":
            self.file_new()
        elif self.current_editor:
            # These functions only work when an editor exists
            if char == "z":
                self.current_editor.edit_undo()
            elif char == "Z":
                self.current_editor.edit_redo()
            elif char == "c":
                self.current_editor.edit_copy()
                log("成功复制")
            elif char == "v":
                self.current_editor.edit_paste()
                log("成功粘贴")
            elif char == "x":
                self.current_editor.edit_cut()
                log("成功剪切")
            elif char == "L":
                self.switch_text_wrap()
            elif char == "s":
                self.file_save()
            elif char == "S":
                self.file_save_as()
            elif char == "w":
                self.file_close()
            elif char == "i":
                self.file_info()
            elif char == "j":
                self.find_error_down()
            elif char == "J":
                self.find_error_up()

    def on_palette_pressed(self):
        if self._palette:
            try:
                self._palette.focus_set()
            except tkinter.TclError:
                alive = False
            else:
                alive = True
        else:
            alive = False
        if not alive:
            self._palette = PaletteWindow(self)
        else:
            self._palette.destroy()
            self._palette = None

    def on_find_error_pressed(self):
        if self.current_editor:
            self.find_error_down()
        else:
            alert("不在编辑状态下无法查错")

    def update_all_settings(self, editor: EditorFile):
        # Update all settings for editor
        self._update_text_wrap(editor)
        self._update_version(editor)

    def _update_text_wrap(self, editor: EditorFile):
        # Update wrap mode for editor
        editor.text.config(wrap=ALL_WRAPS[self.wrap_mode])
    def _modify_text_wrap(self):
        self.config.set("wrap_mode", ALL_WRAPS[self.wrap_mode])
        for editor in self.editors:
            self._update_text_wrap(editor)
        log(
            "已切换自动换行模式为:\n%s" % (
                "关闭" if ALL_WRAPS[self.wrap_mode] == tkinter.NONE else
                "开启" if ALL_WRAPS[self.wrap_mode] == tkinter.CHAR else
                "开启 (防断词)"
            )
        )
    def switch_text_wrap(self):
        # switch wrap mode of Text widget
        self.wrap_mode += 1
        self.wrap_mode %= len(ALL_WRAPS)
        self._modify_text_wrap()

    def _update_version(self, editor: EditorFile):
        # Update command engine version for editor
        editor.update_version(ALL_VERSIONS[self.version])
    def on_version_update(self):
        version_tuple = ALL_VERSIONS[self.version]
        self.config.set("version", list(version_tuple))
        for editor in self.editors:
            self._update_version(editor)
        log(
            "调整命令版本: %s%s" % (
                ".".join(map(str, version_tuple)),
                " (默认)" if version_tuple == DEFAULT_VERSION else ""
            )
        )

    def update_file_menu(self):
        # Update file menu and `self.name2editor` according to `self.editors`
        self.name2editor.clear()
        ## Give a name to every editors, add number tag when names are the same
        name2editors = {}
        for editor in self.editors:
            if editor.file_path is None: # New files
                key = "未命名"
            else:
                _, key = os.path.split(editor.file_path)
            if key not in name2editors:
                name2editors[key] = [editor]
            else:
                name2editors[key].append(editor)
        def _register(editor: EditorFile, name: str):
            if not editor.file_saved:
                self.name2editor[name + "*"] = editor
            else:
                self.name2editor[name] = editor
        for key, editors in name2editors.items():
            if len(editors) == 1:
                _register(editors[0], key)
            else:
                for i, editor in enumerate(editors):
                    _register(editor, "%s (%d)" % (key, i + 1))
        ## Update Combobox
        self.menu_files["values"] = tuple(self.name2editor.keys())
        # Make sure Combobox is selecting to current editor
        for name, editor_ in self.name2editor.items():
            if self.current_editor is editor_:
                self.menu_files.set(name)
                return

    def file_change_to(self, editor: EditorFile):
        # Change to another editor
        # Since Function button binds the previous editor, we disable it here
        self._disable_function()
        self._set_current_editor(editor)
        if self.editor_frame:
            self.editor_frame.grid_forget()
        self.editor_frame = self.current_editor.master
        self.current_editor.text.focus_set()
        self._grid_editor_frame()

    def on_file_change(self, event):
        # Callback when user change the file
        # Since Function mode override some methods of current_editor,
        # We disable it here
        name = self.menu_files.get()
        self.file_change_to(self.name2editor[name])

    @_throws_FileError
    def file_open(self):
        path = tkinter.filedialog.askopenfilename(**FILEDIALOG_OPTIONS)
        if not path:
            return
        # If the file is already open, just open that editor
        for editor in self.editors:
            if (editor.file_path is not None
                    and os.path.samefile(editor.file_path, path)):
                self.file_change_to(editor)
                self.update_file_menu()
                return

        self._prepare_editor_frame()
        self._new_current_editor(EditorFile.from_file(
            path, self.editor_frame, self
        ))
        log("成功打开文件\n%s" % os.path.basename(path))

    def file_new(self):
        self._prepare_editor_frame()
        self._new_current_editor(EditorFile(self.editor_frame, self))
        log("成功新建文件")

    def file_save(self):
        succeeded = self.current_editor.file_save()
        # An untitled file might get its name after saving,
        # so we `update_file_menu`
        self.update_file_menu()
        if succeeded:
            log("保存成功")

    def file_save_as(self):
        succeeded = self.current_editor.file_save_as()
        self.update_file_menu()
        if succeeded:
            log("另存成功")

    def file_close(self):
        succeeded = self.current_editor.file_close()
        if succeeded:
            old_frame = self.editor_frame
            self.editors.remove(self.current_editor)
            # Switch to the last file if exists
            if self.editors:
                self.file_change_to(self.editors[-1])
            # Switch to welcome page if no editor is left
            else:
                self.show_welcome()
            old_frame.destroy()
            self.update_file_menu()
            log("成功关闭文件")

    def file_info(self):
        fp = self.current_editor.file_path
        info = "文件路径: %s\n文件保存状态: %s" % (
            # File path
            "(无)" if fp is None else fp,
            # Save status
            "已保存" if self.current_editor.file_saved else "未保存"
        )
        tkinter.messagebox.showinfo("文件信息", info)

    def _find_error_updown(self, is_down: bool):
        ins = self.current_editor.text.index("insert")
        if ins:
            line, col = _pos_str2int(ins)
        else:
            self.current_editor.text.mark_set("insert", "1.0")
            line, col = 1, 1
        method = (self.current_editor.find_error_down if is_down else
                  self.current_editor.find_error_up)
        location = method(line, col)
        if location is None:
            alert("找不到错误啦~")
        else:
            pos = "%s.%s" % (location.line, location.column - 1)
            self.current_editor.text.see(pos)
            self.current_editor.text.mark_set("insert", pos)
            log("跳转至错误 %d:%d" % (location.line, location.column))
            self.current_editor.hide_popup()
            self.current_editor.update_status()
    def find_error_down(self):
        self._find_error_updown(is_down=True)
    def find_error_up(self):
        self._find_error_updown(is_down=False)

def UI_set(main_win, frame):
    packcls = main_win.get_expand_pack_class_object(
        "b8c164cd-79ff-4c4e-876c-931d2987d1ae"
    )
    packcls.init(main_win, frame)
