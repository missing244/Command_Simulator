from typing import Literal,Union
from io import BytesIO, StringIO
from . import *
from .nbts import TAGLIST,NBTFile
import re

class TokenError(Exception): pass

NumbersReg = [
        (TAG_Byte,   re.compile(r"^-?[0-9]+[Bb]$"),         int),
        (TAG_Short,  re.compile(r"^-?[0-9]+[Ss]$"),         int),
        (TAG_Int,    re.compile(r"^-?[0-9]+$"),             int),
        (TAG_Long,   re.compile(r"^-?[0-9]+[Ll]$"),         int),
        (TAG_Float,  re.compile(r"^-?[0-9]+\.[0-9]+[Ff]$"), float),
        (TAG_Double, re.compile(r"^-?[0-9]+\.[0-9]+$"),     float)
    ]

# 定义Token类型
TOKEN_SPECIFICATION = [
    ('Byte',     r'-?[0-9]{1,3}[Bb]'),
    ('Short',    r'-?[0-9]{1,5}[Ss]'),
    ('Int',      r'-?[0-9]{1,10}(?!\w|\.)'),
    ('Long',     r'-?[0-9]{1,19}[Ll]'),
    ('Float',    r'-?[0-9]{1,25}(?:\.[0-9]{1,25})?[Ff]'),
    ('Double',   r'-?[0-9]{1,25}(?:\.[0-9]{1,25})?(?!\w)'),
    ('String',   r'"(?:[^"]|\\")*"'),
    ('Colon',    r':'),
    ('Comma',    r','),
    ('SemiColon',r';'),
    ('Lbrace',   r'\{'),
    ('Rbrace',   r'\}'),
    ('Lbracket', r'\['),
    ('Rbracket', r'\]'),
    ('Key',      r'\w+'),
    ('WS',       r'[ \t]+'),
    ('Comment',  r'//.*\n|/\*(?:.|\n)*\*/'),
    ('Error',    r'.')
]
TAB = "    "
TokenRegex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
TokenRe = re.compile(TokenRegex)


# 读取部分
class TokenIO(list):
    def read(self, Number=1):
        if not hasattr(self, "Index"):
            self.Index = 0
        Token = self[self.Index]
        self.Index += Number
        return Token
    
    def GetTest(self, Number=0):
        if not hasattr(self, "Index"):
            self.Index = 0
        try:
            return self[self.Index + Number]
        except IndexError:
            return Token(None, None, None, None)

class Token:
    def __init__(self, Type, Value, Pos, CodeString):
        self.Type = Type
        self.Value = Value
        self.Pos = Pos
        self.CodeString = CodeString
    
    def __repr__(self):
        return self.Type + ": " + self.Value + "\n"
    
    def ThrowError(self, List, ErrorText="意外的字符"):
        Line, Pos = GetLine(self.CodeString[0], self.Pos)
        raise TokenError(ErrorText + " %s 位于 %s 行 第%s个字符 到 第%s个字符, 应该为: %s" % 
            (self.Value, Line, Pos[0], Pos[1], List))

def GetLine(Code, Pos):
    Length = Pos[1] - Pos[0]
    Lines = Code[0: Pos[0] + 1].splitlines()
    Pos2 = len(Lines[-1])
    return len(Lines), (Pos2, Pos2 + Length)

def Lexer(Text):
    CodeString = [Text]
    Tokens = TokenIO()
    for mo in TokenRe.finditer(Text):
        Type = mo.lastgroup
        Value = mo.group()
        if Type in ['WS', 'Comment']:
            continue
        elif Type == "Error":
            TokenError("意外的字符 %s 位于 %s 到 %s" % (Value, mo.pos,mo.endpos))
        elif Type:
            Pos = (mo.start(), mo.end())
            Tokens.append(Token(Type, Value, Pos, CodeString))
    return Tokens

def Parser(Tokens):
    if Tokens[0].Type in ["Key", "Int"]:
        Tokens.read(2)
        NBT = ParserSnbt(Tokens)
        NBT.name = Tokens[0]
        return NBT
    else:
        return ParserSnbt(Tokens)

def ParserSnbt(Tokens):
    Token, NBT = Tokens.read(), None
    if Token.Type == "Lbrace":
        NBT = ParserCompound(Tokens)
    elif Token.Type == "Lbracket":
        if Tokens.GetTest().Type == "Key" and Tokens.GetTest(1).Value == ";":
            NBT = ParserArray(Tokens)
        else:
            NBT = ParserList(Tokens)
    elif Token.Type in ["Byte", "Short", "Int", "Long", "Float", "Double"]:
        NBT = ParserNumbers(Token)
    elif Token.Type == "String":
        NBT = ParserString(Token)
    elif Token.Value in ["true", "false"]:
        NBT = ParserNumbers(Token)
    else:
        Token.ThrowError(["{", "[", "true", "false", "数字", "字符串"])
    return NBT

def ParserNumbers(Token):
    for Regex in NumbersReg:
        if Regex[1].match(Token.Value):
            return Regex[0](Regex[2](re.sub(r"[BbSsLlFf]", '', Token.Value)))
    if Token.Value == "true":  return TAG_Byte(1)
    elif Token.Value == "false": return TAG_Byte(0)
    raise TypeError("未知的数字类型 %s" % Token.Type)

def ParserString(Token):
    String = Token.Value.replace(r'\"', '"')[1:-1]
    return TAG_String(String)

def ParserArray(Tokens):
    Token, Type = Tokens.read(), None
    if Token.Value == "B":
        Type = (TAG_Byte_Array, "TAG_Byte")
    elif Token.Value == "I":
        Type = (TAG_Int_Array, "TAG_Int")
    elif Token.Value == "L":
        Type = (TAG_Long_Array, "TAG_Long")
    else:
        Token.ThrowError(["B", "I", "L"], "错误的Array类型")
    NBT = Type[0]()
    Tokens.read()
    Token = Tokens.GetTest()
    if Token.Type == "Rbracket":
        Tokens.read()
        return NBT
    while True:
        try:
            NBT.append(ParserSnbt(Tokens))
        except TypeError:
            Tokens.GetTest(-1).ThrowError([Type[1]], "错误的类型")
        except ValueError:
            Tokens.GetTest(-1).ThrowError([Type[1] + "的数值范围"], "错误的数值范围")
        Token = Tokens.read()
        if Token.Type == "Comma":
            continue
        elif Token.Type == "Rbracket":
            break
        else:
            Token.ThrowError([",", "]"])
    return NBT

def ParserCompound(Tokens):
    NBT = TAG_Compound()
    Token = Tokens.GetTest()
    if Token.Type == "Rbrace":
        Tokens.read()
        return NBT
    while True:
        Token = Tokens.read()
        if Token.Type in ["Key", "Int"]:
            Key = Token.Value
            Token = Tokens.read()
            if Token.Type == "Colon":
                NBT[Key] = ParserSnbt(Tokens)
                Token = Tokens.read()
                if Token.Type == "Comma":
                    continue
                elif Token.Type == "Rbrace":
                    break
                else:
                    Token.ThrowError([",", "}"])
            else:
                Token.ThrowError([":"])
        else:
            Token.ThrowError(["Key"])
    return NBT

def ParserList(Tokens):
    NBT = TAG_List()
    Token = Tokens.GetTest()
    if Token.Type == "Rbracket":
        Tokens.read()
        return NBT
    while True:
        try:
            NBT.append(ParserSnbt(Tokens))
        except TypeError:
            Type = list(TAGLIST.values())[NBT.tagID].__name__
            Tokens.GetTest(-1).ThrowError([Type], "错误的类型")
        except ValueError:
            Type = list(TAGLIST.values())[NBT.tagID].__name__
            Tokens.GetTest(-1).ThrowError([Type + "的数值范围"], "错误的数值范围")
        Token = Tokens.read()
        if Token.Type == "Comma":
            continue
        elif Token.Type == "Rbracket":
            break
        else:
            Token.ThrowError([",", "]"])
    return NBT


# 写入部分
def GetSnbt(Tag, snbt, Formatting=False, indent=0):
    if isinstance(Tag, (TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float, TAG_Double)):
        TagNumbers(Tag, snbt)
    elif isinstance(Tag, TAG_String):
        TagString(Tag, snbt)
    elif isinstance(Tag, (TAG_Byte_Array, TAG_Int_Array, TAG_Long_Array)):
        TagArray(Tag, snbt, Formatting, indent)
    elif isinstance(Tag, TAG_List):
        TagList(Tag, snbt, Formatting, indent)
    elif isinstance(Tag, TAG_Compound):
        TagCompound(Tag, snbt, Formatting, indent)
    else:
        raise TypeError("未知的类型 %s" % Tag)
    return snbt

def TagNumbers(Tag, snbt):
    if Tag.id == 1: snbt.write(  '%sb' % int(Tag.value))
    elif Tag.id == 2: snbt.write('%ss' % int(Tag.value))
    elif Tag.id == 3: snbt.write('%s'  % int(Tag.value))
    elif Tag.id == 4: snbt.write('%sl' % int(Tag.value))
    elif Tag.id == 5: snbt.write('%sf' % float(Tag.value))
    elif Tag.id == 6: snbt.write('%s'  % float(Tag.value))
    else: raise TypeError("错误的类型 %s" % Tag.__class__.__name__)

def TagString(Tag, snbt):
    snbt.write('"' + Tag.value.replace('"', '\\"') + '"')

def TagArray(Tag, snbt, Formatting=False, indent=0):
    if Tag.id == 7:
        Type = ("B", "b")
    elif Tag.id == 11:
        Type = ("I", "")
    elif Tag.id == 12:
        Type = ("L", "l")
    else:
        raise TypeError("非期望的类型 %s 应该为 (TAG_Byte_Array, TAG_Int_Array, TAG_Long_Array)" % Tag)
    ListLength = len(Tag)
    if ListLength == 0:
        snbt.write("[%s;]" % Type[0])
        return
    if not Formatting:
        snbt.write("[%s;" % Type[0])
        for Value, index in zip(Tag, range(1, 2_147_483_639)):
            snbt.write("%s%s" % (Value, Type[1]))
            if index == ListLength:
                snbt.write("]")
                break
            else:
                snbt.write(",")
        return
    Line = '\n'
    if ListLength < 16 and len(str([Value for Value in Tag])) < 50:
        Line = ' '
    snbt.write("[")
    if Line == '\n':
        snbt.write('\n')
        snbt.write(TAB * (indent + 1))
        snbt.write("%s;\n" % Type[0])
    else:
        snbt.write("%s; " % Type[0])
    for Value, index in zip(Tag, range(1, 2_147_483_639)):
        if Line == '\n':
            snbt.write(TAB * (indent + 1))
        snbt.write("%s%s" % (Value, Type[1]))
        if index == ListLength:
            if Line == '\n':
                snbt.write('\n')
                snbt.write(TAB * indent)
            snbt.write("]")
            break
        else:
            snbt.write("," + Line)

def TagList(Tag, snbt, Formatting=False, indent=0):
    ListLength = len(Tag)
    if ListLength == 0:
        snbt.write("[]")
        return
    if not Formatting:
        snbt.write("[")
        for Value, index in zip(Tag, range(1, 2_147_483_639)):
            GetSnbt(Value, snbt)
            if index == ListLength:
                snbt.write("]")
                break
            else:
                snbt.write(",")
        return
    Line = '\n'
    if Tag.tagID in [0, 1, 2, 3, 4, 5, 6, 8] and ListLength < 16:
        if len(str([SubTag.value for SubTag in Tag])) < 50:
            Line = ' '
    snbt.write("[")
    if Line == '\n':
        snbt.write('\n')
    for Value, index in zip(Tag, range(1, 2_147_483_639)):
        if Line == '\n':
            snbt.write(TAB * (indent + 1))
        GetSnbt(Value, snbt, Formatting, indent + 1)
        if index == ListLength:
            if Line == '\n':
                snbt.write('\n')
                snbt.write(TAB * indent)
            snbt.write("]")
            break
        else:
            snbt.write("," + Line)

def TagCompound(Tag, snbt, Formatting=False, indent=0):
    CompoundLength = len(Tag)
    if CompoundLength == 0:
        snbt.write("{}")
        return
    if not Formatting:
        snbt.write("{")
        for Key, index in zip(Tag, range(1, 2_147_483_639)):
            snbt.write(Key + ":")
            GetSnbt(Tag[Key], snbt)
            if index == CompoundLength:
                snbt.write("}")
                break
            else:
                snbt.write(",")
        return
    snbt.write("{\n")
    for Key, index in zip(Tag, range(1, 2_147_483_639)):
        snbt.write(TAB * (indent + 1))
        snbt.write(Key + ": ")
        GetSnbt(Tag[Key], snbt, Formatting, indent + 1)
        if index == CompoundLength:
            snbt.write("\n")
            snbt.write(TAB * indent)
            snbt.write("}")
            break
        else:
            snbt.write(",\n")



def read_from_snbt_file(File: Union[str, bytes, StringIO]):
    if isinstance(File, str):
        with open(File, "r") as SnbtFile:
            snbt = SnbtFile.read()
    elif isinstance(File, bytes):
        snbt = File.decode("utf-8")
    elif isinstance(File, StringIO):
        snbt = File.read()
    else:
        raise TypeError("期望的类型为 (str, bytes, StringIO), 但传入了 %s" % 
            type(File))
    if not snbt:
        raise ValueError("空的字符串")
    Tokens = Lexer(snbt)
    NBT = Parser(Tokens)
    return NBT

def write_to_snbt_file(
    File      : Union[str, StringIO],
    Tag       : Union[NBTFile,TAG_Compound],
    Formatting: bool=False):
    if isinstance(File, str): File = open(File, "w")
    if not isinstance(Tag, (TAG_Compound, TAG_List)):
        raise TypeError("期望类型为 (TAG_Compound, TAG_List)，但传入了 %s" % 
            Tag.__class__.__name__)
    if Tag.name:
        File.write(Tag.name + ':')
    GetSnbt(Tag, File, Formatting)
    try: File.flush()
    except (AttributeError, IOError): pass
    try: File.close() if isinstance(File, str) else None
    except (AttributeError, IOError): pass

def format_snbt(String: str):
    Tokens = Lexer(String)
    NBT = Parser(Tokens)
    SNBT = StringIO()
    write_to_snbt_file(SNBT, NBT, True)
    return SNBT.read()

def comperss_snbt(String: str):
    Tokens = Lexer(String)
    NBT = Parser(Tokens)
    SNBT = StringIO()
    write_to_snbt_file(SNBT, NBT, False)
    return SNBT.read()