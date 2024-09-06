"""
Handle the NBT (Named Binary Tag) data format

For more information about the NBT format:
https://minecraft.gamepedia.com/NBT_format
"""

from io import BytesIO
from typing import Literal,Union
from struct import Struct, error as StructError
from gzip import GzipFile
from collections.abc import MutableMapping, MutableSequence, Sequence

BIG_OR_LITTLE = True

TAG_END        = 0
TAG_BYTE       = 1
TAG_SHORT      = 2
TAG_INT        = 3
TAG_LONG       = 4
TAG_FLOAT      = 5
TAG_DOUBLE     = 6
TAG_BYTE_ARRAY = 7
TAG_STRING     = 8
TAG_LIST       = 9
TAG_COMPOUND   = 10
TAG_INT_ARRAY  = 11
TAG_LONG_ARRAY = 12

class MalformedFileError(Exception): pass


class TAG(object):
    id = None

    def __init__(self, value=None, name=None):
        self.name = name
        self._value = value

    # 解析和编译
    def _parse_buffer(self, buffer):
        raise NotImplementedError(self.__class__.__name__)

    def _render_buffer(self, buffer):
        raise NotImplementedError(self.__class__.__name__)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.test_value(value)
        self._value = value

    def test_value(self, value):
        pass

    # 树打印和格式化
    def tag_info(self):
        # 返回带有类、名称和未嵌套值的Unicode字符串
        return self.__class__.__name__
        + ('(%r)' % self.name if self.name else "")
        + ": " + self.valuestr()

    def valuestr(self):
        # 返回未嵌套值的 Unicode 字符串。对于迭代器，这将返回一个摘要
        return str(self._value)

    def namestr(self):
        # 返回标签名称的 Unicode 字符串
        return str(self.name)

    def pretty_tree(self, indent=0):
        # 返回一个格式化的Unicode字符串表示的自身，其中可迭代的项会被递归详细列出
        return ("\t" * indent) + self.tag_info()

    # Python 2 compatibility; Python 3 uses __str__ instead.
    def __unicode__(self):
        # 返回一个以人类可读格式的Unicode字符串结果
        # 与valuestr()不同，结果对迭代器至少递归到一个层级
        return str(self._value)

    def __str__(self):
        # 返回一个字符串(Python 2中为ASCII格式，Python 3中为Unicode)
        # 结果以人类可读的格式呈现。与valuestr()不同，结果对迭代器至少递归到一个层级
        return str(self._value)

    # 与常规迭代器不同，repr() 不是递归的
    # 对于递归结果，请使用 pretty_tree
    # 迭代器应像常规迭代器一样，对每个项目使用 repr 或 tag_info
    def __repr__(self):
        # 返回一个字符串(Python 2中为ASCII格式，Python 3中为Unicode)
        # 用于调试目的，描述类、名称和ID
        return "<%s(%r) at 0x%x>" % (
            self.__class__.__name__, self.name, id(self))


class _TAG_Numeric(TAG):

    def __init__(self, value=0, name=None, buffer=None):
        self.test_value(value)
        super(_TAG_Numeric, self).__init__(value, name)
        if buffer: self._parse_buffer(buffer)

    def _parse_buffer(self, buffer):
        # Note: buffer.read() may raise an IOError, for example if buffer is a
        # corrupt gzip.GzipFile
        fmt = self.fmt[not BIG_OR_LITTLE]
        self._value = fmt.unpack(buffer.read(fmt.size))[0]

    def _render_buffer(self, buffer):
        fmt = self.fmt[not BIG_OR_LITTLE]
        buffer.write(fmt.pack(self._value))
    
    def test_value(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("期望类型为 (int, float)，但传入了 %s" % type(value))
        try:
            fmt = self.fmt[not BIG_OR_LITTLE]
            fmt.pack(value)
        except:
            raise ValueError("数值的范围不正确(%s)" % (value))


class _TAG_End(TAG):
    id = TAG_END
    fmt = (Struct(">b"), Struct("<b"))

    def _parse_buffer(self, buffer):
        # 注意：buffer.read() 可能会引发 IOError
        # 例如如果 buffer 是一个损坏的 gzip.GzipFile
        fmt = self.fmt[not BIG_OR_LITTLE]
        value = fmt.unpack(buffer.read(1))[0]
        if value != 0 : raise ValueError("标签结束字节必须为 '0'，而不是 '%d'。" % value)

    def _render_buffer(self, buffer):
        buffer.write(b'\x00')


# == Value Tags ==#
class TAG_Byte(_TAG_Numeric):
    id = TAG_BYTE
    fmt = (Struct(">b"), Struct("<b"))


class TAG_Short(_TAG_Numeric):
    id = TAG_SHORT
    fmt = (Struct(">h"), Struct("<h"))


class TAG_Int(_TAG_Numeric):
    id = TAG_INT
    fmt = (Struct(">i"), Struct("<i"))


class TAG_Long(_TAG_Numeric):
    id = TAG_LONG
    fmt = (Struct(">q"), Struct("<q"))


class TAG_Float(_TAG_Numeric):
    id = TAG_FLOAT
    fmt = (Struct(">f"), Struct("<f"))


class TAG_Double(_TAG_Numeric):
    id = TAG_DOUBLE
    fmt = (Struct(">d"), Struct("<d"))


class TAG_Array(TAG, MutableSequence):

    def __init__(self, name=None, buffer=None):
        # TODO: add a value parameter as well
        super(TAG_Array, self).__init__(name=name)
        if buffer: self._parse_buffer(buffer)
        self._value = []

    def _parse_buffer(self, buffer):
        fmt = self.fmt[not BIG_OR_LITTLE]
        length = TAG_Int(buffer=buffer)._value
        size = length * self.type[2]
        self._value = list(fmt.unpack(buffer.read(size)))

    def _render_buffer(self, buffer):
        fmt = self.fmt[not BIG_OR_LITTLE]
        TAG_Int(len(self._value))._render_buffer(buffer)
        for value in self._value:
            buffer.write(fmt.pack(value)[0])

    def test_value(self, value):
        if isinstance(value, self.type[0]):
            fmt = self.fmt[not BIG_OR_LITTLE]
            return fmt.pack(value.value)[0]
        if isinstance(value, bytes):
            try:
                return self.fmt[not BIG_OR_LITTLE].unpack(value)[0]
            except:
                raise ValueError()
        elif isinstance(value, int):
            try:
                self.fmt[not BIG_OR_LITTLE].pack(value)
                return value
            except:
                raise ValueError("数值的范围不正确(%s)" % (value))
        else:
            raise TypeError("期望类型为 (%s, int, %s)，但传入了 %s" % 
                (self.type[1], self.type[0].__name__, type(value)))

    # 魔术方法
    def __len__(self):
        return len(self._value)

    def __iter__(self):
        return iter(self._value)

    def __contains__(self, item):
        return item in self._value

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, value):
        value = self.test_value(value)
        self._value[key] = value

    def __delitem__(self, key):
        del self._value[key]

    def insert(self, key, value):
        value = self.test_value(value)
        self._value.insert(key, value)

    # Printing and Formatting of tree
    def valuestr(self):
        return "[%i %s(s)]" % (len(self._value), self.type[1])

    def __unicode__(self):
        return '[' + ",".join([str(x) for x in self._value]) + ']'

    def __str__(self):
        return '[' + ",".join([str(x) for x in self._value]) + ']'


class TAG_Byte_Array(TAG_Array, MutableSequence):
    id = TAG_BYTE_ARRAY
    fmt = (Struct(">b"), Struct("<b"))
    type = (TAG_Byte, "byte", 1)


class TAG_Int_Array(TAG_Array, MutableSequence):
    id = TAG_INT_ARRAY
    fmt = (Struct(">i"), Struct("<i"))
    type = (TAG_Int, "int", 4)


class TAG_Long_Array(TAG_Array, MutableSequence):
    id = TAG_LONG_ARRAY
    fmt = (Struct(">q"), Struct("<q"))
    type = (TAG_Long, "long", 8)


class TAG_String(TAG, Sequence):
    id = TAG_STRING

    def __init__(self, value="", name=None, buffer=None):
        self.test_value(value)
        super(TAG_String, self).__init__(value, name)
        if buffer : self._parse_buffer(buffer)

    # Parsers and Generators
    def _parse_buffer(self, buffer):
        length = TAG_Short(buffer=buffer)
        read = buffer.read(length._value)
        if len(read) != length._value:
            raise StructError()
        self._value = read.decode("utf-8", "ignore")

    def _render_buffer(self, buffer):
        save_val = self._value.encode("utf-8")
        length = TAG_Short(len(save_val))
        length._render_buffer(buffer)
        buffer.write(save_val)

    def test_value(self, value):
        if not isinstance(value, str):
            raise TypeError("期望类型为 str，但传入了 %s" % type(value))

    # Mixin methods
    def __len__(self):
        return len(self._value)

    def __iter__(self):
        return iter(self._value)

    def __contains__(self, item):
        return item in self._value

    def __getitem__(self, key):
        return self._value[key]

    # Printing and Formatting of tree
    def __repr__(self):
        return self._value


# == Collection Tags ==#
class TAG_List(TAG, MutableSequence):
    id = TAG_LIST

    def __init__(self, type=None, value=None, name=None, buffer=None):
        super(TAG_List, self).__init__(value, name)
        if type: self.tagID = type.id
        else: self.tagID = 0
        self.tags = []
        if buffer: self._parse_buffer(buffer)
        # if self.tagID == None:
        #     raise ValueError("No type specified for list: %s" % (name))

    def _parse_buffer(self, buffer):
        self.tagID = TAG_Byte(buffer=buffer)._value
        self.tags = []
        length = TAG_Int(buffer=buffer)
        for x in range(length._value):
            self.tags.append(TAGLIST[self.tagID](buffer=buffer))

    def _render_buffer(self, buffer):
        TAG_Byte(self.tagID)._render_buffer(buffer)
        length = TAG_Int(len(self.tags))
        length._render_buffer(buffer)
        for i, tag in enumerate(self.tags):
            if tag.id != self.tagID:
                raise ValueError(
                    "列表元素 %d(%s) 的类型 %d != 不等于容器类型 %d" %
                    (i, tag, tag.id, self.tagID))
            tag._render_buffer(buffer)

    def test_value(self, value):
        if isinstance(value, tuple(TAGLIST.values())):
            if len(self.tags) == 0:
                self.tagID = value.id
            if value.id == self.tagID:
                return value
            else:
                raise TypeError("期望类型为 %s，但传入了 %s" % (
                list(TAGLIST.values())[self.tagID], value.__class__.__name__))
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % (
                tuple(TAGLIST.values()), value.__class__.__name__))

    # 魔术方法
    def __len__(self):
        return len(self.tags)

    def __iter__(self):
        return iter(self.tags)

    def __contains__(self, item):
        return item in self.tags

    def __getitem__(self, key):
        return self.tags[key]

    def __setitem__(self, key, value):
        value = self.test_value(value)
        self.tags[key] = value

    def __delitem__(self, key):
        del (self.tags[key])

    def insert(self, key, value):
        value = self.test_value(value)
        self.tags.insert(key, value)

    # Printing and Formatting of tree
    def __repr__(self):
        return "%i 类型条目 %s" % (
            len(self.tags), TAGLIST[self.tagID].__name__)

    # Printing and Formatting of tree
    def valuestr(self):
        return "[%i %s(s)]" % (len(self.tags), TAGLIST[self.tagID].__name__)

    def __unicode__(self):
        return "[" + ", ".join([tag.tag_info() for tag in self.tags]) + "]"

    def __str__(self):
        return "[" + ", ".join([tag.tag_info() for tag in self.tags]) + "]"

    def pretty_tree(self, indent=0):
        output = [super(TAG_List, self).pretty_tree(indent)]
        if len(self.tags):
            output.append(("\t" * indent) + "{")
            output.extend([tag.pretty_tree(indent + 1) for tag in self.tags])
            output.append(("\t" * indent) + "}")
        return '\n'.join(output)


class TAG_Compound(TAG, MutableMapping):
    id = TAG_COMPOUND

    def __init__(self, buffer=None, name=None):
        # TODO: add a value parameter as well
        super(TAG_Compound, self).__init__()
        self.tags = []
        if name: self.name = name
        else: self.name = ""
        if buffer: self._parse_buffer(buffer)

    def _parse_buffer(self, buffer):
        while True:
            type = TAG_Byte(buffer=buffer)
            if type._value == TAG_END:
                break
            else:
                name = TAG_String(buffer=buffer)._value
                try: tag = TAGLIST[type._value]()
                except KeyError: raise ValueError("不正确的标签类型 %d" % type._value)
                tag.name = name
                self.tags.append(tag)
                tag._parse_buffer(buffer)

    def _render_buffer(self, buffer):
        for tag in self.tags:
            TAG_Byte(tag.id)._render_buffer(buffer)
            TAG_String(tag.name)._render_buffer(buffer)
            tag._render_buffer(buffer)
        buffer.write(b'\x00')

    # 魔术方法
    def __len__(self):
        return len(self.tags)

    def __iter__(self):
        for key in self.tags:
            yield key.name

    # xxxx in [xxx]
    def __contains__(self, key):
        if isinstance(key, int):
            return key <= len(self.tags)
        elif isinstance(key, str):
            for tag in self.tags:
                if tag.name == key:
                    return True
            return False
        elif isinstance(key, TAG):
            return key in self.tags
        return False

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.tags[key]
        elif isinstance(key, str):
            for tag in self.tags:
                if tag.name == key:
                    return tag
            else:
                raise KeyError("标签 %s 不存在" % key)
        else:
            raise TypeError(
                "key 必须是一个标签名或者索引, 而不是 %s" % type(key).__name__)

    def __setitem__(self, key, value):
        assert isinstance(value, TAG), "值必须是nbt对象"
        if isinstance(key, int):
            # Just try it. The proper error will be raised if it doesn't work.
            self.tags[key] = value
        elif isinstance(key, str):
            value.name = key
            for i, tag in enumerate(self.tags):
                if tag.name == key:
                    self.tags[i] = value
                    return
            self.tags.append(value)

    def __delitem__(self, key):
        if isinstance(key, int):
            del (self.tags[key])
        elif isinstance(key, str):
            self.tags.remove(self.__getitem__(key))
        else:
            raise ValueError("key 必须是标签的名称或者索引")

    def keys(self):
        return [tag.name for tag in self.tags]

    def iteritems(self):
        for tag in self.tags:
            yield (tag.name, tag)

    # Printing and Formatting of tree
    def __unicode__(self):
        return "{" + ", ".join([tag.tag_info() for tag in self.tags]) + "}"

    def __str__(self):
        return "{" + ", ".join([tag.tag_info() for tag in self.tags]) + "}"

    def valuestr(self):
        return '{%i 个条目}' % len(self.tags)

    def pretty_tree(self, indent=0):
        output = [super(TAG_Compound, self).pretty_tree(indent)]
        if len(self.tags):
            output.append(("\t" * indent) + "{")
            output.extend([tag.pretty_tree(indent + 1) for tag in self.tags])
            output.append(("\t" * indent) + "}")
        return '\n'.join(output)


TAGLIST = {TAG_END: _TAG_End, TAG_BYTE: TAG_Byte, TAG_SHORT: TAG_Short,
           TAG_INT: TAG_Int, TAG_LONG: TAG_Long, TAG_FLOAT: TAG_Float,
           TAG_DOUBLE: TAG_Double, TAG_BYTE_ARRAY: TAG_Byte_Array,
           TAG_STRING: TAG_String, TAG_LIST: TAG_List,
           TAG_COMPOUND: TAG_Compound, TAG_INT_ARRAY: TAG_Int_Array,
           TAG_LONG_ARRAY: TAG_Long_Array}


class NBTFile(TAG_Compound):
    # 解析一个nbt文件

    def __init__(self, data:Union[str, bytes], gzip:bool):
        # 创建一个新的 NBTFile 对象。
        # 指定一个文件名或字节缓冲区。
        # 如果指定了文件名或文件对象，数据应该是 GZip 压缩的。
        super(NBTFile, self).__init__()
        if isinstance(data, str) : file = GzipFile(data, 'rb') if gzip else open(data, "rb")
        elif isinstance(data, bytes) : file = GzipFile(fileobj=BytesIO(data), mode="rb") if gzip else BytesIO(data)
        else : file = GzipFile(fileobj=data, mode="rb") if gzip else data
        self.type = TAG_Byte(self.id)
        # 创建一个文件对象
        # 解析文件给的初始值
        try:
            type = TAG_Byte(buffer=file)
            if type._value == self.id:
                name = TAG_String(buffer=file)._value
                self._parse_buffer(file)
                self.name = name
            else : raise MalformedFileError("文件的第一个标签不是Compound")
        except StructError as e:
            raise MalformedFileError("部分文件解析：文件可能被截断了")

    def write_nbt(self, obj:Union[str, BytesIO], gzip:bool):
        # 创建要写入的文件
        if isinstance(obj, str) : file = GzipFile(obj, "wb") if gzip else open(obj, "wb")
        else : file = GzipFile(fileobj=obj, mode="wb") if gzip else obj
        # 解析树结构并写入
        TAG_Byte(self.id)._render_buffer(file)
        TAG_String(self.name)._render_buffer(file)
        self._render_buffer(file)
        # 确保文件完整写入
        try : file.flush()
        except (AttributeError, IOError) : pass
        try : file.close() if isinstance(obj, str) else None
        except (AttributeError, IOError) : pass




def read_from_nbt_file(
    file     : Union[str,bytes,BytesIO],
    gzip     : bool=False, 
    byteorder: Literal['big','little']='big'):
    
    # 读取一个nbt文件
    global BIG_OR_LITTLE
    BIG_OR_LITTLE = True if byteorder == "big" else False
    return NBTFile(file, gzip)

def write_to_nbt_file(
    file     : Union[str, BytesIO],
    tag      : Union[NBTFile,TAG_Compound],
    gzip     : bool=False,
    byteorder: Literal['big','little'] = 'big') :
    
    global BIG_OR_LITTLE
    BIG_OR_LITTLE = True if byteorder == "big" else False
    if isinstance(tag, NBTFile) : tag.write_nbt(file, gzip)
    else : NBTFile.write_nbt(tag, file, gzip)