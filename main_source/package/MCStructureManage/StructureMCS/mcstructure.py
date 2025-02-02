import os,array,ctypes
from .. import nbt,TypeCheckList
from typing import Union,List,TypedDict,Dict
from io import FileIO, BytesIO

class BLOCK_TYPE(TypedDict): 
    name: str
    states: Dict[str, Union[ctypes.c_byte, ctypes.c_short, ctypes.c_int, ctypes.c_long]]


class Mcstructure :
    """
    基岩版 Mcstructure 结构文件对象
    -----------------------
    * 管理 .mcstructure 为后缀的小端nbt文件
    * 方块按照 xyz 顺序进行储存（z坐标变化最频繁）
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构保存时的位置
    * 可用属性 block_index : 方块索引列表（数量与结构体积相同, -1代表跳过）
    * 可用属性 water_log : 方块是否含水，不含水为-1，含水为1（数量与结构体积相同）
    * 可用属性 block_palette : 方块对象列表
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
        self.water_log: array.array = array.array("i")
        self.block_palette: List[BLOCK_TYPE] = TypeCheckList().setChecker(dict)
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    def error_check(self) :
        Volume = self.size[0] * self.size[1] * self.size[2]
        if len(self.size) != 3 : raise Exception("结构长宽高列表长度不为3")
        if len(self.origin) != 3 : raise Exception("结构保存位置列表长度不为3")
        if len(self.block_index) != Volume : raise Exception("方块索引列表长度与结构体积不相等")
        if len(self.water_log) != Volume : raise Exception("方块含水列表长度与结构体积不相等")
        if any((i not in {-1, 1}) for i in self.water_log) : raise Exception("方块含水列表存在非-1和1的数值")

        if max(self.block_index) >= len(self.block_palette) :
            raise Exception("方块索引列表 中存在超出 方块对象列表 的合法索引长度")
        for block in self.block_palette :
            Error = "方块列表中存在不合法的方块数据( %s )"
            if not isinstance(block.get("name", None), str) : raise Exception(Error % block)
            if not isinstance(block.get("states", None), dict) : raise Exception(Error % block)
            if not all((isinstance(key, str) and isinstance(value, (str, int))) 
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
        StructureObject.water_log = NBT['structure']['block_indices'][1].get_value()

        for block in NBT['structure']['palette']['default']['block_palette'] :
            BlockObj = {"name":str(block["name"]), "states":{}}
            for key, value in (block.get("states").items() if block.get("states", None) else ()) :
                if isinstance(value, nbt.TAG_String) : BlockObj['states'][str(key)] = str(value)
                elif isinstance(value, nbt.TAG_Byte) : BlockObj['states'][str(key)] = ctypes.c_byte(int(value))
                elif isinstance(value, nbt.TAG_Short) : BlockObj['states'][str(key)] = ctypes.c_short(int(value))
                elif isinstance(value, nbt.TAG_Int) : BlockObj['states'][str(key)] = ctypes.c_int(int(value))
                elif isinstance(value, nbt.TAG_Long) : BlockObj['states'][str(key)] = ctypes.c_long(int(value))
            StructureObject.block_palette.append(BlockObj)
        StructureObject.entity_nbt = TypeCheckList(NBT['structure']['entities'])
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
        StructureBlockIndices.append( nbt.TAG_List(self.water_log, nbt.TAG_List) )

        StructureEntity = StructureNBT['structure']['entities'] = nbt.TAG_List(type=nbt.TAG_Compound)
        StructureNBT['structure']['palette'] = nbt.TAG_Compound()
        StructureNBT['structure']['palette']['default'] = nbt.TAG_Compound()
        StructureBlockPalette = StructureNBT['structure']['palette']['default']['block_palette'] = nbt.TAG_List(type=nbt.TAG_Compound)
        StructureBlockNBT = StructureNBT['structure']['palette']['default']['block_position_data'] = nbt.TAG_Compound()

        for entity in self.entity_nbt : StructureEntity.append(entity)
        for block in self.block_palette :
            BLOCK = nbt.TAG_Compound()
            BLOCK["name"] = nbt.TAG_String(block['name'])
            BLOCK["states"] = nbt.TAG_Compound()
            BLOCK["version"] = nbt.TAG_Int(17959425)
            for key, value in block["states"].items() :
                if isinstance(value, (bool, ctypes.c_byte)) : BLOCK['states'][str(key)] = nbt.TAG_Byte(int(value))
                elif isinstance(value, ctypes.c_short) : BLOCK['states'][str(key)] = nbt.TAG_Short(int(value))
                elif isinstance(value, (int, ctypes.c_int)) : BLOCK['states'][str(key)] = nbt.TAG_Int(int(value))
                elif isinstance(value, ctypes.c_long) : BLOCK['states'][str(key)] = nbt.TAG_Long(int(value))
                elif isinstance(value, str) : BLOCK["states"][key] = nbt.TAG_String(value)
            StructureBlockPalette.append(BLOCK)
        for index, block_nbt in self.block_nbt.items() :
            StructureBlockNBT[str(index)] = block_nbt

        if isinstance(buffer, str) : 
            base_path = os.path.realpath(os.path.join(buffer, os.pardir))
            os.makedirs(base_path, exist_ok=True)
            _file = open(buffer, "wb")
        else : _file = buffer
        nbt.write_to_nbt_file(_file, StructureNBT, byteorder="little")
