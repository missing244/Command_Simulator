from .. import nbt
from . import ModifyError, ValueError
from typing import Tuple,List,Union,Dict,Literal,Optional
import types, ctypes, json, re, traceback



SpaceMatch = re.compile('[ ]{0,}')
KeyMatch   = re.compile('"(\\\\.|[^\\\\"]){0,}"')
EqualMatch = re.compile('=|:')
ValueMatch = re.compile('"(\\\\.|[^\\\\"]){0,}"|true|false|[0-9]+')
NextMatch  = re.compile(',')
def BE_BlockStates_Parser(s:str) :
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

ContainerNBT_ID = {"minecraft:chest": "Chest", "minecraft:trapped_chest": "Chest", 
"minecraft:lit_blast_furnace": "BlastFurnace", "minecraft:hopper": "Hopper", 
"minecraft:white_shulker_box": "ShulkerBox", "minecraft:undyed_shulker_box": "ShulkerBox", 
"minecraft:barrel": "Barrel", "minecraft:dispenser": "Dispenser", "minecraft:dropper": "Dropper", 
"minecraft:furnace": "Furnace", "minecraft:lit_furnace": "Furnace", "minecraft:smoker": "Smoker", 
"minecraft:lit_smoker": "Smoker", "minecraft:blast_furnace": "BlastFurnace", "minecraft:ender_chest":"EnderChest"}

def GetNbtID(id:str) :
    id = f"minecraft:{id}" if ":" not in id else id
    if id in ContainerNBT_ID : return ContainerNBT_ID[id]
    elif id.endswith("command_block") : return "CommandBlock"
    elif id.endswith("hanging_sign") : return "HangingSign"
    elif id.endswith("_sign") : return "Sign"
    elif id.endswith("_shelf") : return "Shelf"




class BlockPermutationType :
    """
    ## 基岩版方块预设类
    * 属性**Identifier**        : 方块英文ID **(str)**
    * 属性**States**            : 方块状态 **(Dict[str, Union[str, bool, int]])**
    * 属性**Version**           : 方块数据格式版本 **(int)** 
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_nbt** : 通过NBT对象生成对象
    * 可用方法**to_nbt** : 通过对象生成NBT对象
    """

    def __str__(self) :
        return "<BlockPermutation Id='%s' States=%s>" % (self.Identifier, self.States)
    
    def __repr__(self) :
        return self.__str__()

    def __setattr__(self, name:str, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        else : raise ModifyError("不允许修改%s属性" % name)

    def __delattr__(self, name) :
        raise ModifyError("不允许删除%s属性" % name)
        
    def __hash__(self):
        return self.__hash

    def __eq__(self, value):
        return value.__hash__()  == self.__hash


    def __init__(self, id:str, state:Union[str, Dict[str, Union[str, bool, int]]]={}, version:int=17959425) :
        self.Identifier:str = f"minecraft:{id}" if ":" not in id else id
        self.States:Dict[str, Union[str, bool, int]] = types.MappingProxyType(
            state.copy() if isinstance(state, (dict, types.MappingProxyType)) else BE_BlockStates_Parser(state) )
        self.Version:int = version
        self.__hash = (self.Identifier, *self.States.items()).__hash__()


    @classmethod
    def from_nbt(cls, nbt_data:nbt.TAG_Compound) :
        if not isinstance(nbt_data, nbt.TAG_Compound) or not nbt_data.get("name", "") : return None
        Identifier = nbt_data["name"].value
        States = dict( nbt_data.get("states", dict()).value.items() )
        Version = nbt_data.get("version", ctypes.c_int32(17959425)).value
        
        for i,j in States.items() :
            if j.__class__ is nbt.TAG_Byte : States[i] = bool(j.value)
            elif j.__class__ is nbt.TAG_Int : States[i] = j.value
            elif j.__class__ is nbt.TAG_String : States[i] = j.value

        return cls(Identifier, States, Version)

    def to_nbt(self) -> nbt.TAG_Compound :
        node = nbt.NBT_Builder()
        dict1 = {}
        for i,j in self.States.items() :
            if j.__class__ is bool : dict1[i] = node.byte(j)
            elif j.__class__ is int : dict1[i] = node.int(j)
            elif j.__class__ is str : dict1[i] = node.string(j)

        return node.compound(name=node.string(self.Identifier), states=node.compound(**dict1), 
            version=node.int(self.Version)).build()

class BlockNbtType :
    """
    ## 基岩版方块实体数据类
    * 属性**Identifier**        : 方块实体对应的英文ID **(str)**
    * 属性**x**                 : 方块实体对应x坐标 **(int)**
    * 属性**y**                 : 方块实体对应y坐标 **(int)** 
    * 属性**z**                 : 方块实体对应z坐标 **(int)** 
    * 属性**CustomName**        : 方块实体自定义名字 **(str)** 
    * 属性**ExtraNBT**          : 额外的NBT数据 **(nbt.TAG_Compound)**  
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_nbt** : 通过NBT对象生成对象
    * 可用方法**to_nbt** : 通过对象生成NBT对象
    """

    def __str__(self) :
        return "<Block Id='%s' Pos=%s>" % (self.Identifier, [self.x, self.y, self.z])
    
    def __repr__(self) :
        return self.__str__()

    def __setattr__(self, name:str, value) :
        if name == "Identifier" and isinstance(value, str) : super().__setattr__(name, value)
        elif name == "x" and isinstance(value, int) : super().__setattr__(name, ctypes.c_int32(value).value)
        elif name == "y" and isinstance(value, int) : super().__setattr__(name, ctypes.c_int32(value).value)
        elif name == "z" and isinstance(value, int) : super().__setattr__(name, ctypes.c_int32(value).value)
        elif name == "CustomName" and isinstance(value, str) : super().__setattr__(name, value)
        elif not hasattr(self, name) : super().__setattr__(name, value)
        else : raise ModifyError("不允许修改%s属性" % name)

    def __delattr__(self, name) :
        raise ModifyError("不允许删除%s属性" % name)
        

    def __init__(self, id:str, pos:Tuple[int, int, int]=[0, 0, 0]) :
        from . import ItemType
        self.Identifier:str = id
        self.x:int = pos[0]
        self.y:int = pos[1]
        self.z:int = pos[2]
        self.CustomName:str = ""
        self.Items:Dict[int, ItemType] = {}
        self.ExtraNBT:nbt.TAG_Compound = nbt.TAG_Compound()


    @classmethod
    def from_nbt(cls, nbt_data:nbt.TAG_Compound) :
        from . import ItemType
        if "id" not in nbt_data : return None
        if "x" not in nbt_data : return None
        if "y" not in nbt_data : return None
        if "z" not in nbt_data : return None
        BlockEntityObject = cls(nbt_data["id"].value)
        BlockEntityObject.x = nbt_data["x"].value
        BlockEntityObject.y = nbt_data["y"].value
        BlockEntityObject.z = nbt_data["z"].value
        if "CustomName" in nbt_data : BlockEntityObject.CustomName = nbt_data["CustomName"].value

        for ContainerID in ["Items"] :
            Contanier = getattr(BlockEntityObject, ContainerID)
            for sub_item in nbt_data.get(ContainerID, []) :
                if not("Name" in sub_item and "Slot" in sub_item) : continue
                try : int(sub_item["Slot"].value)
                except : continue
                SubItemObject = ItemType.from_nbt(sub_item)
                if SubItemObject : Contanier[int(sub_item["Slot"].value)] = SubItemObject
        
        ExceptKey = {"Items", "id", "x", "y", "z", "CustomName"}
        for key, value in nbt_data.items() :
            if key in ExceptKey : continue
            BlockEntityObject.ExtraNBT[key] = value.copy()

        return BlockEntityObject
    
    def to_nbt(self):
        NbtObject = nbt.TAG_Compound()

        NbtObject["id"] = nbt.TAG_String(self.Identifier)
        NbtObject["x"] = nbt.TAG_Int(self.x)
        NbtObject["y"] = nbt.TAG_Int(self.y)
        NbtObject["z"] = nbt.TAG_Int(self.z)
        NbtObject["CustomName"] = nbt.TAG_String(self.CustomName)

        for ContainerID in ["Items"] :
            Contanier = getattr(self, ContainerID)
            if not Contanier : continue
            NbtObject[ContainerID] = nbt.TAG_List([], type=nbt.TAG_Compound )
            for slot, item in Contanier.items() :
                ItemNbt = item.to_nbt()
                ItemNbt["Slot"] = nbt.TAG_Byte( ctypes.c_int8(slot).value )
                NbtObject[ContainerID].append( ItemNbt )

        for key, value in self.ExtraNBT.items() :
            NbtObject[key] = value.copy()

        return NbtObject



