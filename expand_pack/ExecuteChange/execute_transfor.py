from typing import Dict,Union,List,Tuple,Literal
from main_source.bedrock_edition.command_class.parser import BaseMatch
import re,os,json,traceback

class CompileError(BaseMatch.Command_Match_Exception) : pass

BLOCK_STATE_FILE_PATH = os.path.join("main_source", "update_source", "import_files", "block_state")
BLOCK_STATE = json.load(open(BLOCK_STATE_FILE_PATH,"r",encoding="utf-8"))
VERSION = (1,19,50)


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


def find_block_state(block_id:str,block_data:int) -> str :
    if block_id not in BLOCK_STATE or block_data <= -1 : return "[]"
    if bin(block_data) not in BLOCK_STATE[block_id] : query_block_state = BLOCK_STATE[block_id]["default"]
    else : query_block_state = BLOCK_STATE[block_id][bin(block_data)]
    if VERSION == (1,19,50) : return_block_state_str = json.dumps(query_block_state,separators=(',', ':'),ensure_ascii=False)
    else : return_block_state_str = json.dumps(query_block_state,separators=(',', '='),ensure_ascii=False)
    return "[%s]" % return_block_state_str[1:len(return_block_state_str)-1]


def Selector_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]],index:int) -> Tuple[str,int] :
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
        if selector in ("@p","@a","@r") : selector_save["type"][0].append("minecraft:player")
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


    if is_player_check and len(selector_save["type"][0]) > 1 : raise CompileError("选择器 %s 只能为玩家类型" % selector_argument)
    if selector_save["distance"][0] > selector_save["distance"][1] : raise CompileError("距离参数上限不能小于下限")
    if selector_save["level"][0] > selector_save["level"][1] : raise CompileError("等级参数上限不能小于下限")
    if len(selector_save["name"][0]) > 1 : raise CompileError("选择器参数 name 具有重复指定的正选条件")
    if len(selector_save["name"][0]) == 1 and len(selector_save["name"][1]) > 0 : raise CompileError("选择器参数 name 同时存在正反选条件")
    if len(selector_save["type"][0]) > 1 : raise CompileError("选择器参数 type 具有重复指定的正选条件")
    if len(selector_save["type"][0]) == 1 and len(selector_save["type"][1]) > 0 : raise CompileError("选择器参数 type 同时存在正反选条件")
    if len(selector_save["m"][0]) > 1 : raise CompileError("选择器参数 m 具有重复指定的正选条件")
    if len(selector_save["m"][0]) == 1 and len(selector_save["m"][1]) > 0 : raise CompileError("选择器参数 m 同时存在正反选条件")

    while tarnsfor_start_index <= index :
        tarnsfor_list.append( token_list[tarnsfor_start_index]["token"].group() )
        tarnsfor_start_index += 1
        
    return ("".join(tarnsfor_list), index + 1)

def BlockState_Transformer(block_id:str,token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]],index:int) -> Tuple[str,int] :
    block_id_state = {} if (block_id not in BLOCK_STATE) else BLOCK_STATE[block_id]
    block_id_state : Dict[Literal["default","support_value"],Union[Dict,Dict]]
    block_state_token : List[str] = []
    if token_list[index]["type"] != "Start_BlockState_Argument" : return ("", index)
    index += 1 ; block_state_token.append("{")

    while 1 :
        if token_list[index]["type"] in ("BlockState","Equal","Value","Next_BlockState_Argument") : 
            block_state_token.append( token_list[index]["token"].group() )
        elif token_list[index]["type"] == "End_BlockState_Argument" : 
            block_state_token.append( "}" ) ; index += 1 ; break
        index += 1

    input_block_state = json.loads("".join(block_state_token))
    for state in input_block_state :
        if state not in block_id_state["support_value"] : raise CompileError("方块 %s 不存在 %s 状态" % (block_id,state))
        if input_block_state[state] not in block_id_state["support_value"][state] : 
            raise CompileError("方块状态 %s 不存在值 %s" % (state,input_block_state[state]))

    if VERSION == (1,19,50) : a = json.dumps(input_block_state, separators=(',', ':'), ensure_ascii=False)
    else : a = json.dumps(input_block_state, separators=(',', '='), ensure_ascii=False)
    return ("[%s]" % "".join(a[1:len(a)-1]), index)


def Command_execute_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    transfor_list = ["execute"] ; index = 1
    while 1 :
        transfor_token1,index = Selector_Transformer(token_list,index)
        transfor_list.append("as %s at @s" % transfor_token1)

        save1 = [token_list[index+i]["token"].group() for i in range(3)]
        if not all([i in "^~" for i in save1]) : transfor_list.append("positioned") ; transfor_list.extend(save1)
        index += 3

        if token_list[index]["type"] == "Command" and token_list[index]["token"].group() == "execute" : 
           index += 1 ; continue
        elif token_list[index]["type"] == "Block_Test" :
            transfor_list.append("if block") ; index += 1
            for i in range(3) : 
                transfor_list.append(token_list[index]["token"].group()) ; index += 1
            block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, find_block_state(block_id,block_data)) )
            if token_list[index]["type"] == "Command" and token_list[index]["token"].group() == "execute" : 
                index += 1 ; continue
        break

    transfor_list.append( "run" )
    #print(transfor_list)
    if token_list[index]["type"] == "Any_Command" : transfor_list.append( token_list[index]["token"].group() )
    else : transfor_list.append( Command_to_Transformer[token_list[index]["token"].group()]( token_list[index:] ) )

    return " ".join(transfor_list)

def Command_fill_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    transfor_list = ["fill"] ; index = 1 ; token_len = len(token_list)
    for i in range(6) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
    if index < token_len : 
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = BlockState_Transformer(block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, find_block_state(block_id,block_data)) )
    else : transfor_list.append( block_id )
    
    while 1 :
        if index >= token_len : break
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

        if index >= token_len : break
        block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
        if index >= token_len : break
        else : transfor_list.append( block_id )
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = BlockState_Transformer(block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, find_block_state(block_id,block_data)) )
        break

    return " ".join(transfor_list)

def Command_setblock_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    transfor_list = ["setblock"] ; index = 1 ; token_len = len(token_list)
    for i in range(3) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
    if index < token_len : 
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = BlockState_Transformer(block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, find_block_state(block_id,block_data)) )
    else : transfor_list.append( block_id )
        
    if index < token_len : 
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

    return " ".join(transfor_list)

def Command_testforblock_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    transfor_list = ["testforblock"] ; index = 1 ; token_len = len(token_list)
    for i in range(3) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
    if index < token_len : 
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = BlockState_Transformer(block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, find_block_state(block_id,block_data)) )
    else : transfor_list.append( block_id )

    return " ".join(transfor_list)

def Command_clone_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    transfor_list = ["clone"] ; index = 1 ; token_len = len(token_list)
    for i in range(9) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    while 1 :
        if index >= token_len : break
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

        if index >= token_len : break
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

        block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
        if index < token_len : 
            if token_list[index]["type"] == "Start_BlockState_Argument" :
                block_state_trans,index = BlockState_Transformer(block_id, token_list, index)
                transfor_list.append( "%s%s" % (block_id, block_state_trans ))
            else :
                block_data = int(token_list[index]["token"].group()) ; index += 1
                transfor_list.append( "%s%s" % (block_id, find_block_state(block_id,block_data)) )
        else : transfor_list.append( block_id )

        break

    return " ".join(transfor_list)




Command_to_Transformer = {
    "execute" : Command_execute_Transformer, 
    "fill" : Command_fill_Transformer, 
    "setblock" : Command_setblock_Transformer, 
    "testforblock" : Command_testforblock_Transformer, 
    "clone" : Command_clone_Transformer,
}

def Start_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) -> Union[str,Tuple[str,Exception]] :
    if token_list[0]["type"] == "Any_Command" : return token_list[0]["token"].group()
    command_name = token_list[0]["token"].group()

    try : return Command_to_Transformer[command_name](token_list)
    except Exception as e :
        traceback.print_exc()
        if hasattr(e,"pos") : s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
        else : s = e.args[0]
        return (s,e)




def Set_Version(is_new:bool) :
    global VERSION
    if is_new : VERSION = (1,20,0)
    else : VERSION = (1,19,50)