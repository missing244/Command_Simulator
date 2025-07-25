from .. import RunTime
from .. import BaseNbtClass,Constants
from package import MCCommandParser as CommandParser
from typing import Dict,Union,List,Tuple,Literal,Callable,TypedDict
import re


COMMAND_TOKEN = List[CommandParser.ParserSystem.Token]
class COMMAND_CONTEXT(TypedDict) :
    executer: BaseNbtClass.entity_nbt
    dimension: Literal["overworld","nether","the_end"]
    pos: List[float]
    rotate: List[float]
    version: List[int]
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
    if Version not in Command_Compile_Dict_Save : Command_Compile_Dict_Save[Version] = {}
    if Command in Command_Compile_Dict_Save[Version] : return Command_Compile_Dict_Save[Version][Command]

    token_list = CommandParser.Start_Tokenizer(Command, Version)
    if isinstance(token_list, tuple) : 
        Command_Compile_Dict_Save[Version][Command] = token_list
        return token_list
    func_object = CommandCompiler.Start_Compile(token_list, _game, Version)
    if isinstance(func_object, tuple) : 
        Command_Compile_Dict_Save[Version][Command] = func_object
        return func_object

    Command_Compile_Dict_Save[Version][Command] = func_object
    return func_object

from . import command_block as CommandBlock
from . import mcfunction as McFunction
from . import terminal as TerminalCommand

