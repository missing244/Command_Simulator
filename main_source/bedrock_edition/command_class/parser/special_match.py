"""
针对 Minecraft 中特殊的结构内建的匹配类
"""

from .base_match import TERMINATOR_RE
from . import BaseMatch
from typing import Dict,Union,List,Tuple
import re

__all__ = ["BE_String","BE_Quotation_String","Relative_Offset_Float","Local_Offset_Float"]

class Illegal_Match(BaseMatch.Command_Match_Exception) : pass


class Command_Root(BaseMatch.Match_Base) :
    '''
    命令根类
    ------------------
    命令应该由此类开始add_leaves\n
    '''
    def __repr__(self) -> str:
        return str(self.tree_leaves)
    
    def __init__(self) -> None:
        super().__init__("Root")
    
    def add_leaves(self,*obj) :
        for i in obj :
            if not isinstance(i,BaseMatch.Match_Base) : 
                raise BaseMatch.Not_Match_Object("obj 不应该存在非 Match_Base 对象")
        super().add_leaves(*obj)
        return self
    def _match_string(self,s:str,s_pointer:int) : pass
    def _auto_complete(self) -> Dict[str,str] : pass


class BE_Not_Int_Float(BaseMatch.Float) :

    def __init__(self, token_type: str, *unit_word: str, terminator: str = BaseMatch.TERMINATOR_RE) -> None:
        super().__init__(token_type, *unit_word, terminator=terminator)
        self.re_test  = re.compile("^[-+]?([0-9]{0,}\\.[0-9]{1,}|[0-9]{1,}\\.[0-9]{0,})$") 

class BE_Range_Int(BaseMatch.Int) :
    """
    MCBE版范围整数匹配
    ------------------------------
    在下一次匹配中，只能匹配到范围整数\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    terminator : 匹配停止的所有字符\n
    >>> BE_Range_Int("Range_Max")
    """
    
    def __init__(self, token_type:str, terminator:str=BaseMatch.TERMINATOR_RE) -> None :
        if not isinstance(terminator,str) : raise TypeError("terminator 提供字符串以外的参数")
        super().__init__(token_type)
        self.re_match = re.compile("[^%s\\.]{0,}" % terminator)

class BE_String(BaseMatch.Match_Base) :
    """
    MCBE版普通字符串匹配
    ------------------------------
    在下一次匹配中，只能匹配到非双引号开头的，非数字字符串\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    terminator : 匹配停止的所有字符\n
    >>> BE_String("Player")
    """
    
    def __init__(self, token_type:str, terminator:str=BaseMatch.TERMINATOR_RE, auto_complete:Dict[str,str]=None) -> None :
        if not isinstance(terminator,str) : raise TypeError("terminator 提供字符串以外的参数")
        super().__init__(token_type)
        self.auto_complete = auto_complete
        self.re_match = re.compile("[^%s]{0,}" % terminator)
        self.re_test  = re.compile("^[-+]?([0-9]{0,}\\.[0-9]{1,}|[0-9]{1,}\\.[0-9]{0,}|[0-9]{1,})$") 

    def _match_string(self,s:str,s_pointer:int) :
        _match = self.re_match.match(s,pos=s_pointer)
        if (not _match.group()) or (self.re_test.search(_match.group())) : 
            raise Illegal_Match(">>%s<< 并不是有效字符串" % _match.group(), pos=(_match.start(),_match.end()), word=_match.group())
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str]: 
        if self.auto_complete is None : return {"string":""}
        else : return self.auto_complete.copy()

class BE_Quotation_String(BaseMatch.Match_Base) :
    """
    MCBE版引号字符串匹配
    ------------------------------
    在下一次匹配中，只能匹配到双引号开头的合法字符串\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    >>> BE_Quotation_String("Player")
    """

    def __init__(self, token_type: str, auto_complete:Dict[str,str]=None) -> None :
        super().__init__(token_type)
        self.re_match = re.compile('"(\\\\.|[^\\\\"]){0,}"')
        self.auto_complete = auto_complete

    def _match_string(self,s:str,s_pointer:int) : 
        len_s = len(s)

        if s[s_pointer] != "\"" :
            raise Illegal_Match(">>%s<< 并不是有效的引号字符串" % s[s_pointer], pos=(s_pointer,s_pointer+1), word=s[s_pointer])

        _match = self.re_match.match(s,s_pointer)
        if not _match : raise Illegal_Match(">>%s<< 并不是有效的引号字符串" % s[s_pointer:len_s], pos=(s_pointer,len_s), word=s[s_pointer:len_s])

        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        if self.auto_complete is None : return {'"string"':""}
        else : return self.auto_complete.copy()

class Relative_Offset_Float(BaseMatch.Match_Base) :
    """
    相对坐标
    ------------------------------
    在下一次匹配中，需要匹配到合法的一个绝对/相对坐标\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    >>> Relative_Offset_Float("Pos")
    """
    
    def __init__(self, token_type:str) -> None :
        super().__init__(token_type)
        self.re_match = re.compile("~[-\\+]?[0-9\\.]{0,}")
        self.re_test  = re.compile("^[-+]?([0-9]{0,}\\.[0-9]{1,}|[0-9]{1,}\\.[0-9]{0,}|[0-9]{1,})$")

    def _match_string(self,s:str,s_pointer:int): 
        _match = self.re_match.match(s,pos=s_pointer)
        if not _match : raise Illegal_Match(">>%s<< 不合法的相对偏量" % s[s_pointer], pos=(s_pointer,s_pointer + 1), word=s[s_pointer])
        if _match.group().__len__() > 1 : 
            if not self.re_test.search(_match.group()[1:]) :
                raise Illegal_Match(">>%s<< 并不是有效的浮点数" % _match.group()[1:], pos=(_match.start()+1,_match.end()), word=_match.group()[1:])
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        if len(self.argument_dimension) : return {"~":self.argument_dimension[0]}
        return {"~":""}

class Local_Offset_Float(BaseMatch.Match_Base) :
    """
    局部坐标
    ------------------------------
    在下一次匹配中，需要匹配到合法一个的局部坐标\n
    ------------------------------
    实例化参数\n
    token_type : 定义该匹配的参数含义\n
    >>> Local_Offset_Float("Pos")
    """
    
    def __init__(self,token_type:str) -> None :
        super().__init__(token_type)
        self.re_match = re.compile("(\\^)[-\\+]?[0-9\\.]{0,}")
        self.re_test  = re.compile("^[-+]?([0-9]{0,}\\.[0-9]{1,}|[0-9]{1,}\\.[0-9]{0,}|[0-9]{1,})$")

    def _match_string(self,s:str,s_pointer:int): 
        _match = self.re_match.match(s,pos=s_pointer)
        if not _match : raise Illegal_Match(">>%s<< 不合法的相对偏量" % s[s_pointer], pos=(s_pointer,s_pointer + 1), word=s[s_pointer])
        if _match.group().__len__() > 1 : 
            if not self.re_test.search(_match.group()[1:]) :
                raise Illegal_Match(">>%s<< 并不是有效的浮点数" % _match.group()[1:], pos=(_match.start()+1,_match.end()), word=_match.group()[1:])
        return {"type":self.token_type, "token":_match}

    def _auto_complete(self) -> Dict[str,str] : 
        if len(self.argument_dimension) : return {"^":self.argument_dimension[0]}
        return {"^":""}

class BE_BlockState_String(BE_Quotation_String) :
    def _set_auto_complete(self,auto_complete={}) :
        self.auto_complete = auto_complete



def String_Tree(token_type:str="Scoreboard_Name",*end_node:BaseMatch.Match_Base):
    """
    自动生成一个计分板名字匹配树\n
    *end_node : 添加下一级匹配类\n
    -------------------------------
    返回匹配列表，请将该列表传入add_leaves时添加解包操作
    """
    return [
        BE_String(token_type).add_leaves(*end_node),
        BE_Quotation_String(token_type).add_leaves(*end_node)
    ]

def Scoreboard_Entity_Name_Tree(*end_node:BaseMatch.Match_Base):
    """
    自动生成一个计分板内项目名的匹配树\n
    *end_node : 添加下一级匹配类\n
    -------------------------------
    返回匹配列表，请将该列表传入add_leaves时添加解包操作
    """
    return [
        BaseMatch.KeyWord("Objective_Name","*").add_leaves(*end_node),
        *BE_Selector_Tree(*end_node)
    ]



def Rotation_Tree(*end_node:BaseMatch.Match_Base):
    """
    自动生成一个朝向匹配树\n
    ...end_node : 添加下一级匹配类\n
    -------------------------------
    返回匹配列表，请将该列表传入add_leaves时添加解包操作
    """
    return [
        BaseMatch.Float("Absolute_Rotation").add_leaves(
            BaseMatch.Float("Absolute_Rotation").add_leaves(*end_node),
            Relative_Offset_Float("Relative_Rotation").add_leaves(*end_node)
        ),
        Relative_Offset_Float("Relative_Rotation").add_leaves(
            BaseMatch.Float("Absolute_Rotation").add_leaves(*end_node),
            Relative_Offset_Float("Relative_Rotation").add_leaves(*end_node)
        )
    ]

def Pos_Tree(*end_node:BaseMatch.Match_Base) -> List[BaseMatch.Match_Base] :
    """
    自动生成一个坐标匹配树\n
    *end_node : 添加下一级匹配类\n
    -------------------------------
    返回匹配列表，请将该列表传入add_leaves时添加解包操作
    """
    return [
        BaseMatch.Float("Absolute_Pos").add_leaves(
            Relative_Offset_Float("Relative_Pos").add_leaves(
                Relative_Offset_Float("Relative_Pos").add_leaves(*end_node),
                BaseMatch.Float("Absolute_Pos").add_leaves(*end_node),
            ),
            BaseMatch.Float("Absolute_Pos").add_leaves(
                Relative_Offset_Float("Relative_Pos").add_leaves(*end_node),
                BaseMatch.Float("Absolute_Pos").add_leaves(*end_node),
            )
        ),
        Relative_Offset_Float("Relative_Pos").add_leaves(
            Relative_Offset_Float("Relative_Pos").add_leaves(
                Relative_Offset_Float("Relative_Pos").add_leaves(*end_node),
                BaseMatch.Float("Absolute_Pos").add_leaves(*end_node),
            ),
            BaseMatch.Float("Absolute_Pos").add_leaves(
                Relative_Offset_Float("Relative_Pos").add_leaves(*end_node),
                BaseMatch.Float("Absolute_Pos").add_leaves(*end_node),
            )
        ),
        Local_Offset_Float("Local_Pos").add_leaves(
            Local_Offset_Float("Local_Pos").add_leaves(
                Local_Offset_Float("Local_Pos").add_leaves(*end_node)
            )
        )
    ]

def Range_Tree(*end_node:BaseMatch.Match_Base) -> List[BaseMatch.Match_Base] :
    """
    自动生成一个范围值匹配树\n
    *end_node : 添加下一级匹配类\n
    -------------------------------
    返回匹配列表，请将该列表传入add_leaves时添加解包操作
    """
    return [
        BE_Range_Int("Range_Min").add_leaves( 
            BaseMatch.KeyWord("Range_Sign","..").add_leaves( 
                BE_Range_Int("Range_Max").add_leaves(*end_node),
                *end_node
            ),
            *end_node
        ),
        BaseMatch.KeyWord("Range_Sign","..").add_leaves( 
            BE_Range_Int("Range_Max").add_leaves(*end_node)
        ),
        BaseMatch.KeyWord("Not","!").add_leaves(
            BE_Range_Int("Range_Min").add_leaves( 
                BaseMatch.KeyWord("Range_Sign","..").add_leaves( 
                    BE_Range_Int("Range_Max").add_leaves(*end_node),
                    *end_node
                ),
                *end_node
            ),
            BaseMatch.KeyWord("Range_Sign","..").add_leaves( 
                BE_Range_Int("Range_Max").add_leaves(*end_node)
            )
        )
    ]



def middle_scores_loop(*end_node:BaseMatch.Match_Base) :
    scores : List[BaseMatch.Match_Base] = [
        BE_String("Scoreboard_Name"),
        BE_Quotation_String("Scoreboard_Name")
    ]
    scores[0].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( *Range_Tree(
        BaseMatch.KeyWord("Next_Score_Argument",",").add_leaves(*scores),
        BaseMatch.KeyWord("End_Score_Argument","}").add_leaves(*end_node)
    )))
    scores[1].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( *Range_Tree(
        BaseMatch.KeyWord("Next_Score_Argument",",").add_leaves(*scores),
        BaseMatch.KeyWord("End_Score_Argument","}").add_leaves(*end_node)
    )))
    return BaseMatch.KeyWord("Start_Score_Argument","{").add_leaves(*scores)

def middle_haspermission_loop(*end_node:BaseMatch.Match_Base) :
    haspermission1 = BaseMatch.KeyWord("Start_Permission_Argument","{")
    haspermission2 = BaseMatch.Enum("Permission_Argument","camera","movement")
    haspermission2.add_leaves( 
        BaseMatch.KeyWord("Equal","=").add_leaves( 
            BaseMatch.Enum("Value","enabled","disabled").add_leaves( 
                BaseMatch.KeyWord("Next_Permission_Argument",",").add_leaves(haspermission2),
                BaseMatch.KeyWord("End_Permission_Argument","}").add_leaves(*end_node)
            )
        )
    )
    return haspermission1.add_leaves(haspermission2)

def middle_hasitem_single_args_loop(*end_node:BaseMatch.Match_Base) :
    hasitem : List[BaseMatch.Match_Base] = [
        BaseMatch.Char("Item_Argument","item"),
        BaseMatch.Char("Item_Argument","data"),
        BaseMatch.Char("Item_Argument","quantity"),
        BaseMatch.Char("Item_Argument","location"),
        BaseMatch.Char("Item_Argument","slot")
    ]
    hasitem[0].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        BaseMatch.AnyString("Item_ID").add_leaves( 
            BaseMatch.KeyWord("Next_Item_Argument",",").add_leaves(*hasitem),
            BaseMatch.KeyWord("End_Item_Argument","}").add_leaves(*end_node)
        )
    ))
    hasitem[1].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        BaseMatch.Int("Data_Value").add_leaves( 
            BaseMatch.KeyWord("Next_Item_Argument",",").add_leaves(*hasitem),
            BaseMatch.KeyWord("End_Item_Argument","}").add_leaves(*end_node)
        )
    ))
    hasitem[2].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        *Range_Tree( 
            BaseMatch.KeyWord("Next_Item_Argument",",").add_leaves(*hasitem),
            BaseMatch.KeyWord("End_Item_Argument","}").add_leaves(*end_node)
        )
    ))
    hasitem[3].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        BaseMatch.Enum("Slot_Type","slot.weapon.mainhand","slot.weapon.offhand",
        "slot.armor.head","slot.armor.chest","slot.armor.legs","slot.armor.feet",
        "slot.enderchest","slot.hotbar","slot.inventory","slot.saddle","slot.armor",
        "slot.armor","slot.chest","slot.equippable").add_leaves( 
            BaseMatch.KeyWord("Next_Item_Argument",",").add_leaves(*hasitem),
            BaseMatch.KeyWord("End_Item_Argument","}").add_leaves(*end_node)
        )
        #"slot.weapon.mainhand","slot.weapon.offhand",
        #"slot.armor.head","slot.armor.chest","slot.armor.legs","slot.armor.feet",
        #"slot.enderchest","slot.hotbar","slot.inventory","slot.saddle","slot.armor",
        #"slot.armor","slot.chest","slot.equippable"
    ))
    hasitem[4].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        *Range_Tree( 
            BaseMatch.KeyWord("Next_Item_Argument",",").add_leaves(*hasitem),
            BaseMatch.KeyWord("End_Item_Argument","}").add_leaves(*end_node)
        )
    ))
    return BaseMatch.KeyWord("Start_Item_Argument","{").add_leaves(*hasitem)

def middle_hasitem_multiple_args_loop(*end_node:BaseMatch.Match_Base) :
    hasitem1 = BaseMatch.KeyWord("Start_Item_Condition","[")
    m1 = BaseMatch.KeyWord("Next_Item_Condition",",")
    hasitem2 = middle_hasitem_single_args_loop( 
        m1, BaseMatch.KeyWord("End_Item_Condition","]").add_leaves(*end_node)
    )
    m1.add_leaves(hasitem2)
    return hasitem1.add_leaves(hasitem2)

def middle_hasproperty_loop(*end_node:BaseMatch.Match_Base) :
    hasProperty1 = BaseMatch.KeyWord("Start_Property_Argument","{")
    hasProperty2 = BaseMatch.Char("Property_Argument","property")
    hasProperty3 = BaseMatch.AnyString("Property")
    hasProperty2.add_leaves(
        BaseMatch.KeyWord("Equal","=").add_leaves(
            BaseMatch.AnyString("Property").add_leaves(
                BaseMatch.KeyWord("Next_Property_Argument",",").add_leaves(hasProperty2,hasProperty3),
                BaseMatch.KeyWord("End_Property_Argument","}").add_leaves(*end_node)
            ),
            BaseMatch.KeyWord("Not","!").add_leaves(
                BaseMatch.AnyString("Property").add_leaves( 
                    BaseMatch.KeyWord("Next_Property_Argument",",").add_leaves(hasProperty2,hasProperty3),
                    BaseMatch.KeyWord("End_Property_Argument","}").add_leaves(*end_node)
                )
            )
        )
    )
    hasProperty3.add_leaves(
        BaseMatch.KeyWord("Equal","=").add_leaves(
            BaseMatch.Enum("Bool","true","false").add_leaves( 
                BaseMatch.KeyWord("Next_Property_Argument",",").add_leaves(hasProperty2,hasProperty3),
                BaseMatch.KeyWord("End_Property_Argument","}").add_leaves(*end_node)
            ),
            BE_Not_Int_Float("Float").add_leaves( 
                BaseMatch.KeyWord("Next_Property_Argument",",").add_leaves(hasProperty2,hasProperty3),
                BaseMatch.KeyWord("End_Property_Argument","}").add_leaves(*end_node)
            ),
            *Range_Tree(
                BaseMatch.KeyWord("Next_Property_Argument",",").add_leaves(hasProperty2,hasProperty3),
                BaseMatch.KeyWord("End_Property_Argument","}").add_leaves(*end_node)
            ),
            BE_Quotation_String("String").add_leaves( 
                BaseMatch.KeyWord("Next_Property_Argument",",").add_leaves(hasProperty2,hasProperty3),
                BaseMatch.KeyWord("End_Property_Argument","}").add_leaves(*end_node)
            ),
        )
    )
    return hasProperty1.add_leaves(hasProperty2,hasProperty3)



def BE_Selector_Tree(*end_node:BaseMatch.Match_Base) :
    """
    自动生成一个目标选择器选择器匹配树\n
    *end_node : 添加下一级匹配类\n
    -------------------------------
    返回匹配列表，请将该列表传入add_leaves时添加解包操作
    """


    Selector_Var2 : List[BaseMatch.Match_Base] = [
        BaseMatch.Enum("Selector_Argument","x","y","z"),     # 0
        BaseMatch.Enum("Selector_Argument","dx","dy","dz"),  # 1
        BaseMatch.Enum("Selector_Argument","r","rm","rx","rxm","ry","rym"), # 2
        BaseMatch.Enum("Selector_Argument","l","lm","c"),    # 3
        BaseMatch.Char("Selector_Argument","type"),          # 4
        BaseMatch.Char("Selector_Argument","m"),             # 5
        BaseMatch.Enum("Selector_Argument","tag"),           # 6
        BaseMatch.Enum("Selector_Argument","name","family"), # 7
        BaseMatch.Char("Selector_Argument","scores"),        # 8
        BaseMatch.Char("Selector_Argument","haspermission"), # 9
        BaseMatch.Char("Selector_Argument","hasitem"),       # 10
        BaseMatch.Char("Selector_Argument","has_property").set_version(1,20,70,"min")   # 11
    ]


    Selector_Var2[0].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        Relative_Offset_Float("Relative_Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BaseMatch.Float("Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        )
    ))
    Selector_Var2[1].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        BaseMatch.Int("Value").set_version(1,19,70,"max").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BaseMatch.Float("Value").set_version(1,19,70,"min").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        )
    ))
    Selector_Var2[2].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( BaseMatch.Float("Value").add_leaves(
        BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
        BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
    )))
    Selector_Var2[3].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( BaseMatch.Int("Value").add_leaves(
        BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
        BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
    )))
    Selector_Var2[4].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        BaseMatch.AnyString("Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BaseMatch.KeyWord("Not","!").add_leaves( BaseMatch.AnyString("Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        )),
    ))
    Selector_Var2[5].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves(
            BaseMatch.Enum("Value",
            "0","survival","s","1","creative","c","2","adventure","a","spectator").add_leaves(
                BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
                BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BaseMatch.KeyWord("Not","!").add_leaves( 
            BaseMatch.Enum("Value",
            "0","survival","s","1","creative","c","2","adventure","a","spectator").add_leaves(
                BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
                BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        )
    )))
    Selector_Var2[6].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        BaseMatch.KeyWord("Not","!").add_leaves( 
            BE_String("Value").add_leaves(
                BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
                BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
            ),
            BE_Quotation_String("Value").add_leaves(
                BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
                BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
            ),
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BE_String("Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BE_Quotation_String("Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
        BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
    ))
    Selector_Var2[7].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        BaseMatch.KeyWord("Not","!").add_leaves( 
            BE_String("Value").add_leaves(
                BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
                BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
            ),
            BE_Quotation_String("Value").add_leaves(
                BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
                BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
            )
        ),
        BE_String("Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        BE_Quotation_String("Value").add_leaves(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        )
    ))
    Selector_Var2[8].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( middle_scores_loop(
        BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
        BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
    )))
    Selector_Var2[9].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( middle_haspermission_loop(
        BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
        BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
    )))
    Selector_Var2[10].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( 
        middle_hasitem_multiple_args_loop(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        ),
        middle_hasitem_single_args_loop(
            BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
            BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
        )
    ))
    Selector_Var2[11].add_leaves( BaseMatch.KeyWord("Equal","=").add_leaves( middle_hasproperty_loop(
        BaseMatch.KeyWord("Next_Selector_Argument",",").add_leaves(*Selector_Var2),
        BaseMatch.KeyWord("End_Selector_Argument","]").add_leaves(*end_node)
    )))

    Selector : List[BaseMatch.Match_Base] = [
        BaseMatch.KeyWord("Selector","@p","@a","@r","@s","@e","@initiator").add_leaves(
            BaseMatch.KeyWord("Start_Selector_Argument","[").add_leaves(*Selector_Var2),
            *end_node
        ),
        BE_String("Player_Name").add_leaves(*end_node),
        BE_Quotation_String("Player_Name").add_leaves(*end_node)
    ]
    return Selector

def BE_BlockState_Tree(*end_node:BaseMatch.Match_Base) :
    """
    自动生成一个方块状态选择器匹配树\n
    ...end_node : 添加下一级匹配类\n
    """
    start1 = BaseMatch.KeyWord("Start_BlockState_Argument","[").add_leaves(
        BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node)
    )
    start2 = BE_BlockState_String("BlockState")
    start2.add_leaves(
        BaseMatch.KeyWord("Equal",":").set_version(1,20,10,"max").add_leaves(
            BE_BlockState_String("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Enum("Value","true","false").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Int("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
        ),
        BaseMatch.KeyWord("Equal","=").set_version(1,20,10,"min").add_leaves(
            BE_BlockState_String("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Enum("Value","true","false").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
            BaseMatch.Int("Value").add_leaves(
                BaseMatch.KeyWord("End_BlockState_Argument","]").add_leaves(*end_node),
                BaseMatch.KeyWord("Next_BlockState_Argument",",").add_leaves(start2)
            ),
        )
    )
    start1.add_leaves(start2)
    return start1






