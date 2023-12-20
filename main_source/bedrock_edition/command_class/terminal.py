from . import CommandParser,HtmlGenerate,Response,COMMAND_CONTEXT,CommandCompiler
from .. import RunTime
from typing import List,Dict,Union,Literal,Tuple
import re,functools

terminal_command_parser = CommandParser.ParserSystem.Command_Parser( 
    CommandParser.SpecialMatch.Command_Root().add_leaves(
        CommandParser.BaseMatch.KeyWord("Command","#").add_leaves(
            CommandParser.BaseMatch.Char("Command","reload").add_leaves(
                    CommandParser.BaseMatch.Enum("Open_CB_View","true","false").add_leaves(
                        CommandParser.BaseMatch.Enum("Structure","none","bdx","mcstructure").add_leaves(
                            CommandParser.BaseMatch.END_NODE
                        ),
                        CommandParser.BaseMatch.END_NODE
                    ),
                    CommandParser.BaseMatch.END_NODE
                ),
            CommandParser.BaseMatch.Char("Command","set").add_leaves(
                    CommandParser.BaseMatch.Char("Argument","command_version").add_leaves(
                        CommandParser.BaseMatch.Int("V1").add_leaves(
                            CommandParser.BaseMatch.Int("V2").add_leaves(
                                CommandParser.BaseMatch.Int("V3").add_leaves( CommandParser.BaseMatch.END_NODE )
                            )   
                        )
                    ),
                    CommandParser.BaseMatch.Char("Argument","test_time").add_leaves(
                        CommandParser.BaseMatch.Int("Time").add_leaves( CommandParser.BaseMatch.END_NODE )
                    )
                ),
            CommandParser.BaseMatch.Char("Command","command").add_leaves(
                CommandParser.BaseMatch.Char("Argument","loop").add_leaves(
                    *CommandParser.CommandTree.Command_Tree.tree_leaves
                ),
                CommandParser.BaseMatch.Char("Argument","delay").add_leaves(
                    CommandParser.BaseMatch.Int("Time").add_leaves(
                        *CommandParser.CommandTree.Command_Tree.tree_leaves
                    )
                ),
                CommandParser.BaseMatch.Char("Argument","end").add_leaves(
                    *CommandParser.CommandTree.Command_Tree.tree_leaves
                )
            ),
        )
    )
)


def Terminal_Compiler(_game:RunTime.minecraft_thread, s:str) :
    Terminal_Command = {
        "reload" : command_reload,
        "set" : command_set,
        "command" : command_command,
    }
    token_list = terminal_command_parser.parser(s, (255,0,0))
    if isinstance(token_list, tuple) : return token_list[1]
    token_list.pop(0)
    return Terminal_Command[token_list[0]["token"].group()](_game, s, token_list)


def command_reload(_game:RunTime.minecraft_thread, command:str, token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    index = 1
    if index >= len(token_list) : 
        return functools.partial(reload_doing,_game=_game,cb_view="false",structure="none")

    index += 1
    if index >= len(token_list) : return functools.partial(reload_doing, _game=_game,
        cb_view=token_list[-1]["token"].group(),structure="none")

    return functools.partial(reload_doing, _game=_game,
        cb_view=token_list[-2]["token"].group(), structure=token_list[-1]["token"].group())

def reload_doing(context:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, cb_view:Literal["true","false"],
                 structure:Literal["none","bdx","mcstructure"]) :
    from . import CommandBlock,McFunction
    CommandBlock.Command_Block_Compile.open_command_block_file(_game)
    McFunction.Function_Compiler(_game)

    if cb_view == "true" : CommandBlock.Command_Block_Compile.generate_command_block_view().generate_html("command_block_view.html")
    if structure == "bdx" : CommandBlock.Command_Block_Compile.transfor_bdx_file()
    elif structure == "mcstructure" : CommandBlock.Command_Block_Compile.transfor_mcstructure_file()

    test_list = (
        CommandBlock.Command_Block_Compile.get_command_block_error()["encoding_error"],
        CommandBlock.Command_Block_Compile.get_command_block_error()["syntax_error"],
        McFunction.get_function_error()["encoding_error"],
        McFunction.get_function_error()["syntax_error"]
    )
    
    html = HtmlGenerate.generate_all_command_load_html()
    html.write_cb_file_encode(test_list[0])
    html.write_cb_file_syntax(test_list[1])
    html.write_func_file_encode(test_list[2])
    html.write_func_file_syntax(test_list[3])
    html.encode_for_html().generate_html(_game.world_name,"command_load.html")

    if any(test_list) :
        HtmlGenerate.setTimeOut(1.5, lambda:HtmlGenerate.webbrowser.open("http://localhost:32323/command_load.html"))
        return Response.Response_Template("文件含有语法或编码错误\n具体信息请在浏览器中查看").substitute({})
    CommandBlock.Command_Block_Compile.write_to_world(_game)
    return Response.Response_Template("全部命令已重载完成", 1, 1).substitute({})


def command_set(_game:RunTime.minecraft_thread, command:str, token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) :
    if token_list[1]["token"].group() == "command_version" : 
        if all([int(token_list[1+i]["token"].group()) >= 0 for i in range(1,4,1)]) :
            return CommandCompiler.CompileError("版本号不能为负数", pos=(token_list[2]["token"].start(),token_list[4]["token"].end()))
        return functools.partial(set_version, _game=_game, version=[int(token_list[1+i]["token"].group()) for i in range(1,4,1)])
    elif token_list[1]["token"].group() == "test_time" : 
        if int(token_list[2]["token"].group()) < 0 : 
            return CommandCompiler.CompileError("测试时间不能为负数", pos=(token_list[2]["token"].start(),token_list[2]["token"].end()))
        return functools.partial(set_testTime, _game=_game, time=int(token_list[2]["token"].group()))

def set_version(context:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, version:tuple) :
    _game.game_version = tuple(version)
    return Response.Response_Template("游戏版本已设置完成", 1, 1).substitute({})

def set_testTime(context:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, time:int) :
    _game.runtime_variable.how_times_run_all_command = time
    return Response.Response_Template("测试时间已设置完成", 1, 1).substitute({})


def command_command(_game:RunTime.minecraft_thread, command:str, token_list:List[Dict[Literal["type","token"],Union[str,re.Match]]]) -> functools.partial :
    if token_list[1]["token"].group() == "loop" : 
        command_object = CommandCompiler.Start_Compile(token_list[2:], _game.game_version, _game)
        if isinstance(command_object, tuple) : return command_object[1]
        return functools.partial(command_loop, _game=_game, command=command[token_list[2]["token"].start()], command_obj=command_object)
    elif token_list[1]["token"].group() == "delay" : 
        if int(token_list[2]["token"].group()) < 0 : 
            return CommandCompiler.CompileError("延时时间不能为负数", pos=(token_list[2]["token"].start(),token_list[2]["token"].end()))
        command_object = CommandCompiler.Start_Compile(token_list[3:], _game.game_version, _game)
        if isinstance(command_object, tuple) : return command_object[1]
        return functools.partial(command_delay, _game=_game, time=int(token_list[2]["token"].group()),
        command=command[token_list[3]["token"].start()], command_obj=command_object)
    elif token_list[1]["token"].group() == "end" : 
        command_object = CommandCompiler.Start_Compile(token_list[2:], _game.game_version, _game)
        if isinstance(command_object, tuple) : return command_object[1]
        return functools.partial(command_end, _game=_game, command=command[token_list[2]["token"].start()], command_obj=command_object)

def command_loop(context:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, command:str, command_obj:functools.partial) :
    _game.runtime_variable.command_will_loop.append( (command, command_obj) )
    return Response.Response_Template("成功添加了循环命令", 1, 1).substitute({})

def command_delay(context:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, time:int, command:str, command_obj:functools.partial) :
    run_gt = time + _game.minecraft_world.game_time
    if run_gt not in _game.runtime_variable.command_will_run : _game.runtime_variable.command_will_run[run_gt] = []
    _game.runtime_variable.command_will_run[run_gt].append( (command, command_obj) )
    return Response.Response_Template("成功添加了延时命令", 1, 1).substitute({})

def command_end(context:COMMAND_CONTEXT, _game:RunTime.minecraft_thread, command:str, command_obj:functools.partial) :
    _game.runtime_variable.command_will_run_test_end.append( (command, command_obj) )
    return Response.Response_Template("成功添加了结束命令", 1, 1).substitute({})


