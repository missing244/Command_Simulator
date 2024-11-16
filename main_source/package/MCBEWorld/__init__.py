"""
基岩版存档读取模块
-----------------------
* 可用函数 Get_World_Edtion : 判断世界类型(网易、基岩、非存档)
* 可用函数 Read_Bedrock_World : 使用基岩版编码模式读取存档
* 可用函数 Read_Netease_World : 使用网易版编码模式读取存档
"""
__version__ = (1, 0, 0)





from typing import Literal,Union
import leveldb,os,io,math,itertools
from ..python_nbt import read_from_nbt_file, write_to_nbt_file, TAG_Compound
from ..file_operation import is_file, is_dir, delete_all_file, file_in_path
from . import chunk_data as ChunkData
from . import other_data as OtherData

Encrypt_Header = b"\x80\x1d\x30\x01"
DimensionType = Literal["overworld", "nether", "the_end"]

class Bedrock_Edtion_World :
    """
    基岩版存档对象
    -----------------------
    * 所有Get开头的方法均可使用
    * 请注意显式调用close方法保存和释放资源
    -----------------------
    * 可用属性 world_name : 世界名
    * 可用属性 world_data : 世界文件level.dat的nbt对象
    * 可用属性 level_db : 世界文件leveldb存档
    -----------------------
    * 可用方法 close : 以网易/基岩版编码格式，保存世界并释放资源
    * 可用方法 Chunk_Pos_Iter : 获取存档中所有的区块坐标的生成器
    * 可用方法 Set_Data : 将Get方法获得的数据对象重新写回存档
    """

    def __init__(self, world_path, encrypt_key:bytes=None) :
        if not is_file(os.path.join(world_path, "levelname.txt")) : world_name = "我的世界"
        else :
            file1 = open(os.path.join(world_path, "levelname.txt"), "r", encoding="utf-8")
            world_name = file1.read()
            file1.close()
        with open(os.path.join(world_path, "level.dat"), "rb") as level_dat_file :
            world_data_version = int.from_bytes(level_dat_file.read(4), "little")
            byte_len = int.from_bytes(level_dat_file.read(4), "little")
            world_data = read_from_nbt_file(level_dat_file.read(byte_len), byteorder='little')

        self.__close = False
        self.world_path = world_path
        self.world_name = world_name
        self.world_data_version = world_data_version
        self.world_data = world_data
        self.encrypt_key = encrypt_key
        self.world_database = leveldb.LevelDB(os.path.join(self.world_path, "db"))

    def __setattr__(self, name, value):
        if name == "world_path" and hasattr(self, "world_path") :
            raise RuntimeError("不允许修改文件路径")
        else : super().__setattr__(name, value)

    def __close__(self) :
        if self.__close : return None

        with open(os.path.join(self.world_path, "levelname.txt"), "w+", encoding="utf-8") as _file :
            _file.write(self.world_name)
        buffer = io.BytesIO()
        write_to_nbt_file(buffer, self.world_data, byteorder='little')
        with open(os.path.join(self.world_path, "level.dat"), "wb") as _file :
            _file.write(self.world_data_version.to_bytes(4, "little"))
            _file.write(buffer.getvalue().__len__().to_bytes(4, "little"))
            _file.write(buffer.getvalue())
            buffer.close()
        self.world_database.close()
        self.__close = True

    def __del__(self) :
        self.close("Bedrock" if self.encrypt_key is None else "Netease")


    def close(self, edtion:Literal["Bedrock", "Netease"]) :
        self.__close__()
        if edtion == "Netease" : 
            if not(isinstance(self.encrypt_key, bytes) and len(self.encrypt_key) == 8) :
                self.encrypt_key = b"abcdefgh"

            source_dir = os.path.join(self.world_path, "db")
            for file_name in os.listdir(source_dir) :
                if not is_file(os.path.join(source_dir, file_name)) : continue
                with open(os.path.join(source_dir, file_name), "rb") as READ_FILE : FILE_BYTES = READ_FILE.read()
                with open(os.path.join(source_dir, file_name), "wb") as WRITE_FILE :
                    WRITE_FILE.write(Encrypt_Header)
                    CycleIter = itertools.cycle(self.encrypt_key)
                    for int1 in FILE_BYTES : WRITE_FILE.write( (int1 ^ next(CycleIter)).to_bytes(1, "little") )


    def Chunk_Pos_Iter(self, dimension:DimensionType) :
        operation_bytes = (43).to_bytes(1, "little", signed=False)
        if dimension == "overworld" : TestBytes = operation_bytes
        elif dimension == "nether" : TestBytes = b"".join((b"\x01\x00\x00\x00", operation_bytes))
        elif dimension == "the_end" : TestBytes = b"".join((b"\x02\x00\x00\x00", operation_bytes))

        for key in self.world_database.keys() :
            if key[8:] != TestBytes : continue
            PosX = int.from_bytes(key[0:4], "little", signed=True)
            PosZ = int.from_bytes(key[4:8], "little", signed=True)
            yield (PosX, PosZ)


    def Get_Data3D(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Data3D.from_leveldb(self.world_database, dimension, chunk_pos_x, chunk_pos_z)

    def Get_Version(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Version.from_leveldb(self.world_database, dimension, chunk_pos_x, chunk_pos_z)

    def Get_Chunk(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Chunks.from_leveldb(self.world_database, dimension, chunk_pos_x, chunk_pos_z)

    def Get_BlockEntity(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.BlockEntity.from_leveldb(self.world_database, dimension, chunk_pos_x, chunk_pos_z)

    def Get_Entity(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.Entity.from_leveldb(self.world_database, dimension, chunk_pos_x, chunk_pos_z)

    def Get_PendingTick(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.PendingTicks.from_leveldb(self.world_database, dimension, chunk_pos_x, chunk_pos_z)

    def Get_RandomTick(self, dimension:DimensionType, chunk_pos_x:int, chunk_pos_z:int) :
        return ChunkData.RandomTicks.from_leveldb(self.world_database, dimension, chunk_pos_x, chunk_pos_z)


    def Get_LocalPlayer(self) :
        return OtherData.LocalPlayer.from_leveldb(self.world_database)

    def Get_OnlinePlayer(self) :
        return OtherData.OnlinePlayer.from_leveldb(self.world_database)

    def Get_Village(self) :
        return OtherData.Village.from_leveldb(self.world_database)

    def Get_Map(self) :
        return OtherData.Map.from_leveldb(self.world_database)

    def Get_Portal(self) :
        return OtherData.Portal.from_leveldb(self.world_database)

    def Get_Mobevent(self) :
        return OtherData.Mobevent.from_leveldb(self.world_database)

    def Get_SchedulerWT(self) :
        return OtherData.SchedulerWT.from_leveldb(self.world_database)

    def Get_Scoreboard(self) :
        return OtherData.Scoreboard.from_leveldb(self.world_database)

    def Get_Structure(self) :
        return OtherData.Structure.from_leveldb(self.world_database)

    def Get_TickingArea(self) :
        return OtherData.TickingArea.from_leveldb(self.world_database)


    def Set_Data(self, data_object) : 
        data_object.to_leveldb(self.world_database)




def Get_World_Edtion(path:str) -> Literal["Bedrock", "Netease", None] :
    """
    获取文件路径对应的存档类型
    * 返回 "Bedrock" : 世界是基岩版世界
    * 返回 "Netease" : 世界是网易版世界
    * 返回 None : 此存档并不是世界存档
    """
    if not is_file(os.path.join(path, "level.dat")) : return None
    if not is_file(os.path.join(path, "db", "CURRENT")) : return None

    with open(os.path.join(path, "db", "CURRENT"), "rb") as _file :
        byte1 = _file.read(4)
        if byte1 == Encrypt_Header : return "Netease"
        else : return "Bedrock"

def Read_Bedrock_World(path:str) :
    return Bedrock_Edtion_World(path)

def Read_Netease_World(path:str) :
    CURRENT = open(os.path.join(path, "db", "CURRENT"), "rb")
    KeyBytes = CURRENT.read(12) ; CURRENT.close()
    if KeyBytes[0:4] != Encrypt_Header : raise Exception("该世界不是网易基岩版世界存档")
    SECRET_KEY = bytes( (i^j for i,j in zip(b"MANIFEST", KeyBytes[4:])) )

    source_dir = os.path.join(path, "db")
    bak_dir = os.path.join(path, "__db__")
    if is_dir(bak_dir) : delete_all_file(bak_dir)
    os.rename(source_dir, bak_dir)
    os.makedirs(source_dir, exist_ok=True)

    for file_name in os.listdir(bak_dir) :
        if not is_file(os.path.join(bak_dir, file_name)) : continue
        with open(os.path.join(bak_dir, file_name), "rb") as READ_FILE :
            with open(os.path.join(source_dir, file_name), "wb") as WRITE_FILE :
                Header = READ_FILE.read(4)
                if Header != Encrypt_Header : 
                    WRITE_FILE.write(Header)
                    WRITE_FILE.write(READ_FILE.read())
                else :
                    CycleIter = itertools.cycle(SECRET_KEY)
                    while 1 :
                        byte1 = READ_FILE.read(1)
                        if not len(byte1) : break
                        WRITE_FILE.write( (byte1[0] ^ next(CycleIter)).to_bytes(1, "little") )

    return Bedrock_Edtion_World(path, SECRET_KEY)

