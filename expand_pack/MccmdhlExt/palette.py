"""Floating palette."""

import tkinter
import tkinter.ttk

from constants import *

HELP = """欢迎使用命令编辑器!
以下是一些可供使用的功能，
PC用户也可用Ctrl+字母触发；
手机用户也可按下“功能”后输入字母触发!"""

class PaletteWindow(tkinter.Toplevel):
    def __init__(self, master):
        # master: pack_class
        super().__init__(master.window)
        self.pack_cls = master
        self.wm_title("命令编辑器面板")
        self.wm_transient(master.window)
        BUTTON_WIDTH = 5 if self.pack_cls.PLATFORM == "windows" else 3
        button_font = BUTTON_FONT.copy()
        button_font.update({"width": BUTTON_WIDTH})
        # --- CONTROLS ---
        frame1 = tkinter.Frame(self)
        frame2 = tkinter.Frame(self)
        lab1 = tkinter.Label(frame1, text="文件操作")
        lab1.grid(row=0, column=0, columnspan=4)
        for text, func, row, col in (
            ("打开(o)", self.pack_cls.file_open, 1, 0),
            ("新建(n)", self.pack_cls.file_new, 1, 1),
        ):
            nb = tkinter.Button(frame1, text=text, command=func, **button_font)
            nb.grid(row=row, column=col)
        def _handle(text, func, row, col, master=frame1):
            def _cb():
                if self.pack_cls.current_editor:
                    func()
            nb = tkinter.Button(master, text=text, command=_cb, **button_font)
            nb.grid(row=row, column=col)
        for args in (
            ("保存(s)", self.pack_cls.file_save, 1, 2),
            ("另存(S)", self.pack_cls.file_save_as, 1, 3),
            ("关闭(w)", self.pack_cls.file_close, 2, 0),
            ("信息(i)", self.pack_cls.file_info, 2, 1),
            ("向上(J)", self.pack_cls.find_error_up, 1, 1, frame2),
            ("向下(j)", self.pack_cls.find_error_down, 1, 2, frame2),
        ):
            _handle(*args)
        # --- EDIT ---
        lab2 = tkinter.Label(frame2, text="编辑")
        lab2.grid(row=0, column=0, columnspan=4)
        find_err_lab = tkinter.Label(frame2, text="查错:")
        find_err_lab.grid(row=1, column=0)
        def _handle2(text, func, row, col):
            def _cb():
                if self.pack_cls.current_editor is not None:
                    getattr(self.pack_cls.current_editor, func)()
            nb = tkinter.Button(frame2, text=text, command=_cb, **button_font)
            nb.grid(row=row, column=col)
        for args in (
            ("撤销(z)", "edit_undo", 2, 0),
            ("重做(Z)", "edit_redo", 2, 1),
            ("复制(c)", "edit_copy", 3, 0),
            ("剪切(x)", "edit_cut", 3, 1),
            ("粘贴(v)", "edit_paste", 3, 2),
        ):
            _handle2(*args)
        # --- SETTINGS ---
        frame3 = tkinter.Frame(self)
        # Version
        lab3 = tkinter.Label(frame3, text="设置项")
        lab3.grid(row=0, column=0, columnspan=4)
        v_lab = tkinter.Label(frame3, text="版本:")
        v_lab.grid(row=1, column=0)
        def v_tuple2str(t: tuple):
            return ".".join(map(str, t))
        self.version_str2tuple = {v_tuple2str(t): t
                                  for t in ALL_VERSIONS}
        self.version_box = tkinter.ttk.Combobox(
            frame3, state="readonly",
            values=tuple(self.version_str2tuple.keys())
        )
        self.version_box.set(v_tuple2str(ALL_VERSIONS[self.pack_cls.version]))
        self.version_box.bind("<<ComboboxSelected>>", self.on_version_change)
        self.version_box.grid(row=1, column=1, columnspan=3)
        # Text Wrap
        wrap_lab = tkinter.Label(frame3, text="换行(L):")
        wrap_lab.grid(row=2, column=0)
        self.wrap = tkinter.IntVar(frame3, value=self.pack_cls.wrap_mode)
        rad1 = tkinter.Radiobutton(frame3, text="关闭", variable=self.wrap,
                                   value=ALL_WRAPS.index(tkinter.NONE))
        rad1.grid(row=2, column=1)
        rad2 = tkinter.Radiobutton(frame3, text="开启", variable=self.wrap,
                                   value=ALL_WRAPS.index(tkinter.CHAR))
        rad2.grid(row=2, column=2)
        rad3 = tkinter.Radiobutton(frame3, text="开启 (防断词)", variable=self.wrap,
                                   value=ALL_WRAPS.index(tkinter.WORD))
        rad3.grid(row=2, column=3)
        self.wrap.trace_add("write", self.on_wrap_change)
        # --- COMBINE EVERYTHING ! ---
        hint_lab = tkinter.Label(self, text=HELP, foreground="DimGray")
        hint_lab.grid(row=0, column=0)
        frame1.grid(row=1, column=0)
        frame2.grid(row=2, column=0)
        frame3.grid(row=3, column=0)

    def on_version_change(self, event):
        version = self.version_str2tuple[self.version_box.get()]
        version_idx = ALL_VERSIONS.index(version)
        self.pack_cls.version = version_idx
        self.pack_cls.on_version_update()

    def on_wrap_change(self, *args, **kw):
        self.pack_cls.wrap_mode = self.wrap.get()
        self.pack_cls._modify_text_wrap()
