from .compiler import CommandPerProcess
from .__private import *
from . import CompileError
import functools, string, random, math, itertools, json, copy
from typing import Dict, Union, List, Tuple, Literal, Callable
DISTANCE_FUNC = lambda pos1x,pos1z,pos2x,pos2z: (pow(pos1x-pos2x, 2) + pow(pos1z-pos2z, 2)) ** 0.5
EntitySlotAcceptItem = {
    "slot.armor.chest" : ["minecraft:leather_chestplate","minecraft:chainmail_chestplate","minecraft:iron_chestplate",
        "minecraft:diamond_chestplate","minecraft:netherite_chestplate","minecraft:golden_chestplate","minecraft:copper_chestplate"],
    "slot.armor.legs" : ["minecraft:leather_leggings","minecraft:chainmail_leggings","minecraft:iron_leggings",
        "minecraft:diamond_leggings","minecraft:netherite_leggings","minecraft:golden_leggings","minecraft:copper_leggings"],
    "slot.armor.feet" : ["minecraft:leather_boots","minecraft:chainmail_boots","minecraft:iron_boots",
        "minecraft:diamond_boots","minecraft:netherite_boots","minecraft:golden_boots","minecraft:copper_boots"]}


class hud :
    """
    /hud <目标: 玩家选择器> <hide|reset> [HUD元素]

    HUD元素取值来自 Constants.HUD_TYPE。本模拟器没有客户端界面状态，
    因此只做参数校验与结果反馈。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        mode = pre_process.args["Argument"][0]                       # hide / reset
        hud_element = pre_process.args.get("Hud_Type", ("all", ))[0]
        if hud_element not in Constants.HUD_TYPE :
            token_index = pre_process.args_token_index["Hud_Type"][0]
            raise CompileError("不存在的HUD元素：%s" % hud_element, token_index[0], token_index[0])

        return functools.partial(cls.run, s=command, entity_get=entity_func, mode=mode, hud_element=hud_element)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            mode:Literal["hide","reset"], hud_element:str="all") :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("以下玩家HUD元素 $element 已$mode：\n$entity").substitute(
            element = hud_element,
            mode = "隐藏" if mode == "hide" else "重置",
            entity = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class inputpermission :
    """
    /inputpermission query <目标: 玩家选择器> [权限] [状态]
    /inputpermission set   <目标: 玩家选择器> <权限> <状态>

    直接映射到 Player.InputPermission（InputPermissionManager），权限名与其 PermissionMap 的键一致：
    camera / movement / lateral_movement / sneak / jump / mount / dismount / move_forward / move_backward /
    move_left / move_right。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        mode = pre_process.args["Argument"][0]                     # query / set

        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        permission = pre_process.args.get("Permission")[0]
        if permission not in Constants.INPUT_PERMISSION :
            token_index = pre_process.args_token_index["Permission"][0]
            raise CompileError("不存在的权限：%s" % permission, token_index[0], token_index[0])
        state = pre_process.args.get("State", (None, ))[0]

        if mode == "set" : return functools.partial(cls.set, s=command, entity_get=entity_func,
            permission=permission, enabled=(state == "enabled"))
        return functools.partial(cls.query, s=command, entity_get=entity_func, permission=permission, state=state)

    def query(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
              permission:str=None, state:str=None) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        if state is None : # 写了权限：输出该权限的值
            msg_list = ["%s --> %s" % (player, player.InputPermission.get_permission(permission)) for player in entity_list]
        else :  # 权限 + 状态：过滤出匹配的玩家
            matched = [str(player) for player in entity_list if player.InputPermission.get_permission(permission) == (state == "enabled")]
            if not matched : return CommandResult(False, s, "没有玩家的 %s 权限为 %s" % (permission, state), [context])
            msg_list = ["%s 的权限为 %s" % (", ".join(matched), state)]

        return CommandResult(True, s, "已查询以下玩家的权限：\n" + "\n".join(msg_list), [context]) \
            .set_affected_entities(entity_list)

    def set(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            permission:str, enabled:bool) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        for player in entity_list : player.InputPermission.set_permission(permission, enabled)
        temp = string.Template("以下玩家的$p权限修改为$v：\n$msg").substitute(
            p = permission, v = "enabled" if enabled else "disabled",
            msg = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class kick :
    """
    /kick <目标: 玩家选择器> [原因]

    本模拟器没有真实连接，因此只做“虚假踢出”：反馈被踢出的玩家与原因。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command

        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        return functools.partial(cls.run, s=command, entity_get=entity_func)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("踢出了以下玩家(虚假踢出)：\n$entity").substitute(
            entity = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class kill :
    """
    /kill [<目标: 选择器>]

    对匹配到的实体调用 Entity.kill()（无生命值的实体直接移除），不写选择器时以执行者为目标。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = None
        if pre_process.selectors : entity_func = pre_process.selectors[0]
        return functools.partial(cls.run, s=command, entity_get=entity_func)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction=None) :
        if entity_get : entity_list:List[Entity] = entity_get(context, game)
        else : entity_list:List[Entity] = [context.executer] if isinstance(context.executer, Entity) else []
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        name_list = [str(i) for i in entity_list]
        for entity in entity_list : entity.kill()
        temp = string.Template("清除了$count个实体：\n$entity").substitute(
            count = len(name_list), entity = ", ".join(name_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class list_command :
    """
    /list

    列出当前世界内的在线玩家。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        return functools.partial(cls.run, s=pre_process.parser_result.command)

    def run(context:CommandContext, game:MinecraftSimulator, s:str) :
        entity_list:List[Player] = list(game.OnlinePlayer)
        temp = string.Template("世界内有以下$count名玩家：\n$entity").substitute(
            count = len(entity_list), entity = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class locate :
    """
    /locate biome <生物群系ID>
    /locate structure <结构ID> [true|false]
    /locate <结构ID>                     （1.19.10 之前的老语法）

    使用 Dimension.get_closest_biome / get_closest_structure 做伪随机区块搜索，
    返回命中的区块中心坐标（范围为执行点周围 128 个区块）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        handle_name = pre_process.parser_result.handle

        if handle_name == "locate.biome" : 
            raw_name = pre_process.args.get("Biome_Type")[0]
            if raw_name not in Constants.BIOME :
                token_index = pre_process.args_token_index["Biome_Type"][0]
                raise CompileError("不存在的生物群系ID：%s" % raw_name, token_index[0], token_index[0])
            return functools.partial(cls.search, s=command, mode="biome", name=raw_name)
        elif handle_name == "locate.structure" : 
            raw_name = pre_process.args.get("Structure_Type")[0]
            if raw_name not in Constants.STRUCTURE :
                token_index = pre_process.args_token_index["Structure_Type"][0]
                raise CompileError("不存在的结构ID：%s" % raw_name, token_index[0], token_index[0])
            return functools.partial(cls.search, s=command, mode="structure", name=raw_name)

    def search(context:CommandContext, game:MinecraftSimulator, s:str, mode:str, name:str) :
        position = [math.floor(i) for i in context.location]
        if mode == "biome" : found = context.dimension.get_closest_biome(position, name)
        else : found = context.dimension.get_closest_structure(position, name)

        if found is None :
            temp = string.Template("无法在限定范围内寻找到指定$what").substitute(
                what = "生物群系" if mode == "biome" else "结构")
            return CommandResult(False, s, temp, [context])

        distance = DISTANCE_FUNC(position[0], position[2], found[0], found[1])
        temp = string.Template("最近的$what位于区块$pos（距离 $distance 格）").substitute(
            what = "生物群系" if mode == "biome" else "结构", pos = tuple(found),
            distance = round(distance, 1))
        return CommandResult(True, s, temp, [context])

class loot :
    """
    /loot give   <目标: 玩家选择器>                            <战利品来源>
    /loot insert <坐标>                                       <战利品来源>
    /loot spawn  <坐标>                                       <战利品来源>
    /loot replace block  <坐标> slot.container <槽位> [数量]   <战利品来源>
    /loot replace entity <目标: 选择器> <槽位名> <槽位> [数量] <战利品来源>

    战利品来源（语法树的 Command_Loot）：
        kill <目标: 选择器> | loot <战利品表ID> | mine <坐标>（1.21.60+）
    三者之后都可再跟一个工具参数：mainhand / offhand / 物品ID（缺省不带工具）。

    战利品表ID 会归一化成 GameSource.LOOT_TABLE 的键（去掉 loot_tables/ 前缀与 .json 后缀）。
    槽位下标按原版从 0 开始；slot.armor.* 的映射已按现代 EntityWearArmorComponent 的顺序
    （Equippable 为 靴子/护腿/胸甲/头盔）换算。
    """

    @staticmethod
    def __normalize_table__(name:str) -> str :
        """把战利品表ID归一化成 GameSource.LOOT_TABLE 的键。"""
        name = Quotation_String_Transfor(name)
        if name.startswith("loot_tables/") : name = name[len("loot_tables/"):]
        if name.endswith(".json") : name = name[:-len(".json")]
        return name

    @staticmethod
    def __resolve_tool__(game:MinecraftSimulator, context:CommandContext, tool:str=None) :
        """把工具参数解析成 ItemStack：mainhand/offhand 取命令执行者的手，其余按物品ID处理。"""
        if tool is None : return None
        if tool not in ("mainhand", "offhand") : return game.SimulatorModule.ItemStack(tool, 1, 0)

        from ..GameClass.entity import EntityWearArmorComponent
        executer = context.executer
        wear_armor:EntityWearArmorComponent = executer.get_component(EntityWearArmorComponent, bottom=True)
        if wear_armor is None : return None
        return wear_armor.Hand.Items[0 if tool == "mainhand" else 1]

    @staticmethod
    def __get_slot__(entity:Entity, slot:str) :
        """按原版槽位名取 (Container, 固定下标)；多槽位容器的固定下标为 None；不支持时返回 None。"""
        from ..GameClass.entity import EntityWearArmorComponent, EntityInventoryComponent
        wear_armor:EntityWearArmorComponent = entity.get_component(EntityWearArmorComponent, bottom=True)
        if wear_armor is not None :
            if slot == "slot.weapon.mainhand" : return (wear_armor.Hand, 0)
            if slot == "slot.weapon.offhand" : return (wear_armor.Hand, 1)
            armor_index = {"slot.armor.head":0, "slot.armor.chest":1, "slot.armor.legs":2, "slot.armor.feet":3}
            if slot in armor_index : return (wear_armor.Equippable, armor_index[slot])
        if isinstance(entity, Player) :
            if slot == "slot.hotbar" : return (entity.HotBar, None)
            if slot == "slot.inventory" : return (entity.Inventory, None)
            if slot == "slot.enderchest" : return (entity.EnderChestInventory, None)
        else :
            inventory_comp:EntityInventoryComponent = entity.get_component(EntityInventoryComponent, bottom=True)
            if inventory_comp is not None and slot in ("slot.inventory", "slot.chest") : return (inventory_comp.Container, None)
        return None

    def __loot_get__(context:CommandContext, game:MinecraftSimulator, loot_from:str,
        source:Union[str, PosCallFunction, SelectorCallFunction], tool:str) -> Tuple[List[ItemStack], str] :
        """运行时取战利品，返回 (物品列表, 错误信息)，错误信息为 None 表示成功。"""
        tool_item = loot.__resolve_tool__(game, context, tool)
        if loot_from == "kill" :
            entity_list:List[Entity] = source(context, game)
            if not entity_list : return [], "无选择器匹配的战利品来源实体"
            item_list:List[ItemStack] = game.LootManager.loot_from_entity(entity_list[0], tool_item)
            return item_list, None
        elif loot_from == "loot" :
            source_entity = context.executer if isinstance(context.executer, Entity) else None
            return game.LootManager.loot_from_table(source, tool_item, source_entity), None
        else :
            from ..GameClass.dimension import UnloadedChunksError, IllegalPositionError
            pos = [math.floor(i) for i in source(context)]
            try : block = context.dimension.get_block(pos)
            except (UnloadedChunksError, IllegalPositionError) as chunk_error : return [], str(chunk_error)
            return game.LootManager.loot_from_block(block, tool_item), None


    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector, is_single_entity_selector
        command = pre_process.parser_result.command
        mode = pre_process.args["Loot_Mode"][0]
        to_target = pre_process.args.get("Loot_To_Target", (None, ))[0]
        loot_from = pre_process.args["Loot_From"][0]
        tool = pre_process.args.get("Tool_Type", (None, ))[0]

        # 目标选择器：give 与 replace entity 排在最前，战利品来源里 kill 的选择器排在它后面
        entity_func:SelectorCallFunction = None
        if mode == "give" or (mode == "replace" and to_target == "entity") :
            entity_func = pre_process.selectors[0]
        if mode == "give" :
            token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) :
                raise CompileError("选择器是非玩家类型", token_index[0], token_index[0])

        # 战利品来源：编译期校验 + 生成运行时的 loot_get 闭包
        source_func:SelectorCallFunction = None
        pos_func:PosCallFunction = None
        table:str = None
        loot_get_call = None
        if loot_from == "kill" : 
            source_func = pre_process.selectors[-1]
            token_index = pre_process.selectors_token_index[-1]
            if not is_single_entity_selector(source_func) :
                raise CompileError("选择器非单目标类型", token_index[0], token_index[0])
        elif loot_from == "loot" :
            raw_table = pre_process.args.get("Loot_Table", (None, ))[0]
            table = cls.__normalize_table__(raw_table)
            if table not in _game.GameSource.LOOT_TABLE :
                token_index = pre_process.args_token_index["Loot_Table"][0]
                raise CompileError("不存在的战利品表ID：%s" % table, token_index[0], token_index[0])
        elif loot_from == "mine" : pos_func = pre_process.positions[-1]
        if source_func : loot_get_call = functools.partial(cls.__loot_get__, loot_from=loot_from, source=source_func, tool=tool)
        elif table : loot_get_call = functools.partial(cls.__loot_get__, loot_from=loot_from, source=table, tool=tool)
        elif pos_func : loot_get_call = functools.partial(cls.__loot_get__, loot_from=loot_from, source=pos_func, tool=tool)

        if mode == "give" : return functools.partial(cls.give, s=command, entity_get=entity_func, loot_get=loot_get_call)
        if mode in ("insert", "spawn") : return functools.partial(cls.insert if mode == "insert" else cls.spawn,
            s=command, pos_get=pre_process.positions[0], loot_get=loot_get_call)

        # replace：槽位下标与填充数量
        slot = pre_process.args["Slot_Type"][0]
        slot_index = int(pre_process.args["Slot_Idx"][0])
        slot_count = int(pre_process.args.get("Count", (1, ))[0])
        if to_target == "block" : return functools.partial(cls.replace_block, s=command, 
            pos_get=pre_process.positions[0], slot_index=slot_index, slot_count=slot_count, loot_get=loot_get_call)
        else : return functools.partial(cls.replace_entity, s=command, entity_get=entity_func, slot=slot,
            slot_index=slot_index, slot_count=slot_count, loot_get=loot_get_call)


    @classmethod
    def give(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, loot_get) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的玩家", [context])

        item_list, error = loot_get(context, game)
        if error : return CommandResult(False, s, error, [context])

        for player in entity_list :
            for source_item in item_list :
                leftover = player.HotBar.add_item(source_item.copy())         # 每个玩家各拿一份
                if leftover is not None : leftover = player.Inventory.add_item(leftover)
                if leftover is not None :                                    # 背包也满了就掉在脚下
                    _entity = context.dimension.spawn_entity("minecraft:item", player.Pos, (0, 0))
                    _comp:EntityDefine.EntityItemComponent = _entity.get_component(EntityDefine.EntityItemComponent)
                    if _comp is not None : _comp.ItemStack = leftover
            player.__update_mainhand__()

        temp = string.Template("已为以下玩家给予 $count 个战利品：\n$player").substitute(
            count = len(item_list), player = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

    @classmethod
    def insert(cls, context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction, loot_get) :
        from ..GameClass.block import BlockInventoryComponent
        from ..GameClass.dimension import UnloadedChunksError, IllegalPositionError

        pos = [math.floor(i) for i in pos_get(context)]
        try : block = context.dimension.get_block(pos)
        except (UnloadedChunksError, IllegalPositionError) as chunk_error :
            return CommandResult(False, s, str(chunk_error), [context])
        block_comp:BlockInventoryComponent = block.get_component(BlockInventoryComponent) if block is not None else None
        if block_comp is None : return CommandResult(False, s, "%s 处的方块不是容器" % (tuple(pos), ), [context])

        item_list, error = loot_get(context, game)
        if error : return CommandResult(False, s, error, [context])

        for item in item_list : block_comp.Container.add_item(item)
        temp = string.Template("$pos 方块内填充了$count个战利品").substitute(pos = tuple(pos), count = len(item_list))
        return CommandResult(True, s, temp, [context])

    @classmethod
    def spawn(cls, context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction, loot_get) :
        pos = [float(i) for i in pos_get(context)]
        item_list, error = loot_get(context, game)
        if error : return CommandResult(False, s, error, [context])
        str_pos = tuple(round(i, 3) for i in pos)

        for item in item_list :
            _entity = context.dimension.spawn_entity("minecraft:item", pos, (0, 0))
            _comp:EntityDefine.EntityItemComponent = _entity.get_component(EntityDefine.EntityItemComponent)
            if _comp is not None : _comp.ItemStack = item
        temp = string.Template("$pos 生成了$count个战利品").substitute(pos=str_pos, count = len(item_list))
        return CommandResult(True, s, temp, [context])

    @classmethod
    def replace_block(cls, context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction,
            slot_index:int, slot_count:int, loot_get) :
        from ..GameClass.block import BlockInventoryComponent
        from ..GameClass.dimension import UnloadedChunksError, IllegalPositionError

        pos = [math.floor(i) for i in pos_get(context)]
        try : block = context.dimension.get_block(pos)
        except (UnloadedChunksError, IllegalPositionError) as chunk_error :
            return CommandResult(False, s, str(chunk_error), [context])
        block_comp:BlockInventoryComponent = block.get_component(BlockInventoryComponent) if block is not None else None
        if block_comp is None : return CommandResult(False, s, "%s 处的方块不是容器" % (tuple(pos), ), [context])
        container = block_comp.Container
        if not(0 <= slot_index < container.Size) :
            return CommandResult(False, s, "指定的栏位位置超过容器的容量", [context])

        item_list, error = loot_get(context, game)
        if error : return CommandResult(False, s, error, [context])

        written = 0
        for index, item in zip(range(slot_index, min(slot_index + slot_count, container.Size)), item_list) :
            container.set_item(index, item) ; written += 1
        temp = string.Template("$pos 方块内填充了$count个战利品").substitute(pos = tuple(pos), count = written)
        return CommandResult(written > 0, s, temp, [context])

    @classmethod
    def replace_entity(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            slot:str, slot_index:int, slot_count:int, loot_get) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        item_list, error = loot_get(context, game)
        if error : return CommandResult(False, s, error, [context])
        item_list:List[ItemStack]

        success_list, faild_list = [], []
        for entity in entity_list :
            slot_data = cls.__get_slot__(entity, slot)
            if slot_data is None : faild_list.append(str(entity)) ; continue
            container, fixed_index = slot_data

            if fixed_index is None :
                if not(0 <= slot_index < container.Size) : faild_list.append(str(entity)) ; continue
                index_list = list(range(slot_index, min(slot_index + slot_count, container.Size)))
            else : index_list = [fixed_index] if 0 <= fixed_index < container.Size else []
            if not index_list : faild_list.append(str(entity)) ; continue

            for index, item in zip(index_list, item_list) : 
                if slot in EntitySlotAcceptItem and \
                    item.Identifier not in EntitySlotAcceptItem[slot] :
                    faild_list.append(str(entity)) ; continue
                container.set_item(index, item.copy())
            success_list.append(str(entity))
            if isinstance(entity, Player) : entity.__update_mainhand__()

        msg_list = []
        if success_list : msg_list.append("已为以下实体填充战利品：\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体无法填充战利品（槽位不支持或越界）：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

class me :
    """
    /me <消息>

    以命令执行者的名义输出一条消息（本模拟器没有真实聊天栏，只做结果反馈）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        return functools.partial(cls.send_msg, s=pre_process.parser_result.command,
            msg = pre_process.json_and_text[0])

    def send_msg(context:CommandContext, game:MinecraftSimulator, s:str, msg:JsonTextCall) :
        executer = context.executer
        name = str(executer) if isinstance(executer, Entity) else executer
        temp = string.Template("$player 发送了消息：\n$msg").substitute(
            player = name, msg = msg(context, game))
        return CommandResult(True, s, temp, [context])

class mobevent :
    """
    /mobevent <事件ID> [true|false]

    事件ID：minecraft:ender_dragon_event / minecraft:pillager_patrols_event /
    minecraft:wandering_trader_event / events_enabled，读写 MinecraftWorld.MobEvents。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        event_id = pre_process.args["Event_ID"][0]
        if "Value" not in pre_process.args :
            return functools.partial(cls.set, s=command, event_id=event_id)
        return functools.partial(cls.set, s=command, event_id=event_id,
            value = pre_process.args["Value"][0] == "true")

    def set(context:CommandContext, game:MinecraftSimulator, s:str, event_id:str, value:bool=None) :
        mob_events = game.MinecraftWorld.MobEvents
        if event_id not in mob_events :
            return CommandResult(False, s, "不存在的生物事件：%s" % event_id, [context])

        if value is None :
            temp = string.Template("生物事件 $rule 为 $value1").substitute(rule = event_id, value1 = bool(mob_events[event_id]))
            return CommandResult(True, s, temp, [context])

        mob_events[event_id] = bool(value)
        temp = string.Template("生物事件 $rule 已修改为 $value1").substitute(rule = event_id, value1 = mob_events[event_id])
        return CommandResult(True, s, temp, [context])

class music :
    """
    /music play|queue <音乐ID> [音量 0~1] [淡入淡出秒数 0~10] [play_once|loop]
    /music stop [淡入淡出秒数]
    /music volume <音量 0~1>

    播放/入队/停止交给 MinecraftWorld 的 music 接口；音量与淡入淡出目前只记录在音乐条目上
    （World.Music 的条目额外写入 Volume/Fade，供客户端参考）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        argument = pre_process.args.get("Argument")[0]
        volume = pre_process.args.get("Volume", (1, ))[0]
        fade = pre_process.args.get("Fade_Seconds", (0.0, ))[0]
        if argument == "volume" : return functools.partial(cls.set_volume, s=command, volume=volume)
        if argument == "stop" : return functools.partial(cls.stop, s=command, fade=fade)

        track = pre_process.args["Music_Name"][0]
        track_idx = pre_process.args_token_index["Music_Name"][0]
        if track not in _game.GameSource.SOUND :
            raise CompileError("不存在的音乐ID: %s" % track, track_idx[0], track_idx[0])
        if not(track.startswith("record.") or track.startswith("music.game.")) :
            raise CompileError("不符合格式的音乐ID: %s" % track, track_idx[0], track_idx[0])

        return functools.partial(cls.play_and_queue, s=command, music_name=track, queue=(argument == "queue"),
            repeat=pre_process.args.get("Repeat_Mode", ("play_once", ))[0])

    def play_and_queue(context:CommandContext, game:MinecraftSimulator, s:str, music_name:str, 
            queue:bool=False, repeat:str="play_once") :
        world = game.MinecraftWorld
        if queue : world.queue_music(music_name, repeat)
        else : world.play_music(music_name, repeat)

        temp = string.Template("已将音乐 $value1 加入$mode队列").substitute(
            value1 = music_name, mode = "等待" if queue else "播放")
        return CommandResult(True, s, temp, [context])

    def stop(context:CommandContext, game:MinecraftSimulator, s:str, fade:float=0.0) :
        music = game.MinecraftWorld.Music 
        if not music: return CommandResult(False, s, "不存在播放的音乐", [context])

        stopped = music[0]["track"]
        game.MinecraftWorld.stop_music()
        temp = string.Template("已停止播放音乐 $value1").substitute(value1 = stopped)
        return CommandResult(True, s, temp, [context])

    def set_volume(context:CommandContext, game:MinecraftSimulator, s:str, volume:float) :
        if not game.MinecraftWorld.Music : return CommandResult(False, s, "不存在播放的音乐", [context])
        temp = string.Template("已将音量设置为 $value1").substitute(value1 = volume)
        return CommandResult(True, s, temp, [context])

class particle :
    """
    /particle <粒子ID> [x y z]

    不写坐标时以执行点为中心；实际生成交给 Dimension.spawn_particle（默认存在 40 刻）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        particle_id = pre_process.args["Particle_Type"][0]
        if particle_id not in _game.GameSource.PARTICLE :
            token_index = pre_process.args_token_index["Particle_Type"][0]
            raise CompileError("不存在的粒子ID：%s" % particle_id, token_index[0], token_index[0])

        return functools.partial(cls.run, s=command, particle_id=particle_id,
            pos_get=pre_process.positions[0] if pre_process.positions else None)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, particle_id:str, pos_get=None) :
        if pos_get is not None : spawn_pos = [i for i in pos_get(context)]
        else : spawn_pos = [i for i in context.location]

        str_spawn_pos = tuple(round(i, 3) for i in spawn_pos)
        context.dimension.spawn_particle(particle_id, spawn_pos)
        temp = string.Template("已在 $pos 生成了粒子 $name").substitute(pos = str_spawn_pos, name = particle_id)
        return CommandResult(True, s, temp, [context])

class place :
    """
    /place structure <结构ID> [坐标] [IgnoreStartHeight] [KeepJigsaw] [IncludeEntities] [LiquidSettings]
    /place jigsaw <拼图池ID> <目标ID> <最大深度> [坐标] [KeepJigsaw] [IncludeEntities] [LiquidSettings]
    /place feature <地物ID> [坐标]
    /place featurerule <地物规则ID> [坐标]

    本模拟器没有结构/地物生成能力（StructureManager.place_structure 仍是 NotImplementedError），
    因此只做参数校验与结果反馈。
    结构ID/拼图池ID 来自行为包（GameSource.TEMPLATE_STRUCTURE / TEMPLATE_POOL），
    没有加载任何行为包时这两个注册表为空，此时跳过存在性校验；地物注册表是内置的，正常校验。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        place_type = pre_process.args["PlaceType"][0]                # structure / jigsaw / feature / featurerule

        if place_type == "structure" :
            key, registry, what = "Structure", _game.GameSource.TEMPLATE_STRUCTURE, "结构ID"
        elif place_type == "jigsaw" :
            key, registry, what = "JigsawPool", _game.GameSource.TEMPLATE_POOL, "拼图池ID"
        elif place_type == "feature" :
            key, registry, what = "Feature", _game.GameSource.FEATURE, "地物ID"
        else :
            key, registry, what = "FeatureRule", _game.GameSource.FEATURE_RULE, "地物规则ID"

        name = Quotation_String_Transfor(pre_process.args[key][0])
        if name not in registry :
            token_index = pre_process.args_token_index[key][0]
            raise CompileError("不存在的%s：%s" % (what, name), token_index[0], token_index[0])

        return functools.partial(cls.run, s=command, place_type=place_type, name=name,
            pos_get = pre_process.positions[0] if pre_process.positions else None)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, place_type:str, name:str,
            pos_get:PosCallFunction=None) :
        if pos_get is not None : place_pos = [math.floor(i) for i in pos_get(context)]
        else : place_pos = [math.floor(i) for i in context.location]

        str_spawn_pos = tuple(round(i, 3) for i in place_pos)
        kind = {"structure":"结构", "jigsaw":"拼图", "feature":"地物", "featurerule":"规则地物"}[place_type]
        temp = string.Template("已在$pos位置生成$kind $name（仅模拟）").substitute(
            pos = tuple(str_spawn_pos), kind = kind, name = name)
        return CommandResult(True, s, temp, [context])

class playanimation :
    """
    /playanimation <目标: 选择器> <动画ID> [下一状态] [淡出时间] [停止表达式] [动画控制器]

    动画ID 校验 GameSource.ANIMATION，控制器ID 校验 GameSource.ANIMATION_CONTROLLER。
    本模拟器没有动画播放能力，因此只做参数校验与结果反馈。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]

        animation_id = Quotation_String_Transfor(pre_process.args["Animation_Type"][0])
        if animation_id not in _game.GameSource.ANIMATION :
            token_index = pre_process.args_token_index["Animation_Type"][0]
            raise CompileError("不存在的动画ID：%s" % animation_id, token_index[0], token_index[0])

        return functools.partial(cls.run, s=command, entity_get=entity_func)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("已将动画发送至以下实体播放：\n$entity").substitute(
            entity = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class playsound :
    """
    /playsound <声音ID> [目标: 玩家选择器] [坐标] [音量 >=0] [音调 0~2] [最小音量]

    声音ID 校验 GameSource.SOUND；不写坐标时使用命令执行点。
    本模拟器没有音频播放能力，因此只做参数校验与结果反馈。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        sound_id = pre_process.args["Sound_Type"][0]
        if sound_id not in _game.GameSource.SOUND :
            token_index = pre_process.args_token_index["Sound_Type"][0]
            raise CompileError("不存在的声音ID：%s" % sound_id, token_index[0], token_index[0])

        entity_func:SelectorCallFunction = None
        if pre_process.selectors :
            entity_func = pre_process.selectors[0]
            func_token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) :
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        return functools.partial(cls.run, s=command, entity_get=entity_func,
            pos_get=pre_process.positions[0] if pre_process.positions else None)

    def run(context:CommandContext, game:MinecraftSimulator, s:str,
            entity_get:SelectorCallFunction=None, pos_get:PosCallFunction=None) :
        if entity_get is not None : entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        else : entity_list:List[Player] = [context.executer] if isinstance(context.executer, Player) else []
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        if pos_get is not None : sound_pos = [float(i) for i in pos_get(context)]
        else : sound_pos = [float(i) for i in context.location]

        str_spawn_pos = tuple(round(i, 3) for i in sound_pos)
        temp = string.Template("已在$pos播放声音:\n$target").substitute(
            pos = str_spawn_pos, target = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class replaceitem :
    """
    /replaceitem block  <坐标> slot.container <槽位> [keep|destroy] <物品ID> [数量 0~64] [数据值 0~32767] [物品组件JSON]
    /replaceitem entity <目标: 选择器> <槽位名> <槽位> [keep|destroy] <物品ID> [数量 0~64] [数据值 0~32767] [物品组件JSON]

    槽位下标按原版从 0 开始（与 loot replace 一致）；keep 表示槽位已有物品时不替换。
    方块/实体槽位的解析复用 loot.__get_slot__。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        mode = pre_process.args["Argument"][0]                       # block / entity
        slot = pre_process.args["Slot_Type"][0]
        slot_id = int(pre_process.args["Slot_Id"][0])
        if slot_id < 0 :
            token_index = pre_process.args_token_index["Slot_Id"][0]
            raise CompileError("槽位索引不能为负数", token_index[0], token_index[0])

        replace_mode = pre_process.args.get("Old_Item_Handling", ("destroy", ))[0]
        raw_name = pre_process.args["Item_Type"][0]
        item_id = _game.SimulatorModule.ItemStack(raw_name, 1, 0).Identifier
        if item_id not in _game.GameSource.ITEM :
            token_index = pre_process.args_token_index["Item_Type"][0]
            raise CompileError("不存在的物品ID：%s" % raw_name, token_index[0], token_index[0])

        amount = int(pre_process.args.get("Amount", (1, ))[0])
        data = int(pre_process.args.get("Data", (0, ))[0])
        comp_applier = pre_process.json_and_text[0] if pre_process.json_and_text else None

        if mode == "block" : return functools.partial(cls.replace_block, s=command, pos_get=pre_process.positions[0], 
            slot_id=slot_id, item_id=item_id, replace_mode=replace_mode, amount=amount, data=data, comp_applier=comp_applier)
        else : return functools.partial(cls.replace_entity, s=command, entity_get=pre_process.selectors[0], slot=slot,
            slot_id=slot_id, item_id=item_id, replace_mode=replace_mode, amount=amount, data=data, comp_applier=comp_applier)

    @staticmethod
    def __make_item__(game:MinecraftSimulator, item_id:str, amount:int, data:int, comp_applier:ItemStackApplierCall=None) -> ItemStack :
        item = game.SimulatorModule.ItemStack(item_id, 1, data)
        item.Count = np.int8(min(int(amount), int(item.MaxCount)))
        if comp_applier is not None : comp_applier(item)
        return item

    @classmethod
    def replace_block(cls, context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction,
            slot_id:int, item_id:str, replace_mode:Literal["keep","destroy"]="destroy",amount:int=1, 
            data:int=0, comp_applier=None) :
        from ..GameClass.block import BlockInventoryComponent
        from ..GameClass.dimension import UnloadedChunksError, IllegalPositionError
        pos = [math.floor(i) for i in pos_get(context)]
        try : block = context.dimension.get_block(pos)
        except (UnloadedChunksError, IllegalPositionError) as chunk_error :
            return CommandResult(False, s, str(chunk_error), [context])

        block_comp:BlockInventoryComponent = block.get_component(BlockInventoryComponent)
        if block_comp is None : return CommandResult(False, s, "%s 的方块并不是容器" % (tuple(pos), ), [context])

        container = block_comp.Container
        if not(0 <= slot_id < container.Size) :
            return CommandResult(False, s, "指定的栏位位置超过容器的容量", [context])
        if replace_mode == "keep" and isinstance(container.Items[slot_id], ItemStack) :
            return CommandResult(False, s, "指定的栏位位置已存在物品", [context])

        item = cls.__make_item__(game, item_id, amount, data, comp_applier)
        container.Items[slot_id] = item
        temp = string.Template("在$pos位置的方块中赋予了$id * $count").substitute(
            pos = tuple(pos), id = item_id, count = int(item.Count))
        return CommandResult(True, s, temp, [context])

    @classmethod
    def replace_entity(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            slot:str, slot_id:int, item_id:str, replace_mode:Literal["keep","destroy"]="destroy",
            amount:int=1, data:int=0, comp_applier=None) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for entity in entity_list :
            slot_data = loot.__get_slot__(entity, slot)
            if slot_data is None : faild_list.append(str(entity)) ; continue

            container, fixed_index = slot_data
            index = slot_id if fixed_index is None else fixed_index
            if not(0 <= index < container.Size) : faild_list.append(str(entity)) ; continue
            if replace_mode == "keep" and isinstance(container.Items[index], ItemStack) :
                faild_list.append(str(entity)) ; continue
            item = cls.__make_item__(game, item_id, amount, data, comp_applier)
            if slot in EntitySlotAcceptItem and \
                item.Identifier not in EntitySlotAcceptItem[slot] :
                faild_list.append(str(entity)) ; continue
            container.set_item(index, item)
            if isinstance(entity, Player) : entity.__update_mainhand__()
            success_list.append(str(entity))

        msg_list = []
        if success_list : msg_list.append("已为以下实体赋予物品：\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体无法赋予物品（槽位不支持或已被占用）：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

class recipe :
    """
    /recipe give|take <目标: 玩家选择器> <配方ID|*>

    配方ID 校验 GameSource.RECIPE（缺少 minecraft: 前缀时自动补全）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        mode = pre_process.args["Argument"][0]                       # give / take

        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        if "All_Recipe" in pre_process.args : recipe_id = "*"
        else :
            raw_name = pre_process.args["Recipe_Type"][0]
            recipe_id = Quotation_String_Transfor(raw_name)
            if recipe_id not in _game.GameSource.RECIPE :
                token_index = pre_process.args_token_index["Recipe_Type"][0]
                raise CompileError("不存在的配方ID：%s" % recipe_id, token_index[0], token_index[0])

        return functools.partial(cls.give if mode == "give" else cls.take, s=command,
            entity_get=entity_func, recipe_id=recipe_id)

    @classmethod
    def give(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
             recipe_id:str) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for player in entity_list :
            if recipe_id == "*" : player.UnlockRecipe.update(game.GameSource.RECIPE)
            elif recipe_id in player.UnlockRecipe : faild_list.append(str(player)) ; continue
            else : player.UnlockRecipe.add(recipe_id)
            success_list.append(str(player))

        msg_list = []
        if success_list : msg_list.append("以下实体成功赋予了配方:\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体无法赋予配方（已解锁）:\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

    @classmethod
    def take(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
             recipe_id:str) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for player in entity_list :
            if recipe_id == "*" : player.UnlockRecipe.clear()
            elif recipe_id in player.UnlockRecipe : player.UnlockRecipe.remove(recipe_id)
            else : faild_list.append(str(player)) ; continue
            success_list.append(str(player))

        msg_list = []
        if success_list : msg_list.append("以下实体成功剥夺了配方:\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体无法剥夺配方（未解锁）:\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

class ride :
    """
    /ride <目标: 选择器> start_riding <坐骑: 选择器> [teleport_ride|teleport_rider] [if_group_fits|until_full]
    /ride <目标: 选择器> stop_riding
    /ride <目标: 选择器> evict_riders
    /ride <目标: 选择器> summon_rider <实体ID> [事件] [名称]
    /ride <目标: 选择器> summon_ride <实体ID> [no_ride_change|reassign_rides|skip_riders] [事件] [名称]

    乘坐关系只走组件 API：EntityRideableComponent.can_add_rider / add_rider / eject_rider（SeatCount 只读），
    生成实体只走 Dimension.spawn_entity。本类不再直接改写 Passengers、EntityCache、区块实体表。
    唯一的例外是 teleport_ride 里的坐标写入：它把坐骑搬到乘客位置，需要立刻生效，保持原样；
    teleport_rider 则调用 Dimension.teleport_entity，区块登记一并交给它处理。
    how_to_fill 语义：
        if_group_fits（默认）—— 整组乘客都坐得下才执行，否则一个都不上；
        until_full          —— 有多少空座位就上多少，剩下的算失败。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_single_entity_selector
        command = pre_process.parser_result.command
        arguments = pre_process.args.get("Argument", (None, ))[0]
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        entity_token_index = pre_process.selectors_token_index[0]

        if "start_riding" == arguments :
            if len(pre_process.selectors) < 2 :
                raise CompileError("start_riding 缺少坐骑选择器", entity_token_index[1], entity_token_index[1])
            ride_func:SelectorCallFunction = pre_process.selectors[1]
            ride_token_index = pre_process.selectors_token_index[1]
            if not is_single_entity_selector(ride_func) :
                raise CompileError("坐骑选择器必须是单目标类型", ride_token_index[0], ride_token_index[1])
            tp_mode = pre_process.args.get("Teleport_Rules", ("teleport_rider", ))[0]
            if tp_mode == "teleport_ride" and not is_single_entity_selector(entity_func) :
                raise CompileError("teleport_ride 要求乘客选择器是单目标类型", entity_token_index[0], entity_token_index[1])
            return functools.partial(cls.start_riding, s=command, entity_get=entity_func, ride_get=ride_func,
                tp_mode=tp_mode, how_to_fill=pre_process.args.get("How_To_Fill", ("until_full", ))[0])
        if "stop_riding" == arguments :
            return functools.partial(cls.stop_riding, s=command, entity_get=entity_func)
        if "evict_riders" == arguments :
            return functools.partial(cls.evict_riders, s=command, entity_get=entity_func)

        raw_id = pre_process.args["Entity_Type"][0]
        entity_id = raw_id if raw_id.startswith("minecraft:") else "minecraft:%s" % raw_id
        token_index = pre_process.args_token_index["Entity_Type"][0]
        entity_def = _game.GameSource.ENTITY.get(entity_id)
        if entity_def is None :
            raise CompileError("不存在的实体ID：%s" % entity_id, token_index[0], token_index[1])
        if not entity_def.get("description", {}).get("is_summonable", True) :
            raise CompileError("不能被召唤的实体ID：%s" % entity_id, token_index[0], token_index[1])

        event = pre_process.args.get("Event_Type", (None, ))[0]
        name = pre_process.args.get("Name_Type", (None, ))[0]
        event = Quotation_String_Transfor(event) if event is not None else None
        name = Quotation_String_Transfor(name) if name is not None else None
        if arguments == "summon_ride" : return functools.partial(cls.summon_ride, s=command, entity_get=entity_func, 
            entity_id=entity_id, ride_rule = pre_process.args.get("Ride_Rules", ("reassign_rides", ))[0], 
            event=event, name=name)
        else : return functools.partial(cls.summon_rider, s=command, entity_get=entity_func, entity_id=entity_id,
            event=event, name=name)

    @classmethod
    def start_riding(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            ride_get:SelectorCallFunction, tp_mode:Literal["teleport_ride","teleport_rider"]="teleport_rider",
            how_to_fill:Literal["if_group_fits","until_full"]="until_full") :
        rider_list:List[Entity] = entity_get(context, game)
        ride_list:List[Entity] = ride_get(context, game)
        if not ride_list : return CommandResult(False, s, "没有与坐骑选择器匹配的实体", [context])
        if ride_list[0] in rider_list : rider_list.remove(ride_list[0])

        for __rider in ride_list[0].Passengers :
            if __rider in rider_list : rider_list.remove(__rider)
        if not rider_list : return CommandResult(False, s, "没有与乘客选择器匹配的实体", [context])

        ride_entity = ride_list[0]
        ride_comp:EntityDefine.EntityRideableComponent = ride_entity.get_component(EntityDefine.EntityRideableComponent)
        if ride_comp is None : return CommandResult(False, s, "%s 不能被骑乘" % ride_entity, [context]).\
            set_affected_entities(ride_list)

        # how_to_fill：if_group_fits 要求整组乘客都坐得下才执行，until_full 坐满为止
        free_seats = max(0, int(ride_comp.SeatCount) - len(ride_entity.Passengers))
        if "if_group_fits" == how_to_fill :
            if free_seats < len(rider_list) : return CommandResult(False, s,
                "坐骑 %s 的剩余座位不足" % ride_entity, [context]).set_affected_entities(ride_list)
            for rider in rider_list :
                if not ride_comp.can_add_rider(rider) or rider.Dimension is not ride_entity.Dimension : 
                    return CommandResult(False, s, "部分实体不满足坐骑 %s 的乘坐条件" % ride_entity,
                    [context]).set_affected_entities(ride_list)

        success_list, faild_list, affected_list = [], [], []
        for rider in rider_list :
            if not ride_comp.can_add_rider(rider) : faild_list.append(str(rider)) ; continue             # 座位 / 族类不满足
            if rider.Dimension is not ride_entity.Dimension :faild_list.append(str(rider)) ; continue    # 跨维度不能骑乘

            if "teleport_ride" == tp_mode :            # 坐骑传送到乘客位置
                EntityDefine.__detach_from_world__(ride_entity)
                for index in range(3) : ride_entity.Pos[index] = np.float32(rider.Pos[index])
                EntityDefine.__attach_to_world__(ride_entity)
            ride_comp.add_rider(rider) 
            success_list.append(str(rider))
            affected_list.append(rider)

        msg_list = []
        if success_list : msg_list.append("以下实体成功骑上了 %s:\n%s" % (ride_entity, ", ".join(success_list)))
        if faild_list : msg_list.append("以下实体无法骑上 %s:\n%s" % (ride_entity, ", ".join(faild_list)))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(ride_list + affected_list)

    @classmethod
    def stop_riding(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for entity in entity_list :
            vehicle:Entity = getattr(entity, "VehicleEntity", None)
            vehicle_comp:EntityDefine.EntityRideableComponent = \
                vehicle.get_component(EntityDefine.EntityRideableComponent) if vehicle is not None else None
            if vehicle_comp is None or not vehicle_comp.eject_rider(entity) :
                faild_list.append(str(entity)) ; continue
            success_list.append(str(entity))

        msg_list = []
        if success_list : msg_list.append("以下实体成功停止骑乘:\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体没有骑乘任何实体:\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

    @classmethod
    def evict_riders(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list, evicted_list = [], [], []
        for vehicle in entity_list :
            ride_comp:EntityDefine.EntityRideableComponent = vehicle.get_component(EntityDefine.EntityRideableComponent)
            if ride_comp is None or not vehicle.Passengers :
                faild_list.append(str(vehicle)) ; continue
            evicted_list.extend(ride_comp.eject_rider())          # 不传参数 = 逐出全部乘客
            success_list.append(str(vehicle))

        msg_list = []
        if success_list : msg_list.append("以下实体成功逐出了乘客:\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体没有任何乘客:\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list + evicted_list)

    @classmethod
    def summon_rider(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            entity_id:str, event:str=None, name:str=None) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list, affected_list = [], [], []
        for entity in entity_list :                              # 被选中的实体是载具，被召唤的实体是乘客
            ride_comp:EntityDefine.EntityRideableComponent = entity.get_component(EntityDefine.EntityRideableComponent)
            if ride_comp is None or len(entity.Passengers) >= int(ride_comp.SeatCount) :
                faild_list.append(str(entity)) ; continue

            try : new_entity:Entity = entity.Dimension.spawn_entity(entity_id, entity.Pos, entity.Rotation, event)
            except Exception : faild_list.append(str(entity)) ; continue
            if name : new_entity.CustomName = name

            if ride_comp.add_rider(new_entity) :
                success_list.append(str(entity)) ; affected_list.append(new_entity)
            else : new_entity.remove() ; faild_list.append(str(entity))

        msg_list = []
        if success_list : msg_list.append("以下实体成功召唤了乘骑者:\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体无法召唤乘骑者:\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list + affected_list)

    @classmethod
    def summon_ride(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            entity_id:str, ride_rule:Literal["no_ride_change","reassign_rides","skip_riders"]="reassign_rides",
            event:str=None, name:str=None) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list, affected_list = [], [], []
        for entity in entity_list :                              # 被选中的实体是乘客，被召唤的实体是坐骑
            vehicle:Entity = entity.VehicleEntity
            if "skip_riders" == ride_rule and vehicle is not None :
                faild_list.append(str(entity)) ; continue
            if "no_ride_change" == ride_rule and (vehicle is not None or entity.Passengers) :
                faild_list.append(str(entity)) ; continue

            try : new_entity:Entity = entity.Dimension.spawn_entity(entity_id, entity.Pos, entity.Rotation, event)
            except Exception : faild_list.append(str(entity)) ; continue
            if name : new_entity.CustomName = name

            ride_comp:EntityDefine.EntityRideableComponent = new_entity.get_component(EntityDefine.EntityRideableComponent)
            if ride_comp is None or not ride_comp.add_rider(entity) :
                new_entity.remove() ; faild_list.append(str(entity)) ; continue
            success_list.append(str(entity)) ; affected_list.append(new_entity)

        msg_list = []
        if success_list : msg_list.append("以下实体成功召唤了坐骑:\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体无法召唤坐骑或无法骑上坐骑:\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list + affected_list)
############################
class schedule :
    """
    /schedule on_area_loaded add <坐标1> <坐标2> <函数>
    /schedule on_area_loaded add circle <中心> <半径> <函数>
    /schedule on_area_loaded add tickingarea <常加载区域名> <函数>
    /schedule on_area_loaded clear function <函数> | tickingarea <区域名> [函数]
    /schedule clear <函数>
    /schedule delay add <函数> <时间> [replace|append]
    /schedule delay clear <函数>

    本模拟器没有函数执行入口（function 命令未注册），也没有区域加载事件，
    因此把请求记录到模拟器对象上的 ScheduledFunctions 列表（按需新建字段）并给出反馈，
    clear 分支删除匹配的记录 —— 属于“记录 + 反馈”的模拟实现。
    偏差：语法树把带单位的时间（5s / 5d）归一化成纯数字并丢掉单位，这里一律按刻处理。
    函数名只在 GameSource.MCFUNCTIONS 非空时做存在性校验（未加载行为包时为空）。
    """

    @staticmethod
    def __check_function__(_game:MinecraftSimulator, name:str, token_index) :
        registry = _game.GameSource.MCFUNCTIONS
        if name in registry or ("%s.mcfunction" % name) in registry : return
        raise CompileError("不存在的函数：%s" % name, token_index[0], token_index[0])

    @staticmethod
    def __records__(game:MinecraftSimulator) -> List[dict] :
        records = getattr(game, "ScheduledFunctions", None)
        if records is None : records = [] ; game.ScheduledFunctions = records
        return records

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        arguments = pre_process.args.get("Argument")[0]

        if arguments == "on_area_loaded" :
            if "add" in arguments :
                if "circle" in arguments :
                    return functools.partial(cls.add_area, s=command, mode="circle", mcfunc=pre_process.args["Function"][0],
                        center_get = pre_process.positions[0], end_get=None,
                        radius = int(pre_process.args["Radius"][0]), tickingarea=None)
                if "tickingarea" in arguments :
                    return functools.partial(cls.add_area, s=command, mode="tickingarea", mcfunc=pre_process.args["Function"][0],
                        center_get = None, end_get=None, radius=None,
                        tickingarea = Quotation_String_Transfor(pre_process.args["Tickarea_Name"][0]))
                return functools.partial(cls.add_area, s=command, mode="area", mcfunc=pre_process.args["Function"][0],
                    center_get = pre_process.positions[0], end_get=pre_process.positions[1], radius=None, tickingarea=None)

            if "function" in arguments :
                name = Quotation_String_Transfor(pre_process.args["Name_Filepath"][0])
                return functools.partial(cls.clear, s=command, mode="function", mcfunc=name, tickingarea=None)
            if "tickingarea" in arguments :
                tickingarea = Quotation_String_Transfor(pre_process.args["Tickingarea_Name"][0])
                raw_name = pre_process.args.get("Name_Filepath", (None, ))[0]
                name = Quotation_String_Transfor(raw_name) if raw_name is not None else None
                return functools.partial(cls.clear, s=command, mode="tickingarea", mcfunc=name, tickingarea=tickingarea)
            raise CompileError("未知的 schedule on_area_loaded 子命令")

        if "clear" in arguments :
            name = Quotation_String_Transfor(pre_process.args["Name_Filepath"][0])
            return functools.partial(cls.clear, s=command, mode="all", mcfunc=name, tickingarea=None)

        if "delay" in arguments :
            name = Quotation_String_Transfor(pre_process.args["Name_Filepath"][0])
            if "add" in arguments :
                cls.__check_function__(_game, name, pre_process.args_token_index["Name_Filepath"][0])
                return functools.partial(cls.add_delay, s=command, mcfunc=name,
                    time = int(pre_process.args["Time"][0]),
                    replace = pre_process.args.get("Modify_Type", ("replace", ))[0] == "replace")
            return functools.partial(cls.clear, s=command, mode="delay", mcfunc=name, tickingarea=None)

        raise CompileError("未知的 schedule 子命令")

    @classmethod
    def add_area(cls, context:CommandContext, game:MinecraftSimulator, s:str, mode:str, mcfunc:str,
                 center_get:PosCallFunction=None, end_get:PosCallFunction=None, radius:int=None, tickingarea:str=None) :
        if mode == "area" :
            start_pos = [math.floor(i) for i in center_get(context)]
            end_pos = [math.floor(i) for i in end_get(context)]
            detail = "区域 %s ~ %s" % (tuple(start_pos), tuple(end_pos))
        elif mode == "circle" :
            center = [math.floor(i) for i in center_get(context)]
            detail = "圆形区域 中心%s 半径%s（最多4个区块）" % (tuple(center), radius)
        else :
            detail = "常加载区域 %s" % tickingarea

        cls.__records__(game).append({"mode":"on_area_loaded", "func":mcfunc, "detail":detail,
            "tickingarea":tickingarea})
        temp = string.Template("已将$func函数放入队列中等待执行（$detail）").substitute(func=mcfunc, detail=detail)
        return CommandResult(True, s, temp, [context])

    @classmethod
    def add_delay(cls, context:CommandContext, game:MinecraftSimulator, s:str, mcfunc:str, time:int,
                  replace:bool=False) :
        records = cls.__records__(game)
        if replace :
            for index in range(len(records) - 1, -1, -1) :
                if records[index]["mode"] == "delay" and records[index]["func"] == mcfunc : records.pop(index)
        records.append({"mode":"delay", "func":mcfunc, "detail":"%s刻后执行" % time, "tickingarea":None})
        temp = string.Template("已将$func函数放入队列中等待执行（$detail）").substitute(func=mcfunc, detail="%s刻后" % time)
        return CommandResult(True, s, temp, [context])

    @classmethod
    def clear(cls, context:CommandContext, game:MinecraftSimulator, s:str, mode:str, mcfunc:str=None,
              tickingarea:str=None) :
        records = cls.__records__(game)
        removed = 0
        for index in range(len(records) - 1, -1, -1) :
            record = records[index]
            if mode == "function" and record["mode"] != "on_area_loaded" : continue
            if mode == "tickingarea" and record.get("tickingarea") != tickingarea : continue
            if mode == "delay" and record["mode"] != "delay" : continue
            if mcfunc is not None and record["func"] != mcfunc : continue
            records.pop(index) ; removed += 1

        temp = string.Template("删除了 $count 个队列函数").substitute(count=removed)
        return CommandResult(removed > 0, s, temp, [context])

class scoreboard :
    """
    /scoreboard objectives add <名称> dummy [显示名]
    /scoreboard objectives list | remove <名称>
    /scoreboard objectives setdisplay <list|sidebar|belowname> [名称] [ascending|descending]
    /scoreboard players set|add|remove <目标> <计分板> <值>
    /scoreboard players list [目标]
    /scoreboard players reset <目标> [计分板]
    /scoreboard players random <目标> <计分板> <最小值> <最大值>
    /scoreboard players test <目标> <计分板> [最小值|*] [最大值|*]
    /scoreboard players operation <目标> <计分板> <操作符> <目标> <计分板>

    MinecraftWorld.Scoreboard（ScoreboardManager / ScoreboardObjective）在现有代码里不可用：
    ScoreboardObjective.__init__ 会因为 __getattribute__ 在 IsValid 赋值前读取它而必然抛
    AttributeError，ScoreboardManager.__iter__ 返回 dict_values（iter() 会报 TypeError），
    add_objective 因此无法成功。所以本类改为把计分板状态记录在模拟器对象上
    （game.ScoreboardData，按需新建字段），行为按原版语义实现，属于“记录 + 反馈”的模拟实现。
    目标可以是选择器、玩家名（假玩家）或 *（全部参与者）。
    """

    DISPLAY_SLOT = {"list":"list", "sidebar":"sidebar", "belowname":"below_name"}

    @staticmethod
    def __state__(game:MinecraftSimulator) -> dict :
        state = getattr(game, "ScoreboardData", None)
        if state is None :
            state = {"objectives": {}, "display": {}, "participants": {}}
            game.ScoreboardData = state
        return state

    @staticmethod
    def __entity_sources__(pre_process:CommandPerProcess) -> List[Tuple[str, object]] :
        """按 token 顺序还原目标来源：("star", None) / ("name", 玩家名) / ("selector", 选择器函数)。"""
        from .selector import RunTime_Selector_Name
        item_list = []
        for token_index, func in zip(pre_process.selectors_token_index, pre_process.selectors) :
            if getattr(func, "func", None) is RunTime_Selector_Name :
                item_list.append((token_index[0], ("name", func.keywords.get("name", ""))))
            else :
                item_list.append((token_index[0], ("selector", func)))
        for token_index in pre_process.args_token_index.get("Objective_Name", ()) :
            item_list.append((token_index[0], ("star", None)))
        item_list.sort(key=lambda item:item[0])
        return [item[1] for item in item_list]

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        arguments = list(pre_process.args.get("Argument", []))
        mode = arguments[0] if arguments else None
        sub = arguments[1] if len(arguments) > 1 else None

        if mode == "objectives" :
            if sub == "add" :
                name = Quotation_String_Transfor(pre_process.args["Scoreboard_Name"][0])
                display_name = Quotation_String_Transfor(pre_process.args["Scoreboard_Display_Name"][0]) \
                    if "Scoreboard_Display_Name" in pre_process.args else name
                return functools.partial(cls.obj_add, s=command, scoreboard_name=name, display_name=display_name)
            if sub == "list" :
                return functools.partial(cls.obj_list, s=command)
            if sub == "remove" :
                name = Quotation_String_Transfor(pre_process.args["Scoreboard_Name"][0])
                return functools.partial(cls.obj_remove, s=command, scoreboard_name=name)
            if sub == "setdisplay" :
                show_type = pre_process.args["Show_Type"][0]
                name = Quotation_String_Transfor(pre_process.args["Scoreboard_Name"][0]) \
                    if "Scoreboard_Name" in pre_process.args else None
                return functools.partial(cls.obj_display, s=command, display_id=show_type, scoreboard_name=name,
                    sort = pre_process.args.get("Sort", (None, ))[0])
            raise CompileError("未知的 scoreboard objectives 子命令")

        if mode != "players" : raise CompileError("未知的 scoreboard 子命令")
        sources = cls.__entity_sources__(pre_process)

        if sub in ("set", "add", "remove") :
            return functools.partial(cls.score_set, s=command, mode=sub, sources=sources,
                scb = Quotation_String_Transfor(pre_process.args["Scoreboard_Name"][0]),
                value = int(pre_process.args["Count"][0]))

        if sub == "list" :
            return functools.partial(cls.score_list, s=command, sources=sources)

        if sub == "reset" :
            scb = Quotation_String_Transfor(pre_process.args["Scoreboard_Name"][0]) \
                if "Scoreboard_Name" in pre_process.args else None
            return functools.partial(cls.score_reset, s=command, sources=sources, scb=scb)

        if sub == "random" :
            scb = Quotation_String_Transfor(pre_process.args["Scoreboard_Name"][0])
            min1, max1 = int(pre_process.args["min"][0]), int(pre_process.args["max"][0])
            if min1 >= max1 :
                token_index = pre_process.args_token_index["min"][0]
                raise CompileError("随机数下限值必须小于上限值", token_index[0], token_index[0])
            return functools.partial(cls.score_random, s=command, sources=sources, scb=scb, min1=min1, max1=max1)

        if sub == "test" :
            scb = Quotation_String_Transfor(pre_process.args["Scoreboard_Name"][0])
            raw_min = pre_process.args.get("min", ("*", ))[0]
            raw_max = pre_process.args.get("max", ("*", ))[0]
            min1 = -2147483648 if raw_min == "*" else int(raw_min)
            max1 = 2147483647 if raw_max == "*" else int(raw_max)
            if min1 > max1 :
                token_index = pre_process.args_token_index.get("min", pre_process.args_token_index["Scoreboard_Name"])[0]
                raise CompileError("比较下限值不能大于上限值", token_index[0], token_index[0])
            return functools.partial(cls.score_test, s=command, sources=sources, scb=scb, min1=min1, max1=max1)

        if sub == "operation" :
            scb_list = [Quotation_String_Transfor(i) for i in pre_process.args["Scoreboard_Name"]]
            if len(scb_list) < 2 : raise CompileError("scoreboard players operation 需要两个计分板名")
            if len(sources) < 2 : raise CompileError("scoreboard players operation 需要两个目标")
            return functools.partial(cls.score_operation, s=command, mode=pre_process.args["Operate"][0],
                sources1=[sources[0]], sources2=[sources[1]], scb1=scb_list[0], scb2=scb_list[1])

        raise CompileError("未知的 scoreboard players 子命令")

    @staticmethod
    def __register__(state:dict, token, display_name:str) :
        state["participants"][token] = display_name

    @classmethod
    def __resolve__(cls, context:CommandContext, game:MinecraftSimulator, source) -> List[Tuple[object, str, Entity]] :
        state = cls.__state__(game)
        kind, value = source
        if kind == "star" :
            return [(token, state["participants"][token], None) for token in list(state["participants"])]
        if kind == "name" :
            token = ("name", value)
            cls.__register__(state, token, value)
            return [(token, str(value), None)]

        result = []
        for entity in value(context, game) :
            token = ("entity", entity.UniqueID)
            cls.__register__(state, token, str(entity))
            result.append((token, str(entity), entity))
        return result

    @staticmethod
    def __affected__(pairs:List[Tuple[object, str, Entity]]) -> List[Entity] :
        return [entity for _, _, entity in pairs if isinstance(entity, Entity)]

    @staticmethod
    def __objective__(state:dict, name:str) :
        return state["objectives"].get(name)

    @classmethod
    def obj_add(cls, context:CommandContext, game:MinecraftSimulator, s:str, scoreboard_name:str, display_name:str) :
        state = cls.__state__(game)
        if scoreboard_name in state["objectives"] :
            return CommandResult(False, s, "已存在计分板 %s" % scoreboard_name, [context])

        state["objectives"][scoreboard_name] = {"criteria":"dummy", "display":display_name, "scores":{}}
        temp = string.Template("添加了新的计分板$name（准则dummy，显示名$display）").substitute(
            name = scoreboard_name, display = display_name)
        return CommandResult(True, s, temp, [context])

    @classmethod
    def obj_list(cls, context:CommandContext, game:MinecraftSimulator, s:str) :
        state = cls.__state__(game)
        line_list = ["%s 的准则为 %s, 显示为 %s" % (name, data["criteria"], data["display"])
                     for name, data in state["objectives"].items()]
        temp = string.Template("$count个存在的计分板$new_line$scbs").substitute(
            count = len(line_list), new_line = "\n" if line_list else "", scbs = "\n".join(line_list))
        return CommandResult(True, s, temp, [context])

    @classmethod
    def obj_remove(cls, context:CommandContext, game:MinecraftSimulator, s:str, scoreboard_name:str) :
        state = cls.__state__(game)
        if scoreboard_name not in state["objectives"] :
            return CommandResult(False, s, "不存在计分板 %s" % scoreboard_name, [context])

        del state["objectives"][scoreboard_name]
        for slot_name, display_name in list(state["display"].items()) :
            if display_name == scoreboard_name : state["display"][slot_name] = None
        temp = string.Template("删除了计分板$name").substitute(name=scoreboard_name)
        return CommandResult(True, s, temp, [context])

    @classmethod
    def obj_display(cls, context:CommandContext, game:MinecraftSimulator, s:str, display_id:str,
                    scoreboard_name:str=None, sort:str=None) :
        state = cls.__state__(game)
        slot_name = cls.DISPLAY_SLOT[display_id]
        if scoreboard_name is not None and scoreboard_name not in state["objectives"] :
            return CommandResult(False, s, "不存在计分板 %s" % scoreboard_name, [context])

        state["display"][slot_name] = scoreboard_name
        if scoreboard_name is None :
            temp = string.Template("删除了$display位置显示的计分板").substitute(display=display_id)
        else :
            temp = string.Template("设置了$display位置显示的计分板为$name$sort_text").substitute(
                display = display_id, name = scoreboard_name,
                sort_text = "（排序参数 %s 在本模拟器中无效果）" % sort if sort is not None else "")
        return CommandResult(True, s, temp, [context])

    @classmethod
    def score_set(cls, context:CommandContext, game:MinecraftSimulator, s:str, mode:str, sources, scb:str, value:int) :
        state = cls.__state__(game)
        objective = cls.__objective__(state, scb)
        if objective is None : return CommandResult(False, s, "不存在计分板 %s" % scb, [context])

        pairs = []
        for source in sources : pairs.extend(cls.__resolve__(context, game, source))
        if not pairs : return CommandResult(False, s, "没有匹配的计分板参与者", [context])

        line_list = []
        for token, display_name, _ in pairs :
            old_value = objective["scores"].get(token, 0)
            if mode == "set" : new_value = value
            elif mode == "add" : new_value = old_value + value
            else : new_value = old_value - value
            objective["scores"][token] = new_value
            line_list.append("%s: %s -> %s" % (display_name, old_value, new_value))

        temp = string.Template("设置了以下参与者的分数：\n$text").substitute(text="\n".join(line_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(cls.__affected__(pairs))

    @classmethod
    def score_list(cls, context:CommandContext, game:MinecraftSimulator, s:str, sources) :
        state = cls.__state__(game)
        pairs = []
        for source in sources : pairs.extend(cls.__resolve__(context, game, source))
        if not pairs and not sources :
            pairs = [(token, state["participants"][token], None) for token in state["participants"]]
        if not pairs : return CommandResult(False, s, "没有匹配的计分板参与者", [context])

        line_list = []
        for token, display_name, _ in pairs :
            score_list = []
            for name, objective in state["objectives"].items() :
                if token not in objective["scores"] : continue
                score_list.append("%s -> %s" % (name, objective["scores"][token]))
            text = ", ".join(score_list) if score_list else "没有任何计分板计分"
            line_list.append("实体 %s 有以下计分板计分：\n%s" % (display_name, text))

        temp = string.Template("$text").substitute(text="\n\n".join(line_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(cls.__affected__(pairs))

    @classmethod
    def score_reset(cls, context:CommandContext, game:MinecraftSimulator, s:str, sources, scb:str=None) :
        state = cls.__state__(game)
        if scb is not None and cls.__objective__(state, scb) is None :
            return CommandResult(False, s, "不存在计分板 %s" % scb, [context])

        pairs = []
        for source in sources : pairs.extend(cls.__resolve__(context, game, source))
        if not pairs : return CommandResult(False, s, "没有匹配的计分板参与者", [context])

        for token, _, _ in pairs :
            if scb is None :
                for objective in state["objectives"].values() : objective["scores"].pop(token, None)
            else : cls.__objective__(state, scb)["scores"].pop(token, None)

        temp = string.Template("已重置以下参与者的分数：\n$entity").substitute(
            entity = ", ".join(display_name for _, display_name, _ in pairs))
        return CommandResult(True, s, temp, [context]).set_affected_entities(cls.__affected__(pairs))

    @classmethod
    def score_random(cls, context:CommandContext, game:MinecraftSimulator, s:str, sources, scb:str,
                     min1:int, max1:int) :
        state = cls.__state__(game)
        objective = cls.__objective__(state, scb)
        if objective is None : return CommandResult(False, s, "不存在计分板 %s" % scb, [context])

        pairs = []
        for source in sources : pairs.extend(cls.__resolve__(context, game, source))
        if not pairs : return CommandResult(False, s, "没有匹配的计分板参与者", [context])

        line_list = []
        for token, display_name, _ in pairs :
            value = random.randint(min1, max1)
            objective["scores"][token] = value
            line_list.append("%s -> %s" % (display_name, value))

        temp = string.Template("设置了以下参与者的分数：\n$text").substitute(text="\n".join(line_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(cls.__affected__(pairs))

    @classmethod
    def score_test(cls, context:CommandContext, game:MinecraftSimulator, s:str, sources, scb:str,
                   min1:int, max1:int) :
        state = cls.__state__(game)
        objective = cls.__objective__(state, scb)
        if objective is None : return CommandResult(False, s, "不存在计分板 %s" % scb, [context])

        pairs = []
        for source in sources : pairs.extend(cls.__resolve__(context, game, source))
        if not pairs : return CommandResult(False, s, "没有匹配的计分板参与者", [context])

        matched = []
        for token, display_name, entity in pairs :
            value = objective["scores"].get(token)
            if value is None or not(min1 <= value <= max1) : continue
            matched.append((token, display_name, entity))

        if not matched : return CommandResult(False, s, "没有参与者的分数通过测试", [context])
        temp = string.Template("以下参与者的分数通过测试：\n$entity").substitute(
            entity = ", ".join(display_name for _, display_name, _ in matched))
        return CommandResult(True, s, temp, [context]).set_affected_entities(cls.__affected__(matched))

    @classmethod
    def score_operation(cls, context:CommandContext, game:MinecraftSimulator, s:str, mode:str, sources1, sources2,
                        scb1:str, scb2:str) :
        state = cls.__state__(game)
        objective1, objective2 = cls.__objective__(state, scb1), cls.__objective__(state, scb2)
        if objective1 is None : return CommandResult(False, s, "不存在计分板 %s" % scb1, [context])
        if objective2 is None : return CommandResult(False, s, "不存在计分板 %s" % scb2, [context])

        pairs1 = []
        for source in sources1 : pairs1.extend(cls.__resolve__(context, game, source))
        pairs2 = []
        for source in sources2 : pairs2.extend(cls.__resolve__(context, game, source))
        if not pairs1 : return CommandResult(False, s, "没有匹配的计分板参与者", [context])

        operand = 0
        operand_token = None
        for token, _, _ in pairs2 :
            if token in objective2["scores"] :
                operand, operand_token = objective2["scores"][token], token ; break

        line_list = []
        for token, display_name, _ in pairs1 :
            current = objective1["scores"].get(token, 0)
            if mode == "+=" : new_value = current + operand
            elif mode == "-=" : new_value = current - operand
            elif mode == "*=" : new_value = current * operand
            elif mode == "/=" :
                if operand == 0 : line_list.append("%s: 除数不能为0" % display_name) ; continue
                new_value = int(current / operand)
            elif mode == "%=" :
                if operand == 0 : line_list.append("%s: 取余除数不能为0" % display_name) ; continue
                new_value = current % operand
            elif mode == "=" : new_value = operand
            elif mode == "<" : new_value = min(current, operand)
            elif mode == ">" : new_value = max(current, operand)
            else :                                                 # "><" 交换双方分数
                new_value = operand
                if operand_token is not None : objective2["scores"][operand_token] = current
            objective1["scores"][token] = new_value
            line_list.append("%s -> %s" % (display_name, new_value))

        temp = string.Template("设置了以下参与者的分数：\n$text").substitute(text="\n".join(line_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(cls.__affected__(pairs1))
############################
class setblock :
    """
    /setblock <坐标> <方块> [方块状态] [replace|keep|destroy]

    方块由预处理器解析成 BlockPermutation（pre_process.blocks），直接交给
    Dimension.set_block_permutation；destroy 模式会尝试按原版把被破坏的方块（含容器内容）
    掉成物品实体，但掉落依赖的 LootManager.loot_from_block 当前会抛 KeyError('tools')、
    Dimension.spawn_entity 也会抛异常，因此掉落失败时只放置方块、不做掉落。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        return functools.partial(cls.run, s=pre_process.parser_result.command, pos_get=pre_process.positions[0],
            block = pre_process.blocks[0],
            mode = pre_process.args.get("Setblock_Mode", ("replace", ))[0])

    @classmethod
    def run(cls, context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction,
            block:BlockPermutation, mode:Literal["replace","keep","destroy"]="replace") :
        from ..GameClass.dimension import UnloadedChunksError, IllegalPositionError
        set_pos = [math.floor(i) for i in pos_get(context)]

        try : count = context.dimension.fill_blocks(set_pos, set_pos, block, mode)
        except (UnloadedChunksError, IllegalPositionError) as chunk_error :
            return CommandResult(False, s, str(chunk_error), [context])

        if count : temp = string.Template("已在$pos放置了指定的方块").substitute(pos = tuple(set_pos))
        else : temp = string.Template("无法在$pos放置指定的方块").substitute(pos = tuple(set_pos))
        return CommandResult(bool(count), s, temp, [context])

class setworldspawn :
    """
    /setworldspawn [坐标]

    直接写入 MinecraftWorld.SpawnLocation；不写坐标时使用命令执行点。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        return functools.partial(cls.run, s=pre_process.parser_result.command,
            pos_get = pre_process.positions[0] if pre_process.positions else None)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction=None) :
        if pos_get is not None : start_pos = [math.floor(i) for i in pos_get(context)]
        else : start_pos = [math.floor(i) for i in context.location]
        start_pos[0] += 0.5 ; start_pos[2] += 0.5

        for index in range(3) : game.MinecraftWorld.SpawnLocation[index] = np.float32(start_pos[index])

        temp = string.Template("世界出生点已设置为$pos").substitute(pos = tuple(start_pos))
        return CommandResult(True, s, temp, [context])

class spawnpoint :
    """
    /spawnpoint [目标: 玩家选择器] [坐标]

    写入 Player.SpawnPoint；不写目标时以命令执行者为目标，不写坐标时使用命令执行点。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        entity_func:SelectorCallFunction = None
        if pre_process.selectors :
            entity_func = pre_process.selectors[0]
            func_token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) :
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        return functools.partial(cls.run, s=pre_process.parser_result.command, entity_get=entity_func,
            pos_get = pre_process.positions[0] if pre_process.positions else None)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction=None,
            pos_get:PosCallFunction=None) :
        if entity_get : entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        else : entity_list:List[Player] = [context.executer] if isinstance(context.executer, Player) else []
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        if pos_get is not None : start_pos = [math.floor(i) for i in pos_get(context)]
        else : start_pos = [math.floor(i) for i in context.location]
        start_pos[0] += 0.5 ; start_pos[2] += 0.5

        for player in entity_list : player.SpawnPoint = [np.float32(i) for i in start_pos]
        temp = string.Template("以下玩家出生点设置为$pos：\n$entity").substitute(
            pos = tuple(start_pos), entity = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class spreadplayers :
    """
    /spreadplayers <x> <z> <散播距离> <区域范围> <目标: 选择器> [最大高度]

    注意：命令树把 x、z 写成了 Absolute_Rotation / Relative_Rotation，因此它们来自
    pre_process.rotations[0]（按 yaw/pitch 编译）。写相对坐标时会错误地以执行者朝向为基准，
    这是命令树的既有问题。

    散布算法（简单版）：
    1. 以「散播距离」为格距把区域切成方格。不同格子中心之间的水平距离必定 >= 散播距离，
       所以「一个实体占一个格子」天然满足间距要求，不需要任何推挤 / 重抽迭代。
    2. 选格子时用三角分布：offset = (rand() - rand()) * 格子数。
       两个独立均匀随机数相减的结果以 0 为峰、向两侧线性递减，因此中间格子最先被占、
       越靠边越少 —— 即「中间概率高、四周概率低」。
    3. 中间格子被占满后才从剩余格子里随机补，保证一定放得下；放不下才报错。
    4. 落点高度用 Dimension.get_surface_block((x, z), 最大高度) 找地表，站在地表上方一格。
    """

    MAX_TRY = 64

    # 基岩版里这些方块不能作为传送落点：熔岩、水、气泡柱、火、岩浆块、凋灵玫瑰、
    # 营火、灵魂营火、甜浆果丛、下界传送门、末地传送门、末地折跃门（含流动液体变种）
    INVALID_SURFACE = {
        "minecraft:lava", "minecraft:flowing_lava", "minecraft:water", "minecraft:flowing_water",
        "minecraft:bubble_column", "minecraft:fire", "minecraft:soul_fire",
        "minecraft:magma", "minecraft:wither_rose", "minecraft:campfire", "minecraft:soul_campfire",
        "minecraft:sweet_berry_bush", "minecraft:portal", "minecraft:end_portal", "minecraft:end_gateway",
    }

    @classmethod
    def __find_landing__(cls, dimension:Dimension, block_x:int, block_z:int, top:int) :
        """
        复用 Dimension.get_surface_block 自上而下找地表，但跳过 INVALID_SURFACE 里的方块
        （熔岩、水、火、营火等不能作为传送落点）。返回落点 y；找不到返回 None。

        两条行为：
        - 区块完全没载入内存：读不到方块，无法判断安全落点 → 直接返回「维度最高位置」；
        - 区块已载入（哪怕未激活）：正常做安全落点判断。
        """
        from ..GameClass.dimension import UnloadedChunksError
        max_y = int(top)
        for _ in range(512) : # 世界高度上限内的安全上限
            # chunk_active=False：已载入但未激活的区块也允许读取，用于安全判断
            # 区块完全没载入 → 不做安全判断，直接放到维度最高位置
            try : surface_block = dimension.get_surface_block((block_x, block_z), max_y, False)
            except UnloadedChunksError : return int(dimension.HeightMax) + 1
            if surface_block is None : return None
            # 地表本身、以及它上方一格，都不能是"无效传送位置"（比如地表上盖着一层火/水）
            above_block = dimension.get_block((block_x, surface_block.y + 1, block_z), False)
            surface_name = surface_block.Permutation.name
            above_name = above_block.Permutation.name if above_block is not None else None
            # 地表本身必须是有效方块，且上方必须是空气（否则会站进石头/火/岩浆块里）
            if surface_name not in cls.INVALID_SURFACE and above_name in (None, "minecraft:air") :
                return surface_block.y + 1
            next_y = surface_block.y - 1         # 这一格不能用 → 继续往下一层找
            if next_y < dimension.HeightMin : return None
            max_y = next_y
        return None

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        distance = float(pre_process.args["Spread_Distance"][0])
        range1 = float(pre_process.args["Max_Range"][0])
        if distance >= range1 :
            token_index = pre_process.args_token_index["Spread_Distance"][0]
            raise CompileError("散播距离必须小于区域范围", token_index[0], token_index[0])

        relative_height = "Relative_Max_Height" in pre_process.args
        if "Max_Height" in pre_process.args : max_height = float(pre_process.args["Max_Height"][0])
        elif relative_height :
            raw_height = pre_process.args["Relative_Max_Height"][0]
            max_height = float(raw_height[1:] or 0)
        else : max_height = 100000

        return functools.partial(cls.run, s=command, entity_get=pre_process.selectors[0],
            hori_get = pre_process.rotations[0], distance=distance, range1=range1,
            max_height=max_height, relative_height=relative_height)

    @classmethod
    def run(cls, context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            hori_get:RotationCallFunction, distance:float, range1:float, max_height:float=100000,
            relative_height:bool=False) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        horizontal = hori_get(context)  # [x, z]
        center_x, center_z = float(horizontal[0]), float(horizontal[1])
        if relative_height : top = int(context.location[1] + max_height)
        else : top = int(max_height)

        # ── 1. 按散播距离切格子；选格子用三角分布 → 中间概率高、四周概率低 ──
        cell_size = max(distance, 1.0)
        half_count = max(0, int(range1 // cell_size))
        all_cells = [(i, j) for i in range(-half_count, half_count + 1)
                     for j in range(-half_count, half_count + 1)]
        used_cells = set() ; landing_cache = {} ; place_list = []

        def cell_landing(cell) :
            """格子中心的 (方块x, 方块z, 落点y)；熔岩/水/火等不能作为落点的方块会被跳过，找不到落点返回 None"""
            if cell not in landing_cache :
                block_x = int(math.floor(center_x + cell[0] * cell_size))
                block_z = int(math.floor(center_z + cell[1] * cell_size))
                landing_cache[cell] = (block_x, block_z,
                    cls.__find_landing__(context.dimension, block_x, block_z, top))
            return landing_cache[cell]

        for _entity in entity_list :
            picked = None
            for _try in range(cls.MAX_TRY) :
                # 三角分布选格子：两次均匀随机相减，中间格子概率最高、最外圈概率为 0
                cell_i = int((random.random() - random.random()) * (half_count + 0.5))
                cell_j = int((random.random() - random.random()) * (half_count + 0.5))
                cell = (min(max(cell_i, -half_count), half_count), min(max(cell_j, -half_count), half_count))
                if cell in used_cells : continue
                if cell_landing(cell)[2] is None : continue        # 落在熔岩/水里 → 换一个格子
                picked = cell ; break
            if picked is None :        # 中间格子被占满 / 都不可落点 → 从其余有落点的格子里挑
                free_cells = [c for c in all_cells if c not in used_cells and cell_landing(c)[2] is not None]
                if not free_cells : return CommandResult(False, s, "附近没有可落脚的传送位置", [context])
                picked = random.choice(free_cells)
            used_cells.add(picked)
            place_list.append(cell_landing(picked))

        # ── 2. 落位（落点高度已在上面算好，站在地表方块上方一格）──
        msg_list = []
        for entity, (block_x, block_z, landing) in zip(entity_list, place_list) :
            entity.Pos[0] = np.float32(block_x + 0.5)
            entity.Pos[1] = np.float32(landing)
            entity.Pos[2] = np.float32(block_z + 0.5)
            context.dimension.teleport_entity(entity, (block_x + 0.5, block_z, landing + 0.5), context.dimension)
            msg_list.append("%s 的坐标 %s" % (str(entity), tuple(float(i) for i in entity.Pos)))

        temp = string.Template("已将下列实体进行散布：\n$msg").substitute(msg="\n".join(msg_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)
