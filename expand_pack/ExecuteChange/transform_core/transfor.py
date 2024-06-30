from typing import Dict,Union,List,Tuple,Literal
from main_source.bedrock_edition.command_class.parser import BaseMatch
from . import TOKEN
import re,os,json,traceback


class CompileError(BaseMatch.Command_Match_Exception) : pass
BLOCK_STATE_FILE_PATH = os.path.join("main_source", "update_source", "import_files", "block_state")
BLOCK_STATE = json.load(open(BLOCK_STATE_FILE_PATH,"r",encoding="utf-8"))


def Quotation_String_transfor(s:str) -> str :
    if s[0] != "\"" or s[-1] != "\"" : return s
    s = s[1:len(s)-1]
    s_list = [] ; index = 0
    while index < (len(s) - 1) :
        if s[index] != "\\" :  s_list.append( s[index] )
        else :
            if s[index+1] == "\\" : s_list.append( "\n" )
            elif s[index+1] == "\"" : s_list.append( "\"" )
        index += 1
    return "".join(s_list)

def Block_ID_transfor(s:str) -> str :
    a = s.split(":",1)
    if len(a) == 1 : return "minecraft:%s" % a[0]
    else : return s


def find_block_state(Syntax_Equal:bool, block_id:str, block_data:int) -> str :
    if block_id not in BLOCK_STATE or block_data <= -1 : return "[]"
    if bin(block_data) not in BLOCK_STATE[block_id] : query_block_state = BLOCK_STATE[block_id]["default"]
    else : query_block_state = BLOCK_STATE[block_id][bin(block_data)]
    if not Syntax_Equal : return_block_state_str = json.dumps(query_block_state,separators=(',', ':'),ensure_ascii=False)
    else : return_block_state_str = json.dumps(query_block_state,separators=(',', '='),ensure_ascii=False)
    return "[%s]" % return_block_state_str[1:len(return_block_state_str)-1]


def Selector_Transformer(token_list:TOKEN, index:int) -> Tuple[str,int] :
    selector_var_all = ("x","y","z","c","dx","dy","dz","rx","ry","rxm","rym","l","lm","r","rm","scores","hasitem","haspermission",
                        "tag","name","family","type","m")
    selector_var_count = { i:0 for i in selector_var_all  }
    selector_save = {"distance":[0,100000000], "level":[0,10000000], "limit":200000, "sort":"nearest", "name":[[],[]], 
                     "type":[[],[]], "m":[[],[]] }
    is_player_check = False ; is_npc_check = False
    
    selector_type = token_list[index]["type"]
    selector = token_list[index]["token"].group()

    if selector_type in ("Player_Name", "Objective_Name") : return (selector, index + 1)
    elif selector_type == "Selector" : 
        if selector in ("@p","@r","@s") : selector_save["limit"] = 1
        if selector in ("@p","@a") : selector_save["type"][0].append("minecraft:player")
        if selector in ("@p","@a") : is_player_check = True
        if selector == "@r" : selector_save["sort"] = "random"
    
    index += 1 ; tarnsfor_list = [selector] ; tarnsfor_start_index = index
    if token_list[index]["type"] != "Start_Selector_Argument" : return (selector, index)
    while 1 :
        index += 1
        if token_list[index]["type"] == "End_Selector_Argument" : break
        if token_list[index]["type"] == "Next_Selector_Argument" : continue
        if token_list[index]["type"] == "Selector_Argument" : 
            selector_argument = token_list[index]["token"].group()

            selector_var_count[ selector_argument ] += 1
            for i in ("x","y","z","c","dx","dy","dz","rx","ry","rxm","rym","l","lm","r","rm","scores","hasitem","haspermission") :
                if selector_var_count[i] > 1 :
                    raise CompileError("重复的选择器 %s 参数" % i,pos=(token_list[index]["token"].start(),token_list[index]["token"].end()))
            
            if selector_argument in ("x","y","z","dx","dy","dz","rx","ry","rxm","rym") : index += 2
            elif selector_argument in ("r","rm") :
                index += 2
                arg_value = float(token_list[index]["token"].group())
                if arg_value < 0 : raise CompileError("距离参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))
                selector_save["distance"][int(selector_argument == "r")] = arg_value
            elif selector_argument in ("l","lm") :
                index += 2
                arg_value = float(token_list[index]["token"].group())
                if arg_value < 0 : raise CompileError("等级参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))
                selector_save["level"][int(selector_argument == "l")] = arg_value
            elif selector_argument == "c" :
                index += 2
                arg_value = int(token_list[index]["token"].group())
                if selector_save["sort"] == "random" and arg_value < 0 :
                    raise CompileError("随机选择器的数量参数不能为负数",pos=(token_list[index-2]["token"].start(),token_list[index]["token"].end()))
            elif selector_argument in ("tag","name","family","type","m") :
                index += 2 ; append_index = None
                if token_list[index]["type"] != "Not" : append_index = 0
                else : 
                    append_index = 1 ; index += 1
                arg_value = Quotation_String_transfor(token_list[index]["token"].group())
                if selector_argument in selector_save : selector_save[selector_argument][append_index].append(arg_value)
            elif selector_argument == "scores" :
                index += 2
                if token_list[index]["type"] == "Start_Score_Argument" :
                    while token_list[index]["type"] != "End_Score_Argument" : index += 1
            elif selector_argument == "haspermission" :
                index += 2
                if token_list[index]["type"] == "Start_Permission_Argument" :
                    while token_list[index]["type"] != "End_Permission_Argument" : index += 1
            elif selector_argument == "hasitem" :
                index += 2
                if token_list[index]["type"] == "Start_Item_Argument" :
                    while token_list[index]["type"] != "End_Item_Argument" : index += 1
                elif token_list[index]["type"] == "Start_Item_Condition" :
                    while token_list[index]["type"] != "End_Item_Condition" : index += 1


    if is_player_check and len(selector_save["type"][0]) > 1 : raise CompileError("选择器 %s 只能为玩家类型" % selector_argument, pos=(tarnsfor_start_index, index))
    if selector_save["distance"][0] > selector_save["distance"][1] : raise CompileError("距离参数上限不能小于下限", pos=(tarnsfor_start_index, index))
    if selector_save["level"][0] > selector_save["level"][1] : raise CompileError("等级参数上限不能小于下限", pos=(tarnsfor_start_index, index))
    if len(selector_save["name"][0]) > 1 : raise CompileError("选择器参数 name 具有重复指定的正选条件", pos=(tarnsfor_start_index, index))
    if len(selector_save["name"][0]) == 1 and len(selector_save["name"][1]) > 0 : raise CompileError("选择器参数 name 同时存在正反选条件", pos=(tarnsfor_start_index, index))
    if len(selector_save["type"][0]) > 1 : raise CompileError("选择器参数 type 具有重复指定的正选条件", pos=(tarnsfor_start_index, index))
    if len(selector_save["type"][0]) == 1 and len(selector_save["type"][1]) > 0 : raise CompileError("选择器参数 type 同时存在正反选条件", pos=(tarnsfor_start_index, index))
    if len(selector_save["m"][0]) > 1 : raise CompileError("选择器参数 m 具有重复指定的正选条件", pos=(tarnsfor_start_index, index))
    if len(selector_save["m"][0]) == 1 and len(selector_save["m"][1]) > 0 : raise CompileError("选择器参数 m 同时存在正反选条件", pos=(tarnsfor_start_index, index))

    while tarnsfor_start_index <= index :
        tarnsfor_list.append( token_list[tarnsfor_start_index]["token"].group() )
        tarnsfor_start_index += 1
        
    return ("".join(tarnsfor_list), index + 1)

def BlockState_Transformer(Syntax_Equal:bool, block_id:str, token_list:TOKEN, index:int) -> Tuple[str,int] :
    block_id_state = {} if (block_id not in BLOCK_STATE) else BLOCK_STATE[block_id]
    block_id_state : Dict[Literal["default","support_value"],Union[Dict,Dict]]
    block_state_token : List[str] = []
    if token_list[index]["type"] != "Start_BlockState_Argument" : return ("", index)
    index += 1 ; block_state_token.append("{")

    while 1 :
        if token_list[index]["type"] in ("BlockState","Equal","Value","Next_BlockState_Argument") : 
            str1 = token_list[index]["token"].group()
            if token_list[index]["type"] == "Equal" and str1 == "=" : str1 = ":"
            block_state_token.append( str1 )
        elif token_list[index]["type"] == "End_BlockState_Argument" : 
            block_state_token.append( "}" ) ; index += 1 ; break
        index += 1

    input_block_state = json.loads("".join(block_state_token))
    for state in input_block_state :
        if state not in block_id_state["support_value"] : raise CompileError("方块 %s 不存在 %s 状态" % (block_id,state))
        if input_block_state[state] not in block_id_state["support_value"][state] : 
            raise CompileError("方块状态 %s 不存在值 %s" % (state,input_block_state[state]))

    if not Syntax_Equal : a = json.dumps(input_block_state, separators=(',', ':'), ensure_ascii=False)
    else : a = json.dumps(input_block_state, separators=(',', '='), ensure_ascii=False)
    return ("[%s]" % "".join(a[1:len(a)-1]), index)



def Pass_Command_execute_1_19_0(token_list:TOKEN) :
    index = 1
    while 1 :
        transfor_token1, index = Selector_Transformer(token_list,index)
        index += 3

        if token_list[index]["type"] == "Command" and token_list[index]["token"].group() == "execute" : 
           index += 1 ; continue
        elif token_list[index]["type"] == "Block_Test" :
            index += 6
            if token_list[index]["type"] == "Command" and token_list[index]["token"].group() == "execute" : 
                index += 1 ; continue
        break

    return index

def Pass_Command_execute_1_19_50(token_list:TOKEN) :
    index = 1
    while index < len(token_list) :
        if token_list[index]["token"].group() in ("as","at") : 
            transfor_token1, index = Selector_Transformer(token_list,index + 1)
        elif token_list[index]["token"].group() in ("align", "anchored", "in") : 
            index += 2
        elif token_list[index]["token"].group() in ("facing","positioned","rotated") : 
            index += 1
            if token_list[index]["token"].group() in ("entity", "as") : 
                transfor_token1,index = Selector_Transformer(token_list,index+1)
            else : 
                go_to = 2 if token_list[index-1]["token"].group() == "rotated" else 3
                index += go_to
        elif token_list[index]["token"].group() in ("if","unless") : 
            index += 1
            if token_list[index]["token"].group() == "block" :
                index += 4 ; block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
                if index < len(token_list) and token_list[index]["type"] == "Start_BlockState_Argument" :
                    block_state_trans,index = BlockState_Transformer(False, block_id, token_list, index)
                elif index < len(token_list) and token_list[index]["type"] == "Block_Data" :
                    block_data = int(token_list[index]["token"].group()) ; index += 1
            elif token_list[index]["token"].group() == "blocks" :index += 11
            elif token_list[index]["token"].group() == "entity" :
                transfor_token1, index = Selector_Transformer(token_list,index + 1)
            elif token_list[index]["token"].group() == "score" :
                transfor_token1, index = Selector_Transformer(token_list,index + 1)
                index += 2
                if token_list[index-1]["token"].group() == "matches" :
                    middle1 = []
                    if token_list[index]["type"] == "Not" : middle1.append("!") ; index += 1
                    if index < len(token_list) and token_list[index]["type"] == "Range_Min" : 
                        middle1.append(token_list[index]["token"].group()) ; index += 1
                    if index < len(token_list) and token_list[index]["type"] == "Range_Sign" : 
                        middle1.append(token_list[index]["token"].group()) ; index += 1
                    if index < len(token_list) and token_list[index]["type"] == "Range_Max" : 
                        middle1.append(token_list[index]["token"].group()) ; index += 1
                else :
                    transfor_token1, index = Selector_Transformer(token_list,index)
                    index += 1
        elif token_list[index]["token"].group() == "run" : 
            index += 1
            if token_list[index]["type"] == "Command" and token_list[index]["token"].group() == "execute" : 
                index += 1 ; continue
            break

    #print(transfor_list)

    return index

