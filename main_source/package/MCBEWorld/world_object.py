from typing import Literal,Union
import leveldb,os,io,array,itertools
from ..python_nbt import read_from_nbt_file, write_to_nbt_file, TAG_Compound
from ..file_operation import is_file, is_dir, delete_all_file, file_in_path
from . import chunk_data as ChunkData
from . import other_data as OtherData

Encrypt_Header = b"\x80\x1d\x30\x01"
DimensionType = Literal["overworld", "nether", "the_end"]


class MinecraftLevelDB(leveldb.LevelDB) :
    """
    基岩版数据库对象
    -----------------------
    * 所有get开头的方法均可使用
    * 可用方法 Chunk_Pos : 获取存档中所有的区块坐标的生成器
    * 可用方法 set_Data : 将get方法获得的数据对象重新写回存档
    """

    def __init__(self, path:str, create_if_missing: bool = False):
        super().__init__(os.path.join(path, "db"), create_if_missing)


    def Chunk_Pos(self, dimension:DimensionType) :
        operation_bytes = (43).to_bytes(1, "little", signed=False)
        if dimension == "overworld" : TestBytes = operation_bytes
        elif dimension == "nether" : TestBytes = b"".join((b"\x01\x00\x00\x00", operation_bytes))
        elif dimension == "the_end" : TestBytes = b"".join((b"\x02\x00\x00\x00", operation_bytes))

        for key in self.keys() :
            if key[8:] != TestBytes : continue
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

class BedrockWorld :
    """
    基岩版存档对象
    -----------------------
    * 请注意显式调用close方法保存和释放资源
    -----------------------
    * 可用属性 world_name : 世界名
    * 可用属性 world_data : 世界文件level.dat的nbt对象
    * 可用属性 world_db   : 世界文件leveldb数据库
    -----------------------
    * 可用方法 close : 保存世界并释放资源
    """

    def __init__(self, world_path:str) :
        if not is_file(os.path.join(world_path, "levelname.txt")) : world_name = "我的世界"
        else :
            file1 = open(os.path.join(world_path, "levelname.txt"), "r", encoding="utf-8")
            world_name = file1.read()
            file1.close()
        with open(os.path.join(world_path, "level.dat"), "rb") as level_dat_file :
            world_data_version = int.from_bytes(level_dat_file.read(4), "little")
            byte_len = int.from_bytes(level_dat_file.read(4), "little")
            world_data = read_from_nbt_file(level_dat_file.read(byte_len), byteorder='little').get_tag()

        self.__close = False
        self.__world_data_version = world_data_version
        self.world_path = world_path
        self.world_name = world_name
        self.world_data = world_data
        self.world_db = MinecraftLevelDB(self.world_path)

    def __setattr__(self, name:str, value):
        if name == "world_path" and hasattr(self, name) :
            raise RuntimeError("不允许修改world_path属性")
        elif hasattr(self, name) and not isinstance( value, type(getattr(self, name)) ) : 
            raise RuntimeError("不允许修改%s修改为类型不同的值" % name)
        else : super().__setattr__(name, value)

    def __del__(self) :
        self.close()


    def close(self) :
        if self.__close : return None

        with io.open(os.path.join(self.world_path, "levelname.txt"), "w+", encoding="utf-8") as _file :
            _file.write(self.world_name)
        buffer = io.BytesIO()
        write_to_nbt_file(buffer, self.world_data, byteorder='little')
        with io.open(os.path.join(self.world_path, "level.dat"), "wb") as _file :
            _file.write(self.__world_data_version.to_bytes(4, "little"))
            _file.write(buffer.getvalue().__len__().to_bytes(4, "little"))
            _file.write(buffer.getvalue())
            buffer.close()
        self.world_db.close()
        self.__close = True

class NeteaseWorld(BedrockWorld) :
    """
    网易版存档对象
    -----------------------
    * 请注意显式调用close方法保存和释放资源
    -----------------------
    * 可用属性 world_name  : 世界名
    * 可用属性 world_data  : 世界文件level.dat的nbt对象
    * 可用属性 world_db    : 世界文件leveldb数据库
    * 可用属性 encrypt_key : 加密密钥，如果为None则不加密
    -----------------------
    * 可用方法 close : 保存世界并释放资源
    """
    def __init__(self, world_path:str):
        with open(os.path.join(world_path, "db", "CURRENT"), "rb") as CURRENT :
            KeyBytes = CURRENT.read(12)
            if KeyBytes[0:4] != Encrypt_Header : raise Exception("该世界不是网易基岩版世界存档")
            SECRET_KEY = bytes( (i^j for i,j in zip(b"MANIFEST", KeyBytes[4:])) )

        source_dir = os.path.join(world_path, "db")
        bak_dir = os.path.join(world_path, "__db__")
        if is_dir(bak_dir) : delete_all_file(bak_dir)
        os.rename(source_dir, bak_dir)
        os.makedirs(source_dir, exist_ok=True)

        for file_name in os.listdir(bak_dir) :
            if not is_file(os.path.join(bak_dir, file_name)) : continue
            READ_FILE = open(os.path.join(bak_dir, file_name), "rb")
            WRITE_FILE = open(os.path.join(source_dir, file_name), "wb")

            Header = READ_FILE.read(4)
            if Header != Encrypt_Header : 
                WRITE_FILE.write(Header)
                WRITE_FILE.write(READ_FILE.read())
            else :
                CycleIter = itertools.cycle(SECRET_KEY)
                FileByte = READ_FILE.read()
                array1 = array.array("B", (i^j for i,j in zip(CycleIter, FileByte)) )
                array1.tofile(WRITE_FILE)
            
            READ_FILE.close()
            WRITE_FILE.close()

        self.encrypt_key = SECRET_KEY
        super().__init__(world_path)
        
    def __setattr__(self, name:str, value):
        if name == "encrypt_key" : super(BedrockWorld, self).__setattr__(name, value)
        else : super().__setattr__(name, value)

    def close(self) :
        super().close()

        if isinstance(self.encrypt_key, bytes) and len(self.encrypt_key) == 8 :
            source_dir = os.path.join(self.world_path, "db")
            for file_name in os.listdir(source_dir) :
                if not is_file(os.path.join(source_dir, file_name)) : continue
                READ_FILE =  open(os.path.join(source_dir, file_name), "rb")
                FILE_BYTES = READ_FILE.read()
                READ_FILE.close()

                WRITE_FILE = open(os.path.join(source_dir, file_name), "wb")
                WRITE_FILE.write(Encrypt_Header)
                CycleIter = itertools.cycle(self.encrypt_key)
                array1 = array.array("B", (i^j for i,j in zip(CycleIter, FILE_BYTES)) )
                array1.tofile(WRITE_FILE)
                WRITE_FILE.close()




def GetWorldEdtion(path:str) -> Literal["Bedrock", "Netease", None] :
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
