import tkinter,webbrowser,re
from typing import Any,Literal,Union,Dict,Tuple,List
import main_source.main_window.function as app_function
import main_source.package.tk_tool as tk_tool

class Announcement(tkinter.Frame) :

    def __init__(self, master: Union[tkinter.Misc, None], var_class:app_function.main_window_variable, **karg) -> None:
        super().__init__(master, **karg)
        self.runtime_variable = var_class

        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Label(self,text="推送信息",fg='black',font=tk_tool.get_default_font(20),width=15,height=1).pack()
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.Announce_InputBox = tkinter.Text(frame_m10,show=None,height=19,width=26,font=tk_tool.get_default_font(10),yscrollcommand=sco1.set)
        self.Announce_InputBox.grid()
        self.Announce_InputBox.insert(tkinter.END,"正在获取推送....")
        self.Announce_InputBox.tag_config("text_red",foreground="red")
        self.Announce_InputBox.tag_config("text_orange",foreground="orange")
        self.Announce_InputBox.tag_config("text_green",foreground="green")
        sco1.config(command=self.Announce_InputBox.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(8)).pack()

        frame_m0 = tkinter.Frame(self)
        self.jump_to_web = tkinter.Button(frame_m0, text='了解更多..', bg='purple' ,fg='white',font=tk_tool.get_default_font(11), width=10, height=1)
        self.jump_to_web.pack(side="left")
        tkinter.Label(frame_m0,height=1,text="    ",font=tk_tool.get_default_font(6)).pack(side="left")
        tkinter.Button(frame_m0, text='关闭本界面', bg='purple' ,fg='white',font=tk_tool.get_default_font(11), width=10, height=1, command=self.destroy).pack(side="left")
        frame_m0.pack()

    def set_notification(self, response2:dict = None) :
        self.Announce_InputBox.delete("0.0", tkinter.END)
        if response2 == None : self.Announce_InputBox.insert(tkinter.END,"推送信息获取失败\n\n\n请点击\"关闭本界面\"按钮\n退出该界面")

        notice = [("    %s" % i) for i in response2['notification']]
        self.Announce_InputBox.insert(tkinter.END, "\n".join(notice))
        if 'url' in response2 : self.jump_to_web.config(command=lambda:webbrowser.open(response2['url']))
        if 'high_light' in response2 :
            for search_str in response2['high_light'] :
                match_list:List[List[re.Match]] = [list(re.finditer(search_str, text1)) for text1 in notice]
                for lines, line_match in enumerate(match_list) :
                    lines += 1
                    for matches in line_match : self.Announce_InputBox.tag_add(
                        response2['high_light'][search_str], "%s.%s"%(lines,matches.start()), "%s.%s"%(lines,matches.end())
                    )
        self.Announce_InputBox.config(state="disabled")


class Bottom_Bar(tkinter.Canvas) : 

    def __init__(self, master: Union[tkinter.Misc, None], var_class:app_function.main_window_variable, **karg) -> None:
        self.runtime_variable = var_class
        super().__init__(master, **karg)
        self.config(height=int(master.winfo_height() * 0.075))
        self.config(width=master.winfo_width())
        self.config(bg="black")
        self.bind("<ButtonRelease-1>", lambda e : print(e,e.x,e.y))











