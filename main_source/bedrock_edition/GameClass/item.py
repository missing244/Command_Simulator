from typing import List, Dict, Union, Literal, Tuple, TypedDict, Generator, Set, Optional
from . import nbt, MinecraftSimulator, MCBELab
from .. import Constants, python_numpy as np



if "ItemComponent" :

    class ItemComponent :

        def __init__(self, item:"ItemStack") :
            self.Item = item

        def __eq__(self, other:"ItemComponent") -> bool :
            return True

        def from_nbt(self, nbt_obj:nbt.TAG_Compound) : 
            return self

        def to_nbt(self, nbt_obj:nbt.TAG_Compound) : 
            return None

    class ItemDurabilityComponent(ItemComponent) :
        
        Identifier = "minecraft:durability"

        def __init__(self, item:"ItemStack"):
            super().__init__(item)
            self.Damage = np.int32(0)
            self.Unbreakable:bool = False

        def __eq__(self, other) :
            if not isinstance(other, self.__class__) : return False
            test1 = self.Damage == other.Damage
            test2 = self.Unbreakable == other.Unbreakable
            return test1 and test2

        @property
        def MaxDurability(self) :
            ItemDef = self.Item.context.GameSource.ITEM
            damage = ItemDef.get(self.Item.Identifier, {}).get("damage", None)
            if not isinstance(damage, int) : damage = None
            return damage


        def from_nbt(self, nbt_obj) :
            tags:nbt.TAG_Compound = nbt_obj.get("tag", nbt.TAG_Compound())
            damage = tags.get("Damage")
            if isinstance(damage, nbt.TAG_Short) : self.Damage = np.int16(damage.value)
            unbreakable = tags.get("Unbreakable")
            if isinstance(unbreakable, nbt.TAG_Byte) : self.Unbreakable = bool(unbreakable.value)
            return self

        def to_nbt(self, nbt_obj):
            if "tag" not in nbt_obj : nbt_obj["tag"] = nbt.TAG_Compound()
            nbt_obj["tag"]["Damage"] = nbt.TAG_Short(self.Damage.value)
            nbt_obj["tag"]["Unbreakable"] = nbt.TAG_Byte(self.Unbreakable)

    class ItemEnchantableComponent(ItemComponent) :

        Identifier = "minecraft:enchantable"
    
        def __init__(self, item:"ItemStack") :
            super().__init__(item)
            self.__Ench:Dict[str, int] = {}

        def __eq__(self, other) :
            if not isinstance(other, self.__class__) : return False
            test1 = self.__Ench == other.__Ench
            return test1

        def from_nbt(self, nbt_obj) :
            tags:nbt.TAG_Compound = nbt_obj.get("tag", nbt.TAG_Compound())
            ench = tags.get("ench")
            if isinstance(ench, nbt.TAG_Compound) :
                for k, v in ench.items() : self.__Ench[k] = v.value if isinstance(v, nbt.TAG_Short) else 0
            return self
                
        def to_nbt(self, nbt_obj) :
            if "tag" not in nbt_obj : nbt_obj["tag"] = nbt.TAG_Compound()
            nbt_obj["tag"]["ench"] = nbt.TAG_Compound({k:nbt.TAG_Short(v) for k, v in self.__Ench.items()})

        def can_add_enchantment(self, enchant_id:str, lvl:int) :
            ItemDef = self.Item.context.GameSource.ITEM.get(self.Item.Identifier, {})
            test = enchant_id in ItemDef.get("can_enchant", ()) 
            if not test : return False

            EnchMax = Constants.ENCHANT[enchant_id]["max_lvl"]
            if lvl > EnchMax : return False
            if self.__Ench.get(enchant_id, 0) : return False
            return True

        def has_enchantment(self, enchant_id:str) :
            return enchant_id in self.__Ench

        def set_enchantment_level(self, enchant_id:str, lvl:int) -> bool :
            """直接设置附魔等级（允许覆盖已有等级），参数非法时返回 False"""
            EnchantData = Constants.ENCHANT.get(enchant_id, None)
            if EnchantData is None : return False
            if not(1 <= lvl <= EnchantData["max_lvl"]) : return False
            self.__Ench[enchant_id] = lvl
            return True

        def add_enchantment(self, enchant_id:str, lvl:int) :
            if not self.can_add_enchantment(enchant_id, lvl) : return False
            self.__Ench[enchant_id] = lvl
            return True

        def remove_enchantment(self, enchant_id:str) :
            if enchant_id not in self.__Ench : return False
            del self.__Ench[enchant_id]
            return True


class ItemStack :

    context:MinecraftSimulator = None

    def __repr__(self) -> str:
        return "<Item %s, %s>" % (self.Identifier, self.Count)

    def __str__(self) -> str :
        return self.Identifier

    def __init__(self, id:str, amount:int=1, damage:int=0) :
        from .block import BlockPermutation
        id = MCBELab.UpgradeItem(id)
        self.Identifier = id if id.startswith("minecraft:") else f"minecraft:{id}"
        self.Count = np.int8(amount)
        self.Damage = np.int16(damage)
        self.KeepOnDeath:bool = False
        self.LockMode:Literal["none", "inventory", "slot"] = "none"
        self.CanDestroy:List[str] = []
        self.CanPlaceOn:List[str] = []
        self.BlockPermutation:BlockPermutation = None
        self.__Component:Dict[str, ItemComponent] = {}

        BlockID, BlockState = MCBELab.TransforBlock(self.Identifier, damage)
        BlockDef = self.context.GameSource.BLOCK.get(BlockID, None)
        if BlockDef is not None : 
            self.Identifier = BlockID
            Permutation = self.context.SimulatorModule.BlockPermutation
            self.BlockPermutation = Permutation(BlockID, BlockState)
            
        ItemDef = self.context.GameSource.ITEM.get(self.Identifier, {})
        if "damage" in ItemDef : 
            component = ItemDurabilityComponent(self)
            self.__Component[component.Identifier] = component
        if "can_enchant" in ItemDef : 
            component = ItemEnchantableComponent(self)
            self.__Component[component.Identifier] = component

    @property
    def MaxCount(self) -> int:
        ItemDef = self.context.GameSource.ITEM
        return ItemDef.get(self.Identifier, {}).get("max_count", 64)


    def has_component(self, component_id:Union[str, ItemComponent]) -> bool :
        if hasattr(component_id, "Identifier") :
            return component_id.Identifier in self.__Component
        else : return component_id in self.__Component

    def get_component(self, component_id:Union[str, ItemComponent]) -> Optional[ItemComponent]:
        if hasattr(component_id, "Identifier") :
            return self.__Component.get(component_id.Identifier)
        else : return self.__Component.get(component_id)

    def get_components(self) -> List[ItemComponent] :
        return list(self.__Component.values())

    def compatible_with(self, item_stack:"ItemStack") -> bool :
        if self is item_stack: return False
        if self.MaxCount == 1 or item_stack.MaxCount == 1: return False          #任一物品不可堆叠（最大堆叠数为1）
        if self.Identifier != item_stack.Identifier: return False                #检查物品 ID
        if self.Damage != item_stack.Damage: return False                        #检查物品数据值
        if self.BlockPermutation != item_stack.BlockPermutation: return False    #检查物品方块映射

        all_component = [ItemDurabilityComponent, ItemEnchantableComponent]
        comp_not_same = False
        for comp_id in all_component :
            comp_self = self.get_component(comp_id)
            comp_other = item_stack.get_component(comp_id)
            if (comp_self is None) != (comp_other is None): return False
            if comp_self != comp_other : comp_not_same = True ; break
        if comp_not_same : return False
        return True

    def stackable_with(self, item_stack:"ItemStack") -> bool :
        """
        检查此物品堆叠是否可以与给定的 ItemStack 堆叠。
        此判断基于物品类型、自定义数据和属性。
        如果可以堆叠则修改双方对象数量，需要考虑最大堆叠。
        对于不可堆叠的物品始终返回 False。
        """ 
        if not self.compatible_with(item_stack) : return False
        if self.Count <= 0 or item_stack.Count <= 0: return False           #检查物品数量

        # 合并逻辑
        max_stack = min(self.MaxCount, item_stack.MaxCount)  # 实际应一致
        total = self.Count.value + item_stack.Count.value

        if total <= max_stack:  # 全部合并到 self
            self.Count = np.int8(total)
            item_stack.Count = np.int8(0)
        else : # 填满 self，剩余留在 item_stack
            self.Count = np.int8(max_stack)
            item_stack.Count = np.int8(total - max_stack)

        return True

    def copy(self) -> "ItemStack" :
        new_item = self.__class__(self.Identifier, int(self.Count), int(self.Damage))
        new_item.KeepOnDeath = self.KeepOnDeath
        new_item.LockMode = self.LockMode
        new_item.CanDestroy = self.CanDestroy.copy()
        new_item.CanPlaceOn = self.CanPlaceOn.copy()

        nbt_obj = nbt.TAG_Compound()
        for _comp in self.get_components(): _comp.to_nbt(nbt_obj)
        for _comp in new_item.get_components(): _comp.from_nbt(nbt_obj)

        return new_item


    def serialization(self) :
        root = nbt.TAG_Compound()
        root["Name"] = nbt.TAG_String(self.Identifier)
        root["Count"] = nbt.TAG_Byte(self.Count.value)
        root["Damage"] = nbt.TAG_Short(self.Damage.value)
        root["KeepOnDeath"] = nbt.TAG_Byte(self.KeepOnDeath)
        root["LockMode"] = nbt.TAG_String(self.LockMode)
        root["tag"] = nbt.TAG_Compound()
        if self.BlockPermutation is not None : 
            root["BlockPermutation"] = self.BlockPermutation.serialization()
        
        destroy_list = nbt.TAG_List([], type=nbt.TAG_String)
        for block_id in self.CanDestroy: destroy_list.append(nbt.TAG_String(block_id))
        root["CanDestroy"] = destroy_list
        place_list = nbt.TAG_List([], type=nbt.TAG_String)
        for block_id in self.CanPlaceOn: place_list.append(nbt.TAG_String(block_id))
        root["CanPlaceOn"] = place_list

        for component in self.__Component.values(): component.to_nbt(root)

        return root

    @classmethod
    def deserialization(cls, nbt_obj:nbt.TAG_Compound) -> Optional["ItemStack"] :
        Permutation = cls.context.SimulatorModule.BlockPermutation
        if "Name" not in nbt_obj or nbt_obj["Name"].value == "minecraft:air": return None

        self = cls(nbt_obj["Name"].value)
        self.Count = np.int8(nbt_obj.get("Count", nbt.TAG_Byte(1)).value)
        self.Damage = np.int16(nbt_obj.get("Damage", nbt.TAG_Byte(0)).value)
        self.KeepOnDeath = bool(nbt_obj.get("KeepOnDeath", nbt.TAG_Byte(0)).value)
        self.LockMode = nbt_obj.get("LockMode", nbt.TAG_String("none")).value
        self.CanDestroy = [v.value for v in nbt_obj.get("CanDestroy", []) if isinstance(v.value, str)]
        self.CanPlaceOn = [v.value for v in nbt_obj.get("CanPlaceOn", []) if isinstance(v.value, str)]
        self.BlockPermutation = Permutation.deserialization(nbt_obj.get("BlockPermutation", {}))
        if self.LockMode not in {"none", "inventory", "slot"} : self.LockMode = "none"

        for _comp in self.get_components() : _comp.from_nbt(nbt_obj)

        return self

