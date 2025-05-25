"""
基岩版存档读取模块
-----------------------
* 可用函数 GetWorldEdtion : 判断存档类型(网易、基岩、非存档)
* 可用函数 GetWorldEncryptKey : 获取存档加密密钥
* 可用函数 GetChunkKey : 根据维度和坐标生成数据库键名
-----------------------
* 可用对象 World : 基岩版存档对象
"""
from .. import python_nbt as nbt
from .functions import GetWorldEdtion, GetWorldEncryptKey
from .world import World