from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction,DataSave
from . import Selector,Rawtext,CompileError,CommandParser
from . import Quotation_String_transfor_1,ID_transfor,BlockState_Compiler,Msg_Compiler
import functools,string,random,math,itertools,json
from typing import Dict,Union,List,Tuple,Literal,Callable


class structure :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        struc_name = token_list[2]["token"]
        if token_list[1]["token"] == "save" :
            pos1 = [token_list[3+i]["token"] for i in range(3)]
            pos2 = [token_list[6+i]["token"] for i in range(3)]
            if 9 >= len(token_list) : return functools.partial(cls.save, name=struc_name, start=pos1, end=pos2)
            if token_list[9]["token"] in ("disk", "memory") : 
                return functools.partial(cls.save, name=struc_name, start=pos1, end=pos2, save_mode=token_list[9]["token"])
            has_entity = ("false","true").index(token_list[9]["token"])
            if 10 >= len(token_list) : return functools.partial(cls.save, name=struc_name, start=pos1, end=pos2, has_entity=bool(has_entity))
            save_mode = token_list[10]["token"]
            if 11 >= len(token_list) : return functools.partial(cls.save, name=struc_name, start=pos1, end=pos2, has_entity=bool(has_entity), save_mode=save_mode)
            has_block = ("false","true").index(token_list[11]["token"])
            return functools.partial(cls.save, name=struc_name, start=pos1, end=pos2, has_entity=bool(has_entity), save_mode=save_mode, has_block=bool(has_block))
        elif token_list[1]["token"] == "load" :
            pos1 = [token_list[3+i]["token"] for i in range(3)]
            if 6 >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1)
            struc_rotate = token_list[6]["token"]
            if 7 >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate)
            struc_mirror = token_list[7]["token"]
            if 8 >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror)
            if token_list[8]["token"] in ("block_by_block", "layer_by_layer") : 
                if 9 >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror)
                if 10 >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror)
                index = 10
            else : index = 9
            if index >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror)
            has_entity = ("false","true").index(token_list[index]["token"]) ; index += 1
            if index >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror,
                has_entity=has_entity)
            has_block = ("false","true").index(token_list[index]["token"]) ; index += 1
            if index >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror,
                has_entity=has_entity, has_block=has_block)
            has_water = ("false","true").index(token_list[index]["token"]) ; index += 1
            if index >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror,
                has_entity=has_entity, has_block=has_block)
            integrity = float(token_list[index]["token"]) ; index += 1
            if index >= len(token_list) : return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror,
                has_entity=has_entity, has_block=has_block, integrity=integrity)
            seed = Quotation_String_transfor_1(token_list[index]["token"])
            return functools.partial(cls.load, name=struc_name, start=pos1, rotation=struc_rotate, mirror=struc_mirror,
                has_entity=has_entity, has_block=has_block, integrity=integrity, seed=seed)
        elif token_list[1]["token"] == "delete" : 
            return functools.partial(cls.delete, name=struc_name)

    def save(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, name:str, start:List[str], end:List[str],
             save_mode:Literal["disk","memory"]="memory", has_entity:bool=True, has_block:bool=True) :
        start_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start, execute_var["rotate"])]
        end_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], end, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos1, end_pos1)) :
            if pos_1 > pos_2 : start_pos1[index] = pos_2; end_pos1[index] = pos_1
        area = [(pos2-pos1+1) for pos1,pos2 in itertools.zip_longest(start_pos1, end_pos1)]
        if not(0 <= area[0] <= 64) or not(0 <= area[2] <= 64) or not(0 <= area[1] <= 319) : 
            return Response.Response_Template("区域$pos1 ~ $pos2超过64*320*64大小").substitute(pos1=tuple(start_pos1), pos2=tuple(end_pos1))
        
        structure_data = BaseNbtClass.structure_nbt().__create__(game.minecraft_chunk, execute_var["dimension"], 
        start_pos1, end_pos1, has_entity, has_block)
        if save_mode == "disk" : 
            if name in game.minecraft_chunk.memory_structure : del game.minecraft_chunk.memory_structure[name]
            game.minecraft_chunk.disk_structure[name] = structure_data
        else : 
            if name in game.minecraft_chunk.disk_structure : del game.minecraft_chunk.disk_structure[name]
            game.minecraft_chunk.memory_structure[name] = structure_data
        return Response.Response_Template("区域$pos1 ~ $pos2内保存为结构 $name", 1, 1).substitute(
            pos1=tuple(start_pos1), pos2=tuple(end_pos1), name=name)

    def load(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, name:str, start:List[str], rotation:str="0_degrees", 
             mirror:str="none", has_entity:bool=True, has_block:bool=True, integrity:float=100, seed=None) :
        if name in game.minecraft_chunk.disk_structure : structure_save = game.minecraft_chunk.disk_structure
        elif name in game.minecraft_chunk.memory_structure : structure_save = game.minecraft_chunk.memory_structure
        else : return Response.Response_Template("不存在结构 $name").substitute(name=name)

        start_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start, execute_var["rotate"])]
        world_height = Constants.DIMENSION_INFO[execute_var["dimension"]]["height"]
        if not(world_height[0] <= start_pos1[1] < world_height[1]) : 
            return Response.Response_Template("无法在$pos位置加载结构").substitute(pos=tuple(start_pos1))

        rotate_m,mirror_m = Constants.MITRAX["rotate"][rotation], Constants.MITRAX["mirror"][mirror]
        end_m = MathFunction.mitrax_transform(rotate_m, mirror_m)
        end_area = MathFunction.vector_transform(structure_save[name].Area, end_m)
        place_pos_start = [i+abs(j)-1 for i,j in itertools.zip_longest(start_pos1, end_area)]

        all_in_load = True
        for i in itertools.product(range(start_pos1[0]//16*16, place_pos_start[0]//16*16 + 1, 16), range(1),
        range(start_pos1[0]//16*16, place_pos_start[0]//16*16 + 1, 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], i) : all_in_load = False
        
        if all_in_load :
            structure_save[name].__output__(game.minecraft_chunk, execute_var["dimension"], start_pos1, 
                rotation, mirror, has_entity, has_block, integrity, seed)
            return Response.Response_Template("已在$pos1加载结构 $name", 1, 1).substitute(pos1=tuple(start_pos1), name=name)
        else :
            from ... import GameLoop
            def async_run() :
                for i in itertools.product(range(start_pos1[0]//16*16, place_pos_start[0]//16*16 + 1, 16),  range(1),
                range(start_pos1[0]//16*16, place_pos_start[0]//16*16 + 1, 16)) :
                    if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], i) : return None
                structure_save[name].__output__(game.minecraft_chunk, execute_var["dimension"], start_pos1, 
                rotation, mirror, has_entity, has_block, integrity, seed)
                return "end"
            GameLoop.modify_async_func("add", async_run)
            return Response.Response_Template("在$pos1加载的结构$name已放入等待队列", 1, 1).substitute(pos1=tuple(start_pos1), name=name)

    def delete(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, name:str) :
        if name in game.minecraft_chunk.disk_structure : del game.minecraft_chunk.disk_structure[name]
        elif name in game.minecraft_chunk.memory_structure : del game.minecraft_chunk.memory_structure[name]
        else : return Response.Response_Template("不存在结构 $name").substitute(name=name)

        return Response.Response_Template("已删除结构 $name", 1, 1).substitute(name=name)


class stopsound :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if index >= len(token_list) : return functools.partial(cls.stop_all, entity_get=entity_func)
        sound_name = Quotation_String_transfor_1(token_list[index]["token"])
        if sound_name not in _game.minecraft_ident.entities :
            raise CompileError("不存在的声音ID：%s" % sound_name, pos=(token_list[index]["start"], token_list[index]["end"]))
        return functools.partial(cls.stop_one, entity_get=entity_func, entity_name=sound_name)

    def stop_all(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("以下玩家停止播放所有声音:\n$players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list)
        )

    def stop_one(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, sound_name:str) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("以下玩家已停止播放 $name 声音:\n$players", 1, len(entity_list)).substitute(
            players=", ".join(ID_tracker(i) for i in entity_list), name=sound_name
        )


class summon_1_0_0 :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        entity_id = ID_transfor(token_list[1]["token"])
        if entity_id not in _game.minecraft_ident.entities :
            raise CompileError("不存在的实体ID：%s" % entity_id, pos=(token_list[1]["start"], token_list[1]["end"]))
        if not _game.minecraft_ident.entities[entity_id]["description"]["is_summonable"] :
            raise CompileError("不能被召唤的实体ID：%s" % entity_id, pos=(token_list[1]["start"], token_list[1]["end"]))
        if 2 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id)
        elif token_list[2]["type"] == "Entity_Name" :
            entity_name = Quotation_String_transfor_1(token_list[2]["token"])
            if 3 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, entity_name=entity_name)
            pos = [token_list[3+i]["token"] for i in range(3)]
            return functools.partial(cls.summon_entity, entity_id=entity_id, entity_name=entity_name, pos=pos)
        else :
            pos = [token_list[2+i]["token"] for i in range(3)]
            if 5 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos)
            entity_event = Quotation_String_transfor_1(token_list[5]["token"])
            if 6 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos, entity_event=entity_event)
            entity_name = Quotation_String_transfor_1(token_list[6]["token"])
            return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos, entity_event=entity_event, entity_name=entity_name)

    def summon_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_id:str, 
                      pos:List[str]=["~", "~", "~"], entity_event:str=None, entity_name:str=None) :
        summon_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], summon_pos) :
            return Response.Response_Template("无法在未加载区域召唤实体").substitute()

        aaa = game.minecraft_chunk.__summon_entity__(game.minecraft_world.difficulty, 
            execute_var["dimension"], entity_id, summon_pos, entity_name, entity_event
        )
        if aaa == Exception : return Response.Response_Template("无法在和平模式下召唤怪物").substitute()
        return Response.Response_Template("成功召唤了实体 $name", 1, 1).substitute(name=ID_tracker(aaa))


class summon_1_70_0 :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        entity_id = ID_transfor(token_list[1]["token"])
        if entity_id not in _game.minecraft_ident.entities :
            raise CompileError("不存在的实体ID：%s" % entity_id, pos=(token_list[1]["start"], token_list[1]["end"]))
        if not _game.minecraft_ident.entities[entity_id]["description"]["is_summonable"] :
            raise CompileError("不能被召唤的实体ID：%s" % entity_id, pos=(token_list[1]["start"], token_list[1]["end"]))
        if 2 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id)
        elif token_list[2]["type"] == "Entity_Name" :
            entity_name = Quotation_String_transfor_1(token_list[2]["token"])
            if 3 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, entity_name=entity_name)
            pos = [token_list[3+i]["token"] for i in range(3)]
            return functools.partial(cls.summon_entity, entity_id=entity_id, entity_name=entity_name, pos=pos)
        else :
            pos = [token_list[2+i]["token"] for i in range(3)]
            if 5 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos)
            if token_list[5]["type"] in ("Absolute_Rotation", "Relative_Rotation") :
                if 6 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, 
                    pos=pos, facing=(token_list[5]["token"],"~"))
                if 7 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, 
                    pos=pos, facing=(token_list[5]["token"], token_list[6]["token"]))
                entity_event = Quotation_String_transfor_1(token_list[7]["token"])
                if 8 >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos,
                    facing=(token_list[5]["token"], token_list[6]["token"]), entity_event=entity_event)
                entity_name = Quotation_String_transfor_1(token_list[8]["token"])
                return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos, 
                    facing=(token_list[5]["token"], token_list[6]["token"]), entity_event=entity_event, entity_name=entity_name)
            if token_list[5]["token"] == "facing" :
                if token_list[6]["type"] in ("Absolute_Pos", "Relative_Pos", "Local_Pos") :
                    index, facing_var = 9, [token_list[6+i]["token"] for i in range(3)]
                else : index, facing_var = Selector.Selector_Compiler(_game, token_list, 6, is_single=True)
                if index >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos, facing=facing_var)
                entity_event = Quotation_String_transfor_1(token_list[index]["token"]) ; index += 1
                if index >= len(token_list) : return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos, facing=facing_var, entity_event=entity_event)
                entity_name = Quotation_String_transfor_1(token_list[index]["token"])
                return functools.partial(cls.summon_entity, entity_id=entity_id, pos=pos, facing=facing_var, entity_event=entity_event, entity_name=entity_name)

    def summon_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_id:str, 
                      pos:List[str]=["~", "~", "~"], facing:List[str]=None, entity_event:str=None, entity_name:str=None) :
        summon_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], summon_pos) :
            return Response.Response_Template("无法在未加载区域召唤实体").substitute()

        if isinstance(facing, (list,tuple)) and len(facing) == 2 :
            facing_x_var = MathFunction.mc_rotate_compute(float(execute_var["rotate"][0]), facing[0], "ry")
            facing_y_var = MathFunction.mc_rotate_compute(float(execute_var["rotate"][1]), facing[1], "rx")
            angle = (facing_x_var, facing_y_var)
        elif isinstance(facing, (list,tuple)) and len(facing) == 3 :
            pos_angle = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
            angle = MathFunction.rotation_angle(summon_pos, pos_angle)
        elif facing :
            entity_list:List[BaseNbtClass.entity_nbt] = facing(execute_var, game)
            if isinstance(entity_list, Response.Response_Template) : return entity_list
            angle = MathFunction.rotation_angle(summon_pos, entity_list[0].Pos)
        else : angle = None

        aaa = game.minecraft_chunk.__summon_entity__( game.minecraft_world.difficulty, 
            execute_var["dimension"], entity_id, summon_pos, entity_name, entity_event
        )
        if angle is not None : aaa.Rotation = [np.float32(angle[0]), np.float32(angle[1])]
        if aaa == Exception : return Response.Response_Template("无法在和平模式下召唤怪物").substitute()
        return Response.Response_Template("成功在 $pos 召唤了\n实体 $name $rotate", 1, 1).substitute(
            pos=tuple(aaa.Pos), name=ID_tracker(aaa), rotate=aaa.Rotation)


class tag :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1)
        if token_list[index]["token"] == "add" : return functools.partial(cls.add, entity_get=entity_func, 
            tag_name=Quotation_String_transfor_1(token_list[index+1]["token"]))
        if token_list[index]["token"] == "remove" : return functools.partial(cls.remove, entity_get=entity_func, 
            tag_name=Quotation_String_transfor_1(token_list[index+1]["token"]))
        if token_list[index]["token"] == "list" : return functools.partial(cls.list, entity_get=entity_func)
    
    def add(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, tag_name:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功添加了标签:\n$entity")
        faild = string.Template("以下实体无法添加标签:\n$entity")
        success_list, faild_list = [], []

        for entity in entity_list :
            if tag_name in entity.Tags or len(entity.Tags) > 1000 :
                faild_list.append(ID_tracker(entity)) ; continue
            entity.Tags.append(tag_name)
            success_list.append(ID_tracker(entity))
        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")

    def remove(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, tag_name:str) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("以下实体成功删除了标签:\n$entity")
        faild = string.Template("以下实体无法删除标签:\n$entity")
        success_list, faild_list = [], []

        for entity in entity_list :
            if tag_name not in entity.Tags :
                faild_list.append(ID_tracker(entity)) ; continue
            entity.Tags.remove(tag_name)
            success_list.append(ID_tracker(entity))
        return Response.Response_Template("$success$is_line$fiald", min(1,len(success_list)), len(success_list)).substitute(
            success=success.substitute(entity=", ".join(success_list)) if success_list else "",
            is_line = "\n" if success_list and faild_list else "",
            fiald=faild.substitute(entity=", ".join(faild_list)) if faild_list else "")

    def list(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list

        success = string.Template("$entity -> $tags")
        success_list = []
        for entity in entity_list :
            success_list.append(success.substitute(entity=ID_tracker(entity), tags=entity.Tags))
        return Response.Response_Template("以下实体打印标签：\n$success", min(1,len(success_list)), len(success_list)).substitute(
            success = "\n".join(success_list)
        )


class teleport :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["type"] in ("Absolute_Pos", "Relative_Pos", "Local_Pos") :
            pos = [ token_list[i]["token"] for i in range(1,4,1) ]
            if 4 >= len(token_list) : return functools.partial(cls.tp_self_pos, pos=pos)
            if token_list[4]["type"] == "Check_For_Blocks" : 
                return functools.partial(cls.tp_self_pos, pos=pos, check_block=("false","true").index(token_list[4]["token"]))
            if token_list[4]["type"] in ("Absolute_Rotation", "Relative_Rotation") :
                if 5 >= len(token_list) : return functools.partial(cls.tp_self_pos, pos=pos, facing=(token_list[4]["token"],"~"))
                if 6 >= len(token_list) : return functools.partial(cls.tp_self_pos, pos=pos, facing=(token_list[4]["token"], token_list[5]["token"]))
                return functools.partial( cls.tp_self_pos, pos=pos, facing=[token_list[4+i]["token"] for i in range(2)],
                    check_block=("false","true").index(token_list[6]["token"]) )
            if token_list[4]["token"] == "facing" :
                if token_list[5]["type"] in ("Absolute_Pos", "Relative_Pos", "Local_Pos") :
                    index, facing_var = 8, [token_list[5+i]["token"] for i in range(3)]
                else : index, facing_var = Selector.Selector_Compiler(_game, token_list, 5, is_single=True)
                if index >= len(token_list) : return functools.partial(cls.tp_self_pos, pos=pos, facing=facing_var)
                return functools.partial( cls.tp_self_pos, pos=pos, facing=facing_var,
                    check_block=("false","true").index(token_list[index]["token"]) )
        else :
            index, entity_get = Selector.Selector_Compiler(_game, token_list, 1)
            if index >= len(token_list) :
                index, entity_get = Selector.Selector_Compiler(_game, token_list, 1, is_single=True)
                return functools.partial(cls.tp_self_entity, pos=entity_get)
            if token_list[index]["type"] == "Check_For_Blocks" : 
                index, entity_get = Selector.Selector_Compiler(_game, token_list, 1, is_single=True)
                return functools.partial(cls.tp_self_entity, pos=entity_get, check_block=("false","true").index(token_list[index]["token"]))
            if token_list[index]["type"] in ("Selector", "Player_Name") :
                index, destination_entity_get = Selector.Selector_Compiler(_game, token_list, index, is_single=True)
                if index >= len(token_list) : return functools.partial(cls.tp_entity_entity, victim=entity_get, pos=destination_entity_get)
                return functools.partial(cls.tp_entity_entity, victim=entity_get, pos=destination_entity_get, 
                                         check_block=("false","true").index(token_list[index]["token"]))
            if token_list[index]["type"] in ("Absolute_Pos", "Relative_Pos", "Local_Pos") :
                pos = [ token_list[i]["token"] for i in range(index, index+3, 1) ] ; index += 3
                if index >= len(token_list) : return functools.partial(cls.tp_entity_pos, victim=entity_get, pos=pos)
                if token_list[index]["type"] == "Check_For_Blocks" : 
                    return functools.partial(cls.tp_entity_pos, victim=entity_get, pos=pos, check_block=("false","true").index(token_list[index]["token"]))
                if token_list[index]["type"] in ("Absolute_Rotation", "Relative_Rotation") :
                    if index+1 >= len(token_list) : return functools.partial(cls.tp_entity_pos, victim=entity_get, pos=pos, facing=(token_list[index]["token"],"~"))
                    if index+2 >= len(token_list) : return functools.partial(cls.tp_entity_pos, victim=entity_get, pos=pos, facing=(token_list[index]["token"], token_list[index+1]["token"]))
                    return functools.partial( cls.tp_entity_pos, victim=entity_get, pos=pos, facing=[token_list[index+i]["token"] for i in range(2)],
                        check_block=("false","true").index(token_list[index+2]["token"]) )
                if token_list[index]["token"] == "facing" : 
                    index += 1
                    if token_list[index]["type"] in ("Absolute_Pos", "Relative_Pos", "Local_Pos") :
                        facing_var = [token_list[index+i]["token"] for i in range(3)] ; index += 3
                    else : index, facing_var = Selector.Selector_Compiler(_game, token_list, index, is_single=True)
                    if index >= len(token_list) : return functools.partial(cls.tp_entity_pos, victim=entity_get, pos=pos, facing=facing_var)
                    return functools.partial( cls.tp_entity_pos, victim=entity_get, pos=pos, facing=facing_var,
                        check_block=("false","true").index(token_list[index]["token"]) )

    def tp_self_pos(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str], 
                    facing:Union[List[str],Callable]=None, check_block:Literal[0,1]=False) :
        victim_entity = execute_var["executer"]
        if not isinstance(victim_entity, BaseNbtClass.entity_nbt) :
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        tp_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        if isinstance(facing, (list,tuple)) and len(facing) == 2 :
            facing_y_var = MathFunction.mc_rotate_compute(float(execute_var["rotate"][0]), facing[0], "ry")
            facing_x_var = MathFunction.mc_rotate_compute(float(execute_var["rotate"][1]), facing[1], "rx")
            angle = (facing_y_var, facing_x_var)
        elif isinstance(facing, (list,tuple)) and len(facing) == 3 :
            angle = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        elif facing :
            entity_list:List[BaseNbtClass.entity_nbt] = facing(execute_var, game)
            if isinstance(entity_list, Response.Response_Template) : return entity_list
            angle = entity_list[0]
        else : angle = None
        
        aaa = game.minecraft_chunk.__teleport_entity__([victim_entity], victim_entity.Dimension, tp_pos, angle, bool(check_block))
        if aaa == Exception : return Response.Response_Template("$pos 无法进行碰撞检查").substitute(pos = tuple(tp_pos))
        if len(aaa) > 0 : return Response.Response_Template("已将下列实体传送至$pos:\n $name", 1, 1).substitute(
            name = ID_tracker(victim_entity) ,
            pos = tuple(("%.4f" % i for i in tp_pos))
        )
        else : return Response.Response_Template("没有实体执行了传送").substitute()

    def tp_self_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:Callable, check_block:Literal[0,1]=False) :
        victim_entity = execute_var["executer"]
        if not isinstance(victim_entity, BaseNbtClass.entity_nbt) :
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()
        destination_entity:List[BaseNbtClass.entity_nbt] = pos(execute_var, game)
        if isinstance(destination_entity, Response.Response_Template) : return destination_entity

        aaa = game.minecraft_chunk.__teleport_entity__([victim_entity], destination_entity[0].Dimension, destination_entity[0].Pos, 
            destination_entity[0].Rotation, bool(check_block))
        if aaa == Exception : return Response.Response_Template("$pos 无法进行碰撞检查").substitute(pos = tuple(destination_entity[0].Pos))
        if len(aaa) > 0 : return Response.Response_Template("已将下列实体传送至$pos:\n $name", 1, 1).substitute(
            name = ID_tracker(victim_entity) ,
            pos = tuple(("%.4f" % i for i in destination_entity[0].Pos))
        )
        else : return Response.Response_Template("没有实体执行了传送").substitute()

    def tp_entity_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, victim:Callable, pos:Callable, check_block:Literal[0,1]=False) :
        victim_entity:List[BaseNbtClass.entity_nbt] = victim(execute_var, game)
        if isinstance(victim_entity, Response.Response_Template) : return victim_entity
        destination_entity:List[BaseNbtClass.entity_nbt] = pos(execute_var, game)
        if isinstance(destination_entity, Response.Response_Template) : return destination_entity

        aaa = game.minecraft_chunk.__teleport_entity__(victim_entity, destination_entity[0].Dimension, destination_entity[0].Pos, 
            destination_entity[0].Rotation, bool(check_block))
        if aaa == Exception : return Response.Response_Template("$pos 无法进行碰撞检查").substitute(pos = tuple(destination_entity[0].Pos))
        if len(aaa) > 0 : return Response.Response_Template("已将下列实体传送至$pos:\n $name", 1, len(aaa)).substitute(
            name = ", ".join( (ID_tracker(i) for i in aaa) ) ,
            pos = tuple(("%.4f" % i for i in destination_entity[0].Pos))
        )
        else : return Response.Response_Template("没有实体执行了传送").substitute()

    def tp_entity_pos(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, victim:Callable, pos:List[str], 
                         facing:Union[List[str],Callable]=None, check_block:Literal[0,1]=False) :
        victim_entity:List[BaseNbtClass.entity_nbt] = victim(execute_var, game)
        if isinstance(victim_entity, Response.Response_Template) : return victim_entity

        tp_pos = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        if isinstance(facing, (list,tuple)) and len(facing) == 2 :
            facing_x_var = MathFunction.mc_rotate_compute(float(execute_var["rotate"][0]), facing[0], "ry")
            facing_y_var = MathFunction.mc_rotate_compute(float(execute_var["rotate"][1]), facing[1], "rx")
            angle = (facing_x_var, facing_y_var)
        elif isinstance(facing, (list,tuple)) and len(facing) == 3 :
            angle = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
        elif facing :
            entity_list:List[BaseNbtClass.entity_nbt] = facing(execute_var, game)
            if isinstance(entity_list, Response.Response_Template) : return entity_list
            angle = entity_list[0]
        else : angle = None

        aaa = game.minecraft_chunk.__teleport_entity__(victim_entity, execute_var["dimension"], tp_pos, angle, bool(check_block))
        if aaa == Exception : return Response.Response_Template("$pos 无法进行碰撞检查").substitute(pos = tuple(tp_pos))
        if len(aaa) > 0 : return Response.Response_Template("已将下列实体传送至$pos:\n $name", 1, len(aaa)).substitute(
            name = ", ".join( (ID_tracker(i) for i in aaa) ) ,
            pos = tuple(("%.4f" % i for i in tp_pos))
        )
        else : return Response.Response_Template("没有实体执行了传送").substitute()


class tellraw :
    #{"rawtext":[{"text":"aaa "},{"selector":"@s[rm=1]"},{"text":" bbb "},{"selector":"@s"}]}
    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)

        json_str_list = [i["token"] for i in itertools.takewhile(lambda x : x["type"] != "All_Json_End", token_list[index:])]
        json_str_list.append(token_list[index + len(json_str_list)]["token"])
        a = json.loads( "".join( f"{i}" for i in json_str_list ) )
        b = Rawtext.Rawtext_Compiler(_game, (255,0,0), a)
        return functools.partial(cls.display, entity_get=entity_func, rawtext=b)

    def display(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, rawtext:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("已为以下玩家显示聊天栏信息：$player\n$msg", 1, 1).substitute(
            player = ", ".join( (ID_tracker(i) for i in entity_list) ),
            msg = rawtext(execute_var, game)
        )


class testfor :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index, entity_func = Selector.Selector_Compiler(_game, token_list, 1)
        return functools.partial(cls.test, entity_get=entity_func)

    def test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        
        return Response.Response_Template("发现了 $count 个实体：$entity", 1, len(entity_list)).substitute(
            count = len(entity_list),
            entity = ", ".join( (ID_tracker(i) for i in entity_list) ),
        )


class testforblock :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        poses = [ token_list[i]["token"] for i in range(1,4,1) ]
        block_id = ID_transfor(token_list[4]["token"])
        if block_id not in _game.minecraft_ident.blocks:
            raise CompileError("不存在的方块ID：%s" % block_id,pos=(token_list[5]["start"], token_list[5]["end"]))
        if 5 >= len(token_list) : block_state = {}
        elif token_list[5]["type"] == "Block_Data" : 
            block_state = int(token_list[5]["token"])
            if block_state == -1 : block_state = {}
        else : _,block_state = BlockState_Compiler( block_id, token_list, 5 )
        return functools.partial(cls.test, pos=poses, block_id=block_id, block_state=block_state)
    
    def test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:tuple, block_id:str, block_state:Union[dict,int]={}) :
        start_pos = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
        
        height_test = Constants.DIMENSION_INFO[execute_var["dimension"]]["height"]
        if not(height_test[0] <= start_pos[1] < height_test[1]) :
            return Response.Response_Template("$pos处于世界之外").substitute(pos=tuple(start_pos))
        if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], start_pos) :
            return Response.Response_Template("起始区域$pos为未加载的区块").substitute(pos=tuple(start_pos))

        aaa = Response.Response_Template("$pos方块与目标方块不相同").substitute(pos=tuple(start_pos))
        if isinstance(block_state, int) and block_state != -1 :
            test_block_obj = BaseNbtClass.block_nbt().__create__(block_id, block_state)
        
        block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], start_pos)
        block_obj = game.minecraft_chunk.block_mapping[block_index]
        if block_obj.Identifier != block_id : return aaa
        if isinstance(block_state, dict) and any([block_obj.BlockState[i] != block_state[i] for i in block_state]) : return aaa
        elif isinstance(block_state, int) and block_state != -1 :
            if any([block_obj.BlockState[i] != test_block_obj.BlockState[i] for i in test_block_obj.BlockState]) : return aaa
        block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], start_pos)

        return Response.Response_Template("$pos方块测试成功", 1, 1).substitute(pos=tuple(start_pos))


class testforblocks :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        poses = [ token_list[i]["token"] for i in range(1,10,1) ]
        if 10 >= len(token_list) : 
            return functools.partial(cls.test, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9])
        return functools.partial(cls.test, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9], 
            mask_mode=token_list[10]["token"])
    
    def error_test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start_pos1, end_pos1, start_pos2, end_pos2) :
        height_test = Constants.DIMENSION_INFO[execute_var["dimension"]]["height"]
        for i,j in [("起始位置", start_pos1),("结束位置", end_pos1),("目标起始位置", start_pos2),("目标结束位置", end_pos2)] :
            if not(height_test[0] <= j[1] < height_test[1]) :
                return Response.Response_Template("$id$pos处于世界之外",response_id=-2147483000).substitute(id=i, pos=tuple(j))

        for j in itertools.product(range(start_pos1[0]//16*16, end_pos1[0]//16*16+16, 16), range(start_pos1[2]//16*16, end_pos1[2]//16*16+16, 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], (j[0],0,j[1])) :
                return Response.Response_Template("起始区域$pos为未加载的区块",response_id=-2147483001).substitute(pos=tuple(start_pos1))

        for j in itertools.product(range(start_pos2[0]//16*16, end_pos2[0]//16*16+16, 16), range(start_pos2[2]//16*16, end_pos2[2]//16*16+16, 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], (j[0],0,j[1])) :
                return Response.Response_Template("目标区域$pos为未加载的区块",response_id=-2147483002).substitute(pos=tuple(start_pos1))

    def test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start1:tuple, end1:tuple, start2:tuple,
             mask_mode:Literal["all","masked"]="all", max_block:int=524288) :
        start_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start1, execute_var["rotate"])]
        end_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], end1, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos1, end_pos1)) :
            if pos_1 > pos_2 : start_pos1[index] = pos_2; end_pos1[index] = pos_1
        start_pos2 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start2, execute_var["rotate"])]
        end_pos2 = [start_pos2[i] + end_pos1[i] - start_pos1[i] for i in range(3)]

        aaa = testforblocks.error_test(execute_var, game, start_pos1, end_pos1, start_pos2, end_pos2)
        if isinstance(aaa, Response.Response_Template) : return aaa

        volue = [end_pos1[i] - start_pos1[i] + 1 for i in range(3)]
        if volue[0] * volue[1] * volue[2] > max_block : 
            return Response.Response_Template("区域大小超过524288个方块",response_id=-2147483003).substitute()


        pos_iter = itertools.zip_longest(
            itertools.product( range(start_pos1[0], end_pos1[0]+1), range(start_pos1[1], end_pos1[1]+1), range(start_pos1[2], end_pos1[2]+1) ),
            itertools.product( range(start_pos2[0], end_pos2[0]+1), range(start_pos2[1], end_pos2[1]+1), range(start_pos2[2], end_pos2[2]+1) ),
        )
        test_list = [False] * (volue[0] * volue[1] * volue[2])
        for index, (start_pos_xyz, test_pos_xyz) in enumerate(pos_iter) :
            start_block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], start_pos_xyz)
            test_block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], test_pos_xyz)
            if mask_mode == "masked" and start_block_index == 0 : continue
            if start_block_index != test_block_index : 
                return Response.Response_Template("区域$start ~ $end内存在不相同的方块").substitute(start=tuple(start_pos2), end=tuple(end_pos2))
            start_block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], start_pos_xyz)
            test_block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], test_pos_xyz)
            json1 = json.dumps(start_block_nbt, default=DataSave.encoding)
            json2 = json.dumps(test_block_nbt, default=DataSave.encoding)
            if hash(json1) != hash(json2) : 
                return Response.Response_Template("区域$start ~ $end内存在不相同的方块").substitute(start=tuple(start_pos2), end=tuple(end_pos2))
            test_list[index] = True

        success_counter = test_list.count(True)
        return Response.Response_Template("在$start ~ $end存在$count个相同方块", min(1,success_counter), success_counter).substitute(
            start=tuple(start_pos2), end=tuple(end_pos2), count=success_counter)


class tickingarea :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"] == "add" : 
            if token_list[2]["token"] == "circle" :
                from_pos = [token_list[3+i]["token"] for i in range(3)]
                radius = int(token_list[6]["token"])
                if not(1 <= radius <= 4) : raise CompileError("区块半径只能在 1~4 范围内", pos=(token_list[6]["start"], token_list[6]["end"]))
                if 7 >= len(token_list) : return functools.partial(cls.add_circle, from_pos=from_pos, radius=radius)
                tickarea_name = Quotation_String_transfor_1(token_list[7]["token"])
                if 8 >= len(token_list) : return functools.partial(cls.add_circle, from_pos=from_pos, radius=radius, name=tickarea_name)
                preload_value = bool( ("false","true").index(token_list[8]["token"]) )
                return functools.partial(cls.add_circle, from_pos=from_pos, radius=radius, name=tickarea_name, preload=preload_value)
            else :
                from_pos = [token_list[2+i]["token"] for i in range(3)]
                to_pos = [token_list[5+i]["token"] for i in range(3)]
                if 8 >= len(token_list) : return functools.partial(cls.add_area, from_pos=from_pos, to_pos=to_pos)
                tickarea_name = Quotation_String_transfor_1(token_list[8]["token"])
                if 9 >= len(token_list) : return functools.partial(cls.add_area, from_pos=from_pos, to_pos=to_pos, name=tickarea_name)
                preload_value = bool( ("false","true").index(token_list[9]["token"]) )
                return functools.partial(cls.add_area, from_pos=from_pos, to_pos=to_pos, name=tickarea_name, preload=preload_value)
        elif token_list[1]["token"] == "list" : 
            if 2 >= token_list.__len__() : return cls.print_area
            else : return functools.partial(cls.print_area, print_all=True)
        elif token_list[1]["token"] == "remove" : 
            if token_list[2]["type"] == "Tickingarea_Name" : return functools.partial(cls.remove_area, 
                name=Quotation_String_transfor_1(token_list[2]["token"]))
            else : return functools.partial(cls.remove_area, pos=[token_list[2+i]["token"] for i in range(3)])
        elif token_list[1]["token"] == "remove_all" : 
            return functools.partial(cls.remove_area, remove_all=True)
        elif token_list[1]["token"] == "preload" : 
            if token_list[2]["type"] == "Tickingarea_Name" : 
                if 3 >= len(token_list) : return functools.partial(cls.preload_set, 
                    name=Quotation_String_transfor_1(token_list[2]["token"]))
                else : 
                    preload_value = bool( ("false","true").index(token_list[3]["token"]) )
                    return functools.partial(cls.preload_set, 
                    name=Quotation_String_transfor_1(token_list[2]["token"]), preload=preload_value)
            else : 
                if 5 >= len(token_list) : return functools.partial(cls.preload_set, 
                    pos=[token_list[2+i]["token"] for i in range(3)])
                else : 
                    preload_value = bool( ("false","true").index(token_list[5]["token"]) )
                    return functools.partial(cls.preload_set, 
                    pos=[token_list[2+i]["token"] for i in range(3)], preload=preload_value)
        
    def add_circle(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, from_pos:List[str], radius:int, 
        name:str=None, preload:bool=False) :
        if game.minecraft_chunk.tickingarea.__len__() >= 10 : 
            return Response.Response_Template("常加载区块数量已达到最大值10个").substitute()
        if name in game.minecraft_chunk.tickingarea : 
            return Response.Response_Template("已存在常加载区块 $name").substitute(name = name)
        
        start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], from_pos, execute_var["rotate"])]
        template1 = {"type":"circle", "radius":radius, "dimension":execute_var["dimension"], "preload":preload, "force_load":[]}
        load_range = (
            start_pos[0] - (radius * 16) , start_pos[0] + 16 + (radius * 16) ,
            start_pos[2] - (radius * 16) , start_pos[2] + 16 + (radius * 16) ,
        )
        for chunk_pos in itertools.product(range(load_range[0], load_range[1], 16), range(load_range[2], load_range[3], 16)) :
            template1["force_load"].append(chunk_pos)     
   
        if name is None :
            for i in ["Area%s" % i for i in range(10)] : 
                if i in game.minecraft_chunk.tickingarea : continue
                game.minecraft_chunk.tickingarea[i] = template1
                return Response.Response_Template("成功添加了常加载区块 $name", 1, 1).substitute(name = i)
        else : 
            game.minecraft_chunk.tickingarea[name] = template1
            return Response.Response_Template("成功添加了常加载区块 $name", 1, 1).substitute(name = name)
    
    def add_area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, from_pos:List[str], to_pos:List[str], 
        name:str=None, preload:bool=False) :
        if game.minecraft_chunk.tickingarea.__len__() >= 10 : 
            return Response.Response_Template("常加载区块数量已达到最大值10个").substitute()
        if name in game.minecraft_chunk.tickingarea : 
            return Response.Response_Template("已存在常加载区块 $name").substitute(name = name)

        start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], from_pos, execute_var["rotate"])]
        end_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], to_pos, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos, end_pos)) :
            if pos_1 > pos_2 : start_pos[index] = pos_2; end_pos[index] = pos_1
        if len(range(start_pos[0], start_pos[2]+1, 16)) * len(range(end_pos[0], end_pos[2]+1, 16)) > 100 :
            return Response.Response_Template("常加载区块内记录的区块数量大于100个").substitute()

        template1 = {"type":"square", "dimension":execute_var["dimension"], "preload":preload, "force_load":[i for i in itertools.product(
            range(start_pos[0], end_pos[0]+1, 16), range(start_pos[2], end_pos[2]+1, 16))]}
        if name is None :
            for i in ["Area%s" % i for i in range(10)] : 
                if i in game.minecraft_chunk.tickingarea : continue
                game.minecraft_chunk.tickingarea[i] = template1
                return Response.Response_Template("成功添加了常加载区块 $name", 1, 1).substitute(name = i)
        else : 
            game.minecraft_chunk.tickingarea[name] = template1
            return Response.Response_Template("成功添加了常加载区块 $name", 1, 1).substitute(name = name)

    def print_area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, print_all:bool=False) :
        list1 = []
        temp1 = string.Template("维度 $dimension 常加载区块 $name : $pos1 ~ $pos2")
        temp2 = string.Template("维度 $dimension 常加载区块 $name : 半径 = $radius")
        for key,value in game.minecraft_chunk.tickingarea.items() :
            if not print_all and value["dimension"] != execute_var["dimension"] : continue
            if value["type"] == "square" : list1.append( temp1.substitute(dimension=value["dimension"], name=key, 
                pos1=tuple(value["force_load"][0]), pos2=tuple(value["force_load"][-1])) )
            elif value["type"] == "circle" :list1.append( temp2.substitute(dimension=value["dimension"], name=key, 
                radius=value["radius"]) )
        if list1 : return Response.Response_Template("$len 个常加载区块正在运行：\n$detial", 1, 1).substitute(len=len(list1), detial = "\n".join(list1))
        else : return Response.Response_Template("$len 个常加载区块正在运行", 1, 1).substitute(len=len(list1))

    def remove_area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]=None, 
                    name:str=None, remove_all:bool=None) :
        remove_list = []
        if pos :
            start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
            for key,value in game.minecraft_chunk.tickingarea.items() :
                if (start_pos[0], start_pos[2]) not in [tuple(i) for i in value["force_load"]] : continue
                remove_list.append(key)
            if len(remove_list) == 0 : return Response.Response_Template("$pos 没有记录的常加载区块").substitute(pos=tuple(start_pos))
        if name :
            if name not in game.minecraft_chunk.tickingarea : 
                return Response.Response_Template("不存在常加载区块 $name").substitute(name = name)
            remove_list.append(name)
        if remove_all : remove_list.extend(list(game.minecraft_chunk.tickingarea))
        
        for i in remove_list : del game.minecraft_chunk.tickingarea[i]
        return Response.Response_Template("已移除常加载区块：$name", 1, 1).substitute(name = ", ".join(remove_list))

    def preload_set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]=None, 
                    name:str=None, preload:bool=None) :
        area_list = []
        if pos :
            start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
            for key,value in game.minecraft_chunk.tickingarea.items() :
                if (start_pos[0], start_pos[2]) not in value["force_load"] : continue
                area_list.append(key)
        if name :
            if name not in game.minecraft_chunk.tickingarea : 
                return Response.Response_Template("不存在常加载区块 $name").substitute(name = name)
            area_list.append(name)
        
        if len(area_list) == 0 : return Response.Response_Template("$pos 没有记录的常加载区块").substitute(pos=tuple(pos))
        if preload is not None :
            for i in area_list : game.minecraft_chunk.tickingarea[i]["preload"] = preload
            return Response.Response_Template("已修改常加载区块的预加载：$name", 1, 1).substitute(name = ", ".join(area_list))
        else :
            if name is not None : return Response.Response_Template("常加载区块 $name 的预加载值为 $value", 1, 1).substitute(
                name = ", ".join(area_list), value = game.minecraft_chunk.tickingarea[name]["preload"])
            else : return Response.Response_Template("常加载区块 $pos 的预加载值为 $value", 1, 1).substitute(
                pos = tuple(pos), value = any( (game.minecraft_chunk.tickingarea[i]["preload"] for i in area_list) ))


class time :

    time_point = {"day":1000, "noon":6000, "sunset":12000, "night":13000, "midnight":18000, "sunrise":23000}

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"] == "query" : 
            return functools.partial(cls.query, mode=token_list[2]["token"])
        if token_list[1]["token"] == "add" : 
            return functools.partial(cls.add, value=int(token_list[2]["token"]))
        if token_list[1]["token"] == "set" : 
            if token_list[2]["type"] == "Time_Int" : value = int(token_list[2]["token"])
            else : value = token_list[2]["token"]
            return functools.partial(cls.set, value=value)
            
    def query(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, mode:Literal["daytime","gametime","day"]) :
        success_msg = Response.Response_Template("查询到 $mode 的值为 $sss", 1, 1)
        if mode == "daytime" : return success_msg.substitute(mode=mode, sss=game.minecraft_world.day_count%24000)
        elif mode == "day" : return success_msg.substitute(mode=mode, sss=game.minecraft_world.day_time)
        elif mode == "gametime" : return success_msg.substitute(mode=mode, sss=game.minecraft_world.game_time)

    def add(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, value:int) :
        game.minecraft_world.day_time += value
        return Response.Response_Template("时间增加了 $sss", 1, value).substitute(value=value)

    def set(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, value:Union[int,str]) :
        if isinstance(value, int) : 
            game.minecraft_world.day_count = np.int32(value)
            game.minecraft_world.day_time = game.minecraft_world.day_count // 24000
        else :
            time1 = time.time_point[value]
            if game.minecraft_world.day_count > (game.minecraft_world.day_time * 24000 + time1) :
                game.minecraft_world.day_count = np.int32((game.minecraft_world.day_time + 1) * 24000 + time1)
            else : game.minecraft_world.day_count = np.int32(game.minecraft_world.day_time * 24000 + time1)
            game.minecraft_world.day_time = game.minecraft_world.day_count // 24000
            return Response.Response_Template("将时间设定为 $sss").substitute(sss=game.minecraft_world.day_count)


class titleraw :
    #{"rawtext":[{"text":"aaa "},{"selector":"@s[rm=1]"},{"text":" bbb "},{"selector":"@s"}]}
    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        if token_list[index]["token"] in ("clear", "reset") : 
            return functools.partial(cls.clear_or_reset, entity_get=entity_func, mode=token_list[index]["token"])
        elif token_list[index]["token"] == "times" : return functools.partial(cls.set_time, entity_get=entity_func)
        elif token_list[index]["token"] in ("title", "subtitle", "actionbar") : 
            ttt = token_list[index]["token"] ; index += 1
            if token_list[index]["type"] == "Msg" :
                aa,bb = Msg_Compiler(_game, token_list[index + 1]["token"], token_list[index + 1]["start"])
                return functools.partial(cls.display_1, entity_get=entity_func, type1=ttt, msg=aa, search_entity=bb)
            else :
                json_str_list = [i["token"] for i in itertools.takewhile(lambda x : x["type"] != "All_Json_End", token_list[index:])]
                json_str_list.append(token_list[index + len(json_str_list)]["token"])
                a = json.loads( "".join( f"{i}" for i in json_str_list ) )
                b = Rawtext.Rawtext_Compiler(_game, (255,0,0), a)
                return functools.partial(cls.display_2, entity_get=entity_func, type1=ttt, rawtext=b)
    
    def clear_or_reset(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, mode:Literal["clear", "reset"]) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if mode == "clear" :
            return Response.Response_Template("已为以下玩家清除所有显示的标题：$player", 1, 1).substitute(
                player = ", ".join( (ID_tracker(i) for i in entity_list) )
            )
        elif mode == "reset" :
            return Response.Response_Template("已为以下玩家重置所有的标题设置：$player", 1, 1).substitute(
                player = ", ".join( (ID_tracker(i) for i in entity_list) )
            )

    def set_time(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("已为以下玩家设置标题淡入淡出时间：$player", 1, 1).substitute(
            player = ", ".join( (ID_tracker(i) for i in entity_list) )
        )

    def display_1(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, type1:Literal["title", "subtitle", "actionbar"], msg:str, search_entity:List[Callable]) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        list1 = [i(execute_var, game) for i in search_entity]
        msg_temp = msg % tuple([
            (", ".join( (ID_tracker(i) for i in entities) ) if isinstance(entities, list) else "") for entities in list1
        ])
        return Response.Response_Template("已为以下玩家设置 $type1 标题：$player\n$msg", 1, 1).substitute(
            type1 = type1,
            player = ", ".join( (ID_tracker(i) for i in entity_list) ),
            msg = msg_temp
        )

    def display_2(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, type1:Literal["title", "subtitle", "actionbar"], rawtext:Callable) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        return Response.Response_Template("已为以下玩家设置 $type1 标题：$player\n$msg", 1, 1).substitute(
            type1 = type1,
            player = ", ".join( (ID_tracker(i) for i in entity_list) ),
            msg = rawtext(execute_var, game)
        )


class toggledownfall :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        return cls.change_weather
    
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
        if token_list[1]["token"] == "add" : 
            volume_id = Quotation_String_transfor_1(token_list[2]["token"])
            if volume_id not in _game.minecraft_ident.volumeareas : 
                raise CompileError("不存在的功能域 ID： %s" % volume_id, 
                pos=(token_list[2]["start"], token_list[2]["end"]))
            from_pos = [token_list[3+i]["token"] for i in range(3)]
            to_pos = [token_list[6+i]["token"] for i in range(3)]
            volume_name = Quotation_String_transfor_1(token_list[9]["token"])
            return functools.partial(cls.add_area, id=volume_id, from_pos=from_pos, to_pos=to_pos, name=volume_name)
        elif token_list[1]["token"] == "list" : 
            if 2 >= token_list.__len__() : return cls.print_area
            else : return functools.partial(cls.print_area, print_all=True)
        elif token_list[1]["token"] == "remove" : 
            if token_list[2]["type"] == "Volumearea_Name" : return functools.partial(cls.remove_area, 
                name=Quotation_String_transfor_1(token_list[2]["token"]))
            else : return functools.partial(cls.remove_area, pos=[token_list[2+i]["token"] for i in range(3)])
        elif token_list[1]["token"] == "remove_all" : 
            return functools.partial(cls.remove_area, remove_all=True)
    
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
        if list1 : return Response.Response_Template("$len 个功能域正在运行：\n$detial", 1, 1).substitute(len=len(list1), detial = "\n".join(list1))
        else : return Response.Response_Template("$len 个功能域正在运行", 1, 1).substitute(len=len(list1))

    def remove_area(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]=None, 
                    name:str=None, remove_all:bool=None) :
        remove_list = []
        if pos :
            start_pos = [math.floor(i)//16*16 for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
            for key,value in game.minecraft_chunk.volumearea.items() :
                if not(value["effect_area"][0][0] <= start_pos[0] <= value["effect_area"][1][0]) : continue
                if not(value["effect_area"][0][1] <= start_pos[2] <= value["effect_area"][1][1]) : continue
                remove_list.append(key)
            if len(remove_list) == 0 : return Response.Response_Template("$pos 没有可以记录的功能域").substitute(pos=tuple(start_pos))
        if name :
            if name not in game.minecraft_chunk.volumearea : return Response.Response_Template("不存在功能域 $name").substitute(name = name)
            remove_list.append(name)
        if remove_all : remove_list.extend(list(game.minecraft_chunk.volumearea))
        
        for i in remove_list : del game.minecraft_chunk.volumearea[i]
        return Response.Response_Template("已移除功能域：$name", 1, 1).substitute(name = ", ".join(remove_list))


class tell :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 1, is_player=True)
        aa,bb = Msg_Compiler(_game, token_list[index]["token"], token_list[index]["start"])
        return functools.partial(cls.send_msg, entity_get=entity_func, msg=aa, search_entity=bb)

    def send_msg(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, msg:str, search_entity:List[Callable]) :
        entity_list = entity_get(execute_var, game)
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        list1 = [i(execute_var, game) for i in search_entity]
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
        if token_list[1]["token"] == "query" : return cls.query
        weather_name = token_list[1]["token"]
        if 2 >= token_list.__len__() : return functools.partial(cls.set, weather_name=weather_name)
        time = int(token_list[2]["token"])
        return functools.partial(cls.set, weather_name=weather_name, time=time)

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
        if token_list[1]["token"][-1] in {"L", "l"} : lvl_value = int(token_list[1]["token"][:-1]) ; func = cls.modify_level
        else : lvl_value = int(token_list[1]["token"]) ; func = cls.modify_point

        if 2 >= token_list.__len__() : return functools.partial(func, entity_get=None, value=lvl_value)
        index,entity_func = Selector.Selector_Compiler(_game, token_list, 2, is_player=True)
        return functools.partial(func, entity_get=entity_func, value=lvl_value)

    def modify_level(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None, value:int=0) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
        if isinstance(entity_list, Response.Response_Template) : return entity_list
        if not isinstance(entity_list[0], BaseNbtClass.entity_nbt) or entity_list[0].Identifier != "minecraft:player" : 
            return Response.Response_Template("没有与目标选择器匹配的目标").substitute()

        for player1 in entity_list : player1.PlayerLevel = max(np.int32(0), player1.PlayerLevel + value)
        temp1 = string.Template("$player 的等级变为 $value")
        return Response.Response_Template("以下玩家的经验值发生变化：\n$msg", 1, len(entity_list)).substitute(
            msg="\n".join( (temp1.substitute(player = ID_tracker(i), value=i.PlayerLevel) for i in entity_list) )
        )

    def modify_point(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable=None, value:int=0) :
        entity_list = entity_get(execute_var, game) if entity_get else [execute_var["executer"]]
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

