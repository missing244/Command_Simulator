"""
func Json_Tree 用于给外部命令树注册命令分支使用\n
func json_tokenizer 用于解析json\n
"""

import re
from typing import Dict,Union,List,Tuple

from . import BaseMatch,SpecialMatch

class Not_Parser_Object(Exception) : pass
class Json_Error(BaseMatch.Command_Match_Exception) : pass

class Json_Start(BaseMatch.KeyWord) : pass
class List_Start(BaseMatch.KeyWord) : pass

class Json_String(BaseMatch.Match_Base) :
    def __init__(self, token_type: str, auto_complete:Dict[str,str]=None) -> None :
        super().__init__(token_type)
        self.re_match = re.compile(r'"([^"\\]|\\u[a-fA-F0-9]{4}|\\[^u])*"')
        self.auto_complete = auto_complete

    def _match_string(self,s:str,s_pointer:int) : 
        len_s = len(s)

        if s[s_pointer] != "\"" :
            raise SpecialMatch.Illegal_Match(">>%s<< 并不是有效的引号字符串" % s[s_pointer], pos=(s_pointer,s_pointer+1), word=s[s_pointer])

        _match = self.re_match.match(s,s_pointer)
        if not _match : raise SpecialMatch.Illegal_Match(">>%s<< 并不是有效的引号字符串" % s[s_pointer:len_s], pos=(s_pointer,len_s), word=s[s_pointer:len_s])

        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        if self.auto_complete == None : return {'"string"':""}
        else : return self.auto_complete.copy()




def creat_value_tree(*end_node) :
    Value = [
        Json_String("Value").add_leaves(*end_node),
        BaseMatch.Float("Value").add_leaves(*end_node),
        BaseMatch.KeyWord("Value","true","false","null").add_leaves(*end_node),
    ]
    return Value

Json = Json_Start("Json_Start","{")
Json_Key_And_Value = Json_String("Key")
Json_Key_And_Value.add_leaves(
    BaseMatch.KeyWord("To",":").add_leaves(
        List_Start("List_Start","[").add_leaves(
            BaseMatch.KeyWord("Json_End","}"),
            BaseMatch.KeyWord("Json_Next",",").add_leaves(Json_Key_And_Value)
        ),
        Json_Start("Json_Start","{").add_leaves(
            BaseMatch.KeyWord("Json_End","}"),
            BaseMatch.KeyWord("Json_Next",",").add_leaves(Json_Key_And_Value)
        ),
        *creat_value_tree(
            BaseMatch.KeyWord("Json_End","}"),
            BaseMatch.KeyWord("Json_Next",",").add_leaves(Json_Key_And_Value)
        )
    )
)
Json.add_leaves(Json_Key_And_Value, BaseMatch.KeyWord("Json_End","}"))

List = List_Start("List_Start","[")
List.add_leaves(
    List_Start("List_Start","["),
    Json_Start("Json_Start","{"),
    *creat_value_tree()
)
for i in List.tree_leaves :
    i.add_leaves(
        BaseMatch.KeyWord("List_End","]"),
        BaseMatch.KeyWord("List_Next",",").add_leaves(*List.tree_leaves)
    ),
List.add_leaves( BaseMatch.KeyWord("List_End","]") )

def Json_Tree(*end_node) :
    return Json_Start("Json_Start","{").add_leaves(*end_node)


class Json_Parser :

    parser_json_root = SpecialMatch.Command_Root().add_leaves(Json)
    parser_list_root = SpecialMatch.Command_Root().add_leaves(List)

    def __init__(self) -> None:
        self.white_space_match = re.compile("[\\u000a\\u0020\\u000d\\u0009]{0,}")
        self.no_match_error1 = re.compile("[^\\{\\},:\\[\\]\\u000a\\u0020\\u000d\\u0009]{1,}")
        self.no_match_error2 = re.compile(".{0,1}")

        self.recursion_count = 0

        self.command_str = ""
        self.read_pointers = 0

    def reset_parser_tree(self) :
        self.recursion_count = 0

    def _jump_space(self, s:str, s_pointer:int) :
        return self.white_space_match.match(s,s_pointer)

    def _parser(self, current_leaves:BaseMatch.Match_Base, Token_list:list) :
        self.recursion_count += 1
        while 1 :
            if not len(current_leaves.tree_leaves) : break

            is_not_successs = True
            for i in current_leaves.tree_leaves :
                if self.recursion_count > 512 : break
                try : a = i._match_string(self.command_str, self.read_pointers)
                except : continue
                else :
                    is_not_successs = False
                    current_leaves = i
                    if (isinstance(i, Json_Start) and Json != i) or (isinstance(i, List_Start) and List != i) : 
                        self._parser(self.parser_json_root if isinstance(i, Json_Start) else self.parser_list_root, Token_list)
                    else : Token_list.append(a)
                    # 防止退栈时阅读指针倒退，因为匹配对象a还是之前匹配过的字符, 例子：{ "a" : { } }
                    if a["token"].end() > self.read_pointers : self.read_pointers = a["token"].end() 
                    break

            if is_not_successs :
                _m_ = self.no_match_error1.match(self.command_str, self.read_pointers)
                if _m_ == None : _m_ = self.no_match_error2.match(self.command_str, self.read_pointers)
                raise BaseMatch.Not_Match(">>%s<< 非期望的参数" % _m_.group(), pos=(_m_.start(),_m_.end()), word=_m_.group())

            if isinstance(current_leaves,BaseMatch.End_Node) : break
            self.read_pointers = self._jump_space(self.command_str, self.read_pointers).end()

        self.recursion_count -= 1

    def parser(self, Token_list:list, command_str:str, pointer:int) :
        self.command_str = command_str
        self.read_pointers = pointer
        self._parser(self.parser_json_root, Token_list)



JSON_PARSER = Json_Parser()
def json_tokenizer(token_list:list, s:str, pos:int) :
    JSON_PARSER.parser(token_list, s, pos)

