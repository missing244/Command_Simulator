from typing import Union,Tuple
import traceback
from . import TOKEN,transfor



def Command_fill_Transformer(BlockSyntax:bool, token_list:TOKEN) :
    transfor_list = ["fill"] ; index = 1 ; token_len = len(token_list)
    for i in range(6) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    block_id = transfor.Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
    if index < token_len : 
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = transfor.BlockState_Transformer(BlockSyntax, block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, transfor.find_block_state(BlockSyntax, block_id,block_data)) )
    else : transfor_list.append( block_id )
    
    while 1 :
        if index >= token_len : break
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

        if index >= token_len : break
        block_id = transfor.Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
        if index >= token_len : break
        else : transfor_list.append( block_id )
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = transfor.BlockState_Transformer(BlockSyntax, block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, transfor.find_block_state(BlockSyntax, block_id, block_data)) )
        break

    return " ".join(transfor_list)

def Command_setblock_Transformer(BlockSyntax:bool, token_list:TOKEN) :
    transfor_list = ["setblock"] ; index = 1 ; token_len = len(token_list)
    for i in range(3) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    block_id = transfor.Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
    if index < token_len : 
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = transfor.BlockState_Transformer(BlockSyntax, block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, transfor.find_block_state(BlockSyntax, block_id,block_data)) )
    else : transfor_list.append( block_id )
        
    if index < token_len : 
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

    return " ".join(transfor_list)

def Command_testforblock_Transformer(BlockSyntax:bool, token_list:TOKEN) :
    transfor_list = ["testforblock"] ; index = 1 ; token_len = len(token_list)
    for i in range(3) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    block_id = transfor.Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
    if index < token_len : 
        if token_list[index]["type"] == "Start_BlockState_Argument" :
            block_state_trans,index = transfor.BlockState_Transformer(BlockSyntax, block_id, token_list, index)
            transfor_list.append( "%s%s" % (block_id, block_state_trans ))
        else :
            block_data = int(token_list[index]["token"].group()) ; index += 1
            transfor_list.append( "%s%s" % (block_id, transfor.find_block_state(BlockSyntax, block_id, block_data)) )
    else : transfor_list.append( block_id )

    return " ".join(transfor_list)

def Command_clone_Transformer(BlockSyntax:bool, token_list:TOKEN) :
    transfor_list = ["clone"] ; index = 1 ; token_len = len(token_list)
    for i in range(9) : 
        transfor_list.append(token_list[index]["token"].group()) ; index += 1

    while 1 :
        if index >= token_len : break
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

        if index >= token_len : break
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1

        if index >= token_len : break
        block_id = transfor.Block_ID_transfor(token_list[index]["token"].group()) ; index += 1
        if index < token_len : 
            if token_list[index]["type"] == "Start_BlockState_Argument" :
                block_state_trans,index = transfor.BlockState_Transformer(BlockSyntax, block_id, token_list, index)
                transfor_list.append( "%s%s" % (block_id, block_state_trans ))
            else :
                block_data = int(token_list[index]["token"].group()) ; index += 1
                transfor_list.append( "%s%s" % (block_id, transfor.find_block_state(BlockSyntax, block_id, block_data)) )
        else : transfor_list.append( block_id )

        break

    return " ".join(transfor_list)




Command_to_Transformer = {
    "fill" : Command_fill_Transformer, 
    "setblock" : Command_setblock_Transformer, 
    "testforblock" : Command_testforblock_Transformer, 
    "clone" : Command_clone_Transformer,
}

def Start_Transformer(BlockSyntax:bool, token_list:TOKEN) -> Union[str,Tuple[str,Exception]] :
    command_name = token_list[0]["token"].group()

    try : return Command_to_Transformer[command_name](BlockSyntax, token_list)
    except Exception as e :
        traceback.print_exc()
        if hasattr(e,"pos") : s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
        else : s = e.args[0]
        return (s,e)


