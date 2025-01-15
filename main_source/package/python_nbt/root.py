"""
    root.py - 根标签相关
"""


from typing import Literal, Union
from io import StringIO, BytesIO, IOBase, RawIOBase, BufferedIOBase, TextIOBase
import zlib, gzip, os

from .error import *
from . import tags, snbt, codec as ce, TAG, TAGLIST

def is_text_io(buffer):
    if not isinstance(buffer, TextIOBase):
        raise NbtBufferError("不符合要求(字符串流)的数据(%s)" % buffer)

def is_byte_io(buffer):
    if not isinstance(buffer, (RawIOBase, BufferedIOBase)):
        raise NbtBufferError("不符合要求(二进制流)的数据(%s)" % buffer)

def is_writ_io(buffer):
    if not buffer.writable():
        raise NbtBufferError("不符合要求(写入流)的数据(%s)" % buffer)

def is_read_io(buffer):
    if not buffer.readable():
        raise NbtBufferError("不符合要求(读取流)的数据(%s)" % buffer)

def is_seek_io(buffer):
    if not buffer.seekable():
        raise NbtBufferError("不符合要求(随机读写流)的数据(%s)" % buffer)

def path_is_file(path):
    if not os.path.exists(path): raise NbtFileError("路径('%s')未找到" % path)
    if not os.path.isfile(path): raise NbtFileError("路径('%s')非文件" % path)

def compress_file(data, zip_mode):
    if zip_mode == 'zlib':
        return zlib.compress(data)
    if zip_mode == 'gzip':
        return gzip.compress(data)
    if zip_mode == 'none':
        return data
    
def decompress_buffer(buffer, zip_mode, head_byte=None):
    if zip_mode is None:
        head_byte = buffer.read(2)
        buffer.seek(0)
    if zip_mode == 'zlib' or head_byte == b'\x78\x9C':
        try: return BytesIO(zlib.decompress(buffer.read()))
        except Exception as e: raise NbtFileError("(%s)zlib解压失败: %s" % (buffer, e.args[0]))
    if zip_mode == 'gzip' or head_byte == b'\x1F\x8B':
        try: return BytesIO(gzip.decompress(buffer.read()))
        except Exception as e: raise NbtFileError("(%s)gzip解压失败: %s" % (buffer, e.args[0]))
    else:
        return buffer

def parse_nbt(buffer, mode):
    byte = buffer_read(buffer, 1, "根标签类型")
    try:
        if (type := ce.bytes_to_tag_type(byte)) not in [TAG.COMPOUND, TAG.LIST]:
            raise NbtDataError("数据的根标签必须是TAG_Compound或TAG_List，但实际是 %s" % type)
    except Exception as e:
        throw_nbt_error(e, buffer, 1)
    byte = buffer_read(buffer, 2, "根标签键名长度")
    try:
        length = ce.bytes_to_length(byte, mode)
    except Exception as e:
        throw_nbt_error(e, buffer, 2)
    byte = buffer_read(buffer, length, "根标签键名")
    try:
        root_name = ce.unpack_data(byte, TAG.STRING)
    except Exception as e:
        throw_nbt_error(e, buffer, length)
    tag = TAGLIST[type]._from_bytesIO(buffer, mode)
    return tag, root_name

def render_nbt(tag, root_name, mode):
    res = bytearray()
    name = ce.pack_data(root_name, TAG.STRING)
    res.extend(ce.tag_type_to_bytes(tag.type))
    res.extend(ce.length_to_bytes(len(name), mode))
    res.extend(name)
    res.extend(tag.to_bytes(mode))
    return bytes(res)

def parse_snbt(buffer):
    with snbt.SnbtIO(buffer.read()) as buffer:
        token = buffer._read_one()
        if token[0] in ["Int", "Float", "Key"]:
            root_name = token[1]
            if (token := buffer._read_one())[1] != ":": buffer.throw_error(token, ":")
            token = buffer._read_one()
        elif token[0] in ["SString", "DString"]:
            root_name = ce.string_to_str(token[1])
            if (token := buffer._read_one())[1] != ":": buffer.throw_error(token, ":")
            token = buffer._read_one()
        else:
            root_name = ''
        if token[1] == "{":
            tag = tags.TAG_Compound._from_snbtIO(buffer)
        elif token[1] == "[":
            tag = tags.TAG_List._from_snbtIO(buffer)
        else:
            buffer.throw_error(token, "{ [ root_name")
        return tag, root_name

def render_snbt(tag, root_name, target, format, size):
    if not isinstance(size, int): raise TypeError("缩进期望类型为 %s，但传入了 %s" % (int, size.__class__))
    if not 1 <= size <= 16: raise ValueError("超出范围(1 ~ 16)的数字 %s" % size)
    if not format:
        target.write(f'{ce.str_to_snbt_key(root_name)}:{tag._to_snbt()}')
    else:
        target.write(f'{ce.str_to_snbt_key(root_name)}: ')
        tag._to_snbt_format(target, 1, size)
    return target


class RootNBT:
    def __init__(self, tag=None, root_name=""):
        self.set_tag(tags.TAG_Compound() if tag is None else tag)
        self.set_root_name(root_name)

    # === nbt ===
    @classmethod
    def from_nbt(cls,
        data     : Union[str, bytes, IOBase],
        zip_mode : Literal['none', 'gzip', 'zlib'] = None,
        byteorder: Literal['little', 'big'] = 'little'):
        if isinstance(data, str):
            path_is_file(data)
            data = open(data, 'rb')
        if isinstance(data, bytes):
            data = BytesIO(data)
        is_byte_io(data) and is_read_io(data) and is_seek_io(data)
        data = decompress_buffer(data, zip_mode)
        return cls(*parse_nbt(data, byteorder == 'big'))
    
    def to_nbt(self,
        target   : Union[str, IOBase] = None,
        zip_mode : Literal['none', 'gzip', 'zlib'] = 'none',
        byteorder: Literal['little', 'big'] = 'little') -> bytes:
        res = True if target is None else False
        if target is None:
            target = BytesIO()
        if isinstance(target, str):
            target = open(target, 'wb')
        is_byte_io(target) and is_writ_io(target) and is_seek_io(target)
        data = render_nbt(self.__tag, self.__root_name, byteorder == 'big')
        data = compress_file(data, zip_mode)
        if not res:
            target.write(data)
        return data

    # === snbt ===
    @classmethod
    def from_snbt(cls, data: Union[str, IOBase]):
        if isinstance(data, str):
            if os.path.exists(data) and not os.path.isfile(data): raise NbtFileError("路径('%s')非文件" % data)
            if os.path.exists(data) and os.path.isfile(data): data = open(data, 'r')
            elif not os.path.exists(data): data = StringIO(data)
        is_text_io(data) and is_read_io(data) and is_seek_io(data)
        return cls(*parse_snbt(data))

    def to_snbt(self, target: Union[str, IOBase] = None, format=False, size=4) -> str:
        res = True if target is None else False
        if target is None:
            target = StringIO()
        if isinstance(target, str):
            target = open(target, 'w')
        is_text_io(target) and is_writ_io(target) and is_seek_io(target)
        data = render_snbt(self.__tag, self.__root_name, target, format, size)
        if res:
            return data.read()

    # === dat ===
    @classmethod
    def from_dat(cls,
        data     : Union[str, bytes, IOBase],
        zip_mode : Literal['none', 'gzip', 'zlib'] = 'none',
        byteorder: Literal['little', 'big'] = 'little'):
        if isinstance(data, str):
            path_is_file(data)
            data = open(data, 'rb')
        if isinstance(data, bytes):
            data = BytesIO(data)
        is_byte_io(data) and is_read_io(data) and is_seek_io(data)
        data = decompress_buffer(data, zip_mode)
        byte = buffer_read(data, 4, "工具版本号")
        try:
            tool_version = ce.unpack_data(byte, TAG.INT, byteorder == 'big')
        except Exception as e:
            throw_nbt_error(e, data, 4)
        byte = buffer_read(data, 4, "除头文件后的长度")
        try:
            length = ce.unpack_data(byte, TAG.INT, byteorder == 'big')
        except Exception as e:
            throw_nbt_error(e, data, 4)
        return cls(*parse_nbt(data, byteorder == 'big'))

    def to_dat(self,
        target   : Union[str, IOBase] = None,
        zip_mode : Literal['none', 'gzip', 'zlib'] = 'none',
        byteorder: Literal['little', 'big'] = 'little') -> bytes:
        res = bool(target)
        if target is None:
            target = BytesIO()
        if isinstance(target, str):
            target = open(target, 'wb')
        is_byte_io(target) and is_writ_io(target) and is_seek_io(target)
        data = render_nbt(self.__tag, self.__root_name, byteorder == 'big')
        data = b'\x0A\x00\x00\00' + ce.pack_data(len(data), TAG.INT, byteorder == 'big') + data
        data = compress_file(data, zip_mode)
        if res:
            return data
        else:
            target.write(data)
            return data

    def get_tag(self) -> tags.TAG_Base:
        return self.__tag

    def get_root_name(self) -> str:
        return self.__root_name

    def set_tag(self, tag: tags.TAG_Base):
        if not isinstance(tag, (tags.TAG_Compound, tags.TAG_List)):
            raise TypeError("非期望的类型 %s 应该为 %s" % (tag, (tags.TAG_Compound, tags.TAG_List)))
        self.__tag = tag

    def set_root_name(self, name: str):
        if not isinstance(name, str):
            raise TypeError("非期望的类型 %s 应该为 %s" % (name, str))
        self.__root_name = name

    def items(self):
        return self.__tag.items()

    def values(self):
        return self.__tag.values()

    def keys(self):
        return self.__tag.keys()

    def __getitem__(self, key: Union[str, int]):
        return self.__tag[key]
    
    def __repr__(self):
        return f"{repr(self.__class__)[:-1]} object\n    {repr(self.__root_name)}: {repr(self.__tag)}\nat 0x{id(self)}>"


def read_from_nbt_file(
    data     : Union[str, bytes, IOBase],
    zip_mode : Literal['none', 'gzip', 'zlib'] = 'none',
    byteorder: Literal['little', 'big'] = 'little') -> RootNBT:
    return RootNBT.from_nbt(data, zip_mode, byteorder)

def write_to_nbt_file(
    file     : Union[str, IOBase],
    tag      : Union[tags.TAG_List, tags.TAG_Compound, RootNBT],
    zip_mode : Literal['none', 'gzip', 'zlib'] = 'none',
    byteorder: Literal['little','big'] = 'little',
    root_name: str = ''):
    if isinstance(tag, (tags.TAG_List, tags.TAG_Compound)):
        tag = RootNBT(tag, root_name)
    tag.to_nbt(file, zip_mode, byteorder)

def read_from_dat_file(
    data     : Union[str, bytes, IOBase],
    zip_mode : Literal['none', 'gzip', 'zlib'] = 'none',
    byteorder: Literal['little', 'big'] = 'little') -> RootNBT:
    return RootNBT.from_dat(data, zip_mode, byteorder)

def write_to_dat_file(
    file     : Union[str, IOBase],
    tag      : Union[tags.TAG_List, tags.TAG_Compound, RootNBT],
    zip_mode : Literal['none', 'gzip', 'zlib'] = 'none',
    byteorder: Literal['little','big'] = 'little',
    root_name: str = ''):
    if isinstance(tag, (tags.TAG_List, tags.TAG_Compound)):
        tag = RootNBT(tag, root_name)
    tag.to_dat(file, zip_mode, byteorder)

def read_from_snbt_file(data: Union[str, bytes, IOBase]) -> RootNBT:
    return RootNBT.from_snbt(data)

def write_to_snbt_file(
    file     : Union[str, IOBase],
    tag      : Union[tags.TAG_List, tags.TAG_Compound, RootNBT],
    root_name: str = '',
    format   : Literal[True, False] = False,
    size     : str = 4):
    if isinstance(tag, (tags.TAG_List, tags.TAG_Compound)):
        tag = RootNBT(tag, root_name)
    tag.to_snbt(file, format, size)
