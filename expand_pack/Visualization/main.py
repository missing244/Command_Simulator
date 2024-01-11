import tkinter,os,sys,webbrowser,traceback,json,tkinter.messagebox,platform,threading,time
from typing import Literal,Union
import main_source.package.tk_tool as tk_tool
from tkinter.constants import *
from main_source.bedrock_edition import RunTime
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))
base_path = os.path.dirname(os.path.abspath(__file__))


test_thread:threading.Thread = threading.Thread(target=lambda:1)
test_thread.start()


class pack_class : 

    def __init__(self) -> None:
        self.main_win = None
        self.game_process:RunTime.minecraft_thread = None
        self.is_start = False

    def do_POST(self,post_data:dict) :
        #print(post_data)
        if not self.is_start : return {"visualization_state": 19 , "msg": "未启动拓展包"}
        if "request_type" not in post_data : return {"visualization_state": 1 , "msg": "上送数据缺少必要参数"}

        elif post_data["request_type"] == "get_debug_data" :
            if self.game_process == None : return {"visualization_state": 7 , "msg": "世界未启动，请先启动一个世界"}
            if self.game_process.visualization_object == None : return {"visualization_state": 9 , "msg": "此世界无法进行可视化调试，请另外选择"}
            if self.game_process.game_load_over == False : return {"visualization_state": 8 , "msg": "世界未加载完成，请稍后重试"}
            if "times" not in post_data : return {"visualization_state": 1 , "msg": "上送数据缺少必要参数"}
            
            a = self.game_process.visualization_object.get_test_data(post_data["times"])
            if a == None : return {"visualization_state": 0, "msg": "数据获取完成"}
            else : return {"visualization_state": -2, "state": "get data", "content": a}


    def check_visualization_var(self,var_json:dict) :
        if self.game_process == None : return {"visualization_state": 7 , "msg": "世界未启动，请先启动一个世界"}
        if self.game_process.visualization_object == None : return {"visualization_state": 9 , "msg": "此世界无法进行可视化调试，请另外选择"}
        a = self.game_process.visualization_object.reset_var(var_json)
        if len(list(a)) : return {"visualization_state": 5 , "msg": "变量格式错误", "error_var": a}
        else : return {"visualization_state": 0 , "msg": "设置可视化参数成功"}

    def set_texmu_input(self,text:str) :
        self.main_win.display_frame["game_run"].input_box1.delete("0.0",END)
        self.main_win.display_frame["game_run"].input_box1.insert(END, text)

    def start_debug(self) :
        if self.game_process == None : return {"visualization_state": 7 , "msg": "世界未启动，请先启动一个世界"}
        if self.game_process.visualization_object == None : return {"visualization_state": 9 , "msg": "此世界无法进行可视化调试，请另外选择"}
        if self.game_process.game_load_over == False : return {"visualization_state": 8 , "msg": "世界未加载完成，请稍后重试"}
        self.game_process.runtime_variable.terminal_command = self.main_win.display_frame["game_run"].input_box1.get("1.0", tkinter.END)
        self.game_process.runtime_variable.terminal_send_command = True
        self.main_win.display_frame["game_terminal"].clear_terminal()
        return {"visualization_state": 0 , "msg": "启动命令调试成功"}

    def get_texmu_feedback(self) :
        if self.game_process == None : return {"visualization_state": 7 , "msg": "世界未启动，请先启动一个世界"}
        if self.game_process.visualization_object == None : return {"visualization_state": 9 , "msg": "此世界无法进行可视化调试，请另外选择"}
        if self.game_process.game_load_over == False : return {"visualization_state": 8 , "msg": "世界未加载完成，请稍后重试"}

        if not self.game_process.visualization_object.first_get_ready : return {"visualization_state": -1 , "state": "wait"}
        else : return {"visualization_state": 0 , "msg": "成功获取终端命令反馈", 
            "content": self.main_win.display_frame["game_terminal"].input_box2.get("1.0", tkinter.END)[:-1]}

    def get_is_testing(self) :
        return self.game_process.runtime_variable.how_times_run_all_command > 0

    def force_stop_test(self) :
        self.game_process.runtime_variable.how_times_run_all_command = -10
        if test_thread.is_alive() : tkinter.messagebox.showinfo("Info", "测试已被终止")
        else : tkinter.messagebox.showerror("Error", "无正在运行的测试")



def set_feedback_text(feedback_tk:tkinter.Text,mode:Literal["Enter_0","Enter_1","Enter_2"],text:str) :
    feedback_tk.config(state=NORMAL)
    feedback_tk.insert(END,text)
    if mode == "Enter_0" : pass
    elif mode == "Enter_1" : feedback_tk.insert(END,"\n")
    elif mode == "Enter_2" : feedback_tk.insert(END,"\n\n")
    feedback_tk.see(END)
    feedback_tk.config(state=DISABLED)

def get_temux_content(get_text_input:tkinter.Text, set_text_input:tkinter.Text) :
    set_text_input.delete("0.0",END)
    text = get_text_input.get("0.0",END)[:-1]
    set_text_input.insert(END,text)

def test_can_open(pack_object:pack_class) :
    try : 
        import brotli
        user_manager = pack_object.main_win.user_manager
        pack_uuid = "c0414919-e6ed-4b41-b2ac-130119684144"
        if pack_uuid not in user_manager.save_data["install_pack_list"] : raise Exception
    except : tkinter.messagebox.showerror("Error","未安装“原版拓展”\n请在拓展界面安装") ; return
    pack_object.is_start = True
    return True

def start_test(feedback_frame_func, pack_object:pack_class, input_tk:tkinter.Text, feedback_tk:tkinter.Text, var_json:dict) :
    global test_thread

    def thread_run() :
        feedback_tk.config(state=NORMAL) ; feedback_tk.delete("0.0",END) ; feedback_tk.config(state=DISABLED)
        set_feedback_text(feedback_tk, "Enter_1", "设置可视化参数....")
        a = pack_object.check_visualization_var({i:var_json[i].get() for i in var_json})
        set_feedback_text(feedback_tk, "Enter_1", a["msg"])
        if a["visualization_state"] == 5 :
            for i in a["error_var"] : set_feedback_text(feedback_tk, "Enter_1", "%s -> %s" % (i,a["error_var"][i]))
        if a["visualization_state"] > 0 : return
        set_feedback_text(feedback_tk, "Enter_1", "")

        time.sleep(0.3)
        set_feedback_text(feedback_tk, "Enter_1", "同步终端命令中....")
        pack_object.set_texmu_input(input_tk.get("0.0",END)[:-1])
        set_feedback_text(feedback_tk, "Enter_2", "同步初始化命令完成")

        time.sleep(0.3)
        set_feedback_text(feedback_tk, "Enter_1", "启用命令调试中....")
        a = pack_object.start_debug()
        if a["visualization_state"] > 0 :
            set_feedback_text(feedback_tk, "Enter_1", a["msg"]) ; return
        set_feedback_text(feedback_tk, "Enter_2", "同步初始化命令完成")

        time.sleep(0.3)
        set_feedback_text(feedback_tk, "Enter_1", "获取初始化命令反馈....")
        while 1 :
            a = pack_object.get_texmu_feedback()
            if a["visualization_state"] != -1 : break
            time.sleep(0.3)
        if a["visualization_state"] > 0 :
            set_feedback_text(feedback_tk, "Enter_1", a["msg"]) ; return
        set_feedback_text(feedback_tk, "Enter_1", "############################")
        set_feedback_text(feedback_tk, "Enter_1", a["content"])
        set_feedback_text(feedback_tk, "Enter_2", "############################")

        time.sleep(0.3)
        set_feedback_text(feedback_tk, "Enter_1", "等待测试完成....")
        while pack_object.get_is_testing() : 
            set_feedback_text(feedback_tk, "Enter_1", "测试剩余 %s 游戏刻" % pack_object.game_process.runtime_variable.how_times_run_all_command) ; time.sleep(0.3)
        set_feedback_text(feedback_tk, "Enter_1", "测试已完成，可跳转网页查看效果")

    if not test_thread.is_alive() : 
        test_thread = threading.Thread(target=thread_run)
        test_thread.start()
        feedback_frame_func()
    else : tkinter.messagebox.showerror("Error", "测试正在运行")

    b = open(os.path.join(base_path,"var_save"),"wb")
    b.write(json.dumps({i:var_json[i].get() for i in var_json}).encode("utf-8"))
    b.close()

def jump_to_see() :
    if test_thread.is_alive() :
        tkinter.messagebox.showinfo("Error","请在测试完成后，跳转网页") ; return
    webbrowser.open("http://localhost:32323/?pack=f3732c87-e742-4213-b98f-4741a238fea0")




def UI_set(main_win, tkinter_Frame:tkinter.Frame) :
    main_tk:tkinter.Tk = main_win.window
    pack_object:pack_class = main_win.get_expand_pack_class_object("f3732c87-e742-4213-b98f-4741a238fea0")
    pack_ui:tkinter.Frame = tkinter_Frame
    blank_height = tkinter.Label(main_tk, text="  ",fg='black',font=tk_tool.get_default_font(6)).winfo_reqheight()
    tkinter.Label(pack_ui, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack()

    main_frame = tkinter.Frame(pack_ui)
    tkinter.Label(main_frame,text="命令可视化",fg='black',font=tk_tool.get_default_font(20),width=15,height=1).pack()
    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()

    tkinter.Label(main_frame,text="命令可视化需要“原版拓展”支持",fg='red',font=tk_tool.get_default_font(10),
                  wraplength=main_tk.winfo_width()-70).pack()
    tkinter.Label(main_frame,text="可以查看实体和部分方块的渲染",fg='black',font=tk_tool.get_default_font(10),
                  wraplength=main_tk.winfo_width()-70).pack()
    tkinter.Label(main_frame,text="首次使用请务必查看帮助！！！",fg='green',font=tk_tool.get_default_font(10),
                  wraplength=main_tk.winfo_width()-70).pack()

    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
    frame_m0 = tkinter.Frame(main_frame)
    frame_m1 = tkinter.Frame(frame_m0)
    tkinter.Button(frame_m1,text="启动",bg='pink',command=lambda:[main_frame.pack_forget(),mode_buttons.pack(),
        var_frame.pack()] if test_can_open(pack_object) else None).pack(side=LEFT)
    tkinter.Label(frame_m1, text="启动可视化界面",fg='black',font=tk_tool.get_default_font(10)).pack(side=LEFT)
    frame_m1.pack(anchor="w")     
    frame_m1 = tkinter.Frame(frame_m0)
    tkinter.Button(frame_m1,text="详情",bg='pink',command=lambda: webbrowser.open("http://localhost:32323/tutorial/ExpandPack.html")).pack(side=LEFT)
    tkinter.Label(frame_m1, text="跳转帮助文档",fg='black',font=tk_tool.get_default_font(10)).pack(side=LEFT)
    frame_m1.pack(anchor="w")
    frame_m0.pack()
    main_frame.pack()


    mode_buttons = tkinter.Frame(pack_ui)
    width_1 = 4 if platform.system() == 'Windows' else 3
    abc1 = tkinter.Button(mode_buttons,text='参数',font=('Arial',13),bg='#ff9900',width=width_1,state=DISABLED,
                   command=lambda:[var_frame.pack(), terminal_frame.pack_forget(), feedback_frame.pack_forget(),
                                   abc1.config(state=DISABLED), abc2.config(state=NORMAL), abc3.config(state=NORMAL)])
    abc1.pack(side='left')
    tkinter.Label(mode_buttons,text="   ", fg='black',font=tk_tool.get_default_font(10)).pack(side='left')
    abc2 = tkinter.Button(mode_buttons,text='终端',font=('Arial',13),bg='#ff9900',width=width_1,
                   command=lambda:[var_frame.pack_forget(), terminal_frame.pack(), feedback_frame.pack_forget(),
                                   abc1.config(state=NORMAL), abc2.config(state=DISABLED), abc3.config(state=NORMAL)])
    abc2.pack(side='left')
    tkinter.Label(mode_buttons,text="   ", fg='black',font=tk_tool.get_default_font(10)).pack(side='left')
    abc3 = tkinter.Button(mode_buttons,text='反馈',font=('Arial',13),bg='#ff9900',width=width_1,
                   command=lambda:[var_frame.pack_forget(), terminal_frame.pack_forget(), feedback_frame.pack(),
                                   abc1.config(state=NORMAL), abc2.config(state=NORMAL), abc3.config(state=DISABLED)])
    abc3.pack(side='left')
    jump_to_feedback = lambda : [var_frame.pack_forget(), terminal_frame.pack_forget(), feedback_frame.pack(), abc1.config(state=NORMAL), abc2.config(state=NORMAL), abc3.config(state=DISABLED)]


    var_frame = tkinter.Frame(pack_ui)
    tkinter.Label(var_frame, text="           ",fg='black',font=tk_tool.get_default_font(3)).pack(anchor="w")
    tkinter.Label(var_frame, text="区域起始位置",fg='black',font=('Arial', 12, "bold")).pack(anchor="w")
    frame_m1 = tkinter.Frame(var_frame)

    tkinter.Label(frame_m1, text="x",fg='black',font=tk_tool.get_default_font(11)).grid(row=1,column=0)
    start_x = tkinter.Entry(frame_m1, width=11, font=tk_tool.get_default_font(11)) ; start_x.grid(row=1,column=1)
    start_x.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))

    tkinter.Label(frame_m1, text="z",fg='black',font=tk_tool.get_default_font(11)).grid(row=1,column=2)
    start_z = tkinter.Entry(frame_m1, width=11, font=tk_tool.get_default_font(11)) ; start_z.grid(row=1,column=3)
    start_z.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    frame_m1.pack(anchor="w")
    

    tkinter.Label(var_frame, text="           ",fg='black',font=tk_tool.get_default_font(3)).pack(anchor="w")
    tkinter.Label(var_frame, text="区域记录大小",fg='black',font=('Arial', 12, "bold")).pack(anchor="w")
    frame_m1 = tkinter.Frame(var_frame)

    tkinter.Label(frame_m1, text="dx",fg='black',font=tk_tool.get_default_font(11)).grid(row=1,column=0)
    area_x = tkinter.Entry(frame_m1, width=10, font=tk_tool.get_default_font(11)) ; area_x.grid(row=1,column=1)
    area_x.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))

    tkinter.Label(frame_m1, text="dy",fg='black',font=tk_tool.get_default_font(11)).grid(row=1,column=2)
    area_y = tkinter.Entry(frame_m1, width=10, font=tk_tool.get_default_font(11)) ; area_y.grid(row=1,column=3)
    area_y.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    frame_m1.pack(anchor="w")

    tkinter.Label(frame_m1, text="dz",fg='black',font=tk_tool.get_default_font(11)).grid(row=2,column=0)
    area_z = tkinter.Entry(frame_m1, width=10, font=tk_tool.get_default_font(11)) ; area_z.grid(row=2,column=1)
    area_z.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    frame_m1.pack(anchor="w")


    tkinter.Label(var_frame, text="           ",fg='black',font=tk_tool.get_default_font(3)).pack(anchor="w")
    tkinter.Label(var_frame, text="实体跟踪",fg='black',font=('Arial', 12, "bold")).pack(anchor="w")
    frame_m1 = tkinter.Frame(var_frame)
    entity_target_0 = tkinter.Entry(frame_m1, width=23, font=tk_tool.get_default_font(11)) ; entity_target_0.grid(row=1,column=0)
    entity_target_0.bind("<FocusIn>", lambda a : main_win.set_focus_input(a))
    tkinter.Canvas(frame_m1,width=entity_target_0.winfo_reqheight(),height=entity_target_0.winfo_reqheight(),bg="pink").grid(row=1,column=1)

    entity_target_1 = tkinter.Entry(frame_m1, width=23, font=tk_tool.get_default_font(11)) ; entity_target_1.grid(row=2,column=0)
    entity_target_1.bind("<FocusIn>", lambda a : main_win.set_focus_input(a))
    tkinter.Canvas(frame_m1,width=entity_target_0.winfo_reqheight(),height=entity_target_0.winfo_reqheight(),bg="purple").grid(row=2,column=1)

    entity_target_2 = tkinter.Entry(frame_m1, width=23, font=tk_tool.get_default_font(11)) ; entity_target_2.grid(row=3,column=0)
    entity_target_2.bind("<FocusIn>", lambda a : main_win.set_focus_input(a))
    tkinter.Canvas(frame_m1,width=entity_target_0.winfo_reqheight(),height=entity_target_0.winfo_reqheight(),bg="yellow").grid(row=3,column=1)

    entity_target_3 = tkinter.Entry(frame_m1, width=23, font=tk_tool.get_default_font(11)) ; entity_target_3.grid(row=4,column=0)
    entity_target_3.bind("<FocusIn>", lambda a : main_win.set_focus_input(a))
    tkinter.Canvas(frame_m1,width=entity_target_0.winfo_reqheight(),height=entity_target_0.winfo_reqheight(),bg="brown").grid(row=4,column=1)

    entity_target_4 = tkinter.Entry(frame_m1, width=23, font=tk_tool.get_default_font(11)) ; entity_target_4.grid(row=5,column=0)
    entity_target_4.bind("<FocusIn>", lambda a : main_win.set_focus_input(a))
    tkinter.Canvas(frame_m1,width=entity_target_0.winfo_reqheight(),height=entity_target_0.winfo_reqheight(),bg="lightblue").grid(row=5,column=1)
    frame_m1.pack(anchor="w")


    terminal_frame = tkinter.Frame(pack_ui)
    
    tkinter.Label(terminal_frame, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack()
    frame_m10 = tkinter.Frame(terminal_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    terminal_input_1 = tkinter.Text(frame_m10,show=None,height=19,width=28,font=tk_tool.get_default_font(10),yscrollcommand=sco1.set,undo=True)
    terminal_input_1.grid()
    terminal_input_1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    sco1.config(command=terminal_input_1.yview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    frame_m10.pack()
    
    tkinter.Label(terminal_frame, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack()
    frame_m20 = tkinter.Frame(terminal_frame)
    tkinter.Button(frame_m20,text="同步内容", bg='pink',fg='black',font=tk_tool.get_default_font(11), width=8, height=1, 
                   command=lambda : get_temux_content(main_win.display_frame["game_run"].input_box1, terminal_input_1)).pack(side='left')
    tkinter.Label(frame_m20, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack(side='left')
    tkinter.Button(frame_m20,text="开始记录", bg='pink',fg='black',font=tk_tool.get_default_font(11), width=8, height=1,
        command=lambda : start_test(jump_to_feedback, pack_object, terminal_input_1, terminal_output_1, {
        "start_x":start_x, "start_z":start_z, "area_x":area_x, "area_y":area_y, "area_z":area_z,
        "entity_target_0":entity_target_0, "entity_target_1":entity_target_1, "entity_target_2":entity_target_2,
        "entity_target_3":entity_target_3, "entity_target_4":entity_target_4
        })).pack(side='left')
    frame_m20.pack()
    main_win.add_can_change_hight_component([terminal_input_1,frame_m20,mode_buttons,blank_height,blank_height])


    feedback_frame = tkinter.Frame(pack_ui)
    tkinter.Label(feedback_frame, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack()
    frame_m10 = tkinter.Frame(feedback_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
    terminal_output_1 = tkinter.Text(frame_m10,show=None,height=18,width=28,font=tk_tool.get_default_font(10),yscrollcommand=sco1.set,
                                     xscrollcommand=sco2.set,state=DISABLED, wrap=NONE)
    terminal_output_1.grid()
    sco1.config(command=terminal_output_1.yview)
    sco2.config(command=terminal_output_1.xview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    sco2.grid(row=1,column=0,sticky=tkinter.E+tkinter.W)
    frame_m10.pack()
    
    tkinter.Label(feedback_frame, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack()
    frame_m21 = tkinter.Frame(feedback_frame)
    tkinter.Button(frame_m21,text="终止测试", bg='#0dd044',fg='black',font=tk_tool.get_default_font(11), width=8, height=1, 
                   command=pack_object.force_stop_test).pack(side='left')
    tkinter.Label(frame_m21, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack(side='left')
    tkinter.Button(frame_m21,text="可视化", bg='#0dd044',fg='black',font=tk_tool.get_default_font(11), width=8, height=1, 
                   command=jump_to_see).pack(side='left')
    frame_m21.pack()
    main_win.add_can_change_hight_component([terminal_output_1,mode_buttons,sco2,frame_m21,blank_height,blank_height])


    get_temux_content(main_win.display_frame["game_run"].input_box1, terminal_input_1)
    try : b = open(os.path.join(base_path,"var_save"),"r",encoding="utf-8")
    except : pass
    else :
        try : c = json.loads(b.read())
        except : pass
        else :
            if "start_x" in c : start_x.insert(END,c["start_x"])
            if "start_z" in c : start_z.insert(END,c["start_z"])
            if "area_x" in c : area_x.insert(END,c["area_x"])
            if "area_y" in c : area_y.insert(END,c["area_y"])
            if "area_z" in c : area_z.insert(END,c["area_z"])
            if "entity_target_0" in c : entity_target_0.insert(END,c["entity_target_0"])
            if "entity_target_1" in c : entity_target_1.insert(END,c["entity_target_1"])
            if "entity_target_2" in c : entity_target_2.insert(END,c["entity_target_2"])
            if "entity_target_3" in c : entity_target_3.insert(END,c["entity_target_3"])
            if "entity_target_4" in c : entity_target_4.insert(END,c["entity_target_4"])
        finally : b.close()







