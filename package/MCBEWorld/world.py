from typing import Literal,Union,List,Dict,Tuple,Iterable
import os,io,gzip,base64,json,sys,array,time
from . import nbt, BaseType
from . import C_API
from .C_leveldb import LevelDB as MinecraftLevelDB

LevelDatFileDefaultData = b'H4sIAF2d12gC/31Wz29bRRCejZNiOz+bphQJKUK+IKGoKC2qqkg9EJdUFU4TJaEtIGSt31vbq+x7+9jd58RUFRcOPXDhAAfEH8KVezkj9YzohSMSByTCN++9xGnVYsmWZ3Z2duab+Wa3QUTPG0RNovo8bWqbqJ2Rck7HikgsU1ulQbltmfkDu+P0QKckVqlt0752iYp3jQx965KOjQ5VDHWAPdWadFv3+zrKTRgLnFBfpC1YPrDOxB05Vs7/RY9aPT6tq+PWxvpaq2fgomuKxdbG548qRSoT1dpoJTpVkZP9sNFTscNCa60V2TwN2Pt47bXGsXZhYnntfywHTnp/3ukXay2VRjbW6aALQLy2aWvjxlrLB5dHIXeqa7MAJYJNc2PWWkec3MS0Vf27mlkfuuvd9Zutx00xT1vWReoOjj8YZ4pqdTr9zzjVGnRHpcrJYN0U47ZEd9MRILVufL/09watX12/efX6NTFHnQ/vbTor40j6IFCs8/LdohRiukkdSLsMbFz76bchsdsGddRImXs4eo7+ePLd8x+/+f3nH55//23tEnV0ooOKi1qVFX/Ie1658unJ169Z+Yz3NFZpW6c6yZO2TTIZdM+ottGIq0qmNgMrTnwZ31WafMQibaN5dFY0BEMkxOWXVVWKtVm6p8JQuf1IGlXnWBdYg4IcVuf8jTMA9Wm3MrS1K2fiS5jVsArY9mQa22Rfqfjjjvjg2bN/rosl2s/kUXp//b42Rg7gm2oXSl2JUSWUsFRCgQQi2kcRsaeKqMGHTNOBTtSTS2XOtTkqAKwsin5YpoebnVfE12yQ7Gmjg1ZeNEmGIKPDxPa8QIuVUokTFDPUy7WJBcKPrXUeefkjHaIhts7UqW/G+xmy/PVp55a4wCJanuBUpz7IYiuh13Q6yg23JmpIokFGD4YhLUwvUCLH2EdimphRQkyRzUgs4Jc5lAYJLUKpLVGmXKI95+eLFiwSf5PKYHdfWmQIRJ2CMiqzLtBMg46kOazCfXqL50pP+oJOZ6i9Jy5Sz6a5byPB8FHKASOD88qiLqxcpsgmCQAppoLNQ5aDSCsvaL0qXQj0ZKX3lVcxPUtR7hyKcqCjw1/EWfPGNpbjAqJoHDFg81DBTIcxxleGqjShwAxVARs5kNjqBANVS4xb5TnA0gZVsEmqpQDm6EeLmGwQhT+uNxsWRZiFImijKvcLEI+UZFpUEUDjbGEcywSNKEAIFec7/b5yRdRvsRhJHmpb2IkRd5onNWdJHaN06NY0eDDxnNRFpVw394znKnk5UnEX7TXsBjsYYHP3nC1xX/WlMVUILAGDU2mO+k6pr07l2gr18zTigCrgDc+ZpXfh5goNpd9UKu2AGyq+m7YdYtajYk5gqbyQNtVQjrR1u5JBPrewp7zNMYjLhQUC9nngXAsGElpA+y1nq3vtQCVo0AAQL1X6wmyiXoJ6H8ga9Yk/dfE2dC+Y7RT3RemRG+JQqUyfTnfRuEwGFN8BYzBIgd+rRuQ7+E5VI3JmYcLBCZXmJ0qeLTfen6LaRTLn5vNtlYXhEtu+qH+g40p/GXw+rhCPhuCuUekgDE9OiNsMXTdwWvVxggAeKXeKNE4NyouLOVifpgwvCJjXKBtlzFsHN5Mo64XMAco/BdUWIfKwZS54JndB/FVy6ssc7eHbNtN4a6BWeyqxI2nAYq7bClVUqYh6nBkbK44KpI2rDPrw18NWbievHJq1PczTQyYsRvxATfNZS+SH9qhnXQz2gRFRYLqzLsLIxCMA9QOrLhaqmHmVKO/RpFDWC2WQA88cLeLZ5kmMe6kQnIx17osyIrAgXeDy4kl1NptWMOKOmXCcot8rs44Z7ICJX2blOS2wbNtLHneOz9tJMXSnF6l4euyz5zY/X/494VLhklgoV7qZNTrCTUH0HzLTYe3vCQAA'
Encrypt_Header = b"\x80\x1d\x30\x01"

def GetWorldEdtion(path:str) :
    """
    获取文件路径对应的存档类型
    * 返回 Netease 字符串: 世界是网易版世界
    * 返回 Bedrock 字符串: 世界是基岩版世界
    * 返回 None : 此存档并不是世界存档
    """
    if not os.path.isfile(os.path.join(path, "level.dat")) : return None
    if not os.path.isfile(os.path.join(path, "db", "CURRENT")) : return None

    with open(os.path.join(path, "db", "CURRENT"), "rb") as _file :
        byte1 = _file.read(4)
        if byte1 == Encrypt_Header : return "Netease"
        else : return "Bedrock"

def GetWorldEncryptKey(path:str) :
    """
    获取文件路径对应的存档加密密钥
    * 返回 int : 此存档的数字密钥
    * 返回 None : 此存档并不是加密存档
    """
    db_file_path = os.path.join(path, "db", "CURRENT")
    if not os.path.isfile(db_file_path) : return None
    with open(db_file_path, "rb") as CURRENT :
        KeyBytes = CURRENT.read(12)
        if KeyBytes[0:4] != Encrypt_Header : return None
        SECRET_KEY = bytes( (i^j for i,j in zip(b"MANIFEST", KeyBytes[4:])) )
        return int.from_bytes(SECRET_KEY, byteorder="big")


class World :
    """
    基岩版存档对象
    -----------------------
    * 当指定路径不存在存档时自动创建
    * 数据库中提供了很多方法可修改世界数据
    * 请务必显式调用close方法保存数据并释放资源
    -----------------------
    * 可用属性 **world_name**         : 世界名字（字符串）
    * 可用属性 **world_nbt**          : level.dat的nbt对象
    * 可用属性 **world_db**           : leveldb数据库
    * 可用属性 **encrypt_key**        : leveldb数据库加密int密钥（网易使用）
    * 可用属性 **StructureManager**   : MCStructure结构管理器(BaseType.Structure)
    -----------------------
    * 可用方法 **close** : 保存世界并释放资源，传参encryption可以控制是否启用加密
    * 可用方法 **import_CommonStructure** : 通过CommonStructure对象将结构写入存档内
    * 可用方法 **export_CommonStructure** : 通过CommonStructure对象将存档写出至结构对象
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
                f.write( C_API.cycle_xor(bytes1, key_bytes) )

    def __netease_decrypt__(self, db_path:str, key:int) :
        key_bytes = key.to_bytes(8, byteorder="big", signed=False)
        name_list = os.listdir(db_path)
        if "CURRENT" in name_list : name_list.remove("CURRENT")
        name_list.append("CURRENT")

        for name in os.listdir(db_path) :
            path = os.path.join(db_path, name)
            if not os.path.isfile(path) : continue
            read_file = open(path, "rb")
            if read_file.read(4) != Encrypt_Header : read_file.close() ; continue
            bytes1 = read_file.read()
            read_file.close()
            with open(path, "wb") as f : f.write( C_API.cycle_xor(bytes1, key_bytes) )


    def __str__(self):
        return "<MCBEWorld name='%s' encrypt=%s>" % (self.world_name, bool(self.encrypt_key))

    def __del__(self) :
        self.close()

    def __setattr__(self, name:str, value):
        if name == "world_nbt" and not isinstance(value, (nbt.TAG_Compound)) : 
            raise TypeError(f"不正确的 world_nbt 类型 ({value.__class__})")
        elif name == "world_name" and not isinstance(value, str) : 
            raise TypeError(f"不正确的 world_name 类型 ({value.__class__})")
        elif name == "encrypt_key" and not isinstance(value, (int, type(None))) : 
            raise TypeError(f"不正确的 encrypt_key 类型 ({value.__class__})")
        elif name == "world_db" and hasattr(self, name) : 
            raise RuntimeError("不允许修改 world_db 属性")
        elif name == "MCStructure" and hasattr(self, name) : 
            raise RuntimeError("不允许修改 MCStructure 属性")
        else : 
            if name == "encrypt_key" and value is not None:
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

        self.encrypt_key = self.__runtime_cache["encrypt_key"]
        self.world_nbt = world_nbt
        self.world_db = MinecraftLevelDB(world_database_path, create_if_missing=True)
        self.StructureManager = BaseType.Structure(self.world_db)

    @property
    def world_name(self):
        if "LevelName" in self.world_nbt : return self.world_nbt["LevelName"].value
        else : return "我的世界"

    @world_name.setter
    def world_name(self, value:str):
        if isinstance(value, str) and len(value) > 0:
            self.world_nbt["LevelName"] = nbt.TAG_String(value)
        else: raise ValueError("世界名必须是非空字符串")
    
    def close(self, encryption=False) :
        if sys.is_finalizing() or self.__close : return None

        world_dat_path = os.path.join(self.__world_path, "level.dat")
        world_database_path = os.path.join(self.__world_path, "db")
        runtime_cache_path = os.path.join(self.__world_path, "runtime.cache")

        with open(runtime_cache_path, "w+", encoding="utf-8") as _file : json.dump(self.__runtime_cache, fp=_file)
        _buffer = io.BytesIO()
        nbt.write_to_nbt_file(_buffer, self.world_nbt, byteorder='little')
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


    def import_CommonStructure(self, CommonStructure, dimension:int, startPos:Tuple[int, int, int], CallbackFunc=None) :
        BlockPalette:List[BaseType.BlockPermutationType] = []
        SizeX, SizeY, SizeZ = CommonStructure.size
        BlockIndex:array.array = CommonStructure.block_index
        BlockNBTTable:Dict[int, nbt.TAG_Compound] = CommonStructure.block_nbt
        BlockPalette.extend(BaseType.BlockPermutationType(j.name, j.states) for j in CommonStructure.block_palette)
        MiddleArray = array.array("H", b"\x00\x00"*len(BlockPalette))
        
        if  (dimension == 0 and ( not(-64 <= startPos[1] < 320) or not(-64 <= startPos[1]+SizeY < 320) )) or \
            (dimension == 1 and ( not(0 <= startPos[1] < 256) or not(0 <= startPos[1]+SizeY < 256) )) or \
            (dimension == 2 and ( not(0 <= startPos[1] < 256) or not(0 <= startPos[1]+SizeY < 256) )) :
            raise ValueError("结构放置超出世界有效高度范围")
        
        Iter1 = C_API.StructureOperatePosRange(startPos[0], startPos[2], startPos[0]+SizeX, startPos[2]+SizeZ)
        SubChunkDict:Dict[int, BaseType.SubChunkType] = {}
        IterLen = len(Iter1)

        for processID, (x1, z1, x2, z2) in enumerate(Iter1, start=1) :
            ChunkKey = BaseType.GenerateChunkLevelDBKey(dimension, x1//16, z1//16)
            for layer in range(startPos[1]//16, (startPos[1]+SizeY-1)//16+1) :
                SubChunkKey = b"%s/%s" % (ChunkKey, layer.to_bytes(1, "little", signed=True))
                if SubChunkKey in self.world_db :
                    SubChunkData = self.world_db.get(SubChunkKey)
                    SubChunkDict[layer] = BaseType.SubChunkType.from_bytes(SubChunkData)
                elif layer != -4 : SubChunkDict[layer] = BaseType.SubChunkType()
            if startPos[1]//16 == -4 and (-4 not in SubChunkDict) : 
                SubChunkDict[-4] = BaseType.GenerateSuperflatSubChunk()
            
            C_API.import_CommonStructure_to_chunk(
                startPos[0], startPos[1], startPos[2], SizeX, SizeY, SizeZ,
                x1, startPos[1], z1, x2, startPos[1]+SizeY, z2, 
                SubChunkDict, BlockIndex, BlockPalette, MiddleArray)
            
            for layer in range(startPos[1]//16, (startPos[1]+SizeY-1)//16+1) :
                SubChunkKey = b"%s/%s" % (ChunkKey, layer.to_bytes(1, "little", signed=True))
                SubChunkData = SubChunkDict[layer].to_bytes(layer)
                self.world_db.put(SubChunkKey, SubChunkData)

            self.world_db.put(ChunkKey+b',', (41).to_bytes(1, "little"))
            self.world_db.put(ChunkKey+b'6', b"\x02\x00\x00\x00")
            SubChunkDict.clear()
            if CallbackFunc : CallbackFunc(processID, IterLen)

        NBT_IO_Cache : Dict[Tuple[int, int], io.BytesIO] = {}
        for index, BlockNBT in BlockNBTTable.items() :
            NBTPosX = (index // (SizeY * SizeZ)) + startPos[0]
            remain = index % (SizeY * SizeZ)
            NBTPosY = (remain // SizeZ) + startPos[1]
            NBTPosZ = (remain % SizeZ) + startPos[2]

            ChunkPosTuple = (NBTPosX//16, NBTPosZ//16)
            if ChunkPosTuple not in NBT_IO_Cache :
                NBT_IO_Cache[ChunkPosTuple] = io.BytesIO()
                ChunkNBTKey = BaseType.GenerateChunkLevelDBKey(dimension, ChunkPosTuple[0], ChunkPosTuple[1], 49)
                if ChunkNBTKey in self.world_db : NBT_IO_Cache[ChunkPosTuple].write( self.world_db.get(ChunkNBTKey) )

            BlockNBTCopy = BlockNBT.copy()
            BlockNBTCopy["x"] = nbt.TAG_Int(NBTPosX)
            BlockNBTCopy["y"] = nbt.TAG_Int(NBTPosY)
            BlockNBTCopy["z"] = nbt.TAG_Int(NBTPosZ)
            nbt.write_to_nbt_file(NBT_IO_Cache[ChunkPosTuple], BlockNBTCopy)
        for ChunkPos, IO1 in NBT_IO_Cache.items() :
            ChunkNBTKey = BaseType.GenerateChunkLevelDBKey(dimension, ChunkPos[0], ChunkPos[1], 49)
            self.world_db.put(ChunkNBTKey, IO1.getvalue())
            IO1.close()

        if "common_structure_range" not in self.__runtime_cache : 
            self.__runtime_cache["common_structure_range"] = {}
        LocalTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.__runtime_cache["common_structure_range"][LocalTime] = [startPos[0], startPos[1], 
            startPos[2], startPos[0]+SizeX, startPos[1]+SizeY, startPos[2]+SizeZ]
        with open(os.path.join(self.__world_path, "runtime.cache"), "w", encoding="utf-8") as f : 
            json.dump(self.__runtime_cache, fp=f)

    def export_CommonStructure(self, CommonStructure, dimension:int, startPos:Tuple[int, int, int], endPos:Tuple[int, int, int],
        CallbackFunc=None) :
        if  (dimension == 0 and ( not(-64 <= startPos[1] < 320) or not(-64 <= endPos[1] < 320) )) or \
            (dimension == 1 and ( not(0 <= startPos[1] < 256) or not(0 <= endPos[1] < 256) )) or \
            (dimension == 2 and ( not(0 <= startPos[1] < 256) or not(0 <= endPos[1] < 256) )) :
            raise ValueError("结构读取区域超出世界有效高度范围")

        startPos, endPos = list(startPos), list(endPos)
        for i,j,k in zip(range(3), startPos, endPos) :
            if j > k : startPos[i], endPos[i] = endPos[i], startPos[i]

        CommonStructure.__init__([j-i+1 for i,j in zip(startPos, endPos)])
        SizeX, SizeY, SizeZ = CommonStructure.size
        BlockIndex:array.array = CommonStructure.block_index
        BlockPalette:Dict[int, nbt.TAG_Compound] = CommonStructure.block_palette
        BlockNBTDict:Dict[int, nbt.TAG_Compound] = CommonStructure.block_nbt
        MiddleArray = array.array("H", b"\x00\x00"*32767)

        BlockPaletteMiddleList:List[BaseType.BlockPermutationType] = [BaseType.BlockPermutationType("air")]
        Iter1 = C_API.StructureOperatePosRange(startPos[0], startPos[2], endPos[0]+1, endPos[2]+1)
        IterLen = len(Iter1)
        for processID, (x1, z1, x2, z2) in enumerate(Iter1, start=1) :
            ChunkObj = BaseType.ChunkType.from_leveldb(self.world_db, dimension, x1//16, z1//16)
            C_API.export_chunk_to_CommonStructure(
                startPos[0], startPos[1], startPos[2], SizeX, SizeY, SizeZ, 
                x1, startPos[1], z1, x2, endPos[1]+1, z2,
                ChunkObj.SubChunks, BlockIndex, BlockPaletteMiddleList, MiddleArray)

            for BlockNBT in ChunkObj.BlockEntities :
                if  not(startPos[0] <= BlockNBT.x <= endPos[0]) or \
                    not(startPos[1] <= BlockNBT.y <= endPos[1]) or \
                    not(startPos[2] <= BlockNBT.z <= endPos[2]) : continue
                NBTPointer = (BlockNBT.x - startPos[0]) * (SizeY * SizeZ) + \
                    (BlockNBT.y - startPos[1]) * SizeZ + (BlockNBT.z - startPos[2])
                BlockNBTDict[NBTPointer] = BlockNBT.to_nbt()
            if CallbackFunc : CallbackFunc(processID, IterLen)
        
        BlockPalette.extend(CommonStructure.BLOCKTYPE(j.Identifier, j.States) for j in BlockPaletteMiddleList)


    def chunk_pos_iter(self, dimension:int) -> Iterable[Tuple[int, int]] :
        for key_bytes in self.world_db.keys() :
            Test1 = C_API.is_chunk_key(key_bytes, dimension)
            if Test1 : yield Test1
    
    def chunk_exists(self, dimension:int, chunk_pos_x:int, chunk_pos_z:int) -> bool :
        key = BaseType.GenerateChunkLevelDBKey(dimension, chunk_pos_x, chunk_pos_z, 44)
        return key in self.world_db

    def get_chunk(self, dimension:int, chunk_pos_x:int, chunk_pos_z:int) -> Union[BaseType.ChunkType, None] : 
        if not self.chunk_exists(dimension, chunk_pos_x, chunk_pos_z) : return None
        return BaseType.ChunkType.from_leveldb(self.world_db, dimension, chunk_pos_x, chunk_pos_z)







