from typing import List, Dict, Union, Any, Tuple, TypedDict, Type, Set, Optional
from . import nbt, MinecraftSimulator
from .. import Constants, np
import random, copy, hashlib, os, json, math, array, itertools, functools
FireDamageType = {"fire", "fire_tick", "campfire", "soul_campfire", "lava", "magma"}
# (护甲值, 保护, 火焰保护, 爆炸保护, 弹射物保护, 摔落缓冲, 抗性提升)
DEFENCE: Dict[str, Tuple[bool, bool, bool, bool, bool, bool, bool]] = {
    # ── 常规伤害：护甲值、保护、抗性提升生效 ──────────────────────────────
    "anvil":         (True,  True,  False, False, False, False, True),  # 铁砧砸落
    "charging":      (True,  True,  False, False, False, False, True),  # 冲撞
    "contact":       (True,  True,  False, False, False, False, True),  # 接触伤害（仙人掌、甜浆果丛等）
    "entity_attack": (True,  True,  False, False, False, False, True),  # 实体攻击
    "falling_block": (True,  True,  False, False, False, False, True),  # 下落方块
    "lightning":     (True,  True,  False, False, False, False, True),  # 闪电
    "mace_smash":    (True,  True,  False, False, False, False, True),  # 重锤猛击
    "none":          (True,  True,  False, False, False, False, True),  # 无来源伤害
    "piston":        (True,  True,  False, False, False, False, True),  # 活塞
    "ram_attack":    (True,  True,  False, False, False, False, True),  # 山羊冲撞
    "stalactite":    (True,  True,  False, False, False, False, True),  # 钟乳石掉落
    "stalagmite":    (True,  True,  False, False, False, False, True),  # 石笋掉落
    "thorns":        (True,  True,  False, False, False, False, True),  # 荆棘
    "wither":        (True,  True,  False, False, False, False, True),  # 凋零效果（同上）

    # ── "爆炸"行：护甲值、保护、爆炸保护、抗性提升生效 ────────────────────
    "block_explosion":  (True, True, False, True,  False, False, True),  # 方块爆炸
    "entity_explosion": (True, True, False, True,  False, False, True),  # 实体爆炸
    "fireworks":        (True, True, False, True,  False, False, True),  # 烟花火箭爆炸
    "self_destruct":    (True, True, False, True,  False, False, True),  # 自爆

    # ── "着火"行：保护、火焰保护、抗性提升生效（护甲值不生效）─────────────
    "campfire":       (False, True, True,  False, False, False, True),  # 站在营火顶部
    "fire":           (False, True, True,  False, False, False, True),  # 着火
    "fire_tick":      (False, True, True,  False, False, False, True),  # 燃烧 tick
    "soul_campfire":  (False, True, True,  False, False, False, True),  # 站在灵魂营火顶部
    "temperature":    (False, True, True,  False, False, False, True),  # 高温/温度伤害

    # ── "熔岩/岩浆块/小火球"行：护甲值、保护、火焰保护、抗性提升生效 ──────
    "lava":  (True, True, True, False, False, False, True),  # 熔岩
    "magma": (True, True, True, False, False, False, True),  # 岩浆块

    # ── "窒息/溺水/魔法/动能/冰冻"行：保护、抗性提升生效（护甲值不生效）──
    "drowning":     (False, True, False, False, False, False, True),  # 溺水
    "fly_into_wall":(False, True, False, False, False, False, True),  # 动能（鞘翅撞墙）
    "freezing":     (False, True, False, False, False, False, True),  # 冰冻（细雪）
    "magic":        (False, True, False, False, False, False, True),  # 魔法（女巫有 -85% 生物修正）
    "suffocation":  (False, True, False, False, False, False, True),  # 窒息

    # ── "弹射物"行：护甲值、保护、弹射物保护、抗性提升生效 ───────────────
    "projectile": (True, True, False, False, True, False, True),

    # ── "摔落"行：保护、摔落缓冲、抗性提升生效（护甲值不生效）────────────
    "fall": (False, True, False, False, False, True, True),

    # ── "监守者远程"行：只有抗性提升生效 ─────────────────────────────────
    "sonic_boom": (False, False, False, False, False, False, True),

    # ── "饥饿/虚空/override"行：七层全部无视 ─────────────────────────────
    "starve":   (False, False, False, False, False, False, False),  # 饥饿
    "void":     (False, False, False, False, False, False, False),  # 虚空
    "override": (False, False, False, False, False, False, False),  # /damage 强制伤害，无视一切减免
}


def __detach_from_world__(entity:"Entity") -> None :
    """
    把实体从"世界登记"里摘掉：区块实体表 + EntityCache + UnloadChunkEntityCache。
    只查内存，不加载区块；玩家不在这些容器里，直接跳过。
    """
    if isinstance(entity, Player) : return
    dimension = entity.Dimension
    if dimension is None : return

    while entity in dimension.EntityCache : dimension.EntityCache.remove(entity)
    while entity in dimension.UnloadChunkEntityCache : dimension.UnloadChunkEntityCache.remove(entity)
    try : chunk = dimension.__get_chunk__(entity.Pos)
    except Exception : return
    while entity in chunk.Entities : chunk.Entities.remove(entity)

def __attach_to_world__(entity:"Entity") -> None :
    """
    把实体登记回世界：所在区块在内存里 → 进 chunk.Entities + EntityCache；
    不在内存里 → 挂到 UnloadChunkEntityCache（等下一次 tick 批量落盘）。
    保证不变量：在 EntityCache 的实体不会同时出现在 UnloadChunkEntityCache。
    """
    if isinstance(entity, Player) : return
    dimension = entity.Dimension
    if dimension is None : return

    while entity in dimension.EntityCache : dimension.EntityCache.remove(entity)
    while entity in dimension.UnloadChunkEntityCache : dimension.UnloadChunkEntityCache.remove(entity)
    try : chunk = dimension.__get_chunk__(entity.Pos)
    except Exception :
        dimension.UnloadChunkEntityCache.append(entity) ; return

    while entity in chunk.Entities : chunk.Entities.remove(entity)
    chunk.Entities.append(entity)
    dimension.EntityCache.append(entity)

if "EntityComponent" :
    
    """
    class EntityBreathableComponent(EntityComponent) :
        Identifier = "minecraft:breathable"

        def __init__(self, entity:"Entity") :
            super().__init__(entity)
            self.CanBreathesAir = True
            self.CanBreatheWater = False
            self.CanBreatheLava = False
            self.CanBreatheSolid = False
            self.TotalSupply: int = 15
            self.Air: int = 0


        def from_json(self, obj: dict):
            self.CanBreathesAir = bool(obj.get('breathes_air', 0))
            self.CanBreatheWater = bool(obj.get('breathes_water', 0))
            self.CanBreatheLava = bool(obj.get('breathes_lava', 0))
            self.CanBreatheSolid = bool(obj.get('breathes_solids', 0))
            self.TotalSupply = int(obj.get('total_supply', 15))
            return self

        def from_nbt(self, nbt_obj):
            self.Air = nbt_obj.get("Air", nbt.TAG_Short(0)).value

        def to_nbt(self, nbt_obj):
            nbt_obj["Air"] = nbt.TAG_Short(self.Air)
    """


    class EntityComponent :

        Identifier = None

        def __init__(self, entity:"Entity") :
            self.entity = entity

        def __tick__(self) :
            pass
            
        def from_json(self, obj:dict) :
            return self

        def from_nbt(self, nbt_obj:nbt.TAG_Compound) : 
            return self

        def to_nbt(self, nbt_obj:nbt.TAG_Compound) : 
            return None

    class EntityPropertyComponent(EntityComponent) :
        Identifier = "minecraft:property"
        # 属性存储：{"property_name": {"value": 当前值, "default":v, "condition": [范围] 或 [枚举列表]}}

        def __init__(self, entity: "Entity") :
            super().__init__(entity)
            self.Properties:Dict[str, Union[str,int,bool,float]] = {}
            self.Config:Dict[str, list] = {}


        def from_json(self, obj) -> "EntityPropertyComponent" :
            EntityDef = self.entity.context.GameSource.ENTITY.get(self.entity.Identifier)
            properties_json = EntityDef.get("description", {}).get("properties")
            if not properties_json: return self

            for prop_name, json_def in properties_json.items():
                prop_type, default = json_def.get("type"), json_def.get("default")
                number_range, string_values = json_def.get("range"), json_def.get("values")
                if default is None : continue
                if prop_type != "bool" and (number_range is None or string_values is None) : continue
                if prop_type == "bool" and default not in {True, False} : continue
                if prop_type == "int" and not( isinstance(number_range, list) and len(number_range) >= 2 and
                    isinstance(number_range[0], int) and isinstance(number_range[1], int) ) : continue
                if prop_type == "float" and not( isinstance(number_range, list) and len(number_range) >= 2 and \
                    isinstance(number_range[0], (int, float)) and isinstance(number_range[1], (int, float)) ) : continue
                if prop_type == "enum" and not( isinstance(string_values, list) and all(isinstance(i, str) 
                    for i in string_values) ) : continue

                if prop_type == "bool" : self.Config[prop_name] = [bool]
                elif prop_type == "int" : 
                    self.Config[prop_name] = [int, number_range[0], number_range[1]]
                    if (not isinstance(default, str)) and not(number_range[0] <= default <= number_range[1]) : default = number_range[0]
                elif prop_type == "float": 
                    self.Config[prop_name] = [float, number_range[0], number_range[1]]
                    if (not isinstance(default, str)) and not(number_range[0] <= default <= number_range[1]) : default = number_range[0]
                elif prop_type == "enum": 
                    self.Config[prop_name] = [str, *string_values]
                    if default not in string_values : default = string_values[0]

                self.set_property(prop_name, default)

            return self

        def to_nbt(self, nbt_obj) :
            prop_tag = nbt.TAG_Compound()
            for prop_name, prop_val in self.Properties.items() :
                config = self.Config[prop_name]
                if config[0] is bool : prop_tag[prop_name] = nbt.TAG_Byte( bool(prop_val) )
                elif config[0] is int : prop_tag[prop_name] = nbt.TAG_Int(prop_val)
                elif config[0] is float : prop_tag[prop_name] = nbt.TAG_Float(prop_val)
                elif config[0] is str : prop_tag[prop_name] = nbt.TAG_String(prop_val)
            nbt_obj["Properties"] = prop_tag

        def from_nbt(self, nbt_obj) :
            prop_tag = nbt_obj.get("Properties")
            if not isinstance(prop_tag, nbt.TAG_Compound): return self

            for prop_name, tag in prop_tag.items():
                if prop_name not in self.Config : continue
                if isinstance(tag, nbt.TAG_Byte): self.set_property(prop_name, bool(tag.value))
                elif isinstance(tag, nbt.TAG_Int): self.set_property(prop_name, tag.value)
                elif isinstance(tag, nbt.TAG_Float): self.set_property(prop_name, tag.value)
                elif isinstance(tag, nbt.TAG_String): self.set_property(prop_name, tag.value)
            return self
        
        
        def has_property(self, property_name) :
            return property_name in self.Properties

        def get_property(self, property_name) :
            if property_name in self.Properties : return self.Properties[property_name]
            return None

        def set_property(self, property_name, value) -> bool :
            config = self.Config.get(property_name)
            if config is None : return False
            
            if config[0] is not str and isinstance(value, str) :
                if config[0] is float : self.Properties[property_name] = random.uniform(config[1], config[2])
                elif config[0] is int : self.Properties[property_name] = random.randint(config[1], config[2])
                elif config[0] is bool : self.Properties[property_name] = random.choice((True, False))
                return True
            elif (config[0] is float and isinstance(value, (int, float)) and config[1]<= value <= config[2]) or \
                (config[0] is int and isinstance(value, int) and config[1]<= value <= config[2]) or \
                (config[0] is bool and isinstance(value, bool)) or \
                (config[0] is str and isinstance(value, str) and value in config) : 
                self.Properties[property_name] = value
                return True
            else : return False

    class EntityEffectComponent(EntityComponent):
        Identifier = "minecraft:effect"

        def __init__(self, entity: "Entity"):
            super().__init__(entity)
            self.__effects: Dict[str, Dict[str, int]] = {}
            # 存储效果：{"effect_name": {"amplifier": int, "duration": int (刻)}}

        def __tick__(self) -> None:
            """每刻调用，减少持续时间并移除过期效果"""
            expired = []
            for name, data in self.__effects.items():
                data["duration"] -= 1
                if data["duration"] == 0 : expired.append(name)
            for name in expired: del self.__effects[name]

        def add_effect(self, effect_name:str, amplifier:int, duration:int) -> bool:
            """
            添加或更新药水效果。
            规则：
            - 如果效果不存在，直接添加。
            - 如果已存在：
                - 若新 amplifier > 旧 amplifier，则替换（持续时间为新 duration）。
                - 若新 amplifier == 旧 amplifier，则取 max(旧 duration, 新 duration)。
                - 若新 amplifier < 旧 amplifier，则忽略。
            返回是否成功添加/更新。
            """
            if effect_name not in Constants.EFFECT : return False
            if amplifier < 0 : raise ValueError("Effect.amplifier不能为负数")
            if duration < -1 : raise ValueError("Effect.duration不能为负数")

            if duration > 0 : duration *= 1 if effect_name in {"instant_damage", "instant_health"} else 20
            new_effect = {"amplifier": amplifier, "duration":duration}
            existing = self.__effects.get(effect_name)
            if existing is None : self.__effects[effect_name] = new_effect ; return True

            old_amp, old_dur = existing["amplifier"], existing["duration"]
            if (amplifier > old_amp) or (amplifier == old_amp and duration > old_dur) :
                self.__effects[effect_name] = new_effect ; return True
            else : return False

        def remove_effect(self, effect_name: str) -> bool:
            """移除效果，若存在则返回 True"""
            if effect_name in self.__effects:
                del self.__effects[effect_name]
                return True
            return False

        def has_effect(self, effect_name: str) -> bool:
            """检查是否拥有该效果（未过期）"""
            return effect_name in self.__effects


        def to_nbt(self, nbt_obj: nbt.TAG_Compound) -> None:
            """将效果列表序列化为 ActiveEffects 列表（原版格式）"""
            effects_list = nbt.TAG_List([], type=nbt.TAG_Compound)
            for name, data in self.__effects.items():
                entry = nbt.TAG_Compound()
                entry["Id"] = nbt.TAG_String(name)
                entry["Amplifier"] = nbt.TAG_Byte(data["amplifier"])
                entry["Duration"] = nbt.TAG_Int(data["duration"])
                effects_list.append(entry)
            nbt_obj["ActiveEffects"] = effects_list

        def from_nbt(self, nbt_obj: nbt.TAG_Compound) -> "EntityEffectComponent":
            """从 NBT 加载效果列表"""
            self.__effects.clear()
            effects_list = nbt_obj.get("ActiveEffects")
            if not isinstance(effects_list, nbt.TAG_List): return self
            for entry in effects_list:
                if not isinstance(entry, nbt.TAG_Compound): continue
                name_tag = entry.get("Id")
                amp_tag = entry.get("Amplifier")
                dur_tag = entry.get("Duration")
                if not( isinstance(name_tag, nbt.TAG_String) and name_tag.value in Constants.EFFECT and
                    isinstance(amp_tag, nbt.TAG_Byte) and amp_tag.value >= 0 and
                    isinstance(dur_tag, nbt.TAG_Int) and dur_tag.value >= 0 ) : continue
                self.__effects[name_tag.value] = {"amplifier": amp_tag.value, "duration":dur_tag.value}
            return self

    class EntityAABBComponent(EntityComponent) :
        Identifier = "minecraft:collision_box"

        def __init__(self, entity:"Entity"):
            super().__init__(entity)
            self.Width: int = 1
            self.Height: int = 1

        def from_json(self, obj: dict):
            self.Width = obj.get('width', 1)
            self.Height = obj.get('height', 1)
            return self

    class EntityRideableComponent(EntityComponent) :
        Identifier = "minecraft:rideable"

        def __init__(self, entity:"Entity") :
            super().__init__(entity)
            self.SeatCount:int = 0
            self.FamilyTypes:Set[str] = set()
            self.SeatPos:list = []

        def __find_matching_seats__(self) -> List[List[float]]:
            """
            根据乘客数量查找满足座位定义的座位。
            """
            matching = []
            for seat in self.SeatPos :
                min_count = seat.get('min_rider_count')
                max_count = seat.get('max_rider_count')
                if min_count <= len(self.entity.Passengers) <= max_count: matching.append(seat["position"])
            return matching

        def __tick__(self) :
            pos_list = self.__find_matching_seats__()
            for i, entity in enumerate(self.entity.Passengers) :
                entity.Pos[0] = self.entity.Pos[0] + pos_list[i][0]
                entity.Pos[1] = self.entity.Pos[1] + pos_list[i][1]
                entity.Pos[2] = self.entity.Pos[2] + pos_list[i][2]


        def from_json(self, obj:dict) :
            self.FamilyTypes.update( obj.get('family_types', []) )
            self.SeatCount = obj.get('seat_count', 0)
            seats = obj.get("seats", {"min_rider_count":0, "max_rider_count":self.SeatCount, "position": [0, 0.7, 0.0]} )
            if isinstance(seats, dict) : seats = [seats]
            for i,j in enumerate(seats, start=1) :
                seat_def = j.copy()
                if not isinstance(seat_def.get("min_rider_count"), int) : seat_def["min_rider_count"] = i
                if not isinstance(seat_def.get("max_rider_count"), int) : seat_def["max_rider_count"] = self.SeatCount
                if not isinstance(seat_def.get("position"), list) : seat_def["position"] = [0, 0.7, 0.0]
                if len(seat_def["position"]) < 3 : seat_def["position"] = [0, 0.7, 0.0]
                self.SeatPos.append(seat_def)
            return self


        def can_add_rider(self, entity:"Entity") -> bool :
            if not entity.IsValid : return False
            if len(self.entity.Passengers) >= self.SeatCount : return False
            _comp:EntityTypeFamilyComponent = entity.get_component(EntityTypeFamilyComponent)
            if not(_comp) : return False
            if not self.FamilyTypes : return True
            if not(set(_comp.Family) & self.FamilyTypes) : return False
            return True

        def add_rider(self, entity:"Entity") -> bool :
            if not self.can_add_rider(entity) : return False
            if entity not in self.entity.Passengers : self.entity.Passengers.append(entity)

            if entity.VehicleEntity :
                _comp:EntityRideableComponent = entity.VehicleEntity.get_component(EntityRideableComponent)
                if _comp : _comp.eject_rider(entity)
            entity.VehicleEntity = self.entity

            __detach_from_world__(entity)

            return True

        def eject_rider(self, entity:Union[None, "Entity"] = None) -> List["Entity"] :
            if isinstance(entity, Entity) :
                if entity not in self.entity.Passengers : return []
                else : 
                    entity.VehicleEntity = None
                    self.entity.Passengers.remove(entity)
                    for i in range(3) : entity.Pos[i] = self.entity.Pos[i]
                    __attach_to_world__(entity)
                    return [entity]

            elif entity is None :
                en_list = self.entity.Passengers.copy()
                self.entity.Passengers.clear()
                for _e in en_list :
                    _e.VehicleEntity = None
                    for i in range(3) : _e.Pos[i] = self.entity.Pos[i]
                    __attach_to_world__(_e)
                return en_list

            else : return []

    class EntityAttackComponent(EntityComponent) :
        Identifier = "minecraft:attack"

        def __init__(self, entity:"Entity") :
            super().__init__(entity)
            self.DamageMin = 0.0
            self.DamageMax = 0.0
            self.EffectName = None
            self.EffectDuration = 0
            self.EffectAmplifier = 0
        
        def from_json(self, obj) :
            damage = obj.get("damage", 0)
            if isinstance(damage, (int, float)) :
                self.DamageMin, self.DamageMax = float(damage), float(damage)
            elif isinstance(damage, list) and len(damage) == 2:
                self.DamageMin, self.DamageMax = float(damage[0]), float(damage[1])
            elif isinstance(damage, dict) :
                min_val, max_val = damage.get("range_min", 0), damage.get("range_max", 0)
                self.DamageMin, self.DamageMax = float(min_val), float(max_val)

            self.EffectName = obj.get("effect_name")  # 可能为 None
            self.EffectDuration = int(obj.get("effect_duration", 0))
            self.EffectAmplifier = int(obj.get("effect_amplifier", 0))

            return self

        def get_damage(self) :
            return random.uniform(self.DamageMin, self.DamageMax)

    class EntityHealthComponent(EntityComponent) :
        Identifier = "minecraft:health"

        def __init__(self, entity:"Entity") :
            super().__init__(entity)
            self.CurrentValue = 0
            self.EffectiveMax = 0
            self.EffectiveMin = 0


        def from_json(self, obj):
            min_val, max_val = obj.get("min", 0), obj.get("max", 20)
            self.EffectiveMin, self.EffectiveMax = float(min_val), float(max_val)

            set_value = obj.get("value", max_val)
            if isinstance(set_value, (int, float)) : self.CurrentValue = float(set_value)
            elif isinstance(set_value, dict) :
                min_val, max_val = set_value.get("range_min", 0), set_value.get("range_max", 20)
                self.CurrentValue = random.uniform(float(min_val), float(max_val))
            return self

        def from_nbt(self, nbt_obj):
            if "Attributes" not in nbt_obj : return None
            attr = nbt_obj["Attributes"].get(self.Identifier)
            if attr is None or not isinstance(attr, nbt.TAG_Float) : return None
            self.set_value(attr.value)
            return self

        def to_nbt(self, nbt_obj):
            if "Attributes" not in nbt_obj : nbt_obj["Attributes"] = nbt.TAG_Compound()
            nbt_obj["Attributes"][self.Identifier] = nbt.TAG_Float(self.CurrentValue)


        def set_value(self, value:float):
            if value < self.EffectiveMin : self.CurrentValue = self.EffectiveMin
            elif value > self.EffectiveMax : self.CurrentValue = self.EffectiveMax
            else : self.CurrentValue = value

    class EntityWearArmorComponent(EntityComponent) :
        Identifier = "minecraft:wear_armor"

        def __init__(self, entity: "Entity") :
            from .sundries_type import Container
            super().__init__(entity)
            self.Hand = Container()
            self.Equippable = Container()
            self.Hand.Size = 2
            self.Equippable.Size = 4
        
        def to_nbt(self, nbt_obj: nbt.TAG_Compound) -> None:
            """序列化：按原版格式写入 HandItems 和 ArmorItems"""
            # 主手 + 副手
            hand_list = nbt.TAG_List([], type=nbt.TAG_Compound)
            for slot in range(2) :
                item = self.Hand.get_item(slot)
                if item is not None: hand_list.append(item.serialization())
                else : hand_list.append(nbt.TAG_Compound())
            nbt_obj["HandItems"] = hand_list

            # 盔甲：靴子、护腿、胸甲、头盔（原版顺序）
            armor_list = nbt.TAG_List([], type=nbt.TAG_Compound)
            for slot in range(4) :
                item = self.Equippable.get_item(slot)
                if item is not None: armor_list.append(item.serialization())
                else: armor_list.append(nbt.TAG_Compound())
            nbt_obj["ArmorItems"] = armor_list

        def from_nbt(self, nbt_obj: nbt.TAG_Compound) :
            ItemStack = self.entity.context.SimulatorModule.ItemStack
            self.Hand.clear_all()
            self.Equippable.clear_all()

            # 读取 HandItems（主手 + 副手）
            hand_list = nbt_obj.get("HandItems")
            if isinstance(hand_list, nbt.TAG_List) :
                for slot in range(min(len(hand_list), 2)):
                    item_tag = hand_list[slot]
                    if isinstance(item_tag, nbt.TAG_Compound):
                        item = ItemStack.deserialization(item_tag)
                        if item is not None: self.Hand.set_item(slot, item)

            # 读取 ArmorItems（靴子、护腿、胸甲、头盔）
            armor_list = nbt_obj.get("ArmorItems")
            if isinstance(armor_list, nbt.TAG_List):
                for slot in range(min(len(armor_list), 4)):
                    item_tag = armor_list[slot]
                    if isinstance(item_tag, nbt.TAG_Compound):
                        item = ItemStack.deserialization(item_tag)
                        if item is not None: self.Equippable.set_item(slot, item)

            return self

    class EntityEquippableComponent(EntityComponent) :
        Identifier = "minecraft:equippable"

        def __init__(self, entity: "Entity") :
            from .item import ItemStack
            super().__init__(entity)
            self.EquipItem:List[ItemStack] = []
            self.Config = []

        def from_json(self, obj) :
            for slot_def in obj.get("slots", []) :
                self.Config.append({"accepted_items": slot_def.get("accepted_items", [])})
            self.EquipItem.clear()
            self.EquipItem.extend(None for i in range(len(self.Config)))
            return self

        def to_nbt(self, nbt_obj: nbt.TAG_Compound) -> None:
            # 主手 + 副手
            item_list = nbt.TAG_List([], type=nbt.TAG_Compound)
            for item in self.EquipItem :
                if item is not None: item_list.append(item.serialization())
                else : item_list.append(nbt.TAG_Compound())
            nbt_obj["EquipItems"] = item_list

        def from_nbt(self, nbt_obj: nbt.TAG_Compound):
            from .item import ItemStack
            self.EquipItem.clear()
            self.EquipItem.extend(None for i in range(len(self.Config)))

            item_list = nbt_obj.get("EquipItems")
            if isinstance(item_list, nbt.TAG_List) :
                for i, item_tag in enumerate(item_list) :
                    if not isinstance(item_tag, nbt.TAG_Compound) : continue
                    item = ItemStack.deserialization(item_tag)
                    if item is not None: self.EquipItem[i] = item

            return self

        def set_item(self, slot:int, item) -> bool:
            """
            在指定槽位放置装备物品。
            :param slot: 槽位索引（0-based，对应 Config 列表下标）
            :param item: 要放置的物品，可为 None 表示卸下装备
            :return: 是否成功设置
            """
            if slot < 0 or slot >= len(self.Config): return False

            if item is not None:
                accepted = self.Config[slot].get("accepted_items", [])
                # 注意：accepted_items 里可能包含带命名空间或不带命名空间的 ID，这里简单比较
                old_id = item.Identifier.replace("minecraft:", "", 1).replace("_", "")
                if item.Identifier not in accepted or old_id not in accepted : return False

            old_item = self.EquipItem[slot]
            if old_item is not None:
                unequip_event = self.Config[slot].get("on_unequip", {}).get("event")
                if unequip_event: self.entity.trigger_event(unequip_event)

            self.EquipItem[slot] = item
            if item is not None:
                equip_event = self.Config[slot].get("on_equip", {}).get("event")
                if equip_event: self.entity.trigger_event(equip_event)

            return True

    class EntityFireImmuneComponent(EntityComponent) :
        Identifier = "minecraft:fire_immune"

    class EntityInventoryComponent(EntityComponent) :
        Identifier = "minecraft:inventory"

        def __init__(self, entity: "Entity") :
            from .sundries_type import Container
            super().__init__(entity)
            self.Container = Container()          # 实际物品存储
            self.Container.Size = 5               # 默认 inventory_size

        def from_json(self, obj: dict):
            self.Container.Size = obj.get("inventory_size", 5)
            return self

        def from_nbt(self, nbt_obj) :
            items_tag = nbt_obj.get("Items")
            if not isinstance(items_tag, nbt.TAG_List) : return self
            self.Container.clear_all()
            ItemStack = self.entity.context.SimulatorModule.ItemStack

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

    class EntityItemComponent(EntityComponent):
        Identifier = "minecraft:item"

        def __init__(self, entity: "Entity") :
            from .item import ItemStack
            super().__init__(entity)
            self.ItemStack: Optional[ItemStack] = None

        def from_nbt(self, nbt_obj: nbt.TAG_Compound) :
            ItemStack = self.entity.context.SimulatorModule.ItemStack
            item_tag = nbt_obj.get("Item")
            if isinstance(item_tag, nbt.TAG_Compound):
                self.ItemStack = ItemStack.deserialization(item_tag)
            return self

        def to_nbt(self, nbt_obj: nbt.TAG_Compound):
            if self.ItemStack is not None:
                nbt_obj["Item"] = self.ItemStack.serialization()

    class EntityLootComponent(EntityComponent):
        Identifier = "minecraft:loot"

        def __init__(self, entity: "Entity"):
            super().__init__(entity)
            self.Table: str = ""

        def from_json(self, obj: dict):
            self.Table = obj.get("table", "")
            return self
    
    class EntityMarkVariantComponent(EntityComponent):
        Identifier = "minecraft:mark_variant"

        def __init__(self, entity: "Entity"):
            super().__init__(entity)
            self.Value: int = 0

        def from_json(self, obj: dict):
            self.Value = obj.get("value", 0)
            return self
    
    class EntityVariantComponent(EntityComponent):
        Identifier = "minecraft:variant"

        def __init__(self, entity: "Entity"):
            super().__init__(entity)
            self.Value: int = 0

        def from_json(self, obj: dict):
            self.Value = obj.get("value", 0)
            return self
    
    class EntityScaleComponent(EntityComponent):
        Identifier = "minecraft:scale"

        def __init__(self, entity: "Entity"):
            super().__init__(entity)
            self.Value: float = 1.0  # 默认正常大小

        def from_json(self, obj: dict):
            self.Value = float(obj.get("value", 1.0))
            return self

    class EntityTypeFamilyComponent(EntityComponent):
        Identifier = "minecraft:type_family"

        def __init__(self, entity: "Entity"):
            super().__init__(entity)
            self.Family: Set[str] = set()

        def from_json(self, obj: dict):
            family_data = obj.get("family", [])
            if isinstance(family_data, list): self.Family = set(family_data)
            return self

        def has_family(self, family_name: str) -> bool:
            return family_name in self.Family

    class EntityDamageSensorComponent(EntityComponent):
        Identifier = "minecraft:damage_sensor"

        def __init__(self, entity: "Entity"):
            super().__init__(entity)
            self.Sensors: List[Dict] = []

        def from_json(self, obj: dict):
            data = obj.get("triggers", []) if isinstance(obj, dict) else obj
            if isinstance(data, list): self.Sensors.extend(data)
            if isinstance(data, dict): self.Sensors.append(data)
            return self

    ComponentMapping: Dict[str, Type[EntityComponent]] = {}
    for ___key, ___value in globals().copy().items() :
        if not hasattr(___value, "mro") : continue
        try : ___value.mro()
        except : continue
        if EntityComponent not in ___value.mro() : continue
        ComponentMapping[___value.Identifier] = ___value


class InputPermissionManager:
    
    Camera = 1
    Movement = 2
    LateralMovement = 4
    Sneak = 5
    Jump = 6
    Mount = 7
    Dismount = 8
    MoveForward = 9
    MoveBackward = 10
    MoveLeft = 11
    MoveRight = 12
    PermissionMap = {"camera": 1, "movement": 2, "lateral_movement": 4, "sneak": 5, "jump": 6, "mount": 7,
    "dismount": 8, "move_forward": 9, "move_backward": 10, "move_left": 11, "move_right": 12}

    def __init__(self):
        self._disabled: set[int] = set()

    def set_permission(self, permission:Union[str, int], enabled:bool = True):
        if permission in self.PermissionMap : permission = self.PermissionMap[permission]
        if enabled: self._disabled.discard(permission)
        else: self._disabled.add(permission)

    def get_permission(self, permission:Union[str, int]) -> bool:
        if permission in self.PermissionMap : permission = self.PermissionMap[permission]
        return permission not in self._disabled

class LevelManager:

    def __init__(self, level: int = 0, progress: float = 0.0):
        self.Level = level
        self.Progress = progress  # 0.0 ~ 1.0

    @staticmethod
    def _total_exp(level:int) -> int:
        """从 0 级升到 level 级所需总经验"""
        if level <= 0: return 0
        elif level <= 16: return level * level + 6 * level
        elif level <= 31: return int(2.5 * level * level - 40.5 * level + 360)
        else: return int(4.5 * level * level - 162.5 * level + 2220)

    @staticmethod
    def _level_from_total(total:float) -> int:
        """根据总经验瞬间计算等级（无循环）"""
        if total < 0: total = 0                                   # 第一段：0~16级
        if total <= 352: return int(math.sqrt(total + 9) - 3)     # 16级总经验
        if total <= 1507:  # 31级总经验
            disc = 40 * total - 7839
            if disc < 0: disc = 0
            return int((81 + math.sqrt(disc)) / 10)
        disc = 72 * total - 54215
        if disc < 0: disc = 0
        return int((325 + math.sqrt(disc)) / 18)

    def _exp_to_next(self, lvl: int) -> int:
        """升到下一级所需的经验值"""
        return self._total_exp(lvl + 1) - self._total_exp(lvl)

    def add_experience(self, amount:float) -> None:
        current_total = self._total_exp(self.Level) + self.Progress * self._exp_to_next(self.Level)
        new_total = max(0, current_total + amount)

        self.Level = self._level_from_total(new_total)
        base = self._total_exp(self.Level)
        needed = self._exp_to_next(self.Level)
        self.Progress = (new_total - base) / needed if needed > 0 else 0.0

    def set_level(self, new_level: int) -> None:
        self.Level = max(0, new_level)


    def serialization(self) -> nbt.TAG_Compound:
        """将等级和进度序列化为 NBT 复合标签"""
        root = nbt.TAG_Compound()
        root["Level"] = nbt.TAG_Int(self.Level)
        root["Progress"] = nbt.TAG_Float(self.Progress)
        return root

    def deserialization(self, tag: nbt.TAG_Compound) -> "LevelManager":
        """从 NBT 复合标签恢复 LevelManager 实例"""
        lv_tag = tag.get("Level")
        if isinstance(lv_tag, nbt.TAG_Int): self.Level = lv_tag.value
        prog_tag = tag.get("Progress")
        if isinstance(prog_tag, nbt.TAG_Float): self.Progress = prog_tag.value

        return self

class GameModeManager:
    """管理单个玩家的游戏模式，支持缩写、整数和默认模式解析"""

    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    DEFAULT = 5
    SPECTATOR = 6

    SHORT_MAP = {
        's': SURVIVAL,     '0': SURVIVAL,     0: SURVIVAL,     'survival': SURVIVAL,
        'c': CREATIVE,     '1': CREATIVE,     1: CREATIVE,     'creative': CREATIVE,
        'a': ADVENTURE,    '2': ADVENTURE,    2: ADVENTURE,    'adventure': ADVENTURE,
        'd': DEFAULT,      '5': DEFAULT,      5: DEFAULT,      'default': DEFAULT,
        'spectator': SPECTATOR }

    def __init__(self, player:"Player") :
        self.__player = player
        self.__mode = player.context.MinecraftWorld.DefaultGamemode

    @property
    def Mode(self) -> int:
        """返回当前游戏模式"""
        return self.__mode

    def query_mode(self, mode:Union[int, str]) :
        """
        设置游戏模式，支持以下输入：
        - 整数 (0,1,2,5)
        - 字符串缩写 ('s','c','a','d','survival','creative','adventure','default','spectator')
        """
        if mode in self.SHORT_MAP: gm = self.SHORT_MAP[mode]
        else : raise ValueError(f"无效的游戏模式: {mode}")

        # 如果设置为 DEFAULT，则自动替换为世界默认模式
        if gm == self.DEFAULT : gm = self.__player.context.MinecraftWorld.DefaultGamemode
        return gm

    def match_mode(self, modes:List[Union[int, str]]) :
        """
        设置游戏模式，支持以下输入：
        - 整数 (0,1,2,5)
        - 字符串缩写 ('s','c','a','d','survival','creative','adventure','default','spectator')
        """
        new_set = set(self.query_mode(i) for i in modes)
        return self.__mode in new_set

    def set_mode(self, mode:Union[int, str]) :
        """
        设置游戏模式，支持以下输入：
        - 整数 (0,1,2,5)
        - 字符串缩写 ('s','c','a','d','survival','creative','adventure','default','spectator')
        """
        self.__mode = self.query_mode(mode)

class AbilityManager:

    def __init__(self):
        self.worldbuilder = True
        self.mayfly = False
        self.mute = False

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value:bool):
        return setattr(self, key, value)


class EntityComponentManager :

    @classmethod
    def trigger_spawn(cls, entity:'Entity') -> None:
        entity_def = entity.context.GameSource.ENTITY.get(entity.Identifier)
        if not entity_def: return None
        entity.EntityGroupStack.append(entity.Identifier)
        if entity.Identifier not in entity.EntityComponentGroups :
            entity.EntityComponentGroups[entity.Identifier] = {}

        groups = entity.EntityComponentGroups[entity.Identifier]
        if "properties" in entity_def["description"] :
            groups[EntityPropertyComponent.Identifier] = EntityPropertyComponent(entity).from_json(None)
        if entity.Identifier == "minecraft:item" :
            groups[EntityItemComponent.Identifier] = EntityItemComponent(entity)
        elif entity.Identifier == "minecraft:player" :
            helath = groups[EntityHealthComponent.Identifier] = EntityHealthComponent(entity)
            groups[EntityEffectComponent.Identifier] = EntityEffectComponent(entity)
            groups[EntityWearArmorComponent.Identifier] = EntityWearArmorComponent(entity)
            helath.EffectiveMin = 0
            helath.EffectiveMax = 20
            helath.CurrentValue = 20

        for k, v in entity_def.get("components").items() :
            _comp = cls._create_component(k, entity)
            if not _comp : continue
            groups[_comp.Identifier] = _comp.from_json(v)

            if isinstance(_comp, EntityTypeFamilyComponent) :
                if "mob" in _comp.Family :
                    groups[EntityEffectComponent.Identifier] = EntityEffectComponent(entity)
                    groups[EntityWearArmorComponent.Identifier] = EntityWearArmorComponent(entity)

    @classmethod
    def trigger_rebuild(cls, entity:'Entity') -> None:
        comp_groups_def = entity.context.GameSource.ENTITY.get(entity.Identifier, {}).get("component_groups", {})

        for gname in entity.EntityGroupStack :
            if gname == entity.Identifier : continue
            if gname not in comp_groups_def : continue
            group_def, comps = comp_groups_def.get(gname, {}), {}
            for comp_id, comp_data in group_def.items():
                comp = cls._create_component(comp_id, entity)
                if comp : comp.from_json(comp_data)
                if not comp: continue
                comps[comp.Identifier] = comp
            entity.EntityComponentGroups[gname] = comps

    @classmethod
    def trigger_event(cls, entity:'Entity', event_name:str) -> None:
        entity_def = entity.context.GameSource.ENTITY.get(entity.Identifier)
        if not entity_def: return None
        events_def = entity_def.get("events", {})
        if event_name not in events_def: return None
        cls._process_event_object(entity, events_def[event_name])

    @classmethod
    def _process_event_object(cls, entity: 'Entity', event_obj: dict) -> None:
        """处理事件对象。支持直接 add/remove 或复合结构 (sequence, randomize, first_valid, trigger)"""

        # 1. 直接的 add / remove
        if "add" in event_obj or "remove" in event_obj :
            cls._apply_add_remove(entity, event_obj)

        # 2. trigger: 触发另一个事件
        if "trigger" in event_obj:
            cls.trigger_event(entity, event_obj["trigger"])

        # 3. sequence: 按顺序执行
        if "sequence" in event_obj:
            for sub in event_obj["sequence"]: cls._process_event_object(entity, sub)

        # 4. randomize: 根据权重随机选择一个子动作
        if "randomize" in event_obj:
            options = event_obj["randomize"]
            if not options: return
            total_weight = sum(opt.get("weight", 1) for opt in options)
            rand = random.uniform(0, total_weight)
            cumulative = 0.0
            for opt in options:
                cumulative += opt.get("weight", 1)
                if rand <= cumulative:
                    cls._process_event_object(entity, opt)
                    break

        # 5. first_valid: 执行第一个满足过滤条件的子动作
        if "first_valid" in event_obj:
            for option in event_obj["first_valid"]:
                filters = option.get("filters", {})
                if cls._check_filters(entity, filters):
                    cls._process_event_object(entity, option)
                    break

        # 6. 其他类型（如 set_property）
        if "set_property" in event_obj:
            _comp: EntityPropertyComponent = entity.get_component(EntityPropertyComponent, True)
            if _comp : 
                for k, v in event_obj["set_property"].items() : _comp.set_property(k, v)

    @classmethod
    def _apply_add_remove(cls, entity: 'Entity', event_obj: dict) -> None:
        comp_groups_def = entity.context.GameSource.ENTITY.get(entity.Identifier, {}).get("component_groups", {})
        stack = entity.EntityGroupStack

        # 先处理 remove
        remove_groups = event_obj.get("remove", {}).get("component_groups", [])
        for gname in remove_groups:
            if gname in stack : stack.remove(gname)

        # 再处理 add
        add_groups = event_obj.get("add", {}).get("component_groups", [])
        for gname in add_groups:
            # 如果该组件组尚未实例化，从定义中创建组件实例并存入 EntityComponentGroups
            if gname not in entity.EntityComponentGroups :
                group_def, comps = comp_groups_def.get(gname, {}), {}
                for comp_id, comp_data in group_def.items():
                    comp = cls._create_component(comp_id, entity)
                    if not comp: continue
                    comps[comp.Identifier] = comp.from_json(comp_data)
                entity.EntityComponentGroups[gname] = comps

            if gname not in stack : stack.append(gname)

    @staticmethod
    def _create_component(comp_id: str, entity: 'Entity') -> Optional['EntityComponent']:
        cls = ComponentMapping.get(comp_id)
        return cls(entity) if cls else None

    @staticmethod
    def _check_filters(entity: 'Entity', filters: dict) -> bool:
        return random.random() < 0.4


class Entity :

    HURT_IMMUNITY_TICKS = 10
    context:MinecraftSimulator = None
    ValidAttr = {"UniqueID", "IsValid", "context", "serialization_dict", "Identifier", 
        "__str__", "__repr__", "__class__"}

    def __init__(self, id:str, new:bool=True) :
        from .world import ScoreboardIdentity
        from .dimension import Dimension

        self.IsValid = True
        self.UniqueID = (self.context.MinecraftWorld.OpenCount << 32) + self.context.MinecraftWorld.EntityCreateCount
        self.Dimension:Dimension = None

        self.Identifier:str = id if id.startswith("minecraft:") else f"minecraft:{id}"
        if self.Identifier == "minecraft:villager" : self.Identifier = "minecraft:villager_v2"
        self.Pos = [np.float32(0), np.float32(0.0), np.float32(0.0)]
        self.Rotation = [np.float32(0), np.float32(0)]
        self.Motion = [np.float32(0), np.float32(0.0), np.float32(0.0)]

        self.OnGround = False
        self.Sleeping = False
        self.LootDropped = True
        self.Invulnerable = False
        self.CustomNameVisible = False

        self.Fire = np.int16(0)
        self.DeathTime = np.int32(0)
        self.FallDistance = np.float32(0)
        self.PortalCooldown = np.int32(0)

        self.CustomName:str = ""
        self.Tags:Set[str] = set()
        self.Passengers:List[Entity] = []
        self.EntityGroupStack:List[str] = []
        self.EntityComponentGroups:Dict[str, Dict[str, EntityComponent]] = {}
        self.ScoreboardIdentity = ScoreboardIdentity(self.UniqueID, ScoreboardIdentity.TypeEntity)

        self.Damage = {"Time":0, "Value":0} 
        self.VehicleEntity: Optional[Entity] = None
        self.context.MinecraftWorld.EntityCreateCount += 1
        EntityComponentManager.trigger_spawn(self)
        if new : EntityComponentManager.trigger_event(self, "minecraft:entity_spawned")

    def __eq__(self, other):
        if not isinstance(other, Entity) : return False
        return self.UniqueID == other.UniqueID

    def __hash__(self):
        return self.UniqueID

    def __setattr__(self, name, value) :
        if name != "Dimension" and name != "VehicleEntity" and hasattr(self, name) : 
            _old = getattr(self, name)
            if _old is not None and not isinstance(value, getattr(self, name).__class__) : 
                raise AttributeError(f"can not modify diffirent type of {name} attribute")
        if name == "Identifier" and hasattr(self, name) :
            raise AttributeError(f"can not modify {name} attribute")

        super().__setattr__(name, value)

    def __getattribute__(self, name:str) :
        super_obj = super()
        if name not in super_obj.__getattribute__("ValidAttr") and not super_obj.__getattribute__("IsValid") : 
            raise AttributeError(f"can not read LifeEnd object")
        return super().__getattribute__(name)

    def __tick__(self) :
        health_comp:EntityHealthComponent = self.get_component(EntityHealthComponent, bottom=True)
        if health_comp and health_comp.CurrentValue <= 0 : self.DeathTime += 1
        if self.DeathTime > 10 : 
            self.remove()
            if isinstance(self, Player) : 
                self.DeathTime = np.int32(0)
                health_comp.set_value(health_comp.EffectiveMax)
                spawnradius = self.context.MinecraftWorld.GameRule.spawnradius
                
                self.Pos[0] = self.SpawnPoint[0] + random.randint(-spawnradius, spawnradius) + 0.5
                self.Pos[1] = self.SpawnPoint[1]
                self.Pos[2] = self.SpawnPoint[2] + random.randint(-spawnradius, spawnradius) + 0.5

        if not self.IsValid: return None
        comp1:EntityEffectComponent = self.get_component(EntityEffectComponent, bottom=True)
        if comp1 : comp1.__tick__()
        comp2:EntityRideableComponent = self.get_component(EntityRideableComponent)
        if comp2 : comp2.__tick__()

        if self.Damage["Time"] > 0 : 
            self.Damage["Time"] -= 1
            if self.Damage["Time"] == 0 : self.Damage["Value"] = 0

        for _entity in self.Passengers.copy() : 
            if not isinstance(self, Player) : _entity.__tick__()

        comp:EntityTypeFamilyComponent = self.get_components("minecraft:type_family")
        if comp and "monster" in comp.Family and self.context.MinecraftWorld.Difficulty == 0 : 
            self.remove()

    def __loot__(self) :
        if self.context.MinecraftWorld.GameRule.domobloot :
            loot_comp:EntityLootComponent = self.get_component(EntityLootComponent)
            if loot_comp: 
                loot_items = self.context.LootManager.loot_from_entity(self)
                for item in loot_items :
                    _entity = self.Dimension.spawn_entity("minecraft:item", self.Pos, (0, 0),
                        register_in_unload_chunk=True)
                    _comp1:EntityItemComponent = _entity.get_component(EntityItemComponent)
                    _comp1.ItemStack = item

    def __str__(self) :
        if isinstance(self, Player) : name = self.CustomName
        elif self.Identifier == "minecraft:item" : 
            _comp:EntityItemComponent = self.get_component(EntityItemComponent)
            item_name = _comp.ItemStack.Identifier.replace("minecraft:", "", 1)
            name = Constants.TRANSLATE_ID["[物品]"].get(item_name, "item.%s.name" % item_name)
        elif self.CustomName == "" : 
            entity_name = self.Identifier.replace("minecraft:", "", 1)
            name = Constants.TRANSLATE_ID["[实体]"].get(entity_name, "entity.%s.name" % entity_name)
        else : name = self.CustomName

        return name

    def __repr__(self):
        str1 = self.Identifier.split(":")[1]
        str2 = f"{self.CustomName}" if isinstance(self, Player) else f"{self.UniqueID:16X}"
        return "%s{%s:%s}" % (self.__class__.__name__, str1, str2)


    def serialization(self) -> nbt.TAG_Compound:
        root = nbt.TAG_Compound()

        root["Identifier"] = nbt.TAG_String(self.Identifier)
        root["UniqueID"] = nbt.TAG_Long(self.UniqueID)  # 使用 Long 保存 64 位 ID

        root["Pos"] = nbt.TAG_List([nbt.TAG_Float(float(v)) for v in self.Pos], type=nbt.TAG_Float)
        root["Rotation"] = nbt.TAG_List([nbt.TAG_Float(float(v)) for v in self.Rotation], type=nbt.TAG_Float)
        root["Motion"] = nbt.TAG_List([nbt.TAG_Float(float(v)) for v in self.Motion], type=nbt.TAG_Float)

        root["OnGround"] = nbt.TAG_Byte(1 if self.OnGround else 0)
        root["Sleeping"] = nbt.TAG_Byte(1 if self.Sleeping else 0)
        root["LootDropped"] = nbt.TAG_Byte(1 if self.LootDropped else 0)
        root["Invulnerable"] = nbt.TAG_Byte(1 if self.Invulnerable else 0)
        root["CustomNameVisible"] = nbt.TAG_Byte(1 if self.CustomNameVisible else 0)

        root["Fire"] = nbt.TAG_Short(int(self.Fire))
        root["FallDistance"] = nbt.TAG_Float(float(self.FallDistance))
        root["PortalCooldown"] = nbt.TAG_Int(int(self.PortalCooldown))

        root["CustomName"] = nbt.TAG_String(self.CustomName)
        root["Tags"] = nbt.TAG_List([nbt.TAG_String(t) for t in self.Tags], type=nbt.TAG_String)
        root["Passengers"] = nbt.TAG_List([p.serialization() for p in self.Passengers], type=nbt.TAG_Compound)
        root["EntityGroupStack"] = nbt.TAG_List([nbt.TAG_String(op) for op in self.EntityGroupStack], type=nbt.TAG_String)
        root["EntityGroupData"] = nbt.TAG_Compound()

        for _comp in self.get_components() : _comp.to_nbt(root["EntityGroupData"])

        return root

    @classmethod
    def deserialization(cls, tag: nbt.TAG_Compound) -> Union[None, "Entity"]:
        ident_tag = tag.get("Identifier")
        if not isinstance(ident_tag, nbt.TAG_String): return None
        if ident_tag.value not in cls.context.GameSource.ENTITY : return None
        entity = cls(ident_tag.value, new=False)

        # 2. 恢复唯一 ID
        uid_tag = tag.get("UniqueID")
        if isinstance(uid_tag, nbt.TAG_Long): entity.UniqueID = uid_tag.value

        # 3. 恢复位置 / 旋转 / 运动
        pos = tag.get("Pos")
        if isinstance(pos, nbt.TAG_List) and len(pos) == 3:
            entity.Pos = [np.float32(float(v.value)) for v in pos if isinstance(v, nbt.TAG_Float)]
        rot = tag.get("Rotation")
        if isinstance(rot, nbt.TAG_List) and len(rot) == 2:
            entity.Rotation = [np.float32(float(v.value)) for v in rot if isinstance(v, nbt.TAG_Float)]
        mot = tag.get("Motion")
        if isinstance(mot, nbt.TAG_List) and len(mot) == 3:
            entity.Motion = [np.float32(float(v.value)) for v in mot if isinstance(v, nbt.TAG_Float)]

        # 4. 布尔状态
        entity.OnGround = bool(tag.get("OnGround", nbt.TAG_Byte(0)).value)
        entity.Sleeping = bool(tag.get("Sleeping", nbt.TAG_Byte(0)).value)
        entity.LootDropped = bool(tag.get("LootDropped", nbt.TAG_Byte(1)).value)
        entity.Invulnerable = bool(tag.get("Invulnerable", nbt.TAG_Byte(0)).value)
        entity.CustomNameVisible = bool(tag.get("CustomNameVisible", nbt.TAG_Byte(0)).value)

        # 5. 数值属性
        entity.Fire = np.int16(tag.get("Fire", nbt.TAG_Short(0)).value)
        entity.FallDistance = np.float32(tag.get("FallDistance", nbt.TAG_Float(0.0)).value)
        entity.PortalCooldown = np.int32(tag.get("PortalCooldown", nbt.TAG_Int(0)).value)

        # 6. 自定义名称、标签
        entity.CustomName = tag.get("CustomName", nbt.TAG_String("")).value
        tags_list = tag.get("Tags")
        if isinstance(tags_list, nbt.TAG_List): entity.Tags.update(t.value for t in tags_list if isinstance(t, nbt.TAG_String))

        # 7. 乘客（递归反序列化）
        passengers_list = tag.get("Passengers")
        if isinstance(passengers_list, nbt.TAG_List):
            for p_tag in passengers_list:
                if not isinstance(p_tag, nbt.TAG_Compound): continue
                ident_tag = p_tag.get("Identifier")
                if ident_tag and ident_tag.value == "minecraft:player" : passenger = Player.deserialization(p_tag, cache=True)
                elif ident_tag : passenger = cls.deserialization(p_tag)
                else : continue
                if passenger : 
                    passenger.VehicleEntity = entity
                    entity.Passengers.append(passenger)

        # 8. 恢复组件组操作栈，重建组件组实例
        defs_list = tag.get("EntityGroupStack")
        if isinstance(defs_list, nbt.TAG_List):
            entity.EntityGroupStack = [op.value for op in defs_list if isinstance(op, nbt.TAG_String)]
        EntityComponentManager.trigger_rebuild(entity)

        # 9. 应用组件 NBT 数据（EntityGroupData）
        comp_data = tag.get("EntityGroupData")
        if isinstance(comp_data, nbt.TAG_Compound):
            for comp in entity.get_components(): comp.from_nbt(comp_data)
        
        _comp:EntityRideableComponent = entity.get_component(EntityRideableComponent)
        if not _comp : 
            for _passer in entity.Passengers :
                if isinstance(entity, Player) : continue
                _chunk = entity.Dimension.__get_chunk__(entity.Pos)
                if _passer not in entity.Dimension.EntityCache : 
                    entity.Dimension.EntityCache.append(_passer)
                if _passer not in _chunk.Entities : 
                    _chunk.Entities.append(_passer)
            entity.Passengers.clear()

        return entity

    def serialization_dict(self) -> Dict[str, Any]:
        """
        生成仅供渲染使用的字典（可 JSON 序列化）。
        """
        super_obj = super()
        def f32(v): return float(v)
        def vec(v): return [f32(x) for x in v]

        data: Dict[str, Any] = {
            "uid":      super_obj.__getattribute__("UniqueID"),
            "type":     super_obj.__getattribute__("Identifier"),
            "pos":      vec(super_obj.__getattribute__("Pos")),
            "rotation": vec(super_obj.__getattribute__("Rotation")),
            "tags":     sorted(super_obj.__getattribute__("Tags")),
            "valid":    bool(self.IsValid),
            "passengers": []
        }

        # 乘客（递归）
        for p in super_obj.__getattribute__("Passengers"):
            data["passengers"].append(p.serialization_dict())

        return data


    def apply_damage(self, amount:float, cause:str="none", source:Optional["Entity"]=None) -> bool :
        """
        对实体造成伤害（基岩版规则）。
            amount               基础伤害值（单位与 minecraft:health 相同，2 点 = 1 颗心）
            cause                伤害类型，取值见 Constants.DAMAGE_CAUSE（fall、fire、entity_attack…）
            source               造成伤害的实体，可为 None
            bypass_immunity      忽略受击后伤害免疫（强制伤害，如 /damage）
            bypass_invulnerable  忽略 Invulnerable 与创造模式免疫
        返回：False 表示这次伤害没生效（免疫 / 实体无效 / 已死亡）；
        """
        def __can_be_damaged__() -> Tuple[bool, float]  :
            fire_test3 = self.context.MinecraftWorld.GameRule.firedamage
            freeze_test = self.context.MinecraftWorld.GameRule.freezedamage
            fall_test = self.context.MinecraftWorld.GameRule.falldamage
            drowning_test = self.context.MinecraftWorld.GameRule.drowningdamage
            if  isinstance(self, Player) and \
                (self.GameMode.Mode == GameModeManager.CREATIVE or
                (fire_test3 and cause in FireDamageType) or 
                (freeze_test and cause == "freezing") or 
                (fall_test and cause == "fall") or 
                (drowning_test and cause == "drowning")) : return (False, 0)

            if self.Invulnerable and cause not in {"self_destruct", "override"} : return (False, 0)
            fire_test1 = bool(self.get_component(EntityFireImmuneComponent)) 
            fire_test2:EntityEffectComponent = self.get_component(EntityEffectComponent)
            if fire_test2 : fire_test2 = fire_test2.has_effect("fire_resistance")
            if (fire_test1 or fire_test2) and cause in FireDamageType : return (False, 0)

            damage_test:EntityDamageSensorComponent = self.get_component(EntityDamageSensorComponent)
            if damage_test : 
                for _test in damage_test.Sensors :
                    if "cause" not in _test : continue
                    if "deals_damage" not in _test : continue
                    _cause, _deals = _test["cause"], _test["deals_damage"]
                    if _cause not in ("all", cause) : continue
                    if  _deals in {"no", "no_but_side_effects_apply", False} : return (False, 0)
                    damage_multiplier = _test.get("damage_multiplier", 1)
                    if not isinstance(damage_multiplier, (float, int)) : damage_multiplier = 1
                    return (True, damage_multiplier)

            return (True, 1)

        def __damage_reduce__(multiplier:float) -> float :
            """
            【留空】护甲值、保护魔咒、抗性提升、伤害吸收等减免，返回减免后的伤害值。
            基岩版是先减免、再由受击后伤害免疫做最后的差值调整，所以这里返回的才是 PHDI 的输入。
            DEFENCE 记录"每个伤害类型受哪些防御层影响"，取值来自 wiki「伤害#伤害值调整」的表格，
            顺序为：(护甲值和盔甲韧性, 保护, 火焰保护, 爆炸保护, 弹射物保护, 摔落缓冲, 抗性提升)
            True = 该层对这次伤害生效，False = 该伤害无视该层。
            表格里没有单列的伤害类型都属"其他"行，所以查不到时用默认值。
            """
            (armor_test, protection_test, fire_protection_test, blast_protection_test,
                projectile_protection_test, feather_falling_test, resistance_test) = \
                DEFENCE.get(cause, (True, True, False, False, False, False, True))

            return amount * multiplier

        if not self.IsValid : return False
        health_comp:EntityHealthComponent = self.get_component(EntityHealthComponent, bottom=True)
        if health_comp is None or health_comp.CurrentValue <= 0 : return False
        damage_data = __can_be_damaged__()
        if not damage_data[0] : return False

        # 1) # 护甲值 / 魔咒 / 药水效果等减免
        amount = float(__damage_reduce__(damage_data[1]))
        if amount < 0 : amount = 0.0

        # 2) 受击后伤害免疫（无懈可击时间）
        if self.Damage["Time"] <= 0 :
            self.Damage["Time"] = self.HURT_IMMUNITY_TICKS
            self.Damage["Value"] = applied = amount
        elif Constants.DAMAGE_CAUSE.get(cause, False) :
            # override / self_destruct：不做差值计算，直接造成原始伤害，但仍刷新免疫时间与最后伤害
            self.Damage["Time"] = self.HURT_IMMUNITY_TICKS
            self.Damage["Value"] = applied =max(self.Damage["Value"], amount)
        else :
            applied = max(amount - self.Damage["Value"], 0.0)
            if applied : self.Damage["Value"] = amount    # 只更新最后伤害，不刷新免疫时间

        # 4) 结算
        if applied > 0 :
            if health_comp.CurrentValue <= applied : self.kill()
            else : health_comp.set_value(health_comp.CurrentValue - applied)

        return True

    def has_component(self, component_id:Union[str, EntityComponent]) -> bool :
        if hasattr(component_id, "Identifier") : component_id = component_id.Identifier
        for key in self.EntityGroupStack :
            if component_id in self.EntityComponentGroups[key] : return True
        return False

    def get_component(self, component_id:Union[str, EntityComponent], bottom:bool=False) -> Optional[EntityComponent]:
        if hasattr(component_id, "Identifier") : component_id = component_id.Identifier
        list1 = self.EntityGroupStack if bottom else reversed(self.EntityGroupStack)
        for key in list1 :
            _comp = self.EntityComponentGroups[key].get(component_id)
            if _comp : return _comp

    def get_components(self) -> List[EntityComponent] :
        comp_dict = {}
        for key in self.EntityGroupStack :
            comp_dict.update(self.EntityComponentGroups[key].items())
        return list(comp_dict.values())

    def trigger_event(self, event_name:str) :
        EntityComponentManager.trigger_event(self, event_name)

    def kill(self) :
        if not self.IsValid : return False

        health_comp:EntityHealthComponent = self.get_component(EntityHealthComponent)
        if health_comp: 
            if health_comp.CurrentValue > 0 : self.__loot__()
            health_comp.set_value(0)
        else: self.__loot__() ; self.remove()
        return True

    def remove(self):
        """立即将实体从世界中移除，清理所有关联。"""
        from .dimension import Chunk
        if not self.IsValid: return False

        #解除载具引用，并从载具的乘客列移除
        if self.VehicleEntity : 
            if self in self.VehicleEntity.Passengers: self.VehicleEntity.Passengers.remove(self)
            self.VehicleEntity = None

        #解除所有乘客引用，并添加乘客进入世界
        for passenger in self.Passengers.copy() :
            passenger.VehicleEntity = None
            health_comp:EntityHealthComponent = passenger.get_component(EntityHealthComponent)
            if health_comp and health_comp.CurrentValue <= 0 : continue
            if not passenger.IsValid : continue

            if isinstance(passenger, Player) : continue
            __attach_to_world__(passenger)
        self.Passengers.clear()

        if not isinstance(self, Player) :
            __detach_from_world__(self)

            scb = self.context.MinecraftWorld.Scoreboard
            scb.clear_participant(self.ScoreboardIdentity)
            self.IsValid = False

class Player(Entity) :
    
    def __init__(self, id:str="minecraft:player", new:bool=True) :
        from .sundries_type import Container
        if id != "minecraft:player" : raise ValueError("ID不是minecraft:player")
        super().__init__(id, new)
        world_spawn_x = self.context.MinecraftWorld.SpawnLocation[0]
        world_spawn_y = self.context.MinecraftWorld.SpawnLocation[1]
        world_spawn_z = self.context.MinecraftWorld.SpawnLocation[2]
        
        self.Sneaking = False
        self.Climbing = False
        self.Sprinting = False
        self.Swimming = False

        self.SelectedSlotIndex = 0
        self.FogStack:List = []
        self.UnlockRecipe:Set[str] = set()
        self.SpawnPoint = [world_spawn_x, world_spawn_y, world_spawn_z]

        self.Ability = AbilityManager()
        self.LevelInfo = LevelManager()
        self.GameMode = GameModeManager(self)
        self.InputPermission = InputPermissionManager()

        self.HotBar = Container()
        self.HotBar.Size = 9
        self.Inventory = Container()
        self.Inventory.Size = 27
        self.EnderChestInventory = Container()
        self.EnderChestInventory.Size = 27

    def __update_mainhand__(self) :
        _comp:EntityWearArmorComponent = self.get_component(EntityWearArmorComponent, bottom=True)
        item = self.HotBar.Items[self.SelectedSlotIndex]
        if _comp : _comp.Hand.set_item(0, item)

    def __tick__(self):
        super().__tick__()
        self.__update_mainhand__()

    def __loot__(self) :
        from .sundries_type import Container
        super().__loot__()
        if not self.context.MinecraftWorld.GameRule.keepinventory : 
            # 死亡掉落：副手、四件盔甲、快捷栏 9 格、背包 27 格（末影箱不掉）
            # 每件物品掉在玩家所在位置高一格、水平 ±1 格的随机位置
            armor_comp:EntityWearArmorComponent = self.get_component(EntityWearArmorComponent, bottom=True)
            drop_list:List[Tuple[Container, range]] = []
            if armor_comp :
                drop_list.append((armor_comp.Hand, (1, )))      # 0 号槽是当前快捷栏物品的引用，掉它会重复
                drop_list.append((armor_comp.Equippable, range(armor_comp.Equippable.Size)))
            drop_list.append((self.HotBar, range(self.HotBar.Size)))
            drop_list.append((self.Inventory, range(self.Inventory.Size)))

            for container, slots in drop_list :
                for slot in slots :
                    item = container.get_item(slot)              # 取深拷贝，掉落物不与玩家栏位共用同一个对象
                    if item is None : continue
                    container.set_item(slot, None)

                    pos = [self.Pos[0] + random.uniform(-1, 1), self.Pos[1] + 1,
                           self.Pos[2] + random.uniform(-1, 1)]
                    _entity = self.Dimension.spawn_entity("minecraft:item", pos, (0, 0))
                    _comp1:EntityItemComponent = _entity.get_component(EntityItemComponent)
                    _comp1.ItemStack = item


    def serialization(self) -> nbt.TAG_Compound:
        root = super().serialization()

        root["Dimension"] = nbt.TAG_String(self.Dimension.Identifier)
        root["Sneaking"] = nbt.TAG_Byte(1 if self.Sneaking else 0)
        root["Climbing"] = nbt.TAG_Byte(1 if self.Climbing else 0)
        root["Sprinting"] = nbt.TAG_Byte(1 if self.Sprinting else 0)
        root["Swimming"] = nbt.TAG_Byte(1 if self.Swimming else 0)

        root["SelectedSlotIndex"] = nbt.TAG_Int(self.SelectedSlotIndex)
        root["SpawnPoint"] = nbt.TAG_List([nbt.TAG_Float(float(v)) for v in self.SpawnPoint], type=nbt.TAG_Float)
        root["LevelInfo"] = self.LevelInfo.serialization()
        root["GameMode"] = nbt.TAG_Int(self.GameMode.Mode)
        root["UnlockRecipe"] = nbt.TAG_List([nbt.TAG_String(v) for v in self.UnlockRecipe], type=nbt.TAG_String)

        items_list = nbt.TAG_List([], type=nbt.TAG_Compound)
        for slot, item in enumerate(self.Inventory.Items):
            item_data = nbt.TAG_Compound()
            item_data["Slot"] = nbt.TAG_Byte(slot)
            if item is not None : item_data["Item"] = item.serialization()
            items_list.append(item_data)
        root["HotBar"] = items_list

        items_list = nbt.TAG_List([], type=nbt.TAG_Compound)
        for slot, item in enumerate(self.Inventory.Items):
            item_data = nbt.TAG_Compound()
            item_data["Slot"] = nbt.TAG_Byte(slot)
            if item is not None : item_data["Item"] = item.serialization()
            items_list.append(item_data)
        root["Inventory"] = items_list
        
        items_list = nbt.TAG_List([], type=nbt.TAG_Compound)
        for slot, item in enumerate(self.EnderChestInventory.Items):
            item_data = nbt.TAG_Compound()
            item_data["Slot"] = nbt.TAG_Byte(slot)
            if item is not None : item_data["Item"] = item.serialization()
            items_list.append(item_data)
        root["EnderChestInventory"] = items_list

        return root

    @classmethod
    def deserialization(cls, tag:nbt.TAG_Compound, cache:bool=False) -> Optional["Player"] :
        from .sundries_type import Container

        if cache :
            player = None
            for _p in cls.context.OnlinePlayer :
                if tag.get("Identifier", nbt.TAG_String()).value != "minecraft:player" : continue
                if _p.UniqueID != tag.get("UniqueID", nbt.TAG_Long()).value : continue
                player = _p
                break
            return player

        player:Player = super().deserialization(tag)

        try : player.Dimension = cls.context.DimensionManager.get_dimension(tag.get("Dimension").value)
        except : player.Dimension = cls.context.DimensionManager.get_dimension("overworld")
        player.Sneaking = bool(tag.get("Sneaking", nbt.TAG_Byte(0)).value)
        player.Climbing = bool(tag.get("Climbing", nbt.TAG_Byte(0)).value)
        player.Sprinting = bool(tag.get("Sprinting", nbt.TAG_Byte(0)).value)
        player.Swimming = bool(tag.get("Swimming", nbt.TAG_Byte(0)).value)
        player.SelectedSlotIndex = tag.get("SelectedSlotIndex", nbt.TAG_Int(0)).value

        sp = tag.get("SpawnPoint")
        if isinstance(sp, nbt.TAG_List) and len(sp) == 3:
            player.SpawnPoint = [np.float32(float(v.value)) for v in sp if isinstance(v, nbt.TAG_Float)]
        level_tag = tag.get("LevelInfo")
        if isinstance(level_tag, nbt.TAG_Compound): player.LevelInfo.deserialization(level_tag)
        gm_tag = tag.get("GameMode")
        if isinstance(gm_tag, nbt.TAG_Int): player.GameMode.set_mode(gm_tag.value)
        recipe = tag.get("UnlockRecipe")
        if isinstance(recipe, nbt.TAG_List) :
            player.UnlockRecipe.update(v.value for v in recipe if isinstance(v, nbt.TAG_String))

        def inventory_save(container:Container, nbt_obj:nbt.TAG_List) :
            if not isinstance(nbt_obj, nbt.TAG_List) : return None
            container.clear_all()
            ItemStack = cls.context.SimulatorModule.ItemStack

            for entry in nbt_obj :
                slot_tag = entry.get("Slot")
                if slot_tag is None: continue
                slot = slot_tag.value
                if not(0 <= slot < container.Size): continue

                item_tag = entry.get("Item")
                if item_tag is None: continue

                item = ItemStack.deserialization(item_tag)
                if item is not None: container.set_item(slot, item)

        hb_tag = tag.get("HotBar")
        if isinstance(hb_tag, nbt.TAG_List): inventory_save(player.HotBar, hb_tag)
        inv_tag = tag.get("Inventory")
        if isinstance(inv_tag, nbt.TAG_List): inventory_save(player.Inventory, inv_tag)
        ec_tag = tag.get("EnderChestInventory")
        if isinstance(ec_tag, nbt.TAG_List): inventory_save(player.EnderChestInventory, ec_tag)

        return player



