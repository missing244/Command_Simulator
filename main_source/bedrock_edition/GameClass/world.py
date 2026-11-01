from typing import List, Dict, Union, Literal, Any, TypedDict, Generator
from . import nbt, MinecraftSimulator
from pathlib import Path
from .. import Constants, python_numpy as np
import random, copy, hashlib, os, json, traceback

if "TypeDefine" :
    
    class Area(TypedDict) :
        AreaType: Literal["square", "circle"]
        Dimension: Constants.DimensionID
        Preload: bool
        StartPos: List[int]
        EndPos: List[int]

    class Music(TypedDict) :
        name: str
        volume: float
        fade: float
        mode: Literal["loop", "play_once"]


class GameRuleManager :
    """管理游戏规则"""

    def __init__(self):
        self.commandblockoutput = True
        self.commandblocksenabled = True
        self.dodaylightcycle = True
        self.doentitydrops = True
        self.dofiretick = True
        self.doimmediaterespawn = False
        self.doinsomnia = True
        self.domobloot = True
        self.domobspawning = True
        self.dotiledrops = True
        self.doweathercycle = True
        self.drowningdamage = True
        self.falldamage = True
        self.firedamage = True
        self.freezedamage = True
        self.keepinventory = True
        self.mobgriefing = True
        self.naturalregeneration = True
        self.pvp = True
        self.respawnblocksexplode = True
        self.sendcommandfeedback = True
        self.showbordereffect = True
        self.showcoordinates = True
        self.showdeathmessages = True
        self.showtags = True
        self.tntexplodes = True
        self.recipesunlock = True
        self.projectilescanbreakblocks = True
        self.showrecipemessages = True
        self.tntexplosiondropdecay = False
        self.dolimitedcrafting = False
        self.showdaysplayed = False
        self.playerwaypoints = True

        self.spawnradius = 5
        self.randomtickspeed = 1
        self.functioncommandlimit = 10000
        self.maxcommandchainlength = 65536
        self.playerssleepingpercentage = 100

    def __setattr__(self, name:str, value:Union[bool, int]):
        if name not in Constants.GAMERULE : raise KeyError("%s 规则不存在" % name)

        GameruleData = Constants.GAMERULE[name]
        if type(value) is not type(GameruleData["default"]) : return None
        # raise TypeError("%s 规则数据类型不正确 (%s)" % (name, type(value)))
        if type(GameruleData["default"]) is int and not GameruleData["min"] <= value <= GameruleData["max"] : return None
        # raise ValueError("%s 规则数据数据不正确 (%s)" % (name, value))

        super().__setattr__(name, value)


    def serialization(self) -> Dict[str, Union[bool, int]] :
        Data = { }
        for gamerule in Constants.GAMERULE :
            if not hasattr(self, gamerule) : continue
            Data[gamerule] = self.__getattribute__(gamerule)
        return Data

    @classmethod
    def deserialization(cls, data:Dict[str, Union[bool, int]]) -> "GameRuleManager" :
        self = cls()
        for gamerule in Constants.GAMERULE :
            if gamerule not in data : continue
            self.__setattr__(gamerule, data[gamerule])
        return self

class TickingAreaManager :
    """管理常加载区块"""

    def __init__(self) :
        self.__area:Dict[str, Area] = {}

    def __iter__(self) : 
        return iter(self.__area.items())

    @property
    def AreaCount(self) :
        return len(self.__area)

    @property
    def MaxAreaCount(self) :
        return 10


    def create_square(self, identifier:str, dimension:Constants.DimensionID,
        start_pos:List[int], end_pos:List[int], preload:bool=False) :
        if not self.has_capacity() : return False
        if len(start_pos) < 3 : raise ValueError("起始坐标参数不足(%s)" % start_pos)
        if len(end_pos) < 3 : raise ValueError("结束坐标参数不足(%s)" % end_pos)
        start_pos = [start_pos[0]//16, start_pos[2]//16]
        end_pos = [end_pos[0]//16, end_pos[2]//16]
        self.__area[identifier] = {"AreaType":"square", "Dimension":dimension,
            "StartPos":start_pos, "EndPos":end_pos, "Preload":preload}

    def create_circle(self, identifier:str, dimension:Constants.DimensionID,
        start_pos:List[int], radius:int, preload:bool=False) :
        if not self.has_capacity() : return False
        if not 1 <= radius <= 4 : raise ValueError("半径参数不合法(%s)" % radius)
        start = [(start_pos[0] // 16) - radius, (start_pos[2] // 16) - radius]
        end = [(start_pos[0] // 16) + 1 + radius, (start_pos[2] // 16) + 1 + radius]
        self.__area[identifier] = {"AreaType":"circle", "Dimension":dimension,
            "StartPos":start, "EndPos":end, "Preload":preload}
    
    def has_tickingarea(self, identifier:str) -> bool :
        return identifier in self.__area

    def has_capacity(self) -> bool :
        return self.AreaCount < self.MaxAreaCount

    def remove_all(self) -> None :
        self.__area.clear()

    def remove_tickingarea(self, identifier:str) -> bool :
        if not self.has_tickingarea(identifier) : return False
        del self.__area[identifier]
        return True


    def serialization(self) -> Dict[str, Area] :
        return copy.deepcopy(self.__area)

    @classmethod
    def deserialization(cls, data:Dict[str, Area]) -> "TickingAreaManager" :
        self = cls()
        for identifier, area_data in data.items() :
            Area = {"AreaType":None, "Dimension":None, "StartPos":None, "EndPos":None, "Preload":False}
            if area_data.get("AreaType") not in {"square", "circle"} : continue
            if not isinstance(area_data.get("Dimension"), str) : continue
            if not isinstance(area_data.get("StartPos"), list) : continue
            if len(area_data.get("StartPos")) < 2 : continue
            if not all(isinstance(i, int) for i in area_data.get("StartPos")[0:2]) : continue
            if not isinstance(area_data.get("EndPos"), list) : continue
            if len(area_data.get("EndPos")) < 2 : continue
            if not all(isinstance(i, int) for i in area_data.get("EndPos")[0:2]) : continue

            Area["AreaType"] = area_data.get("AreaType")
            Area["Dimension"] = area_data.get("Dimension")
            Area["StartPos"] = area_data.get("StartPos")[0:2]
            Area["EndPos"] = area_data.get("EndPos")[0:2]
            Area["Preload"] = area_data.get("Preload", False)
            self.__area[identifier] = Area
        return self

class ScoreboardIdentity :
    """计分板追踪对象数据"""
    TypeEntity = 1
    TypePlayer = 2
    TypeFakePlayer = 3
    
    def __init__(self, id:Union[str, int], type:int, display_name:str=None) :
        self.DisplayName = str(id) if display_name is None else display_name
        self.IdentityType = type
        if isinstance(id, str) : 
            full = int.from_bytes(hashlib.md5(id.encode()).digest(), 'big')
            id = full & 0xffffffffffffffff
        self.Identifier = id

    def __setattr__(self, name, value) :
        if hasattr(self, name) and name not in {"DisplayName"} : 
            raise AttributeError(f"can not modify {name} attribute")
        super().__setattr__(name, value)

    def __eq__(self, other):
        if not isinstance(other, ScoreboardIdentity) : return False
        return self.Identifier == other.Identifier

    def __hash__(self):
        return self.Identifier

class ScoreboardObjective :
    """计分板对象数据"""

    def __init__(self, id:str, criteria:str="dummy", display_name:str=None) :
        self.IsValid = True
        self.Identifier = id
        self.Criteria = criteria
        self.DisplayName = id if display_name is None else display_name
        self.__Scores:Dict[ScoreboardIdentity, np.int32] = {}

    def __setattr__(self, name:str, value):
        if hasattr(self, name) and name not in {"DisplayName", "IsValid"} : 
            raise AttributeError(f"can not modify {name} attribute")
        super().__setattr__(name, value)
    
    def __getattribute__(self, name:str) :
        if name != "IsValid" and not super().__getattribute__("IsValid") : 
            raise AttributeError(f"can not read LifeEnd object")
        return super().__getattribute__(name)

    def __iter__(self):
        return iter(self.__Scores.items())

    def __contains__(self, participant:ScoreboardIdentity):
        return participant in self.__Scores
    
    def __delitem__(self, participant:ScoreboardIdentity) :
        if participant in self : del self.__Scores[participant]
    
    def clear_score(self, participant:ScoreboardIdentity=None) :
        if participant is None : self.__Scores.clear()
        else : del self[participant]

    def get_score(self, participant:ScoreboardIdentity) -> Union[np.int32, None] :
        if participant.__class__ is not ScoreboardIdentity : 
            raise TypeError(f"{participant} is not participant type")
        return self.__Scores.get(participant)

    def set_score(self, participant:ScoreboardIdentity, value:Union[int, np.int32]) :
        if participant.__class__ is not ScoreboardIdentity : 
            raise TypeError(f"{participant} is not participant type")
        if isinstance(value, (int, float)) : value = np.int32(value)
        self.__Scores[participant] = value

class ScoreboardManager :
    """计分板管理"""

    DisplaySlot = ("list", "sidebar", "below_name")

    def __init__(self) :
        self.__DisplayList = None
        self.__DisplaySidebar = None
        self.__DisplayBelowname = None
        self.__Objectives:Dict[str, ScoreboardObjective] = {}

    def __iter__(self):
        return iter(self.__Objectives.values())

    def __contains__(self, id:Union[ScoreboardObjective, str]) :
        if isinstance(id, ScoreboardObjective) : id = id.Identifier
        return id in self.__Objectives

    def add_objective(self, id:str, criteria:str="dummy", display_name:str=None) -> Union[ScoreboardObjective, None] :
        if id in self : return None
        self.__Objectives[id] = ScoreboardObjective(id, criteria, display_name)
        return self.__Objectives[id]

    def get_objective(self, id:str) -> Union[ScoreboardObjective, None] :
        return self.__Objectives.get(id)

    def remove_objective(self, id:Union[ScoreboardObjective, str]) -> bool :
        if id not in self : return False
        if isinstance(id, ScoreboardObjective) : id = id.Identifier

        self.__Objectives[id].IsValid = False
        if self.__DisplayList == id : self.modify_display_slot(self.DisplaySlot[0])
        if self.__DisplaySidebar == id : self.modify_display_slot(self.DisplaySlot[1])
        if self.__DisplayBelowname == id : self.modify_display_slot(self.DisplaySlot[2])
        del self.__Objectives[id]
        return True

    def modify_display_slot(self, slot_name:str, id:Union[ScoreboardObjective, str]=None) -> bool :
        if id not in self : return False
        if isinstance(id, ScoreboardObjective) : id = id.Identifier

        if slot_name == "list" : self.__DisplayList = id
        elif slot_name == "sidebar" : self.__DisplaySidebar = id
        elif slot_name == "below_name" : self.__DisplayBelowname = id
        return True


    def register_identity(self, participant:Any) :
        from .entity import Entity, Player
        if isinstance(participant, Player) :
            return ScoreboardIdentity(participant.UniqueID, ScoreboardIdentity.TypePlayer, participant.NameTag)
        elif isinstance(participant, Entity) :
            return ScoreboardIdentity(participant.UniqueID, ScoreboardIdentity.TypeEntity)
        elif isinstance(participant, str) :
            return ScoreboardIdentity(participant, ScoreboardIdentity.TypeFakePlayer)

    def get_all_participants(self) -> Generator[ScoreboardIdentity, None, None] :
        contains = set()
        for scb in self.__Objectives.values() :
            for scbID, _ in scb.__iter__() :
                if scbID in contains : continue
                contains.add(scbID)
                yield scbID

    def clear_participant(self, participant:ScoreboardIdentity="all") :
        for scb_obj in self.__iter__() :
            if participant == "all" : scb_obj.clear_score()
            else : del scb_obj[participant]


    def serialization(self) -> nbt.TAG_Compound :
        builder = nbt.TAG_Compound()
        builder["FormatVersion"] = nbt.TAG_Byte(1)
        builder["DisplayObjective"] = nbt.TAG_Compound()
        if self.__DisplayList is not None : builder["DisplayObjective"]["list"] = nbt.TAG_String(self.__DisplayList)
        if self.__DisplaySidebar is not None : builder["DisplayObjective"]["sidebar"] = nbt.TAG_String(self.__DisplaySidebar)
        if self.__DisplayBelowname is not None : builder["DisplayObjective"]["belowname"] = nbt.TAG_String(self.__DisplayBelowname)
        builder["Participants"] = nbt.TAG_List([], type=nbt.TAG_Compound)
        builder["Objectives"] = nbt.TAG_List([], type=nbt.TAG_Compound)
        
        IdentiySave = {}
        for scb_obj in self.__iter__() :
            scb_nbt = nbt.TAG_Compound()
            builder["Objectives"].append(scb_nbt)
            scb_nbt["Criteria"] = nbt.TAG_String(scb_obj.Criteria)
            scb_nbt["Identifier"] = nbt.TAG_String(scb_obj.Identifier)
            scb_nbt["DisplayName"] = nbt.TAG_String(scb_obj.DisplayName)
            scb_nbt["Scores"] = nbt.TAG_List([], type=nbt.TAG_Compound)
            
            for identiy, score in scb_obj.__iter__() :
                if identiy not in IdentiySave : 
                    participant = nbt.TAG_Compound()
                    participant["Identifier"] = nbt.TAG_Long(identiy.Identifier)
                    participant["IdentityType"] = nbt.TAG_Byte(identiy.IdentityType)
                    participant["DisplayName"] = nbt.TAG_String(identiy.DisplayName)
                    builder["Participants"].append(participant)
                    IdentiySave[identiy] = len(IdentiySave)
                score_obj = nbt.TAG_Compound()
                score_obj["ScoreboardId"] = nbt.TAG_Int(IdentiySave[identiy])
                score_obj["Score"] = nbt.TAG_Int(score.value)
                scb_nbt["Scores"].append(score_obj)
        
        return builder

    @classmethod
    def deserialization(cls, data:nbt.TAG_Compound) -> "ScoreboardManager" :
        version_tag = data.get("FormatVersion", nbt.TAG_Byte(1))
        if version_tag.value != 1 : raise ValueError(f"Unsupported or missing format version: {version_tag}")

        manager = cls()

        identity_list = []
        participants_tag = data.get("Participants", [])
        for part_tag in participants_tag :
            identifier = part_tag["Identifier"].value      # TAG_Long
            identity_type = part_tag["IdentityType"].value # TAG_Byte
            display_name = part_tag["DisplayName"].value   # TAG_String
            identity = ScoreboardIdentity(identifier, identity_type, display_name)
            identity_list.append(identity)

        objectives_tag = data.get("Objectives", [])
        for obj_tag in objectives_tag :
            obj_id = obj_tag["Identifier"].value
            criteria = obj_tag["Criteria"].value
            display_name = obj_tag["DisplayName"].value

            if obj_id in manager : objective = manager.get_objective(obj_id)
            else : objective = manager.add_objective(obj_id, criteria, display_name)

            # 填充分数
            scores_tag = obj_tag.get("Scores", [])
            for score_entry in scores_tag :
                idx = score_entry["ScoreboardId"].value   # 索引
                score_val = score_entry["Score"].value    # int
                if 0 <= idx < len(identity_list) :
                    identity = identity_list[idx]
                    objective.set_score(identity, np.int32(score_val))

        DisplayObjective = data.get("DisplayObjective", {})
        for i in cls.DisplaySlot : manager.modify_display_slot(i, DisplayObjective.get(i))

        return manager


class World : 

    def __deepcopy__(self, memo):
        memo[id(self)] = self  # 关键：必须先把自身注册到 memo，告诉 deepcopy "我已经处理完了"
        return self            # 返回自身，表示"我不复制自己，直接用原对象"

    def __init__(self, main_thread:"MinecraftSimulator") :
        self.__MainThread = main_thread
        self.EntityCreateCount = 1
        self.OpenCount:int = 0
        self.CurrentTick = np.int32(0)
        self.Seed = random.randint(1, 2**55-1)
        self.Difficulty:Literal[0,1,2,3] = 1
        self.DefaultGamemode:Literal[0,1,2,6] = 1
        self.SimulatorDistance:Literal[4,6,8,10] = 4
        self.WorldType:Literal["infinity", 'flat'] = "infinity"
        self.WeatherType:Literal["clear", 'rain', 'thunder'] = "clear"
        self.SpawnLocation = [np.float32(0.5), np.float32(-50), np.float32(0.5)]
        self.MobEvents = {
            "events_enabled":True, 
            "minecraft:ender_dragon_event":True, 
            "minecraft:pillager_patrols_event":True,
            "minecraft:wandering_trader_event":True
        }

        self.GameRule = GameRuleManager()
        self.Scoreboard = ScoreboardManager()
        self.TickingArea = TickingAreaManager()

        self.Music:List[Music] = []

    def __tick__(self) :
        self.CurrentTick += 1

    
    def play_music(self, trackName:str, repeatMode:str = "play_once") -> None :
        if repeatMode not in ("loop", "play_once"): raise ValueError("重复模式必须为 'loop' 或 'play_once'")
        music = {"track": trackName, "repeat": repeatMode}
        self.Music.insert(0, music)

    def queue_music(self, trackName:str, repeatMode:str = "play_once") -> None :
        if repeatMode not in ("loop", "play_once"): raise ValueError("重复模式必须为 'loop' 或 'play_once'")
        music = {"track": trackName, "repeat": repeatMode}
        self.Music.append(music)

    def stop_music(self) -> None:
        if self.Music : self.Music.pop(0)


    def serialization(self) :
        """
        将世界数据保存到指定路径。
        若 path 指向目录，则在该目录下创建 world.json 和 scoreboard.nbt
        """
        if self.__MainThread.IsChallenge : return None
        root_path = self.__MainThread.WorldPath
        root_path.mkdir(parents=True, exist_ok=True)

        # 主 JSON 文件（包含 World 自身、Time、GameRule、TickingArea）
        main_data = {
            "Seed": self.Seed,
            "OpenCount": self.OpenCount,
            "Difficulty": self.Difficulty,
            "DefaultGamemode": self.DefaultGamemode,
            "SimulatorDistance": self.SimulatorDistance,
            "WorldType": self.WorldType,
            "WeatherType": self.WeatherType,
            "SpawnLocation": [float(v) for v in self.SpawnLocation],  # np.float32 -> float
            "MobEvents": self.MobEvents,
            "GameRule": self.GameRule.serialization(),
            "TickingArea": self.TickingArea.serialization()
        }
        main_file = root_path / "world.json"
        with open(main_file, 'w', encoding='utf-8') as f: json.dump(main_data, f, ensure_ascii=False)

        # 计分板单独存储为 NBT 文件
        scoreboard_nbt = self.Scoreboard.serialization()
        scoreboard_file = root_path / "scoreboard.nbt"
        with open(scoreboard_file, 'wb') as f: nbt.write_to_nbt_file(f, scoreboard_nbt)

    def deserialization(self) :
        """
        从指定路径加载世界数据。
        """
        if self.__MainThread.IsChallenge : return None
        root_path = self.__MainThread.WorldPath
        main_file = root_path / "world.json"
        if not main_file.exists(): return None

        try : 
            with open(main_file, 'r', encoding='utf-8') as f: main_data = json.load(f)
        except : pass
        else :  # 填充基本属性
            self.Seed = main_data.get("Seed", random.randint(1, 2**55-1))
            self.OpenCount = main_data.get("OpenCount", 0) + 1
            self.Difficulty = main_data.get("Difficulty", 1)
            self.DefaultGamemode = main_data.get("DefaultGamemode", 0)
            self.SimulatorDistance = main_data.get("SimulatorDistance", 4)
            self.WorldType = main_data.get("WorldType", "infinity")
            self.WeatherType = main_data.get("WeatherType", "clear")
            spawn = main_data.get("SpawnLocation", [0.5, -50, 0.5])
            if len(spawn) < 3 : spawn = [0.5, -50, 0.5]
            self.SpawnLocation = [np.float32(spawn[0]), np.float32(spawn[1]), np.float32(spawn[2])]
            Mob_Events = main_data.get("MobEvents", {"events_enabled": True,
                "minecraft:ender_dragon_event": True, "minecraft:pillager_patrols_event": True,
                "minecraft:wandering_trader_event": True })
            self.MobEvents.update(Mob_Events)

            if not isinstance(self.Seed, int) : self.Seed = random.randint(1, 2**55-1)
            if not isinstance(self.Difficulty, int) : self.Difficulty = 1
            if not isinstance(self.DefaultGamemode, int) : self.DefaultGamemode = 0
            if not isinstance(self.SimulatorDistance, int) : self.SimulatorDistance = 4
            if self.WorldType not in {"infinity", 'flat'} : self.WorldType = "infinity"
            if self.WeatherType not in {"clear", 'rain', 'thunder'} : self.WeatherType = "clear"

            # 反序列化各管理器
            self.GameRule = GameRuleManager.deserialization( main_data.get("GameRule", {}) )
            self.TickingArea = TickingAreaManager.deserialization( main_data.get("TickingArea", {}) )

        # 加载计分板（NBT 文件）
        scoreboard_file = root_path / "scoreboard.nbt"
        if scoreboard_file.exists() :
            try : nbt_data = nbt.read_from_nbt_file(scoreboard_file).get_tag()
            except : traceback.print_exc()
            else : self.Scoreboard = ScoreboardManager.deserialization(nbt_data)

        return self
