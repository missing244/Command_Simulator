from . import nbt, MCBELab, MinecraftSimulator
from .. import Constants, python_numpy as np
import random, copy, types, os, json, math, array, itertools, functools
from typing import List, Dict, Union, Literal, Tuple, TypedDict, Generator, Set, Optional

ContainerNBT_ID = {"minecraft:chest": 27, "minecraft:trapped_chest": 27, "minecraft:lit_blast_furnace": 4, 
    "minecraft:hopper": 5, "minecraft:shulker_box": 27, "minecraft:undyed_shulker_box": 27, 
    "minecraft:barrel": 27, "minecraft:dispenser": 9, "minecraft:dropper": 9, "minecraft:furnace": 4, 
    "minecraft:lit_furnace": 4, "minecraft:smoker": 4, "minecraft:lit_smoker": 4, "minecraft:blast_furnace": 4, 
    "minecraft:crafter":9, "minecraft:copper_chest": 27, "minecraft:exposed_copper_chest": 27,
    "minecraft:weathered_copper_chest": 27, "minecraft:oxidized_copper_chest": 27,
    "minecraft:waxed_copper_chest": 27, "minecraft:waxed_exposed_copper_chest": 27,
    "minecraft:waxed_weathered_copper_chest": 27, "minecraft:waxed_oxidized_copper_chest": 27,
    "minecraft:chiseled_bookshelf":6, "minecraft:decorated_pot":1}
CommandBlockID = {"minecraft:command_block", "minecraft:repeating_command_block", "minecraft:chain_command_block"}



if "BlockComponent" :

    class BlockComponent :

        def __init__(self, block:"Block") :
            self.Block = block

        def copy(self) : 
            return self

        def from_nbt(self, nbt_obj:nbt.TAG_Compound) : 
            return None

        def to_nbt(self, nbt_obj:nbt.TAG_Compound) : 
            return None

    class BlockInventoryComponent(BlockComponent) :

        Identifier = "minecraft:inventory"
        
        def __init__(self, block:"Block") :
            from .sundries_type import Container
            super().__init__(block)
            self.Container = Container()
            self.Container.Size = ContainerNBT_ID.get(block.Permutation.name, 0)

        def from_nbt(self, nbt_obj) :
            items_tag = nbt_obj.get("Items")
            if not isinstance(items_tag, nbt.TAG_List) : return self
            self.Container.clear_all()
            ItemStack = self.Block.Permutation.context.SimulatorModule.ItemStack

            for entry in items_tag :
                slot_tag = entry.get("Slot")
                if slot_tag is None: continue
                slot = slot_tag.value
                if not(0 <= slot < self.Container.Size): continue

                item_tag = entry.get("Item")
                if item_tag is None: continue

                item = ItemStack.deserialization(item_tag)
                if item is not None: self.Container.set_item(slot, item)

            return self

        def to_nbt(self, nbt_obj) :
            items_list = nbt.TAG_List([], type=nbt.TAG_Compound)
            for slot, item in enumerate(self.Container.Items):
                item_data = nbt.TAG_Compound()
                item_data["Slot"] = nbt.TAG_Byte(slot)
                if item is not None : item_data["Item"] = item.serialization()
                items_list.append(item_data)
            nbt_obj["Items"] = items_list

    class BlockCommandComponent(BlockComponent) :
        
        Identifier = "minecraft:command"

        def __init__(self, block:"Block") :
            super().__init__(block)
            self.Command = ""                    # 字符串
            self.SuccessCount = 0                # 整型
            self.CustomName = ""                 # 字符串
            self.LastExecution = 0               # 长整型（用 int 表示）
            self.TickDelay = 0                   # 整型
            self.Auto = False                    # 布尔型

        def to_nbt(self, nbt_obj:nbt.TAG_Compound) -> None:
            """将组件数据序列化到 NBT 复合标签"""
            nbt_obj["Command"] = nbt.TAG_String(self.Command)
            nbt_obj["SuccessCount"] = nbt.TAG_Int(self.SuccessCount)
            nbt_obj["CustomName"] = nbt.TAG_String(self.CustomName)
            nbt_obj["LastExecution"] = nbt.TAG_Long(self.LastExecution)
            nbt_obj["TickDelay"] = nbt.TAG_Int(self.TickDelay)
            nbt_obj["Auto"] = nbt.TAG_Byte(self.Auto)

        def from_nbt(self, nbt_obj:nbt.TAG_Compound) -> "BlockCommandComponent":
            """从 NBT 复合标签读取数据，更新组件状态"""
            command_tag = nbt_obj.get("Command")
            if isinstance(command_tag, nbt.TAG_String): self.Command = command_tag.value
            success_tag = nbt_obj.get("SuccessCount")
            if isinstance(success_tag, nbt.TAG_Int): self.SuccessCount = success_tag.value
            name_tag = nbt_obj.get("CustomName")
            if isinstance(name_tag, nbt.TAG_String): self.CustomName = name_tag.value
            last_tag = nbt_obj.get("LastExecution")
            if isinstance(last_tag, nbt.TAG_Long): self.LastExecution = last_tag.value
            delay_tag = nbt_obj.get("TickDelay")
            if isinstance(delay_tag, nbt.TAG_Int): self.TickDelay = delay_tag.value
            auto_tag = nbt_obj.get("Auto")
            if isinstance(auto_tag, nbt.TAG_Byte): self.Auto = bool(auto_tag.value)

            return self

class Block:
    """表示维度中的一个方块"""

    def __init__(self):
        from .dimension import Dimension
        self.x = 0
        self.y = 0
        self.z = 0
        self.Dimension:Dimension = None
        self.Permutation:BlockPermutation = None
        self.__Component: Dict[str, BlockComponent] = {}

    def __str__(self):
        return f"<Block Pos={(self.x, self.y, self.z)} Permutation={self.Permutation}>"

    def __setattr__(self, name, value) :
        if  name == "Permutation" and isinstance(value, BlockPermutation) :
            super().__setattr__(name, value)
            self.__Component.clear()
            if value.name in ContainerNBT_ID :
                comp = BlockInventoryComponent(self)
                self.__Component[comp.Identifier] = comp
            if value.name in CommandBlockID :
                comp = BlockCommandComponent(self)
                self.__Component[comp.Identifier] = comp
            return None
        if name in {"x", "y", "z"} : value = math.floor(value)
        super().__setattr__(name, value)

    @property
    def is_air(self) -> bool:
        return self.Permutation.name == "minecraft:air"
    
    @property
    def is_liquid(self) -> bool:
        return self.Permutation.name in {"minecraft:water", "minecraft:lava"}


    def has_component(self, component_id:Union[str, BlockComponent]) -> bool :
        if hasattr(component_id, "Identifier") :
            return component_id.Identifier in self.__Component
        else : return component_id in self.__Component

    def get_component(self, component_id:Union[str, BlockComponent]) -> Optional[BlockComponent]:
        if hasattr(component_id, "Identifier") :
            return self.__Component.get(component_id.Identifier)
        else : return self.__Component.get(component_id)

    def get_components(self) -> List[BlockComponent] :
        return list(self.__Component.values())


    def serialization(self) :
        node = nbt.NBT_Builder()
        nbt_data = node.compound(
            x = node.int(self.x),
            y = node.int(self.y),
            z = node.int(self.z) ).build()
        for _comp in self.__Component.values() : _comp.from_nbt(nbt_data)
        return nbt_data

    def deserialization(self, nbt_data:nbt.TAG_Compound) :
        if "x" not in nbt_data or "y" not in nbt_data or "z" not in nbt_data :
            return None
        self.x = nbt_data["x"].value
        self.y = nbt_data["y"].value
        self.z = nbt_data["z"].value
        for _comp in self.__Component.values() : _comp.from_nbt(nbt_data)
        return self

class BlockPermutation :
    """
    通用方块对象
    ---------------------------------
    * 实现了哈希接口的方块对象
    ---------------------------------
    * 实例化参数 name : 方块ID字符串，如无命名空间则自动添加命名空间
    * 实例化参数 states : 方块状态传参，支持整数、方块状态字符串、方块状态字典
    * states 会自动舍去无效的状态参数
    ---------------------------------
    * 可用类方法 from_nbt: 将 {name:"a", states:{color:"red"}} 的方块nbt转换为方块对象
    * 可用方法 to_nbt: 生成 方块对象 对应的nbt对象
    """

    context:MinecraftSimulator = None

    def __str__(self):
        return f'<BlockPermutation name="{self.name}" states={self.states}>'
    
    def __repr__(self):
        return f'<Block name="{self.name}" states={self.states}>'
    
    def __delattr__(self, name):
        raise Exception("无法删除任何属性")
    
    def __setattr__(self, name, value):
        if hasattr(self, name) : raise Exception("无法修改任何属性")
        super().__setattr__(name, value)
    

    def __hash__(self):
        return self.__hash

    def __eq__(self, value):
        if not isinstance(value, BlockPermutation): return False
        return value.__hash__()  == self.__hash


    def __init__(self, name:str, states:Union[int, str, Dict[str, Union[bool, int, str]]]={}) :
        BlockID, BlockState = MCBELab.TransforBlock(name, states)
        BlockDef = self.context.GameSource.BLOCK.get(BlockID, None)
        if  BlockDef is not None :
            StateTest = BlockDef.get("block_state", {})
            if isinstance(states, int) : 
                for k,v in StateTest.items() : BlockState[k] = v[0]
            else :
                if isinstance(states, dict) : NewState = states
                else : NewState = MCBELab.block.BE_BlockStates_Parser(states)
                for k,v in NewState.items() : 
                    if k in StateTest and v in StateTest[k] : BlockState[k] = v
                    elif k in StateTest : BlockState[k] = StateTest[k][0]
        BlockID, BlockState = MCBELab.UpgradeBlock(BlockID, BlockState)

        self.name = BlockID
        self.states = types.MappingProxyType(BlockState)
        self.__hash = (self.name, *self.states.items()).__hash__()


    def serialization(self) :
        node = nbt.NBT_Builder()
        dict1 = {}
        for i,j in self.states.items() :
            if j.__class__ is bool : dict1[i] = node.byte(j)
            elif j.__class__ is int : dict1[i] = node.int(j)
            elif j.__class__ is str : dict1[i] = node.string(j)
        return node.compound(name=node.string(self.name), states=node.compound(**dict1)).build()

    @classmethod
    def deserialization(cls, nbt_obj:nbt.TAG_Compound) :
        if not isinstance(nbt_obj.get("name", None), nbt.TAG_String) : return None
        dict1 = {}
        for i,j in nbt_obj.get("states", nbt.TAG_Compound()).items() :
            if j.__class__ is nbt.TAG_String : dict1[i] = j.value
            elif j.__class__ is nbt.TAG_Int : dict1[i] = j.value
            elif j.__class__ is nbt.TAG_Byte : dict1[i] = bool(j.value)
        return cls(nbt_obj["name"].value, dict1)


