from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction
from . import Selector,CompileError
import functools,string,random
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
                    _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+1)
                    return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name, facing_entity_get=facing_entity_func)
                elif token_list[index]["token"].group() == "pos" :
                    if (index+4) >= token_list.__len__() : 
                        return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
                    elif token_list[index+4]["token"].group() == "facing" and token_list[index+5]["type"] in ("Selector","Player_Name") :
                        _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+5)
                        return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name, facing_entity_get=facing_entity_func)
                    else : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
                else : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
            elif token_list[index]["token"].group() == "facing" and token_list[index+1]["type"] in ("Selector","Player_Name") :
                _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+1)
                return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name, facing_entity_get=facing_entity_func)
            elif token_list[index]["token"].group() == "pos" :
                if (index+4) >= token_list.__len__() : return functools.partial(cls.set_camera, entity_get=entity_func, camera_id=perset_name)
                elif token_list[index+4]["token"].group() == "facing" and token_list[index+5]["type"] in ("Selector","Player_Name") :
                    _,facing_entity_func = Selector.Selector_Compiler(_game, token_list, index+5)
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









class tell :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        msg_temp = token_list[index]["token"].group()
        
        return functools.partial(cls.set, game=_game, msg=weather_name, search_entity=time)

    def send_msg(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, msg:str, search_entity:List[Callable]) :
        pass

class weather :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group() == "query" : return functools.partial(cls.query, game=_game)
        weather_name = token_list[1]["token"].group()
        if 2 >= token_list.__len__() : return functools.partial(cls.set, game=_game, weather_name=weather_name)
        time = int(token_list[2]["token"].group())
        if time <= 0 : raise CompileError("天气时长不能为非正整数", pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
        return functools.partial(cls.set, game=_game, weather_name=weather_name, time=time)

    def query(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread) :
        aaaa = Response.Response_Template("当前的天气：$weather", 1, 1)
        if game.minecraft_world.sunny_time > 0 : return aaaa.substitute(weather="clear")
        elif game.minecraft_world.rain_time > 0 : return aaaa.substitute(weather="rain")
        elif game.minecraft_world.thunder_time > 0 : return aaaa.substitute(weather="thunder")

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, weather_name:Literal["clear","rain","thunder"], time:int=None) :
        game.minecraft_world.sunny_time = np.int32(0)
        game.minecraft_world.rain_time = np.int32(0)
        game.minecraft_world.thunder_time = np.int32(0)

        if time is None : time = np.int32(random.randint(10000, 30000))
        if weather_name == "clear" : game.minecraft_world.sunny_time = np.int32(time)
        elif weather_name == "rain" : game.minecraft_world.rain_time = np.int32(time)
        elif weather_name == "thunder" : game.minecraft_world.thunder_time = np.int32(time)
        aaaa = Response.Response_Template("将天气更改为 $weather", 1, 1)
        if game.minecraft_world.sunny_time > 0 : return aaaa.substitute(weather="clear")
        elif game.minecraft_world.rain_time > 0 : return aaaa.substitute(weather="rain")
        elif game.minecraft_world.thunder_time > 0 : return aaaa.substitute(weather="thunder")


class xp :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group()[-1] == "L" : lvl_value = int(token_list[1]["token"].group()[:-1]) ; func = cls.modify_level
        else : lvl_value = int(token_list[1]["token"].group()) ; func = cls.modify_point

        if 2 >= token_list.__len__() : return functools.partial(func, entity_get=None, value=lvl_value)
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
        return functools.partial(func, entity_get=entity_func, value=lvl_value)

    def modify_level(execute_var:COMMAND_CONTEXT, entity_get:functools.partial=None, value:int=0) :
        entity_list = entity_get(execute_var) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if entity_get is None and not isinstance(entity_list[0], BaseNbtClass.entity_nbt) : 
            if entity_list[0].Identifier != "minecraft:player" : return Response.Response_Template("没有与目标选择器匹配的目标").substitute({})

        for player1 in entity_list : player1.PlayerLevel = max(np.int32(0), player1.PlayerLevel + value)
        temp1 = string.Template("$player 的等级变为 $value")
        return Response.Response_Template("以下玩家的经验值发生变化：\n$msg", 1, len(entity_list)).substitute(
            msg="\n".join( (temp1.substitute(player = ID_tracker(i), value=i.PlayerLevel) for i in entity_list) )
        )

    def modify_point(execute_var:COMMAND_CONTEXT, entity_get:functools.partial=None, value:int=0) :
        entity_list = entity_get(execute_var) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if entity_get is None and not isinstance(entity_list[0], BaseNbtClass.entity_nbt) : 
            if entity_list[0].Identifier != "minecraft:player" : return Response.Response_Template("没有与目标选择器匹配的目标").substitute({})

        for player1 in entity_list :
            aaaaa = int(player1.PlayerLevel)
            now_point = MathFunction.mc_level2point(aaaaa) + float(player1.PlayerLevelPoint) * MathFunction.mc_next_levelup(aaaaa)
            player1.PlayerLevel = np.int32(MathFunction.mc_point2level(max(0, now_point + value)))
            aaaaa = int(player1.PlayerLevel)
            player1.PlayerLevelPoint = np.float32(
                (max(0, now_point + value) - MathFunction.mc_level2point(aaaaa)) / MathFunction.mc_next_levelup(aaaaa)
            )
        temp1 = string.Template("$player 的等级变为 $value1 : $value2")
        return Response.Response_Template("以下玩家的经验值发生变化：\n$msg", 1, len(entity_list)).substitute(
            msg="\n".join( (temp1.substitute(player = ID_tracker(i), value1=i.PlayerLevel, 
            value2=round(i.PlayerLevelPoint, 4)) for i in entity_list) )
        )

