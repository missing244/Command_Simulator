from .. import BaseNbtClass
from . import parser as CommandParser
from typing import Dict,Union,List,Tuple,Literal
import re


COMMAND_TOKEN = List[Dict[Literal["type","token"],Union[str,re.Match]]]
COMMAND_CONTEXT = Dict[
    Literal["executor", "dimension", "pos", "rotate", "version"],
    Union[BaseNbtClass.entity_nbt, Literal["overworld","nether","the_end"], List[float], List[float], List[int]]
]

def ID_tracker(entity) :
    if isinstance(entity, BaseNbtClass.entity_nbt) and entity.Identifier == "minecraft:player" : name = entity.CustomName
    elif isinstance(entity, BaseNbtClass.entity_nbt) : name = "%s(%s)" % (entity.UniqueID, entity.CustomName)
    else : name = entity
    return name

from . import response as Response
from . import compiler as CommandCompiler
from . import trans_html as HtmlGenerate

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

    def __fill_block__(self,dimension_id,block_id,block_info,start_pos,end_pos=None,fill_mode="replace",fill_block_id=None,fill_block_info=-1):
        if end_pos == None : end_pos = start_pos

        if isinstance(dimension_id,type("")) : dimension_id = world_dimension_str.index(dimension_id)
        test_hight_min = globals()["be_%s_hight_min" % world_dimension_str[dimension_id]]
        test_hight_max = globals()["be_%s_hight_max" % world_dimension_str[dimension_id]]
        if (start_pos[1] < test_hight_min or
            start_pos[1] >= test_hight_max) : return response_object("start_out_of_world",start_pos)
        if (end_pos[1] < test_hight_min or
           end_pos[1] >= test_hight_max) : return response_object("end_out_of_world",end_pos)
        dimension_hight = test_hight_min
        dimension_1 = world_dimension_str[dimension_id]
        middle_chunk = getattr(self,world_dimension_str[dimension_id])

        start_pos_setting = (min(math.floor(start_pos[0]),math.floor(end_pos[0])) , min(math.floor(start_pos[1]),math.floor(end_pos[1])) , min(math.floor(start_pos[2]),math.floor(end_pos[2])))
        end_pos_setting = (max(math.floor(start_pos[0]),math.floor(end_pos[0])) , max(math.floor(start_pos[1]),math.floor(end_pos[1])) , max(math.floor(start_pos[2]),math.floor(end_pos[2])))

        start_pos_chunk = [start_pos_setting[0]//16*16,start_pos_setting[2]//16*16]
        end_pos_chunk = [end_pos_setting[0]//16*16,end_pos_setting[2]//16*16]
        start_pos_chunk_store = copy.deepcopy(start_pos_chunk)

        while start_pos_chunk[0] <= end_pos_chunk[0] :
            while start_pos_chunk[1] <= end_pos_chunk[1] :
                test1 = str((start_pos_chunk[0],start_pos_chunk[1]))
                if not(test1 in game_process.minecraft_chunk_online[dimension_1]) :
                    return response_object("chunk_notfound",[start_pos_chunk[0],"y",start_pos_chunk[1]])
                start_pos_chunk[1] += 16
            start_pos_chunk[1] = start_pos_chunk_store[1]
            start_pos_chunk[0] += 16

        loop_pos = (math.floor(end_pos_setting[0])-math.floor(start_pos_setting[0])+1,
                    math.floor(end_pos_setting[1])-math.floor(start_pos_setting[1])+1,
                    math.floor(end_pos_setting[2])-math.floor(start_pos_setting[2])+1)
        if loop_pos[0] * loop_pos[1] * loop_pos[2] > 32768 : return response_object("outof_block_count",(start_pos,end_pos,32768))

        block_count = 0
        if type(block_info) == type(1) and block_info < 0 : return response_object("block_data_notsupport",block_info)
        block_1 = self.____find_mapping____(block_id,block_info)
        if type(block_1) == type(response_object("success_execute","")) : return block_1

        if type(fill_block_info) == type(1) and fill_block_info == -1 : fill_block_info = {}
        elif type(fill_block_info) == type(1) and fill_block_info < -1 : return response_object("block_data_notsupport",fill_block_info)

        if fill_block_id and fill_mode == "replace" and (isinstance(fill_block_info,dict) or fill_block_info > -1) :
            block_2 = self.____find_mapping____(fill_block_id,fill_block_info)
            if type(block_2) == type(response_object("success_execute","")) : return block_2

        for i in range(loop_pos[1]) :
            for j in range(loop_pos[2]) :
                for k in range(loop_pos[0]) :

                    chunk_pos = ((start_pos_setting[0]+k)//16*16,(start_pos_setting[2]+j)//16*16)
                    chunk_pos_1 = str(chunk_pos)
                    block_pos_1 = (start_pos_setting[0]+k-chunk_pos[0],start_pos_setting[1] + i - dimension_hight,start_pos_setting[2]+j-chunk_pos[1])
                    test_cb_pos = (start_pos_setting[0]+k,start_pos_setting[1] + i,start_pos_setting[2]+j)

                    if fill_mode == "replace" and fill_block_id :
                        if fill_block_info == {} :
                            if game_process.minecraft_block_mapping[
                            self.____find_block____(chunk_pos_1,block_pos_1,dimension_id)].Identifier == fill_block_id :
                                if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                                try : middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)] = game_process.block_comp_func.find_id_nbt(block_id)
                                except : pass
                                middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = block_1
                                game_process.be_register_command_block(test_cb_pos,block_1)
                                block_count += 1
                                
                        elif block_2 == self.____find_block____(chunk_pos_1,block_pos_1,dimension_id) :
                            if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                            try : middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)] = game_process.block_comp_func.find_id_nbt(block_id)
                            except : pass
                            middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = block_1
                            game_process.be_register_command_block(test_cb_pos,block_1)
                            block_count += 1

                    elif fill_mode == "replace" :
                        if block_1 != self.____find_block____(chunk_pos_1,block_pos_1,dimension_id) :
                            if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                            try : middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)] = game_process.block_comp_func.find_id_nbt(block_id)
                            except : pass
                            middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = block_1
                            game_process.be_register_command_block(test_cb_pos,block_1)
                            block_count += 1

                    elif fill_mode == "outline" :
                        if not(0 < k < loop_pos[0]-1 and 0 < j < loop_pos[2]-1 and 0 < i < loop_pos[1]-1) :
                            if block_1 != self.____find_block____(chunk_pos_1,block_pos_1,dimension_id) :
                                if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                                try : middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)] = game_process.block_comp_func.find_id_nbt(block_id)
                                except : pass
                                middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = block_1
                                game_process.be_register_command_block(test_cb_pos,block_1)
                                block_count += 1

                    elif fill_mode == "keep" :
                        if 0 == self.____find_block____(chunk_pos_1,block_pos_1,dimension_id) :
                            if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                            try : middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)] = game_process.block_comp_func.find_id_nbt(block_id)
                            except : pass
                            middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = block_1
                            game_process.be_register_command_block(test_cb_pos,block_1)
                            block_count += 1

                    elif fill_mode == "hollow" :
                        if not(0 < k < loop_pos[0]-1 and 0 < j < loop_pos[2]-1 and 0 < i < loop_pos[1]-1) :
                            if not(block_1 == self.____find_block____(chunk_pos_1,block_pos_1,dimension_id)) :
                                if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                                try : middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)] = game_process.block_comp_func.find_id_nbt(block_id)
                                except : pass
                                middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = block_1
                                game_process.be_register_command_block(test_cb_pos,block_1)
                                block_count += 1
                        else :
                            if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                            middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = 0
                            game_process.be_register_command_block(test_cb_pos,block_1)
                            block_count += 1

                    elif fill_mode == "destroy" :
                        if game_process.minecraft_world.dotiledrops :
                            game_process.minecraft_block_mapping[
                                middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]]
                            ].__summon_item__(dimension_id,(start_pos_setting[0]+k,start_pos_setting[1]+i,start_pos_setting[2]+j))
                        if (str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save']) : del middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)]
                        try : middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)] = game_process.block_comp_func.find_id_nbt(block_id)
                        except : pass
                        middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = block_1
                        game_process.be_register_command_block(test_cb_pos,block_1)
                        block_count += 1

        if block_count : return response_object("success_execute",Template("区域 $pos1 到 $pos2 填充或放置了 $blockcount 个方块").substitute(
        pos1=start_pos_setting,pos2=end_pos_setting,blockcount=block_count),1,block_count)
        else : return response_object("block_not_change",(start_pos_setting,end_pos_setting))

    def __clone_block__(self,dimension_id,start_pos,end_pos,clone_pos,mask_mode="replace",clone_mode="normal",clone_block_id=None,clone_block_info=0):
        start_pos_setting = (min(math.floor(start_pos[0]),math.floor(end_pos[0])) , min(math.floor(start_pos[1]),math.floor(end_pos[1])) , min(math.floor(start_pos[2]),math.floor(end_pos[2])))
        end_pos_setting = (max(math.floor(start_pos[0]),math.floor(end_pos[0])) , max(math.floor(start_pos[1]),math.floor(end_pos[1])) , max(math.floor(start_pos[2]),math.floor(end_pos[2])))
        clone_pos = (math.floor(clone_pos[0]),math.floor(clone_pos[1]),math.floor(clone_pos[2]))
        clone_pos_end = (clone_pos[0] + end_pos_setting[0] - start_pos_setting[0],clone_pos[1] + end_pos_setting[1] - start_pos_setting[1],clone_pos[2] + end_pos_setting[2] - start_pos_setting[2])

        if isinstance(dimension_id,type("")) : dimension_id = world_dimension_str.index(dimension_id)
        test_hight_min = globals()["be_%s_hight_min" % world_dimension_str[dimension_id]]
        test_hight_max = globals()["be_%s_hight_max" % world_dimension_str[dimension_id]]
        if (start_pos[1] < test_hight_min or
            start_pos[1] >= test_hight_max) : return response_object("start_out_of_world",start_pos)
        if (end_pos[1] < test_hight_min or
           end_pos[1] >= test_hight_max) : return response_object("end_out_of_world",end_pos)
        if (clone_pos[1] < test_hight_min or
           clone_pos[1] >= test_hight_max) : return response_object("clone_start_out_of_world",clone_pos)
        if (clone_pos_end[1] < test_hight_min or
           clone_pos_end[1] >= test_hight_max) : return response_object("clone_end_out_of_world",clone_pos_end)
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
        m1 = check_load(clone_pos,clone_pos_end,dimension_1)
        if type(m1) == type(response_object("success_execute","")) : return m1

        loop_pos = (math.floor(end_pos_setting[0])-math.floor(start_pos_setting[0])+1,
                    math.floor(end_pos_setting[1])-math.floor(start_pos_setting[1])+1,
                    math.floor(end_pos_setting[2])-math.floor(start_pos_setting[2])+1)
        if loop_pos[0] * loop_pos[1] * loop_pos[2] > 655360 : return response_object("outof_block_count",(start_pos,end_pos,655360))

        block_count = 0
        if type(clone_block_info) == type(1) and clone_block_info == -1 : clone_block_info = {}
        elif type(clone_block_info) == type(1) and clone_block_info < -1 : return response_object("block_data_notsupport",clone_block_info)

        if clone_block_id and mask_mode == "filtered" and (type(clone_block_info) == type({}) or clone_block_info > -1) :
            block_1 = self.____find_mapping____(clone_block_id,clone_block_info)
            if type(block_1) == type(response_object("success_execute","")) : return block_1

        if clone_mode != "force" :
            try :
                random.randint(max(start_pos_setting[0],clone_pos[0]),min(end_pos_setting[0],clone_pos_end[0]))
                random.randint(max(start_pos_setting[1],clone_pos[1]),min(end_pos_setting[1],clone_pos_end[1]))
                random.randint(max(start_pos_setting[2],clone_pos[2]),min(end_pos_setting[2],clone_pos_end[2]))
            except : pass
            else : return response_object("clone_area_overlap",(start_pos_setting,end_pos_setting,clone_pos,clone_pos_end))

        memory_list = [[],[]]

        for i in range(loop_pos[1]) :
            for j in range(loop_pos[2]) :
                for k in range(loop_pos[0]) :

                    chunk_pos = ((start_pos_setting[0]+k)//16*16,(start_pos_setting[2]+j)//16*16)
                    chunk_pos_1 = str(chunk_pos)
                    block_pos_1 = (start_pos_setting[0]+k-chunk_pos[0],start_pos_setting[1] + i - dimension_hight,start_pos_setting[2]+j-chunk_pos[1])

                    if mask_mode == "filtered" and clone_block_id and ((clone_block_info == {} and 
                    game_process.minecraft_block_mapping[self.____find_block____(chunk_pos_1,block_pos_1,dimension_id)].Identifier == clone_block_id)
                    or block_1 == self.____find_block____(chunk_pos_1,block_pos_1,dimension_id)) :
                        m2,m3 = copy.deepcopy(middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]]),None
                        if str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save'] : m3 = copy.deepcopy(middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)])
                        memory_list[0].append(m2) ; memory_list[1].append(m3)
                    elif mask_mode == "masked" and (0 != self.____find_block____(chunk_pos_1,block_pos_1,dimension_id)) :
                        m2,m3 = copy.deepcopy(middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]]),None
                        if str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save'] : m3 = copy.deepcopy(middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)])
                        memory_list[0].append(m2) ; memory_list[1].append(m3)
                    elif mask_mode == "replace" :
                        m2,m3 = copy.deepcopy(middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]]),None
                        if str(block_pos_1) in middle_chunk[chunk_pos_1]['nbt_save'] : m3 = copy.deepcopy(middle_chunk[chunk_pos_1]['nbt_save'][str(block_pos_1)])
                        memory_list[0].append(m2) ; memory_list[1].append(m3)
                    else : memory_list[0].append(None) ; memory_list[1].append(None)

        for i in range(loop_pos[1]) :
            for j in range(loop_pos[2]) :
                for k in range(loop_pos[0]) :

                    index1 = k + loop_pos[2] * j + i * loop_pos[1]
                    if memory_list[0][index1] == None : continue
                    m2,m3 = memory_list[0][index1],memory_list[1][index1]

                    chunk_pos = ((start_pos_setting[0]+k)//16*16,(start_pos_setting[2]+j)//16*16)
                    chunk_pos_1 = str(chunk_pos)
                    block_pos_1 = (start_pos_setting[0]+k-chunk_pos[0],start_pos_setting[1] + i - dimension_hight,start_pos_setting[2]+j-chunk_pos[1])
                    chunk_pos = ((clone_pos[0]+k)//16*16,(clone_pos[2]+j)//16*16)
                    chunk_pos_2 = str(chunk_pos)
                    block_pos_2 = (clone_pos[0]+k-chunk_pos[0],clone_pos[1] + i - dimension_hight,clone_pos[2]+j-chunk_pos[1])

                    if clone_mode in ["normal","force"] :
                        middle_chunk[chunk_pos_2]['blocks'][block_pos_2[1]*256 + block_pos_2[2]*16 + block_pos_2[0]] = m2
                        if (str(block_pos_2) in middle_chunk[chunk_pos_2]['nbt_save']) : del middle_chunk[chunk_pos_2]['nbt_save'][str(block_pos_2)]
                        if m3 : middle_chunk[chunk_pos_2]['nbt_save'][str(block_pos_2)] = m3
                        game_process.be_register_command_block(block_pos_2,m2)
                        block_count += 1

                    elif clone_mode == "move" :
                        middle_chunk[chunk_pos_1]['blocks'][block_pos_1[1]*256 + block_pos_1[2]*16 + block_pos_1[0]] = 0
                        game_process.be_register_command_block(block_pos_1,0)
                        if (str(block_pos_1) in middle_chunk[chunk_pos_2]['nbt_save']) : del middle_chunk[chunk_pos_2]['nbt_save'][str(block_pos_1)]
                        
                        if (str(block_pos_2) in middle_chunk[chunk_pos_2]['nbt_save']) : del middle_chunk[chunk_pos_2]['nbt_save'][str(block_pos_2)]
                        middle_chunk[chunk_pos_2]['blocks'][block_pos_2[1]*256 + block_pos_2[2]*16 + block_pos_2[0]] = m2
                        if m3 : middle_chunk[chunk_pos_2]['nbt_save'][str(block_pos_2)] = m3
                        game_process.be_register_command_block(block_pos_2,m2)
                        block_count += 1

        if block_count : return response_object("success_execute",Template("区域 $pos1 到 $pos2 复制 $blockcount 个方块").substitute(
        pos1=clone_pos,pos2=clone_pos_end,blockcount=block_count),1,block_count)
        else : return response_object("no_block_clone",(clone_pos,clone_pos_end))
