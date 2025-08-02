from .. import nbt
from ..C_API import chunk_parser
from .. import C_leveldb as leveldb
from typing import Literal,List,Union,Dict,TypedDict,Tuple
import itertools, functools, io, traceback, math, array

class SUBCHUNK(TypedDict) :
    block_index: List[int]
    blocks: List[nbt.TAG_Compound]
    contain_index: List[int]
    contains: List[nbt.TAG_Compound]

def generate_chunk_key(dimension:Literal["overworld", "nether", "the_end"], 
    chunk_pos_x:int, chunk_pos_z:int, operation_id:int=None) :
    chunk_x_bytes = chunk_pos_x.to_bytes(4, "little", signed=True)
    chunk_z_bytes = chunk_pos_z.to_bytes(4, "little", signed=True)
    operation_bytes = operation_id.to_bytes(1, "little", signed=False) if operation_id is not None else b""
    if dimension == "overworld" : return b"".join((chunk_x_bytes, chunk_z_bytes, operation_bytes))
    elif dimension == "nether" : return b"".join((chunk_x_bytes, chunk_z_bytes, b"\x01\x00\x00\x00", operation_bytes))
    elif dimension == "the_end" : return b"".join((chunk_x_bytes, chunk_z_bytes, b"\x02\x00\x00\x00", operation_bytes))



class Data3D :
    """
    高度图 + 生物群系调色板
    -----------------------
    * 可用属性 chunk_x : 区块x坐标
    * 可用属性 chunk_z : 区块z坐标
    * 可用属性 dimension : 区块所处的维度
    * 可用属性 heightmap : 区块内的16*16区域的地表高度
    * 可用属性 biomepalette : 区块内的3d生物群系信息(由于无法解析暂时以字节数组储存)
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    operation_id = 43
    
    def __init__(self, x:int, z:int, dimension:Literal["overworld", "nether", "the_end"], 
        Heightmap:List[int], Biomepalette:bytes) -> None:
        self.chunk_x = x
        self.chunk_z = z
        self.dimension = dimension
        self.heightmap = Heightmap
        self.biomepalette = Biomepalette 

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB, dimension:Literal["overworld", "nether", "the_end"], 
        chunk_pos_x:int, chunk_pos_z:int) :
        key = generate_chunk_key(dimension, chunk_pos_x, chunk_pos_z, cls.operation_id)
        try : value = io.BytesIO(leveldb.get(key))
        except : return None

        heightmap = list(array.array("H", value.read(512)))
        Biomepalette = value.read()
        return cls(chunk_pos_x, chunk_pos_z, dimension, heightmap, Biomepalette)

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        key = generate_chunk_key(self.dimension, self.chunk_x, self.chunk_z, self.operation_id)
        leveldb.put(key, b"".join([
            b"".join(i.to_bytes(2, "little") for i in self.heightmap),
            self.biomepalette
        ]))

class Version :
    """
    数据格式版本
    -----------------------
    * 可用属性 chunk_x : 区块x坐标
    * 可用属性 chunk_z : 区块z坐标
    * 可用属性 dimension : 区块所处的维度
    * 可用属性 version : 区块的数据格式版本，用于游戏内自动升级
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    operation_id = 44

    def __init__(self, x:int, z:int, dimension:Literal["overworld", "nether", "the_end"], version:int) -> None:
        self.chunk_x = x
        self.chunk_z = z
        self.dimension = dimension
        self.version = version

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB, dimension:Literal["overworld", "nether", "the_end"], 
        chunk_pos_x:int, chunk_pos_z:int) :
        key = generate_chunk_key(dimension, chunk_pos_x, chunk_pos_z, cls.operation_id)
        try : value = leveldb.get(key)
        except : return None

        version = int.from_bytes(value, "little")
        return cls(chunk_pos_x, chunk_pos_z, dimension, version)
    
    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        key = generate_chunk_key(self.dimension, self.chunk_x, self.chunk_z, self.operation_id)
        leveldb.put(key, self.version.to_bytes(1, "little"))

class Chunks :
    """
    区块方块数据
    -----------------------
    * 可用属性 chunk_x : 区块x坐标
    * 可用属性 chunk_z : 区块z坐标
    * 可用属性 dimension : 区块所处的维度
    * 可用属性 chunk_data : 区块的方块索引数据与方块列表
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    operation_id = 47
    
    chunk_layer_key = {int.to_bytes(i, length=1, byteorder="little", 
    signed=True):i for i in range(-128, 128) }
    
    def __init__(self, x:int, z:int, dimension:Literal["overworld", "nether", "the_end"]) -> None:
        self.chunk_x = x
        self.chunk_z = z
        self.dimension = dimension
        self.chunk_data:Dict[int, List[Tuple[List[int], List[nbt.TAG_Compound]]]] = {}

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB, dimension:Literal["overworld", "nether", "the_end"], 
        chunk_pos_x:int, chunk_pos_z:int) :
        key = generate_chunk_key(dimension, chunk_pos_x, chunk_pos_z, cls.operation_id)
        Object = cls(chunk_pos_x, chunk_pos_z, dimension)

        for layer_key, layer_int in Object.chunk_layer_key.items() : 
            chunk_key = b"%s%s" % (key, layer_key)
            if chunk_key not in leveldb : continue

            chunk_bytesIO = io.BytesIO( leveldb.get(chunk_key) )
            sub_layers = chunk_bytesIO.read(3)[1]
            print(chunk_bytesIO.getvalue())

            for _ in range(sub_layers) :
                block_use_bit = chunk_bytesIO.read(1)[0] >> 1  # 字节使用的bit位数
                if not block_use_bit : break
                block_count_save_in_4bytes = 32 // block_use_bit # 4个字节能存储多少索引
                read_items = math.ceil(4096 / block_count_save_in_4bytes) # 一共需要多少个int型

                #解析方块索引
                block_index = chunk_parser(chunk_bytesIO.read(read_items * 4), block_use_bit)
                #print(block_index)

                #解析方块
                block_count = int.from_bytes(chunk_bytesIO.read(4), "little")
                blocks = [None] * block_count
                for j in range(block_count) : 
                    blocks[j] = nbt.read_from_nbt_file(chunk_bytesIO, byteorder="little").get_tag()

                if layer_int not in Object.chunk_data : Object.chunk_data[layer_int] = []
                Object.chunk_data[layer_int].append( (block_index, blocks) )

            chunk_bytesIO.close()
        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        key = generate_chunk_key(self.dimension, self.chunk_x, self.chunk_z, self.operation_id)
        func = functools.partial(int.to_bytes, length=1, byteorder="little", signed=True)
        for i, value in self.chunk_data.items() : 
            put_key = b"%s%s" % (key, func(i))
            writebuffer = io.BytesIO(b"")
            writebuffer.write(b"\x0a%s%s" % ( bytes([len(value)]), func(i) ))

            for block_index, blocks in value :
                if min(block_index) < 0 : raise IndexError("方块索引列表中存在负数索引")

                block_use_bit = bin( max(block_index) ).__len__() - 2
                block_count_save_in_4bytes = 32 // block_use_bit
                writebuffer.write( (block_use_bit << 1).to_bytes(1, "little") )

                for j in range(0, 4096, block_count_save_in_4bytes) :
                    save_int = 0
                    for k in block_index[j:j+block_count_save_in_4bytes] :
                        save_int = (save_int | k) << block_use_bit
                    writebuffer.write( (save_int >> block_use_bit).to_bytes(4, "big") )

                writebuffer.write( len(blocks).to_bytes(4, "little") )
                for block in blocks : nbt.write_to_nbt_file(writebuffer, block, byteorder="little")

            leveldb.put(put_key, writebuffer.getvalue())
            writebuffer.close()

class BlockEntity :
    """
    区块方块实体数据
    -----------------------
    * 可用属性 chunk_x : 区块x坐标
    * 可用属性 chunk_z : 区块z坐标
    * 可用属性 dimension : 区块所处的维度
    * 可用属性 block_entities : 区块的方块实体nbt对象列表
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    operation_id = 49
    
    def __init__(self, x:int, z:int, dimension:Literal["overworld", "nether", "the_end"]) -> None:
        self.chunk_x = x
        self.chunk_z = z
        self.dimension = dimension
        self.block_entities:List[nbt.TAG_Compound] = []

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB, dimension:Literal["overworld", "nether", "the_end"], 
        chunk_pos_x:int, chunk_pos_z:int) :
        key = generate_chunk_key(dimension, chunk_pos_x, chunk_pos_z, cls.operation_id)
        try : value = leveldb.get(key)
        except : return None

        Object = cls(chunk_pos_x, chunk_pos_z, dimension)

        buffer = io.BytesIO(value)
        while buffer.tell() < len(value) :
            Object.block_entities.append(nbt.read_from_nbt_file(buffer, byteorder="little").get_tag())
        buffer.close()
        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        key = generate_chunk_key(self.dimension, self.chunk_x, self.chunk_z, self.operation_id)
        buffer = io.BytesIO(b"")
        for i in self.block_entities : nbt.write_to_nbt_file(buffer, i, byteorder="little")
        leveldb.put(key, buffer.getvalue())
        buffer.close()

class Entity :
    """
    区块实体数据
    -----------------------
    * 可用属性 chunk_x : 区块x坐标
    * 可用属性 chunk_z : 区块z坐标
    * 可用属性 dimension : 区块所处的维度
    * 可用属性 entities : 区块的实体nbt对象字典
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """
    
    def __init__(self, x:int, z:int, dimension:Literal["overworld", "nether", "the_end"]) -> None:
        self.chunk_x = x
        self.chunk_z = z
        self.dimension = dimension
        self.entities:Dict[bytes, nbt.TAG_Compound] = {}

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB, dimension:Literal["overworld", "nether", "the_end"], 
        chunk_pos_x:int, chunk_pos_z:int) :
        key = generate_chunk_key(dimension, chunk_pos_x, chunk_pos_z)
        try : value = leveldb.get(b"digp%s" % key)
        except : return None

        Object = cls(chunk_pos_x, chunk_pos_z, dimension)
        for j in range(0, len(value), 8) :
            byte_index = b"actorprefix%s" % value[j:j+8]
            try : entity = nbt.read_from_nbt_file( leveldb.get(byte_index), byteorder="little" ).get_tag()
            except : continue
            else : Object.entities[byte_index] = entity
        
        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        key = generate_chunk_key(self.dimension, self.chunk_x, self.chunk_z)
        entity_index = []
        for index, entity in self.entities.items() :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, entity, byteorder="little")
            leveldb.put(index, buffer.getvalue())
            buffer.close()
            entity_index.append(index[11:])

        leveldb.put(b"digp%s" % key, b"".join(entity_index))

class PendingTicks :
    """
    区块计划事件数据
    -----------------------
    * 可用属性 chunk_x : 区块x坐标
    * 可用属性 chunk_z : 区块z坐标
    * 可用属性 dimension : 区块所处的维度
    * 可用属性 pending_ticks : 区块的计划事件nbt对象列表
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    operation_id = 51
    
    def __init__(self, x:int, z:int, dimension:Literal["overworld", "nether", "the_end"]) -> None:
        self.chunk_x = x
        self.chunk_z = z
        self.dimension = dimension
        self.pending_ticks:List[nbt.TAG_Compound] = []

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB, dimension:Literal["overworld", "nether", "the_end"], 
        chunk_pos_x:int, chunk_pos_z:int) :
        key = generate_chunk_key(dimension, chunk_pos_x, chunk_pos_z, cls.operation_id)
        try : value = leveldb.get(key)
        except : return None

        Object = cls(chunk_pos_x, chunk_pos_z, dimension)

        buffer = io.BytesIO(value)
        while buffer.tell() < len(value) :
            Object.pending_ticks.append(nbt.read_from_nbt_file(buffer, byteorder="little").get_tag())
        buffer.close()
        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        key = generate_chunk_key(self.dimension, self.chunk_x, self.chunk_z, self.operation_id)
        buffer = io.BytesIO(b"")
        for i in self.pending_ticks : nbt.write_to_nbt_file(buffer, i, byteorder="little")
        leveldb.put(key, buffer.getvalue())
        buffer.close()

class RandomTicks :
    """
    区块随机事件数据
    -----------------------
    * 可用属性 chunk_x : 区块x坐标
    * 可用属性 chunk_z : 区块z坐标
    * 可用属性 dimension : 区块所处的维度
    * 可用属性 random_ticks : 区块的随机事件nbt对象列表
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    operation_id = 58

    def __init__(self, x:int, z:int, dimension:Literal["overworld", "nether", "the_end"]) -> None:
        self.chunk_x = x
        self.chunk_z = z
        self.dimension = dimension
        self.random_ticks:List[nbt.TAG_Compound] = []

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB, dimension:Literal["overworld", "nether", "the_end"], 
        chunk_pos_x:int, chunk_pos_z:int) :
        key = generate_chunk_key(dimension, chunk_pos_x, chunk_pos_z, cls.operation_id)
        try : value = leveldb.get(key)
        except : return None

        Object = cls(chunk_pos_x, chunk_pos_z, dimension)

        buffer = io.BytesIO(value)
        while buffer.tell() < len(value) :
            Object.random_ticks.append(nbt.read_from_nbt_file(buffer, byteorder="little").get_tag())
        buffer.close()
        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        key = generate_chunk_key(self.dimension, self.chunk_x, self.chunk_z, self.operation_id)
        buffer = io.BytesIO(b"")
        for i in self.random_ticks : nbt.write_to_nbt_file(buffer, i, byteorder="little")
        leveldb.put(key, buffer.getvalue())
        buffer.close()





