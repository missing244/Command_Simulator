import tkinter,tkinter.messagebox,copy
from tkinter.constants import *
from tkinter import ttk

import main_source.package.tk_tool as tk_tool
import const_func
from typing import List,Literal,Union


window_stack:List[tkinter.Frame] = []
# str -> text ; 
# {"annotation":"", "type":"score", "scoreboard":"", "name":""} ; 
# {"annotation":"", "type":"selector", "name":""}
# {"annotation":"", "type":"translate", "text":"", "json_list":[]} ; 
# "json_list" -> str score selector translate
class Text_Inner_Button(tkinter.Frame) :

    def __init__(self, master, main_win, raw_type:Literal["selector","score","translate"], data:dict=None, **karg) :
        super().__init__(master, **karg)
        self.main_win = main_win
        self.raw_type = raw_type
        if not data :
            if raw_type == "score" : self.rawtext_conpoment = {"annotation":"score", "type":"score", "scoreboard":"", "name":""}
            elif raw_type == "selector" : self.rawtext_conpoment = {"annotation":"selector", "type":"selector", "name":""}
            else : self.rawtext_conpoment = {"annotation":"translate", "type":"translate", "text":"", "json_list":[]}
        else :
            self.rawtext_conpoment = data
        self.bind_ui:Union[translate_ui,selector_ui,score_ui] = None


        left1 = tkinter.Label(self,text=" ",fg='black',font=tk_tool.get_default_font(10),width=1,height=1)
        left1.bind("<Button-1>",lambda a:see_TEXT_index(master,self,0))
        left1.pack(side=LEFT)
        self.button1 = button1 = tkinter.Button(self, text=self.rawtext_conpoment["annotation"], font=tk_tool.get_default_font(9))
        button1.config(command=self.create_new_win)
        button1.pack(side=LEFT)
        right1 = tkinter.Label(self,text=" ",fg='black',font=tk_tool.get_default_font(10),width=1,height=1)
        right1.bind("<Button-1>",lambda a:see_TEXT_index(master,self,1))
        right1.pack(side=LEFT)

    def create_new_win(self) :
        pack_frame:tkinter.Frame = self.main_win.display_frame["expand_pack"]
        if self.raw_type == "score" : self.bind_ui = score_ui.from_json(pack_frame, self.main_win, self, self.rawtext_conpoment)
        elif self.raw_type == "selector" : self.bind_ui = selector_ui.from_json(pack_frame, self.main_win, self, self.rawtext_conpoment)
        else : self.bind_ui = translate_ui.from_json(pack_frame, self.main_win, self, self.rawtext_conpoment)
        window_stack[-1].pack_forget()
        window_stack.append(self.bind_ui)
        window_stack[-1].pack()

    def on_close(self, ui:Union["score_ui","selector_ui","translate_ui"]) :
        self.rawtext_conpoment = ui.to_dict()
        self.button1.config(text=self.rawtext_conpoment["annotation"])
        window_stack.pop()
        ui.pack_forget()
        window_stack[-1].pack()
        if hasattr(window_stack[-1],"input_to_focus") : self.main_win.focus_input = window_stack[-1].input_to_focus


class score_ui(tkinter.Frame) : 

    def __init__(self, master, main_win, Base:Text_Inner_Button, **karg) :
        super().__init__(master, **karg)
        self.base_button_frame = Base
        self.main_win = main_win
        self.rawtext_conpoment = {"annotation":"score", "type":"score", "scoreboard":"", "name":""}

    def __create__(self) :
        tkinter.Label(self,text="注释",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        self.input0 = input0 = tkinter.Entry(self,font=tk_tool.get_default_font(12),justify='center',width=20)
        input0.insert(END,self.rawtext_conpoment['annotation'])
        input0.pack()

        tkinter.Label(self,text="",fg='black',font=('Arial',6),width=15,height=1).pack()
        tkinter.Label(self,text="计分板名称",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        self.input1 = input1 = tkinter.Entry(self,font=tk_tool.get_default_font(12),justify='center',width=20)
        input1.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a)) 
        input1.insert(END,self.rawtext_conpoment['scoreboard'])
        input1.pack()

        tkinter.Label(self,text="",fg='black',font=('Arial',6),width=15,height=1).pack()
        tkinter.Label(self,text="假名或目标选择器",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        self.input2 = input2 = tkinter.Text(self,font=tk_tool.get_default_font(12),width=20,height=3)
        input2.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a)) 
        input2.insert(END,self.rawtext_conpoment['name'])
        input2.pack()

        def update0() : self.rawtext_conpoment['annotation'] = input0.get()
        def update1() : self.rawtext_conpoment['scoreboard'] = input1.get()
        def update2() : self.rawtext_conpoment['name'] = input2.get("1.0",END)[:-1]
        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(10),width=15,height=1).pack()
        tkinter.Button(self,text='确    定',font=tk_tool.get_default_font(10),bg='aquamarine',width=9,height=1,
                       command=lambda : [update0(),update1(),update2(),self.on_close()]).pack()

        self.main_win.focus_input = input1
        return self

    @classmethod
    def from_json(cls, master, main_win, Base, data:dict) :
        ui = cls(master, main_win, Base)
        if "annotation" in data : ui.rawtext_conpoment["annotation"] = data["annotation"]
        if "scoreboard" in data : ui.rawtext_conpoment["scoreboard"] = data["scoreboard"]
        if "name" in data : ui.rawtext_conpoment["name"] = data["name"]
        return ui.__create__()

    def to_dict(self) :
        return self.rawtext_conpoment


    def on_close(self) :
        self.base_button_frame.on_close(self)

class selector_ui(tkinter.Frame) : 

    def __init__(self, master, main_win, Base:Text_Inner_Button, **karg) :
        super().__init__(master, **karg)
        self.base_button_frame = Base
        self.main_win = main_win
        self.rawtext_conpoment = {"annotation":"", "type":"selector", "name":""}

    def __create__(self) :
        tkinter.Label(self,text="注释",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        self.input0 = input0 = tkinter.Entry(self,font=tk_tool.get_default_font(12),justify='center',width=20)
        input0.insert(END,self.rawtext_conpoment['annotation'])
        input0.pack()
        
        tkinter.Label(self,text="",fg='black',font=('Arial',15),width=15,height=1).pack()
        tkinter.Label(self,text="目标选择器或玩家名",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        self.input1 = input1 = tkinter.Text(self,font=tk_tool.get_default_font(12),width=22,height=3)
        input1.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a)) 
        input1.insert(END,self.rawtext_conpoment['name'])
        input1.pack()

        def update0() : self.rawtext_conpoment['annotation'] = input0.get()
        def update1() : self.rawtext_conpoment['name'] = input1.get("1.0",END)[:-1]
        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(10),width=15,height=1).pack()
        tkinter.Button(self,text='确    定',font=tk_tool.get_default_font(10),bg='aquamarine',width=9,height=1,
                       command=lambda : [update0(),update1(),self.on_close()]).pack()

        self.main_win.focus_input = input1
        return self

    @classmethod
    def from_json(cls, master, main_win, Base, data:dict) :
        ui = cls(master, main_win, Base)
        if "annotation" in data : ui.rawtext_conpoment["annotation"] = data["annotation"]
        if "name" in data : ui.rawtext_conpoment["name"] = data["name"]
        return ui.__create__()

    def to_dict(self) :
        return self.rawtext_conpoment


    def on_close(self) :
        self.base_button_frame.on_close(self)

class translate_ui(tkinter.Frame) :

    def __init__(self, master, main_win, Base:Text_Inner_Button, **karg) :
        super().__init__(master, **karg)
        self.base_button_frame = Base
        self.main_win = main_win
        self.rawtext_conpoment = {"annotation":"", "type":"translate", "text":"", "json_list":[]}

    def __create__(self) :
        tkinter.Label(self,text="注释",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        input0 = tkinter.Entry(self,font=tk_tool.get_default_font(12),justify='center',width=20)
        input0.insert(END,self.rawtext_conpoment['annotation'])
        input0.pack()

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(1),width=15,height=1).pack()
        tkinter.Label(self,text="基本内容",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        input1 = tkinter.Text(frame_m10,font=tk_tool.get_default_font(12),width=20,height=6,yscrollcommand=sco1.set,undo=True)
        input1.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a)) 
        input1.insert(END,self.rawtext_conpoment['text'])
        sco1.config(command=input1.yview)
        input1.grid() ; sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(1),width=15,height=1).pack()
        tkinter.Label(self,text="附加with(一行一个元素)",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
        self.input2 = input2 = tkinter.Text(frame_m10,font=tk_tool.get_default_font(12),width=20,height=7,wrap=NONE,yscrollcommand=sco1.set,xscrollcommand=sco2.set,undo=True)
        input2.rawtext_sign = ''
        input2.bind("<FocusIn>",lambda a:self.main_win.set_focus_input(a))
        const_func.content_to_component(input2, self.main_win, self.rawtext_conpoment['json_list'])
        sco1.config(command=input2.yview) ; sco2.config(command=input2.xview)
        input2.grid() ; sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.grid(sticky=tkinter.E+tkinter.W)
        frame_m10.pack()

        def update0() : self.rawtext_conpoment['annotation'] = input0.get()
        def update1() : self.rawtext_conpoment['text'] = input1.get("0.0",END)[:-1]
        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(1),width=15,height=1).pack()
        tkinter.Button(self,text='确    定',font=tk_tool.get_default_font(10),bg='aquamarine',width=9,height=1,
                       command=lambda:[update0(),update1(),self.on_close()]).pack(side="bottom")

        self.main_win.focus_input = input2
        self.input_to_focus = input2
        return self

    @classmethod
    def from_json(cls, master, main_win, Base, data:dict) :
        ui = cls(master, main_win, Base)
        if "annotation" in data : ui.rawtext_conpoment["annotation"] = data["annotation"]
        if "text" in data : ui.rawtext_conpoment["text"] = data["text"]
        if "json_list" in data : ui.rawtext_conpoment["json_list"] = data["json_list"]
        return ui.__create__()

    def to_dict(self) :
        self.rawtext_conpoment["json_list"] = const_func.Text_get_content(self.input2)
        return self.rawtext_conpoment


    def on_close(self) :
        self.base_button_frame.on_close(self)









def batch_add_button(main_win) :
    focus_comp:tkinter.Text = main_win.focus_input
    def combobox_select_change(e:tkinter.Event) :
        list1 = [frame_score, frame_selector, frame_translate]
        for index,element in enumerate(list1) :
            if index == e.widget.current() : element.pack()
            else : element.pack_forget()

    self = tkinter.Toplevel(main_win.window)
    small_win_width, small_win_height = int(self.master.winfo_width()*0.95), int(self.master.winfo_height()*0.55)
    self.resizable(False, False)
    self.geometry('%sx%s+%s+%s'%(small_win_width,small_win_height,self.master.winfo_x(),self.master.winfo_y()))
    self.transient(self.master)
    self.title('setting')

    tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()
    frame_m11 = tkinter.Frame(self)
    tkinter.Label(frame_m11,text="按钮类型",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=10,height=1).pack(side=LEFT)
    input0 = ttk.Combobox(frame_m11, font=tk_tool.get_default_font(13), width=6, state='readonly', justify='center')
    input0["value"] = ("分数", "实体", "翻译")
    input0.current(0)
    input0.bind("<<ComboboxSelected>>", combobox_select_change)
    input0.pack(side=LEFT) ; frame_m11.pack()

    tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()
    frame_m11 = tkinter.Frame(self)
    tkinter.Label(frame_m11,text="按钮数量",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=8,height=1).pack(side=LEFT)
    input1 = tkinter.Entry(frame_m11,font=tk_tool.get_default_font(12),justify='center',width=11)
    input1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
    input1.insert(END,"5")
    input1.pack(side=LEFT) ; frame_m11.pack()

    tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()
    tkinter.Label(self,text="按钮间分隔字符",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=16,height=1).pack()
    input2 = tkinter.Text(self,font=tk_tool.get_default_font(12),width=20,height=2)
    input2.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    input2.pack()

    def update0() : 
        try : 
            if int(input1.get()) < 1 : raise Exception
        except : tkinter.messagebox.showerror("Error","按钮数量应为正整数")
        else :
            if not hasattr(focus_comp, "rawtext_sign") : self.destroy() ; return None
            main_win.focus_input = focus_comp
            times = int(input1.get())
            if input0.current() == 0 : data = {"annotation":"score%s", "type":"score", "scoreboard":score_input1.get(), "name":score_input2.get()}
            elif input0.current() == 1 : data = {"annotation":"selector%s", "type":"selector", "name":selector_input1.get()}
            elif input0.current() == 2 : data = {"annotation":"translate%s", "type":"translate", "text":translate_input1.get("1.0",END)[:-1], "json_list":[]}
            for i in range(times) :
                copy_data = data.copy()
                copy_data["annotation"] = data["annotation"] % i
                inner_button = Text_Inner_Button(focus_comp, main_win, ["score","selector","translate"][input0.current()], copy_data)
                focus_comp.window_create(INSERT, window=inner_button)
                if (i < (times - 1)) : focus_comp.insert(INSERT, input2.get("0.0",END)[:-1])
            self.destroy()
    def update1() : 
        main_win.focus_input = focus_comp

    tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()

    frame_score = tkinter.Frame(self)
    frame_m11 = tkinter.Frame(frame_score)
    tkinter.Label(frame_m11,text="计分板名",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=8,height=1).pack(side=LEFT)
    score_input1 = tkinter.Entry(frame_m11,font=tk_tool.get_default_font(12),justify='center',width=11)
    score_input1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
    score_input1.insert(END,"aaa")
    score_input1.pack(side=LEFT) ; frame_m11.pack()

    tkinter.Label(frame_score,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()
    frame_m12 = tkinter.Frame(frame_score)
    tkinter.Label(frame_m12,text="目标选择器",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=8,height=1).pack()
    score_input2 = tkinter.Entry(frame_m12,font=tk_tool.get_default_font(12),justify='center',width=22)
    score_input2.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
    score_input2.insert(END,"@s[scores={aaa=..1}]")
    score_input2.pack() ; frame_m12.pack()
    frame_score.pack()


    frame_selector = tkinter.Frame(self)
    frame_m12 = tkinter.Frame(frame_selector)
    tkinter.Label(frame_m12,text="目标选择器",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=8,height=1).pack()
    selector_input1 = tkinter.Entry(frame_m12,font=tk_tool.get_default_font(12),justify='center',width=22)
    selector_input1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
    selector_input1.insert(END,"@s")
    selector_input1.pack() ; frame_m12.pack()


    frame_translate = tkinter.Frame(self)
    frame_m12 = tkinter.Frame(frame_translate)
    tkinter.Label(frame_m12,text="翻译基本内容",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=12,height=1).pack()
    translate_input1 = tkinter.Text(frame_m12,font=tk_tool.get_default_font(12),width=22,height=2)
    translate_input1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
    translate_input1.insert(END,"%%s")
    translate_input1.pack() ; frame_m12.pack()


    tkinter.Button(self,text='确    定',font=tk_tool.get_default_font(10),bg='aquamarine',width=9,height=1,
        command=lambda : update0()).pack(side="bottom")
    
    self.protocol("WM_DELETE_WINDOW", lambda:[update1(),self.destroy()])
    self.grab_set()


def see_TEXT_index(focus_input:tkinter.Text, frame1:tkinter.Frame, add_value:int) :
    "设置光标位置"
    if not hasattr(focus_input,"rawtext_sign") : return None
    button_content = focus_input.dump("0.0", END, window=True)
    button_content_text = [i[1] for i in button_content]
    if str(frame1) not in button_content_text : return None
    index1 = button_content_text.index(str(frame1))
    list1 = button_content[index1][2].split(".")
    list1[1] = str(int(list1[1]) + add_value)
    focus_input.focus_set()
    focus_input.mark_set(INSERT,".".join(list1))






