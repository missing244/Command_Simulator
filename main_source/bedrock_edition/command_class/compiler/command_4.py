from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction,DataSave,LootTable,EntityComponent
from . import Selector,Rawtext,CompileError,CommandParser,Command0
from . import Quotation_String_transfor_1,ID_transfor,BlockState_Compiler,Msg_Compiler,ItemComponent_Compiler
import functools,string,random,math,itertools,json
from typing import Dict,Union,List,Tuple,Literal,Callable


class hud :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        mode = token_list[index]["token"].group()
        return functools.partial(cls.run, entity_get=entity_func, mode=mode)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, mode:Literal["hide","reset"], hud_element:str="all") :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        return Response.Response_Template("以下玩家指定的hud已$mode：\n$entity", 1, len(entity_list)).substitute(
            mode = "隐藏" if mode == "hide" else "显示",
            entity = ", ".join( (ID_tracker(i) for i in entity_list) ),
        )

class scriptevent :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        message_id = token_list[1]["token"].group()
        if ":" not in message_id : raise CompileError("需要提供自定义命名空间", 
            pos=(token_list[1]["token"].start(), token_list[1]["token"].end()))
        if "minecraft:" in message_id[0:10] : raise CompileError("需要提供非minecraft的自定义命名空间", 
            pos=(token_list[1]["token"].start(), token_list[1]["token"].end()))
        message = token_list[2]["token"].group()
        return functools.partial(cls.run, message_id=message_id, message=message)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, message_id:str, message:str) :
        return Response.Response_Template("已发送脚本事件（仅模拟）", 1, 1).substitute()

class aimassist :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if token_list[index]["token"].group() == "clear" : return functools.partial(cls.clear, entity_get=entity_func)
        elif token_list[index]["token"].group() == "set" :
            index += 1 ; x_angle = float(token_list[index]["token"].group())
            if not(10 <= x_angle <= 90) : raise CompileError("垂直朝向角需在10和90之间", 
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            if index+1 >= len(token_list) : return functools.partial(cls.set, entity_get=entity_func)

            index += 1 ; y_angle = float(token_list[index]["token"].group())
            if not(10 <= y_angle <= 90) : raise CompileError("水平朝向角需在10和90之间", 
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            if index+1 >= len(token_list) : return functools.partial(cls.set, entity_get=entity_func)

            index += 1 ; distance = float(token_list[index]["token"].group())
            if not(1 <= distance <= 16) : raise CompileError("交互距离需在1和16之间", 
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            return functools.partial(cls.set, entity_get=entity_func)

    def clear(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        for i,_ in enumerate(entity_list) : entity_list[i] = ID_tracker(entity_list[i])

        return Response.Response_Template("已清除以下玩家的辅助瞄准：\n$player", 1, len(entity_list)).substitute(
            player=", ".join(entity_list)
        )

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        for i,_ in enumerate(entity_list) : entity_list[i] = ID_tracker(entity_list[i])

        return Response.Response_Template("已修改以下玩家的辅助瞄准：\n$player", 1, len(entity_list)).substitute(
            player=", ".join(entity_list)
        )

class place :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index = 1
        if token_list[index]["token"].group() == "jigsaw" : 
            index += 3 ; MaxDepth = int(token_list[index]["token"].group())
            if not(1 <= MaxDepth <= 7) : raise CompileError("最大深度需在1和7之间", 
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            if index + 1 >= len(token_list) : return functools.partial(cls.jigsaw, pos=["~", "~", "~"])

            index += 1 ; location = [token_list[i]["token"].group() for i in range(index, index+3, 1)]
            return functools.partial(cls.jigsaw, pos=location)
        elif token_list[index]["token"].group() == "structure" :
            index += 2
            if index >= len(token_list) : return functools.partial(cls.structure, pos=["~", "~", "~"])
            
            location = [token_list[i]["token"].group() for i in range(index, index+3, 1)]
            return functools.partial(cls.structure, pos=location)
        elif token_list[index]["token"].group() == "feature" :
            index += 2
            if index >= len(token_list) : return functools.partial(cls.feature, pos=["~", "~", "~"])
            
            location = [token_list[i]["token"].group() for i in range(index, index+3, 1)]
            return functools.partial(cls.feature, pos=location)
        elif token_list[index]["token"].group() == "featurerule" :
            index += 2
            if index >= len(token_list) : return functools.partial(cls.featurerule, pos=["~", "~", "~"])
            
            location = [token_list[i]["token"].group() for i in range(index, index+3, 1)]
            return functools.partial(cls.featurerule, pos=location)

    def jigsaw(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]) :
        spawn_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        for i in range(3) : spawn_pos[i] = int(spawn_pos[i])

        return Response.Response_Template("已在$x, $y, $z位置生成拼图（仅模拟）", 1, 1).substitute(
            x = spawn_pos[0], y = spawn_pos[1], z = spawn_pos[2]
        )

    def structure(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]) :
        spawn_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        for i in range(3) : spawn_pos[i] = int(spawn_pos[i])

        return Response.Response_Template("已在$x, $y, $z位置生成结构（仅模拟）", 1, 1).substitute(
            x = spawn_pos[0], y = spawn_pos[1], z = spawn_pos[2]
        )

    def feature(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]) :
        spawn_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        for i in range(3) : spawn_pos[i] = int(spawn_pos[i])

        return Response.Response_Template("已在$x, $y, $z位置生成地物（仅模拟）", 1, 1).substitute(
            x = spawn_pos[0], y = spawn_pos[1], z = spawn_pos[2]
        )

    def featurerule(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]) :
        spawn_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        for i in range(3) : spawn_pos[i] = int(spawn_pos[i])

        return Response.Response_Template("已在$x, $y, $z位置生成规则地物（仅模拟）", 1, 1).substitute(
            x = spawn_pos[0], y = spawn_pos[1], z = spawn_pos[2]
        )
