from typing import Dict, Union, List, Tuple, Literal, Callable
import re, functools, traceback, json, itertools
from .__private import CommandContext, BlockPermutation, Quotation_String_Transfor
from .__private import MinecraftSimulator, BlockConditionCall, CompileError
from .. import MathFunction, MCCommandParser, MCBELab
TokenCursor = MCCommandParser.ParserSystem.TokenCursor
Vector3 = MathFunction.Vector3
Matrix4x4 = MathFunction.Matrix4x4
SpecialStates = {"direction":{"south":0, "west":1, "north":2, "east":3}, 
    "facing_direction":{"south":0, "west":1, "north":2, "east":5},
    "top_slot_bit":{"top":True, "bottom":False}}


def calc_local(context: CommandContext, offsets:List[float]) -> Vector3:
    pos = Vector3(*context.location)  # 假设 context.location 可迭代
    yaw, pitch = context.rotation[0], context.rotation[1]
    # 创建旋转矩阵（基向量：右、上、前）
    rot_matrix = Matrix4x4.from_minecraft_rotation(yaw, pitch)
    # 局部偏移向量：左(offsets[0])、上(offsets[1])、前(offsets[2])
    local_offset = Vector3(offsets[0], offsets[1], offsets[2])
    world_offset = rot_matrix.transform_vector(local_offset)
    return pos + world_offset

def calc_abs_rel(context: CommandContext, components:Tuple[bool, float]) -> Vector3:
    pos = Vector3(*context.location)
    result = []
    for i, (is_rel, val) in enumerate(components):
        if is_rel: result.append(pos[i] + val)
        else: result.append(val)
    return Vector3(result[0], result[1], result[2])

def Pos_Compiler(token_cursor: TokenCursor) -> Callable[[CommandContext], Vector3]:
    """
    编译坐标参数，返回一个函数：
    输入：CommandContext
    输出：Vector3 世界坐标
    """
    first_token = token_cursor.peek()

    # 判断是否为本地坐标（^ 开头）
    if first_token["type"] == "Local_Pos":
        offsets = []
        for _ in range(3):
            tok = token_cursor.advance()
            raw = tok["token"]
            offset = float(raw[1:]) if len(raw) > 1 else 0.0
            offsets.append(offset)
        return functools.partial(calc_local, offsets=offsets)

    else:
        components = []  # 每个元素为 (is_relative, value)
        for _ in range(3):
            tok = token_cursor.advance()
            ttype = tok["type"]
            if ttype == "Absolute_Pos":
                number = tok["token"]
                if len(components) != 1 and isinstance(number, int) : number += 0.5
                components.append((False, number))
            elif ttype == "Relative_Pos":
                raw = tok["token"]
                offset = float(raw[1:]) if len(raw) > 1 else 0.0
                components.append((True, offset))

        return functools.partial(calc_abs_rel, components=components)



def calc_rotation(context:CommandContext, components:Tuple[bool, float]) -> List[float]:
    current_yaw, current_pitch = context.rotation[0], context.rotation[1]
    result = []
    for i, (is_rel, val) in enumerate(components):
        if is_rel:
            base = current_yaw if i == 0 else current_pitch
            result.append(base + val)
        else: result.append(val)
    return result

def Rotation_Compiler(token_cursor:TokenCursor) -> Callable[[CommandContext], List[float]]:
    """
    编译旋转参数（yaw, pitch），返回计算函数。
    输入：CommandContext, MinecraftSimulator
    输出：[yaw, pitch]（单位：度）
    """
    components = []  # 每个元素为 (is_relative, value)
    for _ in range(2):
        tok = token_cursor.advance()

        ttype = tok["type"]
        if ttype == "Absolute_Rotation": components.append((False, float(tok["token"])))
        elif ttype == "Relative_Rotation":
            raw = tok["token"]
            offset = float(raw[1:]) if len(raw) > 1 else 0.0
            components.append((True, offset))

    return functools.partial(calc_rotation, components=components)



def _block_state_def(block_id:str) -> Tuple[str, dict] :
    """
    取方块的状态定义（{"default":…, "support_value":…}，即 MCBELab 的 blockstate.json 条目）。
    先按传入的 id 直接查表；查不到就调用 MCBELab.TransforBlock 把 id 规范化
    （补命名空间、旧 id 别名转换）后再查一次；两次都查不到时返回 (id, None)，此时不做状态核验。
    """
    BlockState = MCBELab.block.BlockState
    state_def = BlockState.get(block_id, {}).get("support_value", {})
    if not state_def :
        block_id = MCBELab.TransforBlock(block_id)[0]
        state_def = BlockState.get(block_id, {}).get("support_value", {})
    return block_id, state_def

def _parse_block_states(token_cursor:TokenCursor, block_id:str) -> Dict[str, Union[str, bool, int]]:
    states = {}
    block_id, support_value = _block_state_def(block_id)

    while True:
        key_token = token_cursor.matches("BlockState")  # 假设 key 类型为 BlockState
        if not key_token: break
        key = Quotation_String_Transfor(key_token["token"])
        if key != "minecraft:cardinal_direction" and key != "minecraft:vertical_half" and \
            key not in support_value : raise CompileError("方块 %s 不存在方块状态 %s" % (block_id, key), 
            token_cursor.tell()-1, token_cursor.tell()-1)

        token_cursor.matches("Equal")
        val_token = token_cursor.advance()
        raw_val = val_token["token"]
        if val_token["type"] == "Bool": val = (raw_val == "true")
        elif val_token["type"] == "Int": val = int(raw_val)
        else: val = Quotation_String_Transfor(raw_val)

        # minecraft:cardinal_direction / minecraft:vertical_half 是新式写法：
        # 只有方块自身没有这个状态时才按旧版朝向 / 上下半砖状态换算后核验取值，
        # 若方块本身就以同名状态存在（例如 vault），则走下面的常规核验。
        if key == "minecraft:cardinal_direction" and key not in support_value :
            if "facing_direction" in support_value and SpecialStates["facing_direction"].get(val) not in support_value["facing_direction"] :
                raise CompileError("方块 %s 的方块状态 %s 不支持取值 %s" % (block_id, key, val), token_cursor.tell()-1, token_cursor.tell()-1)
            elif "direction" in support_value and SpecialStates["direction"].get(val) not in support_value["direction"] :
                raise CompileError("方块 %s 的方块状态 %s 不支持取值 %s" % (block_id, key, val), token_cursor.tell()-1, token_cursor.tell()-1)
            else : raise CompileError("方块 %s 不存在方块状态 %s" % (block_id, key), token_cursor.tell()-1, token_cursor.tell()-1)
        elif key == "minecraft:vertical_half" and key not in support_value :
            if "top_slot_bit" in support_value and SpecialStates["top_slot_bit"].get(val) not in support_value["top_slot_bit"] :
                raise CompileError("方块 %s 的方块状态 %s 不支持取值 %s" % (block_id, key, val), token_cursor.tell()-1, token_cursor.tell()-1)
            else : raise CompileError("方块 %s 不存在方块状态 %s" % (block_id, key), token_cursor.tell()-1, token_cursor.tell()-1)
        elif val not in support_value.get(key, ()) : raise CompileError("方块 %s 的方块状态 %s 不支持取值 %s" % (
                block_id, key, val), token_cursor.tell()-1, token_cursor.tell()-1)

        states[key] = val
        if token_cursor.matches("Next_BlockState_Argument"): continue
        elif token_cursor.matches("End_BlockState_Argument"): break

    return states

def Block_Compiler(_game:MinecraftSimulator, token_cursor:TokenCursor, block_id:str) -> Callable[[], BlockPermutation]:
    token_cursor.advance()

    next_tok = token_cursor.peek()
    if next_tok and next_tok["type"] == "Start_BlockState_Argument":
        token_cursor.advance()
        states = _parse_block_states(token_cursor, block_id)
    elif next_tok and next_tok["type"] == "Block_Data":
        data_tok = token_cursor.advance()
        states = int(data_tok["token"])
    else : states = {}

    return _game.SimulatorModule.BlockPermutation(block_id, states)

def Condition_Block_Compiler(_game:MinecraftSimulator, token_cursor: TokenCursor, block_id:str) -> BlockConditionCall :
    token_cursor.advance()
    BlockPermutation = _game.SimulatorModule.BlockPermutation

    next_tok = token_cursor.peek()
    if next_tok and next_tok["type"] == "Start_BlockState_Argument": 
        token_cursor.advance()
        states = _parse_block_states(token_cursor, block_id)
        print(states)
        _block = BlockPermutation(block_id, states)
        testblockID = _block.name
        testblockStates = _block.states
    elif next_tok and next_tok["type"] == "Block_Data":
        data_tok = token_cursor.advance()
        data_value = int(data_tok["token"])
        if data_value >= 0 : 
            _block = BlockPermutation(block_id, data_value)
            testblockID = _block.name
            testblockStates = _block.states
        else :
            _block = BlockPermutation(block_id)
            testblockID = _block.name
            testblockStates = {}
    else : 
        _block = BlockPermutation(block_id)
        testblockID = _block.name
        testblockStates = {}

    # 返回测试函数
    def test_block(permutation:"BlockPermutation") -> bool:
        if permutation.name != testblockID: return False
        if testblockStates :
            for k, v in testblockStates.items():
                if permutation.states.get(k) != v: return False
        return True

    return test_block


