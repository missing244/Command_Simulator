from .compiler import CommandPerProcess
from .__private import *
from . import CompileError
import functools, string, random, math, itertools, json, array
from typing import Dict, Union, List, Tuple, Literal, Callable


def __block_op_index__(dimension:Dimension, condition:BlockConditionCall) -> Optional[int] :
    """
    把"方块对象 / 方块条件谓词"换算成该维度调色板（Dimension.Permutations）里的下标，
    供 CommandResult.affected_blocks 使用。
    谓词能唯一命中一个方块时返回其下标；命中多个（无法确定具体是哪个方块）或都不是时返回 None。
    """
    if condition is None : return None
    matched = [index for index, permutation in enumerate(dimension.Permutations) if condition(permutation)]
    return matched[0] if len(matched) else 2147483647


class ability :

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        handle_name = pre_process.parser_result.handle
        command = pre_process.parser_result.command
        entity_func:functools.partial = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) : 
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        if handle_name == "ability.queryall" :
            return functools.partial(cls.query_all, s=command, entity_get=entity_func)
        elif handle_name == "ability.query" :
            ability_id = pre_process.args.get("AbilityName")[0]
            return functools.partial(cls.query, s=command, entity_get=entity_func, ability_id=ability_id)
        elif handle_name == "ability.set" :
            ability_id = pre_process.args.get("AbilityName")[0]
            set_value = pre_process.args["Value"][0] == "true"
            return functools.partial(cls.set, s=command, entity_get=entity_func, ability_id=ability_id, set_value=set_value)
        

    def query_all(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp = string.Template("玩家 $player 的能力: worldbuilder=$t1 mayfly=$t2 mute=$t3")
        temp2 = string.Template("查询到以下玩家的能力：\n$result").substitute(
            result = "\n".join(( temp.substitute(player=str(i), t1=i.Ability.worldbuilder,
            t2=i.Ability.mayfly, t3=i.Ability.mute) for i in entity_list
        )))
        return CommandResult(True, s, temp2, [context]).set_affected_entities(entity_list)

    def query(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, ability_id:str) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp = string.Template("已查询以下玩家的 $abi 能力: \nTrue: $player1\nFalse: $player2").substitute(
            abi = ability_id, 
            player1 = ", ".join(str(i) for i in entity_list if i.Ability[ability_id]), 
            player2 = ", ".join(str(i) for i in entity_list if not i.Ability[ability_id]))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

    def set(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, ability_id:str, set_value:bool) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        for entity in entity_list : entity.Ability[ability_id] = set_value
        temp = string.Template("已设置以下玩家的 $abi 能力为 $value:\n$player1").substitute(
            abi = ability_id, 
            value = set_value,
            player1 = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class aimassist :

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        handle_name = pre_process.parser_result.handle
        command = pre_process.parser_result.command
        entity_func:functools.partial = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) : 
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])
        
        if handle_name == "aimassist.clear" : return functools.partial(cls.clear, s=command, entity_get=entity_func)
        elif handle_name == "aimassist.set" : return functools.partial(cls.set, s=command, entity_get=entity_func)

    def clear(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("已清除以下玩家的辅助瞄准：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def set(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("已修改以下玩家的辅助瞄准：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

class alwaysday :

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        handle_name = pre_process.parser_result.handle
        command = pre_process.parser_result.command

        if handle_name == "alwaysday.query" : return functools.partial(cls.query, s=command)
        elif handle_name == "alwaysday.set" :
            value = pre_process.args.get("Value")[0] == "true" 
            return functools.partial(cls.set, s=command, set_value=value)

    def query(context:CommandContext, game:MinecraftSimulator, s:str) :
        temp1 = string.Template("游戏规则 alwaysday 为 $value").substitute(
            value=game.MinecraftWorld.GameRule.dodaylightcycle)
        return CommandResult(True, s, temp1, [context])

    def set(context:CommandContext, game:MinecraftSimulator, s:str, set_value:bool) :
        game.MinecraftWorld.GameRule.dodaylightcycle = set_value
        if set_value : game.MinecraftWorld.Time.set_time_of_day("noon")
        temp1 = string.Template("游戏规则 alwaysday 已设置为 $value").substitute(
            value=game.MinecraftWorld.GameRule.dodaylightcycle)
        return CommandResult(True, s, temp1, [context])

class camera :

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector, is_single_entity_selector
        handle_name = pre_process.parser_result.handle
        command = pre_process.parser_result.command
        entity_func:functools.partial = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) : 
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        if handle_name == "camera.clear" :
            return functools.partial(cls.clear, s=command, entity_get=entity_func)
        if handle_name == "camera.fade" :
            rgb = (pre_process.args.get("Color_Red", (0, ))[0], pre_process.args.get("Color_Green", (0, ))[0],
            pre_process.args.get("Color_Blue", (0, ))[0])
            return functools.partial(cls.fade_color, s=command, entity_get=entity_func, rgb=rgb)
        if handle_name == "camera.add_target" :
            entity_func_2:functools.partial = pre_process.selectors[1]
            func_token_index = pre_process.selectors_token_index[1]
            if not is_single_entity_selector(entity_func_2) : 
                raise CompileError("选择器是非单目标类型", func_token_index[0], func_token_index[0])
            return functools.partial(cls.set_focus, s=command, entity_get=entity_func, focus_entity_get=entity_func_2)
        if handle_name == "camera.remove_target" :
            return functools.partial(cls.remove_focus, s=command, entity_get=entity_func)
        if handle_name == "camera.attach" :
            entity_func_2:functools.partial = pre_process.selectors[1]
            func_token_index = pre_process.selectors_token_index[1]
            if not is_single_entity_selector(entity_func_2) : 
                raise CompileError("选择器是非单目标类型", func_token_index[0], func_token_index[0])
            return functools.partial(cls.set_attach, s=command, entity_get=entity_func, focus_entity_get=entity_func_2)
        if handle_name == "camera.detach" :
            return functools.partial(cls.remove_focus, s=command, entity_get=entity_func)
        if handle_name == "camera.play_spline" :
            return functools.partial(cls.play_spline, s=command, entity_get=entity_func)
        if handle_name == "camera.fov_set" :
            fov = pre_process.args["FovValue"][0]
            return functools.partial(cls.set_fov, s=command, entity_get=entity_func, fov=fov)
        if handle_name == "camera.fov_clear" :
            return functools.partial(cls.clear_fov, s=command, entity_get=entity_func)
        if handle_name == "camera.set" :
            camera_type = pre_process.args["Camera_Type"][0]
            func_token_index = pre_process.args_token_index["Camera_Type"][0]
            if camera_type not in _game.GameSource.CAMERA_PERSET :
                raise CompileError("未知的摄像机预设ID：%s" % camera_type, func_token_index[0], func_token_index[0])

            try :
                entity_func_2:functools.partial = pre_process.selectors[1]
                func_token_index = pre_process.selectors_token_index[1]
            except : entity_func_2, func_token_index = None, None
            if entity_func_2 and not is_single_entity_selector(entity_func_2) : 
                raise CompileError("选择器是非单目标类型", func_token_index[0], func_token_index[0])
            return functools.partial(cls.set_camera, s=command, entity_get=entity_func,
                camera_id=camera_type, facing_entity_get=entity_func_2)


    def clear(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("已清除以下玩家的摄像机效果：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def fade_color(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, 
        rgb:Tuple[int, int, int] = (0, 0, 0)) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("将以下玩家的摄像头颜色设置为$rgb：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list), rgb=tuple(rgb))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def set_focus(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, 
        focus_entity_get:SelectorCallFunction) :
        entity_list1:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list1 : return CommandResult(False, s, "无选择器匹配的实体", [context])
        entity_list2:List[Entity] = focus_entity_get(context, game)
        if not entity_list2 : return CommandResult(False, s, "无选择器匹配的聚焦实体", [context])
        temp1 = string.Template("将以下玩家的自由摄像头设置为聚焦相机：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list1))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list1+entity_list2)

    def set_attach(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, 
        focus_entity_get:SelectorCallFunction) :
        entity_list1:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list1 : return CommandResult(False, s, "无选择器匹配的实体", [context])
        entity_list2:List[Entity] = focus_entity_get(context, game)
        if not entity_list2 : return CommandResult(False, s, "无选择器匹配的聚焦实体", [context])
        temp1 = string.Template("将以下玩家的轨道摄像头设置新的聚焦实体：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list1))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list1+entity_list2)

    def play_spline(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("为以下玩家的摄像头播放样条模式：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def remove_focus(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("已清除以下玩家的聚焦摄像机：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def set_fov(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, fov:float) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("将以下玩家的场视角设置为$fov：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list), fov=fov)

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)
    
    def clear_fov(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("将以下玩家的场视角恢复：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def set_camera(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, 
        camera_id:str, facing_entity_get:SelectorCallFunction=None) :
        entity_list1:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list1 : return CommandResult(False, s, "无选择器匹配的实体", [context])
        if facing_entity_get :
            entity_list2:List[Entity] = facing_entity_get(context, game)
            if not entity_list2 : return CommandResult(False, s, "无选择器匹配的朝向目标实体", [context])
        else : entity_list2 = []

        temp1 = string.Template("将以下玩家的摄像头设置为$id：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list1), id=camera_id)

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list1+entity_list2)

class camerashake :

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        handle_name = pre_process.parser_result.handle
        command = pre_process.parser_result.command
        
        entity_func:SelectorCallFunction = None
        if pre_process.selectors :
            entity_func:SelectorCallFunction = pre_process.selectors[0]
            func_token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) : 
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])
        
        if handle_name == "camerashake.add" : return functools.partial(cls.add, s=command, entity_get=entity_func)
        elif handle_name == "camerashake.stop" : return functools.partial(cls.stop, s=command, entity_get=entity_func)

    def stop(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction=None) :
        if entity_get : entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        else : entity_list:List[Player] = [context.executer] if isinstance(context.executer, Player) else []
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("以下玩家的摄像头停止摇晃：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def add(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("以下玩家的摄像头进行摇晃：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))

        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

class clear :
    """
    /clear [<目标: 玩家选择器>] [<物品ID: 字符串>] [<数据值: 整数>] [<最大清除数: 整数>]

    对应语法树（package/MCCommandParser/command_tree.py）：
        clear → [玩家选择器] → [Item_ID] → [Data(-1~32767)] → [Max_Count(>=0)]
    语义：
        - 不写物品ID：清空玩家背包（快捷栏、主背包、盔甲槽、副手），末影箱不参与；
        - 数据值 -1 表示不限数据值；写了具体值时，工具/装备比较耐久损伤，其余比较数据值；
        - 最大清除数 0 表示只统计数量、不真正清除；不写表示不限数量。
    """

    @staticmethod
    def __get_containers__(player:Player) :
        """玩家身上存放物品的容器（末影箱不参与 /clear）。"""
        from ..GameClass.entity import EntityWearArmorComponent
        container_list = [player.HotBar, player.Inventory]
        wear_armor:EntityWearArmorComponent = player.get_component(EntityWearArmorComponent, bottom=True)
        if wear_armor is not None : container_list.extend((wear_armor.Hand, wear_armor.Equippable))
        return container_list

    @staticmethod
    def __match_item__(item:ItemStack, item_id:str, data:int) -> bool :
        """判断物品是否符合清除条件（item_id 已由 ItemStack 归一化过）。"""
        if item.Identifier != item_id : return False
        if data == -1 : return True
        durability:ItemDurabilityComponent = item.get_component(ItemDurabilityComponent)
        if durability is not None : return int(durability.Damage) == data      # 工具/装备：数据值即耐久损伤
        return int(item.Damage) == data                                         # 其余物品：数据值

    @classmethod
    def clear_items(cls, player:Player, item_id:str=None, data:int=-1, max_count:int=None) -> int :
        """
        清除玩家背包中符合条件的物品。
        :param item_id:   归一化后的物品ID，None 表示不限物品
        :param data:      数据值，-1 表示不限
        :param max_count: 清除数量上限；0 表示只统计不删除；None 表示不限
        :return: 匹配到的物品个数（max_count 为 0 时表示“将会被清除”的数量）
        """
        count_only = max_count is not None and int(max_count) == 0
        remain = None if max_count is None else int(max_count)
        cleared = 0

        for container in cls.__get_containers__(player) :
            for slot in range(min(container.Size, len(container.Items))) :
                item:ItemStack = container.Items[slot]
                if not isinstance(item, ItemStack) : continue
                if item_id is not None and not cls.__match_item__(item, item_id, data) : continue

                if count_only : cleared += int(item.Count) ; continue
                take = int(item.Count) if remain is None else min(int(item.Count), remain)
                cleared += take
                if take >= int(item.Count) : container.Items[slot] = None
                else : item.Count = np.int8(int(item.Count) - take)
                if remain is not None :
                    remain -= take
                    if remain <= 0 : return cleared
                player.__update_mainhand__()
        return cleared

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command

        # 1) 目标选择器是可选的：不写时由命令执行者充当目标
        entity_func:SelectorCallFunction = None
        if pre_process.selectors :
            entity_func = pre_process.selectors[0]
            func_token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) :
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        # 2) 物品ID / 数据值 / 最大清除数（依次可选，缺失时用默认值）
        name = pre_process.args.get("Item_ID", (None, ))[0]
        data = pre_process.args.get("Data", (-1, ))[0]
        max_count = pre_process.args.get("Max_Count", (None, ))[0]

        # 3) 用 ItemStack 完成物品ID归一化（命名空间、MCBELab 的旧ID升级），并检查物品是否存在
        item_id = _game.SimulatorModule.ItemStack(name).Identifier if name else name
        if item_id is not None and item_id not in _game.GameSource.ITEM :
            token_index = pre_process.args_token_index["Item_ID"][0]
            raise CompileError("不存在的物品ID：%s" % name, token_index[0], token_index[0])

        return functools.partial(cls.clear_specific, s=command, entity_get=entity_func,
            item_id=item_id, data=data, max_count=max_count)

    def clear_specific(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction=None,
        item_id:str=None, data:int=-1, max_count:int=None) :
        # 没有写选择器时，目标就是命令执行者本身
        if entity_get : entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        else : entity_list:List[Player] = [context.executer] if isinstance(context.executer, Player) else []
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        count_only = max_count is not None and int(max_count) == 0
        msg_list:List[str] = [] ; total_count = 0 ; success = False

        for player in entity_list :
            count = clear.clear_items(player, item_id, data, max_count)
            total_count += count
            if count : success = True

            if item_id is None : item_desc = "物品"
            elif data == -1 : item_desc = item_id
            else : item_desc = "%s(%s)" % (item_id, data)

            if count_only : line = "$player 背包中有 $count 个物品" if item_id is None else "$player 背包中有 $count 个 $item"
            elif count : line = "$player 清除了背包中的 $count 个物品" if item_id is None else "$player 清除了 $count 个 $item"
            else : line = "无法匹配到 $player 背包中的物品"
            msg_list.append(string.Template(line).substitute(player=str(player), count=count, item=item_desc))

        if count_only : title = "已统计以下玩家背包中符合条件的物品：\n$msg"
        elif success : title = "已清除以下玩家的物品：\n$msg"
        else : title = "没有物品被清除：\n$msg"
        text = string.Template(title).substitute(msg="\n".join(msg_list))

        return CommandResult(success, s, text, [context]).set_affected_entities(entity_list)

class clearspawnpoint :
    """
    /clearspawnpoint [<目标: 玩家选择器>]

    清除玩家的个人出生点（床/重生锚），即把 SpawnPoint 重置为世界出生点。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command

        entity_func:SelectorCallFunction = None
        if pre_process.selectors :
            entity_func = pre_process.selectors[0]
            func_token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) :
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        return functools.partial(cls.clear, s=command, entity_get=entity_func)

    def clear(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction=None) :
        # 没有写选择器时，目标就是命令执行者本身
        if entity_get : entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        else : entity_list:List[Player] = [context.executer] if isinstance(context.executer, Player) else []
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        spawn_location = game.MinecraftWorld.SpawnLocation
        for player in entity_list :
            for index in range(3) : player.SpawnPoint[index] = spawn_location[index]

        temp = string.Template("已清除以下玩家的出生点：\n$player").substitute(
            player = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class clone :
    """
    /clone <起点1> <终点1> <目标起点> [replace|masked] [force|move|normal]
    /clone <起点1> <终点1> <目标起点> filtered <force|move|normal> <方块ID> [方块状态|数据值]

    筛选模式：replace（整片覆盖，默认）、masked（只复制源区域内的非空气方块）、
    filtered（只复制与指定方块匹配的方块，方块谓词由 Condition_Block_Compiler 编译）。
    复制模式：normal（源与目标不允许重叠，默认）、force（允许重叠）、move（复制后清空源区域）。
    容器与命令方块的方块实体数据会一并复制。
    """

    MAX_VOLUME = 655360              # 与旧实现一致的区域上限

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        positions = pre_process.positions
        if len(positions) < 3 : raise CompileError("clone 需要三组坐标")

        mask_mode = pre_process.args.get("Mask_Mode", ("replace", ))[0]
        clone_mode = pre_process.args.get("Clone_Mode", ("normal", ))[0]
        block_test:BlockConditionCall = pre_process.blocks[0] if pre_process.blocks else None

        return functools.partial(cls.run, s=command, start1=positions[0], end1=positions[1],
            start2=positions[2], mask_mode=mask_mode, clone_mode=clone_mode, block_test=block_test)

    @classmethod
    def run(cls, context:CommandContext, game:MinecraftSimulator, s:str, 
            start1:PosCallFunction, end1:PosCallFunction, start2:PosCallFunction, 
            mask_mode:Literal["replace","masked","filtered"]="replace",
            clone_mode:Literal["normal","force","move"]="normal", 
            block_test:BlockConditionCall=None) :
        start_pos1 = [math.floor(i) for i in start1(context)]
        end_pos1 = [math.floor(i) for i in end1(context)]
        clone_pos1 = [math.floor(i) for i in start2(context)]
        if start_pos1[0] > end_pos1[0] : start_pos1[0], end_pos1[0] = end_pos1[0], start_pos1[0]
        if start_pos1[1] > end_pos1[1] : start_pos1[1], end_pos1[1] = end_pos1[1], start_pos1[1]
        if start_pos1[2] > end_pos1[2] : start_pos1[2], end_pos1[2] = end_pos1[2], start_pos1[2]
        clone_pos2 = [clone_pos1[index] + end_pos1[index] - start_pos1[index] for index in range(3)]
        volume = [end_pos1[index] - start_pos1[index] + 1 for index in range(3)]
        if volume[0] * volume[1] * volume[2] > cls.MAX_VOLUME :
            return CommandResult(False, s, "区域大小超过%s个方块" % cls.MAX_VOLUME, [context])

        from ..GameClass.dimension import UnloadedChunksError, UnactiveChunksError
        from ..GameClass.dimension import RegionOverlapError, IllegalPositionError
        try : count = context.dimension.clone_blocks(start_pos1, end_pos1, clone_pos1, mask_mode, clone_mode, block_test)
        except (UnloadedChunksError, UnactiveChunksError, IllegalPositionError, RegionOverlapError) as chunk_error :
            return CommandResult(False, s, str(chunk_error), [context])

        block_op = ("clone", start_pos1[0], start_pos1[1], start_pos1[2], end_pos1[0], end_pos1[1], end_pos1[2],
            clone_pos1[0], clone_pos1[1], clone_pos1[2], __block_op_index__(context.dimension, block_test) 
            if mask_mode == "filtered" else None)

        temp = string.Template("在以下区域复制了$count个方块：\n$start ~ $end").substitute(
            start=tuple(clone_pos1), end=tuple(clone_pos2), count=count)
        return CommandResult(count > 0, s, temp, [context]).set_affected_blocks(block_op)

class controlscheme : 

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        handle_name = pre_process.parser_result.handle
        command = pre_process.parser_result.command
        entity_func:functools.partial = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) : 
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        if handle_name == "controlscheme.clear" : 
            return functools.partial(cls.clear, s=command, entity_get=entity_func)
        elif handle_name == "controlscheme.set" : 
            return functools.partial(cls.set, s=command, entity_get=entity_func)

    def clear(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:Callable) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("已清除以下玩家的摄像头控制模式：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

    def set(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:Callable) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])
        temp1 = string.Template("已修改以下玩家的摄像头控制模式：\n$player").substitute(
            player=", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp1, [context]).set_affected_entities(entity_list)

class damage :
    """
    /damage <目标: 选择器> <伤害值> [<伤害类型>] [entity <伤害来源: 选择器>]

    伤害结算全部交给 Entity.apply_damage：免疫判定、各类伤害的减免条件、
    受击后伤害免疫都在那边处理，这里只负责取选择器、编译期校验伤害类型、拼反馈文本。
    伤害类型取自 Constants.DAMAGE_CAUSE；另外语法树允许写 suicide（伤害来源是目标自身）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_single_entity_selector
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]

        amount = pre_process.args["Amount"][0]
        cause = pre_process.args.get("Damager_Type", ("none", ))[0]
        if cause != "suicide" and cause not in Constants.DAMAGE_CAUSE :
            token_index = pre_process.args_token_index["Damager_Type"][0]
            raise CompileError("不存在的伤害类型：%s" % cause, token_index[0], token_index[0])

        # 写了 "entity <选择器>" 时才会有第二个选择器（伤害来源）
        if len(pre_process.selectors) > 1 :
            source_func:SelectorCallFunction = pre_process.selectors[1]
            func_token_index = pre_process.selectors_token_index[1]
            if not is_single_entity_selector(source_func) : 
                raise CompileError("选择器是非单目标类型", func_token_index[0], func_token_index[0])
        else : source_func = None
        return functools.partial(cls.run, s=command, entity_get=entity_func, amount=float(amount),
            cause=cause, source_get=source_func)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
            amount:float, cause:str="none", source_get:SelectorCallFunction=None) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        source:Entity = None
        if source_get is not None :
            source_list:List[Entity] = source_get(context, game)
            if not source_list : return CommandResult(False, s, "无选择器匹配的伤害来源实体", [context])
            source = source_list[0]

        success_list, faild_list = [], []
        for entity in entity_list :
            if entity.apply_damage(amount, cause, source) : success_list.append(str(entity))
            else : faild_list.append(str(entity))

        msg_list = []
        if success_list : msg_list.append("以下实体受到了伤害：\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体免疫了伤害：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

class daylock :
    """
    /daylock [<true|false>]

    与 alwaysday 是同一指令的两种写法（这里保持与 alwaysday 完全一致的行为）：
    写值时为设置 dodaylightcycle 游戏规则并跳到正午，不写时为查询。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        if "Value" in pre_process.args :
            return functools.partial(cls.set, s=command, set_value=pre_process.args["Value"][0] == "true")
        return functools.partial(cls.query, s=command)

    def query(context:CommandContext, game:MinecraftSimulator, s:str) :
        temp = string.Template("游戏规则 dodaylightcycle 为 $value").substitute(
            value = game.MinecraftWorld.GameRule.dodaylightcycle)
        return CommandResult(True, s, temp, [context])

    def set(context:CommandContext, game:MinecraftSimulator, s:str, set_value:bool) :
        game.MinecraftWorld.GameRule.dodaylightcycle = set_value
        if set_value : game.MinecraftWorld.Time.set_time_of_day("noon")
        temp = string.Template("游戏规则 dodaylightcycle 已变更为 $value").substitute(
            value = game.MinecraftWorld.GameRule.dodaylightcycle)
        return CommandResult(True, s, temp, [context])

class dialogue:
    """
    /dialogue open   <NPC: 选择器> <玩家: 选择器> [场景ID]
    /dialogue change <NPC: 选择器> <场景ID> [玩家: 选择器]

    本模拟器只登记了 NPC 对话场景（GameSource.DIALOGUES），没有实际的对话界面，
    因此该指令只做参数校验与结果反馈（与 hud / scriptevent 一样属于“仅模拟”）。
    """

    @staticmethod
    def __npc_list__(entity_npc:SelectorCallFunction, context:CommandContext, game:MinecraftSimulator) -> List[Entity] :
        return [i for i in entity_npc(context, game) if i.Identifier == "minecraft:npc"]

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector, is_single_entity_selector, is_npc_only_selector
        command = pre_process.parser_result.command
        handle_name = pre_process.parser_result.handle
        scene_name = pre_process.args.get("Scene_Name", (None, ))[0]

        if scene_name is not None and scene_name not in _game.GameSource.DIALOGUES :
            token_index = pre_process.args_token_index["Scene_Name"][0]
            raise CompileError("不存在的场景ID：%s" % scene_name, token_index[0], token_index[0])

        # 第 1 个选择器：NPC（必须是单目标）
        entity_npc:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_single_entity_selector(entity_npc) :
            raise CompileError("选择器是非单目标类型", func_token_index[0], func_token_index[0])
        if not is_npc_only_selector(entity_npc) :
            raise CompileError("选择器是非NPC类型", func_token_index[0], func_token_index[0])

        # 第 2 个选择器：玩家（open 必有；change 可选，缺省为命令执行者）
        entity_player:SelectorCallFunction = None
        if len(pre_process.selectors) > 1 :
            entity_player = pre_process.selectors[1]
            func_token_index = pre_process.selectors_token_index[1]
            if not is_player_only_selector(entity_player) :
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        if handle_name == "dialogue.change" : return functools.partial(cls.change, s=command, 
            entity_npc=entity_npc, entity_player=entity_player)
        elif handle_name == "dialogue.open" : return functools.partial(cls.open, s=command, 
            entity_npc=entity_npc, entity_player=entity_player)

    def open(context:CommandContext, game:MinecraftSimulator, s:str, entity_npc:SelectorCallFunction,
            entity_player:SelectorCallFunction) :
        npc_list:List[Entity] = dialogue.__npc_list__(entity_npc, context, game)
        entity_list:List[Player] = [i for i in entity_player(context, game) if isinstance(i, Player)]
        if not npc_list : return CommandResult(False, s, "没有与目标选择器匹配的NPC", [context])
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("已向以下玩家打开NPC对话：\n$player").substitute(
            player = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

    def change(context:CommandContext, game:MinecraftSimulator, s:str, entity_npc:SelectorCallFunction,
               entity_player:SelectorCallFunction=None) :
        npc_list:List[Entity] = dialogue.__npc_list__(entity_npc, context, game)
        if entity_player : entity_list:List[Player] = [i for i in entity_player(context, game) if isinstance(i, Player)]
        else : entity_list:List[Player] = [context.executer] if isinstance(context.executer, Player) else []
        if not npc_list : return CommandResult(False, s, "没有与目标选择器匹配的NPC", [context])
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("已将以下玩家的对话场景切换：\n$player").substitute(
            player = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class difficulty :
    """
    /difficulty <peaceful|easy|normal|hard|p|e|n|h|0|1|2|3>

    设置世界难度；别名到数值的映射由 Constants.DIFFICULT 提供。
    """

    CANONICAL = ("peaceful", "easy", "normal", "hard")

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        token = pre_process.args["Difficulty"][0]
        return functools.partial(cls.set, s=command, value=Constants.DIFFICULT[token])

    def set(context:CommandContext, game:MinecraftSimulator, s:str, value:int) :
        game.MinecraftWorld.Difficulty = value
        temp = string.Template("将游戏难度设置为 $value").substitute(value = difficulty.CANONICAL[value])
        return CommandResult(True, s, temp, [context])

class effect :
    """
    /effect <目标: 选择器> clear [效果ID]
    /effect <目标: 选择器> <效果ID> [秒数|infinite] [增幅器] [是否隐藏粒子]

    说明：
        - 秒数为 0 等价于移除该效果；省略秒数时默认 30 秒；
        - infinite 用一个很长的秒数模拟（本模拟器的效果组件没有“无限”标记）；
        - 隐藏粒子参数会被解析但不生效（效果组件不保存该标记）；
        - 效果ID 去掉 minecraft: 前缀后按 Constants.EFFECT 校验。
    """
    INFINITE_SECONDS = -1          # 语法树允许的最大秒数，用作“无限”的替代

    @staticmethod
    def __effect_comp__(entity:Entity) -> EntityDefine.EntityEffectComponent :
        return entity.get_component(EntityDefine.EntityEffectComponent, bottom=True)

    @classmethod
    def __result__(cls, s:str, context:CommandContext, entity_list:List[Entity],
        success_list:List[str], faild_list:List[str], success_text:str, faild_text:str) -> CommandResult :
        msg_list = []
        if success_list : msg_list.append(success_text + "：\n" + ", ".join(success_list))
        if faild_list : msg_list.append(faild_text + "：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        handle_name = pre_process.parser_result.handle
        entity_func:SelectorCallFunction = pre_process.selectors[0]        # 该指令必须写目标选择器

        effect_id = pre_process.args.get("Effect_Type", (None, ))[0]
        if handle_name == "effect.clear" :
            if effect_id is not None and effect_id not in Constants.EFFECT :
                token_index = pre_process.args_token_index["Effect_Type"][0]
                raise CompileError("不存在的药水效果：%s" % effect_id, token_index[0], token_index[0])
            return functools.partial(cls.clear, s=command, entity_get=entity_func, effect_id=effect_id)
        if handle_name == "effect.give" :
            seconds = pre_process.args.get("Seconds", (30, ))[0]
            if seconds == "infinite" : seconds = cls.INFINITE_SECONDS
            if seconds == 0 : return functools.partial(cls.clear, s=command, entity_get=entity_func, effect_id=effect_id)

            amplifier = pre_process.args.get("Amplifier", (0, ))[0]
            return functools.partial(cls.give, s=command, entity_get=entity_func, effect_id=effect_id,
                seconds=seconds, amplifier=amplifier)

    def clear(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, effect_id:str=None) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for entity in entity_list :
            effect_comp = effect.__effect_comp__(entity)
            if effect_comp is None : faild_list.append(str(entity)) ; continue
            if effect_id is None : removed = sum(1 for name in Constants.EFFECT if effect_comp.remove_effect(name))
            else : removed = 1 if effect_comp.remove_effect(effect_id) else 0
            (success_list if removed else faild_list).append(str(entity))

        return effect.__result__(s, context, entity_list, success_list, faild_list,
            "以下实体成功的移除了效果", "以下实体无法移除效果")

    def give(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, 
            effect_id:str, seconds:int=30, amplifier:int=0) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for entity in entity_list :
            effect_comp = effect.__effect_comp__(entity)
            if effect_comp is None : faild_list.append(str(entity)) ; continue
            if effect_comp.add_effect(effect_id, amplifier, seconds) : success_list.append(str(entity))
            else : faild_list.append(str(entity))

        return effect.__result__(s, context, entity_list, success_list, faild_list,
            "以下实体成功的添加了药水效果", "以下实体无法添加药水效果")

class enchant :
    """
    /enchant <目标: 玩家选择器> <附魔名称|数字ID> [等级]

    作用于玩家当前选中槽位的物品（主手），等级省略时为 1。
    规则与旧实现一致：未附魔则按目标等级附魔；已有等级更低则提升到目标等级；
    相等则 +1（不超过该附魔上限）；已有等级更高则失败。
    """

    @staticmethod
    def __find_enchant__(name_or_id:Union[str, int]) -> Union[str, None] :
        """把附魔名称或附魔数字ID解析为 Constants.ENCHANT 中的键。"""
        if isinstance(name_or_id, str) :
            enchant_id = name_or_id.replace("minecraft:", "", 1).lower()
            return enchant_id if enchant_id in Constants.ENCHANT else None
        for enchant_id, enchant_data in Constants.ENCHANT.items() :
            if enchant_data.get("id") == name_or_id : return enchant_id
        return None

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command

        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        if "Enchant_Type" in pre_process.args :
            raw = pre_process.args["Enchant_Type"][0]
            token_index = pre_process.args_token_index["Enchant_Type"][0]
        else :
            raw = pre_process.args["Enchantment_ID"][0]
            token_index = pre_process.args_token_index["Enchantment_ID"][0]

        enchant_id = cls.__find_enchant__(raw)
        if enchant_id is None :
            raise CompileError("不存在的附魔ID：%s" % raw, token_index[0], token_index[0])

        enchant_max = Constants.ENCHANT[enchant_id]["max_lvl"]
        enchant_level = pre_process.args.get("Level", (1, ))[0]
        if not(1 <= enchant_level <= enchant_max) :
            token_index = pre_process.args_token_index.get("Level", token_index)[0]
            raise CompileError("附魔等级应该在 1~%s 内" % enchant_max, token_index[0], token_index[0])

        return functools.partial(cls.enchant_item, s=command, entity_get=entity_func,
            enchant_id=enchant_id, enchant_level=enchant_level, enchant_max=enchant_max)

    def enchant_item(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
        enchant_id:str, enchant_level:int=1, enchant_max:int=1) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for player in entity_list :
            item:ItemStack = player.HotBar.Items[player.SelectedSlotIndex]      # 主手（选中槽位）物品
            if not isinstance(item, ItemStack) : faild_list.append(str(player)) ; continue

            enchant_comp:ItemEnchantableComponent = item.get_component(ItemEnchantableComponent)
            if enchant_comp is None : faild_list.append(str(player)) ; continue

            can_add = enchant_comp.add_enchantment(enchant_id, enchant_level)
            if can_add : success_list.append(str(player))
            else : faild_list.append(str(player))

        msg_list = []
        if success_list : msg_list.append("以下玩家成功为主手物品添加附魔：\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下玩家无法为主手物品添加附魔：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

class event :
    """
    /event entity <目标: 选择器> <事件ID>

    触发实体自身定义中的事件（GameSource.ENTITY[实体ID]["events"]）；事件ID 允许省略 minecraft: 前缀。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        event_id = pre_process.args.get("Event_ID")[0]
        return functools.partial(cls.run_event, s=command, entity_get=entity_func, event_id=event_id)

    def run_event(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, event_id:str) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for entity in entity_list :
            events = game.GameSource.ENTITY.get(entity.Identifier, {}).get("events", {})
            resolved = event_id if event_id in events else None
            if resolved is None : faild_list.append(str(entity)) ; continue
            entity.trigger_event(resolved)
            success_list.append(str(entity))

        msg_list = []
        if success_list : msg_list.append("以下实体成功的触发了事件：\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下实体无法触发事件：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

class fill :
    """
    /fill <起点: x y z> <终点: x y z> <方块> [replace|destroy|keep|hollow|outline] [替换方块]

    版本兼容：
        - <1.19.70：方块ID 后可跟 [state=value] 方块状态，也可跟旧式数据值；
          数据值在本类的 __make_block__ 里通过 BlockPermutation(name, 数据值) 走 MCBELab 兼容表翻译成方块状态；
        - 1.19.70~1.19.80：语法树只产出方块状态；
        - ≥1.19.80：由子类 fill_1_19_80 负责（逻辑完全一致，只是语法树不再产出 Block_Data）。
    真正的方块写入交给 Dimension.fill_blocks（已实现 replace/replace_block/keep/outline/hollow/destroy）。
    """

    MAX_VOLUME = 32768              # 单次填充的方块数量上限（与旧实现一致）

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command

        fill_mode = pre_process.args.get("Fill_Mode", ("replace", ))[0]
        block = pre_process.blocks[0]

        replace_block = None
        if len(pre_process.blocks) > 1 : replace_block = pre_process.blocks[1]

        return functools.partial(cls.fill_block, s=command, start_pos=pre_process.positions[0],
            end_pos=pre_process.positions[1], block=block, fill_mode=fill_mode, replace_condition=replace_block)

    @classmethod
    def fill_block(cls, context:CommandContext, game:MinecraftSimulator, s:str, 
        start_pos:PosCallFunction, end_pos:PosCallFunction, block:BlockPermutation=None, 
        fill_mode:str="replace", replace_condition:BlockConditionCall=None) :

        start_pos = tuple(math.floor(i) for i in start_pos(context))
        end_pos = tuple(math.floor(i) for i in end_pos(context))
        for index in range(3) :
            if start_pos[index] > end_pos[index] : start_pos[index], end_pos[index] = end_pos[index], start_pos[index]

        height = Constants.DIMENSION_INFO[context.dimension.Identifier]["height"]
        if not(height[0] <= start_pos[1] < height[1]) :
            return CommandResult(False, s, "起始位置%s处于世界之外" % (start_pos, ), [context])
        if not(height[0] <= end_pos[1] < height[1]) :
            return CommandResult(False, s, "结束位置%s处于世界之外" % (end_pos, ), [context])

        volume = (end_pos[0]-start_pos[0]+1) * (end_pos[1]-start_pos[1]+1) * (end_pos[2]-start_pos[2]+1)
        if volume > cls.MAX_VOLUME : return CommandResult(False, s, "区域大小超过%s个方块" % cls.MAX_VOLUME, [context])

        from ..GameClass.dimension import UnloadedChunksError, UnactiveChunksError, IllegalPositionError
        try : count = context.dimension.fill_blocks(start_pos, end_pos, block, fill_mode, replace_condition)
        except (UnloadedChunksError, UnactiveChunksError, IllegalPositionError) as chunk_error :
            return CommandResult(False, s, str(chunk_error), [context])

        block_op = ("fill", start_pos[0], start_pos[1], start_pos[2], end_pos[0], end_pos[1], end_pos[2],
            context.dimension.Permutations.append(block), __block_op_index__(context.dimension, replace_condition))

        temp = string.Template("在以下区域填充了$count个方块：\n$start ~ $end").substitute(
            start=tuple(start_pos), end=tuple(end_pos), count=count)
        return CommandResult(count > 0, s, temp, [context]).set_affected_blocks(block_op)

class fog :
    """
    /fog <目标: 玩家选择器> push <迷雾ID> <用户ID>
    /fog <目标: 玩家选择器> (pop|remove) <用户ID>

    每个玩家维护一个迷雾栈（首次使用时在玩家对象上创建 FogStack），
    push 入栈；pop/remove 移除该用户ID最后压入的一项（栈顶优先）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command

        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        mode = pre_process.args["Mode"][0]
        user_id = Quotation_String_Transfor(pre_process.args["User_Provided_Id"][0])
        if mode == "pop" : return functools.partial(cls.pop, s=command, entity_get=entity_func, user_id=user_id)
        elif mode == "remove" : return functools.partial(cls.remove, s=command, entity_get=entity_func, user_id=user_id)

        fog_id = pre_process.args["Fog_Type"][0]
        if fog_id not in _game.GameSource.FOG :
            token_index = pre_process.args_token_index["Fog_Type"][0]
            raise CompileError("不存在的迷雾ID：%s" % fog_id, token_index[0], token_index[0])
        return functools.partial(cls.push, s=command, entity_get=entity_func, fog_id=fog_id, user_id=user_id)

    def push(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
             fog_id:str, user_id:str) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        for player in entity_list : player.FogStack.append({"user_id":user_id, "id":fog_id})
        temp = string.Template("以下玩家已将迷雾添加至栈内：\n$player").substitute(
            player = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

    def pop(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, user_id:str) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for player in entity_list :
            stack = player.FogStack
            for index in range(len(stack) - 1, -1, -1) :          # 从栈顶开始找该用户ID
                if stack[index]["user_id"] != user_id : continue
                del stack[index] ; success_list.append(str(player)) ; break
            else : faild_list.append(str(player))

        msg_list = []
        if success_list : msg_list.append("以下玩家已移除最后压入的迷雾：\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下玩家不存在压入的迷雾：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

    def remove(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, user_id:str) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for player in entity_list :
            stack = player.FogStack
            success = False
            for index in range(len(stack) - 1, -1, -1) :          # 从栈顶开始找该用户ID
                if stack[index]["user_id"] != user_id : continue
                del stack[index] ; success = True
            if success : success_list.append(str(player))
            else : faild_list.append(str(player))

        msg_list = []
        if success_list : msg_list.append("以下玩家已移除所有压入的迷雾：\n" + ", ".join(success_list))
        if faild_list : msg_list.append("以下玩家不存在压入的迷雾：\n" + ", ".join(faild_list))
        return CommandResult(bool(success_list), s, "\n".join(msg_list), [context]).set_affected_entities(entity_list)

class gamemode :
    """
    /gamemode <模式> [目标: 玩家选择器]

    模式写法：survival/s/0、creative/c/1、adventure/a/2、default/d（世界默认）、spectator。
    """

    MODE_NAME = {0:"生存", 1:"创造", 2:"冒险", 5:"世界默认", 6:"旁观"}

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        mode = pre_process.args["Game_Mode"][0]

        entity_func:SelectorCallFunction = None
        if pre_process.selectors :
            entity_func = pre_process.selectors[0]
            func_token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) :
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        return functools.partial(cls.set_gamemode, s=command, mode=mode, entity_get=entity_func)

    def set_gamemode(context:CommandContext, game:MinecraftSimulator, s:str, mode:Union[str, int],
        entity_get:SelectorCallFunction=None) :
        # 没有写选择器时，目标就是命令执行者本身
        if entity_get : entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        else : entity_list:List[Player] = [context.executer] if isinstance(context.executer, Player) else []
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        for player in entity_list : player.GameMode.set_mode(mode)
        display_gm = entity_list[0].GameMode.Mode
        temp = string.Template("以下玩家已将游戏模式更改为$mode：\n$player").substitute(
            mode = gamemode.MODE_NAME[display_gm], player = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class gamerule :
    """
    /gamerule [<规则名> [true|false|整数]]

    不写规则名时输出全部规则；写规则名不写值时为查询；值按 Constants.GAMERULE 的类型与范围校验
    （GameRuleManager 对非法赋值是静默忽略的，所以在编译期就拦住）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        rule_name = pre_process.args.get("Gamerule_Type", (None, ))[0]
        if rule_name is None : return functools.partial(cls.read_all_rule, s=command)

        rule_name = rule_name.lower()
        rule_data = Constants.GAMERULE.get(rule_name, None)
        if rule_data is None :
            token_index = pre_process.args_token_index["Gamerule_Type"][0]
            raise CompileError("不存在的游戏规则：%s" % rule_name, token_index[0], token_index[0])

        if "Bool_Value" in pre_process.args :
            value = pre_process.args["Bool_Value"][0] == "true"
            token_index = pre_process.args_token_index["Bool_Value"][0]
        elif "Int_Value" in pre_process.args :
            value = pre_process.args["Int_Value"][0]
            token_index = pre_process.args_token_index["Int_Value"][0]
        else :
            return functools.partial(cls.set_gamerule, s=command, rule_name=rule_name)

        if rule_data["default"].__class__ is bool :
            if value.__class__ is not bool :
                raise CompileError("游戏规则 %s 是布尔类型" % rule_name, token_index[0], token_index[0])
        else :
            if value.__class__ is not int :
                raise CompileError("游戏规则 %s 是整数类型" % rule_name, token_index[0], token_index[0])
            if not(rule_data["min"] <= value <= rule_data["max"]) :
                raise CompileError("游戏规则 %s 的取值范围为 %s~%s" % (rule_name, rule_data["min"], rule_data["max"]),
                    token_index[0], token_index[0])

        return functools.partial(cls.set_gamerule, s=command, rule_name=rule_name, value=value)

    def read_all_rule(context:CommandContext, game:MinecraftSimulator, s:str) :
        game_rule = game.MinecraftWorld.GameRule
        text_list = ["%s => %s" % (name, getattr(game_rule, name))
                     for name in Constants.GAMERULE if hasattr(game_rule, name)]
        temp = string.Template("已输出所有游戏规则：\n$text").substitute(text="\n".join(text_list))
        return CommandResult(True, s, temp, [context])

    def set_gamerule(context:CommandContext, game:MinecraftSimulator, s:str, rule_name:str, value:Union[bool,int]=None) :
        game_rule = game.MinecraftWorld.GameRule
        if value is None :
            temp = string.Template("游戏规则 $rule 为 $value1").substitute(
                rule = rule_name, value1 = getattr(game_rule, rule_name))
            return CommandResult(True, s, temp, [context])

        setattr(game_rule, rule_name, value)
        temp = string.Template("游戏规则 $rule 已修改为 $value1").substitute(
            rule = rule_name, value1 = getattr(game_rule, rule_name))
        return CommandResult(True, s, temp, [context])

class give :
    """
    /give <目标: 玩家选择器> <物品ID> [数量] [数据值] [物品组件JSON]

    数量超过堆叠上限时自动拆成多组；快捷栏与背包都放不下的部分会掉落为物品实体。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        name = pre_process.args.get("Item_Type")[0]
        item_id = _game.SimulatorModule.ItemStack(name, 1, 0).Identifier
        if item_id not in _game.GameSource.ITEM :
            token_index = pre_process.args_token_index["Item_Type"][0]
            raise CompileError("不存在的物品ID：%s" % item_id, token_index[0], token_index[0])

        return functools.partial(cls.give_item, s=command, entity_get=entity_func, item_id=item_id,
            count = pre_process.args.get("Amount_Int", (1, ))[0],
            data = pre_process.args.get("Data_Int", (0, ))[0],
            comp_applier = pre_process.json_and_text[0] if pre_process.json_and_text else None)

    def give_item(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
        item_id:str, count:int=1, data:int=0, comp_applier:ItemStackApplierCall=None) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list = []
        ItemStack = game.SimulatorModule.ItemStack
        for player in entity_list :
            success_list.append(str(player))
            if item_id == "minecraft:air" : continue
            
            remain = int(count)
            while remain > 0 :
                item = ItemStack(item_id, 1, data)
                take = min(remain, int(item.MaxCount))
                item.Count = np.int8(take)
                if comp_applier is not None : comp_applier(item)
                remain -= take

                leftover = player.HotBar.add_item(item)
                if leftover is not None : leftover = player.Inventory.add_item(leftover)
                if leftover is not None :                      # 背包已满：掉落为物品实体
                    entity = context.dimension.spawn_entity("minecraft:item", player.Pos, (0, 0))
                    item_comp:EntityDefine.EntityItemComponent = entity.get_component(EntityDefine.EntityItemComponent)
                    if item_comp is not None : item_comp.ItemStack = leftover

            player.__update_mainhand__()

        temp = string.Template("已给予以下玩家 $item * $count：\n$player").substitute(
            item = item_id, count = count, player = ", ".join(success_list))
        return CommandResult(bool(success_list), s, temp, [context]).set_affected_entities(entity_list)


