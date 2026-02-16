from . import nbt, MCBELab
from typing import Union,Dict,Tuple
from types import MappingProxyType
import json


class BlockMeta(type) :

    def __init__(self, *args, **kwds) :
        super().__init__(*args, **kwds)
        self.__cache:Dict[Tuple[str, Union[int, str, tuple]], "Block"] = {}

    def __call__(self, id:str, states:Union[int, str, Dict[str, Union[bool, int, str]]]={}, waterlogged:bool=False) :
        CacheKey = (id, waterlogged, *states.items()) if hasattr(states, "items") else (id, waterlogged, states)

        if CacheKey in self.__cache : return self.__cache[CacheKey]
        self.__cache[CacheKey] = super().__call__(id, states, waterlogged)
        return self.__cache[CacheKey]

class Block(metaclass=BlockMeta) :
    """
    通用方块对象
    ---------------------------------
    * 实现了单例模式和哈希接口的方块对象
    ---------------------------------
    * 实例化参数 name : 方块ID字符串，如无命名空间则自动添加命名空间
    * 实例化参数 states : 方块状态传参，支持整数、方块状态字符串、方块状态字典
    * 实例化参数 waterlogged : 方块是否含水
    * states 会自动舍去无效的状态参数
    ---------------------------------
    * 属性 dataValue : 方块id和方块状态对应的数据值，无法互相转换的数据值会设置为0
    ---------------------------------
    * 可用类方法 from_nbt: 将 {name:"a", states:{color:"red"}} 的方块nbt转换为方块对象
    * 可用方法 to_nbt: 生成 方块对象 对应的nbt对象
    """

    def __str__(self):
        return f'<Block name="{self.name}" states={self.states} waterlog={self.waterlogged}>'
    
    def __repr__(self):
        return f'<Block name="{self.name}" states={self.states}>'
    
    def __delattr__(self, name):
        raise Exception("无法删除任何属性")
    
    def __setattr__(self, name, value):
        if hasattr(self, name) : raise Exception("无法修改任何属性")
        super().__setattr__(name, value)
    

    def __hash__(self):
        return self.__hash

    def __eq__(self, value):
        return value.__hash__()  == self.__hash


    def __init__(self, name:str, states:Union[int, str, Dict[str, Union[bool, int, str]]], waterlogged:bool=False) :
        if "." in name : BlockID, BlockState = MCBELab.RunawayTransforBlock(name)
        else : BlockID, BlockState = MCBELab.TransforBlock(name, states)
        self.name = BlockID
        self.states = MappingProxyType(BlockState)
        self.waterlogged = waterlogged
        self.dataValue = MCBELab.TransforDatavalue(self.name, self.states)
        self.runawayID = MCBELab.BlockTransforRunaway(self.name, self.states)
        self.blockString = "%s[%s]" % (BlockID, json.dumps(BlockState, separators=(',', '='))[1:][:-1])
        
        self.__hash = (self.name, waterlogged, *self.states.items()).__hash__()


    @classmethod
    def from_nbt(cls, nbt_obj:nbt.TAG_Compound) :
        dict1 = {}
        for i,j in nbt_obj.items() :
            if j.__class__ is nbt.TAG_String : dict1[i] = j.value
            elif j.__class__ is nbt.TAG_Int : dict1[i] = j.value
            elif j.__class__ is nbt.TAG_Byte : dict1[i] = bool(j.value)
        return cls(nbt_obj["name"].value, dict1)

    def to_nbt(self) :
        node = nbt.NBT_Builder()
        dict1 = {}
        for i,j in self.states.items() :
            if j.__class__ is bool : dict1[i] = node.byte(j)
            elif j.__class__ is int : dict1[i] = node.int(j)
            elif j.__class__ is str : dict1[i] = node.string(j)
        return node.compound(name=node.string(self.name), states=node.compound(**dict1), 
            val=node.short(self.dataValue[1]), version=node.int(17959425)).build()



