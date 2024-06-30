import tkinter,tkinter.messagebox,os,threading,re,sys,webbrowser,traceback,functools
from tkinter import ttk
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))
base_path = os.path.dirname(os.path.abspath(__file__))

import main_source.package.python_bdx as python_bdx
import main_source.package.tk_tool as tk_tool
import main_source.package.file_operation as file_IO

from transform_core import Analysis_Setting, Command_Str_Transfor

INPUT_PATH = os.path.join(base_path,'input')
OUTPUT_PATH = os.path.join(base_path,'output')
os.makedirs(INPUT_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)
SUPPORT_FILE = re.compile("(\\.mcfunction|\\.txt|\\.bdx)$")
COMMAND_VERSION = ((1,19,0), (1,19,50))
OUTPUT_VERSION  = ((1,19,50), (1,19,70), (1,20,10))
tkinter_component = {}


class pack_class : pass




def open_test(Menu:tkinter.Frame, Trans:tkinter.Frame) :
    global InputTextHashSave

    test1 = tkinter_component["transform_execute"]()
    test2 = tkinter_component["transform_block_command"]()
    test3 = tkinter_component["transform_summon"]()
    if not(test1 or test2 or test3) : 
        tkinter.messagebox.showerror("Error", "请选择需要转换的命令")
        return None
    
    test4 = tkinter_component["command_version"]()
    test5 = tkinter_component["output_version"]()
    if test4 == 1 and test5 == 0 :
        tkinter.messagebox.showerror("Error", "命令版本与导出版本不能相同")
        return None
    
    InputTextHashSave = None
    Menu.pack_forget() ; Trans.pack()
    
def UI_set(main_win, tkinter_Frame:tkinter.Frame) :
    global Root_Win, InputMethod
    Root_Win = main_win.window
    InputMethod = main_win.set_focus_input

    Menu_Frame = tkinter.Frame(tkinter_Frame)
    tkinter.Label(Menu_Frame, text="   ", font=tk_tool.get_default_font(4), height=1).pack()
    tkinter.Label(Menu_Frame,text="语法转换升级",fg='black',font=tk_tool.get_default_font(25)).pack()

    tkinter.Label(Menu_Frame, text="   ", font=tk_tool.get_default_font(4), height=3).pack()
    tkinter.Label(Menu_Frame,text=" 选择需要转换的命令 ",fg='white',bg='#8c0000',font=tk_tool.get_default_font(13)).pack()
    middle_frame_1 = tkinter.Frame(Menu_Frame)
    checkbutton_var1 = tkinter.IntVar() ; checkbutton_var2 = tkinter.IntVar()
    checkbutton_var3 = tkinter.IntVar() ; checkbutton_var4 = tkinter.IntVar()
    checkbutton1 = tkinter.Checkbutton(middle_frame_1, text="execute 命令",font=tk_tool.get_default_font(11), variable=checkbutton_var1, onvalue=1, offvalue=0)
    checkbutton2 = tkinter.Checkbutton(middle_frame_1, text="fill 等方块类命令",font=tk_tool.get_default_font(11), variable=checkbutton_var2, onvalue=1, offvalue=0)
    checkbutton3 = tkinter.Checkbutton(middle_frame_1, text="summon 命令",font=tk_tool.get_default_font(11), variable=checkbutton_var3, onvalue=1, offvalue=0)
    checkbutton4 = tkinter.Checkbutton(middle_frame_1, text="structure 命令",font=tk_tool.get_default_font(11), variable=checkbutton_var4, onvalue=1, offvalue=0)
    checkbutton1.pack(anchor="w") ; checkbutton2.pack(anchor="w")
    checkbutton3.pack(anchor="w") ; checkbutton4.pack(anchor="w")
    middle_frame_1.pack()

    tkinter.Label(Menu_Frame, text="   ", font=tk_tool.get_default_font(10), height=1).pack()
    tkinter.Label(Menu_Frame,text=" 选择原命令版本 ",fg='white',bg='#008c00',font=tk_tool.get_default_font(13)).pack()
    version1 = ttk.Combobox(Menu_Frame, font=tk_tool.get_default_font(11), width=10, state='readonly', justify='center')
    version1["value"] = tuple("%s.%s.%s"%i for i in COMMAND_VERSION) ; version1.current(0) ; version1.pack()
    tkinter.Label(Menu_Frame, text="   ", font=tk_tool.get_default_font(4), height=2).pack()

    tkinter.Label(Menu_Frame,text="  选择导出版本  ",fg='white',bg='#008c00',font=tk_tool.get_default_font(13)).pack()
    version2 = ttk.Combobox(Menu_Frame, font=tk_tool.get_default_font(11), width=10, state='readonly', justify='center')
    version2["value"] = tuple("%s.%s.%s"%i for i in OUTPUT_VERSION) ; version2.current(2) ; version2.pack()

    tkinter.Label(Menu_Frame, text="   ", font=tk_tool.get_default_font(10), height=2).pack()
    middle_frame_2 = tkinter.Frame(Menu_Frame)
    tkinter.Button(middle_frame_2,text=' 打开转换 ',font=tk_tool.get_default_font(12),bg='#9ae9d1',
        command=lambda:open_test(Menu_Frame, Transfor_Frame) ).pack(side="left")
    tkinter.Label(middle_frame_2, text="    ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
    tkinter.Button(middle_frame_2,text=' 帮助文档 ',font=tk_tool.get_default_font(12),bg='#9ae9d1', command=
        lambda:webbrowser.open("http://localhost:32323/?pack=b96d85f5-789c-4812-895c-b1751c150adc&page=help")).pack(side="left")
    middle_frame_2.pack()


    Transfor_Frame = tkinter.Frame(tkinter_Frame)
    tkinter.Button(Transfor_Frame, text="  返回开始界面  ", background="#959cff", font=tk_tool.get_default_font(12),
        command=lambda:[Transfor_Frame.pack_forget(), Menu_Frame.pack()]).pack()
    tkinter.Label(Transfor_Frame, text="   ", font=tk_tool.get_default_font(5), height=1).pack()
    
    middle_frame_3 = tkinter.Frame(Transfor_Frame)
    tkinter.Button(middle_frame_3,text=' 转换文字 ',font=tk_tool.get_default_font(12),bg='#4ae9d1',
        command=lambda:[TransTextFrame.pack(),TransFileFrame.pack_forget()]).pack(side="left")
    tkinter.Label(middle_frame_3, text="    ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
    tkinter.Button(middle_frame_3,text=' 转换文件 ',font=tk_tool.get_default_font(12),bg='#4ae9d1',
        command=lambda:[TransTextFrame.pack_forget(),TransFileFrame.pack()]).pack(side="left")
    middle_frame_3.pack()
    tkinter.Label(Transfor_Frame, text="   ", font=tk_tool.get_default_font(9), height=1).pack()

    TransTextFrame = tkinter.Frame(Transfor_Frame)
    tkinter.Label(TransTextFrame, text=" 命令输入区 ", bg='aqua',fg='black',font=tk_tool.get_default_font(13), height=1).pack()
    InputText = tk_tool.tk_Scrollbar_Text(TransTextFrame, horizontal_scrollbar=False,height=8,width=27,font=tk_tool.get_default_font(10),undo=True)
    InputText.input_box.tag_config("syntax_error", background="#ff6161")
    InputText.input_box.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    InputText.pack()
    OutputText = tk_tool.tk_Scrollbar_Text(TransTextFrame, horizontal_scrollbar=False,height=8,width=27,font=tk_tool.get_default_font(10),undo=True)
    OutputText.input_box.tag_config("syntax_error", background="#ff6161")
    OutputText.input_box.bind("<FocusIn>",lambda a : main_win.set_focus_input(a))
    OutputText.pack()
    tkinter.Label(TransTextFrame, text=" 命令输出区 ", bg='aqua',fg='black',font=tk_tool.get_default_font(13), height=1).pack()
    TransTextFrame.pack()

    TransFileFrame = tkinter.Frame(Transfor_Frame)
    middle_frame_4 = tkinter.Frame(TransFileFrame)
    tkinter.Label(middle_frame_4, text=" 检索到的文件 ", bg='aqua',fg='black',font=tk_tool.get_default_font(13), height=1).pack(side="left")
    tkinter.Label(middle_frame_4, text="        ", font=tk_tool.get_default_font(9), height=1).pack(side="left")
    tkinter.Button(middle_frame_4,text=' 确认转换 ',font=tk_tool.get_default_font(9),bg='#ef9e00',
        command=lambda:Start_Trans_File(main_win.window, OutputFileErrorText.input_box)).pack(side="left")
    middle_frame_4.pack()
    InputFile = tk_tool.tk_Scrollbar_ListBox(TransFileFrame, horizontal_scrollbar=False, height=16,width=27,font=tk_tool.get_default_font(10))
    InputFile.pack()

    Transfor_File_Error_Frame = tkinter.Frame(tkinter_Frame)
    tkinter.Label(Transfor_File_Error_Frame, text="   ", font=tk_tool.get_default_font(9), height=1).pack()
    OutputFileErrorText = tk_tool.tk_Scrollbar_Text(Transfor_File_Error_Frame, horizontal_scrollbar=False,height=19,width=27,font=tk_tool.get_default_font(10),wrap="char")
    OutputFileErrorText.pack()
    tkinter.Label(Transfor_File_Error_Frame, text="   ", font=tk_tool.get_default_font(5), height=1).pack()
    middle_frame_4 = tkinter.Frame(Transfor_File_Error_Frame)
    tkinter.Button(middle_frame_4,text=' 界面返回 ',font=tk_tool.get_default_font(12),bg='#4ae9d1',
        command=lambda:[Transfor_Frame.pack(), Transfor_File_Error_Frame.pack_forget()]).pack(side="left")
    tkinter.Label(middle_frame_4, text="    ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
    tkinter.Button(middle_frame_4,text=' 再次转换 ',font=tk_tool.get_default_font(12),bg='#4ae9d1',
        command=lambda:ReTrans_File()).pack(side="left")
    middle_frame_4.pack()


    tkinter_component["transform_execute"] = checkbutton_var1.get
    tkinter_component["transform_block_command"] = checkbutton_var2.get
    tkinter_component["transform_summon"] = checkbutton_var3.get
    tkinter_component["transform_structure"] = checkbutton_var4.get
    tkinter_component["command_version"] = version1.current
    tkinter_component["output_version"] = version2.current

    tkinter_component["text_input"] = InputText.input_box
    tkinter_component["text_output"] = OutputText.input_box
    tkinter_component["file_input"] = InputFile.input_box
    tkinter_component["file_error"] = OutputFileErrorText.input_box

    tkinter_component["trans_frame"] = Transfor_Frame
    tkinter_component["error_frame"] = Transfor_File_Error_Frame
    
    InputText.input_box.after(500, lambda: Flash_Text_Output(InputText.input_box, OutputText.input_box))
    OutputFileErrorText.input_box.after(500, lambda: Flash_File_Output(InputFile.input_box))
    Menu_Frame.pack()




def Setting_Info() :
    Trans_Command = (tkinter_component["transform_execute"](), 
                     tkinter_component["transform_block_command"](), 
                     tkinter_component["transform_summon"](),
                     tkinter_component["transform_structure"]())
    Start_Version:tuple = tkinter_component["command_version"]()
    End_Version:tuple = tkinter_component["output_version"]()
    return Trans_Command,Start_Version,End_Version


InputTextHashSave = None
def Flash_Text_Output(Input:tkinter.Text, Output:tkinter.Text) :
    global InputTextHashSave
    Input.after(500, lambda: Flash_Text_Output(Input, Output))

    TextContent = tkinter_component["text_input"].get("0.0", "end")[:-1]
    TextHash = hash(TextContent)
    if TextHash == InputTextHashSave : return None
    else : InputTextHashSave = TextHash

    Output.delete("0.0", "end")
    Input.tag_remove("syntax_error", "0.0", "end")
    Analysis_Setting( Setting_Info() )
    str_list = [] ; error_test = False
    for index, str1 in enumerate( TextContent.split("\n") ) :
        if str1.replace(" ", "").__len__() == 0 : continue
        a = Command_Str_Transfor(str1)
        if not isinstance(a, str) : Text_Syntax_Error_Tag(Input, Output, index+1, a) ; error_test = True
        else : str_list.append(a)
    if not error_test : Output.insert("end", "\n".join( str_list ))

def Text_Syntax_Error_Tag(Input:tkinter.Text, Output:tkinter.Text, lines:int, error:tuple) :
    Output.insert('end',"第%s行发生错误：\n%s\n\n" % (lines, error[0]))
    if hasattr(error[1], "pos") : Input.tag_add("syntax_error", "%s.%s"%(lines, error[1].pos[0]), "%s.end"%lines )
    else : Input.tag_add("syntax_error", "%s.%s"%(lines, 0), "%s.end"%lines )
    Input.mark_set( "my_cursor", "%s.end"%lines )
    Input.see( "%s.0"%lines )


FileHashSave = None
def Flash_File_Output(Listbox:tkinter.Listbox) :
    global FileHashSave
    Listbox.after(500, lambda: Flash_File_Output(Listbox))

    file_list = [k.replace(INPUT_PATH, "", 1)[1:] for k in file_IO.file_in_path(INPUT_PATH) if SUPPORT_FILE.search(k)]
    TextHash = hash(" ".join(file_list))
    if TextHash == FileHashSave : return None
    else : FileHashSave = TextHash

    Listbox.delete(0, "end")
    Listbox.insert("end", *file_list)

Error_File_Save = {}
def Start_Trans_File(TK:tkinter.Tk, Error_Print:tkinter.Text) :
    Error_Print.config(state="normal")
    Error_Print.delete("0.0", "end")
    Error_File_Save.clear()
    
    file_path_list = [k for k in file_IO.file_in_path(INPUT_PATH) if SUPPORT_FILE.search(k)]
    tk_things = tk_tool.tk_Msgbox(TK, TK)
    tkinter.Label(tk_things, text="   ", font=tk_tool.get_default_font(4), height=1).pack()
    msg = tkinter.Label(tk_things, text="   ", font=tk_tool.get_default_font(12), height=2)
    msg.pack()

    Analysis_Setting( Setting_Info() )
    threading.Thread(target=Trans_Thread, args=(msg, Error_Print, file_path_list)).start()

def Trans_Thread(Msg:tkinter.Label, Error:tkinter.Text, Path_List:list[str]) :
    Error_List = []

    for index1, path1 in enumerate(Path_List) :
        Error_List.clear()
        Msg.config(text="正在转换中...\n还剩 %s 个文件待转换" % (len(Path_List)-index1))
        if path1[-4:] == ".bdx" : Read_Bdx(path1, Error, Error_List)
        else : Read_Txt(path1, Error, Error_List)

    Error.config(state="disabled")
    Msg.master.destroy()
    tkinter_component["trans_frame"].pack_forget()
    tkinter_component["error_frame"].pack()

def Read_Bdx(path1:str, Error:tkinter.Text, Error_List:list) :
    try : bdx_obj = python_bdx.BDX_File(path1)
    except : 
        Error.insert('end', "文件 %s 发生错误：\n该文件并不是bdx格式的文件\n\n\n" % (
        path1.replace(INPUT_PATH,"",1)[1:], ))
    else :
        command_list = list( Search_Command(bdx_obj.operation_list) )
        for operation_info in command_list :
            if operation_info[1].operation_code != 0x29 : Command = operation_info[1].command
            else :
                nbt = operation_info[1].nbt
                if ('id' not in nbt) or (nbt['id'].value != 'CommandBlock') or ('Command' not in nbt) : continue
                Command = nbt['Command'].value
            a = Command_Str_Transfor(Command)
            if not isinstance(a, str) : Error_List.append( [*operation_info, False] )
            elif operation_info[1].operation_code != 0x29 : operation_info[1].command = a
            else : operation_info[1].nbt['Command'].value = a
        if Error_List : Error_File_Save[path1] = (bdx_obj, list(Error_List)) ; File_Syntax_Error_Tag("bdx", path1, Error, Error_List)
        else : bdx_obj.save_as(path1.replace("input", "output", 1)) ; bdx_obj.close()

def Read_Txt(path1:str, Error:tkinter.Text, Error_List:list) :
    Blank = re.compile("^[ ]{0,}$|^[ ]{0,}#")
    try : Contents = file_IO.read_a_file(path1).split("\n")
    except : 
        Error.insert('end', "文件 %s 发生错误：\n该文件并不是utf-8编码的文件\n\n\n" % (
        path1.replace(INPUT_PATH,"",1)[1:], ))
    else :
        for lines, Command in enumerate(Contents) :
            if Blank.search(Command) : continue
            a = Command_Str_Transfor(Command)
            if not isinstance(a, str) : Error_List.append( [lines, Contents, False] )
            else : Contents[lines] = a
        if Error_List : Error_File_Save[path1] = (Contents, list(Error_List)) ; File_Syntax_Error_Tag("txt", path1, Error, Error_List)
        else : file_IO.write_a_file(path1.replace("input", "output", 1), "\n".join(Contents))

def Search_Command(Operation:list) :
    place_origin = [0, 0, 0]

    for code in Operation :
        oper_code:int = code.operation_code
        if oper_code in {0x06, 0x0c, 0x18, 0x19, 0x1e} : place_origin[2] += code.value
        elif oper_code in {0x16, 0x17, 0x1d} : place_origin[1] += code.value
        elif oper_code in {0x14, 0x15, 0x1c} : place_origin[0] += code.value
        elif oper_code in {0x12, 0x13} : place_origin[2] += 1 if oper_code == 0x12 else -1
        elif oper_code in {0x10, 0x11} : place_origin[1] += 1 if oper_code == 0x10 else -1
        elif oper_code in {0x0e, 0x0f} : place_origin[0] += 1 if oper_code == 0x0e else -1
        elif oper_code in {0x22,0x23,0x24,0x1a,0x1b,0x29} : yield (tuple(place_origin), code)

def File_Syntax_Error_Tag(Type:str, path1:str, Error:tkinter.Text, Error_List:list) :
    Error.insert('end', "文件 %s 发生错误：\n" % (path1.replace(INPUT_PATH,"",1)[1:], ))
    if Type == "bdx" :
        for index, (pos, code, _) in enumerate(Error_List) :
            pointer = Error_List[index]
            Button1 = tkinter.Button(Error, font=tk_tool.get_default_font(10), text="错误", fg="#ff0000")
            Button1.config(command=functools.partial(Spawn_TopLevel, Type, pos, code, Button1, pointer))
            Error.window_create("end", window=Button1)
            if index % 3 != 2 : Error.insert("end", " ")
            else : Error.insert("end", "\n")
    else :
        for index, (line, text_list, _) in enumerate(Error_List) :
            pointer = Error_List[index]
            Button1 = tkinter.Button(Error, font=tk_tool.get_default_font(10), text="错误", fg="#ff0000")
            Button1.config(command=functools.partial(Spawn_TopLevel, Type, line, text_list, Button1, pointer))
            Error.window_create("end", window=Button1)
            if index % 3 != 2 : Error.insert("end", " ")
            else : Error.insert("end", "\n")
    Error.insert('end', "\n\n\n")

def Spawn_TopLevel(Type, pos, code, Button1:tkinter.Button, Error_Pointer:list) :
    top = tkinter.Toplevel(Root_Win, )
    top.title("MsgBox")
    top.geometry( "%sx%s+%s+%s" % (
        int(Root_Win.winfo_width() * 0.95), int(Root_Win.winfo_height() * 0.6),
        Root_Win.winfo_x(), Root_Win.winfo_y()+50 ))
    top.transient(Root_Win)
    
    if Type == "bdx" : 
        pos_text = "CB坐标 %s\n相对于结构起始位置" % str(pos)
        if code.operation_code != 0x29 : Command = code.command
        else : Command = code.nbt['Command'].value
    else : 
        pos_text = "函数文件\n第 %s 行" % (pos + 1)
        Command = code[pos]
    
    tkinter.Label(top, text="   ", font=tk_tool.get_default_font(4), height=1).pack()
    tkinter.Label(top, text=pos_text, font=tk_tool.get_default_font(12), height=2).pack()
    OutputText = tk_tool.tk_Scrollbar_Text(top, horizontal_scrollbar=False, height=8, width=26, font=tk_tool.get_default_font(10),undo=True)
    OutputText.input_box.tag_config("syntax_error", background="#ff6161")
    OutputText.input_box.bind("<FocusIn>", lambda a : InputMethod(a))
    OutputText.input_box.insert("end", Command)
    OutputText.pack()
    Feedback = tkinter.Label(top, text="语法错误， 请修改", font=tk_tool.get_default_font(12), fg="#ff0000")
    Feedback.pack()
    tkinter.Label(top, text="   ", font=tk_tool.get_default_font(4), height=1).pack()
    middle_frame_4 = tkinter.Frame(top)
    tkinter.Button(middle_frame_4,text=' 取消 ',font=tk_tool.get_default_font(12),bg='#4ae9d1',command=top.destroy).pack(side="left")
    tkinter.Label(middle_frame_4, text="      ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
    tkinter.Button(middle_frame_4,text=' 忽略 ',font=tk_tool.get_default_font(12),bg='#4ae9d1',command=lambda:Pass()).pack(side="left")
    tkinter.Label(middle_frame_4, text="      ",fg='black',font=tk_tool.get_default_font(5)).pack(side="left")
    tkinter.Button(middle_frame_4,text=' 确定 ',font=tk_tool.get_default_font(12),bg='#4ae9d1',command=lambda:Trans_Test()).pack(side="left")
    middle_frame_4.pack()

    TextHashSave = None
    def Text_Syntax_Error_Tag(Input=OutputText.input_box, wait=True) :
        nonlocal TextHashSave
        if wait : top.after(500, Text_Syntax_Error_Tag)

        TextContent = Input.get("0.0", "end")[:-1]
        TextHash = hash(TextContent)
        if TextHash == TextHashSave : return None
        else : TextHashSave = TextHash

        a = Command_Str_Transfor(TextContent)
        Input.tag_remove("syntax_error", "0.0", "end")
        if not isinstance(a, str) : 
            if hasattr(a[1], "pos") : Input.tag_add("syntax_error", "1.%s"%a[1].pos[0], "1.end" )
            else : Input.tag_add("syntax_error", "1.0", "1.end" )
            Feedback.config(text="语法错误， 请修改", fg="#ff0000")
        else : Feedback.config(text="语法正确", fg="#00c63c")
    top.after(500, Text_Syntax_Error_Tag)

    def Trans_Test(Input=OutputText.input_box) :
        Text_Syntax_Error_Tag(wait=False)
        if Feedback.cget("text").__len__() > 4 :
            tkinter.messagebox.showerror("Error", "语法错误，无法转换")
            return None
        TextContent = Input.get("0.0", "end")[:-1]
        c = Command_Str_Transfor(TextContent)
        if Type == "bdx" :
            if code.operation_code != 0x29 : code.command = c
            else : code.nbt['Command'].value = c
        else : code[pos] = c
        Button1.config(text="正确", state="disabled")
        Error_Pointer[-1] = True
        top.destroy()

    def Pass() :
        Button1.config(text="忽略", fg="#ff7f27")
        Error_Pointer[-1] = True
        top.destroy()


def ReTrans_File() :
    for path, (obj, Error_list) in Error_File_Save.items() :
        for i in Error_list :
            if i[-1] : continue
            tkinter.messagebox.showerror("Error", "还有命令错误未修改\n请重新检查")
            return None
    for path, (obj, Error_list) in Error_File_Save.items() :
        if path[-4:] == ".bdx" : obj.save_as(path.replace("input", "output", 1)) ; obj.close()
        else : file_IO.write_a_file(path.replace("input", "output", 1), "\n".join(obj))
    tkinter.messagebox.showinfo("Info", "再次转换已完成")
    tkinter_component["error_frame"].pack_forget()
    tkinter_component["trans_frame"].pack()

#execute as @s[r=2,hasitem={item=aaa,data=1}] at @s positioned ~ 2 ~4 if block ^ ^ ^ minecraft:bedrock["infiniburn_bit":false] run setblock ~ ~ ~ minecraft:bedrock["infiniburn_bit":true]
