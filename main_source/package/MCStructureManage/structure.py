from . import nbt,TypeCheckList,Encoder,Decoder
from io import BytesIO,RawIOBase
from typing import Union,List,Dict,Tuple,Literal,TypedDict
import os, json, re, array, ctypes, itertools, functools
from math import floor

class BLOCK_TYPE(TypedDict): 
    name: str
    states: Union[str, ctypes.c_byte, ctypes.c_short, ctypes.c_int, ctypes.c_long]

SupportEncoder = Union[Encoder.BDX, Encoder.MCSTRUCTURE]
SupportDecoder = Union[Decoder.BDX, Decoder.MCSTRUCTURE]



class CommonStructure :

    def __init__(self):
        self.size: array.array = array.array("i", [0,0,0])
        self.origin: array.array = array.array("i", [0,0,0])
        self.block_index: array.array[int] = array.array("i")
        self.water_log: array.array[int] = array.array("i")
        self.block_palette: List[BLOCK_TYPE] = TypeCheckList().setChecker(dict)
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
    def from_buffer(cls, Decoder:SupportDecoder, Reader:Union[str, bytes, RawIOBase]) :
        Common = cls()
        Decoder(Common).decode(Reader)
        return Common

    def save_as(self, Encoder:SupportEncoder, Writer:Union[str, RawIOBase]) :
        Encoder(self).decode(Writer)


    @property
    def volume(self) :
        return self.size[0] * self.size[1] * self.size[2]

    def get_block(self, pos_x:int, pos_y:int, pos_z:int) -> Union[None, BLOCK_TYPE] :
        index = self.__pos_to_index__(floor(pos_x), floor(pos_y), floor(pos_z))
        if not(-1 < index < self.volume) : return None
        if self.block_index[index] < 0 : return {"name":"structure_void", "states":{}} 
        Block = self.block_palette[ self.block_index[index] ].copy()
        Block["states"] = Block["states"].copy()
        return Block
    



