import re, itertools
from dataclasses import dataclass
from .. import MCCommandParser, GameClass, CommandClass
from typing import List, Optional, Tuple, Dict, Union, TypedDict, Literal
MinecraftSimulator = GameClass.MinecraftSimulator
CompileError = CommandClass.CompileError
ParserResult = MCCommandParser.ParserResult

class CBProps(TypedDict):
    """命令方块的部署属性"""
    type: Literal["command_block", "chain_command_block", "repeating_command_block",]   # 方块类型
    direction:   Literal[0, 1, 2, 3, 4, 5]                                              # 朝向
    conditional: bool               # 是否有条件
    auto:        bool               # 是否常开
    delay:       int                # 延迟 tick

# ==================== 常量表 ====================
WORLD_OFFSET = (1600, -64, 1600)   # 局部坐标 → 世界坐标的偏移
LOCAL_X_RANGE = (0, 96)
LOCAL_Y_RANGE = (0, 384)
LOCAL_Z_RANGE = (0, 96)

# 方向别名 → 规范值 0-5（与 Minecraft 命令方块朝向一致）
DIRECTION_ALIAS: Dict[str, int] = {
    "y-": 0, "y+": 1,
    "z-": 2, "z+": 3,
    "x-": 4, "x+": 5
}
# 方向 → 下一个方块相对当前方块的位移
DIRECTION_VECTOR: Dict[int, Tuple[int, int, int]] = {
    0: (0, -1, 0), 1: (0, 1, 0),
    2: (0, 0, -1), 3: (0, 0, 1),
    4: (-1, 0, 0), 5: (1, 0, 0),
}

TYPE_KEYWORDS = {
    "循环": "repeating_command_block",
    "连锁": "chain_command_block",
    "脉冲": "command_block",
}
CONDITIONAL_KEYWORDS = {"有条件": True, "无条件": False}
REDSTONE_KEYWORDS    = {"红石": False, "常开": True}   # 红石=需红石激活, 常开=始终开启

DEFAULT_PROPS: CBProps = {
    "type": "repeating_command_block",  # 默认循环
    "direction": 1,                     # 默认方向y+
    "conditional": False,               # 无条件
    "auto": True,                       # 常开
    "delay": 0,                         # 0 tick
}

# ==================== 数据类 ====================
@dataclass
class CB_Command:
    """一条命令方块部署记录（纯数据，可 JSON 序列化）"""
    world_pos: Tuple[int, int, int]      # 全局坐标
    direction: int                        # 0-5
    type: str                             # command_block / chain_command_block / repeating_command_block
    conditional: bool
    auto: bool
    delay: int
    command: str                # None 表示 empty 空白方块

class CBDeployError(Exception) : pass


# ==================== 编译器 ====================
class CBDeployCompiler:
    """
    命令方块部署脚本编译器
    ----------------------------------------------------
    支持语法：
        ① start <x> <y> <z>
        ② [方向,属性] <MC命令>
           <MC命令>                  (沿用上次方向与属性)
        ③ [方向,属性] empty
        ④ #注释
    """
    START_HEAD = re.compile(r"start[ ]{1,}|start$")
    START_RE = re.compile(r"start\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s*$", re.IGNORECASE)
    HEAD_RE  = re.compile(r"\[([^\]]*)\](.*)$")

    def __init__(self, main_thread) :
        from .. import GameClass
        if not isinstance(main_thread, GameClass.MinecraftSimulator) :
            raise TypeError("main_thread 需要传入 MinecraftSimulator 对象")
        self.__main_thread = main_thread
        self.commands: List[CB_Command] = []
        self.open_errors: List[str] = []
        self.errors: Dict[str, List[Tuple[int, int, str, str]]] = {}


    @staticmethod
    def _validate_local(x:int, y:int, z:int) -> None:
        if not (LOCAL_X_RANGE[0] <= x < LOCAL_X_RANGE[1]):
            raise CBDeployError(f"x={x} 超出范围 [{LOCAL_X_RANGE[0]},{LOCAL_X_RANGE[1]}]")
        if not (LOCAL_Y_RANGE[0] <= y < LOCAL_Y_RANGE[1]):
            raise CBDeployError(f"y={y} 超出范围 [{LOCAL_Y_RANGE[0]},{LOCAL_Y_RANGE[1]}]")
        if not (LOCAL_Z_RANGE[0] <= z < LOCAL_Z_RANGE[1]):
            raise CBDeployError(f"z={z} 超出范围 [{LOCAL_Z_RANGE[0]},{LOCAL_Z_RANGE[1]}]")

    @staticmethod
    def _cursor_move(pos: List[int], direction: int) :
        dx, dy, dz = DIRECTION_VECTOR[direction]
        pos[0] += dx
        pos[1] += dy
        pos[2] += dz

    # ---------- 内部：行解析 ----------
    def _parse_line(self, props:CBProps, line:str, start_index:int) :
        # ④ 注释
        if line.startswith("#", start_index): return None

        # ① start
        if self.START_HEAD.match(line, pos=start_index) :
            m = self.START_RE.match(line, pos=start_index)
            if m is None : raise CBDeployError("start 需指定三个整数")
            _pos = list(int(m.group(i)) for i in (1, 2, 3))
            self._validate_local(*_pos)
            props.update(DEFAULT_PROPS)
            return _pos

        # ② / ③ 命令方块
        # 每次布置前校验 cursor（防止移动后越界）
        # 是否带 [方向,属性] 前缀
        head = self.HEAD_RE.match(line, pos=start_index)
        if head: 
            self._parse_head(props, head.group(1))
            command = head.group(2)
        else : command = line

        # 判定命令体
        __test_command = command.strip()
        if __test_command.lower() == "empty": return ""
        elif not __test_command : return None
        else : return command

    def _parse_head(self, props:CBProps, content:str):
        parts = [s.strip() for s in re.split(r"[,;，；]", content) if s.strip()]
        if not parts: raise CBDeployError("命令方块状态定义头不能为空")

        for porperty in parts :
            if porperty in DIRECTION_ALIAS: props["direction"] = DIRECTION_ALIAS[porperty]
            elif porperty in TYPE_KEYWORDS: props["type"] = TYPE_KEYWORDS[porperty]
            elif porperty in CONDITIONAL_KEYWORDS: props["conditional"] = CONDITIONAL_KEYWORDS[porperty]
            elif porperty in REDSTONE_KEYWORDS: props["auto"] = REDSTONE_KEYWORDS[porperty]
            elif re.match(r"^([0-9]{1,})$", porperty) : props["delay"] = int(porperty)
            else : raise CBDeployError(f"命令方块定义状态含有无效属性 '{porperty}'",)

    # ---------- 命令解析钩子（请自行填入） ----------
    def _parser_command(self, command:str):
        result = self.__main_thread.CommandManager.compile(
            command, self.__main_thread.GameVersion)
        if result.__class__ is ParserResult : raise result.error
        elif result.__class__ is CompileError : raise result


    # ---------- 公开接口 ----------
    def compile(self) :
        """解析整个脚本，错误收集在 self.errors"""
        self.commands.clear()
        self.errors.clear()
        _started = False
        _props:CBProps = dict(DEFAULT_PROPS)
        start_pos:List[int] = [0, 0, 0]
        cb_file_path = self.__main_thread.WorldPath / "command_blocks"
        for path in cb_file_path.glob("*.txt") :
            path_str = str(path)
            try : _f = open(path, "r", encoding="utf-8")
            except PermissionError: self.open_errors.append(f"{path_str} 打开失败(权限不足)") ; continue
            except : self.open_errors.append(f"{path_str} 打开失败(编码错误)") ; continue
            texts = _f.read().split("\n")
            _f.close()

            for line_no, raw in enumerate(texts, start=1):
                line = raw.strip()
                if not line: continue
                start_index = next(i for i,j in enumerate(raw) if j != " ")
                head = self.HEAD_RE.match(raw, pos=start_index)
                except_head_index_start = head.start(2) if head else 0

                try: 
                    _m = self._parse_line(_props, raw, start_index)
                    if  _m.__class__ is list : start_pos = _m ; _started = True
                    elif  _m.__class__ is str : 
                        if not _started : raise CBDeployError("命令写入前需定义 start 命令")
                        self._validate_local(*start_pos)
                        world_pos = tuple(i+j for i,j in zip(WORLD_OFFSET, start_pos))

                        cb = CB_Command(world_pos=world_pos,
                            direction=_props["direction"], type=_props["type"],
                            conditional=_props["conditional"], auto=_props["auto"],
                            delay=_props["delay"], command=_m)
                        self._cursor_move(start_pos, _props["direction"])
                        if _m : self._parser_command(_m)
                        self.commands.append(cb)
                except CBDeployError as e: self.errors.setdefault(path_str, []).append((line_no, 0, line, str(e)))
                except SyntaxError as e: self.errors.setdefault(path_str, []).append((line_no, except_head_index_start+e.pos[0], line, str(e)))
                except CompileError as e: 
                    char_start_index = e.parser_result.tokens[e.start_index]["start"]
                    self.errors.setdefault(path_str, []).append((line_no, except_head_index_start+char_start_index, line, str(e)))
                except Exception as e: self.errors.setdefault(path_str, []).append((line_no, 0, line, repr(e)))

    def write_in_world(self) :
        from ..GameClass.block import BlockCommandComponent
        Overworld = self.__main_thread.DimensionManager.get_dimension("overworld")
        Overworld.__reload_CB_chunk__()
        BlockPermutation = self.__main_thread.SimulatorModule.BlockPermutation
        CBBlockPermutations:Dict[str, List] = {}
        for i, j, k in itertools.product(tuple(TYPE_KEYWORDS.values()), (0, 1, 2, 3, 4, 5), (False, True)) :
            CBBlockPermutations.setdefault(i, []).append(BlockPermutation(i, {"facing_direction":j, "conditional_bit":k}))

        for cb in self.commands :
            idx = cb.direction * 2 + cb.conditional
            bp = CBBlockPermutations[cb.type][idx]
            Overworld.set_block_permutation(cb.world_pos, bp)
            block_obj = Overworld.get_block(cb.world_pos)
            _comp:BlockCommandComponent = block_obj.get_component(BlockCommandComponent)
            _comp.Command = cb.command
            _comp.Auto = cb.auto
            _comp.TickDelay = cb.delay


