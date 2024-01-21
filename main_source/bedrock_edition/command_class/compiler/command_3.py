from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction,DataSave,LootTable,EntityComponent
from . import Selector,Rawtext,CompileError,CommandParser,Command0
from . import Quotation_String_transfor_1,ID_transfor,BlockState_Compiler,Msg_Compiler,ItemComponent_Compiler
import functools,string,random,math,itertools,json
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
        
        return Response.Response_Template("已查询以下玩家的$p权限：\n$msg", 1, len(entity_list)).substitute(
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
            if not hasattr(entity, "Health") : game.minecraft_chunk.__remove_entity__(entity, scoreboard_obj=game.minecraft_scoreboard)
            else : entity.Health = np.float32(0)

        return Response.Response_Template("清除了$count个实体：\n$entity", 1, len(entity_list)).substitute(
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
            aaa = game.minecraft_chunk.__select_biome__(game.minecraft_world.seed, execute_var["dimension"], pos)
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
                loot_get = "loot_tables/%s" % Quotation_String_transfor_1(token_list[index+1]["token"].group())
                if loot_get not in _game.minecraft_ident.loot_tables : raise CompileError("不存在的战利品表ID：%s" % loot_get, 
                pos=(token_list[index+1]["token"].start(), token_list[index+1]["token"].end()))
            return functools.partial(cls.give, entity_get=entity_func_1, loot_get=loot_get)
        if token_list[1]["token"].group() in ("insert", "spawn") :
            index, pos = 5, [token_list[i]["token"].group() for i in range(2,5,1)]
            if token_list[index]["token"].group() == "kill" :
                index, loot_get = Selector.Selector_Compiler(_game, token_list, index+1, is_single=True)
            else : 
                loot_get = "loot_tables/%s" % Quotation_String_transfor_1(token_list[index+1]["token"].group())
                if loot_get not in _game.minecraft_ident.loot_tables : raise CompileError("不存在的战利品表ID：%s" % loot_get, 
                pos=(token_list[index+1]["token"].start(), token_list[index+1]["token"].end()))
            return functools.partial(cls.insert if token_list[1]["token"].group() == "insert" else cls.spawn, pos=pos, loot_get=loot_get)
        if token_list[1]["token"].group() == "replace" :
            if token_list[2]["token"].group() == "block" :
                index, pos = 7, [token_list[i]["token"].group() for i in range(3,6,1)]
                slot_id = int(token_list[index]["token"].group()) ; index += 1
                if slot_id < 0 : raise CompileError("栏位索引不能为负数", 
                    pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
                if token_list[index]["type"] == "Count" :
                    slot_count = int(token_list[index]["token"].group()) ; index += 1
                    if slot_count <= 0 : raise CompileError("栏位范围不能为负数或0", 
                        pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
                else : slot_count = 1
                if token_list[index]["token"].group() == "kill" :
                    index, loot_get = Selector.Selector_Compiler(_game, token_list, index+1, is_single=True)
                else : 
                    loot_get = "loot_tables/%s" % Quotation_String_transfor_1(token_list[index+1]["token"].group())
                    if loot_get not in _game.minecraft_ident.loot_tables : raise CompileError("不存在的战利品表ID：%s" % loot_get, 
                    pos=(token_list[index+1]["token"].start(), token_list[index+1]["token"].end()))
                return functools.partial(cls.replace_block, pos=pos, slot_id=slot_id, slot_count=slot_count, loot_get=loot_get)
            if token_list[2]["token"].group() == "entity" :
                index, entity_func_1 = Selector.Selector_Compiler(_game, token_list, 3, is_player=True)
                slot = token_list[index]["token"].group() ; index += 1
                slot_id = int(token_list[index]["token"].group()) ; index += 1
                if slot_id < 0 : raise CompileError("栏位索引不能为负数", 
                    pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
                if token_list[index]["type"] == "Count" :
                    slot_count = int(token_list[index]["token"].group()) ; index += 1
                    if slot_count <= 0 : raise CompileError("栏位索引不能为负数或0", 
                        pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
                else : slot_count = 1
                if token_list[index]["token"].group() == "kill" :
                    index, loot_get = Selector.Selector_Compiler(_game, token_list, index+1, is_single=True)
                else : 
                    loot_get = "loot_tables/%s" % token_list[index+1]["token"].group()
                    if loot_get not in _game.minecraft_ident.loot_tables : raise CompileError("不存在的战利品表ID：%s" % loot_get, 
                    pos=(token_list[index+1]["token"].start(), token_list[index+1]["token"].end()))
                return functools.partial(cls.replace_entity, entity_get=entity_func_1, slot=slot, slot_index=slot_id, slot_count=slot_count, loot_get=loot_get)

    def give(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, loot_get:Union[str,Callable]) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(loot_get, str) :
            loot_get_entity_list:List[BaseNbtClass.entity_nbt] = loot_get(execute_var, game)
            if isinstance(loot_get_entity_list, Response.Response_Template) : return loot_get_entity_list
            loot_get = loot_get_entity_list[0].DeathLootTable if hasattr(loot_get_entity_list[0], "DeathLootTable") else ""

        item_count:List[int] = []
        for player in entity_list :
            item_list = LootTable.generate(loot_get)
            for item in item_list : player.__pickup_item__(item)
            item_count.append( len(item_list) )

        success = string.Template("$player 掉落了 $count 个物品") ; success_list:List[str] = []
        for index,player in enumerate(entity_list) : 
            success_list.append(success.substitute(player=ID_tracker(player), count=item_count[index]))

        return Response.Response_Template("已为以下玩家给予战利品：\n$msg", 1, sum(item_count)).substitute(
            msg="\n".join(success_list)
        )
        
    def insert(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str], loot_get:Union[str,Callable]) :
        block_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        if  not game.minecraft_chunk.____in_build_area____(execute_var["dimension"], block_pos) or \
            not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], block_pos) :
            return Response.Response_Template("$pos位于世界外或未加载区块").substitute(pos=tuple(block_pos))
        block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], block_pos)
        if (block_nbt is None) or ("Items" not in block_nbt) :
            return Response.Response_Template("$pos的方块并不是容器").substitute(pos=tuple(block_pos))
        if not isinstance(loot_get, str) :
            loot_get_entity_list:List[BaseNbtClass.entity_nbt] = loot_get(execute_var, game)
            if isinstance(loot_get_entity_list, Response.Response_Template) : return loot_get_entity_list
            loot_get = loot_get_entity_list[0].DeathLootTable if hasattr(loot_get_entity_list[0], "DeathLootTable") else ""

        item_list = LootTable.generate(loot_get)
        for item in item_list : game.minecraft_chunk.__block_pickup_item__(execute_var["dimension"],block_pos,item)

        return Response.Response_Template("$pos方块内填充了$count个战利品", 1, len(item_list)).substitute(
            pos=tuple(block_pos), count=len(item_list)
        )

    def spawn(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str], loot_get:Union[str,Callable]) :
        spawn_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        if not isinstance(loot_get, str) :
            loot_get_entity_list:List[BaseNbtClass.entity_nbt] = loot_get(execute_var, game)
            if isinstance(loot_get_entity_list, Response.Response_Template) : return loot_get_entity_list
            loot_get = loot_get_entity_list[0].DeathLootTable if hasattr(loot_get_entity_list[0], "DeathLootTable") else ""

        item_list = LootTable.generate(loot_get)
        for item in item_list : 
            item_entity = item.__change_to_entity__(execute_var["dimension"], spawn_pos)
            game.minecraft_chunk.__add_entity__(item_entity)

        return Response.Response_Template("$pos生成了$count个战利品", 1, len(item_list)).substitute(
            pos=tuple(spawn_pos), count=len(item_list)
        )

    def replace_block(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str], slot_id:int,
                      slot_count:int, loot_get:Union[str,Callable]) :
        block_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        if  not game.minecraft_chunk.____in_build_area____(execute_var["dimension"], block_pos) or \
            not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], block_pos) :
            return Response.Response_Template("$pos位于世界外或未加载区块").substitute(pos=tuple(block_pos))
        block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], block_pos)
        if (block_nbt is None) or ("Items" not in block_nbt) :
            return Response.Response_Template("$pos的方块并不是容器").substitute(pos=tuple(block_pos))
        if not(0 < slot_id <= len(block_nbt["Items"])) : return Response.Response_Template("指定的栏位位置超过容器的容量").substitute()
        if not isinstance(loot_get, str) :
            loot_get_entity_list:List[BaseNbtClass.entity_nbt] = loot_get(execute_var, game)
            if isinstance(loot_get_entity_list, Response.Response_Template) : return loot_get_entity_list
            loot_get = loot_get_entity_list[0].DeathLootTable if hasattr(loot_get_entity_list[0], "DeathLootTable") else ""

        item_list = LootTable.generate(loot_get)
        for index in range(min(len(item_list), slot_count)) : block_nbt["Items"][index] = item_list[index]

        return Response.Response_Template("$pos方块内填充了$count个战利品", 1, len(item_list)).substitute(
            pos=tuple(block_pos), count=len(item_list)
        )

    def replace_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, 
                       slot:str, slot_index:int, slot_count:int, loot_get:Union[str,Callable]) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(loot_get, str) :
            loot_get_entity_list:List[BaseNbtClass.entity_nbt] = loot_get(execute_var, game)
            if isinstance(loot_get_entity_list, Response.Response_Template) : return loot_get_entity_list
            loot_get = loot_get_entity_list[0].DeathLootTable if hasattr(loot_get_entity_list[0], "DeathLootTable") else ""

        success = string.Template("$player 掉落了 $count 个物品") ; success_list:List[str] = []
        for entity in entity_list :
            if slot == "slot.weapon.mainhand" : item_list = (entity.Weapon,0) if hasattr(entity, "Weapon") else None
            elif slot == "slot.weapon.offhand" : item_list = (entity.Weapon,1) if hasattr(entity, "Weapon") else None
            elif slot == "slot.armor.head" : item_list = (entity.Armor,0) if hasattr(entity, "Armor") else None
            elif slot == "slot.armor.chest" : item_list = (entity.Armor,1) if hasattr(entity, "Armor") else None
            elif slot == "slot.armor.legs" : item_list = (entity.Armor,2) if hasattr(entity, "Armor") else None
            elif slot == "slot.armor.feet" : item_list = (entity.Armor,3) if hasattr(entity, "Armor") else None
            elif slot == "slot.enderchest" : item_list = (entity.EnderChest,None) if hasattr(entity, "EnderChest") else None
            elif slot == "slot.hotbar" : item_list = (entity.HotBar,None) if hasattr(entity, "HotBar") else None
            elif slot == "slot.inventory" : item_list = (entity.Inventory["Items"],None) if hasattr(entity, "Inventory") else None
            elif slot == "slot.saddle" : item_list = (entity.Equippable, 0, "Item") if hasattr(entity, "Equippable") else None
            elif slot == "slot.armor" : item_list = (entity.Equippable, 1, "Item") if hasattr(entity, "Equippable") else None
            elif slot == "slot.chest" : item_list = (entity.Inventory["Items"], None) if hasattr(entity, "Inventory") and hasattr(entity, "isChested") and entity.isChested else None
            elif slot == "slot.equippable" : item_list = (entity.Equippable, None, "Item") if hasattr(entity, "Equippable") else None
            if item_list is None : continue
            if not(0 < slot_index <= len(item_list[0])) : continue

            loot_item_list = LootTable.generate(loot_get)
            if not loot_item_list : 
                success_list.append(success.substitute(player=ID_tracker(entity), count=len(loot_item_list))) ; continue
            for index,item in enumerate(loot_item_list) : 
                if slot in Constants.GAME_DATA["accept_item"] and item.Identifier not in Constants.GAME_DATA["accept_item"][slot] : continue
                if item_list[1] is not None :
                    if len(item_list) == 2 : item_list[0][item_list[1]] = loot_item_list[0]
                    else : item_list[0][item_list[1]]["Item"] = loot_item_list[0]
                else :
                    if len(item_list) == 2 : item_list[0][slot_index+index] = item
                    else : item_list[0][slot_index+index]["Item"] = item
                    if index >= (slot_count - 1) : break
            success_list.append(success.substitute(player=ID_tracker(entity), count=index+1))

        if success_list : return Response.Response_Template("已为以下实体给予战利品：\n$msg", 1, len(success_list)).substitute(
            msg="\n".join(success_list))
        else : return Response.Response_Template("没有实体被给予战利品").substitute()


class me :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        aa,bb = Msg_Compiler(_game, token_list[1]["token"].group(), token_list[1]["token"].start())
        return functools.partial(cls.send_msg, msg=aa, search_entity=bb)

    def send_msg(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, msg:str, search_entity:List[Callable]) :
        list1 = [i(execute_var, game) for i in search_entity]
        msg_temp = msg % tuple([
            (", ".join( (ID_tracker(i) for i in entities) ) if isinstance(entities, list) else "") for entities in list1
        ])
        return Response.Response_Template("$player1 发送了消息：\n$msg", 1, 1).substitute(
            player1 = ID_tracker(execute_var["executer"]),
            msg = msg_temp
        )


class mobevent :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        mobevent_name = token_list[1]["token"].group()
        if 2 >= len(token_list) : return functools.partial(cls.set, mobevent_name=mobevent_name)

        value = ("false","true").index(token_list[2]["token"].group())
        return functools.partial(cls.set, mobevent_name=mobevent_name, value=value)

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, mobevent_name:str, value:Union[bool,int]=None) :
        if value is None : return Response.Response_Template("生物事件 $rule 为 $value1", 1, 1).substitute(
            rule=mobevent_name, value1=game.minecraft_world.mob_event[mobevent_name])
        type1 = type(game.minecraft_world.mob_event[mobevent_name])
        game.minecraft_world.mob_event[mobevent_name] = type1(value)
        return Response.Response_Template("生物事件 $rule 已修改为 $value1", 1, 1).substitute(
            rule=mobevent_name, value1=game.minecraft_world.mob_event[mobevent_name]
        )


class music :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group() in ("play", "queue") :
            music_id = Quotation_String_transfor_1(token_list[2]["token"].group())
            if music_id not in _game.minecraft_ident.musics : raise CompileError("不存在的音乐ID：%s" % music_id, 
                pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
            if 3 >= len(token_list) : return functools.partial(cls.play_and_queue, music_name=music_id)
            volume = float(token_list[3]["token"].group())
            if not(0 <= volume <= 1) : raise CompileError("音量应该在 0~1 范围内", 
                pos=(token_list[3]["token"].start(), token_list[3]["token"].end()))
            if 4 >= len(token_list) : return functools.partial(cls.play_and_queue, music_name=music_id)
            fade = float(token_list[4]["token"].group())
            if not(0 <= fade <= 10) : raise CompileError("淡入淡出时间应该在 0~10 范围内", 
                pos=(token_list[4]["token"].start(), token_list[4]["token"].end()))
            return functools.partial(cls.play_and_queue, music_name=music_id)
        elif token_list[1]["token"].group() == "stop" :
            if 2 >= len(token_list) : return cls.stop
            fade = float(token_list[2]["token"].group())
            if not(0 <= fade <= 10) : raise CompileError("淡入淡出时间应该在 0~10 范围内", 
                pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
            return cls.stop
        elif token_list[1]["token"].group() == "volume" :
            volume = float(token_list[2]["token"].group())
            if not(0 <= volume <= 1) : raise CompileError("音量应该在 0~1 范围内", 
                pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
            return functools.partial(cls.set_volume, volume=volume)

    def play_and_queue(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, music_name:str) :
        game.minecraft_chunk.music_stack.append(music_name)
        return Response.Response_Template("已添加了音乐 $value1", 1, 1).substitute(value1=music_name)

    def stop(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread) :
        if game.minecraft_chunk.music_stack :
            aa = game.minecraft_chunk.music_stack.pop(0)
            return Response.Response_Template("已添加了音乐 $value1", 1, 1).substitute(value1=aa)
        else : return Response.Response_Template("不存在播放的音乐").substitute()
    
    def set_volume(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, volume:float) :
        return Response.Response_Template("已将音量设置为 $value1", 1, 1).substitute(value1=volume)


class particle :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        particle_id = Quotation_String_transfor_1(token_list[1]["token"].group())
        if particle_id not in _game.minecraft_ident.particles : raise CompileError("不存在的粒子ID：%s" % particle_id, 
            pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
        if 2 >= len(token_list) : return functools.partial(cls.run, particle_id=particle_id)
        pos = [token_list[i]["token"].group() for i in range(2,5,1)]
        return functools.partial(cls.run, particle_id=particle_id, pos=pos)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, particle_id:str, pos:List[str]=["~","~","~"]) :
        spawn_pos = [float(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
        
        now_time = str(game.minecraft_world.game_time + 40)
        particle_alive = game.runtime_variable.particle_alive
        if now_time not in particle_alive[execute_var["dimension"]] :
            particle_alive[execute_var["dimension"]][now_time] = []
        particle_alive[execute_var["dimension"]][now_time].append({"id":particle_id, "pos":spawn_pos})

        return Response.Response_Template("已在 $pos 生成了粒子 $name", 1, 1).substitute(pos=tuple(spawn_pos), name=particle_id)


class playanimation :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1)
        animation_id = token_list[index]["token"].group() ; index += 1
        if animation_id not in _game.minecraft_ident.animations : raise CompileError("不存在的动画ID：%s" % animation_id, 
            pos=(token_list[2]["token"].start(), token_list[2]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.run, entity_get=entity_func)
        controller_id_1 = token_list[index]["token"].group() ; index += 3
        if controller_id_1 not in _game.minecraft_ident.animation_controllers : raise CompileError("不存在的动画控制器ID：%s" % controller_id_1, 
            pos=(token_list[index-3]["token"].start(), token_list[index-3]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.run, entity_get=entity_func)
        controller_id_2 = token_list[index]["token"].group()
        if controller_id_2 not in _game.minecraft_ident.animation_controllers : raise CompileError("不存在的动画控制器ID：%s" % controller_id_2, 
            pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        return functools.partial(cls.run, entity_get=entity_func)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("动画已发送至客户端播放", 1, 1).substitute()


class playsound :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        sound_id = Quotation_String_transfor_1(token_list[1]["token"].group())
        if sound_id not in _game.minecraft_ident.sounds : raise CompileError("不存在的声音ID：%s" % sound_id, 
            pos=(token_list[1]["token"].start(), token_list[1]["token"].end()))
        if 2 >= len(token_list) : return cls.run

        index, entity_func = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
        if index >= len(token_list) : return functools.partial(cls.run, entity_get=entity_func)

        pos = [token_list[i]["token"].group() for i in range(index,index+3,1)] ; index += 3
        if index >= len(token_list) : return functools.partial(cls.run, entity_get=entity_func, pos=pos)

        volume = float(token_list[index]["token"].group()) ; index += 1
        if volume < 0 : raise CompileError("音量应该为非负数", 
            pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.run, entity_get=entity_func, pos=pos)

        pitch = float(token_list[index]["token"].group()) ; index += 1
        if not(0 <= pitch <= 2) : raise CompileError("音调应该在 0~2 的范围内", 
            pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        if index >= len(token_list) : return functools.partial(cls.run, entity_get=entity_func, pos=pos)

        min_volume = float(token_list[index]["token"].group()) ; index += 1
        if not(0 <= min_volume <= 1) : raise CompileError("最小音量应该在 0~1 的范围内", 
            pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
        return functools.partial(cls.run, entity_get=entity_func, pos=pos)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None, pos:List[str]=["~","~","~"]) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
        
        spawn_pos = [float(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
        
        return Response.Response_Template("在$pos为以下玩家播放声音：\n$player", 1, 1).substitute(
            pos=tuple(spawn_pos), player = ", ".join( (ID_tracker(i) for i in entity_list) )
        )


class replaceitem :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group() == "block" :
            pos = [token_list[i]["token"].group() for i in range(2,5,1)] ; index = 6
            slot_id = int(token_list[index]["token"].group()) ; index += 1
            if token_list[index]["type"] == "Old_Item_Handling" :
                replace_mode = token_list[index]["token"].group() ; index += 1
            else : replace_mode = "destroy"
            item_id = ID_transfor(token_list[index]["token"].group()) ; index += 1
            if item_id not in _game.minecraft_ident.items : raise CompileError("不存在的物品ID：%s" % item_id, 
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : 
                return functools.partial(cls.replace_block, pos=pos, slot_id=slot_id, item_id=item_id, replace_mode=replace_mode)

            amount = int(token_list[index]["token"].group()) ; index += 1
            if not(0 <= amount <= 64) : raise CompileError("数量应该在 0~64 的范围内",
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : 
                return functools.partial(cls.replace_block, pos=pos, slot_id=slot_id, item_id=item_id, replace_mode=replace_mode, amount=amount)

            data = int(token_list[index]["token"].group()) ; index += 1
            if not(0 <= data <= 32767) : raise CompileError("数据值应该在 0~32767 的范围内", 
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : 
                return functools.partial(cls.replace_block, pos=pos, slot_id=slot_id, item_id=item_id, replace_mode=replace_mode, amount=amount, data=data)
            
            item_nbt = ItemComponent_Compiler(_game, token_list, index)
            return functools.partial(cls.replace_block, pos=pos, slot_id=slot_id, item_id=item_id, replace_mode=replace_mode, amount=amount, data=data, item_nbt=item_nbt[1])    
        if token_list[1]["token"].group() == "entity" :
            index, entity_func = Selector.Selector_Compiler(_game, token_list, 2)
            slot_type = token_list[index]["token"].group() ; index += 1
            slot_id = int(token_list[index]["token"].group()) ; index += 1
            if token_list[index]["type"] == "Old_Item_Handling" :
                replace_mode = token_list[index]["token"].group() ; index += 1
            else : replace_mode = "destroy"
            item_id = ID_transfor(token_list[index]["token"].group()) ; index += 1
            if item_id not in _game.minecraft_ident.items : raise CompileError("不存在的物品ID：%s" % item_id, 
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : return functools.partial(cls.replace_entity, entity_get=entity_func, slot=slot_type,
                slot_id=slot_id, item_id=item_id, replace_mode=replace_mode)

            amount = int(token_list[index]["token"].group()) ; index += 1
            if not(0 <= amount <= 64) : raise CompileError("数量应该在 0~64 的范围内",
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : return functools.partial(cls.replace_entity, entity_get=entity_func, slot=slot_type,
                slot_id=slot_id, item_id=item_id, replace_mode=replace_mode, amount=amount)

            data = int(token_list[index]["token"].group()) ; index += 1
            if not(0 <= data <= 32767) : raise CompileError("数据值应该在 0~32767 的范围内", 
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : return functools.partial(cls.replace_entity, entity_get=entity_func, slot=slot_type,
                slot_id=slot_id, item_id=item_id, replace_mode=replace_mode, amount=amount, data=data)
            
            item_nbt = ItemComponent_Compiler(_game, token_list, index)
            return functools.partial(cls.replace_entity, entity_get=entity_func, slot=slot_type, slot_id=slot_id, item_id=item_id, 
            replace_mode=replace_mode, amount=amount, data=data, item_nbt=item_nbt[1])

    def replace_block(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str], slot_id:int, item_id:str, 
                      replace_mode:Literal["keep","destroy"]="destroy", amount:int=1, data:int=0, item_nbt:dict={}) :
        block_pos = [float(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
        if  not game.minecraft_chunk.____in_build_area____(execute_var["dimension"], block_pos) or \
            not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], block_pos) :
            return Response.Response_Template("$pos位于世界外或未加载区块").substitute(pos=tuple(block_pos))
        block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], block_pos)
        if (block_nbt is None) or ("Items" not in block_nbt) :
            return Response.Response_Template("$pos的方块并不是容器").substitute(pos=tuple(block_pos))
        if not(0 < slot_id <= len(block_nbt["Items"])) : return Response.Response_Template("指定的栏位位置超过容器的容量").substitute()

        if item_id in Constants.GAME_DATA['max_count_1_item'] : max_count = 1
        elif item_id in Constants.GAME_DATA['max_count_16_item'] : max_count = 16
        else : max_count = 64
        item_obj = BaseNbtClass.item_nbt().__create__(item_id, min(amount, max_count), data, item_nbt)
        if replace_mode == "keep" and isinstance(block_nbt["Items"][slot_id], BaseNbtClass.item_nbt) :
            return Response.Response_Template("指定的栏位位置已存在物品").substitute()
        block_nbt["Items"][slot_id] = item_obj
        return Response.Response_Template("在$pos位置的容器中赋予了$id * $count", 1, 1).substitute(pos=tuple(block_pos), id=item_id, count=amount)

    def replace_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, slot:str, slot_id:int,
                       item_id:str, replace_mode:Literal["keep","destroy"]="destroy", amount:int=1, data:int=0, item_nbt:dict={}) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("$player 赋予了$id * $count") ; success_list:List[str] = []
        if item_id in Constants.GAME_DATA['max_count_1_item'] : max_count = 1
        elif item_id in Constants.GAME_DATA['max_count_16_item'] : max_count = 16
        else : max_count = 64

        for entity in entity_list :
            if slot == "slot.weapon.mainhand" : item_list = (entity.Weapon,0) if hasattr(entity, "Weapon") else None
            elif slot == "slot.weapon.offhand" : item_list = (entity.Weapon,1) if hasattr(entity, "Weapon") else None
            elif slot == "slot.armor.head" : item_list = (entity.Armor,0) if hasattr(entity, "Armor") else None
            elif slot == "slot.armor.chest" : item_list = (entity.Armor,1) if hasattr(entity, "Armor") else None
            elif slot == "slot.armor.legs" : item_list = (entity.Armor,2) if hasattr(entity, "Armor") else None
            elif slot == "slot.armor.feet" : item_list = (entity.Armor,3) if hasattr(entity, "Armor") else None
            elif slot == "slot.enderchest" : item_list = (entity.EnderChest,None) if hasattr(entity, "EnderChest") else None
            elif slot == "slot.hotbar" : item_list = (entity.HotBar,None) if hasattr(entity, "HotBar") else None
            elif slot == "slot.inventory" : item_list = (entity.Inventory["Items"],None) if hasattr(entity, "Inventory") else None
            elif slot == "slot.saddle" : item_list = (entity.Equippable, 0, "Item") if hasattr(entity, "Equippable") else None
            elif slot == "slot.armor" : item_list = (entity.Equippable, 1, "Item") if hasattr(entity, "Equippable") else None
            elif slot == "slot.chest" : item_list = (entity.Inventory["Items"], None) if hasattr(entity, "Inventory") and hasattr(entity, "isChested") and entity.isChested else None
            elif slot == "slot.equippable" : item_list = (entity.Equippable, None, "Item") if hasattr(entity, "Equippable") else None
            if item_list is None : continue
            if not(0 < slot_id <= len(item_list[0])) : continue
            if slot in Constants.GAME_DATA["accept_item"] and item_id not in Constants.GAME_DATA["accept_item"][slot] : continue
            item_obj = BaseNbtClass.item_nbt().__create__(item_id, min(amount, max_count), data, item_nbt)

            if item_list[1] is not None :
                if len(item_list) == 2 : 
                    if replace_mode == "keep" and isinstance(item_list[0][item_list[1]], BaseNbtClass.item_nbt) : continue
                    item_list[0][item_list[1]] = item_obj
                else : 
                    if replace_mode == "keep" and isinstance(item_list[0][item_list[1]]["Item"], BaseNbtClass.item_nbt) : continue
                    item_list[0][item_list[1]]["Item"] = item_obj
                success_list.append(success.substitute(player=ID_tracker(entity), id=item_id, count=min(amount, max_count)))
            else :
                if len(item_list) == 2 : 
                    if replace_mode == "keep" and isinstance(item_list[0][slot_id], BaseNbtClass.item_nbt) : continue
                    item_list[0][slot_id] = item_obj
                else : 
                    if replace_mode == "keep" and isinstance(item_list[0][slot_id]["Item"], BaseNbtClass.item_nbt) : continue
                    item_list[0][slot_id]["Item"] = item_obj
                success_list.append(success.substitute(player=ID_tracker(entity), id=item_id, count=min(amount, max_count)))

            if slot == "slot.weapon.mainhand" and entity.Identifier == "minecraft:player" : entity.HotBar[entity.SelectSlot] = entity.Weapon[0]
            entity.__update_mainhand__()

        if success_list : return Response.Response_Template("已为以下实体成功给予了物品：\n$msg", 1, len(success_list)).substitute(
            msg="\n".join(success_list))
        else : return Response.Response_Template("没有实体被给予物品").substitute()


class recipe :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        recipe_mode = token_list[1]["token"].group()
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
        recipe_id = Quotation_String_transfor_1(token_list[index]["token"].group())
        if recipe_id != "*" and recipe_id not in _game.minecraft_ident.recipes : raise CompileError("不存在的配方ID：%s" % recipe_id, 
            pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
        return functools.partial(cls.give if recipe_mode == "give" else cls.take, entity_get=entity_func, recipe_id=recipe_id)

    def give(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, recipe_id:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功赋予了配方:\n$entity")
        faild = string.Template("以下实体无法赋予配方:\n$entity")
        success_list, faild_list = [], []

        for entity1 in entity_list :
            if recipe_id == "*" : 
                entity1.UnlockRecipe = list(game.minecraft_ident.recipes.keys())
                success_list.append(ID_tracker(entity1))
            elif recipe_id not in entity1.UnlockRecipe : 
                entity1.UnlockRecipe.append(recipe_id)
                success_list.append(ID_tracker(entity1))
            else : faild_list.append(ID_tracker(entity1))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")

    def take(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, recipe_id:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功剥夺了配方:\n$entity")
        faild = string.Template("以下实体无法剥夺配方:\n$entity")
        success_list, faild_list = [], []

        for entity1 in entity_list :
            if recipe_id == "*" : 
                entity1.UnlockRecipe.clear()
                success_list.append(ID_tracker(entity1))
            elif recipe_id in entity1.UnlockRecipe : 
                entity1.UnlockRecipe.remove(recipe_id)
                success_list.append(ID_tracker(entity1))
            else : faild_list.append(ID_tracker(entity1))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")


class ride :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1)
        if token_list[index]["token"].group() == "start_riding" :
            index, ride_func = Selector.Selector_Compiler(_game, token_list, index+1, is_single=True)
            if index >= len(token_list) : tp_mode = "teleport_rider"
            else : tp_mode = token_list[index]["token"].group() ; index += 1
            if tp_mode == "teleport_ride" : _, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_single=True)
            return functools.partial(cls.start_riding, entity_get=entity_func, ride_get=ride_func, tp_mode=tp_mode)
        if token_list[index]["token"].group() == "stop_riding" :
            return functools.partial(cls.stop_riding, entity_get=entity_func)
        if token_list[index]["token"].group() == "evict_riders" :
            return functools.partial(cls.evict_riders, entity_get=entity_func)
        if token_list[index]["token"].group() == "summon_rider" :
            entity_id = ID_transfor(token_list[index+1]["token"].group()) ; index += 2
            if entity_id not in _game.minecraft_ident.entities : raise CompileError("不存在的实体ID：%s" % entity_id, 
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if not _game.minecraft_ident.entities[entity_id]["description"]["is_summonable"] :
                raise CompileError("不能被召唤的实体ID：%s" % entity_id, pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : return functools.partial(cls.summon_rider, entity_get=entity_func, entity_id=entity_id)
            entity_event = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            if index >= len(token_list) : return functools.partial(cls.summon_rider, entity_get=entity_func, entity_id=entity_id, event=entity_event)
            entity_name = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            return functools.partial(cls.summon_rider, entity_get=entity_func, entity_id=entity_id, event=entity_event, name=entity_name)
        if token_list[index]["token"].group() == "summon_ride" :
            entity_id = ID_transfor(token_list[index+1]["token"].group()) ; index += 2
            if entity_id not in _game.minecraft_ident.entities : raise CompileError("不存在的实体ID：%s" % entity_id, 
                pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if not _game.minecraft_ident.entities[entity_id]["description"]["is_summonable"] :
                raise CompileError("不能被召唤的实体ID：%s" % entity_id, pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
            if index >= len(token_list) : return functools.partial(cls.summon_ride, entity_get=entity_func, entity_id=entity_id)
            ride_rule = token_list[index]["token"].group() ; index += 1
            if index >= len(token_list) : return functools.partial(cls.summon_ride, entity_get=entity_func, entity_id=entity_id, ride_rule=ride_rule)
            entity_event = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            if index >= len(token_list) : return functools.partial(cls.summon_ride, entity_get=entity_func, entity_id=entity_id, ride_rule=ride_rule, event=entity_event)
            entity_name = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            return functools.partial(cls.summon_ride, entity_get=entity_func, entity_id=entity_id, ride_rule=ride_rule, event=entity_event, name=entity_name)

    def start_riding(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, ride_get:Callable, tp_mode:str) :
        entity_list2:List[BaseNbtClass.entity_nbt] = ride_get(execute_var, game)
        if isinstance(entity_list2, Response.Response_Template) : return entity_list2
        entity_list1:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game, _except=entity_list2[0])
        if isinstance(entity_list1, Response.Response_Template) : return entity_list1
        
        success = string.Template("以下实体成功的骑上了$ride:\n$entity") ; success_list = []
        faild = string.Template("以下实体无法骑上$ride:\n$entity") ; faild_list = []

        for entity in entity_list1 :
            pos = entity.Pos ; dimension = entity.Dimension
            aa = entity_list2[0].__sit_start_riding__(entity)
            if aa : 
                if tp_mode == "teleport_ride" : game.minecraft_chunk.__teleport_entity__(entity_list2, dimension, pos)
                game.minecraft_chunk.__remove_entity__(entity)
                entity_list2[0].__sit_update__()
                success_list.append(ID_tracker(entity))
            else : faild_list.append(ID_tracker(entity))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(ride=ID_tracker(entity_list2[0]), entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(ride=ID_tracker(entity_list2[0]), entity=", ".join(faild_list)) if faild_list else "")

    def stop_riding(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list1:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list1, Response.Response_Template) : return entity_list1

        success = string.Template("以下实体成功停止骑乘:\n$entity") ; success_list = []
        faild = string.Template("以下实体没有骑乘任何实体:\n$entity") ; faild_list = []

        entities = [i for i in game.minecraft_chunk.__get_all_load_entity__() if i.__get_passengers__()]
        for ride in entity_list1 : 
            aa = ride.__sit_stop_riding__(entities)
            if not aa : 
                if ride == entity_list1[-1] : faild_list.append(ID_tracker(ride))
                continue
            else : 
                game.minecraft_chunk.__add_entity__(ride)
                success_list.append(ID_tracker(ride))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")
        
    def evict_riders(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list1:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list1, Response.Response_Template) : return entity_list1

        success = string.Template("以下实体成功逐出了乘客:\n$entity") ; success_list = []
        faild = string.Template("以下实体没有任何乘客:\n$entity") ; faild_list = []

        entities = [i for i in game.minecraft_chunk.__get_all_load_entity__() if i.__get_passengers__()]
        for ride in entity_list1 : 
            aa = ride.__sit_evict_riders__()
            if not aa : 
                faild_list.append(ID_tracker(ride))
            else : 
                game.minecraft_chunk.__add_entity__(*aa)
                success_list.append(ID_tracker(ride))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")

    def summon_rider(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, entity_id:str, event:str=None, name:str=None) :
        entity_list1:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list1, Response.Response_Template) : return entity_list1

        success = string.Template("以下实体成功召唤乘骑者:\n$entity") ; success_list = []
        faild = string.Template("以下实体无法召唤乘骑者或无法成为乘骑者:\n$entity") ; faild_list = []

        for entity in entity_list1 :
            aa = BaseNbtClass.entity_nbt().__create__(entity_id, entity.Dimension, entity.Pos, name)
            if game.minecraft_world.difficulty == 0 and ("monster" in aa.FamilyType) : faild_list.append(ID_tracker(entity)) ; continue
            if event : EntityComponent.trigger_event(aa, event)
            bb = entity.__sit_start_riding__(aa)
            if not bb : game.minecraft_chunk.__add_entity__(aa) ; faild_list.append(ID_tracker(entity))
            else : success_list.append(ID_tracker(entity))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")

    def summon_ride(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, entity_id:str, ride_rule:str="reassign_rides", event:str=None, name:str=None) :
        entity_list1:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list1, Response.Response_Template) : return entity_list1

        success = string.Template("以下实体成功召唤了坐骑:\n$entity") ; success_list = []
        faild = string.Template("以下实体无法召唤坐骑或无法骑上坐骑:\n$entity") ; faild_list = []

        entities = [i for i in game.minecraft_chunk.__get_all_load_entity__() if i.__get_passengers__()]
        for entity in entity_list1 :
            aa = BaseNbtClass.entity_nbt().__create__(entity_id, entity.Dimension, entity.Pos, name)
            if event : EntityComponent.trigger_event(aa, event)
            if game.minecraft_world.difficulty == 0 and ("monster" in aa.FamilyType) : faild_list.append(ID_tracker(entity)) ; continue
            if ( ride_rule == "skip_riders" and all((entity not in i.__get_passengers__() for i in entities)) ) or \
               ( ride_rule == "no_ride_change" and entity.__get_passengers__() and all((entity not in i.__get_passengers__() for i in entities)) ) or \
               ( ride_rule == "reassign_rides" ) :
                game.minecraft_chunk.__add_entity__(aa)
                bb = aa.__sit_start_riding__(entity)
                if not bb : faild_list.append(ID_tracker(entity))
                else : game.minecraft_chunk.__add_entity__(aa) ; success_list.append(ID_tracker(entity))
            else : faild_list.append(ID_tracker(entity))

        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")


class schedule :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) : 
        if token_list[1]["token"].group() == "on_area_loaded" :
            if token_list[3]["token"].group() == "circle" :
                pos = [token_list[i]["token"].group() for i in range(4,7,1)]
                radius = int(token_list[7]["token"].group())
                if not(0 <= radius <= 4) : raise CompileError("区块半径只能在 0~4 范围内", pos=(token_list[7]["token"].start(), token_list[7]["token"].end()))
                function_path = token_list[8]["token"].group()
                if function_path not in _game.minecraft_ident.functions : raise CompileError("不存在的函数：%s" % function_path, 
                    pos=(token_list[8]["token"].start(), token_list[8]["token"].end()))
                return functools.partial(cls.circle, from_pos=pos, radius=radius, mcfunc=function_path)
            if token_list[3]["token"].group() == "tickingarea" :
                tickarea_name = Quotation_String_transfor_1(token_list[4]["token"].group())
                function_path = token_list[5]["token"].group()
                if function_path not in _game.minecraft_ident.functions : raise CompileError("不存在的函数：%s" % function_path, 
                    pos=(token_list[5]["token"].start(), token_list[5]["token"].end()))
                return functools.partial(cls.tickingarea, name=tickarea_name, mcfunc=function_path)
            else :
                from_pos = [token_list[3+i]["token"].group() for i in range(3)]
                to_pos = [token_list[6+i]["token"].group() for i in range(3)]
                function_path = token_list[9]["token"].group()
                if function_path not in _game.minecraft_ident.functions : raise CompileError("不存在的函数：%s" % function_path, 
                    pos=(token_list[9]["token"].start(), token_list[9]["token"].end()))
                return functools.partial(cls.area, from_pos=from_pos, to_pos=to_pos, mcfunc=function_path)

    def circle(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, from_pos:List[str], radius:int, mcfunc:str) :
        start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], from_pos, execute_var["rotate"])]
        load_range = (
            start_pos[0] - (radius * 16) , start_pos[0] + 16 + (radius * 16) ,
            start_pos[2] - (radius * 16) , start_pos[2] + 16 + (radius * 16) ,
        )

        force_load = [] 
        for chunk_pos in itertools.product(range(load_range[0], load_range[1], 16), range(load_range[2], load_range[3], 16)) :
            if ((chunk_pos[0] - start_pos[0]) ** 2 + (chunk_pos[1]- start_pos[2]) ** 2) > ((radius * 16) ** 2) : continue
            force_load.append(chunk_pos)
        
        def async_func() :
            set1 = set(force_load) & game.minecraft_chunk.loading_chunk_pos[execute_var["dimension"]]
            if set1.__len__() != force_load.__len__() : return None
            a = {"executer":"server","execute_dimension":"overworld","execute_pos":[0,0,0],"execute_rotate":[0,0],"version":game.game_version}
            Command0.function.run(a, game, mcfunc)
            return "end"
        from ... import GameLoop
        GameLoop.modify_async_func("add", async_func)

        return Response.Response_Template("已将$func函数放入队列中等待执行", 1, 1).substitute(func=mcfunc)

    def tickingarea(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, name:str, mcfunc:str) :

        def async_func() :
            if name not in game.minecraft_chunk.tickingarea : return None
            a = {"executer":"server","execute_dimension":"overworld","execute_pos":[0,0,0],"execute_rotate":[0,0],"version":game.game_version}
            Command0.function.run(a, game, mcfunc)
            return "end"
        from ... import GameLoop
        GameLoop.modify_async_func("add", async_func)

        return Response.Response_Template("已将$func函数放入队列中等待执行", 1, 1).substitute(func=mcfunc)

    def area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, from_pos:List[str], to_pos:List[str], mcfunc:str) :

        start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], from_pos, execute_var["rotate"])]
        end_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], to_pos, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos, end_pos)) :
            if pos_1 > pos_2 : start_pos[index] = pos_2; end_pos[index] = pos_1
        if len(range(start_pos[0], start_pos[2]+1, 16)) * len(range(end_pos[0], end_pos[2]+1, 16)) > 100 :
            return Response.Response_Template("区域内区块数量大于100个").substitute()

        force_load = [i for i in itertools.product(range(start_pos[0], start_pos[2]+1, 16), range(end_pos[0], end_pos[2]+1, 16))]
        def async_func() :
            set1 = set(force_load) & game.minecraft_chunk.loading_chunk_pos[execute_var["dimension"]]
            if set1.__len__() != force_load.__len__() : return None
            a = {"executer":"server","execute_dimension":"overworld","execute_pos":[0,0,0],"execute_rotate":[0,0],"version":game.game_version}
            Command0.function.run(a, game, mcfunc)
            return "end"
        from ... import GameLoop
        GameLoop.modify_async_func("add", async_func)

        return Response.Response_Template("已将$func函数放入队列中等待执行", 1, 1).substitute(func=mcfunc)


class scoreboard :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) : 
        if token_list[1]["token"].group() == "objectives" :
            if token_list[2]["token"].group() == "add" :
                scoreboard_name = Quotation_String_transfor_1(token_list[3]["token"].group())
                predicate_name = token_list[4]["token"].group()
                if 5 >= len(token_list) : display_name = scoreboard_name
                else : display_name = Quotation_String_transfor_1(token_list[5]["token"].group())
                return functools.partial(cls.obj_add, scoreboard_name=scoreboard_name, predicate_name=predicate_name, display_name=display_name)
            elif token_list[2]["token"].group() == "list" : return cls.obj_list
            elif token_list[2]["token"].group() == "remove" :
                scoreboard_name = Quotation_String_transfor_1(token_list[3]["token"].group())
                return functools.partial(cls.obj_remove, scoreboard_name=scoreboard_name)
            elif token_list[2]["token"].group() == "setdisplay" :
                display_id = token_list[3]["token"].group()
                if 4 >= len(token_list) : return functools.partial(cls.obj_display, display_id=display_id)
                scoreboard_name = Quotation_String_transfor_1(token_list[4]["token"].group())
                return functools.partial(cls.obj_display, display_id=display_id, scoreboard_name=scoreboard_name)
        
        if token_list[1]["token"].group() == "players" and token_list[2]["token"].group() != "operation" :
            if token_list[2]["token"].group() in ("set", "add", "remove") :
                if token_list[3]["type"] in ("Objective_Name", "Player_Name") : index, entity_func = 4, token_list[3]["token"].group()
                else : index, entity_func = Selector.Selector_Compiler(_game, token_list, 3)
                scoreboard_name = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
                value = int(token_list[index]["token"].group())
                return functools.partial(cls.score_add_sub_set, mode=token_list[2]["token"].group(), entity_get=entity_func,
                scb=scoreboard_name, value=value)
            if token_list[2]["token"].group() == "list" :
                if 3 >= len(token_list) : entity_func = "*"
                elif token_list[3]["type"] in ("Objective_Name", "Player_Name") : index, entity_func = 4, token_list[3]["token"].group()
                else : index, entity_func = Selector.Selector_Compiler(_game, token_list, 3)
                return functools.partial(cls.score_list, entity_get=entity_func)
            if token_list[2]["token"].group() == "reset" :
                if token_list[3]["type"] in ("Objective_Name", "Player_Name") : index, entity_func = 4, token_list[3]["token"].group()
                else : index, entity_func = Selector.Selector_Compiler(_game, token_list, 3)
                if index >= len(token_list) : return functools.partial(cls.score_reset, entity_get=entity_func)
                scoreboard_name = Quotation_String_transfor_1(token_list[index]["token"].group())
                return functools.partial(cls.score_reset, entity_get=entity_func, scb=scoreboard_name)
            if token_list[2]["token"].group() == "random" :
                if token_list[3]["type"] in ("Objective_Name", "Player_Name") : index, entity_func = 4, token_list[3]["token"].group()
                else : index, entity_func = Selector.Selector_Compiler(_game, token_list, 3)
                scoreboard_name = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
                min1,max1 = int(token_list[index]["token"].group()), int(token_list[index+1]["token"].group())
                if min1 >= max1 : raise CompileError("随机数下限值大于等于上限值", 
                    pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
                return functools.partial(cls.score_random, entity_get=entity_func, scb=scoreboard_name, min1=min1, max1=max1)
            if token_list[2]["token"].group() == "test" :
                if token_list[3]["type"] in ("Objective_Name", "Player_Name") : index, entity_func = 4, token_list[3]["token"].group()
                else : index, entity_func = Selector.Selector_Compiler(_game, token_list, 3)
                scoreboard_name = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
                m1 = token_list[index]["token"].group() ; index += 1
                if m1 == "*" : min1 = -2147483648
                else : min1 = int(m1)
                if index >= len(token_list) : return functools.partial(cls.score_test, entity_get=entity_func, scb=scoreboard_name, min1=min1)
                m1 = token_list[index]["token"].group() ; index += 1
                if m1 == "*" : max1 = 2147483647
                else : max1 = int(m1)
                if min1 > max1 : raise CompileError("比较下限值大于等于上限值", 
                    pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
                return functools.partial(cls.score_test, entity_get=entity_func, scb=scoreboard_name, min1=min1, max1=max1)

        if token_list[1]["token"].group() == "players" and token_list[2]["token"].group() == "operation" :
            if token_list[3]["type"] in ("Objective_Name", "Player_Name") : index, entity_func_1 = 4, token_list[3]["token"].group()
            else : index, entity_func_1 = Selector.Selector_Compiler(_game, token_list, 3)
            scoreboard_name_1 = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            operation_mode = token_list[index]["token"].group() ; index += 1
            if token_list[index]["type"] in ("Objective_Name", "Player_Name") : index, entity_func_2 = index+1, token_list[3]["token"].group()
            else : index, entity_func_2 = Selector.Selector_Compiler(_game, token_list, index)
            scoreboard_name_2 = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
            return functools.partial(cls.score_operation, entity_get1=entity_func_1, scb1=scoreboard_name_1, mode=operation_mode,
                                     entity_get2=entity_func_2, scb2=scoreboard_name_2)

    def obj_add(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, scoreboard_name:str, predicate_name:str, display_name:str) :
        aa = game.minecraft_scoreboard.__add_scoreboard__(scoreboard_name, predicate_name, display_name)
        if aa == Exception : return Response.Response_Template("已存在计分板$scb_name").substitute(scb_name=scoreboard_name)
        return Response.Response_Template("添加了新的计分板$scb_name", 1, 1).substitute(scb_name=scoreboard_name)
    
    def obj_list(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread) :
        list1 = []
        aaa = string.Template("$scb_name的准则为$predicate, 显示为$name")
        for key,value in game.minecraft_scoreboard.scoreboard_list.items() : 
            list1.append(aaa.substitute(scb_name=key, name=value["display_name"], predicate=value["predicate"]))

        return Response.Response_Template("$count个存在的计分板$new_line$scbs", 1, 1).substitute(
            count = list1.__len__(), new_line = "\n" if list1 else "", scbs = "\n".join(list1)
        )

    def obj_remove(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, scoreboard_name:str) :
        aa = game.minecraft_scoreboard.__remove_scoreboard__(scoreboard_name)
        if aa == Exception : return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scoreboard_name)
        return Response.Response_Template("删除了计分板$scb_name", 1, 1).substitute(scb_name=scoreboard_name)

    def obj_display(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, display_id:str, scoreboard_name:str=None) :
        aa = game.minecraft_scoreboard.__set_display__(display_id, scoreboard_name)
        if aa == Exception : return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scoreboard_name)
        if scoreboard_name is None : return Response.Response_Template("删除了$display位置显示的计分板", 1, 1).substitute(display=display_id)
        else : return Response.Response_Template("设置了$display位置显示的计分板", 1, 1).substitute(display=display_id)


    def score_add_sub_set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, mode:str, entity_get:Union[str,Callable], scb:str, value:int) :
        if not game.minecraft_scoreboard.____scb_exists____(scb) :
            return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb)

        if entity_get == "*" : scb_names = game.minecraft_scoreboard.____get_star_obj____()
        elif isinstance(entity_get, str) : scb_names = [entity_get]
        else :
            scb_names:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
            if isinstance(scb_names, Response.Response_Template) : return scb_names

        if mode == "add" : game.minecraft_scoreboard.__add_score__(scb_names, scb, value)
        elif mode == "remove" : game.minecraft_scoreboard.__sub_score__(scb_names, scb, value)
        elif mode == "set" : game.minecraft_scoreboard.__set_score__(scb_names, scb, value)
        scores1 = [game.minecraft_scoreboard.____get_score____(scb,i) for i in scb_names]

        return Response.Response_Template("设置了以下实体的分数：\n$text", 1, 1).substitute(
            text=", ".join( ("%s%s -> %s"%("\n" if (index % 5 == 0 and index != 0) else "", 
            ID_tracker(scb_names[index]), item) ) for index,item in enumerate(scores1)) 
        )

    def score_list(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Union[str,Callable]) :
        if entity_get == "*" : scb_names = game.minecraft_scoreboard.____get_star_obj____()
        elif isinstance(entity_get, str) : scb_names = [entity_get]
        else :
            scb_names:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
            if isinstance(scb_names, Response.Response_Template) : return scb_names

        query_list:List[str] = []
        for i,name in enumerate(scb_names) :
            a = "实体 %s 有以下计分板计分：\n" % ID_tracker(name)
            query_list.append(a)
            for index,scb in enumerate(list(game.minecraft_scoreboard.scoreboard_list)) :
                if not game.minecraft_scoreboard.____score_exists____(scb, name) : continue
                query_list.append("%s -> %s" % (scb, game.minecraft_scoreboard.____get_score____(scb, name)))
                if index != 0 and index % 5 == 0 : query_list.append("\n")
            if query_list[-1] == a : query_list.pop() ; query_list.append("实体 %s 没有任何计分板计分" % ID_tracker(name))
            if i != len(scb_names) - 1 : query_list.append("\n")

        return Response.Response_Template("$text", 1, 1).substitute(text = "".join(query_list))

    def score_reset(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Union[str,Callable], scb:str=None) :
        if entity_get == "*" : scb_names = game.minecraft_scoreboard.____get_star_obj____()
        elif isinstance(entity_get, str) : scb_names = [entity_get]
        else :
            scb_names:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
            if isinstance(scb_names, Response.Response_Template) : return scb_names
        
        aa = game.minecraft_scoreboard.__reset_score__(scb_names, scb)
        if aa == Exception : return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb)
        return Response.Response_Template("已重置以下实体的分数：\n$entity", 1, len(scb_names)).substitute(
            entity = ", ".join( (ID_tracker(i) for i in scb_names) ),
        )
        
    def score_random(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Union[str,Callable], scb:str, min1:int, max1:int) :
        if not game.minecraft_scoreboard.____scb_exists____(scb) :
            return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb)

        if entity_get == "*" : scb_names = game.minecraft_scoreboard.____get_star_obj____()
        elif isinstance(entity_get, str) : scb_names = [entity_get]
        else :
            scb_names:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
            if isinstance(scb_names, Response.Response_Template) : return scb_names

        game.minecraft_scoreboard.__set_random_score__(scb_names, scb, min1, max1)
        scores1 = [game.minecraft_scoreboard.____get_score____(scb,i) for i in scb_names]

        return Response.Response_Template("设置了以下实体的分数：\n$text", 1, 1).substitute(
            text=", ".join( ("%s%s -> %s"%("\n" if (index % 5 == 0 and index != 0) else "", 
            ID_tracker(scb_names[index]), item) ) for index,item in enumerate(scores1)) 
        )

    def score_test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Union[str,Callable], scb:str, min1:int, max1:int=2147483647) :
        if entity_get == "*" : scb_names = game.minecraft_scoreboard.____get_star_obj____()
        elif isinstance(entity_get, str) : scb_names = [entity_get]
        else :
            scb_names:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
            if isinstance(scb_names, Response.Response_Template) : return scb_names

        aa = game.minecraft_scoreboard.__test_score__(scb_names, scb, min1, max1)
        if aa == Exception : return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb)
        if aa : return Response.Response_Template("以下实体的分数通过测试：\n$entity", 1, len(scb_names)).substitute(
            entity = ", ".join( (ID_tracker(i) for i in aa) ))
        else : return Response.Response_Template("没有实体通过分数测试").substitute()


    def score_operation(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get1:Union[str,Callable], scb1:str,
        mode:str, entity_get2:Union[str,Callable], scb2:str) :
        if not game.minecraft_scoreboard.____scb_exists____(scb1) : return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb1)
        if not game.minecraft_scoreboard.____scb_exists____(scb2) : return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb2)
        
        if entity_get1 == "*" : scb_names1 = game.minecraft_scoreboard.____get_star_obj____()
        elif isinstance(entity_get1, str) : scb_names1 = [entity_get1]
        else :
            scb_names1:List[BaseNbtClass.entity_nbt] = entity_get1(execute_var, game)
            if isinstance(scb_names1, Response.Response_Template) : return scb_names1

        if entity_get2 == "*" : scb_names2 = game.minecraft_scoreboard.____get_star_obj____()
        elif isinstance(entity_get2, str) : scb_names2 = [entity_get2]

        oper_dict = {
            "+=":game.minecraft_scoreboard.__add_entity_score__ ,
            "-=":game.minecraft_scoreboard.__sub_entity_score__ ,
            "*=":game.minecraft_scoreboard.__mul_entity_score__ ,
            "/=":game.minecraft_scoreboard.__div_entity_score__ ,
            "%=":game.minecraft_scoreboard.__mod_entity_score__ ,
            "=":game.minecraft_scoreboard.__equral_entity_score__ ,
            "<":game.minecraft_scoreboard.__min_entity_score__ ,
            ">":game.minecraft_scoreboard.__max_entity_score__ ,
            "><":game.minecraft_scoreboard.__exchange_entity_score__ ,
        }
        for entity_1 in scb_names1 : 
            if not isinstance(entity_get2, str) : scb_names2:List[BaseNbtClass.entity_nbt] = entity_get2(execute_var, game)
            if isinstance(scb_names2, Response.Response_Template) : continue
            oper_dict[mode](entity_1, scb1, scb_names2, scb2)
        scores1 = [game.minecraft_scoreboard.____get_score____(scb1,i) for i in scb_names1]

        return Response.Response_Template("设置了以下实体的分数：\n$text", 1, 1).substitute(
            text=", ".join( ("%s%s -> %s"%("\n" if (index % 5 == 0 and index != 0) else "", 
            ID_tracker(scb_names1[index]), item) ) for index,item in enumerate(scores1)) 
        )


class setblock :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        pos = [ token_list[i]["token"].group() for i in range(1,4,1) ]
        block_id = ID_transfor(token_list[4]["token"].group())


class setworldspawn :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if 1 >= len(token_list) : return cls.run
        pos = [ token_list[i]["token"].group() for i in range(1,4,1) ]
        return functools.partial(cls.run, pos=pos)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]=["~","~","~"]) :
        start_pos = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
        start_pos[0] += 0.5 ; start_pos[2] += 0.5
        game.minecraft_world.world_spawn_x = np.float32(start_pos[0])
        game.minecraft_world.world_spawn_y = np.float32(start_pos[1])
        game.minecraft_world.world_spawn_z = np.float32(start_pos[2])

        return Response.Response_Template("世界出生点已设置为$pos", 1, 1).substitute(pos=tuple(start_pos))


class spawnpoint :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if 1 >= len(token_list) : return cls.run
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if index >= len(token_list) : return functools.partial(cls.run, entity_get=entity_func)
        pos = [ token_list[i]["token"].group() for i in range(index,index+3,1) ]
        return functools.partial(cls.run, entity_get=entity_func, pos=pos)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None, pos:List[str]=["~","~","~"]) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        start_pos = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
        start_pos[0] += 0.5 ; start_pos[2] += 0.5
        for entity in entity_list : entity.SpawnPoint = [np.float32(i) for i in start_pos]

        return Response.Response_Template("以下玩家出生点设置为$pos：\n$entity", 1, len(entity_list)).substitute(
            pos = tuple(start_pos),
            entity = ", ".join( (ID_tracker(i) for i in entity_list) ),
        )


class spreadplayers :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) : pass




        