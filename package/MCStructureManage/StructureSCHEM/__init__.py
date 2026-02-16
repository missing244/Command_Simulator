"""
    schematic schem 文件解析模块
    ---------------------------------
    * 可用对象 Schem_V1: 解析schem文件的类
    * 可用对象 Schem_V2: 解析schem文件的类
    * 可用对象 Schem_V3: 解析schem文件的类
    * 可用对象 Schematic: 解析schematic文件的类

    * 可用属性 RuntimeID_to_Block: 数字ID-方块 映射列表
    * 可用属性 Block_to_RuntimeID: 方块-数字ID 映射字典
"""

from .schematic import RuntimeID_to_Block , Block_to_RuntimeID, Schematic
from .schem import Schem_V1, Schem_V2, Schem_V3
