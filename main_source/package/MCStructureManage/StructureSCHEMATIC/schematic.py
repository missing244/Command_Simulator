import os,array,ctypes
from .. import nbt,TypeCheckList
from typing import Union,List,TypedDict,Dict
from io import FileIO, BytesIO

RuntimeID_to_Block = ["air", "stone", "grass", "dirt", "cobblestone", "planks", "sapling",
    "bedrock", "flowing_water", "water", "flowing_lava", "lava", "sand", "gravel", "gold_ore",
	"iron_ore", "coal_ore", "log", "leaves", "sponge", "glass", "lapis_ore", "lapis_block", 
    "dispenser", "sandstone", "noteblock", "bed", "golden_rail", "detector_rail", "sticky_piston",
	"cobweb", "tallgrass", "deadbush", "piston", "piston_head", "wool", "piston_extension",
	"dandelion", "poppy", "brown_mushroom", "red_mushroom", "gold_block", "iron_block", "double_stone_slab",
	"stone_slab", "brick_block", "tnt", "bookshelf", "mossy_cobblestone", "obsidian", "torch",
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
Block_to_RuntimeID = {id:index for index, id in enumerate(RuntimeID_to_Block)}



class Schematic :
    """
    schematic 结构文件对象
    -----------------------
    * 管理 .schematic 为后缀的大端gzip压缩的nbt文件
    * 方块按照 yzx 顺序进行储存（x坐标变化最频繁）
    * 此对象并不能完整保留所有储存的数据
    * 此对象只支持0-255数字id的方块，非该id范围的方块都将忽略
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构保存时的位置
    * 可用属性 offset : 结构保存时的位置的偏移量
    * 可用属性 block_index : 方块索引列表（数量与结构体积相同）
    * 可用属性 block_data : 方块索引列表（数量与结构体积相同）
    * 可用属性 entity_nbt : 实体对象列表
    * 可用属性 block_nbt : 以nbt对象组成的列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """
    

    def __init__(self) :
        self.size: array.array = array.array("i", [0, 0, 0])
        self.origin: array.array = array.array("i", [0, 0, 0])
        self.offset: array.array = array.array("i", [0, 0, 0])
        self.block_index: array.array = array.array("B")
        self.block_data: array.array = array.array("b")
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)
        self.block_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        Volume = self.size[0] * self.size[1] * self.size[2]
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")
        if len(self.origin) != 3 : raise Exception("结构保存位置列表长度不为3")
        if len(self.block_index) != Volume : raise Exception("方块索引列表长度与结构体积不相等")


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO]) :
        NBT = nbt.read_from_nbt_file(buffer, byteorder="big", zip_mode="gzip").get_tag()

        StructureObject = cls()
        StructureObject.size[0] = NBT["Width"].value
        StructureObject.size[1] = NBT["Height"].value
        StructureObject.size[2] = NBT["Length"].value
        StructureObject.origin[0] = NBT.get("WEOriginX", 0)
        StructureObject.origin[1] = NBT.get("WEOriginY", 0)
        StructureObject.origin[2] = NBT.get("WEOriginZ", 0)
        StructureObject.offset[0] = NBT.get("WEOffsetX", 0)
        StructureObject.offset[1] = NBT.get("WEOffsetY", 0)
        StructureObject.offset[2] = NBT.get("WEOffsetZ", 0)
        StructureObject.block_index = array.array("B", NBT['Blocks'].value.tobytes())
        StructureObject.block_data = array.array("B", NBT['Data'].value.tobytes())
        StructureObject.entity_nbt = TypeCheckList(NBT['Entities']).setChecker(nbt.TAG_Compound)
        StructureObject.block_nbt = TypeCheckList(NBT['TileEntities']).setChecker(nbt.TAG_Compound)

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, BytesIO]) :
        self.error_check()

        node = nbt.NBT_Builder()
        NBT = node.compound(
            Width = node.short(self.size[0]),
            Height = node.short(self.size[1]),
            Length = node.short(self.size[2]),
            WEOriginX = node.int(self.origin[0]),
            WEOriginY = node.int(self.origin[1]),
            WEOriginZ = node.int(self.origin[2]),
            WEOffsetX = node.int(self.offset[0]),
            WEOffsetY = node.int(self.offset[1]),
            WEOffsetZ = node.int(self.offset[2]),
            Materials = node.string("Alpha")
        ).build()
        NBT['Blocks'] = nbt.TAG_ByteArray(array.array("b", self.block_index.tobytes()))
        NBT['Data'] = nbt.TAG_ByteArray(array.array("b", self.block_data.tobytes()))
        NBT['Entities'] = nbt.TAG_List(self.entity_nbt, type=nbt.TAG_Compound)
        NBT['TileEntities'] = nbt.TAG_List(self.block_nbt, type=nbt.TAG_Compound)

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "wb")
        else : _file = buffer
        nbt.write_to_nbt_file(_file, NBT, zip_mode="gzip" ,byteorder="big")



