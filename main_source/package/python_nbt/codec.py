"""
    codec.py - 编码与解码工具
"""


import re
from struct import Struct
from typing import Union
from . import TAG
from functools import lru_cache
from json import loads, dumps
from .error import *

number_struct_formats = {
    TAG.BYTE  : (Struct('>b'), Struct('<b')),
    TAG.SHORT : (Struct('>h'), Struct('<h')),
    TAG.INT   : (Struct('>i'), Struct('<i')),
    TAG.LONG  : (Struct('>q'), Struct('<q')),
    TAG.FLOAT : (Struct('>f'), Struct('<f')),
    TAG.DOUBLE: (Struct('>d'), Struct('<d')),
}

tag_type_bytes = {
    b'\x00': TAG.END,
    b'\x01': TAG.BYTE,
    b'\x02': TAG.SHORT,
    b'\x03': TAG.INT,
    b'\x04': TAG.LONG,
    b'\x05': TAG.FLOAT,
    b'\x06': TAG.DOUBLE,
    b'\x07': TAG.BYTE_ARRAY,
    b'\x08': TAG.STRING,
    b'\x09': TAG.LIST,
    b'\x0a': TAG.COMPOUND,
    b'\x0b': TAG.INT_ARRAY,
    b'\x0c': TAG.LONG_ARRAY,
}

number_bytes_len = {
    TAG.BYTE  : 1,
    TAG.SHORT : 2,
    TAG.INT   : 4,
    TAG.LONG  : 8,
    TAG.FLOAT : 4,
    TAG.DOUBLE: 8,
}

string_to_str_rule = {
    '\\\\': '\\',
    '\\"' : '"',
    "\\'" : "'",
    "\\n" : "\n",
    "\\r" : "\r",
}

bytes_tag_type = {v: k for k, v in tag_type_bytes.items()}

length_bytes_formats = {False:Struct('<H'), True:Struct('>H')}

str_snbt_key = re.compile(r"^[a-zA-Z0-9_+-.]*$")

string_to_str_re = re.compile(r'(?i)\\u[a-fA-F0-9]{4}|\\.')


@lru_cache(maxsize=None)
def pack_data(data: Union[int, float, str], data_type: TAG, mode=False) -> bytes:
    if data_type in [TAG.END, TAG.LIST, TAG.COMPOUND, TAG.BYTE_ARRAY, TAG.INT_ARRAY, TAG.LONG_ARRAY]:
        raise TypeError("仅支持数字，字符串类型")
    
    if data_type in [TAG.BYTE, TAG.SHORT, TAG.INT, TAG.LONG]:
        if not isinstance(data, int):
            raise TypeError("数据类型非数字")
        try:
            return number_struct_formats[data_type][not mode].pack(data)
        except:
            raise ValueError("数字范围不正确")
    if data_type in [TAG.FLOAT, TAG.DOUBLE]:
        if not isinstance(data, (float, int)):
            raise TypeError("数据类型非数字")
        try:
            return number_struct_formats[data_type][not mode].pack(data)
        except:
            raise ValueError("数字范围不正确")
    if data_type in [TAG.STRING]:
        if not isinstance(data, str):
            raise TypeError("数据类型非字符串")
        try:
            return data.encode('utf-8')
        except:
            raise ValueError("编码错误")
    
    raise TypeError("期望类型为 %s，但传入了 %s" % (TAG, data_type.__class__))

@lru_cache(maxsize=None)
def unpack_data(data: bytes, data_type: TAG, mode=False) -> Union[int, float, str]:
    if data_type in [TAG.END, TAG.LIST, TAG.COMPOUND, TAG.BYTE_ARRAY, TAG.INT_ARRAY, TAG.LONG_ARRAY]:
        raise TypeError("仅支持数字，字符串类型")
    
    if not isinstance(data, bytes):
        raise TypeError("数据类型非bytes")
    
    if data_type in [TAG.BYTE, TAG.SHORT, TAG.INT, TAG.LONG]:
        try:
            return number_struct_formats[data_type][not mode].unpack(data)
        except:
            raise ValueError("格式不正确")
    if data_type in [TAG.FLOAT, TAG.DOUBLE]:
        try:
            return number_struct_formats[data_type][not mode].unpack(data)
        except:
            raise ValueError("格式不正确")
    if data_type in [TAG.STRING]:
        try:
            return data.decode('utf-8')
        except:
            try:
                return data.decode(encoding='utf-8', errors='ignore')
            except:
                raise ValueError("编码错误")
    
    raise TypeError("期望类型为 %s，但传入了 %s" % (TAG, data_type.__class__))

def bytes_to_tag_type(data: bytes) -> TAG:
    if not isinstance(data, bytes):
        raise TypeError("类型错误")
    return tag_type_bytes[data]

def tag_type_to_bytes(data: TAG) -> TAG:
    if not isinstance(data, TAG):
        raise TypeError("类型错误")
    return bytes_tag_type[data]

def bytes_to_length(data: bytes, mode=False) -> int:
    return length_bytes_formats[mode].unpack(data)[0]

def length_to_bytes(data: int, mode=False) -> bytes:
    return length_bytes_formats[mode].pack(data)

def str_to_snbt_key(data: str) -> str:
    if data == '':
        return '""'
    if str_snbt_key.fullmatch(data):
        return data
    else:
        if   '"' in     data and "'" in     data:
            return '"' + data.replace('"', '\\"') + '"'
        elif '"' in     data and "'" not in data:
            return "'" + data + "'"
        elif '"' not in data and "'" in     data:
            return '"' + data + '"'
        elif '"' not in data and "'" not in data:
            return '"' + data + '"'

def str_to_string(data: str) -> str:
    return dumps(data)

def string_to_str(data: str) -> str:
    def replace_string_to_str(m):
        s = m.group(0)
        if s[0:2] == "\\u":
            return s
        else:
            res = string_to_str_rule.get(s, None)
        if res is None:
            raise ValueError("字符串内(%s到%s个字符)存在无法解析的转义符 '%s'" % (data.find(s), data.find(s) + len(s), s))
        else:
            return res
    return string_to_str_re.sub(replace_string_to_str, data[1:-1])
