from . import nbt, Block
from .block import GetNbtID, GenerateCommandBlockNBT, GenerateContainerNBT, GenerateSignNBT
from .__private import TypeCheckList, BiList
from io import IOBase
from typing import Union,List,Dict,Tuple,Literal,TypedDict
import array, math


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
    * 可用属性 BLOCKTYPE : 公开该结构的使用方块对象类(block_palette元素)
    -----------------------
    * 反序列化方法 from_buffer : 手/自动指定解码器，并且通过路径、字节数字 或 流式缓冲区 生成对象
    * 序列化方法 save_as : 指定编码器，并且通过路径 或 流式缓冲区 保存对象数据
    -----------------------
    * 可用方法 get_block : 传入非负整数坐标，返回方块对象
    * 可用方法 set_block : 传入非负整数坐标和方块，修改方块
    * 可用方法 get_blockNBT : 传入非负整数坐标，返回方块NBT对象
    * 可用方法 set_blockNBT : 传入非负整数坐标和方块NBT，修改方块NBT对象
    * 可用方法 count : 传入方块对象，获取在结构中方块的数量
    * 可用方法 split : 传入起始坐标与结束坐标，获取对应的结构切片
    -----------------------
    * Coder注意事项1 : 部分属性均不可直接修改，请调用对象方法进行修改，以避免数据不正确
    """

    BLOCKTYPE = Block                                                                  #公开该结构的使用方块对象类
    
    def __init__(self, size:Tuple[int, int, int] = (0, 0, 0)) :
        Volume = size[0] * size[1] * size[2]
        if Volume > 2000000000 : raise MemoryError("内存过大无法生成结构模板")
        self.size: array.array = array.array("i", size)                                         #修改元素✘，赋值✘
        self.origin: array.array = array.array("i", [0,0,0])                                    #修改元素✔，赋值✘
        self.block_index: array.array[int] = array.array("h", bytearray(Volume*2))              #修改元素✔，赋值✘
        self.contain_index: Dict[int, int] = {}                                                 #修改元素✔，赋值✘
        self.block_palette: List[Block] = BiList()                                              #修改元素✔，赋值✘
        self.entity_nbt: List[nbt.TAG_Compound] = TypeCheckList().setChecker(nbt.TAG_Compound)  #修改元素✔，赋值✘
        self.block_nbt: Dict[int, nbt.TAG_Compound] = {}                                        #修改元素✔，赋值✘

        #以下私有属性为自动更新变量，只做读取使用
        self.__volume = size[0] * size[1] * size[2]

    def __setattr__(self, name, value) :
        if not hasattr(self, name) : super().__setattr__(name, value)
        elif name == "BLOCKTYPE" : raise Exception("无法修改 %s 属性" % name)
        elif isinstance(value, type(getattr(self, name))) : super().__setattr__(name, value)
        else : raise Exception("无法修改 %s 属性" % name)

    def __delattr__(self, name) :
        raise Exception("无法删除任何属性")


    @classmethod
    def from_buffer(cls, Reader:Union[str, bytes, IOBase], Decoder=None) :
        from . import Codecs, getStructureType

        if Decoder is not None and Codecs.CodecsBase not in Decoder.mro() : 
            raise TypeError(f"{Decoder}是不受支持的解码器")
        elif Decoder is None : 
            CodecsType = getStructureType(Reader)
            if CodecsType is None : raise TypeError(f"{Reader}是不支持解析的文件或数据")

        Common = cls()
        Decoder = CodecsType if Decoder is None else Decoder
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


    def count(self, block_obj:Block) :
        if block_obj not in self.block_palette : return 0
        index_list = [index for index, block in enumerate(self.block_palette) if block_obj == block]
        return sum( self.block_index.count(i) for i in index_list )

    def split(self, start_pos:Tuple[int, int, int], end_pos:Tuple[int, int, int]) -> "CommonStructure" :
        from . import C_API
        if any( j<i for i,j in zip(start_pos, end_pos) ) : 
            raise ValueError("结束坐标%s不能小于起始坐标%s" % (end_pos, start_pos))
        split_size = [ j-i+1 for i,j in zip(start_pos, end_pos) ]
        NewCommonStructure = self.__class__()
        NewCommonStructure.__init__( split_size )
        C_API.split_commonstructure(self.block_index, NewCommonStructure.block_index,
            self.size, start_pos, end_pos)
        NewCommonStructure.block_palette = self.block_palette.copy()

        for entityNBT in self.entity_nbt :
            EnX = entityNBT["Pos"][0] - self.origin[0]
            EnY = entityNBT["Pos"][1] - self.origin[1]
            EnZ = entityNBT["Pos"][2] - self.origin[2]
            if  not(start_pos[0] <= EnX < end_pos[0]+1 and start_pos[1] <= EnY < end_pos[1]+1
                and start_pos[2] <= EnZ < end_pos[2]+1) : continue
            NewentityNBT = entityNBT.copy()
            NewentityNBT["Pos"][0] = nbt.TAG_Float(EnX - start_pos[0])
            NewentityNBT["Pos"][1] = nbt.TAG_Float(EnY - start_pos[1])
            NewentityNBT["Pos"][2] = nbt.TAG_Float(EnZ - start_pos[2])
            NewCommonStructure.entity_nbt.append(NewentityNBT)

        sizeX, sizeY, sizeZ = self.size[0], self.size[1], self.size[2]
        for nbt_index, blockNBT in self.block_nbt.items() :
            blockX = nbt_index // (sizeY * sizeZ)
            blockY = (nbt_index % (sizeY * sizeZ)) // sizeZ
            blockZ = (nbt_index % (sizeY * sizeZ)) % sizeZ
            if  not(start_pos[0] <= blockX <= end_pos[0] and start_pos[1] <= blockY <= end_pos[1]
                and start_pos[2] <= blockZ <= end_pos[2]) : continue
            NewCommonStructure.set_blockNBT(blockX-start_pos[0], blockY-start_pos[1],
                blockZ-start_pos[2], blockNBT.copy())

        return NewCommonStructure

    


