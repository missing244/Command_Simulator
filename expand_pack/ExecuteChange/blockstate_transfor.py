from typing import Dict,Union,List,Tuple,Literal
from execute_transfor import Selector_Transformer,BlockState_Transformer,Command_fill_Transformer
from execute_transfor import Command_setblock_Transformer,Command_testforblock_Transformer,Command_clone_Transformer
from execute_transfor import Block_ID_transfor,find_block_state
import re,traceback



def Command_execute_Transformer(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    transfor_list = ["execute"] ; index = 1
    while index < len(token_list) :
        if token_list[index]["token"].group() in ("as","at") : 
            transfor_list.append(token_list[index]["token"].group())
            transfor_token1, index = Selector_Transformer(token_list,index + 1)
            transfor_list.append(transfor_token1)
        elif token_list[index]["token"].group() in ("align", "anchored", "in") : 
            transfor_list.append(token_list[index]["token"].group())
            transfor_list.append(token_list[index+1]["token"].group())
            index += 2
        elif token_list[index]["token"].group() in ("facing","positioned","rotated") : 
            index += 1
            if token_list[index]["token"].group() in ("entity", "as") : 
                transfor_token1,index = Selector_Transformer(token_list,index+1)
                transfor_list.append("facing entity %s" % transfor_token1)
            else : 
                go_to = 2 if token_list[index-1]["token"].group() == "rotated" else 3
                transfor_list.append("facing %s" % " ".join([token_list[index+i]["token"].group() for i in range(go_to)]))
                index += go_to
        elif token_list[index]["token"].group() in ("if","unless") : 
            transfor_list.append(token_list[index]["token"].group()) ; index += 1
            transfor_list.append(token_list[index]["token"].group())
            if token_list[index]["token"].group() == "block" :
                for i in range(1,4,1) : transfor_list.append(token_list[index+i]["token"].group())
                index += 4 ; block_id = Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
                if token_list[index]["type"] == "Start_BlockState_Argument" :
                    block_state_trans,index = BlockState_Transformer(block_id, token_list, index)
                    transfor_list.append( "%s%s" % (block_id, block_state_trans ))
                elif token_list[index]["type"] == "Block_Data" :
                    block_data = int(token_list[index]["token"].group()) ; index += 1
                    transfor_list.append( "%s%s" % (block_id, find_block_state(block_id,block_data)) )
                else : transfor_list.append( block_id )
            if token_list[index]["token"].group() == "blocks" :
                for i in range(1,11,1) : transfor_list.append(token_list[index+i]["token"].group())
                index += 11
            if token_list[index]["token"].group() == "entity" :
                transfor_token1, index = Selector_Transformer(token_list,index + 1)
                transfor_list.append(transfor_token1)
            if token_list[index]["token"].group() == "score" :
                transfor_token1, index = Selector_Transformer(token_list,index + 1)
                transfor_list.append(transfor_token1)
                transfor_list.append(token_list[index]["token"].group()) ; index += 1
                transfor_list.append(token_list[index]["token"].group()) ; index += 1
                if token_list[index-1]["token"].group() == "matches" :
                    middle1 = []
                    if token_list[index]["type"] == "Not" : middle1.append("!") ; index += 1
                    if index < len(token_list) and token_list[index]["type"] == "Range_Min" : 
                        middle1.append(token_list[index]["token"].group()) ; index += 1
                    if index < len(token_list) and token_list[index]["type"] == "Range_Sign" : 
                        middle1.append(token_list[index]["token"].group()) ; index += 1
                    if index < len(token_list) and token_list[index]["type"] == "Range_Max" : 
                        middle1.append(token_list[index]["token"].group()) ; index += 1
                    transfor_list.append("".join(middle1))
                else :
                    transfor_token1, index = Selector_Transformer(token_list,index)
                    transfor_list.append(transfor_token1)
                    transfor_list.append(token_list[index]["token"].group()) ; index += 1
        elif token_list[index]["token"].group() == "run" : 
            index += 1
            if token_list[index]["type"] == "Command" and token_list[index]["token"].group() == "execute" : 
                index += 1 ; continue
            transfor_list.append("run")
            break

    #print(transfor_list)
    if index < len(token_list) and token_list[index]["type"] == "Any_Command" : transfor_list.append( token_list[index]["token"].group() )
    elif index < len(token_list) : transfor_list.append( Command_to_Transformer[token_list[index]["token"].group()]( token_list[index:] ) )

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
