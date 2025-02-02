"""
    builder.py - 使用代码快速创建nbt结构工具
"""
from typing import Mapping, Union
from . import tags

def test_node(v):
    if not isinstance(v, NBT_Builder_Node): raise TypeError("非期望的类型 %s 应该为 %s" % (v, NBT_Builder_Node))

def test_str(v):
    if not isinstance(v, str): raise TypeError("非期望的类型 %s 应该为 %s" % (v, str))

def test_int(v):
    if not isinstance(v, int): raise TypeError("非期望的类型 %s 应该为 %s" % (v, int))

def test_number(v):
    if not isinstance(v, (int, float)): raise TypeError("非期望的类型 %s 应该为 %s" % (v, (int, float)))


class NBT_Builder:
    def compound(self, **nodes: Union['NBT_Builder_Node', 'NBT_Builder_Proxy']):
        _nodes = {}
        for k, v in nodes.items():
            if isinstance(v, NBT_Builder_Proxy):
                k, v = v.name, v.node
            test_node(v)
            _nodes[k] = v
        return self.return_node(NBT_Compound_Builder_Node(_nodes))

    def list(self, *nodes: 'NBT_Builder_Node') -> 'NBT_List_Builder_Node':
        for v in nodes:
            test_node(v)
        return self.return_node(NBT_List_Builder_Node(nodes))

    def byte_array(self, *nodes: int) -> 'NBT_ByteArray_Builder_Node':
        for v in nodes:
            test_int(v)
        return self.return_node(NBT_ByteArray_Builder_Node(nodes))

    def int_array(self, *nodes: int) -> 'NBT_IntArray_Builder_Node':
        for v in nodes:
            test_int(v)
        return self.return_node(NBT_IntArray_Builder_Node(nodes))

    def long_array(self, *nodes: int) -> 'NBT_LongArray_Builder_Node':
        for v in nodes:
            test_int(v)
        return self.return_node(NBT_LongArray_Builder_Node(nodes))

    def byte(self, v: int) -> 'NBT_Byte_Builder_Node':
        test_int(v)
        return self.return_node(NBT_Byte_Builder_Node(v))

    def short(self, v: int) -> 'NBT_Short_Builder_Node':
        test_int(v)
        return self.return_node(NBT_Short_Builder_Node(v))

    def int(self, v: int) -> 'NBT_Int_Builder_Node':
        test_int(v)
        return self.return_node(NBT_Int_Builder_Node(v))

    def long(self, v: int) -> 'NBT_Long_Builder_Node':
        test_int(v)
        return self.return_node(NBT_Long_Builder_Node(v))

    def float(self, v: Union[int, float]) -> 'NBT_Float_Builder_Node':
        test_number(v)
        return self.return_node(NBT_Float_Builder_Node(v))

    def double(self, v: Union[int, float]) -> 'NBT_Double_Builder_Node':
        test_number(v)
        return self.return_node(NBT_Double_Builder_Node(v))

    def string(self, v: str) -> 'NBT_String_Builder_Node':
        test_str(v)
        return self.return_node(NBT_String_Builder_Node(v))

    def key(self, s: str) -> 'NBT_Builder_Proxy':
        test_str(s)
        return NBT_Builder_Proxy(s)
    
    def return_node(self, node):
        return node

    cpd = compound
    lst = list
    bay = byte_array
    iay = int_array
    lay = long_array
    bte = byte
    sht = short
    lng = long
    flt = float
    dbl = double
    str = string


class NBT_Builder_Proxy(NBT_Builder):
    def __init__(self, name):
        self.name = name
    
    def return_node(self, node):
        self.node = node
        return self


class NBT_Builder_Node:
    tag = tags.TAG_End
    def __init__(self, value):
        self.value = value
    
    def build(self):
        return self.tag(self.value)


class NBT_Compound_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Compound
    def build(self):
        v = self.tag()
        v.set_value({k: v.build() for k, v in self.value.items()})
        return v


class NBT_List_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_List
    def build(self):
        v = self.tag()
        v.set_value([v.build() for v in self.value])
        return v


class NBT_Array_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Array
    def build(self):
        v = self.tag()
        v.set_value(self.value)
        return v


class NBT_ByteArray_Builder_Node(NBT_Array_Builder_Node):
    tag = tags.TAG_ByteArray


class NBT_IntArray_Builder_Node(NBT_Array_Builder_Node):
    tag = tags.TAG_IntArray


class NBT_LongArray_Builder_Node(NBT_Array_Builder_Node):
    tag = tags.TAG_LongArray


class NBT_Byte_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Byte


class NBT_Short_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Short


class NBT_Int_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Int


class NBT_Long_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Long


class NBT_Float_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Float


class NBT_Double_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_Double


class NBT_String_Builder_Node(NBT_Builder_Node):
    tag = tags.TAG_String

