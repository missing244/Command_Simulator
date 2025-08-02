import os,array,ctypes
from .. import nbt
from ..__private import TypeCheckList
from typing import Union,List,TypedDict,Dict,Literal
from io import FileIO, BytesIO


class Schem_V1 :
    """
    Schem 结构文件对象
    -----------------------
    * 管理 .schem 为后缀的大端gzip压缩的nbt文件
    * 方块按照 yzx 顺序进行储存（x坐标变化最频繁）
    * 此对象并不能完整保留所有储存的数据
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 block_index : 方块索引列表（数量与结构体积相同）
    * 可用属性 block_palette : 方块列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """
    

    def __init__(self) :
        self.size: array.array = array.array("i", [0, 0, 0])
        self.block_index: array.array = array.array("B")
        self.block_palette: Dict[int, str] = {}
        self.block_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        Volume = self.size[0] * self.size[1] * self.size[2]
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")
        if len(self.block_index) != Volume : raise Exception("方块索引列表长度与结构体积不相等")


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO]) :
        NBT = nbt.read_from_nbt_file(buffer, byteorder="big", zip_mode="gzip").get_tag()

        StructureObject = cls()
        StructureObject.size[0] = NBT["Width"].value
        StructureObject.size[1] = NBT["Height"].value
        StructureObject.size[2] = NBT["Length"].value
        StructureObject.block_index = NBT['BlockData'].value
        StructureObject.block_palette.update((j.value, i) for i,j in NBT['Palette'].items())
        StructureObject.block_nbt.extend(NBT.get("BlockEntities", []))

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, BytesIO]) :
        #self.error_check()
        raise RuntimeError("该格式无法写回为二进制流对象")

        node = nbt.NBT_Builder()
        NBT = node.compound(
            Version = node.int(2),
            Width = node.short(self.size[0]),
            Height = node.short(self.size[1]),
            Length = node.short(self.size[2]),
            Offset = node.int_array(0, 0, 0),
            Metadata = node.compound(
                WEOffsetX = node.int(0),
                WEOffsetY = node.int(0),
                WEOffsetZ = node.int(0),
            ),
            BlockEntities = node.list(*list(self.block_nbt)),
            BlockData = node.byte_array(),
            Palette = node.compound(),
            PaletteMax = node.int()
        ).build()
        NBT['BlockData'] = nbt.TAG_ByteArray(array.array("b", self.block_index.tobytes()))
        NBT['Palette'] = nbt.TAG_Compound({j:nbt.TAG_Int(i) for i,j in enumerate(self.block_palette)})
        NBT['PaletteMax'] = nbt.TAG_Int( len(NBT['Palette']) )

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "wb")
        else : _file = buffer
        nbt.write_to_nbt_file(_file, NBT, zip_mode="gzip" ,byteorder="big")


    @classmethod
    def is_this_file(cls, data, data_type:Literal["nbt", "json", "bytes"]) :
        if data_type != "nbt" : return False

        NBT = data
        if "Version" in NBT and NBT["Version"].value <= 2 and \
            "Width" in NBT and "Height" in NBT and 'Length' in NBT and \
            "BlockData" in NBT and 'Palette' in NBT : return True
        else : return False

"""
Schematic -> <'TAG_Compound'
    Version --> <class 'TAG_Int'>
    DataVersion --> <class 'TAG_Int'>
    Metadata --> <class 'TAG_Compound'
        Date --> <class 'TAG_Long'>
        WorldEdit --> <class 'TAG_Compound'
            Version --> <class 'TAG_String'>
            EditingPlatform --> <class 'TAG_String'>
            Origin --> <class 'TAG_IntArray'>
            Platforms --> <class 'TAG_Compound'>
        >
    >
    Width --> <class 'TAG_Short'>
    Height --> <class 'TAG_Short'>
    Length --> <class 'TAG_Short'>
    Offset --> <class 'TAG_IntArray'>
    Blocks --> <class 'TAG_Compound'
        Palette --> <class 'package.python_nbt.tags.TAG_Compound' Dict[str, TAG_Int] >
        Data --> <class 'package.python_nbt.tags.TAG_ByteArray'>
        BlockEntities --> <class 'package.python_nbt.tags.TAG_List' List[TAG_Compound] >
    >
>
"""
class Schem_V2(Schem_V1) :
    """
    Schem 结构文件对象
    -----------------------
    * 管理 .schem 为后缀的大端gzip压缩的nbt文件
    * 方块按照 yzx 顺序进行储存（x坐标变化最频繁）
    * 此对象并不能完整保留所有储存的数据
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 block_index : 方块索引列表（数量与结构体积相同）
    * 可用属性 block_palette : 方块列表
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """

    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO]) :
        NBT = nbt.read_from_nbt_file(buffer, byteorder="big", zip_mode="gzip").get_tag()
        NBT = NBT["Schematic"]

        StructureObject = cls()
        StructureObject.size[0] = NBT["Width"].value
        StructureObject.size[1] = NBT["Height"].value
        StructureObject.size[2] = NBT["Length"].value
        StructureObject.block_index = NBT['Blocks']['Data'].value
        StructureObject.block_palette.update((j.value, i) for i,j in NBT['Blocks']['Palette'].items())
        StructureObject.block_nbt.extend(NBT['Blocks'].get("BlockEntities", []))

        return StructureObject


    @classmethod
    def is_this_file(cls, data, data_type:Literal["nbt", "json", "bytes"]) :
        if data_type != "nbt" : return False

        NBT = data
        if "Schematic" not in NBT : return False
        if "Version" in NBT["Schematic"] and NBT["Schematic"]["Version"].value == 3 and \
            "Width" in NBT["Schematic"] and "Height" in NBT["Schematic"] and 'Length' in NBT["Schematic"] and \
            "Blocks" in NBT["Schematic"] : return True
        else : return False
