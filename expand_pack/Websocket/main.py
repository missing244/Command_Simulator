import tkinter,os,sys,platform,random,webbrowser,socket
from typing import List
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))
base_path = os.path.dirname(os.path.abspath(__file__))
import main_source.package.tk_tool as tk_tool
import mc_websocket,tkinter.messagebox

INPUT = [False,False,False,False,False]
widget_dict = {"log":tkinter.Text, "event":tkinter.Listbox, "command":tkinter.Text}

def clear_log() :
    global widget_dict
    widget_dict["log"].config(state=tkinter.NORMAL)
    widget_dict["log"].delete("0.0",tkinter.END)
    widget_dict["log"].config(state=tkinter.DISABLED)


class myClient(mc_websocket.WebSocket_Client) :

    def receive_msg_hook(self, msg_data: List[bytes]):
        widget_dict["log"].config(state=tkinter.NORMAL)
        for i in msg_data :
            try : widget_dict["log"].insert(tkinter.END,str(self.client_ip_port) + "\n" + i.decode("utf-8") + "\n")
            except : pass
        widget_dict["log"].see(tkinter.END)
        widget_dict["log"].config(state=tkinter.DISABLED)


class pack_class :
    
    def __init__(self) -> None :
        self.ws_server:mc_websocket.WebSocket_Server = None
        self.method_list = [self.generate_server, self.exit_server, self.subscribe_event,
            self.unsubscribe_event, self.run_command]

    def reload_method(self) :
        if isinstance(self.ws_server,mc_websocket.WebSocket_Server) : self.ws_server.stop_server()

    def loop_method(self) :
        global INPUT
        for index,bool_1 in enumerate(INPUT) :
            if not bool_1 : continue
            self.method_list[index]()
            INPUT[index] = False

    def generate_server(self) -> None :
        if isinstance(self.ws_server,mc_websocket.WebSocket_Server) : self.ws_server.stop_server()
        ip,port = socket.gethostbyname(socket.gethostname()),random.randint(10000,60000)
        self.ws_server = WS_Server = mc_websocket.WebSocket_Server(ip,port,ClientClassHook=myClient)
        WS_Server.start_server()
        tk_tool.copy_to_clipboard("/connect %s:%s"%(ip,port))
        tkinter.messagebox.showinfo("Info","WS服务器已开启\nIP已复制进剪贴板中")
    
    def exit_server(self) :
        self.ws_server.stop_server()
        self.ws_server = None

    def subscribe_event(self) -> None :
        widget = widget_dict["event"]
        if len(widget.curselection()) < 1 : 
            tkinter.messagebox.showerror("Error","列表框内没有选择\n需要监听的事件") ; return None
        if len(self.ws_server.connenting_client) < 1 : 
            tkinter.messagebox.showerror("Error","没有客户端正在连接") ; return None
        event_name = mc_websocket.Constant.SUBSCRIBE_EVENT[widget.curselection()[0]]
        for i in list(self.ws_server.connenting_client) :
            if i.connect_alive : i.subscribe_event(event_name)

    def unsubscribe_event(self) -> None :
        widget = widget_dict["event"]
        if len(widget.curselection()) < 1 : 
            tkinter.messagebox.showerror("Error","列表框内没有选择\n需要取消监听的事件") ; return None
        if len(self.ws_server.connenting_client) < 1 : 
            tkinter.messagebox.showerror("Error","没有客户端正在连接") ; return None
        event_name = mc_websocket.Constant.SUBSCRIBE_EVENT[widget.curselection()[0]]
        for i in list(self.ws_server.connenting_client) :
            if i.connect_alive : i.unsubscribe_event(event_name)

    def run_command(self) :
        widget = widget_dict["command"]
        if len(self.ws_server.connenting_client) < 1 : 
            tkinter.messagebox.showerror("Error","没有客户端正在连接")
            return None
        command = [i for i in widget.get("1.0",tkinter.END).split("\n") if (i.replace(" ","") != "")]
        for i in list(self.ws_server.connenting_client) :
            if not i.connect_alive : continue
            for j in command : i.run_command(j)



def ws_enter() : INPUT[0] = True
def ws_exit() : INPUT[1] = True
def ws_subscribe() : INPUT[2] = True
def ws_unsubscribe() : INPUT[3] = True
def ws_command() : INPUT[4] = True

def ask_exit() :
    aaa = tkinter.messagebox.askquestion('Title', '是否关闭服务器并退出？')
    return aaa == "yes"



def UI_set(main_win, tkinter_Frame:tkinter.Frame) :
    global widget_dict
    main_tk:tkinter.Tk = main_win.window

    main_frame = tkinter.Frame(tkinter_Frame)
    tkinter.Label(main_frame,text="Websocket服务器",fg='black',font=tk_tool.get_default_font(20),width=15,height=1).pack()
    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()
    
    tkinter.Label(main_frame,text="Webscoket服务器终端界面",fg='black',font=tk_tool.get_default_font(10),
                  wraplength=main_tk.winfo_width()-70).pack()
    tkinter.Label(main_frame,text="让用户了解WS服务器在Minecraft基岩版中支持的功能",fg='black',font=tk_tool.get_default_font(10),
                  wraplength=main_tk.winfo_width()-70).pack()
    tkinter.Label(main_frame,text="安卓用户在运行本拓展包时需将本软件处于小窗模式运行！！！",fg='green',font=tk_tool.get_default_font(10),
                  wraplength=main_tk.winfo_width()-70).pack()

    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()

    frame_m0 = tkinter.Frame(main_frame)
    frame_m1 = tkinter.Frame(frame_m0)
    tkinter.Button(frame_m1,text="启动",bg='pink',command=lambda:[main_frame.pack_forget(),server_frame.pack(),
                   ws_enter(),send_event.pack()]).pack(side=tkinter.LEFT)
    tkinter.Label(frame_m1, text="启动WS服务器",fg='black',font=tk_tool.get_default_font(10)).pack(side=tkinter.LEFT)
    frame_m1.pack(anchor="w")
    frame_m1 = tkinter.Frame(frame_m0)
    tkinter.Button(frame_m1,text="详情",bg='pink',command=lambda:webbrowser.open("http://localhost:32323/tutorial/ExpandPack.html")).pack(side=tkinter.LEFT)
    tkinter.Label(frame_m1, text="跳转帮助文档",fg='black',font=tk_tool.get_default_font(10)).pack(side=tkinter.LEFT)
    frame_m1.pack(anchor="w")
    frame_m0.pack()
    main_frame.pack()


    width_1 = 4 if platform.system() == 'Windows' else 2
    server_frame = tkinter.Frame(tkinter_Frame)
    c1 = tkinter.Label(server_frame, fg='black',font=tk_tool.get_default_font(3), width=3, height=2) ; c1.pack()
    frame_m1 = tkinter.Frame(server_frame)
    tkinter.Button(frame_m1,text='事件',font=tk_tool.get_default_font(10),bg='#ff9900',width=width_1,height=1,
                   command=lambda:[send_event.pack(),send_command.pack_forget(),terminal.pack_forget()]).pack(side='left')
    tkinter.Label(frame_m1, fg='black',font=tk_tool.get_default_font(3), width=3, height=1).pack(side='left')
    tkinter.Button(frame_m1,text='命令',font=tk_tool.get_default_font(10),bg='#ff9900',width=width_1,height=1,
                   command=lambda:[send_event.pack_forget(),send_command.pack(),terminal.pack_forget()]).pack(side='left')
    tkinter.Label(frame_m1, fg='black',font=tk_tool.get_default_font(3), width=3, height=1).pack(side='left')
    tkinter.Button(frame_m1,text='终端',font=tk_tool.get_default_font(10),bg='#ff9900',width=width_1,height=1,
                   command=lambda:[send_event.pack_forget(),send_command.pack_forget(),terminal.pack()]).pack(side='left')
    tkinter.Label(frame_m1, fg='black',font=tk_tool.get_default_font(3), width=3, height=1).pack(side='left')
    tkinter.Button(frame_m1,text='退出',font=tk_tool.get_default_font(10),bg='#ff9900',width=width_1,height=1,
                   command=lambda:[ws_exit(),main_frame.pack(),server_frame.pack_forget()] if ask_exit() else None).pack(side='left')
    frame_m1.pack()
    


    send_event = tkinter.Frame(server_frame)
    list_box = tk_tool.tk_Scrollbar_ListBox(send_event,horizontal_scrollbar=False,height=21,width=26,font=tk_tool.get_default_font(10))
    [list_box.input_box.insert(tkinter.END,i) for i in mc_websocket.Constant.SUBSCRIBE_EVENT]
    list_box.pack()
    frame_m2 = tkinter.Frame(send_event)
    tkinter.Button(frame_m2,text='绑定事件',font=tk_tool.get_default_font(12),bg='pink',width=8,height=1,
                   command=lambda:ws_subscribe()).pack(side='left')
    tkinter.Canvas(frame_m2,width=10,height=5).pack(side='left')
    tkinter.Button(frame_m2,text='解绑事件',font=tk_tool.get_default_font(12),bg='pink',width=8,height=1,
                   command=lambda:ws_unsubscribe()).pack(side='left')
    frame_m2.pack()
    main_win.add_can_change_hight_component([list_box.input_box, c1,frame_m1,frame_m2])


    send_command = tkinter.Frame(server_frame)
    input_box1 = tk_tool.tk_Scrollbar_Text(send_command,horizontal_scrollbar=False,height=22,width=26,font=tk_tool.get_default_font(10))
    input_box1.input_box.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    input_box1.pack()
    tkinter.Button(send_command,text='发送命令',font=tk_tool.get_default_font(12),bg='pink',width=8,height=1,
                   command=lambda:ws_command()).pack()
    main_win.add_can_change_hight_component([input_box1.input_box, c1,frame_m1,frame_m2])


    terminal = tkinter.Frame(server_frame)
    input_box2 = tk_tool.tk_Scrollbar_Text(terminal,horizontal_scrollbar=False,height=22,width=26,font=tk_tool.get_default_font(10),state=tkinter.DISABLED)
    input_box2.pack()
    tkinter.Button(terminal,text='清空日志',font=tk_tool.get_default_font(12),bg='pink',width=8,height=1,
                   command=lambda:clear_log()).pack()
    main_win.add_can_change_hight_component([input_box2.input_box, c1,frame_m1,frame_m2])


    widget_dict['log'] = input_box2.input_box
    widget_dict["event"] = list_box.input_box
    widget_dict["command"] = input_box1.input_box

    return
    ip,port = socket.gethostbyname(socket.gethostname()),random.randint(10000,60000)
    WS_Server = mc_websocket.WebSocket_Server(ip,port)
    print("%s:%s"%(ip,port))
    tkinter.Button(tkinter_Frame,text="开启",command=WS_Server.start_server).pack()
    tkinter.Button(tkinter_Frame,text="关闭",command=WS_Server.stop_server).pack()
    
    tkinter.Button(tkinter_Frame,text="命令",command=lambda : WS_Server.connenting_client[0].run_command("say aaa")).pack()





