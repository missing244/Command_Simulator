from typing import Union,Dict,Tuple
from types import MappingProxyType
import re, os, json


CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
BlockState = json.load(fp=open(os.path.join(CurrentPath, "res", "blockstate.json"), "r", encoding="utf-8"))
OldBlockData = json.load(fp=open(os.path.join(CurrentPath, "res", "flatten.json"), "r", encoding="utf-8"))
RunAwayDataValue = json.load(fp=open(os.path.join(CurrentPath, "res", "RA_Datavalue.json"), "r", encoding="utf-8"))
JEtransfor = json.load(fp=open(os.path.join(CurrentPath, "res", "JEtransfor.json"), "r", encoding="utf-8"))
RuntimeID_to_Block = ["air", "stone", "grass", "dirt", "cobblestone", "planks", "sapling",
    "bedrock", "flowing_water", "water", "flowing_lava", "lava", "sand", "gravel", "gold_ore",
	"iron_ore", "coal_ore", "log", "leaves", "sponge", "glass", "lapis_ore", "lapis_block", 
    "dispenser", "sandstone", "noteblock", "bed", "golden_rail", "detector_rail", "sticky_piston",
	"web", "tallgrass", "deadbush", "piston", "piston_arm_collision", "wool", "air",
	"dandelion", "poppy", "brown_mushroom", "red_mushroom", "gold_block", "iron_block", "stone_double_slab",
	"smooth_stone_slab", "brick_block", "tnt", "bookshelf", "mossy_cobblestone", "obsidian", "torch",
	"fire", "monster_spawner", "oak_stairs", "chest", "redstone_wire", "diamond_ore", "diamond_block",
	"crafting_table", "wheat", "farmland", "furnace", "lit_furnace", "standing_sign", "wooden_door",
	"ladder","rail", "stone_stairs", "wall_sign", "lever", "stone_pressure_plate", "iron_door",
	"wooden_pressure_plate", "redstone_ore",  "lit_redstone_ore", "unlit_redstone_torch", "redstone_torch",
	"stone_button", "snow_layer", "ice", "snow", "cactus", "clay", "reeds", "jukebox", "fence",
	"pumpkin", "netherrack", "soul_sand", "glowstone", "portal", "lit_pumpkin", "cake", "unpowered_repeater",
	"powered_repeater", "stained_glass", "trapdoor", "monster_egg", "stonebrick", "brown_mushroom_block",
	"red_mushroom_block", "iron_bars", "glass_pane", "melon_block", "pumpkin_stem", "melon_stem",
	"vine", "fence_gate", "brick_stairs", "stone_brick_stairs", "mycelium", "waterlily", "nether_brick",
	"nether_brick_fence", "nether_brick_stairs", "nether_wart", "enchanting_table", "brewing_stand",
	"cauldron", "end_portal","end_portal_frame", "end_stone", "dragon_egg", "redstone_lamp",
	"lit_redstone_lamp", "double_wooden_slab", "wooden_slab", "cocoa", "sandstone_stairs", "emerald_ore", 
    "ender_chest", "tripwire_hook", "tripwire", "emerald_block", "spruce_stairs", "birch_stairs",
	"jungle_stairs", "command_block", "beacon", "cobblestone_wall", "flower_pot", "carrots", "potatoes", 
    "wooden_button", "skull", "anvil", "trapped_chest", "light_weighted_pressure_plate", 
    "heavy_weighted_pressure_plate", "unpowered_comparator", "powered_comparator", "daylight_detector",
	"redstone_block", "quartz_ore", "hopper", "quartz_block", "quartz_stairs", "activator_rail",
	"dropper", "stained_hardened_clay", "stained_glass_pane", "leaves2", "log2", "acacia_stairs",
	"dark_oak_stairs", "slime", "barrier", "iron_trapdoor", "prismarine", "sealantern", "hay_block",
	"carpet", "hardened_clay", "coal_block", "packed_ice", "double_plant", "standing_banner",
	"wall_banner", "daylight_detector_inverted", "red_sandstone", "red_sandstone_stairs", "double_stone_slab2",
	"stone_slab2", "spruce_fence_gate", "birch_fence_gate", "jungle_fence_gate", "dark_oak_fence_gate",
	"acacia_fence_gate", "spruce_fence", "birch_fence", "jungle_fence", "dark_oak_fence", "acacia_fence_gate",
	"spruce_door", "birch_door", "jungle_door", "acacia_door", "dark_oak_door", "end_rod", "chorus_plant",
	"chorus_flower", "purpur_block", "purpur_pillar", "purpur_stairs", "purpur_double_slab", "purpur_slab",
	"end_bricks", "beetroots", "grass_path", "end_gateway", "repeating_command_block", "chain_command_block",
	"frosted_ice", "magma", "nether_wart_block", "red_nether_brick", "bone_block", "structure_void",
	"observer", "white_shulker_box", "orange_shulker_box", "magenta_shulker_box", "light_blue_shulker_box",
	"yellow_shulker_box", "lime_shulker_box", "pink_shulker_box", "gray_shulker_box", "light_gray_shulker_box",
	"cyan_shulker_box", "purple_shulker_box", "blue_shulker_box", "brown_shulker_box", "green_shulker_box",
	"red_shulker_box", "black_shulker_box", "white_glazed_terracotta", "orange_glazed_terracotta",
	"magenta_glazed_terracotta", "light_blue_glazed_terracotta", "yellow_glazed_terracotta", 
    "lime_glazed_terracotta", "pink_glazed_terracotta", "gray_glazed_terracotta", "light_gray_glazed_terracotta",
	"cyan_glazed_terracotta", "purple_glazed_terracotta", "blue_glazed_terracotta", "brown_glazed_terracotta",
	"green_glazed_terracotta", "red_glazed_terracotta", "black_glazed_terracotta", "concrete", "concrete_powder",
	"air", "air", "structure_block"]
for index, id in enumerate(RuntimeID_to_Block) : RuntimeID_to_Block[index] = f"minecraft:{id}"
SCHEMATIC_Block_to_RuntimeID = {id:index for index, id in enumerate(RuntimeID_to_Block) if id != "minecraft:air"}
SCHEMATIC_Block_to_RuntimeID["minecraft:air"] = 0

SpecialStates = {"direction":{"south":0, "west":1, "north":2, "east":3}, 
    "facing_direction":{"south":0, "west":1, "north":2, "east":5},
    "top_slot_bit":{"top":True, "bottom":False}}
def TransforBlock(id:str, value:Union[int, str, dict]={}) -> Tuple[str, Dict[str, Union[bool, int, str]]] :
    if id.endswith("seaLantern") : id = "sea_lantern"
    BlockID = f"minecraft:{id}" if ":" not in id else id
    BlockID = OldBlockData["block_id"].get(BlockID, BlockID)

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
    elif value.__class__ is MappingProxyType : value = dict(value)
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

def TransforDatavalue(id:str, states:Dict[str, Union[bool, int, str]]) -> Tuple[int, int] :
    block_id_data = SCHEMATIC_Block_to_RuntimeID.get(id, 0)
    if id not in BlockState : return (block_id_data, 0)
    else :
        DataList = [key for key, value in BlockState[id].items() 
            if (key != "default" and value == states)]
        return (block_id_data, int(DataList[0], 2) if DataList else 0)

def RunawayTransforBlock(id:str) -> Tuple[str, Dict[str, Union[bool, int, str]]] :
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

def BlockTransforRunaway(id:str, states:Dict[str, Union[bool, int, str]]) -> str :
    str1 = id.replace("minecraft:", "", 1)
    if id not in BlockState : return str1
    if "runaway_blockstate_key" not in BlockState[id] : return str1
        
    for key in BlockState[id]["runaway_blockstate_key"] :
        state, state2 = states[key].split("_")[0], states[key].split("_")[1:]
        for i in state2 : state = f"{state}{i[0].upper()}{i[1:]}"
        str1 = f"{str1}.{state}"

    return str1

def RunawayDataValueTransforBlock(id:str, dataValue:int) :
    id = f"minecraft:{id}" if ":" not in id else id
    Binary_Key = bin(dataValue)

    BlockID = id
    Block_State = {}

    RegExpDict = {i:re.compile(i) for i in RunAwayDataValue["RegExp"].keys()}
    ReTestSuccessKey = None
    for reKey, reObj in RegExpDict.items() :
        if not reObj.search(BlockID) : continue
        ReTestSuccessKey = reKey
        break

    if ReTestSuccessKey and Binary_Key in RunAwayDataValue["RegExp"][ReTestSuccessKey] :
        Block_State.update( RunAwayDataValue["RegExp"][ReTestSuccessKey][Binary_Key] )
        #print(1)
    elif BlockID in RunAwayDataValue["Custom"] and Binary_Key in RunAwayDataValue["Custom"][BlockID] :
        Block_State.update( RunAwayDataValue["Custom"][BlockID][Binary_Key] )
        #print(2)
    elif BlockID in BlockState : 
        Block_State.update( BlockState[BlockID].get(Binary_Key, {}) )
        #print(3)
    else : pass #print(4)

    return (BlockID, Block_State)



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
def JE_Transfor_BE_Block(id:str) -> Tuple[str, dict, bool]: 
    start1 = id.find("[") if id.find("[") >= 0 else len(id)
    JE_ID, JE_State = id[:start1], JE_BlockStates_Parser(id[start1:])
    JE_waterlog = True if JE_State.get("waterlogged", False) else False

    #处理方块ID差异
    BE_ID = JEtransfor["Identifier"][JE_ID]["name"] if JE_ID in JEtransfor["Identifier"] else JE_ID
    if IdentifierAndStateSeacher["_slab$"].search(JE_ID) and JE_State.get("type", None) == "double" : 
        if BE_ID.endswith("cut_copper_slab") : BE_ID = BE_ID.replace("cut_copper_slab", "double_cut_copper_slab", 1)
        elif BE_ID[-1] not in "0123456789" : BE_ID = BE_ID[:-5] + "_double_slab"
        else : BE_ID = BE_ID[:-6] + "_double_slab"

    BE_ID, BE_State = TransforBlock(BE_ID)
    if JE_ID.endswith("big_dripleaf_stem") : BE_State["big_dripleaf_head"] = False

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

    return (BE_ID, BE_State, JE_waterlog)

