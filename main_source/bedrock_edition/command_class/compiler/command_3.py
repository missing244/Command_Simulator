from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction,DataSave
from . import Selector,Rawtext,CompileError,CommandParser
from . import Quotation_String_transfor_1,ID_transfor,BlockState_Compiler,Msg_Compiler
import functools,string,random,re,math,itertools,json
from typing import Dict,Union,List,Tuple,Literal,Callable



class inputpermission :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
        permission_name = token_list[index]["token"].group() ; index += 1

        if token_list[1]["token"].group() == "query" : 
            if index >= len(token_list) : return functools.partial(cls.print, entity_get=entity_func, permission_name=permission_name)
            value = token_list[index]["token"].group()
            return functools.partial(cls.print_test, entity_get=entity_func, permission_name=permission_name, value=value)
        elif token_list[1]["token"].group() == "set" : 
            value = token_list[index]["token"].group()
            return functools.partial(cls.set, entity_get=entity_func, permission_name=permission_name, value=value)

    def print(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, permission_name:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("$player = $value") ; msg_list = []
        for i in entity_list : msg_list.append(success.substitute(player=ID_tracker(i), value=i.Permission[permission_name]))
        
        return Response.Response_Template("已查询以下玩家的的$p权限：\n$msg", 1, len(entity_list)).substitute(
            p=permission_name, msg="\n".join(msg_list)
        )
        
    def print_test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, permission_name:str, value:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        
        list1 = [ID_tracker(i) for i in entity_list if i.Permission[permission_name] == value]
        if list1 : return Response.Response_Template("以下玩家的$p权限测试成功：\n$msg", 1, len(list1)).substitute(
            p=permission_name, msg=", ".join( list1 ) )
        else : return Response.Response_Template("没有玩家的$p权限测试成功", 1, len(list1)).substitute(p=permission_name)
        
    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, permission_name:str, value:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        for i in entity_list : i.Permission[permission_name] = value
        return Response.Response_Template("以下玩家的$p权限修改为$v：\n$msg", 1, len(entity_list)).substitute(
            p=permission_name, v=value, msg=", ".join((ID_tracker(i) for i in entity_list)) )


class kick :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["type"] == "Selector" : raise CompileError("kick命令无法使用选择器",
            pos=(token_list[1]["token"].start(), token_list[-1]["token"].end()))
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        return functools.partial(cls.run, entity_get=entity_func)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        
        return Response.Response_Template("踢出了以下玩家(虚假踢出)：$entity", 1, len(entity_list)).substitute(
            count = len(entity_list),
            entity = ", ".join( (ID_tracker(i) for i in entity_list) ),
        )


class kill :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if 1 >= len(token_list) : return cls.run
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1)
        return functools.partial(cls.run, entity_get=entity_func)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        for entity in entity_list : 
            if not hasattr(entity, "Health") : game.minecraft_chunk.__remove_entity__(entity)
            else : entity.Health = np.float32(0)

        return Response.Response_Template("清除了以下实体：\n$entity", 1, len(entity_list)).substitute(
            count = len(entity_list),
            entity = ", ".join( (ID_tracker(i) for i in entity_list) ),
        )


class list_command :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        return cls.run

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread) :
        entity_list = game.minecraft_chunk.player

        return Response.Response_Template("世界内有以下玩家：\n$entity", 1, len(entity_list)).substitute(
            entity = ", ".join( (ID_tracker(i) for i in entity_list) ),
        )


class locate :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group() in ("biome", "structure") : 
            locate_mode = token_list[1]["token"].group() ; index = 2
        else : locate_mode = "structure" ; index = 1

        if locate_mode == "structure" :
            structure_name = token_list[index]["token"].group()
            if structure_name not in Constants.STRUCTURE : raise CompileError("不存在的结构ID：%s" % structure_name, 
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            return functools.partial(cls.search_structure, structure_name=structure_name)
        else :
            biome_name = token_list[index]["token"].group()
            if biome_name not in Constants.BIOME : raise CompileError("不存在的生物群系ID：%s" % biome_name, 
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
            return functools.partial(cls.search_biome, biome_name=biome_name)
    
    def search_structure(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, structure_name:str) :
        exe_start_pos = [math.floor(i) for i in execute_var["pos"]]
        exe_end_pos = list(exe_start_pos)

        exe_start_pos[0] -= 50 * 16 ; exe_start_pos[2] -= 50 * 16
        exe_end_pos[0] += 50 * 16 ; exe_end_pos[2] += 50 * 16
        
        exe_start_pos[0] = exe_start_pos[0] // 16 * 16
        exe_start_pos[2] = exe_start_pos[2] // 16 * 16
        exe_end_pos[0] = exe_end_pos[0] // 16 * 16
        exe_end_pos[2] = exe_end_pos[2] // 16 * 16

        for pos in itertools.product(range(exe_start_pos[0], exe_end_pos[0]+1, 16), range(exe_start_pos[2], exe_end_pos[2]+1, 16)) :
            aaa = game.minecraft_chunk.__select_structure__(game.minecraft_world.seed, execute_var["dimension"], pos)
            if structure_name in aaa : return Response.Response_Template("区块$pos内有指定结构", 1, 1).substitute(pos = pos)

        return Response.Response_Template("无法在限定范围内寻找到指定结构").substitute()
    
    def search_biome(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, biome_name:str) :
        exe_start_pos = [math.floor(i) for i in execute_var["pos"]]
        exe_end_pos = list(exe_start_pos)

        exe_start_pos[0] -= 50 * 16 ; exe_start_pos[2] -= 50 * 16
        exe_end_pos[0] += 50 * 16 ; exe_end_pos[2] += 50 * 16
        
        exe_start_pos[0] = exe_start_pos[0] // 16 * 16
        exe_start_pos[2] = exe_start_pos[2] // 16 * 16
        exe_end_pos[0] = exe_end_pos[0] // 16 * 16
        exe_end_pos[2] = exe_end_pos[2] // 16 * 16

        for pos in itertools.product(range(exe_start_pos[0], exe_end_pos[0]+1, 16), range(exe_start_pos[2], exe_end_pos[2]+1, 16)) :
            aaa = game.minecraft_chunk.__select_structure__(game.minecraft_world.seed, execute_var["dimension"], pos)
            if biome_name in aaa : return Response.Response_Template("区块$pos内有指定生物群系", 1, 1).substitute(pos = pos)

        return Response.Response_Template("无法在限定范围内寻找到指定生物群系").substitute()
    

class loot :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) : 
        if token_list[1]["token"].group() == "give" :
            index, entity_func_1 = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
            if token_list[index]["token"].group() == "kill" :
                index, loot_get = Selector.Selector_Compiler(_game, token_list, index+1, is_single=True)
            else : 
                loot_get = token_list[index+1]["token"].group()
                if loot_get not in _game.minecraft_ident.loot_tables : raise CompileError("不存在的战利品表ID：%s" % loot_get, 
                pos=(token_list[index+1]["token"].start(), token_list[index+1]["token"].end()))
            return functools.partial(cls.give, entity_get=entity_func_1, loot_get=loot_get)
    
    def give(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, loot_get:Union[str,Callable]) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(loot_get, str) :
            loot_get_entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
            if isinstance(loot_get_entity_list, Response.Response_Template) : return loot_get_entity_list
            loot_get = loot_get_entity_list[0].DeathLootTable if hasattr(loot_get_entity_list[0], "DeathLootTable") else ""
        
        from ... import LootTable
        for player in entity_list :
            item_list = LootTable.generate(game.minecraft_ident, loot_get)
            for item in item_list : player.__pickup_item__(item)
        