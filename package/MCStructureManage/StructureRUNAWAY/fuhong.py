import os,array,json,struct,ast
from .. import nbt
from ..__private import TypeCheckList
from typing import Union,List,TypedDict,Dict,Tuple,Literal,Optional
from io import FileIO, BytesIO, StringIO, TextIOBase

class BLOCK1(TypedDict) :
    name: str
    aux: Optional[int]
    x: Tuple[int]
    y: Tuple[int]
    z: Tuple[int]

class FuHong_V1 :
    """
    由 FuHong 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    ----------------------------------------
    * 可用属性 blocks : 方块储存列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.blocks: List[BLOCK1] = TypeCheckList().setChecker(dict)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def get_volume(self) :
        origin_min, origin_max, = [0, 0, 0], [0, 0, 0]

        def pos_iter() :
            for i in self.blocks : yield (i["x"][0], i["y"][0], i["z"][0])
        for i in range(3) : origin_min[i] = min(j[i] for j in pos_iter())
        for i in range(3) : origin_max[i] = max(j[i] for j in pos_iter())

        return origin_min, origin_max

    def error_check(self) :
        for block in self.blocks :
            if not isinstance(block.get("name", None), str) : raise Exception("方块数据缺少或存在错误的 name 参数")
            if not isinstance(block.get("aux", 0), int) : raise Exception("方块数据存在错误的 aux 参数")
            if not isinstance(block.get("x", None), list) : raise Exception("方块数据存在错误的 x 参数")
            if not isinstance(block.get("y", None), list) : raise Exception("方块数据存在错误的 y 参数")
            if not isinstance(block.get("z", None), list) : raise Exception("方块数据存在错误的 z 参数")
            if not len(block["x"]) or not isinstance(block["x"][0], int) : raise Exception("方块数据存在错误的 x 参数")
            if not len(block["y"]) or not isinstance(block["y"][0], int) : raise Exception("方块数据存在错误的 y 参数")
            if not len(block["z"]) or not isinstance(block["z"][0], int) : raise Exception("方块数据存在错误的 z 参数")
            
            block["aux"] = block.get("aux", 0)


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[BLOCK1] = json.load(fp=_file)

        StructureObject = cls()
        super(TypeCheckList, StructureObject.blocks).extend(Json1)

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        self.error_check()

        Json1:List[BLOCK1] = list(self.blocks)

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))
    
    
    @classmethod
    def is_this_file(cls, bytes_io:BytesIO) :
        try : Json1 = json.load(bytes_io)
        except : return False
        if isinstance(Json1, list) and len(Json1) and isinstance(Json1[0], dict) and \
            "name" in Json1[0] and isinstance(Json1[0].get("x", None), list) : return True
        return False

        

class BUILD_INFO(TypedDict) :
    UserInfo: str
    Export_Mode: str
    PlayerGameMode: str
    PlayerSelfSite: str
    WorldName: str
    WorldSeed: str
    WorldTime: str
    WorldTickSpeed: str
    SiteInfo: str
    ExportSiteInfo: str
    BlockInfo: str
    BlockRange: str
    VersionInfo: str
    ExportTime: str
    ExportEndTime: str
    BlocksQuantity: str

class BLOCK2(TypedDict) :
    n: str
    x: List[int]
    y: List[int]
    z: List[int]
    d: List[Dict[Literal["b", "e"], str]]

class ENTITY2(TypedDict) :
    en: str
    x: List[int]
    y: List[int]
    z: List[int]

class BUILD_FORMAT(TypedDict) :
    startX: int
    startZ: int
    block: List[Union[BLOCK2, ENTITY2]]

class FILEFORMAT_V2(TypedDict) :
    Build_Info: BUILD_INFO
    FuHongBuild_FinalFormat: List[BUILD_FORMAT]

class FuHong_V2 :
    """
    由 FuHong 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    -----------------------
    * 可用属性 size : 结构大小
    * 可用属性 origin : 结构储存起始位置
    * 可用属性 chunks : 方块储存列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.origin: array.array = array.array("i", [0, 0, 0])
        self.size: array.array = array.array("i", [0, 0, 0])
        self.chunks: List[BUILD_FORMAT] = TypeCheckList().setChecker(dict)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")
        if len(self.origin) != 3 : raise Exception("结构保存位置列表长度不为3")

        for chunk in self.chunks :
            if not isinstance(chunk.get("startX", None), int) : raise Exception("方块数据缺少或存在错误的 name 参数")
            if not isinstance(chunk.get("startZ", None), int) : raise Exception("方块数据存在错误的 aux 参数")
            for block in chunk["block"] :
                if not (isinstance(block.get("en", None), str) or isinstance(block.get("n", None), str)) : 
                    raise Exception("方块坐标数据存在非法的 en 或 n 参数")
                if not isinstance(block.get("x", None), list) : raise Exception("方块坐标数据存在非法的 x 参数")
                if not isinstance(block.get("y", None), list) : raise Exception("方块坐标数据存在非法的 y 参数")
                if not isinstance(block.get("z", None), list) : raise Exception("方块坐标数据存在非法的 z 参数")
                if not all(isinstance(i, (int, float)) for i in block.get("x")) : raise Exception("方块坐标数据存在错误的 x 参数")
                if not all(isinstance(i, (int, float)) for i in block.get("y")) : raise Exception("方块坐标数据存在错误的 y 参数")
                if not all(isinstance(i, (int, float)) for i in block.get("z")) : raise Exception("方块坐标数据存在错误的 z 参数")
                if "d" in block :
                    if not isinstance(block.get("d", None), list) : raise Exception("方块坐标数据存在非法的 d 参数")
                    for nbtdata in block.get("d") :
                        if not all( isinstance(i, str) for i in nbtdata.values() ) : raise Exception("方块坐标数据存在错误的 nbt 参数")


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:FILEFORMAT_V2 = json.load(fp=_file)
        size_str = Json1["Build_Info"]["ExportSiteInfo"].replace("计算后的导出范围:", "").split(" > ")
        Start, End = ast.literal_eval(f"({size_str[0]})"), ast.literal_eval(f"({size_str[1]})")

        StructureObject = cls()
        for i in range(3) : StructureObject.origin[i] = Start[i]
        for i in range(3) : StructureObject.size[i] = End[i] - Start[i] + 1
        super(TypeCheckList, StructureObject.chunks).extend(Json1["FuHongBuild_FinalFormat"])

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        import time, random
        self.error_check()

        Json1:FILEFORMAT_V2 = { "Build_Info":{
            "UserInfo":"用户名称:3556824 用户称号:3556824 玩家名称:小莫罒乌云加",
            "Export_Mode":"导出模式:两点导出",
            "PlayerGameMode":"玩家游戏模式:1",
            "PlayerSelfSite":"玩家自身坐标:X:%s Y:%s Z:%s" % tuple(self.origin),
            "WorldName":"世界名称:我的世界",
            "WorldSeed":"世界种子:%s" % random.randint(-2**48, 2**48),
            "WorldTime":"世界时间:%s" % random.randint(1, 2**24),
            "WorldTickSpeed":"世界随机刻速度:1",
            "SiteInfo":"调用导出范围:%s,%s,%s > %s,%s,%s" % (*tuple(self.origin), *tuple(i+j-1 for i,j in zip(self.origin, self.size))),
            "ExportSiteInfo":"计算后的导出范围:%s,%s,%s > %s,%s,%s" % (*tuple(self.origin), *tuple(i+j-1 for i,j in zip(self.origin, self.size))),
            "BlockInfo":"单导出区块长度:16 计算大小:1区块",
            "BlockRange":"区块范围:X:%s-%s Z:%s-%s" % (self.origin[0] // 16, (self.origin[0] + self.size[0] - 1) // 16 + 1,
                self.origin[2] // 16, (self.origin[2] + self.size[2] - 1) // 16 + 1),
            "VersionInfo":"format last update:%s author:FuHong" % time.strftime("%Y-%m-%d", time.localtime()),
            "ExportTime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "ExportEndTime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "BlocksQuantity":"区块数量:%s" % len(self.chunks),
            "Command_Simulator_Generate":True},
            "FuHongBuild_FinalFormat":list(self.chunks) }

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, bytes_io:BytesIO) :
        try : Json1 = json.load(bytes_io)
        except : return False
        if isinstance(Json1, dict) and isinstance(Json1.get("Build_Info", None), dict) and \
            isinstance(Json1.get("FuHongBuild_FinalFormat", None), list) : return True
        return False

