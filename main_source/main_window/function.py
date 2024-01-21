import os,traceback,json,time,threading,re,base64,zlib
import main_source.package.file_operation as FileOperation
from typing import List,Literal,Union
from tkinter import ttk ; import tkinter ; import tkinter.messagebox
import main_source.package.connent_API as connent_API

import main_source.main_window.constant as app_constant
import main_source.package.tk_tool as tk_tool

class user_manager :

    save_timestemp = 0
    save_path = os.path.join("save_world", "user_data.data")
    save_data = {} ; info_update = False
    save_data_template = {
        "cookies": {"api_web_cookie":""}, 
        "online_get": {}, 
        "user": {"account":None, "pass_code":None, "data":None},
        "open_app_count": 0,
        "install_pack_list": {},
    }
    login_msg_match = re.compile("<login_msg>[\u0000-\uffff]+</login_msg>")

    def __init__(self) :
        if FileOperation.is_file(self.save_path) :
            try : self.save_data = json.load(fp=open(self.save_path, "r", encoding="utf-8"))
            except : self.save_data = self.save_data_template
        else : self.save_data = self.save_data_template

        if "online_get" not in self.save_data : self.save_data["online_get"] = {}
        if "install_pack_list" not in self.save_data : self.save_data["install_pack_list"] = {}

        if "cookies" not in self.save_data : self.save_data["cookies"] = {"api_web_cookie":""}
        if "api_web_cookie" not in self.save_data["cookies"] : self.save_data["cookies"]["api_web_cookie"] = ""

        if "user" not in self.save_data : self.save_data["user"] = {"account":None, "password":None, "data":None}
        if "account" not in self.save_data["user"] : self.save_data["user"]["account"] = None
        if "pass_code" not in self.save_data["user"] : self.save_data["user"]["pass_code"] = None
        if "data" not in self.save_data["user"] : self.save_data["user"]["data"] = None

        self.save_timestemp = time.time() + 600
        threading.Thread(target=self.save_thread).start()
    
    def save_thread(self) :
        while 1 :
            if time.time() > self.save_timestemp : 
                self.write_back()
                self.save_timestemp = time.time() + 600
            time.sleep(6)

    def write_back(self) :
        json.dump(self.save_data, fp=open(self.save_path, "w+", encoding="utf-8"), indent=4)

    def get_account(self) : 
        json1:dict = self.save_data["user"]
        if not(json1.get("account",None) and json1.get("pass_code",None)) : 
            self.login_out_account() ; return None
        return base64.b64encode(
            json.dumps({"account":json1["account"], "pass_code":json1["pass_code"]}).encode("utf-8")
        ).decode("utf-8")

    def login_out_account(self) :
        self.save_data["user"] = {"account":None, "pass_code":None, "data":None}
        self.write_back()

    def login_account(self, account:str, passcode:str, request_msg:str) :
        match_request_msg = self.login_msg_match.search(request_msg)
        if match_request_msg is None : self.login_out_account() ; return None
        account_log_msg = match_request_msg.group().replace("<login_msg>","").replace("</login_msg>","")

        try : msg_json = json.loads(account_log_msg)
        except : self.login_out_account() ; return None

        if ('stat_code' not in msg_json) or msg_json['stat_code'] > 0 : self.login_out_account() ; return None
        
        if account : self.save_data["user"]["account"] = account
        if passcode : self.save_data["user"]["pass_code"] = passcode
        self.save_data["user"]['data'] = msg_json["server_back"]
        self.write_back()
        return True

    def get_account_info(self) :
        return self.save_data["user"].get("data", None)

class initialization_log :

    def __repr__(self) -> str:
        return str(self.log_text)

    def __init__ (self):
        self.log_text = ""
        self.time_start = time.time()
        self.time_end = 0

    def write_log(self, text:str, space_count:int=0):
        self.log_text += (" " * space_count) + text + "\n"

    def set_time_end(self) :
        self.time_end = time.time()

    def get_spend_time(self) :
        return self.time_end - self.time_start

class Text_Bind_Events :

    class Local_Right_Click_Menu_1 :

        def __init__(self, main_win, **karg) -> None:
            self.main_win = main_win
            self.is_post = False
            self.last_post_x = 0 ; self.last_post_y = 0

            list1 = {'删除':lambda:self.mode_using("clear"), "剪切":lambda:self.mode_using("cut"),
                     '复制':lambda:self.mode_using("copy"),  '粘贴':lambda:self.mode_using("paste")}
            self.menu_list:List[tkinter.Menu] = []
            for key,value in list1.items() :
                Menu = tkinter.Menu(main_win.window, tearoff=False, font=tk_tool.get_default_font(10), **karg)
                Menu.add_command(label=key, command=value)
                self.menu_list.append(Menu)
                Menu.update()
            if app_constant.jnius : 
                Menu = tkinter.Menu(main_win.window, tearoff=False, font=tk_tool.get_default_font(10), **karg)
                Menu.add_command(label='键盘', command=lambda:self.mode_using("weakup_keyboard"))
                self.menu_list.append(Menu)
            self.winfo_reqheight = self.menu_list[0].winfo_reqwidth()

        def mode_using(self, mode) :
            focus_input = self.main_win.focus_input
            mode_using(focus_input, mode)
            for index,item in enumerate(self.menu_list) : item.unpost()
        
        def post(self, x:int, y:int) :
            only_width = self.winfo_reqheight
            half_width = self.winfo_reqheight * len(self.menu_list) // 2
            start_x = x - half_width
            for index,item in enumerate(self.menu_list) : item.post(start_x + only_width * index, y)
            self.is_post = True
            self.last_post_x = x ; self.last_post_y = y

        def unpost(self) :
            if not self.is_post : return None
            for index,item in enumerate(self.menu_list) : item.unpost()
            self.is_post = False

        def set_other_menu(self, other_menu) :
            self.other_menu = other_menu

    class Local_Right_Click_Menu_2 :

        def __init__(self, main_win, **karg) -> None :
            self.main_win = main_win
            self.is_post = False
            self.last_post_x = 0 ; self.last_post_y = 0

            list1 = {"回车":lambda:self.mode_using("return"), '粘贴':lambda:self.mode_using("paste"),
                     "行首":lambda:self.mode_using("jump_line_start"), '行尾':lambda:self.mode_using("jump_line_end"),
                     "选行":lambda:self.mode_using("line_select")}
            self.menu_list:List[tkinter.Menu] = []
            for key,value in list1.items() :
                Menu = tkinter.Menu(main_win.window, tearoff=False, font=tk_tool.get_default_font(10), **karg)
                Menu.add_command(label=key, command=value)
                self.menu_list.append(Menu)
                Menu.update()
            self.winfo_reqwidth = self.menu_list[0].winfo_reqwidth()

        def mode_using(self, mode) :
            focus_input = self.main_win.focus_input
            mode_using(focus_input, mode)
            for index,item in enumerate(self.menu_list) : item.unpost()
            if mode == "line_select" : self.other_menu.post(self.last_post_x, self.last_post_y)

        def post(self, x:int, y:int) :
            only_width = self.winfo_reqwidth
            half_width = self.winfo_reqwidth * len(self.menu_list) // 2
            start_x = x - half_width
            for index,item in enumerate(self.menu_list) : item.post(start_x + only_width * index, y)
            self.is_post = True
            self.last_post_x = x ; self.last_post_y = y

        def unpost(self) :
            if not self.is_post : return None
            for index,item in enumerate(self.menu_list) : item.unpost()
            self.is_post = False

        def set_other_menu(self, other_menu) :
            self.other_menu = other_menu

    def __init__(self, main_win, Text:tkinter.Text) -> None :
        import main_source.main_window.constant as app_constant
        import main_source.main_window.tk_frame as tk_frame
        self.main_win = main_win
        self.app_constants = app_constant
        self.Right_Click_Menu_1 = self.Local_Right_Click_Menu_1(main_win)
        self.Right_Click_Menu_2 = self.Local_Right_Click_Menu_2(main_win)
        self.Right_Click_Menu_1.set_other_menu(self.Right_Click_Menu_2)
        self.Right_Click_Menu_2.set_other_menu(self.Right_Click_Menu_1)
        self.Text = Text

        self.is_left_motion = False
        self.is_have_select = False
        self.insert_pos_save = None
    
    def update_INSERT_pos(self, widget:Union[tkinter.Text, tkinter.Entry, ttk.Entry]) :
        if isinstance(widget, tkinter.Text) : insert_pos = list(widget.bbox(tkinter.INSERT))[0:2]
        else : insert_pos = [widget.index(tkinter.INSERT)*40, widget.winfo_rooty()]
        
        if self.insert_pos_save is None : self.insert_pos_save = insert_pos ; return None
        if not(self.insert_pos_save[0]-100 <= insert_pos[0] <= self.insert_pos_save[0]+100) :
            self.insert_pos_save = insert_pos ; return None
        if not(self.insert_pos_save[1]-40 <= insert_pos[1] <= self.insert_pos_save[1]+40) :
            self.insert_pos_save = insert_pos ; return None
        Menu = self.Right_Click_Menu_2
        if isinstance(widget, tkinter.Text) : x1,y1,x2,y2 = widget.bbox(tkinter.INSERT)
        else : y1 = widget.winfo_rooty()
        x1 = self.main_win.window.winfo_width() // 2
        Menu.post(x1, y1 - (widget.winfo_height()-40 if isinstance(widget, (tkinter.Entry, ttk.Entry)) else 0))


    def left_click_motion_event(self,e:tkinter.Event) :
        if not self.is_left_motion :
            inputMethodManager = self.app_constants.PythonActivity.mActivity.getSystemService(
                self.app_constants.Context.INPUT_METHOD_SERVICE)
            isInputOpen = inputMethodManager.inputMethodWindowVisibleHeight
            if isInputOpen : inputMethodManager.toggleSoftInput(0, 0)
        self.is_left_motion = True

    def left_click_release_event(self, e:tkinter.Event) :
        #显示选中文字的菜单
        if self.is_left_motion and ((isinstance(e.widget, tkinter.Text) and e.widget.tag_ranges("sel")) or (
        isinstance(e.widget, (tkinter.Entry, ttk.Entry)) and e.widget.select_present())) : 
            Menu = self.Right_Click_Menu_1
            if isinstance(e.widget, tkinter.Text) : x1,y1,x2,y2 = e.widget.bbox(tkinter.SEL_FIRST)
            else : x1,y1 = e.widget.winfo_rootx(), e.widget.winfo_rooty()
            x1 = self.main_win.window.winfo_width() // 2
            Menu.post(x1, y1 - (e.widget.winfo_height()+20 if isinstance(e.widget, (tkinter.Entry, ttk.Entry)) else 0))
            self.is_have_select=True
            self.is_left_motion = False
            return None

        if self.is_left_motion : self.is_left_motion = False ; return None
        if self.is_have_select : self.is_have_select = False ; return None
        if isinstance(e,tkinter.Event) : self.update_INSERT_pos(e.widget)

        inputMethodManager = self.app_constants.PythonActivity.mActivity.getSystemService(
            self.app_constants.Context.INPUT_METHOD_SERVICE)
        isInputOpen = inputMethodManager.inputMethodWindowVisibleHeight
        if not isInputOpen : inputMethodManager.toggleSoftInput(0, 0)

    def key_press_event(self, e:tkinter.Event) :
        self.Right_Click_Menu_1.unpost()
        self.Right_Click_Menu_2.unpost()



def mode_using(focus_input:Union[tkinter.Entry,tkinter.Text,ttk.Entry], mode, word=None) : 
    import main_source.main_window.constant as app_constant
    if focus_input is None : return None

    if mode == "select_all" : focus_input.event_generate("<<SelectAll>>")
    elif mode == "cut" : 
        focus_input.event_generate("<<Cut>>")
        focus_input.event_generate("<ButtonRelease>")
    elif mode == "copy" : focus_input.event_generate("<<Copy>>")
    elif mode == "paste" : 
        try : focus_input.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
        except : pass
        if app_constant.PythonActivity and app_constant.Context :
            clipboard = app_constant.PythonActivity.mActivity.getSystemService(app_constant.Context.CLIPBOARD_SERVICE)
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
    elif mode == "clear_all" : 
        focus_input.event_generate("<<SelectAll>>")
        focus_input.event_generate("<<Clear>>")
    elif mode == "clear" : 
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
    elif mode == "weakup_keyboard" :
        import main_source.main_window.constant as app_constants
        inputMethodManager = app_constants.PythonActivity.mActivity.getSystemService(
            app_constants.Context.INPUT_METHOD_SERVICE)
        isInputOpen = inputMethodManager.inputMethodWindowVisibleHeight
        if not isInputOpen : inputMethodManager.toggleSoftInput(0, 0)
    focus_input.focus_set()



def get_app_infomation_and_login(Announcement, user:user_manager, log:initialization_log) :
    import main_source.main_window.constant as app_constant

    log.write_log("正在获取软件信息...")
    def updata_info() :
        response2 = connent_API.request_url_without_error(connent_API.APP_INFO_URL)
        if response2 is None : 
            Announcement.set_notification(None)
            log.write_log("软件信息获取失败", 2) ; user.info_update = True ; return True
        response2 = connent_API.transfor_qq_share(response2.decode("utf-8"))
        response2 = zlib.decompress(base64.b64decode(response2.encode("utf-8"))).decode("utf-8")
        response2 = json.loads(response2)
        user.save_data['online_get'] = response2

        Announcement.set_notification(response2['notification'])
        connent_API.get_online_api(response2['api'])
        user.info_update = True ; log.write_log("软件信息同步完成",2) ; return True

    def test_network() :
        request1 = connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL)
        if request1 is None : log.write_log("网络验证失败",2) ; return False
        else : return True

    def get_info() :
        if app_constant.debug_testing : return None
        data1 = {"userdata":user.get_account()} if (user.get_account() is not None) else None
        request1 = connent_API.request_url_without_error(connent_API.AUTO_LOGIN,data1,user.save_data['cookies']["api_web_cookie"])
        if request1 is None : log.write_log("自动登录连接失败",2) ; return False
        else : 
            log.write_log("自动登录连接成功",2)
            user.save_data['cookies']["api_web_cookie"] = connent_API.request_headers['cookie']
            user.login_account(None,None,request1.decode("utf-8"))
            return True

    for i in [updata_info, test_network, get_info] :
        if not i() : break
    user.write_back() ; log.set_time_end()
    if user.save_data['online_get']['app_version'] != app_constant.APP_VERSION : 
        tkinter.messagebox.showinfo("最新版本已发布\n当前版本:%s\n最新版本:%s" % (app_constant.APP_VERSION,
        user.save_data['online_get']['app_version']))

def flash_minecraft_id(log:initialization_log) :
    update_id_zip_path = os.path.join("main_source", "update_source", "minecraft_id.zip")
    import main_source.update_source.flash_source as flash_source
    log.write_log("正在获取minecraft id...")

    def download_online_id() -> bool :
        try :
            response = connent_API.request_url_without_error(connent_API.UPDATE_BE_ID)
            if response is None : raise Exception
            with open(update_id_zip_path, 'wb') as file1: file1.write(response)
        except : log.write_log("在线BE-ID列表下载失败", 2) ; return True
        else : log.write_log("在线BE-ID列表下载成功", 2) ; return True

    def generate_online_id() -> bool :
        try : flash_source.unzip_id_file()
        except Exception as e : log.write_log(e.args[0], 2) ; return False

        try : a = flash_source.report_source_update_date()
        except Exception as e : log.write_log(e.args[0], 2) ; return False
        for i in a : log.write_log(i, 2)

        a = flash_source.update_minecraft_id()
        for i in a["success"] : log.write_log(i, 2)
        for i in a["error"] : log.write_log(i, 2)

        a = flash_source.flash_search_id()
        for i in a["success"] : log.write_log(i, 2)
        for i in a["error"] : log.write_log(i, 2)

        return True

    for i in [download_online_id,generate_online_id] :
        if not i() : break
    log.set_time_end()

def flash_minecraft_source(user:user_manager, log:initialization_log) :
    source_path = os.path.join("main_source", "update_source", "be_resource.tar")
    import main_source.update_source.flash_source as flash_source
    while not user.info_update : time.sleep(0.2)
    
    log.write_log("正在检查minecraft source...")
    if FileOperation.is_file(source_path) : 
        if zlib.crc32(FileOperation.read_a_file(source_path, "readbyte")) == user.save_data["online_get"]["app_info"]["source_crc32"] :
            log.set_time_end() ; log.write_log("检查完毕，无需更新", 2) ; return None

    log.write_log("正在获取minecraft source...")

    def download_online_source() :
        be_resource = connent_API.request_url_without_error(user.save_data["online_get"]["app_info"]["source_update_url"])
        if be_resource is None : log.write_log("资源联网获取失败",2) ; return False
        log.write_log("资源获取成功", 2)
        with open(source_path, 'wb') as file1 : file1.write(be_resource)
        return True

    def generate_online_source() -> bool :
        try : flash_source.unzip_source_file()
        except Exception as e : log.write_log(e.args[0], 2) ; return False

        a = flash_source.update_minecraft_source()
        for i in a["success"] : log.write_log(i, 2)
        for i in a["error"] : log.write_log(i, 2)
        return True

    for i in [download_online_source,generate_online_source] :
        if not i() : break
    log.set_time_end()


