"""
    MC基岩版结构管理模块
    ---------------------------------
    * 可用模块 StructureBDX: 解析bdx文件的模块
    * 可用模块 StructureMCS: 解析mcstructure文件的模块
    * 可用模块 StructureSCHEM: 解析schem文件的模块
    * 可用模块 StructureSCHEMATIC: 解析schematic文件的模块
    * 可用模块 StructureRUNAWAY: 解析跑路结构文件的模块
    ---------------------------------
    * 可用对象 Block : 方块对象（向低版本支持的方块格式）
    * 可用对象 CommonStructure: 通用结构对象（结构文件需被此对象打开读取）
    ---------------------------------
    * 可用编解码器 Codecs: 通用结构对象from_buffer/save_as方法使用的编码器类
    ---------------------------------
    * 可用函数 getStructureType: 分析结构文件属于以上哪个结构类
"""

from .. import python_nbt as nbt



from . import StructureBDX, StructureMCS, StructureSCHEM
from . import StructureRUNAWAY, StructureSCHEMATIC
from .block import Block
from .codec import Codecs
from .structure import CommonStructure, getStructureType


