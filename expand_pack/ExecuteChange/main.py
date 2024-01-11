import tkinter,tkinter.messagebox,os,threading,re,types,sys,webbrowser,traceback
from tkinter import ttk
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))
base_path = os.path.dirname(os.path.abspath(__file__))

import main_source.package.python_bdx as python_bdx
import main_source.package.python_nbt as python_nbt
import main_source.package.python_numpy as np
import main_source.package.tk_tool as tk_tool
import main_source.package.file_operation as file_IO

import command_tree,execute_transfor,blockstate_transfor
from main_source.bedrock_edition.command_class.parser import ParserSystem


os.makedirs(os.path.join(base_path,'input'),exist_ok=True)
os.makedirs(os.path.join(base_path,'output'),exist_ok=True)
transfor_input = False ; transfor_file = False
tkinter_component = {"input":tkinter.Text, "output":tkinter.Text, "input_version":ttk.Combobox, "output_version":ttk.Combobox}


class pack_class : 

    def __init__(self) -> None :
        self.Parser = ParserSystem.Command_Parser(command_tree.Command_Tree)
        self.Transfor_1_19_50 = execute_transfor.Start_Transformer
        self.Transfor_1_20_00 = blockstate_transfor.Start_Transformer

    def loop_method(self) :
        global transfor_input,transfor_file,tkinter_component
        if not(transfor_input or transfor_file) : return
        tkinter_component["input"].tag_remove("syntax_error", "0.0", tkinter.END)
        if tkinter_component["input_version"].current() == 1 and tkinter_component["output_version"].current() == 0 :
            tkinter.messagebox.showerror("Error", "输入输出选择的版本不正确")
            transfor_file = False
            transfor_input = False
        if tkinter_component["output_version"].current() == 0 : execute_transfor.Set_Version(False)
        elif tkinter_component["output_version"].current() == 1 : execute_transfor.Set_Version(True)

        if transfor_input : 
            if tkinter_component["input_version"].current() == 0 : self.exchange_text_1_19_0()
            elif tkinter_component["input_version"].current() == 1 : self.exchange_text_1_19_50()
            transfor_input = False
        if transfor_file :
            if tkinter_component["input_version"].current() == 0 : self.exchange_dir_1_19_0()
            elif tkinter_component["input_version"].current() == 1 : self.exchange_dir_1_19_50()
            transfor_file = False



    def set_output_mark_and_see(self, lines:int, error:list) :
        global tkinter_component
        tkinter_component["output"].insert('end',"第%s行发生错误：\n %s" % (lines, error[0]))
        if hasattr(error[1], "pos") : tkinter_component["input"].tag_add("syntax_error", 
            "%s.%s"%(lines,error[1].pos[0]), "%s.end"%lines )
        tkinter_component["input"].mark_set( "my_cursor", "%s.0"%lines )
        tkinter_component["input"].see( "%s.0"%lines )

    def set_file_output(self, file:str, lines:int, error:str) :
        tkinter_component["output"].insert('end', "文件 %s (第%s行) 发生错误：\n%s\n\n" % (
            file.replace(base_path,"",1), lines, error))

    def set_bdx_file_output(self, file:str, command:str, error:str) :
        tkinter_component["output"].insert('end', "文件 %s 发生错误：\n%s\n%s\n\n" % (
            file.replace(base_path,"",1), command, error))



    def exchange_text_1_19_0(self) :
        global tkinter_component
        tkinter_component["output"].delete("1.0",'end')
        result_list = []
        input_text = tkinter_component["input"].get("0.0",tkinter.END)[:-1].split("\n")

        for lines,text1 in enumerate(input_text) :
            lines += 1
            if text1.replace(" ","") == "" : continue
            token_list = self.Parser.parser(text1, (1,19,49))
            if isinstance(token_list,tuple) :self.set_output_mark_and_see(lines, token_list) ; return None
            trans_text = self.Transfor_1_19_50(token_list)
            if isinstance(trans_text,tuple) : self.set_output_mark_and_see(lines, trans_text) ; return None
            result_list.append(trans_text)

        tkinter_component["output"].insert('end', "\n".join(result_list))

    def exchange_dir_1_19_0(self) : 
        threading.Thread(target=self.tread_run_exchange_dir_1_19_0).start()

    def tread_run_exchange_dir_1_19_0(self) : 
        global tkinter_component
        tkinter_component["output"].delete("1.0",'end')
        a = tkinter.messagebox.askquestion("Q","二次确认：是否转换在\ninput文件夹下的所有文件？")
        if a != "yes" : return None

        tk_things = tk_tool.tk_Msgbox(self.main_win.window, self.main_win.window)
        tkinter.Label(tk_things, text="   ", font=tk_tool.get_default_font(4), height=1).pack()
        msg = tkinter.Label(tk_things, text="   ", font=tk_tool.get_default_font(12), height=2)
        msg.pack() ; re_bdx = re.compile("\\.bdx$") ; result_list = []
        loop_list = file_IO.file_in_path(os.path.join(base_path, "input"))

        for count,file_name in enumerate(loop_list):
            msg.config(text="正在转换\n%s已转换，共%s个文件" % (count+1 , len(loop_list)))
            if not re.search("(\\.mcfunction|\\.txt|\\.bdx)$",file_name) : continue

            if not re_bdx.search(file_name) :
                try : input_text = file_IO.read_a_file(file_name).split("\n")
                except : continue
                for lines,text1 in enumerate(input_text) :
                    lines += 1
                    if text1.replace(" ","") == "" : continue
                    token_list = self.Parser.parser(text1, (1,19,49))
                    if isinstance(token_list,tuple) :self.set_file_output(file_name, lines, token_list[0]) ; continue
                    trans_text = self.Transfor_1_19_50(token_list)
                    if isinstance(trans_text,tuple) : self.set_file_output(file_name, lines, trans_text[0]) ; continue
                    result_list.append(trans_text)
                file_IO.write_a_file(file_name.replace("input","output",1),"\n".join(result_list))
                result_list.clear()
            else : 
                try : bdx_obj = python_bdx.BDX_File(file_name)
                except : 
                    tkinter_component["output"].insert('end', "文件: %s 发生错误：\n%s\n" % (
                        file_name.replace(base_path,"",1), traceback.format_exc()))
                    continue
                command_dir = [i for i in bdx_obj.operation_list if (i.operation_code in (0x22,0x23,0x24,0x1a,0x1b,0x29))]
                for operation in command_dir :
                    if operation.operation_code != 0x29 : Command = operation.command
                    else :
                        nbt = operation.nbt
                        if not(('id' in nbt) and (nbt['id'].value == 'CommandBlock') and ('Command' in nbt)) : continue
                        Command = nbt['Command'].value
                        if Command == "***" :  self.set_bdx_file_output(file_name, Command, "命令已被网易屏蔽，命令方块坐标(%s, %s, %s)" % (
                            nbt["x"].value, nbt["y"].value, nbt["z"].value)) ; continue
                    if Command.replace(" ","") == "" : continue
                    if isinstance(Command, bytes) : self.set_bdx_file_output(file_name, str(Command), "utf-8解码失败") ; continue
                    token_list = self.Parser.parser(Command, (1,19,49))
                    if isinstance(token_list,tuple) : self.set_bdx_file_output(file_name, Command, token_list[0]) ; continue
                    trans_text = self.Transfor_1_19_50(token_list)
                    if isinstance(trans_text,tuple) : self.set_bdx_file_output(file_name, Command, trans_text[0]) ; continue
                    if operation.operation_code != 0x29 : operation.command = trans_text
                    else : nbt['Command'] = python_nbt.nbt.NBTTagString(trans_text)
                try : bdx_obj.save_as(file_name.replace("input","output",1))
                except : traceback.print_exc()
                else : bdx_obj.close()
            
        tk_things.destroy()
        tkinter_component["output"].insert("1.0", "转换已完成\n\n")



    def exchange_text_1_19_50(self) :
        global tkinter_component
        tkinter_component["output"].delete("1.0",'end')
        result_list = []
        input_text = tkinter_component["input"].get("0.0",tkinter.END)[:-1].split("\n")

        for lines,text1 in enumerate(input_text) :
            lines += 1
            if text1.replace(" ","") == "" : continue
            token_list = self.Parser.parser(text1, (1,19,50))
            if isinstance(token_list,tuple) :self.set_output_mark_and_see(lines, token_list) ; return None
            trans_text = self.Transfor_1_20_00(token_list)
            if isinstance(trans_text,tuple) : self.set_output_mark_and_see(lines, trans_text) ; return None
            result_list.append(trans_text)

        tkinter_component["output"].insert('end', "\n".join(result_list))

    def exchange_dir_1_19_50(self) : 
        threading.Thread(target=self.tread_run_exchange_dir_1_19_50).start()

    def tread_run_exchange_dir_1_19_50(self) : 
        global tkinter_component
        tkinter_component["output"].delete("1.0",'end')
        a = tkinter.messagebox.askquestion("Q","二次确认：是否转换在\ninput文件夹下的所有文件？")
        if a != "yes" : return None

        tk_things = tk_tool.tk_Msgbox(self.main_win.window, self.main_win.window)
        tkinter.Label(tk_things, text="   ", font=tk_tool.get_default_font(4), height=1).pack()
        msg = tkinter.Label(tk_things, text="   ", font=tk_tool.get_default_font(12), height=2)
        msg.pack() ; re_bdx = re.compile("\\.bdx$") ; result_list = []
        loop_list = file_IO.file_in_path(os.path.join(base_path, "input"))
        for count,file_name in enumerate(loop_list):
            msg.config(text="正在转换\n%s已转换，共%s个文件" % (count+1 , len(loop_list)))
            if not re.search("(\\.mcfunction|\\.txt|\\.bdx)$",file_name) : continue

            if re_bdx.search(file_name) :
                try : input_text = file_IO.read_a_file(file_name).split("\n")
                except : continue
                for lines,text1 in enumerate(input_text) :
                    lines += 1
                    if text1.replace(" ","") == "" : continue
                    token_list = self.Parser.parser(text1, (1,19,50))
                    if isinstance(token_list,tuple) :self.set_file_output(file_name, lines, token_list) ; return None
                    trans_text = self.Transfor_1_20_00(token_list)
                    if isinstance(trans_text,tuple) : self.set_file_output(file_name, lines, trans_text) ; return None
                    result_list.append(trans_text)
                file_IO.write_a_file(file_name.replace("input","output",1),"\n".join(result_list))
                result_list.clear()

            else : 
                try :bdx_obj = python_bdx.BDX_File(file_name)
                except : 
                    tkinter_component["output"].insert('end', "文件: %s 发生错误：\n%s\n" % (
                        file_name.replace(base_path,"",1), traceback.format_exc()))
                    continue
                command_dir = [i for i in bdx_obj.operation_list if (i.operation_code in (0x22,0x23,0x24,0x1a,0x1b,0x29))]
                for operation in command_dir :
                    if operation.operation_code != 0x29 : Command = operation.command
                    else :
                        nbt = operation.nbt
                        if not(('id' in nbt) and (nbt['id'].value == 'CommandBlock') and ('Command' in nbt)) : continue
                        Command = nbt['Command'].value
                        if Command == "***" :  self.set_bdx_file_output(file_name, Command, "命令已被网易屏蔽，命令方块坐标(%s, %s, %s)" % (
                            nbt["x"].value, nbt["y"].value, nbt["z"].value)) ; continue
                    if Command.replace(" ","") == "" : continue
                    if isinstance(Command, bytes) : self.set_bdx_file_output(file_name, str(Command), "utf-8 解码失败") ; continue
                    token_list = self.Parser.parser(Command, (1,19,50))
                    if isinstance(token_list,tuple) :self.set_bdx_file_output(file_name, Command, token_list[0]) ; continue
                    trans_text = self.Transfor_1_20_00(token_list)
                    if isinstance(trans_text,tuple) : self.set_bdx_file_output(file_name, Command, trans_text[0]) ; continue
                    if operation.operation_code != 0x29 : operation.command = trans_text
                    else : nbt['Command'] = python_nbt.nbt.NBTTagString(trans_text)
                try : bdx_obj.save_as(file_name.replace("input","output",1))
                except : traceback.print_exc()
                else : bdx_obj.close()
        tk_things.destroy()
        tkinter_component["output"].insert("转换已完成")







def click_transfor_input() :
    global transfor_input,input_text
    transfor_input = True

def click_transfor_file() :
    global transfor_file
    transfor_file = True


def UI_set(main_win, tkinter_Frame:tkinter.Frame) :
    global tkinter_component

    tkinter.Label(tkinter_Frame, text="   ", font=tk_tool.get_default_font(4), height=1).pack()

    frame_m11 = tkinter.Frame(tkinter_Frame)
    tkinter.Label(frame_m11, text="输入区版本", bg='aqua',fg='black',font=tk_tool.get_default_font(11), width=11, height=1).pack(side=tkinter.LEFT)
    input0 = ttk.Combobox(frame_m11, font=tk_tool.get_default_font(11), width=6, state='readonly', justify='center')
    input0["value"] = ("1.19.0", "1.19.50") ; input0.current(0)
    input0.pack(side=tkinter.LEFT) ; frame_m11.pack()
    
    expand_input_1 = tkinter.Text(tkinter_Frame,show=None,height=9,width=27,font=tk_tool.get_default_font(10),undo=True)
    expand_input_1.tag_config("syntax_error", background="#ff6161")
    expand_input_1.pack()
    expand_input_1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    tkinter.Label(tkinter_Frame, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()

    expand_ui_2 = tkinter.Frame(tkinter_Frame)
    tkinter.Button(expand_ui_2, text='转换输入',font=tk_tool.get_default_font(10),bg='orange',width=8,height=1,
    command=click_transfor_input).pack(side='left')
    tkinter.Label(expand_ui_2, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack(side='left')
    tkinter.Button(expand_ui_2, text='帮助',font=tk_tool.get_default_font(10),bg='#7fc8ff',width=4,height=1,
    command=lambda:webbrowser.open("http://localhost:32323/tutorial/ExpandPack.html")).pack(side='left')
    tkinter.Label(expand_ui_2, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack(side='left')
    tkinter.Button(expand_ui_2, text='批量转换',font=tk_tool.get_default_font(10),bg='orange',width=8,height=1,
    command=click_transfor_file).pack(side='left')
    expand_ui_2.pack()

    tkinter.Label(tkinter_Frame, text="", fg='black', font=tk_tool.get_default_font(3), width=2, height=1).pack()
    expand_output_1 = tkinter.Text(tkinter_Frame,show=None,height=9,width=27,font=tk_tool.get_default_font(10),undo=True)
    expand_output_1.pack()
    expand_output_1.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    frame_m11 = tkinter.Frame(tkinter_Frame)
    tkinter.Label(frame_m11, text="输出区版本" , bg='aqua',fg='black',font=tk_tool.get_default_font(11), width=11, height=1).pack(side=tkinter.LEFT)
    input1 = ttk.Combobox(frame_m11, font=tk_tool.get_default_font(11), width=6, state='readonly', justify='center')
    input1["value"] = ("1.19.50", "1.20.0")
    input1.current(0)
    input1.pack(side=tkinter.LEFT) ; frame_m11.pack()

    tkinter_component["input"] = expand_input_1
    tkinter_component["output"] = expand_output_1
    tkinter_component["input_version"] = input0
    tkinter_component["output_version"] = input1





#execute as @s[r=2,hasitem={item=aaa,data=1}] at @s positioned ~ 2 ~4 if block ^ ^ ^ minecraft:bedrock["infiniburn_bit":false] run setblock ~ ~ ~ minecraft:bedrock["infiniburn_bit":true]
