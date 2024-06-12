from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction,EntityComponent,BlockComponent
from . import Selector,CompileError,CommandParser
from . import Quotation_String_transfor_1,ID_transfor,BlockState_Compiler,ItemComponent_Compiler
import functools,string,random,math,itertools,json,copy
from typing import Dict,Union,List,Tuple,Literal,Callable


class ability :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if index >= token_list.__len__() : return functools.partial(cls.query_all, entity_get=entity_func)
        
        ability_id = token_list[index]["token"].group() ; index += 1
        if index >= token_list.__len__() : return functools.partial(cls.query, entity_get=entity_func, ability_id=ability_id)
        
        value = token_list[index]["token"].group()
        return functools.partial(cls.set, entity_get=entity_func, ability_id=ability_id, set_value=value)

    def query_all(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        temp = string.Template("玩家 $player 的能力: worldbuilder=$t1 mayfly=$t2 mute=$t3")
        return Response.Response_Template("查询到以下玩家的能力：\n$result", 1, len(entity_list)).substitute(
        result = "\n".join((
            temp.substitute(player=ID_tracker(i), t1=i.Ability['worldbuilder'],
            t2=i.Ability['mayfly'], t3=i.Ability['mute']) for i in entity_list
        )))

    def query(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, ability_id:str) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        temp = string.Template("玩家 $player 的能力: $abi = $value")
        return Response.Response_Template("查询到以下玩家的能力：\n$result", 1, len(entity_list)).substitute(
            result = "\n".join((
            temp.substitute(player=ID_tracker(i), abi=ability_id, value=i.Ability[ability_id]) for i in entity_list
        )))

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, ability_id:str, set_value:Literal["true","false"]) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        for entity in entity_list : entity.Ability[ability_id] = ("false","true").index(set_value)
        return Response.Response_Template("以下玩家的 $abi 能力设置为 $value ：\n$players", 1, len(entity_list)).substitute(
            abi=ability_id, value=set_value, players=", ".join( (ID_tracker(i) for i in entity_list) )
        )


class alwaysday :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index = 1
        if index >= token_list.__len__() : return functools.partial(cls.query)
        
        value = token_list[index]["token"].group()
        return functools.partial(cls.set, set_value=value)

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
            elif token_list[index]["token"].group() == "view_offset" :
                for i in range(1,3,1) :
                    view_offset = token_list[index+i]["token"]
                    if not (-100 <= int(view_offset.group()) <= 100) : 
                        raise CompileError("视点偏量应该在-100~100之间", pos=(view_offset.start(),view_offset.end()))
                return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
            else : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)

    def clear(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头状态清除 ：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def fade_default(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头设置为黑幕效果 ：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def fade_color(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, rgb:List[int]) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头颜色设置为$rgb：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) ), rgb=tuple(rgb)
        )
    
    def fade_time(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, time:Tuple[int]) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头时间设置为$time：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) ), time=tuple(time)
        )
    
    def fade_time_color(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, time:Tuple[int], rgb:List[int]) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("将以下玩家的摄像头时间和颜色设置为$time,$rgb：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) ), time=tuple(time), rgb=tuple(rgb)
        )

    def set_camera(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, camera_id:str, facing_entity_get:Callable=None) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if isinstance(facing_entity_get, functools.partial) :
            facing_entity_list = entity_get(execute_var, game)
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

    def stop(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if entity_get is None and not isinstance(entity_list[0], BaseNbtClass.entity_nbt) : 
            if entity_list[0].Identifier != "minecraft:player" : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
        return Response.Response_Template("以下玩家的摄像头停止摇晃：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def add(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("以下玩家的摄像头进行摇晃：\n$players", 1, len(entity_list)).substitute(
            players=", ".join( (ID_tracker(i) for i in entity_list) )
        )


class clear :
    
    def clear_items(entity:BaseNbtClass.entity_nbt, container:Literal["Armor","HotBar","Inventory","Weapon"],
                    name:str=None, data:int=-1, max_count:int=2147483647) :
        if name is not None : test_item_obj = BaseNbtClass.item_nbt().__create__(name, 1, data if data != -1 else 0)

        clear_count = 0  ; fill_blank = {}
        clear_list = getattr(entity, container) if container != "Inventory" else getattr(entity, container)["Items"]
        for index,item in enumerate(clear_list) :
            if not isinstance(item, BaseNbtClass.item_nbt) : continue
            if container == "Weapon" and index == 0 : continue

            if name is None : clear_count += int(item.Count) ; clear_list[index] = fill_blank ; continue
            if item.Identifier != test_item_obj.Identifier : continue
            if data != -1 and item.Identifier in Constants.GAME_DATA["damage_tool"] and item.tags["damage"] != data : continue
            elif data != -1 and item.Damage != test_item_obj.Damage : continue

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
        if 1 >= len(token_list) : return functools.partial(cls.clear_specific)

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
        return functools.partial(cls.clear_specific, entity_get=entity_func, name=item_name, data=item_damage, max_count=item_max_clear)

    def clear_specific(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None, name:str=None, data:int=-1, max_count:int=2147483647) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        success = string.Template("$player 清除了符合条件的 $count 个物品")
        faild = string.Template("无法清除 $player 背包中的物品")
        msg_list = [] ; all_count = []
        for entity in entity_list :
            count_list = [
                clear.clear_items(entity, "HotBar", name, data, max_count),
                clear.clear_items(entity, "Inventory", name, data, max_count),
                clear.clear_items(entity, "Armor", name, data, max_count),
                clear.clear_items(entity, "Weapon", name, data, max_count),
            ]
            entity.__update_mainhand__()
            if any(count_list) : msg_list.append( success.substitute(player=ID_tracker(entity), count=sum(count_list)) )
            else : msg_list.append( faild.substitute(player=ID_tracker(entity)) )
            all_count.append(sum(count_list))

        return Response.Response_Template("已清除以下玩家的物品：\n$msg", 1, sum(all_count)).substitute(
            msg="\n".join(msg_list)
        )


class clearspawnpoint :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if 1 >= token_list.__len__() : return cls.clear
        _, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        return functools.partial(cls.clear, entity_get=entity_func)

    def clear(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if entity_get is None and not isinstance(entity_list[0], BaseNbtClass.entity_nbt) : 
            if entity_list[0].Identifier != "minecraft:player" : return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        for entity in entity_list:
            entity.SpawnPoint[0] = game.minecraft_world.world_spawn_x
            entity.SpawnPoint[1] = game.minecraft_world.world_spawn_y
            entity.SpawnPoint[2] = game.minecraft_world.world_spawn_z

        return Response.Response_Template("已清除以下玩家的出生点：$players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list)
        )


class clone :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        poses = [ token_list[i]["token"].group() for i in range(1,10,1) ]
        if 10 >= len(token_list) : 
            return functools.partial(cls.non_fliter, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9])

        mask_mode = token_list[10]["token"].group()
        if mask_mode != "filtered" and 11 >= len(token_list) : 
            return functools.partial(cls.non_fliter, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9], 
            mask_mode=mask_mode)
        elif mask_mode != "filtered" : 
            return functools.partial(cls.non_fliter, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9], 
            mask_mode=mask_mode, clone_mode = token_list[11]["token"].group())
        else : 
            block_id = ID_transfor( token_list[12]["token"].group() )
            if block_id not in _game.minecraft_ident.blocks:
                raise CompileError("不存在的方块ID：%s" % block_id,pos=(token_list[12]["token"].start(), token_list[12]["token"].end()))

            if 13 >= len(token_list) : block_state = {}
            elif token_list[13]["type"] == "Block_Data" : 
                block_state = int(token_list[13]["token"].group())
                if not(-1 <= block_state <= 32767) : raise CompileError("%s 不是一个有效的数据值" % block_state,
                pos=(token_list[13]["token"].start(), token_list[13]["token"].end()))
            else : _,block_state = BlockState_Compiler( block_id, token_list, 13 )
            return functools.partial(cls.fliter, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9], 
            clone_mode = token_list[11]["token"].group(), block_id=block_id, block_state={} if block_state == -1 else block_state)

    def error_test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start_pos1, end_pos1, start_pos2, end_pos2) :
        height_test = Constants.DIMENSION_INFO[execute_var["dimension"]]["height"]
        for i,j in [("起始位置", start_pos1),("结束位置", end_pos1),("复制起始位置", start_pos2),("复制结束位置", end_pos2)] :
            if not(height_test[0] <= j[1] < height_test[1]) :
                return Response.Response_Template("$id$pos处于世界之外").substitute(id=i, pos=tuple(j))

        for j in itertools.product(range(start_pos1[0]//16*16, end_pos1[0]//16*16+16, 16), range(start_pos1[2]//16*16, end_pos1[2]//16*16+16, 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], (j[0],0,j[1])) :
                return Response.Response_Template("起始区域$pos为未加载的区块").substitute(pos=tuple(start_pos1))

        for j in itertools.product(range(start_pos2[0]//16*16, end_pos2[0]//16*16+16, 16), range(start_pos2[2]//16*16, end_pos2[2]//16*16+16, 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], (j[0],0,j[1])) :
                return Response.Response_Template("目标区域$pos为未加载的区块").substitute(pos=tuple(start_pos1))

    def non_fliter(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start1:tuple, end1:tuple, start2:tuple, 
                   mask_mode:str="replace", clone_mode:str="normal") :
        start_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start1, execute_var["rotate"])]
        end_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], end1, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos1, end_pos1)) :
            if pos_1 > pos_2 : start_pos1[index] = pos_2; end_pos1[index] = pos_1
        start_pos2 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start2, execute_var["rotate"])]
        end_pos2 = [start_pos2[i] + end_pos1[i] - start_pos1[i] for i in range(3)]
        
        aaa = clone.error_test(execute_var, game, start_pos1, end_pos1, start_pos2, end_pos2)
        if isinstance(aaa, Response.Response_Template) : return aaa

        if clone_mode != "force" and max(start_pos1[0],start_pos2[0]) <= min(end_pos1[0],end_pos2[0]) and \
            max(start_pos1[1],start_pos2[1]) <= min(end_pos1[1],end_pos2[1]) and \
            max(start_pos1[2],start_pos2[2]) <= min(end_pos1[2],end_pos2[2]) :
            return Response.Response_Template("非force模式下无法区域重叠复制").substitute()

        volue = [end_pos1[i] - start_pos1[i] + 1 for i in range(3)]
        if volue[0] * volue[1] * volue[2] > 655360 : return Response.Response_Template("区域大小超过655360个方块").substitute()

        
        block_index_list = [0] * (volue[0] * volue[1] * volue[2]) ; block_nbt_list = [None] * (volue[0] * volue[1] * volue[2])
        for index,pos_xyz in enumerate(itertools.product( range(start_pos1[0], end_pos1[0]+1), range(start_pos1[1], end_pos1[1]+1), 
            range(start_pos1[2], end_pos1[2]+1) )) :
            block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], pos_xyz)
            if mask_mode == "masked" and block_index == 0 : continue
            block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], pos_xyz)
            block_index_list[index] = block_index
            if block_nbt is not None : block_nbt_list[index] = copy.deepcopy(block_nbt)
            if clone_mode == "move" : 
                game.minecraft_chunk.____set_block____(execute_var["dimension"], pos_xyz, 0)
                game.minecraft_chunk.____set_block_nbt____(execute_var["dimension"], pos_xyz, None)
        
        for index,pos_xyz in enumerate(itertools.product( range(start_pos2[0], end_pos2[0]+1), range(start_pos2[1], end_pos2[1]+1), 
            range(start_pos2[2], end_pos2[2]+1) )) :
            if mask_mode == "masked" and block_index_list[index] == 0 : continue
            game.minecraft_chunk.____set_block____(execute_var["dimension"], pos_xyz, block_index_list[index])
            game.minecraft_chunk.____set_block_nbt____(execute_var["dimension"], pos_xyz, block_nbt_list[index])
        
        if mask_mode != "masked" : success_counter = len(block_index_list)
        else : success_counter = len(block_index_list) - block_index_list.count(0)
        return Response.Response_Template("在$start ~ $end复制了$count个方块", 1, success_counter).substitute(
            start=tuple(start_pos2), end=tuple(end_pos2), count=success_counter)

    def fliter(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start1:tuple, end1:tuple, start2:tuple,
               clone_mode:str, block_id:str, block_state:Union[int,dict]) :
        start_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start1, execute_var["rotate"])]
        end_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], end1, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos1, end_pos1)) :
            if pos_1 > pos_2 : start_pos1[index] = pos_2; end_pos1[index] = pos_1
        start_pos2 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start2, execute_var["rotate"])]
        end_pos2 = [start_pos2[i] + end_pos1[i] - start_pos1[i] for i in range(3)]
        
        aaa = clone.error_test(execute_var, game, start_pos1, end_pos1, start_pos2, end_pos2)
        if isinstance(aaa, Response.Response_Template) : return aaa

        if clone_mode != "force" and max(start_pos1[0],start_pos2[0]) <= min(end_pos1[0],end_pos2[0]) and \
            max(start_pos1[1],start_pos2[1]) <= min(end_pos1[1],end_pos2[1]) and \
            max(start_pos1[2],start_pos2[2]) <= min(end_pos1[2],end_pos2[2]) :
            return Response.Response_Template("非force模式下无法区域重叠复制").substitute()

        volue = [end_pos1[i] - start_pos1[i] + 1 for i in range(3)]
        if volue[0] * volue[1] * volue[2] > 655360 : return Response.Response_Template("区域大小超过655360个方块").substitute()


        if isinstance(block_state, int) and block_state != -1 :
            test_block_obj = BaseNbtClass.block_nbt().__create__(block_id, block_state)
        block_index_list = [None] * (volue[0] * volue[1] * volue[2]) ; block_nbt_list = [None] * (volue[0] * volue[1] * volue[2])
        for index,pos_xyz in enumerate(itertools.product( range(start_pos1[0], end_pos1[0]+1), range(start_pos1[1], end_pos1[1]+1), 
            range(start_pos1[2], end_pos1[2]+1) )) :
            block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], pos_xyz)
            block_obj = game.minecraft_chunk.block_mapping[block_index]
            if block_obj.Identifier != block_id : continue
            if isinstance(block_state, dict) and any([block_obj.BlockState[i] != block_state[i] for i in block_state]) : continue
            elif isinstance(block_state, int) and block_state != -1 :
                if any([block_obj.BlockState[i] != test_block_obj.BlockState[i] for i in test_block_obj.BlockState]) : continue
            block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], pos_xyz)
            block_index_list[index] = block_index
            if block_nbt is not None : block_nbt_list[index] = copy.deepcopy(block_nbt)
            if clone_mode == "move" : 
                game.minecraft_chunk.____set_block____(execute_var["dimension"], pos_xyz, 0)
                game.minecraft_chunk.____set_block_nbt____(execute_var["dimension"], pos_xyz, None)
        
        for index,pos_xyz in enumerate(itertools.product( range(start_pos2[0], end_pos2[0]+1), range(start_pos2[1], end_pos2[1]+1), 
            range(start_pos2[2], end_pos2[2]+1) )) :
            if block_index_list[index] is None : continue
            game.minecraft_chunk.____set_block____(execute_var["dimension"], pos_xyz, block_index_list[index])
            game.minecraft_chunk.____set_block_nbt____(execute_var["dimension"], pos_xyz, block_nbt_list[index])

        success_counter = len(block_index_list) - block_index_list.count(None)
        return Response.Response_Template("在$start ~ $end复制了$count个方块", min(1,success_counter), success_counter).substitute(
            start=tuple(start_pos2), end=tuple(end_pos2), count=success_counter)


class damage :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_hurt = Selector.Selector_Compiler(_game, token_list, 1)
        
        amount = int(token_list[index]["token"].group()); index += 1
        if amount < 0 : raise CompileError("伤害数值应该为正整数", pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.doing_damage, entity_hurt=entity_hurt, amount=amount)

        cause = token_list[index]["token"].group(); index += 1
        if cause != "suicide" and cause not in Constants.DAMAGE_CAUSE :
            raise CompileError("不存在的伤害类型：%s" % cause, pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.doing_damage, entity_hurt=entity_hurt, amount=amount, damage_type=cause)

        _, entity_causer = Selector.Selector_Compiler(_game, token_list, index + 1, is_single=True) # Skip reading the word 'entity', so index+1
        return functools.partial(cls.doing_damage, entity_hurt=entity_hurt, amount=amount, damage_type=cause, entity_causer=entity_causer)

    def doing_damage(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_hurt:Callable, 
                     amount:int, damage_type:str="none", entity_causer:Callable=None):
        entity_list:List[BaseNbtClass.entity_nbt] = entity_hurt(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        entity_couse_list:List[BaseNbtClass.entity_nbt] = entity_causer(execute_var, game) if entity_causer else [None]
        if isinstance(entity_couse_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功的造成伤害:\n$entity")
        faild = string.Template("以下实体无法造成伤害:\n$entity")
        success_list, faild_list = [], []
        for entity in entity_list :
            a = entity.__get_damage__(game.minecraft_world, damage_type, amount, entity_couse_list[0])
            if a : success_list.append(ID_tracker(entity))
            else : faild_list.append(ID_tracker(entity))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")


class daylock :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index = 1
        if index >= token_list.__len__() : return cls.query
        
        value = token_list[index]["token"].group()
        return functools.partial(cls.set, set_value=value)

    def query(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread) :
        return Response.Response_Template("游戏规则 dodaylightcycle 为 $value", 1, 1).substitute(
            value = game.minecraft_world.dodaylightcycle
        )

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, set_value:Literal["true","false"]) :
        game.minecraft_world.dodaylightcycle = bool(("false","true").index(set_value))
        return Response.Response_Template("游戏规则 dodaylightcycle 已变更为 $value", 1, 1).substitute(
            value = game.minecraft_world.dodaylightcycle
        )


class dialogue:

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        open_or_change = token_list[1]["token"].group()
        index, entity_npc = Selector.Selector_Compiler(_game, token_list, 2, is_npc=True, is_single=True)

        if open_or_change == "open":
            index, entity_player = Selector.Selector_Compiler(_game, token_list, index, is_player=True)
            if index >= len(token_list) : return functools.partial(cls.open, entity_npc=entity_npc, entity_player=entity_player)

            scene_name = token_list[index]["token"].group()
            if scene_name not in _game.minecraft_ident.dialogues :
                raise CompileError("不存在的场景ID：%s" % scene_name, pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            return functools.partial(cls.open, entity_npc=entity_npc, entity_player=entity_player)

        elif open_or_change == "change":
            scene_name = token_list[index]["token"].group() ; index += 1
            if index >= len(token_list) : return functools.partial(cls.change, entity_npc=entity_npc)

            _, entity_player = Selector.Selector_Compiler(_game, token_list, index, is_player=True)
            return functools.partial(cls.change, entity_npc=entity_npc, entity_player=entity_player)
        
    def open(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_npc:Callable, entity_player:Callable) :
        entity_list = entity_player(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        npc_list = entity_npc(execute_var, game)
        if isinstance(npc_list, Response.Response_Template) : return npc_list

        return Response.Response_Template("对话已发送至以下玩家:\n$players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list)
        )

    def change(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_npc:Callable, entity_player:Callable=None) :
        npc_list = entity_npc(execute_var, game)
        if isinstance(npc_list, Response.Response_Template) : return npc_list
        entity_list = entity_player(execute_var, game) if entity_player else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        return Response.Response_Template("已更改以下玩家的对话:\n $players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list)
        )


class difficulty :
    DIFFICULTY:list = Constants.GAME_DATA["difficult_type"]

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        difficulty_data = cls.DIFFICULTY
        token = token_list[1]["token"]
        difficulty = difficulty_data.index(token.group()) // 3   #The var 'difficulty' is the numeric id of difficulty
        difficulty_name = difficulty_data[0::3][difficulty]     #Get the column 0 and get the full name of difficulty
        return functools.partial(cls.set, difficulty=difficulty, difficulty_name=difficulty_name)

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, difficulty:int, difficulty_name:str) :
        game.minecraft_world.difficulty = np.int8(difficulty)
        return Response.Response_Template("将游戏难度设置为 $value", 1, 1).substitute(
            value = difficulty_name
        )


class effect :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_get = Selector.Selector_Compiler(_game, token_list, 1)
        effect_id = token_list[index]["token"].group() ; index += 1
        if effect_id == "clear" : return functools.partial(cls.clear, entity_get=entity_get)

        if effect_id not in Constants.EFFECT :
            raise CompileError("不存在的药水效果：%s" % effect_id, pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.give, entity_get=entity_get, effect_id=effect_id)

        times = int(token_list[index]["token"].group()) ; index += 1
        if not(0 <= times <= 1000000) :
            raise CompileError("药水效果时长应该在 0~1000000 内", pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.give, entity_get=entity_get, effect_id=effect_id, times=times)

        amplifier = int(token_list[index]["token"].group()) ; index += 1
        if not(0 <= amplifier <= 255) :
            raise CompileError("药水效果等级应该在 0~255 内", pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        return functools.partial(cls.give, entity_get=entity_get, effect_id=effect_id, times=times, amplifier=amplifier)

    def clear(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, effect_id:str=None) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功的移除了效果:\n$entity")
        faild = string.Template("以下实体无法移除效果:\n$entity")
        success_list, faild_list = [], []

        for entity in entity_list :
            if not hasattr(entity, "ActiveEffects") : faild_list.append(ID_tracker(entity)) ; continue
            if effect_id is None : 
                if entity.ActiveEffects.__len__() : entity.ActiveEffects.clear() ; success_list.append(ID_tracker(entity))
                else : faild_list.append(ID_tracker(entity))
                continue
            if effect_id in entity.ActiveEffects : del entity.ActiveEffects[effect_id]
            success_list.append(ID_tracker(entity))
        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")

    def give(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, effect_id:str, times:int=30, amplifier:int=0) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功的添加了药水效果:\n$entity")
        faild = string.Template("以下实体无法添加药水效果:\n$entity")
        success_list, faild_list = [], []

        for entity in entity_list :
            if not hasattr(entity, "ActiveEffects") : faild_list.append(ID_tracker(entity)) ; continue
            if times == 0 :
                if effect_id in entity.ActiveEffects : del entity.ActiveEffects[effect_id]
            elif effect_id in entity.ActiveEffects :
                aaa = entity.ActiveEffects[effect_id]
                if aaa["Amplifier"] <= amplifier : aaa["Amplifier"] = np.int32(amplifier) ; aaa["Duration"] = np.int16(times)
                elif aaa["Duration"] <= times : aaa["Duration"] = np.int16(times)
            else : 
                aaa = Constants.EFFECT_TEMPLATE.copy()
                aaa["Id"] = effect_id ; aaa["Amplifier"] = np.int32(amplifier) ; aaa["Duration"] = np.int16(times)
                entity.ActiveEffects[effect_id] = aaa
            success_list.append(ID_tracker(entity))
        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")


class enchant :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_get = Selector.Selector_Compiler(_game, token_list, 1)
        if token_list[index]["type"] == "Enchant_Type" : 
            enchant_id = token_list[index]["token"].group()
            if enchant_id not in Constants.ENCHANT :
                raise CompileError("不存在的附魔ID：%s" % enchant_id, pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            enchant_index = Constants.GAME_DATA['number_enchant_id'].index(enchant_id)
        else : 
            enchant_index = int(token_list[index]["token"].group())
            if not(0 <= enchant_index < Constants.GAME_DATA['number_enchant_id'].__len__()) :
                raise CompileError("不存在的附魔ID：%s" % enchant_index, pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            enchant_id = Constants.GAME_DATA['number_enchant_id'][enchant_index]
        index += 1
        enchant_max = Constants.ENCHANT[enchant_id]["max_level"]
        if index >= len(token_list) : return functools.partial(cls.enchant_item, entity_get=entity_get,
            enchant_id=enchant_id, enchant_index=enchant_index, enchant_max=enchant_max)

        enchant_level = int(token_list[index]["token"].group())
        if not(1 <= enchant_level <= enchant_max) :
            raise CompileError("附魔等级应该在 1~%s 内" % enchant_max, pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        return functools.partial(cls.enchant_item, entity_get=entity_get, 
            enchant_id=enchant_id, enchant_index=enchant_index, enchant_max=enchant_max, enchant_level=enchant_level)

    def enchant_item(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, 
                     enchant_id:str, enchant_index:int, enchant_max:int, enchant_level:int=1) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功的为主手物品添加了附魔:\n$entity")
        faild = string.Template("以下实体无法为主手物品添加附魔:\n$entity")
        success_list, faild_list = [], []

        for entity in entity_list :
            if not hasattr(entity, "Weapon") or not isinstance(entity.Weapon[0], BaseNbtClass.item_nbt) or \
            entity.Weapon[0].Identifier not in game.minecraft_ident.items or \
            enchant_id not in game.minecraft_ident.items[entity.Weapon[0].Identifier]['can_enchant'] : 
                faild_list.append(ID_tracker(entity)) ; continue
            item_obj:BaseNbtClass.item_nbt = entity.Weapon[0]
            if "ench" not in item_obj.tags : item_obj.tags["ench"] = []
            m1 = [i["id"] == enchant_index for i in item_obj.tags["ench"]]
            if any(m1) : 
                ench_obj = item_obj.tags["ench"][m1.index(True)]
                if ench_obj["lvl"] < enchant_level : ench_obj["lvl"] = np.int16(enchant_level)
                elif ench_obj["lvl"] == enchant_level : ench_obj["lvl"] = np.int16(enchant_level + 1)
                elif ench_obj["lvl"] == enchant_level == enchant_max : faild_list.append(ID_tracker(entity)) ; continue
                elif ench_obj["lvl"] > enchant_level : faild_list.append(ID_tracker(entity)) ; continue
            else : 
                index = len(m1)
                item_obj.tags["ench"].append(Constants.ENCHANT_TEMPLATE.copy())
                item_obj.tags["ench"][index]["id"] = enchant_id
                item_obj.tags["ench"][index]["lvl"] = np.int16(enchant_level)
            success_list.append(ID_tracker(entity))
        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")


class event :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_get = Selector.Selector_Compiler(_game, token_list, 2)
        event_id = token_list[index]["token"].group()
        return functools.partial(cls.run_event, entity_get=entity_get, event_id=event_id)

    def run_event(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, event_id:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功的触发了事件:\n$entity")
        faild = string.Template("以下实体无法触发事件:\n$entity")
        success_list, faild_list = [], []

        for entity in entity_list :
            if entity.Identifier not in game.minecraft_ident.entities or \
            event_id not in game.minecraft_ident.entities[entity.Identifier]["events"] : 
                faild_list.append(ID_tracker(entity)) ; continue
            EntityComponent.trigger_event(entity, event_id)
            success_list.append(ID_tracker(entity))
        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")


class fill_1_0_0 :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        poses = [ token_list[i]["token"].group() for i in range(1,7,1) ]
        block_id = ID_transfor(token_list[7]["token"].group())
        if block_id not in _game.minecraft_ident.blocks :
            raise CompileError("不存在的方块ID：%s" % block_id, pos=(token_list[7]["token"].start(), token_list[7]["token"].end()))
        if 8 >= len(token_list) : return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6],
            block_id=block_id)

        index = 8
        if token_list[index]["type"] == "Block_Data" : 
            block_state = int(token_list[index]["token"].group())
            if not(0 <= block_state <= 32767) : raise CompileError("%s 不是一个有效的数据值" % block_state,
            pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            if block_state == -1 : block_state = {}
            index += 1
        else : index, block_state = BlockState_Compiler( block_id, token_list, index )
        if index >= len(token_list) : return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6],
            block_id=block_id, block_state=block_state)

        fill_mode = token_list[index]["token"].group() ; index += 1
        if fill_mode != "replace" : return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6],
            block_id=block_id, block_state=block_state, fill_mode=fill_mode)
        elif fill_mode == "replace" and index >= len(token_list) : return functools.partial(cls.fill_block,  
            start1=poses[0:3], end1=poses[3:6], block_id=block_id, block_state=block_state)
        elif fill_mode == "replace" : 
            test_block_id = ID_transfor(token_list[index]["token"].group()) ; index += 1
            if test_block_id not in _game.minecraft_ident.blocks :
                raise CompileError("不存在的方块ID：%s" % test_block_id, pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : return functools.partial(cls.fill_block, start1=poses[0:3], 
                end1=poses[3:6], block_id=block_id, block_state=block_state, test_block=test_block_id)

            if token_list[index]["type"] == "Block_Data" : 
                test_block_state = int(token_list[index]["token"].group())
                if not(-1 <= test_block_state <= 32767) : raise CompileError("%s 不是一个有效的数据值" % test_block_state,
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
                if test_block_state == -1 : test_block_state = {}
                index += 1
            else : index, block_state = BlockState_Compiler( block_id, token_list, index )
            return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6], block_id=block_id,
                block_state=block_state, test_block=test_block_id, test_block_state=test_block_state)

    def error_test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start_pos1, end_pos1) :
        height_test = Constants.DIMENSION_INFO[execute_var["dimension"]]["height"]
        for i,j in [("起始位置", start_pos1),("结束位置", end_pos1)] :
            if not(height_test[0] <= j[1] < height_test[1]) :
                return Response.Response_Template("$id$pos处于世界之外").substitute(id=i, pos=tuple(start_pos1))

        for j in itertools.product(range(start_pos1[0], end_pos1[0], 16), range(start_pos1[2], end_pos1[2], 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], (j[0],0,j[1])) :
                return Response.Response_Template("起始区域$pos为未加载的区块").substitute(pos=tuple(start_pos1))
        if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], end_pos1) :
            return Response.Response_Template("起始区域$pos为未加载的区块").substitute(pos=tuple(start_pos1))

    def fill_block(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start1:List[str], end1:List[str], block_id:str,
            block_state:Union[int,dict]=0, fill_mode:str="replace", test_block:str=None, test_block_state:Union[int,dict]={}) :
        start_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start1, execute_var["rotate"])]
        end_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], end1, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos1, end_pos1)) :
            if pos_1 > pos_2 : start_pos1[index] = pos_2; end_pos1[index] = pos_1

        aaa = fill_1_0_0.error_test(execute_var, game, start_pos1, end_pos1)
        if isinstance(aaa, Response.Response_Template) : return aaa

        volue = [end_pos1[i] - start_pos1[i] + 1 for i in range(3)]
        if volue[0] * volue[1] * volue[2] > 32768 : return Response.Response_Template("区域大小超过32768个方块").substitute()


        new_block_index = game.minecraft_chunk.____find_block_mapping____(block_id, block_state)
        success = [False] * (volue[0] * volue[1] * volue[2])
        if test_block and isinstance(test_block_state, int) and test_block_state != -1 :
            test_block_obj = BaseNbtClass.block_nbt().__create__(test_block, test_block_state)
        for index,pos_xyz in enumerate(itertools.product( range(start_pos1[0], end_pos1[0]+1), range(start_pos1[1], end_pos1[1]+1), 
            range(start_pos1[2], end_pos1[2]+1) )) :
            block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], pos_xyz)
            if fill_mode != "hollow" and block_index == new_block_index : continue
            block_obj = game.minecraft_chunk.block_mapping[block_index]

            if fill_mode == "replace" and test_block and isinstance(test_block_state, dict) :
                if any((block_obj.BlockState[i] != test_block_state[i] for i in test_block_state)) : continue
            elif fill_mode == "replace" and test_block and isinstance(test_block_state, int) and test_block_state != -1 :
                if any((block_obj.BlockState[i] != test_block_obj.BlockState[i] for i in test_block_obj.BlockState)) : continue
            elif fill_mode == "outline" :
                if not all( (start_pos1[i] < pos_xyz[i] < end_pos1[i] for i in range(3)) ) : continue
            elif fill_mode == "keep" and block_index != 0 : continue
            elif fill_mode == "hollow" :
                aaa = all( (start_pos1[i] < pos_xyz[i] < end_pos1[i] for i in range(3)) )
                if aaa and block_index == 0 : continue
                elif not aaa and block_index == new_block_index : continue
                game.minecraft_chunk.____set_block____(execute_var["dimension"], pos_xyz, 0)
                game.minecraft_chunk.____set_block_nbt____(execute_var["dimension"], pos_xyz, None)
                success[index] = True
                continue
            elif fill_mode == "destroy" :
                a = block_obj.__change_to_entity__(execute_var["dimension"], [i+0.5 for i in pos_xyz])
                game.minecraft_chunk.__add_entity__(a)

            game.minecraft_chunk.____set_block____(execute_var["dimension"], pos_xyz, new_block_index)
            game.minecraft_chunk.____set_block_nbt____(execute_var["dimension"], pos_xyz, BlockComponent.find_block_id_nbt(block_id))
            success[index] = True

        success_counter = len(success) - success.count(False)
        return Response.Response_Template("在$start ~ $end填充了$count个方块", min(1,success_counter), success_counter).substitute(
            start=tuple(start_pos1), end=tuple(end_pos1), count=success_counter)


class fill_1_19_80 :

    fill_block:Callable = fill_1_0_0.fill_block

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        poses = [ token_list[i]["token"].group() for i in range(1,7,1) ]
        block_id = ID_transfor(token_list[7]["token"].group())
        if block_id not in _game.minecraft_ident.blocks :
            raise CompileError("不存在的方块ID：%s" % block_id, pos=(token_list[7]["token"].start(), token_list[7]["token"].end()))
        if 8 >= len(token_list) : return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6],
            block_id=block_id)

        index = 8
        if token_list[index]["type"] == "Start_BlockState_Argument" : 
            index, block_state = BlockState_Compiler( block_id, token_list, index )
        else : block_state = 0
        if index >= len(token_list) : return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6],
            block_id=block_id, block_state=block_state)

        fill_mode = token_list[index]["token"].group() ; index += 1
        if fill_mode != "replace" : return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6],
            block_id=block_id, block_state=block_state, fill_mode=fill_mode)
        elif fill_mode == "replace" and index >= len(token_list) : return functools.partial(cls.fill_block, 
            start1=poses[0:3], end1=poses[3:6], block_id=block_id, block_state=block_state)
        elif fill_mode == "replace" : 
            test_block_id = ID_transfor(token_list[index]["token"].group()) ; index += 1
            if test_block_id not in _game.minecraft_ident.blocks :
                raise CompileError("不存在的方块ID：%s" % test_block_id, pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : return functools.partial(cls.fill_block, start1=poses[0:3], 
                end1=poses[3:6], block_id=block_id, block_state=block_state, test_block=test_block_id)

            if token_list[index]["type"] == "Start_BlockState_Argument" : 
                index, test_block_state = BlockState_Compiler( block_id, token_list, index )
            else : test_block_state = {}
            return functools.partial(cls.fill_block, start1=poses[0:3], end1=poses[3:6], block_id=block_id,
                block_state=block_state, test_block=test_block_id, test_block_state=test_block_state)


class fog :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        mode = token_list[index]["token"].group() ; index += 1
        if mode == "push" : 
            fog_id = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            if fog_id not in _game.minecraft_ident.fogs : raise CompileError("不存在的迷雾ID：%s" % fog_id, 
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            user_id = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            return functools.partial(cls.push, entity_get=entity_func, fog_id=fog_id, user_id=user_id)
        else : 
            user_id = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            return functools.partial(cls.pop, entity_get=entity_func, user_id=user_id)
    
    def push(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, fog_id:str, user_id:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        for player in entity_list : player.fogCommandStack.append({"user_id":user_id, "id":fog_id})
        return Response.Response_Template("以下玩家已将迷雾添加至栈内:\n$players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list)
        )

    def pop(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, user_id:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功的移除了最后添加的迷雾:\n$entity")
        faild = string.Template("以下实体不存在添加的迷雾:\n$entity")
        success_list, faild_list = [], []

        for player in entity_list :
            if any((i["user_id"] == user_id for i in player.fogCommandStack)) :
                for index,item in enumerate(list(player.fogCommandStack)) :
                    if item["user_id"] != user_id : continue
                    del player.fogCommandStack[index] ; break
                success_list.append(ID_tracker(player))
            else : faild_list.append(ID_tracker(player))
        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")


class gamemode :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        mode = Constants.GAME_DATA["gamemode_type"].index( token_list[1]["token"].group() ) // 3
        if 2 >= len(token_list) : return functools.partial(cls.set_gamemode, gamemode_value=mode)

        _, player_get = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
        return functools.partial(cls.set_gamemode, gamemode_value=mode, entity_get=player_get)
    
    def set_gamemode(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, gamemode_value:int, entity_get:Callable=None) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
        
        for player in entity_list : player.GameMode = np.int8(gamemode_value)
        translate = ["生存", "创造", "冒险", "旁观"][gamemode_value]
        return Response.Response_Template("以下玩家已将游戏模式更改为$mode:\n$players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list), mode=translate
        )


class gamerule :

    int_gamerule = {"randomtickspeed":None, "spawnradius":None, "playerssleepingpercentage":None,
                    "functioncommandlimit": 10000, "maxcommandchainlength":None}

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        gamerule_name = token_list[1]["token"].group().lower()
        if gamerule_name not in Constants.GAMERULE : raise CompileError("不存在的游戏规则：%s" % gamerule_name, 
            pos=(token_list[1]["token"].start(), token_list[1]["token"].end()))
        if 2 >= len(token_list) : return functools.partial(cls.set_gamerule, gamerule_name=gamerule_name)

        if gamerule_name in cls.int_gamerule and token_list[2]["type"] != "Int_Value" :
            raise CompileError("游戏规则%s不是布尔值类型" % gamerule_name, 
            pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))

        if token_list[2]["type"] == "Int_Value" : value = int(token_list[2]["token"].group())
        else : value = bool(("false","true").index(token_list[2]["token"].group()))
        if gamerule_name in cls.int_gamerule :
            if value < 0 : raise CompileError("游戏规则%s不能为负数" % gamerule_name, 
            pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
            if (cls.int_gamerule[gamerule_name] is not None) and value > cls.int_gamerule[gamerule_name] : 
                raise CompileError("游戏规则%s不能超过%s" % (gamerule_name, cls.int_gamerule[gamerule_name]), 
                pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
        return functools.partial(cls.set_gamerule, gamerule_name=gamerule_name, value=value)
    
    def set_gamerule(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, gamerule_name:str, value:Union[bool,int]=None) :
        if value is None : return Response.Response_Template("游戏规则 $rule 为 $value1", 1, 1).substitute(
            rule=gamerule_name, value1=game.minecraft_world.__getattribute__(gamerule_name))
        type1 = type(game.minecraft_world.__getattribute__(gamerule_name))
        setattr(game.minecraft_world, gamerule_name, type1(value))
        return Response.Response_Template("游戏规则 $rule 已修改为 $value1", 1, 1).substitute(
            rule=gamerule_name, value1=game.minecraft_world.__getattribute__(gamerule_name)
        )


class give :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        lst_len = token_list.__len__()
        
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        item_name = ID_transfor(token_list[index]["token"].group()) ; index += 1
        if item_name not in _game.minecraft_ident.items: raise CompileError("不存在的物品ID: %s" % item_name,
            pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= lst_len : return functools.partial(cls.give_item, entity_get=entity_func, item_id=item_name)

        #Count
        item_count = int(token_list[index]["token"].group()) ; index += 1
        if not(1 <= item_count <= 32767): raise CompileError("%s 不是一个有效的数量" % item_count,
            pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= lst_len : return functools.partial(cls.give_item, entity_get=entity_func, item_id=item_name, count=item_count)

        #Data
        item_data = int(token_list[index]["token"].group()) ; index += 1
        if not(0 <= item_data <= 32767): raise CompileError("%s不是一个有效的数据值" % item_data,
            pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= lst_len : return functools.partial(cls.give_item, entity_get=entity_func, item_id=item_name, data=item_data, count=item_count)

        #Nbt
        item_nbt = ItemComponent_Compiler(_game, token_list, index)
        return functools.partial(cls.give_item, entity_get=entity_func, item_id=item_name, data=item_data, count=item_count, nbt=item_nbt[1])

    def give_item(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, item_id:str, data:int=0, count:int=1, nbt:dict={}) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        itme_obj = BaseNbtClass.item_nbt().__create__(item_id, count, data, nbt)
        itme_obj.Count = count

        for player in entity_list : 
            if player.__pickup_item__(itme_obj) : itme_obj.__change_to_entity__(execute_var["dimension"], player.Pos)
            player.__update_mainhand__()
        return Response.Response_Template("以下玩家已给予 $item * $count :\n$players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list), item=item_id, count=count
        )


