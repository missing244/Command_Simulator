import os,array,json
from .. import nbt,TypeCheckList
from typing import Union,List,TypedDict,Dict,Tuple,Literal,Optional
from io import FileIO, BytesIO, StringIO, TextIOBase

class CB(TypedDict) :
    mode: Literal["Repeating", "Chain", "Tick"]
    auto: Literal[True, False]
    condition: Literal[True, False]
    cmd: str
    last: Optional[str]
    name: Optional[str]
    tick: Optional[int]
    should: Optional[Literal[True, False]]
    on: Optional[Literal[True, False]]

class BLOCK(TypedDict) :
    id: int
    aux: Optional[int]
    p: Tuple[int, int, int]
    cmds: Optional[CB]

class RANGE(TypedDict) :
    start: Tuple[int, int, int]
    end: Tuple[int, int, int]

class PALETTE(TypedDict) :
    list: List[str]




class GangBan :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    -----------------------
    * 可用属性 size : 结构大小
    * 可用属性 origin : 结构保存起始位置
    * 可用属性 blocks : 方块储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.size: array.array = array.array("i", [0,0,0])
        self.origin: array.array = array.array("i", [0,0,0])
        self.blocks: List[BLOCK] = TypeCheckList().setChecker(dict)
        self.block_palette: List[str] = TypeCheckList().setChecker(str)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")
        if len(self.origin) != 3 : raise Exception("结构保存位置列表长度不为3")
        MODE = {"Repeating", "Chain", "Tick"}

        for block in self.blocks :
            if not isinstance(block.get("id", None), int) : raise Exception("方块数据缺少或存在错误的 id 参数")
            if not isinstance(block.get("p", None), list) : raise Exception("方块数据缺少或存在错误的 p 参数")
            if any(not isinstance(i, int) for i in block["p"]) : raise Exception("方块数据存在错误的坐标数据")
            if not isinstance(block.get("aux", 0), int) : raise Exception("方块数据存在错误的 aux 参数")
            if not isinstance(block.get("cmds", {}), dict) : raise Exception("方块数据存在错误的 cmds 参数")
            if "cmds" in block :
                Checker = block["cmds"]
                if Checker.get("mode", None) not in MODE : raise Exception("命令数据缺少或存在错误的 mode 参数")
                if not isinstance(Checker.get("on", False), bool) : raise Exception("命令数据缺少或存在错误的 on 参数")
                if not isinstance(Checker.get("condition", None), bool) : raise Exception("命令数据缺少或存在错误的 condition 参数")
                if not isinstance(Checker.get("cmd", None), str) : raise Exception("命令数据缺少或存在错误的 cmd 参数")
                if not isinstance(Checker.get("last", ""), str) : raise Exception("命令数据缺少或存在错误的 last 参数")
                if not isinstance(Checker.get("name", ""), str) : raise Exception("命令数据缺少或存在错误的 name 参数")
                if not isinstance(Checker.get("tick", 0), int) : raise Exception("命令数据缺少或存在错误的 tick 参数")
                if not isinstance(Checker.get("should", False), bool) : raise Exception("命令数据缺少或存在错误的 should 参数")
                if not isinstance(Checker.get("auto", False), bool) : raise Exception("命令数据缺少或存在错误的 auto 参数")

                Checker["last"] = Checker.get("last", "")
                Checker["name"] = Checker.get("name", "")
                Checker["tick"] = Checker.get("tick", 0)
                Checker["should"] = Checker.get("should", False)
                Checker["auto"] = Checker.get("auto", False)


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[Union[BLOCK, RANGE, PALETTE]] = json.load(fp=_file)
        
        palette:PALETTE = Json1.pop()
        area_range:RANGE = Json1.pop()

        StructureObject = cls()
        for i in range(3) : StructureObject.size[i] = abs(area_range["end"][i] - area_range["start"][i]) + 1
        for i in range(3) : StructureObject.origin[i] = min(area_range["end"][i], area_range["start"][i])
        StructureObject.block_palette.extend(palette["list"])
        super(TypeCheckList, StructureObject.blocks).extend(Json1)

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        self.error_check()

        Json1:List[Union[BLOCK, RANGE, PALETTE]] = list(self.blocks)
        Json1.append({"start":list(self.origin), "end":list(self.size)})
        for i in range(3) : Json1[-1]["end"][i] += (Json1[-1]["start"][i] - 1)
        Json1.append({"list":list(self.block_palette)})

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))



