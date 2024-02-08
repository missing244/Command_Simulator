from .. import COMMAND_TOKEN,COMMAND_CONTEXT,ID_tracker,Response
from ... import RunTime,Constants,BaseNbtClass,np,MathFunction,EntityComponent,BlockComponent
from . import Selector,CompileError,CommandParser,Command2
from . import Quotation_String_transfor_1,ID_transfor,BlockState_Compiler,ItemComponent_Compiler
import functools,string,random,math,itertools,json,copy
from typing import Dict,Union,List,Tuple,Literal,Callable,Generator,Iterator
DIMENSION_LIST = tuple(Constants.DIMENSION_INFO)
CONTEXT_GENERATER = Generator[Union[Tuple[int, COMMAND_CONTEXT, Response.Response_Template], COMMAND_CONTEXT, None], None, None]
SCORE_COMPARE = {
    "=":lambda a,b : a == b, ">":lambda a,b : a > b, "<":lambda a,b : a < b, "<=":lambda a,b : a <= b, ">=":lambda a,b : a >= b,
}

def tramsfor_context(execute_var:COMMAND_CONTEXT,response:Response.Response_Template) :
    pos1 = "[%.3f,%.3f,%.3f]" % tuple(execute_var["pos"])
    rot1 = "(%.1f,%.1f)" % tuple(execute_var["rotate"])
    return "执行者 %s 在 %s 维度\n坐标 %s 以视角 %s 有以下命令反馈: \n%s" % (
        ID_tracker(execute_var["executer"]), execute_var["dimension"], pos1, rot1, response.command_msg)

def head_generate(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, test_func:List[Callable] = []) :
    if not test_func : yield execute_var
    for index,func in enumerate(test_func) : 
        b = func(execute_var, game)
        if not b : yield (1, execute_var, b) ; continue
        if index + 1 == len(test_func) : yield execute_var
    yield None




def as_at_pos(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable,
    pos:List[str], test_func:List[Callable] = []) -> CONTEXT_GENERATER :
    entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
    if isinstance(entity_list, Response.Response_Template) : yield (0, execute_var, entity_list)

    for entity in entity_list :
        a = {"executer":entity, "dimension":DIMENSION_LIST[entity.Dimension], 
             "pos":MathFunction.mc_pos_compute(entity.Pos, pos, entity.Rotation), 
             "rotate":list(entity.Rotation), "version":execute_var['version']}
        
        if not test_func : yield a
        for index,func in enumerate(test_func) : 
            b = func(a, game)
            if not b : yield (1, a, b) ; break
            if index + 1 == len(test_func) : yield a

    yield None

def if_block(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str], block_id:str, block_state=-1) :
    pos_xyz = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
    if not game.minecraft_chunk.____in_build_area____(execute_var["dimension"], pos_xyz) :
        return Response.Response_Template("$pos处于世界之外").substitute(pos=tuple(pos_xyz))
    if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], pos_xyz) :
        return Response.Response_Template("$pos为未加载的区块").substitute(pos=tuple(pos_xyz))

    block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], pos_xyz)
    block_map = game.minecraft_chunk.block_mapping
    if (block_state == -1 or block_state == {}) and block_map[block_index].Identifier != block_id :
        return Response.Response_Template("$pos位置的方块测试失败").substitute(pos=tuple(pos_xyz))
    else :
        new_block_index = game.minecraft_chunk.____find_block_mapping____(block_id, block_state)
        if new_block_index != block_index : return Response.Response_Template("$pos位置的方块测试失败").substitute(pos=tuple(pos_xyz))
    return Response.Response_Template("$pos位置的方块测试通过", 1, 1).substitute(pos=tuple(pos_xyz))

class execute_1_19 :

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN, Version:Tuple[int]) : 
        from . import Start_Compile
        index = 1 ; subcommand_list:List[functools.partial] = [functools.partial(head_generate)]
        while 1 :
            index, entity_func = Selector.Selector_Compiler(_game, token_list, index)
            pos1 = [token_list[i]["token"].group() for i in range(index, index+3, 1)] ; index += 3
            subcommand_list.append( functools.partial(as_at_pos, entity_get=entity_func, pos=pos1) )
            if token_list[index]["token"].group() == "execute" : index += 1 ; continue
            elif token_list[index]["token"].group() == "detect" : 
                pos2 = [token_list[i]["token"].group() for i in range(index+1, index+4, 1)] ; index += 4
                block_id = ID_transfor(token_list[index]["token"].group()) ; index += 1
                if block_id not in _game.minecraft_ident.blocks : raise CompileError("不存在的方块ID：%s" % block_id, 
                    pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
                block_state = int(token_list[index]["token"].group()) ; index += 1

                if not(-1 <= block_state <= 32767) : raise CompileError("%s 不是一个有效的数据值" % block_state,
                pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
                if block_state == -1 : block_state = {}

                if "test_func" not in subcommand_list[-1].keywords : subcommand_list[-1].keywords["test_func"] = []
                test_func = functools.partial(if_block, pos=pos2, block_id=block_id, block_state=block_state)
                subcommand_list[-1].keywords["test_func"].append(test_func)
                if token_list[index]["token"].group() == "execute" : index += 1 ; continue
            func = Start_Compile(token_list[index:], _game, Version)
            if isinstance(func, tuple) : raise func[1]
            else : break
        return functools.partial(cls.run, SubCommands=subcommand_list, CommandCall=func)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, SubCommands:List[Callable], CommandCall:Callable) :
        a = Response.Response_Template("$msg", mcfunction=CommandCall is function.run)

        Exe_Var_Generate:List[CONTEXT_GENERATER] = [SubCommands[0](execute_var, game)] 
        SubCommands_len = len(SubCommands) ; msg_list:List[str] = [] ; success_count = 0
        while Exe_Var_Generate :
            now_execute_var = next(Exe_Var_Generate[-1])
            if now_execute_var is None : Exe_Var_Generate.pop() ; continue
            if isinstance(now_execute_var, tuple) :
                msg_list.append( tramsfor_context(now_execute_var[1], now_execute_var[2]) )
                if not now_execute_var[0] : Exe_Var_Generate.pop()
                continue

            Generate_list_len = len(Exe_Var_Generate)
            if Generate_list_len < SubCommands_len : 
                Exe_Var_Generate.append(SubCommands[Generate_list_len](now_execute_var, game))
            else :
                Command_Back:Response.Response_Template = CommandCall(now_execute_var, game)
                success_count += Command_Back.success_count
                msg_list.append( tramsfor_context(now_execute_var, Command_Back) )
                if CommandCall is function.run : 
                    for i in Command_Back.Function_Feedback : a.add_function_feedback(i)

        a.success_count = min(1,success_count)
        a.result_count = success_count
        return a.substitute(msg = "\n\n".join(msg_list))




def subcommand_as(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, 
    test_func:List[Callable] = []) -> CONTEXT_GENERATER :
    entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
    if isinstance(entity_list, Response.Response_Template) : yield (0, execute_var, entity_list)

    for entity in entity_list :
        a = execute_var.copy()
        a["executer"] = entity

        if not test_func : yield a
        for index,func in enumerate(test_func) : 
            b = func(a, game)
            if not b : yield (1, a, b) ; break
            if index + 1 == len(test_func) : yield a

    yield None

def subcommand_at(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, 
    test_func:List[Callable] = []) -> CONTEXT_GENERATER :
    entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
    if isinstance(entity_list, Response.Response_Template) : yield (0, execute_var, entity_list)

    for entity in entity_list :
        a = execute_var.copy()
        a['dimension'] = DIMENSION_LIST[entity.Dimension]
        a["pos"] = list(entity.Pos)
        a["rotate"] = list(entity.Rotation)
        
        if not test_func : yield a
        for index,func in enumerate(test_func) : 
            b = func(a, game)
            if not b : yield (1, a, b) ; break
            if index + 1 == len(test_func) : yield a

    yield None

def subcommand_facing_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable, anchor:Literal["feet","eyes"],
    test_func:List[Callable] = []) -> CONTEXT_GENERATER :
    entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
    if isinstance(entity_list, Response.Response_Template) : yield (0, execute_var, entity_list)

    for entity in entity_list :
        a = execute_var.copy()
        pos1 = list(entity_list[0].Pos)
        if anchor == "eyes" : pos1[1] = entity_list[0].Pos[1] + entity_list[0].Collision['height'] * 0.844444444444444444444
        a["rotate"] = MathFunction.rotation_angle(execute_var["pos"], entity.Pos)

        if not test_func : yield a
        for index,func in enumerate(test_func) : 
            b = func(a, game)
            if not b : yield (1, a, b) ; break
            if index + 1 == len(test_func) : yield a

    yield None

def subcommand_positioned_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable,
    test_func:List[Callable] = []) -> CONTEXT_GENERATER :
    entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
    if isinstance(entity_list, Response.Response_Template) : yield (0, execute_var, entity_list)

    for entity in entity_list :
        a = execute_var.copy()
        a["pos"] = list(entity.Pos)

        if not test_func : yield a
        for index,func in enumerate(test_func) : 
            b = func(a, game)
            if not b : yield (1, a, b) ; break
            if index + 1 == len(test_func) : yield a

    yield None

def subcommand_rotated_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, entity_get:Callable,
    test_func:List[Callable] = []) -> CONTEXT_GENERATER :
    entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
    if isinstance(entity_list, Response.Response_Template) : yield (0, execute_var, entity_list)

    for entity in entity_list :
        a = execute_var.copy()
        a["rotate"] = list(entity.Rotation)

        if not test_func : yield a
        for index,func in enumerate(test_func) : 
            b = func(a, game)
            if not b : yield (1, a, b) ; break
            if index + 1 == len(test_func) : yield a

    yield None


def subcommand_align(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, x:bool, y:bool, z:bool) :
    if x : execute_var["pos"][0] = math.floor(execute_var["pos"][0])
    if y : execute_var["pos"][1] = math.floor(execute_var["pos"][1])
    if z : execute_var["pos"][2] = math.floor(execute_var["pos"][2])
    return True

def subcommand_in(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, dimension:str) :
    value = Constants.DIMENSION_INFO[execute_var["dimension"]]["scale"] / Constants.DIMENSION_INFO[dimension]["scale"]
    execute_var["pos"][0] = execute_var["pos"][0] * value
    execute_var["pos"][2] = execute_var["pos"][2] * value
    execute_var["dimension"] = dimension
    return True

def subcommand_anchored(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, type:Literal["eyes","feet"]) :
    if not isinstance(execute_var["executer"], BaseNbtClass.entity_nbt) : return True
    execute_var["pos"][0] = execute_var["executer"].Pos[0]
    execute_var["pos"][2] = execute_var["executer"].Pos[2]
    if type == "feet" : execute_var["pos"][1] = execute_var["executer"].Pos[1]
    else : execute_var["pos"][1] = execute_var["executer"].Pos[1] + execute_var["executer"].Collision['height'] * 0.844444444444444444444
    return True

def subcommand_facing_pos(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]) :
    pos_xyz = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
    execute_var["rotate"] = MathFunction.rotation_angle(execute_var["pos"], pos_xyz)
    return True

def subcommand_positioned_pos(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, pos:List[str]) :
    execute_var["pos"] = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
    return True

def subcommand_rotated_pos(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, rotate:List[str]) :
    execute_var["rotate"][0] = MathFunction.mc_rotate_compute(execute_var["rotate"][0], rotate[0], "ry", True)
    execute_var["rotate"][1] = MathFunction.mc_rotate_compute(execute_var["rotate"][1], rotate[1], "rx", True)
    return True

def subcommand_test_block(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, unless:bool, pos:List[str], block_id:str, block_state=-1) :
    m1 = pos_xyz = [math.floor(i) for i in MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])]
    if not game.minecraft_chunk.____in_build_area____(execute_var["dimension"], pos_xyz) :
        return Response.Response_Template("$pos处于世界之外").substitute(pos=tuple(m1))
    if not game.minecraft_chunk.____in_load_chunk____(execute_var["dimension"], pos_xyz) :
        return Response.Response_Template("$pos为未加载的区块").substitute(pos=tuple(m1))

    pos_xyz = MathFunction.mc_pos_compute(execute_var["pos"], pos, execute_var["rotate"])
    block_index = game.minecraft_chunk.____find_block____(execute_var["dimension"], pos_xyz)
    block_map = game.minecraft_chunk.block_mapping
    if block_state == -1 or block_state == {} :
        if (block_map[block_index].Identifier != block_id) ^ unless :
            return Response.Response_Template("$pos位置的方块测试失败").substitute(pos=tuple(m1))
    else :
        new_block_index = game.minecraft_chunk.____find_block_mapping____(block_id, block_state)
        if (new_block_index != block_index) ^ unless: 
            return Response.Response_Template("$pos位置的方块测试失败").substitute(pos=tuple(m1))
    return Response.Response_Template("$pos位置的方块测试通过", 1, 1).substitute(pos=tuple(m1))

def subcommand_test_blocks(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, unless:bool, start1:tuple, end1:tuple, 
    start2:tuple, mask_mode:Literal["all","masked"]) :
    a:Response.Response_Template = Command2.testforblocks.test(execute_var, game, start1, end1, start2, mask_mode, 32768)
    if isinstance(a.response_id, int) and -2147483003 <= a.response_id <= 2147483000 : return a

    if bool(a) ^ unless : return Response.Response_Template("测试通过，计数：$count", 1, a.result_count).substitute(count=a.result_count)
    else : return Response.Response_Template("测试失败，计数：$count", 0, 0).substitute(count=a.result_count)

def subcommand_test_entity(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, unless:bool, entity_get:Callable) :
    entity_list:List[BaseNbtClass.entity_nbt] = entity_get(execute_var, game)
    if isinstance(entity_list, Response.Response_Template) : entity_list = []

    if bool(entity_list) ^ unless : 
        return Response.Response_Template("测试通过，计数：$count", 1, len(entity_list)).substitute(count=len(entity_list))
    else : return Response.Response_Template("测试失败，计数：$count", 0, 0).substitute(count=len(entity_list))

def subcommand_test_score_compare(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, unless:bool, entity_get1:Union[str,Callable],
    scb1:str, mode:str, entity_get2:Union[str,Callable], scb2:str) :
    if not game.minecraft_scoreboard.____scb_exists____(scb1) : 
        return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb1)
    if not game.minecraft_scoreboard.____scb_exists____(scb2) : 
       return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb2)
        
    if isinstance(entity_get1, str) : scb_names1 = [entity_get1]
    else :
        scb_names1:List[BaseNbtClass.entity_nbt] = entity_get1(execute_var, game)
        if isinstance(scb_names1, Response.Response_Template) : return scb_names1
    if isinstance(entity_get2, str) : scb_names2 = [entity_get2]
    else :
        scb_names2:List[BaseNbtClass.entity_nbt] = entity_get2(execute_var, game)
        if isinstance(scb_names2, Response.Response_Template) : return scb_names2

    if not game.minecraft_scoreboard.____score_exists____(scb1, scb_names1[0]) : 
        return Response.Response_Template("$entity在$scb_name计分板没有分数").substitute(entity=ID_tracker(scb_names1[0]), scb_name=scb1)
    if not game.minecraft_scoreboard.____score_exists____(scb2, scb_names2[1]) : 
       return Response.Response_Template("$entity在$scb_name计分板没有分数").substitute(entity=ID_tracker(scb_names2[0]), scb_name=scb2)

    a = game.minecraft_scoreboard.____get_score____(scb1, scb_names1[0])
    b = game.minecraft_scoreboard.____get_score____(scb2, scb_names2[1])
    if SCORE_COMPARE[mode](a,b) ^ unless :
        return Response.Response_Template("分数条件($v1$mode$v2)测试通过", 1, 1).substitute(v1=a, v2=b, mode=mode)
    else : return Response.Response_Template("分数条件($v1$mode$v2)测试失败", 0, 0).substitute(v1=a, v2=b, mode=mode)

def subcommand_test_score_match(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, unless:bool, entity_get1:Union[str,Callable],
    scb1:str, range_not:bool, value1:int, value2:int) :
    if not game.minecraft_scoreboard.____scb_exists____(scb1) : 
        return Response.Response_Template("不存在计分板$scb_name").substitute(scb_name=scb1)

    if isinstance(entity_get1, str) : scb_names1 = [entity_get1]
    else :
        scb_names1:List[BaseNbtClass.entity_nbt] = entity_get1(execute_var, game)
        if isinstance(scb_names1, Response.Response_Template) : return scb_names1

    if not game.minecraft_scoreboard.____score_exists____(scb1, scb_names1[0]) : 
        return Response.Response_Template("$entity在$scb_name计分板没有分数").substitute(entity=ID_tracker(scb_names1[0]), scb_name=scb1)

    a = game.minecraft_scoreboard.____get_score____(scb1, scb_names1[0])
    if (range_not ^ (value1 <= a <= value2)) ^ unless :
        return Response.Response_Template("分数条件($v1$mode$var$mode$v2)测试通过", 1, 1).substitute(v1=value1, v2=value2, var=a, mode="≰" if range_not else "≤")
    else : return Response.Response_Template("分数条件($v1$mode$var$mode$v2)测试失败", 0, 0).substitute(v1=value1, v2=value2, var=a, mode="≰" if range_not else "≤")



class execute_1_19_50 :

    def add_func(subcommand:functools.partial, func:Callable) :
        if "test_func" not in subcommand.keywords : subcommand.keywords["test_func"] = []
        subcommand.keywords["test_func"].append(func)

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN, Version:Tuple[int]) : 
        from . import Start_Compile
        subcommand_list:List[functools.partial] = [functools.partial(head_generate)] 
        index = 1 ; func:Callable = None
        while 1 :
            if token_list[index]["token"].group() == "as" :
                index, entity_func = Selector.Selector_Compiler(_game, token_list, index+1)
                subcommand_list.append( functools.partial(subcommand_as, entity_get=entity_func) )
            elif token_list[index]["token"].group() == "at" :
                index, entity_func = Selector.Selector_Compiler(_game, token_list, index+1)
                subcommand_list.append( functools.partial(subcommand_at, entity_get=entity_func) )
            elif token_list[index]["token"].group() == "facing" :
                if token_list[index+1]["token"].group() == "entity" :
                    index, entity_func = Selector.Selector_Compiler(_game, token_list, index+2)
                    anchor_1 = token_list[index]["token"].group() ; index += 1
                    subcommand_list.append( functools.partial(subcommand_facing_entity, entity_get=entity_func, anchor=anchor_1) )
                else :
                    pos = [token_list[index+i]["token"].group() for i in range(1,4)] ; index += 4
                    cls.add_func(subcommand_list[-1], functools.partial(subcommand_facing_pos, pos=pos))
            elif token_list[index]["token"].group() == "positioned" :
                if token_list[index+1]["token"].group() == "as" :
                    index, entity_func = Selector.Selector_Compiler(_game, token_list, index+2)
                    subcommand_list.append( functools.partial(subcommand_positioned_entity, entity_get=entity_func) )
                else :
                    pos = [token_list[index+i]["token"].group() for i in range(1,4)] ; index += 4
                    cls.add_func(subcommand_list[-1], functools.partial(subcommand_positioned_pos, pos=pos))
            elif token_list[index]["token"].group() == "rotated" :
                if token_list[index+1]["token"].group() == "as" :
                    index, entity_func = Selector.Selector_Compiler(_game, token_list, index+2)
                    subcommand_list.append( functools.partial(subcommand_rotated_entity, entity_get=entity_func) )
                else :
                    rotate = [token_list[index+i]["token"].group() for i in range(1,3)] ; index += 3
                    cls.add_func(subcommand_list[-1], functools.partial(subcommand_rotated_pos, rotate=rotate))
            elif token_list[index]["token"].group() == "align" :
                axes = token_list[index+1]["token"].group() ; index += 2
                cls.add_func(subcommand_list[-1], functools.partial(subcommand_align, x="x" in axes, y="y" in axes, z="z" in axes))
            elif token_list[index]["token"].group() == "anchored" :
                anchor = token_list[index+1]["token"].group() ; index += 2
                for obj in reversed(subcommand_list) :
                    if not(obj.func is subcommand_at or obj.func is subcommand_positioned_entity) : continue
                    cls.add_func(obj, functools.partial(subcommand_anchored, type=anchor)) ; break
            elif token_list[index]["token"].group() == "in" :
                dimension = token_list[index+1]["token"].group() ; index += 2
                cls.add_func(subcommand_list[-1], functools.partial(subcommand_in, dimension=dimension))
            elif token_list[index]["token"].group() in ("if", "unless") :
                unless_mode = token_list[index]["token"].group() == "unless" ; index += 1
                if token_list[index]["token"].group() == "block" :
                    pos = [token_list[i]["token"].group() for i in range(index+1, index+4, 1)] ; index += 4
                    block_id = ID_transfor(token_list[index]["token"].group()) ; index += 1
                    if block_id not in _game.minecraft_ident.blocks : raise CompileError("不存在的方块ID：%s" % block_id, 
                        pos=(token_list[index]["token"].start(), token_list[index]["token"].end()))
                    if index >= len(token_list) or token_list[index]["type"] == "Sub_Command" : block_state = {}
                    elif token_list[index]["type"] == "Block_Data" : 
                        block_state = int(token_list[index]["token"].group()) ; index += 1
                        if not(-1 <= block_state <= 32767) : raise CompileError("%s 不是一个有效的数据值" % block_state,
                        pos=(token_list[index-1]["token"].start(), token_list[index-1]["token"].end()))
                        if block_state == -1 : block_state = {}
                    else : index,block_state = BlockState_Compiler( block_id, token_list, index )
                    cls.add_func(subcommand_list[-1], functools.partial(subcommand_test_block, unless=unless_mode, pos=pos, block_id=block_id, block_state=block_state))
                    if index >= len(token_list) : break
                elif token_list[index]["token"].group() == "blocks" :
                    poses = [ token_list[i]["token"].group() for i in range(index+1,index+10,1) ] ; index += 10
                    mask_mode = token_list[index]["token"].group() ; index += 1
                    cls.add_func(subcommand_list[-1], functools.partial(subcommand_test_blocks, unless=unless_mode, start1=poses[0:3], end1=poses[3:6], start2=poses[6:9], mask_mode=mask_mode))
                    if index >= len(token_list) : break
                elif token_list[index]["token"].group() == "entity" :
                    index, entity_func = Selector.Selector_Compiler(_game, token_list, index+1)
                    cls.add_func(subcommand_list[-1], functools.partial(subcommand_test_entity, unless=unless_mode, entity_get=entity_func))
                    if index >= len(token_list) : break
                elif token_list[index]["token"].group() == "score" :
                    if token_list[index+1]["type"] in "Player_Name" : index, entity_func_1 = index+2, token_list[index+1]["token"].group()
                    else : index, entity_func_1 = Selector.Selector_Compiler(_game, token_list, index+1)
                    scoreboard_name_1 = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
                    operation_mode = token_list[index]["token"].group() ; index += 1
                    if operation_mode != "matches" :
                        if token_list[index]["type"] == "Player_Name" : index, entity_func_2 = index+1, token_list[3]["token"].group()
                        else : index, entity_func_2 = Selector.Selector_Compiler(_game, token_list, index)
                        scoreboard_name_2 = Quotation_String_transfor_1(token_list[index]["token"].group()) ; index += 1
                        cls.add_func(subcommand_list[-1], functools.partial(subcommand_test_score_compare, unless=unless_mode, entity_get1=entity_func_1, 
                        scb1=scoreboard_name_1, mode=operation_mode, entity_get2=entity_func_2, scb2=scoreboard_name_2))
                        if index >= len(token_list) : break
                    else :
                        range_value = [-2147483648, 2147483647]
                        if token_list[index]["type"] == "Not" : range_not = True ; index += 1
                        else : range_not = False
                        if token_list[index]["type"] == "Range_Min" : 
                            range_value[0] = int(token_list[index]["token"].group()) ; index += 1
                        if token_list[index]["type"] != "Range_Sign" : range_value[1] = range_value[0]
                        else :
                            index += 1
                            if index >= len(token_list) : break
                            elif token_list[index]["type"] == "Range_Max" : 
                                range_value[1] = int(token_list[index]["token"].group()) ; index += 1
                        cls.add_func(subcommand_list[-1], functools.partial(subcommand_test_score_match, unless=unless_mode, 
                        entity_get1=entity_func_1, scb1=scoreboard_name_1, range_not=range_not, value1=range_value[0], value2=range_value[1]))
                        if index >= len(token_list) : break
            elif token_list[index]["token"].group() == "run" :
                if token_list[index+1]["token"].group() == "execute" : index += 2 ; continue
                func = Start_Compile(token_list[index+1:], _game, Version)
                if isinstance(func, tuple) : raise func[1]
                else : break
        if func is None : func = subcommand_list[-1].keywords["test_func"][-1] ; subcommand_list[-1].keywords["test_func"].pop()
        return functools.partial(cls.run, SubCommands=subcommand_list, CommandCall=func)

    run = execute_1_19.run





class function :
    
    def execute_context_generate(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, SubCommands:List[Callable]) :
        a = Response.Response_Template("$msg", mcfunction=True)

        Exe_Var_Generate:List[CONTEXT_GENERATER] = [SubCommands[0](execute_var, game)] 
        SubCommands_len = len(SubCommands) ; msg_list:List[str] = [] ; success_count = 0
        while Exe_Var_Generate :
            now_execute_var = next(Exe_Var_Generate[-1])
            if now_execute_var is None : Exe_Var_Generate.pop() ; continue
            if isinstance(now_execute_var, tuple) :
                msg_list.append( tramsfor_context(now_execute_var[1], now_execute_var[2]) )
                if not now_execute_var[0] : Exe_Var_Generate.pop()
                continue

            Generate_list_len = len(Exe_Var_Generate)
            if Generate_list_len < SubCommands_len : 
                Exe_Var_Generate.append(SubCommands[Generate_list_len](now_execute_var, game))
            else :
                Command_Back:Response.Response_Template = yield now_execute_var
                success_count += Command_Back.success_count
                msg_list.append( tramsfor_context(now_execute_var, Command_Back) )
                for i in Command_Back.Function_Feedback : a.add_function_feedback(i)

        a.success_count = min(1,success_count)
        a.result_count = success_count
        yield a.substitute(msg = "\n\n".join(msg_list))

    @classmethod
    def __compiler__(cls, _game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN) : 
        mcfunc = token_list[1]["token"].group()
        return functools.partial(cls.run, mcfunc=mcfunc)

    def run(execute_var:COMMAND_CONTEXT, game:RunTime.minecraft_thread, mcfunc:str) :
        if mcfunc not in game.minecraft_ident.functions : return Response.Response_Template("不存在的函数$name").substitute(name=mcfunc)

        command_count = 0
        execute_function_feedback = None
        Func_Stack:List[ Union[ Tuple[str, Iterator[COMMAND_CONTEXT], List[Tuple[str, Callable]]], Tuple[COMMAND_CONTEXT, 
        Iterator[Tuple[str,functools.partial]], Response.Response_Template, Response.Function_Response_Group]] ] = [[
            execute_var,
            game.minecraft_ident.functions[mcfunc]["command"].__iter__(), 
            Response.Response_Template("运行了$count条命令", 1, 1, mcfunction=True),
            Response.Function_Response_Group(mcfunc, execute_var)
        ]]

        while command_count < game.minecraft_world.functioncommandlimit :
            if isinstance(Func_Stack[-1], tuple) :
                func_context = Func_Stack[-1][1].send(execute_function_feedback)
                execute_function_feedback = None
                if isinstance(func_context, Response.Response_Template) :
                    func_context.set_command(Func_Stack[-1][0])
                    Func_Stack[-2][3].Count += 1
                    Func_Stack[-2][3].add_response(func_context)
                    Func_Stack.pop()
                else :
                    Func_Stack.append([
                        func_context,
                        Func_Stack[-1][2].__iter__(), 
                        Response.Response_Template("运行了$count条命令", 1, 1, mcfunction=True).set_command(command_str), 
                        Response.Function_Response_Group(new_mcfunc, func_context)
                    ])

            try : 
                context = Func_Stack[-1][0]
                command_str, command_func = next(Func_Stack[-1][1])
            except StopIteration : 
                Func_Stack[-1][3].is_End = True
                Func_Stack[-1][2].add_function_feedback(Func_Stack[-1][3])
                if len(Func_Stack) > 1 and isinstance(Func_Stack[-2], list) : 
                    a = Func_Stack[-1][2].substitute(count=Func_Stack[-1][3].Count)
                    Func_Stack[-2][3].add_response(a)
                elif len(Func_Stack) > 1 and isinstance(Func_Stack[-2], tuple) : 
                    execute_function_feedback = Func_Stack[-1][2].substitute(count=Func_Stack[-1][3].Count)
                if len(Func_Stack) > 1 : Func_Stack.pop() ; continue
                else : break

            if command_func.func is function.run :
                new_mcfunc = command_func.keywords["mcfunc"]
                Func_Stack.append([
                    context,
                    game.minecraft_ident.functions[new_mcfunc]["command"].__iter__(), 
                    Response.Response_Template("运行了$count条命令", 1, 1, mcfunction=True).set_command(command_str), 
                    Response.Function_Response_Group(new_mcfunc, context)
                ])
            elif command_func.func is execute_1_19.run and command_func.keywords["CommandCall"].func is function.run : 
                new_mcfunc = command_func.keywords["CommandCall"].keywords["mcfunc"]
                Func_Stack.append( (
                    command_str, 
                    function.execute_context_generate(context, game, command_func.keywords["SubCommands"]),
                    game.minecraft_ident.functions[new_mcfunc]["command"]
                ) )
            else :
                feedback:Response.Response_Template = command_func(context, game)
                feedback.set_command(command_str)
                Func_Stack[-1][3].Count += 1
                Func_Stack[-1][3].add_response(feedback)

            command_count += 1

        return Func_Stack[0][2].substitute(count=command_count)