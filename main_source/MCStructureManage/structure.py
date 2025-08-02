from . import nbt, Block
from .block import GetNbtID, GenerateCommandBlockNBT, GenerateContainerNBT, GenerateSignNBT
from .__private import TypeCheckList, BiList
from io import IOBase
from typing import Union,List,Dict,Tuple,Literal,TypedDict
import array, zlib
from math import floor


def getStructureType(IO_Byte_Path) :
    import io, traceback, json
    from typing import Union
    from . import StructureBDX, StructureMCS, StructureSCHEM
    from . import StructureRUNAWAY, StructureSCHEMATIC
    IO_Byte_Path: Union[str, bytes, io.IOBase]

    if isinstance(IO_Byte_Path, str) : _file = open(IO_Byte_Path, "rb")
    elif isinstance(IO_Byte_Path, bytes) : _file = io.BytesIO(IO_Byte_Path)
    elif isinstance(IO_Byte_Path, io.IOBase) : _file = IO_Byte_Path
    else : raise ValueError(f"{IO_Byte_Path} is not Readable Object")

    data, data_type = _file, "bytes"
    try : 
        data = json.load(fp=_file)
        data_type = "json"
    except : 
        try : 
            _file.seek(0)
            data = nbt.read_from_nbt_file(_file, byteorder="big", zip_mode="gzip").get_tag()
            data_type = "nbt"
        except : 
            try : 
                _file.seek(0)
                data = nbt.read_from_nbt_file(_file, byteorder="little").get_tag()
                data_type = "nbt"
            except : pass

    Test = [StructureBDX.BDX_File, StructureMCS.Mcstructure, StructureSCHEMATIC.Schematic, 
            StructureRUNAWAY.RunAway, StructureRUNAWAY.Kbdx, 
            StructureRUNAWAY.MianYang_V1, StructureRUNAWAY.MianYang_V2, StructureRUNAWAY.MianYang_V3, 
            StructureRUNAWAY.GangBan_V1, StructureRUNAWAY.GangBan_V2, StructureRUNAWAY.GangBan_V3,
            StructureRUNAWAY.GangBan_V4, StructureRUNAWAY.GangBan_V5, StructureRUNAWAY.GangBan_V6,
            StructureRUNAWAY.GangBan_V7,
            StructureRUNAWAY.FuHong_V1, StructureRUNAWAY.FuHong_V2, StructureRUNAWAY.FuHong_V3,
            StructureRUNAWAY.FuHong_V4, StructureRUNAWAY.FuHong_V5, 
            StructureRUNAWAY.QingXu_V1,
            StructureSCHEM.Schem_V1, StructureSCHEM.Schem_V2
            ]

    for class_obj in Test :
        if data_type == "bytes" : data.seek(0)
        try : bool1 = class_obj.is_this_file(data, data_type)
        except : traceback.print_exc() ; continue

        if bool1 : 
            if isinstance(IO_Byte_Path, io.IOBase) : IO_Byte_Path.seek(0)
            return class_obj
    if isinstance(IO_Byte_Path, io.IOBase) : IO_Byte_Path.seek(0)

class CommonStructure :
    """
    基岩版通用结构对象
    -----------------------
    * 所有结构文件将会转换为该结构对象（可能会损失信息）
    * 方块按照 xyz 顺序进行储存（z坐标变化最频繁）
    -----------------------
    * 可用属性 size : 结构长宽高(x, y, z)
    * 可用属性 origin : 结构保存时的位置
    * 可用属性 block_index : 方块索引列表
    * 可用属性 contain_index : 位置索引与方块索引映射的字典
    * 可用属性 block_palette : 方块对象列表（索引指向该列表内的方块）
    * 可用属性 entity_nbt : 实体对象列表
    * 可用属性 block_nbt : 以方块索引字符串数字和nbt对象组成的字典
    -----------------------
    * 反序列化方法 from_buffer : 手/自动指定解码器，并且通过路径、字节数字 或 流式缓冲区 生成对象
    * 序列化方法 save_as : 指定编码器，并且通过路径 或 流式缓冲区 保存对象数据
    -----------------------
    * 可用方法 get_block : 传入非负整数坐标，返回方块对象
    * 可用方法 set_block : 传入非负整数坐标和方块，修改方块
    -----------------------
    * Coder注意事项1 : 部分属性均不可直接修改，请调用对象方法进行修改，以避免数据不正确
    """


    def __init__(self, size:Tuple[int, int, int] = (0, 0, 0)) :
        Volume = size[0] * size[1] * size[2]
        self.size: array.array = array.array("i", size)                                         #修改元素✘，赋值✘
        self.origin: array.array = array.array("i", [0,0,0])                                    #修改元素✔，赋值✘
        self.block_index: array.array[int] = array.array("h", b"\x00\x00" * Volume)             #修改元素✔，赋值✘
        self.contain_index: Dict[int, int] = {}                                                 #修改元素✔，赋值✘
        self.block_palette: List[Block] = BiList()                                              #修改元素✔，赋值✘
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)  #修改元素✔，赋值✘
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}                                        #修改元素✔，赋值✘

        #以下私有属性为自动更新变量，只做读取使用
        self.__volume = size[0] * size[1] * size[2]

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    @classmethod
    def from_buffer(cls, Reader:Union[str, bytes, IOBase], Decoder=None) :
        from . import Codecs
        from . import StructureBDX, StructureMCS, StructureSCHEM
        from . import StructureRUNAWAY, StructureSCHEMATIC
        SupportType = {
            StructureBDX.BDX_File: Codecs.BDX, StructureMCS.Mcstructure: Codecs.MCSTRUCTURE, 
            StructureSCHEMATIC.Schematic: Codecs.SCHEMATIC, 
            StructureRUNAWAY.RunAway: Codecs.RUNAWAY, StructureRUNAWAY.Kbdx: Codecs.KBDX, 
            StructureRUNAWAY.MianYang_V1: Codecs.MIANYANG_V1, StructureRUNAWAY.MianYang_V2: Codecs.MIANYANG_V2, 
            StructureRUNAWAY.MianYang_V3: Codecs.MIANYANG_V3, 
            StructureRUNAWAY.GangBan_V1: Codecs.GANGBAN_V1, StructureRUNAWAY.GangBan_V2: Codecs.GANGBAN_V2,
            StructureRUNAWAY.GangBan_V3: Codecs.GANGBAN_V3, StructureRUNAWAY.GangBan_V4: Codecs.GANGBAN_V4, 
            StructureRUNAWAY.GangBan_V5: Codecs.GANGBAN_V5, StructureRUNAWAY.GangBan_V6: Codecs.GANGBAN_V6, 
            StructureRUNAWAY.GangBan_V7: Codecs.GANGBAN_V7, 
            StructureRUNAWAY.FuHong_V1: Codecs.FUHONG_V1, StructureRUNAWAY.FuHong_V2: Codecs.FUHONG_V2, 
            StructureRUNAWAY.FuHong_V3: Codecs.FUHONG_V3, StructureRUNAWAY.FuHong_V4: Codecs.FUHONG_V4, 
            StructureRUNAWAY.FuHong_V5: Codecs.FUHONG_V5, 
            StructureRUNAWAY.QingXu_V1: Codecs.QINGXU_V1,
            StructureSCHEM.Schem_V1: Codecs.SCHEM_V1, StructureSCHEM.Schem_V2: Codecs.SCHEM_V2, 
        }

        if Decoder is not None and Codecs.CodecsBase not in Decoder.mro() : 
            raise TypeError(f"{Decoder}是不受支持的解码器")
        elif Decoder is None : 
            TypeObj = getStructureType(Reader)
            if TypeObj not in SupportType : raise TypeError(f"{Reader}是不支持解析的文件或数据")

        Common = cls()
        Decoder = SupportType[TypeObj] if Decoder is None else Decoder
        Decoder(Common).decode(Reader)
        return Common

    def save_as(self, Writer:Union[str, IOBase], Encoder, IgnoreAir:bool=True) :
        """
        * 使用json格式输出时，Writer一定为字符串缓冲区或带有编码的文件缓冲区
        * IgnoreAir参数，不在mcstructure和schematic文件中生效
        """
        Encoder(self, IgnoreAir).encode(Writer)


    def get_block(self, pos_x:int, pos_y:int, pos_z:int) -> Union[None, Block] :
        if not(0 <= pos_x < self.size[0]) : return None
        if not(0 <= pos_y < self.size[1]) : return None
        if not(0 <= pos_z < self.size[2]) : return None
        index = (pos_x * self.size[1] + pos_y) * self.size[2] + pos_z
        return self.block_palette[self.block_index[index]]

    def set_block(self, pos_x:int, pos_y:int, pos_z:int, block:Union[int, Block]) :
        index = (pos_x * self.size[1] + pos_y) * self.size[2] + pos_z
        if block.__class__ is int : 
            self.block_index[index] = block 
            Block_ID = self.block_palette[block].name
            NBT_ID_NAME = GetNbtID(Block_ID)
        else : 
            self.block_index[index] = self.block_palette.append(block)
            Block_ID = block.name
            NBT_ID_NAME = GetNbtID(Block_ID)

        if not NBT_ID_NAME : return None
        if NBT_ID_NAME == "CommandBlock" : NBTFunc = GenerateCommandBlockNBT
        elif NBT_ID_NAME == "HangingSign" : NBTFunc = GenerateSignNBT
        elif NBT_ID_NAME == "Sign" : NBTFunc = GenerateSignNBT
        else : NBTFunc = GenerateContainerNBT
        self.block_nbt[index] = NBTFunc(Block_ID)

    def get_blockNBT(self, pos_x:int, pos_y:int, pos_z:int) -> Union[None, nbt.TAG_Compound] :
        index = (pos_x * self.size[1] + pos_y) * self.size[2] + pos_z
        return self.block_nbt.get(index, None)

    def set_blockNBT(self, pos_x:int, pos_y:int, pos_z:int, nbt:Union[None, nbt.TAG_Compound]) :
        index = (pos_x * self.size[1] + pos_y) * self.size[2] + pos_z
        if nbt : self.block_nbt[index] = nbt
        elif index in self.block_nbt : del self.block_nbt[index]


