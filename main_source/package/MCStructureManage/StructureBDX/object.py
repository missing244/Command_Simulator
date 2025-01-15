from .. import TypeCheckList
from . import operation as OperationCode
from typing import Union,Literal,List,Callable
import io, brotli, os, traceback, json

from .operation import match_string_bytes,OPERATION_BYTECODES

Operation = Union[OperationCode.CreateConstantString,OperationCode.PlaceBlockWithBlockStates1,
    OperationCode.AddInt16ZValue0,OperationCode.PlaceBlock,OperationCode.AddZValue0,OperationCode.NOP,
    OperationCode.AddInt32ZValue0,OperationCode.PlaceBlockWithBlockStates2,OperationCode.AddXValue,
    OperationCode.SubtractXValue,OperationCode.AddYValue,OperationCode.SubtractYValue,OperationCode.AddZValue,
    OperationCode.SubtractZValue,OperationCode.AddInt16XValue,OperationCode.AddInt32XValue,OperationCode.AddInt16YValue,
    OperationCode.AddInt32YValue,OperationCode.AddInt16ZValue,OperationCode.AddInt32ZValue,OperationCode.SetCommandBlockData,
    OperationCode.PlaceBlockWithCommandBlockData,OperationCode.AddInt8XValue,OperationCode.AddInt8YValue,OperationCode.AddInt8ZValue,
    OperationCode.UseRuntimeIDPool,OperationCode.PlaceRuntimeBlock,OperationCode.placeBlockWithRuntimeId,
    OperationCode.PlaceRuntimeBlockWithCommandBlockData,OperationCode.PlaceRuntimeBlockWithCommandBlockDataAndUint32RuntimeID,
    OperationCode.PlaceCommandBlockWithCommandBlockData,OperationCode.PlaceRuntimeBlockWithChestData,
    OperationCode.PlaceRuntimeBlockWithChestDataAndUint32RuntimeID,OperationCode.AssignDebugData,OperationCode.PlaceBlockWithChestData,
    OperationCode.PlaceBlockWithNBTData,OperationCode.Terminate]
"""
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))
"""
class BXDFileReadError(Exception): pass
class BXDFileDecodeError(Exception): pass


class BDX_File :

    """
    bdx文件解析对象
    ---------------------------------
    * 用于解析或创建新的bdx对象
    * 在 operation.py 内写明了所有支持的操作码
    ---------------------------------
    * 可用属性 author : 作者名，必须为字符串
    * 可用属性 operation_list : 储存操作码的列表
    ---------------------------------
    * 可用方法 filter : 传入回调函数，筛选符合回调函数的操作码和条件
    * 可用方法 get_volume : 返回 bdx结构 方体的两个斜对角点位置
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) -> None :
        from . import Support_OperationCode
        self.author:str = ""
        self.operation_list: List[Operation] = TypeCheckList().setChecker(Support_OperationCode)

    def __setattr__(self, name, value) :
        if name == "author" and isinstance(value, str) : super().__setattr__(name, value)
        elif not hasattr(self, name) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def filter(self, callback:Callable[[Operation],Literal[True,False]]) :
        """
        返回生成器，生成器生成 Tuple[操作码索引位置，操作码对象]
        """
        return ( 
            OPERATION
            for OPERATION in enumerate(self.operation_list) 
            if callback(OPERATION[1])
        )

    def get_volume(self) :
        origin_min, origin_max, current_pos = [0, 0, 0], [0, 0, 0], [0, 0, 0]
        value, pos_index = 0, 0

        for code in self.operation_list :
            oper_code = code.operation_code
            if oper_code in {0x06, 0x0c, 0x18, 0x19, 0x1e, 0x12, 0x13} : value = code.value ; pos_index = 2
            elif oper_code in {0x10, 0x11, 0x16, 0x17, 0x1d} : value = code.value ; pos_index = 1
            elif oper_code in {0x0e, 0x0f, 0x14, 0x15, 0x1c} : value = code.value ; pos_index = 0
            else : continue
            current_pos[pos_index] += value
            if current_pos[pos_index] < origin_min[pos_index] : origin_min[pos_index] = current_pos[pos_index]
            elif current_pos[pos_index] > origin_max[pos_index] : origin_max[pos_index] = current_pos[pos_index]

        return origin_min, origin_max


    @classmethod
    def from_buffer(cls, buffer:Union[str, bytes, io.BytesIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = io.BytesIO(buffer)
        else : _file = buffer

        if _file.read(3) != b'BD@' : raise BXDFileReadError("不是bdx数据文件")
        bdx_code = io.BytesIO(brotli.decompress(_file.read()))
        if bdx_code.read(4) != b'BDX\0' : raise BXDFileReadError("不是bdx数据文件")

        BDX_Object = cls()
        BDX_Object.author = match_string_bytes(bdx_code).decode("utf-8", errors="ignore")
        try :
            MList = BDX_Object.operation_list
            SuperAppend = super(MList.__class__, MList).append
            while 1 : 
                a = bdx_code.read(1)
                if not a or a == b"\x58" : break
                a = int.from_bytes(a, "big", signed=False)
                SuperAppend(OPERATION_BYTECODES[a].from_bytes(bdx_code))
        except Exception as e :
            #print(len(bdx_code.getvalue()),bdx_code.tell(),bdx_code.getvalue()[bdx_code.tell()-1:])
            #traceback.print_exc()
            _file.close()
            raise e

        return BDX_Object

    def save_as(self, buffer:Union[str, io.FileIO, io.BytesIO]) :
        HaveEndTag = len(self.operation_list) == 0 or \
            isinstance(self.operation_list[-1], OperationCode.Terminate)
        Writer1 = io.BytesIO(b"")
        Writer1.write(b'BDX\0')
        Writer1.write(self.author.encode("utf-8"))
        Writer1.write(b'\0')
        
        for i in self.operation_list : Writer1.write(i.to_bytes())
        if not HaveEndTag : Writer1.write(OperationCode.Terminate().to_bytes())

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "wb")
        else : _file = buffer

        _file.write(b"BD@")
        _file.write(brotli.compress(Writer1.getvalue(), quality=6))
        Writer1.close()
        if isinstance(buffer, str) : _file.close()


CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
RunTimeID_117 = json.load(fp=open(os.path.join(CurrentPath, "runtimeIds_117.json"), "r", encoding="utf-8"))







