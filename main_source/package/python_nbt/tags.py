"""
    tags.py - nbt的所有标签
"""


from typing import Literal, Union
from io import BytesIO, StringIO, IOBase
from array import array
from math import ceil
from collections import deque

from . import TAGLIST, TAG, codec as ce
from .snbt import SnbtIO, get_line
from .error import *
from .abc import *

class TAG_Number(TAG_Base_Number):
    type = None
    unit = None
    
    def __init__(self, value: Union[int, float, 'TAG_Number']=0) -> None:
        self.__value = value
        self.__snbt_cache = f"{value}{self.unit}"

    @classmethod
    def _from_bytes(cls, buffer, mode=False):
        return cls(ce.unpack_data(buffer, cls.type, mode)[0])

    @classmethod
    def _from_bytesIO(cls, buffer, mode=False):
        length = ce.number_bytes_len[cls.type]
        byte = buffer_read(buffer, length, "数字")
        try:
            return cls._from_bytes(byte, mode)
        except Exception as e:
            throw_nbt_error(e, buffer, length)

    @classmethod
    def _from_snbt(cls, buffer):
        with SnbtIO(buffer) as buffer:
            return cls._from_snbtIO(buffer)

    @classmethod
    def _from_snbtIO(cls, buffer):
        token = buffer._read_one()
        value = buffer.parse_value(token)
        if value.type == cls.type:
            return value
        else:
            buffer.throw_error(token, "%s数字" % cls.type)

    def get_value(self) -> Union[int, float]:
        return self.__value

    def set_value(self, value) -> None:
        raise AttributeError("不能调用的方法")
    
    def _to_snbt(self):
        return self.__snbt_cache
    
    def _to_snbt_format(self, buffer, indent, size):
        buffer.write(self.__snbt_cache)
    
    def to_bytes(self, mode: bool=False) -> bytes:
        return ce.pack_data(self.__value, self.type, mode)

    def get_info(self, a: bool=0) -> str:
        return f'{self.__class__.__name__}({self.get_value()})'

    def copy(self) -> 'TAG_Number':
        return self

    def __repr__(self) -> str:
        return f"<{self.type} value={self.__value} bytes={self.to_bytes()} at 0x{id(self)}>"


class TAG_Array(TAG_Base_Array):
    _type = None
    type = None
    unit = None
    range = None
    
    def __init__(self, value: Union[list, array, 'TAG_List', 'TAG_Compound', 'TAG_ByteArray', 'TAG_IntArray', 'TAG_LongArray']=None):
        self.__value = array(self.unit[2])
        if value is None: return
        self.set_value(value)

    @classmethod
    def _from_bytes(cls, buffer, mode=False):
        return cls._from_bytesIO(BytesIO(buffer), mode)

    @classmethod
    def _from_bytesIO(cls, buffer, mode=False):
        byte = buffer_read(buffer, 4, "数组元素个数")
        try:
            count = ce.unpack_data(byte, TAG.INT, mode)[0]
        except Exception as e:
            throw_nbt_error(e, buffer, 4)
        length = ce.number_bytes_len[cls._type]
        size = count * length
        byte = buffer_read(buffer, size, "数组元素")
        array = cls()
        try:
            array.__value.frombytes(byte)
        except Exception as e:
            throw_nbt_error(e, buffer, size)
        if mode: array.__value.byteswap()
        return array

    @classmethod
    def _from_snbt(cls, buffer):
        with SnbtIO(buffer) as buffer:
            if not (token:=buffer._read_one())[1] == "[": buffer.throw_error(token, "{")
            if not (token:=buffer._read_one())[1] == cls.unit[0]: buffer.throw_error(token, cls.unit[0])
            if not (token:=buffer._read_one())[1] == ";": buffer.throw_error(token, ";")
            return cls._from_snbtIO(buffer)

    @classmethod
    def _from_snbtIO(cls, buffer):
        token = buffer._read_one()
        if token[1] == "]": return cls()
        res = deque()
        if not token[0] == "Int": buffer.throw_error(token, "整数")
        if not cls.unit[1] in token[1]: buffer.throw_error(token, "%s的单位" % cls.__name__)
        res.append(int(token[1].rstrip("bl")))
        while True:
            token = buffer._read_one()
            if token[1] == "]":
                Array = cls()
                Array.__value.fromlist(list(res))
                return Array
            elif token[1] == ",":
                token = buffer._read_one()
                if not token[0] == "Int": buffer.throw_error(token, "整数")
                if not cls.unit[1] in token[1]: buffer.throw_error(token, "%s的单位" % cls.__name__)
                res.append(int(token[1].rstrip("bl")))
            else:
                buffer.throw_error(token, "] ,")

    def _to_snbt(self):
        return f"[{self.unit[0]};" + ','.join([f"{str(i)}{self.unit[1]}" for i in self.__value]) + "]"

    def _to_snbt_format(self, buffer, indent, size):
        count, tab = len(self.__value), " " * size
        if count == 0:
            buffer.write(f"[{self.unit[0]};]")
        elif 1 <= count <= 3:
            buffer.write(f"[{self.unit[0]}; " + ', '.join([f"{str(i)}{self.unit[1]}" for i in self.__value]) + "]")
        else:
            buffer.write(f"[\n{tab * indent}{self.unit[0]};\n")
            for v, i in zip(self.__value, range(1, count + 1)):
                buffer.write(f"{tab * indent}{str(v)}{self.unit[1]}")
                if i < count: buffer.write(",\n")
            buffer.write("\n" + tab * (indent - 1) + "]")

    def to_bytes(self, mode: bool=False) -> bytes:
        if mode: self.__value.byteswap()
        res = ce.pack_data(len(self.__value), TAG.INT, mode) + self.__value.tobytes()
        if mode: self.__value.byteswap()
        return res
    
    def get_value(self) -> array:
        return self.__value
    
    def set_value(self, value: Union[list, array, 'TAG_List', 'TAG_Compound', 'TAG_ByteArray', 'TAG_IntArray', 'TAG_LongArray']) -> None:
        if isinstance(value, list):
            try:
                self.__value = array(self.unit[2]).fromlist(value)
            except Exception as e:
                raise ValueError("尝试从(%s)自动转换数值失败 %s" % (value, e.args[0]))
        elif isinstance(value, (TAG_List, TAG_ByteArray, TAG_IntArray, TAG_LongArray)):
            self.set_value(value.get_value())
        elif isinstance(value, TAG_Compound):
            self.set_value(list(value.get_value().values()))
        elif isinstance(value, array) and value.typecode == self.unit[2]:
            self.__value = value
        elif isinstance(value, array):
            try:
                self.__value = array(self.unit[2]).fromlist(value.tolist())
            except Exception as e:
                raise ValueError("尝试从(%s)自动转换数值失败 %s" % (value, e.args[0]))
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((list, array, TAG_List, TAG_Compound, TAG_ByteArray, TAG_IntArray, TAG_LongArray), value))
    
    def test_value(self, value):
        if isinstance(value, int):
            if self.range[0] <= value <= self.range[1]: return value
            raise ValueError("超出范围(%s)的数字 %s" % (self.range, value))
        elif isinstance(value, (TAG_Byte, TAG_Short, TAG_Int, TAG_Long)):
            if self.range[0] <= value.get_value() <= self.range[1]: return value.get_value()
            raise ValueError("超出范围(%s)的数字 %s" % (self.range, value.get_value()))
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % (
                (int, TAG_Byte, TAG_Short, TAG_Int, TAG_Long), value))

    def get_info(self, ellipsis: bool=False) -> str:
        if ellipsis: return f'{self.__class__.__name__}({len(self)} items)'
        if len(self) <= 10:
            return f'{self.__class__.__name__}(' + ''.join([f'\n    {v}' for v in self]) + '\n)'
        else:
            res = []
            for i in range(5): res.append(f'\n    {self[i]}')
            res.append(f'\n    ...more {len(self) - 10}')
            for i in range(len(self) - 5, len(self)): res.append(f'\n    {self[i]}')
            return f'{self.__class__.__name__}(' + ''.join(res) + '\n)'

    def __repr__(self) -> str:
        return f"<{self.type} count={len(self.__value)} at 0x{id(self)}>"

    def copy(self) -> 'TAG_Array':
        return self.__class__(self)


class TAG_End(TAG_Base_End):
    type = TAG.END


class TAG_Byte(TAG_Number, metaclass=TAG_Number_Meta):
    type = TAG.BYTE
    unit = "b"


class TAG_Short(TAG_Number, metaclass=TAG_Number_Meta):
    type = TAG.SHORT
    unit = "s"


class TAG_Int(TAG_Number, metaclass=TAG_Number_Meta):
    type = TAG.INT
    unit = ""


class TAG_Long(TAG_Number, metaclass=TAG_Number_Meta):
    type = TAG.LONG
    unit = "l"


class TAG_Float(TAG_Number, metaclass=TAG_Number_Meta):
    type = TAG.FLOAT
    unit = "f"


class TAG_Double(TAG_Number, metaclass=TAG_Number_Meta):
    type = TAG.DOUBLE
    unit = "d"


class TAG_String(TAG_Base_String, metaclass=TAG_String_Meta):
    type = TAG.STRING
    
    def __init__(self, value: str=""):
        self.__value = None
        self.__cache = None
        if isinstance(value, str):
            self.__value = ce.pack_data(value, self.type)
            self.__cache = value
        elif isinstance(value, bytes):
            self.__value = value
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((str, bytes), value))

    @classmethod
    def _from_bytes(cls, buffer, mode=False):
        return cls(buffer[2:])

    @classmethod
    def _from_bytesIO(cls, buffer, mode=False):
        byte = buffer_read(buffer, 2, "字符串长度")
        try:
            length = ce.bytes_to_length(byte, mode)
        except Exception as e:
            throw_nbt_error(e, buffer, 2)
        byte = buffer_read(buffer, length, "字符串")
        try:
            return cls(byte)
        except Exception as e:
            throw_nbt_error(e, buffer, length)

    @classmethod
    def _from_snbt(cls, buffer):
        with SnbtIO(buffer) as buffer:
            return cls._from_snbtIO(buffer)

    @classmethod
    def _from_snbtIO(cls, buffer):
        token = buffer._read_one()
        value = buffer.parse_value(token)
        if not value.type == cls.type: buffer.throw_error(token, "字符串")
        return value

    def _to_snbt(self):
        try:
            return self.__snbt_cache
        except:
            self.__snbt_cache = ce.str_to_string(self.get_value())
            return self.__snbt_cache

    def _to_snbt_format(self, buffer, indent, size):
        buffer.write(self._to_snbt())

    def to_bytes(self, mode: bool=False) -> bytes:
        return ce.length_to_bytes(len(self.__value), mode) + self.__value

    def get_value(self) -> str:
        if self.__cache is None:
            self.__cache = ce.unpack_data(self.__value, self.type)
        return self.__cache

    def set_value(self, value):
        raise AttributeError("不能调用的方法")

    def get_info(self, a: bool=0) -> str:
        return f'{self.__class__.__name__}({self.to_snbt()})'

    def copy(self) -> 'TAG_String':
        return self

    def __repr__(self) -> str:
        s = self.get_value()
        b = self.to_bytes()
        s = s if len(s) <= 10 else s[:7] +  '...'
        b = b if len(b) <= 10 else b[:7] + b'...'
        return f"<{self.type} value={s} bytes={b} at 0x{id(self)}>"


class TAG_List(TAG_Base_List):
    type = TAG.LIST
    
    def __init__(self, value: Union[list, 'TAG_List', 'TAG_ByteArray', 'TAG_IntArray', 'TAG_LongArray']=None, type: TAG=TAG.END):
        self.set_type(type)
        if self.__is_number_list:
            self.__value = array(ARRAY_TYPECODE[self.__type])
        else:
            self.__value = []
        if value is None: return
        self.set_value(value)

    @classmethod
    def _from_bytes(cls, buffer, mode=False):
        return cls._from_bytesIO(BytesIO(buffer), mode)

    @classmethod
    def _from_bytesIO(cls, buffer, mode=False):
        byte = buffer_read(buffer, 1, "列表元素类型标签")
        try:
            type = ce.bytes_to_tag_type(byte)
        except Exception as e:
            throw_nbt_error(e, buffer, 1)
        tag = TAGLIST[type]
        byte = buffer_read(buffer, 4, "列表元素数量")
        try:
            count = ce.unpack_data(byte, TAG.INT, mode)[0]
        except Exception as e:
            throw_nbt_error(e, buffer, 4)
        List = cls()
        List.set_type(type)
        if type in list(ARRAY_TYPECODE.keys()):
            res = array(ARRAY_TYPECODE[type])
            length = ce.number_bytes_len[type]
            byte = buffer_read(buffer, count * length, "列表元素内容")
            try:
                res.frombytes(byte)
            except Exception as e:
                throw_nbt_error(e, buffer, length)
            if mode: res.byteswap()
            List.__value = res
        else:
            res = [None] * count
            for i in range(count):
                res[i] = tag._from_bytesIO(buffer, mode)
            List.__value = res
        List.test_type()
        return List

    @classmethod
    def _from_snbt(cls, buffer):
        with SnbtIO(buffer) as buffer:
            if not (token:=buffer._read_one())[1] == "[": buffer.throw_error(token, "[")
            return cls._from_snbtIO(buffer)

    @classmethod
    def _from_snbtIO(cls, buffer):
        res, List, Type, is_number = deque(), cls(), None, False
        token = buffer._read_one()
        if token[1] == "]":
            return cls()
        elif token[1] == "B" and buffer._read_one()[1] == ";":
            return TAG_ByteArray._from_snbtIO(buffer)
        elif token[1] == "I" and buffer._read_one()[1] == ";":
            return TAG_IntArray._from_snbtIO(buffer)
        elif token[1] == "L" and buffer._read_one()[1] == ";":
            return TAG_LongArray._from_snbtIO(buffer)
        value = buffer.parse_value(token)
        res.append(value)
        Type = value.type
        if token[0] == "Int" or token[0] == "Float":
            is_number = True
        while True:
            token = buffer._read_one()
            if token[1] == "]":
                List.set_type(Type)
                if is_number:
                    List.__value = array(ARRAY_TYPECODE[Type])
                    List.__value.fromlist(list(res))
                else:
                    List.__value = list(res)
                return List
            elif not token[1] == ",":
                buffer.throw_error(token, ", ]")
            token = buffer._read_one()
            if is_number:
                value = buffer.parse_py_number(token[0], token[1])
                if value is None: raise SnbtParseError("无法解析的数字 '%s' 位于第%s行 第%s个字符到第%s个字符" % (token[1], *get_line(buffer.code, token[2])))
                res.append(value)
                continue
            value = buffer.parse_value(token)
            if not value.type == Type: buffer.throw_error(token, f"类型:{Type}")
            res.append(value)
                

    def _to_snbt(self):
        if self.__is_number_list:
            return "[" + ','.join([i._to_snbt() for i in self]) + "]"
        else:
            return "[" + ','.join([i._to_snbt() for i in self.__value]) + "]"

    def _to_snbt_format(self, buffer, indent, size):
        count, tab = len(self.__value), " " * size
        if count == 0:
            buffer.write("[]")
            return
        type1 = [TAG.BYTE, TAG.SHORT]
        type2 = [TAG.INT, TAG.LONG, TAG.FLOAT, TAG.DOUBLE]
        type3 = type1 + type2
        if count <= 5:
            if self.__type in type1:
                buffer.write("[" + ', '.join([i._to_snbt() for i in self]) + "]")
                return
            elif self.__type in type3 and count <= 3:
                buffer.write("[" + ', '.join([i._to_snbt() for i in self]) + "]")
                return
            elif self.__type == TAG.STRING and count <= 1:
                buffer.write("[" + ', '.join([i._to_snbt() for i in self]) + "]")
                return
        if count >= 16 and self.__type in type3:
            width  = count ** 0.5
            height = int(width) if int(width) == width else int(width) + 1
            width = ceil(width)
            count2, height2 = count - 1, height - 2
            buffer.write("[\n")
            unit = TAGLIST[self.__type].unit
            try:
                for i in range(height):
                    buffer.write(tab * indent)
                    for k in range(width):
                        index = i * width + k
                        if i >= height2 and index == count2:
                            buffer.write(f"{self.__value[index]}{unit}")
                            raise BreakLoop
                        else:
                            buffer.write(f"{self.__value[index]}{unit}, ")
                    buffer.write("\n")
            except BreakLoop:
                pass
            buffer.write("\n" + tab * (indent - 1) + "]")
        else:
            nbt = self if self.__is_number_list else self.__value
            buffer.write("[\n")
            for v, i in zip(nbt, range(1, count + 1)):
                buffer.write(tab * indent)
                v._to_snbt_format(buffer, indent + 1, size)
                if i < count: buffer.write(",\n")
            buffer.write("\n" + tab * (indent - 1) + "]")

    def to_bytes(self, mode=False) -> bytes:
        byte = None
        if self.__is_number_list:
            if mode: self.__value.byteswap()
            byte = self.__value.tobytes()
            if mode: self.__value.byteswap()
        else:
            byte = b''.join([i.to_bytes(mode) for i in self.__value])
        return ce.tag_type_to_bytes(self.__type)\
             + ce.pack_data(len(self.__value), TAG.INT, mode)\
             + byte
    
    def get_value(self) -> Union[array, list]:
        return self.__value
    
    def set_value(self, value: Union[list, 'TAG_List', 'TAG_ByteArray', 'TAG_IntArray', 'TAG_LongArray']):
        if isinstance(value, list):
            type = None if len(value) else TAG.END
            for v in value:
                if type is None and isinstance(v, TAG_Base): type = v.type
                if not isinstance(v, TAG_Base) or not type == v.type: raise TypeError("TAG_List容器元素期望类型为 %s，但传入了 %s" % (type, v.type))
            self.set_type(type)
            self.test_type()
            self.__value = value.copy()
        elif isinstance(value, array) and value.typecode in ARRAY_TYPECODE.values():
            self.__value = value
            self.set_type({v:k for k, v in ARRAY_TYPECODE.items()}[value.typecode])
            self.test_type()
        elif isinstance(value, TAG_List):
            self.set_type(value.get_type())
            self.test_type()
            self.__value = value.get_value().copy()
        elif isinstance(value, (TAG_ByteArray, TAG_IntArray, TAG_LongArray)):
            self.set_type(value._type)
            self.__value = value.get_value()
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((list, TAG_List, TAG_ByteArray, TAG_IntArray, TAG_LongArray), value))
    
    def get_type(self) -> TAG:
        return self.__type
    
    def set_type(self, type: Union[int, TAG, TAG_Base]) -> None:
        if isinstance(type, int):
            self.__type = TAG(type)
            self.test_type()
        elif isinstance(type, TAG):
            self.__type = type
            self.test_type()
        elif type in list(TAGLIST.values()):
            self.__type = type.type
            self.test_type()
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((tuple([TAG] + list(TAGLIST.values()) + [int])), type))
    
    def test_type(self):
        self.__is_number_list = self.__type in list(ARRAY_TYPECODE.keys())
    
    def test_value(self, value):
        if isinstance(value, tuple(TAGLIST.values())):
            if len(self.__value) == 0:
                self.set_type(value.type)
                self.__value = array(ARRAY_TYPECODE[self.__type]) if self.__is_number_list else []
            if value.type == self.__type:
                return value.get_value() if self.__is_number_list else value
            else:
                raise TypeError("期望类型为 %s，但传入了 %s" % (
                list(TAGLIST.values())[self.__type.value].type, value.type))
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % (
                tuple(TAGLIST.values()), value))

    def get_info(self, ellipsis: bool=False) -> str:
        if ellipsis: return f'{self.__class__.__name__}({len(self)} items)'
        if len(self.__value) <= 10:
            return f'{self.__class__.__name__}(' + ''.join([f'\n    {v.get_info(1)}' for v in self]) + '\n)'
        else:
            res = []
            for i in range(5): res.append(f'\n    {self[i].get_info(1)}')
            res.append(f'\n    ...more {len(self) - 10}')
            for i in range(len(self) - 5, len(self)): res.append(f'\n    {self[i].get_info(1)}')
            return f'{self.__class__.__name__}(' + ''.join(res) + '\n)'

    def value_is_array(self) -> bool:
        return self.__is_number_list

    def copy(self) -> 'TAG_List':
        if self.__is_number_list: return self.__class__(self.__value)
        res = self.__class__()
        res.__value = [v.copy() for v in self.__value]
        return res

    def __repr__(self) -> str:
        return f"<{self.type} type={self.__type} count={len(self.__value)} at 0x{id(self)}>"


class TAG_Compound(TAG_Base_Compound):
    type = TAG.COMPOUND
    
    def __init__(self, value: Union[dict, list, 'TAG_Compound', 'TAG_List', 'TAG_ByteArray', 'TAG_IntArray', 'TAG_LongArray']=None):
        self.__value = {}
        if value is None: return
        self.set_value(value)
    
    @classmethod
    def _from_bytes(cls, buffer, mode=False):
        return cls._from_bytesIO(BytesIO(buffer), mode)

    @classmethod
    def _from_bytesIO(cls, buffer, mode=False):
        compound = cls()
        res = compound.__value = {}
        while True:
            byte = buffer_read(buffer, 1, "标签")
            try:
                if (type := ce.bytes_to_tag_type(byte)) == TAG.END: break
            except Exception as e:
                throw_nbt_error(e, buffer, 1)
            byte = buffer_read(buffer, 2, "复合键名长度")
            try:
                length = ce.bytes_to_length(byte, mode)
            except Exception as e:
                throw_nbt_error(e, buffer, 2)
            byte = buffer_read(buffer, length, "复合键名")
            try:
                key = ce.unpack_data(byte, TAG.STRING)
            except Exception as e:
                throw_nbt_error(e, buffer, length)
            res[key] = TAGLIST[type]._from_bytesIO(buffer, mode)
        return compound

    @classmethod
    def _from_snbt(cls, buffer):
        with SnbtIO(buffer) as buffer:
            if not (token:=buffer._read_one())[1] == "{": buffer.throw_error(token, "{")
            return cls._from_snbtIO(buffer)

    @classmethod
    def _from_snbtIO(cls, buffer):
        compound = cls()
        res = compound.__value = {}
        token = buffer._read_one()
        if token[1] == "}": return cls()
        key = buffer.parse_key(token)
        if not buffer._read_one()[1] == ":": buffer.throw_error(token, ":")
        res[key] = buffer.parse_value(buffer._read_one())
        while True:
            token = buffer._read_one()
            if token[1] == "}": return compound
            elif not token[1] == ",": buffer.throw_error(token, ", }")
            key = buffer.parse_key(buffer._read_one())
            if not buffer._read_one()[1] == ":": buffer.throw_error(token, ":")
            res[key] = buffer.parse_value(buffer._read_one())

    def _to_snbt(self):
        return '{' + ','.join([f'{ce.str_to_snbt_key(k)}:{v._to_snbt()}' for k, v in self.__value.items()]) + '}'
    
    def _to_snbt_format(self, buffer, indent, size):
        count, tab, items = len(self.__value), " " * size, self.__value.items()
        if count == 0:
            buffer.write("{}")
        elif count == 1 and list(items)[0][1].type in [TAG.BYTE, TAG.SHORT, TAG.INT, TAG.FLOAT, TAG.DOUBLE]:
            buffer.write("{" + f"{ce.str_to_snbt_key(list(items)[0][0])}: {list(items)[0][1]._to_snbt()}" + "}")
        else:
            buffer.write("{\n")
            for (k, v), i in zip(self.__value.items(), range(1, count + 1)):
                buffer.write(f"{indent * tab}{ce.str_to_snbt_key(k)}: ")
                v._to_snbt_format(buffer, indent + 1, size)
                if i < count: buffer.write(",\n")
            buffer.write("\n" + tab * (indent - 1) + "}")
    
    def to_bytes(self, mode: bool=False) -> bytes:
        res = bytearray()
        for k, v in self.__value.items():
            name = ce.pack_data(k, TAG.STRING)
            res.extend(ce.tag_type_to_bytes(v.type))
            res.extend(ce.length_to_bytes(len(name), mode))
            res.extend(name)
            res.extend(v.to_bytes(mode))
        res.extend(ce.tag_type_to_bytes(TAG.END))
        return bytes(res)
    
    def get_value(self) -> dict:
        return self.__value
    
    def set_value(self, value: Union[dict, list, 'TAG_Compound', 'TAG_List', 'TAG_ByteArray', 'TAG_IntArray', 'TAG_LongArray']):
        if isinstance(value, TAG_Compound):
            self.__value = value.get_value()
        elif isinstance(value, dict):
            if not all(isinstance(k, str) and isinstance(v, TAG_Base) for k, v in value.items()):
                raise TypeError("dict内含非期望类型：%s" % repr(value))
            self.__value = value
        elif isinstance(value, list):
            pass
        elif isinstance(value, TAG_List):
            pass
        elif isinstance(value, (TAG_ByteArray, TAG_IntArray, TAG_LongArray)):
            pass
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((dict, list, TAG_Compound, TAG_List, TAG_ByteArray, TAG_IntArray, TAG_LongArray), value))
    
    def _test_key(self, key):
        if not isinstance(key, str): raise TypeError("Compound键的期望类型为 %s，但传入了 %s" % (str, key))
    
    def _test_value(self, value):
        if not isinstance(value, TAG_Base): raise TypeError("Compound值的期望类型为 %s，但传入了 %s" % (tuple(TAGLIST.values()), value))

    def get_info(self, ellipsis: bool=False) -> str:
        if ellipsis: return f'{self.__class__.__name__}({len(self)} items)'
        if len(self.__value) <= 10:
            return f'{self.__class__.__name__}(' + ''.join([f'\n    {k}: {v.get_info(1)}' for k, v in self.items()]) + '\n)'
        else:
            res = []
            for i, (k, v) in zip(range(5), self.items()):           res.append(f'\n    {k}: {v.get_info(1)}')
            for i, (k, v) in zip(range(5), reversed(self.items())): res.insert(5, f'\n    {k}: {v.get_info(1)}')
            res.insert(5, f'\n    ...more {len(self) - 10}')
            return f'{self.__class__.__name__}(' + ''.join(res) + '\n)'

    def copy(self) -> None:
        res = self.__class__()
        res.__value = {k: v.copy() for k, v in self.__value.items()}
        return res

    def __repr__(self) -> str:
        return f"<{self.type} count={len(self.__value)} at 0x{id(self)}>"


class TAG_ByteArray(TAG_Array):
    _type = TAG.BYTE
    type = TAG.BYTE_ARRAY
    unit = ("B", "b", "b")
    range = (-128, 127)


class TAG_IntArray(TAG_Array):
    _type = TAG.INT
    type = TAG.INT_ARRAY
    unit = ("I", "", "i")
    range = (-2147483648, 2147483647)


class TAG_LongArray(TAG_Array):
    _type = TAG.LONG
    type = TAG.LONG_ARRAY
    unit = ("L", "l", "q")
    range = (-9223372036854775808, 9223372036854775807)
