"""
bdx文件内所有支持的操作类型 \n \n
CreateConstantString, PlaceBlockWithBlockStates1, AddInt16ZValue0, \n
PlaceBlock, AddZValue0, NOP, AddInt32ZValue0, PlaceBlockWithBlockStates2, \n
AddXValue, SubtractXValue, AddYValue, SubtractYValue, AddZValue, \n
SubtractZValue, AddInt16XValue, AddInt32XValue, AddInt16YValue, \n
AddInt32YValue, AddInt16ZValue, AddInt32ZValue, \n
SetCommandBlockData, PlaceBlockWithCommandBlockData, \n
AddInt8XValue, AddInt8YValue, AddInt8ZValue, UseRuntimeIDPool, \n
PlaceRuntimeBlock, PlaceBlockWithRuntimeId, PlaceRuntimeBlockWithCommandBlockData, \n
PlaceRuntimeBlockWithCommandBlockDataAndUint32RuntimeID, \n
PlaceCommandBlockWithCommandBlockData, PlaceRuntimeBlockWithChestData, \n
PlaceRuntimeBlockWithChestDataAndUint32RuntimeID, \n
AssignDebugData, PlaceBlockWithChestData, PlaceBlockWithNBTData, \n
Terminate \n
--------------------------------------
PlaceBlockWithNBTData 会涉及到nbt的修改\n
修改nbt : https://github.com/TowardtheStars/Python-NBT \n
"""


import ctypes,io
from .. import nbt
from typing import TypedDict,Dict,Union

class ChestDataType(TypedDict): 
    name: str
    count: int
    data: int
    slotID: int



class Signed_Int_Meta(type) :
    
    def __init__(self, *arg, **karg) :
        super().__init__(*arg, **karg)
        self._memory = {}
    
    def __call__(self, v:Union[bytes, int]) :
        if v not in self._memory : 
            value = int.from_bytes(v, 'big', signed=True) if v.__class__ is bytes else v
            self._memory[v] = super().__call__(value)
        return self._memory[v]

class Unsigned_Int_Meta(type) :
    
    def __init__(self, *arg, **karg) :
        super().__init__(*arg, **karg)
        self._memory = {}
    
    def __call__(self, v:Union[bytes, int]) :
        if v not in self._memory : 
            value = int.from_bytes(v, 'big', signed=False) if v.__class__ is bytes else v
            self._memory[v] = super().__call__(value)
        return self._memory[v]

class Two_Int_Meta(type) :
    
    def __init__(self, *arg, **karg) :
        super().__init__(*arg, **karg)
        self._memory = {}
    
    def __call__(self, v1:Union[bytes, int], v2:int=None) :
        if v2 is None :
            if v1 not in self._memory : 
                value1 = int.from_bytes(v1[0:2], 'big', signed=False)
                value2 = int.from_bytes(v1[2:4], 'big', signed=False)
                self._memory[v1] = super().__call__(value1, value2)
            return self._memory[v1]
        else : 
            t1 = (v1, v2)
            if t1 not in self._memory : 
                self._memory[t1] = super().__call__(v1, v2)
            return self._memory[t1]
        

class OperationBase :

    """__slots__ = ("operation_code", "string", "blockConstantStringID", "blockStatesConstantStringID", "__value", "blockData",
    "blockStatesString", "mode", "command", "customName", "lastOutput", "tickdelay", "executeOnFirstTick", "trackOutput",
    "conditional", "needsRedstone", "__pool", "__runtimeId", "data", "ChestData", "buffer", "nbt")"""

    def __repr__(self) -> str :
        a = [i for i in dir(self) if (i[0:2] != "__" and i not in ["from_bytes","to_bytes","add_item","operation_code"])]
        b = "".join(["   %s => %s"%(i, print_test(getattr(self,i))) for i in a])
        return "<%s%s>" % (self.__class__.__name__,b)



def print_test(a) :
    if isinstance(a, nbt.TAG_Compound) : return a
    else : return a

def match_string_bytes(bytes_io:io.BytesIO) -> bytes:
    p = bytes_io.tell()
    b = bytes_io.getvalue()
    p2 = b.find(b'\0', p)
    strbytes = bytes_io.read(p2-p)
    bytes_io.seek(1, 1)
    return strbytes

def read_chest_data(SaveList:list,bytes_io:io.BytesIO) :
    name = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
    count = int.from_bytes(bytes_io.read(1),'big',signed=False)
    data = int.from_bytes(bytes_io.read(2),'big',signed=False)
    slotID = int.from_bytes(bytes_io.read(1),'big',signed=False)
    SaveList.append({"name":name, "count":count, "data":data, "slotID":slotID})

def write_chest_data(SaveList:list) :
    #{"name":name, "count":count, "data":data, "slotID":slotID}
    bytes_list = []
    for i in SaveList :
        bytes_list.append(i["name"].encode("utf-8"))
        bytes_list.append(b"\0")
        bytes_list.append(i["count"].to_bytes(1,'big',signed=False))
        bytes_list.append(i["data"].to_bytes(2,'big',signed=False))
        bytes_list.append(i["slotID"].to_bytes(1,'big',signed=False))
    return b"".join(bytes_list)


class CreateConstantString(OperationBase) :
    """
    将特定的 字符串 放入 方块池 。\n
    字符串 在 方块池 中的 ID 将按照调用此命令的顺序进行排序。\n
    如: 你第一次调用这个命令的时候，对应 字符串 的 ID 为 0 ，第二次就是 1 了。\n
    你最多只能添加到 65535。\n
    [译注: 通常情况下，字符串 是一个方块的 英文ID名 ，如 glass ]\n
    ---------------------------------\n
    实例化参数 string: 字符串\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x01

    def __init__(self, string:str) -> None:
        self.string = string

    @classmethod
    def from_bytes(cls, bytes_io:io.BytesIO) :
        a = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        return cls(a)

    def to_bytes(self) -> bytes :
        return b'\x01%s\x00' % self.string.encode("utf-8")
    
class PlaceBlockWithBlockStates1(OperationBase, metaclass=Two_Int_Meta) :
    """
    在画笔所在位置放置一个方块。\n
    同时指定欲放置方块的 方块状态 在方块池中的 ID 为 blockStatesConstantStringID\n
    且该方块在方块池中的 ID 为 blockConstantStringID\n
    方块状态 的格式形如 ["color": "orange"]\n
    ---------------------------------\n
    实例化参数 blockConstantStringID: 整数\n
    实例化参数 blockStatesConstantStringID: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x05

    def __init__(self, blockConstantStringID:int, blockStatesConstantStringID:int) -> None:
        self.blockConstantStringID = ctypes.c_uint16(blockConstantStringID).value
        self.blockStatesConstantStringID = ctypes.c_uint16(blockStatesConstantStringID).value
        self.__bytes_cache = b'%s%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.blockConstantStringID.to_bytes(2,'big',signed=False),
            self.blockStatesConstantStringID.to_bytes(2,'big',signed=False) )

    @classmethod
    def from_bytes(cls, bytes_io:io.BytesIO) :
        return cls(bytes_io.read(4))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt16ZValue0(OperationBase, metaclass=Unsigned_Int_Meta) :
    """
    将画笔的 Z 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x06

    def __init__(self, value:int) -> None:
        self.value = ctypes.c_uint16(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(2,'big',signed=False) )

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(2))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class PlaceBlock(OperationBase, metaclass=Two_Int_Meta) :
    """
    在画笔所在位置放置一个方块。\n
    该方块在方块池中的 ID 为 blockConstantStringID\n
    同时指定欲放置方块的 数据值(附加值) 为 blockData\n
    ---------------------------------\n
    实例化参数 blockConstantStringID: 整数\n
    实例化参数 blockData: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x07

    def __init__(self, blockConstantStringID:int, blockData:int) -> None:
        self.blockConstantStringID = ctypes.c_uint16(blockConstantStringID).value
        self.blockData = ctypes.c_uint16(blockData).value
        self.__bytes_cache = b'%s%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.blockConstantStringID.to_bytes(2,'big',signed=False),
            self.blockData.to_bytes(2,'big',signed=False) )

    @classmethod
    def from_bytes(cls, bytes_io:io.BytesIO) :
        return cls(bytes_io.read(4))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddZValue0(OperationBase) :
    """
    将画笔的 Z 坐标增加 1\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x08

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls, bytes_io:io.BytesIO) :
        return memory_list[4]

    def to_bytes(self) -> bytes :
        return b"\x08"

class NOP(OperationBase) :
    """
    不进行操作\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x09

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls()

    def to_bytes(self) -> bytes :
        return b'\x09'


class AddInt32ZValue0(OperationBase, metaclass=Unsigned_Int_Meta) :
    """
    将画笔的 Z 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x0C

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_uint32(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(4,'big',signed=False) )

    @classmethod
    def from_bytes(cls, bytes_io:io.BytesIO) :
        return cls(bytes_io.read(4))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class PlaceBlockWithBlockStates2(OperationBase) :
    """
    在画笔所在位置放置一个方块。\n
    该方块在方块池中的 ID 为 blockConstantStringID\n
    在画笔所在位置放置一个方块。同时指定欲放置方块的 方块状态 为 blockStatesString\n
    方块状态 blockStatesString 的格式形如 ["color": "orange"]\n
    ---------------------------------\n
    实例化参数 blockConstantStringID: 整数\n
    实例化参数 blockStatesString: 字符串\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x0D

    def __init__(self,blockConstantStringID:int,blockStatesString:str) -> None:
        self.blockConstantStringID = ctypes.c_uint16(blockConstantStringID).value
        self.blockStatesString = blockStatesString

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        blockConstantStringID = int.from_bytes(bytes_io.read(2),'big',signed=False)
        a = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        return cls(blockConstantStringID,a)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.blockConstantStringID.to_bytes(2,'big',signed=False),
            self.blockStatesString.encode("utf-8"),b"\0"
        ])


class AddXValue(OperationBase) :
    """
    将画笔的 X 坐标增加 1\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    value = 1
    operation_code = 0x0E

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls, bytes_io:io.BytesIO) :
        return memory_list[0]

    def to_bytes(self) -> bytes :
        return b"\x0e"

class SubtractXValue(OperationBase) :
    """
    将画笔的 X 坐标减少 1\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    value = -1
    operation_code = 0x0F

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return memory_list[1]

    def to_bytes(self) -> bytes :
        return b"\x0f"

class AddYValue(OperationBase) :
    """
    将画笔的 Y 坐标增加 1\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    value = 1
    operation_code = 0x10

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls, bytes_io:io.BytesIO) :
        return memory_list[2]

    def to_bytes(self) -> bytes :
        return b"\x10"

class SubtractYValue(OperationBase) :
    """
    将画笔的 Y 坐标减少 1\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    value = -1
    operation_code = 0x11

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return memory_list[3]

    def to_bytes(self) -> bytes :
        return b"\x11"

class AddZValue(OperationBase) :
    """
    将画笔的 Z 坐标增加 1\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    value = 1
    operation_code = 0x12

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return memory_list[4]

    def to_bytes(self) -> bytes :
        return b"\x12"

class SubtractZValue(OperationBase) :
    """
    将画笔的 Z 坐标减少 1\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    value = -1
    operation_code = 0x13

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return memory_list[5]

    def to_bytes(self) -> bytes :
        return b"\x13"


class AddInt16XValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 x 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x14

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int16(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(2,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(2))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt32XValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 x 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x15

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int32(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(4,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(4))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt16YValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 Y 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x16

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int16(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(2,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(2))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt32YValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 Y 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x17

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int32(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(4,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(4))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt16ZValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 Z 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x18

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int16(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(2,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(2))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt32ZValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 Z 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x19

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int32(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(4,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(4))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache


class SetCommandBlockData(OperationBase) :
    """
    在画笔当前位置的方块设置命令方块的数据\n
    无论是啥方块都可以加命令方块的数据，但只有命令方块才能起效\n
    ---------------------------------\n
    实例化参数 mode: 整数 {脉冲=0, 重复=1, 连锁=2}\n
    实例化参数 command: 字符串\n
    实例化参数 customName: 字符串\n
    实例化参数 tickdelay: 整数\n
    实例化参数 executeOnFirstTick: 布尔值\n
    实例化参数 trackOutput: 布尔值\n
    实例化参数 conditional: 布尔值\n
    实例化参数 needsRedstone: 布尔值\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x1a

    def __init__(self, mode:int, command:str,
                 customName:str="",tickdelay:int=0,
                 executeOnFirstTick:bool=False,trackOutput:bool=True,
                 conditional:bool=False,needsRedstone:bool=False) -> None:
        self.mode = ctypes.c_uint32(mode).value
        self.command = command
        self.customName = customName
        self.lastOutput = ""
        self.tickdelay = ctypes.c_int32(tickdelay).value
        self.executeOnFirstTick = ctypes.c_uint8(executeOnFirstTick).value
        self.trackOutput = ctypes.c_uint8(trackOutput).value
        self.conditional = ctypes.c_uint8(conditional).value
        self.needsRedstone = ctypes.c_uint8(needsRedstone).value

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        mode = int.from_bytes(bytes_io.read(4),'big',signed=False)
        command = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        customName = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        match_string_bytes(bytes_io)
        tickdelay = int.from_bytes(bytes_io.read(4),'big',signed=True)
        executeOnFirstTick = int.from_bytes(bytes_io.read(1),'big',signed=False)
        trackOutput = int.from_bytes(bytes_io.read(1),'big',signed=False)
        conditional = int.from_bytes(bytes_io.read(1),'big',signed=False)
        needsRedstone = int.from_bytes(bytes_io.read(1),'big',signed=False)
        return cls(mode,command,customName,tickdelay,executeOnFirstTick,
                   trackOutput,conditional,needsRedstone)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.mode.to_bytes(4,'big',signed=False),
            self.command.encode("utf-8"),b'\0',
            self.customName.encode("utf-8"),b'\0',
            self.lastOutput.encode("utf-8"),b'\0',
            self.tickdelay.to_bytes(4,'big',signed=True),
            self.executeOnFirstTick.to_bytes(1,'big',signed=False),
            self.trackOutput.to_bytes(1,'big',signed=False),
            self.conditional.to_bytes(1,'big',signed=False),
            self.needsRedstone.to_bytes(1,'big',signed=False)
        ])

class PlaceBlockWithCommandBlockData(OperationBase) :
    """
    在画笔当前位置放置方块池中 ID 为 blockConstantStringID 的方块，\n
    且该方块的 方块数据值(附加值) 为 blockData\n
    放置完成后，为这个方块设置 命令方块 的数据(若可行的话)\n
    无论是啥方块都可以加命令方块的数据，但只有命令方块才能起效\n
    ---------------------------------\n
    实例化参数 blockConstantStringID: 整数\n
    实例化参数 blockData: 整数\n
    实例化参数 mode: 整数 {脉冲=0, 重复=1, 连锁=2}\n
    实例化参数 command: 字符串\n
    实例化参数 customName: 字符串\n
    实例化参数 tickdelay: 整数\n
    实例化参数 executeOnFirstTick: 布尔值\n
    实例化参数 trackOutput: 布尔值\n
    实例化参数 conditional: 布尔值\n
    实例化参数 needsRedstone: 布尔值\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x1b

    def __init__(self, blockConstantStringID:int,
                 blockData:int, mode:int, command:str,
                 customName:str="",tickdelay:int=0,
                 executeOnFirstTick:bool=False,trackOutput:bool=True,
                 conditional:bool=False,needsRedstone:bool=False) -> None:
        self.blockConstantStringID = ctypes.c_uint16(blockConstantStringID).value
        self.blockData = ctypes.c_uint16(blockData).value
        self.mode = ctypes.c_uint32(mode).value
        self.command = command
        self.customName = customName
        self.lastOutput = ""
        self.tickdelay = ctypes.c_int32(tickdelay).value
        self.executeOnFirstTick = ctypes.c_uint8(executeOnFirstTick).value
        self.trackOutput = ctypes.c_uint8(trackOutput).value
        self.conditional = ctypes.c_uint8(conditional).value
        self.needsRedstone = ctypes.c_uint8(needsRedstone).value

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        blockConstantStringID = int.from_bytes(bytes_io.read(2),'big',signed=False)
        blockData = int.from_bytes(bytes_io.read(2),'big',signed=False)
        mode = int.from_bytes(bytes_io.read(4),'big',signed=False)
        command = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        customName = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        match_string_bytes(bytes_io)
        tickdelay = int.from_bytes(bytes_io.read(4),'big',signed=True)
        executeOnFirstTick = int.from_bytes(bytes_io.read(1),'big',signed=False)
        trackOutput = int.from_bytes(bytes_io.read(1),'big',signed=False)
        conditional = int.from_bytes(bytes_io.read(1),'big',signed=False)
        needsRedstone = int.from_bytes(bytes_io.read(1),'big',signed=False)
        return cls(blockConstantStringID,blockData,
                   mode,command,customName,tickdelay,executeOnFirstTick,
                   trackOutput,conditional,needsRedstone)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.blockConstantStringID.to_bytes(2,'big',signed=False),
            self.blockData.to_bytes(2,'big',signed=False),
            self.mode.to_bytes(4,'big',signed=False),
            self.command.encode("utf-8"),b'\0',
            self.customName.encode("utf-8"),b'\0',
            self.lastOutput.encode("utf-8"),b'\0',
            self.tickdelay.to_bytes(4,'big',signed=True),
            self.executeOnFirstTick.to_bytes(1,'big',signed=False),
            self.trackOutput.to_bytes(1,'big',signed=False),
            self.conditional.to_bytes(1,'big',signed=False),
            self.needsRedstone.to_bytes(1,'big',signed=False)
        ])


class AddInt8XValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 x 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x1c

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int8(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(1,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(1))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt8YValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 y 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x1d

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int8(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(1,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(1))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class AddInt8ZValue(OperationBase, metaclass=Signed_Int_Meta) :
    """
    将画笔的 z 坐标增加 value\n
    ---------------------------------\n
    实例化参数 value: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x1e

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_int8(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(1,'big',signed=True) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(1))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache


class UseRuntimeIDPool(OperationBase, metaclass=Unsigned_Int_Meta) :
    """
    使用预设的 运行时ID方块池\n
    poolId(预设ID) 是 PhoenixBuilder 内的值。\n
    网易MC( 1.17.0 @ 2.0.5 )下的 poolId 被我们定为 117。 \n
    每一个 运行时ID 都对应着一个方块，而且包含其 方块数据值(附加值)\n
    ---------------------------------\n
    实例化参数 pool: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x1f

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_uint8(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(1,'big',signed=False) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(1))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class PlaceRuntimeBlock(OperationBase, metaclass=Unsigned_Int_Meta) :
    """
    使用特定的 运行时ID 放置方块\n
    ---------------------------------\n
    实例化参数 runtimeId: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x20

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_uint16(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(2,'big',signed=False) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(2))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache

class PlaceBlockWithRuntimeId(OperationBase, metaclass=Unsigned_Int_Meta) :
    """
    使用特定的 运行时ID 放置方块\n
    ---------------------------------\n
    实例化参数 runtimeId: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x21

    def __init__(self,value:int) -> None:
        self.value = ctypes.c_uint32(value).value
        self.__bytes_cache = b'%s%s' % ( 
            self.operation_code.to_bytes(1,'big',signed=False),
            self.value.to_bytes(4,'big',signed=False) )

    def __setattr__(self, name:str, value) :
        if hasattr(self, name) : raise Exception("无法修改 %s 属性" % name)
        else : super().__setattr__(name, value)


    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls(bytes_io.read(4))

    def to_bytes(self) -> bytes :
        return self.__bytes_cache



class PlaceRuntimeBlockWithCommandBlockData(OperationBase) :
    """
    使用特定的 运行时ID \n
    在当前画笔的位置放置命令方块\n
    ---------------------------------\n
    实例化参数 runtimeId: 整数\n
    实例化参数 mode: 整数 {脉冲=0, 重复=1, 连锁=2}\n
    实例化参数 command: 字符串\n
    实例化参数 customName: 字符串\n
    实例化参数 tickdelay: 整数\n
    实例化参数 executeOnFirstTick: 布尔值\n
    实例化参数 trackOutput: 布尔值\n
    实例化参数 conditional: 布尔值\n
    实例化参数 needsRedstone: 布尔值\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x22

    def __init__(self, runtimeId:int, mode:int, command:str,
                 customName:str="",tickdelay:int=0,
                 executeOnFirstTick:bool=False,trackOutput:bool=True,
                 conditional:bool=False,needsRedstone:bool=False) -> None:
        self.runtimeId = ctypes.c_uint16(runtimeId).value
        self.mode = ctypes.c_uint32(mode).value
        self.command = command
        self.customName = customName
        self.lastOutput = ""
        self.tickdelay = ctypes.c_int32(tickdelay).value
        self.executeOnFirstTick = ctypes.c_uint8(executeOnFirstTick).value
        self.trackOutput = ctypes.c_uint8(trackOutput).value
        self.conditional = ctypes.c_uint8(conditional).value
        self.needsRedstone = ctypes.c_uint8(needsRedstone).value

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        runtimeId = int.from_bytes(bytes_io.read(2),'big',signed=False)
        mode = int.from_bytes(bytes_io.read(4),'big',signed=False)
        command = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        customName = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        match_string_bytes(bytes_io)
        tickdelay = int.from_bytes(bytes_io.read(4),'big',signed=True)
        executeOnFirstTick = int.from_bytes(bytes_io.read(1),'big',signed=False)
        trackOutput = int.from_bytes(bytes_io.read(1),'big',signed=False)
        conditional = int.from_bytes(bytes_io.read(1),'big',signed=False)
        needsRedstone = int.from_bytes(bytes_io.read(1),'big',signed=False)
        return cls(runtimeId,
                   mode,command,customName,tickdelay,executeOnFirstTick,
                   trackOutput,conditional,needsRedstone)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.runtimeId.to_bytes(2,'big',signed=False),
            self.mode.to_bytes(4,'big',signed=False),
            self.command.encode("utf-8"),b'\0',
            self.customName.encode("utf-8"),b'\0',
            self.lastOutput.encode("utf-8"),b'\0',
            self.tickdelay.to_bytes(4,'big',signed=True),
            self.executeOnFirstTick.to_bytes(1,'big',signed=False),
            self.trackOutput.to_bytes(1,'big',signed=False),
            self.conditional.to_bytes(1,'big',signed=False),
            self.needsRedstone.to_bytes(1,'big',signed=False)
        ])

class PlaceRuntimeBlockWithCommandBlockDataAndUint32RuntimeID(OperationBase) :
    """
    使用特定的 运行时ID \n
    在当前画笔的位置放置命令方块\n
    ---------------------------------\n
    实例化参数 runtimeId: 整数\n
    实例化参数 mode: 整数 {脉冲=0, 重复=1, 连锁=2}\n
    实例化参数 command: 字符串\n
    实例化参数 customName: 字符串\n
    实例化参数 tickdelay: 整数\n
    实例化参数 executeOnFirstTick: 布尔值\n
    实例化参数 trackOutput: 布尔值\n
    实例化参数 conditional: 布尔值\n
    实例化参数 needsRedstone: 布尔值\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x23

    def __init__(self, runtimeId:int, mode:int, command:str,
                 customName:str="",tickdelay:int=0,
                 executeOnFirstTick:bool=False,trackOutput:bool=True,
                 conditional:bool=False,needsRedstone:bool=False) -> None:
        self.runtimeId = ctypes.c_uint32(runtimeId).value
        self.mode = ctypes.c_uint32(mode).value
        self.command = command
        self.customName = customName
        self.lastOutput = ""
        self.tickdelay = ctypes.c_int32(tickdelay).value
        self.executeOnFirstTick = ctypes.c_uint8(executeOnFirstTick).value
        self.trackOutput = ctypes.c_uint8(trackOutput).value
        self.conditional = ctypes.c_uint8(conditional).value
        self.needsRedstone = ctypes.c_uint8(needsRedstone).value

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        runtimeId = int.from_bytes(bytes_io.read(4),'big',signed=False)
        mode = int.from_bytes(bytes_io.read(4),'big',signed=False)
        command = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        customName = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        match_string_bytes(bytes_io)
        tickdelay = int.from_bytes(bytes_io.read(4),'big',signed=True)
        executeOnFirstTick = int.from_bytes(bytes_io.read(1),'big',signed=False)
        trackOutput = int.from_bytes(bytes_io.read(1),'big',signed=False)
        conditional = int.from_bytes(bytes_io.read(1),'big',signed=False)
        needsRedstone = int.from_bytes(bytes_io.read(1),'big',signed=False)
        return cls(runtimeId,
                   mode,command,customName,tickdelay,executeOnFirstTick,
                   trackOutput,conditional,needsRedstone)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.runtimeId.to_bytes(4,'big',signed=False),
            self.mode.to_bytes(4,'big',signed=False),
            self.command.encode("utf-8"),b'\0',
            self.customName.encode("utf-8"),b'\0',
            self.lastOutput.encode("utf-8"),b'\0',
            self.tickdelay.to_bytes(4,'big',signed=True),
            self.executeOnFirstTick.to_bytes(1,'big',signed=False),
            self.trackOutput.to_bytes(1,'big',signed=False),
            self.conditional.to_bytes(1,'big',signed=False),
            self.needsRedstone.to_bytes(1,'big',signed=False)
        ])

class PlaceCommandBlockWithCommandBlockData(OperationBase) :
    """
    使用特定的 运行时ID \n
    在当前画笔的位置放置命令方块\n
    ---------------------------------\n
    实例化参数 data: 整数\n
    实例化参数 mode: 整数 {脉冲=0, 重复=1, 连锁=2}\n
    实例化参数 command: 字符串\n
    实例化参数 customName: 字符串\n
    实例化参数 tickdelay: 整数\n
    实例化参数 executeOnFirstTick: 布尔值\n
    实例化参数 trackOutput: 布尔值\n
    实例化参数 conditional: 布尔值\n
    实例化参数 needsRedstone: 布尔值\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x24

    def __init__(self, data:int, mode:int, command:str,
                 customName:str="",tickdelay:int=0,
                 executeOnFirstTick:bool=False,trackOutput:bool=True,
                 conditional:bool=False,needsRedstone:bool=False) -> None:
        self.data = ctypes.c_uint16(data).value
        self.mode = ctypes.c_uint32(mode).value
        self.command = command
        self.customName = customName
        self.lastOutput = ""
        self.tickdelay = ctypes.c_int32(tickdelay).value
        self.executeOnFirstTick = ctypes.c_uint8(executeOnFirstTick).value
        self.trackOutput = ctypes.c_uint8(trackOutput).value
        self.conditional = ctypes.c_uint8(conditional).value
        self.needsRedstone = ctypes.c_uint8(needsRedstone).value

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        data = int.from_bytes(bytes_io.read(2),'big',signed=False)
        mode = int.from_bytes(bytes_io.read(4),'big',signed=False)
        command = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        customName = match_string_bytes(bytes_io).decode("utf-8", errors="ignore")
        match_string_bytes(bytes_io)
        tickdelay = int.from_bytes(bytes_io.read(4),'big',signed=True)
        executeOnFirstTick = int.from_bytes(bytes_io.read(1),'big',signed=False)
        trackOutput = int.from_bytes(bytes_io.read(1),'big',signed=False)
        conditional = int.from_bytes(bytes_io.read(1),'big',signed=False)
        needsRedstone = int.from_bytes(bytes_io.read(1),'big',signed=False)
        return cls(data,
                   mode,command,customName,tickdelay,executeOnFirstTick,
                   trackOutput,conditional,needsRedstone)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.data.to_bytes(2,'big',signed=False),
            self.mode.to_bytes(4,'big',signed=False),
            self.command.encode("utf-8"),b'\0',
            self.customName.encode("utf-8"),b'\0',
            self.lastOutput.encode("utf-8"),b'\0',
            self.tickdelay.to_bytes(4,'big',signed=True),
            self.executeOnFirstTick.to_bytes(1,'big',signed=False),
            self.trackOutput.to_bytes(1,'big',signed=False),
            self.conditional.to_bytes(1,'big',signed=False),
            self.needsRedstone.to_bytes(1,'big',signed=False)
        ])


class PlaceRuntimeBlockWithChestData(OperationBase) :
    """
    在画笔所在位置放置一个 runtimeId(特定的 运行时ID) \n
    所表示的方块，并向此方块载入数据\n
    ---------------------------------\n
    实例化参数 runtimeId: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    实例化方法 add_item: 在箱子内添加物品\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x25

    def __init__(self, runtimeId:int, ChestData:list=[]) -> None:
        self.runtimeId = ctypes.c_uint16(runtimeId).value
        self.ChestData:ChestDataType = ChestData

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        runtimeId = int.from_bytes(bytes_io.read(2),'big',signed=False)
        count = int.from_bytes(bytes_io.read(1),'big',signed=False)
        ChestData = []
        for i in range(count) : read_chest_data(ChestData,bytes_io)
        return cls(runtimeId,ChestData)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.runtimeId.to_bytes(2,'big',signed=False),
            len(self.ChestData).to_bytes(1,'big',signed=False),
            write_chest_data(self.ChestData)
        ])
    
    def add_item(self,name:str,count:int,data:int,slotID:int) :
        self.ChestData.append(
            {
                "name":name, 
                "count":ctypes.c_uint8(count).value, 
                "data":ctypes.c_uint16(data).value, 
                "slotID":ctypes.c_uint8(slotID).value
            }
        )

class PlaceRuntimeBlockWithChestDataAndUint32RuntimeID(OperationBase) :
    """
    在画笔所在位置放置一个 runtimeId(特定的 运行时ID) \n
    所表示的方块，并向此方块载入数据\n
    ---------------------------------\n
    实例化参数 runtimeId: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    实例化方法 add_item: 在箱子内添加物品\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x26

    def __init__(self, runtimeId:int, ChestData:list=[]) -> None:
        self.runtimeId = ctypes.c_uint32(runtimeId).value
        self.ChestData:ChestDataType = ChestData

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        runtimeId = int.from_bytes(bytes_io.read(4),'big',signed=False)
        count = int.from_bytes(bytes_io.read(1),'big',signed=False)
        ChestData = []
        for i in range(count) : read_chest_data(ChestData,bytes_io)
        return cls(runtimeId,ChestData)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.runtimeId.to_bytes(4,'big',signed=False),
            len(self.ChestData).to_bytes(1,'big',signed=False),
            write_chest_data(self.ChestData)
        ])
    
    def add_item(self,name:str,count:int,data:int,slotID:int) :
        self.ChestData.append(
            {
                "name":name, 
                "count":ctypes.c_uint8(count).value, 
                "data":ctypes.c_uint16(data).value, 
                "slotID":ctypes.c_uint8(slotID).value
            }
        )


class AssignDebugData(OperationBase) :
    """
    记录调试数据，不对建造过程产生任何影响。\n
    ---------------------------------\n
    实例化参数 buffer: 字节数组\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x27

    def __init__(self, buffer:bytes) -> None:
        self.buffer = buffer

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        length = int.from_bytes(bytes_io.read(4),'big',signed=False)
        buffer = bytes_io.read(length)
        return cls(buffer)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            len(self.buffer).to_bytes(4,'big',signed=False),
            self.buffer
        ])


class PlaceBlockWithChestData(OperationBase) :
    """
    在画笔所在位置放置一个 blockConstantStringID \n
    所表示的方块，并向此方块载入数据\n
    ---------------------------------\n
    实例化参数 blockConstantStringID: 整数\n
    实例化参数 blockData: 整数\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    实例化方法 add_item: 在箱子内添加物品\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x28

    def __init__(self, blockConstantStringID:int, blockData:int, ChestData:list=[]) -> None:
        self.blockConstantStringID = ctypes.c_uint16(blockConstantStringID).value
        self.blockData = ctypes.c_uint16(blockData).value
        self.ChestData:ChestDataType = ChestData

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        blockConstantStringID = int.from_bytes(bytes_io.read(2),'big',signed=False)
        blockData = int.from_bytes(bytes_io.read(2),'big',signed=False)
        count = int.from_bytes(bytes_io.read(1),'big',signed=False)
        ChestData = []
        for i in range(count) : read_chest_data(ChestData,bytes_io)
        return cls(blockConstantStringID,blockData,ChestData)

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.blockConstantStringID.to_bytes(2,'big',signed=False),
            self.blockData.to_bytes(2,'big',signed=False),
            len(self.ChestData).to_bytes(1,'big',signed=False),
            write_chest_data(self.ChestData)
        ])
    
    def add_item(self,name:str,count:int,data:int,slotID:int) :
        self.ChestData.append(
            {
                "name":name, 
                "count":ctypes.c_uint8(count).value, 
                "data":ctypes.c_uint16(data).value, 
                "slotID":ctypes.c_uint8(slotID).value
            }
        )


class PlaceBlockWithNBTData(OperationBase) :
    """
    放置一个 blockConstantStringID 所表示的方块\n
    且指定它的 方块状态 在方块池中的 ID 为 blockStatesConstantStringID，\n
    然后指定 nbt 所表示的由小端序 NBT 所存储的 方块实体 数据\n
    ---------------------------------\n
    实例化参数 blockConstantStringID: 整数\n
    实例化参数 blockStatesConstantStringID: 整数\n
    实例化参数 nbt: 对象nbt.NBTTagCompound\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x29

    def __init__(self, blockConstantStringID:int, blockStatesConstantStringID:int, nbt:nbt.TAG_Compound) -> None:
        self.blockConstantStringID = ctypes.c_uint16(blockConstantStringID).value
        self.blockStatesConstantStringID = ctypes.c_uint16(blockStatesConstantStringID).value
        self.nbt = nbt

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        blockConstantStringID = int.from_bytes(bytes_io.read(2),'big',signed=False)
        blockStatesConstantStringID = int.from_bytes(bytes_io.read(2),'big',signed=False)
        int.from_bytes(bytes_io.read(2),'big',signed=False)
        newReader = io.BytesIO(bytes_io.getvalue()[bytes_io.tell():])
        nbt1 = nbt.read_from_nbt_file(newReader, byteorder='little').get_tag()
        bytes_io.read(newReader.tell())
        newReader.close()
        return cls(blockConstantStringID,blockStatesConstantStringID,nbt1)

    def to_bytes(self) -> bytes :
        newReader = io.BytesIO(b"")
        nbt.write_to_nbt_file(newReader, self.nbt, byteorder='little')
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            self.blockConstantStringID.to_bytes(2,'big',signed=False),
            self.blockStatesConstantStringID.to_bytes(2,'big',signed=False),
            self.blockStatesConstantStringID.to_bytes(2,'big',signed=False),
            newReader.getvalue()
        ])


class Terminate(OperationBase) :
    """
    停止读入\n
    ---------------------------------\n
    实例化方法 to_bytes: 将对象转为字节数组\n
    ---------------------------------\n
    类方法 from_bytes: 通过字节转变为对象
    """

    operation_code = 0x58

    def __init__(self) -> None:
        pass

    @classmethod
    def from_bytes(cls,bytes_io:io.BytesIO) :
        return cls()

    def to_bytes(self) -> bytes :
        return b''.join([
            self.operation_code.to_bytes(1,'big',signed=False),
            b"E"
        ])




memory_list = [AddXValue(), SubtractXValue(), AddYValue(), SubtractYValue(), AddZValue(), SubtractZValue()]

OPERATION_BYTECODES = { 
    b"\x01" : CreateConstantString,
    b"\x05" : PlaceBlockWithBlockStates1,
    b"\x06" : AddInt16ZValue0,
    b"\x07" : PlaceBlock,
    b"\x08" : AddZValue0,
    b"\x09" : NOP,
    b"\x0c" : AddInt32ZValue0,
    b"\x0d" : PlaceBlockWithBlockStates2,
    b"\x0e" : AddXValue,
    b"\x0f" : SubtractXValue,
    b"\x10" : AddYValue,
    b"\x11" : SubtractYValue,
    b"\x12" : AddZValue,
    b"\x13" : SubtractZValue,
    b"\x14" : AddInt16XValue,
    b"\x15" : AddInt32XValue,
    b"\x16" : AddInt16YValue,
    b"\x17" : AddInt32YValue,
    b"\x18" : AddInt16ZValue,
    b"\x19" : AddInt32ZValue,
    b"\x1a" : SetCommandBlockData,
    b"\x1b" : PlaceBlockWithCommandBlockData,
    b"\x1c" : AddInt8XValue,
    b"\x1d" : AddInt8YValue,
    b"\x1e" : AddInt8ZValue,
    b"\x1f" : UseRuntimeIDPool,
    b"\x20" : PlaceRuntimeBlock,
    b"\x21" : PlaceBlockWithRuntimeId,
    b"\x22" : PlaceRuntimeBlockWithCommandBlockData,
    b"\x23" : PlaceRuntimeBlockWithCommandBlockDataAndUint32RuntimeID,
    b"\x24" : PlaceCommandBlockWithCommandBlockData,
    b"\x25" : PlaceRuntimeBlockWithChestData,
    b"\x26" : PlaceRuntimeBlockWithChestDataAndUint32RuntimeID,
    b"\x27" : AssignDebugData,
    b"\x28" : PlaceBlockWithChestData,
    b"\x29" : PlaceBlockWithNBTData,
    b"\x58" : Terminate,
}