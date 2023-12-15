import os,traceback,json,time,threading,re,copy,random,base64,tarfile,platform,zlib
import main_source.package.file_operation as FileOperation
from typing import List,Literal,Union
from tkinter import ttk ; import tkinter ; import tkinter.messagebox
import main_source.package.connent_API as connent_API

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
        if match_request_msg == None : self.login_out_account() ; return None
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



def get_app_infomation_and_login(Announcement, user:user_manager, log:initialization_log) :
    import main_source.main_window.constant as app_constant

    log.write_log("正在获取软件信息...")
    def updata_info() :
        response2 = connent_API.request_url_without_error(connent_API.APP_INFO_URL)
        if response2 == None : 
            Announcement.set_notification(None)
            log.write_log("软件信息获取失败", 2) ; return True
        response2 = connent_API.transfor_qq_share(response2.decode("utf-8"))
        response2 = zlib.decompress(base64.b64decode(response2.encode("utf-8"))).decode("utf-8")
        response2 = json.loads(response2)
        user.save_data['online_get'] = response2

        Announcement.set_notification(response2['notification'])
        user.info_update = True ; log.write_log("软件信息同步完成",2) ; return True

    def test_network() :
        request1 = connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL)
        if request1 == None : log.write_log("网络验证失败",2) ; return False
        else : return True

    def get_info() :
        data1 = {"userdata":user.get_account()} if (user.get_account() != None) else None
        request1 = connent_API.request_url_without_error(connent_API.AUTO_LOGIN,data1,user.save_data['cookies']["api_web_cookie"])
        if request1 == None : log.write_log("自动登录连接失败",2) ; return False
        else : 
            log.write_log("自动登录连接成功",2)
            user.save_data['cookies']["api_web_cookie"] = connent_API.request_headers['cookie']
            user.login_account(None,None,request1.decode("utf-8"))
            return True

    for i in [updata_info, test_network, get_info] :
        if not i() : break
    log.set_time_end()
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
            if response == None : raise Exception
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
        if be_resource == None : log.write_log("资源联网获取失败",2) ; return False
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


