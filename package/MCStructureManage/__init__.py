"""
    MC基岩版结构管理模块
    ---------------------------------
    * 可用模块 StructureBDX: 解析bdx文件的模块
    * 可用模块 StructureMCS: 解析mcstructure文件的模块
    * 可用模块 StructureSCHEMATIC: 解析schematic文件的模块
    * 可用模块 StructureRUNAWAY: 解析跑路结构文件的模块
    ---------------------------------
    * 可用对象 Block : 方块对象（向低版本支持的方块格式）
    * 可用对象 CommonStructure: 通用结构对象
    ---------------------------------
    * 可用编解码器 Codecs: 通用结构对象from_buffer/save_as方法使用的编码器类
    ---------------------------------
    * 可用函数 getStructureType: 分析结构文件属于以上哪个结构类
"""

from .. import python_nbt as nbt


def getStructureType(IO_Byte_Path) :
    import io, traceback, json
    from typing import Union
    from . import StructureBDX, StructureMCS, StructureSCHEM
    from . import StructureRUNAWAY, StructureSCHEMATIC
    IO_Byte_Path: Union[str, bytes, io.IOBase]

    if isinstance(IO_Byte_Path, str) : _file = open(IO_Byte_Path, "rb")
    elif isinstance(IO_Byte_Path, bytes) : _file = io.BytesIO(IO_Byte_Path)
    elif isinstance(IO_Byte_Path, io.IOBase) : _file = IO_Byte_Path
    else : raise ValueError(f"{IO_Byte_Path} is not Readable Object")

    data, data_type = _file, "bytes"
    try : data = json.load(fp=_file)
    except : _file.seek(0)
    else : data_type = "json"

    Test = [StructureBDX.BDX_File, StructureMCS.Mcstructure, StructureSCHEMATIC.Schematic, 
            StructureSCHEM.Schem, StructureRUNAWAY.RunAway, StructureRUNAWAY.Kbdx, 
            StructureRUNAWAY.MianYang_V1, StructureRUNAWAY.MianYang_V2, StructureRUNAWAY.MianYang_V3, 
            StructureRUNAWAY.GangBan_V1, StructureRUNAWAY.GangBan_V2, StructureRUNAWAY.GangBan_V3,
            StructureRUNAWAY.GangBan_V4, StructureRUNAWAY.GangBan_V5, StructureRUNAWAY.GangBan_V6,
            StructureRUNAWAY.GangBan_V7,
            StructureRUNAWAY.FuHong_V1, StructureRUNAWAY.FuHong_V2, StructureRUNAWAY.FuHong_V3,
            StructureRUNAWAY.FuHong_V4, StructureRUNAWAY.FuHong_V5, 
            StructureRUNAWAY.QingXu_V1]

    for class_obj in Test :
        if data_type == "bytes" : data.seek(0)
        try : bool1 = class_obj.is_this_file(data, data_type)
        except : traceback.print_exc() ; continue

        if bool1 : 
            if isinstance(IO_Byte_Path, io.IOBase) : IO_Byte_Path.seek(0)
            return class_obj
    if isinstance(IO_Byte_Path, io.IOBase) : IO_Byte_Path.seek(0)


from . import StructureBDX, StructureMCS, StructureSCHEM
from . import StructureRUNAWAY, StructureSCHEMATIC
from .block import Block
from .codec import Codecs
from .structure import CommonStructure


