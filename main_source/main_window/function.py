import os,inspect,json,time,threading,re,base64,zlib,traceback
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

            list1 = {"剪切":lambda:self.mode_using("cut"), '复制':lambda:self.mode_using("copy"), 
                     "换行":lambda:self.mode_using("return"), '粘贴':lambda:self.mode_using("paste"), 
                     "粘贴对象":lambda:self.mode_using("paste_object")}
            self.menu_list:List[tkinter.Menu] = []
            for key,value in list1.items() :
                Menu = tkinter.Menu(main_win.window, tearoff=False, font=tk_tool.get_default_font(10), **karg)
                Menu.add_command(label=key, command=value)
                self.menu_list.append(Menu)
                Menu.update()

        def mode_using(self, mode) :
            focus_input = self.main_win.focus_input
            mode_using(self.main_win, focus_input, mode)
            for index,item in enumerate(self.menu_list) : item.unpost()
        
        def post(self, x:int, y:int) :
            c1 = self.main_win.get_display_expand_pack_record()
            c11 = c1 is not None and hasattr(c1['module'], "Paste_event")

            all_width = [i.winfo_reqwidth()-20 for i in self.menu_list]
            if not c11 : all_width.pop()
            start_x = x - (sum(all_width) // 2)

            for index,item in enumerate(self.menu_list) : 
                if item is self.menu_list[-1] and not c11 : continue
                item.post(start_x + sum(all_width[0:index]), y)
            self.is_post = True

        def unpost(self) :
            if not self.is_post : return None
            for index,item in enumerate(self.menu_list) : item.unpost()
            self.is_post = False

    class Local_Right_Click_Menu_2 :

        def __init__(self, main_win, **karg) -> None :
            self.main_win = main_win
            self.is_post = False

            list1 = {"全选":lambda:self.mode_using("select_all"), "选行":lambda:self.mode_using("line_select"),
                     "换行":lambda:self.mode_using("return"), "粘贴":lambda:self.mode_using("paste"),
                     "粘贴对象":lambda:self.mode_using("paste_object")}
            self.menu_list:List[tkinter.Menu] = []
            for key,value in list1.items() :
                Menu = tkinter.Menu(main_win.window, tearoff=False, font=tk_tool.get_default_font(10), **karg)
                Menu.add_command(label=key, command=value)
                self.menu_list.append(Menu)
                Menu.update()

        def mode_using(self, mode) :
            focus_input = self.main_win.focus_input
            mode_using(self.main_win, focus_input, mode)
            for index,item in enumerate(self.menu_list) : item.unpost()
            if mode == "line_select" : self.other_menu.post(self.last_post_x, self.last_post_y)

        def post(self, x:int, y:int) :
            c1 = self.main_win.get_display_expand_pack_record()
            c11 = c1 is not None and hasattr(c1['module'], "Paste_event")

            all_width = [i.winfo_reqwidth()-20 for i in self.menu_list]
            if not c11 : all_width.pop()
            start_x = x - (sum(all_width) // 2)

            for index,item in enumerate(self.menu_list) : 
                if item is self.menu_list[-1] and not c11 : continue
                item.post(start_x + sum(all_width[0:index]), y)

            self.is_post = True

        def unpost(self) :
            if not self.is_post : return None
            for index,item in enumerate(self.menu_list) : item.unpost()
            self.is_post = False

        def set_other_menu(self, other_menu) :
            self.other_menu = other_menu

    def __init__(self, main_win, Text:tkinter.Text) -> None :
        import main_source.main_window.constant as app_constant
        self.main_win = main_win
        self.app_constants = app_constant
        self.Right_Click_Menu_1 = self.Local_Right_Click_Menu_1(main_win, background="#ffaec8")
        self.Right_Click_Menu_2 = self.Local_Right_Click_Menu_2(main_win, background="#ffaec8")
        self.Right_Click_Menu_2.set_other_menu(self.Right_Click_Menu_1)
        self.Text = Text

        self.is_left_motion = False
        self.is_have_select = False
        self.insert_pos_save = None
    
    def __weakup_keyboard__(self) :
        inputMethodManager = self.app_constants.PythonActivity.mActivity.getSystemService(
            self.app_constants.Context.INPUT_METHOD_SERVICE)
        isInputOpen = inputMethodManager.inputMethodWindowVisibleHeight
        if not isInputOpen : inputMethodManager.toggleSoftInput(0, 0)

    def __weakdown_keyboard__(self) :
        inputMethodManager = self.app_constants.PythonActivity.mActivity.getSystemService(
            self.app_constants.Context.INPUT_METHOD_SERVICE)
        isInputOpen = inputMethodManager.inputMethodWindowVisibleHeight
        if isInputOpen : inputMethodManager.toggleSoftInput(0, 0)

    def update_INSERT_pos(self, widget:Union[tkinter.Text, tkinter.Entry, ttk.Entry]) :
        Menu = self.Right_Click_Menu_2

        if isinstance(widget, tkinter.Text) : insert_pos = list(widget.bbox(tkinter.INSERT))[0:2]
        else : insert_pos = [widget.index(tkinter.INSERT)*40, widget.winfo_rooty()]
        if self.insert_pos_save is None : self.insert_pos_save = insert_pos ; return None

        if not(self.insert_pos_save[0]-100 <= insert_pos[0] <= self.insert_pos_save[0]+100) :
            self.insert_pos_save = insert_pos  ; Menu.unpost(); return None
        if not(self.insert_pos_save[1]-40 <= insert_pos[1] <= self.insert_pos_save[1]+40) :
            self.insert_pos_save = insert_pos ; Menu.unpost() ; return None

        if isinstance(widget, tkinter.Text) : x1,y1,x2,y2 = widget.bbox(tkinter.INSERT)
        else : y1 = widget.winfo_rooty()
        x1 = self.main_win.window.winfo_width() // 2
        if not Menu.is_post : 
            if isinstance(widget, (tkinter.Entry, ttk.Entry)) : Menu.post(x1, y1 - widget.winfo_height() - 30)
            else : Menu.post(x1, widget.winfo_rooty() + y1 - 100)
        else : Menu.unpost()

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
            if isinstance(e.widget, tkinter.Text) : Menu.post(x1, e.widget.winfo_rooty() + y1 - 100)
            else : Menu.post(x1, y1 - e.widget.winfo_reqheight() - 30)

            self.__weakup_keyboard__()
            self.is_have_select = True
            self.is_left_motion = False
            return None

        if self.is_left_motion : self.is_left_motion = False ; return None
        if self.is_have_select : self.is_have_select = False ; return None
        if isinstance(e, tkinter.Event) : self.update_INSERT_pos(e.widget)
        self.__weakup_keyboard__()

    def key_press_event(self, e:tkinter.Event) :
        self.Right_Click_Menu_1.unpost()
        self.Right_Click_Menu_2.unpost()


def mode_using(main_win, focus_input:Union[tkinter.Entry,tkinter.Text,ttk.Entry], mode, word=None) : 
    import main_source.main_window.constant as app_constant
    if focus_input is None : return None

    if mode == "select_all" : focus_input.event_generate("<<SelectAll>>")
    elif mode == "cut" : 
        c1 = main_win.get_display_expand_pack_record()
        if c1 is not None and hasattr(c1['module'], "Copy_event") :
            if isinstance(focus_input, tkinter.Text) : c1['module'].Copy_event(focus_input)
        else :
            focus_input.event_generate("<<Cut>>")
            focus_input.event_generate("<ButtonRelease>")
    elif mode == "copy" : 
        c1 = main_win.get_display_expand_pack_record()
        if c1 is not None and hasattr(c1['module'], "Copy_event") :
            if isinstance(focus_input, tkinter.Text) : c1['module'].Copy_event(focus_input)
        else : focus_input.event_generate("<<Copy>>")
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
    elif mode == "paste_object" :
        try : focus_input.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
        except : pass

        c1 = main_win.get_display_expand_pack_record()
        if c1 is not None and hasattr(c1['module'], "Paste_event") :
            if isinstance(focus_input, tkinter.Text) : c1['module'].Paste_event(focus_input)

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
        return
        tkinter.messagebox.showinfo("Info","最新版本已发布\n当前版本:%s\n最新版本:%s" % (app_constant.APP_VERSION,
        user.save_data['online_get']['app_version']))

def flash_minecraft_id(log:initialization_log) :
    update_id_zip_path = os.path.join("main_source", "update_source", "minecraft_id.zip")
    import main_source.update_source.flash_source as flash_source
    log.write_log("正在获取minecraft id...")

    def download_online_id() -> bool :
        try :
            response = connent_API.request_url_without_error(connent_API.UPDATE_BE_ID, timeout_s=10)
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
        be_resource = connent_API.request_url_without_error(user.save_data["online_get"]["app_info"]["source_update_url"], timeout_s=10)
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



def Beginner_Tutorial(main_win, ask=True) :
    if ask : 
        yesorno = tkinter.messagebox.askquestion("question", "需要进入新手须知吗？")
        if yesorno != "yes" : return None
    main_win.tutorial_mode = True
    threading.Thread(target=Tutorial_Start_1, args=(main_win, )).start()

def Tutorial_Start_1(main_win) :
    def Exit() : main_win.tutorial_mode = False
    main_win.button_bar.pack_forget()
    main_win.set_display_frame("forget_all")
    Exit_Button = tkinter.Button(main_win.window, text="< 退出须知", background="#959cff", font=tk_tool.get_default_font(12), command=Exit)
    Exit_Button.place(x = 16 if main_win.platform == 'android' else 4, 
        y = 16 if main_win.platform == 'android' else 4 )

    try : Tutorial_Start_2(main_win)
    except Exception as e : 
        #traceback.print_exc()
        for key, value in e.args[0].items() :
            if key in {"TK", "main_win", "app_tk_frame", "event_class"} : continue
            if isinstance(value, (float, int, bool, str, tkinter.StringVar, type(Tutorial_Start_1))) : continue
            if value.winfo_exists() : value.destroy()

    Exit_Button.destroy()
    main_win.bind_events()
    main_win.button_bar.pack(side="bottom")
    main_win.set_display_frame("setting_frame")

def Tutorial_Start_2(main_win) :
    import main_source.main_window.tk_frame as app_tk_frame
    TK:tkinter.Tk = main_win.window

    TellWin_1 = tk_tool.tk_TellBox(TK, TK, highlightcolor='green', bg="black")
    TellWin_1.place(x=TellWin_1.rootx, y=TellWin_1.rooty)
    StrVar_1 = tkinter.StringVar(TellWin_1)
    Label_1 = tkinter.Label(TellWin_1, bg="black", fg="white", font=tk_tool.get_default_font(11), textvariable=StrVar_1)
    TellWin_1.create_window(0+TellWin_1.winfo_reqwidth()/2, 0+TellWin_1.winfo_reqheight()/2, window=Label_1)

    sleep_time(main_win, 1)
    play_captions(main_win, StrVar_1, "欢迎来到新手须知\n本教程可以让你熟悉\n必要的操作技巧与方法")
    sleep_time(main_win, 3)

    #技巧1
    def event1(e:tkinter.Event) : 
        nonlocal wait_bool_1
        wait_bool_1 = False
        main_win.display_frame["right_click_menu"].post(
            e.x_root, e.y_root-main_win.display_frame["right_click_menu"].winfo_reqheight())
    wait_bool_1 = True
    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "技巧一   右键菜单\n\n长按屏幕唤起右键菜单\n你可以尝试唤起右键菜单")
    TK.bind("<Button-3>", event1)
    while bool_test(main_win, wait_bool_1) : time.sleep(0.1)
    sleep_time(main_win, 0.3)

    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "你已成功打开右键菜单\n\n右键菜单中有许多辅助功能\n可在帮助文档-使用须知中\n查看具体使用方法")
    sleep_time(main_win, 4)

    #技巧2
    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "命令模拟器使用TK搭建\n许多文字操作无法直接与\n安卓输入法中的功能进行兼容\n\n")
    play_captions(main_win, StrVar_1, "因此需要设计文本操作菜单\n实现文本的复制粘贴操作")
    sleep_time(main_win, 6)

    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "技巧二   文本操作菜单1\n\n在文本框中缓慢拖动选中文字\n松手后唤起文本操作菜单1\n\n你可以尝试唤起文本操作菜单1")
    Text_1 = tkinter.Text(TK, width=18, height=6, font=tk_tool.get_default_font(14))
    event_class = Text_Bind_Events(main_win, Text_1)
    Text_1.bind("<ButtonRelease-1>", event_class.left_click_release_event, add="+")
    Text_1.bind("<B1-Motion>", event_class.left_click_motion_event, add="+")
    Text_1.insert("1.0", "236789312736172489812947612821379802174861287948012784")
    Text_1.place(x=(TK.winfo_width() // 2) - (Text_1.winfo_reqwidth() // 2),
        y = int(TK.winfo_height() / 4))
    while bool_test(main_win, not event_class.Right_Click_Menu_1.is_post) : time.sleep(0.1)
    sleep_time(main_win, 0.3)
    event_class.__weakdown_keyboard__()

    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "你已唤起文本操作菜单1\n\n文本操作菜单1会在\n文字选中时显现")
    sleep_time(main_win, 3)
    Text_1.place_forget()

    #技巧3
    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "技巧三   文本操作菜单2\n\n在文本框中光标位置缓慢点击\n即可唤起文本操作菜单2\n\n你可以尝试唤起文本操作菜单2")
    Text_2 = tkinter.Text(TK, width=18, height=6, font=tk_tool.get_default_font(14))
    event_class = Text_Bind_Events(main_win, Text_2)
    Text_2.bind("<ButtonRelease-1>", event_class.left_click_release_event, add="+")
    Text_2.bind("<B1-Motion>", event_class.left_click_motion_event, add="+")
    Text_2.insert("1.0", "236789312736172489812947612821379802174861287948012784")
    Text_2.place(x=(TK.winfo_width() // 2) - (Text_2.winfo_reqwidth() // 2),
        y = int(TK.winfo_height() / 4))
    while bool_test(main_win, not event_class.Right_Click_Menu_2.is_post) : time.sleep(0.1)
    sleep_time(main_win, 0.3)
    event_class.__weakdown_keyboard__()

    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "你已唤起文本操作菜单2\n\n文本操作菜单2会在\n多次点击相同光标位置时显现")
    sleep_time(main_win, 5)
    Text_2.place_forget()

    #技巧4
    Button_Bar = app_tk_frame.Bottom_Bar(main_win)
    click_menu = False
    def update_menu_text(e:tkinter, self=Button_Bar) : 
        nonlocal click_menu
        test_pass = False
        for text_id_1 in self.menu_list :
            x1,y1,x2,y2 = self.bbox(text_id_1)
            if not(x1 <= e.x <= x2 and y1 <= e.y <= y2) : continue
            if text_id_1 == self.menu_list[4] : self.Menu.post(e.x_root, e.y_root-self.Menu.winfo_reqheight())
            if text_id_1 == self.menu_list[4] : click_menu = True ; continue
            self.itemconfig(text_id_1, fill="#00ff00")
            test_pass = True
            break
        [self.itemconfig(text_id_2, fill="white") for text_id_2 in self.menu_list if (
        test_pass and text_id_1 != text_id_2 and text_id_2 != self.menu_list[-1])]
    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "技巧四   底栏菜单\n\n底栏菜单位于界面底部\n\n你可以尝试唤起底栏菜单")
    Button_Bar.pack(side="bottom")
    Button_Bar.bind("<ButtonRelease-1>", update_menu_text)
    while bool_test(main_win, not click_menu) : time.sleep(0.1)
    sleep_time(main_win, 0.5)

    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "你已唤起底栏菜单")
    sleep_time(main_win, 2)
    Button_Bar.pack_forget()
    
    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "恭喜你完成了新手教程\n\n如有问题可在设置中\n添加QQ群进行交流\n\n4秒后返回设置界面...")
    sleep_time(main_win, 4)

    raise RuntimeError(inspect.currentframe().f_locals)

def sleep_time(main_win, sleep_time:int) :
    while sleep_time > 0 :
        if not main_win.tutorial_mode : 
            raise RuntimeError(inspect.currentframe().f_back.f_locals)
        time.sleep(0.1)
        sleep_time -= 0.1

def play_captions(main_win, Var:tkinter.StringVar, text:str) :
    for str1 in text :
        if not main_win.tutorial_mode : 
            raise RuntimeError(inspect.currentframe().f_back.f_locals)
        Var.set("%s%s" % (Var.get(), str1)) 
        time.sleep(0.1)

def bool_test(main_win, bool1:bool) :
    if not main_win.tutorial_mode : 
        raise RuntimeError(inspect.currentframe().f_back.f_locals)
    return bool1