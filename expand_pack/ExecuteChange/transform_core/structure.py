from typing import Union,Tuple
import traceback
from . import TOKEN

def Command_structure_Transformer(token_list:TOKEN) :
    transfor_list = ["structure"] ; index = 1 ; token_len = len(token_list)
    while 1 :
        if token_list[index]['token'].group() in {"save", "delete"} :
            for i in token_list[index:] : transfor_list.append(i['token'].group())
        else :
            for i in token_list[index:index+7] : transfor_list.append(i['token'].group())
            index += 7
            if index >= token_len : break

            if token_list[index]['type'] == "Animation_Mode" : end =  4
            else : end = 2
            for i in token_list[index:index+end] : transfor_list.append(i['token'].group())
            index += end
            if index >= token_len : break

            transfor_list.append("false")
            for i in token_list[index:index+2] : transfor_list.append(i['token'].group())
        break

    return " ".join(transfor_list)


def Start_Transformer(token_list:TOKEN) -> Union[str,Tuple[str,Exception]] :
    try : return Command_structure_Transformer(token_list)
    except Exception as e :
        traceback.print_exc()
        if hasattr(e,"pos") : s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
        else : s = e.args[0]
        return (s,e)