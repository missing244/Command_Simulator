"""
命令词法器系统\n
Command_Parser用于检查每个同级树分支中满足哪个匹配分支，然后载入满足分支的子分支匹配
"""

from . import BaseMatch, SpecialMatch, JsonPaser

from typing import Dict,Union,List,Tuple,Literal,TypedDict,Optional,Set
import re, traceback, itertools, warnings
Token = BaseMatch.Token
escape_space = re.compile("[ ]{0,}")


class TokenCursor:

    def __init__(self, tokens:List[Token]):
        self.__tokens = tokens
        self.__index = 0

    def is_end(self) -> bool:
        return self.__index >= len(self.__tokens)

    def is_not_end(self) -> bool:
        return self.__index < len(self.__tokens)

    def tell(self) -> int:
        """返回当前游标索引"""
        return self.__index

    def seek(self, offset:int, whence:Literal[0,1,2]=0) -> int:
        """
        移动游标
        ----------------------
        类似 io 的 seek 接口。
        
        :param offset: 偏移量
        :param whence: 基准位置，支持 SEEK_SET(0), SEEK_CUR(1), SEEK_END(2)
        :return: 移动后的绝对索引
        """
        if whence == 0: new_index = offset
        elif whence == 1: new_index = self.__index + offset
        elif whence == 2: new_index = len(self.__tokens) + offset
        else: raise ValueError("无效的 whence 参数，应为 SEEK_SET/SEEK_CUR/SEEK_END")

        if new_index < 0: new_index = 0
        elif new_index > len(self.__tokens): new_index = len(self.__tokens)
        self.__index = new_index
        return self.__index


    def peek(self):
        """查看当前 token，不移动索引；若越界返回 None"""
        if self.is_end(): return None
        return self.__tokens[self.__index]

    def advance(self):
        """返回当前 token 并移动索引；若越界返回 None"""
        token = self.peek()
        if token is not None: self.__index += 1
        return token

    def expect(self, token_type:str):
        """检查当前 token 类型并消费；不符合则抛出异常或返回 None"""
        token = self.peek()
        if token and token["type"] == token_type:
            self.__index += 1
            return token
        return None

    def matches(self, *token_types:str):
        """检查当前 token 是否属于给定类型之一，是则消费并返回 token，否则不移动"""
        token = self.peek()
        if token and token["type"] in token_types:
            self.__index += 1
            return token
        return None

class ParserResult:
    """
    命令解析结果封装
    ----------------------------
    :attribute tokens:     成功匹配的 Token 列表（非辅助节点，如命令、参数等）
    :attribute error:      解析过程中捕获的异常
    :attribute version:     命令编译的版本
    :attribute sub_errors:     解析过程中捕获的异常列表
    :attribute possible_nodes: 若不完整，当前节点下所有可能的下一级子节点（用于补全）
    """
    def __init__(self, command:str, handle:Optional[str], tokens:List['Token'], 
                 error:Optional[Exception], sub_errors: List[Exception], 
                 possible_nodes:List[BaseMatch.Match_Base],
                 version:Tuple[int, int, int]):
        self.command = command
        self.handle = handle
        self.tokens = tokens
        self.error = error
        self.version = version
        self.sub_errors = sub_errors
        self.possible_nodes = possible_nodes

    @property
    def success(self) -> bool:
        """语法是否正确且完整"""
        return self.error is None

    def __repr__(self) -> str:
        return (f"ParserResult(success={self.success}, tokens={len(self.tokens)}, "
                f"errors={len(self.sub_errors)}, handle=\"{self.handle}\")")


    def create_cursor(self) :
        return TokenCursor(self.tokens)

    def get_auto_complete(self) :
        _str1:Dict[str, str] = {}
        for i in self.possible_nodes : _str1.update( i._auto_complete() )
        return _str1

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

    def _parser(self, command_str:str, version:Tuple[int, int, int]) -> List[Token] :
        warnings.warn("Command_Parser is deprecated, use new_function instead", DeprecationWarning, stacklevel=2)
        CommandFlag = {"Command_Start", "Command_End", "Json_Start"}
        command_str_pointer = 0
        current_leaves = self.Tree
        separator_re_match = re.compile("[%s]{%s,%s}" % (
            BaseMatch.string_to_rematch(self.separator), 
            0 if self.separator_count is None else self.separator_count, 
            "" if self.separator_count is None else self.separator_count ))
        Token_list = []

        while current_leaves.tree_leaves :
            is_not_successs = True
            for node in current_leaves.tree_leaves :
                if not self._version_compare(version, node) : continue

                try : a = node._match_string(command_str, command_str_pointer)
                except : continue
                else : Token_list.append(a) if a["type"] not in CommandFlag else None

                if node.__class__ is JsonPaser.Json_Start : 
                    try : JsonPaser.json_tokenizer(Token_list, command_str, command_str_pointer)
                    except : continue
                    finally : command_str_pointer = Token_list[-1]["end"]
                else : command_str_pointer = a["end"]

                is_not_successs = False
                current_leaves = node
                break

            if is_not_successs : 
                _m_ = self.no_match_error1.match(command_str, command_str_pointer)
                if _m_ is None : _m_ = self.no_match_error2.match(command_str, command_str_pointer)
                raise BaseMatch.SyntaxError(">>%s<< 非期望的参数" % _m_.group(), 
                    pos=(_m_.start(),_m_.end()), word=_m_.group(), current=current_leaves)

            command_str_pointer = separator_re_match.match(command_str, command_str_pointer).end()

        return Token_list

    def parser(self, command_str:str, version:Tuple[int, int, int]) -> Union[List[Token], Tuple[str, BaseMatch.Command_Match_Exception]] :
        command_str = command_str[escape_space.match(command_str).end():]
        try : a = self._parser(command_str, version)
        except Exception as e : 
            s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
            return (s, e, self._get_auto_complete(e))
        else : return a


    def parser_v2(self, command_str:str, version:Tuple[int, int, int]) -> ParserResult :
        command_str = command_str[escape_space.match(command_str).end():]

        CommandFlag = {"Command_Start", "Command_End", "Json_Start"}
        command_str_pointer = next((i for i, ch in enumerate(command_str) if ch != ' '), len(command_str))
        current_leaves = self.Tree
        separator_re_match = re.compile("[%s]{%s,%s}" % (
            BaseMatch.string_to_rematch(self.separator), 
            0 if self.separator_count is None else self.separator_count, 
            "" if self.separator_count is None else self.separator_count ))
        Handle, Token_list, Error, Errors, NextNode = None, [], None, [], []

        while current_leaves.tree_leaves :
            is_not_successs = True

            for node in current_leaves.tree_leaves :
                if not self._version_compare(version, node) : continue

                try : token_re = node._match_string(command_str, command_str_pointer)
                except Exception as e : Errors.append(e) ; continue
                if token_re["type"] not in CommandFlag : Token_list.append(token_re)

                if node.__class__ is JsonPaser.Json_Start :
                    try : JsonPaser.json_tokenizer_v2(command_str, 
                        command_str_pointer, Token_list, Errors, NextNode)
                    except : continue
                    finally : command_str_pointer = Token_list[-1]["end"]
                else : command_str_pointer = token_re["end"]

                if node.handle_tag : Handle = node.handle_tag

                Errors.clear()
                current_leaves = node
                is_not_successs = False
                break

            if is_not_successs :
                if node.__class__ is not JsonPaser.Json_Start : NextNode.extend(current_leaves.tree_leaves)
                err_position_str = self.no_match_error1.match(command_str, command_str_pointer)
                if not err_position_str : err_position_str = self.no_match_error2.match(command_str, command_str_pointer)
                Error = BaseMatch.SyntaxError(
                    ">>%s<< 非期望的参数" % err_position_str.group(), 
                    pos=(err_position_str.start(), err_position_str.end()), 
                    word=err_position_str.group())
                break

            command_str_pointer = separator_re_match.match(command_str, command_str_pointer).end()

        return ParserResult(command_str.strip(), Handle, Token_list, Error, Errors, NextNode, version)













