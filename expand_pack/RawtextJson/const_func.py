import tkinter,re
from tkinter.constants import *
import const_obj


def Text_get_content(text_obj:tkinter.Text) : 
    """将Text内容对象进行序列化"""
    button_list = text_obj.winfo_children()
    button_content = text_obj.dump("0.0", END, window=True)
    start = "1.0" ; result_list = []
    button_list_text = [str(i) for i in button_list]
    button_list = [button_list[button_list_text.index(i[1])] for i in button_content]

    for i in range(len(button_content)) :
        get_text = text_obj.get(start,button_content[i][2])
        if get_text != "" : result_list.append(get_text)
        result_list.append(button_list[i].rawtext_conpoment)
        start = button_content[i][2]
    get_text = text_obj.get(start,END)[:-1]
    if get_text != "" : result_list.append(get_text)

    return result_list

def content_to_component(input_text:tkinter.Text, main_win, content_list:list) : 
    """序列化"""
    for i in content_list :
        if isinstance(i,type("")) : input_text.insert(END,i)
        elif isinstance(i,dict) : 
            inner_button = const_obj.Text_Inner_Button(input_text, main_win, i['type'], i)
            input_text.window_create(INSERT, window=inner_button)



def find_return_str(str1 : str) :
    l = list(re.finditer("[\\\\]+n",str1))
    l.reverse()
    return l

def replace_str(base:str, start:int, end:int, replace:str) -> str:
    return "".join([ base[:start] , replace , base[end:] ])



def change_to_text(rawtext_comp:str) :
    return {"text":rawtext_comp}

def change_to_score(rawtext_comp:dict) :
    return {"score" : {"name": rawtext_comp['name'], "objective": rawtext_comp['scoreboard']}}

def change_to_selector(rawtext_comp:dict) :
    return {"selector" : rawtext_comp['name']}

def change_to_translate(rawtext_comp:dict) :
    #print("rawtext_comp：",rawtext_comp)
    return {"translate":rawtext_comp['text'], "with":translate_result(rawtext_comp['json_list'])}

def translate_result(rawtext_list:list) -> dict:
    lines_all = [[]]
    for rawtext_comp in rawtext_list :
        if not isinstance(rawtext_comp,str) : lines_all[-1].append(rawtext_comp) ; continue
        if rawtext_comp.count("\n") == 0 : lines_all[-1].append(rawtext_comp) ; continue
        split_text = rawtext_comp.split("\n")
        for index,str_line in enumerate(split_text) :
            if index > 0 : lines_all.append([])
            if str_line == "" : continue
            list_1 = find_return_str(str_line)
            mid_str1 = str_line
            for iter1 in list_1 :
                count1 = iter1.group().count("\\")
                if count1 == 1 : mid_str1 = replace_str(mid_str1 , iter1.start() , iter1.end() , "\n")
                elif count1 > 1 : mid_str1 = replace_str(mid_str1 , iter1.start() , iter1.end() , "\\" * (count1 - 1) + "n")
            lines_all[-1].append(mid_str1)
    #print(lines_all)

    base_json = {"rawtext":[]} ; base_translate = {"translate":"", "with":{"rawtext":[]}}
    for lines, lines_comp in enumerate(lines_all) :
        if len(lines_comp) == 0 : base_json['rawtext'].append(change_to_text("")) ; continue
        for rawtext_comp in lines_comp :
            if len(lines_comp) == 1 :
                if isinstance(rawtext_comp, str) : base_json['rawtext'].append(change_to_text(rawtext_comp))
                if isinstance(rawtext_comp, dict) :
                    if rawtext_comp['type'] == 'score' : base_json['rawtext'].append(change_to_score(rawtext_comp))
                    elif rawtext_comp['type'] == 'selector' : base_json['rawtext'].append(change_to_selector(rawtext_comp))
                    elif rawtext_comp['type'] == 'translate' : base_json['rawtext'].append(change_to_translate(rawtext_comp))
            else :
                if isinstance(rawtext_comp, str) : base_translate['translate'] += rawtext_comp
                if isinstance(rawtext_comp, dict) :
                    base_translate['translate'] += '%%s'
                    m1 = {"translate" : "%%s", "with" : {"rawtext":[{"text":""}]}}
                    if rawtext_comp['type'] == 'score' : m1['with']['rawtext'].insert(0,change_to_score(rawtext_comp))
                    elif rawtext_comp['type'] == 'selector' : m1['with']['rawtext'].insert(0,change_to_selector(rawtext_comp))
                    elif rawtext_comp['type'] == 'translate' : m1['with']['rawtext'].insert(0,change_to_translate(rawtext_comp))
                    base_translate['with']['rawtext'].append(m1)
        if len(lines_comp) > 1 : 
            base_json['rawtext'].append(base_translate)
            base_translate = {"translate" : "", "with" : {"rawtext":[]}}
    
    return base_json



