from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction,DataSave
from . import Selector,Rawtext,CompileError,CommandParser
from . import Quotation_String_transfor_1,ID_transfor,BlockState_Compiler,Msg_Compiler
import functools,string,random,re,math,itertools,json
from typing import Dict,Union,List,Tuple,Literal,Callable










class teleport :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        pass


class testforblock :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :

        poses = [ token_list[i]["token"].group() for i in range(1,4,1) ]
        block_id = ID_transfor(token_list[4]["token"].group())
        if block_id not in _game.minecraft_ident.blocks:
            raise CompileError("不存在的方块ID：%s" % block_id,pos=(token_list[5]["token"].start(), token_list[5]["token"].end()))
        
        if 5 >= len(token_list) : block_state = {}
        elif token_list[5]["type"] == "Block_Data" : 
            block_state = int(token_list[5]["token"].group())
            if not(-1 <= block_state <= 32767) : raise CompileError("%s 不是一个有效的数据值" % block_state,
            pos=(token_list[5]["token"].start(), token_list[5]["token"].end()))
            if block_state == -1 : block_state = {}
        else : _,block_state = BlockState_Compiler( block_id, token_list, 5 )
        return functools.partial(cls.test, game=_game, pos=poses, block_id=block_id, block_state=block_state)
    
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

        poses = [ token_list[i]["token"].group() for i in range(1,10,1) ]
        if 10 >= len(token_list) : 
            return functools.partial(cls.test, game=_game, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9])
        return functools.partial(cls.test, game=_game, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9], 
            mask_mode=token_list[10]["token"].group())
    
    def error_test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start_pos1, end_pos1, start_pos2, end_pos2) :
        height_test = Constants.DIMENSION_INFO[execute_var["dimension"]]["height"]
        for i,j in [("起始位置", start_pos1),("结束位置", end_pos1),("目标起始位置", start_pos2),("目标结束位置", end_pos2)] :
            if not(height_test[0] <= j[1] < height_test[1]) :
                return Response.Response_Template("$id$pos处于世界之外").substitute(id=i, pos=tuple(j))

        for j in itertools.product(range(start_pos1[0]//16*16, end_pos1[0]//16*16+16, 16), range(start_pos1[2]//16*16, end_pos1[2]//16*16+16, 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], (j[0],0,j[1])) :
                return Response.Response_Template("起始区域$pos为未加载的区块").substitute(pos=tuple(start_pos1))

        for j in itertools.product(range(start_pos2[0]//16*16, end_pos2[0]//16*16+16, 16), range(start_pos2[2]//16*16, end_pos2[2]//16*16+16, 16)) :
            if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], (j[0],0,j[1])) :
                return Response.Response_Template("目标区域$pos为未加载的区块").substitute(pos=tuple(start_pos1))

    def test(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, start1:tuple, end1:tuple, start2:tuple,
             mask_mode:Literal["all","masked"]="all") :
        start_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start1, execute_var["rotate"])]
        end_pos1 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], end1, execute_var["rotate"])]
        for index,(pos_1,pos_2) in enumerate(itertools.zip_longest(start_pos1, end_pos1)) :
            if pos_1 > pos_2 : start_pos1[index] = pos_2; end_pos1[index] = pos_1
        start_pos2 = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], start2, execute_var["rotate"])]
        end_pos2 = [start_pos2[i] + end_pos1[i] - start_pos1[i] for i in range(3)]

        aaa = testforblocks.error_test(execute_var, game, start_pos1, end_pos1, start_pos2, end_pos2)
        if isinstance(aaa, Response.Response_Template) : return aaa

        volue = [end_pos1[i] - start_pos1[i] + 1 for i in range(3)]
        if volue[0] * volue[1] * volue[2] > 524288 : return Response.Response_Template("区域大小超过524288个方块").substitute()


        pos_iter = itertools.zip_longest(
            itertools.product( range(start_pos1[0], end_pos1[0]+1), range(start_pos1[1], end_pos1[1]+1), range(start_pos1[2], end_pos1[2]+1) ),
            itertools.product( range(start_pos2[0], end_pos2[0]+1), range(start_pos2[1], end_pos2[1]+1), range(start_pos2[2], end_pos2[2]+1) ),
        )
        test_list = [False] * (volue[0] * volue[1] * volue[2])
        for index, (start_pos_xyz, test_pos_xyz) in enumerate(pos_iter) :
            start_block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], start_pos_xyz)
            test_block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], test_pos_xyz)
            if mask_mode == "masked" and start_block_index == 0 : continue
            if start_block_index != test_block_index : return Response.Response_Template("区域内存在不相同的方块").substitute()
            start_block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], start_pos_xyz)
            test_block_nbt = game.minecraft_chunk.____find_block_nbt____(execute_var["dimension"], test_pos_xyz)
            json1 = json.dumps(start_block_nbt, default=DataSave.encoding)
            json2 = json.dumps(test_block_nbt, default=DataSave.encoding)
            if hash(json1) != hash(json2) : return Response.Response_Template("区域内存在不相同的方块").substitute()
            test_list[index] = True

        success_counter = test_list.count(True)
        return Response.Response_Template("在$start ~ $end存在$count个相同方块", min(1,success_counter), success_counter).substitute(
            start=tuple(start_pos2), end=tuple(end_pos2), count=success_counter)


class tickingarea :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) :
        if token_list[1]["token"].group() == "add" : 
            if token_list[2]["token"].group() == "circle" :
                from_pos = [token_list[3+i]["token"].group() for i in range(3)]
                radius = int(token_list[6]["token"].group())
                if not(1 <= radius <= 4) : raise CompileError("区块半径只能在 1~4 范围内", pos=(token_list[6]["token"].start(), token_list[6]["token"].end()))
                if 7 >= len(token_list) : return functools.partial(cls.add_circle, game=_game, from_pos=from_pos, radius=radius)
                tickarea_name = Quotation_String_transfor_1(token_list[7]["token"].group())
                if 8 >= len(token_list) : return functools.partial(cls.add_circle, game=_game, from_pos=from_pos, radius=radius, name=tickarea_name)
                preload_value = bool( ("false","true").index(token_list[8]["token"].group()) )
                return functools.partial(cls.add_circle, game=_game, from_pos=from_pos, radius=radius, name=tickarea_name, preload=preload_value)
            else :
                from_pos = [token_list[2+i]["token"].group() for i in range(3)]
                to_pos = [token_list[5+i]["token"].group() for i in range(3)]
                if 8 >= len(token_list) : return functools.partial(cls.add_area, game=_game, from_pos=from_pos, to_pos=to_pos)
                tickarea_name = Quotation_String_transfor_1(token_list[8]["token"].group())
                if 9 >= len(token_list) : return functools.partial(cls.add_area, game=_game, from_pos=from_pos, to_pos=to_pos, name=tickarea_name)
                preload_value = bool( ("false","true").index(token_list[9]["token"].group()) )
                return functools.partial(cls.add_area, game=_game, from_pos=from_pos, to_pos=to_pos, name=tickarea_name, preload=preload_value)
        elif token_list[1]["token"].group() == "list" : 
            if 2 >= token_list.__len__() : return functools.partial(cls.print_area, game=_game)
            else : return functools.partial(cls.print_area, game=_game, print_all=True)
        elif token_list[1]["token"].group() == "remove" : 
            if token_list[2]["type"] == "Tickingarea_Name" : return functools.partial(cls.remove_area, game=_game, 
                name=Quotation_String_transfor_1(token_list[2]["token"].group()))
            else : return functools.partial(cls.remove_area, game=_game, pos=[token_list[2+i]["token"].group() for i in range(3)])
        elif token_list[1]["token"].group() == "remove_all" : 
            return functools.partial(cls.remove_area, game=_game, remove_all=True)
        elif token_list[1]["token"].group() == "preload" : 
            if token_list[2]["type"] == "Tickingarea_Name" : 
                if 3 >= len(token_list) : return functools.partial(cls.preload_set, game=_game, 
                    name=Quotation_String_transfor_1(token_list[2]["token"].group()))
                else : 
                    preload_value = bool( ("false","true").index(token_list[3]["token"].group()) )
                    return functools.partial(cls.preload_set, game=_game, 
                    name=Quotation_String_transfor_1(token_list[2]["token"].group()), preload=preload_value)
            else : 
                if 5 >= len(token_list) : return functools.partial(cls.preload_set, game=_game, 
                    pos=[token_list[2+i]["token"].group() for i in range(3)])
                else : 
                    preload_value = bool( ("false","true").index(token_list[5]["token"].group()) )
                    return functools.partial(cls.preload_set, game=_game, 
                    pos=[token_list[2+i]["token"].group() for i in range(3)], preload=preload_value)
        
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
            if ((chunk_pos[0] - start_pos[0]) ** 2 + (chunk_pos[1]- start_pos[2]) ** 2) > ((radius * 16) ** 2) : continue
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
            range(start_pos[0], start_pos[2]+1, 16), range(end_pos[0], end_pos[2]+1, 16))]}
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
        if token_list[1]["token"].group() == "query" : 
            return functools.partial(cls.query, game=_game, mode=token_list[2]["token"].group())
        if token_list[1]["token"].group() == "add" : 
            return functools.partial(cls.add, game=_game, value=int(token_list[2]["token"].group()))
        if token_list[1]["token"].group() == "set" : 
            if token_list[2]["type"] == "Time_Int" : value = int(token_list[2]["token"].group())
            else : value = token_list[2]["token"].group()
            return functools.partial(cls.set, game=_game, value=value)
            
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
                json_str_list = [i["token"].group() for i in itertools.takewhile(lambda x : x["type"] != "All_Json_End", token_list[index:])]
                json_str_list.append(token_list[index + len(json_str_list) + 1])
                a = json.loads( "".join( json_str_list ))
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

