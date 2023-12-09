#!/usr/bin/python
# -*- coding: UTF-8 -*-

#原生模块加载与设置
from idlelib.calltip_w import CalltipWindow
import webbrowser,http.server,ssl
import json,tkinter,time,threading,sys,base64,gzip,importlib
import zipfile,copy,os,re,types,io,gc,subprocess,traceback
import random,functools,pickle,hmac,tkinter.messagebox,importlib.util,platform
from tkinter import ttk
from typing import List,Dict,Union,Literal
debug_testing = True
ssl._create_default_https_context = ssl._create_unverified_context

#自定义模块加载与设置
import main_source.main_window.constant as app_constants
import main_source.main_window.function as app_function
import main_source.main_window.tk_frame as app_tk_frame
import main_source.package.file_operation as file_IO

if True : #启用软件前的加载项目
    for i in app_constants.First_Load_Build_Dir : os.makedirs(i,exist_ok=True)
    os.makedirs(os.path.join("functionality","example","example_bp","functions"),exist_ok=True)
    manifest_path = os.path.join("functionality","example","example_bp","manifest.json")
    if not(os.path.exists(manifest_path) and os.path.isfile(manifest_path)) : 
        file_IO.write_a_file(os.path.join("functionality","example","example_bp","manifest.json"),app_constants.manifest_json)

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
                respones = debug_win.post_data(datas, self.user_manage.save_data['expand_packs'])
                self.wfile.write(gzip.compress(json.dumps(respones,separators=(',', ':'),default=json_things.encoding).encode('utf-8')))
        
        server_address = ('', 32323)
        http_Resquest = functools.partial(http_Resquest,directory="html_output")
        httpd = server_class(server_address, http_Resquest)
        httpd.serve_forever()
    threading.Thread(target=http_server_create).start()

    def listen_cmd_input() :
        while debug_testing : 
            text1 = input(">>> ")
            try : compile(text1,"","eval")
            except Exception as e : 
                if isinstance(e,SyntaxError) : traceback.print_exc()
                try : exec(text1, globals(), globals())
                except : traceback.print_exc()
            try : 
                a_11 = time.time()
                print(eval(text1),globals(),globals())
                a_22 = time.time()
                print('时间：' + str(a_22 - a_11))
            except : traceback.print_exc()
    threading.Thread(target=listen_cmd_input).start()


import tkinter.font

class control_windows :

    def __init__(self):

        self.user_manager = app_function.user_manager() #用户管理
        self.runtime_variable = app_function.main_window_variable()
        self.game_process = None #模拟世界线程

        self.window = tkinter.Tk()
        self.window.title('minecraft命令调试器')
        self.window.geometry('300x600')
        self.calltip = CalltipWindow(self.window)

        self.in_expand_pack_ui = False #寄存是否在拓展包UI当前界面
        self.change_hight_component_list = [] #可变高度组件列表

        #self.windows_constant()
        app_tk_frame.Announcement(self.window, self.runtime_variable).pack()
        self.window.protocol("WM_DELETE_WINDOW", self.close_window_normal)
        threading.Thread(target=lambda:[time.sleep(1),app_tk_frame.Bottom_Bar(self.window, self.runtime_variable).pack(side="bottom")]).start()
        self.window.mainloop()


    def windows_constant(self):

        self.message = tkinter.Label(self.window, textvariable=self.message_feedback , bg='black',fg='white',font=('Arial', 11), width=27, height=3)

        def Menu_back() :
            popupmenu = tkinter.Menu(self.window,tearoff=False,font=('Arial', 10),borderwidth= 100 if platform.system() == 'Windows' else 1)
            popupmenu.add_command(label='撤销',command=lambda : self.mode_using("undo"))
            popupmenu.add_command(label='恢复',command=lambda : self.mode_using("redo"))
            popupmenu.add_separator()
            popupmenu.add_command(label="全选",command=lambda : self.mode_using("select_all"))
            popupmenu.add_command(label="剪切",command=lambda : self.mode_using("cut"))
            popupmenu.add_command(label='复制',command=lambda : self.mode_using("copy"))
            popupmenu.add_command(label='粘贴',command=lambda : self.mode_using("paste"))
            popupmenu.add_separator()
            popupmenu.add_command(label='清空',command=lambda : self.mode_using("clear"))
            popupmenu.add_command(label='回车',command=lambda : self.mode_using("return"))
            popupmenu.add_separator()
            popupmenu.add_command(label='行首',command=lambda : self.mode_using("jump_line_start"))
            popupmenu.add_command(label='行尾',command=lambda : self.mode_using("jump_line_end"))
            popupmenu.add_command(label='选行',command=lambda : self.mode_using("line_select"))
            
            return lambda a : popupmenu.post(a.winfo_rootx(), a.winfo_rooty())

        self.menu_frame = tkinter.Frame()
        tkinter.Canvas(self.menu_frame,width=2000, height=4).pack()
        frame_m1 = tkinter.Frame(self.menu_frame)
        tkinter.Button(frame_m1,text='游戏',font=('Arial',9),bg='#00ff7f',width=width_1,height=1,command=self.creat_windows_world).pack(side='left')
        tkinter.Canvas(frame_m1,width=10,height=5).pack(side='left')
        tkinter.Button(frame_m1,text='拓展',font=('Arial',9),bg='#00ff7f',width=width_1,height=1,command=self.creat_windows_expand).pack(side='left')
        tkinter.Canvas(frame_m1,width=10,height=5).pack(side='left')
        tkinter.Button(frame_m1,text='窗口',font=('Arial',9),bg='#00ff7f',width=width_1,height=1,command=self.creat_windows_pack).pack(side='left')
        tkinter.Canvas(frame_m1,width=10,height=5).pack(side='left')
        tkinter.Button(frame_m1,text='设置',font=('Arial',9),bg='#00ff7f',width=width_1,height=1,command=self.creat_windows_setting).pack(side='left')
        tkinter.Canvas(frame_m1,width=10,height=5).pack(side='left')
        mode_button = tkinter.Button(frame_m1,text='功能',font=('Arial',9),bg='#00ff7f',width=width_1,height=1)
        mode_button.pack(side='left')
        mode_button.config(command=lambda : Menu_back()(mode_button))
        frame_m1.pack()
        tkinter.Canvas(self.menu_frame,width=2000,height=3).pack()
        tkinter.Canvas(self.menu_frame,bg="black",width=2000,height=4).pack()
        tkinter.Canvas(self.menu_frame,width=2000,height=10).pack()

        if 0 :
            tkinter.Label(self.world_config_frame,text="",fg='black',font=('Arial',2),width=15,height=1).pack()
            frame_m3 = tkinter.Frame(self.world_config_frame)
            tkinter.Button(frame_m3,text='返回界面',font=('Arial',11),bg='aquamarine',width=8,height=1,
                           command=self.creat_windows_world).pack(side='left')
            tkinter.Label(frame_m3,text="",fg='black',font=('Arial',1),width=4,height=1).pack(side='left')
            tkinter.Button(frame_m3,text='生成世界',font=('Arial',11),bg='aquamarine',width=8,height=1,
                           command=save).pack(side='left')
            frame_m3.pack()
        self.game_ready_frame = tkinter.Frame()
        a1 = tkinter.Label(self.game_ready_frame, text="世界设置", bg='#82aaff',fg='black',font=('Arial', 20), width=15, height=1)
        a1.pack()
        tkinter.Canvas(self.game_ready_frame ,width=2000, height=10).pack()

        frame_m3 = tkinter.Frame(self.game_ready_frame)
        tkinter.Button(frame_m3,text='生成',font=('Arial',11),bg='aquamarine',width=5,height=1,command=self.create_world).pack(side='left')
        tkinter.Canvas(frame_m3,width=10, height=1).pack(side='left')
        tkinter.Button(frame_m3,text='删除',font=('Arial',11),bg='aquamarine',width=5,height=1,command=self.delete_world).pack(side='left')
        tkinter.Canvas(frame_m3,width=10, height=1).pack(side='left')
        tkinter.Button(frame_m3,text='进入',font=('Arial',11),bg='aquamarine',width=5,height=1,command=self.join_world).pack(side='left')
        frame_m3.pack()
        tkinter.Canvas(self.game_ready_frame ,width=2000, height=padding_1).pack()
        self.list_select = tkinter.Listbox(self.game_ready_frame,font=('Arial', 13), selectmode=tk_constants.SINGLE, height=9, width=22)
        self.list_select.pack()
        tkinter.Canvas(self.game_ready_frame,width=2000, height=padding_1).pack()
        a2 = tkinter.Button(self.game_ready_frame,text='帮助文档',font=('Arial',11),bg='#D369a9',width=8,height=1,
                       command=lambda : self.open_browser("http://localhost:32323"))
        a2.pack()
        self.add_can_change_hight_component([self.list_select,padding_1*2,10,a1,frame_m3,padding_1,padding_1,a2])


        self.game_run_frame = tkinter.Frame()
        a1 = tkinter.Label(self.game_run_frame, textvariable=self.world_feedback , bg='green',fg='white',font=('Arial', 12), width=21, height=1)
        a1.pack()
        frame_m10 = tkinter.Frame(self.game_run_frame)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.input_box1 = tkinter.Text(frame_m10,show=None,height=22,width=28,font=('Arial', 10),
                                       yscrollcommand=sco1.set,undo=True)
        self.input_box1.grid()
        self.input_box1.bind("<FocusIn>",lambda a : self.set_focus_input(a,self.input_box1))
        sco1.config(command=self.input_box1.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()
        tkinter.Canvas(self.game_run_frame,width=2000, height=9).pack()
        frame_m4 = tkinter.Frame(self.game_run_frame)
        self.send_command_button = tkinter.Button(frame_m4,text="执行", bg='pink',fg='black',font=('Arial', 11), width=5, height=1, command=self.send_command)
        self.send_command_button.pack(side='left')
        tkinter.Canvas(frame_m4,width=5, height=5).pack(side='left')
        self.see_feedback_button = tkinter.Button(frame_m4,text="终端", bg='pink',fg='black',font=('Arial', 11), width=5, height=1, command=self.creat_terminal)
        self.see_feedback_button.pack(side='left')
        tkinter.Canvas(frame_m4,width=5, height=5).pack(side='left')
        tkinter.Button(frame_m4,text='退出',bg='pink',font=('Arial', 11),width=5, height=1,command=self.exit_world).pack(side='left')
        frame_m4.pack()
        self.add_can_change_hight_component([self.input_box1,a1,9,frame_m4])


        self.game_terminal_frame = tkinter.Frame()
        tkinter.Label(self.game_terminal_frame, text="终端执行返回界面",bg="green",fg="white",font=('Arial', 12), width=21, height=1).pack()
        frame_m10 = tkinter.Frame(self.game_terminal_frame)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
        self.input_box2 = tkinter.Text(frame_m10,show=None,height=21,width=28,font=('Arial', 10),wrap=tk_constants.NONE,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
        self.input_box2.grid()
        sco1.config(command=self.input_box2.yview)
        sco2.config(command=self.input_box2.xview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        sco2.grid(row=1,column=0,sticky=tkinter.W+tkinter.E)
        frame_m10.pack()
        tkinter.Canvas(self.game_terminal_frame,width=2000, height=9).pack()
        frame_m4 = tkinter.Frame(self.game_terminal_frame)
        tkinter.Button(frame_m4,text="执行", bg='pink',fg='black',font=('Arial', 11), width=5, height=1, command=self.send_command).pack(side='left')
        tkinter.Canvas(frame_m4,width=5, height=5).pack(side='left')
        tkinter.Button(frame_m4,text="命令", bg='pink',fg='black',font=('Arial', 11), width=5, height=1, command=self.creat_windows_world).pack(side='left')
        tkinter.Canvas(frame_m4,width=5, height=5).pack(side='left')
        tkinter.Button(frame_m4,text='退出',bg='pink',font=('Arial', 11),width=5, height=1,command=self.exit_world).pack(side='left')
        frame_m4.pack()
        self.add_can_change_hight_component([self.input_box2,a1,sco2,9,frame_m4])


        self.expand_pack_frame = tkinter.Frame()
        a1 = tkinter.Label(self.expand_pack_frame,text="拓展包安装",bg='#82aaff',fg='black',font=('Arial',20),width=15,height=1)
        a1.pack()
        tkinter.Canvas(self.expand_pack_frame ,width=2000, height=8).pack()
        frame_m5 = tkinter.Frame(self.expand_pack_frame)
        self.expand_sys_1 = tkinter.Button(frame_m5,text='安卓',font=('Arial', 11),bg='aquamarine' ,width=6, height=1,
                                       command=lambda:self.expand_list_platform("android"))
        self.expand_sys_1.pack(side='left')
        tkinter.Canvas(frame_m5,width=5,height=5).pack(side='left')
        self.expand_sys_2 = tkinter.Button(frame_m5,text='Win',font=('Arial', 11),bg='aquamarine' ,width=6, height=1,
                                       command=lambda:self.expand_list_platform("windows"))
        self.expand_sys_2.pack(side='left')
        tkinter.Canvas(frame_m5,width=5,height=5).pack(side='left')
        self.expand_sys_3 = tkinter.Button(frame_m5,text='iOS',font=('Arial', 11),bg='aquamarine' ,width=6, height=1,
                                       command=lambda:self.expand_list_platform("ios"))
        self.expand_sys_3.pack(side='left')
        frame_m5.pack()

        tkinter.Canvas(self.expand_pack_frame,width=2000,height=8).pack()
        frame_m10 = tkinter.Frame(self.expand_pack_frame)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.expand_select = tkinter.Listbox(frame_m10,font=('Arial',12),selectmode=tk_constants.SINGLE,height=15,width=23,yscrollcommand=sco1.set)
        self.expand_select.grid()
        sco1.config(command=self.expand_select.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()
        tkinter.Canvas(self.expand_pack_frame,width=10,height=10).pack()

        frame_m6 = tkinter.Frame(self.expand_pack_frame)
        tkinter.Button(frame_m6,text='安装',font=('Arial', 12),bg='pink' ,width=5, height=1,command=self.on_expand_install).pack(side='left')
        tkinter.Canvas(frame_m6,width=10, height=5).pack(side='left')
        tkinter.Button(frame_m6,text='重启',font=('Arial', 12),bg='pink' ,width=5, height=1,command=lambda:self.on_expand_enable(True)).pack(side='left')
        tkinter.Canvas(frame_m6,width=10, height=5).pack(side='left')
        tkinter.Button(frame_m6,text='启动',font=('Arial', 12),bg='pink' ,width=5, height=1,command=lambda:self.on_expand_enable(False)).pack(side='left')
        frame_m6.pack()
        self.add_can_change_hight_component([self.expand_select,a1,8,frame_m5,8,10,frame_m6])
        

        if 1 :
            self.setting_frame = tkinter.Frame()
            tkinter.Label(self.setting_frame,text="联网功能",fg='black',font=('Arial',18),width=15,height=1).pack()
            frame_0 = tkinter.Frame(self.setting_frame)
            tkinter.Button(frame_0,text='用户登录',font=('Arial', 12),bg='#66ccff' ,width=9, height=1,command=
                lambda : self.user_login_UI()).pack(side=tk_constants.LEFT)
            tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).pack(side=tk_constants.LEFT)
            tkinter.Button(frame_0,text='官方网站',font=('Arial', 12),bg='#66ccff' ,width=9, height=1,command=
                lambda : self.open_browser("https://commandsimulator.great-site.net")).pack(side=tk_constants.LEFT)
            frame_0.pack()

            tkinter.Canvas(self.setting_frame,width=15, height=padding_1).pack()
            tkinter.Label(self.setting_frame,text="软件帮助",fg='black',font=('Arial',18),width=15,height=1).pack()
            frame_0 = tkinter.Frame(self.setting_frame)
            tkinter.Button(frame_0,text='帮助文档',font=('Arial', 12), bg='#D369a9', width=9, height=1,
                           command = lambda : self.open_browser("http://localhost:32323")).grid(row=0,column=0)
            tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).grid(row=0,column=1)
            tkinter.Button(frame_0,text='常见问题',font=('Arial', 12),bg='#D369a9' ,width=9, height=1,
                           command = lambda : self.open_browser("https://missing254.github.io/cs-tool/tool/Question/")).grid(row=0,column=2)
            tkinter.Canvas(frame_0,width=15, height=padding_1//2).grid(row=1,column=0)
            tkinter.Button(frame_0,text='命令教程',font=('Arial', 12),bg='#0dd044' ,width=9, height=1,
                           command = lambda : self.open_browser("http://localhost:32323/tutorial/CommandGuide.html")).grid(row=2,column=0)
            tkinter.Button(frame_0,text='获取测试',font=('Arial', 12),bg='orange' ,width=9, height=1,
                           command = self.get_app_test).grid(row=2,column=2)
            frame_0.pack()
            
            tkinter.Canvas(self.setting_frame,width=15, height=padding_1).pack()
            tkinter.Label(self.setting_frame,text="软件信息",fg='black',font=('Arial',18),width=15,height=1).pack()
            frame_0 = tkinter.Frame(self.setting_frame)
            tkinter.Button(frame_0,text='使用许可',font=('Arial', 12),bg='#66ccff' ,width=9, height=1,
                           command = lambda : self.app_infomation("use")).grid(row=0,column=0)
            tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).grid(row=0,column=1)
            tkinter.Button(frame_0,text='隐私政策',font=('Arial', 12),bg='#66ccff' ,width=9, height=1,
                           command = lambda : self.app_infomation("privacy")).grid(row=0,column=2)
            tkinter.Canvas(frame_0,width=15, height=padding_1//2).grid(row=1,column=0)
            tkinter.Button(frame_0,text='关于软件',font=('Arial', 12),bg='#66ccff' ,width=9, height=1,
                           command = lambda : self.app_infomation("about")).grid(row=2,column=0)
            tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).grid(row=2,column=1)
            tkinter.Button(frame_0,text='启动日志',font=('Arial', 12),bg='orange' ,width=9, height=1,
                           command = lambda : [self.app_infomation("open")]).grid(row=2,column=2)
            frame_0.pack()

            tkinter.Canvas(self.setting_frame,width=15, height=padding_1).pack()
            tkinter.Label(self.setting_frame,text="联系作者",fg='black',font=('Arial',18),width=15,height=1).pack()
            frame_0 = tkinter.Frame(self.setting_frame)
            tkinter.Button(frame_0,text='提供赞助',font=('Arial', 12),bg='#66ccff' ,width=9, height=1,command=
                lambda : self.open_browser("https://afdian.net/u/3c2e5dc43fd111edb9c052540025c377")).pack(side=tk_constants.LEFT)
            tkinter.Label(frame_0,font=('Arial',10),width=1,height=1).pack(side=tk_constants.LEFT)
            tkinter.Button(frame_0,text='交流群',font=('Arial', 12),bg='#66ccff' ,width=9, height=1,command=
                lambda : self.open_browser("https://missing254.github.io/cs-tool/qq_group.html")).pack(side=tk_constants.LEFT)
            frame_0.pack()
            
        if 1 :
            self.login_frame = tkinter.Frame()
            tkinter.Canvas(self.login_frame,width=15, height=padding_1).pack()
            tkinter.Label(self.login_frame, text="请在下框输入账号", fg='black', font=('Arial', 12), width=28, height=1).pack()
            self.account_input_1 = tkinter.Entry(self.login_frame,width=28)
            self.account_input_1.pack()
            self.account_input_1.bind("<FocusIn>",lambda a : self.set_focus_input(a,self.account_input_1))
            tkinter.Canvas(self.login_frame,width=15, height=padding_1*2).pack()
            tkinter.Label(self.login_frame, text="请在下框输入通行码", fg='black', font=('Arial', 12), width=28, height=1).pack()
            self.account_input_2 = tkinter.Entry(self.login_frame,width=28)
            self.account_input_2.pack()
            self.account_input_2.bind("<FocusIn>",lambda a : self.set_focus_input(a,self.account_input_2))
            tkinter.Canvas(self.login_frame,width=15, height=padding_1*2).pack()
            tkinter.Button(self.login_frame,text='登      录',font=('Arial', 12),bg='#70db93' ,width=12, height=1,command=
                lambda : self.user_login()).pack()
            tkinter.Canvas(self.login_frame,width=15, height=padding_1*2).pack()
            tkinter.Label(self.login_frame, text="如果你没有账号\n请点击下方按钮注册", fg='black', font=('Arial', 12), width=28, height=2).pack()
            tkinter.Button(self.login_frame,text='用户注册',font=('Arial', 12),bg='#66ccff' ,width=17, height=1,command=
                lambda : self.open_browser("https://commandsimulator.great-site.net/register.html")).pack()
            tkinter.Label(self.login_frame, text="如果你需要通行码\n请点击下方按钮申领", fg='black', font=('Arial', 12), width=28, height=2).pack()
            tkinter.Button(self.login_frame,text='申领注册码',font=('Arial', 12),bg='#66ccff' ,width=17, height=1,command=
                lambda : self.open_browser("https://commandsimulator.great-site.net/forgot_pass.html")).pack()
            tkinter.Canvas(self.login_frame,width=15, height=padding_1*2).pack()
            tkinter.Button(self.login_frame,text='返      回',font=('Arial', 12),bg='#d19275' ,width=17, height=1,command=
                lambda : self.creat_windows_setting()).pack()

        self.policy_frame = tkinter.Frame()
        a1 = tkinter.Label(self.policy_frame, textvariable=self.app_policy_title,bg="#d98719",fg="white",font=('Arial', 12), width=21, height=1)
        a1.pack()
        frame_m10 = tkinter.Frame(self.policy_frame)
        sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
        self.input_box4 = tkinter.Text(frame_m10,show=None,height=19,width=25,font=('Arial', 11),yscrollcommand=sco1.set)
        self.input_box4.grid()
        sco1.config(command=self.input_box4.yview)
        sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        frame_m10.pack()
        a2 = tkinter.Button(self.policy_frame,text='返      回',font=('Arial', 12),bg='#d19275' ,width=17, height=1,
                       command=lambda : self.creat_windows_setting())
        a2.pack()
        self.add_can_change_hight_component([self.input_box4,a1,frame_m3,a2])

        if 1 :
            self.user_info_frame = tkinter.Frame()
            tkinter.Label(self.user_info_frame, text="用 户 信 息", bg='#82aaff',fg='black',font=('Arial', 20), width=15, height=1).pack()
            tkinter.Canvas(self.user_info_frame,width=2000, height=padding_1*3).pack()
            tkinter.Label(self.user_info_frame, text="账户", fg='black', font=('Arial', 12), width=22, height=1, justify="left").pack()
            self.user_info_1 = tkinter.Label(self.user_info_frame, text="", fg='black', font=('Arial', 12), width=22, height=1, justify="left")
            self.user_info_1.pack()
            tkinter.Canvas(self.user_info_frame,width=2000, height=int(padding_1*1.5)).pack()
            tkinter.Label(self.user_info_frame, text="创建日期", fg='black', font=('Arial', 12), width=22, height=1, justify="left").pack()
            self.user_info_2 = tkinter.Label(self.user_info_frame, text="", fg='black', font=('Arial', 12), width=22, height=1, justify="left")
            self.user_info_2.pack()
            tkinter.Canvas(self.user_info_frame,width=2000, height=int(padding_1*1.5)).pack()
            tkinter.Label(self.user_info_frame, text="支付点数", fg='black', font=('Arial', 12), width=22, height=1, justify="left").pack()
            self.user_info_3 = tkinter.Label(self.user_info_frame, text="", fg='black', font=('Arial', 12), width=22, height=1, justify="left")
            self.user_info_3.pack()
            tkinter.Canvas(self.user_info_frame,width=2000, height=int(padding_1*1.5)).pack()
            tkinter.Label(self.user_info_frame, text="挑战完成次数", fg='black', font=('Arial', 12), width=22, height=1, justify="left").pack()
            self.user_info_4 = tkinter.Label(self.user_info_frame, text="", fg='black', font=('Arial', 12), width=22, height=1, justify="left")
            self.user_info_4.pack()
            tkinter.Canvas(self.user_info_frame,width=2000, height=int(padding_1*1.5)).pack()
            tkinter.Button(self.user_info_frame,text='登出账户',font=('Arial', 12),bg='#db7093' ,width=17, height=1,command=
                lambda : [self.user_logout(),self.user_login_UI()]).pack()
            tkinter.Canvas(self.user_info_frame,width=2000, height=padding_1).pack()
            tkinter.Button(self.user_info_frame,text='返      回',font=('Arial', 12),bg='#d19275' ,width=17, height=1,command=
                lambda : self.creat_windows_setting()).pack()


    def clean_window(self):
        self.game_ready_frame.pack_forget()
        self.game_run_frame.pack_forget()
        self.expand_pack_frame.pack_forget()
        self.game_terminal_frame.pack_forget()
        self.setting_frame.pack_forget()
        self.login_frame.pack_forget()
        self.policy_frame.pack_forget()
        self.user_info_frame.pack_forget()
        self.world_config_frame.pack_forget()
        self.expand_exit_UI()
        self.focus_input = None
        self.calltip_win.hidetip()

    def creat_windows(self):
        self.annoce_frame.pack_forget()
        self.message.pack(side='bottom')
        self.menu_frame.pack()
        self.right_click_constant()
        self.creat_windows_world()

        if self.user_manager.save_data["open_app_count"] < 2 :
            aaa = tkinter.messagebox.askquestion('Title', '第一次使用\n是否需要阅读文档教程？\n(新手用户必看！！)', )
            if aaa == "yes" : self.open_browser("http://localhost:32323/tutorial/Instructions.html")

        if self.user_manager.save_data["open_app_count"] < 2 :
            aaa = tkinter.messagebox.askquestion('Title', '是否需要阅读常见疑问？\n(安卓用户必看！！)')
            if aaa == "yes" : self.open_browser("https://missing254.github.io/cs-tool/tool/Question/")

        self.user_manager.save_data["open_app_count"] += 1


    def mode_using(self,mode,word = None) : 
        if self.focus_input == None : 
            self.modify_state("你没有选择任何一个文本框",want_record=False) ; return None
        if mode == "select_all" : 
            self.focus_input.event_generate("<<SelectAll>>")
            self.modify_state("文字已全选",want_record=False)
        elif mode == "cut" : 
            if isinstance(self.focus_input,tkinter.Text) and hasattr(self.focus_input,"can_copy_tk_component") : 
                self.copy_text = get_selection_component(self.focus_input)
                if self.copy_text != None : self.focus_input.event_generate("<<Clear>>")
            else : 
                self.focus_input.event_generate("<<Cut>>") ; self.copy_text = None
            self.focus_input.event_generate("<ButtonRelease>")
            self.modify_state("文字已剪切",want_record=False)
        elif mode == "copy" : 
            if isinstance(self.focus_input,tkinter.Text) and hasattr(self.focus_input,"can_copy_tk_component") : 
                self.copy_text = get_selection_component(self.focus_input)
            else : 
                self.focus_input.event_generate("<<Copy>>") ; self.copy_text = None
            self.modify_state("文字已复制",want_record=False)
        elif mode == "paste" : 
            try : self.focus_input.delete(SEL_FIRST, SEL_LAST)
            except : pass
            if self.copy_text : 
                for i in self.copy_text :
                    if type(i) == type("") : self.focus_input.insert(INSERT,i)
                    elif isinstance(self.focus_input,tkinter.Text) :
                        if hasattr(self.focus_input,"can_copy_tk_component") and isinstance(i,type({})) : 
                            if hasattr(self.expand_pack_module,"paste_event") : self.expand_pack_module.paste_event(i["key_arg"])
            elif self.PythonActivity and self.Context :
                activity = self.PythonActivity.mActivity
                clipboard = activity.getSystemService(self.Context.CLIPBOARD_SERVICE)
                clip_data = clipboard.getPrimaryClip()
                if clip_data :
                    item = clip_data.getItemAt(0)
                    if len(item.getText()) : self.focus_input.insert(INSERT,item.getText())
                    else : self.focus_input.event_generate("<<Paste>>")
            else : self.focus_input.event_generate("<<Paste>>")
            self.focus_input.event_generate("<ButtonRelease>")
            self.modify_state("文字已粘贴",want_record=False)
        elif mode == "undo" : 
            try : self.focus_input.edit_undo()
            except : pass
            self.focus_input.event_generate("<ButtonRelease>")
            self.modify_state("已完成撤销操作",want_record=False)
        elif mode == "redo" : 
            try : self.focus_input.edit_redo()
            except : pass
            self.focus_input.event_generate("<ButtonRelease>")
            self.modify_state("已完成恢复操作",want_record=False)
        elif mode == "return" : 
            if not(isinstance(self.focus_input,tkinter.Entry) or isinstance(self.focus_input,ttk.Entry)) : 
                try : self.focus_input.delete(SEL_FIRST, SEL_LAST)
                except : pass
                self.focus_input.insert(INSERT,"\n")
            self.focus_input.event_generate("<ButtonRelease>")
            self.modify_state("已完成回车操作",want_record=False)
        elif mode == "clear" : 
            self.focus_input.event_generate("<<SelectAll>>")
            self.focus_input.event_generate("<<Clear>>")
            self.modify_state("已完成清空操作",want_record=False)
        elif mode == "input" :
            if isinstance(word,type("")) : return None
            try : self.focus_input.delete(SEL_FIRST, SEL_LAST)
            except : pass
            self.focus_input.insert(INSERT,word)
        elif mode == "line_select" :
            if isinstance(self.focus_input,tkinter.Text) : 
                line1 = self.focus_input.index(INSERT).split(".")[0]
                chr_count = len(self.focus_input.get("%s.0" % line1, "%s.end" % line1))
                self.focus_input.tag_add("sel", "%s.0" % line1, "%s.%s" % (line1 , chr_count))
            if isinstance(self.focus_input,tkinter.Entry) or isinstance(self.focus_input,ttk.Entry) : self.focus_input.event_generate("<<SelectAll>>")
        elif mode == "jump_line_start" :
            if isinstance(self.focus_input,tkinter.Text) : 
                line1 = self.focus_input.index(INSERT).split(".")[0]
                self.focus_input.see("%s.0" % line1) ; self.focus_input.mark_set(INSERT,"%s.0" % line1)
            if isinstance(self.focus_input,tkinter.Entry) or isinstance(self.focus_input,ttk.Entry) : 
                self.focus_input.icursor(0) ; self.focus_input.xview_moveto(0)
        elif mode == "jump_line_end" :
            if isinstance(self.focus_input,tkinter.Text) : 
                line1 = self.focus_input.index(INSERT).split(".")[0]
                self.focus_input.see("%s.end" % line1) ; self.focus_input.mark_set(INSERT,"%s.end" % line1)
            if isinstance(self.focus_input,tkinter.Entry) or isinstance(self.focus_input,ttk.Entry) : 
                self.focus_input.icursor(tk_constants.END) ; self.focus_input.xview_moveto(1)
        self.focus_input.focus_set()

    def set_paste_thread(self) :
        def aaa():
            while self.paset_thread_time : 
                self.paset_thread_time -= 1
                time.sleep(0.01)
        if self.paset_thread_time == 0 : 
            self.paset_thread_time = 10
            threading.Thread(target=aaa).start()
        self.paset_thread_time = 10

    def set_focus_input(self,event,compont) :
        if isinstance(compont,tkinter.Text) or isinstance(compont,tkinter.Entry) or isinstance(compont,ttk.Entry) : 
            self.focus_input = compont
        else : 
            self.focus_input = None ; return None

        def aaaa(event : tkinter.Event) :
            self.calltip_win.hidetip()
            if self.PythonActivity and self.Context :
                activity = self.PythonActivity.mActivity
                inputMethodManager = activity.getSystemService(self.Context.INPUT_METHOD_SERVICE)
                isInputOpen = inputMethodManager.inputMethodWindowVisibleHeight
                if not isInputOpen : inputMethodManager.toggleSoftInput(0, 0)
        
        def bbbb(event : tkinter.Event) :
            try : 
                start_index = event.widget.index(SEL_FIRST)
                end_index = event.widget.index(SEL_LAST)
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

        if not hasattr(compont,"is_bind_click") :
            compont.bind("<Button-1>",aaaa,add="+")
            if jnius : compont.bind("<KeyPress>",cccc,add="+")
            if hasattr(compont,"can_copy_tk_component") : compont.bind("<B1-Motion>",bbbb,add="+")
            compont.is_bind_click = True

    def add_can_change_hight_component(self,component_list:list) :
        # 第一个为变高元素，其他为基准元素
        self.change_hight_component_list.append([-1,-1] + component_list)
        #List[ 像素每行, 最大行数, component_list ]



    def creat_windows_world(self):
        if not self.in_game_tag :
            self.clean_window()
            self.game_ready_frame.pack()
        else :
            self.clean_window()
            self.game_run_frame.pack()
            self.input_box1.focus_get()

    def creat_terminal(self):
        self.clean_window()
        self.game_terminal_frame.pack()
        self.input_box2.config(state="normal")
        self.input_box2.delete("0.0","end")
        self.input_box2.insert("end","\n".join(self.terminal_log))
        self.input_box2.config(state="disabled")

    def creat_windows_expand(self):
        if not self.user_manage.info_update : 
            self.modify_state("正在获取软件信息,请稍后....\n可在设置—>启动日志查看","info")
        else :
            self.clean_window()
            self.expand_pack_frame.pack()

    def creat_windows_pack(self):
        self.clean_window()
        if hasattr(self.expand_pack_module,"Menu_set") : self.expand_pack_module.Menu_set(self.popupmenu)
        self.expand_pack_ui_frame.pack()
        self.in_expand_pack_ui = True

    def expand_exit_UI(self) :
        self.expand_pack_ui_frame.pack_forget()
        while self.popupmenu.item_counter > 5 : self.popupmenu.remove_item()
        if self.copy_text and type({}) in [type(i) for i in self.copy_text] : self.copy_text = []
        if self.in_expand_pack_ui and hasattr(self.expand_pack_class,"exit_method") : self.expand_pack_class.exit_method()
        self.in_expand_pack_ui = False

    def creat_windows_setting(self):
        self.modify_state("",want_record=False)
        self.clean_window()
        self.setting_frame.pack()

    def user_login_UI(self) :
        self.clean_window()
        if self.user_manage.get_account_info() == None : self.login_frame.pack()
        else :
            json1 = self.user_manage.get_account_info()
            self.user_info_1.config(text=json1['account'])
            self.user_info_2.config(text=json1['creat_date'])
            self.user_info_3.config(text=json1['pay_point'])
            self.user_info_4.config(text=json1['challenge'])
            self.user_info_frame.pack()

    def app_infomation(self,mode:str) :
        a = {"use":"使用条款","privacy":"隐私条款","about":"关于命令模拟器","open":"启动日志"}
        self.clean_window()
        self.policy_frame.pack()
        self.input_box4.config(state="normal",wrap="char" if mode != "open" else "none")
        self.input_box4.delete("0.0","end")
        self.app_policy_title.set(a[mode])
        if mode == "use" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","use.txt"))
        elif mode == "privacy" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","privacy.txt"))
        elif mode == "about" : text1 = file_IO.read_a_file(os.path.join("main_source","app_policy","about_app.txt"))
        elif mode == "open" : 
            self.modify_state("正在显示启动日志....\n刷新内容需要重新进入该界面")
            text1 = "\n".join([i.log_text for i in self.all_load_log])
        self.input_box4.insert("end",text1)
        self.input_box4.config(state="disabled")

    def get_app_test(self) :
        
        def online() :
            data1 = {"userdata":self.user_manage.get_account()} if (self.user_manage.get_account() != None) else None
            if data1 == None : self.modify_state("用户需要登录才能下载") ; return None

            if connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL) != None : self.modify_state("正在获取测试...\n(1/3)", "info")
            else : self.modify_state("网络连接验证失败") ; return None 

            response1 = connent_API.request_url_without_error(connent_API.APP_TEST,data1,self.user_manage.save_data['cookies']["api_web_cookie"])
            if response1 == None : self.modify_state("网络异常-1") ; return None
            self.user_manage.save_data['cookies']["api_web_cookie"] = connent_API.request_headers["cookie"]

            json1 = json.loads(response1)
            if 'stat_code' in json1 and json1['stat_code'] > 0 : self.modify_state(json1['msg']) ; return None
            elif 'stat_code' not in json1 : self.modify_state("网络下送数据异常") ; return None
            elif 'app_test' not in json1 : self.modify_state("网络下送数据异常") ; return None

            self.modify_state("正在部署测试...\n(2/3)", "info")
            zip1 = zipfile.ZipFile(io.BytesIO(base64.b64decode(json1['app_test']["files"])),"r")
            zip1.extractall("")
            zip1.close()

            for iii in json1["app_test"]['import'] :
                self.modify_state("正在安装 " + iii + "\n请稍后...", "info")
                m1 = subprocess.getstatusoutput("pip3 install " + iii)
                if not m1[0] : continue
                file_IO.write_a_file(os.path.join("log","install_pack.txt"),m1[1])
                self.modify_state("".join(["依赖库 ",iii," 安装失败","\n","日志 install_pack.txt 已保存"]),"error")
                return None
            
            for iii in json1["app_test"]['register_pack'] :
                self.user_manage.save_data["install_pack_list"][iii] = ""
            if json1["app_test"]['register_pack'] : self.user_manage.write_back()
            
            self.modify_state("测试部署完成", "info")

        def run_online() :
            online()
            self.is_installing = False

        if not self.is_installing :
            self.is_installing = True
            threading.Thread(target=run_online).start()




    def in_game_check(self):
        if self.is_installing :
            self.modify_state("错误：你还在安装拓展包","error")
            return False
        else :
            if self.in_game_tag :
                self.modify_state("错误：你还在游戏中","error")
                return False
            else : return True

    def version_check(self):
        if self.select_java.get() : self.select_version = "java"
        elif self.select_bedrock.get() : self.select_version = "bedrock"

        if (self.select_java.get() ^ self.select_bedrock.get()) : return True
        else :
            self.modify_state("错误：请选择一个版本",error)
            return False

    def modify_state(self,text,want_display=True):
        if want_display : self.message_feedback.set(text)

    def modify_world_state(self,text,want_display=True):
        if want_display : self.world_feedback.set(text)


    def click_java(self):
        if self.in_game_check() :
            self.select_version = "java"
            #exec(file_IO.read_a_file(java_nbt_class_main_path),None,globals())
            self.version_1.deselect()
            self.version_2.select()
            self.click_bedrock()
            self.modify_state("java 正在开摆\n自动选择be",info,false)

    def click_bedrock(self):
        try : import brotli
        except :
            self.modify_state("你还没有安装原版拓展","error")
            self.version_2.deselect()
            return None

        if self.in_game_check() :
            self.select_version = "bedrock"
            exec(compile_file(bedrock_nbt_class_main_path),None,globals())
            exec(compile_file(bedrock_command_class_main_path),None,globals())
            self.version_2.select()
            if self.select_bedrock.get() :
                self.version_1.deselect()
                self.flash_world()


    def flash_world(self):
        main_windows_function.flash_list(self)
        gc.collect()


    def close_window_normal(self):
        try : self.exit_world( )
        except : 
            try : self.exit_world( )
            except : pass
        self.user_manage.write_back( )
        time.sleep(0.5)
        os._exit(0)

    def close_window_force(self):
        self.user_manage.write_back( )
        os._exit(0)


    def open_browser(self,url1):
        if url1 : webbrowser.open(url1)

    def create_world(self):
        try : import brotli
        except : self.modify_state("你还没有安装原版拓展","error")
        else : 
            if not self.version_check() : return None
            main_windows_function.create_world(self)
            self.clean_window()
            self.world_config_frame.pack()

    def delete_world(self):
        main_windows_function.delete_world(self)

    def join_world(self):
        if True in [i.is_alive() for i in self.thread_loading] :
            self.modify_state("正在加载软件,请稍后....\n可在设置—>启动日志查看","info")
        if self.in_game_check():
            if len(self.list_select.curselection()) :
                try : 
                    import brotli
                except :
                    self.modify_state("错误: 未安装完整原版拓展\n请在拓展包中选择相应平台安装","error") ; return None
                main_windows_function.join_world(self)
                self.in_game_tag = True ; self.creat_windows_world()
            else : self.modify_state("错误: 无任何选择","error")

    def exit_world(self):
        if not self.in_game_check():
            main_windows_function.leave_world(self)
            self.in_game_tag = False
            self.creat_windows_world()
        else :
            self.modify_state("错误：你并没有加入游戏","error")
        threading.Thread(target = lambda : [time.sleep(5) , gc.collect()]).start()

    def send_command(self):
        if not self.in_game_check() and game_process.game_load_over : main_windows_function.execute_command(self)
        else :
            if not game_process.game_load_over : self.modify_state("错误：请等待游戏刻变化后\n发送命令",error)


    def creat_be_verification_challenge_world(self) :
        global game_process
        if hasattr(game_process,"in_game_tag") and game_process.in_game_tag : self.exit_world()
        self.modify_state("","info",want_record=False)
        self.click_bedrock()
        self.creat_button_count = 2
        world_config_copy = copy.deepcopy(world_config)
        world_config_copy['normal_setting']['simulator_distance'] = 6
        world_config_copy['normal_setting']['world_name'] = "每周挑战%s"%random.randint(100,999)
        random_id = random.randint(2**63,2**64)
        name_of_world = main_windows_function.create_world_treading(self, world_config_copy, challenge=True, challenge_id=random_id)
        return (random_id,name_of_world)

    def check_challenge_world_vaild(self,world_name) :
        return main_windows_function.check_world_vaild(world_name)

    def join_verification_challenge_world(self,name_of_world) :
        try : import brotli
        except :
            self.modify_state("错误: 未安装原版拓展\n请在拓展包中选择相应平台安装","error") ; return None
        if not main_windows_function.check_world_vaild(name_of_world) : 
            self.modify_state("错误: 挑战世界不存在","error") ; return None
        if hasattr(game_process,"in_game_tag") and game_process.in_game_tag : self.exit_world()
        self.modify_state("","info",want_record=False)
        self.click_bedrock()
        main_windows_function.join_world(self,name_of_world)
        self.in_game_tag = True ; self.creat_windows_world()


    def update_expand_list(self):
        # 根据平台更新expand_select
        ## 原版拓展
        vanilla_data = VANILLA_EXPANDS[self.platform]
        all_expands = {vanilla_data[0]: vanilla_data[1]}
        ## 通用拓展
        all_expands.update(self.user_manage.save_data["expand_packs"])
        ## 平台特有
        all_expands.update(self.user_manage.save_data["expand_packs_" + self.platform])
        ## 清理
        self.current_expands.clear()
        self.expand_select.delete(0, "end")
        ## 排序（已安装在前）
        self.expand_uuids = sorted(
            all_expands,
            key = lambda uid: uid not in self.user_manage.save_data["install_pack_list"]
        )
        for uid in self.expand_uuids:
            pack = all_expands[uid]
            self.current_expands[uid] = pack
            if uid in self.user_manage.save_data["install_pack_list"]:
                self.expand_select.insert("end", "[\u2714]%s" % pack["pack_name"])
            else:
                self.expand_select.insert("end", pack["pack_name"])

    def update_platform_buttons(self):
        # 根据平台刷新按钮样式
        d = {"android": self.expand_sys_1, "windows": self.expand_sys_2, "ios": self.expand_sys_3}
        selected = d.pop(self.platform)
        # 按下的平台按钮
        selected.configure(state=tkinter.tk_constants.DISABLED)
        # 未按下的
        for unselected in d.values() : unselected.configure(state=tkinter.tk_constants.NORMAL)

    def expand_list_platform(self,sys_name:str) :
        self.platform = sys_name
        self.update_platform_buttons()
        if sys_name == "ios" : 
            self.modify_state("%s系统暂不支持"%sys_name)
            self.expand_select.delete(0,tk_constants.END)
            return None
        a = {"android":"安卓","windows":"windows","ios":"ios"}
        self.modify_state("你已选择%s系统"%a[sys_name])
        self.update_expand_list()

    def get_selecting_expand(self):
        # 获取当前选择拓展包的uuid
        select = self.expand_select.curselection()
        if len(select) == 0 :
            self.modify_state("错误：你没有选择拓展包","error")
            return None
        return self.expand_uuids[select[0]]

    def on_expand_install(self):
        if self.is_installing : return None
        uid = self.get_selecting_expand()
        if uid is None : return None
        # 判断已安装
        if uid in self.user_manage.save_data["install_pack_list"] and \
            self.user_manage.save_data["install_pack_list"][uid] == self.current_expands[uid]["version"]:
            self.modify_state("%s\n已安装且无更新，正在重新安装" % (
                self.current_expands[uid]["pack_name"]
            ), "warning")
        # 判断是否是原版拓展
        if uid == VANILLA_EXPANDS[self.platform][0] : func = self.vanilla_expand_install
        else : func = self.thirdparty_expand_install
        threading.Thread(target = lambda: func(uid)).start()

    def vanilla_expand_install(self, uid):
        # 安装原版拓展包
        self.is_installing = True

        if not self.platform:
            self.modify_state("错误：你没有选择设备系统", "error")
            return

        aaa = tkinter.messagebox.askquestion('Title', '如果你是首次安装\n请保持软件处于前台模式\n安装时间需要大约2分钟\n\n部分拓展包无需原版拓展！！', )
        if aaa != "yes" : return None


        if uid == VANILLA_EXPANDS["ios"][0] :
            self.modify_state("iOS 支持敬请期待", "info")
            return

        elif uid == VANILLA_EXPANDS["windows"][0] :
            verfy1 = ["import brotli"]
            list1 = ["pip3 install brotlipy"]
            for i in enumerate(list1) :
                self.modify_state("正在安装 brotlipy\n请稍后...", "info")
                try : exec(verfy1[i[0]])
                except : 
                    m1 = subprocess.getstatusoutput(i[1])
                    if m1[0] :
                        file_IO.write_a_file(os.path.join("log","install_pack.txt"),m1[1])
                        self.modify_state("".join(["拓展包 ",i[1]," 安装失败","\n","日志 install_pack.txt 已保存"]),"error")
                        return None

        elif uid == VANILLA_EXPANDS["android"][0] :
            verfy1 = ["import brotli"]
            list1 = ["pip3 install brotlipy"]
            for i in enumerate(list1) :
                self.modify_state("正在安装 brotlipy\n请稍后...",info)
                try : exec(verfy1[i[0]])
                except : 
                    m1 = subprocess.getstatusoutput(i)
                    if m1[0] :
                        file_IO.write_a_file(os.path.join("log","install_pack.txt"),m1[1])
                        self.modify_state("".join(["拓展包 ",i," 安装失败","\n","日志 install_pack.txt 已保存"]),"error")
                        return None
        
        self.modify_state("正在下载材质图片\n请稍后...",info)
        a = connent_API.request_url_without_error(connent_API.BLOCK_TEXTURE_DOWNLOAD)
        if not a :
            self.modify_state("材质图片下载失败","error") ; return
        file_IO.write_a_file(os.path.join("html_output","picture","block_texture.png"),a,"writebyte")
                
        exec("import brotli",globals(),globals())
        self.modify_state("拓展包安装成功","info")

        self.user_manage.save_data["install_pack_list"][uid] = self.current_expands[uid]["version"]
        self.update_expand_list()
        self.is_installing = False

    def thirdparty_expand_install(self, uid):
        # 第三方包（非默认包）
        self.is_installing = True
        name1 = self.current_expands[uid]['pack_name']

        def installing() :
            data1 = {"userdata":self.user_manage.get_account(),'expand':self.get_selecting_expand()} if (self.user_manage.get_account() != None) else None
            if data1 == None : self.modify_state("用户需要登录才能下载") ; return None

            if connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL) != None : self.modify_state("正在获取安装包...\n(1/3)", "info")
            else : self.modify_state("网络连接验证失败") ; return None 

            response1 = connent_API.request_url_without_error(connent_API.UPDATE_EXPAND_PACK,data1,self.user_manage.save_data['cookies']["api_web_cookie"])
            if response1 == None : self.modify_state("网络异常-1") ; return None
            self.user_manage.save_data['cookies']["api_web_cookie"] = connent_API.request_headers["cookie"]

            json1 = json.loads(response1)
            if 'stat_code' in json1 and json1['stat_code'] > 0 : self.modify_state(json1['msg']) ; return None
            elif 'stat_code' not in json1 : self.modify_state("网络下送数据异常") ; return None
            elif 'url' not in json1 : self.modify_state("网络下送数据异常") ; return None

            self.modify_state("正在下载安装包...\n(2/3)", "info")
            response2 = connent_API.request_url_without_error(json1['url'])
            if response2 == None : self.modify_state('获取文件失败\n请重试') ; return None
            os.makedirs(os.path.join("expand_pack",uid), exist_ok=True)
            file_IO.write_a_file(os.path.join("expand_pack",uid,"saves.zip"),response2,'writebyte')

            path1 = os.path.join("expand_pack",uid,"saves.zip")
            if os.path.exists(path1) and os.path.isfile(path1) :
                if uid not in self.user_manage.save_data['expand_packs'] : 
                    self.modify_state("安装失败\n未收录的拓展包") ; os.remove(path1) ; return None
                if 'hash256' not in self.user_manage.save_data['expand_packs'][uid] : 
                    self.modify_state("安装失败\n拓展包无法校验") ; os.remove(path1) ; return None
                file1 = open(path1,"rb") ; bytes1 = file1.read() ; file1.close()
                if self.user_manage.save_data['expand_packs'][uid]['hash256'] != hmac.new(b'command_simulator_expand_pack' , bytes1, 'sha256').hexdigest() : 
                    self.modify_state("安装失败\n拓展包校验未通过") ; os.remove(path1) ; return None
                local_var = {"path_to_change":path1, "zip_path_1":os.path.join("expand_pack",uid)}
                with open(os.path.join("main_source","core_code","aaaaaa.py"),"rb") as e : exec(pickle.loads(e.read()),local_var,{})

            if len(self.current_expands[uid]['import']) : self.modify_state("正在下载依赖库...\n(3/3)", "info")
            for iii in self.current_expands[uid]['import'] :
                self.modify_state("正在安装 " + iii + "\n请稍后...", "info")
                m1 = subprocess.getstatusoutput("pip3 install " + iii)
                if not m1[0] : continue
                file_IO.write_a_file(os.path.join("log","install_pack.txt"),m1[1])
                self.modify_state("".join(["依赖库 ",iii," 安装失败","\n","日志 install_pack.txt 已保存"]),"error")
                return None
            
            self.modify_state(name1 + "\n安装成功") ; return True

        if installing() : 
            self.user_manage.save_data["install_pack_list"][uid] = self.current_expands[uid]["version"]
            self.update_expand_list()
            self.user_manage.write_back()
        self.is_installing = False



    def on_expand_enable(self,reload1) :
        uid = self.get_selecting_expand()
        if uid is None : return
        if uid in [VANILLA_EXPANDS[i][0] for i in VANILLA_EXPANDS] :
            self.modify_state("原版拓展 并不是拓展包\n请选择其他拓展包运行", warning)
            return None

        name1 = self.current_expands[uid]['pack_name']

        if uid not in self.user_manage.save_data["install_pack_list"]:
            self.modify_state(name1 + " 拓展包\n还未安装", "error")
            return None

        if (not debug_testing) and (self.user_manage.save_data["install_pack_list"][uid] != self.user_manage.save_data["expand_packs"][uid]['version']) :
            aaa = tkinter.messagebox.askquestion("Update" , name1 + "\n拓展包检测到有新版本\n是否进行更新",)
            if aaa == "yes" : self.on_expand_install() ; return None
            
        if self.enable_expand(uid,reload1) : self.creat_windows_pack()
        else : return None

    def enable_expand(self, uid, reload1):
        # 检查已安装
        name1 = self.current_expands[uid]["pack_name"]
        if uid not in self.user_manage.save_data["install_pack_list"] : self.modify_state("%s 拓展包\n你还未安装", "error")

        def _expand_error(err):
            traceback.print_exc(file=open(os.path.join("log","enable_expand.txt"), "w+",encoding="utf-8"))
            # 与Python解析拓展包有关错误
            self.modify_state("%s\n拓展包加载出错，日志已保存" % name1, "error")

        local_var = {"path_to_change" : os.path.join("expand_pack",uid,"saves.zip") , "zip_path_1" : os.path.join("expand_pack",uid)}
        try :
            if not debug_testing :
                with open(os.path.join("main_source","core_code","aaaaaa.py"),"rb") as e : exec(pickle.loads(e.read()),local_var,{})
        except Exception as err: 
            _expand_error(err) ; return

        # 加载拓展包主文件main.py
        if self.get_selecting_expand() not in self.expand_pack_open_list or reload1 :
            main_path = os.path.join("expand_pack", uid, "main.py")
            self.run_expand_path = os.path.join("expand_pack", uid)
            if not os.path.exists(main_path): self.modify_state("%s\n拓展包未找到入口文件" % name1, "error") ; return
            spec = importlib.util.spec_from_file_location("<expand %r>" % name1, main_path)
            self.expand_pack_module = module = importlib.util.module_from_spec(spec)
            try : spec.loader.exec_module(module)
            except Exception as err: _expand_error(err) ; return
        
        def reload_module(base_module:types.ModuleType) :
            pack_path = os.path.dirname(base_module.__file__)
            for keys in list(sys.modules.keys()) :
                if not hasattr(sys.modules[keys],"__file__") : continue
                if sys.modules[keys].__file__ == None : continue
                if base_module.__file__ == sys.modules[keys].__file__ : continue
                if pack_path in sys.modules[keys].__file__ : importlib.reload(sys.modules[keys])

        # 读取main.py
        try :
            self.expand_exit_UI() ; test11 = False
            if uid not in self.expand_pack_open_list or reload1 :
                if hasattr(self.expand_pack_class,"reload_method") : self.expand_pack_class.reload_method()
                reload_module(module) #重载拓展包模块
                self.expand_pack_open_list[uid] = {}
                self.expand_pack_open_list[uid]["frame"] = tkinter.Frame()
                self.expand_pack_open_list[uid]['module'] = module
                self.expand_pack_open_list[uid]['class'] = module.pack_class()
                test11 = True

            self.expand_pack_class = self.expand_pack_open_list[uid]['class']
            self.expand_pack_module = self.expand_pack_open_list[uid]['module']
            self.expand_pack_ui_frame = self.expand_pack_open_list[uid]["frame"]
            if test11 : self.expand_pack_module.UI_set(self)
            if hasattr(self.expand_pack_module,"Menu_set") : self.expand_pack_module.Menu_set(tkinter.Menu(self.window,tearoff=False))

        except Exception as err: 
            _expand_error(err)
            if uid in self.expand_pack_open_list : del self.expand_pack_open_list[uid]
        else : self.modify_state("%s\n拓展包启动成功\n如果是第一次使用，查阅帮助文档" % name1, "info") ; return True



    def all_time_loop_event(self) :
        global game_process
        while 1 :
            try : 
                for i in list(self.expand_pack_open_list.keys()) :
                    if i not in self.expand_pack_open_list : continue
                    self.expand_pack_open_list[i]['class'].debug_windows = self
                    self.expand_pack_open_list[i]['class'].game_process = game_process
                    if hasattr(self.expand_pack_open_list[i]['class'],'loop_method') : self.expand_pack_open_list[i]['class'].loop_method()
            except : traceback.print_exc()
            for list1 in self.change_hight_component_list :
                try :
                    list1 : List[Union[int,int,tkinter.Text,tkinter.Text,tkinter.Text]]
                    if list1[0] == -1 : 
                        list1[0] = list1[2].winfo_reqheight() // list1[2].cget("height")
                        list1[1] = list1[2].cget("height")
                    blank_height = self.message.winfo_rooty() - self.menu_frame.winfo_rooty() - self.menu_frame.winfo_height()
                    for i in list1[3:] : blank_height -= i if isinstance(i,int) else i.winfo_reqheight()
                    if list1[2].cget("height") != min(list1[1], blank_height // list1[0] - 1) :
                        list1[2].config(height = min(list1[1], blank_height // list1[0] - 1))
                except : pass

            time.sleep(0.5)

    def open_windows(self):
        self.copy_text = None

        self.all_load_log = [load_log_file(),load_log_file(),load_log_file(),load_log_file()]
        global_dict = globals().copy() ; global_dict['load_log'] = self.all_load_log[0]
        thread1 = threading.Thread(target=exec,args=(compile_file(app_load_code_path),global_dict,{}))
        thread1.start()

        global_dict = globals().copy() ; global_dict['load_log'] = self.all_load_log[1]
        thread2 = threading.Thread(target=exec,args=(compile_file(bedrock_id_load_code_path),global_dict,{}))
        thread2.start()

        global_dict = globals().copy() ; global_dict['load_log'] = self.all_load_log[2] ; global_dict["root_thread"] = thread1
        thread3 = threading.Thread(target=exec,args=(compile_file(bedrock_source_load_code_path),global_dict,{}))
        thread3.start()

        self.thread_loading = [thread1,thread2,thread3]
        threading.Thread(target=exec,args=(compile_file(bedrock_load_end_path),globals().copy(),
                        {"load_log":self.all_load_log[3],"thread_list":self.thread_loading})).start()
        #threading.Thread(target=exec,args=(compile_file(java_load_code_path),globals(),{})).start()
        threading.Thread(target=self.all_time_loop_event).start()
        self.annoce_frame.pack() ; self.windows_run = True ; self.window.mainloop()

    def user_login(self) :
        def start_login() :
            self.in_login = True
            self.modify_state("正在登录...") ; self.user_send_login()
            self.in_login = False
        if not self.in_login : threading.Thread(target=start_login).start()
        else : self.modify_state("请等待登录完成...")

    def user_send_login(self) : 
        if re.search("^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$",self.account_input_1.get()) == None :
            self.modify_state("用户邮箱格式不正确") ; return None
        if re.search("^[a-zA-Z0-9]+$",self.account_input_2.get()) == None  :
            self.modify_state("用户通行码格式不正确") ; return None
        
        login_info_1 = {"account":self.account_input_1.get(), "pass_code":self.account_input_2.get()}
        login_info_2 = base64.b64encode(json.dumps(login_info_1).encode("utf-8")).decode("utf-8")

        if connent_API.request_url_without_error(connent_API.TEST_BAIDU_URL) != None : self.modify_state("正在登录...", "info")
        else : self.modify_state("网络连接验证失败") ; return None 

        response2 = connent_API.request_url_without_error(connent_API.MANUAL_LOGIN,{"userdata":login_info_2},self.user_manage.save_data['cookies']["api_web_cookie"])
        result1 = self.user_manage.write_account(login_info_1['account'],login_info_1['pass_code'],response2.decode("utf-8") if response2 != None else "")
        if result1 : 
            self.user_manage.save_data['cookies']["api_web_cookie"] = connent_API.request_headers["cookie"]
            self.modify_state(result1[1])
        else : self.modify_state("登录失败")

        self.user_login_UI()

    def user_logout(self) : 
        self.user_manage.write_account('','','')



    def get_user(self) :
        return self.user_manage.get_account()

    def get_blank_height(self) :
        return self.message.winfo_rooty() - self.menu_frame.winfo_rooty() - self.menu_frame.winfo_height()
        


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
        if not hasattr(self.expand_pack_open_list[post_json["pack_id"]]['class'],"do_POST") : 
            return {"state" : 6 , "msg" : "拓展包并没有指定Post处理方法"}
        return self.expand_pack_open_list[post_json["pack_id"]]['class'].do_POST(post_json)


    def add_topic(self,on_toplevel_open:types.FunctionType) :
        second_window = tkinter.Toplevel(self.window)
        second_window.resizable(False, False)
        second_window.geometry('%sx%s+%s+%s'%(self.small_win_width,self.small_win_height,self.window.winfo_x(),self.window.winfo_y()))

        second_window.transient(self.window)
        on_toplevel_open(second_window)


    def right_click_constant(self) :
        self.search_translate_id = search_id_object()
        self.small_win_width,self.small_win_height = int(self.window.winfo_width()*0.95),int(self.window.winfo_height()*0.43)
        self.popupmenu = popupmenu = tk_tool.tk_Menu(self.window,tearoff=False,font=('Arial', 10))
        popupmenu.add_command(label="快捷全选复制",command=lambda:[self.mode_using("select_all"),self.mode_using("copy")])
        popupmenu.add_command(label="复制特殊字符",command=self.add_special_char)
        popupmenu.add_command(label="批量复制字符",command=self.add_char)
        popupmenu.add_command(label="查询游戏内ID",command=self.find_id)
        popupmenu.add_command(label="复制文件命令",command=self.copy_file_command)
        self.window.bind("<Button-3>", lambda event : popupmenu.post(event.x_root, event.y_root - popupmenu.winfo_reqheight()))

    def add_special_char(self) : 
        def add(second_window : tkinter.Toplevel) :
            second_window.title('特殊字符')
            Image_list = [(
                tkinter.PhotoImage(file=mc_be_icon.tk_Image(i)) if platform.system() == 'Windows' else tkinter.PhotoImage(file=mc_be_icon.tk_Image(i)).zoom(4,4)
                ) for i in mc_be_icon.icon_list]
            frame_icon = tkinter.Frame(second_window)
            second_window.image_group = Frame_list = [tkinter.Frame(frame_icon) for i in range((len(mc_be_icon.icon_list)//4) + 1)]
            tkinter.Button(frame_icon,width=1,height=5,text="←",bg="#c8bfe7",command=lambda : change_page(-1)).pack(side=tk_constants.LEFT)
            tkinter.Button(frame_icon,width=1,height=5,text="→",bg="#c8bfe7",command=lambda : change_page(1)).pack(side=RIGHT)
            frame_icon.pack()
            second_window.display_id,second_window.mode_id = 0,"ByteCode"

            def change_page(value) : 
                second_window.display_id += value
                if second_window.display_id * 4 > len(second_window.image_group) : second_window.display_id = 0
                if second_window.display_id < 0 : second_window.display_id = len(second_window.image_group) // 4
                for i in range(len(second_window.image_group)) :
                    if (second_window.display_id * 4) <= i < ((second_window.display_id + 1) * 4) :
                        second_window.image_group[i].pack()
                    else : second_window.image_group[i].pack_forget()
                text1.config(text="第%s页"%(second_window.display_id+1,))

            frame_button = tkinter.Frame(second_window)
            buttom1 = tkinter.Button(frame_button,width=10,height=1,text="复制源字符",bg="#b4f0c8",font=('Arial', 9),command=lambda : mode_change("ByteCode"),state=tk_constants.DISABLED)
            buttom1.pack(side=tk_constants.LEFT)
            buttom2 = tkinter.Button(frame_button,width=10,height=1,text="复制Unicode",bg="#b4f0c8",font=('Arial', 9),command=lambda : mode_change("Unicode"))
            buttom2.pack(side=tk_constants.LEFT)
            text1 = tkinter.Label(frame_button,width=6,height=1,text="第%s页"%(second_window.display_id+1,),font=('Arial', 9))
            text1.pack(side=tk_constants.LEFT)
            frame_button.pack(side=tk_constants.BOTTOM)
            label1 = tkinter.Label(second_window,width=25,height=1,text="点击上方图标即可直接复制",font=('Arial', 9))
            label1.pack(side=tk_constants.BOTTOM)

            def mode_change(mode) : 
                second_window.mode_id = mode
                if second_window.mode_id == "ByteCode" : buttom1.config(state=tk_constants.DISABLED)
                else : buttom1.config(state=tk_constants.NORMAL)
                if second_window.mode_id == "Unicode" : buttom2.config(state=tk_constants.DISABLED)
                else : buttom2.config(state=tk_constants.NORMAL)

            def mode_effect(event : tkinter.Event) :
                word_id = event.widget.word_id.replace(".gif","")
                aaa = tkinter.Entry(second_window)
                aaa.focus_set()
                if second_window.mode_id == "ByteCode" :
                    aaa.insert("0",chr(int(word_id, 16)))
                    aaa.selection_range("0","1")
                    aaa.event_generate("<<Copy>>")
                    label1.config(text="元字符%s已存入剪切板"%(word_id,))
                if second_window.mode_id == "Unicode" : 
                    aaa.insert("0","\\u" + word_id)
                    aaa.selection_range("0","6")
                    aaa.event_generate("<<Copy>>")
                    label1.config(text="Unicode字符%s已存入剪切板"%(word_id,))

            for i,j in enumerate(Image_list) : 
                label = tkinter.Label(Frame_list[i//4],image=j)
                label.word_id = mc_be_icon.icon_list[i]
                label.bind('<Button-1>',lambda event : mode_effect(event))
                label.pack(side=tk_constants.LEFT)
            Frame_list[0].pack(); Frame_list[1].pack(); Frame_list[2].pack(); Frame_list[3].pack()
            second_window.mainloop()
        self.add_topic(add)

    def add_char(self) :
        def add(second_window : tkinter.Toplevel) :

            def get_str(only_test:bool=False) : 
                Unicode_collect.tag_remove("red","0.0",tk_constants.END)
                text1 = Unicode_collect.get("0.0",tk_constants.END)[:-1].split("\n")
                test_str1,test_str2 = "^\\\\u[a-fA-F0-9]{4}$","^\\\\u[a-fA-F0-9]{4}~\\\\u[a-fA-F0-9]{4}$"
                list1 = [bool(re.search(test_str1,text1[i]) or re.search(test_str2,text1[i])) for i in range(len(text1))]
                if (False in list1) : 
                    i = list1.index(False) ; label1.config(text = "第%s行格式错误"%(i+1,)) 
                    Unicode_collect.see("%s.%s"%(i+1,len(text1[i])))
                    Unicode_collect.tag_add("red","%s.0"%(i+1,),"%s.%s"%(i+1,len(text1[i])))
                    return False
                if only_test : return True
                entry1 = tkinter.Entry()
                for i in range(len(text1)) :
                    if re.search(test_str1,text1[i]) :
                        entry1.insert(tk_constants.END, chr(int("0x" + text1[i].replace("\\u",""),16)))
                    elif re.search(test_str2,text1[i]) :
                        text2 = text1[i].split("~")
                        start1,end1 = int("0x" + text2[0].replace("\\u",""),16) , int("0x" + text2[1].replace("\\u",""),16)
                        while start1 <= end1 :
                            entry1.insert(tk_constants.END, chr(start1)) ; start1 += 1
                entry1.selection_range("0",tk_constants.END)
                entry1.event_generate("<<Copy>>")
                label1.config(text = "Unicode字符已全部存入剪切板")

            def add_faver_1() :
                if not get_str(True) : return None
                frame_save_name.pack()
                frame_copy_str.pack_forget()

            def add_faver_2() :
                self.user_manage.save_data["faver_string"][Name_collect.get()] = Unicode_collect.get("0.0",tk_constants.END)[:-1]
                self.user_manage.write_back()
                frame_save_name.pack_forget()
                flesh_faver_and_open()

            def flesh_faver_and_open() :
                search_result.delete(0,tk_constants.END)
                for i in list(self.user_manage.save_data["faver_string"]) :
                    if type(self.user_manage.save_data["faver_string"][i]) != type("") : del self.user_manage.save_data["faver_string"][i]
                    else : search_result.insert(tk_constants.END,str(i))
                frame_copy_str.pack_forget()
                frame_save_name.pack_forget()
                copy_faver_frame.pack()

            def start_copy():
                if len(search_result.curselection()) == 0 : 
                    label10.config(text="未选择需要复制的收藏") ; return
                select = search_result.curselection()[0]
                m1 = Unicode_collect.get("0.0",tk_constants.END)[:-1]
                Unicode_collect.delete("0.0",tk_constants.END)
                Unicode_collect.insert(tk_constants.END,self.user_manage.save_data["faver_string"][search_result.get(select)])
                get_str()
                Unicode_collect.delete("0.0",tk_constants.END)
                Unicode_collect.insert(tk_constants.END,m1)
                label10.config(text="收藏复制成功")

            def delete_faver() :
                if len(search_result.curselection()) == 0 : 
                    label10.config(text="未选择需要复制的收藏") ; return
                select = search_result.curselection()[0]
                del self.user_manage.save_data["faver_string"][search_result.get(select)]
                self.user_manage.write_back()
                flesh_faver_and_open()
                label10.config(text="删除成功")


            second_window.title('批量复制')
            
            tkinter.Label(second_window, text="",fg='black',font=('Arial', 6), width=15, height=1).pack()
            
            frame_copy_str = tkinter.Frame(second_window)
            Unicode_collect = tkinter.Text(frame_copy_str, show=None, height=4, width=30, font=('Arial', 10))
            Unicode_collect.bind("<FocusIn>",lambda a : self.set_focus_input(a,Unicode_collect))
            Unicode_collect.pack()
            Unicode_collect.tag_config("red",background='red')
            tkinter.Label(frame_copy_str, text="",fg='black',font=('Arial', 6), width=15, height=1).pack()

            frame_m3 = tkinter.Frame(frame_copy_str)
            tkinter.Button(frame_m3,text='批量复制',font=('Arial',10),bg='aquamarine',width=8,height=1,command=get_str).pack(side='left')
            tkinter.Label(frame_m3, text="",fg='black',font=('Arial', 6), width=1, height=1).pack(side='left')
            tkinter.Button(frame_m3,text='退出窗口',font=('Arial',10),bg='aquamarine',width=8,height=1,command=second_window.destroy).pack(side='left')
            frame_m3.pack()
            frame_m3 = tkinter.Frame(frame_copy_str)
            tkinter.Button(frame_m3,text='添加收藏',font=('Arial',10),bg='pink',width=8,height=1,command=add_faver_1).pack(side='left')
            tkinter.Label(frame_m3, text="",fg='black',font=('Arial', 6), width=1, height=1).pack(side='left')
            tkinter.Button(frame_m3,text='打开收藏',font=('Arial',10),bg='pink',width=8,height=1,command=flesh_faver_and_open).pack(side='left')
            frame_m3.pack()

            tkinter.Label(frame_copy_str, text="",fg='black',font=('Arial', 1), width=15, height=1).pack()
            label1 = tkinter.Label(frame_copy_str, text="请使用\\uXXXX或\n\\uXXXX~\\uXXXX格式填写\nXXXX为4位16进制，可多行",fg='black',font=('Arial', 10), width=22, height=3)
            label1.pack()
            label2 = tkinter.Label(frame_copy_str, text="点击查询更多字符",fg='blue',font=('Arial', 10), width=22, height=1)
            label2.pack()
            label2.bind("<Button-1>",lambda e:self.open_browser("https://missing254.github.io/cs-tool/tool/Unicode/page_1.html"))
            frame_copy_str.pack()


            frame_save_name = tkinter.Frame(second_window)
            tkinter.Label(frame_save_name, text="为该收藏的命名",fg='blue',font=('Arial', 10), width=22, height=1).pack()
            tkinter.Label(frame_save_name, text="",fg='black',font=('Arial', 6), width=15, height=1).pack()
            Name_collect = tkinter.Entry(frame_save_name, width=30, font=('Arial', 10))
            Name_collect.bind("<FocusIn>",lambda a : self.set_focus_input(a,Name_collect))
            Name_collect.pack()

            tkinter.Label(frame_save_name, text="",fg='black',font=('Arial', 6), width=15, height=1).pack()
            frame_m3 = tkinter.Frame(frame_save_name)
            tkinter.Button(frame_m3,text='确定',font=('Arial',10),bg='pink',width=8,height=1,command=add_faver_2).pack(side='left')
            tkinter.Label(frame_m3, text="",fg='black',font=('Arial', 6), width=3, height=1).pack(side='left')
            tkinter.Button(frame_m3,text='取消',font=('Arial',10),bg='pink',width=8,height=1,
                           command=lambda:[frame_save_name.pack_forget(),frame_copy_str.pack()]).pack(side='left')
            frame_m3.pack()


            copy_faver_frame = tkinter.Frame(second_window)
            frame_m10 = tkinter.Frame(copy_faver_frame)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            search_result = tkinter.Listbox(frame_m10,font=('Arial',10),selectmode=tk_constants.SINGLE,height=9,width=28,
                                            yscrollcommand=sco1.set)
            search_result.grid()
            sco1.config(command=search_result.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            search_result.bind("<Double-Button-1>",lambda e : start_copy())
            frame_m10.pack()
            label10 = tkinter.Label(copy_faver_frame, text="双击项目自动复制",fg='black',font=('Arial', 10), width=26, height=2)
            label10.pack()
            frame_m3 = tkinter.Frame(copy_faver_frame)
            tkinter.Button(frame_m3,text='返回',font=('Arial',10),bg='aquamarine',width=4,height=1,
                           command=lambda:[copy_faver_frame.pack_forget(),frame_copy_str.pack()]).pack(side='left')
            tkinter.Label(frame_m3, text="",fg='black',font=('Arial', 6), width=1, height=1).pack(side='left')
            tkinter.Button(frame_m3,text='删除',font=('Arial',10),bg='aquamarine',width=4,height=1,command=delete_faver).pack(side='left')
            tkinter.Label(frame_m3, text="",fg='black',font=('Arial', 6), width=1, height=1).pack(side='left')
            tkinter.Button(frame_m3,text='退出',font=('Arial',10),bg='aquamarine',width=4,height=1,command=second_window.destroy).pack(side='left')
            frame_m3.pack()

        self.add_topic(add)

    def find_id(self) :

        def add(second_window : tkinter.Toplevel) :
            second_window.title('游戏内ID')

            def search(self,search) :
                search_result.delete(0,tk_constants.END)
                list1 = self.search_translate_id.search_str(search(),use_regx.get())
                if list1 == None : 
                    label1.config(text = "正则表达式格式错误") ; return None
                search_result.insert(tk_constants.END,*[i[0] for i in list1])
                label1.config(text = "搜索成功")

            def copy() :
                if len(search_result.curselection()) == 0 : 
                    label1.config(text = "没有选择需要复制的ID") ; return
                entry1 = tkinter.Entry()
                entry1.insert(tk_constants.END, self.search_translate_id.search[search_result.curselection()[0]][1])
                entry1.selection_range("0",tk_constants.END)
                entry1.event_generate("<<Copy>>")
                label1.config(text = "ID 复制完成")
            
            tkinter.Label(second_window, text="",fg='black',font=('Arial', 1), width=15, height=1).pack()
            frame_m10 = tkinter.Frame(second_window)
            search_collect = tkinter.Entry(frame_m10, show=None, width=18, font=('Arial', 11))
            search_collect.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
            search_collect.bind("<<update-status>>", lambda a : search(self,search_collect.get))
            search_collect.bind("<FocusIn>",lambda a : self.set_focus_input(a,search_collect))
            search_collect.pack(side='left')
            use_regx = tkinter.BooleanVar(second_window,False)
            tkinter.Checkbutton(frame_m10,text='正则',font=('Arial',10),variable=use_regx,onvalue=True,offvalue = False,height=1,
                                command=lambda : search(self,search_collect.get)).pack(side='left')
            frame_m10.pack()
            tkinter.Label(second_window, text="",fg='black',font=('Arial', 1), width=15, height=1).pack()

            frame_m10 = tkinter.Frame(second_window)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
            search_result = tkinter.Listbox(frame_m10,font=('Arial',10),selectmode=tk_constants.SINGLE,height=9,width=26,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
            search_result.grid()
            sco1.config(command=search_result.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            sco2.config(command=search_result.xview)
            sco2.grid(sticky=tkinter.E+tkinter.W)
            search_result.bind("<Double-Button-1>",lambda e : copy())
            frame_m10.pack()
            tkinter.Label(second_window, text="",fg='black',font=('Arial', 1), width=15, height=1).pack()
            label1 = tkinter.Label(second_window, text="双击项目以复制",fg='black',font=('Arial', 10), width=22, height=1)
            label1.pack()

            tkinter.Label(second_window, text="",fg='black',font=('Arial', 1), width=15, height=1).pack()

        self.add_topic(add)

    def copy_file_command(self) :
        
        def read_saves() -> dict :
            save_path = os.path.join("functionality","command","saves.pick")
            if not os.path.exists(save_path) or not os.path.isfile(save_path) : return {}
            else : 
                with open(save_path, 'rb') as f : a = pickle.load(f)
                return a
                
        def save_saves(data1 : dict , second_window : tkinter.Toplevel) :
            save_path = os.path.join("functionality","command","saves.pick")
            with open(save_path, 'wb') as f: pickle.dump(data1,f)
            second_window.destroy()

        def add(second_window : tkinter.Toplevel) :
            second_window.title('命令复制')
            read_file_data = read_saves()

            def open_file() :
                if len(search_result.curselection()) == 0 : 
                    label1.config(text = "你没有选择需要打开的文件") ; return None
                path1 = search_result.get(search_result.curselection())
                try : f = open(os.path.join("functionality","command") + path1,"r",encoding="utf-8")
                except : 
                    label1.config(text = "文件打开失败") ; return None
                else : 
                    content_1 = f.read() ; f.close()
                    if path1 not in read_file_data : read_file_data[path1] = {"lines" : 1}
                    copy_frame.file_content = [i for i in content_1.split("\n") if len(i.replace(" ",""))]
                    copy_frame.file_name = path1
                    open_frame.pack_forget() ; copy_frame.pack()
                    find_command(add_value = 0)
            

            open_frame = tkinter.Frame(second_window)

            tkinter.Label(open_frame, text="",fg='black',font=('Arial', 1), width=15, height=1).pack()
            frame_m10 = tkinter.Frame(open_frame)
            sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
            sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
            search_result = tkinter.Listbox(frame_m10,font=('Arial',10),selectmode=tk_constants.SINGLE,height=11,width=28,
                                            yscrollcommand=sco1.set,xscrollcommand=sco2.set)
            search_result.grid()
            sco1.config(command=search_result.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            sco2.config(command=search_result.xview)
            sco2.grid(sticky=tkinter.E+tkinter.W)
            search_result.bind("<Double-Button-1>",lambda e : open_file())
            frame_m10.pack()

            def chech_name(data) :
                if re.search(".txt$|.mcfunction$",data[1]) : 
                    try : open(data[2],"r",encoding="utf-8").close()
                    except : return False
                    else : return True
                else : return False
            for i in file_IO.search_file(os.path.join("functionality","command"),chech_name) : 
                if i[0] == "dir" : continue
                search_result.insert(tk_constants.END,i[3].replace(os.path.join("functionality","command"),"",1))

            label1 = tkinter.Label(open_frame, text="双击项目打开文件\n点击文本框复制，绿色为复制成功",fg='black',font=('Arial', 10), width=26, height=2)
            label1.pack()
            open_frame.pack()


            def find_command(set_value = None , add_value = None) :
                try :
                    if set_value != None and int(set_value) : pass
                    if add_value != None and int(add_value) : pass
                except : return None
                value1 = read_file_data[copy_frame.file_name]['lines']
                if set_value : value1 = int(set_value)
                elif add_value : value1 += int(add_value)
                if not (1 <= value1 <= len(copy_frame.file_content)) : return None
                command_display_1.config(state="normal")
                command_display_1.delete("0.0",tk_constants.END)
                command_display_1.insert(tk_constants.END,copy_frame.file_content[value1-1])
                command_display_1.config(state="disabled")
                read_file_data[copy_frame.file_name]['lines'] = value1
                counter1.config(text="第%s条 共%s条" % (value1,len(copy_frame.file_content)))

            def copy_text() :
                entry1 = tkinter.Entry()
                entry1.insert(tk_constants.END, copy_frame.file_content[read_file_data[copy_frame.file_name]['lines'] - 1])
                entry1.selection_range("0",tk_constants.END)
                entry1.event_generate("<<Copy>>")
                command_display_1.tag_add("green","0.0",tk_constants.END)
            
            copy_frame = tkinter.Frame(second_window)
            width_2 = 4 if platform.system() == 'Windows' else 2
            tkinter.Label(copy_frame, text="",fg='black',font=('Arial', 3), width=15, height=1).pack()
            frame_m10 = tkinter.Frame(copy_frame)
            sco1 = tkinter.Scrollbar(frame_m10, orient='vertical')
            command_display_1 = tkinter.Text(frame_m10, show=None, height=9, width=30, font=('Arial', 10), 
                                             yscrollcommand=sco1.set, state='disabled')
            command_display_1.grid()
            sco1.config(command=command_display_1.yview)
            sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
            command_display_1.tag_config("green",foreground='#05a705',underline=True)
            command_display_1.bind("<Button-1>",lambda e: copy_text())
            frame_m10.pack()

            tkinter.Label(copy_frame, text="",fg='black',font=('Arial', 6), width=15, height=1).pack()
            frame_m10 = tkinter.Frame(copy_frame)
            tkinter.Button(frame_m10,text='←',font=('Arial',10),bg='#9ae9d1',width=width_2,height=1,
                           command=lambda : find_command(add_value = -1)).grid(row=0,column=0)
            tkinter.Label(frame_m10, text="",fg='black',font=('Arial', 3), width=6, height=1).grid(row=0,column=1)
            tkinter.Button(frame_m10,text='返回',font=('Arial',10),bg='#00ffff',width=6,height=1,
                           command=lambda : [open_frame.pack() , copy_frame.pack_forget()]).grid(row=0,column=2)
            tkinter.Label(frame_m10, text="",fg='black',font=('Arial', 3), width=6, height=1).grid(row=0,column=3)
            tkinter.Button(frame_m10,text='→',font=('Arial',10),bg='#9ae9d1',width=width_2,height=1,
                           command=lambda : find_command(add_value = 1)).grid(row=0,column=4)
            frame_m10.pack()

            tkinter.Label(copy_frame, text="",fg='black',font=('Arial',3), width=15, height=1).pack()
            frame_m10 = tkinter.Frame(copy_frame)
            set_page = tkinter.Entry(frame_m10,width=12,justify='center')
            set_page.insert(tk_constants.END,"输入数值跳转")
            set_page.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
            set_page.bind("<<update-status>>", lambda a : find_command(set_value=set_page.get()))
            set_page.bind("<FocusIn>",lambda a : self.set_focus_input(a,set_page))
            set_page.pack(side=tk_constants.LEFT)

            counter1 = tkinter.Label(frame_m10, text="",fg='black',font=('Arial', 10), width=15, height=1)
            counter1.pack(side=tk_constants.LEFT)
            frame_m10.pack()
            second_window.protocol("WM_DELETE_WINDOW", lambda : save_saves(read_file_data,second_window))

        self.add_topic(add)




debug_windows = control_windows()
