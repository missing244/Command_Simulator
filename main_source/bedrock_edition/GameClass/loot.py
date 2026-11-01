from typing import List, Dict, Union, Optional
from . import MinecraftSimulator
from .. import Constants, python_numpy as np
import random

from .block import Block
from .entity import Entity, Player, EntityLootComponent
from .item import ItemStack, ItemEnchantableComponent, ItemDurabilityComponent


class LootTableManager :

    def __init__(self, main_thread:"MinecraftSimulator") -> None :
        self.MainThread = main_thread
        self.ItemStack = self.MainThread.SimulatorModule.ItemStack
        self.LootBlock = Constants.BLOCK_LOOT
        self.LootTable = self.MainThread.GameSource.LOOT_TABLE
        self.BlockDef = self.MainThread.GameSource.BLOCK

    def __table_normalize__(self, table_name:str) :
        table_name = table_name.replace("loot_tables/", "", 1) if table_name.startswith("loot_tables/") else table_name
        table_name = table_name[:-5] if table_name.endswith(".json") else table_name
        return table_name


    def loot_from_block(self, block:Block, tool:ItemStack=None) -> List[ItemStack] :

        def condition_test(rule:Dict[str, Union[str, dict]]):
            condition:Dict[str, Union[str, dict]] = global_condition[ rule["condition"] ]
            for k, v in condition.items() :
                if k == "enchantment" : 
                    if not isinstance(tool, ItemStack) : return False
                    Enchat:ItemEnchantableComponent = tool.get_component(ItemEnchantableComponent)
                    if (not Enchat) or (not Enchat.has_enchantment(v)) : return False
                elif k == "required_tool" :
                    if not isinstance(tool, ItemStack) : return False
                    any_condition = False
                    for t, lvl in v.items() :
                        tool_list = global_tools[t]
                        if tool.Identifier not in tool_list : continue
                        if tool_list.index(tool.Identifier) < lvl : continue
                        any_condition = True
                        break
                    if not any_condition : return False
            return True

        def self_item() :
            item_obj = self.ItemStack(block_id, 1)
            return [item_obj]

        def other_item(data:Dict[str, int]) :
            list1 = []
            for k, v in data.items() :
                item_obj = self.ItemStack(k, v)
                list1.append(item_obj)
            return list1

        block_id = block.Permutation.name
        loot_data = self.LootBlock.get(block_id)
        global_tools = self.LootBlock["global"]["tools"]
        global_condition = self.LootBlock["global"]["condition"]
        if loot_data is not None :
            if len(loot_data) == 0 : return []
            rules = loot_data.get("rules", ())
            for rule in rules : 
                if not condition_test(rule) : continue
                R_Item = rule["result"]
                if R_Item == "self" : return self_item()
                else : return other_item(R_Item)
            return []
        else : return self_item()

    def loot_from_entity(self, entity:Entity, tool:ItemStack=None) -> List[ItemStack] :
        loot_obj:EntityLootComponent = entity.get_component(EntityLootComponent)
        if not loot_obj : return []
        table_name = self.__table_normalize__(loot_obj.Table)
        return self.loot_from_table(table_name, tool, entity)

    def loot_from_table(self, table_path:str, tool:ItemStack=None, source:Entity=None) -> List[ItemStack] :

        def _roll_loot_tier(initial_range: int, bonus_rolls: int, bonus_chance: float) -> int:
            tier = random.randint(0, initial_range-1)
            for _ in range(bonus_rolls):
                if random.random() < bonus_chance: tier += 1
            return tier

        def _select_entry(entries: list) -> Optional[dict]:
            """
            根据权重+幸运值，从 entries 列表中随机选择一个条目。
            权重公式：weight + floor(quality * luck)
            """
            if not entries: return None

            adjusted_weights = []
            total_weight = 0.0
            for entry in entries:
                base_weight = entry.get("weight", 1)
                adjusted_weights.append(base_weight)
                total_weight += base_weight

            if total_weight <= 0: return None

            cumulative = 0.0
            rand = random.uniform(0, total_weight)
            for entry, weight in zip(entries, adjusted_weights):
                cumulative += weight
                if rand <= cumulative:
                    if _check_conditions(entry.get("conditions", [])) : return entry
                    else: return None  # 条件不满足，该次抽取落空
            return None

        def _check_conditions(conditions: list) -> bool:
            from .entity import EntityMarkVariantComponent, EntityVariantComponent
            for _cond in conditions :
                if _cond["condition"] == "has_mark_variant" : 
                    if not isinstance(source, Entity) : return False
                    _comp:EntityMarkVariantComponent = source.get_component(EntityMarkVariantComponent)
                    if (not _comp) or _cond["value"] != _comp.Value : return False
                elif _cond["condition"] == "has_variant" : 
                    if not isinstance(source, Entity) : return False
                    _comp:EntityVariantComponent = source.get_component(EntityVariantComponent)
                    if (not _comp) or _cond["value"] != _comp.Value : return False
                elif _cond["condition"] in {"random_chance", "random_chance_with_looting"} :
                    if random.random() > _cond["chance"] : return False
                elif _cond["condition"] == "random_regional_difficulty_chance" :
                    if random.random() > _cond["max_chance"] : return False
                elif _cond["condition"] == "killed_by_player_or_pets" : return False
                elif _cond["condition"] == "killed_by_player" : return False
            return True

        def _process_entry(entry: dict) -> List['ItemStack']:
            """根据 entry 类型生成物品并执行 functions"""
            etype = entry.get("type", "item")
            name = entry.get("name", "")

            if etype == "item":
                item = self.ItemStack(name, 1)
                for func in entry.get("functions", []): _apply_function(item, func)
                return [item] if item.Count > 0 else []
            elif etype == "loot_table": return self.loot_from_table(name, tool, source)
            elif etype == "empty": return []

        def _apply_function(item:'ItemStack', func:dict) -> None:
            func_name = func.get("function", "").replace("minecraft:", "", 1)
            if func_name == "set_count":
                count_val = func.get("count", 1)
                if isinstance(count_val, dict) : 
                    min_var = count_val.get("min", 1)
                    choose_count = random.randint(min_var, count_val.get("max", min_var))
                    item.Count = np.int8(choose_count)
                else: item.Count = np.int8( int(count_val) )
                if item.Count > item.MaxCount : item.Count = np.int8(item.MaxCount)
            elif func_name == "set_data":
                count_val = func.get("data", 0)
                item.Damage = np.int16( int(count_val) )
            elif func_name == "set_damage":
                damage_val = func.get("damage", 0)
                _comp:ItemDurabilityComponent = item.get_component(ItemDurabilityComponent)
                if not _comp : return None
                if isinstance(damage_val, dict) : 
                    min_var = damage_val.get("min", 0)
                    choose_damage = random.uniform(min_var, damage_val.get("max", min_var))
                    _comp.Damage = np.int32(_comp.MaxDurability * choose_damage)
                else: _comp.Damage = np.int32(_comp.MaxDurability * damage_val)


        table_path = self.__table_normalize__(table_path)
        table = self.LootTable.get(table_path, {})
        if not table or "pools" not in table: return []

        items = []
        for pool in table["pools"]:
            # 0. 验证条件
            if not _check_conditions(pool.get("conditions", [])) : continue
            entries = pool.get("entries", [])

            # 1. 确定该 pool 的抽取次数
            if "rolls" in pool :
                rolls = pool.get("rolls", 1)
                if isinstance(rolls, dict): count = random.randint(rolls.get("min", 0), rolls.get("max", 0))
                else: count = max(0, int(rolls))

                # 2. 从 entries 中加权随机选择一个 entry
                for _ in range(count):
                    entry = _select_entry(entries)
                    if entry is None: continue
                    generated = _process_entry(entry)
                    items.extend(i for i in generated if i.Count)

            elif "tiers" in pool :
                initial_range = pool["tiers"]["initial_range"]
                bonus_rolls = pool["tiers"]["bonus_rolls"]
                bonus_chance = pool["tiers"]["bonus_chance"]
                index = _roll_loot_tier(initial_range, bonus_rolls, bonus_chance)
                index = max(0, min(index, len(entries)-1))
                if not _check_conditions(entries[index].get("conditions", [])) : continue
                generated = _process_entry(entries[index])
                items.extend(i for i in generated if i.Count)

        return items
    
