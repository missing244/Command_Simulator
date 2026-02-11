from . import nbt, MCBELab
from .block import Block
from .__private import TypeCheckList, BiList
from . import StructureAXIOM_BP, StructureBDS, StructureBDX, StructureCONSTRUCTION
from . import StructureCOVSTRUCTURE, StructureIBIMPORT, StructureMCFUNZIP, StructureMCS, StructureNEXUS
from . import StructureNEXUS_NP, StructureRUNAWAY, StructureSCHEM, StructureSCHEMATIC

from typing import Union,Dict,Tuple,Literal,List
import abc, re, io, json, array, itertools, urllib.parse, os, math, zipfile, traceback, zlib
ExecuteTest = re.compile("[ ]*?/?[ ]*?execute[ ]*?(as|at|align|anchored|facing|in|positioned|rotated|if|unless|run)")


class Codecs :
    """
    编解码器类
    ---------------------------------
    * 通过 Codecs.XXXX 调用指定的编解码器
    ---------------------------------
    * 可用类 BDX: 解析/生成 bdx 文件的编解码器
    * 可用类 AXIOM_BP: 解析 axiom_bp 文件的解码器（编码禁用）
    * 可用类 CONSTRUCTION: 解析/生成 construction 文件的编解码器
    * 可用类 BDS: 解析/生成 bds 文件的编解码器
    * 可用类 COVSTRUCTURE: 解析/生成 covstructure 文件的编解码器
    * 可用类 NEXUS_NP: 解析/生成 nexus_np 文件的编解码器
    * 可用类 NEXUS: 解析/生成 nexus 文件的编解码器
    * 可用类 MCSTRUCTURE: 解析/生成 mcstructure 文件的编解码器
    * 可用类 SCHEMATIC: 解析/生成 schematic 文件的编解码器
    * 可用类 SCHEM_V1: 解析/生成 schem 文件的编解码器
    * 可用类 SCHEM_V2: 解析/生成 schem 文件的编解码器
    * 可用类 MIANYANG_V1: 解析/生成 绵阳 json结构文件的编解码器
    * 可用类 MIANYANG_V2: 解析/生成 绵阳 json结构文件的编解码器
    * 可用类 MIANYANG_V3: 解析/生成 绵阳 json结构文件的编解码器
    * 可用类 GANGBAN_V1: 解析/生成 钢板 json结构文件的编解码器
    * 可用类 GANGBAN_V2: 解析/生成 钢板 json结构文件的编解码器
    * 可用类 GANGBAN_V3: 解析/生成 钢板 json结构文件的编解码器
    * 可用类 GANGBAN_V4: 解析/生成 钢板 json结构文件的编解码器
    * 可用类 GANGBAN_V5: 解析/生成 钢板 json结构文件的编解码器
    * 可用类 GANGBAN_V6: 解析/生成 钢板 json结构文件的编解码器
    * 可用类 GANGBAN_V7: 解析/生成 钢板 json结构文件的编解码器
    * 可用类 RUNAWAY: 解析/生成 跑路官方 json结构文件的编解码器
    * 可用类 KBDX: 解析/生成 Kbdx 结构文件的编解码器
    * 可用类 FUHONG_V1: 解析 FUHONG json结构文件的解码器（编码禁用）
    * 可用类 FUHONG_V2: 解析 FUHONG json结构文件的解码器（编码禁用）
    * 可用类 FUHONG_V3: 解析/生成 FUHONG json结构文件的编解码器
    * 可用类 FUHONG_V4: 解析/生成 FUHONG json结构文件的编解码器
    * 可用类 FUHONG_V5: 解析/生成 FUHONG json结构文件的编解码器
    * 可用类 QINGXU_V1: 解析/生成 情绪 json结构文件的编解码器
    * 可用类 MCFUNZIP: 生成 mcfunzip 文件的编码器（解码禁用）
    * 可用类 IBIMPORT: 生成 ibimport 文件的编码器（解码禁用）
    * 可用类 FunctionCommand: 生成 函数命令 zip文件的编码器
    * 可用类 TextCommand: 生成 文本命令 txt文件的编码器
    """

    class CodecsBase(abc.ABC) :

        def __init__(self, Common, IgnoreAir:bool=True, **CodecKwargs):
            from . import CommonStructure
            self.Common:CommonStructure = Common
            self.IgnoreAir:bool = IgnoreAir
            self.CodecKwargs:dict = CodecKwargs

        @abc.abstractmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) -> bool :
            raise NotImplementedError()

        @abc.abstractmethod
        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]) :
            raise NotImplementedError()

        @abc.abstractmethod
        def encode(self, Writer:Union[str, io.BufferedIOBase]) :
            raise NotImplementedError()

    class BDX(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            from . import brotli
            if DataType != "bytes" : return False

            if Data.read(3) != b'BD@' : return False
            try : a = brotli.decompress(Data.read())[0:4]
            except : return False

            if a != b'BDX\0' : return False
            else : return True

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]) :
            CommandBlockID = ["minecraft:command_block", "minecraft:repeating_command_block", 
                "minecraft:chain_command_block"]
            BDX = StructureBDX.BDX_File.from_buffer(Reader)
            PosStart, PosEnd = BDX.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            ConstStr = BDX.const_str

            def Operation_0x05(Oper: StructureBDX.OperationCode.PlaceBlockWithBlockStates1, x:int, y:int, z:int) :
                block = Block(ConstStr[Oper.blockConstantStringID], ConstStr[Oper.blockStatesConstantStringID])
                StructureObject.set_block(x, y, z, block)

            def Operation_0x07(Oper: StructureBDX.OperationCode.PlaceBlock, x:int, y:int, z:int) :
                block = Block(ConstStr[Oper.blockConstantStringID], Oper.blockData)
                StructureObject.set_block(x, y, z, block)

            def Operation_0x0d(Oper: StructureBDX.OperationCode.PlaceBlockWithBlockStates2, x:int, y:int, z:int) :
                block = Block(ConstStr[Oper.blockConstantStringID], Oper.blockStatesString)
                StructureObject.set_block(x, y, z, block)

            def Operation_0x1a(Oper: StructureBDX.OperationCode.SetCommandBlockData, x:int, y:int, z:int) :
                block = StructureObject.get_block(x, y, z)
                if not block.name.endswith("command_block") : return None

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(Oper.command),
                    CustomName = node.string(Oper.customName),
                    ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                    auto = node.byte(int(not Oper.needsRedstone)),
                    TickDelay = node.int(Oper.tickdelay),
                    conditionalMode = node.byte(Oper.conditional),
                    TrackOutput = node.byte(1),
                    Version = node.int(38 if ExecuteTest.match(Oper.command) else 19)
                ).build()
                StructureObject.set_blockNBT(x, y, z, CommandBlockNbt)

                if block.name != CommandBlockID[Oper.mode] : 
                    StructureObject.set_block(x, y, z, Block(CommandBlockID[Oper.mode], block.states) )

            def Operation_0x1b(Oper: StructureBDX.OperationCode.PlaceBlockWithCommandBlockData, x:int, y:int, z:int) :
                block = Block(ConstStr[Oper.blockConstantStringID], Oper.blockData)
                StructureObject.set_block(x, y, z, block)

                block = StructureObject.get_block(x, y, z)
                if not block.name.endswith("command_block") : return None

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(Oper.command),
                    CustomName = node.string(Oper.customName),
                    ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                    auto = node.byte(int(not Oper.needsRedstone)),
                    TickDelay = node.int(Oper.tickdelay),
                    conditionalMode = node.byte(Oper.conditional),
                    TrackOutput = node.byte(1),
                    Version = node.int(38 if ExecuteTest.match(Oper.command) else 19),
                ).build()
                StructureObject.set_blockNBT(x, y, z, CommandBlockNbt)

                if block.name != CommandBlockID[Oper.mode] : 
                    StructureObject.set_block( x, y, z, Block(CommandBlockID[Oper.mode], block.states) )

            def Operation_0x20(Oper: StructureBDX.OperationCode.PlaceRuntimeBlock, x:int, y:int, z:int) :
                BlockID, Data = StructureBDX.RunTimeID_117[Oper.runtimeId]
                block = Block(BlockID, Data)
                StructureObject.set_block(x, y, z, block)

            def Operation_0x22(Oper: StructureBDX.OperationCode.PlaceRuntimeBlockWithCommandBlockData, x:int, y:int, z:int) :
                BlockID, Data = StructureBDX.RunTimeID_117[Oper.runtimeId]
                block = Block(BlockID, Data)
                StructureObject.set_block(x, y, z, block)

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(Oper.command),
                    CustomName = node.string(Oper.customName),
                    ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                    auto = node.byte(int(not Oper.needsRedstone)),
                    TickDelay = node.int(Oper.tickdelay),
                    conditionalMode = node.byte(Oper.conditional),
                    TrackOutput = node.byte(1),
                    Version = node.int(38 if ExecuteTest.match(Oper.command) else 19),
                ).build()
                StructureObject.set_blockNBT(x, y, z, CommandBlockNbt)

                if BlockID != CommandBlockID[Oper.mode] : 
                    StructureObject.set_block( x, y, z, Block(CommandBlockID[Oper.mode], block.states) )

            def Operation_0x24(Oper: StructureBDX.OperationCode.PlaceCommandBlockWithCommandBlockData, x:int, y:int, z:int) :
                block = Block(CommandBlockID[Oper.mode], Oper.data)
                StructureObject.set_block(x, y, z, block)

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(Oper.command),
                    CustomName = node.string(Oper.customName),
                    ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                    auto = node.byte(int(not Oper.needsRedstone)),
                    conditionalMode = node.byte(Oper.conditional),
                    TickDelay = node.int(Oper.tickdelay),
                    TrackOutput = node.byte(1),
                    Version = node.int(19),
                ).build()
                StructureObject.set_blockNBT( x, y, z, CommandBlockNbt )

            def Operation_0x25(Oper: StructureBDX.OperationCode.PlaceRuntimeBlockWithChestData, x:int, y:int, z:int) :
                BlockID, Data = StructureBDX.RunTimeID_117[Oper.runtimeId]
                block = Block(BlockID, Data)
                StructureObject.set_block(x, y, z, block)
                
                ContainerNbt = MCBELab.GenerateBlockEntityNBT(block.name)
                if not ContainerNbt : return None

                node = nbt.NBT_Builder()
                for Item in Oper.ChestData :
                    ContainerNbt["Items"].append( node.compound(
                        Count = node.byte(Item["count"]),
                        Damage = node.short(Item["data"]),
                        Name = node.string(Item["name"]),
                        Slot = node.byte(Item["slotID"]),
                        tag = node.compound()
                    ).build() )
                StructureObject.set_blockNBT( x, y, z, ContainerNbt )

            def Operation_0x28(Oper: StructureBDX.OperationCode.PlaceBlockWithChestData, x:int, y:int, z:int) :
                block = Block(ConstStr[Oper.blockConstantStringID], Oper.blockData)
                StructureObject.set_block(x, y, z, block)

                ContainerNbt = MCBELab.GenerateBlockEntityNBT(block.name)
                if not ContainerNbt : return None

                node = nbt.NBT_Builder()
                for Item in Oper.ChestData :
                    ContainerNbt["Items"].append( node.compound(
                        Count = node.byte(Item["count"]),
                        Damage = node.short(Item["data"]),
                        Name = node.string(Item["name"]),
                        Slot = node.byte(Item["slotID"]),
                        tag = node.compound()
                    ).build() )
                StructureObject.set_blockNBT( x, y, z, ContainerNbt )

            def Operation_0x29(Oper: StructureBDX.OperationCode.PlaceBlockWithNBTData, x:int, y:int, z:int) :
                block = Block(ConstStr[Oper.blockConstantStringID], ConstStr[Oper.blockStatesConstantStringID])
                StructureObject.set_block(x, y, z, block)
                StructureObject.set_blockNBT(x, y, z, Oper.nbt)

            FUNCTION = {0x05:Operation_0x05, 0x07:Operation_0x07, 0x0d:Operation_0x0d,
            0x1a:Operation_0x1a, 0x1b:Operation_0x1b, 0x20:Operation_0x20, 0x21:Operation_0x20,
            0x22:Operation_0x22, 0x23:Operation_0x22, 0x24:Operation_0x24, 0x25:Operation_0x25,
            0x26:Operation_0x25, 0x28:Operation_0x28, 0x29:Operation_0x29}
            
            for PosX, PosY, PosZ, Oper in BDX.get_blocks() :
                if Oper.operation_code not in FUNCTION : continue
                FUNCTION[Oper.operation_code](Oper, PosX-PosStart[0], PosY-PosStart[1], PosZ-PosStart[2])

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            BDX = StructureBDX.BDX_File()
            PlaceBlockWithNBTData = StructureBDX.OperationCode.PlaceBlockWithNBTData
            PlaceBlockWithBlockStates = StructureBDX.OperationCode.PlaceBlockWithBlockStates1
            AddXValue = StructureBDX.OperationCode.AddXValue
            AddYValue = StructureBDX.OperationCode.AddYValue
            AddZValue = StructureBDX.OperationCode.AddZValue
            AddInt32XValue = StructureBDX.OperationCode.AddInt32XValue
            AddInt32YValue = StructureBDX.OperationCode.AddInt32YValue
            AddInt32ZValue = StructureBDX.OperationCode.AddInt32ZValue
            append_function = super(TypeCheckList, BDX.operation_list).append
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )

            for Block in self.block_palette :
                state_str = json.dumps(dict(Block.states), separators=(',', '='))
                state_str = f"[{ state_str[1:len(state_str)-1] }]"
                BDX.const_str.append(Block.name)
                BDX.const_str.append(state_str)
            
            s_posx, s_posy, s_posz = 0, 0, 0
            for index, (block_index, (pos_x, pos_y, pos_z)) in Generator :                
                if block_index < 0 : continue
                if IgnoreAir and self.block_palette[block_index].name == "minecraft:air" : continue

                if pos_x != s_posx : 
                    pos_sub = pos_x - s_posx
                    append_function(AddXValue() if pos_sub == 1 else AddInt32XValue(pos_sub))
                    s_posx = pos_x
                if pos_y != s_posy : 
                    pos_sub = pos_y - s_posy
                    append_function(AddYValue() if pos_sub == 1 else AddInt32YValue(pos_sub))
                    s_posy = pos_y
                if pos_z != s_posz : 
                    pos_sub = pos_z - s_posz
                    append_function(AddZValue() if pos_sub == 1 else AddInt32ZValue(pos_sub))
                    s_posz = pos_z

                if index in self.block_nbt : append_function(
                    PlaceBlockWithNBTData(2*block_index, 2*block_index+1, self.block_nbt[index]) )
                else : append_function( PlaceBlockWithBlockStates(2*block_index, 2*block_index+1) )

            BDX.save_as(Writer)

    class AXIOM_BP(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False
            try : return StructureAXIOM_BP.AxiomBP.verify(Data)
            except : return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureAXIOM_BP.AxiomBP.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__(Struct1.size)
            StructureObject.origin = Struct1.origin
            StructureObject.block_index = Struct1.block_index
            StructureObject.block_nbt = {}
            StructureObject.entity_nbt = TypeCheckList().setChecker(nbt.TAG_Compound)

            block_list = [None] * len(Struct1.block_palette)
            for index, block in enumerate(Struct1.block_palette) :
                java_name = block.get("Name", "minecraft:air")
                java_props = block.get("Properties", {})
                if not isinstance(java_props, dict) : java_props = {}

                parsed_props = {}
                for k, v in java_props.items() :
                    if not isinstance(k, str) : continue
                    if isinstance(v, str) :
                        if v == "true" : parsed_props[k] = True
                        elif v == "false" : parsed_props[k] = False
                        else : parsed_props[k] = v
                    else : parsed_props[k] = str(v)

                try :
                    be_block = MCBELab.JE_Transfor_BE_Block(java_name, parsed_props)
                    block_list[index] = Block(*be_block)
                except :
                    block_list[index] = Block("minecraft:air")

            StructureObject.block_palette.__init__(block_list)

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            raise RuntimeError("AXIOM_BP 不支持编码")

    class CONSTRUCTION(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False
            try : return StructureCONSTRUCTION.Construction.verify(Data)
            except : return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureCONSTRUCTION.Construction.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__(Struct1.size)
            StructureObject.origin = Struct1.origin
            StructureObject.block_index = Struct1.block_index
            StructureObject.block_nbt = Struct1.block_nbt

            block_list = [None] * len(Struct1.block_palette)
            for index, block in enumerate(Struct1.block_palette) :
                namespace = block.get("namespace", "minecraft")
                blockname = block.get("blockname", "unknown")
                properties = block.get("properties", {})
                if not isinstance(properties, dict) : properties = {}
                if "__version__" in properties : del properties["__version__"]

                block_id = f"{namespace}:{blockname}" if ":" not in blockname else blockname
                try : block_list[index] = Block(block_id, properties)
                except : block_list[index] = Block(block_id, {})
            StructureObject.block_palette.__init__(block_list)

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            self = self.Common
            Struct1 = StructureCONSTRUCTION.Construction()

            Struct1.size = array.array("i", self.size)
            Struct1.origin = array.array("i", self.origin)
            Struct1.block_index = array.array("i", self.block_index)
            Struct1.block_nbt = {k:v.copy() for k,v in self.block_nbt.items()}

            for block in self.block_palette :
                namespace, blockname = (block.name.split(":", 1) if ":" in block.name else ("minecraft", block.name))
                Struct1.block_palette.append({
                    "namespace" : namespace,
                    "blockname" : blockname,
                    "properties" : dict(block.states)
                })

            Struct1.save_as(Writer)

    class BDS(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False
            try : return StructureBDS.BDS.verify(Data)
            except : return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureBDS.BDS.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__(Struct1.size)
            StructureObject.origin = Struct1.origin
            StructureObject.block_index = Struct1.block_index
            StructureObject.block_nbt = Struct1.block_nbt

            block_list = [None] * len(Struct1.block_palette)
            for index, block in enumerate(Struct1.block_palette) :
                name = block.get("name", "minecraft:air")
                states = block.get("states", {})
                data_value = block.get("data", 0)
                states_string = block.get("states_string", "")

                try :
                    if isinstance(states, dict) and states : block_list[index] = Block(name, states)
                    elif isinstance(states_string, str) and states_string : block_list[index] = Block(name, states_string)
                    else : block_list[index] = Block(name, data_value)
                except :
                    try : block_list[index] = Block(name, {})
                    except : block_list[index] = Block("minecraft:air", {})
            StructureObject.block_palette.__init__(block_list)

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            self = self.Common
            Struct1 = StructureBDS.BDS()

            Struct1.size = array.array("i", self.size)
            Struct1.origin = array.array("i", self.origin)
            Struct1.block_index = array.array("i", self.block_index)
            Struct1.block_nbt = {k:v.copy() for k,v in self.block_nbt.items()}

            for block in self.block_palette :
                data_value = 0
                if isinstance(getattr(block, "dataValue", None), (tuple, list)) and len(block.dataValue) > 1 :
                    data_value = int(block.dataValue[1])
                Struct1.block_palette.append({
                    "name" : block.name,
                    "states" : dict(block.states),
                    "data" : data_value,
                    "states_string" : ""
                })

            Struct1.save_as(Writer)

    class COVSTRUCTURE(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            if not isinstance(Data, dict) : return False

            size = Data.get("size", Data.get("dimensions", None))
            if not (isinstance(size, list) and len(size) >= 3) : return False

            if "structure" in Data and isinstance(Data["structure"], dict) :
                struct_obj = Data["structure"]
                return ("block_indices" in struct_obj or "blocks" in struct_obj)

            return ("block_indices" in Data or "blocks" in Data)

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureCOVSTRUCTURE.CovStructure.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__(Struct1.size)
            StructureObject.origin = Struct1.origin
            StructureObject.block_index = Struct1.block_index
            StructureObject.block_nbt = Struct1.block_nbt
            StructureObject.entity_nbt = Struct1.entity_nbt

            block_list = [None] * len(Struct1.block_palette)
            for index, block in enumerate(Struct1.block_palette) :
                name = block.get("name", "minecraft:air")
                states = block.get("states", {})
                data_value = block.get("data", 0)
                states_string = block.get("states_string", "")

                try :
                    if isinstance(states, dict) and states : block_list[index] = Block(name, states)
                    elif isinstance(states_string, str) and states_string : block_list[index] = Block(name, states_string)
                    else : block_list[index] = Block(name, data_value)
                except :
                    try : block_list[index] = Block(name, {})
                    except : block_list[index] = Block("minecraft:air", {})
            StructureObject.block_palette.__init__(block_list)

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            self = self.Common
            Struct1 = StructureCOVSTRUCTURE.CovStructure()

            Struct1.size = array.array("i", self.size)
            Struct1.origin = array.array("i", self.origin)
            Struct1.block_index = array.array("i", self.block_index)
            Struct1.block_nbt = {k:v.copy() for k,v in self.block_nbt.items()}
            Struct1.entity_nbt = TypeCheckList(i.copy() for i in self.entity_nbt).setChecker(nbt.TAG_Compound)

            for block in self.block_palette :
                data_value = 0
                if isinstance(getattr(block, "dataValue", None), (tuple, list)) and len(block.dataValue) > 1 :
                    data_value = int(block.dataValue[1])
                Struct1.block_palette.append({
                    "name" : block.name,
                    "states" : dict(block.states),
                    "data" : data_value,
                    "version" : 17959425
                })

            Struct1.save_as(Writer)

    class NEXUS_NP(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False
            try : return StructureNEXUS_NP.NexusNP.verify(Data)
            except : return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureNEXUS_NP.NexusNP.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__(Struct1.size)
            StructureObject.origin = Struct1.origin
            StructureObject.block_index = Struct1.block_index
            StructureObject.block_nbt = Struct1.block_nbt

            block_list = [None] * len(Struct1.block_palette)
            for index, block in enumerate(Struct1.block_palette) :
                name = block.get("name", "minecraft:air")
                states = block.get("states", {})
                data_value = block.get("data", 0)
                states_string = block.get("states_string", "")

                try :
                    if isinstance(states, dict) and states : block_list[index] = Block(name, states)
                    elif isinstance(states_string, str) and states_string : block_list[index] = Block(name, states_string)
                    else : block_list[index] = Block(name, data_value)
                except :
                    try : block_list[index] = Block(name, {})
                    except : block_list[index] = Block("minecraft:air", {})
            StructureObject.block_palette.__init__(block_list)

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            self = self.Common
            Struct1 = StructureNEXUS_NP.NexusNP()

            Struct1.size = array.array("i", self.size)
            Struct1.origin = array.array("i", self.origin)
            Struct1.block_index = array.array("i", self.block_index)
            Struct1.block_nbt = {k:v.copy() for k,v in self.block_nbt.items()}

            for block in self.block_palette :
                data_value = 0
                if isinstance(getattr(block, "dataValue", None), (tuple, list)) and len(block.dataValue) > 1 :
                    data_value = int(block.dataValue[1])
                Struct1.block_palette.append({
                    "name" : block.name,
                    "states" : dict(block.states),
                    "data" : data_value,
                    "states_string" : ""
                })

            Struct1.save_as(Writer)


    class NEXUS(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False
            try : return StructureNEXUS.Nexus.verify(Data)
            except : return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            password = self.CodecKwargs.get("password", "")
            if not isinstance(password, str) : password = str(password)
            Struct1 = StructureNEXUS.Nexus.from_buffer(Reader, password=password)

            StructureObject = self.Common
            StructureObject.__init__(Struct1.size)
            StructureObject.origin = Struct1.origin
            StructureObject.block_index = Struct1.block_index
            StructureObject.entity_nbt = Struct1.entity_nbt
            StructureObject.block_nbt = Struct1.block_nbt

            for key, value in StructureObject.block_nbt.items() :
                if "block_entity_data" not in value : continue
                StructureObject.block_nbt[key] = value["block_entity_data"]

            block_list = [None] * len(Struct1.block_palette)
            for index, block in enumerate(Struct1.block_palette) :
                name = block["name"].value
                state = {i:(bool(j.value) if isinstance(j, nbt.TAG_Byte) else j.value) for i,j in block["states"].items()}
                block_list[index] = Block(name, state)
            StructureObject.block_palette.__init__(block_list)

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            Common = self.Common
            password = self.CodecKwargs.get("password", "")
            author = self.CodecKwargs.get("author", "")
            compression = self.CodecKwargs.get("compression", StructureNEXUS.Nexus.COMP_BROTLI)

            if not isinstance(password, str) : password = str(password)
            if not isinstance(author, str) : author = str(author)
            try : compression = int(compression)
            except : compression = StructureNEXUS.Nexus.COMP_BROTLI

            Struct1 = StructureNEXUS.Nexus()
            Struct1.size = array.array("i", Common.size)
            Struct1.origin = array.array("i", Common.origin)
            Struct1.block_index = array.array("i", Common.block_index)
            Struct1.block_palette = TypeCheckList(i.to_nbt() for i in Common.block_palette).setChecker(nbt.TAG_Compound)
            Struct1.entity_nbt = TypeCheckList(i.copy() for i in Common.entity_nbt).setChecker(nbt.TAG_Compound)
            Struct1.block_nbt = {k:nbt.TAG_Compound({"block_entity_data":v.copy()}) for k,v in Common.block_nbt.items()}

            Struct1.save_as(Writer, password=password, author=author, compression=compression)

    class MCSTRUCTURE(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "nbt" : return False
            NBT = Data

            if "size" in NBT and "structure_world_origin" in NBT and 'structure' in NBT : return True
            else : return False

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]):
            MCS = StructureMCS.Mcstructure.from_buffer(Reader)
            
            StructureObject = self.Common
            StructureObject.size = MCS.size
            StructureObject.origin = MCS.origin
            StructureObject.block_index = MCS.block_index
            StructureObject.contain_index = {i:j for i,j in enumerate(MCS.contain_index) if j >= 0}
            StructureObject.entity_nbt = MCS.entity_nbt
            StructureObject.block_nbt = MCS.block_nbt

            for key, value in StructureObject.block_nbt.items() :
                if "block_entity_data" not in value : continue
                StructureObject.block_nbt[key] = value["block_entity_data"]

            block_list = [None] * len(MCS.block_palette)
            for index, block in enumerate(MCS.block_palette) :
                name = block["name"].value
                state = {i:(bool(j.value) if isinstance(j, nbt.TAG_Byte) else j.value) for i,j in block["states"].items()}
                block_list[index] = Block(name, state)
                
            StructureObject.block_palette.__init__(block_list)

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            self = self.Common
            MCS = StructureMCS.Mcstructure()

            MCS.size = self.size
            MCS.origin = self.origin
            MCS.block_index = array.array("i", self.block_index)
            MCS.contain_index = array.array("i", b"\xff\xff\xff\xff" * len(self.block_index))
            MCS.block_palette = TypeCheckList(i.to_nbt() for i in self.block_palette)
            MCS.entity_nbt = self.entity_nbt
            MCS.block_nbt = self.block_nbt.copy()

            for i,j in self.contain_index.items() : MCS.contain_index[i] = j

            for key, value in MCS.block_nbt.items() :
                MCS.block_nbt[key] = nbt.TAG_Compound({"block_entity_data":value})
            MCS.save_as(Writer)

    class SCHEMATIC(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "nbt" : return False

            NBT = Data
            if "Width" in NBT and "Height" in NBT and 'Length' in NBT and \
                "Blocks" in NBT and 'Data' in NBT : return True
            else : return False

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]):
            from .C_API import codecs_parser_schematic, handling_waterlog
            SCHMATIC = StructureSCHEMATIC.Schematic.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__( SCHMATIC.size )
            RunTimeBlock = StructureSCHEMATIC.RuntimeID_to_Block

            NBTBlockBit = array.array("B", b"\x00"*256)
            for index, blockname in enumerate(RunTimeBlock) : 
                UID = MCBELab.GetNbtUID(blockname)
                if UID : NBTBlockBit[index] = UID

            BlockPaletteArray = array.array("H", b"\x00\x00"*65536)
            NBTDict = codecs_parser_schematic(SCHMATIC.block_index, SCHMATIC.block_data, 
                StructureObject.block_index, BlockPaletteArray, NBTBlockBit, SCHMATIC.size)

            BlockList = [None] * max(BlockPaletteArray)
            for block_id, block_index in enumerate(BlockPaletteArray) :
                if not block_index : continue
                BlockList[block_index-1] = Block(RunTimeBlock[block_id >> 8], block_id & 255)
            StructureObject.block_palette.__init__( [Block("minecraft:air")] + BlockList )

            for key, value in NBTDict.items() :
                block = StructureObject.block_palette[StructureObject.block_index[key]]
                StructureObject.block_nbt[key] = MCBELab.GenerateBlockEntityNBT(block.name)

        def encode(self, Writer:Union[str, io.BufferedIOBase]) :
            raise RuntimeError(f"{Writer} 并不支持序列化数据对象")
            IgnoreAir, self = self.IgnoreAir, self.Common
            SCHMATIC = StructureSCHEMATIC.Schematic()
            for i in range(3) : 
                SCHMATIC.size[i] = self.size[i]
                SCHMATIC.origin[i] = self.origin[i]

            StructX, StructY, StructZ = self.size[0], self.size[1], self.size[2]
            SCHMATIC.block_index = array.array("B", b"\x00" * len(self.block_index))
            SCHMATIC.block_data = array.array("B", b"\x00" * len(self.block_index))

            PosIter = itertools.product(range(self.size[0]), range(self.size[1]), range(self.size[2]))
            for block_index, (posx, posy, posz) in zip(self.block_index, PosIter) :
                if block_index < 0 : continue
                block:Block = self.block_palette[ block_index ]
                if block.name not in StructureSCHEMATIC.Block_to_RuntimeID : continue
                Index = posy * StructZ * StructX + posz * StructX + posx

                SCHMATIC.block_index[Index] = block.dataValue[0]
                SCHMATIC.block_data[Index] = block.dataValue[1]

            SCHMATIC.save_as(Writer)

    class SCHEM_V1(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "nbt" : return False

            NBT = Data
            if "Version" in NBT and "Width" in NBT and "Height" in NBT and 'Length' in NBT and \
                "BlockData" in NBT and 'Palette' in NBT : return True
            else : return False

        def operation_structure(self, Schma_File:StructureSCHEM.Schem_V1) :
            from .C_API import codecs_parser_schem, handling_waterlog
            StructureObject = self.Common
            StructureObject.__init__( Schma_File.size )

            blocks:List[Block] = [None] * len(Schma_File.block_palette)
            for index, block in Schma_File.block_palette.items() : 
                block_data = MCBELab.JE_Transfor_BE_Block(block)
                blocks[index] = Block(block_data[0], block_data[1], block_data[2])
            StructureObject.block_palette.__init__(blocks)

            NBTBlockBit = array.array("B", b"\x00"*len(StructureObject.block_palette))
            for index, block in enumerate(StructureObject.block_palette) : 
                UID = MCBELab.GetNbtUID(block.name)
                if UID : NBTBlockBit[index] = UID

            NBTDict = codecs_parser_schem(Schma_File.block_index, StructureObject.block_index,
                NBTBlockBit, Schma_File.size)
            for key, value in NBTDict.items() :
                block = StructureObject.block_palette[StructureObject.block_index[key]]
                StructureObject.block_nbt[key] = MCBELab.GenerateBlockEntityNBT(block.name)

            if handling_waterlog(StructureObject.block_index, StructureObject.contain_index,
                StructureObject.block_palette, StructureObject.size) :
                StructureObject.block_palette.append( Block("water") )

            """
                O_X, O_Y, O_Z = Schma_File.size
                block_index, pos_x, pos_y, pos_z = 0, 0, 0, 0
                for index_data in Schma_File.block_index :
                    block_index |= 0b0111_1111 & index_data
                    if index_data >= 0 :
                        StructureObject.set_block(pos_x, pos_y, pos_z, block_index)
                        nbtdata = MCBELab.GenerateContainerNBT(blocks[block_index].name)
                        if nbtdata : StructureObject.set_blockNBT(pos_x, pos_y, pos_z, nbtdata)
                        block_index = 0
                        pos_x += 1
                        if pos_x >= O_X : pos_x = 0 ; pos_z += 1
                        if pos_z >= O_Z : pos_z = 0 ; pos_y += 1
            """
            
        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]):
            Schma_File = StructureSCHEM.Schem_V1.from_buffer(Reader)
            self.operation_structure(Schma_File)

        def encode(self, Writer:Union[str, io.BufferedIOBase]) :
            raise RuntimeError(f"{Writer} 并不支持序列化数据对象")

    class SCHEM_V2(SCHEM_V1) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "nbt" : return False

            NBT = Data
            if "Version" in NBT and "Width" in NBT and "Height" in NBT and \
                'Length' in NBT and "Blocks" in NBT : return True
            else : return False

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]):
            Schma_File = StructureSCHEM.Schem_V2.from_buffer(Reader)
            self.operation_structure(Schma_File)

    class SCHEM_V3(SCHEM_V1) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "nbt" : return False

            NBT = Data
            if "Schematic" not in NBT : return False
            if "Version" in NBT["Schematic"] and "Width" in NBT["Schematic"] and "Height" in NBT["Schematic"] and \
                'Length' in NBT["Schematic"] and "Blocks" in NBT["Schematic"] : return True
            else : return False

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]):
            Schma_File = StructureSCHEM.Schem_V3.from_buffer(Reader)
            self.operation_structure(Schma_File)

    class LITEMATIC_V1(CodecsBase) :
        
        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "nbt" : return False
            NBT = Data

            if "Version" in NBT and 'Regions' in NBT : return True
            else : return False

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]) :
            from .C_API import codecs_parser_litematic, handling_waterlog
            LiteNBT = nbt.read_from_nbt_file(Reader, "gzip", "big").get_tag()
            Regions:Dict[str, nbt.TAG_Compound] = LiteNBT["Regions"]
            StructureObject = self.Common
            
            #计算所有区域合并后的最小最大坐标
            PosListMin, PosListMax = {"x":[], "y":[], "z":[]}, {"x":[], "y":[], "z":[]}
            for Region, PosType in itertools.product(Regions.values(), "xyz") :
                pos1 = Region["Position"][PosType].value 
                pos2 = Region["Size"][PosType].value
                if pos2 < 0 : 
                    pos3 = pos1 + pos2
                    pos1 -= 1
                    pos1, pos3 = pos3, pos1
                else : pos3 = pos1 + pos2 - 1
                PosListMin[PosType].append(pos1)
                PosListMax[PosType].append(pos3)
            for key, val in PosListMin.items() : PosListMin[key] = min(val)
            for key, val in PosListMax.items() : PosListMax[key] = max(val)
            StructureObject.__init__( [PosListMax[key]-PosListMin[key]+1 for key in "xyz"] )
            StructureObject.block_palette.append( Block("air") )
            
            #计算区域的最小坐标点，方块调色板，方块数组
            OriginX, OriginY, OriginZ = PosListMin["x"], PosListMin["y"], PosListMin["z"]
            RegionOrigin:List[int] = []
            RegionSize:List[int] = []
            for Region, PosType in itertools.product(Regions.values(), "xyz") :
                if PosType == "x" : RegionOrigin.clear()
                pos1 = Region["Position"][PosType].value 
                pos2 = Region["Size"][PosType].value
                if pos2 < 0 : pos1 = pos1 + pos2
                RegionOrigin.append(pos1)
                RegionSize.append( abs(pos2) )
                if PosType != "z" : continue

                IndexMap = array.array("H", b"\x00\x00"*len(Region['BlockStatePalette']))
                for index, JE_Block in enumerate(Region['BlockStatePalette']) :
                    JE_Block_ID = JE_Block["Name"].value
                    JE_Block_State = {}
                    for key, val in JE_Block.get("Properties", {}).items() :
                        if val.value == "true" : JE_Block_State[key] = True
                        elif val.value == "false" : JE_Block_State[key] = False
                        else : JE_Block_State[key] = val.value
                    BE_Block = MCBELab.JE_Transfor_BE_Block(JE_Block_ID, JE_Block_State)
                    IndexMap[index] = StructureObject.block_palette.append( Block(*BE_Block) )

                NBTBlockBit = array.array("B", b"\x00"*len(StructureObject.block_palette))
                for index, block in enumerate(StructureObject.block_palette) : 
                    UID = MCBELab.GetNbtUID(block.name)
                    if UID : NBTBlockBit[index] = UID

                bits_per_block = max(2, math.ceil(math.log2( len(IndexMap) )))

                NBTDict = codecs_parser_litematic(
                    IndexMap, NBTBlockBit, Region["BlockStates"].value, StructureObject.block_index, 
                    OriginX, OriginY, OriginZ,
                    StructureObject.size[0], StructureObject.size[1], StructureObject.size[2],
                    RegionOrigin[0], RegionOrigin[1], RegionOrigin[2],
                    RegionSize[0], RegionSize[1], RegionSize[2],
                    bits_per_block)

                #print( max(StructureObject.block_index), len(StructureObject.block_palette) )

                for key, value in NBTDict.items() :
                    block = StructureObject.block_palette[StructureObject.block_index[key]]
                    StructureObject.block_nbt[key] = MCBELab.GenerateBlockEntityNBT(block.name)

                if handling_waterlog(StructureObject.block_index, StructureObject.contain_index,
                    StructureObject.block_palette, StructureObject.size) :
                    StructureObject.block_palette.append( Block("water") )

        def encode(self, Writer:Union[str, io.BufferedIOBase]) :
            raise RuntimeError(f"{Writer} 并不支持序列化数据对象")

    class JAVASTRUCTURE(CodecsBase) :
        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "nbt" : return False
            NBT = Data

            if "blocks" in NBT and 'palette' in NBT and 'size' in NBT : return True
            else : return False

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]) :
            from .C_API import handling_waterlog
            StructureNBT = nbt.read_from_nbt_file(Reader, "gzip", "big").get_tag()
            StructureObject = self.Common
            size = [i.value for i in StructureNBT["size"]]
            StructureObject.__init__( size )
            
            BlockList = [None] * len(StructureNBT["palette"])
            AirTest = False
            for block_index, block_data  in enumerate(StructureNBT["palette"]) :
                java_id = block_data["Name"].value
                java_state = {}
                for key, val in block_data.get("Properties", {}).items() :
                    if val.value == "true" : java_state[key] = True
                    elif val.value == "false" : java_state[key] = False
                    else : java_state[key] = val.value
                BE_Block = MCBELab.JE_Transfor_BE_Block(java_id, java_state)
                if BE_Block[0] == "minecraft:air" : AirTest = True
                BlockList[block_index] = Block(*BE_Block)
            if AirTest : StructureObject.block_palette.__init__( BlockList )
            else : StructureObject.block_palette.__init__( [Block("air")] + BlockList )

            for struct_block in StructureNBT["blocks"] :
                Posx = struct_block["pos"][0].value
                Posy = struct_block["pos"][1].value
                Posz = struct_block["pos"][2].value
                Paletteid = struct_block["state"].value
                if AirTest : StructureObject.set_block(Posx, Posy, Posz, Paletteid)
                else : StructureObject.set_block(Posx, Posy, Posz, Paletteid+1)

            if handling_waterlog(StructureObject.block_index, StructureObject.contain_index,
                StructureObject.block_palette, StructureObject.size) :
                StructureObject.block_palette.append( Block("water") )

        def encode(self, Writer:Union[str, io.BufferedIOBase]) :
            raise RuntimeError(f"{Writer} 并不支持序列化数据对象")

    class MIANYANG_V1(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, dict) and ("chunkedBlocks" in Json1) \
                and ("namespaces" in Json1)and ("totalBlocks" in Json1) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.MianYang_V1.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            CommandMatch = re.compile('(?<=Command:").*(?=",CustomName)', re.DOTALL)
            CustomNameMatch = re.compile('(?<=CustomName:").*(?=",ExecuteOnFirstTick)', re.DOTALL)
            AutoMatch = re.compile('(?<=auto:)-?[0-9]+(?=b)')
            TickDelayMatch = re.compile('(?<=TickDelay:)-?[0-9]+(?=,)')
            VersionMatch = re.compile('(?<=Version:)-?[0-9]+(?=,)')
            for chunk in Struct1.chunks :
                o_x, o_z = chunk["startX"]-PosStart[0], chunk["startZ"]-PosStart[2]
                for block in chunk["blocks"] :
                    posx, posy, posz = o_x + block[2], block[3] - PosStart[1], o_z + block[4]
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Struct1.block_palette[block[0]], block[1])
                    block_obj = Block(Ra_ID, Ra_State)
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    try : BlockJsonData = json.loads(block[-1])
                    except : continue
                    nbtstr = urllib.parse.unquote(BlockJsonData['blockCompleteNBT'])

                    m1 = CommandMatch.search(nbtstr)
                    m2 = CustomNameMatch.search(nbtstr)
                    m3 = AutoMatch.search(nbtstr)
                    m4 = TickDelayMatch.search(nbtstr)
                    m5 = VersionMatch.search(nbtstr)

                    node = nbt.NBT_Builder()
                    CommandBlockNbt = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(m1.group() if m1 else ""),
                        CustomName = node.string(m2.group() if m2 else ""),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(int( m3.group() if m3 else 0 )),
                        TickDelay = node.int(int( m4.group() if m4 else 0 )),
                        conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                        TrackOutput = node.byte(1),
                        Version = node.int(int( m5.group() if m5 else 19 )),
                    ).build()
                    StructureObject.set_blockNBT(posx, posy, posz, CommandBlockNbt)

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.MianYang_V1()
            nbtstr = '{Command:"%s",CustomName:"%s",ExecuteOnFirstTick:0b,LPCommandMode:%s,' + \
                'LPCondionalMode:%sb,LPRedstoneMode:%sb,LastExecution:0l,LastOutput:"",' + \
                'LastOutputParams:[],SuccessCount:0,TickDelay:%s,TrackOutput:1b,' + \
                'Version:%s,auto:%sb,conditionMet:%sb,powered:0b}'
            LPCommandMode = {"minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2, "minecraft:command_block":0}

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            Chunks:Dict[Tuple[int,int], dict] = {}
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[ block_index ]
                BlockID, BlockState, dataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and block.name == "minecraft:air" : continue

                realX, realY, realZ = o_x + posx, o_y + posy, o_z + posz
                chunk_pos = (realX//16*16, realZ//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = {
                    "startX":chunk_pos[0], "startZ":chunk_pos[1], "blocks":[]}
                
                chunk_block = [block_index, dataValue, realX-chunk_pos[0], realY, realZ-chunk_pos[1]]
                Chunks[chunk_pos]["blocks"].append(chunk_block)

                if index not in self.block_nbt : continue
                if block.name not in LPCommandMode : continue

                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    name = node.string(BlockID),
                    states = node.compound(
                        conditional_bit=node.byte(BlockState["conditional_bit"]),
                        facing_direction=node.int(BlockState["facing_direction"])
                    ),
                    val = node.short(dataValue),
                    version = node.int(17959425),
                ).build()

                NBTObj = self.block_nbt[index]
                BlockSNbtIO = io.StringIO()
                nbt.write_to_snbt_file(BlockSNbtIO, BlockData)
                chunk_block.append(json.dumps({
                    "blockNBT":urllib.parse.quote(BlockSNbtIO.getvalue()),
                    "blockCompleteNBT":urllib.parse.quote(nbtstr % (
                        NBTObj["Command"].value, NBTObj["CustomName"].value, LPCommandMode[BlockID],
                        int(BlockState["conditional_bit"]), int(not NBTObj["auto"].value),
                        NBTObj["TickDelay"].value, NBTObj["Version"].value, NBTObj["auto"].value, 
                        int(BlockState["conditional_bit"]) ))
                }))

            Struct1.chunks.extend(Chunks.values())
            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)

    class MIANYANG_V2(CodecsBase) :
        
        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, dict) and ("chunkedBlocks" in Json1) \
                and ("namespaces" in Json1) and ("totB" in Json1): return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.MianYang_V2.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            CommandMatch = re.compile('(?<=Command:").*(?=",CustomName)', re.DOTALL)
            CustomNameMatch = re.compile('(?<=CustomName:").*(?=",ExecuteOnFirstTick)', re.DOTALL)
            AutoMatch = re.compile('(?<=auto:)-?[0-9]+(?=b)')
            TickDelayMatch = re.compile('(?<=TickDelay:)-?[0-9]+(?=,)')
            VersionMatch = re.compile('(?<=Version:)-?[0-9]+(?=,)')

            for chunk in Struct1.chunks :
                o_x, o_z = chunk["startX"]-PosStart[0], chunk["startZ"]-PosStart[2]
                for block in chunk["blocks"] :
                    posx, posy, posz = o_x + block[2], block[3] - PosStart[1], o_z + block[4]
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Struct1.block_palette[block[0]], block[1])
                    block_obj = Block(Ra_ID, Ra_State)
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    try : BlockJsonData = json.loads(block[-1])
                    except : continue
                    nbtstr = urllib.parse.unquote(BlockJsonData['blockCompleteNBT'])
                    
                    m1 = CommandMatch.search(nbtstr)
                    m2 = CustomNameMatch.search(nbtstr)
                    m3 = AutoMatch.search(nbtstr)
                    m4 = TickDelayMatch.search(nbtstr)
                    m5 = VersionMatch.search(nbtstr)

                    if block_obj.name.endswith("command_block") : 
                        node = nbt.NBT_Builder()
                        CommandBlockNbt = node.compound(
                            id = node.string("CommandBlock"),
                            Command = node.string(m1.group() if m1 else ""),
                            CustomName = node.string(m2.group() if m2 else ""),
                            ExecuteOnFirstTick = node.byte(1),
                            auto = node.byte(int( m3.group() if m3 else 0 )),
                            TickDelay = node.int(int( m4.group() if m4 else 0 )),
                            conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                            TrackOutput = node.byte(1),
                            Version = node.int(int( m5.group() if m5 else 19 )),
                        ).build()
                        StructureObject.set_blockNBT(posx, posy, posz, CommandBlockNbt)
                    else :
                        try : nbtObj = nbt.read_from_snbt_file( io.StringIO(nbtstr) ).get_tag()
                        except : continue
                        if "Items" not in nbtObj : continue
                        StructureObject.set_blockNBT(posx, posy, posz, nbtObj)


            for entity in Struct1.entities :
                posx, posy, posz = entity[0]-PosStart[0], entity[1]-PosStart[1], entity[2]-PosStart[2]
                EntityNBT = MCBELab.GenerateEntity( entity[4], (posx, posy, posz), entity[3] )
                if EntityNBT : StructureObject.entity_nbt.append(EntityNBT)

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.MianYang_V2()
            nbtstr = '{Command:"%s",CustomName:"%s",ExecuteOnFirstTick:0b,LPCommandMode:%s,' + \
                'LPCondionalMode:%sb,LPRedstoneMode:%sb,LastExecution:0l,LastOutput:"",' + \
                'LastOutputParams:[],SuccessCount:0,TickDelay:%s,TrackOutput:1b,' + \
                'Version:%s,auto:%sb,conditionMet:%sb,powered:0b}'
            LPCommandMode = {"minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2, "minecraft:command_block":0}

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            Chunks:Dict[Tuple[int,int], dict] = {}
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[ block_index ]
                BlockID, BlockState, dataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and block.name == "minecraft:air" : continue

                realX, realY, realZ = o_x + posx, o_y + posy, o_z + posz
                chunk_pos = (realX//16*16, realZ//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = {
                    "startX":chunk_pos[0], "startZ":chunk_pos[1], "blocks":[]}
                
                chunk_block = [block_index, dataValue, realX-chunk_pos[0], realY, realZ-chunk_pos[1]]
                Chunks[chunk_pos]["blocks"].append(chunk_block)

                if index not in self.block_nbt : continue

                BlockData = block.to_nbt()
                NBTObj = self.block_nbt[index]
                BlockSNbtIO = io.StringIO()
                nbt.write_to_snbt_file(BlockSNbtIO, BlockData)
                if block.name in LPCommandMode : 
                    chunk_block.append(json.dumps({
                        "blockNBT":urllib.parse.quote(BlockSNbtIO.getvalue()),
                        "blockCompleteNBT":urllib.parse.quote(nbtstr % (
                            NBTObj["Command"].value, NBTObj["CustomName"].value, LPCommandMode[BlockID],
                            int(BlockState["conditional_bit"]), int(not NBTObj["auto"].value),
                            NBTObj["TickDelay"].value, NBTObj["Version"].value, NBTObj["auto"].value, 
                            int(BlockState["conditional_bit"]) ))
                    }))
                else : 
                    SNbtIO = io.StringIO()
                    nbt.write_to_snbt_file(SNbtIO, NBTObj)
                    chunk_block.append(json.dumps({
                        "blockNBT":urllib.parse.quote(BlockSNbtIO.getvalue()),
                        "blockCompleteNBT":urllib.parse.quote(SNbtIO.getvalue())
                    }))

            for entity in self.entity_nbt :
                Struct1.entities.append([
                    entity["Pos"][0].value - self.origin[0],
                    entity["Pos"][1].value - self.origin[1],
                    entity["Pos"][2].value - self.origin[2],
                    entity.get("CustomName", nbt.TAG_String()).value,
                    entity["identifier"].value,
                ])

            Struct1.chunks.extend(Chunks.values())
            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)
 
    class MIANYANG_V3(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False
            
            try : Json1 = json.load(fp=io.BytesIO( zlib.decompress(Data.read()) ) )
            except : return False
            if isinstance(Json1, dict) and ("chunkedBlocks" in Json1) \
                and ("namespaces" in Json1) and ("totB" in Json1): return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.MianYang_V3.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            CommandMatch = re.compile('(?<=Command:").*(?=",CustomName)', re.DOTALL)
            CustomNameMatch = re.compile('(?<=CustomName:").*(?=",ExecuteOnFirstTick)', re.DOTALL)
            AutoMatch = re.compile('(?<=auto:)-?[0-9]+(?=b)')
            TickDelayMatch = re.compile('(?<=TickDelay:)-?[0-9]+(?=,)')
            VersionMatch = re.compile('(?<=Version:)-?[0-9]+(?=,)')

            for chunk in Struct1.chunks :
                o_x, o_z = chunk["startX"]-PosStart[0], chunk["startZ"]-PosStart[2]
                for block in chunk["blocks"] :
                    posx, posy, posz = o_x + block[2], block[3] - PosStart[1], o_z + block[4]
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Struct1.block_palette[block[0]], block[1])
                    block_obj = Block(Ra_ID, Ra_State)
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    try : BlockJsonData = json.loads(block[-1])
                    except : continue
                    nbtstr = urllib.parse.unquote(BlockJsonData['blockCompleteNBT'])
                    
                    m1 = CommandMatch.search(nbtstr)
                    m2 = CustomNameMatch.search(nbtstr)
                    m3 = AutoMatch.search(nbtstr)
                    m4 = TickDelayMatch.search(nbtstr)
                    m5 = VersionMatch.search(nbtstr)

                    if block_obj.name.endswith("command_block") : 
                        node = nbt.NBT_Builder()
                        CommandBlockNbt = node.compound(
                            id = node.string("CommandBlock"),
                            Command = node.string(m1.group() if m1 else ""),
                            CustomName = node.string(m2.group() if m2 else ""),
                            ExecuteOnFirstTick = node.byte(1),
                            auto = node.byte(int( m3.group() if m3 else 0 )),
                            TickDelay = node.int(int( m4.group() if m4 else 0 )),
                            conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                            TrackOutput = node.byte(1),
                            Version = node.int(int( m5.group() if m5 else 19 )),
                        ).build()
                        StructureObject.set_blockNBT(posx, posy, posz, CommandBlockNbt)
                    else :
                        try : nbtObj = nbt.read_from_snbt_file( io.StringIO(nbtstr) ).get_tag()
                        except : continue
                        if "Items" not in nbtObj : continue
                        StructureObject.set_blockNBT(posx, posy, posz, nbtObj)


            for entity in Struct1.entities :
                posx, posy, posz = entity[0]-PosStart[0], entity[1]-PosStart[1], entity[2]-PosStart[2]
                EntityNBT = MCBELab.GenerateEntity( entity[4], (posx, posy, posz), entity[3])
                if EntityNBT : StructureObject.entity_nbt.append(EntityNBT)

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.MianYang_V3()
            nbtstr = '{Command:"%s",CustomName:"%s",ExecuteOnFirstTick:0b,LPCommandMode:%s,' + \
                'LPCondionalMode:%sb,LPRedstoneMode:%sb,LastExecution:0l,LastOutput:"",' + \
                'LastOutputParams:[],SuccessCount:0,TickDelay:%s,TrackOutput:1b,' + \
                'Version:%s,auto:%sb,conditionMet:%sb,powered:0b}'
            LPCommandMode = {"minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2, "minecraft:command_block":0}

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            Chunks:Dict[Tuple[int,int], dict] = {}
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[ block_index ]
                BlockID, BlockState, dataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and block.name == "minecraft:air" : continue

                realX, realY, realZ = o_x + posx, o_y + posy, o_z + posz
                chunk_pos = (realX//16*16, realZ//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = {
                    "startX":chunk_pos[0], "startZ":chunk_pos[1], "blocks":[]}
                
                chunk_block = [block_index, dataValue, realX-chunk_pos[0], realY, realZ-chunk_pos[1]]
                Chunks[chunk_pos]["blocks"].append(chunk_block)

                if index not in self.block_nbt : continue

                BlockData = block.to_nbt()
                NBTObj = self.block_nbt[index]
                BlockSNbtIO = io.StringIO()
                nbt.write_to_snbt_file(BlockSNbtIO, BlockData)
                if block.name in LPCommandMode : 
                    chunk_block.append(json.dumps({
                        "blockNBT":urllib.parse.quote(BlockSNbtIO.getvalue()),
                        "blockCompleteNBT":urllib.parse.quote(nbtstr % (
                            NBTObj["Command"].value, NBTObj["CustomName"].value, LPCommandMode[BlockID],
                            int(BlockState["conditional_bit"]), int(not NBTObj["auto"].value),
                            NBTObj["TickDelay"].value, NBTObj["Version"].value, NBTObj["auto"].value, 
                            int(BlockState["conditional_bit"]) ))
                    }))
                else : 
                    SNbtIO = io.StringIO()
                    nbt.write_to_snbt_file(SNbtIO, NBTObj)
                    chunk_block.append(json.dumps({
                        "blockNBT":urllib.parse.quote(BlockSNbtIO.getvalue()),
                        "blockCompleteNBT":urllib.parse.quote(SNbtIO.getvalue())
                    }))

            for entity in self.entity_nbt :
                Struct1.entities.append([
                    entity["Pos"][0].value - self.origin[0],
                    entity["Pos"][1].value - self.origin[1],
                    entity["Pos"][2].value - self.origin[2],
                    entity.get("CustomName", nbt.TAG_String()).value,
                    entity["identifier"].value,
                ])

            Struct1.chunks.extend(Chunks.values())
            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)
 
    class GANGBAN_V1(CodecsBase) :
        
        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, list) and len(Json1) >= 2 and \
                (isinstance(Json1[-1], dict) and "list" in Json1[-1]) and \
                (isinstance(Json1[-2], dict) and "start" in Json1[-2] and "end" in Json1[-2]) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V1.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__( Struct1.size )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = Struct1.origin[0], Struct1.origin[1], Struct1.origin[2]
            for block in Struct1.blocks :
                Ra_ID, Ra_State = Struct1.block_palette[block["id"]], block.get("aux", 0)
                Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                block_obj = Block(Ra_ID, Ra_State)
                posx, posy, posz = block["p"][0] - O_X, block["p"][1] - O_Y, block["p"][2] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

                if "cmds" not in block : continue
                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(block["cmds"].get("cmd", "")),
                    CustomName = node.string(block["cmds"].get("name", "")),
                    ExecuteOnFirstTick = node.byte(1),
                    auto = node.byte(block["cmds"].get("on", 1)),
                    TickDelay = node.int(block["cmds"].get("tick", 0)),
                    TrackOutput = node.byte(block["cmds"].get("should", 1)),
                    conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                    Version = node.int(38 if ExecuteTest.match(block["cmds"].get("cmd", "")) else 19),
                ).build()
                StructureObject.set_blockNBT(posx, posy, posz, BlockData)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V1()

            Struct1.size = self.size
            Struct1.origin = self.origin

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            CommandBlockGangBan = {"minecraft:repeating_command_block":"Repeating", 
                "minecraft:chain_command_block":"Chain", "minecraft:command_block":"Tick"}

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                
                block = {"id":block_index, "aux":DataValue, "p":[o_x + posx, o_y + posy, o_z + posz]}
                Struct1.blocks.append(block)
                
                if index not in self.block_nbt : continue
                if BlockID not in CommandBlockGangBan : continue
                block["cmds"] = {
                    "mode":CommandBlockGangBan[BlockID],
                    "condition":bool(BlockState["conditional_bit"]),
                    "cmd":self.block_nbt[index]["Command"].value,
                    "name":self.block_nbt[index]["CustomName"].value,
                    "tick":self.block_nbt[index]["TickDelay"].value,
                    "should":bool(self.block_nbt[index]["TrackOutput"]),
                    "on":bool(self.block_nbt[index]["auto"])
                }

            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)

    class GANGBAN_V2(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, list) and len(Json1) >= 2 and \
                (isinstance(Json1[-1], dict) and "list" in Json1[-1]) and \
                (isinstance(Json1[0], dict) and "p" in Json1[0] and "id" in Json1[0]) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V2.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for block in Struct1.blocks :
                Ra_ID, Ra_State = Struct1.block_palette[block["id"]], block.get("aux", 0)
                Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                block_obj = Block(Ra_ID, Ra_State)
                posx, posy, posz = block["p"][0] - O_X, block["p"][1] - O_Y, block["p"][2] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

                if "cmds" not in block : continue
                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(block["cmds"].get("cmd", "")),
                    CustomName = node.string(block["cmds"].get("name", "")),
                    ExecuteOnFirstTick = node.byte(1),
                    auto = node.byte(block["cmds"].get("on", 1)),
                    TickDelay = node.int(block["cmds"].get("tick", 0)),
                    TrackOutput = node.byte(block["cmds"].get("should", 1)),
                    conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                    Version = node.int(38 if ExecuteTest.match(block["cmds"].get("cmd", "")) else 19),
                ).build()
                StructureObject.set_blockNBT(posx, posy, posz, BlockData)

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V2()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            CommandBlockGangBan = {"minecraft:repeating_command_block":"Repeating", 
                "minecraft:chain_command_block":"Chain", "minecraft:command_block":"Tick"}

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                
                block = {"id":block_index, "aux":DataValue, "p":[o_x + posx, o_y + posy, o_z + posz]}
                Struct1.blocks.append(block)
                
                if index not in self.block_nbt : continue
                if BlockID not in CommandBlockGangBan : continue
                block["cmds"] = {
                    "mode":CommandBlockGangBan[BlockID],
                    "condition":bool(BlockState["conditional_bit"]),
                    "cmd":self.block_nbt[index]["Command"].value,
                    "name":self.block_nbt[index]["CustomName"].value,
                    "tick":self.block_nbt[index]["TickDelay"].value,
                    "should":bool(self.block_nbt[index]["TrackOutput"]),
                    "on":bool(self.block_nbt[index]["auto"])
                }

            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)

    class GANGBAN_V3(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, list) and len(Json1) >= 2 and \
                (isinstance(Json1[0], dict) and "name" in Json1[0]) and \
                (isinstance(Json1[1], str)) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V3.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for chunk in Struct1.chunks :
                o_x, o_y, o_z = chunk["grids"]["x"]-O_X, O_Y, chunk["grids"]["z"]-O_Z
                for block in chunk["data"] :
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Struct1.block_palette[block[0]], block[1])
                    block_obj = Block(Ra_ID, Ra_State)
                    posx, posy, posz = block[2] + o_x, block[3] - o_y, block[4] + o_z
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    if block[5] != "nbt" : continue

                    NbtName = MCBELab.GetNbtID(block_obj.name)
                    if not NbtName : continue
                    SNBT = nbt.read_from_snbt_file( io.StringIO(block[6]) ).get_tag()
                    SNBT["id"] = nbt.TAG_String(NbtName)
                    StructureObject.set_blockNBT( posx, posy, posz, SNBT )

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V3()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            Chunks:Dict[Tuple[int,int], dict] = {}
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                realX, realY, realZ = o_x + posx, o_y + posy, o_z + posz
                chunk_pos = (realX//16*16, realZ//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = {
                    "id":len(Chunks), "grids":{"x":chunk_pos[0], "z":chunk_pos[1],
                    "x1":chunk_pos[0]+16, "z1":chunk_pos[1]+16}, "data":[]}
                
                chunk_block = [block_index, DataValue, realX-chunk_pos[0], realY, realZ-chunk_pos[1]]
                Chunks[chunk_pos]["data"].append(chunk_block)

                if index not in self.block_nbt : continue

                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    name = node.string(BlockID),
                    states = node.compound(**{
                        i:( node.byte(j) if isinstance(j, bool) else node.int(j)
                        ) for i,j in BlockState.items()
                    }),
                    val = node.short(DataValue),
                    version = node.int(17959425),
                ).build()

                NBTObj = self.block_nbt[index]
                BlockSNbtIO1, BlockSNbtIO2 = io.StringIO(), io.StringIO()
                nbt.write_to_snbt_file(BlockSNbtIO1, NBTObj, format=False)
                nbt.write_to_snbt_file(BlockSNbtIO2, BlockData, format=False)
                Copy1 = chunk_block.copy()
                Copy1.append("nbt2")
                Copy1.append(BlockSNbtIO2.getvalue()[3:])

                Chunks[chunk_pos]["data"].append(Copy1)
                chunk_block.append("nbt")
                NBTstr = BlockSNbtIO1.getvalue()
                chunk_block.append(NBTstr[3:] if NBTstr[0:3] == '"":' else NBTstr)

            Struct1.chunks.extend(Chunks.values())
            Struct1.block_palette.update((i, j.name) for i,j in enumerate(self.block_palette))
            Struct1.save_as(Writer)

    class GANGBAN_V4(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, list) and len(Json1) >= 2 and \
                (isinstance(Json1[0], dict) and "name" in Json1[0]) and \
                (isinstance(Json1[1], list) and Json1[1] and isinstance(Json1[1][0], str)) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V4.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for chunk in Struct1.chunks :
                o_x, o_y, o_z = chunk["grids"]["x"]-O_X, O_Y, chunk["grids"]["z"]-O_Z
                for block in chunk["data"] :
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Struct1.block_palette[block[0]], block[1])
                    block_obj = Block(Ra_ID, Ra_State)
                    posx, posy, posz = block[2] + o_x, block[3] - o_y, block[4] + o_z
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    if block[5] != "nbt" : continue

                    NbtName = MCBELab.GetNbtID(block_obj.name)
                    if not NbtName : continue
                    SNBT = nbt.read_from_snbt_file( io.StringIO(block[6]) ).get_tag()
                    SNBT["id"] = nbt.TAG_String(NbtName)
                    StructureObject.set_blockNBT( posx, posy, posz, SNBT )

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V4()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            Chunks:Dict[Tuple[int,int], dict] = {}
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                realX, realY, realZ = o_x + posx, o_y + posy, o_z + posz
                chunk_pos = (realX//16*16, realZ//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = {
                    "id":len(Chunks), "grids":{"x":chunk_pos[0], "z":chunk_pos[1],
                    "x1":chunk_pos[0]+16, "z1":chunk_pos[1]+16}, "data":[]}
                
                chunk_block = [block_index, DataValue, realX-chunk_pos[0], realY, realZ-chunk_pos[1]]
                Chunks[chunk_pos]["data"].append(chunk_block)

                if index not in self.block_nbt : continue

                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    name = node.string(BlockID),
                    states = node.compound(**{
                        i:( node.byte(j) if isinstance(j, bool) else node.int(j)
                        ) for i,j in BlockState.items()
                    }),
                    val = node.short(DataValue),
                    version = node.int(17959425),
                ).build()

                NBTObj = self.block_nbt[index]
                BlockSNbtIO1, BlockSNbtIO2 = io.StringIO(), io.StringIO()
                nbt.write_to_snbt_file(BlockSNbtIO1, NBTObj, format=False)
                nbt.write_to_snbt_file(BlockSNbtIO2, BlockData, format=False)
                Copy1 = chunk_block.copy()
                Copy1.append("nbt2")
                Copy1.append(BlockSNbtIO2.getvalue()[3:])

                Chunks[chunk_pos]["data"].append(Copy1)
                chunk_block.append("nbt")
                NBTstr = BlockSNbtIO1.getvalue()
                chunk_block.append(NBTstr[3:] if NBTstr[0:3] == '"":' else NBTstr)

            Struct1.chunks.extend(Chunks.values())
            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)

    class GANGBAN_V5(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, list) and len(Json1) >= 3 and \
                isinstance(Json1[0], int) and isinstance(Json1[-1], list) and \
                (isinstance(Json1[-2], dict) and "ep" in Json1[-2]) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V5.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__( Struct1.size )
            StructureObject.block_palette.append( Block("minecraft:air") )

            CommandBlockGangBan = ["minecraft:command_block", "minecraft:repeating_command_block", 
                "minecraft:chain_command_block"]
            Pointer, blocklen, blockdata = 0, len(Struct1.blocks), Struct1.blocks
            while Pointer < blocklen :
                datatype, blockindex, datavar = blockdata[Pointer], blockdata[Pointer+4], blockdata[Pointer+5]
                posx, posy, posz = blockdata[Pointer+1], blockdata[Pointer+2], blockdata[Pointer+3]
                if datatype != 1 : 
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Struct1.block_palette[blockindex], datavar)
                    StructureObject.set_block(posx, posy, posz, Block(Ra_ID, Ra_State))
                Pointer += 6
                if datatype == 3 : continue

                blocknbt = blockdata[Pointer]
                Pointer += 1
                if datatype == 1 :
                    node = nbt.NBT_Builder()
                    BlockData = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(blocknbt.get("cmd", "")),
                        CustomName = node.string(blocknbt.get("name", "")),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(blocknbt.get("auto", 1)),
                        TickDelay = node.int(blocknbt.get("delay", 0)),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(blocknbt.get("condition", 0)),
                        Version = node.int(38 if ExecuteTest.match(blocknbt.get("cmd", "")) else 19),
                    ).build()
                    StructureObject.set_block(posx, posy, posz, Block(CommandBlockGangBan[datavar], blockindex))
                    StructureObject.set_blockNBT(posx, posy, posz, BlockData)
                elif datatype == 4 : 
                    Contanier = MCBELab.GenerateBlockEntityNBT( Struct1.block_palette[blockindex] )
                    if Contanier is None : continue
                    for item in blocknbt :
                        if "ns" not in item or "slot" not in item : continue
                        if None in set(item.values()) : continue
                        itemID = item["ns"] if item["ns"].startswith("minecraft:") else "minecraft:" + item["ns"]
                        Contanier["Items"].append(nbt.TAG_Compound({
                            "Name": nbt.TAG_String(itemID),
                            "Count": nbt.TAG_Byte(item.get("num", 1)),
                            "Damage": nbt.TAG_Short(item.get("aux", 0)),
                            "Slot": nbt.TAG_Byte(item["slot"]),
                            "Block": Block(itemID, 0).to_nbt()
                        }))
                    StructureObject.set_blockNBT(posx, posy, posz, Contanier)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V5()
            Struct1.size = self.size

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            CommandBlockGangBan = {"minecraft:command_block":0, "minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2 }

            data_list = [0, 0, 0, 0, 0, 0]
            EXTEND = super(TypeCheckList, Struct1.blocks).extend
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                data_list[1], data_list[2], data_list[3] = posx, posy, posz
                if BlockID in CommandBlockGangBan :
                    data_list[4], data_list[5] = DataValue, CommandBlockGangBan[BlockID]
                else : data_list[4], data_list[5] = block_index, DataValue

                if index not in self.block_nbt : 
                    EXTEND(data_list) ; continue
                NBT_Object = self.block_nbt[index]
                if "Items" in NBT_Object :
                    data_list[0] = 4
                    data_list.append([])
                    for SlotID, Item in enumerate(NBT_Object["Items"]) : 
                        if "Slot" in Item : SlotID = Item["Slot"].value
                        data_list[-1].append({"ns":Item["Name"].value,
                        "aux":Item["Damage"].value,"num":Item["Count"].value,"slot":SlotID})
                elif BlockID.endswith("command_block") :
                    data_list[0] = 1
                    data_list.append({
                        "auto":bool(NBT_Object["auto"].value),
                        "condition":bool(BlockState["conditional_bit"]),
                        "cmd":NBT_Object["Command"].value,
                        "name":NBT_Object["CustomName"].value,
                        "delay":NBT_Object["TickDelay"].value})
                else : data_list[0] = 3
                EXTEND(data_list)
                del data_list[6:]

            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)

    class GANGBAN_V6(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, list) and len(Json1) >= 3 and \
                isinstance(Json1[0], list) and isinstance(Json1[-2], (list, dict)) and \
                isinstance(Json1[-1], list) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V6.from_buffer(Reader)
            if Struct1.size is not None :
                PosStart, PosEnd = [-1,-1,-1], Struct1.size
            else : PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            pos_cache, real_pos = [0, 0, 0], [0, 0, 0]
            TranslateReverse = {j:i for i,j in MCBELab.ItemTranslateData.items()}
            CommandBlockGangBan = ["minecraft:command_block", "minecraft:repeating_command_block", 
                "minecraft:chain_command_block"]
            for block in Struct1.blocks :
                for i in range(3) : 
                    pos_cache[i] += block[i]
                    real_pos[i] = pos_cache[i] - PosStart[i]

                if block[-1].__class__ is dict and "cmd" in block[-1] :
                    node = nbt.NBT_Builder()
                    BlockData = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(block[-1]["cmd"]),
                        CustomName = node.string(block[-1].get("name", "")),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(block[-1].get("auto", 1)),
                        TickDelay = node.int(block[-1].get("delay", 0)),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(block[-1].get("condition", 0)),
                        Version = node.int(38 if ExecuteTest.match(block[-1]["cmd"]) else 19),
                    ).build()
                    StructureObject.set_block(*real_pos, Block(CommandBlockGangBan[block[4]], block[3]))
                    StructureObject.set_blockNBT(*real_pos, BlockData)
                else : 
                    Ra_ID, Ra_State = Struct1.block_palette[block[3]], block[4]
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                    StructureObject.set_block(*real_pos, Block(Ra_ID, Ra_State))
                    if block[-1].__class__ is list :
                        Contanier = MCBELab.GenerateBlockEntityNBT( Struct1.block_palette[block[3]] )
                        if Contanier is None : continue
                        for item in block[-1] :
                            if "ns" not in item or "slot" not in item : continue
                            if None in set(item.values()) : continue
                            itemID = item["ns"] if item["ns"].startswith("minecraft:") else "minecraft:" + item["ns"]
                            Contanier["Items"].append(nbt.TAG_Compound({
                                "Name": nbt.TAG_String(itemID),
                                "Count": nbt.TAG_Byte(item.get("num", 1)),
                                "Damage": nbt.TAG_Short(item.get("aux", 0)),
                                "Slot": nbt.TAG_Byte(item["slot"]),
                                "Block": Block(itemID, 0).to_nbt()
                            }))
                        StructureObject.set_blockNBT(*real_pos, Contanier)

            for entity in Struct1.entities :
                entityNBT = MCBELab.GenerateEntity(entity[4], (entity[0]-PosStart[0], entity[1]-PosStart[1], entity[2]-PosStart[2]))
                if not entityNBT : continue
                entityNBT["Item"]["Name"] = nbt.TAG_String("minecraft:" + TranslateReverse.get(entity[3], "stone"))
                StructureObject.entity_nbt.append(entityNBT)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V6()
            Struct1.size = self.size

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            CommandBlockGangBan = {"minecraft:command_block":0, "minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2 }

            for entity in self.entity_nbt :
                data_list = [entity["Pos"][0].value, entity["Pos"][1].value, entity["Pos"][2].value, None, None]
                if entity["identifier"].value == "minecraft:item" :
                    ItemName = entity["Item"]["Name"].value.replace("minecraft:", "", 1)
                    data_list[3], data_list[4] = MCBELab.ItemTranslateData.get(ItemName, "石头"), "minecraft:item"
                else : 
                    EntityName = entity["identifier"].value.replace("minecraft:", "", 1)
                    data_list[3], data_list[4] = MCBELab.EntityTranslateData.get(EntityName, ""), entity["identifier"].value
                Struct1.entities.append(data_list)

            pos_cache = [0, 0, 0]
            APPEND = super(TypeCheckList, Struct1.blocks).append
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                
                data_list = [posx-pos_cache[0], posy-pos_cache[1], posz-pos_cache[2], None, None]
                if BlockID in CommandBlockGangBan :
                    data_list[3], data_list[4] = DataValue, CommandBlockGangBan[BlockID]
                else : data_list[3], data_list[4] = block_index, DataValue
                APPEND(data_list)
                pos_cache[0], pos_cache[1], pos_cache[2] = posx, posy, posz

                if index not in self.block_nbt : continue
                NBT_Object = self.block_nbt[index]
                if "Items" in NBT_Object :
                    data_list.append([])
                    for SlotID, Item in enumerate(NBT_Object["Items"]) : 
                        if "Slot" in Item : SlotID = Item["Slot"].value
                        data_list[-1].append({"ns":Item["Name"].value,
                        "aux":Item["Damage"].value,"num":Item["Count"].value,"slot":SlotID})
                elif BlockID.endswith("command_block") :
                    data_list.append({
                        "auto":bool(NBT_Object["auto"].value),
                        "condition":bool(BlockState["conditional_bit"]),
                        "cmd":NBT_Object["Command"].value,
                        "name":NBT_Object["CustomName"].value,
                        "delay":NBT_Object["TickDelay"].value})

            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)

    class GANGBAN_V7(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False

            try : Json1 = json.load(fp=io.BytesIO( zlib.decompress(Data.read()) ) )
            except : return False

            if isinstance(Json1, list) and len(Json1) >= 3 and isinstance(Json1[-1], list) and \
                isinstance(Json1[0], list) and isinstance(Json1[-2], (list, dict)) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V7.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            pos_cache = [0, 0, 0]
            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            TranslateReverse = {j:i for i,j in MCBELab.ItemTranslateData.items()}
            CommandBlockGangBan = ["minecraft:command_block", "minecraft:repeating_command_block", 
                "minecraft:chain_command_block"]
            for block in Struct1.blocks :
                for i in range(3) : pos_cache[i] += block[i]
                posx, posy, posz = pos_cache[0] - O_X, pos_cache[1] - O_Y, pos_cache[2] - O_Z
                if block[-1].__class__ is dict and "cmd" in block[-1] :
                    node = nbt.NBT_Builder()
                    BlockData = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(block[-1]["cmd"]),
                        CustomName = node.string(block[-1].get("name", "")),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(block[-1].get("auto", 1)),
                        TickDelay = node.int(block[-1].get("delay", 0)),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(block[-1].get("condition", 0)),
                        Version = node.int(38 if ExecuteTest.match(block[-1]["cmd"]) else 19),
                    ).build()
                    StructureObject.set_block(posx, posy, posz, Block(CommandBlockGangBan[block[4]], block[3]))
                    StructureObject.set_blockNBT(posx, posy, posz, BlockData)
                else : 
                    Ra_ID, Ra_State = Struct1.block_palette[block[3]], block[4]
                    Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                    StructureObject.set_block(posx, posy, posz, Block(Ra_ID, Ra_State))
                    if block[-1].__class__ is list :
                        Contanier = MCBELab.GenerateBlockEntityNBT( Struct1.block_palette[block[3]] )
                        if Contanier is None : continue
                        for item in block[-1] :
                            if None in set(item.values()) : continue
                            itemID = item["ns"] if item["ns"].startswith("minecraft:") else "minecraft:" + item["ns"]
                            Contanier["Items"].append(nbt.TAG_Compound({
                                "Name": nbt.TAG_String(itemID),
                                "Count": nbt.TAG_Byte(item.get("num", 1)),
                                "Damage": nbt.TAG_Short(item.get("aux", 0)),
                                "Slot": nbt.TAG_Byte(item["slot"]),
                                "Block": Block(itemID, 0).to_nbt()
                            }))
                        StructureObject.set_blockNBT(posx, posy, posz, Contanier)

            for entity in Struct1.entities :
                entityNBT = MCBELab.GenerateEntity(entity[4], (entity[0], entity[1], entity[2]))
                if not entityNBT : continue
                entityNBT["Item"]["Name"] = nbt.TAG_String("minecraft:" + TranslateReverse.get(entity[3], "stone"))
                StructureObject.entity_nbt.append(entityNBT)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V7()

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            CommandBlockGangBan = {"minecraft:command_block":0, "minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2 }

            for entity in self.entity_nbt :
                data_list = [entity["Pos"][0].value, entity["Pos"][1].value, entity["Pos"][2].value, None, None]
                if entity["identifier"].value == "minecraft:item" :
                    ItemName = entity["Item"]["Name"].value.replace("minecraft:", "", 1)
                    data_list[3], data_list[4] = MCBELab.ItemTranslateData.get(ItemName, "石头"), "minecraft:item"
                else : 
                    EntityName = entity["identifier"].value.replace("minecraft:", "", 1)
                    data_list[3], data_list[4] = MCBELab.EntityTranslateData.get(EntityName, ""), entity["identifier"].value
                Struct1.entities.append(data_list)

            pos_cache = [0, 0, 0]
            APPEND = super(TypeCheckList, Struct1.blocks).append
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                
                data_list = [posx-pos_cache[0], posy-pos_cache[1], posz-pos_cache[2], None, None]
                if BlockID in CommandBlockGangBan :
                    data_list[3], data_list[4] = DataValue, CommandBlockGangBan[BlockID]
                else : data_list[3], data_list[4] = block_index, DataValue
                APPEND(data_list)
                pos_cache[0], pos_cache[1], pos_cache[2] = posx, posy, posz

                if index not in self.block_nbt : continue
                NBT_Object = self.block_nbt[index]
                if "Items" in NBT_Object :
                    data_list.append([])
                    for SlotID, Item in enumerate(NBT_Object["Items"]) : 
                        if "Slot" in Item : SlotID = Item["Slot"].value
                        data_list[-1].append({"ns":Item["Name"].value,
                        "aux":Item["Damage"].value,"num":Item["Count"].value,"slot":SlotID})
                elif BlockID.endswith("command_block") :
                    data_list.append({
                        "auto":bool(NBT_Object["auto"].value),
                        "condition":bool(BlockState["conditional_bit"]),
                        "cmd":NBT_Object["Command"].value,
                        "name":NBT_Object["CustomName"].value,
                        "delay":NBT_Object["TickDelay"].value})

            Struct1.block_palette.extend(i.name for i in self.block_palette)
            Struct1.save_as(Writer)

    class RUNAWAY(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if not isinstance(Json1, list)  : return False
            if any(not isinstance(i, dict) for i in Json1[0:10]) : return False
            if isinstance(Json1, list) and len(Json1) and isinstance(Json1[0], dict) and \
                "name" in Json1[0] and isinstance(Json1[0].get("x", None), int) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.RunAway.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for block in Struct1.blocks :
                Ra_ID, Ra_State = block["name"], block.get("aux", 0)
                Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                block_obj = Block(Ra_ID, Ra_State)
                posx, posy, posz = block["x"] - O_X, block["y"] - O_Y, block["z"] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.RunAway()

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                block = {"name":BlockID, "aux":DataValue, "x":posx, "y":posy, "z":posz}
                Struct1.blocks.append(block)

            Struct1.save_as(Writer)

    class KBDX(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "bytes" : return False

            try : 
                block_count = int.from_bytes(Data.read(4), "little", signed=False)
                Data.seek(20 * block_count, 1)
                json.load(Data)
            except : return False
            else : return True

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.Kbdx.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            block_palette = {j:i for i,j in Struct1.block_palette.items()}

            for block in Struct1.blocks :
                Ra_ID, Ra_State = block_palette[block[3]], block[4]
                Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                block_obj = Block(Ra_ID, Ra_State)
                posx, posy, posz = block[0] - O_X, block[1] - O_Y, block[2] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

            for snbt in Struct1.block_nbt :
                posx, posy, posz = snbt["x"] - O_X, snbt["y"] - O_Y, snbt["z"] - O_Z
                node = nbt.NBT_Builder()
                if snbt["id"].endswith("command_block") :
                    BlockData = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(snbt.get("Command", "")),
                        CustomName = node.string(snbt.get("CustomName", "")),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(not snbt.get("redstone", 0)),
                        TickDelay = node.int(snbt.get("TickDelay", 1)),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(snbt.get("isConditional", 0)),
                        Version = node.int(38 if ExecuteTest.match(snbt.get("Command", "")) else 19),
                    ).build()
                    StructureObject.set_blockNBT(posx, posy, posz, BlockData)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.Kbdx()
            CommandBlockID = {"minecraft:command_block":0, "minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2}

            for index, block_obj in enumerate(self.block_palette) : 
                Struct1.block_palette[block_obj.runawayID] = index

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                block_index = Struct1.block_palette[block.runawayID]
                block = (posx, posy, posz, block_index, DataValue)
                Struct1.blocks.append(block)

                if index not in self.block_nbt : continue
                NBT_Obj = self.block_nbt[index]
                if BlockID.endswith("command_block") :
                    DataDict = { "Command": NBT_Obj["Command"].value, "CustomName": NBT_Obj["CustomName"].value,
                        "ExecuteOnFirstTick": True, "LastOutput": "", "Mode": CommandBlockID[BlockID],
                        "TickDelay": NBT_Obj["TickDelay"].value, "TrackOutput": True, "id": BlockID.replace("minecraft:", "", 1),
                        "isConditional": NBT_Obj["conditionalMode"].value, "redstone": bool(NBT_Obj["auto"].value),
                        "x": posx, "y": posy, "z": posz}
                    Struct1.block_nbt.append(DataDict)

            Struct1.save_as(Writer)

    class FUHONG_V1(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, list) and len(Json1) and isinstance(Json1[0], dict) and \
                "name" in Json1[0] and isinstance(Json1[0].get("x", None), list) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V1.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for block in Struct1.blocks :
                Ra_ID, Ra_State = block["name"], block.get("aux", 0)
                Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                block_obj = Block(Ra_ID, Ra_State)
                posx, posy, posz = block["x"][0] - O_X, block["y"][0] - O_Y, block["z"][0] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

        def encode(self, Writer):
            raise RuntimeError(f"{Writer} 并不支持序列化数据对象")
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.FuHong_V1()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                block = {"name":BlockID, "aux":DataValue, "x":[o_x + posx], "y":[o_y + posy], "z":[o_z + posz]}
                Struct1.blocks.append(block)

            Struct1.save_as(Writer)

    class FUHONG_V2(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, dict) and isinstance(Json1.get("Build_Info", None), dict) and \
                isinstance(Json1.get("FuHongBuild_FinalFormat", None), list) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V2.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )


            def Command(x:int, y:int, z:int, block_id:str, data:Union[Dict[Literal["b", "e"], str], Tuple[str, int, int, str]]) :
                if data.__class__ is dict :
                    if "e" not in Nbtdata : return None
                    NBT_obj = nbt.read_from_snbt_file( io.StringIO(Nbtdata["e"]) )
                    StructureObject.set_blockNBT(x, y, z, NBT_obj.get_tag())
                else :
                    if len(data) < 4 : return None
                    CommandBlockNBT = MCBELab.GenerateBlockEntityNBT("command_block")
                    CommandStr = data[0] if isinstance(data[0], str) else ""
                    CommandBlockNBT["Command"] = nbt.TAG_String(CommandStr)
                    CommandBlockNBT["TickDelay"] = nbt.TAG_Int(data[1])
                    CommandBlockNBT["auto"] = nbt.TAG_Byte(data[2])
                    CommandBlockNBT["CustomName"] = nbt.TAG_String(data[3])
                    CommandBlockNBT["Version"] = nbt.TAG_Int(38 if ExecuteTest.match(CommandStr) else 19)
                    StructureObject.set_blockNBT(x, y, z, CommandBlockNBT)

            def Container(x:int, y:int, z:int, block_id:str, data:Union[Dict[Literal["b", "e"], str], Dict[Literal["d"], List[dict]]]) :
                if "e" in data :
                    if "e" not in Nbtdata : return None
                    NBT_obj = nbt.read_from_snbt_file( io.StringIO(Nbtdata["e"]) )
                    StructureObject.set_blockNBT(x, y, z, NBT_obj.get_tag())
                else : 
                    ContanierNBT = MCBELab.GenerateBlockEntityNBT( block_id )
                    if ContanierNBT is None : return None
                    for item in data.get("d", []) :
                        if item.__class__ is not dict : continue
                        if "name" not in item or "slot" not in item : continue
                        itemID = item["name"] if item["name"].startswith("minecraft:") else "minecraft:%s"%item["name"]
                        ContanierNBT["Items"].append(nbt.TAG_Compound({
                            "Name": nbt.TAG_String(itemID),
                            "Count": nbt.TAG_Byte(item.get("count", 1)),
                            "Damage": nbt.TAG_Short(item.get("damage", 1)),
                            "Slot": nbt.TAG_Byte(item["slot"]),
                            "Block": Block(itemID, 0).to_nbt()
                        }))
                    StructureObject.set_blockNBT(x, y, z, ContanierNBT)


            for chunk in Struct1.chunks :
                for data_obj in chunk["block"] :
                    if "en" in data_obj :
                        entity_id = data_obj["en"]
                        for posx,posy,posz in zip(data_obj["x"], data_obj["y"], data_obj["z"]) :
                            EntityNBT = MCBELab.GenerateEntity(entity_id, (posx, posy, posz))
                            if EntityNBT : StructureObject.entity_nbt.append(EntityNBT)
                    elif "n" in data_obj :
                        iter1 = data_obj.get("a", itertools.repeat(0))
                        if isinstance(iter1, int) : iter1 = itertools.repeat(iter1)
                        if "d" in data_obj : iter2 = data_obj["d"]
                        elif "c" in data_obj : iter2 = zip(data_obj["c"]["c"], data_obj["c"]["t"], data_obj["c"]["a"], data_obj["c"]["n"])
                        else : iter2 = itertools.repeat(None)
                        for posx,posy,posz,datavar,Nbtdata in zip(data_obj["x"], data_obj["y"], data_obj["z"], iter1, iter2) :
                            posx, posy, posz = posx-PosStart[0], posy-PosStart[1], posz-PosStart[2]
                            Ra_ID, Ra_State = data_obj["n"], datavar
                            Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                            block_obj = Block(Ra_ID, Ra_State)
                            StructureObject.set_block(posx, posy, posz, block_obj)
                            if Nbtdata is None : continue
                            if data_obj["n"].endswith("command_block") : Command(posx, posy, posz, block_obj.name, Nbtdata)
                            else : Container(posx, posy, posz, block_obj.name, Nbtdata)

        def encode(self, Writer):
            raise RuntimeError(f"{Writer} 并不支持序列化数据对象")
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.FuHong_V2()

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            ChunkCache:Dict[Tuple[int, int], Dict[Literal["block", "entity"], dict]] = {}

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                chunk_pos = (posx//16*16, posz//16*16)
                if chunk_pos not in ChunkCache : ChunkCache[chunk_pos] = {"block":{}, "entity":{}}
                block_data_list = ChunkCache[chunk_pos]["block"]
                if BlockID not in block_data_list : block_data_list[BlockID] = {"n":BlockID, "x":[],"y":[],"z":[], "a":[]}
                block_data_list[BlockID]["x"].append( posx )
                block_data_list[BlockID]["y"].append( posy )
                block_data_list[BlockID]["z"].append( posz )
                block_data_list[BlockID]["a"].append( DataValue )

                if index not in self.block_nbt : continue
                NBT_Obj = self.block_nbt[index]
                if BlockID.endswith("command_block") : 
                    if "c" not in block_data_list[BlockID] : block_data_list[BlockID]["c"] = {
                        "c": [], "t": [], "a": [], "n": []}
                    block_data_list[BlockID]["c"]["c"].append(NBT_Obj["Command"].value)
                    block_data_list[BlockID]["c"]["t"].append(NBT_Obj["TickDelay"].value)
                    block_data_list[BlockID]["c"]["a"].append(NBT_Obj["auto"].value)
                    block_data_list[BlockID]["c"]["n"].append(NBT_Obj["CustomName"].value)
                if "Items" in NBT_Obj :
                    if "d" not in block_data_list[BlockID] : block_data_list[BlockID]["d"] = []
                    block_data_list[BlockID]["d"].append({"d":[]})
                    ItemSave = block_data_list[BlockID]["d"][-1]["d"]
                    for item in NBT_Obj["Items"] : 
                        ItemSave.append({
                            "name": item["Name"].value, "damage": item["Damage"].value,
                            "count": item["Count"].value, "slot": item["Slot"].value
                        })


            for entity in self.entity_nbt :
                EntityID = entity["identifier"].value
                posx, posy, posz = entity["Pos"][0].value, entity["Pos"][1].value, entity["Pos"][2].value

                chunk_pos = (posx//16*16, posz//16*16)
                if chunk_pos not in ChunkCache : ChunkCache[chunk_pos] = {"block":{}, "entity":{}}
                block_data_list = ChunkCache[chunk_pos]["entity"]
                if EntityID not in block_data_list : block_data_list[EntityID] = {"en":EntityID,"x":[],"y":[],"z":[]}
                block_data_list[EntityID]["x"].append( posx-chunk_pos[0] )
                block_data_list[EntityID]["y"].append( posy-self.origin[1] )
                block_data_list[EntityID]["z"].append( posz-chunk_pos[1] )
            
            for pos, data in ChunkCache.items() :
                chunk_data = {"startX":pos[0]//16,"startZ":pos[1]//16,"block":[]}
                chunk_data["block"].extend(data["entity"].values())
                chunk_data["block"].extend(data["block"].values())
                Struct1.chunks.append(chunk_data)

            Struct1.save_as(Writer)

    class FUHONG_V3(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data
            
            if isinstance(Json1, dict) and isinstance(Json1.get("BlocksList", None), list) and \
                isinstance(Json1.get("FuHongBuild", None), list) : return True
            return False

        def __encode__(self, Struct1:Union[StructureRUNAWAY.FuHong_V3, StructureRUNAWAY.FuHong_V4]) :
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            def Container(id:str, data:List[Tuple[str, int, int, int]]) :
                ContanierNBT = MCBELab.GenerateBlockEntityNBT( id )
                if ContanierNBT is None : return None
                for item in data :
                    if item.__class__ is not list or len(item) < 4 : continue
                    itemID = item[0] if item[0].startswith("minecraft:") else "minecraft:%s"%item[0]
                    ContanierNBT["Items"].append(nbt.TAG_Compound({
                        "Name": nbt.TAG_String(itemID),
                        "Count": nbt.TAG_Byte(item[2]),
                        "Damage": nbt.TAG_Short(item[1]),
                        "Slot": nbt.TAG_Byte(item[3]),
                        "Block": Block(itemID, 0).to_nbt()
                    }))
                return ContanierNBT

            def Sign(id:str, data:str) :
                SignNBT = MCBELab.GenerateBlockEntityNBT(id)
                if SignNBT is None : return None
                
                SignNBT["FrontText"]["Text"] = nbt.TAG_String(data)
                return SignNBT

            def Command(id:str, data:Tuple[str, int, int, str]) :
                if data.__class__ is not list or len(data) < 4 : return None
                CommandBlockNBT = MCBELab.GenerateBlockEntityNBT(id)
                if CommandBlockNBT is None : return None
                CommandStr = data[0] if isinstance(data[0], str) else ""
                CommandBlockNBT["Command"] = nbt.TAG_String(CommandStr)
                CommandBlockNBT["TickDelay"] = nbt.TAG_Int(data[1])
                CommandBlockNBT["auto"] = nbt.TAG_Byte(data[2])
                CommandBlockNBT["CustomName"] = nbt.TAG_String(data[3] if len(data) > 3 else "")
                CommandBlockNBT["Version"] = nbt.TAG_Int(38 if ExecuteTest.match(CommandStr) else 19)
                return CommandBlockNBT

            for chunk in Struct1.chunks :
                chunk_x, chunk_z = chunk.get("startX", 0), chunk.get("startZ", 0)
                if not Struct1.block_calculation_pos : chunk_x, chunk_z = 0, 0

                for data_obj in chunk["block"] :
                    id, datavar = data_obj[0], data_obj[1]
                    Pos1, Pos2, Pos3 = data_obj[2], data_obj[3], data_obj[4]
                    nbtdata = data_obj[5] if len(data_obj) > 5 else []

                    if id.__class__ is str :
                        EntityNBT = MCBELab.GenerateEntity(id, (chunk_x+Pos1, Pos2, chunk_z+Pos3), datavar)
                        if EntityNBT : StructureObject.entity_nbt.append(EntityNBT)
                    else :
                        Ra_ID, Ra_State = Struct1.block_palette[id], datavar
                        Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                        block_obj = Block(Ra_ID, Ra_State)
                        nbt_iter = [None] * len(Pos1) ; nbt_iter[0:len(nbtdata)] = nbtdata
                        if block_obj.name.endswith("command_block") : NBTFunc = Command
                        elif block_obj.name.endswith("hanging_sign") : NBTFunc = Sign
                        elif block_obj.name.endswith("_sign") : NBTFunc = Sign
                        else : NBTFunc = Container

                        for posx,posy,posz,blockdata in zip(data_obj[2], data_obj[3], data_obj[4], nbt_iter) :
                            posx,posy,posz = chunk_x+posx-PosStart[0], posy-PosStart[1], chunk_z+posz-PosStart[2]
                            StructureObject.set_block(posx,posy,posz, block_obj)
                            if not blockdata : continue
                            NBT_obj = NBTFunc(block_obj.name, blockdata)
                            StructureObject.set_blockNBT(posx,posy,posz, NBT_obj)

        def __decode__(self, Struct1:Union[StructureRUNAWAY.FuHong_V3, StructureRUNAWAY.FuHong_V4]) :
            IgnoreAir, self = self.IgnoreAir, self.Common

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            ChunkCache:Dict[Tuple[int, int], list] = {}

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                chunk_pos = (posx//16*16, posz//16*16)
                if chunk_pos not in ChunkCache : ChunkCache[chunk_pos] = {"block":{}, "entity":[]}
                block_data_list = ChunkCache[chunk_pos]["block"]
                BlockHash = (BlockID, DataValue)
                if BlockHash not in block_data_list : 
                    block_data_list[BlockHash] = [block_index, DataValue, [], [], []]
                block_data_list[BlockHash][2].append( posx-chunk_pos[0] )
                block_data_list[BlockHash][3].append( posy )
                block_data_list[BlockHash][4].append( posz-chunk_pos[1] )

                if BlockID.endswith("command_block") : 
                    if block_data_list[BlockHash].__len__() < 6 : block_data_list[BlockHash].append([])
                    if index in self.block_nbt : 
                        NBT_Obj = self.block_nbt[index]
                        block_data_list[BlockHash][-1].append([NBT_Obj["Command"].value, 
                        NBT_Obj["TickDelay"].value, NBT_Obj["auto"].value, NBT_Obj["CustomName"].value ])
                    else : block_data_list[BlockHash][-1].append(["", 0, 0, ""])
                elif BlockID.endswith("_sign") : 
                    if block_data_list[BlockHash].__len__() < 6 : block_data_list[BlockHash].append([])
                    if index in self.block_nbt : 
                        NBT_Obj = self.block_nbt[index]
                        if "FrontText" in NBT_Obj : block_data_list[BlockHash][-1].append(NBT_Obj["FrontText"]["Text"].value)
                        else : block_data_list[BlockHash][-1].append(NBT_Obj["Text"].value)
                    else : block_data_list[BlockHash][-1].append( "" )
                elif "Items" in self.block_nbt.get(index, {}) : 
                    if block_data_list[BlockHash].__len__() < 6 : block_data_list[BlockHash].append([])
                    block_data_list[BlockHash][-1].append([])
                    if index in self.block_nbt : 
                        NBT_Obj = self.block_nbt[index]
                        for SlotID, item in enumerate(NBT_Obj["Items"]) : 
                            if "Slot" in item : SlotID = item["Slot"].value
                            block_data_list[BlockHash][-1][-1].append(
                                [item["Name"].value, item["Damage"].value, item["Count"].value, SlotID] )

            for entity in self.entity_nbt :
                EntityID = entity["identifier"].value
                EntityName = entity.get("CustomName", nbt.TAG_String()).value
                posx, posy, posz = entity["Pos"][0].value, entity["Pos"][1].value, entity["Pos"][2].value

                chunk_pos = (posx//16*16, posz//16*16)
                if chunk_pos not in ChunkCache : ChunkCache[chunk_pos] = {"block":{}, "entity":[]}
                block_data_list = ChunkCache[chunk_pos]["entity"]
                block_data_list.append( [EntityID, EntityName, posx-chunk_pos[0], 
                    posy-self.origin[1], posz-chunk_pos[1]] )
            
            for pos, data in ChunkCache.items() :
                chunk_data = {"startX":pos[0],"startZ":pos[1],"block":[]}
                chunk_data["block"].extend(data["entity"])
                chunk_data["block"].extend(data["block"].values())
                Struct1.chunks.append(chunk_data)

            Struct1.block_palette.extend(i.name for i in self.block_palette)

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V3.from_buffer(Reader)
            self.__encode__(Struct1)

        def encode(self, Writer):
            Struct1 = StructureRUNAWAY.FuHong_V3()
            self.__encode__(Struct1)
            Struct1.save_as(Writer)

    class FUHONG_V4(FUHONG_V3) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            from . import C_API

            if DataType != "bytes" : return False
            try : Json1 = json.loads( C_API.fuhong_v5_decrypt( zlib.decompress(Data.read()) ) )
            except : return False

            if isinstance(Json1, dict) and isinstance(Json1.get("BlocksList", None), list) and \
                isinstance(Json1.get("FuHongBuild", None), list) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V4.from_buffer(Reader)
            self.__encode__(Struct1)

        def encode(self, Writer):
            Struct1 = StructureRUNAWAY.FuHong_V4()
            self.__encode__(Struct1)
            Struct1.save_as(Writer)

    class QINGXU_V1(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, dict) and "totalBlocks" in Json1 and \
                isinstance(Json1.get("0", None), str) : return True
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.QingXu_V1.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            for chunk in Struct1.chunks :
                for block in chunk :
                    block_obj = Block(block["Name"])
                    posx, posy, posz = block["X"] - O_X, block["Y"] - O_Y, block["Z"] - O_Z
                    StructureObject.set_block(posx, posy, posz, block_obj)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.QingXu_V1()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            Chunks:Dict[Tuple[int,int], list] = {}
            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                
                chunk_pos = (o_x + posx//16*16, o_z + posz//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = []

                Chunks[chunk_pos].append({"Name":block.runawayID, "X":o_x + posx, "Y":o_y + posy, "Z":o_z + posz})
            
            Struct1.chunks.extend(Chunks.values())
            Struct1.save_as(Writer)

    class TIMEBUILDER_V1(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            if DataType != "json" : return False
            Json1 = Data

            if isinstance(Json1, dict) and Json1.get("version", None) == "TimeBuilder" and \
                isinstance(Json1.get("block", None), list) : return True
            return False
        
        def decode(self, Reader:Union[str, io.IOBase]) :
            Struct1 = StructureRUNAWAY.TimeBuilder_V1.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )

            block_list = [None] * len(Struct1.blocks)
            for index, block in enumerate(Struct1.blocks) :
                Ra_ID, Ra_State = block["name"], block["aux"]
                Ra_ID, Ra_State = MCBELab.RunawayDataValueTransforBlock(Ra_ID, Ra_State)
                block_list[index] = Block(Ra_ID, Ra_State)
            StructureObject.block_palette.__init__([Block("minecraft:air")] + block_list)

            start_x, start_y, start_z = PosStart
            for index, block in enumerate(Struct1.blocks, start=1) :
                for posx, posy, posz in block["pos"] : 
                    StructureObject.set_block(posx-start_x, posy-start_y, posz-start_z, index)

        def encode(self, Writer:Union[str, io.IOBase]) :
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.TimeBuilder_V1()

            Generator = zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))

            for block in self.block_palette :
                Struct1.blocks.append({"name":block.name, "aux":block.dataValue[1], "pos":[]})

            JsonBlockData = Struct1.blocks
            for block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                BlockObj = self.block_palette[block_index]
                if IgnoreAir and BlockObj.name == "minecraft:air" : continue
                JsonBlockData[block_index]["pos"].append([posx, posy, posz])
            
            if IgnoreAir : 
                MiddleLen = len(Struct1.blocks)
                for index, block_data in enumerate( list( reversed(Struct1.blocks) ), start=1 ) :
                    if block_data["name"] != "minecraft:air" : continue
                    Struct1.blocks.pop(MiddleLen - index)

            Struct1.save_as(Writer)


    class MCFUNZIP(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            raise RuntimeError(f"{Reader} 不支持通过 MCFUNZIP 解析为结构")

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureMCFUNZIP.MCFunZip()

            Struct1.size = array.array("i", self.size)
            Struct1.origin = array.array("i", self.origin)
            Struct1.block_index = array.array("i", self.block_index)
            Struct1.block_nbt = {k:v.copy() for k,v in self.block_nbt.items()}

            for block in self.block_palette :
                data_value = 0
                if isinstance(getattr(block, "dataValue", None), (tuple, list)) and len(block.dataValue) > 1 :
                    data_value = int(block.dataValue[1])
                Struct1.block_palette.append({
                    "name" : block.name,
                    "states" : dict(block.states),
                    "data" : data_value,
                    "states_string" : ""
                })

            Struct1.save_as(Writer, ignore_air=IgnoreAir)

    class IBIMPORT(CodecsBase) :

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            raise RuntimeError(f"{Reader} 不支持通过 IBIMPORT 解析为结构")

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureIBIMPORT.IBImport()

            Struct1.size = array.array("i", self.size)
            Struct1.origin = array.array("i", self.origin)
            Struct1.block_index = array.array("i", self.block_index)
            Struct1.block_nbt = {k:v.copy() for k,v in self.block_nbt.items()}

            for block in self.block_palette :
                data_value = 0
                if isinstance(getattr(block, "dataValue", None), (tuple, list)) and len(block.dataValue) > 1 :
                    data_value = int(block.dataValue[1])
                Struct1.block_palette.append({
                    "name" : block.name,
                    "states" : dict(block.states),
                    "data" : data_value,
                    "states_string" : ""
                })

            Struct1.save_as(Writer, ignore_air=IgnoreAir)

    class FunctionCommand(CodecsBase) :

        @staticmethod
        def generate_command(self, IgnoreAir:bool, origin=(0,0,0)) :
            can_setblock = [True] * len(self.block_index)
            size_x, size_y, size_z = self.size[0], self.size[1], self.size[2]
            block_string = [block.blockString for block in self.block_palette]

            #快速获取方块索引位置
            get_index = lambda x,y,z: (x * size_y + y) * size_z + z
            #快速测试区域体积
            volume_test = lambda x1,y1,z1,x2,y2,z2 : abs((x2-x1+1) * (y2-y1+1) * (z2-z1+1)) <= 32768
            #测试是否可填充
            def can_fill(index:int, block:int) -> bool:
                return can_setblock[index] and self.block_index[index] == block
            #贪心寻找最大区域
            def process(x:int, y:int, z:int, b:int) :
                ex, ey, ez = x + 1, y + 1, z + 1
                for ex in range(x+1, size_x, 1) :
                    idx = get_index(ex, y, z)
                    if not can_fill(idx, b) : break

                for ez in range(z+1, size_z, 1) :
                    ok = volume_test(x, y, z, ex-1, y, ez)
                    for ex_m in range(x, ex, 1) :
                        idx = get_index(ex_m, y, ez)
                        ok = can_fill(idx, b) and ok
                        if not ok : break
                    if not ok : break

                for ey in range(y+1, size_y, 1) :
                    ok = volume_test(x, y, z, ex-1, ey, ez-1)
                    for ez_m in range(z, ez, 1) :
                        for ex_m in range(x, ex, 1) :
                            idx = get_index(ex_m, ey, ez_m)
                            ok = can_fill(idx, b) and ok
                            if not ok : break
                        if not ok : break
                    if not ok : break

                for xx in range(x, ex):
                    for yy in range(y, ey):
                        for zz in range(z, ez):
                            i = get_index(xx, yy, zz)
                            can_setblock[i] = False

                ex -= 1 ; ey -= 1 ; ez -= 1
                block_str = block_string[b]

                if x == ex and y == ey and z == ez : 
                    return f"setblock ~{x+origin[0]} ~{y+origin[1]} ~{z+origin[2]} {block_str}\n"
                else : return f"fill ~{x+origin[0]} ~{y+origin[1]} ~{z+origin[2]} ~{ex+origin[0]} ~{ey+origin[1]} ~{ez+origin[2]} {block_str}\n"

            for x in range(size_x):
                for y in range(size_y):
                    for z in range(size_z):
                        current_block_pos = get_index(x, y, z)
                        block = self.block_index[current_block_pos]
                        if block < 0 : continue
                        if IgnoreAir and self.block_palette[block].name == "minecraft:air" : continue
                        if can_setblock[current_block_pos]: yield process(x, y, z, block)

        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            return False

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            raise RuntimeError(f"{Reader} 并不支持通过函数命令解析为结构")

        def encode(self, Writer):
            if isinstance(Writer, str) : 
                base_path = os.path.realpath(os.path.join(Writer, os.pardir))
                os.makedirs(base_path, exist_ok=True)
                _file = zipfile.ZipFile(Writer, "w")
            else : _file = zipfile.ZipFile(Writer, "w")
            
            # 计分板变量 FileCounter, CountDownTime
            __init__ = [
                "scoreboard objectives add StructureLoader dummy",
                "scoreboard players set ProcessCounter StructureLoader 0",
                "scoreboard players set CountDownTime StructureLoader 0",
                'setblock ~ ~ ~ repeating_command_block["facing_direction"=1]',
                'setblock ~ ~1 ~ chain_command_block["facing_direction"=1]',
                'tellraw @p {"rawtext":[{"text":"请按照以下流程生成建筑：\n1. 在循环命令方块里插入命令\n   function Loader/__loop__\n2. 在连锁命令方块里插入命令\n   function Loader/__wait__\n3. 启动循环命令方块"}]}'
                ]
            __loop__ = [
                "execute if score CountDownTime StructureLoader matches 0 run scoreboard players add ProcessCounter StructureLoader 1",
                "execute if score CountDownTime StructureLoader matches 1.. run scoreboard players remove CountDownTime StructureLoader 1",
                "execute if score ProcessCounter StructureLoader matches 11000.. run scoreboard objectives remove StructureLoader",
                "execute if score ProcessCounter StructureLoader matches 11000.. run setblock ~ ~ ~ air"]
            __wait__ = []
            
            __commands__, proccess_counter = [], 1
            range_x = range(0, self.Common.size[0], 80)
            range_z = range(0, self.Common.size[2], 80)
            subfile_name = "Loader/process%s.mcfunction"
            loop_command = "execute if score CountDownTime StructureLoader matches 0 " + \
                "if score ProcessCounter StructureLoader matches %s run function StructureLoader/process%s"
            wait_command_1 = "execute if score ProcessCounter StructureLoader matches %s run tickingarea remove ImportProcess_982"
            wait_command_2 = "execute if score ProcessCounter StructureLoader matches %s run tickingarea add ~%s ~ ~%s ~%s ~ ~%s ImportProcess_982"
            wait_command_3 = "execute if score ProcessCounter StructureLoader matches %s run scoreboard players set CountDownTime StructureLoader 300"
            for ox, oz in itertools.product(range_x, range_z) :
                NewCommon = self.Common.split( (ox, 0, oz), (min(ox+80, self.Common.size[0]-1), 
                    self.Common.size[1]-1, min(oz+80, self.Common.size[2]-1)))
                __wait__.append(wait_command_1 % proccess_counter)
                __wait__.append(wait_command_2 % (proccess_counter, ox, oz, ox+80, oz+80))
                __wait__.append(wait_command_3 % proccess_counter)
                proccess_counter += 1

                for command in self.generate_command(NewCommon, self.IgnoreAir, (ox, 0, oz)) : 
                    if len(__commands__) >= 5000 : 
                        with _file.open(subfile_name%proccess_counter, "w") as f :
                            f.write("".join( __commands__ ).encode("utf-8"))
                        __loop__.append(loop_command % (proccess_counter, proccess_counter))

                        __commands__.clear()
                        proccess_counter += 1
                    else : __commands__.append(command)

                if not __commands__ : continue
                with _file.open(subfile_name%proccess_counter, "w") as f : 
                    f.write("".join( __commands__ ).encode("utf-8"))
                __loop__.append(loop_command % (proccess_counter, proccess_counter))
                proccess_counter += 1

            for key, val in {"__loop__":__loop__, "__init__":__init__, "__wait__":__wait__}.items() :
                f = _file.open("Loader/%s.mcfunction" % key, "w")
                f.write("\n".join( val ).encode("utf-8"))
                f.close()

    class TextCommand(FunctionCommand) :
        
        @classmethod
        def verify(self, Data:Union[io.IOBase, nbt.TAG_Compound, dict], 
            DataType:Literal["nbt", "json", "bytes"]) :
            return False
        
        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            raise RuntimeError(f"{Reader} 并不支持通过函数命令解析为结构")

        def encode(self, Writer):
            if isinstance(Writer, str) : 
                base_path = os.path.realpath(os.path.join(Writer, os.pardir))
                os.makedirs(base_path, exist_ok=True)
                _file = open(Writer, "w+", encoding="utf-8")
            else : _file = Writer
            if not isinstance(_file, io.TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")

            range_x = range(0, self.Common.size[0], 80)
            range_z = range(0, self.Common.size[2], 80)
            for ox, oz in itertools.product(range_x, range_z) :
                NewCommon = self.Common.split( (ox, 0, oz), (min(ox+80, self.Common.size[0]-1), 
                    self.Common.size[1]-1, min(oz+80, self.Common.size[2]-1)))
                _file.write("/tickingarea remove ImportProcess_982\n")
                _file.write("/tickingarea add ~%s ~ ~%s ~%s ~ ~%s ImportProcess_982\n" % (ox, oz, ox+80, oz+80))
                for command in self.generate_command(NewCommon, self.IgnoreAir, (ox, 0, oz)) :
                    _file.write(f"/{command}")



SupportCodecs = [Codecs.BDX, Codecs.AXIOM_BP, Codecs.CONSTRUCTION, Codecs.BDS, Codecs.COVSTRUCTURE,
    Codecs.NEXUS_NP, Codecs.NEXUS, Codecs.MCSTRUCTURE, Codecs.SCHEMATIC, Codecs.RUNAWAY, Codecs.KBDX, 
    Codecs.MIANYANG_V1, Codecs.MIANYANG_V2, Codecs.MIANYANG_V3, Codecs.GANGBAN_V1, Codecs.GANGBAN_V2,
    Codecs.GANGBAN_V3, Codecs.GANGBAN_V4, Codecs.GANGBAN_V5, Codecs.GANGBAN_V6, Codecs.GANGBAN_V7, 
    Codecs.FUHONG_V1, Codecs.FUHONG_V2, Codecs.FUHONG_V3, Codecs.FUHONG_V4, #Codecs.FUHONG_V5, 
    Codecs.QINGXU_V1, Codecs.TIMEBUILDER_V1, Codecs.SCHEM_V1, Codecs.SCHEM_V2, Codecs.SCHEM_V3, 
    Codecs.LITEMATIC_V1, Codecs.JAVASTRUCTURE]

def registerCodecs(CodecsType:type) :
    if Codecs.CodecsBase not in CodecsType.mro() :
        raise TypeError(f"{CodecsType} 是不规范的的解码器")
    if CodecsType not in SupportCodecs :
        SupportCodecs.append(CodecsType)

def getStructureType(IO_Byte_Path: Union[str, bytes, io.IOBase]) :
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

    for class_obj in SupportCodecs :
        if data_type == "bytes" : data.seek(0)
        try : bool1 = class_obj.verify(data, data_type)
        except : traceback.print_exc() ; continue

        if bool1 : 
            if isinstance(IO_Byte_Path, io.IOBase) : IO_Byte_Path.seek(0)
            return class_obj
    if isinstance(IO_Byte_Path, io.IOBase) : IO_Byte_Path.seek(0)



