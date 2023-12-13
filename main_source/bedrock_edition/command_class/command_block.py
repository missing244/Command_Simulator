import re,os,itertools
from . import HtmlGenerate,CommandParser,CommandCompiler
from .. import MathFunction,Constants,RunTime,FileOperation,np,BlockComponent
import main_source.package.python_nbt as python_nbt
from typing import Dict,List,Tuple


KEYWORD_COMMENTARY = re.compile("^[ ]{0,}//")
KEYWORD_START = (
    re.compile("^[ ]{0,}start"), re.compile("[ ]{0,}[0-9]{0,}"), re.compile("[ ]{0,}[0-9]{0,}"), 
    re.compile("[ ]{0,}[0-9]{0,}"), re.compile("[ ]{0,}$")
)
INT_RE_TEST = re.compile("^[0-9]{1,}$")
KEYWORD_EMPTY = re.compile("^[ ]{0,}empty")


class command_block_compile_system :

    # file example
    # "start posx posy posz"
    # "[facing，参数A，参数B，参数C，参数D] 循环/连锁/脉冲 有条件/无条件 红石/常开 延时"
    # "facing: 0 y- ; 1 y+ ; 2 z- ; 3 z+ ; 4 x- ; 5 x+ ; "

    def __init__(self) -> None:
        self.cb_type_id = {"循环":"minecraft:repeating_command_block", "连锁":"minecraft:chain_command_block", "脉冲":"minecraft:command_block"}
        self.cb_condition_id = {"有条件":True, "无条件":False}
        self.cb_auto_id = {"红石":False, "常开":True}
        self.command_block_facing_str = ("0","1","2","3","4","5","y-","y+","z-","z+","x-","x+")
        self.command_block_facing = {0:(0,-1,0), 1:(0,1,0), 2:(0,0,-1), 3:(0,0,1), 4:(-1,0,0), 5:(1,0,0)}

        self.game_version = [0,0,0]
        self.file_name = ""
        self.encoding_error:List[str] = []
        self.syntax_error:Dict[str, List[Tuple[int,List[int],str,str]]] = {} #lines version command error_msg

        self.command_block_data = {}

        self.cb_place_pos = [-1,-1,-1]
        self.default_property = [1,"脉冲","无条件","红石",0,"",None]

    def reset_all_saves(self) :
        self.command_block_data.clear()
        self.encoding_error.clear()
        self.syntax_error.clear()
        self.default_property = [1,"脉冲","无条件","红石",0,"",None]
        self.cb_place_pos = [-1,-1,-1]

    def open_command_block_file(self, _game:RunTime.minecraft_thread) : 
        self.game_version = _game.game_version ; self.reset_all_saves()
        cb_file_path = os.path.join("save_world", _game.world_name, "command_blocks")

        for file_name in list(os.walk(cb_file_path))[0][2] :
            if file_name[-4:] != ".txt" : continue
            self.file_name = file_path = os.path.join(cb_file_path,file_name)
            cb_file_content = FileOperation.read_a_file(file_path)
            if isinstance(cb_file_content,tuple) : self.encoding_error.append(file_path) ; continue

            self.check_syntax(_game, cb_file_content.split("\n"))


    def check_syntax(self, _game:RunTime.minecraft_thread, content_list:List[str]) : 
        for lines,cb_command in enumerate(content_list) :
            
            lines += 1
            if cb_command.replace(" ","") == "" : continue
            if KEYWORD_COMMENTARY.search(cb_command) : continue

            if self.cb_place_pos == [-1,-1,-1] : 
                middle1 = self.keyword_start_syntax(lines,cb_command)
                if isinstance(middle1, tuple) :
                    if self.file_name not in self.syntax_error : self.syntax_error[self.file_name] = []
                    self.syntax_error[self.file_name].append(middle1)
                    break
                self.cb_place_pos = middle1
                continue

            if KEYWORD_START[0].match(cb_command) : 
                middle1 = self.keyword_start_syntax(lines, cb_command)
                if isinstance(middle1, tuple) :
                    if self.file_name not in self.syntax_error : self.syntax_error[self.file_name] = []
                    self.syntax_error[self.file_name].append(middle1)
                    break
                self.cb_place_pos = middle1
                continue

            middle1 = self.keyword_cb_syntax(_game, lines, cb_command)
            if not isinstance(middle1, list) : continue

            if tuple(self.cb_place_pos) in self.command_block_data : 
                if self.file_name not in self.syntax_error : self.syntax_error[self.file_name] = []
                self.syntax_error[self.file_name].append((lines,self.game_version,cb_command,"该位置的命令方块与其他命令方块发生位置冲突"))
                continue
            if not(0 <= self.cb_place_pos[0] <= 95 and 0 <= self.cb_place_pos[2] <= 95 and -64 <= self.cb_place_pos[1] <= 319) : 
                if self.file_name not in self.syntax_error : self.syntax_error[self.file_name] = []
                self.syntax_error[self.file_name].append((lines,self.game_version,cb_command,"该位置的命令方块超过了合法布置区域"))
                continue

            cb_pos = (self.cb_place_pos[0] + 1600, self.cb_place_pos[1], self.cb_place_pos[2] + 1600)
            self.command_block_data[cb_pos] = {}
            self.command_block_data[cb_pos]['block_state'] = {"facing_direction": middle1[0], "conditional_bit": self.cb_condition_id[middle1[2]]}
            self.command_block_data[cb_pos]["id"] = self.cb_type_id[middle1[1]]
            self.command_block_data[cb_pos]["auto"] = self.cb_auto_id[middle1[3]]
            self.command_block_data[cb_pos]["delay"] = middle1[4]
            self.command_block_data[cb_pos]["command"] = middle1[5]
            self.command_block_data[cb_pos]["command_object"] = middle1[6]
            for i in range(3) : self.cb_place_pos[i] += self.command_block_facing[middle1[0]][i]

    def keyword_start_syntax(self, lines:int, text:str) : 
        string_match = KEYWORD_START[0].match(text)
        if string_match == None : return (lines, self.game_version, text, "命令方块文件最开始需要指定start命令")
        
        string_match = KEYWORD_START[1].match(text, string_match.end())
        if string_match == None or not(0 <= int(string_match.group()) <= 95) : 
            return (lines, self.game_version, text, "start命令的x坐标需要在 0到95 之间")
        pos_x = int(string_match.group())

        string_match = KEYWORD_START[2].match(text, string_match.end())
        if string_match == None or not(-64 <= int(string_match.group()) <= 319) : 
            return (lines, self.game_version, text, "start命令的y坐标需要在 -64到319 之间")
        pos_y = int(string_match.group())

        string_match = KEYWORD_START[3].match(text, string_match.end())
        if string_match == None or not(0 <= int(string_match.group()) <= 95) : 
            return (lines, self.game_version, text, "start命令的z坐标需要在 0到95 之间")
        pos_z = int(string_match.group())

        string_match = KEYWORD_START[4].match(text, string_match.end())
        if string_match == None : return (lines, self.game_version, text, "start命令末尾含有多余的参数")

        return [pos_x, pos_y, pos_z]

    def keyword_cb_syntax(self, _game:RunTime.minecraft_thread, lines:int, text:str):
        if re.compile("^[ ]{0,}\\u005b").match(text) : middle1 = self.keyword_cb_property_syntax(_game,lines,text)
        else : middle1 = self.keyword_cb_command_syntax(_game,lines,text)
        if isinstance(middle1, tuple) :
            if self.file_name not in self.syntax_error : self.syntax_error[self.file_name] = []
            self.syntax_error[self.file_name].append(middle1)
            return False
        return middle1

    def keyword_cb_property_syntax(self, _game:RunTime.minecraft_thread, lines:int, text:str) : 
        cb_property_str = re.compile("\\u005b.*?\\u005d").search(text)
        if cb_property_str == None : return (lines, self.game_version, text, "命令方块属性语法错误")

        command_str = text[cb_property_str.end():]
        cb_property = re.split("[,，;；]",cb_property_str[1:len(cb_property_str)-1])

        re_test1 = None if (cb_property[0] not in self.command_block_facing_str) else cb_property[0]
        if re_test1 == None : return (lines, self.game_version, text, "非法的命令方块朝向参数")

        self.default_property[0] = self.command_block_facing_str.index(re_test1)
        for info1 in cb_property[1:] :
            if (info1 in self.cb_type_id) : self.default_property[1] = info1
            elif (info1 in self.cb_condition_id) : self.default_property[2] = info1
            elif (info1 in self.cb_auto_id) : self.default_property[3] = info1
            elif INT_RE_TEST.search(info1) :
                if int(info1) < 0 : return (lines, self.game_version, text, "命令方块延时参数应为非负数")
                self.default_property[4] = int(info1)
            else : return (lines, self.game_version, text, "无效的命令方块属性参数( %s )" % info1)

        if KEYWORD_EMPTY.match(command_str) : 
            self.default_property[5] = "" ; self.default_property[6] = None
            return list(self.default_property)
        elif command_str.replace(" ","") == "" : return None

        token_list = CommandParser.Start_Tokenizer(command_str, self.game_version)
        if isinstance(token_list, tuple) : return (lines, self.game_version, command_str, token_list[0])
        command_object = CommandCompiler.Start_Compile(token_list, self.game_version, _game)
        if isinstance(command_object, tuple) : return (lines, self.game_version, command_str, command_object[0])

        self.default_property[5] = command_str ; self.default_property[6] = command_object
        return list(self.default_property)

    def keyword_cb_command_syntax(self, _game:RunTime.minecraft_thread, lines:int, text:str) :
        token_list = CommandParser.Start_Tokenizer(text, self.game_version)
        if isinstance(token_list, tuple) : return (lines, self.game_version, text, token_list[0])
        command_object = CommandCompiler.Start_Compile(token_list, self.game_version, _game)
        if isinstance(command_object, tuple) : return (lines, self.game_version, text, command_object[0])

        self.default_property[5] = text ; self.default_property[6] = command_object
        return list(self.default_property)


    def get_command_block_error(self) :
        return {
            "encoding_error" : self.encoding_error.copy(),
            "syntax_error" : self.syntax_error.copy(),
        }

    def generate_command_block_view(self) : 
        return HtmlGenerate.generate_command_block_html(self.command_block_data).encode_for_js()

    def write_to_world(self, _game:RunTime.minecraft_thread) : 
        for will_load in Constants.COMMAND_BLOCK_LOAD_CHUNK :
            _game.minecraft_chunk.____generate_chunk____(_game.minecraft_world, 'overworld', will_load)

        for cb_pos in self.command_block_data :
            block_index = _game.minecraft_chunk.____find_block_mapping____(
                self.command_block_data[cb_pos]['id'], self.command_block_data[cb_pos]['block_state'])

            cb_nbt = BlockComponent.find_id_nbt(self.command_block_data[cb_pos]['id'])
            cb_nbt['auto'] = self.command_block_data[cb_pos]['auto']
            cb_nbt['Command'] = self.command_block_data[cb_pos]['command']
            cb_nbt['TickDelay'] = np.int32(self.command_block_data[cb_pos]['delay'])
            _game.minecraft_chunk.____set_block____("overworld", cb_pos, block_index)
            _game.minecraft_chunk.____set_block_nbt____("overworld", cb_pos, cb_nbt)

            _game.minecraft_chunk.____register_command_block____(cb_pos, block_index)
            _game.minecraft_chunk.____register_runtime_command____(
                self.command_block_data[cb_pos]['command'],
                self.command_block_data[cb_pos]["command_object"]
            )


    def transfor_bdx_file(self, _game:RunTime.minecraft_thread) :
        import main_source.package.python_bdx as python_bdx
        a = python_bdx.BDX_File(os.path.join("functionality", "structure_output", _game.world_name+".bdx"),"wb")
        a.author = "Command_Simulator"
        pos_start = [0,0,0] ; cb_type = {"minecraft:command_block":0,"minecraft:repeating_command_block":1,"minecraft:chain_command_block":2}
        for i in list(self.command_block_data) :
            posx = i[0] - pos_start[0] ; pos_start[0] = i[0]
            posy = i[1] - pos_start[1] ; pos_start[1] = i[1]
            posz = i[2] - pos_start[2] ; pos_start[2] = i[2]
            if posx != 0 : a.operation_list.append(python_bdx.OperationCode.AddInt8XValue(posx))
            if posy != 0 : a.operation_list.append(python_bdx.OperationCode.AddInt16YValue(posy))
            if posz != 0 : a.operation_list.append(python_bdx.OperationCode.AddInt8ZValue(posz))
            cb_data = self.command_block_data[i]
            a.operation_list.append(
                python_bdx.OperationCode.PlaceCommandBlockWithCommandBlockData(
                    data = cb_data["block_state"]["facing_direction"],
                    mode = cb_type[cb_data["id"]],
                    command = cb_data["command"],
                    tickdelay = cb_data["delay"],
                    conditional = cb_data["block_state"]["conditional_bit"],
                    needsRedstone = not cb_data["auto"],
                )
            )
        a.close()

    def transfor_mcstructure_file(self, _game:RunTime.minecraft_thread) :

        python_nbt.nbt.change_to_little()

        def return_mcstructure_format() :
            a = python_nbt.nbt.NBTTagCompound()
            a['format_version'] = python_nbt.nbt.NBTTagInt(1)

            a['structure_world_origin'] = python_nbt.nbt.NBTTagList(tag_type=python_nbt.nbt.NBTTagInt)
            for i in range(3) : a['structure_world_origin'].append(python_nbt.nbt.NBTTagInt(0))

            a['structure'] = python_nbt.nbt.NBTTagCompound()
            a['structure']['block_indices'] = python_nbt.nbt.NBTTagList(tag_type=python_nbt.nbt.NBTTagList)
            for i in range(2) : a['structure']['block_indices'].append(python_nbt.nbt.NBTTagList(tag_type=python_nbt.nbt.NBTTagInt))

            a['structure']['entities'] = python_nbt.nbt.NBTTagList(tag_type=python_nbt.nbt.NBTTagCompound)

            a['structure']['palette'] = python_nbt.nbt.NBTTagCompound()
            a['structure']['palette']['default'] = python_nbt.nbt.NBTTagCompound()
            a['structure']['palette']['default']['block_palette'] = python_nbt.nbt.NBTTagList(tag_type=python_nbt.nbt.NBTTagCompound)
            a['structure']['palette']['default']['block_position_data'] = python_nbt.nbt.NBTTagCompound()

            return a

        def return_command_block_data_format() :
            base = python_nbt.nbt.NBTTagCompound()
            a = python_nbt.nbt.NBTTagCompound()
            a["Command"] = python_nbt.nbt.NBTTagString()
            a["CustomName"] = python_nbt.nbt.NBTTagString()
            a["ExecuteOnFirstTick"] = python_nbt.nbt.NBTTagByte(1)
            a["LPCommandMode"] = python_nbt.nbt.NBTTagInt()
            a["LPCondionalMode"] = python_nbt.nbt.NBTTagByte()
            a["LPRedstoneMode"] = python_nbt.nbt.NBTTagByte()
            a["LastExecution"] = python_nbt.nbt.NBTTagLong()
            a["LastOutput"] = python_nbt.nbt.NBTTagString()
            a["LastOutputParams"] = python_nbt.nbt.NBTTagList(tag_type=python_nbt.nbt.NBTTagInt)
            a["SuccessCount"] = python_nbt.nbt.NBTTagInt()
            a["TickDelay"] = python_nbt.nbt.NBTTagInt()
            a["TrackOutput"] = python_nbt.nbt.NBTTagByte(1)
            a["Version"] = python_nbt.nbt.NBTTagInt(19 if MathFunction.version_compare(_game.game_version,[1,19,50]) == -1 else 36)
            a["auto"] = python_nbt.nbt.NBTTagByte()
            a["conditionMet"] = python_nbt.nbt.NBTTagByte()
            a["conditionalMode"] = python_nbt.nbt.NBTTagByte()
            a["id"] = python_nbt.nbt.NBTTagString("CommandBlock")
            a["isMovable"] = python_nbt.nbt.NBTTagByte(1)
            a["powered"] = python_nbt.nbt.NBTTagByte()
            a["x"] = python_nbt.nbt.NBTTagInt()
            a["y"] = python_nbt.nbt.NBTTagInt()
            a["z"] = python_nbt.nbt.NBTTagInt()
            base["block_entity_data"] = a
            return base

        cb_type = ["minecraft:command_block","minecraft:chain_command_block","minecraft:repeating_command_block"]
        cb_condition,cb_facing = [0,1],[0,1,2,3,4,5]
        mcstructure_format = return_mcstructure_format()
        structure_size = [0,0,0]

        for i in list(self.command_block_data) :
            structure_size[0] = max(structure_size[0],i[0] - 1600)
            structure_size[1] = max(structure_size[1],i[1] + 64)
            structure_size[2] = max(structure_size[2],i[2] - 1600)
        for i in range(len(structure_size)) : structure_size[i] += 1
        
        mcstructure_format['size'] = python_nbt.nbt.NBTTagList(tag_type=python_nbt.nbt.NBTTagInt)
        for i in structure_size : mcstructure_format['size'].append(python_nbt.nbt.NBTTagInt(i))
            
        if 1 :
            mc_block = python_nbt.nbt.NBTTagCompound()
            mc_block['name'] = python_nbt.nbt.NBTTagString("minecraft:air")
            mc_block['version'] = python_nbt.nbt.NBTTagInt(
                17959425 if MathFunction.version_compare(_game.game_version,[1,19,50]) == -1 else 18098179)
            mc_block['states'] = python_nbt.nbt.NBTTagCompound()
            mcstructure_format['structure']['palette']['default']['block_palette'].append(mc_block)

        for i in itertools.product(cb_type,cb_condition,cb_facing) :
            command_block = python_nbt.nbt.NBTTagCompound()
            command_block['name'] = python_nbt.nbt.NBTTagString(i[0])
            command_block['version'] = python_nbt.nbt.NBTTagInt(
                17959425 if MathFunction.version_compare(_game.game_version,[1,19,50]) == -1 else 18098179)
            command_block['states'] = python_nbt.nbt.NBTTagCompound()
            command_block['states']["conditional_bit"] = python_nbt.nbt.NBTTagByte(i[1])
            command_block['states']["facing_direction"] = python_nbt.nbt.NBTTagInt(i[2])
            mcstructure_format['structure']['palette']['default']['block_palette'].append(command_block)

        for i in enumerate( itertools.product(range(structure_size[0]),range(-64,-64+structure_size[1],1),range(structure_size[2]))) :
            aaa = (i[1][0] + 1600, i[1][1], i[1][2] + 1600)
            if aaa not in self.command_block_data : 
                mcstructure_format['structure']['block_indices'][0].append(python_nbt.nbt.NBTTagInt())
                continue
            menory = self.command_block_data[aaa]
            command_block_format = return_command_block_data_format()
            command_block_format["block_entity_data"]["Command"] = python_nbt.nbt.NBTTagString(menory["command"])
            command_block_format["block_entity_data"]["TickDelay"] = python_nbt.nbt.NBTTagInt(menory["delay"])
            command_block_format["block_entity_data"]["auto"] = python_nbt.nbt.NBTTagByte(menory["auto"])
            command_block_format["block_entity_data"]["x"] = python_nbt.nbt.NBTTagInt(i[1][0])
            command_block_format["block_entity_data"]["y"] = python_nbt.nbt.NBTTagInt(i[1][1])
            command_block_format["block_entity_data"]["z"] = python_nbt.nbt.NBTTagInt(i[1][2])
            
            mcstructure_format['structure']['palette']['default']['block_position_data'][str(i[0])] = command_block_format
            palette_index = ( 
                cb_type.index(menory["id"]) * len(cb_condition) * len(cb_facing) +
                cb_condition.index(int(menory["block_state"]["conditional_bit"])) * len(cb_facing) +
                cb_facing.index(menory["block_state"]["facing_direction"]) + 1
            )
            mcstructure_format['structure']['block_indices'][0].append(python_nbt.nbt.NBTTagInt(palette_index))

        for i in range(structure_size[0] * structure_size[1] * structure_size[2]) :
            mcstructure_format['structure']['block_indices'][1].append(python_nbt.nbt.NBTTagInt(-1))

        python_nbt.nbt.write_to_nbt_file(
            os.path.join("functionality","structure_output", _game.world_name + ".mcstructure"),
            mcstructure_format, gzip=False, byteorder="little"
        )



Command_Block_Compile = command_block_compile_system()
