from .. import nbt
from ..C_API import chunk_parser, chunk_serialize
from . import ModifyError, ValueError
from typing import Tuple,List,Union,Dict,Literal,Optional
import types, ctypes, math, traceback, array, io, random
from . import BlockPermutationType

DefaultChunkData = b'\x01\x00\x02\x00\x02\x00\x02\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' * 256
DefaultChunkPalette = [BlockPermutationType("air"), BlockPermutationType("bedrock", {"infiniburn_bit":False}),
    BlockPermutationType("dirt", {"dirt_type":"normal"}), BlockPermutationType("grass")]


def GenerateChunkLevelDBKey(dimension:int, chunk_pos_x:int, chunk_pos_z:int, operation_id:int=None) :
    chunk_x_bytes = chunk_pos_x.to_bytes(4, "little", signed=True)
    chunk_z_bytes = chunk_pos_z.to_bytes(4, "little", signed=True)
    dimension_bytes = dimension.to_bytes(4, "little", signed=True)
    operation_bytes = operation_id.to_bytes(1, "little", signed=False) if operation_id is not None else b""
    if dimension : return b"".join((chunk_x_bytes, chunk_z_bytes, dimension_bytes, operation_bytes))
    else : return b"".join((chunk_x_bytes, chunk_z_bytes, dimension_bytes, operation_bytes))


class SubChunkType :
    """
    ## 子区块类
    * 属性**Version**               : 区块数据格式版本 **(int)** 
    * 属性**BlockIndex**            : 区块高度数组 **(array.array[int])**
    * 属性**BlockPalette**          : 区块生物群系 **(List[BlockPermutationType])**
    * 属性**ContainBlockIndex**     : 区块方块信息 **(array.array[int])**
    * 属性**BlockBlockPalette**     : 区块实体列表 **(List[BlockPermutationType])**
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_bytes** : 通过bytes生成对象
    * 可用方法**to_bytes** : 通过对象生成bytes
    """

    def __str__(self) :
        return "<SubChunk Version='%s' Pointer=%s>" % ( self.Version, hex(id(self)).upper() )
    
    def __repr__(self) :
        return self.__str__()

    def __setattr__(self, name:str, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        else : raise ModifyError("不允许修改%s属性" % name)

    def __delattr__(self, name) :
        raise ModifyError("不允许删除%s属性" % name)
    

    def __init__(self) :
        self.Version:int = 9
        self.BlockIndex = array.array("H", b"\x00\x00"*4096)
        self.BlockPalette:List[BlockPermutationType] = [BlockPermutationType("air")]
        self.ContainBlockIndex = array.array("H", b"\x00\x00"*4096)
        self.ContainBlockPalette:List[BlockPermutationType] = [BlockPermutationType("air")]


    @classmethod
    def from_bytes(cls, bytes_io: Union[bytes, io.IOBase]) :
        if isinstance(bytes_io, bytes) : bytes_io = io.BytesIO(bytes_io)
        if not isinstance(bytes_io, io.BufferedIOBase) : raise TypeError("传参需要bytes或BufferedIO类")

        ChunkObject = cls()
        sub_layers = bytes_io.read(3)[1]
        LayersName = [("BlockIndex", "BlockPalette"), ("ContainBlockIndex", "ContainBlockPalette")]
        for i in range(sub_layers) :
            block_use_bit = bytes_io.read(1)[0] >> 1  # 字节使用的bit位数
            if not block_use_bit : continue
            block_count_save_in_4bytes = 32 // block_use_bit # 4个字节能存储多少索引
            read_items = math.ceil(4096 / block_count_save_in_4bytes) # 一共需要多少个int型
            block_index_bytes = bytes_io.read(read_items*4)
            if len(block_index_bytes) != read_items*4 : raise RuntimeError("区块数据不完整")
            chunk_parser(block_index_bytes, getattr(ChunkObject, LayersName[i][0]), block_use_bit) #解析方块索引

            block_count = int.from_bytes(bytes_io.read(4), "little")
            BlockList = getattr(ChunkObject, LayersName[i][1])
            BlockList.clear()
            for j in range(block_count) : BlockList.append( 
                BlockPermutationType.from_nbt( nbt.read_from_nbt_file(bytes_io, byteorder="little").get_tag() ) )

        return ChunkObject

    def to_bytes(self, layer_id:int) :
        BytesIO_1 = io.BytesIO()
        BytesIO_1.write( self.Version.to_bytes(1, "little") )
        BytesIO_1.write( b"\x02" )
        BytesIO_1.write( layer_id.to_bytes(1, "little", signed=True) )
        
        LayersName = [("BlockIndex", "BlockPalette"), ("ContainBlockIndex", "ContainBlockPalette")]
        for i,j in LayersName :
            IndexList:array.array = getattr(self, i)
            BlockList:List[BlockPermutationType] = getattr(self, j)

            block_count = len(BlockList)
            block_use_bit = math.ceil(math.log2(block_count))
            BytesIO_1.write( (block_use_bit << 1).to_bytes(1, "little") )
            BytesIO_1.write( chunk_serialize(IndexList, block_count) )

            BytesIO_1.write( block_count.to_bytes(4, "little") )
            for block in BlockList : nbt.write_to_nbt_file(BytesIO_1, block.to_nbt(), byteorder="little")

        return BytesIO_1.getvalue()

class ChunkType :
    """
    ## 基岩版区块类
    * 属性**Version**           : 区块数据格式版本 **(int)**
    * 属性**SubChunks**         : 区块方块信息 **(Dict[str, Union[str, bool, int]])**
    * 属性**Entities**          : 区块实体列表 **(Dict[bytes, EntityType])**
    * 属性**BlockEntities**     : 区块方块实体列表 **(List[BlockNbtType])**
    * 属性**PendingTicks**      : 区块等待刻信息 **(List[nbt.TAG_Compound])**
    * 属性**RandomTicks**       : 区块随机刻信息 **(List[nbt.TAG_Compound])**
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_bytes** : 通过bytes生成对象
    * 可用方法**to_bytes** : 通过对象生成bytes
    """

    def __str__(self) :
        return "<Chunk Version='%s' Pointer=%s>" % (self.Version, hex(id(self)))
    
    def __repr__(self) :
        return self.__str__()

    def __setattr__(self, name:str, value) :
        if name == "Version" and isinstance(value, int) : super().__setattr__(name, value)
        elif not hasattr(self, name) : super().__setattr__(name, value)
        else : raise ModifyError("不允许修改%s属性" % name)

    def __delattr__(self, name) :
        raise ModifyError("不允许删除%s属性" % name)
        

    def __init__(self) :
        from . import EntityType, ItemEntityType, MobType, BlockNbtType
        self.Version:int = 41
        self.SubChunks:Dict[int, SubChunkType] = {}
        self.Entities:List[Union[EntityType, ItemEntityType, MobType]] =  {}
        self.BlockEntities:List[BlockNbtType] = []
        self.PendingTicks:List[nbt.TAG_Compound] = []
        self.RandomTicks:List[nbt.TAG_Compound] = []


    @classmethod
    def from_leveldb(cls, minecraft_leveldb, dimension:int, chunk_pos_x:int, chunk_pos_z:int) :
        from . import NBTtoEntity, BlockNbtType

        ChunkObject = cls()
        LevelDBKey = GenerateChunkLevelDBKey(dimension, chunk_pos_x, chunk_pos_z)

        #获取区块数据版本
        try : ChunkObject.Version = int.from_bytes( minecraft_leveldb.get( LevelDBKey+b',' ), "little" )
        except : pass
        #获取区块方块数据
        ChunkByteHeader = LevelDBKey + b'/'
        for layer_id in range(-128, 128) : 
            chunk_key = b"%s%s" % (ChunkByteHeader, layer_id.to_bytes(1, "little", signed=True))
            try : SubChunk = SubChunkType.from_bytes( minecraft_leveldb.get(chunk_key) )
            except : continue
            else : ChunkObject.SubChunks[layer_id] = SubChunk
        #获取区块实体数据
        EntityIndexKey = b"digp" + LevelDBKey
        try :
            EntityIndexData = io.BytesIO( minecraft_leveldb.get(EntityIndexKey) )
            for i in range(0, len( EntityIndexData.getbuffer() ), 8) :
                byte_index = EntityIndexData.read(8)
                EntityKey = b"actorprefix%s" % byte_index
                try : EntityObj = NBTtoEntity( minecraft_leveldb.get(EntityKey) )
                except : continue
                else : 
                    if not EntityObj : continue
                    ChunkObject.Entities.append(EntityObj)
        except : pass
        #获取区块方块实体
        NBtData = minecraft_leveldb.get( LevelDBKey+b"1" )
        NBtDataLength = len(NBtData)
        buffer = io.BytesIO(NBtData)
        while buffer.tell() < NBtDataLength : 
            try : BlockNBT = BlockNbtType.from_nbt(nbt.read_from_nbt_file(buffer, byteorder="little").get_tag())
            except : continue
            else : 
                if BlockNBT : ChunkObject.BlockEntities.append( BlockNBT )
        buffer.close()
        #获取区块计划刻、随机刻数据
        KeyIter = {b'3':"PendingTicks", b':':"RandomTicks"}
        for keybytes, propertyID in KeyIter.items() :
            try :
                NBtData = minecraft_leveldb.get( LevelDBKey+keybytes )
                NBtDataLength = len(NBtData)
                buffer = io.BytesIO(NBtData)
                PropertyObject = getattr(ChunkObject, propertyID)
                while buffer.tell() < NBtDataLength : PropertyObject.append( 
                    nbt.read_from_nbt_file(buffer, byteorder="little").get_tag() )
                buffer.close()
            except : pass

        return ChunkObject

    def to_leveldb(self, minecraft_leveldb, dimension:int, chunk_pos_x:int, chunk_pos_z:int,
        *, IncludeEntity=False) :
        #from ..C_leveldb import LevelDB
        #minecraft_leveldb: LevelDB = LevelDB

        LevelDBKey = GenerateChunkLevelDBKey(dimension, chunk_pos_x, chunk_pos_z)
        #设置区块数据版本
        minecraft_leveldb.put(LevelDBKey+b',', self.Version.to_bytes(1, "little"))
        minecraft_leveldb.put(LevelDBKey+b'6', b"\x02\x00\x00\x00")
        #设置区块计划刻、随机刻数据
        KeyIter = {b'3':"PendingTicks", b':':"RandomTicks"}
        for keybytes, propertyID in KeyIter.items() :
            buffer = io.BytesIO()
            PropertyObject = getattr(self, propertyID)
            for NBT in PropertyObject : 
                try : nbt.write_to_nbt_file(buffer, NBT, byteorder="little")
                except : pass
            minecraft_leveldb.put( LevelDBKey+keybytes, buffer.getvalue() )
            buffer.close()
        #设置方块实体
        buffer = io.BytesIO()
        for BlockObj in self.BlockEntities : 
            BlockObjNBT = BlockObj.to_nbt()
            BlockObjNBT["x"] = nbt.TAG_Int((BlockObjNBT["x"] % 16) + chunk_pos_x * 16)
            BlockObjNBT["z"] = nbt.TAG_Int((BlockObjNBT["z"] % 16) + chunk_pos_z * 16)
            try : nbt.write_to_nbt_file(buffer, BlockObjNBT, byteorder="little")
            except : pass
        minecraft_leveldb.put( LevelDBKey+b"1", buffer.getvalue() )
        buffer.close()
        #设置区块实体
        if IncludeEntity :
            EntityIndexKey = b"digp" + LevelDBKey
            EntityIndex = io.BytesIO()
            for Entity in self.Entities :
                EntityBytes = io.BytesIO()
                EntityNBT = Entity.to_nbt()
                index_1 = (-(EntityNBT["UniqueID"].value >> 32)).to_bytes(4, "big")
                index_2 = (EntityNBT["UniqueID"].value & 0xffffffff).to_bytes(4, "big")
                byte_index = b"%s%s" % (index_1, index_2)
                EntityNBT["Pos"][0] = nbt.TAG_Float( (EntityNBT["Pos"][0] % 16) + chunk_pos_x * 16 )
                EntityNBT["Pos"][2] = nbt.TAG_Float( (EntityNBT["Pos"][2] % 16) + chunk_pos_z * 16 )
                nbt.write_to_nbt_file(EntityBytes, EntityNBT, byteorder="little")
                EntityKey = b"actorprefix%s" % byte_index
                minecraft_leveldb.put(EntityKey, EntityBytes.getvalue())
                EntityBytes.close()
                EntityIndex.write(byte_index)
            minecraft_leveldb.put(EntityIndexKey, EntityIndex.getvalue())
            EntityIndex.close()
        #设置区块方块
        ChunkByteHeader = LevelDBKey + b'/'
        for layer_id, chunk in self.SubChunks.items() : 
            chunk_key = b"%s%s" % (ChunkByteHeader, layer_id.to_bytes(1, "little", signed=True))
            try : SubChunkData = chunk.to_bytes( layer_id )
            except : continue
            else : minecraft_leveldb.put(chunk_key, SubChunkData)



