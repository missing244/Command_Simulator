import tkinter,platform,typing


class tk_Menu(tkinter.Menu) :

    def __init__(self, master: tkinter.Misc , **karg ) -> None:
        super().__init__(master,**karg)
        self.item_counter = 0

    def add_checkbutton(self, **karg) -> None:
        self.item_counter += 1
        return super().add_checkbutton(**karg)
    
    def add_command(self, **karg) -> None:
        self.item_counter += 1
        return super().add_command(**karg)
    
    def add_radiobutton(self, **karg) -> None:
        self.item_counter += 1
        return super().add_radiobutton(**karg)
    
    def add_separator(self, **karg) -> None:
        self.item_counter += 1
        return super().add_separator(**karg)

    def remove_item(self) :
        self.item_counter -= 1
        return super().delete(tkinter.END)


class tk_Sliding(tkinter.Canvas) :
    """
    你需要在frame属性中添加组件
    """

    def __init__(self, master: tkinter.Misc , **karg ) -> None:
        super().__init__(master,**karg)
        self.store_y_motion = 0
        self.frame = tkinter.Frame(self)
        self.add_component()

    def add_component(self) :
        def scroll_by_wheel(event:tkinter.Event) :
            if event.widget not in self.frame.winfo_children() : return None
            self.yview_scroll(int(-1*(event.delta/120)), "units")

        def start_to_move(event:tkinter.Event) : 
            if event.widget not in self.frame.winfo_children() : return None
            self.store_y_motion = event.y

        def scroll_by_motion(event:tkinter.Event) :
            if event.widget not in self.frame.winfo_children() : return None
            self.yview_moveto(self.yview()[0] + (self.store_y_motion - event.y)/(1600 if platform.system() == 'Windows' else 2800))
            self.store_y_motion = event.y

        self.create_window((4,4), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", lambda event: self.configure(scrollregion=self.bbox("all")))
        self.bind_all("<MouseWheel>", scroll_by_wheel)
        self.bind_all("<B1-Motion>", scroll_by_motion)
        self.bind_all("<Button-1>", start_to_move)


class tk_Msgbox(tkinter.Toplevel) :

    """
    初始化参数 parent_window : 父窗口Tk或Toplevel
    可自定义该窗口内的内容
    """
    
    def __init__(self, master: tkinter.Misc, parent_window:typing.Union[tkinter.Tk,tkinter.Toplevel], **karg) :
        if not(isinstance(parent_window,tkinter.Tk) or isinstance(parent_window,tkinter.Toplevel)) : raise TypeError("parent_window 类型不正确")
        super().__init__(master,**karg)
        self.add_component(parent_window)

    def add_component(self,parent_window : typing.Union[tkinter.Tk,tkinter.Toplevel]) :

        # 设置Toplevel窗口的标题
        self.title("MsgBox")
        self.resizable(False, False)
        self.geometry("%sx%s+%s+%s"%(int(parent_window.winfo_width()*2/3),int(parent_window.winfo_height()/5),
                                    int(parent_window.winfo_x() + parent_window.winfo_width()/2 - parent_window.winfo_width()/3),
                                    int(parent_window.winfo_y() + parent_window.winfo_height()/2 - parent_window.winfo_height()/10)))

        # 禁用关闭按钮
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # 将Toplevel窗口设置为模态窗口
        self.grab_set()


class tk_Scrollbar_Text(tkinter.Frame) :
    """
    初始化参数均在属性input_box上生效
    """

    def __init__(self, master: tkinter.Misc, vertical_scrollbar=True,horizontal_scrollbar=True, **karg ) -> None:
        super().__init__(master)
        self.input_box = tkinter.Text(self,show=None,height=21,width=28,font=('Arial', 10),undo=True)
        self.input_box.config(**karg)
        self.input_box.grid()
        if vertical_scrollbar :
            sco1 = tkinter.Scrollbar(self,orient='vertical')
            self.input_box.config(yscrollcommand=sco1.set)
            sco1.config(command=self.input_box.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        if horizontal_scrollbar :
            sco2 = tkinter.Scrollbar(self,orient="horizontal")
            self.input_box.config(yscrollcommand=sco2.set)
            sco2.config(command=self.input_box.xview)
            sco2.grid(row=1,column=0,sticky=tkinter.W+tkinter.E)


class tk_Scrollbar_ListBox(tkinter.Frame) :
    """
    初始化参数均在属性input_box上生效
    """

    def __init__(self, master: tkinter.Misc, vertical_scrollbar=True,horizontal_scrollbar=True, **karg ) -> None:
        super().__init__(master)
        self.input_box = tkinter.Listbox(self,show=None,height=21,width=28,font=('Arial', 10))
        self.input_box.config(**karg)
        self.input_box.grid()
        if vertical_scrollbar :
            sco1 = tkinter.Scrollbar(self,orient='vertical')
            self.input_box.config(yscrollcommand=sco1.set)
            sco1.config(command=self.input_box.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        if horizontal_scrollbar :
            sco2 = tkinter.Scrollbar(self,orient="horizontal")
            self.input_box.config(yscrollcommand=sco2.set)
            sco2.config(command=self.input_box.xview)
            sco2.grid(row=1,column=0,sticky=tkinter.W+tkinter.E)



def copy_to_clipboard(text:str) :
    entry1 = tkinter.Entry()
    entry1.insert(tkinter.END, text)
    entry1.selection_range("0",tkinter.END)
    entry1.event_generate("<<Copy>>")


def get_selection_component(text : tkinter.Text) :
    button_list = text.winfo_children() ; button_content = text.dump("0.0", tkinter.END, window=True)
    result_list = []
    button_list_text = [str(i) for i in button_list]
    button_list = [button_list[button_list_text.index(i[1])] for i in button_content]

    def compare_pos(now : str,start : str,end : str) :
        now,start,end = [int(i) for i in now.split(".")],[int(i) for i in start.split(".")],[int(i) for i in end.split(".")]
        return (start[0] <= now[0] <= end[0]) and (start[1] <= now[1] <= end[1])

    try :
        start_index = start = text.index("sel.first")
        end_index = text.index("sel.last")
    except : return None
    else : 
        for i in range(len(button_content)) :
            if not compare_pos(button_content[i][2],start_index,end_index) : continue
            get_text = text.get(start,button_content[i][2])
            if get_text != "" : result_list.append(get_text)
            result_list.append({
                "key_arg" : button_list[i].key_arg.copy() if (
                    hasattr(button_list[i],'key_arg') and isinstance(button_list[i].key_arg,type({}))
                ) else None
            })
            start = button_content[i][2]
        result_list.append(text.get(start,end_index))
    return result_list


def get_default_font(size:int) :
    import tkinter.font
    a = tkinter.font.nametofont("TkDefaultFont").actual()['family']
    return tkinter.font.Font(family=a,size=size)