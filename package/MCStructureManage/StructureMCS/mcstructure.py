import os,array,ctypes
from .. import nbt
from ..__private import TypeCheckList
from typing import Union,List,TypedDict,Dict
from io import FileIO, BytesIO

class BLOCK_TYPE(TypedDict): 
    name: nbt.TAG_String
    states: Dict[str, Union[nbt.TAG_String, nbt.TAG_Byte, nbt.TAG_Int]]


class Mcstructure :
    """
    基岩版 Mcstructure 结构文件对象
    -----------------------
    * 管理 .mcstructure 为后缀的小端nbt文件
    * 方块按照 xyz 顺序进行储存（z坐标变化最频繁）
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构保存时的位置
    * 可用属性 block_index : 方块索引列表（-1代表跳过）
    * 可用属性 contain_index : 方块是否含有其他方块，方块索引列表（例如含水，-1代表跳过）
    * 可用属性 block_palette : 方块对象列表（索引指向该列表内的方块）
    * 可用属性 entity_nbt : 实体对象列表
    * 可用属性 block_nbt : 以方块索引字符串数字和nbt对象组成的字典
    -----------------------
    * 可用类方法 from_buffer : 通过路径、字节数字 或 流式缓冲区 生成对象
    * 可用方法 save_as : 通过路径 或 流式缓冲区 保存对象数据
    """
    

    def __init__(self) :
        self.size: array.array = array.array("i", [0, 0, 0])
        self.origin: array.array = array.array("i", [0, 0, 0])
        self.block_index: array.array = array.array("i")
        self.contain_index: array.array = array.array("i")
        self.block_palette: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        ValueType = (nbt.TAG_String, nbt.TAG_Byte, nbt.TAG_Int)
        Volume = self.size[0] * self.size[1] * self.size[2]
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")
        if len(self.origin) != 3 : raise Exception("结构保存位置列表长度不为3")
        if len(self.block_index) != Volume : raise Exception("方块索引列表长度与结构体积不相等")
        if len(self.contain_index) != Volume : raise Exception("方块含水列表长度与结构体积不相等")
        
        if max(self.contain_index) >= len(self.block_palette) : 
            raise Exception("方块包含列表 中存在超出 方块对象列表 的索引长度值")
        if max(self.block_index) >= len(self.block_palette) :
            raise Exception("方块索引列表 中存在超出 方块对象列表 的索引长度值")
        for block in self.block_palette :
            Error = "方块列表中存在不合法的方块数据( %s )"
            if not isinstance(block.get("name", None), nbt.TAG_String) : raise Exception(Error % block)
            if not isinstance(block.get("states", None), nbt.TAG_Compound) : raise Exception(Error % block)
            if not all((isinstance(key, str) and isinstance(value, ValueType)) 
               for key,value in block["states"].items()) : raise Exception(Error % block)
        for index, block_nbt in self.block_nbt.items() :
            if not isinstance(index, int) : raise Exception("方块NBT索引存在不为整数的对象( %s )" % index)
            elif not isinstance(block_nbt, nbt.TAG_Compound) : raise Exception("方块NBT对象存在不为NBT组件的对象( %s )" % block_nbt)


    @classmethod
    def from_buffer(cls, buffer:Union[str, FileIO, BytesIO]) :
        NBT = nbt.read_from_nbt_file(buffer, byteorder="little")

        StructureObject = cls()
        StructureObject.size = NBT["size"].get_value()
        StructureObject.origin = NBT["structure_world_origin"].get_value()
        StructureObject.block_index = NBT['structure']['block_indices'][0].get_value()
        StructureObject.contain_index = NBT['structure']['block_indices'][1].get_value()
        StructureObject.block_palette.extend(NBT['structure']['palette']['default']['block_palette'])
        StructureObject.entity_nbt.extend(NBT['structure']['entities'])
        for index_str, block_nbt in NBT['structure']['palette']['default']['block_position_data'].items() :
            StructureObject.block_nbt[int(index_str)] = block_nbt

        return StructureObject

    def save_as(self, buffer:Union[str, FileIO, BytesIO]) :
        self.error_check()

        StructureNBT = nbt.TAG_Compound()
        StructureNBT['format_version'] = nbt.TAG_Int(1)
        StructureNBT['size'] = nbt.TAG_List(self.size, type=nbt.TAG_Int)
        StructureNBT['structure_world_origin'] = nbt.TAG_List(self.origin, type=nbt.TAG_Int)
        StructureNBT['structure'] = nbt.TAG_Compound()
        StructureBlockIndices = StructureNBT['structure']['block_indices'] = nbt.TAG_List(type=nbt.TAG_List)
        StructureBlockIndices.append( nbt.TAG_List(self.block_index, nbt.TAG_Int) )
        StructureBlockIndices.append( nbt.TAG_List(self.contain_index, nbt.TAG_List) )

        StructureEntity = StructureNBT['structure']['entities'] = nbt.TAG_List(type=nbt.TAG_Compound)
        StructureNBT['structure']['palette'] = nbt.TAG_Compound()
        StructureNBT['structure']['palette']['default'] = nbt.TAG_Compound()
        StructureBlockPalette = StructureNBT['structure']['palette']['default']['block_palette'] = nbt.TAG_List(type=nbt.TAG_Compound)
        StructureBlockNBT = StructureNBT['structure']['palette']['default']['block_position_data'] = nbt.TAG_Compound()

        for entity in self.entity_nbt : StructureEntity.append(entity)
        for block in self.block_palette :
            if "version" not in block : block["version"] = nbt.TAG_Int(17959425)
            StructureBlockPalette.append(block)
        for index, block_nbt in self.block_nbt.items() :
            StructureBlockNBT[str(index)] = block_nbt

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "wb")
        else : _file = buffer
        nbt.write_to_nbt_file(_file, StructureNBT, byteorder="little")


    @classmethod
    def is_this_file(cls, bytes_io:BytesIO) :
        try : NBT = nbt.read_from_nbt_file(bytes_io, byteorder="little").get_tag()
        except : return False

        if "size" in NBT and "structure_world_origin" in NBT and 'structure' in NBT : return True
        else : return False


