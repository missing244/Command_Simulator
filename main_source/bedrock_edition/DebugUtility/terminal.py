from . import MCCommandParser as CommandParser, GameClass, CommandClass
from typing import List, Dict, Union, Literal, Tuple, Callable
import re, functools, webbrowser, json
MinecraftSimulator = GameClass.MinecraftSimulator
CompileError = CommandClass.CompileError
CommandContext = CommandClass.CommandContext
CommandResult = CommandClass.CommandResult
ParserResult = CommandParser.ParserResult
MCCommandCall = CommandClass.MCCommandCall
MCFUNCTION_COMMAND_ERROR_START = re.compile("[ ]{0,}/")
MCFUNCTION_NONE_COMMAND = re.compile("[ ]{0,}$|[ ]{0,}#")


TerminalCommandParser = CommandParser.ParserSystem.Command_Parser( 
    CommandParser.SpecialMatch.Command_Root().add_leaves(
        CommandParser.BaseMatch.KeyWord("Command_Start","#").add_leaves(
            CommandParser.BaseMatch.Char("Command", "reload").add_leaves(
                CommandParser.BaseMatch.END_NODE
            ),
            CommandParser.BaseMatch.Char("Command", "testing").add_leaves(
                CommandParser.BaseMatch.Int("TestTime").add_leaves( 
                    CommandParser.BaseMatch.Enum("OpenWeb","false","true").add_leaves(
                        CommandParser.BaseMatch.Int("x1").add_leaves(
                        CommandParser.BaseMatch.Int("y1").add_leaves(
                        CommandParser.BaseMatch.Int("z1").add_leaves(
                        CommandParser.BaseMatch.Int("x2").add_leaves(
                        CommandParser.BaseMatch.Int("y2").add_leaves(
                        CommandParser.BaseMatch.Int("z2").add_leaves(
                            CommandParser.BaseMatch.END_NODE
                        ))))))
                    )
                )
            ),
            CommandParser.BaseMatch.Char("Command", "command").add_leaves(
                CommandParser.BaseMatch.Enum("Argument", "tick_start_loop", "tick_end_loop",
                    "tick_start_delay", "tick_end_delay").add_leaves(
                    CommandParser.BaseMatch.Int("Time").add_leaves(
                        CommandParser.BaseMatch.AnyMsg("Command").add_leaves( CommandParser.BaseMatch.END_NODE )
                    )
                ),
            ),
            CommandParser.BaseMatch.AnyMsg("Note").add_leaves( CommandParser.BaseMatch.END_NODE )
        )
    )
)

def Terminal_Compiler(_game:MinecraftSimulator, s:str) -> Union[None, ParserResult, functools.partial] :
    Terminal_Command = {
        "reload" : command_reload,
        "setting" : command_testing,
        "command" : command_command,
    }
    parser_result = TerminalCommandParser.parser_v2(s, _game.GameVersion)
    if not parser_result.success : return parser_result
    Command = parser_result.tokens[0]["token"]
    if Command not in Terminal_Command : return None
    return Terminal_Command[Command](_game, parser_result)


def command_reload(_game:MinecraftSimulator, parser_result:ParserResult) :
    return functools.partial(reload_doing, s=parser_result.command)

def Function_Checker(_game:MinecraftSimulator) :
    from ..CommandClass import CompileError
    MCFUNCTIONS = _game.GameSource.MCFUNCTIONS
    mcfunction_error:Dict[str, List[Tuple[int, int, str, str]]] = {}

    for sub_path, (abs_path, version, contents) in MCFUNCTIONS.copy().items() :
        function_calls:List[Callable[[CommandContext, MinecraftSimulator], CommandResult]] = []
        for lines, command_str in enumerate(contents, start=1) :
            if MCFUNCTION_NONE_COMMAND.match(command_str) : continue

            _re = MCFUNCTION_COMMAND_ERROR_START.match(command_str)
            if _re :
                mcfunction_error.setdefault(abs_path, []).append( (lines, _re.end()-1, command_str, "mcfunction命令不能以/开头") )
                continue

            func_object = _game.CommandManager.compile(command_str, version)
            if isinstance(func_object, ParserResult) :
                _idx = func_object.error.pos[0]
                mcfunction_error.setdefault(abs_path, []).append( (lines, _idx, command_str, str(func_object.error)) )
                continue
            elif isinstance(func_object, CompileError) : 
                _idx = func_object.parser_result.tokens[func_object.start_index]["start"]
                mcfunction_error.setdefault(abs_path, []).append( (lines, _idx, command_str, str(func_object.error)) )
                continue
            else : function_calls.append(func_object)
        MCFUNCTIONS[sub_path] = function_calls

    return mcfunction_error

def reload_doing(context:CommandContext, _game:MinecraftSimulator, s:str) :
    from . import CBDeployCompiler, HtmlClass
    _game.GameSource.MCFUNCTIONS.clear()
    _game.GameSource.update_BP_mcfunction()

    error_dict = Function_Checker(_game)
    cb_compiler = CBDeployCompiler(_game)
    cb_compiler.compile()

    if error_dict or cb_compiler.open_errors or cb_compiler.errors :
        _game.GameSource.MCFUNCTIONS.clear()
        html_content = HtmlClass.CommandLoadHTML
        for ph, data in [
            (r"/*__FUNC_COMPILE_ERRORS__*/{}", error_dict),
            (r"/*__CB_FILES__*/{}", cb_compiler.open_errors),
            (r"/*__CB_COMPILE_ERRORS__*/{}", cb_compiler.errors)]:
            html_content = html_content.replace(ph, json.dumps(data), 1)
        uid = _game.WebsiteRegister(html_content)
        HtmlClass.setTimeOut(2, webbrowser.open_new, f"http://localhost:32323/?tempfile={uid}")
        return CommandResult(False, s, "文件存在错误，请注意修改\n即将打开错误反馈网页", [context])
    else : 
        cb_compiler.write_in_world()
        return CommandResult(True, s, "已成功重载函数和命令方块", [context])


def command_testing(_game:MinecraftSimulator, parser_result:ParserResult) :
    command = parser_result.command
    tokens = parser_result.tokens
    if tokens[1]["token"] < 0 : return CompileError("测试时间不能为负数", 2, 3)
    time = tokens[1]["token"]
    web_view = tokens[2]["token"] == "true"
    start_pos = list(tokens[i]["token"] for i in range(3, 6))
    end_pos = list(tokens[i]["token"] for i in range(6, 9))
    for i in range(3) : 
        if start_pos[i] <= end_pos[i] : continue
        start_pos[i], end_pos[i] = end_pos[i], start_pos[i]
    return functools.partial(set_test, s=command, time=time, web_view=web_view, 
        start_pos=tuple(start_pos), end_pos=tuple(end_pos))

def set_test(context:CommandContext, _game:MinecraftSimulator, s:str, 
    time:int, web_view:bool, start_pos:Tuple[int, int, int], end_pos:Tuple[int, int, int]) :
    current_time = 0
    _game.DebugTerminal.__clear_all_feedback__()

    def create_feedback() :
        _game.DebugTerminal.__create_feedback__()

    def test_things() :
        nonlocal current_time
        TestSave = _game.DebugTerminal.__get_feedback__()
        NotImplementedError
        current_time += 1
        if current_time >= time : return "break"

    _game.TickScheduler.unregister_interval(create_feedback, all=True)
    _game.TickScheduler.unregister_interval(test_things, all=True)
    _game.TickScheduler.register_interval(1, create_feedback)
    _game.TickScheduler.register_interval(1, test_things, end_of_tick=True)
    return CommandResult(True, s, f"已设置完成: 测试时间={time}, 反馈网页={web_view}\n测试位置={start_pos}~{end_pos}", [context])


def command_command(_game:MinecraftSimulator, parser_result:ParserResult) :
    token_list = parser_result.tokens
    if token_list[2]["token"] <= 0 : return CompileError("循环时间不能为非正数", 2, 2)
    command_object = _game.CommandManager.compile(token_list[3]["token"], _game.GameVersion)
    if not callable(command_object) : return command_object

    if token_list[1]["token"] == "tick_start_loop" : func = command_loop_start
    if token_list[1]["token"] == "tick_end_loop" : func = command_loop_end
    if token_list[1]["token"] == "tick_start_delay" : func = command_delay_start
    if token_list[1]["token"] == "tick_end_delay" : func = command_delay_end
    return functools.partial(func, s=token_list[3]["token"].strip(), command_obj=command_object)

def command_loop_start(context:CommandContext, _game:MinecraftSimulator, s:str, time:int, command_obj:MCCommandCall) :
    def callback() :
        TestSave = _game.DebugTerminal.__get_feedback__()
        result = command_obj()
        result.output = "[StartTick循环]" + result.output
        TestSave.Commands.append(result)
    _game.TickScheduler.unregister_interval(callback, all=True)
    _game.TickScheduler.register_interval(time, callback)
    return CommandResult(True, s, f"已设置tick开始循环函数: 时间={time}", [context])

def command_loop_end(context:CommandContext, _game:MinecraftSimulator, s:str, time:int, command_obj:MCCommandCall) :
    def callback() :
        TestSave = _game.DebugTerminal.__get_feedback__()
        result = command_obj()
        result.output = "[EndTick循环]" + result.output
        TestSave.Commands.append(result)
    _game.TickScheduler.unregister_interval(callback, all=True)
    _game.TickScheduler.register_interval(time, callback, end_of_tick=True)
    return CommandResult(True, s, f"已设置tick结束循环函数: 时间={time}", [context])

def command_delay_start(context:CommandContext, _game:MinecraftSimulator, s:str, time:int, command_obj:MCCommandCall) :
    def callback() :
        TestSave = _game.DebugTerminal.__get_feedback__()
        result = command_obj()
        result.output = "[StartTick延时]" + result.output
        TestSave.Commands.append(result)
    _game.TickScheduler.unregister_delay(callback, all=True)
    _game.TickScheduler.register_delay(time, callback)
    return CommandResult(True, s, f"已设置tick开始延时函数: 时间={time}", [context])

def command_delay_end(context:CommandContext, _game:MinecraftSimulator, s:str, time:int, command_obj:MCCommandCall) :
    def callback() :
        TestSave = _game.DebugTerminal.__get_feedback__()
        result = command_obj()
        result.output = "[EndTick延时]" + result.output
        TestSave.Commands.append(result)
    _game.TickScheduler.unregister_delay(callback, all=True)
    _game.TickScheduler.register_delay(time, callback, end_of_tick=True)
    return CommandResult(True, s, f"已设置tick开始结束函数: 时间={time}", [context])


