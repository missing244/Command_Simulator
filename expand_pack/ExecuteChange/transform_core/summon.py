from typing import Union,Tuple
import traceback
from . import TOKEN


def Command_summon_Transformer(token_list:TOKEN) :
    transfor_list = ["summon"] ; index = 1 ; token_len = len(token_list)

    while 1 :
        transfor_list.append( token_list[index]["token"].group() ) ; index += 1
        if index >= token_len : break

        if token_list[index]["type"] == "Entity_Name" :
            transfor_list.append( token_list[index]["token"].group() ) ; index += 1
            if index >= token_len : break

            for i in range(3) : transfor_list.append( token_list[index+i]["token"].group() )
            index += 3
            if index >= token_len : break
        else :
            for i in range(3) : transfor_list.append( token_list[index+i]["token"].group() )
            index += 3
            if index >= token_len : break
            
            transfor_list.append( "~ ~" )
            transfor_list.append( token_list[index]["token"].group() ) ; index += 1
            if index >= token_len : break
            
            transfor_list.append( token_list[index]["token"].group() ) ; index += 1
            if index >= token_len : break
        
        break
    
    return " ".join(transfor_list)




def Start_Transformer(token_list:TOKEN) -> Union[str,Tuple[str,Exception]] :
    try : return Command_summon_Transformer(token_list)
    except Exception as e :
        traceback.print_exc()
        if hasattr(e,"pos") : s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
        else : s = e.args[0]
        return (s,e)