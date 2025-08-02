"""
# 基岩版存档读取模块
* 可用模块**BaseType**: 物品，实体，方块，区块的基类实现模块
-----------------------
* 可用对象**World**: 基岩版存档对象
-----------------------
* 可用函数**GetWorldEdtion**: 判断存档类型(网易、基岩、非存档)
* 可用函数**GetWorldEncryptKey**: 获取存档加密密钥
"""
from .. import python_nbt as nbt
from . import BaseType
from .world import World, GetWorldEdtion, GetWorldEncryptKey