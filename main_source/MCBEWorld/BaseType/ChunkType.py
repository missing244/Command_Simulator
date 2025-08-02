from .. import nbt
from ..C_API import chunk_parser, chunk_serialize
from . import ModifyError, ValueError
from typing import Tuple,List,Union,Dict,Literal,Optional
import types, ctypes, math, traceback, array, io




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
        from . import BlockPermutationType
        self.Version:int = 9
        self.BlockIndex = array.array("H", b"\x00\x00"*4096)
        self.BlockPalette:List[BlockPermutationType] = [BlockPermutationType("air")]
        self.ContainBlockIndex = array.array("H", b"\x00\x00"*4096)
        self.ContainBlockPalette:List[BlockPermutationType] = [BlockPermutationType("air")]


    @classmethod
    def from_bytes(cls, bytes_io: Union[bytes, io.IOBase]) :
        from . import BlockPermutationType
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
            block_index = chunk_parser(bytes_io.read(read_items*4), block_use_bit) #解析方块索引
            IndexList = getattr(ChunkObject, LayersName[i][0])
            IndexList[0:4096] = array.array("H", block_index)
            
            block_count = int.from_bytes(bytes_io.read(4), "little")
            BlockList = getattr(ChunkObject, LayersName[i][1])
            BlockList.clear()
            for j in range(block_count) : BlockList.append( 
                BlockPermutationType.from_nbt( nbt.read_from_nbt_file(bytes_io, byteorder="little").get_tag() ) )

        return ChunkObject

    def to_bytes(self, layer_id:int) :
        from . import BlockPermutationType
        BytesIO_1 = io.BytesIO()
        BytesIO_1.write( self.Version.to_bytes(1, "little") )
        BytesIO_1.write( b"\x02" )
        BytesIO_1.write( layer_id.to_bytes(1, "little", True) )
        
        LayersName = [("BlockIndex", "BlockPalette"), ("ContainBlockIndex", "ContainBlockPalette")]
        for i,j in LayersName :
            IndexList:array.array = getattr(self, LayersName[i])
            BlockList:List[BlockPermutationType] = getattr(self, LayersName[j])

            block_count = len(BlockList)
            block_use_bit = bin( block_count ).__len__() - 2
            BytesIO_1.write( (block_use_bit << 1).to_bytes(1, "little") )
            BytesIO_1.write( chunk_serialize(IndexList.tolist(), block_count) )

            BytesIO_1.write( block_count.to_bytes(4, "little") )
            for block in BlockList : nbt.write_to_nbt_file(BytesIO_1, block.to_nbt(), byteorder="little")

        return BytesIO_1.getvalue()


class ChunkType :
    """
    ## 基岩版区块类
    * 属性**Version**           : 区块数据格式版本 **(int)**
    * 属性**Biomepalette**      : 区块生物群系 **(bytes)暂时**
    * 属性**SubChunks**         : 区块方块信息 **(Dict[str, Union[str, bool, int]])**
    * 属性**Entities**          : 区块实体列表 **(List[EntityType])**
    * 属性**BlockEntities**     : 区块方块实体列表 **(List[BlockNbtType])**
    * 属性**PendingTicks**      : 区块等待刻信息 **(nbt.)**
    * 属性**RandomTicks**       : 区块随机刻信息 **(Dict[str, Union[str, bool, int]])**
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_bytes** : 通过bytes生成对象
    * 可用方法**to_bytes** : 通过对象生成bytes
    """

    def __str__(self) :
        return "<Chunk Version='%s' Pointer=%s>" % (self.Version, hex(id(self)))
    
    def __repr__(self) :
        return self.__str__()

    def __setattr__(self, name:str, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        else : raise ModifyError("不允许修改%s属性" % name)

    def __delattr__(self, name) :
        raise ModifyError("不允许删除%s属性" % name)
        

    def __init__(self) :
        from . import EntityType, ItemEntityType, MobType, BlockNbtType
        self.Version:int = 41
        self.Biomepalette:bytes = b'\x01\x01\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        self.SubChunks:Dict[int, SubChunkType] = {}
        self.Entities:List[EntityType, ItemEntityType, MobType] =  []
        self.BlockEntities:List[BlockNbtType] = []
        self.PendingTicks:nbt.TAG_Compound = nbt.TAG_Compound()
        self.RandomTicks:nbt.TAG_Compound = nbt.TAG_Compound()
    



