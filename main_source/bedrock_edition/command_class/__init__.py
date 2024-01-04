from .. import BaseNbtClass,Constants
from .. import RunTime
from . import parser as CommandParser
from typing import Dict,Union,List,Tuple,Literal,Callable
import re


COMMAND_TOKEN = List[Dict[Literal["type","token"],Union[str,re.Match]]]
COMMAND_CONTEXT = Dict[
    Literal["executer", "dimension", "pos", "rotate", "version"],
    Union[BaseNbtClass.entity_nbt, Literal["overworld","nether","the_end"], List[float], List[float], List[int]]
]
Command_Compile_Dict_Save:Dict[Tuple[int],Dict[str,Callable]] = {}

def ID_tracker(entity:Union[str, BaseNbtClass.entity_nbt]) :
    if isinstance(entity, BaseNbtClass.entity_nbt) and entity.Identifier == "minecraft:player" : name = entity.CustomName
    elif isinstance(entity, BaseNbtClass.entity_nbt) and entity.CustomName == "" : 
        entity_name = entity.Identifier.replace("minecraft:","",1)
        CustomName = Constants.TRANSLATE_ID["[实体]"].get(entity_name, "entity.%s.name" % entity_name)
        name = "%s(%s)" % (entity.UniqueID, CustomName)
    elif isinstance(entity, BaseNbtClass.entity_nbt) : name = "%s(%s)" % (entity.UniqueID, entity.CustomName)
    else : name = entity
    return name

from . import response as Response
from . import compiler as CommandCompiler
from . import trans_html as HtmlGenerate

def Command_Tokenizer_Compiler(_game:RunTime.minecraft_thread, Command:str, Version:Tuple[int]) :
    Version = tuple(Version)
    if Version in Command_Compile_Dict_Save and Command in Command_Compile_Dict_Save[Version] :
        return Command_Compile_Dict_Save[Version][Command]

    token_list = CommandParser.Start_Tokenizer(Command, Version)
    if isinstance(token_list, tuple) : return token_list
    func_object = CommandCompiler.Start_Compile(token_list, Version, _game)
    if isinstance(func_object, tuple) : return func_object

    if Version not in Command_Compile_Dict_Save : Command_Compile_Dict_Save[Version] = {}
    Command_Compile_Dict_Save[Version][Command] = func_object
    return func_object

from . import command_block as CommandBlock
from . import mcfunction as McFunction
from . import terminal as TerminalCommand


















if 0 :
    def __test_for_blocks__(self,dimension_id,start_pos,end_pos,test_pos,test_mode="all"):
        start_pos_setting = (min(math.floor(start_pos[0]),math.floor(end_pos[0])) , min(math.floor(start_pos[1]),math.floor(end_pos[1])) , min(math.floor(start_pos[2]),math.floor(end_pos[2])))
        end_pos_setting = (max(math.floor(start_pos[0]),math.floor(end_pos[0])) , max(math.floor(start_pos[1]),math.floor(end_pos[1])) , max(math.floor(start_pos[2]),math.floor(end_pos[2])))
        test_pos = (math.floor(test_pos[0]),math.floor(test_pos[1]),math.floor(test_pos[2]))
        test_pos_end = (test_pos[0] + end_pos_setting[0] - start_pos_setting[0],test_pos[1] + end_pos_setting[1] - start_pos_setting[1],test_pos[2] + end_pos_setting[2] - start_pos_setting[2])

        if isinstance(dimension_id,type("")) : dimension_id = world_dimension_str.index(dimension_id)
        test_hight_min = globals()["be_%s_hight_min" % world_dimension_str[dimension_id]]
        test_hight_max = globals()["be_%s_hight_max" % world_dimension_str[dimension_id]]
        if (start_pos[1] < test_hight_min or
            start_pos[1] >= test_hight_max) : return response_object("start_out_of_world",start_pos)
        if (end_pos[1] < test_hight_min or
           end_pos[1] >= test_hight_max) : return response_object("end_out_of_world",end_pos)
        if (test_pos[1] < test_hight_min or
           test_pos[1] >= test_hight_max) : return response_object("test_start_out_of_world",test_pos)
        if (test_pos_end[1] < test_hight_min or
           test_pos_end[1] >= test_hight_max) : return response_object("test_end_out_of_world",test_pos_end)
        dimension_hight = test_hight_min
        dimension_1 = world_dimension_str[dimension_id]
        middle_chunk = getattr(self,world_dimension_str[dimension_id])


        def check_load(start_pos_setting_1,end_pos_setting_1,dimension_1) :
            start_pos_chunk = [start_pos_setting_1[0]//16*16,start_pos_setting_1[2]//16*16]
            end_pos_chunk = [end_pos_setting_1[0]//16*16,end_pos_setting_1[2]//16*16]
            start_pos_chunk_store = copy.deepcopy(start_pos_chunk)

            while start_pos_chunk[0] <= end_pos_chunk[0] :
                while start_pos_chunk[1] <= end_pos_chunk[1] :
                    test1 = str((start_pos_chunk[0],start_pos_chunk[1]))
                    if not(test1 in game_process.minecraft_chunk_online[dimension_1]) :
                        return response_object("chunk_notfound",[start_pos_chunk[0],"y",start_pos_chunk[1]])
                    start_pos_chunk[1] += 16
                start_pos_chunk[1] = start_pos_chunk_store[1]
                start_pos_chunk[0] += 16

        m1 = check_load(start_pos_setting,end_pos_setting,dimension_1)
        if type(m1) == type(response_object("success_execute","")) : return m1
        m1 = check_load(test_pos,test_pos_end,dimension_1)
        if type(m1) == type(response_object("success_execute","")) : return m1

        loop_pos = (math.floor(end_pos_setting[0])-math.floor(start_pos_setting[0])+1,
                    math.floor(end_pos_setting[1])-math.floor(start_pos_setting[1])+1,
                    math.floor(end_pos_setting[2])-math.floor(start_pos_setting[2])+1)
        if loop_pos[0] * loop_pos[1] * loop_pos[2] > 524288 : return response_object("outof_block_count",(start_pos,end_pos,524288))

        block_count = 0
        for i in range(loop_pos[1]) :
            for j in range(loop_pos[2]) :
                for k in range(loop_pos[0]) :
                    if test_mode == "all" :
                        test1 = self.____find_chunk_block_2____((start_pos_setting[0]+k,start_pos_setting[1]+i,start_pos_setting[2]+j),dimension_id)
                        test2 = self.____find_chunk_block_2____((test_pos[0]+k,test_pos[1]+i,test_pos[2]+j),dimension_id)
                        test3 = self.____find_block_nbt____((start_pos_setting[0]+k,start_pos_setting[1]+i,start_pos_setting[2]+j),dimension_1)
                        test4 = self.____find_block_nbt____((test_pos[0]+k,test_pos[1]+i,test_pos[2]+j),dimension_1)

                        if not(test1 == test2 and hash(str(test3)) == hash(str(test4))) : 
                            """print(
                            game_process.minecraft_block_mapping[test1] , game_process.minecraft_block_mapping[test2],
                            test1 == test2,hash(str(test3)) , hash(str(test4)),hash(str(test3)) == hash(str(test4)),
                            (start_pos_setting[0]+k,start_pos_setting[1]+i,start_pos_setting[2]+j),
                            (test_pos[0]+k,test_pos[1]+i,test_pos[2]+j)
                            )"""
                            return response_object("test_area_faild",(start_pos_setting,end_pos_setting,test_pos,test_pos_end))
                        block_count += 1
                    elif test_mode == "masked" :
                        test1 = self.____find_chunk_block_2____((start_pos_setting[0]+k,start_pos_setting[1]+i,start_pos_setting[2]+j),dimension_id)
                        if test1 == 0 : continue
                        test2 = self.____find_chunk_block_2____((test_pos[0]+k,test_pos[1]+i,test_pos[2]+j),dimension_id)
                        test3 = self.____find_block_nbt____((start_pos_setting[0]+k,start_pos_setting[1]+i,start_pos_setting[2]+j),dimension_1)
                        test4 = self.____find_block_nbt____((test_pos[0]+k,test_pos[1]+i,test_pos[2]+j),dimension_1)

                        if not(test1 == test2 and hash(str(test3)) == hash(str(test4))) : 
                            return response_object("test_area_faild",(start_pos_setting,end_pos_setting,test_pos,test_pos_end))
                        block_count += 1

        if block_count :
            return response_object("success_execute",Template("区域 $pos1 到 $pos2 比对通过 $blockcount 个方块").substitute(
            pos1=test_pos,pos2=test_pos_end,blockcount=block_count),1,block_count)
        else : return response_object("test_area_faild",(start_pos_setting,end_pos_setting,test_pos,test_pos_end))
