import os,array,json,struct
from .. import nbt,TypeCheckList
from typing import Union,List,TypedDict,Dict,Tuple,Literal,Optional
from io import FileIO, BytesIO, StringIO, TextIOBase

class BLOCK1(TypedDict) :
    name: str
    aux: Optional[int]
    x: int
    y: int
    z: int

class BLOCK2(TypedDict) :
    name: str
    aux: Optional[int]
    x: Tuple[int]
    y: Tuple[int]
    z: Tuple[int]



class RunAway :
    """
    由 RunAway 官方文档教程提供的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    -----------------------
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
            for i in self.blocks : yield (i["x"], i["y"], i["z"])
        for i in range(3) : origin_min[i] = min(j[i] for j in pos_iter())
        for i in range(3) : origin_max[i] = max(j[i] for j in pos_iter())

        return origin_min, origin_max

    def error_check(self) :
        for block in self.blocks :
            if not isinstance(block.get("name", None), str) : raise Exception("方块数据缺少或存在错误的 name 参数")
            if not isinstance(block.get("aux", 0), int) : raise Exception("方块数据存在错误的 aux 参数")
            if not isinstance(block.get("x", None), int) : raise Exception("方块数据存在错误的 x 参数")
            if not isinstance(block.get("y", None), int) : raise Exception("方块数据存在错误的 y 参数")
            if not isinstance(block.get("z", None), int) : raise Exception("方块数据存在错误的 z 参数")
            
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


class FuHong(RunAway) :
    """
    由 FuHong 开发的结构文件对象
    -----------------------
    * 以 .json 为后缀的json格式文件
    -----------------------
    * 可用属性 blocks : 方块储存列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.blocks: List[BLOCK2] = TypeCheckList().setChecker(dict)


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


class Kbdx :
    """
    由 RunAway 官方开发的结构文件对象
    -----------------------
    * 以 .kbdx 为后缀的二进制格式文件
    -----------------------
    * 可用属性 blocks : 方块储存列表
    * 可用属性 block_palette : 方块id映射表
    * 可用属性 block_nbt : 方块索引储存列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """


    def __init__(self) :
        self.blocks: List[Tuple[int, int, int, int]] = TypeCheckList().setChecker(tuple)
        self.block_palette: List[str] = TypeCheckList(["air"]).setChecker(str)
        self.block_nbt: List[dict] = TypeCheckList().setChecker(dict)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def get_volume(self) :
        origin_min, origin_max, = [0, 0, 0], [0, 0, 0]

        for i in range(3) : origin_min[i] = min(j[i] for j in self.blocks)
        for i in range(3) : origin_max[i] = max(j[i] for j in self.blocks)

        return origin_min, origin_max

    def error_check(self) :
        for block in self.blocks :
            if len(block) < 4 : raise Exception("方块数据不完整")
            if not isinstance(block[0], int) : raise Exception("方块数据存在错误的 x 参数")
            if not isinstance(block[1], int) : raise Exception("方块数据存在错误的 y 参数")
            if not isinstance(block[2], int) : raise Exception("方块数据存在错误的 z 参数")
            if not isinstance(block[3], int) : raise Exception("方块数据存在错误的 index 参数")
            if block[3] < 1 : raise Exception("方块数据的 index 参数必须大于0")


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO]) :
        if isinstance(buffer,str) : _file = open(buffer, "rb")
        elif isinstance(buffer,bytes) : _file = BytesIO(buffer)
        else : _file = buffer
        
        StructureObject = cls()
        block_count = int.from_bytes(_file.read(4), "little", signed=False)
        S1 = struct.Struct(f'<iiiQ')

        blocks = TypeCheckList(["air"] * block_count).setChecker(tuple)
        setmethod = super(TypeCheckList, blocks).__setitem__
        setmethod( slice(0, block_count, 1), S1.iter_unpack( _file.read(20 * block_count)) )
        StructureObject.blocks = blocks

        save_data:dict = json.load(_file)
        StructureObject.block_nbt = TypeCheckList(save_data.get('BlockEntityData', [])).setChecker(dict)
        del save_data['BlockEntityData']

        StructureObject.block_palette = TypeCheckList([None] * (max(save_data.values()) + 1)).setChecker(str)
        for i,j in save_data.items() : StructureObject.block_palette[j] = i

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, StringIO]) :
        self.error_check()

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "wb")
        else : _file = buffer

        S1 = struct.Struct(f'<iiiQ')
        for i in self.blocks : buffer.write( S1.pack(*i) )

        Json1 = {'BlockEntityData': list(self.block_nbt)}
        for i,j in enumerate(self.block_palette[1:], start=1) : Json1[j] = f'{i}'

        buffer.write( json.dumps(Json1, separators=(',', ':')).encode("utf-8") )

