import tkinter,tkinter.messagebox,webbrowser,re,json,os,traceback,pickle,base64
import copy,random,threading,time,gc,zlib,subprocess,sys,types,importlib.util,zipfile
from typing import Any,Literal,Union,Dict,Tuple,List,Callable
import tkinter.ttk as ttk

import main_source.main_window.function as app_function
import main_source.main_window.constant as app_constant

import main_source.package.tk_tool as tk_tool
import main_source.package.mc_be_icon as mc_be_icon
import main_source.package.file_operation as FileOperation
import main_source.package.connent_API as connent_API

import main_source.bedrock_edition as Minecraft_BE


class Announcement(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)

        c1 = tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)) ; c1.pack()
        c2 = tkinter.Label(self,text="推送信息",fg='black',font=tk_tool.get_default_font(20),width=15,height=1) ; c2.pack()
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
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()

        frame_m0 = tkinter.Frame(self)
        self.jump_to_web = tkinter.Button(frame_m0, text='了解更多..', bg='purple' ,fg='white',font=tk_tool.get_default_font(11), width=10, height=1)
        self.jump_to_web.pack(side="left")
        tkinter.Label(frame_m0,height=1,text="    ",font=tk_tool.get_default_font(6)).pack(side="left")
        tkinter.Button(frame_m0, text='关闭本界面', bg='purple' ,fg='white',font=tk_tool.get_default_font(11), width=10, height=1,
        command=lambda : [self.pack_forget(), main_win.creat_windows()]).pack(side="left")
        frame_m0.pack()
        main_win.add_can_change_hight_component([self.Announce_InputBox, c1,c2,c1,c1,frame_m0])

    def set_notification(self, response2:dict = None) :
        self.Announce_InputBox.delete("0.0", tkinter.END)
        if response2 == None : 
            self.Announce_InputBox.insert(tkinter.END,"推送信息获取失败\n\n\n请点击\"关闭本界面\"按钮\n退出该界面")
            return

        notice = [("    %s" % i) for i in response2['information']]
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

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.config(height=int(self.master.winfo_height() * 0.075))
        self.config(width=self.master.winfo_width())
        self.config(bg="black")
        self.bind("<ButtonRelease-1>", self.update_menu_text)
        self.Menu = Bottom_Bar_Menu(main_win)
        self.main_win = main_win

        canvas_width = int(self.cget("width")) ; canvas_height = int(self.cget("height"))
        text_id_0 = self.create_text(20, 20, text="游戏", font=tk_tool.get_default_font(14, weight="bold"), fill="#00ff00")
        self.coords(text_id_0, int(canvas_width*0.13), canvas_height//2)
        text_id_1 = self.create_text(20, 20, text="拓展", font=tk_tool.get_default_font(14, weight="bold"), fill="white")
        self.coords(text_id_1, int(canvas_width*0.315), canvas_height//2)
        text_id_2 = self.create_text(20, 20, text="窗口", font=tk_tool.get_default_font(14, weight="bold"), fill="white")
        self.coords(text_id_2, int(canvas_width*0.5), canvas_height//2)
        text_id_3 = self.create_text(20, 20, text="设置", font=tk_tool.get_default_font(14, weight="bold"), fill="white")
        self.coords(text_id_3, int(canvas_width*0.685), canvas_height//2)
        text_id_4 = self.create_text(20, 20, text="菜单", font=tk_tool.get_default_font(14, weight="bold"), fill="#00c8ff")
        self.coords(text_id_4, int(canvas_width*0.87), canvas_height//2)
        self.menu_list = [text_id_0, text_id_1, text_id_2, text_id_3, text_id_4]

    def update_menu_text(self,e:tkinter.Event) -> None:
        test_pass = False
        for text_id_1 in self.menu_list :
            x1,y1,x2,y2 = self.bbox(text_id_1)
            if not(x1 <= e.x <= x2 and y1 <= e.y <= y2) : continue
            if text_id_1 == self.menu_list[0] : self.main_win.game_ready_or_run()
            elif text_id_1 == self.menu_list[1] : self.main_win.set_display_frame('choose_expand')
            elif text_id_1 == self.menu_list[2] : self.main_win.set_display_frame('expand_pack')
            elif text_id_1 == self.menu_list[3] : self.main_win.set_display_frame('setting_frame')
            elif text_id_1 == self.menu_list[4] : self.Menu.post(e.x_root, e.y_root)
            if text_id_1 == self.menu_list[4] : continue
            self.itemconfig(text_id_1, fill="#00ff00")
            test_pass = True
            break
        [self.itemconfig(text_id_2, fill="white") for text_id_2 in self.menu_list if (
        test_pass and text_id_1 != text_id_2 and text_id_2 != self.menu_list[-1])]


class Bottom_Bar_Menu(tkinter.Menu) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, tearoff=False, font=tk_tool.get_default_font(10), **karg)
        self.main_win = main_win

        self.add_command(label='撤销',command=lambda : self.mode_using("undo"))
        self.add_command(label='恢复',command=lambda : self.mode_using("redo"))
        self.add_command(label='清空',command=lambda : self.mode_using("clear"))
        self.add_command(label='回车',command=lambda : self.mode_using("return"))
        self.add_separator()
        self.add_command(label="全选",command=lambda : self.mode_using("select_all"))
        self.add_command(label="剪切",command=lambda : self.mode_using("cut"))
        self.add_command(label='复制',command=lambda : self.mode_using("copy"))
        self.add_command(label='粘贴',command=lambda : self.mode_using("paste"))
        self.add_separator()
        self.add_command(label='行首',command=lambda : self.mode_using("jump_line_start"))
        self.add_command(label='行尾',command=lambda : self.mode_using("jump_line_end"))
        self.add_command(label='选行',command=lambda : self.mode_using("line_select"))
        self.add_separator()
        self.add_command(label='退出',command=lambda : self.exit())

    def mode_using(self, mode, word=None) : 
        focus_input:Union[tkinter.Entry,tkinter.Text,ttk.Entry] = self.main_win.focus_input
        if focus_input == None : return None

        if mode == "select_all" : focus_input.event_generate("<<SelectAll>>")
        elif mode == "cut" : 
            focus_input.event_generate("<<Cut>>") ; self.copy_text = None
            focus_input.event_generate("<ButtonRelease>")
        elif mode == "copy" : focus_input.event_generate("<<Copy>>") ; self.copy_text = None
        elif mode == "paste" : 
            try : focus_input.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
            except : pass
            if app_constant.PythonActivity and app_constant.Context :
                clipboard = app_constant.PythonActivity.getSystemService(app_constant.Context.CLIPBOARD_SERVICE)
                clip_data = clipboard.getPrimaryClip()
                if clip_data :
                    item = clip_data.getItemAt(0)
                    if len(item.getText()) : focus_input.insert(tkinter.INSERT,item.getText())
                    else : focus_input.event_generate("<<Paste>>")
            else : focus_input.event_generate("<<Paste>>")
            focus_input.event_generate("<ButtonRelease>")
        elif mode == "undo" : 
            try : focus_input.edit_undo()
            except : pass
            focus_input.event_generate("<ButtonRelease>")
        elif mode == "redo" : 
            try : focus_input.edit_redo()
            except : pass
            focus_input.event_generate("<ButtonRelease>")
        elif mode == "return" : 
            if not(isinstance(focus_input,tkinter.Entry) or isinstance(focus_input,ttk.Entry)) : 
                try : focus_input.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
                except : pass
                focus_input.insert(tkinter.INSERT,"\n")
            focus_input.event_generate("<ButtonRelease>")
        elif mode == "clear" : 
            focus_input.event_generate("<<SelectAll>>")
            focus_input.event_generate("<<Clear>>")
        elif mode == "input" :
            if isinstance(word,type("")) : return None
            try : focus_input.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
            except : pass
            focus_input.insert(tkinter.INSERT,word)
        elif mode == "line_select" :
            if isinstance(focus_input,tkinter.Text) : 
                line1 = focus_input.index(tkinter.INSERT).split(".")[0]
                chr_count = len(focus_input.get("%s.0" % line1, "%s.end" % line1))
                focus_input.tag_add("sel", "%s.0" % line1, "%s.%s" % (line1 , chr_count))
            if isinstance(focus_input,tkinter.Entry) or isinstance(focus_input,ttk.Entry) : focus_input.event_generate("<<SelectAll>>")
        elif mode == "jump_line_start" :
            if isinstance(focus_input,tkinter.Text) : 
                line1 = focus_input.index(tkinter.INSERT).split(".")[0]
                focus_input.see("%s.0" % line1) ; focus_input.mark_set(tkinter.INSERT,"%s.0" % line1)
            if isinstance(focus_input,tkinter.Entry) or isinstance(focus_input,ttk.Entry) : 
                focus_input.icursor(0) ; focus_input.xview_moveto(0)
        elif mode == "jump_line_end" :
            if isinstance(focus_input,tkinter.Text) : 
                line1 = focus_input.index(tkinter.INSERT).split(".")[0]
                focus_input.see("%s.end" % line1) ; focus_input.mark_set(tkinter.INSERT,"%s.end" % line1)
            if isinstance(focus_input,tkinter.Entry) or isinstance(focus_input,ttk.Entry) : 
                focus_input.icursor(tkinter.END) ; focus_input.xview_moveto(1)
        focus_input.focus_set()

    def exit(self) :
        user_manager:app_function.user_manager = self.main_win.user_manager
        aaa = tkinter.messagebox.askquestion("Question","是否退出本软件？？")
        if aaa == "yes" : user_manager.write_back() ; os._exit(0)

class Right_Click_Menu(tk_tool.tk_Menu) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window,  tearoff=False, **karg)
        small_win_width, small_win_height = int(self.master.winfo_width()*0.95), int(self.master.winfo_height()*0.43)
        self.add_command(label="复制特殊字符",command=lambda : Special_Char(main_win, small_win_width, small_win_height).mainloop())
        self.add_command(label="批量复制字符",command=lambda : Unicode_char(main_win, small_win_width, small_win_height).mainloop())
        self.add_command(label="查询游戏内ID",command=lambda : Find_Minecraft_ID(main_win, small_win_width, small_win_height).mainloop())
        self.add_command(label="复制文件命令",command=lambda : Copy_File_Command(main_win, small_win_width, small_win_height).mainloop())

        main_win.window.bind("<Button-3>", lambda e : self.post(e.x_root, e.y_root))


class Special_Char(tkinter.Toplevel) :

    def __init__(self, main_win, small_win_width, small_win_height, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.display_id = 0
        self.mode_id = "ByteCode"
        self.image_list = [
            ( mc_be_icon.tk_Image(i) if self.main_win.platform == "windows" else mc_be_icon.tk_Image(i).zoom(4,4)
            ) for i in mc_be_icon.icon_list
        ]

        small_win_width, small_win_height = int(self.master.winfo_width()*0.95), int(self.master.winfo_height()*0.43)
        self.resizable(False, False)
        self.geometry('%sx%s+%s+%s'%(small_win_width,small_win_height,self.master.winfo_x(),self.master.winfo_y()))
        self.transient(self.master)
        self.title('特殊字符')

        frame_icon = tkinter.Frame(self)
        self.image_group = Frame_list = [tkinter.Frame(frame_icon) for i in range((len(mc_be_icon.icon_list)//4) + 1)]
        tkinter.Button(frame_icon,width=1,height=5,text="←",bg="#c8bfe7",command=lambda : self.change_page(-1)).pack(side=tkinter.LEFT)
        tkinter.Button(frame_icon,width=1,height=5,text="→",bg="#c8bfe7",command=lambda : self.change_page(1)).pack(side=tkinter.RIGHT)
        frame_icon.pack()

        frame_button = tkinter.Frame(self)
        self.buttom1 = tkinter.Button(frame_button,width=10,height=1,text="复制源字符",bg="#b4f0c8",font=tk_tool.get_default_font(9),
            command=lambda : self.mode_change("ByteCode"), state=tkinter.DISABLED)
        self.buttom1.pack(side=tkinter.LEFT)
        self.buttom2 = tkinter.Button(frame_button,width=10,height=1,text="复制Unicode",bg="#b4f0c8",font=tk_tool.get_default_font(9),
            command=lambda : self.mode_change("Unicode"))
        self.buttom2.pack(side=tkinter.LEFT)
        self.page = tkinter.Label(frame_button,width=6,height=1,text="第%s页"%(self.display_id+1,),font=tk_tool.get_default_font(9))
        self.page.pack(side=tkinter.LEFT)
        frame_button.pack(side=tkinter.BOTTOM)
        self.label1 = tkinter.Label(self,width=25,height=1,text="点击上方图标即可直接复制",font=tk_tool.get_default_font(9))
        self.label1.pack(side=tkinter.BOTTOM)

        for i,j in enumerate(self.image_list) : 
            label = tkinter.Label(Frame_list[i//4],image=j)
            label.word_id = mc_be_icon.icon_list[i]
            label.bind('<Button-1>',lambda event : self.mode_effect(event))
            label.pack(side=tkinter.LEFT)
        Frame_list[0].pack(); Frame_list[1].pack(); Frame_list[2].pack(); Frame_list[3].pack()
    
    def change_page(self, value:int) : 
        self.display_id += value
        if self.display_id * 4 > len(self.image_group) : self.display_id = 0
        if self.display_id < 0 : self.display_id = len(self.image_group) // 4
        for i in range(len(self.image_group)) :
            if (self.display_id * 4) <= i < ((self.display_id + 1) * 4) : self.image_group[i].pack()
            else : self.image_group[i].pack_forget()
        self.page.config(text="第%s页"%(self.display_id+1,))

    def mode_change(self, mode:Literal["ByteCode", "Unicode"]) : 
        self.mode_id = mode
        if self.mode_id == "ByteCode" : self.buttom1.config(state=tkinter.DISABLED)
        else : self.buttom1.config(state=tkinter.NORMAL)
        if self.mode_id == "Unicode" : self.buttom2.config(state=tkinter.DISABLED)
        else : self.buttom2.config(state=tkinter.NORMAL)

    def mode_effect(self, event : tkinter.Event) :
        word_id = event.widget.word_id.replace(".gif","")
        if self.mode_id == "ByteCode" :
            tk_tool.copy_to_clipboard(chr(int(word_id, 16)))
            self.label1.config(text="元字符%s已存入剪切板" % word_id)
        if self.mode_id == "Unicode" : 
            tk_tool.copy_to_clipboard("\\u" + word_id)
            self.label1.config(text="Unicode字符%s已存入剪切板" % word_id)

class Unicode_char(tkinter.Toplevel) :

    def __init__(self, main_win, small_win_width, small_win_height, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.test_str1 = re.compile("^\\\\u[a-fA-F0-9]{4}$")
        self.test_str2 = re.compile("^\\\\u[a-fA-F0-9]{4}~\\\\u[a-fA-F0-9]{4}$")

        small_win_width, small_win_height = int(self.master.winfo_width()*0.95), int(self.master.winfo_height()*0.43)
        self.resizable(False, False)
        self.geometry('%sx%s+%s+%s'%(small_win_width,small_win_height,self.master.winfo_x(),self.master.winfo_y()))
        self.transient(self.master)
        self.title('批量复制')
            
        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()
            
        frame_copy_str = tkinter.Frame(self)
        self.Unicode_collect = tkinter.Text(frame_copy_str, show=None, height=4, width=30, font=tk_tool.get_default_font(10))
        self.Unicode_collect.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        self.Unicode_collect.pack()
        self.Unicode_collect.tag_config("red",background='red')
        tkinter.Label(frame_copy_str, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()

        frame_m3 = tkinter.Frame(frame_copy_str)
        tkinter.Button(frame_m3,text='批量复制',font=tk_tool.get_default_font(10),bg='aquamarine',width=8,height=1,command=self.get_str).pack(side='left')
        tkinter.Label(frame_m3, text="    ", fg='black',font=tk_tool.get_default_font(6), height=1).pack(side='left')
        tkinter.Button(frame_m3,text='退出窗口',font=tk_tool.get_default_font(10),bg='aquamarine',width=8,height=1,command=self.destroy).pack(side='left')
        frame_m3.pack()

        tkinter.Label(frame_copy_str, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        self.label1 = tkinter.Label(frame_copy_str, text="请使用\\uXXXX或\n\\uXXXX~\\uXXXX格式填写\nXXXX为4位16进制，可多行",fg='black',
                                    font=tk_tool.get_default_font(10), width=22, height=3)
        self.label1.pack()
        label2 = tkinter.Label(frame_copy_str, text="点击查询更多字符",fg='blue',font=tk_tool.get_default_font(10), width=22, height=1)
        label2.pack()
        label2.bind("<Button-1>",lambda e: webbrowser.open("https://missing254.github.io/cs-tool/tool/Unicode/page_1.html"))
        frame_copy_str.pack()

    def get_str(self) : 
        self.Unicode_collect.tag_remove("red","0.0",tkinter.END)
        text1 = self.Unicode_collect.get("0.0",tkinter.END)[:-1].split("\n")
        list1 = [bool(self.test_str1.search(i) or self.test_str2.search(i)) for i in text1]
        if (False in list1) : 
            i = list1.index(False) ; self.label1.config(text = "第%s行格式错误"%(i+1,)) 
            self.Unicode_collect.see("%s.%s"%(i+1,len(text1[i])))
            self.Unicode_collect.tag_add("red","%s.0"%(i+1,),"%s.%s"%(i+1,len(text1[i])))
            return False

        copy_text_list = []
        for i in text1 :
            if self.test_str1.search(i) : copy_text_list.append(chr(int("0x" + i.replace("\\u",""),16)))
            elif self.test_str2.search(i) :
                text2 = i.split("~")
                start1,end1 = int("0x" + text2[0].replace("\\u",""),16) , int("0x" + text2[1].replace("\\u",""),16)
                while start1 <= end1 : copy_text_list.append(chr(start1)) ; start1 += 1
        tk_tool.copy_to_clipboard("".join(copy_text_list))
        self.label1.config(text = "Unicode字符已全部存入剪切板")

class Find_Minecraft_ID(tkinter.Toplevel) :

    class search_id_object :
        
        def __init__(self) -> None:
            try : self.MC_ID = json.load(fp=open(os.path.join('main_source','update_source','import_files', 'translate'),"r",encoding="utf-8"))
            except : self.MC_ID = {} ; traceback.print_exc()
        
        def search_str(self, condition_str:str, is_regx=False) :
            if condition_str.replace(" ","") == "" : return []
            self.search_list = result_list = []
            if not is_regx : condition_str = "".join( [("\\u" + hex(ord(i)).replace("0x","0000")[-4:]) for i in condition_str] )
            
            try: 
                if is_regx and re.compile(condition_str).search("") : return None
            except : return None
            compile_re = re.compile(condition_str)

            for i in self.MC_ID :
                result_list += [
                    ("%s%s" % (i,self.MC_ID[i][j]),j) for j in self.MC_ID[i] if compile_re.search("%s%s" % (i,self.MC_ID[i][j]))
                ]

            return result_list
    
    def __init__(self, main_win, small_win_width, small_win_height, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.search_translate_id = self.search_id_object()

        small_win_width, small_win_height = int(self.master.winfo_width()*0.95), int(self.master.winfo_height()*0.43)
        self.resizable(False, False)
        self.geometry('%sx%s+%s+%s'%(small_win_width,small_win_height,self.master.winfo_x(),self.master.winfo_y()))
        self.transient(self.master)
        self.title('查找游戏ID')

        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        frame_m10 = tkinter.Frame(self)
        search_collect = tkinter.Entry(frame_m10, show=None, width=18, font=tk_tool.get_default_font(11))
        search_collect.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease-1>")
        search_collect.bind("<<update-status>>", lambda a : self.search(search_collect.get))
        search_collect.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        search_collect.pack(side='left')
        self.use_regx = tkinter.BooleanVar(self,False)
        tkinter.Checkbutton(frame_m10,text='正则',font=tk_tool.get_default_font(10),variable=self.use_regx,onvalue=True,offvalue=False,
                            height=1,command=lambda : self.search(search_collect.get)).pack(side='left')
        frame_m10.pack()
        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()

        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
        self.search_result = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(10),selectmode=tkinter.SINGLE,height=7,width=26,
            yscrollcommand=sco1.set,xscrollcommand=sco2.set)
        self.search_result.grid()
        sco1.config(command=self.search_result.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.config(command=self.search_result.xview)
        sco2.grid(sticky=tkinter.E+tkinter.W)
        self.search_result.bind("<Double-Button-1>",lambda e : self.copy())
        frame_m10.pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(1), width=15, height=1).pack()
        self.label1 = tkinter.Label(self, text="双击项目以复制",fg='black',font=tk_tool.get_default_font(10), width=22, height=1)
        self.label1.pack()

        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(1), width=15, height=1).pack()

    def search(self, search:Callable) :
        self.search_result.delete(0,tkinter.END)
        list1 = self.search_translate_id.search_str(search(), self.use_regx.get())
        if list1 == None : self.label1.config(text = "正则表达式格式错误") ; return None
        self.search_result.insert(tkinter.END,*[i[0] for i in list1])
        if len(list1) : self.label1.config(text = "搜索成功")

    def copy(self) :
        if len(self.search_result.curselection()) == 0 : self.label1.config(text = "没有选择需要复制的ID") ; return
        for chinese,english in enumerate(self.search_translate_id.search_list) :
            if chinese == self.search_result.curselection()[0] : break
        tk_tool.copy_to_clipboard(english[1])
        self.label1.config(text = "ID 复制完成")

class Copy_File_Command(tkinter.Toplevel) :

    def __init__(self, main_win, small_win_width, small_win_height, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.read_file_data = self.read_saves()

        self.resizable(False, False)
        self.geometry('%sx%s+%s+%s'%(small_win_width,small_win_height,self.master.winfo_x(),self.master.winfo_y()))
        self.transient(self.master)
        self.title('命令复制')

        self.open_frame = open_frame = tkinter.Frame(self)
        tkinter.Label(open_frame, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        frame_m10 = tkinter.Frame(open_frame)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
        self.search_result = search_result = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(9), selectmode=tkinter.SINGLE,
            height=9, width=28, yscrollcommand=sco1.set,xscrollcommand=sco2.set)
        search_result.grid()
        sco1.config(command=search_result.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.config(command=search_result.xview)
        sco2.grid(sticky=tkinter.E+tkinter.W)
        search_result.bind("<Double-Button-1>",lambda e : self.open_file())
        frame_m10.pack()
        self.label1 = tkinter.Label(open_frame, text="双击项目打开文件\n点击文本框复制，绿色为复制成功", fg='black',
            font=tk_tool.get_default_font(10), width=26, height=2)
        self.label1.pack()
        open_frame.pack()

        self.copy_frame = copy_frame = tkinter.Frame(self)
        width_2 = 4 if self.main_win.platform == 'Windows' else 2
        tkinter.Label(copy_frame, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
        frame_m10 = tkinter.Frame(copy_frame)
        sco1 = tkinter.Scrollbar(frame_m10, orient='vertical')
        self.command_display_1 = command_display_1 = tkinter.Text(frame_m10, show=None, height=8, width=30, 
            font=tk_tool.get_default_font(9), yscrollcommand=sco1.set, state='disabled')
        command_display_1.grid()
        sco1.config(command=command_display_1.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        command_display_1.tag_config("green",foreground='#05a705',underline=True)
        command_display_1.bind("<Button-1>",lambda e: self.copy_text())
        frame_m10.pack()

        tkinter.Label(copy_frame, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()
        frame_m10 = tkinter.Frame(copy_frame)
        tkinter.Button(frame_m10,text='←',font=tk_tool.get_default_font(9),bg='#9ae9d1',width=width_2,height=1,
                        command=lambda : self.find_command(add_value = -1)).grid(row=0,column=0)
        tkinter.Label(frame_m10, text="",fg='black',font=tk_tool.get_default_font(3), width=6, height=1).grid(row=0,column=1)
        tkinter.Button(frame_m10,text='返回',font=tk_tool.get_default_font(9),bg='#00ffff',width=6,height=1,
                        command=lambda : [open_frame.pack() , copy_frame.pack_forget()]).grid(row=0,column=2)
        tkinter.Label(frame_m10, text="",fg='black',font=tk_tool.get_default_font(3), width=6, height=1).grid(row=0,column=3)
        tkinter.Button(frame_m10,text='→',font=tk_tool.get_default_font(9),bg='#9ae9d1',width=width_2,height=1,
                        command=lambda : self.find_command(add_value = 1)).grid(row=0,column=4)
        frame_m10.pack()

        tkinter.Label(copy_frame, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()

        frame_m10 = tkinter.Frame(copy_frame)
        set_page = tkinter.Entry(frame_m10,width=12,justify='center')
        set_page.insert(tkinter.END,"输入数值跳转")
        set_page.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
        set_page.bind("<<update-status>>", lambda a : self.find_command(set_value=set_page.get()))
        set_page.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        set_page.pack(side=tkinter.LEFT)

        self.counter1 = tkinter.Label(frame_m10, text="",fg='black',font=tk_tool.get_default_font(10), width=15, height=1)
        self.counter1.pack(side=tkinter.LEFT)
        frame_m10.pack()
        self.protocol("WM_DELETE_WINDOW", lambda : self.save_saves(self.read_file_data))

        path1 = os.path.join("functionality","command","")
        for i in [i for i in FileOperation.file_in_path(path1) if self.check_name(i)] : 
            if i[0] == "dir" : continue
            search_result.insert(tkinter.END, i.replace(path1,"",1))

    def read_saves(self) -> dict :
        save_path = os.path.join("functionality","command","saves.pick")
        if not os.path.exists(save_path) or not os.path.isfile(save_path) : return {}
        else : 
            with open(save_path, 'rb') as f : a = pickle.load(f)
            return a
                
    def save_saves(self, data1:dict) :
        save_path = os.path.join("functionality","command","saves.pick")
        with open(save_path, 'wb') as f: pickle.dump(data1,f)
        self.destroy()

    def open_file(self) :
        if len(self.search_result.curselection()) == 0 : self.label1.config(text = "你没有选择需要打开的文件") ; return None
        path1 = self.search_result.get(self.search_result.curselection())
        try : f = open(os.path.join("functionality","command",path1),"r",encoding="utf-8")
        except : self.label1.config(text = "文件打开失败") ; traceback.print_exc() ; return None
        else : 
            content_1 = f.read() ; f.close()
            if path1 not in self.read_file_data : self.read_file_data[path1] = {"lines" : 1}
            self.file_content = [i for i in content_1.split("\n") if len(i.replace(" ",""))]
            self.file_name = path1
            self.open_frame.pack_forget() ; self.copy_frame.pack()
            self.find_command(add_value = 0)

    def check_name(self, file_name:str) :
        if re.search(".txt$|.mcfunction$",file_name) == None : return False
        try : open(file_name,"r",encoding="utf-8").close()
        except : return False
        else : return True



    def find_command(self, set_value = None , add_value = None) :
        try :
            if set_value != None and int(set_value) : pass
            if add_value != None and int(add_value) : pass
        except : return None
        value1 = self.read_file_data[self.file_name]['lines']
        if set_value : value1 = int(set_value)
        elif add_value : value1 += int(add_value)
        if not (1 <= value1 <= len(self.file_content)) : return None
        self.command_display_1.config(state="normal")
        self.command_display_1.delete("0.0",tkinter.END)
        self.command_display_1.insert(tkinter.END,self.file_content[value1-1])
        self.command_display_1.config(state="disabled")
        self.read_file_data[self.file_name]['lines'] = value1
        self.counter1.config(text="第%s条 共%s条" % (value1,len(self.file_content)))

    def copy_text(self) :
        self.command_display_1.tag_add("green","0.0",tkinter.END)
        tk_tool.copy_to_clipboard(self.file_content[self.read_file_data[self.file_name]['lines'] - 1])


class Game_Ready(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        a1 = tkinter.Label(self, text="模拟世界存档", bg='#82aaff',fg='black',font=tk_tool.get_default_font(20), width=15, height=1)
        a1.pack()

        c1 = tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)) ; c1.pack()

        frame_m3 = tkinter.Frame(self)
        tkinter.Button(frame_m3,text='生成',font=tk_tool.get_default_font(11),bg='aquamarine',width=5,height=1,command=self.create_world).pack(side='left')
        tkinter.Label(frame_m3, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m3,text='删除',font=tk_tool.get_default_font(11),bg='aquamarine',width=5,height=1,command=self.delete_world).pack(side='left')
        tkinter.Label(frame_m3, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m3,text='进入',font=tk_tool.get_default_font(11),bg='aquamarine',width=5,height=1,command=self.join_world).pack(side='left')
        frame_m3.pack()
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        self.list_select = tkinter.Listbox(self,font=tk_tool.get_default_font(13), selectmode=tkinter.SINGLE, height=13, width=22)
        self.list_select.pack()
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()

        frame_m4 = tkinter.Frame(self)
        tkinter.Button(frame_m4,text='帮助文档',font=tk_tool.get_default_font(11),bg='#D369a9',width=8,height=1,
        command=lambda : webbrowser.open("http://localhost:32323")).pack(side='left')
        tkinter.Label(frame_m4, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m4,text='常见问题',font=tk_tool.get_default_font(11),bg='#D369a9',width=8,height=1,
        command=lambda : webbrowser.open("https://missing254.github.io/cs-tool/tool/Question/")).pack(side='left')
        frame_m4.pack()

        main_win.add_can_change_hight_component([self.list_select, a1,c1,frame_m3,c1,c1,frame_m4])
        self.flash_world()

    def create_world(self):
        try : import brotli
        except : tkinter.messagebox.showerror("Error","命令模拟器\n没有安装原版拓展")
        else : self.main_win.set_display_frame("creat_world")

    def delete_world(self):
        if len(self.list_select.curselection()) == 0 : return
        text1 = self.list_select.get(self.list_select.curselection()).split("-->")[1]
        FileOperation.delete_all_file(os.path.join('save_world', text1))
        aaa = tkinter.messagebox.askquestion('Question', '第1次确认\n是否删除选择的世界？\n所有文件都将会被删除!!!')
        if aaa != "yes" : return
        aaa = tkinter.messagebox.askquestion('Question', '第2次确认\n是否删除选择的世界？\n所有文件都将会被删除!!!')
        if aaa != "yes" : return
        tkinter.messagebox.showinfo("Success", "世界 %s \n已成功删除" % text1)
        self.flash_world()

    def join_world(self):
        import main_source.main_window.constant as app_constants
        if any([i.is_alive() for i in self.main_win.initialization_process]) :
            tkinter.messagebox.showerror("Error", "正在加载软件,请稍后....") ; return None
        
        if len(self.list_select.curselection()) == 0 : return None
        try : import brotli
        except : tkinter.messagebox.showerror("Error", "未安装完整原版拓展\n请在拓展包界面中安装") ; return None
        else : importlib.reload(Minecraft_BE.Constants)
        game_process = Minecraft_BE.RunTime.minecraft_thread()
        world_name = self.list_select.get(self.list_select.curselection()).split("-->")[1]
        func = self.main_win.display_frame["game_run"].set_gametime
        aaa = game_process.__game_loading__(world_name, func)
        if isinstance(aaa, Warning) : tkinter.messagebox.showwarning("Warning", aaa.args[0])
        elif isinstance(aaa, Exception) : tkinter.messagebox.showerror("Error", aaa.args[0]) ; return None
        self.main_win.game_process = game_process
        self.main_win.game_ready_or_run()
        self.main_win.display_frame["game_run"].join_world()
        self.main_win.display_frame["game_terminal"].join_world()
        game_process.loop_thread.start()
    
    def flash_world(self) : 
        self.list_select.delete(0,"end")
        file_path,dir_list,_ = list(os.walk("save_world"))[0]

        for dir_name in dir_list :
            now_test = os.path.join(file_path, dir_name) ; text_pass = True
            for prove_file_name in app_constant.world_file_prove :
                try : json.load(fp=open(os.path.join(now_test,prove_file_name), "r", encoding="utf-8"))
                except : text_pass = False ; break
            if not text_pass : continue
            world_name = json.load(fp=open(os.path.join(now_test,'level_name'), "r", encoding="utf-8"))["name"]
            textbox_text = "-->".join((world_name, dir_name))
            self.list_select.insert(tkinter.END,textbox_text)

class Creat_World(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.world_config_copy = copy.deepcopy(app_constant.world_config)

        tkinter.Label(self,text="世界名字",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        self.input0 = input0 = tkinter.Entry(self,font=tk_tool.get_default_font(12),justify='center',width=20)
        input0.insert(tkinter.END, self.world_config_copy['normal_setting']['world_name'])
        input0.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
        input0.pack()

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()
        tkinter.Label(self,text="世界种子",fg='black',font=tk_tool.get_default_font(12),width=20,height=1).pack()
        self.input1 = input1 = tkinter.Entry(self,font=tk_tool.get_default_font(12),justify='center',width=20)
        input1.insert(tkinter.END,str(random.randint(-2**50,2**50)))
        input1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
        input1.pack()

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()
        frame_m11 = tkinter.Frame(self)
        tkinter.Label(frame_m11,text="世界难度",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=10,height=1).pack(side=tkinter.LEFT)
        self.input2 = input2 = ttk.Combobox(frame_m11, font=tk_tool.get_default_font(12), width=6, state='readonly', justify='center')
        input2["value"] = ("和平", "简单", "普通", "困难")
        input2.current(2)
        input2.pack(side=tkinter.LEFT)
        frame_m11.pack()
            
        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(1),width=15,height=1).pack()
        frame_m11 = tkinter.Frame(self)
        tkinter.Label(frame_m11,text="世界类型",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=10,height=1).pack(side=tkinter.LEFT)
        self.input3 = input3 = ttk.Combobox(frame_m11, font=tk_tool.get_default_font(12), width=6, state='readonly', justify='center')
        input3["value"] = ("普通", "平坦")
        input3.current(0)
        input3.pack(side=tkinter.LEFT)
        frame_m11.pack()

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(1),width=15,height=1).pack()
        frame_m11 = tkinter.Frame(self)
        tkinter.Label(frame_m11,text="模拟距离",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=10,height=1).pack(side=tkinter.LEFT)
        self.input4 = input4 = ttk.Combobox(frame_m11, font=tk_tool.get_default_font(12), width=6, state='readonly', justify='center')
        input4["value"] = ("4", "6", "8", "10")
        input4.current(0)
        input4.pack(side=tkinter.LEFT)
        frame_m11.pack()
            
        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(1),width=15,height=1).pack()
        frame_m11 = tkinter.Frame(self)
        tkinter.Label(frame_m11,text="函数运行上限",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=12,height=1).pack(side=tkinter.LEFT)
        self.input5 = input5 = tkinter.Entry(frame_m11,font=tk_tool.get_default_font(12),justify='center',width=7)
        input5.insert(tkinter.END,self.world_config_copy['be_gamerule']['functionCommandLimit'])
        input5.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
        input5.pack(side=tkinter.LEFT)
        frame_m11.pack()
            
        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(1),width=15,height=1).pack()
        frame_m11 = tkinter.Frame(self)
        tkinter.Label(frame_m11,text="命令方块上限",bg="#b0b0b0",fg='black',font=tk_tool.get_default_font(12),width=12,height=1).pack(side=tkinter.LEFT)
        self.input6 = input6 = tkinter.Entry(frame_m11,font=tk_tool.get_default_font(12),justify='center',width=7)
        input6.insert(tkinter.END,self.world_config_copy['be_gamerule']['maxCommandChainLength'])
        input6.bind("<FocusIn>",lambda a : main_win.set_focus_input(a)) 
        input6.pack(side=tkinter.LEFT)
        frame_m11.pack()

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()
        self.input7 = input7 = tkinter.IntVar(self)
        tkinter.Checkbutton(self,text='启用命令方块',font=tk_tool.get_default_font(12),variable=input7,onvalue=True,
                            offvalue=False,width=15,height=1).pack()

        self.input8 = input8 = tkinter.IntVar(self)
        tkinter.Checkbutton(self,text='生物死亡掉落',font=tk_tool.get_default_font(12),variable=input8,onvalue=True,
                            offvalue = False,width=15,height=1).pack()

        self.input9 = input9 = tkinter.IntVar(self)
        tkinter.Checkbutton(self,text='方块破坏掉落',font=tk_tool.get_default_font(12),variable=input9,onvalue=True,offvalue=False,
                            width=15,height=1).pack()

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(2),width=15,height=1).pack()
        frame_m3 = tkinter.Frame(self)
        tkinter.Button(frame_m3,text='返回界面',font=tk_tool.get_default_font(11),bg='aquamarine',width=8,height=1,
                        command=lambda:main_win.set_display_frame("game_ready")).pack(side='left')
        tkinter.Label(frame_m3,text="",fg='black',font=tk_tool.get_default_font(1),width=4,height=1).pack(side='left')
        tkinter.Button(frame_m3,text='生成世界',font=tk_tool.get_default_font(11),bg='aquamarine',width=8,height=1,
                        command=self.save).pack(side='left')
        frame_m3.pack()

    def save(self) :
        try : 
            if int(self.input5.get()) < 0 or int(self.input5.get()) > 10000 : raise Exception
            self.world_config_copy['be_gamerule']['functionCommandLimit'] = int(self.input5.get())
        except : tkinter.messagebox.showerror("Error","函数运行上限\n应填入 0~10000 的整数") ; return None
                
        try : 
            if int(self.input6.get()) <= 0  or int(self.input6.get()) > 100000 : raise Exception
            self.world_config_copy['be_gamerule']['maxCommandChainLength'] = int(self.input6.get())
        except : tkinter.messagebox.showerror("Error","命令方块上限\n应填入 0~100000 的整数") ; return None
        self.world_config_copy['normal_setting']['world_name'] = self.input0.get()
        self.world_config_copy['normal_setting']['seed'] = self.input1.get()
        self.world_config_copy['normal_setting']['difficulty'] = self.input2.current()
        self.world_config_copy['normal_setting']['world_data_type'] = ["infinity","flat"][self.input3.current()]
        self.world_config_copy['normal_setting']['simulator_distance'] = int(self.input4["value"][self.input4.current()])
        self.world_config_copy['be_gamerule']['commandBlocksEnabled'] = bool(self.input7.get())
        self.world_config_copy['be_gamerule']['doMobLoot'] = bool(self.input8.get())
        self.world_config_copy['be_gamerule']['doTileDrops'] = bool(self.input9.get()) 

        if self.create_world() : self.main_win.game_ready_or_run()

    def create_world(self):
        aaa = tkinter.messagebox.askquestion('Title', '二次确认\n是否确认创建世界？', )
        if aaa != "yes" : return None
        os.makedirs("save_world", exist_ok=True)
        rand_text = hex(random.randint(268435456, 536870912))[3:]
        try :
            level_name = json.dumps({"name":self.world_config_copy['normal_setting']['world_name'],
                "verification_challenge":None, "verification_id":None, 'terminal_command':""})
            FileOperation.write_a_file(os.path.join("save_world",rand_text,"level_name"), level_name)

            world_info = Minecraft_BE.BaseNbtClass.world_nbt().__load__(self.world_config_copy).__save__()
            FileOperation.write_a_file(os.path.join("save_world",rand_text,"world_info"), 
                json.dumps(world_info, ensure_ascii=False, default=Minecraft_BE.DataSave.encoding))

            scoreboard = Minecraft_BE.BaseNbtClass.scoreboard_nbt().__save__()
            FileOperation.write_a_file(os.path.join("save_world",rand_text,"scoreboard"), 
                json.dumps(scoreboard, ensure_ascii=False, default=Minecraft_BE.DataSave.encoding))

            chunk_data = Minecraft_BE.BaseNbtClass.chunk_nbt().__save__()
            chunk_data['block_mapping'].extend(Minecraft_BE.Constants.DEFAULT_BLOCK_MAP)
            FileOperation.write_a_file(os.path.join("save_world",rand_text,"chunk_data"), 
                json.dumps(chunk_data, ensure_ascii=False, default=Minecraft_BE.DataSave.encoding))
        except :
            FileOperation.delete_all_file(os.path.join("save_world",rand_text))
            tkinter.messagebox.showerror("Error","创建世界错误\n日志 create_world.txt 已生成")
            traceback.print_exc(file=open(os.path.join("log","create_world.txt"), "w+",encoding="utf-8"))
            return None

        os.makedirs(os.path.join("save_world",rand_text,"behavior_packs"),exist_ok=True)
        os.makedirs(os.path.join("save_world",rand_text,"resource_packs"),exist_ok=True)
        os.makedirs(os.path.join("save_world",rand_text,"command_blocks"),exist_ok=True)
        os.makedirs(os.path.join("save_world",rand_text,"chunk_info","overworld"),exist_ok=True)
        os.makedirs(os.path.join("save_world",rand_text,"chunk_info","nether"),exist_ok=True)
        os.makedirs(os.path.join("save_world",rand_text,"chunk_info","the_end"),exist_ok=True)

        self.main_win.display_frame["game_ready"].flash_world()
        return True

class Game_Run(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()

        self.world_gt = tkinter.Label(self, bg='green',fg='white',font=tk_tool.get_default_font(12), width=21, height=1)
        self.world_gt.pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.input_box1 = tkinter.Text(frame_m10,show=None,height=22,width=28,font=tk_tool.get_default_font(10),
            yscrollcommand=sco1.set,undo=True)
        self.input_box1.grid()
        self.input_box1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        self.input_box1.tag_config("syntax_error", background="#ff6161")
        sco1.config(command=self.input_box1.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()

        c1 = tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1) ; c1.pack()

        frame_m4 = tkinter.Frame(self)
        self.send_command_button = tkinter.Button(frame_m4,text="执行", bg='pink',fg='black',
            font=tk_tool.get_default_font(11), width=5, height=1, command=self.send_command)
        self.send_command_button.pack(side='left')
        tkinter.Label(frame_m4, text="", fg='black', font=tk_tool.get_default_font(3),width=2,height=1).pack(side='left')
        self.see_feedback_button = tkinter.Button(frame_m4,text="终端", bg='pink',fg='black',
            font=tk_tool.get_default_font(11), width=5, height=1, command=self.display_terminal)
        self.see_feedback_button.pack(side='left')
        tkinter.Label(frame_m4, text="", fg='black', font=tk_tool.get_default_font(3),width=2,height=1).pack(side='left')
        tkinter.Button(frame_m4, text='退出', bg='pink',font=tk_tool.get_default_font(11), width=5, height=1,
            command=self.exit_world).pack(side='left')
        frame_m4.pack()

        main_win.add_can_change_hight_component([self.input_box1, c1,self.world_gt,c1,frame_m4])

    def join_world(self) : 
        def aaaa(_game:Minecraft_BE.RunTime.minecraft_thread, Terminal = self.input_box1) :
            Terminal.tag_remove("syntax_error", "1.0",'end')
            for feedback in _game.runtime_variable.terminal_command_feedback :
                if isinstance(feedback, tuple) : 
                    Terminal.tag_add("syntax_error", "%s.%s" % (feedback[0],feedback[2]), "%s.end" % feedback[0])
        Minecraft_BE.GameLoop.modify_termial_end_hook("add",aaaa)

        game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
        self.input_box1.delete("1.0",'end')
        while game_process.world_infomation == None : pass
        if ("verification_challenge" not in game_process.world_infomation) or (
            not game_process.world_infomation['verification_challenge']) : 
            self.input_box1.insert('end', game_process.world_infomation['terminal_command'])
            self.input_box1.config(state="normal")
            self.send_command_button.config(state="normal")
            self.see_feedback_button.config(state="normal")
            self.input_box1.see("end")
        else : 
            self.input_box1.config(state="disabled")
            self.send_command_button.config(state="disabled")
            self.see_feedback_button.config(state="disabled")

    def exit_world(self):
        game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
        game_process.in_game_tag = False
        game_process.world_infomation['terminal_command'] = self.input_box1.get("0.0","end")[:-1]

        aaa = game_process.__exit_world__()
        if isinstance(aaa, Warning) : tkinter.messagebox.showwarning("Warning", aaa.args[0])
        elif isinstance(aaa, Exception) : tkinter.messagebox.showerror("Error", aaa.args[0])

        self.main_win.game_process = None
        self.main_win.game_ready_or_run()
        threading.Thread(target=lambda:[time.sleep(4), gc.collect()]).start()

    def send_command(self) :
        game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
        game_process.runtime_variable.terminal_command = self.input_box1.get("1.0", tkinter.END)
        #exec(self.input_box1.get("1.0",'end'),globals(),locals())
        game_process.runtime_variable.terminal_send_command = True
        self.display_terminal()
        self.main_win.display_frame["game_terminal"].clear_terminal()

    def display_terminal(self) : 
        self.main_win.set_display_frame("game_terminal")

    def set_gametime(self, time:int) :
        self.world_gt.config(text="游戏刻：%s" % time)

class Game_Terminal(tkinter.Frame) :
    
    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()

        c0 = tkinter.Label(self, text="终端执行返回界面",bg="green",fg="white",font=tk_tool.get_default_font(12), width=21, height=1)
        c0.pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
        self.input_box2 = tkinter.Text(frame_m10,show=None,height=21,width=28,font=tk_tool.get_default_font(10),wrap=tkinter.NONE,
            yscrollcommand=sco1.set,xscrollcommand=sco2.set)
        self.input_box2.grid()
        sco1.config(command=self.input_box2.yview)
        sco2.config(command=self.input_box2.xview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.grid(row=1,column=0,sticky=tkinter.W+tkinter.E)
        frame_m10.pack()

        c1 = tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1) ; c1.pack()

        frame_m4 = tkinter.Frame(self)
        tkinter.Button(frame_m4,text="执行", bg='pink',fg='black',font=tk_tool.get_default_font(11), width=5, height=1, 
                       command=self.send_command).pack(side='left')
        tkinter.Label(frame_m4, text="", fg='black', font=tk_tool.get_default_font(3),width=2,height=1).pack(side='left')
        tkinter.Button(frame_m4,text="命令", bg='pink',fg='black',font=tk_tool.get_default_font(11), width=5, height=1, 
                       command=self.display_input).pack(side='left')
        tkinter.Label(frame_m4, text="", fg='black', font=tk_tool.get_default_font(3),width=2,height=1).pack(side='left')
        tkinter.Button(frame_m4,text='退出',bg='pink',font=tk_tool.get_default_font(11), width=5, height=1,
                       command=self.exit_world).pack(side='left')
        frame_m4.pack()

        main_win.add_can_change_hight_component([self.input_box2, c0,c1,sco2,c1,frame_m4])

    def join_world(self) : 
        game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
        self.input_box2.delete("1.0",'end')
        
        def aaaa(_game:Minecraft_BE.RunTime.minecraft_thread, Terminal = self.input_box2) :
            Terminal.delete("1.0",'end')
            for feedback in _game.runtime_variable.terminal_command_feedback :
                if isinstance(feedback, tuple) : 
                    error_command = _game.runtime_variable.terminal_command.split("\n")[feedback[0]-1]
                    Terminal.insert(tkinter.END, "[\u2718]%s\n%s\n\n" % (error_command,feedback[1]))
                else : 
                    Terminal.insert(tkinter.END, "[%s]%s\n%s\n\n" % ("\u2714" if feedback.success_count else "\u2718",
                    feedback.command, feedback.command_msg))
        Minecraft_BE.GameLoop.modify_termial_end_hook("add",aaaa)

    def clear_terminal(self) :
        self.input_box2.delete("1.0",'end')
        self.input_box2.insert(tkinter.END, "等待执行......")

    def send_command(self) : 
        self.main_win.display_frame["game_run"].send_command()

    def display_input(self) : 
        self.main_win.set_display_frame("game_run")

    def exit_world(self) : 
        self.main_win.display_frame["game_run"].exit_world()


class Choose_Expand(tkinter.Frame) :
    
    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.expand_pack_list = {
            "c0414919-e6ed-4b41-b2ac-130119684144": {
                "crc32": None, "pack_name": "原版拓展(模拟器专用)", "import":["pycparser","cffi",'brotlipy']
            }}
        self.is_installing = False #正在安装拓展包

        a1 = tkinter.Label(self,text="拓展包安装",bg='#82aaff',fg='black',font=tk_tool.get_default_font(20),width=15,height=1)
        a1.pack()

        c1 = tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1) ; c1.pack()

        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.expand_select = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(12),selectmode=tkinter.SINGLE,
            height=17,width=23,yscrollcommand=sco1.set)
        self.expand_select.grid()
        sco1.config(command=self.expand_select.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()

        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()

        frame_m6 = tkinter.Frame(self)
        tkinter.Button(frame_m6,text='安装',font=tk_tool.get_default_font(12),bg='pink',width=5, height=1,
                       command=self.on_expand_install).pack(side='left')
        tkinter.Canvas(frame_m6,width=10, height=5).pack(side='left')
        tkinter.Button(frame_m6,text='重启',font=tk_tool.get_default_font(12),bg='pink',width=5, height=1,
                       command=lambda:self.on_expand_enable(True)).pack(side='left')
        tkinter.Canvas(frame_m6,width=10, height=5).pack(side='left')
        tkinter.Button(frame_m6,text='启动',font=tk_tool.get_default_font(12),bg='pink',width=5, height=1,
                       command=lambda:self.on_expand_enable(False)).pack(side='left')
        frame_m6.pack()
        
        threading.Thread(target=self.flash_expand_pack_list).start()
        main_win.add_can_change_hight_component([self.expand_select, a1,c1,c1,frame_m6])
        #self.add_can_change_hight_component([self.expand_select,a1,8,frame_m5,8,10,frame_m6])


    def flash_expand_pack_list(self) :
        while not self.main_win.user_manager.info_update : time.sleep(0.33)
        user_manager:app_function.user_manager = self.main_win.user_manager
        self.expand_select.delete(0,tkinter.END)

        if ("app_info" in user_manager.save_data["online_get"] and \
            "expand_pack_info" in user_manager.save_data["online_get"]["app_info"]) : 
            for uid,pack_info in user_manager.save_data["online_get"]["app_info"]["expand_pack_info"].items() :
                self.expand_pack_list[uid] = pack_info

        for uid,pack_info in self.expand_pack_list.items() :
            if uid in user_manager.save_data["install_pack_list"]:
                self.expand_select.insert(tkinter.END, "[\u2714]%s" % pack_info["pack_name"])
            else: self.expand_select.insert(tkinter.END, pack_info["pack_name"])

    def get_selecting_expand(self):
        # 获取当前选择拓展包的uuid
        select = self.expand_select.curselection()
        if len(select) == 0 : return None
        return list(self.expand_pack_list)[select[0]]

    def on_expand_install(self):
        uid = self.get_selecting_expand()
        if uid is None : return None
        # 判断是否是原版拓展
        if uid == list(self.expand_pack_list)[0] :
            aaa = tkinter.messagebox.askquestion('Title', '如果你是首次安装\n请保持软件处于前台模式\n安装时间需要大约2分钟\n\n部分拓展包无需原版拓展！！', )
            if aaa != "yes" : return None 
            func = self.vanilla_expand_install
        else : func = self.thirdparty_expand_install
        threading.Thread(target = lambda: func(uid)).start()

    def vanilla_expand_install(self, uid:str):
        self.is_installing = True
        user_manager:app_function.user_manager = self.main_win.user_manager
        msg_box = tk_tool.tk_Msgbox(self.main_win.window, self.main_win.window)
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        msg_laber = tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(10))
        msg_laber.pack()
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        module = self.expand_pack_list[uid]["import"]

        def installing() :
            for index,element in enumerate(module) :
                msg_laber.config(text=msg_laber.cget("text") + ("正在安装 %s...\n" % element))
                m1 = subprocess.getstatusoutput("pip install %s" % element)
                if not m1[0] : continue
                FileOperation.write_a_file(os.path.join("log","install_pack.txt"),m1[1])
                tkinter.messagebox.showerror("Error", "模块 %s 安装失败\n日志 install_pack.txt 已保存")
                return None

            msg_laber.config(text=msg_laber.cget("text") + "正在下载材质图片...\n")
            a = connent_API.request_url_without_error(connent_API.BLOCK_TEXTURE_DOWNLOAD)
            if not a : tkinter.messagebox.showerror("Error", "材质图片下载失败") ; return None
            FileOperation.write_a_file(os.path.join("html_output","picture","block_texture.png"),a,"wb")

            try : import brotli
            except : tkinter.messagebox.showerror("Error", "原版拓展安装失败")
            else : msg_laber.config(text=msg_laber.cget("text") + "原版拓展安装成功")
            user_manager.save_data["install_pack_list"][uid] = None
            self.flash_expand_pack_list()
            return True

        if installing() : time.sleep(2)
        self.is_installing = False
        msg_box.destroy()

    def thirdparty_expand_install(self, uid:str):
        # 第三方包（非默认包）
        self.is_installing = True
        user_manager:app_function.user_manager = self.main_win.user_manager
        msg_box = tk_tool.tk_Msgbox(self.main_win.window, self.main_win.window)
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        msg_laber = tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(10))
        msg_laber.pack()
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        name1 = self.expand_pack_list[uid]['pack_name']
        module = self.expand_pack_list[uid]["import"]
        dir_name = self.expand_pack_list[uid]["dir_name"]

        def installing() :
            data1 = {"userdata":user_manager.get_account(), 'expand_pack_uuid':uid}
            if data1["userdata"] == None : tkinter.messagebox.showerror("Error","用户需要登录才能下载") ; return None

            if connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL) != None : 
                msg_laber.config(text=msg_laber.cget("text") + "正在获取安装包...(1/3)\n")
            else : tkinter.messagebox.showerror("Error","网络连接验证失败") ; return None 

            response1 = connent_API.request_url_without_error(connent_API.UPDATE_EXPAND_PACK, data1, 
            user_manager.save_data['cookies']["api_web_cookie"])
            if response1 == None : tkinter.messagebox.showerror("Error","网络异常-1") ; return None
            user_manager.save_data['cookies']["api_web_cookie"] = connent_API.request_headers["cookie"]

            json1 = json.loads(response1)
            if 'stat_code' in json1 and json1['stat_code'] > 0 : tkinter.messagebox.showerror("Error",json1['msg']) ; return None
            elif 'stat_code' not in json1 :tkinter.messagebox.showerror("Error","网络下送数据异常-1") ; return None
            elif 'url' not in json1 : tkinter.messagebox.showerror("Error","网络下送数据异常-2") ; return None

            save_path = os.path.join("expand_pack", dir_name, "saves.zip")
            msg_laber.config(text=msg_laber.cget("text") + "正在下载安装包...(2/3)\n")
            response2 = connent_API.request_url_without_error(json1['url'])
            if response2 == None : tkinter.messagebox.showerror("Error",'获取文件失败，请重试') ; return None
            os.makedirs(os.path.join("expand_pack", dir_name), exist_ok=True)
            FileOperation.write_a_file(save_path, response2, "wb")

            if uid not in self.expand_pack_list : 
                tkinter.messagebox.showerror("Error","安装失败\n未收录的拓展包") ; os.remove(save_path) ; return None
            if 'crc32' not in self.expand_pack_list[uid] : 
                tkinter.messagebox.showerror("Error","安装失败\n拓展包无法校验") ; os.remove(save_path) ; return None
            if self.expand_pack_list[uid]['crc32'] != zlib.crc32(FileOperation.read_a_file(save_path, "readbyte")) : 
                tkinter.messagebox.showerror("Error","安装失败\n拓展包校验未通过") ; os.remove(save_path) ; return None

            if len(self.expand_pack_list[uid]['import']) : msg_laber.config(text=msg_laber.cget("text") + "正在下载依赖库...(3/3)\n")
            for iii in self.expand_pack_list[uid]['import'] :
                msg_laber.config(text=msg_laber.cget("text") + "正在安装 %s ...\n" % iii)
                m1 = subprocess.getstatusoutput("pip3 install " + iii)
                if not m1[0] : continue
                FileOperation.write_a_file(os.path.join("log","install_pack.txt"),m1[1])
                tkinter.messagebox.showerror("Error","依赖库 %s 安装失败\n日志 install_pack.txt 已保存" % iii)
                return None
            
            msg_laber.config(text=msg_laber.cget("text") + ("%s 安装成功" % name1))
            user_manager.save_data["install_pack_list"][uid] = None
            self.flash_expand_pack_list()
            return True

        if installing() : time.sleep(2)
        self.is_installing = False
        msg_box.destroy()


    def on_expand_enable(self, reload1:bool) :
        uid = self.get_selecting_expand()
        user_manager:app_function.user_manager = self.main_win.user_manager
        if uid is None : return None
        if uid == list(self.expand_pack_list)[0] :
            tkinter.messagebox.showerror("Error","原版拓展 并不是拓展包\n请选择其他拓展包运行") ; return None

        name1 = self.expand_pack_list[uid]['pack_name']
        dir_name = self.expand_pack_list[uid]["dir_name"]
        save_path = os.path.join("expand_pack", dir_name, "saves.zip")

        if uid not in user_manager.save_data["install_pack_list"]:
            tkinter.messagebox.showerror("Error", name1 + " 拓展包\n还未安装") ; return None
        if (not app_constant.debug_testing) and (self.expand_pack_list[uid]['crc32'] != zlib.crc32(FileOperation.read_a_file(save_path, "readbyte"))) :
            aaa = tkinter.messagebox.askquestion("Update", name1 + "拓展包\n检测到有新版本\n是否进行更新?",)
            if aaa == "yes" : self.on_expand_install() ; return None

        self.enable_expand(uid, reload1)

    def enable_expand(self, uid:str, reload1:bool):
        # 检查已安装
        name1 = self.expand_pack_list[uid]["pack_name"]
        user_manager:app_function.user_manager = self.main_win.user_manager
        expand_pack_open_list:Dict[str,Dict[Literal["frame","module","object"],
            Union[tkinter.Frame,types.ModuleType,object]]] = self.main_win.expand_pack_open_list
        if uid not in user_manager.save_data["install_pack_list"] : 
            tkinter.messagebox.showerror("Error", "%s 拓展包\n你还未安装" % name1)

        def _expand_error(err) : # 与Python解析拓展包有关错误
            traceback.print_exc(file=open(os.path.join("log","enable_expand.txt"), "w+",encoding="utf-8"))
            tkinter.messagebox.showerror("Error", "%s\n拓展包加载出错，日志已保存" % name1)

        dir_name = self.expand_pack_list[uid]["dir_name"]
        save_path1 = os.path.join("expand_pack", dir_name, "saves.zip")
        save_path2 = os.path.join("expand_pack", dir_name)
        if not app_constant.debug_testing :
            try : 
                with zipfile.ZipFile(save_path1,"r") as zip_file1 : zip_file1.extractall(save_path2)
            except Exception as err: _expand_error(err) ; return

        def reload_module(base_module:types.ModuleType) :
            pack_path = os.path.dirname(base_module.__file__)
            for keys in list(sys.modules.keys()) :
                if not hasattr(sys.modules[keys],"__file__") : continue
                if sys.modules[keys].__file__ == None : continue
                if base_module.__file__ == sys.modules[keys].__file__ : continue
                if pack_path in sys.modules[keys].__file__ : importlib.reload(sys.modules[keys])

        # 加载拓展包主文件main.py
        if uid not in expand_pack_open_list or reload1 :
            main_path = os.path.join("expand_pack", dir_name, "main.py")
            if not os.path.exists(main_path): tkinter.messagebox.showerror("Error", "%s\n拓展包未找到入口文件" % name1) ; return
            spec = importlib.util.spec_from_file_location("<expand %r>" % name1, main_path)
            module = importlib.util.module_from_spec(spec)
            try : spec.loader.exec_module(module)
            except Exception as err: _expand_error(err) ; return

        # 读取main.py
        try :
            if uid not in expand_pack_open_list or reload1 :
                if uid in expand_pack_open_list and hasattr(expand_pack_open_list[uid]['object'],"reload_method") : 
                    expand_pack_open_list[uid]['object'].reload_method()
                reload_module(module) #重载拓展包模块
                expand_pack_open_list[uid] = {}
                expand_pack_open_list[uid]["dir_name"] = dir_name
                expand_pack_open_list[uid]["frame"] = tkinter.Frame(self.main_win.window)
                expand_pack_open_list[uid]['module'] = module
                expand_pack_open_list[uid]['object'] = module.pack_class()
                module.UI_set(self.main_win, expand_pack_open_list[uid]["frame"])
            if hasattr(expand_pack_open_list[uid]['module'], "Menu_set") : 
                expand_pack_open_list[uid]['module'].Menu_set(tkinter.Menu())
        except Exception as err: 
            _expand_error(err)
            if uid in expand_pack_open_list : del expand_pack_open_list[uid]
        else :
            self.main_win.display_frame["expand_pack"] = expand_pack_open_list[uid]["frame"]
            class event :
                x = self.main_win.button_bar.bbox(self.main_win.button_bar.menu_list[2])[0]
                y = self.main_win.button_bar.bbox(self.main_win.button_bar.menu_list[2])[1]
            self.main_win.button_bar.update_menu_text(event())

class Expand_Pack_Example(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win

        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=6).pack()
        tkinter.Label(self, text="该界面为拓展包的\n功能界面", bg='#6b6b6b', fg='white', font=tk_tool.get_default_font(12),
            width=20, height=2).pack()


class Setting(tkinter.Frame) :
    
    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win


        tkinter.Label(self,text="联网功能",fg='black',font=tk_tool.get_default_font(18),width=15,height=1).pack()
        frame_0 = tkinter.Frame(self)
        tkinter.Button(frame_0,text='用户登录',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,command=
            lambda:self.main_win.user_was_login()).pack(side=tkinter.LEFT)
        tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).pack(side=tkinter.LEFT)
        tkinter.Button(frame_0,text='官方网站',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,command=
            lambda:webbrowser.open("https://commandsimulator.great-site.net")).pack(side=tkinter.LEFT)
        frame_0.pack()

        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()

        tkinter.Label(self,text="软件帮助",fg='black',font=tk_tool.get_default_font(18),width=15,height=1).pack()
        frame_0 = tkinter.Frame(self)
        tkinter.Button(frame_0,text='帮助文档',font=tk_tool.get_default_font(12), bg='#D369a9', width=9, height=1,
            command = lambda : webbrowser.open("http://localhost:32323")).grid(row=0,column=0)
        tkinter.Label(frame_0,font=tk_tool.get_default_font(10),width=1,height=1).grid(row=0,column=1)
        tkinter.Button(frame_0,text='常见问题',font=tk_tool.get_default_font(12),bg='#D369a9' ,width=9, height=1,
            command = lambda : webbrowser.open("https://missing254.github.io/cs-tool/tool/Question/")).grid(row=0,column=2)
        frame_0.pack()
            
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()

        tkinter.Label(self,text="软件信息",fg='black',font=tk_tool.get_default_font(18),width=15,height=1).pack()
        frame_0 = tkinter.Frame(self)
        tkinter.Button(frame_0,text='使用许可',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,
            command = lambda:main_win.app_infomation("use")).grid(row=0,column=0)
        tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).grid(row=0,column=1)
        tkinter.Button(frame_0,text='隐私政策',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,
            command = lambda:main_win.app_infomation("privacy")).grid(row=0,column=2)
        tkinter.Label(frame_0, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).grid(row=1,column=0)
        tkinter.Button(frame_0,text='关于软件',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,
            command = lambda:main_win.app_infomation("about")).grid(row=2,column=0)
        tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).grid(row=2,column=1)
        tkinter.Button(frame_0,text='启动日志',font=tk_tool.get_default_font(12),bg='orange' ,width=9, height=1,
            command = lambda:main_win.app_infomation("open")).grid(row=2,column=2)
        frame_0.pack()

        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()

        tkinter.Label(self,text="联系作者",fg='black',font=tk_tool.get_default_font(18),width=15,height=1).pack()
        frame_0 = tkinter.Frame(self)
        tkinter.Button(frame_0,text='提供赞助',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,command=
            lambda:webbrowser.open("https://afdian.net/u/3c2e5dc43fd111edb9c052540025c377")).pack(side=tkinter.LEFT)
        tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).pack(side=tkinter.LEFT)
        tkinter.Button(frame_0,text='交流群',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,command=
            lambda:webbrowser.open("https://missing254.github.io/cs-tool/qq_group.html")).pack(side=tkinter.LEFT)
        frame_0.pack()

class Login(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.in_login = False

        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()
        tkinter.Label(self, text="请在下框输入账号", fg='black', font=tk_tool.get_default_font(12), width=28, height=1).pack()
        self.account_input_1 = tkinter.Entry(self,font=tk_tool.get_default_font(10),width=26)
        self.account_input_1.pack()
        self.account_input_1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()
        tkinter.Label(self, text="请在下框输入通行码", fg='black', font=tk_tool.get_default_font(12), width=28, height=1).pack()
        self.account_input_2 = tkinter.Entry(self,font=tk_tool.get_default_font(10),width=26)
        self.account_input_2.pack()
        self.account_input_2.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()
        tkinter.Button(self,text='登      录',font=tk_tool.get_default_font(12),bg='#70db93' ,width=12, height=1,
            command=lambda:self.user_login()).pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()
        tkinter.Label(self, text="如果你没有账号\n请点击下方按钮注册", fg='black', font=tk_tool.get_default_font(12), width=28, height=2).pack()
        tkinter.Button(self,text='用户注册',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=17, height=1,
            command=lambda:webbrowser.open("https://commandsimulator.great-site.net/register.html")).pack()
        tkinter.Label(self, text="如果你需要通行码\n请点击下方按钮申领", fg='black', font=tk_tool.get_default_font(12), width=28, height=2).pack()
        tkinter.Button(self,text='申领注册码',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=17, height=1,
            command=lambda:webbrowser.open("https://commandsimulator.great-site.net/forgot_pass.html")).pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()
        tkinter.Button(self,text='返      回',font=tk_tool.get_default_font(12),bg='#d19275' ,width=17, height=1,
            command=lambda:self.main_win.set_display_frame('setting_frame')).pack()

    def user_login(self) :
        threading.Thread(target=self.user_send_login).start()

    def user_send_login(self) : 

        def start_login() :            
            login_info_1 = {"account":self.account_input_1.get(), "pass_code":self.account_input_2.get()}
            login_info_2 = base64.b64encode(json.dumps(login_info_1).encode("utf-8")).decode("utf-8")

            if connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL) == None :
                msg_laber.config(text=msg_laber.cget("text") + "网络连接验证失败\n") ; return None 

            response2 = connent_API.request_url_without_error(connent_API.MANUAL_LOGIN,{"userdata":login_info_2},user_manager.save_data['cookies']["api_web_cookie"])
            result1 = user_manager.login_account(login_info_1['account'],login_info_1['pass_code'],response2.decode("utf-8") if response2 != None else "")
            if result1 : 
                user_manager.save_data['cookies']["api_web_cookie"] = connent_API.request_headers["cookie"]
                msg_laber.config(text=msg_laber.cget("text") + "登录成功") ; user_manager.write_back() ; return True
            else : msg_laber.config(text=msg_laber.cget("text") + "登录失败")

        if re.search("^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$",self.account_input_1.get()) == None :
            tkinter.messagebox.showerror("Error","用户邮箱格式不正确") ; return None
        if re.search("^[a-zA-Z0-9]+$",self.account_input_2.get()) == None  :
            tkinter.messagebox.showerror("Error","用户通行码格式不正确") ; return None

        user_manager:app_function.user_manager = self.main_win.user_manager
        msg_box = tk_tool.tk_Msgbox(self.main_win.window, self.main_win.window)
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        msg_laber = tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(10))
        msg_laber.pack()
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        self.in_login = True
        msg_laber.config(text=msg_laber.cget("text") + "正在登录...\n")
        if start_login() : 
            self.main_win.user_was_login()
        self.in_login = False
        time.sleep(1.5)
        msg_box.destroy()

class User_Info(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        user_manager:app_function.user_manager = self.main_win.user_manager

        tkinter.Label(self, text="用 户 信 息", bg='#82aaff',fg='black',font=tk_tool.get_default_font(18), width=15, height=1).pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=2).pack()
        tkinter.Label(self, text="账户", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left").pack()
        self.user_info_1 = tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left")
        self.user_info_1.pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=2).pack()
        tkinter.Label(self, text="创建日期", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left").pack()
        self.user_info_2 = tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left")
        self.user_info_2.pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=2).pack()
        tkinter.Label(self, text="支付点数", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left").pack()
        self.user_info_3 = tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left")
        self.user_info_3.pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=2).pack()
        tkinter.Label(self, text="挑战完成次数", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left").pack()
        self.user_info_4 = tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(12), width=22, height=1, justify="left")
        self.user_info_4.pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=2).pack()
        tkinter.Button(self,text='登出账户',font=tk_tool.get_default_font(12),bg='#db7093' ,width=17, height=1,command=
            lambda:[user_manager.login_out_account(),main_win.user_was_login()]).pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=2).pack()
        tkinter.Button(self,text='返      回',font=tk_tool.get_default_font(12),bg='#d19275' ,width=17, height=1,command=
            lambda:self.main_win.set_display_frame('setting_frame')).pack()

class Policy(tkinter.Frame) :
    
    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win

        self.policy_title = tkinter.Label(self, text="",bg="#d98719",fg="white",font=tk_tool.get_default_font(12), width=21, height=1)
        self.policy_title.pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.input_box4 = tkinter.Text(frame_m10,show=None,height=22,width=25,font=tk_tool.get_default_font(11),yscrollcommand=sco1.set)
        self.input_box4.grid()
        sco1.config(command=self.input_box4.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()
        a2 = tkinter.Button(self,text='返      回', font=tk_tool.get_default_font(12), bg='#d19275', width=17, height=1,
            command=lambda:self.main_win.set_display_frame('setting_frame'))
        a2.pack()

        main_win.add_can_change_hight_component([self.input_box4, self.policy_title,a2])
        #self.add_can_change_hight_component([self.input_box4,a1,frame_m3,a2])

