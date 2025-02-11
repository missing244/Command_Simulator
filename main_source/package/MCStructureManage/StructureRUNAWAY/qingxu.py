import os,array,json
from .. import nbt,TypeCheckList
from typing import Union,List,TypedDict,Dict,Tuple,Optional
from io import FileIO, BytesIO, StringIO, TextIOBase

class FormatError(Exception) : pass

class FILE_FORMAT(TypedDict) :
    Block_ID: str
    Size: int

class BLOCK(TypedDict) :
    Name: str
    x: int
    y: int
    z: int


class QingXu :
    """
    由 情绪 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * 格式：{ "Block-1": "{\\"Name\\":\\"grass\\",\\"x\\":0,\\"y\\":0,\\"z\\":0}", "Size": 1}
    -----------------------
    * 可用属性 chunks : 区块储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """
    

    def __init__(self) :
        self.blocks: List[BLOCK] = TypeCheckList().setChecker(dict)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        for block in self.blocks :
            if not isinstance(block.get("Name", None), str) : raise Exception("区块数据缺少或存在错误 Name 参数")
            if not isinstance(block.get("x", None), int) : raise Exception("区块数据缺少或存在错误 x 参数")
            if not isinstance(block.get("y", None), int) : raise Exception("区块数据缺少或存在错误 y 参数")
            if not isinstance(block.get("z", None), int) : raise Exception("区块数据缺少或存在错误 z 参数")

    def get_volume(self) :
        origin_min, origin_max, str1 = [0, 0, 0], [0, 0, 0], ["x", "y", "z"]

        for i in range(3) : origin_min[i] = min(j[str1[i]] for j in self.blocks)
        for i in range(3) : origin_max[i] = max(j[str1[i]] for j in self.blocks)

        return origin_min, origin_max


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer, str) : _file = open(buffer, "rb")
        elif isinstance(buffer, bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:FILE_FORMAT = json.load(fp=_file)
        
        if "Size" not in Json1 : raise FormatError("文件缺少Size参数")

        StructureObject = cls()
        Append = super(TypeCheckList, StructureObject.blocks).append
        for i in range(1, Json1["Size"]+1, 1) :
            a = Json1.get(f"Block-{i}", None)
            if a : Append( json.loads(a) )

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        self.error_check()
        Json1:FILE_FORMAT = {"Size":len(self.blocks)}
        for i,j in enumerate(self.blocks, start=1) : Json1[f"Block-{i}"] = json.dumps(j, separators=(',', ':'))

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))



