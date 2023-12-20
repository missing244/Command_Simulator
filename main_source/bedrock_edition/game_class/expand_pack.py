from typing import List,Dict,Union,Literal,Tuple
from . import RunTime
import re


class block_object :

    def __init__(self,id:str,state:dict,nbt:dict) -> None:
        self.Identifier = id
        self.BlockState = state
        self.BlockEntityTag = nbt


class visualization :

    def __init__(self,game_thread:RunTime.minecraft_thread) -> None:
        from .. import CommandParser,CommandCompiler
        
        self.Selector = CommandParser.ParserSystem.Command_Parser( 
            CommandParser.SpecialMatch.Command_Root().add_leaves(
                *CommandParser.SpecialMatch.BE_Selector_Tree(CommandParser.BaseMatch.END_NODE)
            )
        )
        self.Compiler = CommandCompiler.Selector.Selector_Compiler

        self.game_thread = game_thread
        self.first_get_ready = False 
        self.defalt_chunk = [0 for i in range(16 * 16 * 384)]

        self.start_x = 0 ; self.start_y = -64 ; self.start_z = 0
        self.area_x = 16 ; self.area_y = 64 ; self.area_z = 16

        self.track_entity = []
        self.debug_data = []


    def reset_var(self,var_json:dict):
        target_var_name_test = re.compile("^entity_target_")
        color_name = {"entity_target_0": "pink", "entity_target_1": "purple","entity_target_2": "yellow",
                      "entity_target_3": "brown", "entity_target_4": "lightblue"}
        int_test = re.compile("^-?[0-9]{0,}$\\b")
        error_var_list = {} ; self.track_entity.clear() ; self.debug_data.clear()
        self.first_get_ready = False

        for var_name in list(var_json) :
            var_name : str
            if var_json[var_name].replace(" ","") == "" : continue
            elif target_var_name_test.search(var_name) : 
                Token1 = self.Selector.parser(var_json[var_name], self.game_thread.game_version)
                if isinstance(Token1, tuple) : error_var_list[var_name] = Token1[0] ; continue
                try : selector_func = self.Compiler(self.game_thread, Token1, 0)
                except Exception as e : error_var_list[var_name] = e.args[0] ; continue
                self.track_entity.append({"entity": selector_func[1], "color": color_name[var_name]})

            else :
                if int_test.search(var_json[var_name]) == None : 
                    error_var_list[var_name] = "输入数据并不是整数" ; continue
                if var_name in ["area_x","area_z"] and not(1 <= int(var_json[var_name]) <= 100) :
                    error_var_list[var_name] = "输入的整数超过未在1~128之间" ; continue
                if var_name in ["area_y"] and not(1 <= int(var_json[var_name]) <= 384) :
                    error_var_list[var_name] = "输入的整数超过未在1~384之间" ; continue
                setattr(self, var_name, int(var_json[var_name]))
        return error_var_list


    def save_a_test_data(self) :
        debug_dict = {
            "chunks": self.get_debug_chunks() if self.game_thread.in_game_tag else {},
            "entities": self.get_debug_entity() if self.game_thread.in_game_tag else [],
            "particle": self.game_thread.runtime_variable.particle_alive["overworld"].copy(),
            "global_time" : int(self.game_thread.minecraft_world.game_time),
            "var_saves" : {"start_x":self.start_x, "start_y":self.start_y, "start_z":self.start_z, 
                           "area_x":self.area_x, "area_y":self.area_y, "area_z":self.area_z}
        }
        self.debug_data.append(debug_dict)
        if not self.game_thread.in_game_tag : self.set_test_end_flag()

    def get_debug_chunks(self) :
        chunks = {}

        chunk_start = [self.start_x // 16 * 16, self.start_z // 16 * 16]
        chunk_end = [(self.start_x + self.area_x - 1) // 16 * 16, (self.start_z + self.area_z - 1 ) // 16 * 16]
        dimension_data = self.game_thread.minecraft_chunk.loading_chunk["overworld"]
        m1 = chunk_start[1]
        while chunk_start[0] <= chunk_end[0] :
            while chunk_start[1] <= chunk_end[1] :
                if not self.game_thread.in_game_tag : return {}
                chunk_pos_1 = "(%s, %s)" % tuple(chunk_start)
                if tuple(chunk_start) in dimension_data : chunks[chunk_pos_1] = dimension_data[tuple(chunk_start)]['blocks'][0:self.area_y*16*16]
                else : chunks[chunk_pos_1] = self.defalt_chunk
                chunk_start[1] += 16
            chunk_start[0] += 16 ; chunk_start[1] = m1
        chunks["block_map"] = [i.Identifier for i in self.game_thread.minecraft_chunk.block_mapping]
        return chunks

    def get_debug_entity(self) :
        entity = []
        for entity_test in self.track_entity :
            execute_var = {"executer":"Server","dimension":"overworld","pos":[0,0,0],"rotate":[0,0],
                           "version":self.game_thread.game_version}
            entity_list = entity_test['entity'](execute_var)
            if not isinstance(entity_list, list) : entity.append({"entity":[],"color":entity_test["color"]}) ; continue
            entity.append({
                "entity":[i.__save__() for i in entity_list if (
                    self.start_x <= i.Pos[0] <= (self.start_x + self.area_x) and self.start_z <= i.Pos[2] <= (self.start_z + self.area_z))
                ],"color":entity_test["color"]})
        return entity

    def set_test_end_flag(self) :
        self.debug_data.append("Test_End")
        self.first_get_ready = False 


    def get_test_data(self,times:int) :
        if (self.area_x * self.area_z) >= (80 * 80) : base1 = 5
        if (self.area_x * self.area_z) >= (60 * 60) : base1 = 12
        if (self.area_x * self.area_z) >= (40 * 40) : base1 = 18
        if (self.area_x * self.area_z) >= (20 * 20) : base1 = 40
        if (self.area_x * self.area_z) >= (0 * 0) : base1 = 60
        a = self.debug_data[times * base1 : base1 * (times + 1)]
        if len(a) == 0 : return None
        return a


