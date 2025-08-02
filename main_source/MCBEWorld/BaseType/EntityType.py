from .. import nbt
from . import ModifyError, ValueError
from typing import Tuple,List,Union,Dict,Literal,Optional
import array, random, ctypes, copy, traceback, io

NotMobEntityList = {"area_effect_cloud", "arrow", "boat", "breeze_wind_charge_projectile", "chest_boat",
    "chest_minecart", "command_block_minecart", "dragon_fireball", "egg", "ender_crystal", "ender_pearl",
    "evocation_fang", "eye_of_ender_signal", "falling_block", "fireball", "fireworks_rocket", "fishing_hook",
    "hopper_minecart", "item", "leash_knot", "lightning_bolt", "lingering_potion", "llama_spit", "minecart",
    "ominous_item_spawner", "painting", "shulker_bullet", "small_fireball", "splash_potion", "snowball",
    "thrown_trident", "tnt", "tnt_minecart", "wind_charge_projectile", "wither_skull", "wither_skull_dangerous",
    "xp_bottle", "xp_orb"}
EffectID = ["speed", "slowness", "haste", "mining_fatigue", "strength", "instant_health", "instant_damage", "jump_boost",
    "nausea", "regeneration", "resistance", "fire_resistance", "water_breathing", "invisibility", "blindness", "night_vision",
    "hunger", "weakness", "poison", "wither", "health_boost", "absorption", "saturation", "levitation", "fatal_poison",
    "conduit_power", "slow_falling", "bad_omen", "village_hero", "darkness", "trial_omen", "wind_charged", "weaving", "oozing",
    "infested", "raid_omen"]

for i in list(NotMobEntityList) : 
    NotMobEntityList.remove(i) ; NotMobEntityList.add(f"minecraft:{i}")


class EntityType :
    """
    ## 基岩版实体对象
    * 属性**UniqueID**            : 实体在世界中的唯一数字ID **(int)**
    * 属性**Identifier**          : 实体英文ID **(str)**
    * 属性**Pos**                 : 实体坐标 **(List[float, float, float])**
    * 属性**Rotation**            : 实体朝向 **(List[float, float])**
    * 属性**CustomName**          : 实体名字 **(str)**
    * 属性**CustomNameVisible**   : 实体是否隐藏名字 **(bool)**
    * 属性**Invulnerable**        : 实体是否为无敌模式 **(bool)**
    * 属性**Tags**                : 实体拥有的标签 **(set)**  
    * 属性**ChestItems**          : 容器实体(漏斗矿车，箱子矿车等)的内含物品 **(Dict[int, ItemType])**  
    * 属性**FallingBlock**        : 下落方块的方块数据 **(BlockPermutationType)**  
    * 属性**ExtraNBT**            : 额外的NBT数据 **(nbt.TAG_Compound)**  
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_nbt** : 通过NBT对象生成实体对象
    * 可用方法**to_nbt** : 通过实体对象生成NBT对象
    * 可用方法**copy** : 复制并生成一个独立的实体对象
    """

    def __str__(self) :
        return "<Entity Id='%s' UniqueID=%s>" % (self.Identifier, self.UniqueID)
    
    def __repr__(self) :
        return self.__str__()

    def __setattr__(self, name:str, value) :
        try : self.__initialize
        except : super().__setattr__(name, value) ; return None

        if name == "Identifier" and isinstance(value, str) : super().__setattr__(name, 
            f"minecraft:{value}" if not ":" not in value else value)
        elif name == "CustomName" and isinstance(value, str) : super().__setattr__(name, value)
        elif name == "UniqueID" and isinstance(value, int) : super().__setattr__(name, value)
        elif name == "CustomNameVisible" and isinstance(value, bool) : super().__setattr__(name, bool(value))
        elif name == "Invulnerable" and isinstance(value, bool) : super().__setattr__(name, bool(value))
        elif hasattr(self, name) : raise ValueError("属性%s不允许赋值支持以外的数值" % name)
        else : raise ModifyError("属性%s不允许修改" % name)

    def __delattr__(self, name) :
        raise ModifyError("不允许删除%s属性" % name)
        
    def __init__(self, id:str, pos:Tuple[int, int, int]=[0, 0, 0], rotation:Tuple[int, int]=[0,0]) :
        from . import ItemType, BlockPermutationType

        #实体通用属性
        self.UniqueID:int = random.randint(2**32, 2**34)
        self.Identifier:str = f"minecraft:{id}" if ":" not in id else id
        self.Pos = array.array("f", pos)
        self.Rotation = array.array("f", rotation)
        self.CustomName:str = ""
        self.CustomNameVisible:bool = False
        self.Invulnerable:bool = False
        self.Tags:set = set()

        #箱船，箱子矿车特殊属性
        self.ChestItems:Dict[int, ItemType] = {}
        #下落的方块特殊属性
        self.FallingBlock:Optional[BlockPermutationType] = None

        self.ExtraNBT:nbt.TAG_Compound = nbt.TAG_Compound()
        self.__initialize = True
        

    @classmethod
    def from_nbt(cls, nbt_data:nbt.TAG_Compound, Obj=None) :
        from . import ItemType, BlockPermutationType

        if not isinstance(nbt_data, nbt.TAG_Compound) or not nbt_data.get("identifier", "") : return None
        EntityObject = cls(nbt_data["identifier"].value) if not Obj else Obj
        EntityObject.UniqueID = nbt_data["UniqueID"].value
        for i in range(3) : EntityObject.Pos[i] = nbt_data["Pos"][i].value
        for i in range(2) : EntityObject.Rotation[i] = nbt_data["Rotation"][i].value
        EntityObject.CustomName = nbt_data["CustomName"].value if "CustomName" in nbt_data else ""
        EntityObject.CustomNameVisible = bool(nbt_data.get("CustomNameVisible", False))
        EntityObject.Invulnerable = bool(nbt_data.get("Invulnerable", False))
        for item in nbt_data.get("Tags", []) : EntityObject.Tags.add(item.value)
        if "FallingBlock" in nbt_data : EntityObject.FallingBlock = BlockPermutationType.from_nbt(nbt_data["FallingBlock"])
        
        for sub_item in nbt_data.get("ChestItems", []) :
            if not("Name" in sub_item and "Slot" in sub_item) : continue
            try : int(sub_item["Slot"].value)
            except : continue
            SubItemObject = ItemType.from_nbt(sub_item)
            if SubItemObject : EntityObject.ChestItems[int(sub_item["Slot"].value)] = SubItemObject

        ExceptKey = {"identifier", "UniqueID", "Pos", "Rotation", "CustomName", "CustomNameVisible",
            "Invulnerable", "ChestItems", "FallingBlock"}
        for key, value in nbt_data.items() :
            if key in ExceptKey : continue
            EntityObject.ExtraNBT[key] = value.copy()

        return EntityObject

    def to_nbt(self) -> nbt.TAG_Compound :
        node = nbt.NBT_Builder()
        NBTObject = node.compound(
            identifier = node.string( self.Identifier ),
            UniqueID = node.long( self.UniqueID ),
            Pos = node.list( node.float(self.Pos[0]), node.float(self.Pos[1]), node.float(self.Pos[2]) ),
            Rotation = node.list( node.float(self.Pos[0]), node.float(self.Pos[1]) ),
            CustomName = node.string( self.CustomName ),
            CustomNameVisible = node.byte( self.CustomNameVisible ),
            Invulnerable = node.byte( self.Invulnerable )
        ).build()
        if self.ChestItems : 
            NBTObject["ChestItems"] = nbt.TAG_List([], type=nbt.TAG_Compound )
            for slot, item in self.ChestItems.items() :
                ItemNbt = item.to_nbt()
                ItemNbt["Slot"] = nbt.TAG_Byte( ctypes.c_int8(slot).value )
                NBTObject["ChestItems"].append( ItemNbt )
        if self.FallingBlock: NBTObject["FallingBlock"] = self.FallingBlock.to_nbt()
        for key, value in self.ExtraNBT.items() :
            NBTObject[key] = value.copy()

        return NBTObject

    def copy(self) -> "EntityType" :
        EntityObject = self.__class__()
        for key, value in self.__dict__.items() :
            if key.startswith("_") : continue
            if key == "ChestItems" : continue
            if key == "ActiveEffects" : continue
            if key == "Inventory" : continue
            if key == "EnderChestInventory" : continue
            EntityObject[key] = value.copy() if hasattr(value, "copy") else value
        for key, value in self.ChestItems.items() : EntityObject.ChestItems[key] = value.copy()
        for key, value in self.ExtraNBT.items() : EntityObject.ExtraNBT[key] = value.copy()
        EntityObject.UniqueID = random.randint(2**32, 2**34)
        return EntityObject

class ItemEntityType(EntityType) :
    """
    ## 基岩版实体对象
    * 属性**UniqueID**            : 实体在世界中的唯一数字ID **(int)**
    * 属性**Identifier**          : 实体英文ID **(str)**
    * 属性**Pos**                 : 实体坐标 **(List[float, float, float])**
    * 属性**Rotation**            : 实体朝向 **(List[float, float])**
    * 属性**CustomName**          : 实体名字 **(str)**
    * 属性**CustomNameVisible**   : 实体是否隐藏名字 **(bool)**
    * 属性**Invulnerable**        : 实体是否为无敌模式 **(bool)**
    * 属性**Tags**                : 实体拥有的标签 **(set)**  
    * 属性**ExtraNBT**            : 额外的NBT数据 **(nbt.TAG_Compound)**  

    掉落物的共同标签
    * 属性**Age**                 : 实体是否隐藏名字 **(int)**
    * 属性**Health**              : 实体是否为无敌模式 **(int)**
    * 属性**Item**                : 实体拥有的标签 **(ItemType)**  
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_nbt** : 通过NBT对象生成实体对象
    * 可用方法**to_nbt** : 通过实体对象生成NBT对象
    * 可用方法**copy** : 复制并生成一个独立的实体对象
    """
    
    def __setattr__(self, name:str, value) :
        from . import ItemType
        if name == "Age" and isinstance(value, int) : super(EntityType, self).__setattr__(name, ctypes.c_int16(value).value)
        elif name == "Health" and isinstance(value, int) : super(EntityType, self).__setattr__(name, ctypes.c_int16(value).value)
        elif name == "Item" and isinstance(value, (ItemType, type(None))) : super(EntityType, self).__setattr__(name, value)
        else : super().__setattr__(name, value)

    def __init__(self, id, pos=[0, 0, 0], rotation=[0, 0]) :
        from . import ItemType
        self.Age:int = 0
        self.Health:int = 5
        self.Item:ItemType = None

        super().__init__(id, pos, rotation)


    @classmethod
    def from_nbt(cls, nbt_data:nbt.TAG_Compound) :
        from . import ItemType

        EntityObject = cls("minecraft:item")
        EntityObject.Age = nbt_data["Age"].value
        EntityObject.Health = nbt_data["Health"].value
        EntityObject.Item = ItemType.from_nbt(nbt_data["Item"])

        Entity = super().from_nbt(nbt_data, EntityObject)
        ExceptKey = {"Age", "Health", "Item"}
        for key in list(Entity.ExtraNBT.keys()) :
            if key in ExceptKey : del Entity.ExtraNBT[key]
        
        return Entity
    
    def to_nbt(self):
        NbtObject = super().to_nbt()
        NbtObject["Age"] = nbt.TAG_Short( self.Age )
        NbtObject["Health"] = nbt.TAG_Short( self.Health )
        NbtObject["Item"] = self.Item.to_nbt()
        return NbtObject

class MobType(EntityType) : 
    """
    ## 基岩版实体对象
    * 属性**UniqueID**            : 实体在世界中的唯一数字ID **(int)**
    * 属性**Identifier**          : 实体英文ID **(str)**
    * 属性**Pos**                 : 实体坐标 **(List[float, float, float])**
    * 属性**Rotation**            : 实体朝向 **(List[float, float])**
    * 属性**CustomName**          : 实体名字 **(str)**
    * 属性**CustomNameVisible**   : 实体是否隐藏名字 **(bool)**
    * 属性**Invulnerable**        : 实体是否为无敌模式 **(bool)**
    * 属性**Tags**                : 实体拥有的标签 **(set)**  
    * 属性**ExtraNBT**            : 额外的NBT数据 **(nbt.TAG_Compound)**  

    生物的共同标签
    * 属性**ActiveEffects**  : 生物的药水效果数据 **(Dict[药效ID, Dict[Literal["Amplifie", "Duration", "ShowParticles"], int]])**
    * 属性**Mainhand**       : 生物主手物品 **(ItemType)**
    * 属性**Offhand**        : 生物副手物品 **(ItemType)**
    * 属性**ArmorHead**      : 生物头盔位置的物品 **(ItemType)**
    * 属性**ArmorChest**     : 生物胸甲位置的物品 **(ItemType)**
    * 属性**ArmorLegs**      : 生物护腿位置的物品 **(ItemType)**
    * 属性**ArmorFeet**      : 生物靴子位置的物品 **(ItemType)**
    * 属性**ArmorWolf**      : 狼铠位置的物品 **(ItemType)**
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_nbt** : 通过NBT对象生成实体对象
    * 可用方法**to_nbt** : 通过实体对象生成NBT对象
    * 可用方法**copy** : 复制并生成一个独立的实体对象
    """

    def __str__(self) :
        return "<Mob Id='%s' UniqueID=%s>" % (self.Identifier, self.UniqueID)

    def __setattr__(self, name:str, value) :
        from . import ItemType
        SupportType = (ItemType, type(None))
        if name == "Mainhand" and isinstance(value, SupportType) : super(EntityType, self).__setattr__(name, value)
        elif name == "Offhand" and isinstance(value, SupportType) : super(EntityType, self).__setattr__(name, value)
        elif name == "ArmorHead" and isinstance(value, SupportType) : super(EntityType, self).__setattr__(name, value)
        elif name == "ArmorChest" and isinstance(value, SupportType) : super(EntityType, self).__setattr__(name, value)
        elif name == "ArmorLegs" and isinstance(value, SupportType) : super(EntityType, self).__setattr__(name, value)
        elif name == "ArmorFeet" and isinstance(value, SupportType) : super(EntityType, self).__setattr__(name, value)
        elif name == "ArmorWolf" and isinstance(value, SupportType) : super(EntityType, self).__setattr__(name, value)
        else : super().__setattr__(name, value)
    
    def __init__(self, id:str, pos:Tuple[int, int, int]=[0, 0, 0], rotation:Tuple[int, int]=[0,0]) :
        from . import ItemType

        #生物特殊属性
        self.ActiveEffects:Dict[str, Dict[Literal["Amplifie", "Duration", "ShowParticles"], int]]={}
        self.Mainhand:Optional[ItemType] = None
        self.Offhand:Optional[ItemType] = None
        self.ArmorHead:Optional[ItemType] = None
        self.ArmorChest:Optional[ItemType] = None
        self.ArmorLegs:Optional[ItemType] = None
        self.ArmorFeet:Optional[ItemType] = None
        self.ArmorWolf:Optional[ItemType] = None

        super().__init__(id, pos, rotation)


    @classmethod
    def from_nbt(cls, nbt_data:nbt.TAG_Compound, Obj=None) :
        from . import ItemType
        EntityObject = cls(nbt_data["identifier"].value) if not Obj else Obj
        EntityObject.Offhand = ItemType.from_nbt(nbt_data["Offhand"][0] if len(nbt_data["Offhand"]) > 0 else {})
        EntityObject.Mainhand = ItemType.from_nbt(nbt_data["Mainhand"][0] if len(nbt_data["Mainhand"]) > 0 else {})
        EntityObject.ArmorHead = ItemType.from_nbt(nbt_data["Armor"][0] if len(nbt_data["Armor"]) > 0 else {})
        EntityObject.ArmorChest = ItemType.from_nbt(nbt_data["Armor"][1] if len(nbt_data["Armor"]) > 1 else {})
        EntityObject.ArmorLegs = ItemType.from_nbt(nbt_data["Armor"][2] if len(nbt_data["Armor"]) > 2 else {})
        EntityObject.ArmorFeet = ItemType.from_nbt(nbt_data["Armor"][3] if len(nbt_data["Armor"]) > 3 else {})
        EntityObject.ArmorWolf = ItemType.from_nbt(nbt_data["Armor"][4] if len(nbt_data["Armor"]) > 4 else {})

        for EffectData in nbt_data.get("ActiveEffects", []) :
            EntityObject.ActiveEffects[ EffectID[ EffectData["Id"].value-1 ] ] = {"Amplifie": EffectData["Amplifier"].value, 
                "Duration": EffectData["Duration"].value, "ShowParticles": EffectData["ShowParticles"].value }
            
        Entity = super().from_nbt(nbt_data, EntityObject)
        ExceptKey = {"Offhand", "Mainhand", "Armor", "ActiveEffects"}
        for key in list(Entity.ExtraNBT.keys()) :
            if key in ExceptKey : del Entity.ExtraNBT[key]
        
        return Entity
    
    def to_nbt(self):
        from . import NoneItemNBT
        NbtObject = super().to_nbt()
        NbtObject["Offhand"] = nbt.TAG_List( [ self.Offhand.to_nbt() if self.Offhand else NoneItemNBT.copy() ], type=nbt.TAG_Compound )
        NbtObject["Mainhand"] = nbt.TAG_List( [ self.Mainhand.to_nbt() if self.Mainhand else NoneItemNBT.copy() ], type=nbt.TAG_Compound )
        NbtObject["Armor"] = nbt.TAG_List( [ NoneItemNBT.copy() for i in range(5) ], type=nbt.TAG_Compound )
        if self.ArmorHead : NbtObject["Armor"][0] = self.ArmorHead.to_nbt()
        if self.ArmorChest : NbtObject["Armor"][1] = self.ArmorChest.to_nbt()
        if self.ArmorLegs : NbtObject["Armor"][2] = self.ArmorLegs.to_nbt()
        if self.ArmorFeet : NbtObject["Armor"][3] = self.ArmorFeet.to_nbt()
        if self.ArmorWolf : NbtObject["Armor"][4] = self.ArmorWolf.to_nbt()
        NbtObject["ActiveEffects"] = nbt.TAG_List( [], type=nbt.TAG_Compound )
        for EffectName, EffectData in self.ActiveEffects.items() :
            EffectNBT = nbt.TAG_Compound()
            EffectNBT["Ambient"] = nbt.TAG_Byte(0)
            EffectNBT["Amplifier"] = nbt.TAG_Byte(EffectData["Amplifie"])
            EffectNBT["DisplayOnScreenTextureAnimation"] = nbt.TAG_Byte(0)
            EffectNBT["Duration"] = nbt.TAG_Int(EffectData["Duration"])
            EffectNBT["DurationEasy"] = nbt.TAG_Int(EffectData["Duration"])
            EffectNBT["DurationHard"] = nbt.TAG_Int(EffectData["Duration"])
            EffectNBT["DurationNormal"] = nbt.TAG_Int(EffectData["Duration"])
            EffectNBT["ShowParticles"] = nbt.TAG_Byte(EffectData["ShowParticles"])
            EffectNBT["Id"] = nbt.TAG_Byte( EffectID.index(EffectName)+1 )
            EffectNBT["FactorCalculationData"] = nbt.TAG_Compound()
            EffectNBT["FactorCalculationData"]["factor_current"] = nbt.TAG_Float(0)
            EffectNBT["FactorCalculationData"]["factor_previous"] = nbt.TAG_Float(0)
            EffectNBT["FactorCalculationData"]["factor_start"] = nbt.TAG_Float(0)
            EffectNBT["FactorCalculationData"]["factor_target"] = nbt.TAG_Float(1)
            EffectNBT["FactorCalculationData"]["had_applied"] = nbt.TAG_Byte(1)
            EffectNBT["FactorCalculationData"]["had_last_tick"] = nbt.TAG_Byte(0)
            EffectNBT["FactorCalculationData"]["padding_duration"] = nbt.TAG_Int(0)
            EffectNBT["FactorCalculationData"]["ticks_active"] = nbt.TAG_Int(0)
            NbtObject["ActiveEffects"].append( EffectNBT )
        return NbtObject

    def copy(self):
        MobObject = super().copy()
        for i,j in MobObject.ActiveEffects.items() : MobObject.ActiveEffects[i] = j.copy()
        return MobObject
        
class PlayerType(MobType) :
    """
    ## 基岩版实体对象
    * 属性**UniqueID**            : 实体在世界中的唯一数字ID **(int)**
    * 属性**Identifier**          : 实体英文ID **(str)**
    * 属性**Pos**                 : 实体坐标 **(List[float, float, float])**
    * 属性**Rotation**            : 实体朝向 **(List[float, float])**
    * 属性**CustomName**          : 实体名字 **(str)**
    * 属性**CustomNameVisible**   : 实体是否隐藏名字 **(bool)**
    * 属性**Invulnerable**        : 实体是否为无敌模式 **(bool)**
    * 属性**Tags**                : 实体拥有的标签 **(set)**  
    * 属性**ExtraNBT**            : 额外的NBT数据 **(nbt.TAG_Compound)**  

    生物的共同标签
    * 属性**ActiveEffects**  : 生物的药水效果数据 **(Dict[药效ID, Dict[Literal["Amplifie", "Duration", "ShowParticles"], int]])**
    * 属性**Mainhand**       : 生物主手物品 **(ItemType)**
    * 属性**Offhand**        : 生物副手物品 **(ItemType)**
    * 属性**ArmorHead**      : 生物头盔位置的物品 **(ItemType)**
    * 属性**ArmorChest**     : 生物胸甲位置的物品 **(ItemType)**
    * 属性**ArmorLegs**      : 生物护腿位置的物品 **(ItemType)**
    * 属性**ArmorFeet**      : 生物靴子位置的物品 **(ItemType)**
    
    玩家的共同标签
    * 属性**GameMode**             : 玩家游戏模式 **(int)**
    * 属性**Dimension**            : 玩家处于的维度 **(int)**
    * 属性**LevelData**            : 玩家经验条数据 **(Dict[Literal["Level", "Progress"], int])**
    * 属性**SpawnLocation**        : 玩家出生点信息 **(Dict[Literal["Dimension", "X", "Y", "Z"], int])**
    * 属性**Inventory**            : 玩家背包信息 **(Dict[int, ItemType])**  
    * 属性**EnderChestInventory**  : 玩家背包信息 **(Dict[int, ItemType])**  
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_nbt** : 通过NBT对象生成实体对象
    * 可用方法**to_nbt** : 通过实体对象生成NBT对象
    """

    def __str__(self) :
        return "<Player Id='%s' UniqueID=%s>" % (self.Identifier, self.UniqueID)
    
    def __setattr__(self, name:str, value) :
        if name == "GameMode" and isinstance(value, int) : super(EntityType, self).__setattr__(name, ctypes.c_int32(value).value)
        elif name == "Dimension" and isinstance(value, int) : super(EntityType, self).__setattr__(name, ctypes.c_int32(value).value)
        else : super().__setattr__(name, value)
    
    def __init__(self, id:str, pos:Tuple[int, int, int]=[0, 0, 0], rotation:Tuple[int, int]=[0,0]) :
        from . import ItemType
        self.GameMode = 1
        self.Dimension = 0
        self.LevelData:Dict[Literal["Level", "Progress"], int] = {"Level":0, "Progress":0}
        self.SpawnLocation:Dict[Literal["Dimension", "X", "Y", "Z"], int] = {"Dimension":0, "X":0, "Y":0, "Z":0}
        self.Inventory:Dict[int, ItemType] = {}
        self.EnderChestInventory:Dict[int, ItemType] = {}
        
        super().__init__(id, pos, rotation)

    @classmethod
    def from_nbt(cls, nbt_data:nbt.TAG_Compound) :
        from . import ItemType
        EntityObject = cls("minecraft:player")
        EntityObject = super().from_nbt(nbt_data, EntityObject)
        EntityObject.GameMode = nbt_data["PlayerGameMode"].value
        EntityObject.Dimension = nbt_data["DimensionId"].value
        EntityObject.LevelData["Level"] = nbt_data["PlayerLevel"].value
        EntityObject.LevelData["Progress"] = nbt_data["PlayerLevelProgress"].value
        EntityObject.SpawnLocation["Dimension"] = nbt_data["SpawnDimension"].value
        EntityObject.SpawnLocation["X"] = nbt_data["SpawnX"].value
        EntityObject.SpawnLocation["Y"] = nbt_data["SpawnY"].value
        EntityObject.SpawnLocation["Z"] = nbt_data["SpawnZ"].value

        for ContainerID in ["Inventory", "EnderChestInventory"] :
            Contanier = getattr(EntityObject, ContainerID)
            for sub_item in nbt_data.get(ContainerID, []) :
                if not("Name" in sub_item and "Slot" in sub_item) : continue
                try : int(sub_item["Slot"].value)
                except : continue
                SubItemObject = ItemType.from_nbt(sub_item)
                if SubItemObject : Contanier[int(sub_item["Slot"].value)] = SubItemObject
        EntityObject.Mainhand = EntityObject.Inventory.get(nbt_data.get(
            "SelectedInventorySlot", ctypes.c_uint8(0)).value, None)

        Entity = super().from_nbt(nbt_data, EntityObject)
        ExceptKey = {"PlayerGameMode", "DimensionId", "PlayerLevel", "PlayerLevelProgress", "SpawnDimension",
            "SpawnX", "SpawnY", "SpawnZ", "Inventory", "EnderChestInventory"}
        for key in list(Entity.ExtraNBT.keys()) :
            if key in ExceptKey : del Entity.ExtraNBT[key]
        
        return Entity
    
    def to_nbt(self):
        NbtObject = super().to_nbt()

        NbtObject["PlayerGameMode"] = nbt.TAG_Int(self.GameMode)
        NbtObject["DimensionId"] = nbt.TAG_Int(self.Dimension)
        NbtObject["PlayerLevel"] = nbt.TAG_Int(self.LevelData["Level"])
        NbtObject["PlayerLevelProgress"] = nbt.TAG_Float(self.LevelData["Progress"])
        NbtObject["SpawnDimension"] = nbt.TAG_Int(self.SpawnLocation["Dimension"])
        NbtObject["SpawnX"] = nbt.TAG_Int(self.SpawnLocation["X"])
        NbtObject["SpawnY"] = nbt.TAG_Int(self.SpawnLocation["Y"])
        NbtObject["SpawnZ"] = nbt.TAG_Int(self.SpawnLocation["Z"])

        for ContainerID in ["Inventory", "EnderChestInventory"] :
            Contanier = getattr(self, ContainerID)
            if not Contanier : continue
            NbtObject[ContainerID] = nbt.TAG_List([], type=nbt.TAG_Compound )
            for slot, item in Contanier.items() :
                ItemNbt = item.to_nbt()
                ItemNbt["Slot"] = nbt.TAG_Byte( ctypes.c_int8(slot).value )
                NbtObject[ContainerID].append( ItemNbt )

        return NbtObject

    def copy(self):
        raise RuntimeError("玩家对象无法被拷贝")


def NBTtoEntity(nbt_data: Union[bytes, nbt.TAG_Compound]) :
    if isinstance(nbt_data, nbt.TAG_Compound) : nbt_data = nbt.read_from_nbt_file(nbt_data).get_tag()
    if not len( nbt_data.get("identifier", "") ) : return None

    id = nbt_data["identifier"].value
    EntityID = f"minecraft:{id}" if ":" not in id else id
    if EntityID == "minecraft:player" : return PlayerType.from_nbt( nbt_data )
    elif EntityID == "minecraft:item" : return ItemEntityType.from_nbt( nbt_data )
    elif EntityID in NotMobEntityList : return EntityType.from_nbt( nbt_data )
    else : return MobType.from_nbt( nbt_data )

