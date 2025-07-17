import tkinter,tkinter.messagebox,webbrowser,re,json,os,traceback,pickle,base64
import copy,random,threading,time,gc,zlib,subprocess,sys,types,importlib.util,zipfile
from typing import Any,Literal,Union,Dict,Tuple,List,Callable
import tkinter.ttk as ttk

import main_source.main_window.function as app_function
import main_source.main_window.constant as app_constant

import package.tk_tool as tk_tool
import package.file_operation as FileOperation
import package.connent_API as connent_API

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
        if response2 is None : 
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
        text_id_1 = self.create_text(20, 20, text="模拟", font=tk_tool.get_default_font(14, weight="bold"), fill="white")
        self.coords(text_id_1, int(canvas_width*0.315), canvas_height//2)
        text_id_2 = self.create_text(20, 20, text="拓展", font=tk_tool.get_default_font(14, weight="bold"), fill="white")
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
            if text_id_1 == self.menu_list[0] : self.main_win.set_display_frame('welcome_screen')
            elif text_id_1 == self.menu_list[1] : self.main_win.game_ready_or_run()
            elif text_id_1 == self.menu_list[2] : self.main_win.set_display_frame('choose_expand')
            elif text_id_1 == self.menu_list[3] : self.main_win.set_display_frame('setting_frame')
            elif text_id_1 == self.menu_list[4] : self.Menu.post(e.x_root, e.y_root-self.Menu.winfo_reqheight())
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
        self.add_command(label='清空',command=lambda : self.mode_using("clear_all"))
        self.add_separator()
        self.add_command(label='行首',command=lambda : self.mode_using("jump_line_start"))
        self.add_command(label='行尾',command=lambda : self.mode_using("jump_line_end"))
        self.add_command(label='选行',command=lambda : self.mode_using("line_select"))
        self.add_separator()
        if app_constant.jnius : self.add_command(label='键盘',command=lambda : self.mode_using("weakup_keyboard"))
        self.add_command(label='退出',command=lambda : self.exit())

    def mode_using(self, mode) :
        focus_input = self.main_win.focus_input
        app_function.mode_using(self.main_win, focus_input, mode)

    def exit(self) :
        user_manager:app_function.user_manager = self.main_win.user_manager
        aaa = tkinter.messagebox.askquestion("Question","是否退出本软件？？")
        if aaa == "yes" : 
            threading.Thread(target=lambda:[time.sleep(10), os._exit(0)]).start()
            game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
            if game_process is not None :
                text = self.main_win.display_frame["game_run"].input_box1.get("0.0","end")[:-1]
                game_process.world_infomation['terminal_command'] = text
                game_process.__exit_world__()
            time.sleep(0.5) ; os._exit(0)

class Global_Right_Click_Menu(tk_tool.tk_Menu) :

    def __init__(self, master, **karg) -> None:
        super().__init__(master, tearoff=False, font=tk_tool.get_default_font(10), **karg)


class Welcome_Screen(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(6)).pack()
        tkinter.Label(self, text="命令模拟器", fg='black', font=tk_tool.get_default_font(25), width=15, height=1).pack()
        tkinter.Label(self,height=2,text="         ",font=tk_tool.get_default_font(6)).pack()
        
        tkinter.Button(self,text='开始命令模拟',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=self.main_win.game_ready_or_run).pack(side="top")
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Button(self,text='查询游戏内ID',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("find_minecraft_ID")).pack(side="top")
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Button(self,text='复制特殊字符',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("special_char")).pack(side="top")
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Button(self,text='批量复制字符',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("unicode_char")).pack(side="top")
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Button(self,text='结构文件转换',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("structure_transfor")).pack(side="top")
        if self.main_win.platform == "android" or app_constant.debug_testing :
            tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
            tkinter.Button(self,text='复制文件命令',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("copy_file_command")).pack(side="top")
        tkinter.Label(self,height=2,text="         ",font=tk_tool.get_default_font(8)).pack()

        frame_m4 = tkinter.Frame(self)
        tkinter.Button(frame_m4,text='使用须知',font=tk_tool.get_default_font(11),bg='#D369a9',width=8,height=1,
        command=lambda:webbrowser.open("http://localhost:32323/tutorial/Instructions.html")).pack(side='left')
        tkinter.Label(frame_m4, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m4,text='常见问题',font=tk_tool.get_default_font(11),bg='#D369a9',width=8,height=1,
        command=lambda:webbrowser.open("https://commandsimulator.great-site.net/tool/Question/")).pack(side='left')
        frame_m4.pack()
        tkinter.Label(self, text="新用户一定要阅读 使用须知\n安卓用户一定要阅读 常见问题", font=tk_tool.get_default_font(10), height=2, fg="red").pack()

class Special_Char(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.display_id = 0
        self.mode_id = "ByteCode"
        self.image_list:List[tkinter.PhotoImage] = []

        icon_zip_file = zipfile.ZipFile(os.path.join("main_source","app_source","icon.zip"), "r")
        icon_list = icon_zip_file.namelist()
        
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(6)).pack()
        frame_icon = tk_tool.ScrollableFrame(self)
        frame_icon.canvas.config(width=self.main_win.window.winfo_reqwidth()*92//100, 
            height=self.main_win.window.winfo_reqheight()*70//100)
        for index, photo_name in enumerate(icon_list) :
            photo = tkinter.PhotoImage(master=frame_icon, data=icon_zip_file.open(photo_name).read())
            if self.main_win.platform == "android" : photo = photo.zoom(4, 4)
            label = tkinter.Label(frame_icon.scrollable_frame, image=photo)
            label.file_name=photo_name.replace(".gif", "").lower()
            label.grid(row=index//4, column=index%4)
            label.bind('<Button-1>', lambda event : self.mode_effect(event))
            self.image_list.append(photo)
            if self.main_win.platform == "android" : self.image_list[-1].zoom(4, 4)
        frame_icon.pack()

        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        self.label1 = tkinter.Label(self,width=25,height=1,text="点击上方图标即可直接复制",font=tk_tool.get_default_font(9))
        self.label1.pack(side=tkinter.TOP)
        frame_button = tkinter.Frame(self)
        self.buttom1 = tkinter.Button(frame_button,width=11,height=1,text="复制源字符",bg="#b4f0c8",font=tk_tool.get_default_font(9),
            command=lambda : self.mode_change("ByteCode"), state=tkinter.DISABLED)
        self.buttom1.pack(side=tkinter.LEFT)
        self.buttom2 = tkinter.Button(frame_button,width=11,height=1,text="复制Unicode",bg="#b4f0c8",font=tk_tool.get_default_font(9),
            command=lambda : self.mode_change("Unicode"))
        self.buttom2.pack(side=tkinter.LEFT)
        frame_button.pack(side=tkinter.TOP)
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(8)).pack()
        tkinter.Button(self,height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()

    def mode_change(self, mode:Literal["ByteCode", "Unicode"]) : 
        self.mode_id = mode
        if self.mode_id == "ByteCode" : self.buttom1.config(state=tkinter.DISABLED)
        else : self.buttom1.config(state=tkinter.NORMAL)
        if self.mode_id == "Unicode" : self.buttom2.config(state=tkinter.DISABLED)
        else : self.buttom2.config(state=tkinter.NORMAL)

    def mode_effect(self, event:tkinter.Event) :
        word_id = event.widget.file_name
        if self.mode_id == "ByteCode" :
            tk_tool.copy_to_clipboard(chr(int(word_id, 16)))
            self.label1.config(text="元字符%s已存入剪切板" % word_id)
        if self.mode_id == "Unicode" : 
            tk_tool.copy_to_clipboard("\\u" + word_id)
            self.label1.config(text="Unicode字符%s已存入剪切板" % word_id)

class Unicode_Char(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.test_str1 = re.compile("^\\\\u[a-fA-F0-9]{4}$")
        self.test_str2 = re.compile("^\\\\u[a-fA-F0-9]{4}~\\\\u[a-fA-F0-9]{4}$")

        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()
        self.Unicode_collect = tkinter.Text(self, height=6, width=28, font=tk_tool.get_default_font(10))
        self.Unicode_collect.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        self.Unicode_collect.bind("<<Modified>>",lambda a : self.get_str(True))
        self.Unicode_collect.pack()
        self.Unicode_collect.tag_config("red", background='red')
        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()

        frame_m3 = tkinter.Frame(self)
        tkinter.Button(frame_m3,text='批量复制',font=tk_tool.get_default_font(10),bg='aquamarine',width=10,height=1,command=self.get_str).pack(side='left')
        tkinter.Label(frame_m3, text="    ", fg='black',font=tk_tool.get_default_font(6), height=1).pack(side='left')
        tkinter.Button(frame_m3,text='查询字符',font=tk_tool.get_default_font(10),bg='aquamarine',width=10,height=1,
            command=lambda:webbrowser.open("https://commandsimulator.great-site.net/tool/Unicode/page_1.html")).pack(side='left')
        frame_m3.pack()

        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        self.label1 = tkinter.Label(self, text="请使用\\uXXXX或\n\\uXXXX~\\uXXXX格式填写\nXXXX为4位16进制，可多行",fg='black',
            font=tk_tool.get_default_font(10), width=22, height=3)
        self.label1.pack()

        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()
        self.Unicode_Render = tk_tool.tk_Scrollbar_Text(self, True, False, height=6, width=26, font=tk_tool.get_default_font(10))
        self.Unicode_Render.input_box.insert("0.0", "预览窗口，等待输入...")
        self.Unicode_Render.input_box.config(state="disabled")
        self.Unicode_Render.pack()

        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(8)).pack()
        tkinter.Button(self,height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()

    def check_syntax(self) :
        self.Unicode_collect.edit_modified(False)
        self.Unicode_collect.tag_remove("red", "0.0", tkinter.END)
        text1 = self.Unicode_collect.get("0.0",tkinter.END)[:-1].split("\n")
        list1 = [bool(self.test_str1.search(i) or self.test_str2.search(i)) for i in text1]
        if (False in list1) : 
            i = list1.index(False)
            self.Unicode_Render.input_box.config(state="normal")
            self.Unicode_Render.input_box.delete("0.0", "end")
            self.Unicode_Render.input_box.insert("0.0", "第%s行格式错误"%(i+1,))
            self.Unicode_Render.input_box.config(state="disabled")
            self.Unicode_collect.see("%s.%s"%(i+1,len(text1[i])))
            self.Unicode_collect.tag_add("red","%s.0"%(i+1,),"%s.%s"%(i+1,len(text1[i])))
            return False
        return True

    def get_str(self, only_check=False) : 
        text1 = self.Unicode_collect.get("0.0",tkinter.END)[:-1].split("\n")
        if not self.check_syntax() : return None

        copy_text_list = []
        for i in text1 :
            if self.test_str1.search(i) : copy_text_list.append(chr(int("0x" + i.replace("\\u",""),16)))
            elif self.test_str2.search(i) :
                text2 = i.split("~")
                start1,end1 = int("0x" + text2[0].replace("\\u",""),16) , int("0x" + text2[1].replace("\\u",""),16)
                while start1 <= end1 : copy_text_list.append(chr(start1)) ; start1 += 1
        
        self.Unicode_Render.input_box.config(state="normal")
        self.Unicode_Render.input_box.delete("0.0", "end")
        if only_check :
            self.Unicode_Render.input_box.insert("0.0", "".join(copy_text_list))
        else : 
            tk_tool.copy_to_clipboard("".join(copy_text_list))
            self.Unicode_Render.input_box.insert("0.0", "Unicode字符已全部存入剪切板")
        self.Unicode_Render.input_box.config(state="disabled")

class Find_Minecraft_ID(tkinter.Frame) :

    class search_id_object :
        
        def __init__(self) -> None:
            try : self.MC_ID = json.load(fp=open(os.path.join('main_source','update_source','import_files','translate'),"r",encoding="utf-8"))
            except : self.MC_ID = {} ; traceback.print_exc()
        
        def search_str(self, condition_str:str, is_regx=False, search_setting:Dict[str,bool]={}) :
            if condition_str.replace(" ","") == "" : return []
            if not is_regx : condition_str = "".join( [("\\u" + hex(ord(i)).replace("0x","0000")[-4:]) for i in condition_str] )
            
            try: 
                if is_regx and re.compile(condition_str).search("") : return None
            except : return None
            compile_re = re.compile(condition_str)

            result_list = []
            self.search_result = {}
            for key1, value1 in self.MC_ID.items() :
                if not search_setting.get("全部", False) and not search_setting.get(key1[1:][:-1], False) : continue
                result_list += [ "%s%s" % (key1, chinese)
                    for english, chinese in value1.items()
                    if compile_re.search(chinese) ]
                self.search_result.update({"%s%s" % (key1, chinese):english for english, chinese in value1.items()
                    if compile_re.search(chinese)})

            return result_list
    
    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.search_translate_id = self.search_id_object()
        self.search_object = ['全部', '物品', '方块', '实体', '群系', '伤害', '药效', '附魔', '槽位', '迷雾', '规则', '结构', '掉落', '声音']

        self.search_setting:Dict[str, tkinter.BooleanVar] = {}
        for item in self.search_object : self.search_setting[item] = tkinter.BooleanVar(self, False)
        self.search_setting['全部'].set(True)

        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        frame_m10 = tkinter.Frame(self)
        self.search_collect = search_collect = tkinter.Entry(frame_m10, width=18, font=tk_tool.get_default_font(11))
        search_collect.event_add("<<update-status>>", "<KeyRelease>", "<ButtonRelease-1>")
        search_collect.bind("<<update-status>>", lambda a : self.search())
        search_collect.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        search_collect.pack(side='left')
        self.use_regx = tkinter.BooleanVar(self, False)
        tkinter.Checkbutton(frame_m10,text='正则',font=tk_tool.get_default_font(10),variable=self.use_regx,
            onvalue=True,offvalue=False, height=1,command=self.search).pack(side='left')
        frame_m10.pack()
        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()

        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
        self.search_result = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(10),selectmode=tkinter.SINGLE,
            height=16,width=26,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
        self.search_result.grid(row=0,column=0)
        sco1.config(command=self.search_result.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.config(command=self.search_result.xview)
        sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
        self.search_result.bind("<Double-Button-1>",lambda e : self.copy())
        tkinter.Button(frame_m10,height=1,text="S",font=tk_tool.get_default_font(6),bg="aqua",
            command=lambda:self.setting()).grid(row=1,column=1)
        frame_m10.pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(1), width=15, height=1).pack()

        self.label1 = tkinter.Label(self, text="双击项目复制，点击浅蓝色按钮设置",fg='black',font=tk_tool.get_default_font(10), width=27, height=1)
        self.label1.pack()

        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()
        tkinter.Button(self,height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()

    def setting(self) :
        toplevel = tkinter.Toplevel(self.main_win.window)
        toplevel.resizable(False, False)
        toplevel.transient(self.master)
        toplevel.grab_set()
        toplevel.title('Setting')
        for index, item in enumerate(self.search_object) : 
            tkinter.Checkbutton(toplevel, text=item,font=tk_tool.get_default_font(10), variable=self.search_setting[item],
            onvalue=True,offvalue=False, height=1,command=self.search).grid(row=index//4, column=index%4)
        display_x = self.master.winfo_x() + (self.master.winfo_width() - toplevel.winfo_reqwidth()) // (
            6 if self.main_win.platform == "android" else 3)
        display_y = self.master.winfo_y() + (self.master.winfo_height() - toplevel.winfo_reqheight()) // 2
        toplevel.geometry("+%s+%s" % (display_x, display_y))

    def search(self) :
        dict1 = {i:j.get() for i,j in self.search_setting.items()}
        if dict1["全部"] and list(dict1.values()).count(True) > 1 : 
            self.search_setting["全部"].set(False)
            dict1["全部"] = False
        list1 = self.search_translate_id.search_str(self.search_collect.get(), self.use_regx.get(), dict1)
        if list1 is None : self.label1.config(text = "正则表达式格式错误") ; return None
        self.search_result.delete(0, tkinter.END)
        self.search_result.insert(tkinter.END, *list1)
        if len(list1) : self.label1.config(text = "搜索成功")

    def copy(self) :
        if len(self.search_result.curselection()) == 0 : self.label1.config(text = "没有选择需要复制的ID") ; return
        select_item = self.search_result.get(self.search_result.curselection()[0])
        tk_tool.copy_to_clipboard(self.search_translate_id.search_result[select_item])
        self.label1.config(text = "ID 复制完成")

class Copy_File_Command(tkinter.Frame) :
    base_path = os.path.join("functionality", "command")
    file_list_hash = -1

    def __loop__(self) :
        if self.main_win.now_display_frame != "copy_file_command" : return None

        file_list = []
        path1 = os.path.join(self.base_path, "")
        for i in [i for i in FileOperation.file_in_path(path1) if self.check_name(i)] : 
            file_list.append( i.replace(path1, "", 1) )
        
        file_list_hash = sum( hash(i) for i in file_list )
        if file_list_hash == self.file_list_hash : return None
        self.search_result.delete(0, tkinter.END)
        for i in file_list : self.search_result.insert(tkinter.END, i)
        self.file_list_hash = file_list_hash
        

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.read_file_data = self.read_saves()

        tkinter.Label(self, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
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
        self.label1 = tkinter.Label(open_frame, fg='black',font=tk_tool.get_default_font(10), width=26, height=6,
            text="双击项目打开文件\n点击文本框复制，绿色为复制成功\n\n该功能适用于安卓小窗模式\n请将mc函数或文本文件放入\nfunctionality/command文件夹下")
        self.label1.pack()
        tkinter.Label(open_frame,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()
        tkinter.Button(open_frame,height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()
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
        
        self.bind("<Unmap>", lambda e: self.save_saves())

    
    def read_saves(self) -> dict :
        save_path = os.path.join(self.base_path, "saves.pick")
        if not os.path.exists(save_path) or not os.path.isfile(save_path) : return {}
        else : 
            with open(save_path, 'rb') as f : a = pickle.load(f)
            return a
                
    def save_saves(self) :
        if not hasattr(self, "save_hash") : self.save_hash = -1
        hash1 = json.dumps(self.read_file_data).__hash__()
        save_path = os.path.join(self.base_path, "saves.pick")
        if hash1 == self.save_hash : return None
        with open(save_path, 'wb') as f: pickle.dump(self.read_file_data, f)
        self.save_hash = hash1

    def open_file(self) :
        if len(self.search_result.curselection()) == 0 : self.label1.config(text = "你没有选择需要打开的文件") ; return None
        path1 = self.search_result.get(self.search_result.curselection())
        try : f = open(os.path.join(self.base_path, path1),"r",encoding="utf-8")
        except : self.label1.config(text = "文件打开失败") ; traceback.print_exc() ; return None
        else : 
            content_1 = f.read() ; f.close()
            if path1 not in self.read_file_data : self.read_file_data[path1] = {"lines" : 1}
            self.file_content = [i for i in content_1.split("\n") if len(i.replace(" ",""))]
            self.file_name = path1
            self.open_frame.pack_forget() ; self.copy_frame.pack()
            self.find_command(add_value = 0)

    def check_name(self, file_name:str) :
        if re.search(".txt$|.mcfunction$",file_name) is None : return False
        try : open(file_name,"r",encoding="utf-8").close()
        except : return False
        else : return True

    def find_command(self, set_value = None , add_value = None) :
        try :
            if set_value is not None and int(set_value) : pass
            if add_value is not None and int(add_value) : pass
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

class BE_Structure_Transfor(tkinter.Frame) :
    base_path = os.path.join("functionality", "BE_Structure")
    file_list_hash = -1

    def __loop__(self) :
        if self.main_win.now_display_frame != "structure_transfor" : return None

        file_list = []
        path1 = os.path.join(self.base_path, "")
        for i in [i for i in os.listdir(path1) if os.path.isfile( os.path.join(path1, i) )] : 
            file_list.append( i.replace(path1, "", 1) )
        
        file_list_hash = sum( hash(i) for i in file_list )
        if file_list_hash == self.file_list_hash : return None
        self.search_result.delete(0, tkinter.END)
        for i in file_list : self.search_result.insert(tkinter.END, i)
        self.file_list_hash = file_list_hash

    def __init__(self, main_win, **karg) -> None :
        from package.MCStructureManage import Codecs

        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.codecs = {
            "请选择转换格式": None,
            "bdx文件": (".bdx", Codecs.BDX), "mcstructure文件": (".mcstructure", Codecs.MCSTRUCTURE), 
            "MianYang_V1 Json文件": (".json", Codecs.MIANYANG_V1), "MianYang_V2 Json文件": (".json", Codecs.MIANYANG_V2), 
            "MianYang_V3 building文件（最新）": (".building", Codecs.MIANYANG_V3),
            "GangBan_V1 Json文件": (".json", Codecs.GANGBAN_V1), "GangBan_V2 Json文件": (".json", Codecs.GANGBAN_V2), 
            "GangBan_V3 Json文件": (".json", Codecs.GANGBAN_V3), "GangBan_V4 Json文件": (".json", Codecs.GANGBAN_V4), 
            "GangBan_V5 Json文件": (".json", Codecs.GANGBAN_V5), "GangBan_V6 Json文件": (".json", Codecs.GANGBAN_V6), 
            "GangBan_V7 reb文件（最新）": (".reb", Codecs.GANGBAN_V7), 
            "RunAway Json文件": (".json", Codecs.RUNAWAY), "万花筒 Kbdx文件": (".kbdx", Codecs.KBDX),
            "FuHong_V3 Json文件": (".json", Codecs.FUHONG_V3), "FuHong_V4 Json文件": (".json", Codecs.FUHONG_V4), 
            "FuHong_V5 fhbuild文件（最新）": (".fhbuild", Codecs.FUHONG_V5), 
            "QingXu_V1 Json文件": (".json", Codecs.QINGXU_V1), 
            "MC函数 Zip文件": (".zip", Codecs.FunctionCommand), "MC命令 Txt文件": (".txt", Codecs.TextCommand)}

        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(6)).pack()

        MainScreen = tkinter.Frame(self) 
        MainScreen.pack()
        frame_m10 = tkinter.Frame(MainScreen)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
        self.search_result = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(10),selectmode=tkinter.SINGLE,
            height=10,width=26,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
        self.search_result.grid(row=0,column=0)
        sco1.config(command=self.search_result.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.config(command=self.search_result.xview)
        sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
        frame_m10.pack()

        tkinter.Label(MainScreen, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        self.transfor_choose = ttk.Combobox(MainScreen, font=tk_tool.get_default_font(11), width=22, state='readonly', justify='center')
        self.transfor_choose["value"] = list( i for i,j in self.codecs.items() )
        self.transfor_choose.current(0)
        self.transfor_choose.pack()
        
        tkinter.Label(MainScreen, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        frame_m4 = tkinter.Frame(MainScreen)
        tkinter.Button(frame_m4, height=1,text=" 阅读使用须知 ",font=tk_tool.get_default_font(10), bg="#fdd142",
            command=lambda:[FeedbackScreen.pack(), MainScreen.pack_forget(), self.add_tips()]).pack(side='left')
        tkinter.Label(frame_m4, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m4, height=1,text=" 开始转换文件 ",font=tk_tool.get_default_font(10), bg="#9ae9d1",
            command=lambda:[FeedbackScreen.pack(), MainScreen.pack_forget(), self.start_thread()]).pack(side='left')
        frame_m4.pack()

        tkinter.Label(MainScreen, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        tkinter.Label(MainScreen, text="请将需要转换的结构文件放入\nfunctionality/BE_Structure文件夹下\n文件将生成在该目录下的result文件夹内",
            fg='black', font=tk_tool.get_default_font(10)).pack()
        
        tkinter.Label(MainScreen, height=1,text="         ",font=tk_tool.get_default_font(8)).pack()
        tkinter.Button(MainScreen, height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()
        

        FeedbackScreen = tkinter.Frame(self) 
        frame_m10 = tkinter.Frame(FeedbackScreen)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.input_box = tkinter.Text(frame_m10,show=None,height=20,width=25,font=tk_tool.get_default_font(11),yscrollcommand=sco1.set)
        self.input_box.grid()
        sco1.config(command=self.input_box.yview)
        sco1.grid(row=0,column=1, sticky=tkinter.N+tkinter.S)
        frame_m10.pack()

        tkinter.Label(FeedbackScreen, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
        self.back_button = tkinter.Button(FeedbackScreen, height=1,text=" 返回上一页 ",font=tk_tool.get_default_font(13), bg="#9ae9d1",
            command=lambda:[FeedbackScreen.pack_forget(), MainScreen.pack()])
        self.back_button.pack()


    def start_thread(self) :
        threading.Thread(target=self.transfor_file).start()

    def transfor_file(self) :
        from package.MCStructureManage import CommonStructure

        self.input_box.delete("0.0", tkinter.END)
        if self.transfor_choose.current() < 1 : 
            self.input_box.insert(tkinter.END, "转换格式选择不正确\n请重新选择")
            return None
        if not self.search_result.get(0, tkinter.END) : 
            self.input_box.insert(tkinter.END, "没有任何文件被转换\n请确认是否放入文件")
            return None

        self.back_button.config(state=tkinter.DISABLED)
        file_name_list = self.search_result.get(0, tkinter.END)
        file_type_re = re.compile("\\.[0-9a-zA-Z]{0,}$")
        choose_trans_mode = self.codecs[self.transfor_choose.get()]
        for index, file_name in enumerate(file_name_list, start=1) :
            self.input_box.insert(tkinter.END, "正在转换 %s/%s 文件...\n%s\n" % (index, len(file_name_list), file_name))
            self.input_box.see(tkinter.END)
            time.sleep(0.3)

            file_path = os.path.join( self.base_path, file_name )
            try : Struct1 = CommonStructure.from_buffer(file_path)
            except Exception as e : 
                self.input_box.insert( tkinter.END, e.args[0] + "\n\n" )
                self.input_box.see(tkinter.END)
                continue
            end_name = file_type_re.search(file_name)
            save_file_name = (file_name+choose_trans_mode[0]) if end_name is None else (file_name[:end_name.start()]+choose_trans_mode[0])
            save_file_path = os.path.join( self.base_path, "result", save_file_name )
            Struct1.save_as(save_file_path, choose_trans_mode[1])
            self.input_box.insert(tkinter.END, "文件转换完成 (%s/%s)\n\n" % (index, len(file_name_list)))
            self.input_box.see(tkinter.END)
        
        self.back_button.config(state=tkinter.NORMAL)

    def add_tips(self) :
        from package.MCStructureManage import Codecs
        self.input_box.delete("0.0", tkinter.END)

        Tips = [
            "本工具支持读取的文件：",
            "bdx  mcstructure  schematic",
            "schem  跑路json  万花筒kbdx",
            "绵阳Json  绵阳building",
            "钢板Json  钢板reb",
            "浮鸿Json  浮鸿fhbuild",
            "情绪json",
            "",
            "",
            "",
            "如果发现有文件无法被读取，且确定是结构文件，可以点击",
            "",
            "设置-联系作者-交流群",
            "",
            "在交流群中与作者进行技术交流，litematic文件暂时不会支持"
        ]
        self.input_box.insert(tkinter.END, "\n".join(Tips))





class Game_Ready(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        a1 = tkinter.Label(self, text="模拟世界存档", bg='#82aaff',fg='black',font=tk_tool.get_default_font(20), width=15, height=1)
        a1.pack()

        c1 = tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)) ; c1.pack()
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        self.list_select = tkinter.Listbox(self,font=tk_tool.get_default_font(13), selectmode=tkinter.SINGLE, height=16, width=22)
        self.list_select.bind("<Double-ButtonRelease-1>", lambda e : self.join_world())
        self.list_select.pack()
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()

        frame_m3 = tkinter.Frame(self)
        tkinter.Button(frame_m3,text='新建',font=tk_tool.get_default_font(11),bg='aquamarine',width=5,height=1,command=self.create_world).pack(side='left')
        tkinter.Label(frame_m3, text="   ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m3,text='删除',font=tk_tool.get_default_font(11),bg='aquamarine',width=5,height=1,command=self.delete_world).pack(side='left')
        tkinter.Label(frame_m3, text="   ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m3,text='进入',font=tk_tool.get_default_font(11),bg='aquamarine',width=5,height=1,command=self.join_world).pack(side='left')
        frame_m3.pack()

        main_win.add_can_change_hight_component([self.list_select, a1,c1,c1,c1,frame_m3])
        self.flash_world()

    def create_world(self) :
        self.main_win.set_display_frame("creat_world")

    def delete_world(self):
        if len(self.list_select.curselection()) == 0 : return
        text1 = self.list_select.get(self.list_select.curselection()).split("-->")[1]
        aaa = tkinter.messagebox.askquestion('Question', '第1次确认\n是否删除选择的世界？\n所有文件都将会被删除!!!')
        if aaa != "yes" : return
        aaa = tkinter.messagebox.askquestion('Question', '第2次确认\n是否删除选择的世界？\n所有文件都将会被删除!!!')
        if aaa != "yes" : return
        tkinter.messagebox.showinfo("Success", "世界 %s \n已成功删除" % text1)
        FileOperation.delete_all_file(os.path.join('save_world', text1))
        self.flash_world()

    def join_world(self):
        import main_source.main_window.constant as app_constants
        if any([i.is_alive() for i in self.main_win.initialization_process]) :
            tkinter.messagebox.showerror("Error", "正在加载软件,请稍后....") ; return None

        if len(self.list_select.curselection()) == 0 : return None
        game_process = Minecraft_BE.RunTime.minecraft_thread()
        world_name = self.list_select.get(self.list_select.curselection()).split("-->")[1]
        func1 = self.main_win.display_frame["game_run"].set_gametime
        func2 = self.main_win.set_error_log
        aaa = game_process.__game_loading__(world_name, func1, func2)
        if isinstance(aaa, Warning) : tkinter.messagebox.showwarning("Warning", aaa.args[0])
        elif isinstance(aaa, Exception) : func2(*aaa.args) ; return None
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
            self.main_win.set_error_log(
                "创建世界错误\n日志 create_world.txt 已保存", 
                traceback.format_exc())
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

        frame_m9 = tkinter.Frame(self)
        self.world_gt = tkinter.Label(frame_m9, bg='green',fg='white',font=tk_tool.get_default_font(12), width=12, height=1)
        self.focus_pos = tkinter.Label(frame_m9, text="0, 0", fg='black',font=tk_tool.get_default_font(12), width=9, height=1)
        self.world_gt.grid(row=0,column=0)
        self.focus_pos.grid(row=0,column=1)
        frame_m9.pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.input_box1 = tkinter.Text(frame_m10,show=None,height=22,width=28,font=tk_tool.get_default_font(10),
            yscrollcommand=sco1.set,undo=True)
        self.input_box1.grid()
        self.input_box1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
        self.input_box1.bind("<ButtonRelease-1>", self.set_focus_pos, add="+")
        self.input_box1.bind("<KeyRelease>", self.set_focus_pos, add="+")
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

        main_win.add_can_change_hight_component([self.input_box1, c1, frame_m9, c1, frame_m4])

    def join_world(self) : 
        def aaaa(_game:Minecraft_BE.RunTime.minecraft_thread, Terminal = self.input_box1) :
            Terminal.tag_remove("syntax_error", "1.0",'end')
            for feedback in _game.runtime_variable.terminal_command_feedback :
                if isinstance(feedback, tuple) : 
                    Terminal.tag_add("syntax_error", "%s.%s" % (feedback[0],feedback[2]), "%s.end" % feedback[0])
        Minecraft_BE.GameLoop.modify_termial_end_hook("add",aaaa)

        game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
        self.input_box1.delete("1.0",'end')
        while game_process.world_infomation is None : pass
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

    def exit_world(self) :
        game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
        game_process.world_infomation['terminal_command'] = self.input_box1.get("0.0","end")[:-1]

        self.main_win.game_process = None
        self.main_win.game_ready_or_run()
        threading.Thread(target=lambda:[time.sleep(4), gc.collect()]).start()

        aaa = game_process.__exit_world__()
        if isinstance(aaa, Warning) : tkinter.messagebox.showwarning("Warning", aaa.args[0])
        elif isinstance(aaa, Exception) : self.main_win.set_error_log(*aaa.args)


    def send_command(self) :
        game_process:Minecraft_BE.RunTime.minecraft_thread = self.main_win.game_process
        game_process.runtime_variable.terminal_command = self.input_box1.get("1.0", tkinter.END)
        #exec(self.input_box1.get("1.0",'end'),globals(),locals())
        game_process.runtime_variable.terminal_send_command = True
        self.display_terminal()
        self.main_win.display_frame["game_terminal"].clear_terminal()

    def display_terminal(self) : 
        self.main_win.set_display_frame("game_terminal")

    def set_focus_pos(self, e) :
        row,clo = self.input_box1.index(tkinter.INSERT).split(".")
        self.focus_pos.config(text="%s, %s" % (row,clo))

    def set_gametime(self, time:int) :
        self.world_gt.config(text="%s刻" % time)

class Game_Terminal(tkinter.Frame) :
    
    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win

        tkinter.Label(self,text="",fg='black',font=tk_tool.get_default_font(3),width=15,height=1).pack()

        self.test_time = c0 = tkinter.Label(self, text="终端执行返回界面",bg="green",fg="white",font=tk_tool.get_default_font(12), width=21, height=1)
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

        def print_gt(_game:Minecraft_BE.RunTime.minecraft_thread, Terminal = self.test_time) :
            left_time = _game.runtime_variable.how_times_run_all_command
            if _game.runtime_variable.how_times_run_all_command > 0 : Terminal.config(text="测试剩余 %s 刻" % left_time)
            elif _game.runtime_variable.how_times_run_all_command == 0 : Terminal.config(text="终端执行返回界面")
        Minecraft_BE.GameLoop.modify_tick_end_hook("add", print_gt)

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
        self.expand_pack_list = {}
        self.is_installing = False #正在安装拓展包

        a1 = tkinter.Label(self,text="拓展包管理",bg='#82aaff',fg='black',font=tk_tool.get_default_font(20),width=15,height=1)
        a1.pack()
        c1 = tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)) ; c1.pack()
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()

        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.expand_select = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(12),selectmode=tkinter.SINGLE,
            height=17,width=23,yscrollcommand=sco1.set)
        self.expand_select.bind("<Double-ButtonRelease-1>", lambda e : self.on_expand_enable(False))
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
        main_win.add_can_change_hight_component([self.expand_select, a1,c1,c1,c1,frame_m6])
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
        func = self.thirdparty_expand_install
        threading.Thread(target = lambda: func(uid)).start()

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
        builtin_module = self.expand_pack_list[uid].get("builtin_module", [])

        def installing() :
            data1 = {"userdata":user_manager.get_account(), 'expand_pack_uuid':uid}
            if data1["userdata"] is None : tkinter.messagebox.showerror("Error","用户需要登录才能下载") ; return None

            if connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL) is not None : 
                msg_laber.config(text=msg_laber.cget("text") + "正在获取安装包...(1/3)\n")
            else : tkinter.messagebox.showerror("Error","网络连接验证失败") ; return None 

            response1 = connent_API.request_url_without_error(connent_API.UPDATE_EXPAND_PACK, data1, 
            user_manager.save_data['cookies']["api_web_cookie"])
            if response1 is None : tkinter.messagebox.showerror("Error","网络异常-1") ; return None
            user_manager.save_data['cookies']["api_web_cookie"] = connent_API.request_headers["cookie"]

            json1 = json.loads(response1)
            if 'state_code' in json1 and json1['state_code'] > 0 : tkinter.messagebox.showerror("Error",json1['msg']) ; return None
            elif 'state_code' not in json1 :tkinter.messagebox.showerror("Error","网络下送数据异常-1") ; return None
            elif 'url' not in json1 : tkinter.messagebox.showerror("Error","网络下送数据异常-2") ; return None

            save_path = os.path.join("expand_pack", dir_name, "saves.zip")
            msg_laber.config(text=msg_laber.cget("text") + "正在下载安装包...(2/3)\n")
            response2 = connent_API.request_url_without_error(json1['url'], timeout_s=4)
            if response2 is None : tkinter.messagebox.showerror("Error",'获取文件失败，请重试') ; return None
            os.makedirs(os.path.join("expand_pack", dir_name), exist_ok=True)
            FileOperation.write_a_file(save_path, response2, "wb")

            if uid not in self.expand_pack_list : 
                tkinter.messagebox.showerror("Error","安装失败\n未收录的拓展包") ; os.remove(save_path) ; return None
            if 'crc32' not in self.expand_pack_list[uid] : 
                tkinter.messagebox.showerror("Error","安装失败\n拓展包无法校验") ; os.remove(save_path) ; return None
            if self.expand_pack_list[uid]['crc32'] != zlib.crc32(response2) : 
                tkinter.messagebox.showerror("Error","安装失败\n拓展包校验未通过") ; os.remove(save_path) ; return None

            try :
                for index, m_name in enumerate(builtin_module) : exec("import %s" % m_name, {}, {})
            except : 
                for index, iii in enumerate(module) :
                    if index == 0 : msg_laber.config(text=msg_laber.cget("text") + "正在下载依赖库...(3/3)\n")
                    msg_laber.config(text=msg_laber.cget("text") + "正在安装 %s ...\n" % iii)
                    m1 = subprocess.getstatusoutput("pip3 install " + iii)
                    if not m1[0] : continue
                    self.main_win.set_error_log("模块 %s 安装失败\n日志 install_pack.txt 已保存" % iii, m1[1])
                    return None

            msg_laber.config(text=msg_laber.cget("text") + ("%s 安装成功" % name1))
            user_manager.save_data["install_pack_list"][uid] = None
            user_manager.write_back()
            self.flash_expand_pack_list()
            return True

        if installing() : time.sleep(2)
        self.is_installing = False
        msg_box.destroy()


    def on_expand_enable(self, reload1:bool) :
        uid = self.get_selecting_expand()
        user_manager:app_function.user_manager = self.main_win.user_manager
        if uid is None : return None

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
            self.main_win.set_error_log(
                "%s\n拓展包加载出错，日志已保存" % name1, 
                traceback.format_exc()
            )

        dir_name = self.expand_pack_list[uid]["dir_name"]
        save_path1 = os.path.join("expand_pack", dir_name, "saves.zip")
        save_path2 = os.path.join("expand_pack", dir_name)
        if not app_constant.debug_testing :
            try : 
                with zipfile.ZipFile(save_path1, "r") as zip_file1 : zip_file1.extractall(save_path2)
            except Exception as err: _expand_error(err) ; return

        def reload_module(base_module:types.ModuleType) :
            pack_path = os.path.dirname(base_module.__file__)
            for keys in list(sys.modules.keys()) :
                if not hasattr(sys.modules[keys], "__file__") : continue
                if sys.modules[keys].__file__ is None : continue
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
                if "frame" in expand_pack_open_list.get(uid, {}) : expand_pack_open_list[uid]["frame"].destroy()
                expand_pack_open_list[uid] = {}
                expand_pack_open_list[uid]["dir_name"] = dir_name
                expand_pack_open_list[uid]["frame"] = tkinter.Frame(self.main_win.window)
                expand_pack_open_list[uid]['module'] = module
                expand_pack_open_list[uid]['object'] = module.pack_class()
                module.UI_set(self.main_win, expand_pack_open_list[uid]["frame"])
        except Exception as err: 
            _expand_error(err)
            if uid in expand_pack_open_list : del expand_pack_open_list[uid]
        else :
            self.main_win.display_frame["expand_pack"] = expand_pack_open_list[uid]["frame"]
            self.main_win.set_display_frame("expand_pack")
            for i in self.main_win.button_bar.menu_list[0:4] : self.main_win.button_bar.itemconfig(i, fill="white")


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
            command = lambda:webbrowser.open("http://localhost:32323")).grid(row=0,column=0)
        tkinter.Label(frame_0,font=tk_tool.get_default_font(10),width=1,height=1).grid(row=0,column=1)
        tkinter.Button(frame_0,text='常见问题',font=tk_tool.get_default_font(12),bg='#D369a9' ,width=9, height=1,
            command = lambda:webbrowser.open("https://commandsimulator.great-site.net/tool/Question/")).grid(row=0,column=2)
        if main_win.platform == 'android' :
            tkinter.Label(frame_0, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).grid(row=1,column=0)
            tkinter.Button(frame_0,text='新手须知',font=tk_tool.get_default_font(12),bg='#D369a9' ,width=9, height=1,
                command = lambda:app_function.Beginner_Tutorial(self.main_win)).grid(row=2,column=0)
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
            lambda:webbrowser.open("https://afdian.com/a/commandsimulator")).pack(side=tkinter.LEFT)
        tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).pack(side=tkinter.LEFT)
        tkinter.Button(frame_0,text='交流群',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,command=
            lambda:webbrowser.open("https://commandsimulator.great-site.net/qq_group.html")).pack(side=tkinter.LEFT)
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
        tkinter.Label(self, text="请在下框输入密码", fg='black', font=tk_tool.get_default_font(12), width=28, height=1).pack()
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
        tkinter.Label(self, text="如果你忘记密码\n请点击下方按钮申领", fg='black', font=tk_tool.get_default_font(12), width=28, height=2).pack()
        tkinter.Button(self,text='重置密码',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=17, height=1,
            command=lambda:webbrowser.open("https://commandsimulator.great-site.net/forgot.html")).pack()
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()
        tkinter.Button(self,text='返      回',font=tk_tool.get_default_font(12),bg='#d19275' ,width=17, height=1,
            command=lambda:self.main_win.set_display_frame('setting_frame')).pack()

    def user_login(self) :
        threading.Thread(target=self.user_send_login).start()

    def user_send_login(self) : 

        def start_login() :            
            login_info_1 = {"account":self.account_input_1.get(), "password":self.account_input_2.get()}
            login_info_2 = base64.b64encode(json.dumps(login_info_1).encode("utf-8")).decode("utf-8")

            if connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL) is None :
                msg_laber.config(text=msg_laber.cget("text") + "网络连接验证失败\n") ; return None 

            response2 = connent_API.request_url_without_error(connent_API.MANUAL_LOGIN, {"userdata":login_info_2}, user_manager.save_data['cookies']["api_web_cookie"])
            result1 = user_manager.login_account(login_info_1['account'],login_info_1['password'],response2.decode("utf-8") if response2 is not None else "")
            if result1 : 
                user_manager.save_data['cookies']["api_web_cookie"] = connent_API.request_headers["cookie"]
                msg_laber.config(text=msg_laber.cget("text") + "登录成功") ; return True
            else : msg_laber.config(text=msg_laber.cget("text") + "登录失败")

        if re.search(r"^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$",self.account_input_1.get()) is None :
            tkinter.messagebox.showerror("Error","用户邮箱格式不正确") ; return None
        if re.search("^[a-zA-Z0-9]+$",self.account_input_2.get()) is None  :
            tkinter.messagebox.showerror("Error","用户密码格式不正确") ; return None

        user_manager:app_function.user_manager = self.main_win.user_manager
        msg_box = tk_tool.tk_Msgbox(self.main_win.window, self.main_win.window)
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        msg_laber = tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(10))
        msg_laber.pack()
        tkinter.Label(msg_box, text="", fg='black', font=tk_tool.get_default_font(3), height=1).pack()
        self.in_login = True
        msg_laber.config(text=msg_laber.cget("text") + "正在登录...\n")
        if start_login() : self.main_win.user_was_login()
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
        self.notes = tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(13),fg="red")
        self.notes.pack()

        main_win.add_can_change_hight_component([self.input_box4, self.policy_title,a2])
        #self.add_can_change_hight_component([self.input_box4,a1,frame_m3,a2])


class Log_Display(tkinter.Frame) :
    
    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.last_frame_name = None

        self.log_title = tkinter.Label(self, bg="#d98719",fg="white",font=tk_tool.get_default_font(12), width=21, height=1)
        self.log_title.config(text="后台日志信息")
        self.log_title.pack()
        frame_m10 = tkinter.Frame(self)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient='horizontal')
        self.input_box4 = tkinter.Text(frame_m10,height=21,width=25,font=tk_tool.get_default_font(10),
            yscrollcommand=sco1.set, xscrollcommand=sco2.set, wrap="none")
        self.input_box4.grid()
        sco1.config(command=self.input_box4.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.config(command=self.input_box4.xview)
        sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
        frame_m10.pack()

        frame_0 = tkinter.Frame(self)
        tkinter.Button(frame_0,text='返回界面',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,command=
            self.back_to_frame).pack(side=tkinter.LEFT)
        tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).pack(side=tkinter.LEFT)
        tkinter.Button(frame_0,text='复制日志',font=tk_tool.get_default_font(12),bg='#66ccff' ,width=9, height=1,command=
            self.copy_clipboard).pack(side=tkinter.LEFT)
        frame_0.pack()

        main_win.add_can_change_hight_component([self.input_box4, sco2, self.log_title, frame_0])

    def set_log(self, error_msg:str, log:str, save_path:str=None) :
        self.last_frame_name = self.main_win.now_display_frame
        self.input_box4.insert("end", error_msg+"\n")
        self.input_box4.insert("end", log)
        self.input_box4.insert("end", "\n\n\n")
        self.main_win.set_display_frame("log_display")
        tkinter.messagebox.showerror("Error", error_msg)


    def back_to_frame(self) :
        self.main_win.set_display_frame(self.last_frame_name)
    
    def copy_clipboard(self) :
        tk_tool.copy_to_clipboard(self.input_box4.get("0.0", "end")[:-1])




