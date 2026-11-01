import os,inspect,json,time,threading,re,base64,zlib,traceback,random
from tkinter import ttk
import tkinter, tkinter.messagebox
import package.file_operation as FileOperation
from typing import List, Dict, Union
import package.connent_API as connent_API
import package.tk_tool as tk_tool


class user_manager :

    save_path = os.path.join("save_world", "user_data.data")
    login_msg_match = re.compile("<login_msg>[\u0000-\uffff]+</login_msg>")
    save_data_template = {
        "client_info": {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.%s.%s' % 
            (random.randint(1000, 9999), random.randint(1000, 9999)),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-CH-UA": "",
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": "Windows",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }, 
        "online_get": {}, 
        "user": {"account":None, "password":None, "data":None},
        "open_app_count": 0,
        "install_pack_list": {},
    }

    def __init__(self) :
        self.save_data = {}
        self.info_update = False

        if os.path.isfile(self.save_path) :
            a = FileOperation.read_a_file(self.save_path)
            try : self.save_data = json.loads(a)
            except : self.save_data = self.save_data_template
        else : self.save_data = self.save_data_template

        if "online_get" not in self.save_data : self.save_data["online_get"] = {}
        if "install_pack_list" not in self.save_data : self.save_data["install_pack_list"] = {}
        if "client_info" not in self.save_data : self.save_data["client_info"] = {}

        client_info, template_info = self.save_data["client_info"], self.save_data_template["client_info"]
        if "cookie" not in client_info : client_info["cookie"] = {}
        for key in template_info :
            if key not in client_info : client_info[key] = template_info[key]

        if "user" not in self.save_data : self.save_data["user"] = {"account":None, "password":None, "data":None}
        if "account" not in self.save_data["user"] : self.save_data["user"]["account"] = None
        if "password" not in self.save_data["user"] : self.save_data["user"]["password"] = None
        if "data" not in self.save_data["user"] : self.save_data["user"]["data"] = None

    def write_back(self) :
        FileOperation.write_a_file(self.save_path, json.dumps(self.save_data, indent=4))


    def get_connent_header(self) :
        cookie =  '; '.join([f"{key}={value}" for key, value in self.save_data["client_info"]["cookie"].items()])
        copy_header = dict(self.save_data["client_info"])
        copy_header['cookie'] = cookie
        return copy_header

    def set_cookie(self, data:Dict[str,str]) :
        self.save_data["client_info"]["cookie"].update(data)


    def get_account(self, base64encode=True) : 
        json1 = {"account":None, "password":None}
        json1["account"] = self.save_data["user"].get("account")
        json1["password"] = self.save_data["user"].get("password")
        if not isinstance(json1["account"], str) : 
            self.login_out() ; return None
        if not isinstance(json1["password"], str) : 
            self.login_out() ; return None
        
        if not base64encode : return json1
        json_str = json.dumps(json1).encode("utf-8")
        return base64.b64encode(json_str).decode("utf-8")

    def get_account_info(self) -> Union[dict, None] :
        return self.save_data["user"].get("data", None)


    def login_out(self) :
        self.save_data["user"] = {"account":None, "password":None, "data":None}
        self.write_back()

    def login_account(self, account:str="", passcode:str="", auto_login:bool=False) :
        post_data = {"userdata":""}
        request_header = self.get_connent_header()
        if auto_login : post_data["userdata"] = self.get_account()
        elif bool(account) and bool(passcode) : 
            login_info_1 = {"account":account, "password":passcode}
            post_data["userdata"] = base64.b64encode(json.dumps(login_info_1).encode("utf-8")).decode("utf-8")

        #print(connent_API.AUTO_LOGIN, post_data, request_header)
        responseData = connent_API.url_request(connent_API.AUTO_LOGIN, post_data, request_header)
        if responseData is None : return None

        match_request_msg = self.login_msg_match.search(responseData.decode("utf-8"))
        if match_request_msg is None : self.login_out() ; return None
        account_log_msg = match_request_msg.group().replace("<login_msg>","").replace("</login_msg>","")

        try : msg_json = json.loads(account_log_msg)
        except : self.login_out() ; return None

        if ('state_code' not in msg_json) or msg_json['state_code'] > 0 : 
            self.login_out() ; return None
        
        if account : self.save_data["user"]["account"] = account
        if passcode : self.save_data["user"]["password"] = passcode
        self.save_data["user"]['data'] = msg_json["server_back"]
        self.save_data['client_info']["cookie"]["__test"] = request_header["cookie"].split("=")[1]
        self.write_back()
        return msg_json["server_back"]

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
            c1 = self.main_win.get_display_expand_pack()
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
            focus_input:Union[tkinter.Text, tkinter.Entry] = self.main_win.focus_input
            mode_using(self.main_win, focus_input, mode)
            for index,item in enumerate(self.menu_list) : item.unpost()
            if mode in {"line_select", "select_all"} : 
                if isinstance(focus_input, tkinter.Text) : x1,y1,x2,y2 = focus_input.bbox(tkinter.INSERT)
                else : x1,y1 = focus_input.winfo_rootx(), focus_input.winfo_rooty()
                x1 = self.main_win.window.winfo_width() // 2
                if isinstance(focus_input, tkinter.Text) : self.other_menu.post(x1, focus_input.winfo_rooty() + y1 - 100)
                else : self.other_menu.post(x1, y1 - focus_input.winfo_reqheight() - 30)

        def post(self, x:int, y:int) :
            c1 = self.main_win.get_display_expand_pack()
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
        c1 = main_win.get_display_expand_pack()
        if c1 is not None and hasattr(c1['module'], "Copy_event") :
            if isinstance(focus_input, tkinter.Text) : c1['module'].Copy_event(focus_input)
        else :
            focus_input.event_generate("<<Cut>>")
            focus_input.event_generate("<ButtonRelease>", state=256)
    elif mode == "copy" : 
        c1 = main_win.get_display_expand_pack()
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
        focus_input.event_generate("<ButtonRelease>", state=256)
    elif mode == "paste_object" :
        try : focus_input.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
        except : pass

        c1 = main_win.get_display_expand_pack()
        if c1 is not None and hasattr(c1['module'], "Paste_event") :
            if isinstance(focus_input, tkinter.Text) : c1['module'].Paste_event(focus_input)

    elif mode == "undo" : 
        try : focus_input.edit_undo()
        except : pass
        focus_input.event_generate("<ButtonRelease>", state=256)
    elif mode == "redo" : 
        try : focus_input.edit_redo()
        except : pass
        focus_input.event_generate("<ButtonRelease>", state=256)
    elif mode == "return" : 
        if not(isinstance(focus_input,tkinter.Entry) or isinstance(focus_input,ttk.Entry)) : 
            try : focus_input.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
            except : pass
            focus_input.insert(tkinter.INSERT,"\n")
        focus_input.event_generate("<ButtonRelease>", state=256)
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
    request_header = user.get_connent_header()
    online_response:bytes = None

    def test_network() :
        log.write_log("正在验证网络通信...")
        request1 = connent_API.url_request(connent_API.TEST_BAIDU_URL, request_headers=request_header)
        if request1 is None : log.write_log("网络通信验证失败", 2) ; return False
        else : log.write_log("网络通信验证成功", 2) ; return True

    def get_online_info() :
        nonlocal online_response
        log.write_log("正在获取软件信息...")
        online_response = connent_API.url_request(connent_API.APP_INFO_URL, request_headers=request_header)
        if online_response is None : 
            Announcement.set_notification(None)
            log.write_log("软件信息获取失败", 2)
            user.info_update = True
            return True
        log.write_log("软件信息获取成功", 2)
        return True

    def updata_info() :
        log.write_log("正在解析软件信息...")
        try : 
            response2 = connent_API.transfor_qq_share(online_response.decode("utf-8"))
            response2 = zlib.decompress(base64.b64decode(response2.encode("utf-8"))).decode("utf-8")
            response2 = json.loads(response2)
        except :
            if "notification" in user.save_data['online_get'] :
                Announcement.set_notification(user.save_data['online_get']['notification'])
            if "api" in user.save_data['online_get'] :
                connent_API.get_online_api(user.save_data['online_get']['api'])
            log.write_log("无法解析信息，已使用上一次数据", 2)
        else :
            user.save_data['online_get'] = response2
            Announcement.set_notification(user.save_data['online_get']['notification'])
            connent_API.get_online_api(user.save_data['online_get']['api'])
            log.write_log("软件信息同步完成", 2)
        finally :
            user.info_update = True
            return True

    def get_info() :
        if app_constant.debug_testing : return None
        log.write_log("正在自动登录账户...") 
        request1 = user.login_account(auto_login=True)
        if request1 : 
            log.write_log("自动登录成功", 2)
            return True
        else : 
            log.write_log("自动登录失败", 2) ; return False

    for i in [test_network, get_online_info, updata_info, get_info] :
        if not i() : break
        log.write_log("") 
    user.write_back()
    log.set_time_end()

    OnlineVersion = user.save_data['online_get']['app_version']
    OnlineVersion = [int(i) for i in OnlineVersion.split(".")]
    OnlineVersion.append(0)
    OnlineVersion = tuple(OnlineVersion)
    if not app_constant.debug_testing and OnlineVersion != app_constant.APP_VERSION : 
        tkinter.messagebox.showinfo("Info","最新版本已发布\n当前版本:%s.%s.%s\n最新版本:%s" % (app_constant.APP_VERSION[0],
        app_constant.APP_VERSION[1], app_constant.APP_VERSION[2], user.save_data['online_get']['app_version']))


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
    main_win.button_bar.pack(side="bottom")
    main_win.set_display_frame("setting_frame")

def Tutorial_Start_2(main_win) :
    import main_source.main_window.display_ui as app_tk_frame
    TK:tkinter.Tk = main_win.window

    TellWin_1 = tk_tool.tk_TellBox(TK, TK, highlightcolor='green', bg="black")
    TellWin_1.place(x=TellWin_1.rootx, y=TellWin_1.rooty)
    StrVar_1 = tkinter.StringVar(TellWin_1)
    Label_1 = tkinter.Label(TellWin_1, bg="black", fg="white", font=tk_tool.get_default_font(11), textvariable=StrVar_1)
    TellWin_1.create_window(0+TellWin_1.winfo_reqwidth()/2, 0+TellWin_1.winfo_reqheight()/2, window=Label_1)

    sleep_time(main_win, 1)
    play_captions(main_win, StrVar_1, "欢迎来到新手须知\n本教程可以让你熟悉\n必要的操作技巧与方法")
    sleep_time(main_win, 3)

    #技巧2
    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "命令模拟器使用TK搭建\n许多文字操作无法直接与\n安卓输入法中的功能进行兼容\n\n")
    play_captions(main_win, StrVar_1, "因此需要设计文本操作菜单\n实现文本的复制粘贴操作")
    sleep_time(main_win, 6)

    StrVar_1.set("")
    play_captions(main_win, StrVar_1, "技巧一   文本操作菜单1\n\n在文本框中缓慢拖动选中文字\n松手后唤起文本操作菜单1\n\n你可以尝试唤起文本操作菜单1")
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
    play_captions(main_win, StrVar_1, "技巧二   文本操作菜单2\n\n在文本框中光标位置缓慢点击\n即可唤起文本操作菜单2\n\n你可以尝试唤起文本操作菜单2")
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
    play_captions(main_win, StrVar_1, "技巧三   底栏菜单\n\n底栏菜单位于界面底部\n\n你可以尝试唤起底栏菜单")
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




