"""
    第三方魔改客户端 结构文件解析模块
    ---------------------------------
    * 可用对象 MianYang: 解析 绵阳 开发的json结构文件的类
    * 可用对象 GangBan_V1: 解析 钢板 开发的json结构文件的类
    * 可用对象 GangBan_V2: 解析 钢板 开发的json结构文件的类
    * 可用对象 GangBan_V3: 解析 钢板 开发的json结构文件的类
    * 可用对象 RunAway: 解析 跑路官方 开发的json结构文件的类
    * 可用对象 Kbdx: 解析 跑路官方 开发的kbdx结构文件的类
    * 可用对象 FuHong_V1: 解析 FuHong 开发的json结构文件的类
    * 可用对象 FuHong_V2: 解析 FuHong 开发的json结构文件的类
    * 可用对象 QingXu_V1: 解析 情绪 开发的json结构文件的类
    * 可用对象 TimeBuilder_V1: 解析 Aionos 开发的json结构文件的类
"""

from .mianyang import MianYang_V1, MianYang_V2, MianYang_V3
from .gangban import GangBan_V1, GangBan_V2, GangBan_V3
from .gangban import GangBan_V4, GangBan_V5, GangBan_V6, GangBan_V7
from .classic import RunAway, Kbdx
from .fuhong import FuHong_V1, FuHong_V2, FuHong_V3, FuHong_V4, FuHong_V5
from .qingxu import QingXu_V1
from .timebuild import TimeBuilder_V1
