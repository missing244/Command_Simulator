from typing import Dict,Union,List,Tuple,Literal
import re,functools,traceback
from .. import CommandParser
from ... import RunTime
class CompileError(CommandParser.BaseMatch.Command_Match_Exception) : pass

from . import selector as Selector
from . import rawtext as Rawtext
from . import command_1 as Command1

be_command_list = [
    'ability', 'alwaysday', 'camera', 'camerashake', 'clear', 'clearspawnpoint', 'clone', 'damage', 'daylock', 'dialogue',
    'difficulty', 'effect', 'enchant', 'event', 'execute', 'fill', 'fog', 'function', 'gamemode', 'gamerule', 
    'give', 'inputpermission', 'kick', 'kill', 'list', 'locate', 'loot', 'structure', 'me', 'mobevent',
    'msg', 'music', 'particle', 'playanimation', 'playsound', 'replaceitem', "recipe", 'ride', 'say', 'schedule',
    'scoreboard', 'setblock', 'setworldspawn', 'spawnpoint', 'spreadplayers', 'stopsound', 'summon', 'tag', 'teleport', 'tell',
    'tellraw', 'testfor', 'testforblock', 'testforblocks', 'tickingarea', 'time', 'title', 'titleraw', 'toggledownfall', 'tp',
    'volumearea', 'w', 'weather', 'xp'
]

Command_to_Compiler = {
    # key:class or key:{tuple:class}
    "ability" : Command1.ability, "alwaysday" : Command1.alwaysday, "camera" : Command1.camera,
    "camerashake" : Command1.camerashake,

    "weather" : Command1.weather,
    "xp" : Command1.xp
}

def Quotation_String_transfor_1(s:str) -> str :
    """用于名字中含有非法字符的转换 \"a\\na\" -> ana """
    if s[0] != "\"" or s[-1] != "\"" : return s
    s = s[1:len(s)-1]
    s_list = [] ; index = 0
    while index < (len(s) - 1) :
        if s[index] != "\\" :  s_list.append( s[index] )
        else :
            if s[index+1] == "\\" : s_list.append( "\n" )
            elif s[index+1] == "\"" : s_list.append( "\"" )
        index += 1
    return "".join(s_list)

def Start_Compile(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]], 
                  version:Tuple[int], _game:RunTime.minecraft_thread) -> Union[functools.partial,Tuple[str,Exception],None] :
    if token_list[0]["type"] != "Command" : return None
    command_name = token_list[0]["token"].group()
    if command_name not in Command_to_Compiler : return None

    if isinstance(Command_to_Compiler[command_name], type) : func = Command_to_Compiler[command_name]
    else :
        func = None ; func_version_list = list(Command_to_Compiler[command_name])
        for version_index,choose_version in enumerate(func_version_list) :
            version_int1 = version[0] * 1000000 + version[1] * 1000 + version[2]
            version_int2 = choose_version[0] * 1000000 + choose_version[1] * 1000 + choose_version[2]
            if version_int2 > version_int1 : func = Command_to_Compiler[command_name][func_version_list[version_index-1]]
        if not func : func = Command_to_Compiler[command_name][func_version_list[-1]]

    try : return func.__compiler__(_game, token_list)
    except Exception as e :
        if hasattr(e,"pos") : s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
        else : s = e.args[0]
        if not isinstance(e, CompileError) : traceback.print_exc()
        return (s,e)
    
