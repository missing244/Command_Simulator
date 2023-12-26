from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction
from . import Selector,CompileError,CommandParser
import functools,string,random,re
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














class tell :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        msg_temp = token_list[index]["token"].group() ; msg_temp_start = token_list[index]["token"].start()
        search_entity_list = []
        re_search = list(re.compile("@(p|a|r|e|s|initiator)").finditer(msg_temp))
        re_search.reverse()
        for re_obj in re_search :
            token_1 = Selector_Parser.parser(msg_temp[re_obj.start():], (100,0,0))
            if isinstance(token_1, tuple) : 
                if hasattr(token_1[1], "pos") : 
                    token_1[1].pos = tuple([i+re_obj.start()+msg_temp_start for i in token_1[1].pos])
                raise token_1[1]
            msg_temp = replace_str(msg_temp, re_obj.start()+token_1[0]["token"].start(), 
                re_obj.start()+token_1[-2]["token"].end(), "%s")
            search_entity_list.append( Selector.Selector_Compiler(_game, token_1, 0)[1] )
        search_entity_list.reverse()
        return functools.partial(cls.send_msg, entity_get=entity_func, msg=msg_temp, search_entity=search_entity_list)

    def send_msg(execute_var:COMMAND_CONTEXT, entity_get:functools.partial, msg:str, search_entity:List[Callable]) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        list1 = [i(execute_var) for i in search_entity]
        msg_temp = msg % tuple([
            (", ".join( (ID_tracker(i) for i in entities) ) if isinstance(entities, list) else "") for entities in list1
        ])
        return Response.Response_Template("$player1 向以下玩家发送了悄悄话：\n$player2\n$msg", 1, 1).substitute(
            player1 = ID_tracker(execute_var["executer"]),
            player2 = ", ".join( (ID_tracker(i) for i in entity_list) ),
            msg = msg_temp
        )


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

