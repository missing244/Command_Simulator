import os,itertools,json
from .. import nbt
from ..__private import TypeCheckList
from typing import Union,List,TypedDict,Literal
from io import FileIO, BytesIO, StringIO, TextIOBase

class FormatError(Exception) : pass

class BLOCK(TypedDict) :
    Name: str
    X: int
    Y: int
    Z: int


class QingXu_V1 :
    """
    由 情绪 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * 格式：{ "0": "{\"0\":\"{\\\"Name\\\":\\\"grass\\\",\\\"X\\\":0,\\\"Y\\\":0,\\\"Z\\\":0}\"", "totalBlocks": 1}
    ----------------------------------------
    * 可用属性 chunks : 区块储存列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """
    

    def __init__(self) :
        self.chunks: List[List[BLOCK]] = TypeCheckList().setChecker(list)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        for chunk in self.chunks :
            for block in chunk :
                if not isinstance(block, dict) : raise Exception("方块数据不为dict参数")
                if not isinstance(block.get("Name", None), str) : raise Exception("方块数据缺少或存在错误 Name 参数")
                if not isinstance(block.get("X", None), int) : raise Exception("方块数据缺少或存在错误 X 参数")
                if not isinstance(block.get("Y", None), int) : raise Exception("方块数据缺少或存在错误 Y 参数")
                if not isinstance(block.get("Z", None), int) : raise Exception("方块数据缺少或存在错误 Z 参数")

    def get_volume(self) :
        origin_min, origin_max, str1 = [0, 0, 0], [0, 0, 0], ["X", "Y", "Z"]

        for i in range(3) : origin_min[i] = min(block[str1[i]] for block in itertools.chain(*self.chunks))
        for i in range(3) : origin_max[i] = max(block[str1[i]] for block in itertools.chain(*self.chunks))

        return origin_min, origin_max


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer, str) : _file = open(buffer, "rb")
        elif isinstance(buffer, bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1 = json.load(fp=_file)
        
        if "totalBlocks" not in Json1 : raise FormatError("文件缺少totalBlocks参数")

        StructureObject = cls()
        for i in range(Json1["totalBlocks"]) :
            chunk = json.loads(Json1.get(f"{i}", '{"totalPoints":0}'))
            if not chunk : continue
            StructureObject.chunks.append( [] )
            for j in range(chunk["totalPoints"]) : 
                block = chunk.get(f"{j}", None)
                if not block : continue
                StructureObject.chunks[-1].append(json.loads(block))

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        #self.error_check()
        Json1 = {"totalBlocks":len(self.chunks)}
        for i, chunk in enumerate(self.chunks) : 
            minX, maxX = min(i["X"] for i in chunk), max(i["X"] for i in chunk)
            minY, maxY = min(i["Y"] for i in chunk), max(i["Y"] for i in chunk)
            minZ, maxZ = min(i["Z"] for i in chunk), max(i["Z"] for i in chunk)
            Cache = {"totalPoints": len(chunk), "centerX":(minX+maxX)//2, 
                "centerY":(minY+maxY)//2, "centerZ":(minZ+maxZ)//2}
            for j, block in enumerate(chunk) : Cache[f"{j}"] = json.dumps(block, separators=(',', ':'))
            Json1[f"{i}"] = json.dumps(Cache, separators=(',', ':'))

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer

        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))



