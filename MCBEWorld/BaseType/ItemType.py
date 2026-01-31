from .. import nbt
from . import ModifyError, ValueError
from typing import Tuple,List,Union,Dict,Literal
import array, random, ctypes, copy, traceback

EnchantEmun = {'protection': 0, 'fire_protection': 1, 'feather_falling': 2, 'blast_protection': 3, 'projectile_protection': 4,
    'thorns': 5, 'respiration': 6, 'depth_strider': 7, 'aqua_affinity': 8, 'sharpness': 9, 'smite': 10, 'bane_of_arthropods': 11, 
    'knockback': 12, 'fire_aspect': 13, 'looting': 14, 'efficiency': 15, 'silk_touch': 16, 'unbreaking': 17, 'fortune': 18, 
    'power': 19, 'punch': 20, 'flame': 21, 'infinity': 22, 'luck_of_the_sea': 23, 'lure': 24, 'frost_walker': 25, 'mending': 26, 
    'binding': 27, 'vanishing': 28, 'impaling': 29, 'riptide': 30, 'loyalty': 31, 'channeling': 32, 'multishot': 33, 'piercing': 34, 
    'quick_charge': 35, 'soul_speed': 36, 'swift_sneak': 37, 'wind_burst': 38, 'density': 39, 'breach': 40}



class ItemType :
    """
    ## 基岩版物品对象
    * 属性**Identifier**   : 物品英文ID **(str)**
    * 属性**Count**        : 物品数量 **(int)**
    * 属性**DataValue**    : 物品数据值 **(int)**
    * 属性**CanDestroy**   : 物品在冒险模式可摧毁的方块 **(List[str])**
    * 属性**CanPlaceOn**   : 物品在冒险模式可放置方块 **(List[str])**
    * 属性**Name**         : 物品自定义名称 **(str)**
    * 属性**Lore**         : 物品自定义描述 **(List[str])**
    * 属性**Damage**       : 物品破损度 **(int)**
    * 属性**Enchantment**  : 物品的附魔数据 **(Dict[str, int])**
    * 属性**ItemLockMode** : 物品在玩家物品栏中被锁定的模式 **(None|"lock_in_slot"|"lock_in_inventory")**
    * 属性**KeepOnDeath**  : 物品在玩家死亡时是否保留 **(int)**
    * 属性**Items**        : 物品容器数据 **Dict[int, ItemType]**
    * 属性**ExtraNBT**     : 额外的NBT数据 **(nbt.TAG_Compound)**  
    --------------------------------------------------------------------------------------------
    * 可用类方法**from_nbt** : 通过NBT对象生成物品对象
    * 可用方法**to_nbt** : 通过物品对象生成NBT对象
    * 可用方法**copy** : 复制并生成一个独立的物品对象
    --------------------------------------------------------------------------------------------
    * 物品的附魔数据的Dict中的Key需要以下ID: 
    'protection', 'fire_protection', 'feather_falling', 'blast_protection', 'projectile_protection', 
    'thorns', 'respiration', 'depth_strider', 'aqua_affinity', 'sharpness', 'smite', 'bane_of_arthropods', 
    'knockback', 'fire_aspect', 'looting', 'efficiency', 'silk_touch', 'unbreaking', 'fortune', 'power', 
    'punch', 'flame', 'infinity', 'luck_of_the_sea', 'lure', 'frost_walker', 'mending', 'binding', 'vanishing', 
    'impaling', 'riptide', 'loyalty', 'channeling', 'multishot', 'piercing', 'quick_charge', 'soul_speed', 
    'swift_sneak', 'wind_burst', 'density', 'breach'
    """

    def __str__(self) :
        return "<Item Id='%s' Count=%s>" % (self.Identifier, self.Count)
    
    def __repr__(self):
        return self.__str__()

    def __setattr__(self, name:str, value):
        try : self.__initialize
        except : super().__setattr__(name, value) ; return None
        ItemLockMode = [None, "lock_in_slot", "lock_in_inventory"]

        if name == "Identifier" and isinstance(value, str) : super().__setattr__(name, 
            f"minecraft:{value}" if not ":" not in value else value)
        elif name == "Count" and isinstance(value, int) : super().__setattr__(name, ctypes.c_int8(value).value)
        elif name == "DataValue" and isinstance(value, int) : super().__setattr__(name, ctypes.c_int16(value).value)
        elif name == "Damage" and isinstance(value, int) : super().__setattr__(name, ctypes.c_int16(value).value)
        elif name == "Name" and isinstance(value, str) : super().__setattr__(name, value)
        elif name == "ItemLockMode" and value in {0, 1, 2} : super().__setattr__(name, ItemLockMode[value])
        elif name == "ItemLockMode" and value in set(ItemLockMode) : super().__setattr__(name, value)
        elif name == "KeepOnDeath" and isinstance(value, bool) : super().__setattr__(name, bool(value))
        elif hasattr(self, name) : raise ValueError("属性%s不允许赋值支持以外的数值" % name)
        else : raise ModifyError("属性%s不允许修改" % name)

    def __delattr__(self, name):
        raise ModifyError("不允许删除%s属性" % name)
        
    def __init__(self, id:str, count:int=1, data_value:int=0) :
        self.Identifier:str = f"minecraft:{id}" if ":" not in id else id
        self.Count:int = ctypes.c_int8(count).value
        self.DataValue:int = ctypes.c_int16(data_value).value
        self.CanDestroy:List[str] = []
        self.CanPlaceOn:List[str] = []
        self.Name:str = ""
        self.Lore:List[str] = []
        self.Damage:int = 0
        self.Enchantment:Dict[str, int] = {}
        self.ItemLockMode:Literal[None, "lock_in_slot", "lock_in_inventory"] = None
        self.KeepOnDeath:bool = False
        self.Items:Dict[int, "ItemType"] = {}
        self.ExtraNBT:nbt.TAG_Compound = nbt.TAG_Compound()
        self.__initialize = True


    @classmethod
    def from_nbt(cls, nbt_data:nbt.TAG_Compound) :
        if not isinstance(nbt_data, nbt.TAG_Compound) or not len(nbt_data.get("Name", "")) : return None
        Identifier = nbt_data["Name"].value
        DataValue = nbt_data.get("Damage", ctypes.c_int8(0)).value
        Count = nbt_data.get("Count", ctypes.c_int8(0)).value
        ItemObject = cls(Identifier, Count, DataValue)
        ItemObject.CanDestroy.extend(str(i.value) for i in nbt_data.get("CanDestroy", ()))
        ItemObject.CanPlaceOn.extend(str(i.value) for i in nbt_data.get("CanPlaceOn", ()))
        for sub_item in nbt_data.get("tag", {}).get("Items", []) :
            if not("Name" in sub_item and "Slot" in sub_item) : continue
            try : int(sub_item["Slot"].value)
            except : continue
            SubItemObject = cls.from_nbt(sub_item)
            if SubItemObject : ItemObject.Items[int(sub_item["Slot"].value)] = SubItemObject
        EnchantList = list(EnchantEmun.keys())
        for sub_ench in nbt_data.get("tag", {}).get("ench", []) :
            if not("id" in sub_ench and "lvl" in sub_ench) : continue
            try : ench_id, ench_lvl = int(sub_ench["id"].value), ctypes.c_int16(sub_ench["lvl"].value).value
            except : continue
            if ench_id > max(EnchantEmun.values()) : continue
            ItemObject.Enchantment[ EnchantList[ench_id] ] = ench_lvl

        try : ItemObject.Name = nbt_data["tag"]["display"]["Name"].value
        except : pass
        try : ItemObject.Lore.extend(str(i.value) for i in nbt_data["tag"]["display"]["Lore"])
        except : pass
        try : ItemObject.Damage = nbt_data["tag"]["Damage"].value
        except : pass
        try : ItemObject.ItemLockMode = nbt_data["tag"]["minecraft:item_lock"].value
        except : pass
        try : ItemObject.KeepOnDeath = bool(nbt_data["tag"]["minecraft:keep_on_death"].value)
        except : pass

        ExceptKey = {"Items", "ench", "display", "Damage", "minecraft:item_lock", "minecraft:keep_on_death"}
        for key, value in nbt_data.get("tag", {}).items() :
            if key in ExceptKey : continue
            ItemObject.ExtraNBT[key] = value.copy()

        return ItemObject

    def to_nbt(self) -> nbt.TAG_Compound :
        node = nbt.NBT_Builder()
        NBTObject = node.compound(
            Name = node.string( self.Identifier ),
            Count = node.byte( self.Count ),
            Damage = node.short( self.DataValue ),
            WasPickedUp = node.byte(0),
            CanDestroy = node.list( *[node.string(i) for i in self.CanDestroy if isinstance(i, str)] ),
            CanPlaceOn = node.list( *[node.string(i) for i in self.CanPlaceOn if isinstance(i, str)] ),
            tag = node.compound(
                display=node.compound(),
                Damage=node.short(self.Damage),
                **{"minecraft:keep_on_death": node.byte(self.KeepOnDeath)},
            )
        ).build()
        if self.Name : NBTObject["tag"]["display"]["Name"] = nbt.TAG_String(self.Name)
        if self.Lore : NBTObject["tag"]["display"]["Lore"] = nbt.TAG_List(
            [nbt.TAG_String(i) for i in self.Lore if isinstance(i, str)], type=nbt.TAG_String )
        if self.Enchantment : 
            NBTObject["tag"]["ench"] = nbt.TAG_List([ nbt.TAG_Compound(
                {"id":nbt.TAG_Short(EnchantEmun[i]), "lvl":nbt.TAG_Short(ctypes.c_int16(j).value)} )
                for i,j in self.Enchantment.items() if i in EnchantEmun], type=nbt.TAG_Compound )
        if self.ItemLockMode : 
            ItemLockMode = {"lock_in_slot":1, "lock_in_inventory":2}
            NBTObject["tag"]["minecraft:item_lock"] = nbt.TAG_Byte( ItemLockMode[self.ItemLockMode] )
        if self.Items :
            NBTObject["tag"]["Items"] = nbt.TAG_List([], type=nbt.TAG_Compound )
            for slot, item in self.Items.items() :
                ItemNbt = item.to_nbt()
                ItemNbt["Slot"] = nbt.TAG_Byte( ctypes.c_int8(slot).value )
                NBTObject["tag"]["Items"].append( ItemNbt )
        for key, value in self.ExtraNBT.items() :
            NBTObject["tag"][key] = value.copy()

        return NBTObject

    def copy(self) -> "ItemType" :
        ItemObject = self.__class__()
        for key, value in self.__dict__.items() :
            if key.startswith("_") : continue
            if key == "Items" : continue
            ItemObject[key] = value.copy() if hasattr(value, "copy") else value
        for key, value in self.Items.items() : ItemObject.Items[key] = value.copy()
        for key, value in self.ExtraNBT.items() : ItemObject.ExtraNBT[key] = value.copy()
        return ItemObject




NoneItemNBT = ItemType("", 0, 0).to_nbt()
NoneItemNBT["Name"] = nbt.TAG_String()
del NoneItemNBT["tag"]
del NoneItemNBT["CanDestroy"]
del NoneItemNBT["CanPlaceOn"]
