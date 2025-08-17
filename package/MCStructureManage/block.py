from . import nbt, StructureSCHEMATIC

from typing import Union,Dict,Tuple
from types import MappingProxyType
import re, os, json


CommandBlockIDTest = re.compile("command_block$")
CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
BlockState = json.load(fp=open(os.path.join(CurrentPath, "res", "blockstate.json"), "r", encoding="utf-8"))
OldBlockData = json.load(fp=open(os.path.join(CurrentPath, "res", "flatten.json"), "r", encoding="utf-8"))
JEtransfor = json.load(fp=open(os.path.join(CurrentPath, "res", "JEtransfor.json"), "r", encoding="utf-8"))

SpecialStates = {"direction":{"south":0, "west":1, "north":2, "east":3}, 
    "facing_direction":{"south":0, "west":1, "north":2, "east":5},
    "top_slot_bit":{"top":True, "bottom":False}}
def TransforBlock(id:str, value:Union[int, str, dict]={}) -> Tuple[str, Dict[str, Union[bool, int, str]]]:
    if id.endswith("seaLantern") : id = "sea_lantern"
    BlockID = f"minecraft:{id}" if ":" not in id else id

    if BlockID in BlockState and value.__class__ is int :
        NewBlockID = BlockID
        NewBlockState = BlockState[BlockID].get(bin(value), BlockState[BlockID]["default"])
        return (NewBlockID, dict( sorted(NewBlockState.items()) ))
    elif BlockID in OldBlockData["block"] : 
        NewBlockID = OldBlockData["block"][BlockID]["block_id"]
        NewBlockState = OldBlockData["block"][BlockID]["block_data"]
    elif BlockID in BlockState :
        NewBlockID = BlockID
        NewBlockState = BlockState[BlockID]["default"]
    else : return (BlockID, {})

    NewBlockState = dict( sorted(NewBlockState.items()) )
    if value.__class__ is str : value = BE_BlockStates_Parser(value)
    elif value.__class__ is dict : value = value.copy()
    elif value.__class__ is MappingProxyType : value = value
    else : value = {}

    cardinal_direction = value.get("minecraft:cardinal_direction", None)
    if cardinal_direction in SpecialStates["direction"] :
        if "facing_direction" in NewBlockState : 
            value["facing_direction"] = SpecialStates["facing_direction"][cardinal_direction]
        elif "direction" in NewBlockState : 
            value["direction"] = SpecialStates["direction"][cardinal_direction]
        del value["minecraft:cardinal_direction"]
    
    vertical_half = value.get("minecraft:vertical_half", None)
    if vertical_half in SpecialStates["top_slot_bit"] :
        if "top_slot_bit" in NewBlockState : 
            value["top_slot_bit"] = SpecialStates["top_slot_bit"][vertical_half]
        del value["minecraft:vertical_half"]
    #print(1, NewBlockID, NewBlockState, value)

    NewBlockState.update( (i,j) for i,j in value.items() if (i in NewBlockState)
        and (j in BlockState[NewBlockID]["support_value"][i]) )
    return (NewBlockID, NewBlockState)

def TransforDatavalue(block:"Block") -> Tuple[int, int] :
    block_id_data = StructureSCHEMATIC.Block_to_RuntimeID.get(block.name, 0)
    if block.name not in BlockState : return (block_id_data, 0)
    else :
        DataList = [key for key, value in BlockState[block.name].items() 
            if (key != "default" and value == block.states)]
        return (block_id_data, int(DataList[0], 2) if DataList else 0)

def TransforRunawayBlock(id:Union[str, "Block"]) :
    if id.__class__ is str :
        str1 = id.split(".")
        block_id, block_state = str1[0], str1[1:]
        block_id = f"minecraft:{block_id}" if ":" not in block_id else block_id
        if not block_state or block_id not in BlockState : return (block_id, {})
        if "runaway_blockstate_key" not in BlockState[block_id] : return (block_id, {})

        States, UpperTest = {}, re.compile("[A-Z]")
        support_value = BlockState[block_id]["support_value"]
        for key in BlockState[block_id]["runaway_blockstate_key"] :
            for state in block_state :
                test_result = UpperTest.search(state)
                if test_result : 
                    start, end = test_result.start(), test_result.end()
                    state = f"{state[0:start]}_{state[start].lower()}{state[end:]}"
                if state not in support_value[key] : continue
                States[key] = state
                break
        
        return (block_id, States)
    else :
        str1 = id.name.replace("minecraft:", "", 1)
        if id.name not in BlockState : return str1
        if "runaway_blockstate_key" not in BlockState[id.name] : return str1
        
        for key in BlockState[id.name]["runaway_blockstate_key"] :
            state, state2 = id.states[key].split("_")[0], id.states[key].split("_")[1:]
            for i in state2 : state = f"{state}{i[0].upper()}{i[1:]}"
            str1 = f"{str1}.{state}"

        return str1

SpaceMatch = re.compile('[ ]{0,}')
KeyMatch   = re.compile('"(\\\\.|[^\\\\"]){0,}"')
EqualMatch = re.compile('=|:')
ValueMatch = re.compile('"(\\\\.|[^\\\\"]){0,}"|true|false|[0-9]+')
NextMatch  = re.compile(',')
def BE_BlockStates_Parser(s:str) :
    index = SpaceMatch.match(s).end()
    if index >= len(s) or s[index] != "[" : return {}
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

KeyMatch_1   = re.compile('[a-zA-Z0-9]+')
EqualMatch_1 = re.compile('=')
ValueMatch_1 = re.compile('[a-zA-Z0-9]+')
def JE_BlockStates_Parser(s:str) :
    index = SpaceMatch.match(s).end()
    if index >= len(s) or s[index] != "[" : return {}
    else : index += 1

    StateSave = {}
    while index < len(s) :
        index = SpaceMatch.match(s, pos=index).end()
        KEY = KeyMatch_1.match(s, index)
        if KEY is None : break
        else : index = KEY.end()

        index = SpaceMatch.match(s, pos=index).end()
        EQUAL = EqualMatch_1.match(s, index)
        if EQUAL is None : break
        else : index = EQUAL.end()

        index = SpaceMatch.match(s, pos=index).end()
        VALUE = ValueMatch_1.match(s, index)
        if VALUE is None : break
        else : index = VALUE.end()
        
        try : StateSave[KEY.group()] = json.loads(VALUE.group())
        except : StateSave[KEY.group()] = VALUE.group()

        index = SpaceMatch.match(s, pos=index).end()
        if s[index] == "," : index += 1
        else : break

    return StateSave

IdentifierAndStateSeacher = {i:re.compile(i) for i in JEtransfor["IdentifierAndState"].keys()}
def JE_Transfor_BE_Block(id:str) -> "Block": 
    start1 = id.find("[") if id.find("[") >= 0 else len(id)
    JE_ID, JE_State = id[:start1], JE_BlockStates_Parser(id[start1:])

    #处理方块ID差异
    BE_ID = JEtransfor["Identifier"][JE_ID]["name"] if JE_ID in JEtransfor["Identifier"] else JE_ID
    if IdentifierAndStateSeacher["_slab$"].search(JE_ID) and JE_State.get("type", None) == "double" : 
        if BE_ID[-1] not in "0123456789" : BE_ID = BE_ID[:-5] + "_double_slab"
        else : BE_ID = BE_ID[:-6] + "_double_slab"
    BE_ID, BE_State = TransforBlock(BE_ID)

    #特殊方块对应方块状态处理
    Marcher1 = None
    for re1, re2 in IdentifierAndStateSeacher.items() :
        if not re2.search(JE_ID) : continue
        Marcher1 = re1
        break
    for je_state, be_state_data in JEtransfor["IdentifierAndState"].get(Marcher1, {}).items() :
        if je_state not in JE_State : continue
        if str(JE_State[je_state]) not in be_state_data : continue
        if be_state_data["BEstate"] not in BE_State : continue

        if Marcher1 == "_slab$" and str(JE_State[je_state]) == "double" : pass
        else : BE_State[be_state_data["BEstate"]] = be_state_data[str(JE_State[je_state])]
        del JE_State[je_state]
    
    #普通方块状态处理
    for je_state, je_state_value in JE_State.items() :
        if je_state not in JEtransfor["State"] : continue
        transfor_key, transfor_value = None, None
        for transfor_key_1, transfor_value_1 in JEtransfor["State"][je_state].items() :
            #print(JE_State, BE_State, transfor_key_1, transfor_value_1)
            if transfor_key_1 not in BE_State : continue
            transfor_key, transfor_value = transfor_key_1, transfor_value_1
            break
        if not transfor_key : continue
        if transfor_value is None : BE_State[transfor_key] = je_state_value
        elif str(je_state_value) in transfor_value : BE_State[transfor_key] = transfor_value[str(je_state_value)]

    #特殊方块状态处理
    if BE_ID in JEtransfor["Special"] :
        transfor_info = JEtransfor["Special"][BE_ID]
        default_var = 0
        for je_state_key, je_state_value in JE_State.items() :
            #print(je_state_key, je_state_value)
            if je_state_key not in transfor_info : continue
            if transfor_info["Operation"] == "OR" : default_var |= (transfor_info[je_state_key] if je_state_value else 0)
        BE_State[transfor_info["BEstate"]] = default_var

    return Block(BE_ID, BE_State)


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



class BlockMeta(type) :

    def __init__(self, *args, **kwds) :
        super().__init__(*args, **kwds)
        self.__cache:Dict[Tuple[str, Union[int, str, tuple]], "Block"] = {}

    def __call__(self, id:str, states:Union[int, str, Dict[str, Union[bool, int, str]]]={}) :
        CacheKey = (id, *states.items()) if hasattr(states, "items") else (id, states)

        if CacheKey in self.__cache : return self.__cache[CacheKey]
        self.__cache[CacheKey] = super().__call__(id, states)
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
    * 属性 dataValue : 方块id和方块状态对应的数据值，无法互相转换的数据值会设置为0
    ---------------------------------
    * 可用类方法 from_nbt: 将 {name:"a", states:{color:"red"}} 的方块nbt转换为方块对象
    * 可用方法 to_nbt: 生成 方块对象 对应的nbt对象
    """

    def __str__(self):
        return f'<Block name="{self.name}" states={self.states}>'
    
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


    def __init__(self, id:str, states:Union[int, str, Dict[str, Union[bool, int, str]]]) :
        if "." in id : BlockID, BlockState = TransforRunawayBlock(id)
        else : BlockID, BlockState = TransforBlock(id, states)
        self.name = BlockID
        self.states = MappingProxyType(BlockState)
        self.dataValue = TransforDatavalue(self)
        self.runawayID = TransforRunawayBlock(self)
        self.blockString = "%s[%s]" % (BlockID, json.dumps(BlockState, separators=(',', '='))[1:][:-1])
        
        self.__hash = (self.name, *self.states.items()).__hash__()


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



def GenerateCommandBlockNBT(id:str) -> nbt.TAG_Compound :
    if not id.endswith("command_block") : return None
    node = nbt.NBT_Builder()
    return node.compound(
        id = node.string("CommandBlock"),
        Command = node.string(""),
        CustomName = node.string(""),
        ExecuteOnFirstTick = node.byte(1),
        auto = node.byte(0),
        TickDelay = node.int(0),
        conditionalMode = node.byte(0),
        TrackOutput = node.byte(1),
        Version = node.int(19)
    ).build()

def GenerateContainerNBT(id:str) -> Union[None, nbt.TAG_Compound] :
    id = f"minecraft:{id}" if ":" not in id else id
    id = ContainerNBT_ID.get(id, None)
    if not id : return None
    node = nbt.NBT_Builder()
    return node.compound(
        Findable = node.byte(0),
        IsOpened = node.byte(0),
        isMovable = node.byte(1),
        id = node.string(id),
        Items = node.list() 
    ).build()

def GenerateSignNBT(id:str) -> nbt.TAG_Compound : 
    block_nbt_id = GetNbtID(id)
    if block_nbt_id != "HangingSign" and block_nbt_id != "Sign" : return None
    node = nbt.NBT_Builder()
    return node.compound(
        IsWaxed = node.byte(0),
        isMovable = node.byte(1),
        id = node.string(block_nbt_id),
        BackText = node.compound(
            FilteredText = node.string(""),
            HideGlowOutline = node.byte(0),
            IgnoreLighting = node.byte(0),
            PersistFormatting = node.byte(1),
            SignTextColor = node.int(-16777216),
            Text = node.string(""),
            TextOwner = node.string("") ),
        FrontText = node.compound(
            FilteredText = node.string(""),
            HideGlowOutline = node.byte(0),
            IgnoreLighting = node.byte(0),
            PersistFormatting = node.byte(1),
            SignTextColor = node.int(-16777216),
            Text = node.string(""),
            TextOwner = node.string("") )
    ).build()