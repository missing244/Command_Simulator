"""
最原始的匹配类\n
由Match_Base为基类拓展的，各个子类匹配模块\n
通过Match_Base.tree_leaves实现树结构搭建每个命令匹配分支\n
"""



import re,abc
from typing import Dict,Union,List,Tuple,Literal

__all__ = ["Match_Base","Enum","Char","KeyWord","Int","Float"]

class Not_Match_Object(Exception) : pass
class Command_Match_Exception(Exception) :
    def __init__(self, *args, **kargs) :
        super().__init__(*args)
        for i in kargs : self.__setattr__(i,kargs[i])

class Not_Match(Command_Match_Exception) : pass
class To_Many_Args(Command_Match_Exception) : pass



def string_to_rematch(s:str) -> str :
    """将字符串转换为合法的正则表达式"""
    s_list = [ "\\u" + ("000%s" % hex( ord(i)).replace("0x","",1) )[-4:] for i in s]
    return "".join(s_list)

TERMINATOR_RE = string_to_rematch(' ,@~^$&"!#%+*/=[{]}\|<>`')


class Match_Base(metaclass=abc.ABCMeta) :
    '''
    匹配对象基类
    ------------------
    你不应该直接使用这个类\n
    ------------------------------------
    所有从此基类继承的类都应该有以下实例化参数\n
    token_type : 定义该匹配的参数含义\n
    token_type的格式如下 -> "Dimension:dimension1;dimension2;...."\n
    Dimension 是对 token 的参数类型标注\n
    dimension1 是对 自动补全列表 的第1个参数进行提示解释\n
    后续依次类推.......\n
    ------------------------------------
    所有从此基类继承的类都有以下公用方法\n
    add_leaves : 添加同级的命令分支\n
    ------------------------------------
    提供给开发者重写的方法\n
    _match_string : 提供自动补全的字符串列表，必须写明传参s、s_pointer，s是源字符串，s_pointer是源字符串当前匹配停止的位置
    _auto_complete : 提供自动补全的字符串列表
    '''

    def __init__(self,token_type:str) -> None :
        if not isinstance(token_type,str) : raise TypeError("token_type 提供字符串以外的参数")
        token_type1 = token_type.split(":",1)
        self.token_type = token_type1[0]
        self.tree_leaves:List[Match_Base] = []
        self.maximum_version:Union[None,List[int]] = None
        self.minimum_version:Union[None,List[int]] = None
        if len(token_type1) > 1 : self.argument_dimension = token_type1[1].split(";")
        else : self.argument_dimension = []

    def __repr__(self) -> str:
        return self.__class__.__name__
        
    def add_leaves(self,*obj) :
        for i in obj :
            if not isinstance(i,Match_Base) : 
                raise Not_Match_Object("%s 为非匹配对象" % i)
            self.tree_leaves.append(i)
        return self

    @abc.abstractmethod
    def _match_string(self,s:str,s_pointer:int) -> re.Match : pass
    
    @abc.abstractmethod
    def _auto_complete(self) -> Dict[str,str] : pass

    def set_version(self, v1:int, v2:int, v3:int, _type:Literal["min","max"]) :
        if _type == "min" : self.minimum_version = (v1,v2,v3)
        elif _type == "max" : self.maximum_version = (v1,v2,v3)
        return self

class End_Node(Match_Base) :
    """
    命令结束标志
    ------------------------------
    在下一次匹配中，应该无法匹配到任何除分隔符(例如空格)以外的字符\n
    ------------------------------
    实例化参数\n
    >>> End_Node()
    """
    
    def __init__(self) -> None :
        super().__init__("END")
        self.re_match = re.compile(".{0,}")

    def _match_string(self, s:str, s_pointer:int): 
        _match = self.re_match.match(s, pos=s_pointer)
        if _match and _match.group().__len__() > 0 : 
            raise To_Many_Args(">>%s<< 多余的参数" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())

    def _auto_complete(self) -> Dict[str,str] : return {"\n" : "行结束"}

END_NODE = End_Node()


class Enum(Match_Base) :
    """
    枚举值
    ------------------------------
    在下一次匹配中，只能匹配到 s 参数提供的字符串\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    *s : 所有可以匹配的字符串\n
    terminator : 匹配停止的所有字符\n
    >>> Enum("Enum",  "ab","cd","ef")
    """
    
    def __repr__(self) -> str:
        return str(self.re_test)

    def __init__(self, token_type:str, *s:str, terminator:str=TERMINATOR_RE) -> None :
        for i in s :
            if not isinstance(i,str) : raise TypeError("s 提供字符串以外的参数")
        if not isinstance(terminator,str) : raise TypeError("terminator 提供字符串以外的参数")
        super().__init__(token_type)
        self.base_input = s
        self.re_match = re.compile("[^%s]{0,}" % terminator)
        self.re_test  = re.compile("^(%s)$" % "|".join([string_to_rematch(i) for i in s])) 

    def _match_string(self,s:str,s_pointer:int): 
        _match = self.re_match.match(s,pos=s_pointer)
        if not self.re_test.search(_match.group()) : 
            raise Not_Match(">>%s<< 并不是有效字符" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str]: 
        a = {}
        for i in range(len(self.base_input)) :
            if i < len(self.argument_dimension) : 
                a[self.base_input[i]] = self.argument_dimension[i]
            else : a[self.base_input[i]] = ""
        return a

class Char(Match_Base) :
    """
    字符串
    ------------------------------
    在下一次匹配中，只能匹配到 s 参数提供的字符串\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    s : 可以匹配到的字符串\n
    terminator : 匹配停止的所有字符\n
    >>> Char("Command",  "ab")
    """
    def __repr__(self) -> str:
        return str(self.re_test)
    
    def __init__(self, token_type:str, s:str, terminator:str=TERMINATOR_RE) -> None :
        if not isinstance(s,str) : raise TypeError("s 提供字符串以外的参数")
        if not isinstance(terminator,str) : raise TypeError("terminator 提供字符串以外的参数")
        super().__init__(token_type)
        self.base_input = s
        self.re_match = re.compile("[^%s]{0,}" % terminator)
        self.re_test  = re.compile("^(%s)$" % string_to_rematch(s)) 

    def _match_string(self,s:str,s_pointer:int): 
        _match = self.re_match.match(s,pos=s_pointer)
        if not self.re_test.search(_match.group()) : 
            raise Not_Match(">>%s<< 并不是有效字符" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        a = {}
        if len(self.argument_dimension) > 0 : 
            a[self.base_input] = self.argument_dimension[0]
        else : a[self.base_input] = ""
        return a

class KeyWord(Match_Base) :
    """
    关键字符
    ------------------------------
    在下一次匹配中，必须匹配到 s 参数提供的字符串\n
    但是匹配器传入的字符串阅读指针，一定跳过分隔符字符，例如命令中的空格\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    *s : 可以匹配的所有字符串\n
    >>> KeyWord("Selector_Start",  "[")
    """
    def __repr__(self) -> str:
        return str(self.re_test)

    def __init__(self, token_type:str, *s:str) -> None :
        if not isinstance(token_type,str) : raise TypeError("type 提供字符串以外的参数")
        for i in s :
            if not isinstance(i,str) : raise TypeError("s 提供字符串以外的参数")
        super().__init__(token_type)
        self.base_input = s
        self.re_match   = [re.compile(".{1,%s}" % len(i)) for i in s]
        self.re_test    = [re.compile(string_to_rematch(i)) for i in s]

    def _match_string(self,s:str,s_pointer:int) : 
        _match = [i.match(s, pos=s_pointer) for i in self.re_match]
        a = [self.re_test[index].search(item.group()) for index,item in enumerate(_match)]
        if not any(a) : raise Not_Match(">>%s<< 并不是有效的字符" % _match[0].group(), 
            pos=(_match[0].start(),_match[0].end()), word=_match[0].group())
        return {"type":self.token_type, "token":next( (_match[index] for index,item in enumerate(a) if item) )}

    def _auto_complete(self) -> Dict[str,str] : 
        a = {}
        for i in range(len(self.base_input)) :
            if i < len(self.argument_dimension) : 
                a[self.base_input[i]] = self.argument_dimension[i]
            else : a[self.base_input[i]] = ""
        return a

class Int(Match_Base) :
    """
    整数
    ------------------------------
    在下一次匹配中，需要匹配到合法的整数\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    terminator : 匹配停止的所有字符\n
    *unit_word : 所有可匹配的单位字符串\n
    >>> Int("Count",   "L","D")
    """

    def __init__(self, token_type:str, *unit_word:str, terminator:str=TERMINATOR_RE) -> None :
        if not isinstance(terminator,str) : raise TypeError("terminator 提供字符串以外的参数")
        for i in unit_word :
            if not isinstance(i,str) : raise TypeError("unit_word 提供字符串以外的参数")
        super().__init__(token_type)
        self.re_match = re.compile("[-+]?[^%s]{0,}" % terminator)
        self.re_test  = re.compile("^(-+)?[0-9]{1,}$")
        self.unit_word = unit_word
        self.unit_word_test  = re.compile("(%s)$" % "|".join([string_to_rematch(i) for i in unit_word])) if unit_word else None

    def _match_string(self,s:str,s_pointer:int) : 
        _match = self.re_match.match(s,pos=s_pointer)
        if self.unit_word_test : 
            b = self.unit_word_test.search(_match.group())
            if not b : raise Not_Match(">>%s<< 并不具有有效的整数单位" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
            a = self.re_test.search(_match.group()[0:b.start()])
        else : a = self.re_test.search(_match.group())
        if not a or not(-2147483648 <= int(a.group()) <= 2147483647) : 
            raise Not_Match(">>%s<< 并不是有效的整数" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str]:
        aaaa = ""
        if len(self.argument_dimension) : aaaa = self.argument_dimension[0]
        if self.unit_word : return {(str("0" + i)):aaaa for i in self.unit_word}
        else : return {"0":aaaa}

class Float(Match_Base) :
    """
    浮点数
    ------------------------------
    在下一次匹配中，需要匹配到合法的浮点数\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    terminator : 匹配停止的所有字符\n
    *unit_word : 所有可匹配的单位字符串\n
    >>> Float("Time",     "L","D")
    """
    
    def __init__(self, token_type:str, *unit_word:str, terminator:str=TERMINATOR_RE) -> None :
        if not isinstance(terminator,str) : raise TypeError("terminator 提供字符串以外的参数")
        for i in unit_word :
            if not isinstance(i,str) : raise TypeError("unit_word 提供字符串以外的参数")
        super().__init__(token_type)
        self.re_match = re.compile("[-+]?[^%s]{0,}" % terminator)
        self.re_test  = re.compile("^[-+]?([0-9]{0,}\\.[0-9]{1,}|[0-9]{1,}\\.[0-9]{0,}|[0-9]{1,})$") 
        self.unit_word = unit_word
        self.unit_word_test  = re.compile("(%s)$" % "|".join([string_to_rematch(i) for i in unit_word])) if unit_word else None

    def _match_string(self,s:str,s_pointer:int): 
        _match = self.re_match.match(s,pos=s_pointer)
        if self.unit_word_test : 
            b = self.unit_word_test.search(_match.group())
            if not b : raise Not_Match(">>%s<< 并不具有有效的整数单位" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
            a = self.re_test.search(_match.group()[0:b.start()])
        else : a = self.re_test.search(_match.group())
        if not a : raise Not_Match(">>%s<< 并不是有效的浮点数" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        aaaa = ""
        if len(self.argument_dimension) : aaaa = self.argument_dimension[0]
        if self.unit_word : return {("0" + i):aaaa for i in self.unit_word}
        else : return {"0":aaaa}


class AnyString(Match_Base) :
    """
    任意字符串
    ------------------------------
    在下一次匹配中，尽可能尝试匹配到更多的，连续的非终止字符\n
    适用于Minecraft ID\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    atuo_complete : 自动提示将会提示的内容\n
    terminator : 匹配停止的所有字符\n
    >>> AnyString("ID")
    """
    
    def __init__(self, token_type:str, atuo_complete:Dict[str,str]={}, terminator:str=TERMINATOR_RE) -> None :
        if not isinstance(terminator,str) : raise TypeError("terminator 提供字符串以外的参数")
        super().__init__(token_type)
        self.re_match = re.compile("[^%s]{0,}" % terminator)
        self.atuo_complete = atuo_complete

    def _match_string(self, s:str, s_pointer:int): 
        _match = self.re_match.match(s, pos=s_pointer)
        if len(_match.group()) == 0 : raise Not_Match(">>%s<< 需要参数" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        return self.atuo_complete

class AnyMsg(Match_Base) :
    """
    任意消息
    ------------------------------
    在下一次匹配中，直接匹配后续所有的字符\n
    适用于title say等消息\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    atuo_complete : 自动提示将会提示的内容\n
    >>> AnyMsg("Msg")
    """
    
    def __init__(self, token_type:str) -> None :
        super().__init__(token_type)
        self.re_match = re.compile("(.|\\u000a|\\u000d){0,}")

    def _match_string(self, s:str, s_pointer:int): 
        _match = self.re_match.match(s, pos=s_pointer)
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        return {}





if __name__ == "__main__" :
    print(string_to_rematch("\""))
    a = Int()._match_string("a  +1213123123  c",3)
    print(a)