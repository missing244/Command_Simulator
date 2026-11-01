from typing import List, Dict, Union, Literal, Tuple, TypedDict, Iterable
from typing import Set, Sequence, Optional, Generic, TypeVar, Callable
from . import nbt, MinecraftSimulator
from .block import BlockPermutation, Block, BlockComponent
from .sundries_type import iter_pos
from .. import Constants, python_numpy as np
import random, zlib, io, os, struct, math, array, itertools, traceback, sqlite3

T = TypeVar('T')
Chunk_DB_Create = """
    CREATE TABLE IF NOT EXISTS chunks (
        x INT NOT NULL,
        z INT NOT NULL,
        version TINYINT NOT NULL DEFAULT 1,   -- 区块数据格式版本，默认 1
        block_index BLOB NOT NULL,       -- array("H") 直接转字节，固定 768 字节
        block_entities BLOB NOT NULL,    -- Dict[int, Block] 序列化为二进制
        entities BLOB NOT NULL,          -- int64 数组的原始字节
        PRIMARY KEY (x, z)
    );
"""
Chunk_DB_Read =  "SELECT block_index, block_entities, entities FROM chunks WHERE x=? AND z=?"
Chunk_DB_Write = "REPLACE INTO chunks (x, z, block_index, block_entities, entities) VALUES (?, ?, ?, ?, ?)"
Chunk_DB_Exists = "SELECT 1 FROM chunks WHERE x=? AND z=?"
Chunk_DB_Read_Entity  = "SELECT entities FROM chunks WHERE x=? AND z=?"
Chunk_DB_Write_Entity = "UPDATE chunks SET entities=? WHERE x=? AND z=?"

DefaultBlockPalette = [
    {"Identifier":"minecraft:air","BlockState":{}},
    {"Identifier":"minecraft:grass","BlockState":{}},
    {"Identifier":"minecraft:stone","BlockState":{"stone_type": "stone"}},
    {"Identifier":"minecraft:dirt","BlockState":{"dirt_type": "normal"}},
    {"Identifier":"minecraft:netherrack","BlockState":{}},
    {"Identifier":"minecraft:end_stone","BlockState":{}},
    {"Identifier":"minecraft:bedrock","BlockState":{"infiniburn_bit":False}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 0,"conditional_bit": False}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 1,"conditional_bit": False}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 2,"conditional_bit": False}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 3,"conditional_bit": False}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 4,"conditional_bit": False}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 5,"conditional_bit": False}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 0,"conditional_bit": True}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 1,"conditional_bit": True}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 2,"conditional_bit": True}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 3,"conditional_bit": True}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 4,"conditional_bit": True}},
    {"Identifier":"minecraft:command_block","BlockState": {"facing_direction": 5,"conditional_bit": True}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 0,"conditional_bit": False}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 1,"conditional_bit": False}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 2,"conditional_bit": False}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 3,"conditional_bit": False}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 4,"conditional_bit": False}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 5,"conditional_bit": False}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 0,"conditional_bit": True}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 1,"conditional_bit": True}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 2,"conditional_bit": True}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 3,"conditional_bit": True}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 4,"conditional_bit": True}},
    {"Identifier":"minecraft:chain_command_block","BlockState": {"facing_direction": 5,"conditional_bit": True}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 0,"conditional_bit": False}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 1,"conditional_bit": False}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 2,"conditional_bit": False}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 3,"conditional_bit": False}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 4,"conditional_bit": False}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 5,"conditional_bit": False}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 0,"conditional_bit": True}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 1,"conditional_bit": True}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 2,"conditional_bit": True}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 3,"conditional_bit": True}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 4,"conditional_bit": True}},
    {"Identifier":"minecraft:repeating_command_block","BlockState": {"facing_direction": 5,"conditional_bit": True}},
    {"Identifier":"minecraft:redstone_block","BlockState": {}} ]
InfinityWorldArray = b'x\x9c\xed\xda\xbb\t\x80P\x00\x04A?\xf0\xfa/\xd9\xd4H\x05AW\x9c\xb9\xf0Z\xd81\x8d\xc3-?\xdfzs\xf3\xc9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x8a\xe3\xfa_\xff\xaf\xff\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0@\xff\xaf\xff\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0O\xff\xaf\xff\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0O\xff\xaf\xff\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xef\xb9\xfe\x7f\xef\x8d_\xff\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0w\xe9\xff\xf5\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\xe9\xff\xf5\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\xe9\xff\xf5\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\xe9\xff\xf5\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\xe9\xff\xf5\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4=\xd7\xff\x7fs\xfa\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xf4\xff\xfa\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\xf4\xff\xfa\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\xf4\xff\xfa\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\xf4\xff\xfa\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa6\x19\x80\x1b\xe1'
FlatWorldArray = b'x\x9c\xed\xda1\r\x00 \x00\xc00\x08\t\xfe%\xe3\x00\x0e\x9e\x1d\xedll\x8f}m}6\x1f\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00o\xf7\xfb\xdf\xff\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\xfe\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8\xf3\xff\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x9f\xff\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\xe7\xff\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80>\xff?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\xf9\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xcf\xff\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00}\xfe\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8\xf3\xff\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x9f\xff\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\xe7\xff\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80>\xff?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf4\x1d\xf3\xd7\r\x01'
NetherArray = b"x\x9c\xed\xd7\xb1\r\xc0 \x00\xc00\x06\xc4\xff'\xf7\x03\x18\x11\xa9\x9d+\xb2\xc6\xda6\x7f\x1e\x00\x00\x00\xbc`\x7f\xf7\xe7n\xff\xf7\xed\x00\x00\x00\xe0\x05\xfe\xdf\xff\x03\x00\x00\xd0\xe7\xff\xfd?\x00\x00\x00}\xfe\xdf\xff\x03\x00\x00\xd0\xe7\xff\xfd?\x00\x00\x00}\xfe\xdf\xff\x03\x00\x00\xd0\xe7\xff\xfd?\x00\x00\x00}\xfe\xdf\xff\x03\x00\x00\xd0\xe7\xff\xfd?\x00\x00\x00}\xfe\xdf\xff\x03\x00\x00\xd0\xe7\xff\xfd?\x00\x00\x00}\xfe\xdf\xff\x03\x00\x00\xd0\xe7\xff\xfd?\x00\x00\x00}\xfe\xdf\xff\x03\x00\x00\xd0\xe7\xff\xfd?\x00\x00\x00}\xa7\xbf\xff\x00\x83\xf2,\x01"
TheEndArray = b'x\x9c\xed\xd91\x11\xc00\x00\xc4\xb0,\xe5O\xb9\x0c\xba\xfa\xfa\x91\x0c\xc3\xe7|{.\x0f\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\x16\xd4\xff\xbd\x0e\x00\x00\x00\x00\x00\x00\x00\xfe\xe0\x05\xa4E(\x01'
CommandBlockID = {"minecraft:command_block", "minecraft:repeating_command_block", "minecraft:chain_command_block"}
NO_COLLISION_BLOCKS = frozenset({
    # 空气
    "minecraft:air",
    # 液体 / 气泡柱（不阻挡移动）
    "minecraft:water", "minecraft:flowing_water", "minecraft:lava", "minecraft:flowing_lava",
    "minecraft:bubble_column",
    # 草 / 蕨 / 枯木 / 大型植物
    "minecraft:short_grass", "minecraft:grass", "minecraft:tall_grass", "minecraft:fern",
    "minecraft:large_fern", "minecraft:double_plant", "minecraft:deadbush",
    "minecraft:sweet_berry_bush", "minecraft:reeds", "minecraft:sugar_cane",
    "minecraft:kelp", "minecraft:seagrass",
    # 作物
    "minecraft:wheat", "minecraft:carrots", "minecraft:potatoes", "minecraft:beetroot",
    "minecraft:melon_stem", "minecraft:pumpkin_stem",
    "minecraft:torchflower_crop", "minecraft:pitcher_crop",
    # 花
    "minecraft:dandelion", "minecraft:poppy", "minecraft:blue_orchid", "minecraft:allium",
    "minecraft:azure_bluet", "minecraft:red_tulip", "minecraft:orange_tulip",
    "minecraft:white_tulip", "minecraft:pink_tulip", "minecraft:oxeye_daisy",
    "minecraft:cornflower", "minecraft:lily_of_the_valley", "minecraft:sunflower",
    "minecraft:lilac", "minecraft:rose_bush", "minecraft:peony",
    "minecraft:torchflower", "minecraft:pitcher_plant",
    "minecraft:red_flower", "minecraft:yellow_flower", "minecraft:wither_rose",
    "minecraft:waterlily",
    # 树苗 / 蘑菇
    "minecraft:oak_sapling", "minecraft:spruce_sapling", "minecraft:birch_sapling",
    "minecraft:jungle_sapling", "minecraft:acacia_sapling", "minecraft:dark_oak_sapling",
    "minecraft:mangrove_propagule", "minecraft:cherry_sapling", "minecraft:pale_oak_sapling",
    "minecraft:red_mushroom", "minecraft:brown_mushroom",
    # 无碰撞的装饰 / 功能方块
    "minecraft:torch", "minecraft:soul_torch", "minecraft:redstone_torch", "minecraft:unlit_redstone_torch",
    "minecraft:copper_torch", "minecraft:redstone_wire", "minecraft:vine", "minecraft:web",
    "minecraft:rail", "minecraft:golden_rail", "minecraft:detector_rail", "minecraft:activator_rail",
    "minecraft:fire", "minecraft:soul_fire", "minecraft:light_block", "minecraft:structure_void",
    # 告示牌（站立牌 / 墙牌 / 悬挂牌）
    "minecraft:standing_sign", "minecraft:wall_sign",
    "minecraft:oak_hanging_sign", "minecraft:spruce_hanging_sign", "minecraft:birch_hanging_sign",
    "minecraft:jungle_hanging_sign", "minecraft:acacia_hanging_sign", "minecraft:dark_oak_hanging_sign",
    "minecraft:mangrove_hanging_sign", "minecraft:cherry_hanging_sign", "minecraft:bamboo_hanging_sign",
    "minecraft:crimson_hanging_sign", "minecraft:warped_hanging_sign", "minecraft:pale_oak_hanging_sign",
    "minecraft:poplar_hanging_sign",
    "minecraft:spruce_standing_sign", "minecraft:spruce_wall_sign",
    "minecraft:birch_standing_sign", "minecraft:birch_wall_sign",
    "minecraft:jungle_standing_sign", "minecraft:jungle_wall_sign",
    "minecraft:acacia_standing_sign", "minecraft:acacia_wall_sign",
    "minecraft:darkoak_standing_sign", "minecraft:darkoak_wall_sign",
    "minecraft:mangrove_standing_sign", "minecraft:mangrove_wall_sign",
    "minecraft:cherry_standing_sign", "minecraft:cherry_wall_sign",
    "minecraft:bamboo_standing_sign", "minecraft:bamboo_wall_sign",
    "minecraft:crimson_standing_sign", "minecraft:crimson_wall_sign",
    "minecraft:warped_standing_sign", "minecraft:warped_wall_sign",
    "minecraft:pale_oak_standing_sign", "minecraft:pale_oak_wall_sign",
    "minecraft:poplar_standing_sign", "minecraft:poplar_wall_sign",
    # 按钮 / 拉杆 / 压力板
    "minecraft:wooden_button", "minecraft:stone_button", "minecraft:spruce_button", "minecraft:birch_button",
    "minecraft:jungle_button", "minecraft:acacia_button", "minecraft:dark_oak_button",
    "minecraft:mangrove_button", "minecraft:cherry_button", "minecraft:bamboo_button",
    "minecraft:crimson_button", "minecraft:warped_button", "minecraft:pale_oak_button",
    "minecraft:polished_blackstone_button", "minecraft:poplar_button", "minecraft:lever",
    "minecraft:wooden_pressure_plate", "minecraft:stone_pressure_plate",
    "minecraft:light_weighted_pressure_plate", "minecraft:heavy_weighted_pressure_plate",
    "minecraft:spruce_pressure_plate", "minecraft:birch_pressure_plate", "minecraft:jungle_pressure_plate",
    "minecraft:acacia_pressure_plate", "minecraft:dark_oak_pressure_plate",
    "minecraft:mangrove_pressure_plate", "minecraft:cherry_pressure_plate", "minecraft:bamboo_pressure_plate",
    "minecraft:crimson_pressure_plate", "minecraft:warped_pressure_plate",
    "minecraft:pale_oak_pressure_plate", "minecraft:polished_blackstone_pressure_plate",
    "minecraft:poplar_pressure_plate",
    # 旗帜 / 梯子 / 绊线 / 花盆 / 传送门
    "minecraft:standing_banner", "minecraft:wall_banner",
    "minecraft:ladder", "minecraft:trip_wire", "minecraft:tripwire", "minecraft:tripwire_hook",
    "minecraft:flower_pot",
    "minecraft:portal", "minecraft:nether_portal", "minecraft:end_portal", "minecraft:end_gateway",
    # 藤蔓 / 地衣 / 垂根 / 孢子花
    "minecraft:cave_vines", "minecraft:cave_vines_body_with_berries", "minecraft:cave_vines_head_with_berries",
    "minecraft:twisting_vines", "minecraft:weeping_vines",
    "minecraft:glow_lichen", "minecraft:sculk_vein", "minecraft:pale_hanging_moss", "minecraft:hanging_roots",
    "minecraft:spore_blossom", "minecraft:nether_sprouts", "minecraft:crimson_roots", "minecraft:warped_roots",
    # 细碎植被 / 小型植物
    "minecraft:leaf_litter", "minecraft:pink_petals", "minecraft:wildflowers", "minecraft:resin_clump",
    "minecraft:small_dripleaf_block", "minecraft:cocoa", "minecraft:nether_wart",
    "minecraft:short_dry_grass", "minecraft:tall_dry_grass", "minecraft:bush",
    "minecraft:cactus_flower", "minecraft:firefly_bush",
    "minecraft:open_eyeblossom", "minecraft:closed_eyeblossom", "minecraft:pointed_dripstone",
    # 旧版 ID 别名
    "minecraft:sapling", "minecraft:tallgrass",
    # 物品展示框
    "minecraft:frame", "minecraft:glow_frame"})

class UnloadedChunksError(Exception) : pass
class IllegalPositionError(Exception) : pass
class RegionOverlapError(Exception) : pass
class SummonFalidError(Exception) : pass
class ParticleDef(TypedDict) :
    Identifier:str
    Location:Sequence[float]
    Duration:int



class ChunkDataBase :

    def __init__(self, main_thread:MinecraftSimulator, dimension:"Dimension", path:str):
        self.__loaded = False
        self.__path = path
        self.__dimension = dimension
        self.__chunkDB:sqlite3.Connection  = None


    def lazy_load(self) :
        if self.__loaded : return None

        path = self.__path
        if path == ":memory:" :
            self.__chunkDB = sqlite3.Connection(path)
            self.__chunkDB.execute(Chunk_DB_Create)
            self.__loaded = True
            return None

        self.__chunkDB:sqlite3.Connection  = sqlite3.Connection(path / "chunks.db")
        self.__chunkDB.execute(Chunk_DB_Create)
        self.__loaded = True

    def close(self) :
        if self.__chunkDB : self.__chunkDB.close()

    def commit(self) :
        if self.__chunkDB : self.__chunkDB.commit()


    def get_chunk(self, pos:Tuple[int, int]) :
        self.lazy_load()
        row = self.__chunkDB.execute(Chunk_DB_Read, pos).fetchone()
        if row is None: return None
        return Chunk(self.__dimension).from_bytes(row)

    def get_chunk_entity(self, pos:Tuple[int, int]) :
        """
        读一个区块的实体索引（8 字节 UniqueID 列表），不需要把区块载入内存。
        返回 None 表示该区块还没存过盘（没有行）；返回 b"" 表示区块存在但没有实体。
        """
        self.lazy_load()
        row = self.__chunkDB.execute(Chunk_DB_Read_Entity, pos).fetchone()
        if row is None : return b""

        data = zlib.decompress(row[0])
        return data

    def save_chunk(self, pos:Tuple[int, int], chunk:"Chunk", auto_save:bool=True) :
        self.lazy_load()
        block_data, block_entities_data, entities_data = chunk.to_bytes()
        self.__chunkDB.execute(Chunk_DB_Write, (pos[0], pos[1], block_data, block_entities_data, entities_data) )
        if auto_save : self.commit()

    def save_chunk_entity(self, pos:Tuple[int, int], data:bytes, auto_save:bool=True) :
        self.lazy_load()

        row = self.__chunkDB.execute(Chunk_DB_Exists, pos).fetchone()
        if row is None: self.save_chunk(pos, Chunk(self.__dimension), auto_save=False)

        zip_data = zlib.compress(data)
        self.__chunkDB.execute(Chunk_DB_Write_Entity, (zip_data, pos[0], pos[1]))
        if auto_save : self.commit()


    def add_chunk_entity(self, *entities) :
        from .entity import Entity, Player

        for entity in entities :
            if not isinstance(entity, Entity) : raise TypeError("entity 传入了非实体类型")
            if isinstance(entity, Player) : raise TypeError("entity 传入了玩家类型")

            pos = (math.floor(entity.Pos[0] / 16), math.floor(entity.Pos[2] / 16))
            entity_bytes = self.get_chunk_entity(pos)
            io1 = io.BytesIO()
            io1.write(entity_bytes)
            nbt.write_to_nbt_file(io1, entity.serialization())
            self.save_chunk_entity(pos, io1.getvalue(), auto_save=False)
        
        self.commit()

class BiList(Generic[T]):

    def __init__(self, iterable: Iterable[T] = ()) -> None:
        self.__forward: List[T] = []
        self.__backward: Dict[T, int] = {}
        self.extend(iterable)

    def __str__(self) -> str:
        return str(self.__forward)

    def __repr__(self) -> str:
        return f"<BiList Object id={id(self)}\n    list={self.__forward}\n    dict={self.__backward}\n>"

    def __iter__(self):
        return self.__forward.__iter__()

    def __len__(self) -> int:
        return len(self.__forward)

    def __getitem__(self, index: Union[int, T]) -> T:
        return self.__forward[index] if index.__class__ is int else self.__backward[index]

    def __setitem__(self, key: int, value: T) -> None:
        if key >= len(self.__forward):
            raise IndexError(f'Key {key} out of index.')
        if value in self.__backward:
            raise ValueError("不允许赋值相同对象")
        if self.__forward[key] in self.__backward:
            del self.__backward[self.__forward[key]]
        self.__forward[key] = value
        self.__backward[value] = key

    def __delitem__(self, key: Union[int, T]) -> None:
        if key.__class__ is int:
            if key >= len(self.__forward):
                raise IndexError(f'Key {key} out of index.')
            del self.__backward[self.__forward[key]]
            del self.__forward[key]
            for i in range(key, len(self.__forward)):
                self.__backward[self.__forward[i]] = i
        elif key in self.__backward:
            idx = self.__backward[key]
            del self.__forward[self.__backward[key]]
            del self.__backward[key]
            for i in range(idx, len(self.__forward)):
                self.__backward[self.__forward[i]] = i
        else:
            raise KeyError(f'Key or value {key} not found.')

    def __contains__(self, value: T) -> bool:
        return value in self.__backward

    def __reversed__(self):
        return self.__forward.__reversed__()

    def clear(self) -> None:
        self.__forward.clear()
        self.__backward.clear()

    def copy(self) -> 'BiList[T]':
        return self.__class__(self.__forward)

    def append(self, value: T) -> int:
        if value in self.__backward:
            return self.__backward[value]
        self.__backward[value] = len(self.__forward)
        self.__forward.append(value)
        return self.__backward[value]

    def insert(self, index: int, value: T) -> None:
        if value in self.__backward:
            raise ValueError("不允许赋值相同对象")
        self.__forward.insert(index, value)
        for i, j in zip(self.__forward[index:], itertools.count(index)):
            self.__backward[i] = j

    def extend(self, iterable: Iterable[T]) -> None:
        for value in iterable:
            if value in self.__backward:
                continue
            self.__backward[value] = len(self.__forward)
            self.__forward.append(value)

    def pop(self, index: int) -> T:
        a = self.__forward.pop(index)
        del self.__backward[a]
        for i, j in zip(self.__forward[index:], itertools.count(index)):
            self.__backward[i] = j
        return a

    def remove(self, value: T) -> None:
        if value not in self.__backward:
            raise ValueError(f"object {value} not in list.")
        a = self.__backward[value]
        self.pop(a)

    def index(self, value: T, start: int = 0, stop: int = 2**63 - 1) -> int:
        return self.__forward.index(value, start, stop)

class TimeManager :
    """管理游戏时间"""

    def __init__(self):
        self.__TimeOfDay = {"day":1000, "noon":6000, "sunset":12000, "night":13000, "midnight":18000, "sunrise":23000}
        self.CurrentTime = np.int32(0)
        self.Paused:bool = False
    
    @property
    def TicksPerDay(self) : return np.int32(24000)
    
    @property
    def TicksPerSecond(self) : return np.int32(20)

    def get_day(self) :
        return self.CurrentTime // self.TicksPerDay

    def get_time_of_day(self) :
        return self.CurrentTime % self.TicksPerDay


    def set_time(self, v:int) :
        self.CurrentTime = np.int32(v)

    def set_time_of_day(self, v:str) :
        time = self.__TimeOfDay.get(v)
        if time is None : raise KeyError(f"{v} not in time of day")
        
        dif_time = time - self.get_time_of_day()  #23000 - 23500
        if dif_time > 0 : self.CurrentTime += dif_time
        else : self.CurrentTime += (self.TicksPerDay + dif_time)

    def resolve_time_marker(self, marker:str) -> Optional[int] :
        """
        时间标记（1.26.60 /time set <TimeMarker>）→ 当日的刻数。
        允许带 minecraft: 命名空间前缀；不认识时返回 None。
        """
        return self.__TimeOfDay.get(str(marker).split(":", 1)[-1])


    def serialization(self) :
        Data = nbt.TAG_Compound({"CurrentTime":self.CurrentTime.value})
        return Data

    def deserialization(self, data:nbt.TAG_Compound) -> "TimeManager" :
        if not isinstance(data, nbt.TAG_Compound) : return self
        self.CurrentTime = np.int32( int( data.get("CurrentTime", 0) ))
        return self



class Chunk :
    """
    BlockIndex -> Array<u_short>
    BlockEntities -> Array<nbt>
    Entities -> Array<nbt>
    """

    def __init__(self, dimension:"Dimension", empty_chunk:bool=False) :
        from .block import Block
        from .entity import Entity
        self.__dimension = dimension
        self.BlockIndex = array.array("H")
        self.Entities:List[Entity] = []
        self.BlockEntities: Dict[int, Block] = {}

        if empty_chunk :
            self.BlockIndex.append(0)
            self.BlockIndex = self.BlockIndex * (16 * 16 * (self.__dimension.HeightMax - self.__dimension.HeightMin))
        elif  self.__dimension.Identifier == "overworld" and \
            self.__dimension.MainThread.MinecraftWorld.WorldType == "infinity" :
            self.BlockIndex.frombytes( zlib.decompress(InfinityWorldArray) )
        elif  self.__dimension.Identifier == "overworld" and \
            self.__dimension.MainThread.MinecraftWorld.WorldType == "flat" :
            self.BlockIndex.frombytes( zlib.decompress(FlatWorldArray) )
        elif  self.__dimension.Identifier == "nether" :
            self.BlockIndex.frombytes( zlib.decompress(NetherArray) )
        elif  self.__dimension.Identifier == "the_end" :
            self.BlockIndex.frombytes( zlib.decompress(TheEndArray) )

    def __get_index__(self, x:int, y:int, z:int) :
        x, y, z = int(x)%16, int(y)-self.__dimension.HeightMin, int(z)%16
        return (x * self.__dimension.Height + y) * 16 + z

    def from_bytes(self, data:Tuple[bytes, bytes, bytes]) :
        from .block import Block
        self.BlockIndex = array.array("H")
        self.BlockIndex.frombytes(zlib.decompress(data[0]))

        nbt_bytesIO = io.BytesIO(zlib.decompress(data[1]))
        while nbt_bytesIO.tell() != len(nbt_bytesIO.getbuffer()) :
            try : nbt_data = nbt.read_from_nbt_file(nbt_bytesIO).get_tag()
            except : break
            block_obj = Block()
            block_obj.Dimension = self.__dimension
            if "x" not in nbt_data or "y" not in nbt_data or "z" not in nbt_data : continue
            x, y, z = nbt_data["x"].value, nbt_data["y"].value, nbt_data["z"].value
            index = self.__get_index__(x, y, z)
            block_obj.Permutation = self.__dimension.Permutations[self.BlockIndex[index]]
            block_obj.deserialization(nbt_data)
            block_obj.Dimension = self.__dimension
            self.BlockEntities[index] = block_obj

        Entity = self.__dimension.MainThread.SimulatorModule.Entity
        nbt_bytesIO = io.BytesIO(zlib.decompress(data[2]))
        while nbt_bytesIO.tell() != len(nbt_bytesIO.getbuffer()) :
            try : nbt_data = nbt.read_from_nbt_file(nbt_bytesIO).get_tag()
            except : break
            entity = Entity.deserialization(nbt_data)
            if not entity : continue
            entity.Dimension = self.__dimension
            self.Entities.append(entity)
        
        return self

    def to_bytes(self) -> Tuple[bytes, bytes, bytes] :
        block_index_bytes = zlib.compress(self.BlockIndex.tobytes())

        bio_be = io.BytesIO()
        for idx, block in self.BlockEntities.items():
            nbt_data = block.serialization()
            nbt.write_to_nbt_file(bio_be, nbt_data)
        block_entities_bytes = zlib.compress(bio_be.getvalue())

        bio_ent = io.BytesIO()
        for entity in self.Entities :
            nbt.write_to_nbt_file(bio_ent, entity.serialization())
        entities_bytes = zlib.compress(bio_ent.getvalue())

        return (block_index_bytes, block_entities_bytes, entities_bytes)

class Dimension :

    def __init__(self, main_thread:MinecraftSimulator, id:Constants.DimensionID) :
        from .entity import Entity
        if id not in Constants.DIMENSION_INFO : raise ValueError(f"{id}不是有效的维度名")
        self.DB_Path = main_thread.WorldPath / "dimension" / id
        if main_thread.IsChallenge : self.DB_Path = ":memory:"
        else : os.makedirs(self.DB_Path, exist_ok=True)

        self.Identifier = id
        self.MainThread = main_thread
        self.HeightMin = Constants.DIMENSION_INFO[id]["height"][0]
        self.HeightMax = Constants.DIMENSION_INFO[id]["height"][1]
        self.Height = (self.HeightMax - self.HeightMin)
        self.EntityCache:List[Entity] = []
        self.UnloadChunkEntityCache:List[Entity] = []
        self.Particles:List[ParticleDef] = []
        self.Permutations:BiList[BlockPermutation] = BiList()
        self.Timer = TimeManager() if Constants.DIMENSION_INFO[id]["Time"] else None
        for i in DefaultBlockPalette : self.Permutations.append(
            main_thread.SimulatorModule.BlockPermutation(i["Identifier"], i["BlockState"]) )

        self.__Chunks:Dict[Tuple[int,int], Chunk] = {}
        self.__DataBase = ChunkDataBase(main_thread, self, self.DB_Path)

    def __setattr__(self, name, value):
        if not hasattr(self, name) : super().__setattr__(name, value)
        else : raise RuntimeError(f"不允许修改 {name} 属性")

    def __get_chunk__(self, pos:Sequence[int], vector3=True) :
        if vector3 : chunk_pos = (math.floor(pos[0])//16, math.floor(pos[2])//16)
        else : chunk_pos = pos
        if chunk_pos not in self.__Chunks : raise UnloadedChunksError(f"区块{chunk_pos}未载入内存")
        return self.__Chunks[chunk_pos]

    def __load_chunk__(self, pos:Tuple[int, int]): 
        if pos in self.__Chunks : return self.__Chunks[pos]
        if self.Identifier == "overworld" and \
            pos in Constants.COMMAND_BLOCK_LOAD_CHUNK :
            self.__Chunks[pos] = Chunk(self, empty_chunk=True)
            return self.__Chunks[pos]

        chunk = self.__DataBase.get_chunk(pos)
        if chunk is None: chunk = Chunk(self)

        seen = set(self.EntityCache)
        for entity in chunk.Entities :
            if entity in seen : continue
            self.EntityCache.append(entity)
            seen.add(entity)

        self.__Chunks[pos] = chunk
        return chunk

    def __save_chunk__(self, pos:Tuple[int, int], auto_save:bool=True):
        if pos not in self.__Chunks : return None
        if self.Identifier == "overworld" and \
            pos in Constants.COMMAND_BLOCK_LOAD_CHUNK : return None

        chunk = self.__Chunks[pos]
        self.__DataBase.save_chunk(pos, chunk, auto_save)
        seen = set(self.EntityCache)
        for entity in chunk.Entities :
            if entity in seen : 
                try : 
                    while 1 : self.EntityCache.remove(entity)
                except : pass
                seen.remove(entity)
            entity.IsValid = False
        del self.__Chunks[pos]


    def __reload_CB_chunk__(self) :
        if self.Identifier != "overworld" : return
        for pos in Constants.COMMAND_BLOCK_LOAD_CHUNK :
            self.__Chunks[pos] = Chunk(self, empty_chunk=True)

    def __tick__(self) :
        chunk_radius = self.MainThread.MinecraftWorld.SimulatorDistance
        compute_load_chunk:Set[Tuple[int, int]] = set()

        #处理上一刻存在的非加载区块实体
        self.__DataBase.add_chunk_entity(*self.UnloadChunkEntityCache)
        self.UnloadChunkEntityCache.clear()

        #玩家加载区域计算
        for player in self.MainThread.OnlinePlayer :
            if player.Dimension is not self : continue
            posx, posz = math.floor(player.Pos[0]) // 16, math.floor(player.Pos[2]) // 16
            load_range = (posx-chunk_radius, posx+1+chunk_radius, posz-chunk_radius, posz+1+chunk_radius)
            for chunk_pos in itertools.product( range(load_range[0], load_range[1]), range(load_range[2], load_range[3]) ) :
                if (abs(chunk_pos[0] - posx) + abs(chunk_pos[1] - posz) > 
                    (chunk_radius + (0 if chunk_pos[0] == posx or chunk_pos[1] == posz else 1))) : continue
                compute_load_chunk.add(chunk_pos)
        #常加载区域计算
        for _, area in self.MainThread.MinecraftWorld.TickingArea.__iter__() :
            if area["Dimension"] != self.Identifier : continue
            x1, x2, z1, z2 = area["StartPos"][0], area["EndPos"][0]+1, area["StartPos"][1], area["EndPos"][1]+1
            for chunk_pos in itertools.product( range(x1, x2), range(z1, z2) ) : compute_load_chunk.add(chunk_pos)
        #命令方块区域计算
        if self.Identifier == "overworld" : compute_load_chunk.update(Constants.COMMAND_BLOCK_LOAD_CHUNK)

        for chunk_pos in compute_load_chunk : 
            _chunk = self.__load_chunk__(chunk_pos)
            for _entity in _chunk.Entities.copy() : _entity.__tick__()
        save_pos_list = set(self.__Chunks.keys()) - compute_load_chunk
        for chunk_pos in save_pos_list : self.__save_chunk__(chunk_pos, auto_save=False)
        self.__DataBase.commit()

        for _particle in self.Particles.copy() :
            if _particle["Duration"] <= 0 : self.Particles.remove(_particle)
            _particle["Duration"] -= 1

        if self.MainThread.MinecraftWorld.GameRule.dodaylightcycle and \
            self.Timer and (not self.Timer.Paused) : self.Timer.CurrentTime += 1


    def is_chunk_active(self, pos:Sequence[int]) :
        try : chunk = self.__get_chunk__(pos)
        except : return False
        return True

    def get_closest_biome(self, pos:Sequence[int], biome:str) -> Optional[Tuple[int, int]]:
        a = zlib.crc32(self.Identifier.encode())
        def _get_pseudo(chunk_x: int, chunk_z: int) -> str :
            seed = (chunk_x * 374761393) ^ (chunk_z * 668265263)
            seed = (seed ^ a) & 0x7FFFFFFF
            return biome_list[seed % len(biome_list)]

        if biome not in Constants.BIOME: return None
        if self.Identifier not in Constants.BIOME[biome]["dimension"]: return None

        candidates = []
        max_radius = 256
        cx, cz = pos[0] >> 4, pos[2] >> 4
        biome_list = list(i for i,j in Constants.BIOME.items() if self.Identifier in j["dimension"])

        # 按切比雪夫距离 (max(|dx|,|dz|)) 递增搜索
        for r in range(0, max_radius + 1) :
            candidates.clear()
            if r == 0: candidates.append( (0, 0) )
            else :
                candidates.extend([(dx, -r) for dx in range(-r, r + 1)]) # 上边 (dx: -r -> r, dz = -r)
                candidates.extend([(dx, r) for dx in range(-r, r + 1)])  # 下边 (dx: -r -> r, dz = r)
                candidates.extend([(-r, dz) for dz in range(-r + 1, r)]) # 左边 (dx = -r, dz: -r+1 -> r-1)
                candidates.extend([(r, dz) for dz in range(-r + 1, r)])  # 右边 (dx = r, dz: -r+1 -> r-1)

            for dx, dz in candidates:
                target_cx = cx + dx
                target_cz = cz + dz
                generate_biome = _get_pseudo(target_cx, target_cz)
                if generate_biome == biome : return (target_cx * 16 + 8, target_cz * 16 + 8)

        return None

    def get_closest_structure(self, pos:Sequence[int], structure:str) -> Optional[Tuple[int, int]]:
        a = zlib.crc32(self.Identifier.encode())
        def _get_pseudo(chunk_x: int, chunk_z: int) -> str :
            seed = (chunk_x * 374761393) ^ (chunk_z * 668265263)
            seed = (seed ^ a) & 0x7FFFFFFF
            return structure_list[seed % len(structure_list)]

        if structure not in Constants.STRUCTURE: return None
        if self.Identifier not in Constants.STRUCTURE[structure]["dimension"]: return None

        candidates = []
        max_radius = 256
        cx, cz = pos[0] >> 4, pos[2] >> 4
        structure_list = list(i for i,j in Constants.STRUCTURE.items() if self.Identifier in j["dimension"])

        # 按切比雪夫距离 (max(|dx|,|dz|)) 递增搜索
        for r in range(0, max_radius + 1) :
            candidates.clear()
            if r == 0: candidates.append( (0, 0) )
            else :
                candidates.extend([(dx, -r) for dx in range(-r, r + 1)]) # 上边 (dx: -r -> r, dz = -r)
                candidates.extend([(dx, r) for dx in range(-r, r + 1)])  # 下边 (dx: -r -> r, dz = r)
                candidates.extend([(-r, dz) for dz in range(-r + 1, r)]) # 左边 (dx = -r, dz: -r+1 -> r-1)
                candidates.extend([(r, dz) for dz in range(-r + 1, r)])  # 右边 (dx = r, dz: -r+1 -> r-1)

            for dx, dz in candidates:
                target_cx = cx + dx
                target_cz = cz + dz
                generate = _get_pseudo(target_cx, target_cz)
                if generate == structure : return (target_cx * 16 + 8, target_cz * 16 + 8)

        return None

    def get_block_permutation(self, pos:Sequence[int]) -> BlockPermutation :
        chunk = self.__get_chunk__(pos)
        if not(self.HeightMin <= pos[1] < self.HeightMax) : raise IllegalPositionError(f"位置{pos}处于世界之外")
        index = chunk.__get_index__(pos[0], pos[1], pos[2])
        return self.Permutations[ chunk.BlockIndex[index] ]

    def get_block(self, pos:Sequence[int]) -> Block :
        chunk = self.__get_chunk__(pos)
        if not(self.HeightMin <= pos[1] < self.HeightMax) : raise IllegalPositionError(f"位置{pos}处于世界之外")
        index = chunk.__get_index__(pos[0], pos[1], pos[2])
        if index in chunk.BlockEntities : return chunk.BlockEntities[index]
        block_obj = Block()
        block_obj.Permutation = self.Permutations[ chunk.BlockIndex[index] ]
        block_obj.x = pos[0]
        block_obj.y = pos[1]
        block_obj.z = pos[2]
        block_obj.Dimension = self
        if block_obj.get_components() : chunk.BlockEntities[index] = block_obj
        return block_obj

    def get_surface_block(self, pos:Tuple[int, int], max_y:int=100000) :
        x, z = math.floor(pos[0]), math.floor(pos[1])
        max_y = max(self.HeightMin, min(max_y, self.HeightMax - 1))
        for y in range(max_y, self.HeightMin-1, -1) :
            block = self.get_block((x, y, z))
            if block.Permutation.name == "minecraft:air" : continue
            return block
        return None

    def set_block_permutation(self, pos:Sequence[int], block:BlockPermutation) -> BlockPermutation :
        chunk = self.__get_chunk__(pos)
        if not(self.HeightMin <= pos[1] < self.HeightMax) : raise IllegalPositionError(f"位置{pos}处于世界之外")
        index = chunk.__get_index__(pos[0], pos[1], pos[2])
        block_index = self.Permutations.append(block)
        chunk.BlockIndex[index] = block_index

        if index in chunk.BlockEntities : 
            block_obj = chunk.BlockEntities[index]
            if block_obj.get_components() : block_obj.Permutation = block
            else : del chunk.BlockEntities[index]

    def fill_blocks(self, start_pos:Sequence[int], end_pos:Sequence[int], block:BlockPermutation,
        fill_options:Literal["outline","hollow","destroy","keep","replace"]="replace", 
        replace_condition:Callable[[BlockPermutation], bool]=None) :
        from .entity import EntityItemComponent
        from .block import BlockInventoryComponent

        def replace_mode(chunk_obj:Chunk, x:int, y:int, z:int, index:int) :
            if chunk_obj.BlockIndex[index] != block_index :
                chunk_obj.BlockIndex[index] = block_index
                return 1
            else: return 0

        def replace_block_mode(chunk_obj:Chunk, x:int, y:int, z:int, index:int) :
            if not replace_condition(self.Permutations[chunk_obj.BlockIndex[index]]) : return 0
            if chunk_obj.BlockIndex[index] != block_index :
                chunk_obj.BlockIndex[index] = block_index
                return 1
            else: return 0

        def keep_mode(chunk_obj:Chunk, x:int, y:int, z:int, index:int) :
            if chunk_obj.BlockIndex[index] : return 0
            if chunk_obj.BlockIndex[index] != block_index :
                chunk_obj.BlockIndex[index] = block_index
                return 1
            else: return 0

        def outline_mode(chunk_obj:Chunk, x:int, y:int, z:int, index:int) :
            is_inside = (start_pos[0] < x < end_pos[0] and
                start_pos[1] < y < end_pos[1] and start_pos[2] < z < end_pos[2])
            if not is_inside :
                if chunk_obj.BlockIndex[index] != block_index : 
                    chunk_obj.BlockIndex[index] = block_index
                    return 1
                else : return 0
            else: return 0

        def hollow_mode(chunk_obj:Chunk, x:int, y:int, z:int, index:int) :
            is_inside = (start_pos[0] < x < end_pos[0] and
                start_pos[1] < y < end_pos[1] and start_pos[2] < z < end_pos[2])
            if not is_inside : 
                if chunk_obj.BlockIndex[index] != block_index :
                    chunk_obj.BlockIndex[index] = block_index
                    return 1
                else : return 0
            else : 
                if chunk_obj.BlockIndex[index] != 0 :
                    chunk_obj.BlockIndex[index] = 0
                    return 1
                else : return 0

        def __get_block(chunk_obj:Chunk, x:int, y:int, z:int, index:int) :
            if index in chunk_obj.BlockEntities : return chunk_obj.BlockEntities[index]
            block_obj = Block()
            block_obj.Permutation = self.Permutations[ chunk_obj.BlockIndex[index] ]
            block_obj.x, block_obj.y, block_obj.z = x, y, z
            block_obj.Dimension = self
            if block_obj.get_components() : chunk_obj.BlockEntities[index] = block_obj
            return block_obj

        def destroy_mode(chunk_obj:Chunk, x:int, y:int, z:int, index:int) :
            block_obj = __get_block(chunk_obj, x, y, z, index)

            if self.MainThread.MinecraftWorld.GameRule.dotiledrops :
                loot_items = self.MainThread.LootManager.loot_from_block(block_obj, pickaxe_tool)
                if not loot_items : loot_items = self.MainThread.LootManager.loot_from_block(block_obj, slove_tool)
                if loot_items :
                    _pos = (x+random.random(), y+random.random(), z+random.random())
                    _entity = self.spawn_entity("minecraft:item", _pos, (0, 0))
                    _comp1:EntityItemComponent = _entity.get_component(EntityItemComponent)
                    _comp1.ItemStack = loot_items[0]
                _comp2:BlockInventoryComponent = block_obj.get_component(BlockInventoryComponent)
                if not block_obj.Permutation.name.endswith("_shulker_box") and _comp2 :
                    for _item in _comp2.Container.Items :
                        _pos = (block_obj.x+random.random(), block_obj.y+random.random(), block_obj.z+random.random())
                        _entity = self.spawn_entity("minecraft:item", _pos, (0, 0))
                        _comp1:EntityItemComponent = _entity.get_component(EntityItemComponent)
                        _comp1.ItemStack = _item

            chunk_obj.BlockIndex[index] = block_index
            return 1


        ItemStack = self.MainThread.SimulatorModule.ItemStack
        start_pos = [math.floor(i) for i in start_pos[0:3]]
        end_pos = [math.floor(i) for i in end_pos[0:3]]
        if start_pos[0] > end_pos[0] : start_pos[0], end_pos[0] = end_pos[0], start_pos[0]
        if start_pos[1] > end_pos[1] : start_pos[1], end_pos[1] = end_pos[1], start_pos[1]
        if start_pos[2] > end_pos[2] : start_pos[0], end_pos[2] = end_pos[2], start_pos[2]
        if not(self.HeightMin <= start_pos[1] < self.HeightMax) : raise IllegalPositionError(f"起始位置{start_pos}处于世界之外")
        if not(self.HeightMin <= end_pos[1] < self.HeightMax) : raise IllegalPositionError(f"结束位置{end_pos}处于世界之外")
        block_index = self.Permutations.append(block)
        for cx1, cz1, cx2, cz2 in iter_pos(start_pos[0], start_pos[2], end_pos[0], end_pos[2]) :
            chunk_pos = (cx1//16, cz1//16)
            if chunk_pos not in self.__Chunks : raise UnloadedChunksError(f"区块{chunk_pos}未载入内存")

        count = 0
        slove_tool = ItemStack("netherite_shovel")
        pickaxe_tool = ItemStack("netherite_pickaxe")
        func_choose = {"outline":outline_mode, "hollow":hollow_mode, "destroy":destroy_mode, 
            "keep":keep_mode, "replace":replace_mode}[fill_options]
        if callable(replace_condition) : func_choose = replace_block_mode
        for cx1, cz1, cx2, cz2 in iter_pos(start_pos[0], start_pos[2], end_pos[0], end_pos[2]) :
            chunk_pos = (cx1//16, cz1//16)
            chunk_obj = self.__Chunks[chunk_pos]
            pos_iter = itertools.product(range(cx1, cx2), range(start_pos[1], end_pos[1]+1), range(cz1, cz2))
            for x, y, z in pos_iter :
                index = chunk_obj.__get_index__(x, y, z)
                count += func_choose(chunk_obj, x, y, z, index)

                if index in chunk_obj.BlockEntities : 
                    block_obj = chunk_obj.BlockEntities[index]
                    if block_obj.get_components() : block_obj.Permutation = block
                    else : del chunk_obj.BlockEntities[index]

        return count

    def clone_blocks(self, start_pos:Sequence[int], end_pos:Sequence[int], clone_pos:Sequence[int],
        mask_mode:Literal["replace","masked","filtered"]="replace",
        clone_mode:Literal["normal","force","move"]="normal", 
        block_test:Callable[[BlockPermutation], bool]=None) :

        start_pos = [math.floor(i) for i in start_pos]
        end_pos = [math.floor(i) for i in end_pos]
        clone_pos = [math.floor(i) for i in clone_pos]
        if start_pos[0] > end_pos[0] : start_pos[0], end_pos[0] = end_pos[0], start_pos[0]
        if start_pos[1] > end_pos[1] : start_pos[1], end_pos[1] = end_pos[1], start_pos[1]
        if start_pos[2] > end_pos[2] : start_pos[2], end_pos[2] = end_pos[2], start_pos[2]
        clone_pos_end = [clone_pos[index] + end_pos[index] - start_pos[index] for index in range(3)]
        if not(self.HeightMin <= start_pos[1] < self.HeightMax) : raise IllegalPositionError(f"复制起始位置{start_pos}处于世界之外")
        if not(self.HeightMin <= end_pos[1] < self.HeightMax) : raise IllegalPositionError(f"复制结束位置{end_pos}处于世界之外")
        if not(self.HeightMin <= clone_pos[1] < self.HeightMax) : raise IllegalPositionError(f"导出起始位置{start_pos}处于世界之外")
        if not(self.HeightMin <= clone_pos_end[1] < self.HeightMax) : raise IllegalPositionError(f"导出结束位置{end_pos}处于世界之外")

        if clone_mode != "force" and all( max(start_pos[index], clone_pos[index]) <= 
            min(end_pos[index], clone_pos_end[index]) for index in range(3)) :
            raise RegionOverlapError("非force模式下无法区域重叠复制")
        for cx1, cz1, cx2, cz2 in iter_pos(start_pos[0], start_pos[2], end_pos[0], end_pos[2]) :
            chunk_pos = (cx1//16, cz1//16)
            if chunk_pos not in self.__Chunks : raise UnloadedChunksError(f"复制区块{chunk_pos}未载入内存")
        for cx1, cz1, cx2, cz2 in iter_pos(clone_pos[0], clone_pos[2], clone_pos_end[0], clone_pos_end[2]) :
            chunk_pos = (cx1//16, cz1//16)
            if chunk_pos not in self.__Chunks : raise UnloadedChunksError(f"导出区块{chunk_pos}未载入内存")

        volume = [end_pos[index] - start_pos[index] + 1 for index in range(3)]
        total = volume[0] * volume[1] * volume[2]
        read_iter = itertools.product(range(start_pos[0], end_pos[0]+1), range(start_pos[1], end_pos[1]+1), 
                                      range(start_pos[2], end_pos[2]+1))
        clear_iter = itertools.product(range(start_pos[0], end_pos[0]+1), range(start_pos[1], end_pos[1]+1), 
                                       range(start_pos[2], end_pos[2]+1))
        save_iter = itertools.product(range(clone_pos[0], clone_pos_end[0]+1), range(clone_pos[1], clone_pos_end[1]+1), 
                                      range(clone_pos[2], clone_pos_end[2]+1))
        copied_flags = bytearray(total)
        read_index_list = array.array("H", (0, )) * total
        block_data_list:List[Block] = [None] * total

        # 1) 先整体快照源区域：只记录调色板下标 + 方块实体的 NBT
        #  （两个区域共用同一个 self.Permutations，写回时直接搬下标；
        #   masked/filtered 跳过的位置 copied_flags 保持 0，move/重叠复制也不会读到已被改写的方块）
        for index, (x, y, z) in enumerate(read_iter) :
            chunk_obj = self.__Chunks[(x // 16, z // 16)]
            local_index = chunk_obj.__get_index__(x, y, z)
            block_index = chunk_obj.BlockIndex[local_index]
            permutation = self.Permutations[block_index]
            if mask_mode == "masked" and permutation.name == "minecraft:air" : continue
            if mask_mode == "filtered" and not (block_test and block_test(permutation)) : continue

            copied_flags[index] = 1
            read_index_list[index] = block_index

            block_obj = chunk_obj.BlockEntities.get(local_index)
            if block_obj : block_data_list[index] = block_obj

        # 2) move：复制完成后把源区域里真正被复制的方块清成空气
        if clone_mode == "move" :
            for index, (x, y, z) in enumerate(clear_iter) :
                if not copied_flags[index] : continue
                chunk_obj = self.__Chunks[(x // 16, z // 16)]
                local_index = chunk_obj.__get_index__(x, y, z)
                chunk_obj.BlockIndex[local_index] = 0
                if local_index in chunk_obj.BlockEntities : del chunk_obj.BlockEntities[local_index]

        # 3) 写入目标区域
        count = 0
        for index, (x, y, z) in enumerate(save_iter) :
            if not copied_flags[index] : continue
            chunk_obj = self.__Chunks[(x // 16, z // 16)]
            local_index = chunk_obj.__get_index__(x, y, z)
            chunk_obj.BlockIndex[local_index] = read_index_list[index]

            if local_index in chunk_obj.BlockEntities :         # 目标位置原有的方块实体一律丢弃
                del chunk_obj.BlockEntities[local_index]
            old_block_obj = block_data_list[index]
            if old_block_obj : # 按新方块类型重建组件后把数据灌回去
                block_obj = self.get_block((x, y, z))
                for _comp1 in old_block_obj.get_components() : 
                    nbt_obj = nbt.TAG_Compound()
                    _comp1.to_nbt(nbt_obj)
                    block_obj.get_component(_comp1).from_nbt(nbt_obj)
            count += 1

        return count

    def spawn_entity(self, id:str, pos:Sequence[float], rotation:Sequence[float], spawn_event:str=None,
            register_in_world=True, register_in_unload_chunk:bool=False) :
        from .entity import EntityTypeFamilyComponent

        EntityClass = self.MainThread.SimulatorModule.Entity
        entity = EntityClass(id)
        entity.Pos[0] = np.float32(pos[0])
        entity.Pos[1] = np.float32(pos[1])
        entity.Pos[2] = np.float32(pos[2])
        entity.Rotation[0] = np.float32(rotation[0])
        entity.Rotation[1] = np.float32(rotation[1])
        entity.Dimension = self
        if spawn_event : entity.trigger_event(spawn_event)
        comp:EntityTypeFamilyComponent = entity.get_components("minecraft:type_family")
        if comp and "monster" in comp.Family and self.MainThread.MinecraftWorld.Difficulty == 0 : 
            raise SummonFalidError(f"和平模式无法召唤怪物")

        if register_in_world :
            if register_in_unload_chunk and not self.is_chunk_active(pos) :
                self.UnloadChunkEntityCache.append(entity)
            else :
                chunk:Chunk = self.__get_chunk__(pos)
                chunk.Entities.append(entity)
                self.EntityCache.append(entity)

        return entity

    def spawn_particle(self, id:str, pos:Sequence[int], duration:int=40) :
        _particle:ParticleDef = {"Identifier":id, "Location":pos, "Duration":duration}
        self.Particles.append(_particle)

    def teleport_entity(self, entity, pos:Sequence[int], dimension:"Dimension"=None, 
            rotation:Sequence[float]=None, check_blocks:bool=False, keep_velocity:bool=False) -> bool :
        """
        把实体传送到指定坐标（可跨维度）。返回是否传送成功。

        :param pos:          目标坐标，至少 3 个分量（可以是浮点）
        :param dimension:    目标维度；None 表示留在 self 这个维度
        :param rotation:     目标朝向 [yaw, pitch]；None 表示不修改朝向
        :param check_blocks: 是否检查碰撞箱（实体碰撞箱不能和方块碰撞箱重叠）
        :param keep_velocity:是否保留 Motion；False 会把 Motion 清零
        """
        from .entity import Entity, Player, EntityAABBComponent, EntityScaleComponent, EntityRideableComponent
        if not isinstance(entity, Entity) : raise TypeError("entity 传入了非实体对象")
        if len(pos) < 3 : raise ValueError("pos 至少需要 3 个分量")
        if dimension is not None and not isinstance(dimension, Dimension) : raise TypeError("dimension 传入了非维度对象")
        if rotation is not None and len(rotation) < 2 : raise ValueError("rotation 至少需要 2 个分量")

        target:Dimension = self if dimension is None else dimension
        if not entity.IsValid : return False

        # 1) 遮挡判断：只遍历碰撞箱的 8 个顶点
        #    读方块用 chunk_active=False —— 只要求区块在内存里，不要求它是 Active
        if check_blocks :
            aabb_comp:EntityAABBComponent = entity.get_component(EntityAABBComponent, bottom=True)
            scale_comp:EntityScaleComponent = entity.get_component(EntityScaleComponent, bottom=True)
            scale = float(scale_comp.Value) if scale_comp else 1.0
            width = (float(aabb_comp.Width) if aabb_comp else 1.0) * scale
            height = (float(aabb_comp.Height) if aabb_comp else 1.0) * scale

            eps = 1e-5
            box_x1, box_x2 = float(pos[0]) - width / 2, float(pos[0]) + width / 2 - eps
            box_y1, box_y2 = float(pos[1])           , float(pos[1]) + height   - eps
            box_z1, box_z2 = float(pos[2]) - width / 2, float(pos[2]) + width / 2 - eps

            checked_cells = set()
            for corner_x in (box_x1, box_x2) :
                for corner_y in (box_y1, box_y2) :
                    for corner_z in (box_z1, box_z2) :
                        cell = (math.floor(corner_x), math.floor(corner_y), math.floor(corner_z))
                        if cell in checked_cells : continue
                        checked_cells.add(cell)
                        if not(target.HeightMin <= cell[1] < target.HeightMax) : continue
                        try : _block = target.get_block_permutation(cell, chunk_active=False)
                        except UnloadedChunksError : return False # 顶点处读不到方块 → 无法确认安全
                        if _block.name not in NO_COLLISION_BLOCKS : return False

        # 2) 骑乘关系
        #    - 被传送者本身是乘客 → 一律强制下车
        #    - 跨维度 → 连同它的乘客一起解除乘骑（不带着乘客穿维度）
        same_dimension = entity.Dimension is target
        vehicle:Entity = entity.VehicleEntity
        if vehicle is not None : 
            _comp:EntityRideableComponent = vehicle.get_component(EntityRideableComponent)
            if _comp : _comp.eject_rider(entity)
            entity.VehicleEntity = None
        if not same_dimension :
            _comp:EntityRideableComponent = entity.get_component(EntityRideableComponent)
            if _comp : _comp.eject_rider()

        # 3) 记录旧归属（只查询，不加载任何区块）
        old_dimension:Dimension = entity.Dimension
        old_chunk_pos = (math.floor(entity.Pos[0]) // 16, math.floor(entity.Pos[2]) // 16)
        old_chunk:Chunk = None
        try : old_chunk = old_dimension.__get_chunk__(old_chunk_pos, vector3=False)
        except UnloadedChunksError : pass

        # 4) 写坐标 / 朝向 / 速度
        for index in range(3) : entity.Pos[index] = np.float32(pos[index])
        if rotation is not None :
            entity.Rotation[0] = np.float32(rotation[0])
            entity.Rotation[1] = np.float32(rotation[1])
        if not keep_velocity :
            for index in range(3) : entity.Motion[index] = np.float32(0)

        # 5) 旧归属注销 + 目标归属登记
        #    目标区块在内存里 → 直接进 chunk.Entities / EntityCache；
        #    不在内存里 → 挂到 UnloadChunkEntityCache，等下一次 __tick__ 批量落盘。
        new_chunk_pos = (math.floor(pos[0]) // 16, math.floor(pos[2]) // 16)

        # 旧维度：区块 / EntityCache / 未加载登记表，三处都摘干净
        if old_chunk is not None :
            while entity in old_chunk.Entities : old_chunk.Entities.remove(entity)
        while entity in old_dimension.EntityCache : old_dimension.EntityCache.remove(entity)
        while entity in old_dimension.UnloadChunkEntityCache : old_dimension.UnloadChunkEntityCache.remove(entity)

        # 目标维度也先摘一遍：跨维度时 old_dimension 与 target 不是同一个，
        # 实体可能因为之前的停放/延迟写盘残留在 target 的两个缓存里。
        # 先摘后放，才能保证不变量：在 EntityCache 的实体不会同时出现在 UnloadChunkEntityCache。
        if old_dimension is not target :
            while entity in target.EntityCache : target.EntityCache.remove(entity)
            while entity in target.UnloadChunkEntityCache : target.UnloadChunkEntityCache.remove(entity)

        if isinstance(entity, Player) :
            entity.Dimension = target
            return True

        # is_chunk_active 的实际语义是"区块是否在内存里"（__get_chunk__ 不抛就 True）
        # 注意它接收的是世界坐标（内部会 //16），不能传 new_chunk_pos
        if target.is_chunk_active(pos) :
            new_chunk:Chunk = target.__get_chunk__(new_chunk_pos, vector3=False)
            new_chunk.Entities.append(entity)
            target.EntityCache.append(entity)                   # 已确保不在登记表里
        else : target.UnloadChunkEntityCache.append(entity)     # 已确保不在 EntityCache 里

        entity.Dimension = target

        return True


    def serialization(self) :
        block_nbt = nbt.TAG_Compound()
        block_nbt["BlockPalette"] = nbt.TAG_List([], type=nbt.TAG_Compound)
        for i in self.Permutations : block_nbt["BlockPalette"].append(i.serialization())
        if self.Timer : block_nbt["Clock"] = self.Timer.serialization()

        if not self.MainThread.IsChallenge : 
            _path = self.DB_Path / "DataSave.nbt"
            nbt.write_to_nbt_file(_path, block_nbt, zip_mode="gzip")

        for i in list(self.__Chunks) : self.__save_chunk__(i)
        self.__DataBase.commit()
        self.__DataBase.close()

    def deserialization(self) :
        if self.MainThread.IsChallenge : return None
        _path = self.DB_Path / "BlockPermutations.nbt"
        if not _path.exists() : return self

        try : nbt_data:nbt.TAG_Compound = nbt.read_from_nbt_file(_path, zip_mode="gzip").get_tag()
        except : traceback.print_exc() ; return self

        self.Permutations.clear()
        BlockPermutation = self.MainThread.SimulatorModule.BlockPermutation
        for i in nbt_data["BlockPalette"] : 
            permutation = BlockPermutation.deserialization(i)
            self.Permutations.append(permutation)
        if self.Timer : self.Timer.deserialization(nbt_data.get("Clock", nbt.TAG_Compound()))

        return self






