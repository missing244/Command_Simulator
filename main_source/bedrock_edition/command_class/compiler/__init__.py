from typing import Dict,Union,List,Tuple,Literal
import re,functools,traceback,json,itertools
from .. import CommandParser,COMMAND_TOKEN
from ... import RunTime,Constants
class CompileError(CommandParser.BaseMatch.Command_Match_Exception) : pass

def Quotation_String_transfor_1(s:str) -> str :
    """用于名字中含有非法字符的转换 \"a\\na\" -> ana """
    if s[0] != "\"" or s[-1] != "\"" : return s
    s = s[1:len(s)-1]
    s_list = [] ; index = 0
    while index < len(s) :
        if s[index] != "\\" :  s_list.append( s[index] )
        else :
            if s[index+1] == "\\" : s_list.append( "\n" )
            elif s[index+1] == "\"" : s_list.append( "\"" )
        index += 1
    return "".join(s_list)

def ID_transfor(s:str) -> str :
    """ stone -> minecraft:stone """
    a = s.split(":",1)
    if len(a) == 1 : return "minecraft:%s" % a[0]
    else : return s

def BlockState_Compiler(block_id:str, token_list:COMMAND_TOKEN, index:int) -> Tuple[int,dict] :
    block_id = ID_transfor(block_id)
    block_id_state = {} if (block_id not in Constants.BLOCK_STATE) else Constants.BLOCK_STATE[block_id]
    block_id_state : Dict[Literal["default","support_value"], Union[Dict,Dict]]
    block_state_token : List[str] = []
    if token_list[index]["type"] != "Start_BlockState_Argument" : return ({}, index)
    index += 1 ; block_state_token.append("{")

    while 1 :
        if token_list[index]["type"] in ("BlockState","Value","Next_BlockState_Argument") : 
            block_state_token.append( token_list[index]["token"].group() )
        elif token_list[index]["type"] == "Equal" : 
            block_state_token.append(":")
        elif token_list[index]["type"] == "End_BlockState_Argument" : 
            block_state_token.append("}") ; index += 1 ; break
        index += 1

    input_block_state = json.loads("".join(block_state_token))
    for state in input_block_state :
        if state not in block_id_state["support_value"] : 
            raise CompileError("方块 %s 不存在 %s 状态" % (block_id,state))
        if input_block_state[state] not in block_id_state["support_value"][state] : 
            raise CompileError("方块状态 %s 不存在值 %s" % (state,input_block_state[state]))

    return (index, input_block_state)

def ItemComponent_Compiler(_game:RunTime.minecraft_thread, token_list:COMMAND_TOKEN, index:int) -> Tuple[int,dict] :
    json_str_list = [i["token"].group() for i in itertools.takewhile(lambda x : x["type"] != "All_Json_End", token_list[index:])]
    json_str_list.append(token_list[index + len(json_str_list)]["token"].group())
    index = index + len(json_str_list)
    item_nbt = json.loads("".join(json_str_list))
    key_list = set(("minecraft:keep_on_death", "minecraft:can_destroy", "minecraft:can_place_on", "minecraft:item_lock"))
    if set(item_nbt) - key_list : raise CompileError("不存在的物品组件：%s" % ", ".join( set(item_nbt) - key_list ))
    if "minecraft:keep_on_death" in item_nbt and (not isinstance(item_nbt["minecraft:keep_on_death"], dict) or 
        item_nbt["minecraft:keep_on_death"].__len__() > 0) : raise CompileError("keep_on_death 物品组件的值应该为 {}")

    if "minecraft:can_destroy" in item_nbt and (not isinstance(item_nbt["minecraft:can_destroy"], dict) or 
        item_nbt["minecraft:can_destroy"].__len__() != 1 or "blocks" not in item_nbt["minecraft:can_destroy"] or 
        not isinstance(item_nbt["minecraft:can_destroy"]["blocks"], list) or 
        any( (not isinstance(i,str) for i in item_nbt["minecraft:can_destroy"]["blocks"]) )) : 
        raise CompileError('can_destroy 物品组件的值应该为 {"blocks":["air", ...]}')
    if "minecraft:can_destroy" in item_nbt :
        for i in item_nbt["minecraft:can_destroy"]["blocks"] :
            if (i if ":" in i else ("minecraft:%s" % i)) not in _game.minecraft_ident.blocks :
                raise CompileError('can_destroy 物品组件中存在不存在的方块ID%s' % i)

    if "minecraft:can_place_on" in item_nbt and (not isinstance(item_nbt["minecraft:can_place_on"], dict) or 
        item_nbt["minecraft:can_place_on"].__len__() != 1 or "blocks" not in item_nbt["minecraft:can_place_on"] or 
        not isinstance(item_nbt["minecraft:can_place_on"]["blocks"], list) or 
        any( (not isinstance(i,str) for i in item_nbt["minecraft:can_place_on"]["blocks"]) )) : 
            raise CompileError('can_place_on 物品组件的值应该为 {"blocks":["air", ...]}')
    if "minecraft:can_place_on" in item_nbt :
        for i in item_nbt["minecraft:can_place_on"]["blocks"] :
            if (i if ":" in i else ("minecraft:%s" % i)) not in _game.minecraft_ident.blocks :
                raise CompileError('can_place_on 物品组件中存在不存在的方块ID%s' % i)

    if "minecraft:item_lock" in item_nbt and (not isinstance(item_nbt["minecraft:item_lock"], dict) or 
        item_nbt["minecraft:item_lock"].__len__() != 1 or "mode" not in item_nbt["minecraft:item_lock"] or 
        not isinstance(item_nbt["minecraft:item_lock"]["mode"], str) or 
        item_nbt["minecraft:item_lock"]["mode"] not in ("lock_in_inventory", "lock_in_slot") ) : 
        raise CompileError('item_lock 物品组件的值应该为 {"mode":"lock_in_inventory" 或 "lock_in_slot"}')
    
    return (index, item_nbt)

def replace_str(base:str, start:int, end:int, replace:str) -> str:
    return "".join([ base[:start] , replace , base[end:] ])

def Msg_Compiler(_game:RunTime.minecraft_thread, msg_temp:str, msg_temp_start:int) :
    search_entity_list:List = []
    re_search = list(re.compile("@(p|a|r|e|s|initiator)").finditer(msg_temp))
    re_search.reverse()
    for re_obj in re_search :
        token_1 = Selector_Parser.parser(msg_temp[re_obj.start():], (100,0,0))
        if isinstance(token_1, tuple) : 
            if hasattr(token_1[1], "pos") : 
                token_1[1].pos = tuple([i+re_obj.start()+msg_temp_start for i in token_1[1].pos])
            raise token_1[1]
        msg_temp = replace_str(msg_temp, re_obj.start()+token_1[0]["token"].start(), 
            re_obj.start()+token_1[-2]["token"].end(), "%s")
        search_entity_list.append( Selector.Selector_Compiler(_game, token_1, 0)[1] )
    search_entity_list.reverse()
    return (msg_temp, search_entity_list)

Selector_Parser = CommandParser.ParserSystem.Command_Parser(
    CommandParser.SpecialMatch.Command_Root().add_leaves(
        *CommandParser.SpecialMatch.BE_Selector_Tree(
            CommandParser.BaseMatch.AnyMsg("Msg").add_leaves(CommandParser.BaseMatch.END_NODE)
        )
    )
)

from . import selector as Selector
from . import rawtext as Rawtext
from . import command_1 as Command1
from . import command_2 as Command2
from . import command_0 as Command0
from . import command_3 as Command3
from . import command_4 as Command4

be_command_list = [
    'ability', 'alwaysday', 'camera', 'camerashake', 'clear', 'clearspawnpoint', 'clone', 'damage', 'daylock', 'dialogue',
    'difficulty', 'effect', 'enchant', 'event', 'execute', 'fill', 'fog', 'function', 'gamemode', 'gamerule', 
    'give', 'inputpermission', 'kick', 'kill', 'list', 'locate', 'loot', 'me', 'mobevent', 'msg', 
    'music', 'particle', 'playanimation', 'playsound', 'replaceitem', "recipe", 'ride', 'say', 'schedule', 'scoreboard',
    'setblock', 'setworldspawn', 'spawnpoint', 'spreadplayers', 'structure', 'stopsound', 'summon', 'tag', 'teleport', 'tell', 
    'tellraw', 'testfor', 'testforblock', 'testforblocks', 'tickingarea', 'time', 'title', 'titleraw', 'toggledownfall', 'tp',
    'volumearea', 'w', 'weather', 'xp', "scriptevent"
]

Command_to_Compiler = {
    # key:class or key:{tuple:class}
    "execute": {(0,0,0):Command0.execute_1_19, (1,19,50):Command0.execute_1_19_50}, "function":Command0.function,

    "ability": Command1.ability, "alwaysday": Command1.alwaysday, "camera": Command1.camera,
    "camerashake": Command1.camerashake, "clear": Command1.clear, "clearspawnpoint": Command1.clearspawnpoint,
    "clone": Command1.clone, "damage": Command1.damage, "daylock": Command1.daylock,
    "dialogue": Command1.dialogue, "effect":Command1.effect, "enchant":Command1.enchant,
    "event": Command1.event, "fill":{(0,0,0):Command1.fill_1_0_0, (1,19,80):Command1.fill_1_19_80}, "fog":Command1.fog,
    "gamemode": Command1.gamemode, "gamerule":Command1.gamerule, "give":Command1.give,

    "inputpermission": Command3.inputpermission, "kick":Command3.kick, "kill":Command3.kill,
    "list": Command3.list_command, "locate":Command3.locate, "loot":Command3.loot,
    "me": Command3.me, "say":Command3.me, "mobevent":Command3.mobevent,
    "music": Command3.music, "particle":Command3.particle, "playanimation":Command3.playanimation,
    "playsound": Command3.playsound, "replaceitem":Command3.replaceitem, "recipe":Command3.recipe,
    "ride": Command3.ride, "schedule":Command3.schedule, "scoreboard":Command3.scoreboard,
    "setblock": Command3.setblock, "setworldspawn":Command3.setworldspawn, "spawnpoint":Command3.spawnpoint,
    "spreadplayers":Command3.spreadplayers,

    "structure": Command2.structure, "stopsound": Command2.stopsound, "summon": {(0,0,0):Command2.summon_1_0_0, (1,19,80):Command2.summon_1_70_0}, 
    "tag": Command2.tag, "teleport" : Command2.teleport, "tp" : Command2.teleport, 
    "tellraw": Command2.tellraw, "testfor" : Command2.testfor, "testforblock" : Command2.testforblock, 
    "testforblocks" : Command2.testforblocks, "tickingarea" : Command2.tickingarea, "time" : Command2.time, 
    "title" : Command2.titleraw, "titleraw" : Command2.titleraw, "toggledownfall" : Command2.toggledownfall,
    "volumearea" : Command2.volumearea, "tell" : Command2.tell, "msg" : Command2.tell,
    "w" : Command2.tell, "weather" : Command2.weather, "xp" : Command2.xp,

    "hud" : Command4.hud, "scriptevent":Command4.scriptevent
}

def Start_Compile(token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]], _game:RunTime.minecraft_thread, 
                  version:Tuple[int]) -> Union[functools.partial,Tuple[str,Exception],None] :
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

    try : 
        if command_name == "execute" : return func.__compiler__(_game, token_list, version)
        else : return func.__compiler__(_game, token_list)
    except Exception as e :
        if hasattr(e,"pos") : s = "%s\n错误位于字符%s至%s" % (e.args[0], e.pos[0], e.pos[1])
        else : s = e.args[0]
        if not isinstance(e, CommandParser.BaseMatch.Command_Match_Exception) : traceback.print_exc()
        return (s,e)
    
