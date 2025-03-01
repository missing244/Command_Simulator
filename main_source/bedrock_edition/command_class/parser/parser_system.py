"""
命令词法器系统\n
Command_Parser用于检查每个同级树分支中满足哪个匹配分支，然后载入满足分支的子分支匹配
"""

from . import BaseMatch,SpecialMatch,JsonPaser

from typing import Dict,Union,List,Tuple,Literal
import re,traceback,itertools
escape_space = re.compile("[ ]{0,}")

class Command_Parser :
    """
    词法器\n
    ------------------------
    实例化参数\n
    Tree : SpecialMatch.Command_Root类开始嵌套的命令树\n
    separator : 一个分隔字符\n
    separator_count : 每段匹配结构之间需要需要相隔多少分隔符\n
    """

    def __init__(self,Tree:SpecialMatch.Command_Root, separator:str=" ", separator_count:int=None) -> None:
        if not isinstance(Tree,SpecialMatch.Command_Root) : raise TypeError("Tree 参数只能为 SpecialMatch.Command_Root 类")

        if not isinstance(separator,str) : raise TypeError("separator 参数只能为字符串")
        if separator.__len__() != 1 : raise Exception("separator 参数应该只存在一个字符")

        if not isinstance(separator_count, (type(None), int)) : raise TypeError("separator_count 参数只能为整数")
        if isinstance(separator_count, int) and separator_count < 1 : raise Exception("separator_count 参数应该为正整数")

        self.Tree = Tree
        self.separator = separator
        self.separator_count = separator_count
        self.no_match_error1 = re.compile("[^%s]{1,}" % BaseMatch.TERMINATOR_RE)
        self.no_match_error2 = re.compile(".{0,1}")


    def _version_compare(self, version:Tuple[int, int, int], leaves:BaseMatch.Match_Base) :
        if leaves.maximum_version is leaves.minimum_version is None : return True

        if leaves.maximum_version is None : max_v = (1000,0,0) 
        else : max_v = leaves.maximum_version
        if leaves.minimum_version is None : min_v = (0,0,0)
        else : min_v = leaves.minimum_version

        return min_v <= version < max_v

    def _get_auto_complete(self, e:Exception) :
        _str1 = {}
        for i in e.current.tree_leaves : _str1.update(i._auto_complete())
        re_match1 = re.compile(BaseMatch.string_to_rematch(e.word))
        for i in list(_str1.keys()) :
            a = re_match1.search(i)
            if a is None : del _str1[i]
        return _str1

    def _parser(self, command_str:str, version:Tuple[int, int, int]) -> List[Dict[Literal["type","token"], Union[str, re.Match]]] :
        command_str_pointer = 0
        current_leaves = self.Tree
        separator_re_match = re.compile("[%s]{%s,%s}" % (
            BaseMatch.string_to_rematch(self.separator), 
            0 if self.separator_count is None else self.separator_count, 
            "" if self.separator_count is None else self.separator_count ))
        self.Token_list = Token_list = []

        while 1 :
            if not current_leaves.tree_leaves : break

            is_not_successs = True
            for i in current_leaves.tree_leaves :
                if not self._version_compare(version, i) : continue

                if i.__class__ is JsonPaser.Json_Start :
                    try : a = i._match_string(command_str,command_str_pointer)
                    except : continue
                    JsonPaser.json_tokenizer(Token_list, command_str, command_str_pointer)
                    is_not_successs = False
                    current_leaves = i
                    command_str_pointer = Token_list[-1]["token"].end()
                else :
                    try : a = i._match_string(command_str,command_str_pointer)
                    except : continue
                    is_not_successs = False
                    current_leaves = i
                    if isinstance(current_leaves, BaseMatch.End_Node) : break
                    command_str_pointer = a["token"].end()
                    if a["type"] != "Command_Start" : Token_list.append(a)
                break

            if is_not_successs : 
                _m_ = self.no_match_error1.match(command_str,command_str_pointer)
                if _m_ is None : _m_ = self.no_match_error2.match(command_str,command_str_pointer)
                raise BaseMatch.Not_Match(">>%s<< 非期望的参数" % _m_.group(), 
                    pos=(_m_.start(),_m_.end()), word=_m_.group(), current=current_leaves)
            
            if current_leaves.__class__ is BaseMatch.End_Node : break
            command_str_pointer = separator_re_match.match(command_str, command_str_pointer).end()

        return Token_list

    def parser(self, command_str:str, version:Tuple[int, int, int]) -> Union[List[Dict], Tuple[str, BaseMatch.Command_Match_Exception]] :
        """
        return {"type":str, "token":re.Match}
        or
        return Tuple[ Error_str, Dict ]
        """
        command_str = command_str[escape_space.match(command_str).end():]
        try : a = self._parser(command_str, version)
        except Exception as e : 
            s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
            return (s, e, self._get_auto_complete(e))
        else : return a













