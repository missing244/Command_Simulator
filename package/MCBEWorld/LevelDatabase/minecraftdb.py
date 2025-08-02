import os
from .. import C_leveldb as leveldb
from typing import Literal
from . import chunk_data as ChunkData
from . import other_data as OtherData

DimensionType = Literal["overworld", "nether", "the_end"]

class MinecraftLevelDB(leveldb.LevelDB) :
    """
    基岩版数据库对象
    -----------------------
    * 所有get开头的方法均可使用
    * 可用方法 Chunk_Pos : 获取存档中所有的区块坐标的生成器
    * 可用方法 set_Data : 将get方法获得的数据对象重新写回存档
    """

    def __init__(self, path:str):
        super().__init__(path, create_if_missing=True)


    def Chunk_Pos(self, dimension:DimensionType) :
        operation_bytes = 47
        TestIndex = 8 if dimension == "overworld" else 12

        for key in self.keys() :
            if len(key[TestIndex:1000]) != 2 or key[TestIndex] != operation_bytes : continue
            PosX = int.from_bytes(key[0:4], "little", signed=True)
            PosZ = int.from_bytes(key[4:8], "little", signed=True)
            yield (PosX, PosZ)


    def get_Data3D(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Data3D.from_leveldb(self, dimension, chunk_pos_x, chunk_pos_z)

    def get_Version(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Version.from_leveldb(self, dimension, chunk_pos_x, chunk_pos_z)

    def get_Chunk(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Chunks.from_leveldb(self, dimension, chunk_pos_x, chunk_pos_z)

    def get_BlockEntity(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.BlockEntity.from_leveldb(self, dimension, chunk_pos_x, chunk_pos_z)

    def get_Entity(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Entity.from_leveldb(self, dimension, chunk_pos_x, chunk_pos_z)

    def get_PendingTick(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.PendingTicks.from_leveldb(self, dimension, chunk_pos_x, chunk_pos_z)

    def get_RandomTick(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.RandomTicks.from_leveldb(self, dimension, chunk_pos_x, chunk_pos_z)


    def get_LocalPlayer(self) :
        return OtherData.LocalPlayer.from_leveldb(self)

    def get_OnlinePlayer(self) :
        return OtherData.OnlinePlayer.from_leveldb(self)

    def get_Village(self) :
        return OtherData.Village.from_leveldb(self)

    def get_Map(self) :
        return OtherData.Map.from_leveldb(self)

    def get_Portal(self) :
        return OtherData.Portal.from_leveldb(self)

    def get_Mobevent(self) :
        return OtherData.Mobevent.from_leveldb(self)

    def get_SchedulerWT(self) :
        return OtherData.SchedulerWT.from_leveldb(self)

    def get_Scoreboard(self) :
        return OtherData.Scoreboard.from_leveldb(self)

    def get_Structure(self) :
        return OtherData.Structure.from_leveldb(self)

    def get_TickingArea(self) :
        return OtherData.TickingArea.from_leveldb(self)


    def set_Data(self, data_object) : 
        data_object.to_leveldb(self)

