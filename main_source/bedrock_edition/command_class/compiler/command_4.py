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
