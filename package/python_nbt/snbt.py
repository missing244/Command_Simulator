"""
    snbt.py - snbt处理相关
"""


from enum import Enum
from collections import deque
from functools import lru_cache
import re

from . import TAGLIST, TAG, codec as ce
from .error import *

TOKEN_SPECIFICATION = [
    ('Int',     r'-?[0-9]+[BbSsLl]?(?![0-9a-zA-Z+\-\._])'),
    ('Float',   r'-?(?:\.?[0-9]+|[0-9]+\.(?:[0-9]+)?)[FfdD]?'),
    ('SString', r'"(?:\\"|[^"])*"'),
    ('DString', r"'(?:\\'|[^'])*'"),
    ('Symbol',  r':|,|;|\{|\}|\[|\]'),
    ('Key',     r'[0-9a-zA-Z+\-\._]+'),
    ('WS',      r'[ \t\n]+'),
    ('Comment', r'//.*\n|/\*(?:.|\n)*\*/'),
    ('Error',   r'[^0-9a-zA-Z+\-\._ \t\n]+'),
]
TokenRe = re.compile('|'.join('(?P<%s>%s)' % i for i in TOKEN_SPECIFICATION))


class SnbtIO:
    def __init__(self, code):
        self.tokens = Tokenizer(code)
        self.code = code

    def parse_key(self, token):
        type = token[0]
        if type in {"Int","Float","Key"}:
            return token[1]
        elif type in {"SString","DString"}:
            return ce.string_to_str(token[1])
        else:
            raise SnbtParseError("非期望的字符('%s')类型 %s 位于%s行 第%s个字符到第%s个字符 应为一个 key" % (token[1], type, *get_line(self.code, token[2])))

    def parse_value(self, token):
        if token[0] == "Int" or token[0] == "Float":
            try:
                res = self.parse_number(token[0], token[1])
                if res is None: return TAGLIST[TAG.STRING](token[1])
                else: return res
            except:
                return TAGLIST[TAG.STRING](token[1])
        elif token[0] == "SString" or token[0] == "DString":
            try:
                return TAGLIST[TAG.STRING](ce.string_to_str(token[1]))
            except ValueError as e:
                raise SnbtParseError("%s 位于第%s行 第%s个字符到第%s个字符" % (e.args[0], *get_line(self.code, token[2])))
        elif token[1] == "{":
            return TAGLIST[TAG.COMPOUND]._from_snbtIO(self)
        elif token[1] == "[":
            return TAGLIST[TAG.LIST]._from_snbtIO(self)
        elif token[1] == "true":
            return TAGLIST[TAG.BYTE](1)
        elif token[1] == "false":
            return TAGLIST[TAG.BYTE](0)
        else:
            self.throw_error(token, "数字，字符串，复合，列表，数组")

    @lru_cache(maxsize=None)
    def parse_number(self, Type, Value):
        if Value[-1] == "b" or Value[-1] == "B":
            return TAGLIST[TAG.BYTE](int(Value[0:-1]))
        elif Value[-1] == "s" or Value[-1] == "S":
            return TAGLIST[TAG.SHORT](int(Value[0:-1]))
        elif Value[-1] == "l" or Value[-1] == "L":
            return TAGLIST[TAG.LONG](int(Value[0:-1]))
        elif Value[-1] == "f" or Value[-1] == "F":
            return TAGLIST[TAG.FLOAT](float(Value[0:-1]))
        elif Value[-1] == "d" or Value[-1] == "D":
            return TAGLIST[TAG.DOUBLE](float(Value[0:-1]))
        elif Type == "Int":
            return TAGLIST[TAG.INT](int(Value))
        elif Type == "Float":
            return TAGLIST[TAG.DOUBLE](float(Value))
        else:
            return None

    @lru_cache(maxsize=None)
    def parse_py_number(self, Type, Value):
        if Value[-1] in "bBsSlL":
            return int(Value[0:-1])
        elif Value[-1] == "fFdD":
            return float(Value[0:-1])
        elif Type == "Int":
            return int(Value)
        elif Type == "Float":
            return float(Value)
        else:
            return None

    def close(self):
        try:
            item = next(self.tokens)
        except StopIteration:
            return True
        else:
            raise SnbtParseError("语法分析已完成，末尾(%s行 %s到%s个字符)有多余字符" % get_line(self.code, item[2]))

    def read(self, number=0):
        if number < 0: raise ValueError("非法值 %s" % number)
        if number == 0:
            res = deque()
            try:
                while True: res.append(self._read_one())
            except SnbtTokenError:
                return tuple(res)
        if number == 1:
            return self._read_one()
        if number == 2:
            return (self._read_one(), self._read_one())
        else:
            res = deque()
            for _ in range(number):
                res.append(self._read_one())
            return tuple(res)

    def _read_one(self):
        try:
            return next(self.tokens)
        except StopIteration:
            raise SnbtTokenError("词法分析时到达末尾")

    def throw_error(self, token, value=""):
        raise SnbtParseError("非期望的字符 '%s' 位于%s行 第%s个字符到第%s个字符 应为 %s" % (token[1], *get_line(self.code, token[2]), value))
    
    def __enter__(self):
        return self
    
    def __exit__(self, a, b, c):
        self.close()
        


def Tokenizer(code):
    for mo in TokenRe.finditer(code):
        type = mo.lastgroup
        value = mo.group()
        if type in ['WS', 'Comment']:
            continue
        elif type == "Error":
            raise SnbtTokenError("意外的字符 %s 位于%s行 第%s个字符到第%s个字符" % (value, *get_line(code, (mo.start(), mo.end()))))
        elif type:
            yield (type, value, mo.span())

def get_line(Code, Pos):
    Length = Pos[1] - Pos[0]
    Lines = Code[0: Pos[0] + 1].splitlines()
    Pos2 = len(Lines[-1])
    return len(Lines), Pos2, Pos2 + Length
