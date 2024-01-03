from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction
from . import Selector,Rawtext,CompileError,CommandParser,Quotation_String_transfor_1,ID_transfor,BlockState_Transformer,Msg_Compiler
import functools,string,random,re,math,itertools,json
from typing import Dict,Union,List,Tuple,Literal,Callable










class teleport :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        pass


class titleraw :
    #{"rawtext":[{"text":"aaa "},{"selector":"@s[rm=1]"},{"text":" bbb "},{"selector":"@s"}]}
    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if token_list[index]["token"].group() in ("clear", "reset") : 
            return functools.partial(cls.clear_or_reset, entity_get=entity_func, mode=token_list[index]["token"].group())
        elif token_list[index]["token"].group() == "times" :
            for i in range(3) :
                time_m = token_list[index+1+i]["token"]
                if int(time_m.group()) >= 0 : continue
                raise CompileError("天气时长不能为非正整数", pos=(time_m.start(), time_m.end()))
            return functools.partial(cls.set_time, entity_get=entity_func)
        elif token_list[index]["token"].group() in ("title", "subtitle", "actionbar") : 
            ttt = token_list[index]["token"].group()
            if token_list[index + 1]["type"] == "Msg" :
                aa,bb = Msg_Compiler(_game, token_list[index + 1]["token"].group(), token_list[index + 1]["token"].start())
                return functools.partial(cls.display_1, entity_get=entity_func, type1=ttt, msg=aa, search_entity=bb)
            else :
                a = json.loads( "".join( [token_list[i]["token"].group() for i in range(index + 1, len(token_list), 1)] ) )
                b = Rawtext.Rawtext_Compiler(_game, (255,0,0), a)
                return functools.partial(cls.display_2, entity_get=entity_func, type1=ttt, rawtext=b)
    
    def clear_or_reset(execute_var:COMMAND_CONTEXT, entity_get:Callable, mode:Literal["clear", "reset"]) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if mode == "clear" :
            return Response.Response_Template("已为以下玩家清除所有显示的标题：$player", 1, 1).substitute(
                player = ", ".join( (ID_tracker(i) for i in entity_list) )
            )
        elif mode == "reset" :
            return Response.Response_Template("已为以下玩家重置所有的标题设置：$player", 1, 1).substitute(
                player = ", ".join( (ID_tracker(i) for i in entity_list) )
            )

    def set_time(execute_var:COMMAND_CONTEXT, entity_get:Callable) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("已为以下玩家设置标题淡入淡出时间：$player", 1, 1).substitute(
            player = ", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def display_1(execute_var:COMMAND_CONTEXT, entity_get:Callable, type1:Literal["title", "subtitle", "actionbar"], msg:str, search_entity:List[Callable]) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        list1 = [i(execute_var) for i in search_entity]
        msg_temp = msg % tuple([
            (", ".join( (ID_tracker(i) for i in entities) ) if isinstance(entities, list) else "") for entities in list1
        ])
        return Response.Response_Template("已为以下玩家设置 $type1 标题：$player\n$msg", 1, 1).substitute(
            type1 = type1,
            player = ", ".join( (ID_tracker(i) for i in entity_list) ),
            msg = msg_temp
        )

    def display_2(execute_var:COMMAND_CONTEXT, entity_get:Callable, type1:Literal["title", "subtitle", "actionbar"], rawtext:Callable) :
        entity_list = entity_get(execute_var)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("已为以下玩家设置 $type1 标题：$player\n$msg", 1, 1).substitute(
            type1 = type1,
            player = ", ".join( (ID_tracker(i) for i in entity_list) ),
            msg = rawtext(execute_var)
        )


class toggledownfall :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        return functools.partial(cls.change_weather, game=_game)
    
    def change_weather(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread) : 
        time = random.randint(10000,30000)
        if game.minecraft_world.rain_time or game.minecraft_world.thunder_time :
            game.minecraft_world.sunny_time = np.int32(time)
            game.minecraft_world.rain_time = np.int32(0)
            game.minecraft_world.thunder_time = np.int32(0)
        else :
            game.minecraft_world.sunny_time = np.int32(0)
            if random.randint(0,1) : 
                game.minecraft_world.thunder_time = np.int32(0)
                game.minecraft_world.rain_time = np.int32(time)
            else : 
                game.minecraft_world.rain_time = np.int32(0)
                game.minecraft_world.thunder_time = np.int32(time)
        aaaa = Response.Response_Template("将天气更改为 $weather", 1, 1)
        if game.minecraft_world.sunny_time > 0 : return aaaa.substitute(weather="clear")
        elif game.minecraft_world.rain_time > 0 : return aaaa.substitute(weather="rain")
        elif game.minecraft_world.thunder_time > 0 : return aaaa.substitute(weather="thunder")


class volumearea :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group() == "add" : 
            volume_id = Quotation_String_transfor_1(token_list[2]["token"].group())
            if volume_id not in _game.minecraft_ident.volumeareas : 
                raise CompileError("不存在的功能域 ID： %s" % volume_id, 
                pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
            from_pos = [token_list[3+i]["token"].group() for i in range(3)]
            to_pos = [token_list[6+i]["token"].group() for i in range(3)]
            volume_name = Quotation_String_transfor_1(token_list[9]["token"].group())
            return functools.partial(cls.add_area, game=_game, id=volume_id, from_pos=from_pos, to_pos=to_pos, name=volume_name)
        elif token_list[1]["token"].group() == "list" : 
            if 2 >= token_list.__len__() : return functools.partial(cls.print_area, game=_game)
            else : return functools.partial(cls.print_area, game=_game, print_all=True)
        elif token_list[1]["token"].group() == "remove" : 
            if token_list[2]["type"] == "Volumearea_Name" : return functools.partial(cls.remove_area, game=_game, 
                name=Quotation_String_transfor_1(token_list[2]["token"].group()))
            else : return functools.partial(cls.remove_area, game=_game, pos=[token_list[2+i]["token"].group() for i in range(3)])
        elif token_list[1]["token"].group() == "remove_all" : 
            return functools.partial(cls.remove_area, game=_game, remove_all=True)
    
    def add_area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, id:str, from_pos:List[str],
                 to_pos:List[str], name:str) :
        if name in game.minecraft_chunk.volumearea : 
            return Response.Response_Template("已存在功能域 $name").substitute(name = name)

        start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], from_pos, execute_var["rotate"])]
        end_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], to_pos, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos, end_pos)) :
            if pos_1 > pos_2 : start_pos[index] = pos_2; end_pos[index] = pos_1
        template1 = {"dimension":execute_var["dimension"], "id":id, "effect_area":[(start_pos[0], start_pos[2]), (end_pos[0], end_pos[2])]}

        game.minecraft_chunk.volumearea[name] = template1
        return Response.Response_Template("成功添加了功能域 $name", 1, 1).substitute(name = name)

    def print_area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, print_all:bool=False) :
        list1 = []
        temp1 = string.Template("维度 $dimension 功能域 $name : $pos1 ~ $pos2")
        for key,value in game.minecraft_chunk.volumearea.items() :
            if not print_all and value["dimension"] != execute_var["dimension"] : continue
            list1.append( temp1.substitute(dimension=value["dimension"], name=key, 
                pos1=tuple(value["effect_area"][0]), pos2=tuple(value["effect_area"][1])) )
        return Response.Response_Template("$len 个功能域正在运行：\n$detial", 1, 1).substitute(len=len(list1), detial = "\n".join(list1))

    def remove_area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]=None, 
                    name:str=None, remove_all:bool=None) :
        remove_list = []
        if pos :
            start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
            for key,value in game.minecraft_chunk.volumearea.items() :
                if not(value["effect_area"][0][0] <= start_pos[0] <= value["effect_area"][1][0]) : continue
                if not(value["effect_area"][0][1] <= start_pos[2] <= value["effect_area"][1][1]) : continue
                remove_list.append(key)
        if name :
            if name not in game.minecraft_chunk.volumearea : return Response.Response_Template("不存在功能域 $name").substitute(name = name)
            remove_list.append(name)
        if remove_all : remove_list.extend(list(game.minecraft_chunk.volumearea))
        
        if len(remove_list) == 0 : return Response.Response_Template("没有可以移除的功能域").substitute()
        for i in remove_list : del game.minecraft_chunk.volumearea[i]
        return Response.Response_Template("已移除功能域：$name", 1, 1).substitute(name = ", ".join(remove_list))


class tell :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        aa,bb = Msg_Compiler(_game, token_list[index]["token"].group(), token_list[index]["token"].start())
        return functools.partial(cls.send_msg, entity_get=entity_func, msg=aa, search_entity=bb)

    def send_msg(execute_var:COMMAND_CONTEXT, entity_get:Callable, msg:str, search_entity:List[Callable]) :
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

    def modify_level(execute_var:COMMAND_CONTEXT, entity_get:Callable=None, value:int=0) :
        entity_list = entity_get(execute_var) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        for player1 in entity_list : player1.PlayerLevel = max(np.int32(0), player1.PlayerLevel + value)
        temp1 = string.Template("$player 的等级变为 $value")
        return Response.Response_Template("以下玩家的经验值发生变化：\n$msg", 1, len(entity_list)).substitute(
            msg="\n".join( (temp1.substitute(player = ID_tracker(i), value=i.PlayerLevel) for i in entity_list) )
        )

    def modify_point(execute_var:COMMAND_CONTEXT, entity_get:Callable=None, value:int=0) :
        entity_list = entity_get(execute_var) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

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

