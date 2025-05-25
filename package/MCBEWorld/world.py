from typing import Literal,Union,List,Tuple
import leveldb,os,io,array,itertools,weakref,gzip,base64,json,sys
from . import nbt, GetWorldEdtion, GetWorldEncryptKey
from .C_API import cycle_xor
from . import LevelDatabase

LevelDatFileDefaultData = b'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'
Encrypt_Header = b"\x80\x1d\x30\x01"


class World :
    """
    基岩版存档对象
    -----------------------
    * 当指定路径不存在存档时自动创建
    * 数据库中提供了很多方法可修改世界数据
    * 请注意显式调用close方法保存和释放资源
    -----------------------
    * 可用属性 world_name  : 世界名(字符串)
    * 可用属性 world_nbt   : level.dat的nbt对象
    * 可用属性 world_db    : leveldb数据库
    * 可用属性 encrypt_key : leveldb数据库加密int密钥（网易使用）
    -----------------------
    * 可用方法 close : 保存世界并释放资源，传参encryption可以控制是否启用加密
    """

    def __netease_encrypt__(self, db_path:str, key:int) : 
        key_bytes = key.to_bytes(8, signed=False)
        name_list = os.listdir(db_path)
        if "CURRENT" in name_list : name_list.remove("CURRENT")
        name_list.insert(0, "CURRENT")

        for name in os.listdir(db_path) :
            path = os.path.join(db_path, path)
            if not os.path.isfile(path) : continue
            read_file = open(path, "rb")
            if read_file.read(4) == Encrypt_Header : read_file.close() ; continue
            bytes1 = read_file.read()
            read_file.close()
            with open(path, "wb") as f : 
                f.write( Encrypt_Header )
                f.write( cycle_xor(bytes1, key_bytes) )

    def __netease_decrypt__(self, db_path:str, key:int) :
        key_bytes = key.to_bytes(8, signed=False)
        name_list = os.listdir(db_path)
        if "CURRENT" in name_list : name_list.remove("CURRENT")
        name_list.append("CURRENT")

        for name in os.listdir(db_path) :
            path = os.path.join(db_path, path)
            if not os.path.isfile(path) : continue
            read_file = open(path, "rb")
            if read_file.read(4) != Encrypt_Header : read_file.close() ; continue
            bytes1 = read_file.read()
            read_file.close()
            with open(path, "wb") as f : f.write( cycle_xor(bytes1, key_bytes) )


    def __del__(self) :
        self.close()

    def __setattr__(self, name:str, value):
        if name == "world_nbt" and isinstance(self.world_nbt, (nbt.RootNBT, nbt.TAG_Compound)) : 
            raise TypeError(f"不正确的 world_nbt 类型 ({value.__class__})")
        elif name == "world_name" and isinstance(self.world_name, str) : 
            raise TypeError(f"不正确的 world_name 类型 ({value.__class__})")
        elif name == "encrypt_key" and isinstance(self.encrypt_key, int): 
            raise TypeError(f"不正确的 encrypt_key 类型 ({value.__class__})")
        elif name == "world_db" : raise RuntimeError("不允许修改 world_db 属性")
        else : 
            if name == "encrypt_key" :
                if not(0 <= value <= (2**64)-1) : raise ValueError("encrypt_key 应为非负数且不超过8字节整数最大值")
                self.__runtime_cache["encrypt_key"] = value
            super().__setattr__(name, value)

    def __init__(self, world_path:str) :
        world_dat_path = os.path.join(world_path, "level.dat")
        world_name_path = os.path.join(world_path, "levelname.txt")
        world_database_path = os.path.join(world_path, "db")
        runtime_cache_path = os.path.join(world_path, "runtime.cache")

        os.makedirs(world_path, exist_ok=True)
        os.makedirs(world_database_path, exist_ok=True)
        
        if not os.path.isfile( world_dat_path ) : 
            with open(world_dat_path, "wb") as f : f.write( gzip.decompress( base64.b64decode(LevelDatFileDefaultData) ) )
        if not os.path.isfile( world_name_path ) : 
            with open(world_name_path, "w+", encoding="utf-8") as f : f.write( "我的世界" )
        if not os.path.isfile( runtime_cache_path ) : 
            with open(runtime_cache_path, "w+", encoding="utf-8") as f : f.write( '{"encrypt_key":null}' )
        
        encrypt_key = GetWorldEncryptKey(world_path) if GetWorldEdtion(world_path) == "Netease" else None
        if encrypt_key is not None : self.__netease_decrypt__(world_database_path, encrypt_key)
        

        with open(os.path.join(world_path, "level.dat"), "rb") as level_dat_file :
            data_version = int.from_bytes(level_dat_file.read(4), "little")
            byte_len = int.from_bytes(level_dat_file.read(4), "little")
            world_nbt = nbt.read_from_nbt_file(level_dat_file.read(byte_len), byteorder='little').get_tag()


        self.__close = False
        self.__world_path = world_path
        self.__data_version = data_version
        with open(runtime_cache_path, "rb") as f : self.__runtime_cache = json.load(fp=f)
        if self.__runtime_cache["encrypt_key"] is None and encrypt_key is None : self.__runtime_cache["encrypt_key"] = None
        if self.__runtime_cache["encrypt_key"] is not None and encrypt_key is None : pass
        if self.__runtime_cache["encrypt_key"] is None and encrypt_key is not None : self.__runtime_cache["encrypt_key"] = encrypt_key
        if self.__runtime_cache["encrypt_key"] is not None and encrypt_key is not None : self.__runtime_cache["encrypt_key"] = encrypt_key
        with open(runtime_cache_path, "w", encoding="utf-8") as f : json.dump(self.__runtime_cache, fp=f)

        with open(world_name_path, "r", encoding="utf-8") as f : self.world_name = f.read()
        self.encrypt_key = self.__runtime_cache["encrypt_key"]
        self.world_nbt = world_nbt
        self.world_db = LevelDatabase.MinecraftLevelDB(world_database_path)


    def close(self, encryption=True) :
        if self.__close or sys.is_finalizing() : return None

        world_dat_path = os.path.join(self.__world_path, "level.dat")
        world_name_path = os.path.join(self.__world_path, "levelname.txt")
        world_database_path = os.path.join(self.__world_path, "db")
        runtime_cache_path = os.path.join(self.__world_path, "runtime.cache")

        with open(runtime_cache_path, "w+", encoding="utf-8") as _file : json.dump(self.__runtime_cache, fp=_file)
        with open(world_name_path, "w+", encoding="utf-8") as _file : _file.write(self.world_name)
        _buffer = io.BytesIO()
        nbt.write_to_nbt_file(buffer, self.world_nbt, byteorder='little')
        buffer = _buffer.getvalue()
        _buffer.close()
        with io.open(world_dat_path, "wb") as _file :
            _file.write(self.__data_version.to_bytes(4, "little"))
            _file.write(buffer.__len__().to_bytes(4, "little"))
            _file.write(buffer)
        self.world_db.close()
        if encryption and self.encrypt_key is not None : 
            self.__netease_encrypt__(world_database_path, self.encrypt_key)

        self.__close = True













