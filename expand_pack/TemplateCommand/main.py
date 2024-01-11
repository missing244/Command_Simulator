import tkinter,os,pickle,sys,re,platform,random,math,threading,time,string,json,webbrowser,traceback
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))
base_path = os.path.dirname(os.path.abspath(__file__))
from tkinter import ttk
import main_source.package.tk_tool as tk_tool
import tkinter.messagebox

tk_component = {"frame":{"main_frame":tkinter.Frame, "edit_frame":tkinter.Frame, "result_frame":tkinter.Frame},
    "open_list":tkinter.Listbox, "input1":tkinter.Text, "input2":tkinter.Text,
    "temple_title":tkinter.Entry, "generate_times":tkinter.Entry, "temp_choose":ttk.Combobox, 
    "output1":tkinter.Text}

os.makedirs(os.path.join(base_path,'import'),exist_ok=True)
os.makedirs(os.path.join(base_path,'export'),exist_ok=True)
if (not os.path.exists(os.path.join(base_path,'template_saves')) or not os.path.isfile(os.path.join(base_path,'template_saves'))) : 
    with open(os.path.join(base_path,'template_saves'), 'wb') as f: pickle.dump([], f)



def replace_zero(str1 : str) :
    return re.sub(r"(\.\d*?[1-9])0+$|(\.)0+$", r"\1", str1)




class pack_class : 

    def __init__(self) -> None : 
        try : 
            with open(os.path.join(base_path,'template_saves'), 'rb') as f: self.save_data = pickle.load(f)
        except : 
            with open(os.path.join(base_path,'template_saves'), 'wb') as f: pickle.dump([], f)
            with open(os.path.join(base_path,'template_saves'), 'rb') as f: self.save_data = pickle.load(f)
        self.template_index = 0
        self.save_timestemp = time.time() + 600

        self.support_const = {'var0':None, 'var1':None, 'var2':None, 'var3':None, 'pi':math.pi, "tau":math.tau, 'e':math.e, 'degrees':math.pi/180}
        self.support_compute = {'sin':math.sin, 'cos':math.cos, "tan":math.tan, 'random':random.random, 'randfloat':random.uniform,
                                'randint':random.randint, 'pow':math.pow, 'log':lambda a,N: 1/math.log(N,a), 'arcsin':math.asin,
                                'arccos':math.acos, 'arctan':math.atan, 'floor':math.floor, 'ceil':math.ceil, "factorial":math.factorial,
                                "comb":lambda k,n: 1/math.comb(n,k), 'abs':abs, "sqrt":math.sqrt, }

    def loop_method(self) :
        if time.time() > self.save_timestemp :
            self.save_file(False)
            self.save_timestemp = time.time() + 600


    def import_file(self) : 
        f_l = list(os.walk(os.path.join(base_path,'import')))[0]
        success1,faile1 = 0,0
        for i in f_l[2] :
            try : 
                f1 = open(os.path.join(f_l[0],i),"r",encoding="utf-8")
                json1 = json.loads(f1.read())
                if not isinstance(json1, dict) : raise Exception
                if ("name" not in json1) or not isinstance(json1['name'],str) : raise Exception
                if ("template_command" not in json1) or isinstance(json1['template_command'],str) : raise Exception
                if ("generate_times" not in json1) or isinstance(json1['generate_times'],str) : raise Exception
                if ("Template" not in json1) or isinstance(json1['Template'],list) : raise Exception
                for j in json1['Template'] :
                    if not isinstance(j, dict) : raise Exception
                    if ("temp_name" not in j) or not isinstance(j['temp_name'], str) : raise Exception
                    if ("temp_type" not in j) or not isinstance(j['temp_type'], int) : raise Exception
                    if ("temp_detial" not in j) or not isinstance(j['temp_detial'], str) : raise Exception
                self.save_data.append(json1)
                self.save_file(False)
            except : faile1 += 1 ; f1.close()
            else : success1 += 1 ; f1.close() ; os.remove(os.path.join(f_l[0],i))
        tk_component['open_list'].delete(0,tkinter.END)
        for i in self.save_data : tk_component['open_list'].insert(tkinter.END,i['name'])
        tkinter.messagebox.showinfo("Info","已导入import文件夹的文件\n%s成功 %s失败"%(success1,faile1))

    def export_file(self) : 
        if not self.get_selecting_template() : return None
        select = self.save_data[tk_component['open_list'].curselection()[0]]
        f1 = open(os.path.join(base_path,'export',select['name']+"[%s]"%(time.strftime('%Y-%m-%d %H-%M-%S')) + ".json"),"w+",encoding="utf-8")
        f1.write(json.dumps(select))
        f1.close()
        tkinter.messagebox.showinfo("Info","已在export文件夹导出\n模板 %s"%select['name'])



    def save_file(self, dispaly=True) :
        with open(os.path.join(base_path,'template_saves'), 'wb') as f: pickle.dump(self.save_data,f)
        if dispaly : tkinter.messagebox.showinfo("Info","已成功保存模板")

    def open_win(self, win_id='main_frame') : 
        for i in tk_component['frame'].keys() :
            if i == win_id : tk_component['frame'][i].pack()
            else : tk_component['frame'][i].pack_forget()

    def creat_new_template(self) : 
        tk_component['open_list'].delete(0,tkinter.END)
        self.save_data.append({'name': '模板'+str(random.randint(0,100000)), "template_command": "", "generate_times": "0", "Template": []}) 
        #{"temp_name": "", "temp_type": 0, "temp_detial": ""}
        for i in self.save_data : tk_component['open_list'].insert(tkinter.END,i['name'])
        self.save_file(False)

    def get_selecting_template(self):
        select = tk_component['open_list'].curselection()
        if len(select) == 0 : return False
        else : return True

    def delete_template(self) :
        if not self.get_selecting_template() : return None
        a = tkinter.messagebox.askquestion("Q","二次确认\n是否删除该模板？")
        if a != "yes" : return None
        del self.save_data[tk_component['open_list'].curselection()[0]]
        tk_component['open_list'].delete(0,tkinter.END)
        for i in self.save_data: tk_component['open_list'].insert(tkinter.END,i['name'])
        self.save_file(False)
        tkinter.messagebox.showinfo("Info","已经删除模板")

    def open_template(self):
        self.template_index = 0 ; self.template_details_choose = None
        if not self.get_selecting_template() : return None
        middle1 = tk_component['open_list'].curselection()[0]
        self.template_choose = middle2 = self.save_data[middle1]
        self.all_set_template_details = { i['temp_name']:i for i in self.template_choose["Template"] } ###
        tk_component["input1"].delete("0.0",tkinter.END)
        tk_component["input2"].delete("0.0",tkinter.END)
        tk_component["temple_title"].delete("0",tkinter.END)
        tk_component["generate_times"].delete("0",tkinter.END)
        tk_component["input1"].insert(tkinter.END,middle2['template_command'])
        tk_component["temple_title"].insert(tkinter.END,middle2['name'])
        tk_component["generate_times"].insert(tkinter.END,middle2['generate_times'])
        tk_component["temp_choose"].current(0)
        self.update_hight_light()
        self.open_win('edit_frame')


    def save_title(self):
        self.template_choose["name"] = tk_component['temple_title'].get()

    def save_command(self):
        self.template_choose["template_command"] = tk_component['input1'].get("0.0","end")[:-1]
        self.update_hight_light()

    def save_gentime(self):
        self.template_choose["generate_times"] = tk_component['generate_times'].get()

    def save_temp(self):
        try : self.template_details_choose["temp_detial"] = tk_component['input2'].get("0.0","end")[:-1]
        except : pass

    def save_gentype(self):
        gentype = tk_component['temp_choose'].current()
        try : self.template_details_choose["temp_type"] = gentype
        except : pass


    def choose_template_details(self, value) :
        if value == 0 and ((self.template_index) > len(self.template_choose['Template']) or (self.template_index < 1)): return None
        if value != 0 and (self.template_index + value) > len(self.template_choose['Template']) : return None
        if value != 0 and (self.template_index + value) < 1 : return None
        tk_component['input1'].tag_remove('select', "0.0",tkinter.END)
        self.template_index += value
        self.template_details_choose = self.template_choose['Template'][self.template_index-1]
        tk_component['temp_choose'].current(self.template_details_choose['temp_type'])
        tk_component["input2"].delete("0.0",tkinter.END)
        tk_component["input2"].insert(tkinter.END,self.template_details_choose['temp_detial'])

        test1 = self.template_details_choose['temp_name']
        command_list = tk_component['input1'].get("0.0","end")[:-1].split("\n")
        match_list = [list(re.finditer("\\$temp[0-9]+",text1)) for text1 in command_list]
        for i in range(len(match_list)) :
            for j in match_list[i] :
                if not j.group() == test1 : continue
                tk_component['input1'].tag_add('select', "%s.%s"%(i+1,j.start()), "%s.%s"%(i+1,j.end()))
                tk_component['input1'].see("%s.%s"%(i+1,j.end()))

    def update_hight_light(self): 
        command_list = tk_component['input1'].get("0.0","end")[:-1].split("\n")
        match_list = [list(re.finditer("\\$temp[0-9]+",text1)) for text1 in command_list]
        tk_component['input1'].tag_remove('template', "0.0",tkinter.END)
        for i in range(len(match_list)) :
            for j in match_list[i] :
                if j == None : continue
                tk_component['input1'].tag_add('template', "%s.%s"%(i+1,j.start()), "%s.%s"%(i+1,j.end()))
        self.update_temp_detials(match_list)

    def update_temp_detials(self,match_list) :
        self.template_choose['Template'].clear() ; was_registered = []
        for i in range(len(match_list)) :
            for j in match_list[i] :
                if j.group() not in self.all_set_template_details : 
                    self.all_set_template_details[j.group()] = {"temp_name": j.group(), "temp_type": 0, "temp_detial": ""}
                if j.group() not in was_registered :
                    self.template_choose['Template'].append(self.all_set_template_details[j.group()])
                    was_registered.append(j.group())
        self.choose_template_details(0)

    def exit_template(self) :
        self.save_file()
        tk_component['open_list'].delete(0,tkinter.END)
        for i in self.save_data : tk_component['open_list'].insert(tkinter.END,i['name'])
        self.open_win()


    def test_can_generate(self) :
        try : 
            text1 = tk_component['generate_times'].get()
            if (math.floor(float(text1)) < 1) or ("." in text1) : raise Exception
        except : tkinter.messagebox.showerror("Error","生成次数不是正整数") ; return None
        
        for temp1 in self.template_choose['Template'] :
            if temp1['temp_type'] == 0 : 
                tkinter.messagebox.showerror("Error","模板样式未选择模板类型\n%s"%temp1['temp_name']) ; return None
            elif temp1['temp_type'] == 3 : 
                try : self.test_var(temp1['temp_detial'],temp1['temp_name'])
                except : return None
            elif temp1['temp_type'] == 4 : 
                test_text1 = temp1['temp_detial'].split("\n")
                if len(test_text1) < 2 : tkinter.messagebox.showerror("Error","模板样式%s\n提供参数过少"%temp1['temp_name']) ; return None
                try : self.test_var(test_text1[0],temp1['temp_name'])
                except : traceback.print_exc() ; return None

                count_var = test_text1[1].count("%s")
                if count_var != (len(test_text1) - 2) : 
                    tkinter.messagebox.showerror("Error","模板样式%s提供的\n后续表达式数量不对等"%temp1['temp_name']) ; return None
                for i in test_text1[2:] :
                    try : self.test_var(i,temp1['temp_name'])
                    except : traceback.print_exc() ; return None

        if self.generate_command() : self.result_window()

    def test_var(self,str1, name) :
        try : byte_code = compile(str1, "string", "eval")
        except : tkinter.messagebox.showerror("Error","模板样式%s\n出现语法错误"%name) ; raise Exception
        set1 = set(byte_code.co_names) - set(tuple(self.support_const.keys()) + tuple(self.support_compute.keys()))
        if len(set1) : tkinter.messagebox.showerror("Error","模板样式%s\n出现非法变量\n%s"%(name,set1)) ; raise Exception

    def generate_command(self) :
        times,all_times = 0,math.floor(float(tk_component['generate_times'].get()))
        tk_component["output1"].delete("0.0",tkinter.END) ; self.support_const['var0'] = all_times
        template1 = string.Template(tk_component["input1"].get("0.0",tkinter.END))

        while times < all_times :
            self.support_const['var1'] = times + 1 ; temp_json = {}
            for temp1 in self.template_choose['Template'] :
                name1 = temp1['temp_name'].replace("$","",1)
                if temp1['temp_type'] == 1 : 
                    list1 = temp1['temp_detial'].split('\n')
                    if times >= len(list1) : times = all_times ; break
                    temp_json[name1] = list1[times]
                elif temp1['temp_type'] == 2 : 
                    list1 = temp1['temp_detial'].split('\n')
                    temp_json[name1] = list1[times%len(list1)]
                elif temp1['temp_type'] == 3 : 
                    try : 
                        temp_json[name1] = eval(temp1['temp_detial'],self.support_const,self.support_compute)
                        if type(temp_json[name1]) in [type(1.0)] : temp_json[name1] = replace_zero("%.10f" % temp_json[name1])
                    except : tkinter.messagebox.showerror("Error","模板样式%s\n出现运算错误"%temp1['temp_name']) ; return None
                elif temp1['temp_type'] == 4 : 
                    test_text1 = temp1['temp_detial'].split("\n")
                    try : gen_count = eval(test_text1[0],self.support_const,self.support_compute)
                    except : tkinter.messagebox.showerror("Error","模板样式%s\n字段次数运算错误"%temp1['temp_name']) ; return None
                    if not isinstance(gen_count,(float,int)) : 
                        tkinter.messagebox.showerror("Error","模板样式%s\n生成次数出现非数字"%temp1['temp_name']) ; return None

                    self.support_const['var3'] = gen_count = math.floor(gen_count); count_var = test_text1[1].count("%s"); text_list = []
                    if gen_count < 0 : tkinter.messagebox.showerror("Error","模板样式%s\n生成次数出现负数"%temp1['temp_name']) ; return None
                        
                    for i in range(gen_count) :
                        self.support_const['var2'] = i + 1
                        try : var_list = [eval(test_text1[2 + j],self.support_const,self.support_compute) for j in range(count_var)]
                        except : tkinter.messagebox.showerror("Error","模板样式%s\n出现运算错误"%temp1['temp_name']) ; return None
                        #print(var_list,temp_json)
                        var_list = [(replace_zero("%.10f" % j) if isinstance(j,float) else j) for j in var_list]
                        text_list.append(test_text1[1]%tuple(var_list))
                    self.support_const['var2'] = None ; self.support_const['var3'] = None ; temp_json[name1] = " ".join(text_list)

            if times < all_times : tk_component['output1'].insert(tkinter.END, template1.safe_substitute(temp_json)) ; times += 1

        self.support_const['var1'] = None
        return True


    def result_window(self) :
        self.open_win('result_frame')

    def copy_all(self) :
        text = tk_component["output1"].get("0.0", tkinter.END)[:-1]
        tk_tool.copy_to_clipboard(text)


def UI_set(main_win, tkinter_Frame:tkinter.Frame) :
    global tk_component
    pack_object:pack_class = main_win.get_expand_pack_class_object("cf061f76-414f-410e-ad6b-7b1876343918")

    main_frame = tkinter.Frame(tkinter_Frame)
    tkinter.Label(main_frame,text="命令模板生成",fg='black',font=tk_tool.get_default_font(20),width=15,height=1).pack()

    tkinter.Canvas(main_frame,width=2000,height=10).pack()
    frame_m10 = tkinter.Frame(main_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    file_select = tkinter.Listbox(frame_m10,font=tk_tool.get_default_font(12),selectmode=tkinter.SINGLE,height=15,width=24,yscrollcommand=sco1.set)
    file_select.grid()
    sco1.config(command=file_select.yview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    file_select.bind("<Double-ButtonRelease-1>", lambda e : pack_object.open_template())
    frame_m10.pack()
    tkinter.Canvas(main_frame,width=10,height=10).pack()

    frame_m6 = tkinter.Frame(main_frame)
    tkinter.Button(frame_m6,text='新建',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,
        command=pack_object.creat_new_template).pack(side='left')
    tkinter.Label(frame_m6,fg='black',font=tk_tool.get_default_font(6),width=2,height=1).pack(side='left')
    tkinter.Button(frame_m6,text='删除',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,
        command=pack_object.delete_template).pack(side='left')
    tkinter.Label(frame_m6,fg='black',font=tk_tool.get_default_font(6),width=2,height=1).pack(side='left')
    tkinter.Button(frame_m6,text='打开',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,
        command=pack_object.open_template).pack(side='left')
    frame_m6.pack()
    main_frame.pack()

    tkinter.Label(main_frame, text="",fg='black',font=tk_tool.get_default_font(1), width=15, height=1).pack()
    frame_m6 = tkinter.Frame(main_frame)
    tkinter.Button(frame_m6,text='导入',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,
        command=pack_object.import_file).pack(side='left')
    tkinter.Label(frame_m6,fg='black',font=tk_tool.get_default_font(6),width=2,height=1).pack(side='left')
    tkinter.Button(frame_m6,text='导出',font=tk_tool.get_default_font(12),bg='#9ae9d1' ,width=5, height=1,
        command=pack_object.export_file).pack(side='left')
    tkinter.Label(frame_m6,fg='black',font=tk_tool.get_default_font(6),width=2,height=1).pack(side='left')
    tkinter.Button(frame_m6,text='帮助',font=tk_tool.get_default_font(12),bg='#7fc8ff' ,width=5, height=1,
        command=lambda: webbrowser.open("http://localhost:32323/tutorial/ExpandPack.html")).pack(side='left')
    frame_m6.pack()
    main_frame.pack()


    edit_frame = tkinter.Frame(tkinter_Frame)
    temple_title = tkinter.Entry(edit_frame,font=tk_tool.get_default_font(13),width=18,justify='center')
    temple_title.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    temple_title.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
    temple_title.bind("<<update-status>>", lambda a:pack_object.save_title())
    temple_title.pack()
    tkinter.Label(edit_frame, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()

    frame_m10 = tkinter.Frame(edit_frame)
    tkinter.Label(frame_m10, text="模板生成次数",bg="#b0b0b0",fg='black', font=tk_tool.get_default_font(13), width=15, height=1).pack(side='left')
    gen_times = tkinter.Entry(frame_m10, font=tk_tool.get_default_font(13), width=5, justify='center')
    gen_times.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    gen_times.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
    gen_times.bind("<<update-status>>", lambda a:pack_object.save_gentime())
    gen_times.pack(side='left')
    frame_m10.pack()

    frame_m10 = tkinter.Frame(edit_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    expand_input_1 = tkinter.Text(frame_m10,show=None,height=11,width=30,font=tk_tool.get_default_font(10),undo=True,yscrollcommand=sco1.set)
    expand_input_1.grid()
    expand_input_1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    sco1.config(command=expand_input_1.yview)
    expand_input_1.tag_config("template",foreground="orange")
    expand_input_1.tag_config("select",background="#467f46")
    expand_input_1.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
    expand_input_1.bind("<<update-status>>", lambda a:pack_object.save_command())
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    frame_m10.pack()

    tkinter.Label(edit_frame, fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()

    frame_m10 = tkinter.Frame(edit_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    expand_input_2 = tkinter.Text(frame_m10,show=None,height=5,width=30,font=tk_tool.get_default_font(10),undo=True,yscrollcommand=sco1.set)
    expand_input_2.grid()
    expand_input_2.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    expand_input_2.event_add("<<update-status>>","<KeyRelease>", "<ButtonRelease>")
    expand_input_2.bind("<<update-status>>", lambda a : pack_object.save_temp())
    sco1.config(command=expand_input_2.yview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    frame_m10.pack()

    width_2 = 3 if platform.system() == 'Windows' else 1
    frame_m10 = tkinter.Frame(edit_frame)
    tkinter.Button(frame_m10,text='←',font=tk_tool.get_default_font(9),bg='#9ae9d1',width=width_2,height=1,
        command=lambda : pack_object.choose_template_details(-1)).grid(row=0,column=0)
    com = ttk.Combobox(frame_m10, font=tk_tool.get_default_font(13), width=10, state='readonly', justify='center')
    com["value"] = ("请选择种类", "单次列表", "循环列表", "复杂表达式", "多段字符")
    com.bind("<<ComboboxSelected>>", lambda a : pack_object.save_gentype())
    com.current(0)
    com.grid(row=0,column=2)
    tkinter.Button(frame_m10,text='→',font=tk_tool.get_default_font(9),bg='#9ae9d1',width=width_2,height=1,
        command=lambda:pack_object.choose_template_details(1)).grid(row=0,column=3)
    frame_m10.pack()

    tkinter.Label(edit_frame, text="",fg='black',font=tk_tool.get_default_font(6), width=15, height=1).pack()
    frame_m6 = tkinter.Frame(edit_frame)
    tkinter.Button(frame_m6,text='保存退出',font=tk_tool.get_default_font(12),bg='#00ffff' ,width=9, height=1,
        command=pack_object.exit_template).pack(side='left')
    tkinter.Canvas(frame_m6,width=15, height=5).pack(side='left')
    tkinter.Button(frame_m6,text='生成命令',font=tk_tool.get_default_font(12),bg='#00ffff' ,width=9, height=1,
        command=pack_object.test_can_generate).pack(side='left')
    frame_m6.pack()

    result_frame = tkinter.Frame(tkinter_Frame)
    tkinter.Label(result_frame, text="命令输出界面",fg='black',font=tk_tool.get_default_font(13), width=15, height=1).pack()
    frame_m10 = tkinter.Frame(result_frame)
    sco1 = tkinter.Scrollbar(frame_m10,orient='vertical')
    sco2 = tkinter.Scrollbar(frame_m10,orient="horizontal")
    expand_output_1 = tkinter.Text(frame_m10,show=None,wrap=tkinter.NONE,height=20,width=30,font=tk_tool.get_default_font(10),undo=True,yscrollcommand=sco1.set, xscrollcommand=sco2.set)
    expand_output_1.grid()
    expand_output_1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    sco1.config(command=expand_output_1.yview)
    sco1.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
    sco2.config(command=expand_output_1.xview)
    sco2.grid(sticky=tkinter.W+tkinter.E)
    frame_m10.pack()

    tkinter.Label(result_frame, text="",fg='black',font=tk_tool.get_default_font(3), width=15, height=1).pack()

    frame_m6 = tkinter.Frame(result_frame)
    tkinter.Button(frame_m6,text='返回模板',font=tk_tool.get_default_font(12),bg='#00ffff' ,width=9, height=1,
                   command=lambda:pack_object.open_win('edit_frame')).pack(side='left')
    tkinter.Canvas(frame_m6,width=15, height=5).pack(side='left')
    tkinter.Button(frame_m6,text='复制全部',font=tk_tool.get_default_font(12),bg='#00ffff' ,width=9, height=1,
                   command=lambda:pack_object.copy_all()).pack(side='left')
    frame_m6.pack()




    tk_component = {"frame":{"main_frame":main_frame, "edit_frame":edit_frame, "result_frame":result_frame},
    "open_list":file_select, "input1": expand_input_1, "input2": expand_input_2,
    "temple_title": temple_title, "generate_times": gen_times, "temp_choose": com, "output1": expand_output_1}
    for i in pack_object.save_data : file_select.insert(tkinter.END,i['name'])

