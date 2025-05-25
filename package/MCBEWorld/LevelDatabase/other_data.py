from .. import nbt
from typing import Literal,List,Union,Dict,Tuple
import leveldb, io


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
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        try : value = leveldb.get(b"~local_player")
        except : return None

        player = nbt.read_from_nbt_file(value, byteorder="little").get_tag()
        return cls(player)
    
    def to_leveldb(self, leveldb:leveldb.LevelDB) :
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
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        Object = cls()
        for key in leveldb.keys() :
            if key[0:7] != b"player_" : continue
            value = leveldb.get(key)
            Object[key.decode("utf-8")] = nbt.read_from_nbt_file(value, byteorder="little").get_tag()
        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        for key,value in self.players.items() :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, value, byteorder="little")
            leveldb.put(key.encode("utf-8"), buffer.getvalue())
            buffer.close()

class Village :
    """
    村庄数据
    -----------------------
    * 可用属性 villages : 世界内的所有村庄
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """
    
    def __init__(self) -> None:
        self.villages:Dict[str, Dict[Literal["dimension", "DWELLERS", "INFO", "PLAYERS", "POI"], 
            Union[str, nbt.TAG_Compound, nbt.TAG_Compound, nbt.TAG_Compound, nbt.TAG_Compound]]] = {}

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        Object = cls()
        dimension = None ; uuid = None ; data_name = None
        for i in leveldb.keys() :
            if i[0:8] != b'VILLAGE_' : continue
            list1 = i.decode("utf-8").split("_")
            dimension, uuid, data_name = list1[1], list1[2], list1[3]
            if uuid not in Object.villages : Object.villages[uuid] = {}
            if "dimension" not in Object.villages[uuid] : 
                Object.villages[uuid]["dimension"] = dimension
            if data_name not in Object.villages[uuid] : 
                Object.villages[uuid][data_name] = nbt.read_from_nbt_file(leveldb.get(i), byteorder="little").get_tag()

        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        for uuid, value_1 in self.villages.items() :
            for data_name, value_2 in value_1.items() :
                if data_name == "dimension" : continue
                key = "VILLAGE_%s_%s_%s" % (value_1["dimension"], uuid, data_name)
                key = key.encode("utf-8")

                buffer = io.BytesIO(b"")
                nbt.write_to_nbt_file(buffer, value_2, byteorder="little")
                leveldb.put(key, buffer.getvalue())
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
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        Object = cls()
        for i in leveldb.keys() :
            if i[0:4] != b'map_' : continue
            Object.maps[i.decode("utf-8")] = nbt.read_from_nbt_file(leveldb.get(i), byteorder="little").get_tag()

        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        for key, value in self.maps :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, value, byteorder="little")
            leveldb.put(key.encode("utf-8"), buffer.getvalue())
            buffer.close()

class Portal :
    """
    传送门数据
    -----------------------
    * 可用属性 nbt : 存档内激活的传送门nbt数据
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """
    
    def __init__(self, nbt1:nbt.TAG_Compound) -> None:
        self.nbt = nbt1

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        try : value = leveldb.get(b'portals')
        except : return None
        nbt1 = nbt.read_from_nbt_file(value, byteorder="little")

        return cls(nbt1)

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        buffer = io.BytesIO(b"")
        nbt.write_to_nbt_file(buffer, self.nbt, byteorder="little")
        leveldb.put(b'portals', buffer.getvalue())
        buffer.close()

class Mobevent :
    """
    生物事件数据
    -----------------------
    * 可用属性 nbt : 生物事件开关nbt数据
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """
    
    def __init__(self, nbt1:nbt.TAG_Compound) -> None:
        self.nbt = nbt1

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        try : value = leveldb.get(b'mobevents')
        except : return None
        nbt1 = nbt.read_from_nbt_file(value, byteorder="little").get_tag()

        return cls(nbt1)

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        buffer = io.BytesIO(b"")
        nbt.write_to_nbt_file(buffer, self.nbt, byteorder="little")
        leveldb.put(b'mobevents', buffer.getvalue())
        buffer.close()

class SchedulerWT :
    """
    延迟事件数据
    -----------------------
    * 可用属性 nbt : 延迟事件nbt数据
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """
    
    def __init__(self, nbt:nbt.TAG_Compound) -> None:
        self.nbt = nbt

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        try : value = leveldb.get(b'schedulerWT')
        except : return None
        nbt1 = nbt.read_from_nbt_file(value, byteorder="little").get_tag()

        return cls(nbt1)

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        buffer = io.BytesIO(b"")
        nbt.write_to_nbt_file(buffer, self.nbt, byteorder="little")
        leveldb.put(b'schedulerWT', buffer.getvalue())
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
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        try : value = leveldb.get(b'scoreboard')
        except : return None
        nbt1 = nbt.read_from_nbt_file(value, byteorder="little").get_tag()

        return cls(nbt1)

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        buffer = io.BytesIO(b"")
        nbt.write_to_nbt_file(buffer, self.nbt, byteorder="little")
        leveldb.put(b'scoreboard', buffer.getvalue())
        buffer.close()

class Structure :
    """
    磁盘结构数据
    -----------------------
    * 可用属性 structures : 结构nbt数据字典
    -----------------------
    * 可用类方法 from_leveldb : 在leveldb对象中获取本对象需要的数据
    * 可用方法 to_leveldb : 将数据写入leveldb对象中
    """

    def __init__(self) -> None:
        self.structures:Dict[str, nbt.TAG_Compound] = {}

    @classmethod
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        Object = cls()
        for i in leveldb.keys() :
            if i[0:18] != b'structuretemplate_' : continue
            str1 = i.decode("utf-8").split("_", 1)
            Object.structures[str1[1]] = nbt.read_from_nbt_file(leveldb.get(i), byteorder="little").get_tag()

        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        for name, value in self.structures.items() :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, value, byteorder="little")
            key = ("structuretemplate_%s" % name).encode("utf-8")
            leveldb.put(key, buffer.getvalue())
            buffer.close()

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
    def from_leveldb(cls, leveldb:leveldb.LevelDB) :
        Object = cls()
        for i in leveldb.keys() :
            if i[0:12] != b'tickingarea_' : continue
            str1 = i.decode("utf-8").split("_", 1)
            Object.tickingareas[str1[1]] = nbt.read_from_nbt_file(leveldb.get(i), byteorder="little").get_tag()

        return Object

    def to_leveldb(self, leveldb:leveldb.LevelDB) :
        for name, value in self.tickingareas :
            buffer = io.BytesIO(b"")
            nbt.write_to_nbt_file(buffer, value, byteorder="little")
            key = ("tickingarea_%s" % name).encode("utf-8")
            leveldb.put(key, buffer.getvalue())
            buffer.close()




