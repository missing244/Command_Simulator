from typing import Literal,Union
import leveldb,os,io,math,itertools
from ..python_nbt import read_from_nbt_file, write_to_nbt_file, TAG_Compound
from . import chunk_data as ChunkData
from . import other_data as OtherData

DataType = Literal[
    "Data3D", "Version", "SubChunkPrefix", "BlockEntity", "Entity", "PendingTicks", "RandomTicks",
    "LocalPlayer", "OnlinePlayer", "Village", "Map", "Portal", "Mobevent", "SchedulerWT", "Scoreboard",
    "Structure", "TickingArea"
]
ReturnDataType = Union[None, ChunkData.DataType, OtherData.DataType]




class BE_World :
    
    """
    我的世界基岩版存档对象
    -----------------------
    * 请注意显式调用close方法保存和释放资源
    -----------------------
    * 可用属性 world_name : 世界名
    * 可用属性 level_data : 世界文件level.dat的nbt对象
    * 可用属性 world_database : 世界文件leveldb存档
    -----------------------
    * 可用方法 leveldb_get : 根据提供的参数获取区块等数据
    * 可用方法 leveldb_set : 将提供的对象写入存档
    * 可用方法 close : 关闭并保存所有文件，释放缓存
    """

    ChunkData = {
        "Data3D":ChunkData.ChunkData3D, "Version":ChunkData.ChunkVersion, "SubChunkPrefix":ChunkData.ChunkSubChunkPrefix, 
        "BlockEntity":ChunkData.ChunkBlockEntity, "Entity":ChunkData.ChunkEntity, "PendingTicks":ChunkData.ChunkPendingTicks,
        "RandomTicks":ChunkData.ChunkRandomTicks
    }
    OtherData = {
        "LocalPlayer":OtherData.LocalPlayer, "OnlinePlayer":OtherData.OnlinePlayer, "Village":OtherData.Village, 
        "Map":OtherData.Map, "Portal":OtherData.Portal, "Mobevent":OtherData.Mobevent, "SchedulerWT":OtherData.SchedulerWT, 
        "Scoreboard":OtherData.Scoreboard, "Structure":OtherData.Structure, "TickingArea":OtherData.TickingArea,
    }

    def __init__(self, world_path:str, default_db:str="db") -> None :
        self.world_path = world_path
        if  not os.path.exists(os.path.join(self.world_path, "levelname.txt")) or \
            not os.path.isfile(os.path.join(self.world_path, "levelname.txt")) :
            self.world_name = "我的世界"
        else :
            file1 = open(os.path.join(self.world_path, "levelname.txt"), "r", encoding="utf-8")
            self.world_name = file1.read()
            file1.close()
        with open(os.path.join(self.world_path, "level.dat"), "rb") as level_dat_file :
            self.level_data_version = int.from_bytes(level_dat_file.read(4), "little")
            _ = int.from_bytes(level_dat_file.read(4), "little")
            self.level_data = read_from_nbt_file(level_dat_file, byteorder='little')
        self.world_database = leveldb.LevelDB(os.path.join(self.world_path, default_db))

    def leveldb_get(self, data_type:DataType, dimension:Literal["overworld", "nether", "the_end"]=None, 
        pos_x:Union[int, float]=None, pos_z:Union[int, float]=None) -> ReturnDataType : 
        """
        当 data_type 参数属于 BE_World.ChunkData 时， \n
        需要填写后续所有参数 \n
        返回 None 表示不存在这个数据
        """

        if data_type in self.ChunkData :
            if dimension not in {"overworld", "nether", "the_end"} : raise ValueError("dimension参数需要填写维度名")
            if not isinstance(pos_x, (float, int)) : raise ValueError("pos_x参数需要填写数值")
            if not isinstance(pos_z, (float, int)) : raise ValueError("pos_z参数需要填写数值")
            pos_x = math.floor(pos_x) // 16 ; pos_z = math.floor(pos_z) // 16
            return self.ChunkData[data_type].from_leveldb(self.world_database, dimension, pos_x, pos_z)
        elif data_type in self.OtherData :
            return self.OtherData[data_type].from_leveldb(self.world_database)

    def leveldb_set(self, data_object:DataType) : 
        data_object.to_leveldb(self.world_database)

    def close(self) :
        with open(os.path.join(self.world_path, "levelname.txt"), "w+", encoding="utf-8") as _file :
            _file.write(self.world_name)
        with open(os.path.join(self.world_path, "level.dat"), "wb") as _file :
            buffer = io.BytesIO()
            write_to_nbt_file(buffer, self.level_data, byteorder='little')
            _file.write(self.level_data_version.to_bytes(4, "little"))
            _file.write(buffer.getvalue().__len__().to_bytes(4, "little"))
            _file.write(buffer.getvalue())
            buffer.close()
        self.world_database.close()


class Netease_World(BE_World) :

    """
    我的世界网易基岩版存档对象
    -----------------------
    * 请注意显式调用close方法保存和释放资源
    -----------------------
    * 可用属性 world_name : 世界名
    * 可用属性 level_data : 世界文件level.dat的nbt对象
    * 可用属性 world_database : 世界文件leveldb存档
    -----------------------
    * 可用方法 leveldb_get : 根据提供的参数获取区块等数据
    * 可用方法 leveldb_set : 将提供的对象写入存档
    * 可用方法 close : 关闭并保存所有文件，释放缓存
    """
    Encrypt_Header = b"\x80\x1d\x30\x01"

    def __init__(self, world_path: str) -> None :
        Memory_Dir = os.path.join(world_path, "__db__")
        if os.path.exists( Memory_Dir ) and os.path.isdir( Memory_Dir ) :
            path,_,file = list(os.walk(Memory_Dir))[0]
            for file_name in file : os.remove( os.path.join(path, file_name))

        CURRENT = open(os.path.join(world_path, "db", "CURRENT"), "rb")
        KeyBytes = CURRENT.read(12) ; CURRENT.close()
        if KeyBytes[0:4] != self.Encrypt_Header : raise Exception("该世界不是网易基岩版世界存档")
        self.secret_key = [i^j for i,j in zip(b"MANIFEST", KeyBytes[4:])]
        
        path,_,file = list(os.walk( os.path.join(world_path, "db") ))[0]
        os.makedirs( Memory_Dir, exist_ok=True)
        for file_name in file :
            new_file_obj = open(os.path.join(Memory_Dir, file_name), "wb")
            file_obj = open(os.path.join(path, file_name), "rb")
            Header = file_obj.read(4)
            if Header != self.Encrypt_Header : 
                new_file_obj.write(Header)
                new_file_obj.write(file_obj.read())
                continue
            else :
                cycle_iter = itertools.cycle(self.secret_key)
                while 1 :
                    byte1 = file_obj.read(1)
                    if not len(byte1) : break
                    new_file_obj.write((byte1[0] ^ next(cycle_iter)).to_bytes(1, "little"))
            file_obj.close()
            new_file_obj.close()

        super().__init__(world_path, "__db__")

    def close(self) :
        super().close()
        
        Old_Dir = os.path.join(self.world_path, "db")
        if os.path.exists( Old_Dir ) and os.path.isdir( Old_Dir ) :
            path,dir,file = list(os.walk(Old_Dir))[0]
            for file_name in file : os.remove(os.path.join(path, file_name))

        Memory_Dir = os.path.join(self.world_path, "__db__")
        if os.path.exists( Memory_Dir ) and os.path.isdir( Memory_Dir ) :
            path,_,file = list(os.walk(Memory_Dir))[0]
            for file_name in file : 
                new_file_obj = open(os.path.join(path, file_name), "rb")
                old_file_obj = open(os.path.join(Old_Dir, file_name), "wb")
                if file_name[-4:] == ".log" : old_file_obj.write(new_file_obj.read())
                else :
                    cycle_iter = itertools.cycle(self.secret_key)
                    old_file_obj.write(self.Encrypt_Header)
                    while 1 :
                        byte1 = new_file_obj.read(1)
                        if not len(byte1) : break
                        old_file_obj.write((byte1[0] ^ next(cycle_iter)).to_bytes(1, "little"))
                new_file_obj.close() ; old_file_obj.close()



