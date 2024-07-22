from ..python_nbt import read_from_nbt_file, write_to_nbt_file
from typing import Literal,Union
import leveldb,os,io,math
DataType = Literal[
    "Data3D", "Version", "SubChunkPrefix", "BlockEntity", "Entity", "PendingTicks", "RandomTicks",
    "LocalPlayer", "OnlinePlayer", "Villages", "Maps", "Portals", "SchedulerWT", "StructureTemplate", "TickingArea"
]

class BE_World :
    
    """
    我的世界基岩版存档对象
    -----------------------
    * 可用属性 world_name : 世界名
    * 可用属性 level_data : 世界文件level.dat的nbt对象
    * 可用属性 world_database : 世界文件leveldb存档
    -----------------------
    * 可用方法 leveldb_get : 
    * 可用方法 close : 关闭并保存所有文件，释放缓存
    """

    ChunkData = {"Data3D", "Version", "SubChunkPrefix", "BlockEntity", "Entity", "PendingTicks", "RandomTicks"}
    OtherData = {"LocalPlayer", "OnlinePlayer", "Villages", "Maps", "Portals", "SchedulerWT", "StructureTemplate", "TickingArea"}

    def __init__(self, world_path:str) -> None :
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
        self.world_database = leveldb.LevelDB(os.path.join(self.world_path, "db"))

    def leveldb_get(self, data_type:DataType, dimension:Literal["Overworld", "Nether", "TheEnd"]=None, 
        pos_x:Union[int, float]=None, pos_z:Union[int, float]=None) : 
        if data_type in self.ChunkData :
            if dimension not in {"Overworld", "Nether", "TheEnd"} : raise ValueError("dimension参数需要填写维度名")
            if not isinstance(pos_x, (float, int)) : raise ValueError("pos_x参数需要填写数值")
            if not isinstance(pos_z, (float, int)) : raise ValueError("pos_z参数需要填写数值")
            pos_x = math.floor(pos_x) // 16 ; pos_z = math.floor(pos_z) // 16

    def leveldb_set(self, data_object:DataType) : pass

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









