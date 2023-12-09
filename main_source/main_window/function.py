import os,traceback,json,time,threading,re,copy,random,base64,tarfile,platform
import main_source.package.file_operation as FileOperation
from typing import List,Literal,Union
from tkinter import ttk ; import tkinter

class user_manager :

    save_path = os.path.join("save_world", "user_data.data")
    save_data = {} ; update_end_function_list = []
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
        if not isinstance(self.save_data["user_account"],type({})) : self.save_data["user_account"] = {}
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
        return self.save_data_template["user"].get("data", None)

class main_window_variable :

    def __init__(self) -> None:
        self.expand_pack_open = {} #拓展包启动列表
        self.paset_thread_time = 0  #输入降频计时

        self.platform:Literal["windows","android"] = None #系统名称
        system_info = platform.uname()
        if system_info.system.lower() == 'windows' : self.platform = 'windows'
        elif system_info.system.lower() == 'linux' and system_info.machine == "aarch64" : self.platform = 'android'

        self.focus_input:Union[tkinter.Text, tkinter.Entry, ttk.Entry] = None #当前选择的输入框

        self.is_installing = False #正在安装拓展包
        self.is_login = False #正在登录





























class main_windows_function :


    def check_world_file(now_test,dir_obj):

            for i in world_file_prove :
                try : 
                    file1 = open(os.path.join(now_test,i),"r",encoding='utf-8')
                    json.loads(file1.read())
                except :
                    try :
                        if not(tarfile.is_tarfile(os.path.join(now_test,i))) : return (False,None,None)
                    except : return (False,None,None)
                else : file1.close()

            try :
                file1 = open(os.path.join(now_test,"level_name"),"r",encoding='utf-8')
                json1 = json.loads(file1.read())
                world_name = json1['name']
                world_version = json1['version']
                file1.close()
            except : return (False,None,None)
            else :
                if isinstance(world_name,str) and (world_version in ["java","bedrock"]): return (True,world_name,world_version,dir_obj)
                else : return (False,None,None)



    def create_world(self) :
        world_config_copy = copy.deepcopy(world_config)
        for i in self.world_config_frame.winfo_children() : i.destroy()
        if self.select_version == "java" : pass
        elif self.select_version == "bedrock" : pass

    def modify_world(self,world_name : str) :
        for i in self.world_config_frame.winfo_children() : i.destroy()
        if self.select_version == "java" : pass
        elif self.select_version == "bedrock" : pass

    def flash_list(self):

        if self.version_check() and self.in_game_check() :
            self.list_select.delete(0,"end")
            file_list = list(os.walk("save_world"))[0]

            for dir_obj in file_list[1] :
                now_test = os.path.join(file_list[0],dir_obj)
                check_reault = main_windows_function.check_world_file(now_test,dir_obj)
                if check_reault[0] :
                    textbox_text = "-->".join([check_reault[1],check_reault[3]])
                    if self.select_java.get() and check_reault[2] == "java" :
                        self.list_select.insert('end',textbox_text)
                    if self.select_bedrock.get() and check_reault[2] == "bedrock" :
                        self.list_select.insert('end',textbox_text)

            self.modify_state("执行操作：刷新世界列表")

    def create_world_treading(self , world_config_json : dict,challenge:bool = False,challenge_id = None):
            self.creat_button_count += 1

            if self.creat_button_count < 2 : 
                self.modify_state("二次确认\n是否创建世界？","info",False) ; return None 
            self.creat_button_count = 0
            os.makedirs("save_world",exist_ok=True)

            rand_text = hex(random.randint(268435456 , 536870912))[3:]
            try :
                for i in world_file_prove :
                    if i == 'world_info' : nbt_class.minecraft_world(self).__create__(world_config_json).__save__(os.path.join("save_world",rand_text,i))
                    elif i == 'level_name' :
                        ttt = json.dumps(
                            {"name":world_config_json['normal_setting']['world_name'], "version": self.select_version,
                            "verification_challenge": challenge, "verification_id": challenge_id}
                        )
                        file_IO.write_a_file( os.path.join("save_world",rand_text,i) , ttt )
                    elif i == 'scoreboard' : nbt_class.scoreboard_nbt().__save__(rand_text)
                    elif i == 'block_mapping' : file_IO.write_a_file( os.path.join("save_world",rand_text,i) , file_IO.read_a_file(os.path.join(bedrock_command_thing_path,"default_map")) )
                    elif i == 'player_info' : file_IO.write_a_file( os.path.join("save_world",rand_text,i) , "[]" )
                    else : file_IO.write_a_file( os.path.join("save_world",rand_text,i) , "{}" )
            except :
                file_IO.delete_all_file(os.path.join("save_world",rand_text))
                self.modify_state("创建世界错误\n日志 create.txt 已生成","error")
                traceback.print_exc(file=open(os.path.join("log","create.txt"), "w+",encoding="utf-8"))
                return None

            os.makedirs(os.path.join("save_world",rand_text,"behavior_packs"),exist_ok=True)
            os.makedirs(os.path.join("save_world",rand_text,"resource_packs"),exist_ok=True)
            os.makedirs(os.path.join("save_world",rand_text,"command_blocks"),exist_ok=True)
            os.makedirs(os.path.join("save_world",rand_text,"chunk_info","overworld"),exist_ok=True)
            os.makedirs(os.path.join("save_world",rand_text,"chunk_info","nether"),exist_ok=True)
            os.makedirs(os.path.join("save_world",rand_text,"chunk_info","the_end"),exist_ok=True)

            self.flash_world()
            if not challenge : 
                self.creat_windows_world() ; self.modify_state("执行操作：创建世界")
            return rand_text

    def delete_world(self):
        if self.in_game_check():
            if len(self.list_select.curselection()) :
                self.delete_button_count += 1
                if self.delete_button_count > 3 :
                    self.delete_button_count = 0
                    text1 = self.list_select.get(self.list_select.curselection()).split("-->")[1]
                    file_IO.delete_all_file(os.path.join('save_world',text1))
                    self.modify_state("执行操作：删除世界")
                    self.flash_world()
                else:
                        self.modify_state("第" + str(self.delete_button_count) + "次确认\n是否删除选择的世界？\n所有文件都将会被删除!!!","info",False)
            else :
                self.modify_state("错误: 无任何选择","error")

    def join_world(self,name_of_world=None):
        global game_process
        def main_game(self):
            global game_process
            game_process = minecraft_running()
            if self.select_version == "bedrock" : game_process.____be_init_chunk____()
            elif self.select_version == "java" : game_process.____je_init_chunk____()

        p1 = threading.Thread(target=main_game,args=(self,))
        p1.start()

        if name_of_world and main_windows_function.check_world_vaild(name_of_world) : text1 = name_of_world
        elif name_of_world and main_windows_function.check_world_vaild(name_of_world) == False : return None
        else : text1 = self.list_select.get(self.list_select.curselection()).split("-->")[1]
        self.in_game_world = text1

        while p1.is_alive() : time.sleep(0.2)
        
        self.main_process = game_process
        game_process.in_game_world = self.in_game_world

        if self.select_version == "bedrock" : game_process.loop_tread = threading.Thread(target=game_process.__be_running__,args=(text1,))
        elif self.select_version == "java" : game_process.loop_tread = threading.Thread(target=game_process.__je_running__,args=(text1,))

        game_process.loop_tread.start()
        self.input_box1.delete("1.0",'end')
        while game_process.world_infomation == None : pass
        if ("verification_challenge" not in game_process.world_infomation) or (not game_process.world_infomation['verification_challenge']) : 
            self.input_box1.insert('end', game_process.world_infomation['terminal_command'])
            self.input_box1.config(state="normal")
            self.send_command_button.config(state="normal")
            self.see_feedback_button.config(state="normal")
            self.input_box1.see("end")
        else : 
            self.input_box1.config(state="disabled")
            self.send_command_button.config(state="disabled")
            self.see_feedback_button.config(state="disabled")

    def leave_world(self,not_save_exit = False):
        global game_process
        a = game_process
        game_process.in_game_tag = False
        game_process.world_infomation['terminal_command'] = self.input_box1.get("0.0","end")[:-1]
        while game_process.loop_tread.is_alive() : time.sleep(0.2)

        if not(not_save_exit) and game_process.game_load_over : game_process.exit_world()
        else : self.modify_state("不保存已退出")

        self.main_process = None
        game_process = None

    def execute_command(self) :
        self.modify_state("执行操作：发送命令\n等待被游戏执行")
        self.terminal_log.clear()
        #exec(self.input_box1.get("1.0",'end'),globals(),locals())
        game_process.is_terminal_send_command = True
        return True

    def check_world_vaild(world_name) :
        return main_windows_function.check_world_file(os.path.join("save_world",world_name),world_name)[0]



def compare_version(v1,v2) :
    if len(v1) > len(v2) : return None
    for i in range(len(v1)) :
        if v1[i] > v2[i] : return 1
        elif v1[i] < v2[i] : return -1
    return 0


def compile_file(txt_file_path) :
    return compile(file_operation().read_a_file(txt_file_path),txt_file_path,'exec')


def skip_space(text1) :
    return re.split("^[ ]{0,}",re.split("[ ]{0,}$",text1)[0])[1]


def setTimeOut(sleep_time,func,*args1) :
    def time_out_func(sleep_time,func,*args1) :
        time.sleep(sleep_time)
        func(*args1)
    threading.Thread(target=time_out_func,args=(sleep_time,func) + args1).start()


class search_id_object :
    
    def __init__(self) -> None:
        try : self.MC_ID = json.load(open(os.path.join('main_source' , 'id_tanslate.json'),"r",encoding="utf-8"))
        except : self.MC_ID = {} ; traceback.print_exc()
        self.search = []
    
    def search_str(self,condition_str : str,is_regx=False) :
        if condition_str.replace(" ","") == "" : return []
        result_list = []

        if not is_regx :
            m1,m2 = "\\u","0000"
            condition_str = "".join( [(m1 + hex(ord(i)).replace("0x",m2)[-4:]) for i in condition_str])
        
        try: 
            if re.compile(condition_str).search("") : return None
        except : 
            self.search = result_list ; return None

        for i in self.MC_ID.keys() :
            result_list += [(j,self.MC_ID[i][j]) for j in list(self.MC_ID[i].keys()) if re.search(condition_str,j)]

        self.search = result_list
        return result_list









