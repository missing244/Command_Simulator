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
    * 可用属性 block_index : 方块索引列表
    * 可用属性 contain_index : 方块是否含有其他方块，方块索引列表（例如含水，-1代表跳过）
    * 可用属性 block_palette : 方块对象列表（索引指向该列表内的方块）
    * 可用属性 entity_nbt : 实体对象列表
    * 可用属性 block_nbt : 以方块索引字符串数字和nbt对象组成的字典
    -----------------------
    * 反序列化方法 from_buffer : 指定解码器，并且通过路径、字节数字 或 流式缓冲区 生成对象
    * 序列化方法 save_as : 指定编码器，并且通过路径 或 流式缓冲区 保存对象数据
    -----------------------
    * 可用方法 get_block : 传入非负整数坐标，返回方块对象
    * 可用方法 set_block : 传入非负整数坐标和方块，修改方块
    -----------------------
    * Coder注意事项1 : 部分属性均不可直接修改，请调用对象方法进行修改，以免数据不正确
    """


    def __init__(self, size:Tuple[int, int, int] = (0, 0, 0)) :
        Volume = size[0] * size[1] * size[2]
        self.size: array.array = array.array("i", size)                                         #修改元素✘，赋值✘
        self.origin: array.array = array.array("i", [0,0,0])                                    #修改元素✔，赋值✘
        self.block_index: array.array[int] = array.array("i", b"\x00\x00\x00\x00" * Volume)     #修改元素✔，赋值✘
        self.contain_index: array.array[int] = array.array("i", b"\xff\xff\xff\xff" * Volume)   #修改元素✔，赋值✘
        self.block_palette: BiList = BiList()                                                   #修改元素✔，赋值✘
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)  #修改元素✔，赋值✘
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}                                        #修改元素✔，赋值✘

        #以下私有属性为自动更新变量，只做读取使用
        self.__S_xy = size[1] * size[2]
        self.__volume = size[0] * size[1] * size[2]

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


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


    def get_block(self, pos_x:int, pos_y:int, pos_z:int) -> Union[None, Block] :
        index = pos_x * self.__S_xy + pos_y * self.size[2] + pos_z
        return self.block_palette[self.block_index[index]] if (index < self.__volume) else None

    def set_block(self, pos_x:int, pos_y:int, pos_z:int, block:Union[int, Block]) :
        index = pos_x * self.__S_xy + pos_y * self.size[2] + pos_z
        if block.__class__ is int : self.block_index[index] = block 
        else : self.block_index[index] = self.block_palette.append(block)
    
    def get_blockNBT(self, pos_x:int, pos_y:int, pos_z:int) -> Union[None, nbt.TAG_Compound] :
        index = pos_x * self.__S_xy + pos_y * self.size[2] + pos_z
        return self.block_nbt.get(index, None)

    def set_blockNBT(self, pos_x:int, pos_y:int, pos_z:int, nbt:nbt.TAG_Compound) :
        index = pos_x * self.__S_xy + pos_y * self.size[2] + pos_z
        self.block_nbt[index] = nbt
    


