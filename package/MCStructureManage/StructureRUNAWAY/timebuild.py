import os,itertools,json
from .. import nbt
from ..__private import TypeCheckList
from typing import Union,List,TypedDict,Literal,Dict
from io import FileIO, BytesIO, StringIO, TextIOBase

class FormatError(Exception) : pass

class FileFormat(TypedDict) :
    version: str
    block: List["BLOCK"]

class BLOCK(TypedDict) :
    name: str
    aux: int
    pos: List[int]



class TimeBuilder_V1 :
    """
    由 Aionos 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * 格式：{"version": "TimeBuilder", "block": [  
    * {"name": "mycelium", "aux": 0, "pos": [ [0,0,33] ] }]}
    ----------------------------------------
    * 可用属性 blocks : 方块储存列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """
    

    def __init__(self) :
        self.blocks: List["BLOCK"] = TypeCheckList().setChecker(dict)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        for block in self.blocks :
            if not isinstance(block, dict) : raise Exception("方块数据不为dict参数")
            if not isinstance(block.get("name", None), str) : raise Exception("方块数据缺少或存在错误 name 参数")
            if not isinstance(block.get("aux", None), int) : raise Exception("方块数据缺少或存在错误 aux 参数")
            if not isinstance(block.get("pos", None), list) : raise Exception("方块数据缺少或存在错误 pos 参数")
            for pos in block.get("pos", None) :
                if len(pos) < 3 : raise Exception("方块坐标数据数量不足")
                if not isinstance(pos[0], int) : raise Exception("方块数据缺少或存在错误 x 参数")
                if not isinstance(pos[1], int) : raise Exception("方块数据缺少或存在错误 y 参数")
                if not isinstance(pos[2], int) : raise Exception("方块数据缺少或存在错误 z 参数")

    def get_volume(self) :
        origin_min, origin_max = [0, 0, 0], [0, 0, 0]
        
        for block in self.blocks :
            for i in range(3) : 
                origin_min[i] = min(origin_min[i], min(pos[i] for pos in block["pos"]))
                origin_max[i] = max(origin_max[i], max(pos[i] for pos in block["pos"]))

        return origin_min, origin_max


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer, str) : _file = open(buffer, "rb")
        elif isinstance(buffer, bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1 = json.load(fp=_file)
        
        if Json1.get("version", None) != "TimeBuilder" : raise FormatError("文件缺少version参数")

        StructureObject = cls()
        StructureObject.blocks.extend(Json1["block"])

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        self.error_check()
        Json1 = {"version": "TimeBuilder", "block":self.blocks}

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, data, data_type:Literal["nbt", "json", "bytes"]) :
        if data_type != "json" : return False
        Json1 = data

        if isinstance(Json1, dict) and Json1.get("version", None) == "TimeBuilder" and \
            isinstance(Json1.get("block", None), list) : return True
        return False



