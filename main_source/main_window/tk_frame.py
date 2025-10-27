import tkinter,tkinter.messagebox,webbrowser,re,json,os,traceback,pickle,base64,itertools
import copy,random,threading,time,gc,zlib,subprocess,sys,types,importlib.util,zipfile,shutil
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
        text_id_0 = self.create_text(20, 20, text="主页", font=tk_tool.get_default_font(14, weight="bold"), fill="#00ff00")
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
        tkinter.Button(self,text='MC游戏ID查询',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("find_minecraft_ID")).pack(side="top")
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Button(self,text='MC字符查找器',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("copy_char_tool")).pack(side="top")
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Button(self,text='结构转换工具',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("structure_transfor")).pack(side="top")
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
        tkinter.Button(self,text='存档读取工具',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("mcworld_reader")).pack(side="top")
        if self.main_win.platform == "android" or app_constant.debug_testing :
            tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
            tkinter.Button(self,text='复制文件命令',font=tk_tool.get_default_font(13),bg='#66ccff',width=16,height=1,
            command=lambda:self.main_win.set_display_frame("copy_file_command")).pack(side="top")
        tkinter.Label(self,height=2,text="         ",font=tk_tool.get_default_font(7)).pack()

        frame_m4 = tkinter.Frame(self)
        tkinter.Button(frame_m4,text='使用须知',font=tk_tool.get_default_font(11),bg='#D369a9',width=8,height=1,
        command=lambda:webbrowser.open("http://localhost:32323/tutorial/Instructions.html")).pack(side='left')
        tkinter.Label(frame_m4, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
        tkinter.Button(frame_m4,text='常见问题',font=tk_tool.get_default_font(11),bg='#D369a9',width=8,height=1,
        command=lambda:webbrowser.open("https://commandsimulator.great-site.net/tool/Question/")).pack(side='left')
        frame_m4.pack()
        tkinter.Label(self, text="新用户一定要阅读 使用须知\n安卓用户一定要阅读 常见问题", font=tk_tool.get_default_font(10), height=2, fg="red").pack()

class Copy_Char_Tool(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.display_id = 0
        self.mode_id = "ByteCode"
        self.image_list:List[tkinter.PhotoImage] = []

        icon_zip_file = zipfile.ZipFile(os.path.join("main_source","app_source","icon.zip"), "r")
        icon_list = icon_zip_file.namelist()
        
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()
        frame_m0 = tkinter.Frame(self) ; frame_m0.pack()
        tkinter.Button(frame_m0, height=1,text=" 特殊字符 ",bg="#e9ff46",font=tk_tool.get_default_font(10),
            command=lambda: [frame_special_char.pack(), frame_normal_char.pack_forget(), 
            frame_back_button.pack_forget(), frame_back_button.pack()]).grid(row=0, column=0)
        tkinter.Label(frame_m0, text="      ",font=tk_tool.get_default_font(10)).grid(row=0, column=1)
        tkinter.Button(frame_m0, height=1,text=" 普通字符 ",bg="#e9ff46",font=tk_tool.get_default_font(10),
            command=lambda: [frame_special_char.pack_forget(), frame_normal_char.pack(),
            frame_back_button.pack_forget(), frame_back_button.pack()]).grid(row=0, column=2)
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()

        if 1 :
            frame_special_char = tkinter.Frame(self) ; frame_special_char.pack()
            frame_icon = tk_tool.ScrollableFrame(frame_special_char)
            frame_icon.canvas.config(width=self.main_win.window.winfo_reqwidth()*92//100, 
                height=self.main_win.window.winfo_reqheight()*60//100)
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

            tkinter.Label(frame_special_char,height=1,text="         ",font=tk_tool.get_default_font(4)).pack()
            self.label1 = tkinter.Label(frame_special_char,width=25,height=1,text="点击上方图标即可直接复制",font=tk_tool.get_default_font(9))
            self.label1.pack(side=tkinter.TOP)
            frame_button = tkinter.Frame(frame_special_char)
            self.buttom1 = tkinter.Button(frame_button,width=11,height=1,text="复制源字符",bg="#b4f0c8",font=tk_tool.get_default_font(9),
                command=lambda : self.mode_change("ByteCode"), state=tkinter.DISABLED)
            self.buttom1.pack(side=tkinter.LEFT)
            self.buttom2 = tkinter.Button(frame_button,width=11,height=1,text="复制Unicode",bg="#b4f0c8",font=tk_tool.get_default_font(9),
                command=lambda : self.mode_change("Unicode"))
            self.buttom2.pack(side=tkinter.LEFT)
            frame_button.pack(side=tkinter.TOP)

        if 1 :
            self.test_str1 = re.compile("^\\\\u[a-fA-F0-9]{4}$")
            self.test_str2 = re.compile("^\\\\u[a-fA-F0-9]{4}~\\\\u[a-fA-F0-9]{4}$")

            frame_normal_char = tkinter.Frame(self)
            self.Unicode_collect = tkinter.Text(frame_normal_char, height=6, width=28, font=tk_tool.get_default_font(10))
            self.Unicode_collect.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
            self.Unicode_collect.bind("<<Modified>>",lambda a : self.get_str(True))
            self.Unicode_collect.pack()
            self.Unicode_collect.tag_config("red", background='red')
            tkinter.Label(frame_normal_char, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()

            frame_m3 = tkinter.Frame(frame_normal_char)
            tkinter.Button(frame_m3,text='批量复制',font=tk_tool.get_default_font(10),bg='aquamarine',width=10,height=1,command=self.get_str).pack(side='left')
            tkinter.Label(frame_m3, text="    ", fg='black',font=tk_tool.get_default_font(6), height=1).pack(side='left')
            tkinter.Button(frame_m3,text='查询字符',font=tk_tool.get_default_font(10),bg='aquamarine',width=10,height=1,
                command=lambda:webbrowser.open("https://commandsimulator.great-site.net/tool/Unicode/page_1.html")).pack(side='left')
            frame_m3.pack()

            tkinter.Label(frame_normal_char, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
            self.label2 = tkinter.Label(frame_normal_char, text="请使用\\uXXXX或\n\\uXXXX~\\uXXXX格式填写\nXXXX为4位16进制，可多行",fg='black',
                font=tk_tool.get_default_font(10), width=22, height=3)
            self.label2.pack()

            tkinter.Label(frame_normal_char, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()
            self.Unicode_Render = tk_tool.tk_Scrollbar_Text(frame_normal_char, True, False, height=6, width=26, font=tk_tool.get_default_font(10))
            self.Unicode_Render.input_box.insert("0.0", "预览窗口，等待输入...")
            self.Unicode_Render.input_box.config(state="disabled")
            self.Unicode_Render.pack()

        frame_back_button = tkinter.Frame(self) ; frame_back_button.pack()
        tkinter.Label(frame_back_button,height=1,text="         ",font=tk_tool.get_default_font(8)).pack()
        tkinter.Button(frame_back_button,height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
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
            self.label1.config(text="源字符%s已存入剪切板" % word_id)
        if self.mode_id == "Unicode" : 
            tk_tool.copy_to_clipboard("\\u" + word_id)
            self.label1.config(text="Unicode字符%s已存入剪切板" % word_id)

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
            try : self.MC_ID = json.load(fp=open(os.path.join('main_source','update_source',
                'import_files','translate'), "r", encoding="utf-8"))
            except : self.MC_ID = {} ; traceback.print_exc()
        
        def search_str(self, condition_str:str, is_regx=False, search_setting:Dict[str,bool]={}) :
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

        self.label1 = tkinter.Label(self, text="双击项目复制，点击浅蓝色按钮设置",fg='black',
            font=tk_tool.get_default_font(10), width=28, height=1)
        self.label1.pack()

        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()
        tkinter.Button(self,height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()
        self.search()
        self.label1.config(text = "双击项目复制，点击浅蓝色按钮设置")

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
    base_path = os.path.join("functionality", "Command_Text")
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
        self.label1 = tkinter.Label(open_frame, fg='black',font=tk_tool.get_default_font(10), width=26, height=7,
            text="双击项目打开文件\n点击文本框复制，绿色为复制成功\n\n该功能适用于安卓小窗模式\n请将mc函数或文本文件放入\nfunctionality/Command_Text\n文件夹下")
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

class BE_Structure_Tool(tkinter.Frame) :
    base_path = os.path.join("functionality", "BE_Structure")
    android_outside_storage = "/storage/emulated/0/Documents/Pydroid3/Command_Simulator/BE_Structure"

    def __loop__(self) :
        if self.main_win.now_display_frame != "structure_transfor" : return None

        file_list = {}
        inside_path = os.path.join(self.base_path, "")
        for i in os.listdir(inside_path) : 
            real_path = os.path.join(inside_path, i)
            if not os.path.isfile(real_path) : continue
            file_name = i.replace(inside_path, "", 1) + "(内部)"
            file_list[file_name] = {"real_path":real_path, "real_name":i, "outside":False}
        
        if self.main_win.platform == "android" :
            try :
                outside_path = os.path.join(self.android_outside_storage, "")
                for i in os.listdir(outside_path) : 
                    real_path = os.path.join(outside_path, i)
                    if not os.path.isfile(real_path)  : continue
                    file_name = i.replace(outside_path, "", 1) + "(外部)"
                    file_list[file_name] = {"real_path":real_path, "real_name":i, "outside":True}
            except : pass

        if set(file_list) == set(self.file_list) : return None
        self.search_result.delete(0, tkinter.END)
        for i in file_list : self.search_result.insert(tkinter.END, i)
        self.file_list = file_list

    @staticmethod
    def __get_codecs__() :
        from package.MCBEWorld import World
        from package.MCStructureManage import Codecs
        return {
            "请选择文件格式": None,
            "mcworld 存档文件夹": ("", World),
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
            "TimeBuilder_V1 Json文件": (".json", Codecs.TIMEBUILDER_V1), 
            "MC函数 Zip文件": (".zip", Codecs.FunctionCommand), "MC命令 Txt文件": (".txt", Codecs.TextCommand)}

    def __init__(self, main_win, **karg) -> None :
        os.makedirs(self.base_path, exist_ok=True)
        if main_win.platform == "android" :
            try : os.makedirs(self.android_outside_storage, exist_ok=True)
            except : pass

        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        self.file_list:Dict[str, Dict[Literal["real_path", "real_name", "outside"], Union[str, bool]]] = {}
        self.can_readFile: bool = True
        self.choose_index: Tuple[int] = ()
        self.enable_split = tkinter.IntVar(main_win.window, 0)
        self.split_size = [99999, 99999, 99999]
        self.merge_page = 0
        self.merge_info: List[Tuple[str, int, int, int]] = []
        self.codecs = self.__get_codecs__()

        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()
        ReadTips = tkinter.Frame(self) 
        ReadTips.pack()
        tkinter.Label(ReadTips, text="初次使用请先阅读",fg='red', font=tk_tool.get_default_font(12)).pack(side='left')
        tkinter.Button(ReadTips, height=1,text=tk_tool.platform_string("使用说明"),font=tk_tool.get_default_font(9), bg="#fdd142",
            command=lambda:[FeedbackScreen.pack(), MainScreen.pack_forget(), SubScreen_3_1.pack_forget(), self.add_tips()]).pack(side='left')
        tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()

        def set_ListBox_focus() :
            for i in self.choose_index : self.search_result.select_set(i)

        if "结构列表" :
            MainScreen = tkinter.Frame(self) 
            MainScreen.pack()
            frame_m10 = tkinter.Frame(MainScreen)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
            self.search_result = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(10),selectmode=tkinter.SINGLE,
                height=9,width=26,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
            self.search_result.bind("<ButtonRelease-1>", self.test_can_readFile)
            self.search_result.grid(row=0,column=0)
            sco1.config(command=self.search_result.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            sco2.config(command=self.search_result.xview)
            sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
            frame_m10.pack()


            def Click_StructureTips() :
                SubScreen_1.pack()
                SubScreen_2.pack_forget()
                SubScreen_3.pack_forget()
                SubScreen_0.pack_forget(), 
                SubScreen_0.pack()
                self.search_result.bind("<ButtonRelease-1>", lambda e:[self.test_can_readFile(e),
                    self.set_choose_index()] )
                self.search_result.config(selectmode=tkinter.SINGLE)
                self.search_result.select_clear(0, "end")
            
            def Click_Transfor() :
                SubScreen_1.pack_forget()
                SubScreen_2.pack()
                SubScreen_3.pack_forget()
                SubScreen_0.pack_forget()
                SubScreen_0.pack()
                self.search_result.bind("<ButtonRelease-1>", lambda e:self.set_choose_index() )
                self.search_result.config(selectmode=tkinter.MULTIPLE)
                self.search_result.select_clear(0, "end")

            def Click_McworldMerge() :
                SubScreen_1.pack_forget()
                SubScreen_2.pack_forget()
                SubScreen_3.pack()
                SubScreen_0.pack_forget()
                SubScreen_0.pack()
                self.search_result.bind("<ButtonRelease-1>", lambda e:self.set_choose_index() )
                self.search_result.config(selectmode=tkinter.MULTIPLE)
                self.search_result.select_clear(0, "end")

            tkinter.Label(MainScreen, text=" ",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()
            frame_m4 = tkinter.Frame(MainScreen)
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("结构详情"),font=tk_tool.get_default_font(10), bg="#9ae9d1",
                command=Click_StructureTips).pack(side='left')
            tkinter.Label(frame_m4, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("转换器"),font=tk_tool.get_default_font(10), bg="#9ae9d1",
                command=Click_Transfor).pack(side='left')
            tkinter.Label(frame_m4, text="  ", font=tk_tool.get_default_font(11), height=1).pack(side='left')
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("合并器"),font=tk_tool.get_default_font(10), bg="#9ae9d1",
                command=Click_McworldMerge).pack(side='left')
            frame_m4.pack()

        if "结构信息UI" :
            SubScreen_1 = tkinter.Frame(MainScreen) 
            SubScreen_1.pack()
            tkinter.Label(SubScreen_1, text="", fg='black',font=tk_tool.get_default_font(5), width=15, height=1).grid(row=0, column=0)
            self.FileInfo1 = tkinter.Label(SubScreen_1, text="文件名：(点击列表中的文件)", fg='black',
                font=tk_tool.get_default_font(10), width=25, height=1, anchor='w')
            self.FileInfo2 = tkinter.Label(SubScreen_1, text="结构大小：", fg='black',font=tk_tool.get_default_font(10), width=25, height=1, anchor='w')
            self.FileInfo3 = tkinter.Label(SubScreen_1, text="结构体积：", fg='black',font=tk_tool.get_default_font(10), width=25, height=1, anchor='w')
            self.FileInfo4 = tkinter.Label(SubScreen_1, text="空气方块数：", fg='black',font=tk_tool.get_default_font(10), width=25, height=1, anchor='w')
            self.FileInfo5 = tkinter.Label(SubScreen_1, text="非空气方块数：", fg='black',font=tk_tool.get_default_font(10), width=25, height=1, anchor='w')
            self.FileInfo6 = tkinter.Label(SubScreen_1, text="方块NBT数：", fg='black',font=tk_tool.get_default_font(10), width=25, height=1, anchor='w')
            self.FileInfo1.grid(row=1, column=0)
            self.FileInfo2.grid(row=2, column=0)
            self.FileInfo3.grid(row=3, column=0)
            self.FileInfo4.grid(row=4, column=0)
            self.FileInfo5.grid(row=5, column=0)
            self.FileInfo6.grid(row=6, column=0)

        def start_trans() :
            self.choose_index = self.search_result.curselection()
            if self.transfor_choose.current() < 1 : 
                tkinter.messagebox.showerror("Error", "转换格式选择不正确\n请重新选择")
                return None
            if not self.choose_index : 
                tkinter.messagebox.showerror("Error", "没有任何文件被转换\n请确认是否选择文件")
                return None
            
            self.input_box.delete("0.0", tkinter.END)
            FeedbackScreen.pack()
            MainScreen.pack_forget()
            self.start_thread_1()

        if "转换选择界面" :
            SubScreen_2 = tkinter.Frame(MainScreen)
            tkinter.Label(SubScreen_2, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            tkinter.Label(SubScreen_2, text="点击列表，选择单个或多个条目",fg="#2756FF", font=tk_tool.get_default_font(10)).pack()
            tkinter.Label(SubScreen_2, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            self.transfor_choose = ttk.Combobox(SubScreen_2, font=tk_tool.get_default_font(11), width=22, state='readonly', justify='center')
            self.transfor_choose.bind("<<ComboboxSelected>>", lambda e:self.transfor_choose.after(10, set_ListBox_focus))
            self.transfor_choose["value"] = list( i for i,j in self.codecs.items() )
            self.transfor_choose.current(0)
            self.transfor_choose.pack()
            tkinter.Label(SubScreen_2, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()
            frame_m4 = tkinter.Frame(SubScreen_2)
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("全选"),font=tk_tool.get_default_font(9), bg="#ff6cf5",
                command=lambda:[self.search_result.select_set(0, "end"), self.search_result.event_generate("<ButtonRelease-1>")]).pack(side='left')
            tkinter.Label(frame_m4, text=" ", font=tk_tool.get_default_font(5), height=1).pack(side='left')
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("清空"),font=tk_tool.get_default_font(9), bg="#ff6cf5",
                command=lambda:[self.search_result.select_clear(0, "end"), self.search_result.event_generate("<ButtonRelease-1>")]).pack(side='left')
            tkinter.Label(frame_m4, text=" ", font=tk_tool.get_default_font(5), height=1).pack(side='left')
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("设置"),font=tk_tool.get_default_font(9), bg="#61eaff",
                command=lambda:self.transfor_setting(tkinter.Toplevel(main_win.window))).pack(side="left")
            tkinter.Label(frame_m4, text=" ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("转换"),font=tk_tool.get_default_font(9), bg="#61eaff",
                command=start_trans).pack(side="left")
            frame_m4.pack()

        if "合并选择界面" :
            def ClickStartMerge() :
                self.choose_index = self.search_result.curselection()
                self.search_result.unbind("<ButtonRelease-1>")
                MainScreen.pack_forget() ; SubScreen_3_1.pack()
                self.merge_ready()

            SubScreen_3 = tkinter.Frame(MainScreen)
            tkinter.Label(SubScreen_3, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            tkinter.Label(SubScreen_3, text="点击列表，选择单个或多个条目\n将选中的结构合并在新建存档内",fg="#2756FF", 
                font=tk_tool.get_default_font(11)).pack()
            tkinter.Label(SubScreen_3, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            self.MergeWorldNameEntry = tkinter.Entry(SubScreen_3, fg='black', font=tk_tool.get_default_font(11), width=24, justify="center")
            self.MergeWorldNameEntry.insert("end", "结构合并存档%s" % ("0000%s" % random.randint(0, 99999))[-5:])
            self.MergeWorldNameEntry.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            self.MergeWorldNameEntry.pack()
            tkinter.Label(SubScreen_3, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            frame_m4 = tkinter.Frame(SubScreen_3)
            tkinter.Button(frame_m4, height=1,text=" 全选 ",font=tk_tool.get_default_font(9), bg="#ff6cf5",
                command=lambda:self.search_result.select_set(0, "end")).pack(side='left')
            tkinter.Label(frame_m4, text=" ", font=tk_tool.get_default_font(5), height=1).pack(side='left')
            tkinter.Button(frame_m4, height=1,text=" 清空 ",font=tk_tool.get_default_font(9), bg="#ff6cf5",
                command=lambda:self.search_result.select_clear(0, "end")).pack(side='left')
            tkinter.Label(frame_m4, text=" ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
            tkinter.Button(frame_m4, height=1,text=" 开始合并 ",font=tk_tool.get_default_font(9), bg="#61eaff",
                command=ClickStartMerge).pack(side="left")
            frame_m4.pack()

        def start_merge() :
            if not self.choose_index : 
                tkinter.messagebox.showerror("Error", "没有任何文件被选中\n请确认是否选择文件")
                return None
            
            self.input_box.delete("0.0", tkinter.END)
            FeedbackScreen.pack()
            SubScreen_3_1.pack_forget()
            MainScreen.pack_forget()
            self.start_thread_2()

        if "放置坐标UI" :
            SubScreen_3_1 = tkinter.Frame(self)

            def merge_entry_input(e:tkinter.Event, pos_index:int) :
                list_index = (self.merge_page - 1) * 6
                sub_index = int(str(e.widget)[-3])
                if not e.widget.get() : return None

                try : int(e.widget.get())
                except :
                    str1 = e.widget.get()
                    e.widget.delete(0, "end")
                    str1 = "".join(i for i in str1 if i in "0123456789")
                    if not str1 : return None
                    e.widget.insert("end", str1)
                    Var = int(str1)
                else : Var = int(e.widget.get())
                if list_index+sub_index >= len(self.merge_info) : return None
                self.merge_info[list_index+sub_index][pos_index] = Var

            InputBoxUI = tkinter.Frame(SubScreen_3_1) ; InputBoxUI.pack()
            self.Merge_UI:List[Tuple[tkinter.Label, tkinter.Entry, tkinter.Entry, tkinter.Entry]] = []
            for index in range(6) :
                Info0 = tkinter.Label(InputBoxUI, text="设置结构放置起点", width=26, font=tk_tool.get_default_font(10), name="info%s" % index)
                Info0.pack()
                frame_m4 = tkinter.Frame(InputBoxUI) ; frame_m4.pack()
                StartX = tkinter.Entry(frame_m4, justify='center', font=tk_tool.get_default_font(10), width=7, name="input%s_1" % index)
                StartY = tkinter.Entry(frame_m4, justify='center', font=tk_tool.get_default_font(10), width=7, name="input%s_2" % index)
                StartZ = tkinter.Entry(frame_m4, justify='center', font=tk_tool.get_default_font(10), width=7, name="input%s_3" % index)
                StartX.grid(row=3*index+1, column=0)
                StartY.grid(row=3*index+1, column=1)
                StartZ.grid(row=3*index+1, column=2)
                StartX.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
                StartY.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
                StartZ.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
                StartX.bind("<KeyRelease>",lambda a : merge_entry_input(a, 1), add="+")
                StartY.bind("<KeyRelease>",lambda a : merge_entry_input(a, 2), add="+")
                StartZ.bind("<KeyRelease>",lambda a : merge_entry_input(a, 3), add="+")
                self.Merge_UI.append([Info0, StartX, StartY, StartZ])
                if index != 5 : tkinter.Label(InputBoxUI, text="  ", font=tk_tool.get_default_font(5)).pack()

            tkinter.Label(SubScreen_3_1, height=1,text="         ",font=tk_tool.get_default_font(2)).pack()
            self.merge_page_display = tkinter.Label(SubScreen_3_1, height=1,text="第1页   共1页", font=tk_tool.get_default_font(10),width=20)
            self.merge_page_display.pack()
            tkinter.Label(SubScreen_3_1, height=1,text="         ",font=tk_tool.get_default_font(2)).pack()

            frame_m4 = tkinter.Frame(SubScreen_3_1)
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("返回"),font=tk_tool.get_default_font(10),bg="#00FF88",
                command=lambda:[SubScreen_3_1.pack_forget(), MainScreen.pack(), 
                self.search_result.bind("<ButtonRelease-1>", lambda e:self.set_choose_index() ) ]).pack(side="left")
            tkinter.Label(frame_m4, height=1,text=" ",font=tk_tool.get_default_font(8)).pack(side="left")
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("<"),font=tk_tool.get_default_font(10),bg="#00FFF7",
                command=lambda:self.merge_page_set(-1)).pack(side="left")
            tkinter.Label(frame_m4, height=1,text=" ",font=tk_tool.get_default_font(8)).pack(side="left")
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string(">"),font=tk_tool.get_default_font(10),bg="#00FFF7",
                command=lambda:self.merge_page_set(1)).pack(side="left")
            tkinter.Label(frame_m4, height=1,text=" ",font=tk_tool.get_default_font(8)).pack(side="left")
            tkinter.Button(frame_m4, height=1,text=" 启动合并 ",font=tk_tool.get_default_font(10),bg="#00FF88",
                command=start_merge).pack(side="left")
            frame_m4.pack()

        SubScreen_0 = tkinter.Frame(MainScreen)
        SubScreen_0.pack()
        tkinter.Label(SubScreen_0, height=1,text="         ",font=tk_tool.get_default_font(5)).pack()
        tkinter.Button(SubScreen_0, height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()
        
        if "FeedbackScreen" :
            FeedbackScreen = tkinter.Frame(self) 
            frame_m10 = tkinter.Frame(FeedbackScreen)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            self.input_box = tkinter.Text(frame_m10,show=None,height=18,width=25,font=tk_tool.get_default_font(11),yscrollcommand=sco1.set)
            self.input_box.grid()
            sco1.config(command=self.input_box.yview)
            sco1.grid(row=0,column=1, sticky=tkinter.N+tkinter.S)
            frame_m10.pack()

            tkinter.Label(FeedbackScreen, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
            self.back_button = tkinter.Button(FeedbackScreen, height=1,text=" 返回上一页 ",font=tk_tool.get_default_font(12), bg="#9ae9d1",
                command=lambda:[FeedbackScreen.pack_forget(), MainScreen.pack(), 
                self.search_result.bind("<ButtonRelease-1>", lambda e:self.set_choose_index() )  ])
            self.back_button.pack()


    def transfor_setting(self, toplevel:tkinter.Toplevel) :
        parent_window = toplevel.master
        toplevel.transient(parent_window)
        toplevel.title("Setting")
        toplevel.geometry('%sx%s+%s+%s' % (
            int(parent_window.winfo_width()*9/10), int(parent_window.winfo_height()/2.7),
            int(parent_window.winfo_x() + parent_window.winfo_width()/2 - toplevel.winfo_reqwidth()/1.5),
            int(parent_window.winfo_y() + parent_window.winfo_height()/2 - toplevel.winfo_reqheight()/2) ))

        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        tkinter.Checkbutton(toplevel, text="启用结构分割（存档转换无效）", font=tk_tool.get_default_font(10), variable=self.enable_split, 
            onvalue=1, offvalue=0).pack()
        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        frame_m0 = tkinter.Frame(toplevel)
        frame_m0.pack()
        tkinter.Label(frame_m0, text="最小分割长度x", font=tk_tool.get_default_font(10), width=12, height=1).grid(row=0, column=0)
        SplitX = tkinter.Entry(frame_m0, justify='center', font=tk_tool.get_default_font(10), width=6)
        tkinter.Label(frame_m0, text="最小分割长度y", font=tk_tool.get_default_font(10), width=12, height=1).grid(row=1, column=0)
        SplitY = tkinter.Entry(frame_m0, justify='center', font=tk_tool.get_default_font(10), width=6)
        tkinter.Label(frame_m0, text="最小分割长度z", font=tk_tool.get_default_font(10), width=12, height=1).grid(row=2, column=0)
        SplitZ = tkinter.Entry(frame_m0, justify='center', font=tk_tool.get_default_font(10), width=6)
        SplitX.grid(row=0, column=1) ; SplitX.insert(0, str(self.split_size[0]))
        SplitY.grid(row=1, column=1) ; SplitY.insert(0, str(self.split_size[1]))
        SplitZ.grid(row=2, column=1) ; SplitZ.insert(0, str(self.split_size[2]))
        SplitX.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
        SplitY.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
        SplitZ.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))

        def test_value() :
            re1 = re.compile("^([0-9]+)$")
            if not re1.search(SplitX.get()) : 
                FeedBack.config(text="x参数格式错误") ; return None
            if not re1.search(SplitY.get()) : 
                FeedBack.config(text="y参数格式错误") ; return None
            if not re1.search(SplitZ.get()) : 
                FeedBack.config(text="z参数格式错误") ; return None
            self.split_size[0] = int(SplitX.get())
            self.split_size[1] = int(SplitY.get())
            self.split_size[2] = int(SplitZ.get())
            for i in self.choose_index : self.search_result.select_set(i)
            toplevel.destroy()

        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        FeedBack = tkinter.Label(toplevel, text=" 请输入分割参数 ", fg='red', font=tk_tool.get_default_font(10), width=15, height=1)
        FeedBack.pack()
        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        tkinter.Button(toplevel, height=1,text=" 保存设置 ",font=tk_tool.get_default_font(10), bg="#6eee70", command=test_value).pack()


    def start_thread_1(self) :
        tkinter.messagebox.showinfo("Info", "运行中如果将此APP变为后台\n安卓系统会暂停APP运行\n转换也将随之暂停\n\n如需运行其他应用\n可将该APP变为小窗")
        threading.Thread(target=self.transfor_file).start()

    def transfor_file(self) :
        from package.MCStructureManage import CommonStructure

        self.back_button.config(state=tkinter.DISABLED)
        listbox_name_list = self.search_result.get(0, tkinter.END)
        file_name_list:List[str] = [listbox_name_list[i] for i in self.choose_index]
        file_type_re = re.compile("\\.[0-9a-zA-Z]{0,}$")
        choose_trans_mode = self.codecs[self.transfor_choose.get()]

        for index, file_name in enumerate(file_name_list, start=1) :
            self.input_box.insert(tkinter.END, "正在转换 %s/%s 文件...\n%s\n" % (index, len(file_name_list), file_name))
            self.input_box.see(tkinter.END)
            time.sleep(0.3)

            if self.file_list[file_name]["outside"] : save_root_path = os.path.join(self.android_outside_storage, "result")
            else : save_root_path = os.path.join(self.base_path, "result")

            file_path = self.file_list[file_name]["real_path"]
            end_name = file_type_re.search( self.file_list[file_name]["real_name"] )
            save_file_name = file_name if end_name is None else file_name[:end_name.start()]
            save_split_file_dir = os.path.join( save_root_path, save_file_name+"(分割)" )
            save_file_path = os.path.join( save_root_path, save_file_name + choose_trans_mode[0] )

            try : Struct1 = CommonStructure.from_buffer(file_path)
            except Exception as e : 
                self.input_box.insert( tkinter.END, "转换发生错误，有疑问可询问开发者\n" )
                self.input_box.insert( tkinter.END, traceback.format_exc() + "\n\n" )
                self.input_box.see(tkinter.END)
                continue

            try :
                self.input_box.insert(tkinter.END, "正在生成转换文件...\n")
                self.input_box.see(tkinter.END)
                self.generate_file(self.enable_split.get(), self.transfor_choose.current(), self.split_size,
                    Struct1, save_file_name, save_split_file_dir, save_file_path, choose_trans_mode, self.input_box)
            except : 
                self.input_box.insert( tkinter.END, "转换发生错误，有疑问可询问开发者\n" )
                self.input_box.insert( tkinter.END, traceback.format_exc() + "\n\n" )
            else :
                self.input_box.insert(tkinter.END, "文件转换完成 (%s/%s)\n\n" % (index, len(file_name_list)))
                self.input_box.see(tkinter.END)
        
        self.back_button.config(state=tkinter.NORMAL)

    @staticmethod
    def generate_file(EnableSplit:bool, TransFormatChoose:int, SplitSize:Tuple[int,int,int], 
        Struct1, Name:str, SaveDir:str, SaveFile:str, TransMode:list, FeedBackShow:tkinter.Text) :
        from package.MCBEWorld import World

        if EnableSplit and TransFormatChoose != 1 :
            range_x = range(0, Struct1.size[0], SplitSize[0])
            range_y = range(0, Struct1.size[1], SplitSize[1])
            range_z = range(0, Struct1.size[2], SplitSize[2])
            split_pos_iter = itertools.product( range_x, range_y, range_z )
            struct_count = len(range_x) * len(range_y) * len(range_z)
            if struct_count != 1 :
                os.makedirs(SaveDir, exist_ok=True)
                for current_count, split_origin in enumerate(split_pos_iter, 1) :
                    save_file_path = os.path.join(SaveDir, Name) + ("[%s,%s,%s]" % split_origin) + TransMode[0]
                    #print(save_file_path)
                    split_max = ( min(split_origin[0]+SplitSize[0], Struct1.size[0]) - 1,
                        min(split_origin[1]+SplitSize[1], Struct1.size[1]) - 1,
                        min(split_origin[2]+SplitSize[2], Struct1.size[2]) - 1 )
                    FeedBackShow.insert(tkinter.END, "正在生成分割转换文件(%s/%s)...\n" % (current_count, struct_count))
                    Struct2 = Struct1.split(split_origin, split_max)
                    Struct2.save_as( save_file_path, TransMode[1] )
                return None

        if TransFormatChoose != 1 : Struct1.save_as(SaveFile, TransMode[1])
        else :
            save_file_path = SaveFile + "@[0,-64,0]~[%s,%s,%s]" % (Struct1.size[0], Struct1.size[1]-64, Struct1.size[2])
            MCWorld = World(save_file_path)
            MCWorld.world_name = Name
            MCWorld.import_CommonStructure(Struct1, 0, (0, -64, 0))
            MCWorld.close()
            BE_Structure_Tool.generate_mcworld(save_file_path)

    @staticmethod
    def generate_mcworld(world_path:str) :
        MCWorldZipFile = zipfile.ZipFile(world_path+".mcworld", "w")
        for dirpath, _, filenames in os.walk(world_path) :
            for filename in filenames : 
                file_name = os.path.join(dirpath, filename)
                arc_file_name = file_name.replace(world_path, "", 1)
                MCWorldZipFile.write( file_name, arc_file_name )

        MCWorldZipFile.close()
        for dirpath, _, filenames in os.walk(world_path) :
            for filename in filenames : os.remove( os.path.join(dirpath, filename) )
        for dirpath, dirnames, _ in os.walk(world_path) :
            for dirname in dirnames : 
                try : os.removedirs( os.path.join(dirpath, dirname) )
                except : pass


    def add_tips(self) :
        self.input_box.delete("0.0", tkinter.END)

        Tips = [
            "本工具支持读取的文件：",
            "bdx  mcstructure  schematic",
            "schem  跑路json  万花筒kbdx",
            "绵阳Json  绵阳building",
            "钢板Json  钢板reb",
            "浮鸿Json  浮鸿fhbuild",
            "情绪json TimeBuilderJson",
            "",
            "",
            "内部路径：",
            "<<Button_Copy_Inside_Path>>",
            "",
            "外部路径：",
            "<<Button_Copy_Outside_Path>>",
            "",
            "",
            "非澎湃OS用户请将需要读取的结构文件放置在内部路径"
            "文件夹内。澎湃OS用户需要将结构文件需要放置在外部路径"
            "文件夹内，避免文件读取发生权限错误。",
            "",
            "",
            "结构详情：读取结构文件并显示结构信息摘要，例如结构大小、空气数量等等。",
            "",
            "转换器：选择转换的文件格式，被选中的文件如果为内部路径的文件，则转换结果会生成在内部路径的result文件夹内。"
            "反之则会生成在外部路径的result文件夹内。如果结构过大，推荐启用设置内的结构分割模式。",
            "",
            "合并器：选中需要合并的结构文件，设置每个结构放置的起点坐标（结构放置如果重叠会互相覆盖，请估计好大小），"
            "合并完成的存档文件夹将生成在内部路径的的result文件夹内。",
            "",
            "",
            "如果发现有文件无法被读取，且确定是结构文件，可以点击",
            "→→ 设置-联系作者-交流群 ←←",
            "在交流群中与作者进行技术交流，litematic文件暂时不会支持",
            "",
        ]
        
        for index, Object in enumerate(Tips) :
            if Object == "<<Button_Copy_Inside_Path>>" :
                self.input_box.window_create(tkinter.END, window=tkinter.Button(self.input_box, height=1,
                text="点击复制内部路径",font=tk_tool.get_default_font(8), bg="#9ae9d1",
                command=lambda:tk_tool.copy_to_clipboard( os.path.realpath( os.path.join("functionality", "BE_Structure") ) )))
            elif Object == "<<Button_Copy_Outside_Path>>" :
                self.input_box.window_create(tkinter.END, window=tkinter.Button(self.input_box, height=1,
                text="点击复制外部路径",font=tk_tool.get_default_font(8), bg="#9ae9d1",
                command=lambda:tk_tool.copy_to_clipboard( self.android_outside_storage ) ))
            else : 
                if index < len(Tips)-1 and Tips[index+1].startswith("<<") :
                    self.input_box.insert(tkinter.END, Object)
                else : self.input_box.insert(tkinter.END, Object+"\n")
        
    def set_choose_index(self) :
        self.choose_index = self.search_result.curselection()


    def test_can_readFile(self, event:tkinter.Event) :
        if not self.can_readFile : return None
        self.can_readFile = False
        threading.Thread(target=self.show_structure_info, args=(event, )).start()

    def show_structure_info(self, event:tkinter.Event) :
        from package.MCStructureManage import CommonStructure,Block

        Widget:tkinter.Listbox = event.widget
        Selector:tuple = Widget.curselection()
        if not Selector : return None
        
        self.FileInfo1.config(text="文件名：(正在解析)")
        file_name = self.search_result.get(Selector[0])
        file_path = self.file_list[file_name]["real_path"]
        try : Structure1 = CommonStructure.from_buffer(file_path)
        except MemoryError :
            self.FileInfo1.config(text="文件名：%s" % file_name)
            self.FileInfo2.config(text="结构大小：内存溢出")
            self.FileInfo3.config(text="结构体积：内存溢出")
            self.FileInfo4.config(text="空气方块数：内存溢出")
            self.FileInfo5.config(text="非空气方块数：内存溢出")
            self.FileInfo6.config(text="方块NBT数：内存溢出")
        except PermissionError :
            self.FileInfo1.config(text="文件名：%s" % file_name)
            self.FileInfo2.config(text="结构大小：文件权限不足")
            self.FileInfo3.config(text="结构体积：文件权限不足")
            self.FileInfo4.config(text="空气方块数：文件权限不足")
            self.FileInfo5.config(text="非空气方块数：文件权限不足")
            self.FileInfo6.config(text="方块NBT数：文件权限不足")
        except :
            self.FileInfo1.config(text="文件名：%s" % file_name)
            self.FileInfo2.config(text="结构大小：解析失败")
            self.FileInfo3.config(text="结构体积：解析失败")
            self.FileInfo4.config(text="空气方块数：解析失败")
            self.FileInfo5.config(text="非空气方块数：解析失败")
            self.FileInfo6.config(text="方块NBT数：解析失败")
        else :
            Size = tuple(Structure1.size)
            AirCount = Structure1.count( Block("air") )
            self.FileInfo1.config(text="文件名：%s" % file_name)
            self.FileInfo2.config(text="结构大小：%s" % str(Size))
            self.FileInfo3.config(text="结构体积：%s" % (Size[0]*Size[1]*Size[2]))
            self.FileInfo4.config(text="空气方块数：%s" % AirCount)
            self.FileInfo5.config(text="非空气方块数：%s" % (Size[0]*Size[1]*Size[2]-AirCount))
            self.FileInfo6.config(text="方块NBT数：%s" % len(Structure1.block_nbt))
        
        self.can_readFile = True


    def merge_ready(self) :
        self.merge_info.clear()
        listbox_name_list = self.search_result.get(0, tkinter.END)
        file_name_list = [listbox_name_list[i] for i in self.search_result.curselection()]
        for name in file_name_list : self.merge_info.append([name, 0, -64, 0])
        self.merge_page_set()

    def merge_page_set(self, value:int=None) :
        if value is None : self.merge_page = 1 ; value = 0
        page_max = len(self.merge_info) // 6 + 1
        if not(0 < self.merge_page + value <= page_max) : return None
        self.merge_page += value
        self.merge_page_display.config(text="第%s页   共%s页" % (self.merge_page, page_max))

        current_index = self.merge_page - 1
        objects = self.merge_info[current_index*6:current_index*6+6]
        while len(objects) < 6 : objects.append(None)
        for index, obj in enumerate(objects) :
            if obj is None : 
                self.Merge_UI[index][0].config(text="此项无效，无需补充")
                self.Merge_UI[index][1].delete(0, "end")
                self.Merge_UI[index][2].delete(0, "end")
                self.Merge_UI[index][3].delete(0, "end")
            else :
                self.Merge_UI[index][0].config(text="%s 放置起点" % obj[0])
                self.Merge_UI[index][1].delete(0, "end")
                self.Merge_UI[index][2].delete(0, "end")
                self.Merge_UI[index][3].delete(0, "end")
                self.Merge_UI[index][1].insert("end", str(obj[1]))
                self.Merge_UI[index][2].insert("end", str(obj[2]))
                self.Merge_UI[index][3].insert("end", str(obj[3]))

    def start_thread_2(self) :
        tkinter.messagebox.showinfo("Info", "运行中如果将此APP变为后台\n安卓系统会暂停APP运行\n写入也将随之暂停\n\n如需运行其他应用\n可将该APP变为小窗")
        threading.Thread(target=self.merge_run).start()

    def merge_run(self) :
        from package.MCStructureManage import CommonStructure
        from package.MCBEWorld import World
        ProcessSet = set()

        self.back_button.config(state=tkinter.DISABLED)
        world_name = self.MergeWorldNameEntry.get()
        world_path = os.path.join( self.base_path, "result", world_name )
        MCWorld = World(world_path)
        MCWorld.world_name = world_name
        self.input_box.insert(tkinter.END, "%s 已生成...\n\n" % world_name)
        time.sleep(1)

        def Callback(v1, v2) :
            Process = int( v1 / v2 * 100 / 5 )
            if Process in ProcessSet : return None
            ProcessSet.add(Process)
            self.input_box.insert(tkinter.END, "正在生成结构对象(%s%%)...\n" % (Process*5))
            self.input_box.see(tkinter.END)

        for index, [file_name, posx, posy, posz] in enumerate(self.merge_info, start=1) :
            file_path = self.file_list[file_name]["real_path"]
            self.input_box.insert(tkinter.END, "正在合并 %s/%s 文件...\n%s\n" % (index, len(self.merge_info), file_name))
            self.input_box.see(tkinter.END)

            try : Struct1 = CommonStructure.from_buffer(file_path)
            except Exception as e : 
                self.input_box.insert( tkinter.END, "合并发生错误，有疑问可询问开发者\n" )
                self.input_box.insert( tkinter.END, traceback.format_exc() + "\n\n" )
                self.input_box.see(tkinter.END)
                continue

            MCWorld.import_CommonStructure(Struct1, 0, (posx, posy, posz), Callback)
            self.input_box.insert(tkinter.END, "合并已完成(%s/%s)\n\n" % (index, len(self.merge_info)))
            self.input_box.see(tkinter.END)
            ProcessSet.clear()
            time.sleep(1)
        
        MCWorld.close()
        self.generate_mcworld(world_path)

        self.input_box.insert(tkinter.END, "所有结构均已合并完成，在 " + world_name + " 内的runtime.cache文本文件中，" \
            "记录了所有被写入的结构的坐标范围")
        self.input_box.see(tkinter.END)
        self.back_button.config(state=tkinter.NORMAL)

class BE_World_Tool(tkinter.Frame) :
    base_path = os.path.join("functionality", "BE_World")
    android_outside_storage = "/storage/emulated/0/Documents/Pydroid3/Command_Simulator/BE_World"

    def __loop__(self) :
        if self.main_win.now_display_frame != "mcworld_reader" : return None
        from package.MCBEWorld import GetWorldEdtion

        world_list = {}
        inside_path = os.path.join(self.base_path, "")
        for i in os.listdir(inside_path) : 
            real_path = os.path.join(inside_path, i)
            dir_name = i.replace(inside_path, "", 1) + "(内部)"
            world_list[dir_name] = {"real_path":real_path, "outside":False}

        if self.main_win.platform == "android" :
            try :
                outside_path = os.path.join(self.android_outside_storage, "")
                for i in os.listdir(outside_path) : 
                    real_path = os.path.join(outside_path, i)
                    dir_name = i.replace(inside_path, "", 1) + "(外部)"
                    world_list[dir_name] = {"real_path":real_path, "outside":True}
            except : pass

        if set(world_list) != set(self.world_list) : 
            self.search_result.delete(0, tkinter.END)
            self.copy_mcs2world_list.delete(0, tkinter.END)
            for dir, data in world_list.items() :
                real_path = data["real_path"]
                if os.path.isdir(real_path) and GetWorldEdtion(real_path) : 
                    self.search_result.insert(tkinter.END, dir)
                    if self.NowOpenWorldDirName != dir : self.copy_mcs2world_list.insert(tkinter.END, dir)
                data["is_world"] = False
            self.world_list = world_list

    def __init__(self, main_win, **karg) -> None :
        from package.MCBEWorld import World
        if main_win.platform == "android" :
            try : os.makedirs(self.android_outside_storage, exist_ok=True)
            except : pass

        super().__init__(main_win.window, **karg)
        self.world_list: Dict[str, Dict[Literal["real_path", "outside"], Union[str, bool]]] = {}
        self.main_win = main_win
        self.NowOpenWorld:World = None
        self.NowOpenWorldDirName:str = None
        self.split_size = [99999, 99999, 99999]
        self.enable_split = tkinter.IntVar(main_win.window, 0)
        self.codecs = BE_Structure_Tool.__get_codecs__()

        def OpenWorld() :
            if not self.search_result.curselection() :
                tkinter.messagebox.showerror("Error", "没有在列表框中\n选中世界")
                return None
            MainScreen.pack_forget(); MainScreen_1.pack()
            Key = self.search_result.get( self.search_result.curselection()[0] )
            self.NowOpenWorld = World( self.world_list[Key]["real_path"] )
            self.NowOpenWorldDirName = Key
            self.open_title.config( text="已打开世界：%s" % Key )
            self.back_button.config( command=lambda:[FeedbackScreen.pack_forget(), MainScreen_1.pack()] )
            self.mcs_list.delete(0, tkinter.END)
            self.mcs_list.insert(tkinter.END, *[i for i in self.NowOpenWorld.StructureManager])
            self.world_list.clear()

        def CloseAndSave() :
            MainScreen.pack(); MainScreen_1.pack_forget()
            self.NowOpenWorld.close()
            self.NowOpenWorld = None
            self.NowOpenWorldDirName = None
            self.back_button.config( command=lambda:[FeedbackScreen.pack_forget(), MainScreen.pack()] )

        if "主界面" :
            tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()
            ReadTips = tkinter.Frame(self) 
            ReadTips.pack()
            tkinter.Label(ReadTips, text="初次使用请先阅读",fg='red', font=tk_tool.get_default_font(12)).pack(side='left')
            tkinter.Button(ReadTips, height=1,text=tk_tool.platform_string("使用说明"),font=tk_tool.get_default_font(9), bg="#fdd142",
                command=lambda:[FeedbackScreen.pack(), MainScreen.pack_forget(), MainScreen_1.pack_forget(),
                self.add_tips()]).pack(side='left')
            tkinter.Label(self,height=1,text="         ",font=tk_tool.get_default_font(5)).pack()

            MainScreen = tkinter.Frame(self) 
            MainScreen.pack()
            frame_m10 = tkinter.Frame(MainScreen)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
            self.search_result = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(10),selectmode=tkinter.SINGLE,
                height=9,width=26,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
            self.search_result.bind("<ButtonRelease-1>", self.show_world_info)
            self.search_result.grid(row=0,column=0)
            sco1.config(command=self.search_result.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            sco2.config(command=self.search_result.xview)
            sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
            frame_m10.pack()
        
        if "详情界面" :
            SubScreen_1 = tkinter.Frame(MainScreen) 
            SubScreen_1.pack()
            tkinter.Label(SubScreen_1, text="", fg='black',font=tk_tool.get_default_font(5), width=15, height=1).grid(row=0, column=0)
            self.FileInfo1 = tkinter.Label(SubScreen_1, text="文件夹：(点击列表中的世界)", fg='black',font=tk_tool.get_default_font(10), width=26, height=1, anchor='w')
            self.FileInfo2 = tkinter.Label(SubScreen_1, text="世界名：", fg='black',font=tk_tool.get_default_font(10), width=26, height=1, anchor='w')
            self.FileInfo3 = tkinter.Label(SubScreen_1, text="世界类型：", fg='black',font=tk_tool.get_default_font(10), width=26, height=1, anchor='w')
            self.FileInfo4 = tkinter.Label(SubScreen_1, text="MCS结构：", fg='black',font=tk_tool.get_default_font(10), width=26, height=1, anchor='w')
            self.FileInfo5 = tkinter.Label(SubScreen_1, text="加密密钥：", fg='black',font=tk_tool.get_default_font(10), width=26, height=1, anchor='w')
            self.FileInfo1.grid(row=1, column=0)
            self.FileInfo2.grid(row=2, column=0)
            self.FileInfo3.grid(row=3, column=0)
            self.FileInfo4.grid(row=4, column=0)
            self.FileInfo5.grid(row=5, column=0)

            frame_m4 = tkinter.Frame(MainScreen)
            tkinter.Label(frame_m4, text="  ", font=tk_tool.get_default_font(5), height=1).pack()
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("打开世界提取结构"),font=tk_tool.get_default_font(10), bg="#9ae9d1",
                command=OpenWorld).pack()
            frame_m4.pack()

        if "进入世界界面" :
            MainScreen_1 = tkinter.Frame(self)
            frame_m4 = tkinter.Frame(MainScreen_1)
            self.open_title = tkinter.Label(MainScreen_1, text="已打开世界：TRsxjawRa==",fg='black',font=tk_tool.get_default_font(9), width=28, height=1)
            self.open_title.pack()
            Mode_Button1 = tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("MCS导出"),font=tk_tool.get_default_font(9), bg="#9ae9d1",
                command=lambda: [Mode_Button1.config(state=tkinter.DISABLED), Mode_Button2.config(state=tkinter.NORMAL), 
                Mode_Button3.config(state=tkinter.NORMAL), SubScreen_11.pack(), SubScreen_12.pack_forget(), SubScreen_13.pack_forget(),
                CloseWorld.pack_forget(), CloseWorld.pack() ])
            Mode_Button2 = tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("MCS转移"),font=tk_tool.get_default_font(9), bg="#9ae9d1",
                command=lambda: [Mode_Button1.config(state=tkinter.NORMAL), Mode_Button2.config(state=tkinter.DISABLED), 
                Mode_Button3.config(state=tkinter.NORMAL), SubScreen_11.pack_forget(), SubScreen_12.pack(), SubScreen_13.pack_forget(),
                CloseWorld.pack_forget(), CloseWorld.pack() ])
            Mode_Button3 = tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("选区导出"),font=tk_tool.get_default_font(9), bg="#9ae9d1",
                command=lambda: [Mode_Button1.config(state=tkinter.NORMAL), Mode_Button2.config(state=tkinter.NORMAL), 
                Mode_Button3.config(state=tkinter.DISABLED), SubScreen_11.pack_forget(), SubScreen_12.pack_forget(), SubScreen_13.pack(),
                CloseWorld.pack_forget(), CloseWorld.pack() ])
            Mode_Button1.pack(side='left')
            tkinter.Label(frame_m4, text=" ", font=tk_tool.get_default_font(8), height=1).pack(side='left')
            Mode_Button2.pack(side='left')
            tkinter.Label(frame_m4, text=" ", font=tk_tool.get_default_font(8), height=1).pack(side='left')
            Mode_Button3.pack(side='left')
            Mode_Button1.config(state=tkinter.DISABLED)
            frame_m4.pack()
            tkinter.Label(MainScreen_1, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()

        if "导出MCS界面" :
            SubScreen_11 = tkinter.Frame(MainScreen_1) ; SubScreen_11.pack()
            tkinter.Label(SubScreen_11, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()

            frame_m10 = tkinter.Frame(SubScreen_11)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
            self.mcs_list = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(10),selectmode=tkinter.MULTIPLE,
                height=10,width=26,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
            self.mcs_list.grid(row=0,column=0)
            sco1.config(command=self.mcs_list.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            sco2.config(command=self.mcs_list.xview)
            sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
            frame_m10.pack()
            
            def start_export_mcs() :
                if not self.mcs_list.curselection() : 
                    tkinter.messagebox.showerror("Error", "没有MCS结构被选中\n请确认是否选择MCS?")
                    return None
                
                self.input_box.delete("0.0", tkinter.END)
                FeedbackScreen.pack()
                MainScreen_1.pack_forget()
                self.start_thread(1)
            
            tkinter.Label(SubScreen_11, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            tkinter.Label(SubScreen_11, text="点击列表，选择单个或多个条目",fg="#2756FF", 
                font=tk_tool.get_default_font(11)).pack()
            tkinter.Label(SubScreen_11, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            frame_m4 = tkinter.Frame(SubScreen_11)
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("全选"),font=tk_tool.get_default_font(9), bg="#ff6cf5",
                command=lambda:self.mcs_list.select_set(0, "end")).pack(side='left')
            tkinter.Label(frame_m4, text=" ", font=tk_tool.get_default_font(5), height=1).pack(side='left')
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("清空"),font=tk_tool.get_default_font(9), bg="#ff6cf5",
                command=lambda:self.mcs_list.select_clear(0, "end")).pack(side='left')
            tkinter.Label(frame_m4, text=" ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
            tkinter.Button(frame_m4, height=1,text=tk_tool.platform_string("导出MCS"),font=tk_tool.get_default_font(9), bg="#61eaff",
                command=start_export_mcs).pack(side="left")
            frame_m4.pack()

        if "转移MCS界面" : 
            SubScreen_12 = tkinter.Frame(MainScreen_1)
            tkinter.Label(SubScreen_12, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()

            frame_m10 = tkinter.Frame(SubScreen_12)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
            self.copy_mcs2world_list = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(10),selectmode=tkinter.SINGLE,
                height=10,width=26,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
            self.copy_mcs2world_list.grid(row=0,column=0)
            sco1.config(command=self.copy_mcs2world_list.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            sco2.config(command=self.copy_mcs2world_list.xview)
            sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
            frame_m10.pack()
            
            def start_transfer_mcs() :
                if not self.copy_mcs2world_list.curselection() : 
                    tkinter.messagebox.showerror("Error", "没有存档被选中\n请确认是否选择存档?")
                    return None
                
                self.input_box.delete("0.0", tkinter.END)
                FeedbackScreen.pack()
                MainScreen_1.pack_forget()
                self.start_thread(2)
            
            tkinter.Label(SubScreen_12, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            tkinter.Label(SubScreen_12, text="点击列表，选择单个条目",fg="#2756FF", 
                font=tk_tool.get_default_font(11)).pack()
            tkinter.Label(SubScreen_12, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
            tkinter.Button(SubScreen_12, height=1,text=tk_tool.platform_string("转移MCS至存档"),font=tk_tool.get_default_font(9), bg="#61eaff",
                command=start_transfer_mcs).pack()

        if "导出结构" : 
            def start_creat_CommonStructure() :
                try : int(StartX.get())
                except : tkinter.messagebox.showerror("Error", "起始X坐标格式错误") ; return None
                try : int(StartY.get())
                except : tkinter.messagebox.showerror("Error", "起始Y坐标格式错误") ; return None
                try : int(StartZ.get())
                except : tkinter.messagebox.showerror("Error", "起始Z坐标格式错误") ; return None
                try : int(EndX.get())
                except : tkinter.messagebox.showerror("Error", "结束X坐标格式错误") ; return None
                try : int(EndY.get())
                except : tkinter.messagebox.showerror("Error", "结束Y坐标格式错误") ; return None
                try : int(EndZ.get())
                except : tkinter.messagebox.showerror("Error", "结束Z坐标格式错误") ; return None
                if self.transfor_choose.current() == 0 :
                    tkinter.messagebox.showerror("Error", "未选择导出格式") ; return None
                self.input_box.delete("0.0", tkinter.END)
                FeedbackScreen.pack()
                MainScreen_1.pack_forget()
                InputList = [int(i.get()) for i in (StartX, StartY, StartZ, EndX, EndY, EndZ) ]
                self.start_thread(3, [InputList[i] for i in range(0, 3)], [InputList[i] for i in range(3, 6)])

            SubScreen_13 = tkinter.Frame(MainScreen_1)
            tkinter.Label(SubScreen_13, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()
            tkinter.Label(SubScreen_13, text="选择导出维度",fg='black',font=tk_tool.get_default_font(11), width=15, height=1).pack()
            self.dimension_choose = ttk.Combobox(SubScreen_13, font=tk_tool.get_default_font(10), width=22, state='readonly', justify='center')
            self.dimension_choose["value"] = ["主世界", "地狱", "末地"]
            self.dimension_choose.current(0)
            self.dimension_choose.pack()
            tkinter.Label(SubScreen_13, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()
            tkinter.Label(SubScreen_13, text="起始位置(x, y, z)",fg='black',font=tk_tool.get_default_font(11), width=15, height=1).pack()
            frame_m10 = tkinter.Frame(SubScreen_13)
            StartX = tkinter.Entry(frame_m10, justify='center', font=tk_tool.get_default_font(10), width=9)
            StartY = tkinter.Entry(frame_m10, justify='center', font=tk_tool.get_default_font(10), width=6)
            StartZ = tkinter.Entry(frame_m10, justify='center', font=tk_tool.get_default_font(10), width=9)
            StartX.grid(row=0, column=0)
            StartY.grid(row=0, column=1)
            StartZ.grid(row=0, column=2)
            StartX.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            StartY.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            StartZ.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            frame_m10.pack()

            tkinter.Label(SubScreen_13, text=" ",fg='black',font=tk_tool.get_default_font(2), width=15, height=1).pack()
            tkinter.Label(SubScreen_13, text="结束位置(x, y, z)",fg='black',font=tk_tool.get_default_font(11), width=15, height=1).pack()
            frame_m10 = tkinter.Frame(SubScreen_13)
            EndX = tkinter.Entry(frame_m10, justify='center', font=tk_tool.get_default_font(10), width=9)
            EndY = tkinter.Entry(frame_m10, justify='center', font=tk_tool.get_default_font(10), width=6)
            EndZ = tkinter.Entry(frame_m10, justify='center', font=tk_tool.get_default_font(10), width=9)
            EndX.grid(row=0, column=0)
            EndY.grid(row=0, column=1)
            EndZ.grid(row=0, column=2)
            EndX.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            EndY.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            EndZ.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            frame_m10.pack()
            [ i.insert("end", "0") for i in (StartX, StartY, StartZ, EndX, EndY, EndZ) ]

            tkinter.Label(SubScreen_13, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()
            self.transfor_choose = ttk.Combobox(SubScreen_13, font=tk_tool.get_default_font(10), width=22, state='readonly', justify='center')
            self.transfor_choose["value"] = list( i for i,j in self.codecs.items() )
            self.transfor_choose.current(0)
            self.transfor_choose.pack()
            tkinter.Label(SubScreen_13, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()
            self.ExplotFileNameEntry = tkinter.Entry(SubScreen_13, fg='black', font=tk_tool.get_default_font(11), width=22, justify="center")
            self.ExplotFileNameEntry.insert("end", "请输入导出文件名")
            self.ExplotFileNameEntry.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
            self.ExplotFileNameEntry.pack()
            tkinter.Label(SubScreen_13, text="",fg='black',font=tk_tool.get_default_font(5), width=15, height=1).pack()

            frame_m4 = tkinter.Frame(SubScreen_13)
            tkinter.Button(frame_m4, text=tk_tool.platform_string("设置"),font=tk_tool.get_default_font(10), bg="#61eaff",
                command=lambda:self.transfor_setting(tkinter.Toplevel(main_win.window))).pack(side="left")
            tkinter.Label(frame_m4, text="     ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
            tkinter.Button(frame_m4, text=tk_tool.platform_string("确认导出"),font=tk_tool.get_default_font(10),
                bg="#61eaff", command=start_creat_CommonStructure).pack(side="left")
            frame_m4.pack()

        CloseWorld = tkinter.Frame(MainScreen_1)
        tkinter.Label(CloseWorld, height=1,text="         ",font=tk_tool.get_default_font(8)).pack()
        tkinter.Button(CloseWorld, height=1,text="<<关闭世界并返回",font=tk_tool.get_default_font(13),bg="#bfff36",
            command=CloseAndSave).pack()
        CloseWorld.pack()

        SubScreen_END = tkinter.Frame(MainScreen)
        tkinter.Label(SubScreen_END, height=1,text="         ",font=tk_tool.get_default_font(8)).pack()
        tkinter.Button(SubScreen_END, height=1,text="<<返回主界面",font=tk_tool.get_default_font(13),bg="orange",
            command=lambda:self.main_win.set_display_frame("welcome_screen")).pack()
        SubScreen_END.pack()
        
        if "FeedbackScreen" :
            FeedbackScreen = tkinter.Frame(self) 
            frame_m10 = tkinter.Frame(FeedbackScreen)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            self.input_box = tkinter.Text(frame_m10,show=None,height=18,width=25,font=tk_tool.get_default_font(11),yscrollcommand=sco1.set)
            self.input_box.grid()
            sco1.config(command=self.input_box.yview)
            sco1.grid(row=0,column=1, sticky=tkinter.N+tkinter.S)
            frame_m10.pack()

            tkinter.Label(FeedbackScreen, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
            self.back_button = tkinter.Button(FeedbackScreen, height=1,text=" 返回上一页 ",font=tk_tool.get_default_font(13), bg="#9ae9d1",
                command=lambda:[FeedbackScreen.pack_forget(), MainScreen_1.pack() if self.NowOpenWorld else MainScreen.pack()])
            self.back_button.pack()


    def start_thread(self, mode:int, *args) :
        tkinter.messagebox.showinfo("Info", "运行中如果将此APP变为后台\n安卓系统会暂停APP运行\n程序运行也将随之暂停\n\n如需运行其他应用\n可将该APP变为小窗")
        self.back_button.config(state=tkinter.DISABLED)
        if mode == 1 : threading.Thread(target=self.explot_mcs).start()
        if mode == 2 : threading.Thread(target=self.transfer_mcs).start()
        if mode == 3 : threading.Thread(target=self.creat_commonstructure, args=(args[0], args[1])).start()

    def explot_mcs(self) :
        choose_index = self.mcs_list.curselection()
        choose_len = len( choose_index )
        if self.world_list[self.NowOpenWorldDirName]["outside"] : save_root_path = os.path.join(self.android_outside_storage, "result")
        else : save_root_path = os.path.join(self.base_path, "result")

        os.makedirs( save_root_path, exist_ok=True )
        for index, choose_index in enumerate(choose_index, start=1) :
            mcs_name = self.mcs_list.get(choose_index)
            self.input_box.insert(tkinter.END, "正在导出 %s/%s 结构...\n%s\n" % (index, choose_len, mcs_name))
            self.input_box.see(tkinter.END)

            save_file_path = os.path.join( save_root_path, mcs_name.replace(":", "_")+".mcstructure" )
            with open(save_file_path, "wb") as _f : _f.write( self.NowOpenWorld.StructureManager.get(mcs_name) )
            self.input_box.insert(tkinter.END, "MCS结构导出完成 (%s/%s)\n\n" % (index, choose_len))
            self.input_box.see(tkinter.END)
            time.sleep(0.1)

        self.back_button.config(state=tkinter.NORMAL)

    def transfer_mcs(self) :
        from package.MCBEWorld import World

        transfer_target_world = self.copy_mcs2world_list.get( self.copy_mcs2world_list.curselection() )
        transfer_target_world_OBJ = World( self.world_list[transfer_target_world]["real_path"] )
        mcs_len = len( self.NowOpenWorld.StructureManager )
        os.makedirs( os.path.join( self.base_path, "result" ), exist_ok=True )
        for index, mcs_name in enumerate(self.NowOpenWorld.StructureManager, start=1) :
            self.input_box.insert(tkinter.END, "正在转移 %s/%s 结构...\n%s\n" % (index, mcs_len, mcs_name))
            self.input_box.see(tkinter.END)

            transfer_target_world_OBJ.StructureManager.set(
                mcs_name, self.NowOpenWorld.StructureManager.get(mcs_name) )
            self.input_box.insert(tkinter.END, "MCS结构转移完成 (%s/%s)\n\n" % (index, mcs_len))
            self.input_box.see(tkinter.END)
            time.sleep(0.1)

        transfer_target_world_OBJ.close()
        self.back_button.config(state=tkinter.NORMAL)

    def creat_commonstructure(self, start:Tuple[int, int, int], end:Tuple[int, int, int]) :
        from package.MCStructureManage import CommonStructure
        ProcessSet = set()

        def Callback(v1, v2) :
            Process = int( v1 / v2 * 100 )
            if Process in ProcessSet : return None
            ProcessSet.add(Process)
            self.input_box.insert(tkinter.END, "正在生成结构对象(%s%%)...\n" % Process)
            self.input_box.see(tkinter.END)

        Struct1 = CommonStructure()
        self.NowOpenWorld.export_CommonStructure(Struct1, self.dimension_choose.current(), start, end, Callback)

        if self.world_list[self.NowOpenWorldDirName]["outside"] : save_root_path = os.path.join(self.android_outside_storage, "result")
        else : save_root_path = os.path.join(self.base_path, "result")
        choose_trans_mode = self.codecs[self.transfor_choose.get()]

        save_file_name = self.ExplotFileNameEntry.get()
        save_split_file_dir = os.path.join( save_root_path, save_file_name+"(分割)" )
        save_file_path = os.path.join( save_root_path, save_file_name + choose_trans_mode[0] )

        self.input_box.insert(tkinter.END, "正在生成结构文件%s...\n" % save_file_name)
        self.input_box.see(tkinter.END)
        try :
            BE_Structure_Tool.generate_file(self.enable_split.get(), self.transfor_choose.current(), self.split_size,
            Struct1, save_file_name, save_split_file_dir, save_file_path, choose_trans_mode, self.input_box)
        except : 
            self.input_box.insert( tkinter.END, "转换发生错误，有疑问可询问开发者\n" )
            self.input_box.insert( tkinter.END, traceback.format_exc() + "\n\n" )
        else :
            self.input_box.insert(tkinter.END, "结构文件%s已生成完毕\n" % save_file_name)
            self.input_box.see(tkinter.END)
        self.back_button.config(state=tkinter.NORMAL)


    def add_tips(self) :
        self.input_box.delete("0.0", tkinter.END)

        Tips = [
            "本工具用于读取存档文件夹中的结构内容，"
            "zip文件与mcworld文件请先自行解压出存档文件夹。",
            "合法的存档：进入首层文件夹后应存在level.dat与db文件夹。",
            "",
            "内部路径：",
            "<<Button_Copy_Inside_Path>>",
            "",
            "外部路径：",
            "<<Button_Copy_Outside_Path>>",
            "",
            "",
            "非澎湃OS用户请将需要读取的存档文件夹放置在内部路径"
            "文件夹内。澎湃OS用户需要将存档文件夹需要放置在外部路径"
            "文件夹内，避免文件读取发生权限错误。",
            "",
            "",
            "存档详情：读取存档文件夹内容并显示信息摘要，例如MCS数量、世界类型等等。",
            "",
            "MCS导出：选择世界内的MCS结构进行导出，如果存档文件夹位于内部储存，"
            "则导出结果会生成在内部路径的result文件夹内，反之会生成在外部路径的result文件夹内。",
            "",
            "MCS转移：选中需要转移MCS的目标存档文件夹，即可拷贝MCS至目标存档。",
            "",
            "选区导出：指定存档内的起始和结束位置，起始和结束位置的方块都将会被导出至目标文件格式。",
            "",
            "",
        ]
        
        for index, Object in enumerate(Tips) :
            if Object == "<<Button_Copy_Inside_Path>>" :
                self.input_box.window_create(tkinter.END, window=tkinter.Button(self.input_box, height=1,
                text="点击复制内部路径",font=tk_tool.get_default_font(8), bg="#9ae9d1",
                command=lambda:tk_tool.copy_to_clipboard( os.path.realpath( os.path.join("functionality", "BE_World") ) )))
            elif Object == "<<Button_Copy_Outside_Path>>" :
                self.input_box.window_create(tkinter.END, window=tkinter.Button(self.input_box, height=1,
                text="点击复制外部路径",font=tk_tool.get_default_font(8), bg="#9ae9d1",
                command=lambda:tk_tool.copy_to_clipboard( self.android_outside_storage ) ))
            else : 
                if index < len(Tips)-1 and Tips[index+1].startswith("<<") :
                    self.input_box.insert(tkinter.END, Object)
                else : self.input_box.insert(tkinter.END, Object+"\n")

    def show_world_info(self, event:tkinter.Event) :
        from package.MCBEWorld import World

        Widget:tkinter.Listbox = event.widget
        Selector:tuple = Widget.curselection()
        if not Selector : return None
        
        dir_name = self.search_result.get(Selector[0])
        dir_path = self.world_list[dir_name]["real_path"]
        try :  WorldObject = World(dir_path)
        except PermissionError :
            self.FileInfo1.config(text="文件名：%s" % dir_name)
            self.FileInfo2.config(text="结世界名：文件权限不足")
            self.FileInfo3.config(text="世界类型：文件权限不足")
            self.FileInfo4.config(text="MCS结构：文件权限不足")
            self.FileInfo5.config(text="加密密钥：文件权限不足")
        except :
            self.FileInfo1.config(text="文件夹：%s" % dir_name)
            self.FileInfo2.config(text="世界名：解析失败")
            self.FileInfo3.config(text="世界类型：解析失败")
            self.FileInfo4.config(text="MCS结构：解析失败")
            self.FileInfo5.config(text="加密密钥：解析失败")
        else : 
            try : WorldName = WorldObject.world_nbt["LevelName"].value
            except : WorldName = "我的世界"
            self.FileInfo1.config(text="文件夹：%s" % dir_name)
            self.FileInfo2.config(text="世界名：%s" % WorldName)
            self.FileInfo3.config(text="世界类型：%s" % 'Bedrock' if WorldObject.encrypt_key is None else 'Netease')
            self.FileInfo4.config(text="MCS结构：%s" % len( WorldObject.StructureManager ))
            self.FileInfo5.config(text="加密密钥：%s" % WorldObject.encrypt_key)

    def transfor_setting(self, toplevel:tkinter.Toplevel) :
        parent_window = toplevel.master
        toplevel.transient(parent_window)
        toplevel.title("Setting")
        toplevel.geometry('%sx%s+%s+%s' % (
            int(parent_window.winfo_width()*9/10), int(parent_window.winfo_height()/2.7),
            int(parent_window.winfo_x() + parent_window.winfo_width()/2 - toplevel.winfo_reqwidth()/1.5),
            int(parent_window.winfo_y() + parent_window.winfo_height()/2 - toplevel.winfo_reqheight()/2) ))

        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        tkinter.Checkbutton(toplevel, text="启用结构分割（存档转换无效）", font=tk_tool.get_default_font(10), variable=self.enable_split, 
            onvalue=1, offvalue=0).pack()
        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        frame_m0 = tkinter.Frame(toplevel)
        frame_m0.pack()
        tkinter.Label(frame_m0, text="最小分割长度x", font=tk_tool.get_default_font(10), width=12, height=1).grid(row=0, column=0)
        SplitX = tkinter.Entry(frame_m0, justify='center', font=tk_tool.get_default_font(10), width=6)
        tkinter.Label(frame_m0, text="最小分割长度y", font=tk_tool.get_default_font(10), width=12, height=1).grid(row=1, column=0)
        SplitY = tkinter.Entry(frame_m0, justify='center', font=tk_tool.get_default_font(10), width=6)
        tkinter.Label(frame_m0, text="最小分割长度z", font=tk_tool.get_default_font(10), width=12, height=1).grid(row=2, column=0)
        SplitZ = tkinter.Entry(frame_m0, justify='center', font=tk_tool.get_default_font(10), width=6)
        SplitX.grid(row=0, column=1) ; SplitX.insert(0, str(self.split_size[0]))
        SplitY.grid(row=1, column=1) ; SplitY.insert(0, str(self.split_size[1]))
        SplitZ.grid(row=2, column=1) ; SplitZ.insert(0, str(self.split_size[2]))
        SplitX.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
        SplitY.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))
        SplitZ.bind("<FocusIn>",lambda a : self.main_win.set_focus_input(a))

        def test_value() :
            re1 = re.compile("^([0-9]+)$")
            if not re1.search(SplitX.get()) : 
                FeedBack.config(text="x参数格式错误") ; return None
            if not re1.search(SplitY.get()) : 
                FeedBack.config(text="y参数格式错误") ; return None
            if not re1.search(SplitZ.get()) : 
                FeedBack.config(text="z参数格式错误") ; return None
            self.split_size[0] = int(SplitX.get())
            self.split_size[1] = int(SplitY.get())
            self.split_size[2] = int(SplitZ.get())
            toplevel.destroy()

        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        FeedBack = tkinter.Label(toplevel, text=" 请输入分割参数 ", fg='red', font=tk_tool.get_default_font(10), width=15, height=1)
        FeedBack.pack()
        tkinter.Label(toplevel, text=" ", fg='black', font=tk_tool.get_default_font(3), width=15, height=1).pack()
        tkinter.Button(toplevel, height=1,text=" 保存设置 ",font=tk_tool.get_default_font(10), bg="#6eee70", command=test_value).pack()


class Game_Ready(tkinter.Frame) :

    def __init__(self, main_win, **karg) -> None:
        super().__init__(main_win.window, **karg)
        self.main_win = main_win
        a1 = tkinter.Label(self, text="命令模拟存档", bg='#82aaff',fg='black',font=tk_tool.get_default_font(20), width=15, height=1)
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
        self.expand_select = tkinter.Listbox(frame_m10, font=tk_tool.get_default_font(12), selectmode=tkinter.SINGLE,
            height=16, width=23, yscrollcommand=sco1.set)
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
        
        tkinter.Label(self, text="Version: %s" % app_constant.APP_VERSION, fg='black', font=tk_tool.get_default_font(11), height=1).pack(side="bottom")
        tkinter.Label(self, text="", fg='black', font=tk_tool.get_default_font(5), width=2, height=2).pack(side="bottom")

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



