from . import nbt, Block
from .__private import TypeCheckList, BiList
from io import IOBase
from typing import Union,List,Dict,Tuple,Literal,TypedDict
import os, json, re, array, ctypes, itertools, functools
from math import floor







class CommonStructure :
    """
    基岩版通用结构对象
    -----------------------
    * 所有结构文件将会转换为该结构对象（可能会损失信息）
    * 方块按照 xyz 顺序进行储存（z坐标变化最频繁）
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构保存时的位置
    * 可用属性 block_index : 方块索引列表（-1代表跳过）
    * 可用属性 contain_index : 方块是否含有其他方块，方块索引列表（例如含水，-1代表跳过）
    * 可用属性 block_palette : 方块对象列表（索引指向该列表内的方块）
    * 可用属性 entity_nbt : 实体对象列表
    * 可用属性 block_nbt : 以方块索引字符串数字和nbt对象组成的字典
    -----------------------
    * 可用类方法 from_buffer : 指定解码器，并且通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as :指定编码器，并且通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self, size:Tuple[int, int, int] = (0, 0, 0)):
        Volume = size[0] * size[1] * size[2]
        self.size: array.array = array.array("i", size)
        self.origin: array.array = array.array("i", [0,0,0])
        self.block_index: array.array[int] = array.array("i", b"\x00\x00\x00\x00" * Volume)
        self.contain_index: array.array[int] = array.array("i", b"\xff\xff\xff\xff" * Volume)
        self.block_palette: List[Block] = BiList()
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def __pos_to_index__(self, pos_x:int, pos_y:int, pos_z:int) :
        return pos_x * self.size[1] * self.size[2] + \
        pos_y * self.size[2] + pos_z


    @classmethod
    def from_buffer(cls, Decoder, Reader:Union[str, bytes, IOBase]) :
        Common = cls()
        Decoder(Common).decode(Reader)
        return Common

    def save_as(self, Encoder, Writer:Union[str, IOBase], IgnoreAir:bool=True) :
        """
        * 使用json格式输出时，Writer一定为字符串缓冲区或带有编码的文件缓冲区
        * IgnoreAir参数，不在mcstructure和schematic文件中生效
        """
        Encoder(self, IgnoreAir).encode(Writer)


    @property
    def volume(self) :
        return self.size[0] * self.size[1] * self.size[2]

    def get_block(self, pos_x:int, pos_y:int, pos_z:int) -> Union[None, Block] :
        index = self.__pos_to_index__(floor(pos_x), floor(pos_y), floor(pos_z))
        if not(-1 < index < self.volume) : return None
        if self.block_index[index] < 0 : return {"name":"structure_void", "states":{}} 
        Block = self.block_palette[ self.block_index[index] ].copy()
        Block["states"] = Block["states"].copy()
        return Block
    



