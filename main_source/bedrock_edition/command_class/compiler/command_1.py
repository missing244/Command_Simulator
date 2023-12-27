from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction
from . import Selector,CompileError,CommandParser,Quotation_String_transfor_1,ID_transfor
import functools,string,random,re,math,itertools
from typing import Dict,Union,List,Tuple,Literal,Callable


def replace_str(base:str, start:int, end:int, replace:str) -> str:
    return "".join([ base[:start] , replace , base[end:] ])

Selector_Parser = CommandParser.ParserSystem.Command_Parser(
    CommandParser.SpecialMatch.Command_Root().add_leaves(
        *CommandParser.SpecialMatch.BE_Selector_Tree(
            CommandParser.BaseMatch.AnyMsg("Msg").add_leaves(CommandParser.BaseMatch.END_NODE)
        )
    )
)






class ability :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if index >= token_list.__len__() : return functools.partial(cls.query_all, entity_get=entity_func)
        
        ability_id = token_list[index]["token"].group() ; index += 1
        if index >= token_list.__len__() : return functools.partial(cls.query, entity_get=entity_func, ability_id=ability_id)
        
        value = token_list[index]["token"].group()
        return functools.partial(cls.set, entity_get=entity_func, ability_id=ability_id, set_value=value)

    def query_all(execute_var:COMMAND_CONTEXT, entity_get:functools.partial) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        temp = string.Template("玩家 $player 的能力: worldbuilder=$t1 mayfly=$t2 mute=$t3")
        return Response.Response_Template("查询到以下玩家的能力：\n$result", 1, len(entity_list)).substitute(
        result = "\n".join((
            temp.substitute(player=ID_tracker(i), t1=i.Ability['worldbuilder'],
            t2=i.Ability['mayfly'], t3=i.Ability['mute']) for i in entity_list
        )))

    def query(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, ability_id:str) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        temp = string.Template("玩家 $player 的能力: $abi = $value")
        return Response.Response_Template("查询到以下玩家的能力：\n$result", 1, len(entity_list)).substitute(
            result = "\n".join((
            temp.substitute(player=ID_tracker(i), abi=ability_id, value=i.Ability[ability_id]) for i in entity_list
        )))

    def set(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, ability_id:str, set_value:Literal["true","false"]) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        for entity in entity_list : entity.Ability[ability_id] = ("false","true").index(set_value)
        return Response.Response_Template("以下玩家的 $abi 能力设置为 $value ：\n$players", 1, len(entity_list)).substitute(
            abi=ability_id, value=set_value, players=", ".join( (ID_tracker(i) for i in entity_list) )
        )


class alwaysday :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index = 1
        if index >= token_list.__len__() : return functools.partial(cls.query, game=_game)
        
        value = token_list[index]["token"].group()
        return functools.partial(cls.set, game=_game, set_value=value)

    def query(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread) :
        return Response.Response_Template("游戏规则 dodaylightcycle 为 $value", 1, 1).substitute(
            value = game.minecraft_world.dodaylightcycle
        )

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, set_value:Literal["true","false"]) :
        game.minecraft_world.dodaylightcycle = bool(("false","true").index(set_value))
        game.minecraft_world.day_time = np.int32(6000)
        return Response.Response_Template("游戏规则 dodaylightcycle 已变更为 $value", 1, 1).substitute(
            value = game.minecraft_world.dodaylightcycle
        )


class camera :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if token_list[index]["token"].group() == "clear" : return functools.partial(cls.clear, entity_get=entity_func)
        elif token_list[index]["token"].group() == "fade" : 
            index += 1
            if index >= token_list.__len__() : return functools.partial(cls.fade_default, entity_get=entity_func)
            elif token_list[index]["token"].group() == "color" : 
                rgb_color= []
                for i in range(1,4,1) :
                    color_re = token_list[index+i]["token"]
                    if not (0 <= int(color_re.group()) <= 255) : raise CompileError("rgb颜色含有非法参数", pos=(color_re.start(),color_re.end()))
                    rgb_color.append(color_re.group())
                return functools.partial(cls.fade_color, entity_get=entity_func, rgb=rgb_color)
            elif token_list[index]["token"].group() == "time" : 
                fade_time= []
                for i in range(1,4,1) :
                    color_re = token_list[index+i]["token"]
                    if not (0 <= float(color_re.group()) <= 10) : raise CompileError("淡入淡出时间含有非法参数", pos=(color_re.start(),color_re.end()))
                    fade_time.append(color_re.group())
                index += 4
                if index >= token_list.__len__() : return functools.partial(cls.fade_time, entity_get=entity_func, time=fade_time)
                rgb_color= []
                for i in range(1,4,1) :
                    color_re = token_list[index+i]["token"]
                    if not (0 <= float(color_re.group()) <= 255) : raise CompileError("rgb颜色含有非法参数", pos=(color_re.start(),color_re.end()))
                    rgb_color.append(color_re.group())
                return functools.partial(cls.fade_time_color, entity_get=entity_func, time=fade_time, rgb=rgb_color)
        elif token_list[index]["token"].group() == "set" : 
            index += 2 ; perset_name = token_list[index-1]["token"].group()
            if perset_name not in Constants.GAME_DATA["camera_perset"] :
                raise CompileError("无法在相机预设ID内寻找到 %s" % perset_name, pos=(token_list[index-1]["token"].start(),token_list[index-1]["token"].end()))
            if index >= token_list.__len__() or token_list[index]["token"].group() == "default" : 
                return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
            elif token_list[index]["token"].group() == "ease" :
                index += 3
                if index >= token_list.__len__() or token_list[index]["token"].group() == "default" :
                    return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
                elif token_list[index]["token"].group() == "facing" and token_list[index+1]["type"] in ("Selector","Player_Name") :
                    _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+1, is_single=True)
                    return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name, facing_entity_get=facing_entity_func)
                elif token_list[index]["token"].group() == "pos" :
                    if (index+4) >= token_list.__len__() : 
                        return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
                    elif token_list[index+4]["token"].group() == "facing" and token_list[index+5]["type"] in ("Selector","Player_Name") :
                        _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+5, is_single=True)
                        return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name, facing_entity_get=facing_entity_func)
                    else : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
                else : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
            elif token_list[index]["token"].group() == "facing" and token_list[index+1]["type"] in ("Selector","Player_Name") :
                _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+1, is_single=True)
                return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name, facing_entity_get=facing_entity_func)
            elif token_list[index]["token"].group() == "pos" :
                if (index+4) >= token_list.__len__() : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
                elif token_list[index+4]["token"].group() == "facing" and token_list[index+5]["type"] in ("Selector","Player_Name") :
                    _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+5, is_single=True)
                    return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name, facing_entity_get=facing_entity_func)
                else : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
            else : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)

    def clear(execute_var:COMMAND_CONTEXT, entity_get:functools.partial) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头状态清除 ：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def fade_default(execute_var:COMMAND_CONTEXT, entity_get:functools.partial) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头设置为黑幕效果 ：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def fade_color(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, rgb:List[int]) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头颜色设置为$rgb：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) ), rgb=tuple(rgb)
        )
    
    def fade_time(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, time:Tuple[int]) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头时间设置为$time：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) ), time=tuple(time)
        )
    
    def fade_time_color(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, time:Tuple[int], rgb:List[int]) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头时间和颜色设置为$time,$rgb：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) ), time=tuple(time), rgb=tuple(rgb)
        )

    def set_camera(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, camera_id:str, facing_entity_get:functools.partial=None) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if isinstance(facing_entity_get, functools.partial) :
            facing_entity_list = entity_get(execute_var)
            if isinstance(facing_entity_list, Response.Response_Template) : return facing_entity_list

        return Response.Response_Template("将以下玩家的摄像头设置为$id：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) ), id=camera_id
        )


class camerashake :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group() == "stop" :
            if 2 >= token_list.__len__() : return cls.stop
            index,entity_func = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
            return functools.partial(cls.stop, entity_get=entity_func)
        else :
            index,entity_func = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
            if index < token_list.__len__() and not(0 <= float(token_list[index]["token"].group()) <= 4) :
                raise CompileError("摄像头摇晃幅度参数超过0 ~ 4的范围", pos=(token_list[index]["token"].start(),token_list[index]["token"].end()))
            return functools.partial(cls.add, entity_get=entity_func)

    def stop(execute_var:COMMAND_CONTEXT, entity_get:functools.partial=None) :
        entity_list = entity_get(execute_var) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if entity_get is None and not isinstance(entity_list[0], BaseNbtClass.entity_nbt) : 
            if entity_list[0].Identifier != "minecraft:player" : return Response.Response_Template("没有与目标选择器匹配的目标").substitute({})
        return Response.Response_Template("以下玩家的摄像头停止摇晃：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def add(execute_var:COMMAND_CONTEXT, entity_get:functools.partial) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("以下玩家的摄像头进行摇晃：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )


class clear :
    
    def clear_items(entity:BaseNbtClass.entity_nbt, container:Literal["Armor","HotBar","Inventory","Weapon"],
                    name:str=None, data:int=-1, max_count:int=2147483647) :
        clear_count = 0 ; clear_list = getattr(entity, container) ; fill_blank = {}
        for index,item in enumerate(clear_list) :
            if not isinstance(item, BaseNbtClass.item_nbt) : continue
            if container == "Weapon" and index == 0 : continue

            if name is None : clear_count += int(item.Count) ; clear_list[index] = fill_blank ; continue
            if item.Identifier != name : continue
            if data != -1 and item.Identifier in Constants.GAME_DATA["damage_tool"] and item.tags["damage"] != data : continue
            elif data != -1 and item.Damage["damage"] != data : continue

            if max_count == 0 : clear_count += int(item.Count) ; continue
            if clear_count < max_count :              #Case1: The max clear num is enough to delete this item
                m1 = min(item.Count, max_count - clear_count)
                clear_count += int(m1)
                if item.Count == m1 : clear_list[index] = fill_blank
                else : item.Count -= m1
                if clear_count >= max_count : break
        return clear_count

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if 2 >= len(token_list) : raise NotImplementedError("暂未实现不带目标选择器运行该命令")
        if index >= len(token_list) : return functools.partial(cls.clear_specific)

        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if index >= len(token_list) : return functools.partial(cls.clear_specific, entity_get=entity_func)
        
        item_name = ID_transfor(token_list[index]["token"].group())
        if item_name not in _game.minecraft_ident.items:
            raise CompileError("不存在的物品ID：%s" % item_name,pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        else : index += 1
        if index >= len(token_list) : return functools.partial(cls.clear_specific, entity_get=entity_func, name=item_name)

        #Item data value
        item_damage = int(token_list[index]["token"].group())
        if not(-1 <= item_damage <= 32767):    #Invalid number
            raise CompileError("%s 不是一个有效的数据值" % item_damage, pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        else : index += 1
        if index >= len(token_list) : return functools.partial(cls.clear_specific, entity_get=entity_func, 
            name=item_name, data=item_damage)

        #The amount of the item which needs to clear
        item_max_clear = int(token_list[index]["token"].group())
        if not(0 <= item_max_clear <= 2147483647): 
            raise CompileError("%s 不是一个有效的最大数量" % item_max_clear, pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.clear_specific, entity_get=entity_func, 
            name=item_name, data=item_damage, max_count=item_max_clear)

    def clear_specific(execute_var:COMMAND_CONTEXT, entity_get:Callable=None, name:str=None, data:int=-1, max_count:int=2147483647) :
        entity_list = entity_get(execute_var) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if entity_get is None and not isinstance(entity_list[0], BaseNbtClass.entity_nbt) : 
            if entity_list[0].Identifier != "minecraft:player" : return Response.Response_Template("没有与目标选择器匹配的目标").substitute({})
        for entity in entity_list :
            clear.clear_items(entity, "HotBar", name, data, max_count)
            clear.clear_items(entity, "Inventory", name, data, max_count)
            clear.clear_items(entity, "Armor", name, data, max_count)
            clear.clear_items(entity, "Weapon", name, data, max_count)


class clearspawnpoint :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if 2 >= token_list.__len__() : return functools.partial(cls.clear, game=_game)
        _, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        return functools.partial(cls.clear, game=_game, entity_get=entity_func)

    def clear(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:functools.partial=None) :
        entity_list = entity_get(execute_var) if entity_get else []
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        for entity in entity_list:
            entity.SpawnPoint[0] = game.minecraft_world.world_spawn_x
            entity.SpawnPoint[1] = game.minecraft_world.world_spawn_y
            entity.SpawnPoint[2] = game.minecraft_world.world_spawn_z

        return Response.Response_Template("$players 的生成点已清除", len(entity_list), 1).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list)
        )


class clone :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        if 1: raise NotImplementedError("暂未实现该命令")

        poses = (
            token_list[1]["token"].group(),
            token_list[2]["token"].group(),
            token_list[3]["token"].group(),
            token_list[4]["token"].group(),
            token_list[5]["token"].group(),
            token_list[6]["token"].group(),
            token_list[7]["token"].group(),
            token_list[8]["token"].group(),
            token_list[9]["token"].group(),
        )
        lst_len = token_list.__len__()

        if lst_len == 10: return functools.partial(cls.non_fliter, game=_game, poses=poses)

        token_10 = token_list[10]["token"].group() #lst_len >= 11; index = 10
        if token_10 == "flitered":
            clone_mode      = token_list[11]["token"].group()
            tile_name       = token_list[12]["token"].group()
            block_states    = token_list[13]["token"].group()
            return functools.partial(cls.fliter, game=_game, poses=poses, clone_mode=clone_mode, tile_name=tile_name, block_states=block_states)
        else:
            index = 10
            mask_mode = token_10; index += 1
            if index >= lst_len: return functools.partial(cls.non_fliter, game=_game, poses=poses, mask_mode=mask_mode)

            clone_mode = token_list[index]["token"].group()
            return functools.partial(cls.non_fliter, game=_game, poses=poses, mask_mode=mask_mode, clone_mode=clone_mode)

    def fliter(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, poses:tuple, clone_mode:str, tile_name:str, block_states:str) :
        return None

    def non_fliter(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, poses:tuple, mask_mode:str="replace", clone_mode:str="normal") :
        return None


class damage:

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if 1: raise NotImplementedError("暂未实现该命令")
        lst_len = token_list.__len__()

        index, entity_hurt = Selector.Selector_Compiler(_game, token_list, 1)
        
        amount = int(token_list[index]["token"].group()); index += 1
        if index >= lst_len : return functools.partial(cls.no_cause, game=_game, entity_hurt=entity_hurt, amount=amount)
        
        cause = int(token_list[index]["token"].group()); index += 1
        if index >= lst_len : return functools.partial(cls.has_cause_without_entity, game=_game, entity_hurt=entity_hurt, amount=amount, cause=cause)
        
        _, entity_damager = Selector.Selector_Compiler(_game, token_list, index+1) # Skip reading the word 'entity', so index+1
        return functools.partial(cls.has_cause_with_entity, game=_game, entity_hurt=entity_hurt, amount=amount, cause=cause, entity_damager=entity_damager)

    def no_cause(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_hurt:functools.partial, amount:int):
        entity_list = entity_hurt(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return None
    
    def has_cause_without_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_hurt:functools.partial, amount:int, cause:str):
        entity_list = entity_hurt(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return None
    
    def has_cause_with_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_hurt:functools.partial, amount:int, cause:str, entity_damager:functools.partial):
        entity_list = entity_hurt(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return None


class dialogue:

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        if 1: raise NotImplementedError("暂未实现该命令中的判断选择器是否取出单个实体的功能")

        lst_len = token_list.__len__()

        open_or_change = token_list[1]["token"].group()

        _, entity_npc = Selector.Selector_Compiler(_game, token_list, 2, is_npc=True, is_single=True)

        if open_or_change == "open":
            _, entity_player = Selector.Selector_Compiler(_game, token_list, 3, is_player=True)
            if lst_len == 4 : return functools.partial(cls.open, game=_game, entity_npc=entity_npc, entity_player=entity_player)

            scene_name = token_list[4]["token"].group()
            return functools.partial(cls.open, game=_game, entity_npc=entity_npc, entity_player=entity_player, scene_name=scene_name)

        elif open_or_change == "change":
            scene_name = token_list[3]["token"].group()
            if lst_len == 4 : return functools.partial(cls.open, game=_game, entity_npc=entity_npc, scene_name=scene_name)

            _, entity_player = Selector.Selector_Compiler(_game, token_list, 4, is_player=True, is_single=True)
            return functools.partial(cls.open, game=_game, entity_npc=entity_npc, scene_name=scene_name, entity_player=entity_player)
        
    def open(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_npc:functools.partial, entity_player:functools.partial, scene_name:str=None) :
        
        entity_list = entity_player(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        
        result_count = len(entity_list)
        success_count = int(bool(result_count))

        if scene_name in game.minecraft_ident.dialogues or scene_name is None: 
            return Response.Response_Template("对话已发送至 $players", success_count, result_count).substitute(
                players=", ".join(ID_tracker(i) for i in entity_list)
            )
        else:
            return Response.Response_Template("引用了无效的场景", 0, 0).substitute(
                players=", ".join(ID_tracker(i) for i in entity_list)
            )
    
    def change(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_npc:functools.partial, scene_name:str, entity_player:functools.partial=None) :
        
        entity_list = entity_player(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        
        result_count = len(entity_list)
        success_count = int(bool(result_count))

        if scene_name in game.minecraft_ident.dialogues: 
            return Response.Response_Template("已更改 $players 的对话", success_count, result_count).substitute(
                players=", ".join(ID_tracker(i) for i in entity_list)
            )
        elif entity_player is None:
            return Response.Response_Template("已更改所有玩家的对话", success_count, result_count).substitute()
        else:
            return Response.Response_Template("引用了无效的场景", 0, 0).substitute(
                players=", ".join(ID_tracker(i) for i in entity_list)
            )


class difficulty :
    # DIFFICULTY = [
    #     "peaceful", "0",    "p"
    #     "easy",     "1",    "e",
    #     "normal",   "2",    "n",
    #     "hard",     "3",    "h",
    # ]
    DIFFICULTY = Constants.GAME_DATA["difficult_type"]

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        difficulty_data = cls.DIFFICULTY
        token = token_list[1]["token"]
        difficulty = cls.DIFFICULTY.index(token.group()) // 3   #The var 'difficulty' is the numeric id of difficulty
        difficulty_name = difficulty_data[0::3][difficulty]     #Get the column 0 and get the full name of difficulty
        return functools.partial(cls.set, game=_game, difficulty=difficulty, difficulty_name=difficulty_name)

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, difficulty:int, difficulty_name:str) :
        game.minecraft_world.difficulty = np.int8(difficulty)
        return Response.Response_Template("将游戏难度设置为 $value", 1, 1).substitute(
            value = difficulty_name
        )


class effect:

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        raise NotImplementedError("暂未实现该命令")


class enchant:

    ENCHANTMENT_NAMES = Constants.GAME_DATA["number_enchant_id"]     #Sorted by numeric id acendingly
    FEEDBACK_MESSAGES = {
        "no_item_entities":"目标没有拿着物品:$no_item_entities",
        "conflict_entities":"不能向目标物品添加选定附魔:$conflict_entities",
        "success_entities":"$success_entities 附魔成功",
    }
    ENTITIES_FOR_MESSAGES = {
        "no_item_entities":[],
        "conflict_entities":[],
        "success_entities":[],
    }

    def to_name(id:str, ENCHANTMENT_NAMES=ENCHANTMENT_NAMES) -> Dict[Literal["name", "washed_id"], Union[str, None]]:
        '''
        Transfer the effect id into fullname id
        '''
        result = {"name":None, "washed_id":None}
        if id.isdigit():
            index = int(id)
            if index >= len(ENCHANTMENT_NAMES):
                result["name"] = None
                result["washed_id"] = id
            else:
                result["name"] = ENCHANTMENT_NAMES[index]
        else:
            id = id.lower()
            if id not in ENCHANTMENT_NAMES:
                result["name"] = None
                result["washed_id"] = id
            else:
                result["name"] = id
        return result
    
    def is_enchantment_conflicting(item:dict, enchantment_name:str) -> bool:
        return False
    

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN, *, to_name=to_name) :

        kargs = {"game":_game}; lst_len = token_list.__len__()
        
        #Selector
        index = 1
        index, kargs["entity_func"] = Selector.Selector_Compiler(_game, token_list, index)
        
        #Enchantment id
        feedback            = to_name(token_list[index]["token"].group())
        enchantment_name    = feedback["name"]
        washed_id           = feedback["washed_id"]

        if enchantment_name is None:
            error_pos = (token_list[index]["token"].start(), token_list[index]["token"].end())
            raise CompileError(f"无效的附魔ID:'{washed_id}'", pos=error_pos)
        
        kargs["enchantment_name"] = enchantment_name; index += 1
        if index >= lst_len : return functools.partial(cls.do, **kargs)

        #Enchantment level
        enchantment_level   = int(token_list[index]["token"].group())
        enchantment_max_level = Constants.ENCHANT[enchantment_name]["max_level"]
        error_message       = None
        if not(1 <= enchantment_level <= enchantment_max_level): error_message = f"{enchantment_name} 不支持等级 {enchantment_level}"
        elif not(-2147483648 <= enchantment_level <= 2147483647): error_message = f"'{enchantment_level}' 不是一个有效的数字"
        if error_message:
            error_pos = (token_list[index]["token"].start(), token_list[index]["token"].end())
            raise CompileError(error_message, pos=error_pos)
        kargs["enchantment_level"] = enchantment_level
        index += 1
        if index >= lst_len : return functools.partial(cls.do, **kargs)


class give:

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        kargs = {"game":_game}; lst_len = token_list.__len__()
        
        #Selector
        index = 1
        index, kargs["entity_func"] = Selector.Selector_Compiler(_game, token_list, index, is_player=True)
        
        #Item
        item_name = ID_transfor(token_list[index]["token"].group())
        if item_name not in _game.minecraft_ident.items:
            raise CompileError(f"不存在名为{item_name}的物品",
                               pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        kargs["item_name"] = item_name; index += 1
        if index >= lst_len : return functools.partial(cls.do, **kargs)

        #Data
        item_data = int(token_list[index]["token"].group())
        if not(0 <= item_data <= 32767):
            raise CompileError(f"'{item_data}' 不是一个有效的数字",
                               pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        kargs["item_data"] = item_data; index += 1
        if index >= lst_len : return functools.partial(cls.do, **kargs)

        #Count
        item_count = int(token_list[index]["token"].group())
        if not(1 <= item_count <= 32767):
            raise CompileError(f"'{item_count}' 不是一个有效的数字",
                               pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        kargs["item_count"] = item_count; index += 1
        if index >= lst_len : return functools.partial(cls.do, **kargs)

        #Nbt
        kargs["item_nbt"] = int(token_list[index]["token"].group())
        return functools.partial(cls.do, **kargs)






