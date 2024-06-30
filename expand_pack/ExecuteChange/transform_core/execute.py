from typing import Union,Tuple
import traceback
from . import TOKEN,transfor,Command_Str_Transfor


def Command_execute_Transformer_1_19_0(BlockSyntax:bool, token_list:TOKEN) :
    transfor_list = ["execute"] ; index = 1
    while 1 :
        transfor_token1,index = transfor.Selector_Transformer(token_list,index)
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
            block_id = transfor.Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, transfor.find_block_state(BlockSyntax, block_id, block_data)) )
            if token_list[index]["type"] == "Command" and token_list[index]["token"].group() == "execute" : 
                index += 1 ; continue
        break

    transfor_list.append( "run" )
    if token_list[index]["type"] == "Any_Command" : transfor_list.append( token_list[index]["token"].group() )
    else : 
        aaaaa = Command_Str_Transfor( None, FastPath=token_list[index:] )
        if isinstance(aaaaa, tuple) : raise aaaaa[1]
        transfor_list.append( aaaaa )

    return " ".join(transfor_list)

def Command_execute_Transformer_1_19_50(BlockSyntax:bool, token_list:TOKEN) :
    transfor_list = ["execute"] ; index = 1
    while index < len(token_list) :
        if token_list[index]["token"].group() in ("as","at") : 
            transfor_list.append(token_list[index]["token"].group())
            transfor_token1, index = transfor.Selector_Transformer(token_list,index + 1)
            transfor_list.append(transfor_token1)
        elif token_list[index]["token"].group() in ("align", "anchored", "in") : 
            transfor_list.append(token_list[index]["token"].group())
            transfor_list.append(token_list[index+1]["token"].group())
            index += 2
        elif token_list[index]["token"].group() in ("facing","positioned","rotated") : 
            index += 1
            if token_list[index]["token"].group() in ("entity", "as") : 
                transfor_token1,index = transfor.Selector_Transformer(token_list,index+1)
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
                index += 4 ; block_id = transfor.Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
                if index < len(token_list) and token_list[index]["type"] == "Start_BlockState_Argument" :
                    block_state_trans,index = transfor.BlockState_Transformer(BlockSyntax, block_id, token_list, index)
                    transfor_list.append( "%s%s" % (block_id, block_state_trans ))
                elif index < len(token_list) and token_list[index]["type"] == "Block_Data" :
                    block_data = int(token_list[index]["token"].group()) ; index += 1
                    transfor_list.append( "%s%s" % (block_id, transfor.find_block_state(BlockSyntax, block_id, block_data)) )
                else : transfor_list.append( block_id )
            elif token_list[index]["token"].group() == "blocks" :
                for i in range(1,11,1) : transfor_list.append(token_list[index+i]["token"].group())
                index += 11
            elif token_list[index]["token"].group() == "entity" :
                transfor_token1, index = transfor.Selector_Transformer(token_list,index + 1)
                transfor_list.append(transfor_token1)
            elif token_list[index]["token"].group() == "score" :
                transfor_token1, index = transfor.Selector_Transformer(token_list,index + 1)
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
                    transfor_token1, index = transfor.Selector_Transformer(token_list,index)
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
    elif index < len(token_list) : 
        aaaaa = Command_Str_Transfor( None, FastPath=token_list[index:] )
        if isinstance(aaaaa, tuple) : raise aaaaa[1]
        transfor_list.append( aaaaa )

    return " ".join(transfor_list)



def Start_Transformer(BlockSyntax:bool, token_list:TOKEN, HightVersion:bool) -> Union[str,Tuple[str,Exception]] :
    try : return [Command_execute_Transformer_1_19_0, Command_execute_Transformer_1_19_50][HightVersion](BlockSyntax, token_list)
    except Exception as e :
        traceback.print_exc()
        if hasattr(e,"pos") : s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
        else : s = e.args[0]
        return (s,e)