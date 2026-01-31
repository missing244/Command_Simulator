"""
    abc.py - tag的所有基类
"""


from typing import Literal, Union, ValuesView, KeysView, ItemsView, Tuple
from abc import ABC, ABCMeta, abstractmethod
from io import BytesIO, StringIO, IOBase
from array import array

from . import TAGLIST, TAG, tags
from .snbt import SnbtIO, get_line

ARRAY_TYPECODE = {
    TAG.BYTE:   "b",
    TAG.SHORT:  "h",
    TAG.INT:    "i",
    TAG.LONG:   "q",
    TAG.FLOAT:  "f",
    TAG.DOUBLE: "d",
}

def buffer_is_readable(buffer):
    if not isinstance(buffer, IOBase): return False
    if not buffer.readable(): raise TypeError("io(%s)不能读" % buffer)
    if not buffer.seekable(): raise TypeError("io(%s)不能随机访问" % buffer)
    return True

def try_to_number(v):
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, TAG_Base_Number):
        return v.get_value()
    raise ValueError("数值自动转换失败：" + repr(v))


class TAG_Number_Meta(ABCMeta):
    def __init__(self, *arg) :
        super().__init__(*arg)
        self._memory = {}
    
    def __call__(self, v=0) :
        v = try_to_number(v)
        if v not in self._memory:
            self._memory[v] = super().__call__(v)
        return self._memory[v]


class TAG_String_Meta(ABCMeta):
    def __init__(self, *arg) :
        super().__init__(*arg)
        self._memory = {}
    
    def __call__(self, v=b'') :
        if v not in self._memory:
            self._memory[v] = super().__call__(v)
        return self._memory[v]


class TAG_Base(ABC):
    type: TAG = None
    __slots__ = ()

    @classmethod
    def from_bytes(cls, buffer: Union[bytes, IOBase], mode: bool=False) -> 'TAG_Base':
        if buffer_is_readable(buffer):
            return cls._from_bytesIO(buffer, mode)
        elif isinstance(buffer, bytes):
            return cls._from_bytes(buffer, mode)
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((BytesIO, bytes), repr(buffer)))

    @classmethod
    def from_snbt(cls, buffer: Union[str, SnbtIO]) -> 'TAG_Base':
        if isinstance(buffer, SnbtIO):
            return cls._from_snbtIO(buffer)
        elif isinstance(buffer, str):
            return cls._from_snbt(buffer)
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((SnbtIO, str), repr(buffer)))

    @classmethod
    @abstractmethod
    def _from_bytesIO(cls, buffer, mode): pass

    @classmethod
    @abstractmethod
    def _from_bytes(cls, buffer, mode): pass
    
    @classmethod
    @abstractmethod
    def _from_snbtIO(cls, buffer): pass

    @classmethod
    @abstractmethod
    def _from_snbt(cls, buffer): pass

    @abstractmethod
    def get_value(self): pass

    @abstractmethod
    def set_value(self, value): pass

    def to_snbt(self, Format: bool=False, size: int=4) -> str:
        if Format:
            if not isinstance(size, int): raise TypeError("缩进期望类型为 %s，但传入了 %s" % (int, repr(size)))
            if not 1 <= size <= 16: raise ValueError("超出范围(1 ~ 16)的数字 %s" % size)
            buffer = StringIO()
            self._to_snbt_format(buffer, 1, size)
            buffer.seek(0)
            return buffer.read()
        else:
            return self._to_snbt()

    @abstractmethod
    def _to_snbt(self): pass

    @abstractmethod
    def _to_snbt_format(self, buffer, indent, size): pass

    @abstractmethod
    def to_bytes(self): pass

    def print_info(self): print(self.get_info())

    @abstractmethod
    def get_info(self, ellipsis=False): pass

    @abstractmethod
    def copy(self): pass

    @property
    def value(self): return self.get_value()

    @value.setter
    def value(self, value): self.set_value(value)

    @property
    def id(self): return self.type.value

    @id.setter
    def id(self, value): raise AttributeError("不可修改的属性 id")

    @abstractmethod
    def __repr__(self): pass

    def __str__(self) -> str: return self.to_snbt()

    def __bytes__(self) -> bytes: return self.to_bytes()
    
    def __bool__(self) -> bool: return bool(self.get_value())


class TAG_Base_End(TAG_Base):

    @classmethod
    def _from_bytesIO(buffer, mode): pass

    @classmethod
    def _from_bytes(buffer, mode): pass
    
    @classmethod
    def _from_snbtIO(buffer): pass

    @classmethod
    def _from_snbt(buffer): pass

    def get_value(self): pass

    def set_value(self, value): pass

    def _to_snbt(self): pass

    def _to_snbt_format(self, buffer, indent, size): pass

    def to_bytes(self): pass

    def get_info(self, ellipsis=False): pass

    def copy(self): pass

    def __repr__(self): pass


class TAG_Base_Number(TAG_Base):

    def __hash__(self):
        return hash(self.get_value())
    
    def __format__(self, fs):
        return format(self.get_value(), fs)
    
    def __lt__(self, other):
        return self.get_value() < try_to_number(other)
    
    def __le__(self, other):
        return self.get_value() <= try_to_number(other)
    
    def __eq__(self, other):
        return self.get_value() == try_to_number(other)
    
    def __ne__(self, other):
        return self.get_value() != try_to_number(other)
    
    def __gt__(self, other):
        return self.get_value() > try_to_number(other)
    
    def __ge__(self, other):
        return self.get_value() >= try_to_number(other)
    
    def __add__(self, other):
        return self.__class__(self.get_value() + try_to_number(other))
    
    def __sub__(self, other):
        return self.__class__(self.get_value() - try_to_number(other))
    
    def __mul__(self, other):
        return self.__class__(self.get_value() * try_to_number(other))
    
    def __truediv__(self, other):
        return self.__class__(self.get_value() / try_to_number(other))
    
    def __floordiv__(self, other):
        return self.__class__(self.get_value() // try_to_number(other))
    
    def __mod__(self, other):
        return self.__class__(self.get_value() % try_to_number(other))
    
    def __divmod__(self, other):
        q = self.__class__(self.get_value() // try_to_number(other))
        r = self.__class__(self.get_value() % try_to_number(other))
        return (q, r)
    
    def __pow__(self, other, modulo=None):
        res = self.get_value() ** try_to_number(other)
        if modulo is not None:
            res = res % modulo
        return self.__class__(res)
    
    def __lshift__(self, other):
        return self.__class__(self.get_value() << try_to_number(other))
    
    def __rshift__(self, other):
        return self.__class__(self.get_value() >> try_to_number(other))
    
    def __and__(self, other):
        return self.__class__(self.get_value() & try_to_number(other))
    
    def __xor__(self, other):
        return self.__class__(self.get_value() ^ try_to_number(other))
    
    def __or__(self, other):
        return self.__class__(self.get_value() | try_to_number(other))
    
    def __radd__(self, other):
        return self.__class__(self.get_value() + try_to_number(other))
    
    def __rsub__(self, other):
        return self.__class__(self.get_value() - try_to_number(other))
    
    def __rmul__(self, other):
        return self.__class__(self.get_value() * try_to_number(other))
    
    def __rtruediv__(self, other):
        return self.__class__(self.get_value() / try_to_number(other))
    
    def __rfloordiv__(self, other):
        return self.__class__(self.get_value() // try_to_number(other))
    
    def __rmod__(self, other):
        return self.__class__(self.get_value() % try_to_number(other))
    
    def __rdivmod__(self, other):
        q = self.__class__(self.get_value() // try_to_number(other))
        r = self.__class__(self.get_value() % try_to_number(other))
        return (q, r)
    
    def __rpow__(self, other, modulo=None):
        res = self.get_value() ** try_to_number(other)
        if modulo is not None:
            res = res % modulo
        return self.__class__(res)
    
    def __rlshift__(self, other):
        return self.__class__(self.get_value() << try_to_number(other))
    
    def __rrshift__(self, other):
        return self.__class__(self.get_value() >> try_to_number(other))
    
    def __rand__(self, other):
        return self.__class__(self.get_value() & try_to_number(other))
    
    def __rxor__(self, other):
        return self.__class__(self.get_value() ^ try_to_number(other))
    
    def __ror__(self, other):
        return self.__class__(self.get_value() | try_to_number(other))
    
    def __pos__(self):
        return self.__class__(+self.get_value())
    
    def __neg__(self):
        return self.__class__(-self.get_value())
    
    def __abs__(self):
        return self.__class__(abs(self.get_value()))
    
    def __invert__(self):
        return self.__class__(~self.get_value())
    
    def __float__(self):
        return tags.TAG_Double(self.get_value())
    
    def __round__(self, n=None):
        return self.__class__(round(self.get_value(), n) if n else round(self.get_value()))
    
    def __index__(self):
        return int(self.get_value())


class TAG_Base_String(TAG_Base):
    type = TAG.STRING
    
    def __len__(self):
        return len(self.get_value())

    def __str__(self):
        return self.get_value()
    
    def __hash__(self):
        return hash(self.get_value())
    
    def __format__(self, fs):
        return format(self.get_value(), fs)
    
    def __add__(self, other):
        if isinstance(other, str):
            return self.__class__(self.get_value() + other)
        elif isinstance(other, self.__class__):
            return self.__class__(self.get_value() + other.get_value())
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((self.__class__, str), repr(other)))
    
    def __mul__(self, other):
        return self.__class__(self.get_value() * other)
    
    def __mod__(self, other):
        return self.__class__(self.get_value() % other)


class TAG_Base_List(TAG_Base):

    @abstractmethod
    def get_type(self): pass

    @abstractmethod
    def set_type(self, type): pass

    @abstractmethod
    def test_type(self): pass

    @abstractmethod
    def test_value(self, value): pass

    @abstractmethod
    def value_is_array(self): pass

    def __add__(self, other):
        if isinstance(other, TAG_Base_List):
            if other.get_type() != self.get_type():
                raise TypeError("TAG_List容器类型期望类型为 %s，但传入了 %s" % (self.get_type(), other.get_type()))
            if not bool(other): return self.__class__(self)
            return self.__class__(self.get_value() + other.get_value())
        elif isinstance(other, list):
            return self.__class__(other) + self
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((self.__class__, list), other.__class__))

    def __len__(self):
        return len(self.get_value())

    def __iter__(self):
        if self.value_is_array():
            return iter(TAGLIST[self.get_type()](i) for i in self.get_value())
        else:
            return iter(self.get_value())

    def __contains__(self, item):
        return item in self.get_value()

    def __getitem__(self, key):
        if self.value_is_array():
            return TAGLIST[self.get_type()](self.get_value()[key])
        else:
            return self.get_value()[key]

    def __setitem__(self, key, value):
        value = self.test_value(value)
        self.get_value()[key] = value

    def __delitem__(self, key):
        del (self.get_value()[key])

    def __reversed__(self):
        return self.__class__(reversed(self.get_value()))

    def reversed(self) -> None:
        self.get_value().reversed()

    def insert(self, key: int, value: 'TAG_Base'):
        value = self.test_value(value)
        self.get_value().insert(key, value)

    def append(self, value: 'TAG_Base') -> None:
        value = self.test_value(value)
        self.get_value().append(value)

    def clear(self) -> None:
        if self.value_is_array():
            self.set_value(array(ARRAY_TYPECODE[self.get_type()]))
        else:
            self.get_value().clear()

    def pop(self, key: int) -> 'TAG_Base':
        if self.value_is_array():
            return TAGLIST[self.get_type()](self.get_value().pop(key))
        else:
            return self.get_value().pop(key)

    def remove(self, value: 'TAG_Base') -> None:
        value = self.test_value(value)
        self.get_value().remove(value)

    def extend(self, other: 'TAG_List') -> None:
        if isinstance(other, self.__class__):
            if self.get_type() != other.get_type():
                raise TypeError("%s 和 %s 类型不一致" % (self, other))
            self.get_value().extend(other.get_value())
        else:
            try:
                self.extend(self.__class__(other))
            except Exception as e:
                raise TypeError("尝试自动转换失败: %s" % e.args[0])


class TAG_Base_Compound(TAG_Base):

    @abstractmethod
    def _test_key(self, key): pass

    @abstractmethod
    def _test_value(self, value): pass

    def __len__(self):
        return len(self.get_value())

    def __getitem__(self, key):
        self._test_key(key)
        return self.get_value()[key]

    def __setitem__(self, key, value):
        self._test_key(key) and self._test_value(value)
        self.get_value()[key] = value

    def __delitem__(self, key):
        self._test_key(key)
        del self.get_value()[key]

    def __iter__(self):
        return iter(self.get_value())

    def __contains__(self, item):
        return item in self.get_value()

    def clear(self) -> None:
        self.get_value().clear()

    def get(self, key: str, default: any=None) -> 'TAG_Base':
        self._test_key(key)
        return self.get_value().get(key, default)

    def items(self) -> ItemsView[str, 'TAG_Base']:
        return self.get_value().items()

    def keys(self) -> KeysView[str]:
        return self.get_value().keys()

    def values(self) -> ValuesView['TAG_Base']:
        return self.get_value().values()

    def pop(self, key: str, default: any=None) -> 'TAG_Base':
        self._test_key(key)
        return self.get_value().pop(key, default)

    def popitem(self) -> Tuple[str, 'TAG_Base']:
        return self.get_value().popitem()

    def setdefault(self, key: str, default: any=None) -> 'TAG_Base':
        self._test_key(key) and self._test_value(default)
        return self.get_value().setdefault(key, default)


class TAG_Base_Array(TAG_Base):
    unit = ()

    @abstractmethod
    def test_value(self, value): pass

    def __add__(self, other):
        if isinstance(other, TAG_Base_Array):
            if other.__class__ != self.__class__: raise TypeError("期望类型为 %s，但传入了 %s" % (self.__class__, other.__class__))
            if not bool(other): return self.__class__(self)
            return self.__class__(self.get_value() + other.get_value())
        elif isinstance(other, list):
            return self.__class__(other) + self
        elif isinstance(other, array) and other.typecode == self.unit[2]:
            return self.__class__(self.get_value() + other)
        else:
            raise TypeError("期望类型为 %s，但传入了 %s" % ((self.__class__, list, array), other.__class__))
    
    def __len__(self):
        return len(self.get_value())

    def __iter__(self):
        return iter(self.get_value())

    def __contains__(self, item):
        return item in self.get_value()

    def __getitem__(self, key):
        return self.get_value()[key]

    def __setitem__(self, key, value):
        value = self.test_value(value)
        self.get_value()[key] = value

    def __delitem__(self, key):
        del (self.get_value()[key])

    def __reversed__(self):
        return self.__class__(reversed(self.get_value()))

    def reversed(self) -> None:
        self.get_value().reversed()

    def insert(self, key: int, value: int) -> None:
        value = self.test_value(value)
        self.get_value().insert(key, value)

    def append(self, value: int) -> None:
        value = self.test_value(value)
        self.get_value().append(value)

    def clear(self) -> None:
        self.set_value(array(self.unit[2]))

    def pop(self, key: int) -> int:
        return self.get_value().pop(key)

    def remove(self, value: int) -> None:
        self.get_value().remove(value)

    def extend(self, other: 'TAG_Array'):
        if isinstance(other, self.__class__):
            self.get_value().extend(other.get_value())
        else:
            try:
                self.extend(self.__class__(other))
            except Exception as e:
                raise TypeError("尝试自动转换失败: %s" % e.args[0])
