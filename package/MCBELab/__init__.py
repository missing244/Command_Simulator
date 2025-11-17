"""
    MC基岩版数据模块
    ---------------------------------
    * 可用函数 TransforBlock: 向低版本兼容的(方块+方块状态)数据分析
    * 可用函数 TransforDatavalue: (方块+方块状态)获取数据值
    * 可用函数 JE_Transfor_BE_Block: JE(方块+方块状态)数据分析
    ---------------------------------
    * 可用函数 GetNbtUID: 获取方块对应的NBT数字UID
    * 可用函数 GetNbtID: 获取方块对应的NBT英文ID
    * 可用函数 GenerateBlockEntityNBT: 生成方块对应的NBT
    ---------------------------------
    * 可用函数 GenerateEntity: 生成一个实体
"""


from .. import python_nbt as nbt

from .block import TransforBlock, TransforDatavalue, RunawayTransforBlock, BlockTransforRunaway, JE_Transfor_BE_Block
from .block_entity import GetNbtUID, GetNbtID, GenerateBlockEntityNBT
from .entity import GenerateEntity
from .translate import ItemTranslateData, BlockTranslateData, EntityTranslateData