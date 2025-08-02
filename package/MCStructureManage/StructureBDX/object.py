from ..__private import TypeCheckList
from . import operation as OperationCode
from .. import C_brotli as brotli
from typing import Union,Literal,List,Callable,Generator,Tuple
import io, os, traceback, json

from .operation import match_string_bytes,OPERATION_BYTECODES

Operation = Union[OperationCode.CreateConstantString,OperationCode.PlaceBlockWithBlockStates1,
    OperationCode.AddInt16ZValue0,OperationCode.PlaceBlock,OperationCode.AddZValue0,OperationCode.NOP,
    OperationCode.AddInt32ZValue0,OperationCode.PlaceBlockWithBlockStates2,OperationCode.AddXValue,
    OperationCode.SubtractXValue,OperationCode.AddYValue,OperationCode.SubtractYValue,OperationCode.AddZValue,
    OperationCode.SubtractZValue,OperationCode.AddInt16XValue,OperationCode.AddInt32XValue,OperationCode.AddInt16YValue,
    OperationCode.AddInt32YValue,OperationCode.AddInt16ZValue,OperationCode.AddInt32ZValue,OperationCode.SetCommandBlockData,
    OperationCode.PlaceBlockWithCommandBlockData,OperationCode.AddInt8XValue,OperationCode.AddInt8YValue,OperationCode.AddInt8ZValue,
    OperationCode.UseRuntimeIDPool,OperationCode.PlaceRuntimeBlock,OperationCode.PlaceBlockWithRuntimeId,
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
    * 可用属性 const_str : 储存使用的常量字符串列表
    * 可用属性 operation_list : 储存操作码的列表
    ---------------------------------
    * 可用方法 filter : 传入回调函数，筛选符合回调函数的操作码和条件
    * 可用方法 get_volume : 返回 bdx结构 方体的两个斜对角点位置
    * 可用方法 get_blocks : 返回 bdx结构 中所有修改或放置方块的操作码的生成器
    ---------------------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) -> None :
        from . import Support_OperationCode
        self.author:str = ""
        self.const_str: List[str] = []
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
        Oper = {0x06:2, 0x0c:2, 0x18:2, 0x19:2, 0x1e:2, 0x12:2, 0x13:2, 0x10:1, 0x11:1, 0x16:1, 0x17:1, 0x1d:1,
            0x0e:0, 0x0f:0, 0x14:0, 0x15:0, 0x1c:0}
        pos_index = 0

        for code in self.operation_list :
            if code.operation_code not in Oper : continue
            pos_index = Oper[code.operation_code]
            current_pos[pos_index] += code.value
            if current_pos[pos_index] < origin_min[pos_index] : origin_min[pos_index] = current_pos[pos_index]
            elif current_pos[pos_index] > origin_max[pos_index] : origin_max[pos_index] = current_pos[pos_index]

        return origin_min, origin_max

    def get_blocks(self) -> Generator[Tuple[int, int, int, Operation], None, None] :
        from . import PosX_Change_OperationCode, PosY_Change_OperationCode, PosZ_Change_OperationCode
        
        PosXChange = set(PosX_Change_OperationCode)
        PosYChange = set(PosY_Change_OperationCode)
        PosZChange = set(PosZ_Change_OperationCode)
        PosX, PosY, PosZ = 0, 0, 0
        PlaceBlockCode = {0x05, 0x07, 0x0d, 0x1a, 0x1b, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x28, 0x29}

        for Oper in self.operation_list :
            OperClass = Oper.__class__
            if OperClass in PosXChange : PosX += Oper.value ; continue
            elif OperClass in PosYChange : PosY += Oper.value ; continue
            elif OperClass in PosZChange : PosZ += Oper.value ; continue

            if Oper.operation_code not in PlaceBlockCode : continue
            yield (PosX, PosY, PosZ, Oper)


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
        MList = BDX_Object.operation_list
        SuperAppend = super(MList.__class__, MList).append
        try :
            while 1 : 
                a = bdx_code.read(1)
                if not a or a == b"\x58" : break
                b = OPERATION_BYTECODES[a].from_bytes(bdx_code)
                BDX_Object.const_str.append(b.string) if a == b"\x01" else SuperAppend(b)
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
        
        for i in self.const_str : Writer1.write(OperationCode.CreateConstantString(i).to_bytes())
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

    
    @classmethod
    def is_this_file(cls, data, data_type:Literal["nbt", "json", "bytes"]) :
        if data_type != "bytes" : return False

        if data.read(3) != b'BD@' : return False
        try : a = brotli.decompress(data.read())[0:4]
        except : return False

        if a != b'BDX\0' : return False
        else : return True


CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
RunTimeID_117 = json.load(fp=open(os.path.join(CurrentPath, "runtimeIds_117.json"), "r", encoding="utf-8"))







