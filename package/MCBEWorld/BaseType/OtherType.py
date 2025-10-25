from .. import nbt
from ..C_leveldb import LevelDB
from . import ModifyError, ValueError
from typing import Tuple,List,Union,Dict,Literal,Generator,Any
import io, random, array, copy, traceback


class LocalPlayer :
    """
    本地玩家数据
    -----------------------
    * 可用属性 player : 本地玩家的nbt数据
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """
    
    def __init__(self, player:nbt.TAG_Compound) -> None:
        self.player = player

    @classmethod
    def from_leveldb(cls, leveldb:LevelDB) :
        try : value = leveldb.get(b"~local_player")
        except : return None

        player = nbt.read_from_nbt_file(value, byteorder="little").get_tag()
        return cls(player)
    
    def to_leveldb(self, leveldb:LevelDB) :
        buffer = io.BytesIO(b"")
        nbt.write_to_nbt_file(buffer, self.player, byteorder="little")
        leveldb.put(b"~local_player", buffer.getvalue())
        buffer.close()

class OnlinePlayer :
    """
    联机玩家数据
    -----------------------
    * 可用属性 players : 联机玩家数据字典
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    def __init__(self) -> None:
        self.players:Dict[str, nbt.TAG_Compound] = {}

    @classmethod
    def from_leveldb(cls, leveldb:LevelDB) :
        Object = cls()
        for key in leveldb.keys() :
            if key[0:7] != b"player_" : continue
            value = leveldb.get(key)
            Object[key.decode("utf-8")] = nbt.read_from_nbt_file(value, byteorder="little").get_tag()
        return Object

    def to_leveldb(self, leveldb:LevelDB) :
        for key,value in self.players.items() :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, value, byteorder="little")
            leveldb.put(key.encode("utf-8"), buffer.getvalue())
            buffer.close()

class Scoreboard :
    """
    计分板数据
    -----------------------
    * 可用属性 nbt : 计分板nbt数据
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    def __init__(self, nbt:nbt.TAG_Compound) -> None:
        self.nbt = nbt

    @classmethod
    def from_leveldb(cls, leveldb:LevelDB) :
        try : value = leveldb.get(b'scoreboard')
        except : return None
        nbt1 = nbt.read_from_nbt_file(value, byteorder="little").get_tag()

        return cls(nbt1)

    def to_leveldb(self, leveldb:LevelDB) :
        buffer = io.BytesIO(b"")
        nbt.write_to_nbt_file(buffer, self.nbt, byteorder="little")
        leveldb.put(b'scoreboard', buffer.getvalue())
        buffer.close()

class Map :
    """
    纸质地图数据
    -----------------------
    * 可用属性 maps : 纸质地图nbt数据列表
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """
    
    def __init__(self) -> None:
        self.maps:Dict[str, nbt.TAG_Compound] = {}

    @classmethod
    def from_leveldb(cls, leveldb:LevelDB) :
        Object = cls()
        for i in leveldb.keys() :
            if i[0:4] != b'map_' : continue
            Object.maps[i.decode("utf-8")] = nbt.read_from_nbt_file(leveldb.get(i), byteorder="little").get_tag()

        return Object

    def to_leveldb(self, leveldb:LevelDB) :
        for key, value in self.maps :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, value, byteorder="little")
            leveldb.put(key.encode("utf-8"), buffer.getvalue())
            buffer.close()

class Structure :
    """
    磁盘结构数据
    -----------------------
    * 实例化参数 **leveldb** : LevelDB对象
    -----------------------
    * 可用魔法方法 **\_\_len__**       : 获取存档中的结构总数量
    * 可用魔法方法 **\_\_iter__**      : 迭代存档中的所有结构名
    * 可用魔法方法 **\_\_contains__**  : 判断结构名是否存在于存档中
    -----------------------
    * 可用方法 **clear**  : 清空存档内的所有结构(谨慎调用)
    * 可用方法 **getAll** : 根据名字获取存档内的结构数据
    * 可用方法 **get**    : 根据名字获取存档内的结构数据
    * 可用方法 **set**    : 根据名字向存档内写入结构数据
    * 可用方法 **delete** : 根据名字删除存档内的结构(谨慎调用)
    """

    def __str__(self) :
        return "<Structure Name=%s>" % (list(self), )

    def __init__(self, leveldb:LevelDB) -> None:
        self.__leveldb = leveldb

    def __iter__(self) -> Generator[str, Any, None]:
        for i,_ in self.__leveldb.iterate(b'structuretemplate_') :
            if not i.startswith(b'structuretemplate_') : break
            name:str = i.decode("utf-8").split("_", 1)[1]
            yield name

    def __contains__(self, name:str) -> bool :
        key = ("structuretemplate_%s" % name).encode("utf-8")
        return key in self.__leveldb
    
    def __len__(self) -> int :
        Count = 0
        for i,_ in self.__leveldb.iterate(b'structuretemplate_') :
            if not i.startswith(b'structuretemplate_') : break
            Count += 1
        return Count
    

    def clear(self) -> None :
        name_list = list(self)
        for name in name_list : 
            key = ("structuretemplate_%s" % name).encode("utf-8")
            self.__leveldb.delete(key)

    def getAll(self) -> List[str] :
        return list(self)

    def get(self, name:str) -> bytes :
        key = ("structuretemplate_%s" % name).encode("utf-8")
        return self.__leveldb.get(key)

    def set(self, name:str, bytes1:bytes) -> bytes :
        key = ("structuretemplate_%s" % name).encode("utf-8")
        self.__leveldb.put(key, bytes1)

    def delete(self, name:str) :
        key = ("structuretemplate_%s" % name).encode("utf-8")
        self.__leveldb.delete(key)

class TickingArea :
    """
    常加载区块数据
    -----------------------
    * 可用属性 tickingareas : 常加载区块nbt数据字典
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    def __init__(self) -> None:
        self.tickingareas:Dict[str, nbt.TAG_Compound] = {}

    @classmethod
    def from_leveldb(cls, leveldb:LevelDB) :
        Object = cls()
        for i in leveldb.keys() :
            if i[0:12] != b'tickingarea_' : continue
            str1 = i.decode("utf-8").split("_", 1)
            Object.tickingareas[str1[1]] = nbt.read_from_nbt_file(leveldb.get(i), byteorder="little").get_tag()

        return Object

    def to_leveldb(self, leveldb:LevelDB) :
        for name, value in self.tickingareas :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, value, byteorder="little")
            key = ("tickingarea_%s" % name).encode("utf-8")
            leveldb.put(key, buffer.getvalue())
            buffer.close()


