from .__private import TypeCheckList
from . import nbt, StructureBDX, StructureMCS
from . import StructureRUNAWAY, StructureSCHEMATIC

from typing import Union,List,Dict,Tuple,Literal,TypedDict
from types import MappingProxyType
import abc, re, os, io, json, array, itertools, urllib.parse, ctypes
CommandBlockIDTest = re.compile("command_block$")
CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
BlockState = json.load(fp=open(os.path.join(CurrentPath, "res", "blockstate.json"), "r", encoding="utf-8"))
OldBlockData = json.load(fp=open(os.path.join(CurrentPath, "res", "flatten.json"), "r", encoding="utf-8"))

SpecialStates = {"direction":{"south":0, "west":1, "north":2, "east":3}, 
    "facing_direction":{"south":0, "west":1, "north":2, "east":5}}
def TransforBlock(id:str, value:Union[int, str, dict]) -> Tuple[str, Dict[str, Union[bool, int, str]]]:
    BlockID = f"minecraft:{id}" if id.find("minecraft:") else id
    if value.__class__ is str : value = StringTransforBlockStates(value)

    if BlockID in BlockState :
        NewBlockID = BlockID
        NewBlockState = BlockState[BlockID].get(bin(value), None)
        if NewBlockState is None : NewBlockState = BlockState[BlockID]["default"]
    elif BlockID in OldBlockData["block"] : 
        NewBlockID = OldBlockData["block"][BlockID]["block_id"]
        NewBlockState = OldBlockData["block"][BlockID]["block_data"]
    else : return (BlockID, {})

    NewBlockState = dict( sorted(NewBlockState.items()) )
    if isinstance(value, dict) : 
        new_value = value.copy()
        cardinal_direction = new_value.get("minecraft:cardinal_direction", None)
        if cardinal_direction in SpecialStates["direction"] :
            if "facing_direction" in NewBlockState : 
                new_value["facing_direction"] = SpecialStates["facing_direction"][cardinal_direction]
            elif "direction" in NewBlockState : 
                new_value["direction"] = SpecialStates["direction"][cardinal_direction]
            del new_value["minecraft:cardinal_direction"]
        NewBlockState.update( (i,j) for i,j in new_value.items() 
        if (i in NewBlockState) and (j in BlockState[BlockID]["support_value"][i]) )
    return (NewBlockID, NewBlockState)

def TransforDatavalue(block:"Block") -> Tuple[Union[int, None], int] :
    block_id_data = StructureSCHEMATIC.Block_to_RuntimeID.get(block.name, None)
    if block.name not in BlockState : return (block_id_data, 0)
    else :
        DataList = [key for key, value in BlockState[block.name].items() 
            if (key != "default" and value == block.states)]
        return (block_id_data, int(DataList[0], 2) if DataList else 0)

SpaceMatch = re.compile('[ ]{0,}')
KeyMatch   = re.compile('"(\\\\.|[^\\\\"]){0,}"')
EqualMatch = re.compile('=|:')
ValueMatch = re.compile('"(\\\\.|[^\\\\"]){0,}"|true|false|[0-9]+')
NextMatch  = re.compile(',')
def StringTransforBlockStates(s:str) :
    index = SpaceMatch.match(s).end()
    if s[index] != "[" : return {}
    else : index += 1

    StateSave = {}
    while index < len(s) :
        index = SpaceMatch.match(s, pos=index).end()
        KEY = KeyMatch.match(s, index)
        if KEY is None : break
        else : index = KEY.end()

        index = SpaceMatch.match(s, pos=index).end()
        EQUAL = EqualMatch.match(s, index)
        if EQUAL is None : break
        else : index = EQUAL.end()

        index = SpaceMatch.match(s, pos=index).end()
        VALUE = ValueMatch.match(s, index)
        if VALUE is None : break
        else : index = VALUE.end()
        
        StateSave[json.loads(KEY.group())] = json.loads(VALUE.group())

        index = SpaceMatch.match(s, pos=index).end()
        if s[index] == "," : index += 1
        else : break

    return StateSave


BlockNBT_ID = {"minecraft:chest": "Chest", "minecraft:trapped_chest": "Chest", 
"minecraft:lit_blast_furnace": "BlastFurnace", "minecraft:hopper": "Hopper", 
"minecraft:white_shulker_box": "ShulkerBox", "minecraft:undyed_shulker_box": "ShulkerBox", 
"minecraft:barrel": "Barrel", "minecraft:dispenser": "Dispenser", "minecraft:dropper": "Dropper", 
"minecraft:furnace": "Furnace", "minecraft:lit_furnace": "Furnace", "minecraft:smoker": "Smoker", 
"minecraft:lit_smoker": "Smoker", "minecraft:blast_furnace": "BlastFurnace", "minecraft:ender_chest":"Chest"}

def GetNbtID(id:str) :
    id = f"minecraft:{id}" if id.find("minecraft:") else id
    if id in BlockNBT_ID : return BlockNBT_ID[id]
    elif id.endswith("hanging_sign") : return "HangingSign"
    elif id.endswith("_sign") : return "Sign"



class BlockMeta(type) :

    def __init__(self, *args, **kwds) :
        super().__init__(*args, **kwds)
        self.__cache:Dict[Tuple[str, Union[int, str, frozenset]], "Block"] = {}

    def __call__(self, id:str, states:Union[int, str, Dict[str, Union[bool, int, str]]]):
        BlockID = id if id.startswith("minecraft:") else f"minecraft:{id}"

        CacheKey = (BlockID, frozenset(states.items())) if states.__class__ is dict else (BlockID, states)

        if CacheKey in self.__cache : return self.__cache[CacheKey]
        self.__cache[CacheKey] = super().__call__(BlockID, states)
        return self.__cache[CacheKey]

class Block(metaclass=BlockMeta) :
    """
    通用方块对象
    ---------------------------------
    * 实现了单例模式和哈希接口的方块对象
    ---------------------------------
    * 实例化参数 id : 方块ID字符串，如无命名空间则自动添加命名空间
    * 实例化参数 states : 方块状态传参，支持整数、方块状态字符串、方块状态字典
    * states 会自动舍去无效的状态参数
    ---------------------------------
    * 可用类方法 from_nbt: 将 {name:"a", states:{color:"red"}} 的方块nbt转换为方块对象
    * 可用方法 to_nbt: 生成 方块对象 对应的nbt对象
    """

    def __str__(self):
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


    def __init__(self, id:str, states:Union[int, str, Dict[str, Union[bool, int, str]]]) :
        saves = TransforBlock(id, states)

        self.name = saves[0]
        self.states = MappingProxyType(saves[1])
        self.dataValue = TransforDatavalue(self)
        self.__hash = (self.name, *self.states.keys(), *self.states.values()).__hash__()


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
        return node.compound(name=node.string(self.name), states=node.compound(**dict1)).build()


def GenerateCommandBlockNBT() -> nbt.TAG_Compound :
    node = nbt.NBT_Builder()
    return node.compound(
        id = node.string("CommandBlock"),
        Command = node.string(""),
        CustomName = node.string(""),
        ExecuteOnFirstTick = node.byte(1),
        auto = node.byte(0),
        TickDelay = node.int(0),
        conditionalMode = node.byte(0),
        TrackOutput = node.int(1),
        Version = node.int(19)
    ).build()

def GenerateContainerNBT(id:str) -> nbt.TAG_Compound :
    node = nbt.NBT_Builder()
    return node.compound(
        id = node.string(GetNbtID(id)),
        Items = node.list() 
    ).build()

