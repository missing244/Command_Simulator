#!/usr/bin/python
# -*- coding: UTF-8 -*-

#原生模块加载与设置
from idlelib.calltip_w import CalltipWindow
import http.server, ssl, importlib
import json, tkinter, tkinter.font, tkinter.messagebox, time,threading, sys, gzip, gc
import platform, os, types, traceback, webbrowser, re, functools
from tkinter import ttk
from typing import List,Dict,Union,Literal
ssl._create_default_https_context = ssl._create_unverified_context

#删除旧文件
import main_source.main_window.update_change as update_change

#自定义模块加载与设置
import main_source.main_window.constant as app_constants
import main_source.main_window.function as app_function
import main_source.main_window.tk_frame as app_tk_frame
import main_source.package.file_operation as file_IO

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
                    if "pack" not in query_components or "page" not in query_components : return None
                    if query_components['pack'][0] not in debug_windows.expand_pack_open_list : return None
                    
                    pack_dir_name = debug_windows.expand_pack_open_list[query_components['pack'][0]]["dir_name"]
                    if query_components["page"][0] == "index" :
                        path1 = os.path.join("expand_pack", pack_dir_name, "index.html")
                        if not(os.path.exists(path1) and os.path.isfile(path1)) : return None
                        send_bytes = file_IO.read_a_file(path1,"readbyte")
                    elif query_components["page"][0] == "help" :
                        path1 = os.path.join("expand_pack", pack_dir_name, "help.html")
                        if not(os.path.exists(path1) and os.path.isfile(path1)) : return None
                        send_bytes = file_IO.read_a_file(path1,"readbyte")

                    self.send_response(200)
                    self.send_header('Content-type', 'texthtml')
                    self.end_headers()
                    self.wfile.write(send_bytes)
                else : super().do_GET()

            def do_POST(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Encoding', 'gzip')
                self.end_headers()
                datas = self.rfile.read(int(self.headers['content-length']))
                respones = debug_windows.post_data(datas, debug_windows.user_manager.save_data['install_pack_list'])
                self.wfile.write(gzip.compress(json.dumps(respones,separators=(',', ':'),
                    default=Minecraft_BE.DataSave.encoding).encode('utf-8')))

        server_address = ('', 32323)
        http_Resquest = functools.partial(http_Resquest, directory="html_output")
        httpd = server_class(server_address, http_Resquest)
        httpd.serve_forever()
    threading.Thread(target=http_server_create).start()

    def listen_cmd_input() :
        while app_constants.debug_testing : 
            text1 = input(">>> ")
            aaaa = globals()
            a_11 = time.time()
            try : compile(text1,"","eval")
            except Exception as e : 
                try : exec(text1, aaaa, aaaa)
                except : traceback.print_exc()
            else :
                try : print(eval(text1, aaaa, aaaa))
                except : traceback.print_exc()
            print('时间：%s' % str(time.time() - a_11))
    threading.Thread(target=listen_cmd_input).start()



class control_windows :

    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title('minecraft命令调试器')
        self.window.geometry('300x600')
        self.calltip_win = CalltipWindow(self.window)

        self.display_frame:Dict[str,tkinter.Frame] = {}
        self.now_display_frame:str = ""
        self.focus_input:Union[tkinter.Entry,tkinter.Text,ttk.Entry] = None
        self.expand_pack_open_list:Dict[str,Dict[Literal["dir_name","frame","module","object"],
            Union[str,tkinter.Frame,types.ModuleType,object]]] = {}

        self.change_hight_component_list = [] #可变高度组件列表
        self.paset_thread_time:int = 0  #输入降频计时
        self.tutorial_mode:bool = False  #是否在教程模式
        self.platform:Literal["windows","android"] = None #系统名称
        system_info = platform.uname()
        if system_info.system.lower() == 'windows' : self.platform = 'windows'
        elif system_info.system.lower() == 'linux' and system_info.machine == "aarch64" : self.platform = 'android'

        Announcement = app_tk_frame.Announcement(self)
        Announcement.pack()

        self.user_manager = app_function.user_manager() #用户管理
        self.initialization_log = [app_function.initialization_log() for i in range(5)]
        self.initialization_process:List[threading.Thread] = [
            threading.Thread(target=app_function.get_app_infomation_and_login, args=(Announcement, self.user_manager, self.initialization_log[0])),
            threading.Thread(target=app_function.flash_minecraft_id, args=(self.initialization_log[1], )),
            threading.Thread(target=app_function.flash_minecraft_source, args=(self.user_manager, self.initialization_log[2])),
            threading.Thread(target=app_function.check_leveldb_c_extension, args=(self.platform, self.initialization_log[3])),
            threading.Thread(target=app_function.check_brotli_c_extension, args=(self.platform, self.initialization_log[4])),
        ]
        self.game_process:Minecraft_BE.RunTime.minecraft_thread = None #模拟世界线程

        #self.windows_constant()
        for i in self.initialization_process : i.start()
        self.window.protocol("WM_DELETE_WINDOW", self.window_exit)


    def creat_windows(self):
        self.button_bar = app_tk_frame.Bottom_Bar(self)
        self.button_bar.pack(side="bottom")
        self.display_frame["right_click_menu"] = app_tk_frame.Global_Right_Click_Menu(self)

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
        self.display_frame["log_display"] = app_tk_frame.Log_Display(self)
        self.set_display_frame("game_ready")

        self.user_manager.save_data["open_app_count"] += 1
        if self.user_manager.save_data["open_app_count"] == 1 and self.platform == "android" :
            yesorno = tkinter.messagebox.askquestion("question", "看起来您是第一次打开\n需要熟悉软件如何使用吗？(新用户请务必点击确定！)")
            if self.platform == "android" and yesorno == "yes" : app_function.Beginner_Tutorial(self, False)
            elif self.platform == "windows" and yesorno == "yes" : webbrowser.open("http://localhost:32323/tutorial/Instructions.html")
        
        self.bind_events()

    def bind_events(self):
        self.window.bind("<Button-3>", lambda e : self.display_frame["right_click_menu"].post(
            e.x_root, e.y_root-self.display_frame["right_click_menu"].winfo_reqheight()))

    def window_exit(self) :
        threading.Thread(target=lambda:[time.sleep(10), os._exit(0)]).start()
        if self.game_process is not None :
            text = self.display_frame["game_run"].input_box1.get("0.0","end")[:-1]
            self.game_process.world_infomation['terminal_command'] = text
            self.game_process.__exit_world__()
        time.sleep(0.5)
        os._exit(0)


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

        def cccc(event : tkinter.Event) :
            if event.keycode == -1 : self.set_paste_thread()
            if self.paset_thread_time and event.keycode != -1 : return 'break'

        if not hasattr(compont, "is_bind_click") :
            if app_constants.jnius : 
                event_class = app_function.Text_Bind_Events(self, compont)
                compont.bind("<ButtonRelease-1>", event_class.left_click_release_event, add="+")
                compont.bind("<B1-Motion>", event_class.left_click_motion_event, add="+")
                compont.bind("<KeyPress>", cccc, add="+")
                compont.bind("<KeyPress>", event_class.key_press_event, add="+")
            compont.is_bind_click = True


    def set_display_frame(self, name:str) :
        if name == "forget_all" : 
            if self.now_display_frame in self.display_frame :
                self.display_frame[self.now_display_frame].pack_forget()
            self.now_display_frame = ""
            return None

        if name not in self.display_frame or name == self.now_display_frame: return None
        if self.now_display_frame != "" : self.display_frame[self.now_display_frame].pack_forget()
        if "expand_pack" in (self.now_display_frame, name) :
            test_flag = False
            for uuid,data in self.expand_pack_open_list.items() : #判断隶属的拓展包
                if data["frame"] != self.display_frame["expand_pack"] : continue
                test_flag = True ; break

            if test_flag and self.now_display_frame == "expand_pack" and name != "expand_pack" : #退出拓展包界面
                right_click_menu:app_tk_frame.Global_Right_Click_Menu = self.display_frame["right_click_menu"]
                while right_click_menu.item_counter > 4 : right_click_menu.remove_item()
                if hasattr(data["object"],"exit_method") : data["object"].exit_method()
            if test_flag and self.now_display_frame != "expand_pack" and name == "expand_pack" :  #进入拓展包界面
                right_click_menu:app_tk_frame.Global_Right_Click_Menu = self.display_frame["right_click_menu"]
                if right_click_menu.item_counter <= 4 and hasattr(data["module"], "Menu_set") : data["module"].Menu_set(right_click_menu)
                if hasattr(data["object"],"exit_method") : data["object"].exit_method()
        self.now_display_frame = name
        self.display_frame[self.now_display_frame].pack()
        self.focus_input = None

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
        self.display_frame["policy_frame"].notes.config(text = "")
        if mode == "use" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","use.txt"))
        elif mode == "privacy" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","privacy.txt"))
        elif mode == "about" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","about_app.txt"))
        elif mode == "open" : 
            self.display_frame["policy_frame"].notes.config(text = "重新进入 “启动日志” 即可刷新内容")
            text1 = "\n".join([i.log_text for i in self.initialization_log])
            if not any([i.is_alive() for i in self.initialization_process]) : 
                text1 += "\n初始化完毕，耗时%s秒" % (int(max([i.get_spend_time() for i in self.initialization_log]) * 1000) / 1000)
        self.display_frame["policy_frame"].input_box4.insert("end",text1)
        self.set_display_frame("policy_frame")

    def set_error_log(self, *arg, **karg) :
        self.display_frame["log_display"].set_log(*arg, **karg)


    def get_expand_pack_class_object(self,uuid:str) -> object :
        a = self.expand_pack_open_list.get(uuid, None)
        if a is None : return None
        return a.get('object')

    def get_display_expand_pack_record(self) :
        if self.now_display_frame != "expand_pack" : return None

        saves = None
        for packUUID in self.expand_pack_open_list : 
            if self.display_frame["expand_pack"] is not self.expand_pack_open_list[packUUID]["frame"] : continue
            saves = self.expand_pack_open_list[packUUID]
        return saves

    def add_can_change_hight_component(self,component_list:list) :
        # 第一个为变高元素，其他为基准元素
        self.change_hight_component_list.append([-1,-1] + component_list)
        #List[ 像素每行, 最大行数, component_list ]

    def all_time_loop_event(self) :
        will_remove_can_change_hight_component:List[int] = []
        while 1 :
            #拓展包循环事件部分
            try : 
                for i in list(self.expand_pack_open_list) :
                    if i not in self.expand_pack_open_list : continue
                    self.expand_pack_open_list[i]['object'].main_win = self
                    self.expand_pack_open_list[i]['object'].game_process = self.game_process
                    if hasattr(self.expand_pack_open_list[i]['object'],'loop_method') : 
                        self.expand_pack_open_list[i]['object'].loop_method()
            except : traceback.print_exc()
            #变高组件循环事件部分
            for index, list1 in enumerate(self.change_hight_component_list.copy()) :
                if not list1[2].winfo_exists() : 
                    will_remove_can_change_hight_component.append(index) ; continue
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
            if len(will_remove_can_change_hight_component) :
                will_remove_can_change_hight_component.reverse()
                for i in will_remove_can_change_hight_component : self.change_hight_component_list.pop(i)
                will_remove_can_change_hight_component.clear()
            time.sleep(0.5)


    def post_data(self, data_1:bytes, pack_list:dict) :
        post_json = json.loads(data_1.decode('utf-8'))
        
        operation_json = {
            "expand_pack_run": self.post_to_expand_pack,
        }
        
        if ("operation" not in post_json) : return {"state": 1 , "msg": "传输数据不合法"}
        if (post_json["operation"] not in operation_json) : return {"state": 2 , "msg": "指定操作不合法"}
        if (post_json["operation"] == "expand_pack_run") and ("pack_id" not in post_json) : return {"state": 1 , "msg": "传输数据不合法"}
        if (post_json["operation"] == "expand_pack_run" and post_json["pack_id"] not in pack_list) : return {"state": 3 , "msg": "无效的拓展包ID"}
        if (post_json["operation"] == "expand_pack_run" and post_json["pack_id"] not in self.expand_pack_open_list) : return {"state": 4 , "msg": "指定的拓展包未启动"}

        try : return operation_json[post_json["operation"]](post_json)
        except :
            traceback.print_exc()
            return {"state" : 5 , "msg" : traceback.format_exc()}

    def post_to_expand_pack(self, post_json:dict) : 
        if not hasattr(self.expand_pack_open_list[post_json["pack_id"]]['object'],"do_POST") : 
            return {"state" : 6 , "msg" : "拓展包并没有指定Post处理方法"}
        return self.expand_pack_open_list[post_json["pack_id"]]['object'].do_POST(post_json)





debug_windows = control_windows()
threading.Thread(target=debug_windows.all_time_loop_event).start()
debug_windows.window.mainloop()

Minecraft_BE.Command_Compile_Dict_Save
importlib.reload(Minecraft_BE.Command_Tokenizer_Compiler(debug_windows.game_process, "aaaa", (1,20,60)))
importlib.reload(Minecraft_BE.CommandCompiler.Command1)
#debug_windows.game_process.minecraft_chunk.loading_chunk["overworld"][(0,0)]
debug_windows.game_process.minecraft_chunk.player
debug_windows.game_process.minecraft_ident.functions.keys()

# //[a-zA-Z \\+->:_.'\\",~0-9()]{0,}   update_pack\bedrock_edition\**\**\**.json
debug_windows.get_display_expand_pack_record()
