from typing import List, Dict, Union, Literal, Tuple, Callable
from .__private import MinecraftSimulator, CommandContext, Entity, ItemStack, CompileError
from .. import MCCommandParser
import re, functools, json, functools
TokenCursor = MCCommandParser.ParserSystem.TokenCursor

selector_tree = MCCommandParser.SpecialMatch.Command_Root().add_leaves(*MCCommandParser.SpecialMatch.BE_Selector_Tree(MCCommandParser.BaseMatch.END_NODE))
Parser = MCCommandParser.ParserSystem.Command_Parser(selector_tree)


def ItemComponent_Applier(item_stack:ItemStack, item_component:dict) -> Callable[[ItemStack], ItemStack]:
    if "minecraft:keep_on_death" in item_component: item_stack.KeepOnDeath = True
    if "minecraft:can_destroy" in item_component:
        item_stack.CanDestroy = [b if ":" in b else f"minecraft:{b}" for b in item_component["minecraft:can_destroy"]["blocks"]]
    if "minecraft:can_place_on" in item_component:
        item_stack.CanPlaceOn = [b if ":" in b else f"minecraft:{b}" for b in item_component["minecraft:can_place_on"]["blocks"]]
    if "minecraft:item_lock" in item_component:
        mode = item_component["minecraft:item_lock"]["mode"]
        item_stack.LockMode = "inventory" if mode == "lock_in_inventory" else "slot"
    return item_stack

def ItemComponent_Compiler(_game:MinecraftSimulator, token_cursor:TokenCursor) :
    start, end, __cache = token_cursor.tell(), 0, []
    while 1 :
        __token = token_cursor.advance()
        __cache.append(str(__token["token"]))
        if __token["type"] == "All_Json_End" : break
    end = token_cursor.tell()
    component_json = json.loads("".join(__cache))

    key_list = {"minecraft:keep_on_death", "minecraft:can_destroy", "minecraft:can_place_on", "minecraft:item_lock"}
    check_key = set(component_json) - key_list
    if check_key : raise CompileError("不存在的物品组件：%s" % ", ".join(check_key), start, end)

    if "minecraft:keep_on_death" in component_json and (not isinstance(component_json["minecraft:keep_on_death"], dict) or 
        component_json["minecraft:keep_on_death"].__len__() > 0) : raise CompileError("keep_on_death 物品组件的值应该为 {}")

    if "minecraft:can_destroy" in component_json and (
        not isinstance(component_json["minecraft:can_destroy"], dict) or 
        component_json["minecraft:can_destroy"].__len__() != 1 or 
        "blocks" not in component_json["minecraft:can_destroy"] or 
        not isinstance(component_json["minecraft:can_destroy"]["blocks"], list)) : 
        raise CompileError('can_destroy 物品组件的值应该为 {"blocks":["air", ...]}', start, end)
    elif "minecraft:can_destroy" in component_json :
        for _block_id in component_json["minecraft:can_destroy"]["blocks"] :
            if not isinstance(_block_id, str) : raise CompileError('can_destroy.blocks内含有非字符串参数', start, end)
            _block_id = _block_id if _block_id.startswith("minecraft:") else f"minecraft:{_block_id}"
            if _block_id not in _game.GameSource.BLOCK : raise CompileError('can_destroy.blocks内含有不存在的方块ID：%s' % _block_id, start, end)

    if "minecraft:can_place_on" in component_json and (
        not isinstance(component_json["minecraft:can_place_on"], dict) or 
        component_json["minecraft:can_place_on"].__len__() != 1 or 
        "blocks" not in component_json["minecraft:can_place_on"] or 
        not isinstance(component_json["minecraft:can_place_on"]["blocks"], list)) : 
        raise CompileError('can_place_on 物品组件的值应该为 {"blocks":["air", ...]}', start, end)
    elif "minecraft:can_place_on" in component_json :
        for _block_id in component_json["minecraft:can_place_on"]["blocks"] :
            if not isinstance(_block_id, str) : raise CompileError('can_place_on.blocks内含有非字符串参数', start, end)
            _block_id = _block_id if _block_id.startswith("minecraft:") else f"minecraft:{_block_id}"
            if _block_id not in _game.GameSource.BLOCK : raise CompileError('can_place_on.blocks内含有不存在的方块ID：%s' % _block_id, start, end)

    if "minecraft:item_lock" in component_json and (
        not isinstance(component_json["minecraft:item_lock"], dict) or 
        component_json["minecraft:item_lock"].__len__() != 1 or 
        "mode" not in component_json["minecraft:item_lock"] or 
        not isinstance(component_json["minecraft:item_lock"]["mode"], str) or 
        component_json["minecraft:item_lock"]["mode"] not in ("lock_in_inventory", "lock_in_slot") ) : 
        raise CompileError('item_lock 物品组件的值应该为 {"mode":"lock_in_inventory" 或 "lock_in_slot"}', start, end)

    return functools.partial(ItemComponent_Applier, item_component=component_json)


def RunTime_Rawtext(context:CommandContext, _game:MinecraftSimulator, rawtext_json:dict):
    text_list = RunTime_Analysis(context, _game, rawtext_json)
    return "".join(text_list)

def RunTime_Analysis(context:CommandContext, _game:MinecraftSimulator, rawtext_json:dict) -> List[str]:
    from ..GameClass.world import ScoreboardIdentity

    text_list: List[str] = []
    scoreboard = _game.MinecraftWorld.Scoreboard  # 根据实际调整

    for text_json in rawtext_json["rawtext"]:

        if "text" in text_json: text_list.append(text_json["text"])

        elif "selector" in text_json:
            entity_list:List[Entity] = text_json["selector"](context, _game)
            if not entity_list : continue
            text_list.append(", ".join(e.__str__() for e in entity_list))
            continue

        elif "scores" in text_json:
            objective_name = text_json["scores"]["objective"]
            name_value = text_json["scores"]["name"]

            objective = scoreboard.get_objective(objective_name)
            if objective is None: continue

            if isinstance(name_value, str):
                scb_id = ScoreboardIdentity(name_value, ScoreboardIdentity.TypeFakePlayer)
                score = objective.get_score(scb_id)
                if score is not None: text_list.append(str(score.value))
                continue
            else:
                entity_list:List[Entity] = name_value(context, _game)
                if not entity_list: continue
                score_parts = []
                for entity in entity_list:
                    identity = entity.ScoreboardIdentity
                    score = objective.get_score(identity)
                    if score is not None: score_parts.append(str(score))
                if score_parts: text_list.append(", ".join(score_parts))
                continue

        elif "translate" in text_json:
            translate_text = text_json["translate"]
            with_data = text_json.get("with")

            rawtext_list = []
            if with_data is not None:
                if isinstance(with_data, dict): rawtext_list = RunTime_Analysis(context, _game, with_data)
                elif isinstance(with_data, list): rawtext_list.extend(with_data)

            # 处理占位符
            # 先处理 %%s 顺序替换（但需注意 %%s 与 %%数字 混用时行为）
            # 再处理 %%数字（如 %1, %2）索引替换
            # 这里简化：按原逻辑用正则依次替换
            # 注意：Minecraft 中 %%s 实际上表示顺序参数，%%d 等可能不同，但这里沿用你的逻辑
            # 建议改进为统一处理

            pointer = 0
            while "%%s" in translate_text:
                if pointer < len(rawtext_list): replace_with = str(rawtext_list[pointer])
                else: replace_with = ""
                pointer += 1
                translate_text = translate_text.replace("%%s", replace_with, 1)

            while True:
                match = re.search(r"%%(\d+)", translate_text)
                if not match: break
                idx = pointer + int(match.group(1)) - 1 
                if idx < len(rawtext_list): replace_with = str(rawtext_list[idx])
                else: replace_with = ""
                translate_text = translate_text[:match.start()] + replace_with + translate_text[match.end():]

            text_list.append(translate_text)            

    return text_list

def Rawtext_Analysis(_game: MinecraftSimulator, rawtext_json:dict, token_range:dict, path:str="root") -> None:
    from .selector import Selector_Compiler

    if "rawtext" not in rawtext_json: raise CompileError(f"{path}: 缺少 'rawtext' 键", **token_range)
    if not isinstance(rawtext_json["rawtext"], list): raise CompileError(f"{path}.rawtext: 需要提供列表", **token_range)

    for index, text_json in enumerate(rawtext_json["rawtext"]):
        current_path = f"{path}.rawtext[{index}]"

        if "text" in text_json:
            if not isinstance(text_json["text"], str):
                raise CompileError(f"{current_path}.text: 需要提供字符串", **token_range)

        elif "selector" in text_json:
            if not isinstance(text_json["selector"], str):
                raise CompileError(f"{current_path}.selector: 需要提供字符串", **token_range)

            parser_result = Parser.parser_v2(text_json["selector"], _game.GameVersion)
            if not parser_result.success : 
                raise CompileError(f"{current_path}.selector: 选择器语法错误: {parser_result.error.args[0]}", **token_range)
            try : entity_func = Selector_Compiler(_game, parser_result.create_cursor())
            except CompileError as e: raise CompileError(f"{current_path}.selector: {e}", **token_range) from e
            text_json["selector"] = entity_func

        elif "scores" in text_json:
            if not isinstance(text_json["scores"], dict):
                raise CompileError(f"{current_path}.scores: 需要提供对象", **token_range)
            if "objective" not in text_json["scores"]:
                raise CompileError(f"{current_path}.scores: 缺少 'objective'", **token_range)
            if "name" not in text_json["scores"]:
                raise CompileError(f"{current_path}.scores: 缺少 'name'", **token_range)
            if not isinstance(text_json["scores"]["objective"], str):
                raise CompileError(f"{current_path}.scores.objective: 需要提供字符串", **token_range)
            if not isinstance(text_json["scores"]["name"], str):
                raise CompileError(f"{current_path}.scores.name: 需要提供字符串", **token_range)

            name_str = text_json["scores"]["name"].strip()
            if name_str and name_str[0] == "@":
                parser_result = Parser.parser_v2(text_json["scores"]["name"], _game.GameVersion)
                if not parser_result.success :
                    raise CompileError(f"{current_path}.scores.name: 选择器语法错误: {parser_result.error.args[0]}", **token_range)
                try : entity_func = Selector_Compiler(_game, parser_result.create_cursor())
                except CompileError as e: raise CompileError(f"{current_path}.selector: {e}", **token_range) from e
                text_json["scores"]["name"] = entity_func

        elif "translate" in text_json:
            if not isinstance(text_json["translate"], str):
                raise CompileError(f"{current_path}.translate: 需要提供字符串", **token_range)

            if "with" in text_json:
                with_data = text_json["with"]
                if isinstance(with_data, dict):
                    Rawtext_Analysis(_game, with_data, token_range, path=current_path+".with")
                elif isinstance(with_data, list) and not all(isinstance(i, str) for i in with_data):
                    raise CompileError(f"{current_path}.with: 列表只能包含字符串", **token_range)
                else: raise CompileError(f"{current_path}.with: 需要提供字符串列表或 rawtext 对象", **token_range)

        else: raise CompileError(f"{current_path}: 元素需要提供有效的组件信息", **token_range)

def Rawtext_Compiler(_game:MinecraftSimulator, token_cursor:TokenCursor):
    start, end, __cache = token_cursor.tell(), 0, []
    while 1 :
        __token = token_cursor.advance()
        __cache.append(str(__token["token"]))
        if __token["type"] == "All_Json_End" : break
    end = token_cursor.tell()
    rawtext_json = json.loads("".join(__cache))
    Rawtext_Analysis(_game, rawtext_json, {"start_index":start, "end_index":end})
    return functools.partial(RunTime_Rawtext, rawtext_json=rawtext_json)


def split_by_selectors(s: str):
    """
    以 Minecraft 选择器为分隔符切分字符串。
    正确处理引号内的方括号和转义字符。
    """
    parts:List[str] = []
    last = 0
    i = 0
    n = len(s)

    while i < n:
        # 找选择器起点：@ + a/e/p/r/s
        if s[i] == '@' and i + 1 < n and s[i + 1] in 'aeprs':
            start = i
            i += 2

            # 若有方括号块，按“引号感知”方式匹配平衡方括号
            if i < n and s[i] == '[':
                depth = 1
                i += 1
                in_quote = None          # 当前引号类型，None 表示不在引号内

                while i < n and depth > 0:
                    c = s[i]

                    if in_quote:
                        # 处于引号内：只看是否遇到结束引号
                        if c == '\\' and i + 1 < n:
                            i += 2        # 跳过转义的字符
                            continue
                        if c == in_quote: in_quote = None
                    else:
                        # 引号外：引号开启、方括号计数
                        if c == '"' or c == "'": in_quote = c
                        elif c == '[': depth += 1
                        elif c == ']': depth -= 1
                    i += 1

            parts.append(s[last:start])
            parts.append(s[start:i])
            last = i
        else: i += 1

    parts.append(s[last:])
    return parts

def RunTime_SelectorMsg(context:CommandContext, _game:MinecraftSimulator, msg:list) -> str :
    msg = msg.copy()
    for i, call in enumerate(msg) :
        if isinstance(call, str) : continue
        entity_list:List[Entity] = call(context, _game)
        if not entity_list : msg[i] = ""
        msg[i] = ", ".join(e.__str__() for e in entity_list)
    return "".join(msg)

def SelectorMsg_Compiler(_game:MinecraftSimulator, token_cursor:TokenCursor) :
    from .selector import Selector_Compiler

    start_index, end_index = token_cursor.tell(), token_cursor.tell()
    __token = token_cursor.advance()
    str_list = split_by_selectors(__token["token"])
    
    for i, msg_string in enumerate(str_list) :
        if not msg_string.startswith("@") : continue
        parser_result = Parser.parser_v2(msg_string, _game.GameVersion)
        if not parser_result.success : 
            raise CompileError(f"选择器语法错误: {parser_result.error.args[0]}", start_index, end_index)
        try : entity_func = Selector_Compiler(_game, parser_result.create_cursor())
        except CompileError as e: raise CompileError(f"selector: {e}", start_index, end_index) from e
        str_list[i] = entity_func

    return functools.partial(RunTime_SelectorMsg, msg=str_list)


