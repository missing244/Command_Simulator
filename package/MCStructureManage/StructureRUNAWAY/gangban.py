import os,array,json,re
from .. import nbt
from ..__private import TypeCheckList
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

class GangBan_V1 :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * List[BLOCK, ..., RANGE, PALETTE]]
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
        #self.error_check()

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


    @classmethod
    def is_this_file(cls, data, data_type:Literal["bytes", "json"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, list) and len(Json1) >= 2 and \
            (isinstance(Json1[-1], dict) and "list" in Json1[-1]) and \
            (isinstance(Json1[-2], dict) and "start" in Json1[-2] and "end" in Json1[-2]) : return True
        return False

class GangBan_V2 :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * List[BLOCK, ..., PALETTE]]
    -----------------------
    * 可用属性 blocks : 方块储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.blocks: List[BLOCK] = TypeCheckList().setChecker(dict)
        self.block_palette: List[str] = TypeCheckList().setChecker(str)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
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

    def get_volume(self) :
        origin_min, origin_max, = [0, 0, 0], [0, 0, 0]

        def pos_iter() :
            for block in self.blocks :
                if "p" in block : yield block["p"]
        for i in range(3) : origin_min[i] = min(j[i] for j in pos_iter())
        for i in range(3) : origin_max[i] = max(j[i] for j in pos_iter())

        return origin_min, origin_max


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[Union[BLOCK, PALETTE]] = json.load(fp=_file)
        
        palette:PALETTE = Json1.pop()

        StructureObject = cls()
        StructureObject.block_palette.extend(palette["list"])
        super(TypeCheckList, StructureObject.blocks).extend(Json1)

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        #self.error_check()

        Json1:List[Union[BLOCK, PALETTE]] = list(self.blocks)
        Json1.append({"list":list(self.block_palette)})

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, data, data_type:Literal["bytes", "json"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, list) and len(Json1) >= 2 and \
            (isinstance(Json1[-1], dict) and "list" in Json1[-1]) and \
            (isinstance(Json1[0], dict) and "p" in Json1[0] and "id" in Json1[0]) : return True
        return False



class INFO1(TypedDict) :
    name: str
    x: int
    y: int
    z: int
    xcha: int
    ycha: int
    zcha: int
    real_task_block: int

class CHUNK(TypedDict) :
    id: int
    grids: Dict[Literal["x","x1","z","z1"], int]
    data: List[Tuple[int,int,int,int,int,Literal["nbt", "nbt2"],str]]

class GangBan_V3 :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * List[Union[INFO1, str, CHUNK]]
    -----------------------
    * 可用属性 chunks : 区块储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.chunks: List[CHUNK] = TypeCheckList().setChecker(dict)
        self.block_palette: Dict[int, str] = {}

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        block_count = 0

        for chunk in self.chunks :
            if not isinstance(chunk.get("id", None), int) : raise Exception("区块数据缺少或存在错误的 id 参数")
            if not isinstance(chunk.get("grids", None), dict) : raise Exception("区块数据缺少或存在错误的 p 参数")
            if not isinstance(chunk["grids"].get("x", None), int) : raise Exception("区块范围缺少或存在错误的 x 数据")
            if not isinstance(chunk["grids"].get("z", None), int) : raise Exception("区块范围缺少或存在错误的 z 数据")
            if not isinstance(chunk["grids"].get("x1", None), int) : raise Exception("区块范围缺少或存在错误的 x1 数据")
            if not isinstance(chunk["grids"].get("z1", None), int) : raise Exception("区块范围缺少或存在错误的 z1 数据")
            if not isinstance(chunk.get("data", None), list) : raise Exception("区块数据缺少或存在错误的 id 参数")
            block_count += len(chunk["data"])
            for block in chunk["data"] :
                pos_str = "(%s, %s)" % (chunk["grids"]['x'], chunk["grids"]['z'])
                if len(block) < 5 : raise Exception(f"方块数据缺少关键参数{pos_str}")
                if any(not isinstance(block[i], int) for i in range(5)) : raise Exception(f"方块数据存在非法参数{pos_str}")
                nbtdata = block[5:]
                if not nbtdata : continue
                if len(nbtdata) < 2 : raise Exception(f"方块nbt数据不完整{pos_str}")
                if nbtdata[0] not in {"nbt", "nbt2"} : raise Exception(f"方块nbt数据存在非法参数{pos_str}")
                if not isinstance(nbtdata[1], str) : raise Exception(f"方块nbt数据存在非法参数{pos_str}")

        return block_count

    def get_volume(self) :
        origin_min, origin_max, = [0, 0, 0], [0, 0, 0]

        def pos_iter() :
            for chunk in self.chunks :
                o_x, o_z = chunk["grids"]["x"], chunk["grids"]["z"]
                for block in chunk["data"] :
                    yield (o_x+block[2], block[3], o_z+block[4])
        for i in range(3) : origin_min[i] = min(j[i] for j in pos_iter())
        for i in range(3) : origin_max[i] = max(j[i] for j in pos_iter())

        return origin_min, origin_max
    

    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[Union[INFO1, str, CHUNK]] = json.load(fp=_file)

        palette:str = Json1[1]
        re1 = re.compile(r"\[(-?[0-9]+)\](.*?)\[(-?[0-9]+)\]")

        StructureObject = cls()
        StructureObject.block_palette.update(
            (int(i.group(1)), i.group(2)) for i in re1.finditer(palette))
        super(TypeCheckList, StructureObject.chunks).extend(Json1[2:])

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        block_count = self.error_check()
        start_pos, end_pos = self.get_volume()

        Json1:List[Union[INFO1, str, CHUNK]] = [
            {"name":"new_v2", "x":0, "y":0, "z":0,
             "xcha":end_pos[0] - start_pos[0] + 1, 
             "zcha":end_pos[1] - start_pos[1] + 1, 
             "ycha":end_pos[2] - start_pos[2] + 1, 
             "real_task_block":block_count},
             "".join(f"[{i}]{j}[{i}]" for i,j in self.block_palette.items()),
             *self.chunks ]

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, data, data_type:Literal["bytes", "json"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, list) and len(Json1) >= 2 and \
            (isinstance(Json1[0], dict) and "name" in Json1[0]) and \
            (isinstance(Json1[1], str)) : return True
        return False



class INFO2(TypedDict) :
    name: str
    xcha: int
    ycha: int
    zcha: int
    real_task_block: int

class GangBan_V4(GangBan_V3) :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * List[Union[INFO2, List[str], CHUNK]]
    -----------------------
    * 可用属性 chunks : 区块储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """

    def __init__(self):
        super().__init__()
        super(GangBan_V3, self).__delattr__("block_palette")
        self.block_palette:List[str] = TypeCheckList().setChecker(str)

    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[Union[INFO2, List[str], CHUNK]] = json.load(fp=_file)

        palette:List[str] = Json1[1]

        StructureObject = cls()
        StructureObject.block_palette.extend(palette)
        super(TypeCheckList, StructureObject.chunks).extend(Json1[2:])

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        block_count = self.error_check()
        start_pos, end_pos = self.get_volume()

        Json1:List[Union[INFO2, List[str], CHUNK]] = [
            {"name":"new_v3", 
             "xcha":end_pos[0] - start_pos[0] + 1, 
             "zcha":end_pos[1] - start_pos[1] + 1, 
             "ycha":end_pos[2] - start_pos[2] + 1, 
             "real_task_block":block_count},
            list(self.block_palette), *self.chunks ]

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, data, data_type:Literal["bytes", "json"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, list) and len(Json1) >= 2 and \
            (isinstance(Json1[0], dict) and "name" in Json1[0]) and \
            (isinstance(Json1[1], list) and Json1[1] and isinstance(Json1[1][0], str)) : return True
        return False



class AREA_SIZE(TypedDict) :
    ep: Tuple[int, int, int]
    
class CONTANIER(TypedDict) :
    ns: str
    aux: int
    num: int
    slot: int

class CB_DATA(TypedDict) :
    auto: bool
    condition: bool
    cmd: str
    name: str
    delay: int

AREA_ENTITY = Tuple[int, int, int, str, str]

AREA_BLOCK = Tuple[int, int, int, int, int, Union[List[CONTANIER], CB_DATA]]

class GangBan_V5 :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * List[Union[AREA_ENTITY, AREA_BLOCK, AREA_SIZE, List[str]]]
    -----------------------
    * 可用属性 size : 结构大小
    * 可用属性 blocks : 方块储存列表
    * 可用属性 entities : 实体储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.size: array.array = array.array("i", [0, 0, 0])
        self.blocks: List[AREA_BLOCK] = TypeCheckList().setChecker(list)
        self.entities: List[AREA_ENTITY] = TypeCheckList().setChecker(list)
        self.block_palette: List[str] = TypeCheckList().setChecker(str)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")

        for entity in self.entities :
            if len(entity) < 5 : raise Exception("实体参数不完整")
            if any(not isinstance(i, (int,float)) for i in entity[0:3]) : raise Exception(f"实体坐标参数存在非法数据")
            if not isinstance(entity[3], str) : raise Exception(f"实体名字参数存在非法数据")
            if not isinstance(entity[4], str) : raise Exception(f"实体id参数存在非法数据")

        for block in self.blocks :
            data_len = len(block)
            if data_len < 5 : raise Exception("方块参数不完整")
            if any(not isinstance(block[i], int) for i in range(5)) : raise Exception("方块数据存在非法参数")
            if data_len > 5 and isinstance(block[5], list) :
                for item in block[5] :
                    if not isinstance(item.get("ns", None), (str, type(None))) : raise Exception(f"物品id参数存在非法数据")
                    if not isinstance(item.get("aux", None), (int, type(None))) : raise Exception(f"物品aux参数存在非法数据")
                    if not isinstance(item.get("num", None), (int, type(None))) : raise Exception(f"物品num参数存在非法数据")
                    if not isinstance(item.get("slot", None), (int, type(None))) : raise Exception(f"物品slot参数存在非法数据")
            if data_len > 5 and isinstance(block[5], dict) :
                if not isinstance(block[5].get("auto", None), bool) : raise Exception(f"命令方块auto参数存在非法数据")
                if not isinstance(block[5].get("condition", None), bool) : raise Exception(f"命令方块condition参数存在非法数据")
                if not isinstance(block[5].get("cmd", None), str) : raise Exception(f"命令方块cmd参数存在非法数据")
                if not isinstance(block[5].get("name", None), str) : raise Exception(f"命令方块name参数存在非法数据")
                if not isinstance(block[5].get("delay", None), int) : raise Exception(f"命令方块delay参数存在非法数据")


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[Union[AREA_ENTITY, AREA_BLOCK, AREA_SIZE, List[str]]] = json.load(fp=_file)

        palette:List[str] = Json1.pop()
        area:AREA_SIZE = Json1.pop()

        StructureObject = cls()
        StructureObject.size = array.array("i", (i+1 for i in area["ep"]))
        StructureObject.block_palette.extend(palette)
        B_APPEND = super(TypeCheckList, StructureObject.blocks).append
        E_APPEND = super(TypeCheckList, StructureObject.entities).append
        for data in Json1 :
            if type(data[3]) is str : E_APPEND(data)
            else : B_APPEND(data)

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        #self.error_check()

        Json1:List[Union[AREA_ENTITY, AREA_BLOCK, AREA_SIZE, PALETTE]] = [
            *self.entities,
            *self.blocks,
            {"ep": [i-1 for i in self.size]},
            list(self.block_palette) ]

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, data, data_type:Literal["bytes", "json"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, list) and len(Json1) >= 3 and \
            isinstance(Json1[0], list) and isinstance(Json1[-1], list) and \
            (isinstance(Json1[-2], dict) and "ep" in Json1[-2]) : return True
        return False

class GangBan_V6 :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * List[Union[AREA_ENTITY, AREA_BLOCK, List[str]]]
    -----------------------
    * 可用属性 blocks : 方块储存列表
    * 可用属性 entities : 实体储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.blocks: List[AREA_BLOCK] = TypeCheckList().setChecker(list)
        self.entities: List[AREA_ENTITY] = TypeCheckList().setChecker(list)
        self.block_palette: List[str] = TypeCheckList().setChecker(str)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        for entity in self.entities :
            if len(entity) < 5 : raise Exception("实体参数不完整")
            if any(not isinstance(i, (int,float)) for i in entity[0:3]) : raise Exception(f"实体坐标参数存在非法数据")
            if not isinstance(entity[3], str) : raise Exception(f"实体名字参数存在非法数据")
            if not isinstance(entity[4], str) : raise Exception(f"实体id参数存在非法数据")

        for block in self.blocks :
            data_len = len(block)
            if data_len < 5 : raise Exception("方块参数不完整")
            if any(not isinstance(block[i], int) for i in range(5)) : raise Exception("方块数据存在非法参数")
            if data_len > 5 and isinstance(block[5], list) :
                for item in block[5] :
                    if not isinstance(item.get("ns", None), (str, type(None))) : raise Exception(f"物品id参数存在非法数据")
                    if not isinstance(item.get("aux", None), (int, type(None))) : raise Exception(f"物品aux参数存在非法数据")
                    if not isinstance(item.get("num", None), (int, type(None))) : raise Exception(f"物品num参数存在非法数据")
                    if not isinstance(item.get("slot", None), (int, type(None))) : raise Exception(f"物品slot参数存在非法数据")
            if data_len > 5 and isinstance(block[5], dict) :
                if not isinstance(block[5].get("auto", None), bool) : raise Exception(f"命令方块auto参数存在非法数据")
                if not isinstance(block[5].get("condition", None), bool) : raise Exception(f"命令方块condition参数存在非法数据")
                if not isinstance(block[5].get("cmd", None), str) : raise Exception(f"命令方块cmd参数存在非法数据")
                if not isinstance(block[5].get("name", None), str) : raise Exception(f"命令方块name参数存在非法数据")
                if not isinstance(block[5].get("delay", None), int) : raise Exception(f"命令方块delay参数存在非法数据")

    def get_volume(self) :
        origin_min, origin_max, = [0, 0, 0], [0, 0, 0]

        def pos_iter() :
            a1 = [0, 0, 0]
            for block in self.blocks :
                a1[0] += block[0]
                a1[1] += block[1]
                a1[2] += block[2]
                yield a1
        for i in range(3) : origin_min[i] = min(j[i] for j in pos_iter())
        for i in range(3) : origin_max[i] = max(j[i] for j in pos_iter())

        return origin_min, origin_max
    

    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[Union[AREA_ENTITY, AREA_BLOCK, List[str]]] = json.load(fp=_file)

        palette:List[str] = Json1.pop()

        StructureObject = cls()
        StructureObject.block_palette.extend(palette)
        B_APPEND = super(TypeCheckList, StructureObject.blocks).append
        E_APPEND = super(TypeCheckList, StructureObject.entities).append
        for data in Json1 :
            if data[3].__class__ is str : E_APPEND(data)
            elif data[0] is None : continue
            else : B_APPEND(data)

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        #self.error_check()

        Json1:List[Union[AREA_ENTITY, AREA_BLOCK, PALETTE]] = [
            *self.entities,
            *self.blocks,
            [None, None, None, None, None],
            list(self.block_palette) ]

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, data, data_type:Literal["bytes", "json"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, list) and len(Json1) >= 2 and isinstance(Json1[-1], list) and \
            (isinstance(Json1[-2], list) and Json1[-2][0] is None) : return True
        return False

class GangBan_V7 :
    """
    由 钢板 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * List[Union[int, List[CONTANIER], CB_DATA, AREA_SIZE, List[str]]]
    -----------------------
    * 可用属性 size : 结构大小
    * 可用属性 blocks : 方块储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.size: array.array = array.array("i", [0, 0, 0])
        self.blocks: List[int, Union[List[CONTANIER], CB_DATA]] = TypeCheckList().setChecker((list, int, dict))
        self.block_palette: List[str] = TypeCheckList().setChecker(str)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")

        for block in self.blocks :
            data_len = len(block)
            if data_len < 5 : raise Exception("方块参数不完整")
            if any(not isinstance(block[i], int) for i in range(5)) : raise Exception("方块数据存在非法参数")
            if data_len > 5 and isinstance(block[5], list) :
                for item in block[5] :
                    if not isinstance(item.get("ns", None), (str, type(None))) : raise Exception(f"物品id参数存在非法数据")
                    if not isinstance(item.get("aux", None), (int, type(None))) : raise Exception(f"物品aux参数存在非法数据")
                    if not isinstance(item.get("num", None), (int, type(None))) : raise Exception(f"物品num参数存在非法数据")
                    if not isinstance(item.get("slot", None), (int, type(None))) : raise Exception(f"物品slot参数存在非法数据")
            if data_len > 5 and isinstance(block[5], dict) :
                if not isinstance(block[5].get("auto", None), bool) : raise Exception(f"命令方块auto参数存在非法数据")
                if not isinstance(block[5].get("condition", None), bool) : raise Exception(f"命令方块condition参数存在非法数据")
                if not isinstance(block[5].get("cmd", None), str) : raise Exception(f"命令方块cmd参数存在非法数据")
                if not isinstance(block[5].get("name", None), str) : raise Exception(f"命令方块name参数存在非法数据")
                if not isinstance(block[5].get("delay", None), int) : raise Exception(f"命令方块delay参数存在非法数据")


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:List[Union[int, List[CONTANIER], CB_DATA, AREA_SIZE, List[str]]] = json.load(fp=_file)

        palette:List[str] = Json1.pop()
        area:AREA_SIZE = Json1.pop()

        StructureObject = cls()
        StructureObject.size = array.array("i", (i+1 for i in area["ep"]))
        StructureObject.block_palette.extend(palette)
        super(TypeCheckList, StructureObject.blocks).extend(Json1)

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        #self.error_check()

        Json1:List[Union[int, List[CONTANIER], CB_DATA, AREA_SIZE, List[str]]] = [
            *self.blocks,
            {"ep": [i-1 for i in self.size]},
            list(self.block_palette) ]

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, data, data_type:Literal["bytes", "json"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, list) and len(Json1) >= 3 and \
            isinstance(Json1[0], int) and isinstance(Json1[-1], list) and \
            (isinstance(Json1[-2], dict) and "ep" in Json1[-2]) : return True
        return False


