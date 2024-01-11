import tkinter,os,pickle,sys,random,time,json,webbrowser,tkinter.font,traceback
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))
base_path = os.path.dirname(os.path.abspath(__file__))
from tkinter.constants import *
import tkinter.messagebox,typing
from tkinter import ttk
import main_source.package.tk_tool as tk_tool

import const_obj
import const_func

os.makedirs(os.path.join(base_path,'import'),exist_ok=True)
os.makedirs(os.path.join(base_path,'export'),exist_ok=True)

main_win = None


class pack_class : 

    def __init__(self) -> None : 
        try : 
            with open(os.path.join(base_path,'rawtext_saves'), 'rb') as f: self.save_data = pickle.load(f)
        except : 
            with open(os.path.join(base_path,'rawtext_saves'), 'wb') as f: pickle.dump([], f)
            with open(os.path.join(base_path,'rawtext_saves'), 'rb') as f: self.save_data = pickle.load(f)
        self.save_timestemp = time.time() + 600
        self.last_save_hash_1 = -1
        self.last_save_hash_2 = -1
        self.template_choose = None


    def check_file(self,data_list) :
        for i in data_list :
            if isinstance(i,(str,dict)) : raise Exception
            if isinstance(i, dict) :
                if ('type' not in i) or ('annotation' not in i) or (type(i['annotation']) != type("")) : raise Exception
                if i['type'] not in ("score",'selector','translate') : raise Exception
                if i['type'] == "score" and not isinstance(i['scoreboard'], str) or not isinstance(i['name'],str) : raise Exception
                if i['type'] == "selector" and not isinstance(i['name'], str) : raise Exception
                if i['type'] == "translate" and not isinstance(i['text'], str) : raise Exception
                if isinstance(i['json_list'], list) : raise Exception
                self.check_file(i['json_list'])

    def import_file(self) : 
        f_l = list(os.walk(os.path.join(base_path,'import')))[0]
        success1, faile1 = 0, 0
        for i in f_l[2] :
            try : 
                f1 = open(os.path.join(f_l[0],i),"r",encoding="utf-8")
                json1 = json.loads(f1.read())
                if ('name' not in json1) or ('text_to_json' not in json1) or (
                    type(json1['name']) != type("") or type(json1['text_to_json']) != type([])
                ) : raise Exception
                self.check_file(json1)
                self.save_data.append(json1)
                self.save_file(False)
            except : faile1 += 1 ; f1.close() ; traceback.print_exc()
            else : success1 += 1 ; f1.close() ; os.remove(os.path.join(f_l[0],i))
        tk_component['open_list'].delete(0,END)
        for i in self.save_data : tk_component['open_list'].insert(END,i['name'])
        tkinter.messagebox.showinfo("Info","已导入import文件夹中的文件\n%s成功 %s失败"%(success1,faile1))

    def export_file(self) : 
        if not self.get_selecting_rawtext() : return None
        select = self.save_data[tk_component['open_list'].curselection()[0]]
        f1 = open(os.path.join(base_path,'export',select['name'] + "[%s]"%(time.strftime('%Y-%m-%d %H-%M-%S')) + ".json"),"w+",encoding="utf-8")
        f1.write(json.dumps(select))
        f1.close()
        tkinter.messagebox.showinfo("Info","已导出在export文件夹导出\n模板 %s"%select['name'])


    def save_file(self,dispaly=True) :
        with open(os.path.join(base_path,'rawtext_saves'), 'wb') as f: pickle.dump(self.save_data,f)
        if dispaly : tkinter.messagebox.showinfo("Info","已成功保存rawtext内容")


    def creat_new_rawtext(self) : 
        tk_component['open_list'].delete(0,END)
        self.save_data.append({'name': 'Json模板'+str(random.randint(0,100000)), "text_to_json": []}) 
        for i in self.save_data : tk_component['open_list'].insert(END,i['name'])
        self.save_file(False)

    def get_selecting_rawtext(self):
        select = tk_component['open_list'].curselection()
        if len(select) == 0 : return False
        else : return True

    def delete_rawtext(self) :
        if not self.get_selecting_rawtext() : return None
        a = tkinter.messagebox.askquestion("Info","二次确认\n是否删除该模板？")
        if a != "yes" : return None
        del self.save_data[tk_component['open_list'].curselection()[0]]
        tk_component['open_list'].delete(0,END)
        for i in self.save_data: tk_component['open_list'].insert(END,i['name'])
        self.save_file(False)
        tkinter.messagebox.showinfo("Info","已删除Json模板")

    def open_rawtext(self):
        self.last_save_hash_1 = -1 ; self.last_save_hash_2 = -1
        if not self.get_selecting_rawtext() : return None
        middle1 = tk_component['open_list'].curselection()[0]
        self.template_choose = middle2 = self.save_data[middle1]
        tk_component["Json_title"].delete("0",END)
        tk_component["Json_title"].insert(END,middle2["name"])
        tk_component["expand_input_1"].delete("0.0",END)
        self.main_win.focus_input = tk_component["expand_input_1"]
        const_func.content_to_component(tk_component["expand_input_1"], self.main_win, middle2["text_to_json"])
        self.open_win('edit_frame')

    def open_win(self,win_id = 'main_frame') : 
        for i in tk_component['frame'].keys() :
            if i == win_id : tk_component['frame'][i].pack()
            else : tk_component['frame'][i].pack_forget()


    def save_title(self):
        self.template_choose["name"] = tk_component['Json_title'].get()

    def save_content(self):
        self.template_choose["text_to_json"] = const_func.Text_get_content(tk_component['expand_input_1'])


    def loop_method(self) :
        if "tk_component" not in globals() : return
        middle1 = const_func.Text_get_content(tk_component['expand_input_1'])
        if self.last_save_hash_1 != hash(str(middle1)) and self.template_choose != None :
            self.last_save_hash_1 = hash(str(middle1))
            tk_component['expand_output_1'].config(state=NORMAL)
            tk_component['expand_output_1'].delete("0.0",END)
            tk_component['expand_output_1'].insert(END,json.dumps(self.update_json_result(middle1),
                ensure_ascii=False,separators=(',', ':')))
            tk_component['expand_output_1'].see(END)
            tk_component['expand_output_1'].config(state=DISABLED)
        #print(const_func.Text_get_content(tk_component['expand_input_1']))
        if time.time() > self.save_timestemp :
            if self.template_choose != None and self.last_save_hash_2 != self.last_save_hash_1 : 
                self.last_save_hash_2 = self.last_save_hash_1
                self.template_choose["text_to_json"] = const_func.Text_get_content(tk_component['expand_input_1'])
                self.save_file(False)
                #print(23123123123123)
            self.save_timestemp = time.time() + 600

    def update_json_result(self,data_list) :
        base_json = {"rawtext":[]}
        for rawtext_comp in data_list :
            if type(rawtext_comp) == type("") : base_json['rawtext'].append(const_func.change_to_text(rawtext_comp))
            if type(rawtext_comp) == type({}) and rawtext_comp['type'] == 'score' : 
                base_json['rawtext'].append(const_func.change_to_score(rawtext_comp))
            if type(rawtext_comp) == type({}) and rawtext_comp['type'] == 'selector' : 
                base_json['rawtext'].append(const_func.change_to_selector(rawtext_comp))
            if type(rawtext_comp) == type({}) and rawtext_comp['type'] == 'translate' : 
                base_json['rawtext'].append(const_func.change_to_translate(rawtext_comp))

        return base_json



def Text_add_button(raw_type:typing.Literal["selector","score","translate"]) :
    focus_comp:tkinter.Text = main_win.focus_input
    if not isinstance(focus_comp, tkinter.Text) : return None
    if not hasattr(focus_comp, "rawtext_sign") : return None
    
    inner_button = const_obj.Text_Inner_Button(focus_comp, main_win, raw_type)
    focus_comp.window_create(INSERT, window=inner_button)

def Menu_set(Menu1:tkinter.Menu) :
    Menu1.add_separator()
    Menu1.add_command(label="添加显示分数" , command=lambda : Text_add_button("score"))
    Menu1.add_command(label="添加显示名字" , command=lambda : Text_add_button("selector"))
    Menu1.add_command(label="添加翻译组件" , command=lambda : Text_add_button("translate"))
    Menu1.add_separator()
    Menu1.add_command(label="批量添加按钮" , command=lambda : const_obj.batch_add_button(main_win))



def UI_set(main_win1, tkinter_Frame:tkinter.Frame) :
    global main_win,tk_component
    main_win = main_win1
    pack_object:pack_class = main_win.get_expand_pack_class_object("b61a9a5c-0831-4d2a-b4bd-56513876be27")

    blank_height = tkinter.Label(tkinter_Frame, text="  ",fg='black',font=tk_tool.get_default_font(6)).winfo_reqheight()
    tkinter.Label(tkinter_Frame, text="  ",fg='black',font=tk_tool.get_default_font(6)).pack()

    main_frame = tkinter.Frame(tkinter_Frame)
    tkinter.Label(main_frame,text="Rawtext Json",fg='black',font=tk_tool.get_default_font(20),width=15,height=1).pack()
    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(1), width=2, height=1).pack()

    frame_m10 = tkinter.Frame(main_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    file_select = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(12),selectmode=SINGLE,height=15,width=24,yscrollcommand=sco1.set)
    file_select.grid()
    sco1.config(command=file_select.yview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    file_select.bind("<Double-ButtonRelease-1>", lambda e : pack_object.open_rawtext())
    frame_m10.pack()

    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(1), width=2, height=1).pack()

    frame_m6 = tkinter.Frame(main_frame)
    tkinter.Button(frame_m6,text='新建',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,command=pack_object.creat_new_rawtext).pack(side='left')
    tkinter.Label(frame_m6, text="",fg='black',font=tk_tool.get_default_font(3), width=2, height=1).pack(side='left')
    tkinter.Button(frame_m6,text='删除',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,command=pack_object.delete_rawtext).pack(side='left')
    tkinter.Label(frame_m6, text="",fg='black',font=tk_tool.get_default_font(3), width=2, height=1).pack(side='left')
    tkinter.Button(frame_m6,text='打开',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,command=pack_object.open_rawtext).pack(side='left')
    frame_m6.pack()

    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()

    frame_m6 = tkinter.Frame(main_frame)
    tkinter.Button(frame_m6,text='导入',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,command=pack_object.import_file).pack(side='left')
    tkinter.Label(frame_m6, text="",fg='black',font=tk_tool.get_default_font(3), width=2, height=1).pack(side='left')
    tkinter.Button(frame_m6,text='导出',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,command=pack_object.export_file).pack(side='left')
    tkinter.Label(frame_m6, text="",fg='black',font=tk_tool.get_default_font(3), width=2, height=1).pack(side='left')
    tkinter.Button(frame_m6,text='帮助',font=tk_tool.get_default_font(12),bg='#7fc8ff' ,width=5, height=1,command=lambda: webbrowser.open("http://localhost:32323/tutorial/ExpandPack.html")).pack(side='left')
    frame_m6.pack()
    main_frame.pack()
    
    
    font1 = tkinter.font.Font(family='Courier New', size=10)
    edit_frame = tkinter.Frame(tkinter_Frame)

    Json_title = tkinter.Entry(edit_frame,font=tk_tool.get_default_font(13),width=18,justify='center')
    Json_title.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
    Json_title.bind("<<update-status>>", lambda a : pack_object.save_title())
    Json_title.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    Json_title.pack()
    tkinter.Label(edit_frame, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()

    frame_m10 = tkinter.Frame(edit_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
    expand_input_1 = tkinter.Text(frame_m10,show=None,wrap=NONE,height=10,width=26,font=tk_tool.get_default_font(10),undo=True,yscrollcommand=sco1.set,xscrollcommand=sco2.set)
    expand_input_1.grid()
    expand_input_1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    expand_input_1.rawtext_sign = ''
    sco1.config(command=expand_input_1.yview)
    sco2.config(command=expand_input_1.xview)
    expand_input_1.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
    expand_input_1.bind("<<update-status>>", lambda a : pack_object.save_content())
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    sco2.grid(sticky=tkinter.W+tkinter.E)
    frame_m10.pack()

    frame_m10 = tkinter.Frame(edit_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    expand_output_1 = tkinter.Text(frame_m10,show=None,height=10,width=26,font=font1,yscrollcommand=sco1.set)
    expand_output_1.grid()
    expand_output_1.config(state="disabled")
    sco1.config(command=expand_output_1.yview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    frame_m10.pack()

    def save_and_quit() :
        pack_object.save_title()
        pack_object.save_content()
        pack_object.save_file()
        pack_object.open_win()
        pack_object.template_choose = None
        file_select.delete(0,END)
        for i in pack_object.save_data : file_select.insert(END,i['name'])
    def copy_text() :
        entry1 = tkinter.Entry()
        entry1.insert(END, expand_output_1.get("0.0",END)[:-1])
        entry1.selection_range("0",END)
        entry1.event_generate("<<Copy>>")

    tkinter.Label(edit_frame, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()
    frame_m6 = tkinter.Frame(edit_frame)
    tkinter.Button(frame_m6,text='退出',font=tk_tool.get_default_font(12),bg='#00ffff' ,width=5, height=1,command=save_and_quit).pack(side='left')
    tkinter.Label(frame_m6, text="",fg='black',font=tk_tool.get_default_font(3), width=2, height=1).pack(side='left')
    tkinter.Button(frame_m6,text='复制结果',font=tk_tool.get_default_font(12),bg='#00ffff' ,width=9, height=1,command=copy_text).pack(side='left')

    frame_m6.pack()


    test_frame = tkinter.Frame(tkinter_Frame)
    frame_m10 = tkinter.Frame(test_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    expand_test_1 = tkinter.Text(frame_m10,show=None,height=13,width=26,font=font1,wrap=NONE,yscrollcommand=sco1.set,state="disabled")
    expand_test_1.grid()
    sco1.config(command=expand_test_1.yview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    frame_m10.pack()
    
    tk_component = {"frame":{"main_frame": main_frame,"edit_frame": edit_frame,"test_frame": test_frame}, 
    "open_list": file_select, "Json_title": Json_title, "expand_input_1": expand_input_1, "expand_output_1": expand_output_1,
    "expand_test_1": expand_test_1}
    for i in pack_object.save_data : file_select.insert(END,i['name'])
    const_obj.window_stack.append(tkinter_Frame)
    const_obj.window_stack.append(edit_frame)
    edit_frame.input_to_focus = expand_input_1