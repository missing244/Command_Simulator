"""
基岩版存档读取模块
-----------------------
* 可用函数 GetWorldEdtion : 判断世界类型(网易、基岩、非存档)
* 可用函数 GetChunkKey : 根据维度和坐标生成数据库键名
-----------------------
* 可用对象 BedrockWorld : 使用基岩版编码模式读取存档
* 可用对象 NeteaseWorld : 使用网易版编码模式读取存档
"""
from .. import python_nbt as nbt

from .world_object import (
    GetWorldEdtion, 
    BedrockWorld, 
    NeteaseWorld ) 
from .chunk_data import generate_chunk_key as GetChunkKey