import os,array,json
from .. import nbt
from ..__private import TypeCheckList
from typing import Union,List,TypedDict,Dict,Tuple,Optional
from io import FileIO, BytesIO, StringIO, TextIOBase

class CHUNK(TypedDict) :
    startX: int
    startZ: int
    blocks: List[Tuple[int,int,int,int,int,str]]
class FILE_FORMAT(TypedDict) :
    chunkedBlocks: List[CHUNK]
    namespaces: List[str]
    totalBlocks: int
class FormatError(Exception) : pass



class MianYang :
    """
    由 绵阳 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    * 区块中每个方块数据含义：[方块索引，方块数据值，x，y，z，JsonStr?]
    -----------------------
    * 可用属性 chunks : 区块储存列表
    * 可用属性 block_palette : 方块ID映射列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """
    

    def __init__(self) :
        self.chunks: List[CHUNK] = TypeCheckList().setChecker(dict)
        self.block_palette: List[str] = TypeCheckList().setChecker(str)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        block_count = 0
        for chunk in self.chunks :
            if not isinstance(chunk.get("startX", None), int) : raise Exception("区块数据缺少或存在错误 startX 参数")
            if not isinstance(chunk.get("startZ", None), int) : raise Exception("区块数据缺少或存在错误 startZ 参数")
            if not isinstance(chunk.get("blocks", None), list) : raise Exception("区块数据缺少或存在错误 blocks 参数")
            for block in chunk["blocks"] : 
                if not isinstance(block, list) : raise Exception(f"区块({chunk['startX']},{chunk['startZ']})存在错误方块参数")
                if len(block) < 5 : raise Exception(f"区块({chunk['startX']},{chunk['startZ']})方块参数数量不足")
                if any(not isinstance(i, int) for i in block[0:5]) : raise Exception(f"区块({chunk['startX']},{chunk['startZ']})存在非整数方块或坐标参数")
                if len(block) > 5 :
                    if not isinstance(block[5], str) : raise Exception(f"区块({chunk['startX']},{chunk['startZ']})存在错误nbt类型")
                    Error = 0
                    try : json.loads(block[5])
                    except : Error = 1
                    if Error : raise Exception(f"区块({chunk['startX']},{chunk['startZ']})存在无法解析的nbt数据")
            block_count += len(chunk["blocks"])
        return block_count

    def get_volume(self) :
        origin_min, origin_max, = [0, 0, 0], [0, 0, 0]

        def pos_iter() :
            for chunk in self.chunks :
                o_x, o_z = chunk["startX"], chunk["startZ"]
                for block in chunk["blocks"] :
                    yield (o_x+block[2], block[3], o_z+block[4])
        for i in range(3) : origin_min[i] = min(j[i] for j in pos_iter())
        for i in range(3) : origin_max[i] = max(j[i] for j in pos_iter())

        return origin_min, origin_max


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO, StringIO]) :
        if isinstance(buffer, str) : _file = open(buffer, "rb")
        elif isinstance(buffer, bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        Json1:FILE_FORMAT = json.load(fp=_file)
        
        if "chunkedBlocks" not in Json1 : raise FormatError("文件缺少chunkedBlocks参数")
        if "namespaces" not in Json1 : raise FormatError("文件缺少namespaces参数")

        StructureObject = cls()
        StructureObject.chunks.extend(Json1["chunkedBlocks"])
        StructureObject.block_palette.extend(Json1["namespaces"])

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        block_count = self.error_check()
        Json1:FILE_FORMAT = {"chunkedBlocks":list(self.chunks), 
            "namespaces":list(self.block_palette), "totalBlocks":block_count}

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "w+", encoding="utf-8")
        else : _file = buffer
        
        if not isinstance(_file, TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")
        json.dump(Json1, _file, separators=(',', ':'))


    @classmethod
    def is_this_file(cls, bytes_io:BytesIO) :
        try : Json1 = json.load(fp=bytes_io)
        except : return False
        if isinstance(Json1, dict) and ("chunkedBlocks" in Json1) \
            and ("namespaces" in Json1) : return True
        return False

