
from . import base_match as BaseMatch
from . import special_match as SpecialMatch
from . import json_paser as JsonPaser
from . import command_tree as CommandTree
from . import parser_system as ParserSystem

Parser = ParserSystem.Command_Parser(CommandTree.Command_Tree)

def Start_Tokenizer(command:str, version:tuple) :
    return Parser.parser(command, version)



