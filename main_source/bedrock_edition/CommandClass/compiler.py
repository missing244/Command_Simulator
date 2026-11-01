from typing import Dict, Union, List, Tuple, Literal, Callable
import functools, traceback, json, itertools
from .__private import MinecraftSimulator, CommandContext, BlockPermutation, CompileError, BlockConditionCall
from .. import MCCommandParser



class CommandPerProcess:

    def __init__(self, _game:MinecraftSimulator, parser_result:MCCommandParser.ParserResult) :
        self.__game = _game
        self.parser_result = parser_result
        self.positions:List[Callable[[CommandContext]]] = []
        self.rotations:List[Callable[[CommandContext]]] = []
        self.args:Dict[str, List[Union[str, int, float]]] = {}
        self.selectors:List[Callable[[CommandContext, MinecraftSimulator]]] = []
        self.json_and_text:List[Callable[[CommandContext, MinecraftSimulator]]] = []
        self.blocks:List[Union[BlockPermutation, BlockConditionCall]] = []

        self.selectors_token_index:List[Tuple[int, int]] = []
        self.args_token_index:Dict[str, List[Tuple[int, int]]] = {}

        self.__pre_process()

    def __pre_process(self) :
        from .selector import Selector_Compiler
        from .json_text import Rawtext_Compiler, ItemComponent_Compiler, SelectorMsg_Compiler
        from .other import Pos_Compiler, Block_Compiler, Condition_Block_Compiler, Rotation_Compiler

        token_cursor = self.parser_result.create_cursor()
        rawtext_command = {"tellraw", "titleraw"}
        while not token_cursor.is_end() :
            token = token_cursor.peek()
            if token["type"] in {"Selector", "Player_Name"} :
                _start = token_cursor.tell()
                call_obj = Selector_Compiler(self.__game, token_cursor)
                _end = token_cursor.tell()
                self.selectors.append(call_obj)
                self.selectors_token_index.append((_start, _end))
            elif token["type"] in {"Json_Start", "SelectorMsg"} :
                if self.args.get("Command")[0] in rawtext_command : 
                    call_obj = Rawtext_Compiler(self.__game, token_cursor)
                elif token["type"] == "SelectorMsg" : call_obj = SelectorMsg_Compiler(self.__game, token_cursor)
                else : call_obj = ItemComponent_Compiler(self.__game, token_cursor)
                self.json_and_text.append(call_obj)
            elif token["type"] in {"Absolute_Pos", "Relative_Pos", "Local_Pos"} :
                call_obj = Pos_Compiler(token_cursor)
                self.positions.append(call_obj)
            elif token["type"] in {"Absolute_Rotation", "Relative_Rotation"} :
                call_obj = Rotation_Compiler(token_cursor)
                self.rotations.append(call_obj)
            elif token["type"] in {"Block_ID", "Block_ID(Condition)"} :
                block_id = token["token"]
                if token["type"] == "Block_ID" : 
                    call_obj = Block_Compiler(self.__game, token_cursor, block_id)
                    if call_obj.name not in self.__game.GameSource.BLOCK: 
                        raise CompileError(f"不存在的方块 ID: {block_id}", token_cursor.tell(), token_cursor.tell()+1)
                else : call_obj = Condition_Block_Compiler(self.__game, token_cursor, block_id)
                self.blocks.append(call_obj)
            else :
                self.args.setdefault(token["type"], []).append(token["token"])
                self.args_token_index.setdefault(token["type"], []).append((token_cursor.tell(), token_cursor.tell()+1))
                token_cursor.advance()

def Start_Compile(_game:MinecraftSimulator, parser_result:MCCommandParser.ParserResult) -> Union[functools.partial, CompileError] :
    command_test = parser_result.tokens[0]
    if command_test["type"] != "Command" : raise RuntimeError(f"{command_test['token']}不是命令树解析根", 0, 1)
    if command_test["token"] not in Command_Compiler_Mapping : raise RuntimeError(f"{command_test['token']}不是被注册的命令", 0, 1)

    try : PerProcessObject = CommandPerProcess(_game, parser_result)
    except CompileError as e : e.parser_result = parser_result ; return e

    CompilerObject = Command_Compiler_Mapping[command_test["token"]]
    if isinstance(CompilerObject, dict) : 
        Compiler_Object_Copy = CompilerObject
        for version, compiler in Compiler_Object_Copy.items() :
            if version <= parser_result.version : CompilerObject = compiler

    try : callback:functools.partial = CompilerObject.__compiler__(_game, PerProcessObject)
    except CompileError as e : e.parser_result = parser_result ; return e
    except Exception as e : raise e
    else : return callback

    

from . import sub_compiler_1 as SubComplier1
from . import sub_compiler_2 as SubComplier2
from . import sub_compiler_3 as SubComplier3

Command_Compiler_Mapping = {
    "ability": SubComplier1.ability, "aimassist":SubComplier1.aimassist, "alwaysday": SubComplier1.alwaysday, 
    "camera": SubComplier1.camera, "camerashake": SubComplier1.camerashake, "clear": SubComplier1.clear,
    "clearspawnpoint": SubComplier1.clearspawnpoint, "clone": SubComplier1.clone, "controlscheme": SubComplier1.controlscheme,
    "damage": SubComplier1.damage, "daylock": SubComplier1.daylock, "dialogue": SubComplier1.dialogue,
    "difficulty":SubComplier1.difficulty, "effect":SubComplier1.effect, "enchant":SubComplier1.enchant, 
    "event": SubComplier1.event, "fill":SubComplier1.fill, "fog":SubComplier1.fog, "gamemode":SubComplier1.gamemode, 
    "gamerule":SubComplier1.gamerule, "give":SubComplier1.give,
    
    "hud":SubComplier2.hud, "inputpermission": SubComplier2.inputpermission, "kick":SubComplier2.kick, 
    "kill":SubComplier2.kill, "list": SubComplier2.list_command, "locate":SubComplier2.locate, 
    "loot":SubComplier2.loot, "me": SubComplier2.me, "say":SubComplier2.me, "mobevent":SubComplier2.mobevent,
    "music": SubComplier2.music, "particle":SubComplier2.particle, "place":SubComplier2.place, 
    "playanimation":SubComplier2.playanimation, "playsound": SubComplier2.playsound, "replaceitem":SubComplier2.replaceitem,
    "recipe":SubComplier2.recipe, "ride": SubComplier2.ride, "schedule":SubComplier2.schedule, "scoreboard":SubComplier2.scoreboard,
    "setblock": SubComplier2.setblock, "setworldspawn":SubComplier2.setworldspawn, "spawnpoint":SubComplier2.spawnpoint,
    "spreadplayers":SubComplier2.spreadplayers,

    "scriptevent":SubComplier3.scriptevent, "structure":SubComplier3.structure, "stopsound":SubComplier3.stopsound, 
    "summon":{(0,0,0):SubComplier3.summon_1_0_0, (1,19,80):SubComplier3.summon_1_70_0}, 
    "tag":SubComplier3.tag, "teleport":SubComplier3.teleport, "tp":SubComplier3.teleport, 
    "tellraw":SubComplier3.tellraw, "testfor":SubComplier3.testfor, "testforblock":SubComplier3.testforblock, 
    "testforblocks":SubComplier3.testforblocks, "tickingarea":SubComplier3.tickingarea, "time":SubComplier3.time, 
    "title":SubComplier3.titleraw, "titleraw":SubComplier3.titleraw, "toggledownfall":SubComplier3.toggledownfall,
    "volumearea":SubComplier3.volumearea, "tell":SubComplier3.tell, "msg":SubComplier3.tell,
    "w":SubComplier3.tell, "weather":SubComplier3.weather, "xp":SubComplier3.xp,
}



"""
Command_Compiler_Mapping = {
    "execute": {(0,0,0):SubComplier0.execute_1_19, (1,19,50):SubComplier0.execute_1_19_50}, "function":SubComplier0.function,

    
    
    

  }
"""

