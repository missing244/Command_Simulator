from typing import List,Dict,Union,Literal,Tuple
from ... import RunTime
from .. import ID_tracker,COMMAND_CONTEXT,Response
from . import Selector,CompileError,CommandParser
import re,functools

selector_tree = CommandParser.SpecialMatch.Command_Root().add_leaves(*CommandParser.SpecialMatch.BE_Selector_Tree(CommandParser.BaseMatch.END_NODE))
Parser = CommandParser.ParserSystem.Command_Parser(selector_tree)
selector_test = re.compile("^[ ]{0,}@")


def Rawtext_Compiler(_game:RunTime.minecraft_thread, version:List[int], rawtext_json:dict):
    Rawtext_Analysis(_game, version, rawtext_json)
    return functools.partial(RunTime_Rawtext, rawtext_json=rawtext_json)

def Rawtext_Analysis(_game:RunTime.minecraft_thread, version:List[int], rawtext_json:dict) :
    if "rawtext" not in rawtext_json : raise CompileError("rawtext json需要存在 rawtext 指定")
    if not isinstance(rawtext_json["rawtext"], list) : raise CompileError("rawtext json的 rawtext 需要提供列表")

    for text_json in rawtext_json["rawtext"] :
        if "text" in text_json and not isinstance(text_json["text"], str) : 
            raise CompileError("rawtext json的 text 对象需要提供字符串")

        if "selector" in text_json : 
            if not isinstance(text_json["selector"], str) : raise CompileError("rawtext json的 selector 需要提供字符串")
            token_list = Parser.parser(text_json["selector"], version)
            if isinstance(token_list, tuple) : raise CompileError("selector组件中的选择器" + token_list[0])
            _,entity_func = Selector.Selector_Compiler(_game, token_list, 0, is_player=True)
            text_json["selector"] = entity_func

        elif "scores" in text_json : 
            if not isinstance(text_json["scores"], dict) : raise CompileError("rawtext json的 scores 需要提供对象")
            if "objective" not in text_json["scores"] : raise CompileError("rawtext json的 scores 需要提供 objective 指定")
            if not isinstance(text_json["scores"]["objective"], str) : raise CompileError("rawtext json的 scores.objective 需要提供字符串")
            if "name" not in text_json["scores"] : raise CompileError("rawtext json的 scores 需要提供 name 指定")
            if not isinstance(text_json["scores"]["name"], str) : raise CompileError("rawtext json的 scores.name 需要提供字符串")
            a = selector_test.search(text_json["scores"]["name"]) 
            if a is None : continue
            token_list = Parser.parser(text_json["selector"], version)
            if isinstance(token_list, tuple) : raise CompileError("选择器" + token_list[0])
            _,entity_func = Selector.Selector_Compiler(_game, token_list, 0, is_player=True)

        if "translate" in text_json :
            if not isinstance(text_json["translate"], str) : raise CompileError("rawtext json的 translate 需要提供字符串")
            if "with" in text_json and isinstance(text_json["with"], dict) : Rawtext_Compiler(_game, version, text_json["with"])
            elif "with" in text_json and isinstance(text_json["with"], list) and not all([isinstance(i,str) for i in text_json["with"]]) :
                raise CompileError("rawtext json的 translate.with 需要提供只含有字符串的列表")
            elif "with" in text_json : raise CompileError("rawtext json的 translate.with 需要提供字符串列表或rawtext json")


def RunTime_Rawtext(execute_var:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, rawtext_json:dict):
    text_list = RunTime_Analysis(execute_var, _game, rawtext_json)
    return "".join(text_list)

def RunTime_Analysis(execute_var:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, rawtext_json:dict):
    text_list:List[str] = []
    for text_json in rawtext_json["rawtext"] :
        if "text" in text_json : text_list.append(text_json["text"])

        elif "selector" in text_json : 
            entity_list = text_json["selector"](execute_var, _game)
            if isinstance(entity_list, Response.Response_Template) : continue
            text_list.append(", ".join( (ID_tracker(i) for i in entity_list) ))

        elif "scores" in text_json and isinstance(text_json["scores"]["name"], str) : 
            board,name = text_json["scores"]["objective"],text_json["scores"]["name"]
            score_value = _game.minecraft_scoreboard.____get_score____(board, name)
            if score_value != Exception : text_list.append(str(score_value))

        elif "scores" in text_json : 
            board = text_json["scores"]["objective"]
            entity_list = text_json["scores"]["name"](execute_var, _game)
            if isinstance(entity_list, Response.Response_Template) : continue
            text_list.append(", ".join( (_game.minecraft_scoreboard.____get_score____(board, i) for i in entity_list) ))

        if "translate" in text_json :
            rawtext_list = []
            if "with" in text_json and isinstance(text_json["with"], dict) :
                rawtext_list = RunTime_Analysis(execute_var, _game, text_json["with"])
            elif "with" in text_json and isinstance(text_json["with"], list) :
                rawtext_list = text_json["with"]

            pointer, translate_text = 0, text_json["translate"]
            while ("%%s" in translate_text) :
                if pointer >= rawtext_list.__len__() : translate_text = translate_text.replace("%%s","",1)
                else : translate_text = translate_text.replace("%%s",rawtext_list[pointer],1)
                pointer += 1

            while 1 :
                re_test1 = re.search("%%[0-9]", translate_text)
                if re_test1 is None : break
                replace_pointer = pointer + int(re_test1.group().replace("%%", "", 1)) - 1
                if replace_pointer >= rawtext_list.__len__() : translate_text = translate_text.replace("%%s","",1)
                else : translate_text = translate_text.replace("%%s",rawtext_list[replace_pointer],1)

            text_list.append(translate_text)
    return text_list