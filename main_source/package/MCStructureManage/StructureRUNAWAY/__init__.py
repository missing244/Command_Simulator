"""
    跑路 结构文件解析模块
    ---------------------------------
    * 可用对象 MianYang: 解析 绵阳 开发的json结构文件的类
    * 可用对象 GangBan_V1: 解析 钢板 开发的json结构文件的类
    * 可用对象 GangBan_V2: 解析 钢板 开发的json结构文件的类
    * 可用对象 GangBan_V3: 解析 钢板 开发的json结构文件的类
    * 可用对象 RunAway: 解析 跑路官方 开发的json结构文件的类
    * 可用对象 FuHong: 解析 FuHong 开发的json结构文件的类
    * 可用对象 QingXu: 解析 情绪 开发的json结构文件的类
    * 可用函数 getStructureType: 分析json结构文件属于以上哪个结构类
"""

from .mianyang import MianYang
from .gangban import GangBan_V1, GangBan_V2, GangBan_V3
from .classic import RunAway, FuHong, Kbdx
from .qingxu import QingXu

def getStructureType(buffer) :
    import json, io
        
    if isinstance(buffer, str) : _file = open(buffer, "rb")
    elif isinstance(buffer, bytes) : _file = io.BytesIO(buffer)
    else : _file = buffer

    try : Json1 = json.load(fp=_file)
    except : return None

    if isinstance(Json1, dict) and ("chunkedBlocks" in Json1) and \
        ("namespaces" in Json1) : return MianYang
    elif isinstance(Json1, list) and len(Json1) >= 2 and \
        (isinstance(Json1[-1], dict) and "list" in Json1[-1]) and \
        (isinstance(Json1[-2], dict) and "start" in Json1[-2] and "end" in Json1[-2]) : return GangBan_V1
    elif isinstance(Json1, list) and len(Json1) >= 2 and \
        (isinstance(Json1[0], dict) and "name" in Json1[0]) and \
        (isinstance(Json1[1], list) and Json1[1] and isinstance(Json1[1][0], str)) : return GangBan_V2
    elif isinstance(Json1, list) and len(Json1) >= 2 and isinstance(Json1[-1], list) and \
        (isinstance(Json1[-2], dict) and "ep" in Json1[-1]) : return GangBan_V3
    elif isinstance(Json1, list) and len(Json1) and isinstance(Json1[0], dict) and \
        "name" in Json1[0] and isinstance(Json1[0].get("x", None), int) : return RunAway
    elif isinstance(Json1, list) and len(Json1) and isinstance(Json1[0], dict) and \
        "name" in Json1[0] and isinstance(Json1[0].get("x", None), list) : return FuHong
    elif isinstance(Json1, dict) and "totalBlocks" in Json1 and isinstance(Json1.get("0", None), str) : return QingXu
    else : return None