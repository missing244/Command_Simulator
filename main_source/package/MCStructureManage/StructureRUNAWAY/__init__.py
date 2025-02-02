"""
    跑路 结构文件解析模块
    ---------------------------------
    * 可用对象 MianYang: 解析 绵阳 开发的json结构文件的类
    * 可用对象 GangBan: 解析 钢板 开发的json结构文件的类
    * 可用对象 RunAway: 解析 跑路官方 开发的json结构文件的类
    * 可用函数 getStructureType: 分析json结构文件属于哪个结构类
"""

from .mianyang import MianYang
from .gangban import GangBan
from .classic import RunAway

def getStructureType(buffer) :
    import json, io
        
    if isinstance(buffer, str) : _file = open(buffer, "rb")
    elif isinstance(buffer, bytes) : _file = io.BytesIO(buffer)
    else : _file = buffer

    Json1 = json.load(fp=_file)
    if isinstance(Json1, dict) and ("chunkedBlocks" in Json1) and \
        ("namespaces" in Json1) : return MianYang
    elif isinstance(Json1, list) and len(Json1) > 1 and \
        (isinstance(Json1[-1], dict) and "list" in Json1[-1]) and \
        (isinstance(Json1[-2], dict) and "start" in Json1[-2] and "end" in Json1[-2]) : return GangBan
    elif isinstance(Json1, list) and len(Json1) and isinstance(Json1[0], dict) and \
        "name" in Json1[0] : return RunAway
    else : return None