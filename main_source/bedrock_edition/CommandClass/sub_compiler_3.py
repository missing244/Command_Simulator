from .compiler import CommandPerProcess
from .__private import *
from . import CompileError
import functools, string, random, math, itertools, json, copy
from typing import Dict, Union, List, Tuple, Literal, Callable
from .. import MathFunction


# ==============================================================================================
# 模块级公共工具
# ==============================================================================================

def __facing_rotation__(origin:List[float], target:List[float]) -> List[float] :
    """计算从 origin 指向 target 的 (yaw, pitch)（单位：度）。"""
    direction = MathFunction.Vector3(target[0] - origin[0], target[1] - origin[1], target[2] - origin[2])
    yaw, pitch = direction.to_minecraft_rotation()
    return [float(yaw), float(pitch)]

def __facing_angle__(context:CommandContext, game:MinecraftSimulator, facing_get, facing_type:str, origin:List[float]) :
    """
    统一解析 facing 参数（坐标 / 实体选择器 / 旋转角）。
    :return: (rotation, error_message)，两者至少有一个为 None
    """
    if facing_get is None : return (None, None)
    if facing_type == "rotation" : return ([float(i) for i in facing_get(context)], None)
    if facing_type == "pos" : return (__facing_rotation__(origin, [float(i) for i in facing_get(context)]), None)

    entity_list:List[Entity] = facing_get(context, game)
    if not entity_list : return (None, "没有与目标选择器匹配的目标")
    return (__facing_rotation__(origin, [float(i) for i in entity_list[0].Pos]), None)

def __do_teleport__(dimension:Dimension, entity_list:List[Entity], pos:List[float], rotation:List[float]=None) :
    """把实体传送到指定维度的坐标（模拟器没有传送接口，直接写实体字段并同步维度的实体缓存）。"""
    for entity in entity_list :
        if entity.Dimension is not dimension :
            old_dimension = entity.Dimension
            if old_dimension is not None and entity in old_dimension.EntityCache :
                old_dimension.EntityCache.remove(entity)
            dimension.EntityCache.append(entity)
            entity.Dimension = dimension
        for index in range(3) : entity.Pos[index] = np.float32(pos[index])
        if rotation is not None :
            entity.Rotation[0] = np.float32(rotation[0]) ; entity.Rotation[1] = np.float32(rotation[1])

def __summon_entity__(context:CommandContext, game:MinecraftSimulator, entity_id:str, pos:List[float],
    rotation:List[float]=None, entity_event:str=None, entity_name:str=None) :
    """
    生成实体并登记进区块。
    注：Dimension.spawn_entity 内部用 np.float32 标量去赋值 entity.Rotation，
        会被 Entity.__setattr__ 的类型检查拒绝（AttributeError），因此这里手动完成等价流程。
    """
    dimension = context.dimension
    if dimension.is_chunk_active(pos) is not True : return None

    entity:Entity = game.SimulatorModule.Entity(entity_id)
    for index in range(3) : entity.Pos[index] = np.float32(pos[index])
    if rotation is not None :
        entity.Rotation[0] = np.float32(rotation[0]) ; entity.Rotation[1] = np.float32(rotation[1])
    entity.Dimension = dimension
    if entity_name : entity.CustomName = entity_name
    if entity_event : entity.trigger_event(entity_event)

    chunk = dimension.__get_chunk__(pos)
    chunk.Entities.append(entity)
    dimension.EntityCache.append(entity)
    return entity

def __target_list__(context:CommandContext, game:MinecraftSimulator, entity_get:SelectorCallFunction) -> List[Entity] :
    """没有写选择器时以命令执行者为目标。"""
    if entity_get is not None : return list(entity_get(context, game))
    return [context.executer] if isinstance(context.executer, Entity) else []

def __result_text__(success_list:List[str], faild_list:List[str], success_text:str, faild_text:str) -> str :
    success = string.Template("$text:\n$entity")
    return string.Template("$success$is_line$faild").substitute(
        success = success.substitute(text=success_text, entity=", ".join(success_list)) if success_list else "",
        is_line = "\n" if success_list and faild_list else "",
        faild = success.substitute(text=faild_text, entity=", ".join(faild_list)) if faild_list else "")


class scriptevent :
    """
    /scriptevent <消息ID: 命名空间:名称> <消息>

    本模拟器没有脚本引擎，只做"仅模拟"反馈。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        message_id = pre_process.args["Message_ID"][0]
        token_index = pre_process.args_token_index["Message_ID"][0]
        if ":" not in message_id :
            raise CompileError("需要提供自定义命名空间", token_index[0], token_index[0])
        if message_id[0:10] == "minecraft:" :
            raise CompileError("需要提供非minecraft的自定义命名空间", token_index[0], token_index[0])

        return functools.partial(cls.run, s=command, message_id=message_id,
            message=pre_process.args["Message"][0])

    def run(context:CommandContext, game:MinecraftSimulator, s:str, message_id:str, message:str) :
        temp = string.Template("已发送脚本事件（仅模拟）：\n$id -> $msg").substitute(id=message_id, msg=message)
        return CommandResult(True, s, temp, [context])

# TODO
class structure :
    """
    /structure save <名称> <起点> <终点> [是否包含实体] [memory|disk] [是否包含方块]
    /structure load <名称> <起点> [旋转] [镜像] [逐方块|逐层] [动画秒数] [是否包含实体] [是否包含方块]
                     [是否含水] [完整度] [种子]
    /structure delete <名称>

    结构读写交给 MinecraftSimulator.StructureManage（CommonStructure / .mcstructure 文件）。
    """

    # 与旧实现一致的区域上限（x/z 最多 64 格，y 最多 320 格）
    MAX_SIZE = (64, 320, 64)

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        model = pre_process.args["Model"][0]
        name = Quotation_String_Transfor(pre_process.args["Structure_Name"][0])

        if model == "save" :
            positions = pre_process.positions
            if len(positions) < 2 : raise CompileError("structure save 需要起点与终点坐标")
            return functools.partial(cls.save, s=command, name=name, start_pos=positions[0], end_pos=positions[1],
                save_mode = pre_process.args.get("Save_Mode", ("memory", ))[0],
                has_entity = pre_process.args.get("IncludeEntities", ("true", ))[0] == "true",
                has_block = pre_process.args.get("IncludeBlocks", ("true", ))[0] == "true")

        if model == "load" :
            positions = pre_process.positions
            if not positions : raise CompileError("structure load 需要起点坐标")
            seed = pre_process.args.get("Seed", (None, ))[0]
            return functools.partial(cls.load, s=command, name=name, start_pos=positions[0],
                rotation = pre_process.args.get("Rotation", ("0_degrees", ))[0],
                mirror = pre_process.args.get("Mirror", ("none", ))[0],
                has_entity = pre_process.args.get("Include_Entities", ("true", ))[0] == "true",
                has_block = pre_process.args.get("Include_Blocks", ("true", ))[0] == "true",
                waterlogged = pre_process.args.get("Waterlogged", ("true", ))[0] == "true",
                integrity = pre_process.args.get("Integrity", (100.0, ))[0],
                seed = Quotation_String_Transfor(seed) if seed is not None else None)

        return functools.partial(cls.delete, s=command, name=name)

    def save(context:CommandContext, game:MinecraftSimulator, s:str, name:str, start_pos:PosCallFunction,
             end_pos:PosCallFunction, save_mode:Literal["disk", "memory"]="memory",
             has_entity:bool=True, has_block:bool=True) :
        start = [math.floor(i) for i in start_pos(context)]
        end = [math.floor(i) for i in end_pos(context)]
        for index in range(3) :
            if start[index] > end[index] : start[index], end[index] = end[index], start[index]

        area = [end[index] - start[index] + 1 for index in range(3)]
        for index in range(3) :
            if not(0 <= area[index] <= structure.MAX_SIZE[index]) :
                temp = string.Template("区域$pos1 ~ $pos2超过64*320*64大小").substitute(
                    pos1=tuple(start), pos2=tuple(end))
                return CommandResult(False, s, temp, [context])

        from ..GameClass.dimension import UnloadedChunksError, UnactiveChunksError
        try : structure_obj = game.StructureManage.create_structure(context.dimension, start, end)
        except (UnloadedChunksError, UnactiveChunksError) as chunk_error :
            return CommandResult(False, s, str(chunk_error), [context])

        # 说明：create_structure 只搬运方块，has_entity / has_block 目前无法生效（见报告）
        game.StructureManage.set_structure(name, structure_obj, save_mode)

        temp = string.Template("区域$pos1 ~ $pos2内保存为结构 $name").substitute(
            pos1=tuple(start), pos2=tuple(end), name=name)
        return CommandResult(True, s, temp, [context])

    def load(context:CommandContext, game:MinecraftSimulator, s:str, name:str, start_pos:PosCallFunction,
             rotation:Literal["0_degrees", "90_degrees", "180_degrees", "270_degrees"]="0_degrees",
             mirror:Literal["none", "x", "z", "xz"]="none", has_entity:bool=True, has_block:bool=True,
             waterlogged:bool=True, integrity:float=100.0, seed:str=None) :
        if name not in game.StructureManage :
            return CommandResult(False, s, "不存在结构 %s" % name, [context])

        structure_obj = game.StructureManage.get_structure(name)
        if structure_obj is None : return CommandResult(False, s, "不存在结构 %s" % name, [context])

        start = [math.floor(i) for i in start_pos(context)]
        size = [int(i) for i in structure_obj.size]
        height = Constants.DIMENSION_INFO[context.dimension.Identifier]["height"]
        if not(height[0] <= start[1] < height[1]) :
            return CommandResult(False, s, "无法在%s位置加载结构" % (tuple(start), ), [context])

        from ..GameClass.dimension import UnloadedChunksError, UnactiveChunksError
        BlockPermutationClass = game.SimulatorModule.BlockPermutation
        block_palette = structure_obj.block_palette
        block_index = structure_obj.block_index
        placed_count = 0

        for pos_x in range(size[0]) :
            for pos_y in range(size[1]) :
                for pos_z in range(size[2]) :
                    block = block_palette[block_index[(pos_x * size[1] + pos_y) * size[2] + pos_z]]
                    if block is None : continue

                    mirror_x, mirror_z = pos_x, pos_z
                    if mirror in ("x", "xz") : mirror_x = size[0] - 1 - mirror_x
                    if mirror in ("z", "xz") : mirror_z = size[2] - 1 - mirror_z
                    if rotation == "90_degrees" : mirror_x, mirror_z = size[2] - 1 - mirror_z, mirror_x
                    elif rotation == "180_degrees" : mirror_x, mirror_z = size[0] - 1 - mirror_x, size[2] - 1 - mirror_z
                    elif rotation == "270_degrees" : mirror_x, mirror_z = mirror_z, size[0] - 1 - mirror_x

                    target = (start[0] + mirror_x, start[1] + pos_y, start[2] + mirror_z)
                    if not(height[0] <= target[1] < height[1]) : continue
                    if integrity < 100 and random.uniform(0, 100) > integrity : continue      # 完整度：按比例跳过方块
                    try : context.dimension.set_block_permutation(target,
                        BlockPermutationClass(block.name, dict(block.states)))
                    except (UnloadedChunksError, UnactiveChunksError) as chunk_error :
                        return CommandResult(False, s, str(chunk_error), [context])
                    placed_count += 1

        temp = string.Template("已在$pos1加载结构 $name（放置 $count 个方块）").substitute(
            pos1=tuple(start), name=name, count=placed_count)
        return CommandResult(True, s, temp, [context])

    def delete(context:CommandContext, game:MinecraftSimulator, s:str, name:str) :
        if name not in game.StructureManage :
            return CommandResult(False, s, "不存在结构 %s" % name, [context])

        del game.StructureManage[name]
        temp = string.Template("已删除结构 $name").substitute(name=name)
        return CommandResult(True, s, temp, [context])

class stopsound :
    """
    /stopsound <目标: 玩家选择器> [声音ID]

    本模拟器没有声音播放栈，只做"仅模拟"反馈。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        sound_name = pre_process.args.get("Sound_Type", (None, ))[0]
        if sound_name is not None and sound_name not in _game.GameSource.SOUND :
            token_index = pre_process.args_token_index["Sound_Type"][0]
            raise CompileError("不存在的声音ID：%s" % sound_name, token_index[0], token_index[0])

        return functools.partial(cls.run, s=command, entity_get=entity_func)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        player = ", ".join(str(i) for i in entity_list)
        temp = string.Template("以下玩家已停止播放声音:\n$players").substitute(players=player)
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class summon_1_0_0 :
    """
    /summon <实体ID> [坐标] [事件] [名称]        （1.19.70 及更早的语法树）

    该分支不支持 facing 参数（facing 属于 1.19.80 及以上的语法树）。
    """

    VERSION = (0, 0, 0)

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        entity_id = pre_process.args["Entity_Type"][0]
        entity_id = entity_id if entity_id.startswith("minecraft:") else "minecraft:%s" % entity_id
        token_index = pre_process.args_token_index["Entity_Type"][0]
        if entity_id not in _game.GameSource.ENTITY :
            raise CompileError("不存在的实体ID：%s" % entity_id, token_index[0], token_index[0])
        if not _game.GameSource.ENTITY[entity_id]["description"].get("is_summonable", True) :
            raise CompileError("不能被召唤的实体ID：%s" % entity_id, token_index[0], token_index[0])

        entity_name = pre_process.args.get("Entity_Name", (None, ))[0]
        return functools.partial(cls.run, s=command, entity_id=entity_id,
            pos_get = pre_process.positions[0] if pre_process.positions else None,
            entity_event = pre_process.args.get("Entity_Event", (None, ))[0],
            entity_name = Quotation_String_Transfor(entity_name) if entity_name is not None else None)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_id:str, pos_get:PosCallFunction=None,
            entity_event:str=None, entity_name:str=None) :
        summon_pos = [float(i) for i in pos_get(context)] if pos_get is not None else [float(i) for i in context.location]
        entity = __summon_entity__(context, game, entity_id, summon_pos, None, entity_event, entity_name)
        if entity is None : return CommandResult(False, s, "无法在未加载区域召唤实体", [context])

        temp = string.Template("成功召唤了实体 $name").substitute(name=str(entity))
        return CommandResult(True, s, temp, [context]).set_affected_entities([entity])

class summon_1_70_0 :
    """
    /summon <实体ID> [坐标] [旋转|facing <坐标|选择器>] [事件] [名称]     （1.19.80 及以上的语法树）
    """

    VERSION = (1, 19, 80)

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_single_entity_selector
        command = pre_process.parser_result.command
        entity_id = pre_process.args["Entity_Type"][0]
        entity_id = entity_id if entity_id.startswith("minecraft:") else "minecraft:%s" % entity_id
        token_index = pre_process.args_token_index["Entity_Type"][0]
        if entity_id not in _game.GameSource.ENTITY :
            raise CompileError("不存在的实体ID：%s" % entity_id, token_index[0], token_index[0])
        if not _game.GameSource.ENTITY[entity_id]["description"].get("is_summonable", True) :
            raise CompileError("不能被召唤的实体ID：%s" % entity_id, token_index[0], token_index[0])

        facing_get, facing_type = None, None
        if "facing" in pre_process.args.get("Argument", ()) :
            if len(pre_process.positions) > 1 : facing_get, facing_type = pre_process.positions[1], "pos"
            elif pre_process.selectors :
                func_token_index = pre_process.selectors_token_index[-1]
                if not is_single_entity_selector(pre_process.selectors[-1]) :
                    raise CompileError("选择器是非单目标类型", func_token_index[0], func_token_index[0])
                facing_get, facing_type = pre_process.selectors[-1], "entity"
        elif pre_process.rotations : facing_get, facing_type = pre_process.rotations[0], "rotation"

        entity_name = pre_process.args.get("Entity_Name", (None, ))[0]
        return functools.partial(cls.run, s=command, entity_id=entity_id,
            pos_get = pre_process.positions[0] if pre_process.positions else None,
            facing_get = facing_get, facing_type = facing_type,
            entity_event = pre_process.args.get("Entity_Event", (None, ))[0],
            entity_name = Quotation_String_Transfor(entity_name) if entity_name is not None else None)

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_id:str, pos_get:PosCallFunction=None,
            facing_get=None, facing_type:str=None, entity_event:str=None, entity_name:str=None) :
        summon_pos = [float(i) for i in pos_get(context)] if pos_get is not None else [float(i) for i in context.location]
        rotation, error = __facing_angle__(context, game, facing_get, facing_type, summon_pos)
        if error is not None : return CommandResult(False, s, error, [context])

        entity = __summon_entity__(context, game, entity_id, summon_pos, rotation, entity_event, entity_name)
        if entity is None : return CommandResult(False, s, "无法在未加载区域召唤实体", [context])

        temp = string.Template("成功在 $pos 召唤了\n实体 $name $rotate").substitute(
            pos = tuple("%.4f" % float(i) for i in entity.Pos), name=str(entity),
            rotate = tuple(round(float(i), 4) for i in entity.Rotation))
        return CommandResult(True, s, temp, [context]).set_affected_entities([entity])

class tag :
    """
    /tag <目标: 选择器> add <标签>
    /tag <目标: 选择器> remove <标签>
    /tag <目标: 选择器> list

    注：语法树里 list 分支的 token 类型是 Command（会落进 args["Command"]），
        add/remove 分支才是 Argument。
    """

    MAX_TAG_COUNT = 32767

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]

        if "Argument" in pre_process.args :
            tag_name = Quotation_String_Transfor(pre_process.args["Tag"][0])
            if pre_process.args["Argument"][0] == "add" :
                return functools.partial(cls.add, s=command, entity_get=entity_func, tag_name=tag_name)
            return functools.partial(cls.remove, s=command, entity_get=entity_func, tag_name=tag_name)

        return functools.partial(cls.list, s=command, entity_get=entity_func)

    def add(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, tag_name:str) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for entity in entity_list :
            if tag_name in entity.Tags or len(entity.Tags) >= tag.MAX_TAG_COUNT :
                faild_list.append(str(entity)) ; continue
            entity.Tags.add(tag_name)
            success_list.append(str(entity))

        return CommandResult(bool(success_list), s, __result_text__(
            success_list, faild_list, "以下实体成功添加了标签", "以下实体无法添加标签"), [context]
        ).set_affected_entities(entity_list)

    def remove(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, tag_name:str) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        success_list, faild_list = [], []
        for entity in entity_list :
            if tag_name not in entity.Tags :
                faild_list.append(str(entity)) ; continue
            entity.Tags.discard(tag_name)
            success_list.append(str(entity))

        return CommandResult(bool(success_list), s, __result_text__(
            success_list, faild_list, "以下实体成功删除了标签", "以下实体无法删除标签"), [context]
        ).set_affected_entities(entity_list)

    def list(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("$entity -> $tags")
        text = string.Template("以下实体打印标签：\n$success").substitute(
            success = "\n".join(temp.substitute(entity=str(i), tags=", ".join(sorted(i.Tags))) for i in entity_list))
        return CommandResult(True, s, text, [context]).set_affected_entities(entity_list)

class teleport :
    """
    /teleport <坐标> [旋转|facing <坐标|选择器>] [true|false]
    /teleport <坐标> facing <坐标|选择器> [true|false]
    /teleport <目标: 选择器> <坐标> [旋转|facing ...] [true|false]
    /teleport <目标: 选择器> <目的地: 选择器> [true|false]
    /teleport <目的地: 选择器> [true|false]         （传送命令执行者）

    注：模拟器没有传送接口，直接写实体的 Pos / Rotation，并同步维度的实体缓存；
        末位的 true|false（是否进行碰撞检查）会被解析但不生效；
        目的地选择器匹配到多个目标时取第一个（与旧实现 is_single=True 的限流行为一致）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_single_entity_selector
        command = pre_process.parser_result.command
        tokens = pre_process.parser_result.tokens
        selectors, positions, rotations = pre_process.selectors, pre_process.positions, pre_process.rotations

        check = pre_process.args.get("Check_For_Blocks", (None, ))[0]
        check_block = (check == "true") if check is not None else None
        has_facing = "facing" in pre_process.args.get("Argument", ())

        def build_facing(position_count:int, selector_index:int) :
            """返回 (facing_callable, facing_type)。"""
            if not has_facing : return (rotations[0], "rotation") if rotations else (None, None)
            if len(positions) > position_count : return (positions[position_count], "pos")
            if len(selectors) > selector_index :
                func_token_index = pre_process.selectors_token_index[selector_index]
                if not is_single_entity_selector(selectors[selector_index]) :
                    raise CompileError("选择器是非单目标类型", func_token_index[0], func_token_index[0])
                return (selectors[selector_index], "entity")
            return (None, None)

        # 分支一：第一个参数是选择器 —— 既有可能是待传送目标，也有可能是目的地实体
        if tokens[1]["type"] in ("Selector", "Player_Name") :
            victim_func:SelectorCallFunction = selectors[0]
            if positions :
                facing_get, facing_type = build_facing(1, 1)
                return functools.partial(cls.tp_entity_pos, s=command, victim_get=victim_func,
                    pos_get=positions[0], facing_get=facing_get, facing_type=facing_type, check_block=check_block)

            if len(selectors) > 1 :
                return functools.partial(cls.tp_entity_entity, s=command, victim_get=victim_func,
                    destination_get=selectors[1], check_block=check_block)

            return functools.partial(cls.tp_self_entity, s=command, destination_get=victim_func, check_block=check_block)

        # 分支二：第一个参数是坐标 —— 传送命令执行者
        if not positions : raise CompileError("teleport 缺少目标坐标")
        facing_get, facing_type = build_facing(1, 0)
        return functools.partial(cls.tp_self_pos, s=command, pos_get=positions[0],
            facing_get=facing_get, facing_type=facing_type, check_block=check_block)

    def tp_self_pos(context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction,
                    facing_get=None, facing_type:str=None, check_block:bool=None) :
        victim = context.executer
        if not isinstance(victim, Entity) : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        tp_pos = [float(i) for i in pos_get(context)]
        angle, error = __facing_angle__(context, game, facing_get, facing_type, tp_pos)
        if error is not None : return CommandResult(False, s, error, [context])

        __do_teleport__(context.dimension, [victim], tp_pos, angle)
        temp = string.Template("已将下列实体传送至$pos:\n$name").substitute(
            pos = tuple("%.4f" % i for i in tp_pos), name=str(victim))
        return CommandResult(True, s, temp, [context]).set_affected_entities([victim])

    def tp_self_entity(context:CommandContext, game:MinecraftSimulator, s:str, destination_get:SelectorCallFunction,
                       check_block:bool=None) :
        victim = context.executer
        if not isinstance(victim, Entity) : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        destination_list:List[Entity] = destination_get(context, game)
        if not destination_list : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        destination = destination_list[0]
        __do_teleport__(destination.Dimension, [victim],
            [float(i) for i in destination.Pos], [float(i) for i in destination.Rotation])
        temp = string.Template("已将下列实体传送至$pos:\n$name").substitute(
            pos = tuple("%.4f" % float(i) for i in destination.Pos), name=str(victim))
        return CommandResult(True, s, temp, [context]).set_affected_entities([victim])

    def tp_entity_entity(context:CommandContext, game:MinecraftSimulator, s:str, victim_get:SelectorCallFunction,
                         destination_get:SelectorCallFunction, check_block:bool=None) :
        victim_list:List[Entity] = victim_get(context, game)
        if not victim_list : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        destination_list:List[Entity] = destination_get(context, game)
        if not destination_list : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        destination = destination_list[0]
        __do_teleport__(destination.Dimension, victim_list,
            [float(i) for i in destination.Pos], [float(i) for i in destination.Rotation])
        temp = string.Template("已将下列实体传送至$pos:\n$name").substitute(
            pos = tuple("%.4f" % float(i) for i in destination.Pos),
            name = ", ".join(str(i) for i in victim_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(victim_list)

    def tp_entity_pos(context:CommandContext, game:MinecraftSimulator, s:str, victim_get:SelectorCallFunction,
                      pos_get:PosCallFunction, facing_get=None, facing_type:str=None, check_block:bool=None) :
        victim_list:List[Entity] = victim_get(context, game)
        if not victim_list : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        tp_pos = [float(i) for i in pos_get(context)]
        angle, error = __facing_angle__(context, game, facing_get, facing_type, tp_pos)
        if error is not None : return CommandResult(False, s, error, [context])

        __do_teleport__(context.dimension, victim_list, tp_pos, angle)
        temp = string.Template("已将下列实体传送至$pos:\n$name").substitute(
            pos = tuple("%.4f" % i for i in tp_pos), name=", ".join(str(i) for i in victim_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(victim_list)

class tellraw :
    """
    /tellraw <目标: 玩家选择器> <rawtext JSON>

    JSON 由 pre_process.json_and_text 中的 Rawtext_Compiler 编译，运行期得到纯文本。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])
        if not pre_process.json_and_text : raise CompileError("tellraw 缺少 rawtext JSON 参数")

        return functools.partial(cls.run, s=command, entity_get=entity_func, rawtext=pre_process.json_and_text[0])

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, rawtext) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("已为以下玩家显示聊天栏信息：$player\n$msg").substitute(
            player = ", ".join(str(i) for i in entity_list), msg=rawtext(context, game))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class testfor :
    """
    /testfor <目标: 选择器>
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        return functools.partial(cls.run, s=command, entity_get=pre_process.selectors[0])

    def run(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction) :
        entity_list:List[Entity] = entity_get(context, game)
        if not entity_list : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        temp = string.Template("发现了 $count 个实体：$entity").substitute(
            count = len(entity_list), entity = ", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class testforblock :
    """
    /testforblock <坐标> <方块ID> [方块状态|数据值]

    方块条件由 pre_process.blocks 中的 Condition_Block_Compiler 编译成 test_block(permutation) -> bool。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        if not pre_process.positions : raise CompileError("testforblock 缺少坐标参数")
        if not pre_process.blocks : raise CompileError("testforblock 缺少方块参数")

        return functools.partial(cls.run, s=command, pos_get=pre_process.positions[0], block_test=pre_process.blocks[0])

    def run(context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction, block_test:BlockConditionCall) :
        from ..GameClass.dimension import UnloadedChunksError, UnactiveChunksError
        test_pos = [math.floor(i) for i in pos_get(context)]

        height = Constants.DIMENSION_INFO[context.dimension.Identifier]["height"]
        if not(height[0] <= test_pos[1] < height[1]) :
            return CommandResult(False, s, "%s处于世界之外" % (tuple(test_pos), ), [context])

        try : permutation = context.dimension.get_block_permutation(test_pos)
        except UnloadedChunksError :
            return CommandResult(False, s, "起始区域%s为未加载的区块" % (tuple(test_pos), ), [context])
        except UnactiveChunksError :
            return CommandResult(False, s, "起始区域%s为非活跃的区块" % (tuple(test_pos), ), [context])

        if not block_test(permutation) :
            return CommandResult(False, s, "%s方块与目标方块不相同" % (tuple(test_pos), ), [context])

        return CommandResult(True, s, "%s方块测试成功" % (tuple(test_pos), ), [context])

class testforblocks :
    """
    /testforblocks <起点1> <终点1> <目标起点> [masked|all]

    只比较方块 ID 与方块状态（模拟器没有把方块实体的 NBT 暴露成可比较的接口）。
    """

    MAX_VOLUME = 524288

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        if len(pre_process.positions) < 3 : raise CompileError("testforblocks 需要三组坐标")
        return functools.partial(cls.run, s=command, start1=pre_process.positions[0],
            end1=pre_process.positions[1], start2=pre_process.positions[2],
            mask_mode = pre_process.args.get("Model", ("all", ))[0])

    def run(context:CommandContext, game:MinecraftSimulator, s:str, start1:PosCallFunction, end1:PosCallFunction,
            start2:PosCallFunction, mask_mode:Literal["all", "masked"]="all", max_block:int=MAX_VOLUME) :
        from ..GameClass.dimension import UnloadedChunksError, UnactiveChunksError
        start_pos1 = [math.floor(i) for i in start1(context)]
        end_pos1 = [math.floor(i) for i in end1(context)]
        for index in range(3) :
            if start_pos1[index] > end_pos1[index] : start_pos1[index], end_pos1[index] = end_pos1[index], start_pos1[index]
        start_pos2 = [math.floor(i) for i in start2(context)]
        end_pos2 = [start_pos2[index] + end_pos1[index] - start_pos1[index] for index in range(3)]

        height = Constants.DIMENSION_INFO[context.dimension.Identifier]["height"]
        for name, pos in (("起始位置", start_pos1), ("结束位置", end_pos1),
                          ("目标起始位置", start_pos2), ("目标结束位置", end_pos2)) :
            if not(height[0] <= pos[1] < height[1]) :
                return CommandResult(False, s, "%s%s处于世界之外" % (name, tuple(pos)), [context])

        volume = [end_pos1[index] - start_pos1[index] + 1 for index in range(3)]
        if volume[0] * volume[1] * volume[2] > max_block :
            return CommandResult(False, s, "区域大小超过%s个方块" % max_block, [context])

        same_count = 0
        for offset in itertools.product(range(volume[0]), range(volume[1]), range(volume[2])) :
            pos_a = (start_pos1[0] + offset[0], start_pos1[1] + offset[1], start_pos1[2] + offset[2])
            pos_b = (start_pos2[0] + offset[0], start_pos2[1] + offset[1], start_pos2[2] + offset[2])
            try :
                block_a = context.dimension.get_block_permutation(pos_a)
                block_b = context.dimension.get_block_permutation(pos_b)
            except (UnloadedChunksError, UnactiveChunksError) :
                return CommandResult(False, s, "区域%s ~ %s为未加载或非活跃的区块" % (
                    tuple(start_pos1), tuple(end_pos1)), [context])

            if mask_mode == "masked" and block_a.name == "minecraft:air" : continue
            if block_a.name != block_b.name or dict(block_a.states) != dict(block_b.states) :
                return CommandResult(False, s, "区域%s ~ %s内存在不相同的方块" % (
                    tuple(start_pos2), tuple(end_pos2)), [context])
            same_count += 1

        temp = string.Template("在$start ~ $end存在$count个相同方块").substitute(
            start=tuple(start_pos2), end=tuple(end_pos2), count=same_count)
        return CommandResult(same_count > 0, s, temp, [context])

class tickingarea :
    """
    /tickingarea add <起点> <终点> [名称] [true|false]
    /tickingarea add circle <中心> <半径 1~4> [名称] [true|false]
    /tickingarea list [all-dimensions]
    /tickingarea remove <名称|坐标>
    /tickingarea remove_all
    /tickingarea preload <名称|坐标> [true|false]

    数据存放在 MinecraftWorld.TickingArea（TickingAreaManager，最多 10 个），坐标按区块存储。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        argument = pre_process.args["Argument"][0]

        if argument == "add" :
            name = pre_process.args.get("Tickingarea_Name", (None, ))[0]
            name = Quotation_String_Transfor(name) if name is not None else None
            preload = pre_process.args.get("Preload", ("false", ))[0] == "true"
            if pre_process.args.get("Model", (None, ))[0] == "circle" :
                radius = pre_process.args["Radius"][0]
                if not(1 <= radius <= 4) :
                    token_index = pre_process.args_token_index["Radius"][0]
                    raise CompileError("区块半径只能在 1~4 范围内", token_index[0], token_index[0])
                return functools.partial(cls.add_circle, s=command, from_pos=pre_process.positions[0],
                    radius=radius, name=name, preload=preload)
            if len(pre_process.positions) < 2 : raise CompileError("tickingarea add 需要起点与终点坐标")
            return functools.partial(cls.add_area, s=command, from_pos=pre_process.positions[0],
                to_pos=pre_process.positions[1], name=name, preload=preload)

        if argument == "list" :
            return functools.partial(cls.print_area, s=command, print_all=("All_Dimensions" in pre_process.args))

        if argument == "remove_all" :
            return functools.partial(cls.remove_area, s=command, remove_all=True)

        if argument == "remove" :
            if "Tickingarea_Name" in pre_process.args :
                return functools.partial(cls.remove_area, s=command,
                    name=Quotation_String_Transfor(pre_process.args["Tickingarea_Name"][0]))
            return functools.partial(cls.remove_area, s=command, pos_get=pre_process.positions[0])

        if argument == "preload" :
            preload = pre_process.args.get("Preload", (None, ))[0]
            if "Tickingarea_Name" in pre_process.args :
                return functools.partial(cls.preload_set, s=command,
                    name=Quotation_String_Transfor(pre_process.args["Tickingarea_Name"][0]),
                    preload = None if preload is None else (preload == "true"))
            return functools.partial(cls.preload_set, s=command, pos_get=pre_process.positions[0],
                preload = None if preload is None else (preload == "true"))

        raise CompileError("未知的 tickingarea 参数：%s" % argument)

    @staticmethod
    def __find_free_name__(manager) -> str :
        for index in range(manager.MaxAreaCount) :
            name = "Area%s" % index
            if not manager.has_tickingarea(name) : return name
        return None

    @staticmethod
    def __add_area__(context:CommandContext, game:MinecraftSimulator, name:str, creator) :
        """返回 (名称, 错误信息)。"""
        manager = game.MinecraftWorld.TickingArea
        if not manager.has_capacity() : return (None, "常加载区块数量已达到最大值10个")
        if name is not None and manager.has_tickingarea(name) : return (None, "已存在常加载区块 %s" % name)

        if name is None :
            name = tickingarea.__find_free_name__(manager)
            if name is None : return (None, "常加载区块数量已达到最大值10个")

        creator(name)
        return (name, None)

    def add_circle(context:CommandContext, game:MinecraftSimulator, s:str, from_pos:PosCallFunction, radius:int,
                   name:str=None, preload:bool=False) :
        start_pos = [math.floor(i) for i in from_pos(context)]
        def creator(identifier:str) :
            game.MinecraftWorld.TickingArea.create_circle(identifier, context.dimension.Identifier,
                start_pos, radius, preload)
        name, error = tickingarea.__add_area__(context, game, name, creator)
        if error is not None : return CommandResult(False, s, error, [context])

        temp = string.Template("成功添加了常加载区块 $name").substitute(name=name)
        return CommandResult(True, s, temp, [context])

    def add_area(context:CommandContext, game:MinecraftSimulator, s:str, from_pos:PosCallFunction,
                 to_pos:PosCallFunction, name:str=None, preload:bool=False) :
        start_pos = [math.floor(i) for i in from_pos(context)]
        end_pos = [math.floor(i) for i in to_pos(context)]
        for index in range(3) :
            if start_pos[index] > end_pos[index] : start_pos[index], end_pos[index] = end_pos[index], start_pos[index]

        chunk_count = (abs(end_pos[0] // 16 - start_pos[0] // 16) + 1) * (abs(end_pos[2] // 16 - start_pos[2] // 16) + 1)
        if chunk_count > 100 : return CommandResult(False, s, "常加载区块内记录的区块数量大于100个", [context])

        def creator(identifier:str) :
            game.MinecraftWorld.TickingArea.create_square(identifier, context.dimension.Identifier,
                start_pos, end_pos, preload)
        name, error = tickingarea.__add_area__(context, game, name, creator)
        if error is not None : return CommandResult(False, s, error, [context])

        temp = string.Template("成功添加了常加载区块 $name").substitute(name=name)
        return CommandResult(True, s, temp, [context])

    @staticmethod
    def __match_chunk__(area:dict, chunk_pos:Tuple[int, int]) -> bool :
        return area["StartPos"][0] <= chunk_pos[0] <= area["EndPos"][0] and \
               area["StartPos"][1] <= chunk_pos[1] <= area["EndPos"][1]

    def print_area(context:CommandContext, game:MinecraftSimulator, s:str, print_all:bool=False) :
        manager = game.MinecraftWorld.TickingArea
        temp_square = string.Template("维度 $dimension 常加载区块 $name : $pos1 ~ $pos2")
        temp_circle = string.Template("维度 $dimension 常加载区块 $name : 半径 = $radius")

        text_list = []
        for identifier, area in manager :
            if not print_all and area["Dimension"] != context.dimension.Identifier : continue
            if area["AreaType"] == "circle" :
                radius = (area["EndPos"][0] - area["StartPos"][0] - 1) // 2
                text_list.append(temp_circle.substitute(dimension=area["Dimension"], name=identifier, radius=radius))
            else :
                text_list.append(temp_square.substitute(dimension=area["Dimension"], name=identifier,
                    pos1="(%s, %s)" % (area["StartPos"][0], area["StartPos"][1]),
                    pos2="(%s, %s)" % (area["EndPos"][0], area["EndPos"][1])))

        if text_list : return CommandResult(True, s, string.Template("$len 个常加载区块正在运行：\n$detial").substitute(
            len=len(text_list), detial="\n".join(text_list)), [context])
        return CommandResult(True, s, string.Template("$len 个常加载区块正在运行").substitute(len=len(text_list)), [context])

    def remove_area(context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction=None,
                    name:str=None, remove_all:bool=None) :
        manager = game.MinecraftWorld.TickingArea
        remove_list = []

        if pos_get is not None :
            start_pos = [math.floor(i) for i in pos_get(context)]
            chunk_pos = (start_pos[0] // 16, start_pos[2] // 16)
            for identifier, area in manager :
                if tickingarea.__match_chunk__(area, chunk_pos) : remove_list.append(identifier)
            if not remove_list :
                return CommandResult(False, s, "%s 没有记录的常加载区块" % (tuple(start_pos), ), [context])

        if name is not None :
            if not manager.has_tickingarea(name) :
                return CommandResult(False, s, "不存在常加载区块 %s" % name, [context])
            remove_list.append(name)

        if remove_all : remove_list.extend([identifier for identifier, _ in manager])

        for identifier in remove_list : manager.remove_tickingarea(identifier)
        temp = string.Template("已移除常加载区块：$name").substitute(name=", ".join(remove_list))
        return CommandResult(True, s, temp, [context])

    def preload_set(context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction=None,
                    name:str=None, preload:bool=None) :
        manager = game.MinecraftWorld.TickingArea
        area_list = []

        if pos_get is not None :
            start_pos = [math.floor(i) for i in pos_get(context)]
            chunk_pos = (start_pos[0] // 16, start_pos[2] // 16)
            for identifier, area in manager :
                if tickingarea.__match_chunk__(area, chunk_pos) : area_list.append(identifier)
            if not area_list :
                return CommandResult(False, s, "%s 没有记录的常加载区块" % (tuple(start_pos), ), [context])

        if name is not None :
            if not manager.has_tickingarea(name) :
                return CommandResult(False, s, "不存在常加载区块 %s" % name, [context])
            area_list.append(name)

        if preload is not None :
            for identifier, area in manager :
                if identifier in area_list : area["Preload"] = preload
            temp = string.Template("已修改常加载区块的预加载：$name").substitute(name=", ".join(area_list))
            return CommandResult(True, s, temp, [context])

        temp = string.Template("常加载区块 $name 的预加载值为 $value")
        text_list = [temp.substitute(name=identifier, value=bool(area["Preload"]))
                     for identifier, area in manager if identifier in area_list]
        return CommandResult(True, s, "\n".join(text_list), [context])

class time :
    """
    /time add <刻数>
    /time query <daytime|gametime|day>
    /time set <day|noon|sunrise|sunset|night|midnight|刻数>

    数据存放在 MinecraftWorld.Time（TimeManager）。
    """

    TIME_OF_DAY = ("day", "noon", "sunrise", "sunset", "night", "midnight")

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        model = pre_process.args["Time_Model"][0]

        if model == "query" :
            return functools.partial(cls.query, s=command, mode=pre_process.args["Time_Type"][0])
        if model == "add" :
            return functools.partial(cls.add, s=command, value=pre_process.args["Amount"][0])
        if "Time_Int" in pre_process.args :
            return functools.partial(cls.set, s=command, value=pre_process.args["Time_Int"][0])
        return functools.partial(cls.set, s=command, value=pre_process.args["Time"][0])

    def query(context:CommandContext, game:MinecraftSimulator, s:str, mode:Literal["daytime", "gametime", "day"]) :
        time_manager = game.MinecraftWorld.Time
        if mode == "daytime" : value = time_manager.get_time_of_day()
        elif mode == "day" : value = time_manager.get_day()
        else : value = time_manager.get_gametime()

        temp = string.Template("查询到 $mode 的值为 $value").substitute(mode=mode, value=value)
        return CommandResult(True, s, temp, [context])

    def add(context:CommandContext, game:MinecraftSimulator, s:str, value:int) :
        time_manager = game.MinecraftWorld.Time
        time_manager.set_time(int(time_manager.CurrentTime) + int(value))
        temp = string.Template("时间增加了 $value 刻，当前时刻为 $now").substitute(
            value=value, now=time_manager.get_time_of_day())
        return CommandResult(True, s, temp, [context])

    def set(context:CommandContext, game:MinecraftSimulator, s:str, value:Union[int, str]) :
        time_manager = game.MinecraftWorld.Time
        if isinstance(value, int) :
            # 与游戏一致：设置的是当天的时间点，而不是整个世界总刻数
            time_manager.set_time(int(time_manager.get_day()) * int(time_manager.TicksPerDay) + int(value))
        else : time_manager.set_time_of_day(value)

        temp = string.Template("将时间设定为 $value").substitute(
            value = time_manager.get_time_of_day() if isinstance(value, int) else value)
        return CommandResult(True, s, temp, [context])

class titleraw :
    """
    /title <目标: 玩家选择器> clear|reset
    /title <目标: 玩家选择器> times <淡入> <停留> <淡出>
    /title <目标: 玩家选择器> title|subtitle|actionbar <文本或rawtext JSON>
    /titleraw <目标: 玩家选择器> title|subtitle|actionbar <rawtext JSON>

    文本参数由 pre_process.json_and_text 编译（title 是 SelectorMsg，titleraw 是 Rawtext）。
    注：语法树里 times 的第三、四个参数都被命名为 Fade_Out，因此按位置取用。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        model = pre_process.args["Model"][0]
        if model in ("clear", "reset") :
            return functools.partial(cls.clear_or_reset, s=command, entity_get=entity_func, mode=model)
        if model == "times" :
            return functools.partial(cls.set_time, s=command, entity_get=entity_func,
                fade_in = pre_process.args["Fade_In"][0], stay = pre_process.args["Fade_Out"][0],
                fade_out = pre_process.args["Fade_Out"][1])
        if not pre_process.json_and_text : raise CompileError("缺少标题文本参数")

        return functools.partial(cls.display, s=command, entity_get=entity_func, type1=model,
            text=pre_process.json_and_text[0])

    def clear_or_reset(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
                       mode:Literal["clear", "reset"]) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        line = "已为以下玩家清除所有显示的标题：$player" if mode == "clear" else "已为以下玩家重置所有的标题设置：$player"
        temp = string.Template(line).substitute(player=", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

    def set_time(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
                 fade_in:int=0, stay:int=0, fade_out:int=0) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("已为以下玩家设置标题淡入/停留/淡出时间为 $in/$stay/$out：$player").substitute(
            **{"in":fade_in}, stay=stay, out=fade_out, player=", ".join(str(i) for i in entity_list))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

    def display(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction,
                type1:Literal["title", "subtitle", "actionbar"], text) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        temp = string.Template("已为以下玩家设置 $type1 标题：$player\n$msg").substitute(
            type1=type1, player=", ".join(str(i) for i in entity_list), msg=text(context, game))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class toggledownfall :
    """
    /toggledownfall

    在 clear 与 rain/thunder 之间切换 MinecraftWorld.WeatherType。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        return functools.partial(cls.change_weather, s=pre_process.parser_result.command)

    def change_weather(context:CommandContext, game:MinecraftSimulator, s:str) :
        world = game.MinecraftWorld
        if world.WeatherType == "clear" : world.WeatherType = random.choice(("rain", "thunder"))
        else : world.WeatherType = "clear"

        temp = string.Template("将天气更改为 $weather").substitute(weather=world.WeatherType)
        return CommandResult(True, s, temp, [context])

class volumearea :
    """
    /volumearea add <功能域ID> <起点> <终点> <名称>
    /volumearea list [all-dimensions]
    /volumearea remove <名称|坐标>
    /volumearea remove_all

    注：模拟器没有功能域（volume area）子系统，这里记录在 MinecraftWorld.VolumeArea 上，
        只做模拟反馈，不参与存档序列化，也不校验功能域 ID 是否存在。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        argument = pre_process.args["Argument"][0]

        if argument == "add" :
            if len(pre_process.positions) < 2 : raise CompileError("volumearea add 需要起点与终点坐标")
            return functools.partial(cls.add_area, s=command, volume_id=pre_process.args["Identifier"][0],
                from_pos=pre_process.positions[0], to_pos=pre_process.positions[1],
                name=Quotation_String_Transfor(pre_process.args["Volumearea_Name"][0]))

        if argument == "list" :
            return functools.partial(cls.print_area, s=command, print_all=("All_Dimensions" in pre_process.args))

        if argument == "remove_all" :
            return functools.partial(cls.remove_area, s=command, remove_all=True)

        if "Volumearea_Name" in pre_process.args :
            return functools.partial(cls.remove_area, s=command,
                name=Quotation_String_Transfor(pre_process.args["Volumearea_Name"][0]))
        return functools.partial(cls.remove_area, s=command, pos_get=pre_process.positions[0])

    @staticmethod
    def __manager__(game:MinecraftSimulator) -> dict :
        world = game.MinecraftWorld
        if not hasattr(world, "VolumeArea") : world.VolumeArea = {}
        return world.VolumeArea

    def add_area(context:CommandContext, game:MinecraftSimulator, s:str, volume_id:str, from_pos:PosCallFunction,
                 to_pos:PosCallFunction, name:str) :
        volume_area = volumearea.__manager__(game)
        if name in volume_area :
            return CommandResult(False, s, "已存在功能域 %s" % name, [context])

        start_pos = [math.floor(i) for i in from_pos(context)]
        end_pos = [math.floor(i) for i in to_pos(context)]
        for index in range(3) :
            if start_pos[index] > end_pos[index] : start_pos[index], end_pos[index] = end_pos[index], start_pos[index]

        volume_area[name] = {"dimension":context.dimension.Identifier, "id":volume_id,
            "effect_area":[(start_pos[0], start_pos[2]), (end_pos[0], end_pos[2])]}
        temp = string.Template("成功添加了功能域 $name").substitute(name=name)
        return CommandResult(True, s, temp, [context])

    def print_area(context:CommandContext, game:MinecraftSimulator, s:str, print_all:bool=False) :
        volume_area = volumearea.__manager__(game)
        temp1 = string.Template("维度 $dimension 功能域 $name : $pos1 ~ $pos2")

        text_list = []
        for identifier, area in volume_area.items() :
            if not print_all and area["dimension"] != context.dimension.Identifier : continue
            text_list.append(temp1.substitute(dimension=area["dimension"], name=identifier,
                pos1=tuple(area["effect_area"][0]), pos2=tuple(area["effect_area"][1])))

        if text_list : return CommandResult(True, s, string.Template("$len 个功能域正在运行：\n$detial").substitute(
            len=len(text_list), detial="\n".join(text_list)), [context])
        return CommandResult(True, s, string.Template("$len 个功能域正在运行").substitute(len=len(text_list)), [context])

    def remove_area(context:CommandContext, game:MinecraftSimulator, s:str, pos_get:PosCallFunction=None,
                    name:str=None, remove_all:bool=None) :
        volume_area = volumearea.__manager__(game)
        remove_list = []

        if pos_get is not None :
            start_pos = [math.floor(i) for i in pos_get(context)]
            for identifier, area in volume_area.items() :
                if not(area["effect_area"][0][0] <= start_pos[0] <= area["effect_area"][1][0]) : continue
                if not(area["effect_area"][0][1] <= start_pos[2] <= area["effect_area"][1][1]) : continue
                remove_list.append(identifier)
            if not remove_list :
                return CommandResult(False, s, "%s 没有可以记录的功能域" % (tuple(start_pos), ), [context])

        if name is not None :
            if name not in volume_area : return CommandResult(False, s, "不存在功能域 %s" % name, [context])
            remove_list.append(name)

        if remove_all : remove_list.extend(list(volume_area))
        for identifier in remove_list : del volume_area[identifier]

        temp = string.Template("已移除功能域：$name").substitute(name=", ".join(remove_list))
        return CommandResult(True, s, temp, [context])

class tell :
    """
    /tell|msg|w <目标: 玩家选择器> <消息>

    消息里的选择器由 pre_process.json_and_text 中的 SelectorMsg_Compiler 编译。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        entity_func:SelectorCallFunction = pre_process.selectors[0]
        func_token_index = pre_process.selectors_token_index[0]
        if not is_player_only_selector(entity_func) :
            raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])
        if not pre_process.json_and_text : raise CompileError("tell 缺少消息参数")

        return functools.partial(cls.send_msg, s=command, entity_get=entity_func, msg=pre_process.json_and_text[0])

    def send_msg(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction, msg) :
        entity_list:List[Player] = [i for i in entity_get(context, game) if isinstance(i, Player)]
        if not entity_list : return CommandResult(False, s, "无选择器匹配的实体", [context])

        executer = context.executer
        temp = string.Template("$player1 向以下玩家发送了悄悄话：\n$player2\n$msg").substitute(
            player1 = str(executer) if isinstance(executer, Entity) else "服务器",
            player2 = ", ".join(str(i) for i in entity_list), msg=msg(context, game))
        return CommandResult(True, s, temp, [context]).set_affected_entities(entity_list)

class weather :
    """
    /weather clear|rain|thunder [持续刻数]
    /weather query

    天气存放在 MinecraftWorld.WeatherType；持续刻数记录在 MinecraftWorld.WeatherDuration（新增字段，不参与存档）。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        command = pre_process.parser_result.command
        argument = pre_process.args["Argument"][0]
        if argument == "query" : return functools.partial(cls.query, s=command)

        return functools.partial(cls.set, s=command, weather_name=argument,
            duration = pre_process.args.get("Duration", (None, ))[0])

    def query(context:CommandContext, game:MinecraftSimulator, s:str) :
        temp = string.Template("当前的天气：$weather").substitute(weather=game.MinecraftWorld.WeatherType)
        return CommandResult(True, s, temp, [context])

    def set(context:CommandContext, game:MinecraftSimulator, s:str, weather_name:Literal["clear", "rain", "thunder"],
            duration:int=None) :
        world = game.MinecraftWorld
        world.WeatherType = weather_name
        world.WeatherDuration = int(random.randint(10000, 30000) if duration is None else duration)

        temp = string.Template("将天气更改为 $weather（持续 $duration 刻）").substitute(
            weather=world.WeatherType, duration=world.WeatherDuration)
        return CommandResult(True, s, temp, [context])

class xp :
    """
    /xp <数量> [目标: 玩家选择器]
    /xp <数量>L [目标: 玩家选择器]

    经验等级存放在 Player.LevelInfo（LevelManager：Level / Progress / add_experience / set_level）。
    注：语法树的 Amount 用了 Int("Amount","L","l")，单位字符 L 不会进入 token，
        只能从 parser_result.command 的原文里按 token 的字符区间判断。
    """

    @classmethod
    def __compiler__(cls, _game:MinecraftSimulator, pre_process:CommandPerProcess) :
        from .selector import is_player_only_selector
        command = pre_process.parser_result.command
        XP_Value = pre_process.args.get("Amount", (None, ))[0]
        XPLevelValue = pre_process.args.get("AmountLevel", (None, ))[0]

        entity_func:SelectorCallFunction = None
        if pre_process.selectors :
            entity_func = pre_process.selectors[0]
            func_token_index = pre_process.selectors_token_index[0]
            if not is_player_only_selector(entity_func) :
                raise CompileError("选择器是非玩家类型", func_token_index[0], func_token_index[0])

        return functools.partial(cls.modify_level if XP_Value is None else cls.modify_point, s=command,
            entity_get=entity_func, value=value)

    def modify_level(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction=None,
                     value:int=0) :
        entity_list = __target_list__(context, game, entity_get)
        player_list:List[Player] = [i for i in entity_list if isinstance(i, Player)]
        if not player_list : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        for player in player_list : player.LevelInfo.set_level(max(0, int(player.LevelInfo.Level) + int(value)))

        temp = string.Template("$player 的等级变为 $value")
        text = string.Template("以下玩家的经验值发生变化：\n$msg").substitute(
            msg = "\n".join(temp.substitute(player=str(i), value=i.LevelInfo.Level) for i in player_list))
        return CommandResult(True, s, text, [context]).set_affected_entities(player_list)

    def modify_point(context:CommandContext, game:MinecraftSimulator, s:str, entity_get:SelectorCallFunction=None,
                     value:int=0) :
        entity_list = __target_list__(context, game, entity_get)
        player_list:List[Player] = [i for i in entity_list if isinstance(i, Player)]
        if not player_list : return CommandResult(False, s, "没有与目标选择器匹配的目标", [context])

        for player in player_list : player.LevelInfo.add_experience(value)

        temp = string.Template("$player 的等级变为 $value1 : $value2")
        text = string.Template("以下玩家的经验值发生变化：\n$msg").substitute(
            msg = "\n".join(temp.substitute(player=str(i), value1=i.LevelInfo.Level,
                value2=round(float(i.LevelInfo.Progress), 4)) for i in player_list))
        return CommandResult(True, s, text, [context]).set_affected_entities(player_list)


