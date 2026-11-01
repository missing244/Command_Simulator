from typing import Dict, Union, List, Tuple, Literal, Optional, Set, TypedDict
from .. import np, Constants, MCCommandParser
from .__private import *
import re, functools, math, random, itertools
TokenCursor = MCCommandParser.ParserSystem.TokenCursor

DIMENSION_LIST= list(Constants.DIMENSION_INFO)
DISTANCE_FUNC = lambda item,origin_x,origin_y,origin_z : ((item.Pos[0]-origin_x)**2 + (item.Pos[1]-origin_y)**2 + (item.Pos[2]-origin_z)**2) ** 0.5
Selector_Argument = {"x", "y", "z", "c", "dx", "dy", "dz", "rx", "ry", "rxm", "rym", "l", "lm", "r", "rm", "scores",
    "hasitem", "haspermission", "has_property", "tag", "name", "family", "type", "m"}
Selector_Argument_Single = {"x", "y", "z", "c", "dx", "dy", "dz", "rx", "ry", "rxm", "rym", "l", "lm", "r", "rm",
    "scores", "hasitem", "haspermission", "has_property"}
Entity_SlotID = ("slot.weapon.mainhand","slot.weapon.offhand", "slot.armor.head","slot.armor.chest","slot.armor.legs",
    "slot.armor.feet","slot.hotbar","slot.inventory")
SELECTOR_VAR_MEMEROY:Dict[int, "SelectorSaveDict"] = {0:{"sort":"nearest"}}

class HasItemCondition(TypedDict, total=False):
    item: str                    # 物品ID
    location: str                # 物品栏位置
    data: int                    # 数据值
    quantity: Tuple[bool, int, int]   # (not, min, max)
    slot: Tuple[bool, int, int]       # (not, min, max)

class HasPropertyCondition(TypedDict, total=False):
    condition: Literal["has_property", "property_test"]
    name: str
    value: Union[str, int, float, bool, None]
    min: Union[int, float, None]
    max: Union[int, float, None]
    unless: bool

class SelectorSaveDict(TypedDict, total=False):
    # 坐标相关
    pos_x: float
    pos_y: float
    pos_z: float
    relative_x: float
    relative_y: float
    relative_z: float

    dx: float
    dy: float
    dz: float
    rx: float
    rxm: float
    ry: float
    rym: float

    l: float
    lm: float
    r: float
    rm: float

    limit: int
    sort: Literal["nearest", "farthest"]
    scores_if: List[Tuple[str, int, int]]
    scores_unless: List[Tuple[str, int, int]]
    m_if: Set[str]
    m_unless: Set[str]

    tag_if: Set[str]
    tag_unless: Set[str]
    name_if: Set[str]
    name_unless: Set[str]
    type_if: Set[str]
    type_unless: Set[str]
    family_if: Set[str]
    family_unless: Set[str]

    hasitem: List[HasItemCondition]
    permission_test: Dict[str, Literal["enable", "disable"]]
    has_property: List[HasPropertyCondition]




def minecraft_ID_transfor(s:str) :
    if ":" not in s : return "minecraft:%s" % s
    return s

def Quotation_String_transfor_2(s:str) -> str :
    """将字符直接拿去双引号"""
    if s[0] != "\"" or s[-1] != "\"" : return s
    return s[1:len(s)-1]



class test_tools :

    def scores_test_if(_game:MinecraftSimulator, boards:List[Tuple[str, int, int]], entity:Entity) :
        scbID = entity.ScoreboardIdentity
        for board_test in boards :
            board_name, var1, var2 = board_test[0], board_test[1], board_test[2]
            if not _game.MinecraftWorld.Scoreboard.get_objective(board_name) : return False
            a = _game.MinecraftWorld.Scoreboard.get_objective(board_name).get_score(scbID)
            if a is None or not(var1 <= a.value <= var2) : return False
        return True
    
    def scores_test_unless(_game:MinecraftSimulator, boards:List[Tuple[str, int, int]], entity:Entity) :
        scbID = entity.ScoreboardIdentity
        for board_test in boards :
            board_name, var1, var2 = board_test[0], board_test[1], board_test[2]
            if not _game.MinecraftWorld.Scoreboard.get_objective(board_name) : return True
            a = _game.MinecraftWorld.Scoreboard.get_objective(board_name).get_score(scbID)
            if a is None or var1 <= a.value <= var2 : return True
        return False
    
    def name_test(entity:Entity, name_list:List[str]) :
        entity_name = entity.CustomName.lower()
        if entity_name : return entity_name in name_list
        if entity_name in name_list : return True
        entity_id = entity.Identifier.replace("minecraft:", "", 1)
        CustomName = Constants.TRANSLATE_ID["[实体]"].get(entity_id, "entity.%s.name" % entity_id)
        return CustomName in name_list

def Selector_Condition_Test(context:CommandContext, _game:MinecraftSimulator, origin:List[np.float32], 
    selector_var:SelectorSaveDict, entity:Union[Player, Entity], is_alive:bool=True) -> bool :

    if not entity.IsValid : return False
    __health_comp:EntityDefine.EntityHealthComponent = entity.get_component(EntityDefine.EntityHealthComponent)
    if is_alive and __health_comp and __health_comp.CurrentValue <= 0 : return False

    if "type_if" in selector_var and entity.Identifier not in selector_var["type_if"] : return False
    if "type_unless" in selector_var and entity.Identifier in selector_var["type_unless"] : return False
    if "name_if" in selector_var and not test_tools.name_test(entity, selector_var["name_if"]) : return False
    if "name_unless" in selector_var and test_tools.name_test(entity, selector_var["name_unless"]) : return False

    if "rx" in selector_var and entity.Rotation[1] > selector_var["rx"] : return False
    if "rxm" in selector_var and entity.Rotation[1] < selector_var["rxm"] : return False
    if "ry" in selector_var and entity.Rotation[0] > selector_var["ry"] : return False
    if "rym" in selector_var and entity.Rotation[0] < selector_var["rym"] : return False

    if "l" in selector_var and (not isinstance(entity, Player) or entity.LevelInfo.Level > selector_var["l"]) : return False
    if "lm" in selector_var and (not isinstance(entity, Player) or entity.LevelInfo.Level < selector_var["lm"]) : return False
    if "m_if" in selector_var and (not isinstance(entity, Player) or not entity.GameMode.match_mode(selector_var["m_if"])) : return False
    if "m_unless" in selector_var and (not isinstance(entity, Player) or entity.GameMode.match_mode(selector_var["m_unless"])) : return False

    if "tag_if" in selector_var :
        if "" in selector_var["tag_if"] and entity.Tags : return False
        elif "" not in selector_var["tag_if"] and not(selector_var["tag_if"] <= entity.Tags) : return False
    if "tag_unless" in selector_var :
        if "" in selector_var["tag_unless"] and (not entity.Tags) : return False
        elif "" not in selector_var["tag_unless"] and (selector_var["tag_unless"] & entity.Tags) : return False

    if "family_if" in selector_var or "family_unless" in selector_var :
        __family_comp:EntityDefine.EntityTypeFamilyComponent = entity.get_component(EntityDefine.EntityTypeFamilyComponent)
        __family = __family_comp.Family if __family_comp else set()
        if "family_if" in selector_var and not(selector_var["family_if"] <= __family) : return False
        if "family_unless" in selector_var and (selector_var["family_unless"] & __family) : return False

    if "scores_if" in selector_var and not test_tools.scores_test_if(_game, selector_var["scores_if"], entity) : return False
    if "scores_unless" in selector_var and test_tools.scores_test_unless(_game, selector_var["scores_unless"], entity) : return False

    if "permission_test" in selector_var :
        if not isinstance(entity, Player) : return False
        for _premission, __able in selector_var["permission_test"].items() :
            __test1 = __able == "enable"
            __test2 = entity.InputPermission.get_permission(_premission)
            if __test1 != __test2 : return False
    
    if "r" in selector_var or "rm" in selector_var :
        if entity.Dimension is not context.dimension : return False
        distance = DISTANCE_FUNC(entity, *origin)
        if "r" in selector_var and distance > selector_var["r"] : return False
        if "rm" in selector_var and distance < selector_var["rm"] : return False

    if "hasitem" in selector_var :
        ArmorComp:EntityDefine.EntityWearArmorComponent = entity.get_component(EntityDefine.EntityWearArmorComponent)
        EquippableComp:EntityDefine.EntityEquippableComponent = entity.get_component(EntityDefine.EntityEquippableComponent)
        InventoryComp:EntityDefine.EntityInventoryComponent = entity.get_component(EntityDefine.EntityInventoryComponent)
        InventoryComp = InventoryComp.Container if InventoryComp else None
        HotBarComp = entity.HotBar if isinstance(entity, Player) else None
        InventoryComp = entity.Inventory if isinstance(entity, Player) else InventoryComp
        EnderInventoryComp = entity.EnderChestInventory if isinstance(entity, Player) else None
        for condition in selector_var["hasitem"]:
            item_id = condition["item"]
            data_val = condition["data"]
            locations = condition["location"]
            quantity_range = condition["quantity"]
            slot_range = condition["slot"] if condition["slot"] else (True, 0, 63)
            slot_items:List[Optional[ItemStack]] = []

            for location in ([locations] if locations else Entity_SlotID) :
                if location == "slot.weapon.mainhand" and ArmorComp and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(ArmorComp.Hand.get_item(0, deepcopy=False))
                elif location == "slot.weapon.offhand" and ArmorComp and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(ArmorComp.Hand.get_item(1, deepcopy=False))
                elif location == "slot.armor.head" and ArmorComp and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(ArmorComp.Equippable.get_item(0, deepcopy=False))
                elif location == "slot.armor.chest" and ArmorComp and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(ArmorComp.Equippable.get_item(1, deepcopy=False))
                elif location == "slot.armor.legs" and ArmorComp and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(ArmorComp.Equippable.get_item(2, deepcopy=False))
                elif location == "slot.armor.feet" and ArmorComp and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(ArmorComp.Equippable.get_item(3, deepcopy=False))
                elif location == "slot.enderchest" and EnderInventoryComp :
                    for __slot_id in range(0, EnderInventoryComp.Size) :
                        if (slot_range[0] == (slot_range[1] <= __slot_id <= slot_range[2])
                        ) : slot_items.append(EnderInventoryComp.get_item(__slot_id, deepcopy=False))
                elif location == "slot.hotbar" and HotBarComp :
                    for __slot_id in range(0, HotBarComp.Size) :
                        if (slot_range[0] and slot_range[1] <= __slot_id <= slot_range[2]) or (
                        not slot_range[0] and not(slot_range[1] <= __slot_id <= slot_range[2])
                        ) : slot_items.append(HotBarComp.get_item(__slot_id, deepcopy=False))
                elif location == "slot.inventory" and InventoryComp :
                    for __slot_id in range(0, InventoryComp.Size) :
                        if (slot_range[0] == (slot_range[1] <= __slot_id <= slot_range[2])
                        ) : slot_items.append(InventoryComp.get_item(__slot_id, deepcopy=False))
                elif location == "slot.saddle" and EquippableComp and len(EquippableComp.EquipItem) > 0 and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(EquippableComp.EquipItem[0])
                elif location == "slot.armor" and EquippableComp and len(EquippableComp.EquipItem) > 1 and (
                    (slot_range[0] == (slot_range[1] <= 0 <= slot_range[2])
                    )) : slot_items.append(EquippableComp.EquipItem[1])
                elif location == "slot.chest": pass
                elif location == "slot.equippable": pass

            item_count = 0
            for item_obj in slot_items :
                if not(item_obj) or item_obj.Identifier != item_id : continue
                if "damage" in _game.GameSource.ITEM.get(item_obj.Identifier, {}) :
                    _comp:ItemDurabilityComponent = item_obj.get_component(ItemDurabilityComponent)
                    if _comp and (data_val < 0 or _comp.Damage == data_val): item_count += int(item_obj.Count)
                elif item_obj.Damage == data_val: item_count += int(item_obj.Count)

            # 检查 quantity 范围
            q_not, q_min, q_max = quantity_range
            in_q_range = (q_min <= item_count <= q_max)
            if q_not ^ in_q_range: return False

    if "dx" in selector_var or "dy" in selector_var or "dz" in selector_var :
        if entity.Dimension is not context.dimension : return False
        AABB:EntityDefine.EntityAABBComponent = entity.get_component(EntityDefine.EntityAABBComponent)
        Scale:EntityDefine.EntityScaleComponent = entity.get_component(EntityDefine.EntityScaleComponent)
        AABB_Width, AABB_Height = AABB.Width if AABB else 0, AABB.Height if AABB else 0
        ScaleVar = Scale.Value if Scale else 1
        Width, Height = AABB_Width*ScaleVar/2, AABB_Height*ScaleVar

        x, y, z = origin[0], origin[1], origin[2]
        dx, dy, dz = selector_var.get("dx", 0), selector_var.get("dy", 0), selector_var.get("dz", 0)

        min_x, min_y, min_z = min(x, x + dx), min(y, y + dy), min(z, z + dz)
        max_x, max_y, max_z = max(x, x + dx) + 1, max(y, y + dy) + 1, max(z, z + dz) + 1
        entity_min_x = entity.Pos[0] - Width
        entity_max_x = entity.Pos[0] + Width
        entity_min_y = entity.Pos[1]
        entity_max_y = entity.Pos[1] + Height
        entity_min_z = entity.Pos[2] - Width
        entity_max_z = entity.Pos[2] + Width

        if (entity_max_x < min_x or entity_min_x > max_x or
            entity_max_y < min_y or entity_min_y > max_y or
            entity_max_z < min_z or entity_min_z > max_z):
            return False

    if "has_property" in selector_var :
        PropertyComp:EntityDefine.EntityPropertyComponent = entity.get_component(EntityDefine.EntityPropertyComponent)
        PropertyDict = PropertyComp.Properties if PropertyComp else {}
        for condition in selector_var["has_property"] :
            prop_name, cond_not, cond_type = condition["name"], condition["unless"], condition["condition"]
            prop_exists = prop_name in PropertyDict

            if cond_type == "has_property":
                if prop_exists == cond_not: return False
                else : continue
            elif cond_type == "property_test":
                if not prop_exists: return False
                prop_value = PropertyDict[prop_name]

                if "min" in condition and condition["min"] is not None:
                    min_val, max_val = condition["min"], condition["max"]
                    try: in_range = (min_val <= prop_value <= max_val)
                    except TypeError: return False
                    result = in_range
                elif "value" in condition and condition["value"] is not None:
                    expected = condition["value"]
                    result = isinstance(expected, prop_value.__class__) and prop_value == expected
                else: result = False

                if cond_not: result = not result
                if not result: return False

    return True



def apply_selector_position(context_location:List[float], selector_save:SelectorSaveDict) -> List[np.float32]:
    """根据选择器参数计算新位置（不修改原列表）"""
    new_pos = list(np.float32(i) for i in context_location)

    if "x" in selector_save: new_pos[0] = np.float32(selector_save["x"])
    elif "relative_x" in selector_save: 
        new_pos[0] = np.float32(new_pos[0]) + np.float32(selector_save["relative_x"])

    # Y 轴
    if "y" in selector_save: new_pos[0] = np.float32(selector_save["y"])
    elif "relative_y" in selector_save: 
        new_pos[0] = np.float32(new_pos[0]) + np.float32(selector_save["relative_y"])

    # Z 轴
    if "z" in selector_save: new_pos[0] = np.float32(selector_save["z"])
    elif "relative_z" in selector_save: 
        new_pos[0] = np.float32(new_pos[0]) + np.float32(selector_save["relative_z"])

    return new_pos

def get_all_passengers(entity:'Entity') -> List['Entity'] :
    result, visited = [], set()
    stack = list(entity.Passengers)
    while stack :
        passenger = stack.pop(0)
        if isinstance(passenger, Player) : continue
        if passenger in visited : continue          # Entity.__hash__ = UniqueID
        visited.add(passenger)
        result.append(passenger)
        stack.extend(passenger.Passengers)
    return result

#@e
def RunTime_Selector_Entity(context:CommandContext, _game:MinecraftSimulator, selector_var:SelectorSaveDict) -> List[Entity] :
    entity_list_copy:List[Entity] = []
    entity_list_copy.extend(_game.OnlinePlayer)
    for __player in _game.OnlinePlayer : entity_list_copy.extend(get_all_passengers(__player))
    for _dim in Constants.DIMENSION_INFO.keys() : 
        all_load_entity = _game.DimensionManager.get_dimension(_dim).EntityCache
        all_unload_entity = _game.DimensionManager.get_dimension(_dim).UnloadChunkEntityCache
        all_entity = all_load_entity + all_unload_entity
        entity_list_copy.extend(all_entity)
        for _e in all_entity : entity_list_copy.extend(get_all_passengers(_e))

    select_origin = apply_selector_position(context.location, selector_var)
    entity_limit = selector_var.get("limit", 2147483647)
    entity_saves:List[Entity] = [i for i in entity_list_copy if Selector_Condition_Test(context, _game, select_origin, selector_var, i)]
    entity_list_result = sorted(
        entity_saves, key=functools.partial(DISTANCE_FUNC, origin_x=select_origin[0],
        origin_y=select_origin[1], origin_z=select_origin[2]), 
        reverse=(selector_var.get("sort", "nearest")=="farthest")
    )

    return entity_list_result[0 : entity_limit]

#"player"
def RunTime_Selector_Name(context:CommandContext, _game:MinecraftSimulator, name:str) -> List[Entity] :
    entity_saves : List[Entity] = [entity for entity in _game.OnlinePlayer if name == entity.CustomName]
    if not entity_saves : return entity_saves

    __health_comp:EntityDefine.EntityHealthComponent = entity_saves[0].get_component(EntityDefine.EntityHealthComponent)
    if __health_comp and __health_comp.CurrentValue <= 0 : entity_saves.clear()
    return entity_saves

#@p
def RunTime_Selector_Player(context:CommandContext, _game:MinecraftSimulator, selector_var:SelectorSaveDict) -> List[Entity] :
    entity_list:List[Player] = []
    select_origin = apply_selector_position(context.location, selector_var)
    entity_limit = selector_var.get("limit", 1)
    for _entity in _game.OnlinePlayer :
        test = Selector_Condition_Test(context, _game, select_origin, selector_var, _entity, is_alive=True)
        if test : entity_list.append(_entity)

    entity_list_result = sorted(
        entity_list, key=functools.partial(DISTANCE_FUNC, origin_x=select_origin[0],
        origin_y=select_origin[1], origin_z=select_origin[2]), 
        reverse=(selector_var.get("sort", "nearest")=="farthest")
    )

    return entity_list_result[0 : entity_limit]

#@a
def RunTime_Selector_All_Player(context:CommandContext, _game:MinecraftSimulator, selector_var:SelectorSaveDict) -> List[Entity] : 
    entity_list:List[Player] = []
    select_origin = apply_selector_position(context.location, selector_var)
    entity_limit = selector_var.get("limit", 2147483647)
    for _entity in _game.OnlinePlayer :
        test = Selector_Condition_Test(context, _game, select_origin, selector_var, _entity, is_alive=False)
        if test : entity_list.append(_entity)

    entity_list_result = sorted(
        entity_list, key=functools.partial(DISTANCE_FUNC, origin_x=select_origin[0],
        origin_y=select_origin[1], origin_z=select_origin[2]),
        reverse=(selector_var.get("sort", "nearest")=="farthest")
    )

    return entity_list_result[0 : entity_limit]

#@r
def RunTime_Selector_Random(context:CommandContext, _game:MinecraftSimulator, selector_var:SelectorSaveDict) -> List[Entity] :
    entity_list_copy:List[Entity] = []
    entity_list_copy.extend(_game.OnlinePlayer)
    type_if = selector_var.get("type_if", set())
    type_unless = selector_var.get("type_unless", set())
    if type_unless or (type_if and "minecraft:player" not in type_if) :
        for __player in _game.OnlinePlayer : entity_list_copy.extend(get_all_passengers(__player))
        for _dim in Constants.DIMENSION_INFO.keys() : 
            all_load_entity = _game.DimensionManager.get_dimension(_dim).EntityCache
            all_unload_entity = _game.DimensionManager.get_dimension(_dim).UnloadChunkEntityCache
            all_entity = all_load_entity + all_unload_entity
            entity_list_copy.extend(all_entity)
            for _e in all_entity : entity_list_copy.extend(get_all_passengers(_e))

    select_origin = apply_selector_position(context.location, selector_var)
    entity_limit = selector_var.get("limit", 1)
    entity_saves:List[Entity] = [i for i in entity_list_copy if Selector_Condition_Test(context, _game, select_origin, selector_var, i)]

    random.shuffle(entity_saves)
    return entity_saves[0 : entity_limit]

#@s
def RunTime_Selector_Self(context:CommandContext, _game:MinecraftSimulator, selector_var:SelectorSaveDict) -> List[Entity] :
    entity_list = [context.executer] if isinstance(context.executer, Entity) else []
    select_origin = apply_selector_position(context.location, selector_var)
    test = bool(entity_list) and Selector_Condition_Test(context, _game, select_origin, selector_var, entity_list[0], is_alive=False)

    if not test : entity_list.clear()
    return entity_list

#@initiator
def RunTime_Selector_Initiator(context:CommandContext, _game:MinecraftSimulator) -> List[Entity] :
    return []



def HasItem_Complier(_game:MinecraftSimulator, token_cursor:TokenCursor) :
    conditions:List[dict] = [] 

    __start_conditions = token_cursor.matches("Start_Item_Condition")
    __condition = {"item":None, "location":None, "data":0, "quantity":(True, 1, 131072), "slot":None}
    condition = __condition.copy()
    while True :
        if token_cursor.matches("End_Item_Argument") :
            __current = token_cursor.tell() - 1
            if not condition["item"] : raise CompileError("hasitem条件缺少物品ID", __current, __current+1)
            if (not condition["location"]) and condition["slot"] : 
                raise CompileError("hasitem条件缺少location定义", __current, __current+1)
            conditions.append(condition)
            if __start_conditions is None : break
            elif token_cursor.matches("Next_Item_Condition"): continue
            elif token_cursor.matches("End_Item_Condition"): break
            else : break
        elif token_cursor.matches("Next_Item_Argument"): continue
        elif token_cursor.matches("Start_Item_Argument"): 
            condition = __condition.copy()
            continue
        elif token_cursor.peek()["type"] == "Item_Argument" :
            key_token = token_cursor.advance()
            key = key_token["token"]  # item/data/quantity/location/slot
            token_cursor.advance()

            if key == "item":
                __token = token_cursor.advance()
                condition["item"] = item_id = minecraft_ID_transfor(__token["token"])
                if item_id not in _game.GameSource.ITEM :
                    raise CompileError("hasitem.item 参数是无效物品ID", token_cursor.tell()-1, token_cursor.tell())
            elif key == "data":
                __token = token_cursor.advance()
                data_val = __token["token"]
                if not (0 <= data_val <= 32767):
                    raise CompileError("hasitem data 值必须在 0~32767 之间", token_cursor.tell()-1, token_cursor.tell())
                condition["data"] = data_val
            elif key == "quantity":
                range_data = Range_Complier(token_cursor)
                condition["quantity"] = range_data
            elif key == "location":
                __token = token_cursor.advance()
                condition["location"] = __token["token"]
            elif key == "slot":
                range_data = Range_Complier(token_cursor)
                condition["slot"] = range_data

        else : break
    return conditions

def Range_Complier(token_cursor:TokenCursor) -> Tuple[bool, int, int]:
    range_list = [True, -2147483648, 2147483647]
    if token_cursor.matches("Not") : range_list[0] = False
    
    __token = token_cursor.matches("Range_Min")
    if __token : range_list[1] = __token["token"]

    if token_cursor.matches("Range_Sign") :
        __token = token_cursor.matches("Range_Max")
        if __token : range_list[2] = __token["token"]
    else : range_list[2] = range_list[1]

    return tuple(range_list)

def Selector_Save_Set(_game:MinecraftSimulator, selector_save:SelectorSaveDict, 
    token_cursor:TokenCursor, selector_argument:str) :

    if selector_argument in {"x","y","z"} :
        token_cursor.seek(1, 1)
        __token = token_cursor.advance()
        key1 = "pos_%s" % selector_argument
        key2 = "relative_%s" % selector_argument
        if __token["type"] == "Value" : selector_save[key1] = __token["token"]
        elif __token["type"] == "Relative_Value" :
            if len(__token["token"]) > 1 : selector_save[key2] = float(__token["token"][1:])
            else : selector_save[key2] = 0.0

    elif selector_argument in {"dx","dy","dz","rxm","rx","rym","ry"} :
        token_cursor.seek(1, 1)
        __token = token_cursor.advance()
        selector_save[selector_argument] = __token["token"]

    elif selector_argument in {"lm","l"} :
        token_cursor.seek(1, 1)
        __token = token_cursor.advance()
        selector_save[selector_argument] = __token["token"]
        if selector_save[selector_argument] < 0 : raise CompileError("等级参数不能为负数", token_cursor.tell()-1, token_cursor.tell())
    
    elif selector_argument in {"rm","r"} :
        token_cursor.seek(1, 1)
        __token = token_cursor.advance()
        selector_save[selector_argument] = __token["token"]
        if selector_save[selector_argument] < 0 : raise CompileError("距离参数不能为负数", token_cursor.tell()-1, token_cursor.tell())

    elif selector_argument == "c" :
        token_cursor.seek(1, 1)
        __token = token_cursor.advance()
        selector_save["limit"] = __token["token"]
        if selector_save["limit"] == 0 : raise CompileError("数量参数不能为0", token_cursor.tell()-1, token_cursor.tell())
        elif selector_save["limit"] < 0 : 
            selector_save["sort"] = "farthest"
            selector_save["limit"] = -selector_save["limit"]

    elif selector_argument == "scores" :
        token_cursor.seek(2, 1)
        while 1 :
            __token = token_cursor.advance()
            if __token["type"] == "End_Score_Argument" : break
            if __token["type"] == "Next_Score_Argument" : continue
            score_name = Quotation_String_transfor_2(__token["token"])

            range_data = Range_Complier(token_cursor)
            score_mode = "scores_if" if range_data[0] else "scores_unless"
            score_min, score_max = range_data[1], range_data[2]
            if score_mode not in selector_save : selector_save[score_mode] = []
            selector_save[score_mode].append((score_name, score_min, score_max))

    elif selector_argument == "haspermission" :
        token_cursor.seek(2, 1)
        while 1 :
            __token = token_cursor.advance()
            if __token["type"] == "End_Permission_Argument" : break
            elif __token["type"] == "Next_Permission_Argument" : continue
            elif __token["type"] == "Permission_Argument" :
                permission = __token["token"]
                if permission not in Constants.INPUT_PERMISSION :
                    raise CompileError("不存在的输入权限ID：%s" % permission, token_cursor.tell()-1, token_cursor.tell())
                token_cursor.seek(1, 1)
                __token = token_cursor.advance()
                if "permission_test" not in selector_save : selector_save["permission_test"] = {}
                selector_save["permission_test"][permission] = __token["token"]

    elif selector_argument == "hasitem" :
        token_cursor.seek(1, 1)
        hasitem_list = HasItem_Complier(_game, token_cursor)
        selector_save.setdefault("hasitem", []).extend(hasitem_list)

    elif selector_argument in {"tag", "name", "family", "type", "m"} :
        token_cursor.seek(1, 1)
        __token = token_cursor.matches("Not")
        mode = ("%s_unless" if __token else "%s_if") % selector_argument
        
        __token = token_cursor.matches("Value")
        if selector_argument == "tag" and (not __token) :
            if mode not in selector_save : selector_save[mode] = set()
            selector_save[mode].add("")
        else : 
            __value = Quotation_String_transfor_2(__token["token"])
            if selector_argument == "type" : 
                __value = minecraft_ID_transfor(__value)
                if __value not in _game.GameSource.ENTITY : 
                    raise CompileError("不存在的实体ID：%s" % __value, token_cursor.tell()-1, token_cursor.tell())
                if __value == "minecraft:villager" : __value = "minecraft:villager_v2"
            if mode not in selector_save : selector_save[mode] = set()
            if selector_argument == "name" : __value = __value.lower()
            selector_save[mode].add(__value)

    elif selector_argument == "has_property" :
        token_cursor.seek(2, 1)
        while 1 :
            __token = token_cursor.advance()
            if __token["type"] == "End_Property_Argument" : break
            elif __token["type"] == "Next_Property_Argument" : continue
            elif __token["type"] == "Property_Argument" : 
                token_cursor.seek(1, 1)
                condition_json = {"condition":"has_property", "name":"", "not":False}
                if token_cursor.matches("Not") : condition_json["not"] = True
                _token = token_cursor.advance()
                condition_json["name"] = name = _token["token"]
                if not any( (name in data["description"].get("properties", {}) \
                    for _, data in _game.GameSource.ENTITY.items()) ) :
                    raise CompileError("不存在的实体属性：%s" % name, token_cursor.tell()-1, token_cursor.tell())
                if "has_property" not in selector_save : selector_save["has_property"] = []
                selector_save["has_property"].append(condition_json)
            elif __token["type"] == "Property" : 
                condition_json = {"condition":"property_test", "name":"", "value":None, "min":None, "max":None, "unless":False}
                condition_json["name"] = name = __token["token"]
                if not any( (name in data["description"].get("properties", {}) \
                    for _, data in _game.GameSource.ENTITY.items()) ) :
                    raise CompileError("不存在的实体属性：%s" % name, token_cursor.tell()-1, token_cursor.tell())
                
                token_cursor.seek(1, 1)
                __token = token_cursor.advance()
                if __token["type"] == "Bool" : condition_json["value"] = _token["token"] == "true"
                elif __token["type"] == "Float" : condition_json["value"] = __token["token"]
                elif __token["type"] == "String" : condition_json["value"] = Quotation_String_transfor_2(__token["token"])
                else :
                    token_cursor.seek(-1, 1)
                    range_data = Range_Complier(token_cursor)
                    if not range_data[0] : condition_json["unless"] = True
                    condition_json["min"], condition_json["max"] = range_data[1], range_data[2]

                if "has_property" not in selector_save : selector_save["has_property"] = []
                selector_save["has_property"].append(condition_json)

def Selector_Compiler(_game:MinecraftSimulator, token_cursor:TokenCursor) :
    """{
        "x":float, "y":float, "z":float, "relative_x":float, "relative_y":float, "relative_z":float,
        "dx": float, "dy": float, "dz": float, "rx": float, "rxm": float, "ry": float, "rym": float,
        "l": float, "lm": float, "r": float, "rm": float, 
        "scores_if":[], "scores_unless":[],  --->  List[(str, int, int)]
        "m_if":{}, "m_unless":{}, 
        "tag_if":{}, "tag_unless":{},
        "name_if":{}, "name_unless":{}, 
        "type_if":{}, "type_unless":{},
        "family_if":{}, "family_unless":{}, 
        "hasitem":[], "permission_test":{}, "has_property":[],
        "limit":int, "sort":nearest|farthest,
    }"""

    selector_save:SelectorSaveDict = {"sort":"nearest"}
    selector_token = token_cursor.advance()
    selector_var = selector_token["token"]
    cursor_start_pointer = start_token_index = token_cursor.tell()
    selector_argument_count = {i:0 for i in Selector_Argument_Single}

    #玩家名字选择器编译
    if selector_token["type"] == "Player_Name" :
        player_name = Quotation_String_transfor_2(selector_var)
        return functools.partial(RunTime_Selector_Name, name=player_name)

    #选择器函数导出
    if selector_var == "@p" : selector_func = RunTime_Selector_Player
    elif selector_var == "@a" : selector_func = RunTime_Selector_All_Player
    elif selector_var == "@r" : selector_func = RunTime_Selector_Random
    elif selector_var == "@e" : selector_func = RunTime_Selector_Entity
    elif selector_var == "@s" : selector_func = RunTime_Selector_Self
    elif selector_var == "@initiator" : return RunTime_Selector_Initiator
    elif selector_var == "@n" : selector_save["limit"] = 1 ; selector_func = RunTime_Selector_Entity

    #选择器哈希计算
    check_sum = 0
    if token_cursor.is_not_end() and token_cursor.peek()["type"] == "Start_Selector_Argument" :
        while token_cursor.is_not_end() :
            __token = token_cursor.advance()
            check_sum += hash(__token["token"])
            if __token["type"] == "End_Selector_Argument" : break
        if check_sum in SELECTOR_VAR_MEMEROY : selector_save = SELECTOR_VAR_MEMEROY[check_sum]
        else : token_cursor.seek(cursor_start_pointer)
    else : 
        selector_save = SELECTOR_VAR_MEMEROY[check_sum]
        return functools.partial(selector_func, selector_var=selector_save)

    #选择器参数编译
    if check_sum not in SELECTOR_VAR_MEMEROY :
        while token_cursor.is_not_end() :
            __token = token_cursor.advance()
            if   __token["type"] == "Next_Selector_Argument" : continue
            elif __token["type"] == "Start_Selector_Argument" : continue
            elif __token["type"] == "End_Selector_Argument" : break
            elif __token["type"] == "Selector_Argument" : 
                selector_argument = __token["token"]
                if selector_argument in selector_argument_count :
                    selector_argument_count[selector_argument] += 1
                    if selector_argument_count[selector_argument] > 1 : raise CompileError(
                        "重复的选择器 %s 参数" % selector_argument, token_cursor.tell()-1, token_cursor.tell())
                Selector_Save_Set(_game, selector_save, token_cursor, selector_argument)
        SELECTOR_VAR_MEMEROY[check_sum] = selector_save

    end_token_index = token_cursor.tell() - 1
    if "r" in selector_save and "rm" in selector_save and selector_save["rm"] > selector_save["r"] : 
        raise CompileError("距离参数上限不能小于下限", start_token_index, end_token_index)
    if "l" in selector_save and "lm" in selector_save and selector_save["lm"] > selector_save["l"] : 
        raise CompileError("等级参数上限不能小于下限", start_token_index, end_token_index)

    if selector_func is RunTime_Selector_Random and selector_save["sort"] == "farthest" :
        raise CompileError("随机选择器的数量参数不能为负数", start_token_index, end_token_index)
    if selector_func is RunTime_Selector_Player and len(selector_save.get("type_if", {})) > 0 and \
        "minecraft:player" in selector_save["type_if"] :
        raise CompileError("@p选择器指定了非玩家条件", start_token_index, end_token_index)
    if selector_func is RunTime_Selector_All_Player and len(selector_save.get("type_if", {})) > 0 and \
        "minecraft:player" in selector_save["type_if"] :
        raise CompileError("@a选择器指定了非玩家条件", start_token_index, end_token_index)
    if selector_func is RunTime_Selector_Random and selector_save["sort"] == "farthest" :
        raise CompileError("随机选择器的数量参数不能为负数", start_token_index, end_token_index)
    if "name_if" in selector_save and len(selector_save["name_if"]) > 1 : 
        raise CompileError("选择器参数 name 具有重复指定的正选条件", start_token_index, end_token_index)
    if "name_if" in selector_save and "name_unless" in selector_save and len(selector_save["name_if"]) > 0 and len(selector_save["name_unless"]) > 0 : 
        raise CompileError("选择器参数 name 同时存在正反选条件", start_token_index, end_token_index)
    if "type_if" in selector_save and len(selector_save["type_if"]) > 1 : 
        raise CompileError("选择器参数 type 具有重复指定的正选条件", start_token_index, end_token_index)
    if "type_if" in selector_save and "type_unless" in selector_save and len(selector_save["type_if"]) > 0 and len(selector_save["type_unless"]) > 0 :
        raise CompileError("选择器参数 type 同时存在正反选条件", start_token_index, end_token_index)
    if "m_if" in selector_save and len(selector_save["m_if"]) > 1 : 
        raise CompileError("选择器参数 m 具有重复指定的正选条件", start_token_index, end_token_index)
    if "m_if" in selector_save and "m_unless" in selector_save and len(selector_save["m_if"]) > 0 and len(selector_save["m_unless"]) > 0 :
        raise CompileError("选择器参数 m 同时存在正反选条件", start_token_index, end_token_index)
    
    return functools.partial(selector_func, selector_var=selector_save)




def is_player_only_selector(selector_partial:functools.partial) -> bool:
    """
    判断编译后的选择器是否只匹配玩家。
    -----------------------------
    :param selector_partial: functools.partial 对象，来自 Selector_Compiler
    :return: True 表示只匹配玩家，False 表示可能匹配其他实体
    """
    func = selector_partial.func

    # 直接就是玩家专用选择器
    if func in (RunTime_Selector_Player, RunTime_Selector_All_Player, 
        RunTime_Selector_Name, RunTime_Selector_Self, RunTime_Selector_Initiator): return True

    # 实体/自身等选择器需要检查 type_if
    if func in (RunTime_Selector_Entity, RunTime_Selector_Random):
        # 获取传入的关键字参数（可能存在 selector_var）
        keywords = selector_partial.keywords or {}
        selector_var = keywords.get("selector_var", {})
        type_if = selector_var.get("type_if")
        if type_if is not None :
            if "minecraft:player" in type_if : return True
        elif func is RunTime_Selector_Random :
            if type_if is None : return True
        return False

    return False

def is_npc_only_selector(selector_partial:functools.partial) -> bool:
    """
    判断编译后的选择器是否只匹配NPC。
    -------------------------------
    :param selector_partial: functools.partial 对象，来自 Selector_Compiler
    :return: True 表示只匹配玩家，False 表示可能匹配其他实体
    """
    func = selector_partial.func
    if func is RunTime_Selector_Self : return True

    # 实体/自身等选择器需要检查 type_if
    if func in (RunTime_Selector_Entity, RunTime_Selector_Random):
        # 获取传入的关键字参数（可能存在 selector_var）
        keywords = selector_partial.keywords or {}
        selector_var = keywords.get("selector_var", {})
        type_if = selector_var.get("type_if", {})
        if "minecraft:npc" in type_if : return True
        return False

    return False

def is_single_entity_selector(selector_partial:functools.partial) -> bool :
    if selector_partial.func is RunTime_Selector_Self : return True
    if selector_partial.func is RunTime_Selector_Initiator : return True

    selector_var = selector_partial.keywords.get("selector_var", {})
    if selector_partial.func is RunTime_Selector_Random and "limit" not in selector_var : return True
    if selector_partial.func is RunTime_Selector_Player and "limit" not in selector_var : return True
    limit = selector_var.get("limit", 2147483647)
    return limit == 1
