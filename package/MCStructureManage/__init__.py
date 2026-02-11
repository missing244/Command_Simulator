"""
    MC基岩版结构管理模块
    ---------------------------------
    * 可用模块 StructureBDX: 解析bdx文件的模块
    * 可用模块 StructureAXIOM_BP: 解析axiom_bp文件的模块
    * 可用模块 StructureCONSTRUCTION: 解析construction文件的模块
    * 可用模块 StructureBDS: 解析bds文件的模块
    * 可用模块 StructureCOVSTRUCTURE: 解析covstructure文件的模块
    * 可用模块 StructureNEXUS_NP: 解析nexus_np文件的模块
    * 可用模块 StructureNEXUS: 解析nexus文件的模块
    * 可用模块 StructureMCFUNZIP: 生成mcfunzip文件的模块（仅编码）
    * 可用模块 StructureIBIMPORT: 生成ibimport文件的模块（仅编码）
    * 可用模块 StructureMCS: 解析mcstructure文件的模块
    * 可用模块 StructureSCHEM: 解析schem文件的模块
    * 可用模块 StructureSCHEMATIC: 解析schematic文件的模块
    * 可用模块 StructureRUNAWAY: 解析跑路结构文件的模块
    ---------------------------------
    * 可用对象 Block : 方块对象（向低版本支持的方块格式）
    * 可用对象 CommonStructure: 通用结构对象（结构文件需被此对象打开读取）
    ---------------------------------
    * 可用编解码器 Codecs: 通用结构对象from_buffer/save_as方法使用的编码器类
    * 可用编解码器父类 Codecs.CodecsBase: 自定义解/编码器需要继承的父类
    ---------------------------------
    * 可用函数 getStructureType: 分析结构文件使用什么解码器打开（返回None或者解码器类）
    * 可用函数 registerCodecs: 注册一个自定义的编/解码器
"""

from .. import python_nbt as nbt
from .. import MCBELab
from ..Py_module import C_brotli as brotli



from . import StructureBDX, StructureAXIOM_BP, StructureBDS, StructureCONSTRUCTION
from . import StructureCOVSTRUCTURE, StructureIBIMPORT, StructureMCFUNZIP, StructureMCS
from . import StructureNEXUS, StructureNEXUS_NP, StructureSCHEM
from . import StructureRUNAWAY, StructureSCHEMATIC
from .block import Block
from .codec import Codecs, getStructureType, registerCodecs
from .structure import CommonStructure


