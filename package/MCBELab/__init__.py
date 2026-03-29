"""
    MC基岩版数据模块
    ---------------------------------
    * 可用函数 TransforBlock: 向低版本兼容的(方块+方块状态)转换函数
    * 可用函数 TransforDatavalue: 由(方块+方块状态)计算数据值函数
    * 可用函数 JE_Transfor_BE_Block: JE(方块+方块状态)转换BE(方块+方块状态)函数
    * 可用函数 UpgradeBlock: 低版本兼容的(方块+方块状态)升级函数
    ---------------------------------
    * 可用函数 GetNbtUID: 获取方块对应的NBT数字UID
    * 可用函数 GetNbtID: 获取方块对应的NBT英文ID
    * 可用函数 GenerateBlockEntityNBT: 生成方块对应的NBT
    ---------------------------------
    * 可用函数 GenerateEntity: 生成一个实体
    ---------------------------------
    * 可用常量 AIR_BLOCKS: 空气方块定义
    * 可用函数 ResolveBlockColor: 解析方块颜色
"""


from .. import python_nbt as nbt

from .block import TransforBlock, TransforDatavalue, RunawayTransforBlock, UpgradeBlock
from .block import BlockTransforRunaway, JE_Transfor_BE_Block, RunawayDataValueTransforBlock
from .block_entity import GetNbtUID, GetNbtID, GenerateBlockEntityNBT
from .entity import GenerateEntity
from .translate import ItemTranslateData, BlockTranslateData, EntityTranslateData
from .block_color import AIR_BLOCKS, ResolveBlockColor


