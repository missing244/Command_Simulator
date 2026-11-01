from dataclasses import dataclass, field
from .. import Constants, np, MCCommandParser
from ..GameClass.entity import Entity, Player
from ..GameClass.block import BlockPermutation
from ..GameClass.item import ItemStack, ItemDurabilityComponent
from ..GameClass.item import ItemEnchantableComponent
from ..GameClass.dimension import Dimension
from ..GameClass import entity as EntityDefine
from ..GameClass.thread import MinecraftSimulator
from typing import Dict, Union, List, Tuple, Literal, Callable, Iterable, Optional
import struct, io, json


# 方块操作记录（CommandResult.affected_blocks）——用"方块调色板下标"描述被改动的方块，
# 下标即 context.dimension.Permutations 中的位置（同一维度内有效）：
#   ("setblock", x, y, z, block_index)
#   ("fill",  x1, y1, z1, x2, y2, z2, block_index, replace_condition_index)
#   ("clone", x1, y1, z1, x2, y2, z2, x3, y3, z3, filter_condition_index)
# 坐标均为方块坐标：(x1,y1,z1)~(x2,y2,z2) 是源区域（fill 里就是填充区域）的两个端点且已排序，
# (x3,y3,z3) 是 clone 的目标起点；
# 末位是该操作涉及的"第二个方块"（fill 的替换条件方块 / clone 的 filter 过滤方块）的调色板下标，
# 该方块不存在、或条件谓词无法唯一确定某个方块时为 None。
BlockOP = Union[Tuple[Literal["setblock"], int, int, int, int],
    Tuple[Literal["fill"], int, int, int, int, int, int, int, Optional[int]],
    Tuple[Literal["clone"], int, int, int, int, int, int, int, int, int, Optional[int]]]

MCCommandCall = Callable[[MinecraftSimulator, "CommandContext"], "CommandResult"]
SelectorCallFunction = Callable[[MinecraftSimulator, "CommandContext"], List[Entity]]
PosCallFunction = Callable[["CommandContext"], Tuple[np.float32, np.float32, np.float32]]
RotationCallFunction = Callable[["CommandContext"], Tuple[np.float32, np.float32]]
BlockConditionCall = Callable[[BlockPermutation], bool]
ItemStackApplierCall = Callable[[ItemStack], ItemStack]
JsonTextCall = Callable[["CommandContext", MinecraftSimulator], str]

@dataclass
class CompileError(Exception):
    """所有命令编译异常的基类"""
    message: str
    start_index: int  # 在扁平 TokenList 中的起始位置
    end_index: int    # 结束位置（用于高亮错误区域）
    parser_result: MCCommandParser.ParserResult = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        base = f"[位置 {self.start_index}-{self.end_index}] {self.message}"
        return base

class CommandContext :
    """
    命令上下文对象（标准类实现）
    CommandContext序列化:
        int64   executor_id       // 执行者 UniqueID，若无则为 0
        int16   dimension         // 0=主世界  1=地狱  2=末地
        float32 pos_x
        float32 pos_y
        float32 pos_z
        float32 ry
        float32 rx
    """
    DIMENSION_ID_MAP = {"overworld": 0, "nether": 1, "the_end": 2}

    def __init__(self, executer: Union[Entity, Literal["Server", "CommandBlock"]], 
        dimension:Dimension, pos:List[float], rotate:List[float]):
        self.executer = executer
        self.dimension = dimension
        self.location = [np.float32(i) for i in pos]
        self.rotation = [np.float32(i) for i in rotate]

    def __repr__(self) -> str:
        return (
            f"CommandContext(executer={self.executer!r}, "
            f"dimension={self.dimension!r}, pos={self.location!r}, "
            f"rotate={self.rotation!r}"
        )


    def with_executor(self, entity:Optional[Entity]) -> 'CommandContext':
        return self.__class__(entity, self.dimension, self.location, self.rotation)

    def with_position(self, pos:List[float]) -> 'CommandContext':
        return self.__class__(self.executer, self.dimension, pos, self.rotation)

    def with_dimension(self, dim:Dimension) -> 'CommandContext':
        scale1 = Constants.DIMENSION_INFO[self.dimension.Identifier]["scale"]
        scale2 = Constants.DIMENSION_INFO[dim.Identifier]["scale"]
        location = self.location.copy()
        location[0] = location[0] * (scale1 / scale2)
        location[2] = location[2] * (scale1 / scale2)
        return self.__class__(self.executer, dim, location, self.rotation)

    def with_rotation(self, rot:List[float]) -> 'CommandContext':
        return self.__class__(self.executer, self.dimension, self.location, rot)


    def serialize(self) -> bytes:
        """序列化为紧凑二进制格式（小端序）"""
        if isinstance(self.executer, Entity) : executor_id = self.executer.UniqueID
        elif self.executer == "Server" : executor_id = int.from_bytes("\xff\xff\xff\xff\xff\xff\xff\xf0")
        elif self.executer == "CommandBlock" : executor_id = int.from_bytes("\xff\xff\xff\xff\xff\xff\xff\xf1")
        dim_name = self.dimension.Identifier
        dim_id = self.DIMENSION_ID_MAP.get(dim_name, 0)
        pos = [i.value for i in self.location]
        rot = [i.value for i in self.rotation]

        #打包：< 小端，q=int64, h=int16, f=float32
        return struct.pack(
            "<qhfffff",
            executor_id,
            dim_id,
            pos[0], pos[1], pos[2],
            rot[0], rot[1])

@dataclass
class CommandResult :
    """
    CommandResult序列化（字段顺序即 serialize() 的写出顺序，affected_blocks 写在最后）:
        bool    success
        string  command
        string  output
        array   context_history      // 元素为 CommandContext
        array   affected_entities    // 元素为 Entity.serialization_dict() 的 JSON
        array   child_results        // 元素为 CommandResult（递归）
        json    affected_blocks      // 单个方块操作记录 BlockOP，无方块改动时为 null
    """

    success: bool
    command: str
    output: str
    context_history: List[CommandContext]
    affected_blocks: BlockOP = None
    affected_entities: List[dict] = ()
    child_results: List["CommandResult"] = ()

    def set_affected_entities(self, iterable:Iterable[Entity]) :
        self.affected_entities = [_entity.serialization_dict() for _entity in iterable]
        return self

    def set_affected_blocks(self, block_op:Optional[BlockOP]) :
        """记录本次命令改动的方块：传入一个 BlockOP 元组，None 表示没有方块改动"""
        self.affected_blocks = None if block_op is None else tuple(block_op)
        return self

    @staticmethod
    def write_string(buf:io.BytesIO, s:str):
        data = s.encode('utf-8')
        str_len = len(data).to_bytes(4, "little", signed=False)
        buf.write(str_len)
        buf.write(data)

    def serialize(self) -> bytes :
        buf = io.BytesIO()

        buf.write(self.success.to_bytes(1, "little", signed=False))   # success (byte)
        self.write_string(buf, self.command)                          # command (string)
        self.write_string(buf, self.output)                           # output (string)

        # context_history (array of CommandContext)
        data_len = len(self.context_history).to_bytes(2, "little", signed=False)
        buf.write(data_len)
        for ctx in self.context_history: buf.write(ctx.serialize())

        # affected_entities (array of int64)
        data_len = len(self.affected_entities).to_bytes(4, "little", signed=False)
        buf.write(data_len)
        for _entity in self.affected_entities:
            _entity_bytes = json.dumps(_entity, separators=(',', ':')).encode("utf-8")
            data_len = len(_entity_bytes).to_bytes(4, "little", signed=False)
            buf.write(data_len)
            buf.write(_entity_bytes)

        # child_results (array of CommandResult)
        data_len = len(self.child_results).to_bytes(4, "little", signed=False)
        buf.write(data_len)
        for child in self.child_results:
            child_bytes = child.serialize()
            data_len = len(child_bytes).to_bytes(4, "little", signed=False)
            buf.write(data_len)
            buf.write(child_bytes)

        # affected_blocks (单个方块操作记录 BlockOP，JSON；无方块改动时是 "null")
        # 放在 child_results 之后，是为了让"只解析到 child_results 就结束"的旧解析器仍能工作
        block_bytes = json.dumps(
            None if self.affected_blocks is None else list(self.affected_blocks),
            separators=(',', ':')).encode("utf-8")
        buf.write(len(block_bytes).to_bytes(4, "little", signed=False))
        buf.write(block_bytes)

        return buf.getvalue()

@dataclass
class CommandRuntimeError(Exception):
    """所有命令编译异常的基类"""
    message: str

    def __str__(self) -> str:
        base = f"{self.__class__.__name__}({self.message})"
        return base

def Quotation_String_Transfor(s: str) -> str:
    """
    去掉首尾双引号，并按指定规则处理转义
    """
    if len(s) < 2 or s[0] != '"' or s[-1] != '"':
        return s

    inner = s[1:-1]
    result = []
    i = 0
    while i < len(inner):
        ch = inner[i]
        if ch == '\\' and i + 1 < len(inner):
            nxt = inner[i + 1]
            if nxt == '\\': result.append('\\')
            elif nxt == '"': result.append('"')
            elif nxt == 'n': result.append('n')
            elif nxt == 'r': result.append('r')
            elif nxt == 't': result.append('t')
            else:
                result.append('\\')
                result.append(nxt)
            i += 2
        else:
            result.append(ch)
            i += 1

    return ''.join(result)








