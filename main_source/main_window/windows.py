import webbrowser, os, types, urllib.parse, http.server, traceback, uuid
import threading, time, json, functools, tkinter, tkinter.messagebox
from tkinter import ttk
from typing import List, Dict, Union, Literal, TypedDict, Any

#自定义模块加载与设置
from . import constant as app_constants
from . import function as app_function
from . import display_ui as display_ui
import package.file_operation as file_IO
from .. import bedrock_edition as Minecraft_BE #模拟世界模块加载


class ExpandPackData(TypedDict) :
    dir_name: str
    frame: tkinter.Frame
    module: types.ModuleType
    object: object

class DisplayUI(TypedDict) :
    right_click_menu: display_ui.Global_Right_Click_Menu
    welcome_screen: display_ui.Welcome_Screen
    copy_char_tool: display_ui.Copy_Char_Tool
    find_minecraft_ID: display_ui.Find_Minecraft_ID
    structure_transfor: display_ui.BE_Structure_Tool
    mcworld_reader: display_ui.BE_World_Tool
    copy_file_command: display_ui.Copy_File_Command
    game_ready: display_ui.Game_Ready
    create_world: display_ui.Create_World
    game_run: display_ui.Game_Run
    gamerunning_setting: display_ui.GameRunning_Setting
    game_terminal: display_ui.Game_Terminal
    choose_expand: display_ui.Choose_Expand
    setting_frame: display_ui.Setting
    login_frame: display_ui.Login
    user_info: display_ui.User_Info
    policy_frame: display_ui.Policy
    log_display: display_ui.Log_Display


class HTTP_Request_Handler(http.server.SimpleHTTPRequestHandler) :

    def __init__(self, request, client_address, server, *,
                 directory=None, main_win:"control_windows"=None):
        if not isinstance(main_win, control_windows) : raise TypeError("HTTP服务器绑定的main_win对象不正确")
        self.main_thread_windows: control_windows = main_win
        super().__init__(request, client_address, server, directory=directory)


    def do_Get_Behiver(self, query_components:dict) :
        debug_windows = self.main_thread_windows

        def post_to_2Dstructure(type:Literal["structure", "world"]) :
            import base64
            Bind2DImage:bytes = None
            if type == "structure" : Bind2DImage = debug_windows.display_frame["structure_transfor"].view_2D_object
            elif type == "world" : Bind2DImage = debug_windows.display_frame["mcworld_reader"].view_2D_object

            if Bind2DImage is None : return {"state": 2 , "msg": "结构对象暂未加载"}
            base64_data = base64.b64encode(Bind2DImage).decode('utf-8')
            data_url = f"data:image/png;base64,{base64_data}"

            return data_url.encode('utf-8')

        pack_dir_name = None
        if 'pack' in query_components :
            pack_id = query_components['pack'][0]
            if pack_id not in debug_windows.expand_pack_open_list : return None
            else : pack_dir_name = debug_windows.expand_pack_open_list[pack_id]["dir_name"]

        if pack_dir_name and query_components.get("page", [None])[0] == "index" :
            path1 = os.path.join("expand_pack", pack_dir_name, "index.html")
            if not os.path.isfile(path1) : return None
            return file_IO.read_a_file(path1, "readbyte")
        elif pack_dir_name and query_components.get("page", [None])[0] == "help" :
            path1 = os.path.join("expand_pack", pack_dir_name, "help.html")
            if not os.path.isfile(path1) : return None
            return file_IO.read_a_file(path1, "readbyte")
        elif query_components.get("tempfile", [None])[0].__class__ is str :
            _uid = query_components.get("tempfile", [""])[0]
            if _uid not in self.server.temp_file : return None
            return self.server.temp_file[_uid]
        elif query_components.get("render", [None])[0] in {"StructureRender", "WorldRender", "CommandBlockRender"} :
            path1 = os.path.join("local_server", "tools", "StructureRender.html")
            if not os.path.isfile(path1) : return None
            render_type:str = query_components.get("render")[0]
            return file_IO.read_a_file(path1, "readbyte").replace(b"%Type%", render_type.encode())
        elif query_components.get("render", [None])[0] in {"Structure2DRender", "World2DRender"} :
            path1 = os.path.join("local_server", "tools", "StructurePlane.html")
            if not os.path.isfile(path1) : return None
            render_type = query_components.get("render")[0]
            struct_type = "structure" if render_type == "Structure2DRender" else "world"
            png_data = post_to_2Dstructure(struct_type)
            return file_IO.read_a_file(path1, "readbyte").replace(b"%ImageData%", png_data)

    def do_Post_Behiver(self, query_components:dict) :
        debug_windows = self.main_thread_windows

        def post_to_expand_pack(post_json:dict) -> Union[Dict[str, Any], bytes] : 
            pack_list = debug_windows.user_manager.save_data['install_pack_list']
            open_pack = debug_windows.expand_pack_open_list
            if "pack_id" not in post_json : return {"state": 1 , "msg": "传输数据不合法"}
            if post_json["pack_id"] not in pack_list : return {"state": 3 , "msg": "无效的拓展包ID"}
            if post_json["pack_id"] not in open_pack : return {"state": 4 , "msg": "指定的拓展包未启动"}
            if not hasattr(open_pack[post_json["pack_id"]]['object'], "do_POST") : 
                return {"state" : 6 , "msg" : "拓展包并没有指定Post处理方法"}
            return open_pack[post_json["pack_id"]]['object'].do_POST(post_json)

        def post_to_3Dstructure(render_type:str, post_json:dict) -> Union[Dict[str, Any], bytes] :
            BindViewObject:display_ui.__StructureView__ = None
            if render_type == "structure" : BindViewObject = debug_windows.display_frame["structure_transfor"].view_object
            elif render_type == "world" : BindViewObject = debug_windows.display_frame["mcworld_reader"].view_object
            elif render_type == "command_block" : BindViewObject = debug_windows.display_frame["gamerunning_setting"].view_object

            if BindViewObject is None : return {"state": 2 , "msg": "结构对象暂未加载"}
            if post_json.get("process", None) == "getSizePalette" :
                return {"size":BindViewObject.getSize(), "palette":BindViewObject.getPalette()}
            if post_json.get("process", None) == "getIndexData" :
                if not isinstance(post_json.get("index", None), int) : return {"state": 1 , "msg": "传输数据不合法(posX非整数)"}
                if not isinstance(post_json.get("read", None), int) : return {"state": 1 , "msg": "传输数据不合法(posZ非整数)"}
                if post_json.get("index", -1) < 0 : return {"state": 1 , "msg": "传输数据不合法(index < 0)"}
                if post_json.get("read", -1) < 0 : return {"state": 1 , "msg": "传输数据不合法(read < 0)"}
                return BindViewObject.getIndexData(post_json["index"], post_json["read"])

        operation_mode = {
            "expand_pack_run": post_to_expand_pack,
            "StructureRender": lambda e: post_to_3Dstructure("structure", e),
            "WorldRender": lambda e: post_to_3Dstructure("world", e),
            "CommandBlockRender": lambda e: post_to_3Dstructure("command_block", e)
        }

        OperationMode = query_components.get("operation", None)
        if (OperationMode not in operation_mode) : return {"state": 2 , "msg": "指定操作不合法"}

        try : return operation_mode[OperationMode](query_components)
        except : return {"state" : 5 , "msg" : traceback.format_exc()}


    def log_message(self, format, *args):
        return None

    def do_GET(self):
        url_obj = urllib.parse.urlparse(self.path)
        if url_obj.path == "/" and url_obj.query != "" :
            query_components = urllib.parse.parse_qs(url_obj.query)

            if ("render" in query_components) and \
               ("pack" in query_components and "page" in query_components) : 
                return None

            send_bytes = self.do_Get_Behiver(query_components)
            self.send_response(200)
            self.send_header('Content-type', 'texthtml')
            self.end_headers()
            self.wfile.write(send_bytes)
        else : super().do_GET()

    def do_POST(self):
        client_post_data = self.rfile.read(int(self.headers['content-length']))
        try : client_post_json = json.loads(client_post_data)
        except : client_post_json = {}

        if "operation" in client_post_json : ResponesData = self.do_Post_Behiver(client_post_json)
        else : ResponesData = {"state": 1 , "msg": "传输数据不合法"}

        self.send_response(200)
        if isinstance(ResponesData, bytes) : 
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write( ResponesData )
        else : 
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write( json.dumps(ResponesData, separators=(',', ':')).encode('utf-8'))

class HTTP_Custom_Server(http.server.ThreadingHTTPServer) :

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate = True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.temp_file: Dict[str, bytes] = {}

    def register_tempfile(self, content:Union[str, bytes]) -> str :
        if isinstance(content, str) : content = content.encode("utf-8")
        elif not isinstance(content, bytes) :
            raise TypeError(f"content 必须是 str 或 bytes，实际为 {type(content).__name__}")

        uid = str(uuid.uuid4())
        self.temp_file[uid] = content

        while len(self.temp_file) > 15 :
            oldest_uid = next(iter(self.temp_file))
            del self.temp_file[oldest_uid]

        return uid


class control_windows :

    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title('minecraft命令调试器')
        self.window.geometry('300x600')
        http_Resquest = functools.partial(HTTP_Request_Handler, directory="local_server", main_win=self)

        self.now_display_frame:str = ""                                                 #当前显示的UI ID
        self.tutorial_mode:bool = False                                                 #是否在教程模式
        self.focus_input:Union[tkinter.Entry, tkinter.Text, ttk.Entry] = None           #当前交点输入对象
        self.platform:Literal["windows", "android"] = app_constants.SoftwarePlatform    #用户平台系统类型
        self.http_server = HTTP_Custom_Server(('', 32323), http_Resquest)               #主线程开启的HTTP服务器
        self.game_process:Minecraft_BE.GameClass.MinecraftSimulator = None              #模拟世界线程

        self.display_frame:DisplayUI = {}
        self.expand_pack_open_list:Dict[str, ExpandPackData] = {}
        self.change_hight_component_list:List[Union[int, tkinter.Misc]] = []            #可变高度组件列表
        
        self.RightClickMenu = display_ui.Global_Right_Click_Menu(self.window)
        Announcement = display_ui.Announcement(self)
        Announcement.pack()

        self.user_manager = app_function.user_manager() #用户管理
        self.initialization_log = [app_function.initialization_log() for i in range(5)]
        self.initialization_process:List[threading.Thread] = [
            threading.Thread(target=app_function.get_app_infomation_and_login, 
                args=(Announcement, self.user_manager, self.initialization_log[0]))
        ]

        for i in self.initialization_process : i.start()
        self.window.protocol("WM_DELETE_WINDOW", self.window_exit)
        self.window.bind("<Button-3>", lambda e : self.RightClickMenu.post(
            e.x_root, e.y_root-self.RightClickMenu.winfo_reqheight()))
        threading.Thread(target=self.http_server.serve_forever, daemon=True).start()
        threading.Thread(target=self.all_time_loop_event, daemon=True).start()


    def create_windows(self) :
        self.button_bar = display_ui.Bottom_Bar(self)
        self.button_bar.pack(side="bottom")
        self.expend_pack_showtips = tkinter.Label(self.window, text="进入拓展包后，点击下方“返回”字体\n即可返回“拓展包管理”界面", 
            fg="#6376FF", font=display_ui.tk_tool.get_default_font(10))

        self.display_frame["welcome_screen"] = display_ui.Welcome_Screen(self)
        self.display_frame["copy_char_tool"] = display_ui.Copy_Char_Tool(self)
        self.display_frame["find_minecraft_ID"] = display_ui.Find_Minecraft_ID(self)
        self.display_frame["structure_transfor"] = display_ui.BE_Structure_Tool(self)
        self.display_frame["mcworld_reader"] = display_ui.BE_World_Tool(self)
        self.display_frame["copy_file_command"] = display_ui.Copy_File_Command(self)

        self.display_frame["game_ready"] = display_ui.Game_Ready(self)
        self.display_frame["create_world"] = display_ui.Create_World(self)
        self.display_frame["game_run"] = display_ui.Game_Run(self)
        self.display_frame["gamerunning_setting"] = display_ui.GameRunning_Setting(self)
        self.display_frame["game_terminal"] = display_ui.Game_Terminal(self)

        self.display_frame["choose_expand"] = display_ui.Choose_Expand(self)

        self.display_frame["setting_frame"] = display_ui.Setting(self)
        self.display_frame["login_frame"] = display_ui.Login(self)
        self.display_frame["user_info"] = display_ui.User_Info(self)
        self.display_frame["policy_frame"] = display_ui.Policy(self)
        self.display_frame["log_display"] = display_ui.Log_Display(self)

        self.set_display_frame("welcome_screen")

        self.user_manager.save_data["open_app_count"] += 1
        if self.user_manager.save_data["open_app_count"] == 1 :
            yesorno = tkinter.messagebox.askquestion("question", "看起来您是第一次使用\n需要熟悉软件如何使用吗？\n(新用户请务必点击确定！)")
            if self.platform == "android" and yesorno == "yes" : app_function.Beginner_Tutorial(self, False)
            elif self.platform == "windows" and yesorno == "yes" : webbrowser.open("http://localhost:32323/tutorial/Instructions.html")

    def window_exit(self) :
        threading.Thread(target=lambda:[time.sleep(10), os._exit(0)]).start()
        if self.game_process is not None : 
            self.display_frame["game_run"].exit_world()
        time.sleep(0.5)
        os._exit(0)


    def set_focus_input(self, event:tkinter.Event) :
        componemt = event.widget
        if isinstance(componemt, (tkinter.Text, tkinter.Entry, ttk.Entry)) : self.focus_input = componemt
        else : self.focus_input = None ; return None

        if not hasattr(componemt, "is_bind_click") :
            if app_constants.jnius : 
                event_class = app_function.Text_Bind_Events(self, componemt)
                componemt.bind("<ButtonRelease-1>", event_class.left_click_release_event, add="+")
                componemt.bind("<B1-Motion>", event_class.left_click_motion_event, add="+")
                componemt.bind("<KeyPress>", event_class.key_press_event, add="+")
            componemt.is_bind_click = True

    def set_display_frame(self, name:str) :
        if name == "forget_all" : 
            if self.now_display_frame in self.display_frame :
                self.display_frame[self.now_display_frame].pack_forget()
            self.now_display_frame = ""
            return None

        if name == "choose_expand" and self.now_display_frame == "expand_pack" : pass
        elif name == "choose_expand" and "expand_pack" in self.display_frame: name = "expand_pack"
        else : pass

        if name not in self.display_frame or name == self.now_display_frame: return None
        if self.now_display_frame != "" : self.display_frame[self.now_display_frame].pack_forget()

        if "expand_pack" in (self.now_display_frame, name) :
            test_flag = False
            for uuid, data in self.expand_pack_open_list.items() : #判断隶属的拓展包
                if data["frame"] != self.display_frame["expand_pack"] : continue
                test_flag = True ; break

            right_click_menu = self.RightClickMenu
            if test_flag and self.now_display_frame == "expand_pack" and name != "expand_pack" : #退出拓展包界面
                while right_click_menu.item_counter : right_click_menu.remove_item()
                if hasattr(data["object"], "exit_method") : data["object"].exit_method()
                self.button_bar.exit_expand_pack()
            if test_flag and self.now_display_frame != "expand_pack" and name == "expand_pack" :  #进入拓展包界面
                if hasattr(data["module"], "Menu_set") : data["module"].Menu_set(right_click_menu)
                if hasattr(data["object"], "exit_method") : data["object"].exit_method()
                self.button_bar.inter_expand_pack()

        self.display_frame[name].pack()
        self.now_display_frame = name
        if name == "choose_expand" : self.expend_pack_showtips.pack(side="bottom")
        else : self.expend_pack_showtips.pack_forget()
        self.focus_input = None


    def display_simulator_UI(self) :
        self.button_bar.set_menu_text(1)
        if not self.game_process : self.set_display_frame("game_ready")
        else : self.set_display_frame("game_run")

    def display_userdata_UI(self):
        account_data = self.user_manager.get_account(False)
        account_info = self.user_manager.get_account_info()
        if account_data and account_info : 
            self.display_frame["user_info"].set_display_userdata(
            account_data['account'], account_info)
            self.set_display_frame("user_info")
        else : self.set_display_frame("login_frame")

    def app_infomation(self, mode:str) :
        self.display_frame["policy_frame"].set_display_content(mode)
        self.set_display_frame("policy_frame")

    def set_error_log(self, *arg, **karg) :
        self.display_frame["log_display"].set_log(*arg, **karg)
        self.set_display_frame("log_display")


    def get_expand_pack_class_object(self, uuid:str) -> object :
        a = self.expand_pack_open_list.get(uuid, None)
        if a is None : return None
        return a.get('object')

    def get_display_expand_pack(self) -> ExpandPackData:
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
            for i in list(self.expand_pack_open_list) :
                try : 
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
            
            if "copy_file_command" in self.display_frame : self.display_frame["copy_file_command"].__loop__()
            if "structure_transfor" in self.display_frame : self.display_frame["structure_transfor"].__loop__()
            if "mcworld_reader" in self.display_frame : self.display_frame["mcworld_reader"].__loop__()
            time.sleep(0.5)

