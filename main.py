#!/usr/bin/python
# -*- coding: UTF-8 -*-

#原生模块加载与设置
from idlelib.calltip_w import CalltipWindow
import webbrowser,http.server,ssl
import json,tkinter,tkinter.font,time,threading,sys,base64,gzip
import platform,copy,os,re,types,io,gc,subprocess,traceback,importlib
import random,functools,pickle,hmac,tkinter.messagebox,importlib.util
from tkinter import ttk
from typing import List,Dict,Union,Literal
ssl._create_default_https_context = ssl._create_unverified_context

#自定义模块加载与设置
import main_source.main_window.constant as app_constants
import main_source.main_window.function as app_function
import main_source.main_window.tk_frame as app_tk_frame
import main_source.package.file_operation as file_IO
import main_source.package.tk_tool as tk_tool

#模拟世界模块加载
import main_source.bedrock_edition as Minecraft_BE


if True : #启用软件前的加载项目
    for i in app_constants.First_Load_Build_Dir : os.makedirs(i,exist_ok=True)
    os.makedirs(os.path.join("functionality","example","example_bp","functions"),exist_ok=True)
    manifest_path = os.path.join("functionality","example","example_bp","manifest.json")
    if not(os.path.exists(manifest_path) and os.path.isfile(manifest_path)) : 
        file_IO.write_a_file(os.path.join("functionality","example","example_bp","manifest.json"),app_constants.manifest_json)
    del manifest_path

    def http_server_create(server_class=http.server.HTTPServer, handler_class=http.server.SimpleHTTPRequestHandler):
        from urllib import parse
        class http_Resquest(handler_class) :

            def do_GET(self):
                url_obj = parse.urlparse(self.path)
                if url_obj.path == "/" and url_obj.query != "" :
                    query_components = parse.parse_qs(url_obj.query)
                    if "pack" not in query_components : return None
                    path1 = os.path.join("expand_pack",query_components['pack'][0],"index.html")
                    if not(os.path.exists(path1) and os.path.isfile(path1)) : return None
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(file_IO.read_a_file(path1,"readbyte"))
                else : super().do_GET()

            def do_POST(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Encoding', 'gzip')
                self.end_headers()
                datas = self.rfile.read(int(self.headers['content-length']))
                respones = debug_windows.post_data(datas, debug_windows.user_manager.save_data['expand_packs'])
                self.wfile.write(gzip.compress(json.dumps(respones,separators=(',', ':'),
                    default=Minecraft_BE.DataSave.encoding).encode('utf-8')))
        
        server_address = ('', 32323)
        http_Resquest = functools.partial(http_Resquest,directory="html_output")
        httpd = server_class(server_address, http_Resquest)
        httpd.serve_forever()
    threading.Thread(target=http_server_create).start()

    def listen_cmd_input() :
        while app_constants.debug_testing : 
            text1 = input(">>> ")
            aaaa = globals()
            try : compile(text1,"","eval")
            except Exception as e : 
                try : exec(text1, aaaa, aaaa)
                except : traceback.print_exc()
            else :
                try : 
                    a_11 = time.time()
                    print(eval(text1, aaaa, aaaa))
                    a_22 = time.time()
                    print('时间：' + str(a_22 - a_11))
                except : traceback.print_exc()
    threading.Thread(target=listen_cmd_input).start()


class control_windows :

    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title('minecraft命令调试器')
        self.window.geometry('300x600')
        self.calltip_win = CalltipWindow(self.window)

        self.display_frame:Dict[str,tkinter.Frame] = {}
        self.now_display_frame = ""
        self.focus_input:Union[tkinter.Entry,tkinter.Text,ttk.Entry] = None
        self.expand_pack_open_list:Dict[str,Dict[Literal["frame","module","object"],
            Union[tkinter.Frame,types.ModuleType,object]]] = {}
        self.change_hight_component_list = [] #可变高度组件列表

        Announcement = app_tk_frame.Announcement(self)
        Announcement.pack()

        self.user_manager = app_function.user_manager() #用户管理
        self.initialization_log = [app_function.initialization_log() for i in range(3)]
        self.initialization_process:List[threading.Thread] = [
            threading.Thread(target=app_function.get_app_infomation_and_login, args=(Announcement, self.user_manager, self.initialization_log[0])),
            threading.Thread(target=app_function.flash_minecraft_id, args=(self.initialization_log[1], )),
            threading.Thread(target=app_function.flash_minecraft_source, args=(self.user_manager, self.initialization_log[2])),
        ]
        self.game_process:Minecraft_BE.RunTime.minecraft_thread = None #模拟世界线程

        #self.windows_constant()
        for i in self.initialization_process : i.start()
        self.window.protocol("WM_DELETE_WINDOW", lambda:[self.user_manager.write_back(), os._exit(0)])

        self.paset_thread_time = 0  #输入降频计时
        self.platform:Literal["windows","android"] = None #系统名称
        system_info = platform.uname()
        if system_info.system.lower() == 'windows' : self.platform = 'windows'
        elif system_info.system.lower() == 'linux' and system_info.machine == "aarch64" : self.platform = 'android'


    def creat_windows(self):
        self.button_bar = app_tk_frame.Bottom_Bar(self)
        self.button_bar.pack(side="bottom")
        self.display_frame["right_click_menu"] = app_tk_frame.Right_Click_Menu(self)
        self.display_frame["game_ready"] = app_tk_frame.Game_Ready(self)
        self.display_frame["creat_world"] = app_tk_frame.Creat_World(self)
        self.display_frame["game_run"] = app_tk_frame.Game_Run(self)
        self.display_frame["game_terminal"] = app_tk_frame.Game_Terminal(self)
        self.display_frame["choose_expand"] = app_tk_frame.Choose_Expand(self)
        self.display_frame["expand_pack"] = app_tk_frame.Expand_Pack_Example(self)
        self.display_frame["setting_frame"] = app_tk_frame.Setting(self)
        self.display_frame["login_frame"] = app_tk_frame.Login(self)
        self.display_frame["policy_frame"] = app_tk_frame.Policy(self)
        self.display_frame["user_info"] = app_tk_frame.User_Info(self)
        self.set_display_frame("game_ready")

        if self.user_manager.save_data["open_app_count"] < 2 :
            aaa = tkinter.messagebox.askquestion('Title', '第一次使用\n是否需要阅读文档教程？\n(新手用户必看！！)', )
            if aaa == "yes" : self.open_browser("http://localhost:32323/tutorial/Instructions.html")

        if self.user_manager.save_data["open_app_count"] < 2 :
            aaa = tkinter.messagebox.askquestion('Title', '是否需要阅读常见疑问？\n(安卓用户必看！！)')
            if aaa == "yes" : self.open_browser("https://missing254.github.io/cs-tool/tool/Question/")

        self.user_manager.save_data["open_app_count"] += 1


    def set_paste_thread(self) :
        def aaa():
            while self.paset_thread_time : 
                self.paset_thread_time -= 1
                time.sleep(0.01)
        if self.paset_thread_time == 0 : 
            self.paset_thread_time = 10
            threading.Thread(target=aaa).start()
        self.paset_thread_time = 10

    def set_focus_input(self,event:tkinter.Event) :
        compont = event.widget
        if isinstance(compont,(tkinter.Text, tkinter.Entry, ttk.Entry)) : self.focus_input = compont
        else : self.focus_input = None ; return None

        def aaaa(event : tkinter.Event) :
            self.calltip_win.hidetip()
            if app_constants.jnius :
                inputMethodManager = app_constants.PythonActivity.getSystemService(app_constants.Context.INPUT_METHOD_SERVICE)
                isInputOpen = inputMethodManager.inputMethodWindowVisibleHeight
                if not isInputOpen : inputMethodManager.toggleSoftInput(0, 0)

        def bbbb(event : tkinter.Event) :
            try : 
                start_index = event.widget.index(tkinter.SEL_FIRST)
                end_index = event.widget.index(tkinter.SEL_LAST)
            except : pass
            else :
                if self.calltip_win.anchor_widget != event.widget : self.calltip_win.anchor_widget = event.widget
                aaa = "您选中了\n%s ~ %s"%(start_index,end_index)
                start_index = "%s.0" % tuple(start_index.split(".")[0])
                end_index = "%s.end" % tuple(end_index.split(".")[0])
                self.calltip_win.showtip(aaa,start_index,end_index)
                self.calltip_win.label.config(text=aaa)

        def cccc(event : tkinter.Event) :
            if event.keycode == -1 : self.set_paste_thread()
            if self.paset_thread_time and event.keycode != -1 : return 'break'

        if not hasattr(compont, "is_bind_click") :
            compont.bind("<Button-1>",aaaa,add="+")
            if app_constants.jnius : compont.bind("<KeyPress>",cccc,add="+")
            if hasattr(compont,"can_copy_tk_component") : compont.bind("<B1-Motion>",bbbb,add="+")
            compont.is_bind_click = True


    def set_display_frame(self, name:str) :
        if name not in self.display_frame : return
        if name == self.now_display_frame : return
        if self.now_display_frame != "" : self.display_frame[self.now_display_frame].pack_forget()
        if "expand_pack" in (self.now_display_frame, name) :
            test_flag = False
            for uuid,data in self.expand_pack_open_list.items() : #判断隶属的拓展包
                if data["frame"] != self.display_frame["expand_pack"] : continue
                test_flag = True ; break
            if test_flag and self.now_display_frame == "expand_pack" and name != "expand_pack" : #退出拓展包界面
                right_click_menu:app_tk_frame.Right_Click_Menu = self.display_frame["right_click_menu"]
                while right_click_menu.item_counter > 4 : right_click_menu.remove_item()
                if hasattr(data["object"],"exit_method") : data["object"].exit_method()
            if test_flag and self.now_display_frame != "expand_pack" and name == "expand_pack" :  #进入拓展包界面
                right_click_menu:app_tk_frame.Right_Click_Menu = self.display_frame["right_click_menu"]
                if right_click_menu.item_counter <= 4 and hasattr(data["module"], "Menu_set") : data["module"].Menu_set(right_click_menu)
                if hasattr(data["object"],"exit_method") : data["object"].exit_method()
        self.now_display_frame = name
        self.display_frame[self.now_display_frame].pack()

    def game_ready_or_run(self):
        if not self.game_process : self.set_display_frame("game_ready")
        else : self.set_display_frame("game_run")

    def user_was_login(self):
        if self.user_manager.get_account_info() : 
            json1 = self.user_manager.get_account_info()
            self.display_frame["user_info"].user_info_1.config(text=self.user_manager.save_data["user"]['account'])
            self.display_frame["user_info"].user_info_2.config(text=json1['creat_date'])
            self.display_frame["user_info"].user_info_3.config(text=json1['pay_point'])
            self.display_frame["user_info"].user_info_4.config(text=json1['challenge'])
            self.set_display_frame("user_info")
        else : self.set_display_frame("login_frame")

    def app_infomation(self, mode:str) :
        a = {"use":"使用条款","privacy":"隐私条款","about":"关于命令模拟器","open":"启动日志"}
        self.display_frame["policy_frame"].input_box4.config(wrap="char" if mode != "open" else "none")
        self.display_frame["policy_frame"].input_box4.delete("0.0","end")
        self.display_frame["policy_frame"].policy_title.config(text = a[mode])
        if mode == "use" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","use.txt"))
        elif mode == "privacy" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","privacy.txt"))
        elif mode == "about" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","about_app.txt"))
        elif mode == "open" : 
            text1 = "\n".join([i.log_text for i in self.initialization_log])
            if not any([i.is_alive() for i in self.initialization_process]) : 
                text1 += "\n初始化完毕，耗时%s秒" % (int(max([i.get_spend_time() for i in self.initialization_log]) * 1000) / 1000)
        self.display_frame["policy_frame"].input_box4.insert("end",text1)
        self.set_display_frame("policy_frame")


    def add_can_change_hight_component(self,component_list:list) :
        # 第一个为变高元素，其他为基准元素
        self.change_hight_component_list.append([-1,-1] + component_list)
        #List[ 像素每行, 最大行数, component_list ]

    def all_time_loop_event(self) :
        while 1 :
            try : 
                for i in list(self.expand_pack_open_list) :
                    if i not in self.expand_pack_open_list : continue
                    self.expand_pack_open_list[i]['object'].debug_windows = self
                    self.expand_pack_open_list[i]['object'].game_process = self.game_process
                    if hasattr(self.expand_pack_open_list[i]['object'],'loop_method') : 
                        self.expand_pack_open_list[i]['object'].loop_method()
            except : traceback.print_exc()
            for list1 in self.change_hight_component_list :
                try :
                    list1 : List[Union[int,int,tkinter.Text,tkinter.Text,tkinter.Text]]
                    if list1[0] == -1 : 
                        list1[0] = list1[2].winfo_reqheight() // list1[2].cget("height")
                        list1[1] = list1[2].cget("height")
                    try : blank_height = self.window.winfo_height() - self.button_bar.winfo_height()
                    except : blank_height = self.window.winfo_height()
                    for i in list1[3:] : blank_height -= i if isinstance(i,int) else i.winfo_reqheight()
                    if list1[2].cget("height") != min(list1[1], blank_height // list1[0] - 1) :
                        list1[2].config(height = min(list1[1], blank_height // list1[0] - 1))
                except : pass

            time.sleep(0.5)


    def post_data(self, data_1:bytes, pack_list:dict) :
        post_json = json.loads(data_1.decode('utf-8'))
        
        operation_json = {
            "expand_pack_run" : self.post_to_expand_pack,
        }
        
        if ("operation" not in post_json) : return {"state" : 1 , "msg" : "传输数据不合法"}
        if (post_json["operation"] not in operation_json) : return {"state" : 2 , "msg" : "指定操作不合法"}
        if (post_json["operation"] == "expand_pack_run") and ("pack_id" not in post_json) : return {"state" : 1 , "msg" : "传输数据不合法"}
        if (post_json["operation"] == "expand_pack_run" and post_json["pack_id"] not in pack_list) : return {"state" : 3 , "msg" : "无效的拓展包ID"}
        if (post_json["operation"] == "expand_pack_run" and post_json["pack_id"] not in self.expand_pack_open_list) : return {"state" : 4 , "msg" : "指定的拓展包未启动"}

        try : return operation_json[post_json["operation"]](post_json)
        except :
            traceback.print_exc()
            return {"state" : 5 , "msg" : traceback.format_exc()}

    def post_to_expand_pack(self,post_json:dict) : 
        if not hasattr(self.expand_pack_open_list[post_json["pack_id"]]['object'],"do_POST") : 
            return {"state" : 6 , "msg" : "拓展包并没有指定Post处理方法"}
        return self.expand_pack_open_list[post_json["pack_id"]]['object'].do_POST(post_json)


debug_windows = control_windows()
threading.Thread(target=debug_windows.all_time_loop_event).start()
debug_windows.window.mainloop()



