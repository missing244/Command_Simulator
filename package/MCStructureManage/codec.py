from . import nbt
from .block import Block, GetNbtID, JE_Transfor_BE_Block
from .block import GenerateContainerNBT, GenerateSignNBT, GenerateCommandBlockNBT
from .__private import TypeCheckList, BiList
from . import StructureBDX, StructureMCS, StructureSCHEM
from . import StructureRUNAWAY, StructureSCHEMATIC

from typing import Union,Dict,Tuple,Literal,List
import abc, re, io, json, array, itertools, urllib.parse, random, os, math, zipfile
ExecuteTest = re.compile("[ ]*?/?[ ]*?execute[ ]*?(as|at|align|anchored|facing|in|positioned|rotated|if|unless|run)")
CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
Translate = json.load(fp=open(os.path.join(CurrentPath, "res", "translate.json"), "r", encoding="utf-8"))

def GenerateEntity(id:str, pos:Tuple[int, int, int], name:str=None) :
    Snbt = """{Air:300s,Armor:[{Count:0b,Damage:0s,Name:"",WasPickedUp:0b},{Count:0b,Damage:0s,Name:"",WasPickedUp:0b},
    {Count:0b,Damage:0s,Name:"",WasPickedUp:0b},{Count:0b,Damage:0s,Name:"",WasPickedUp:0b},{Count:0b,Damage:0s,Name:"",WasPickedUp:0b}],
    Attributes:[{Base:0.0f,Current:0.0f,DefaultMax:16.0f,DefaultMin:0.0f,Max:16.0f,Min:0.0f,Name:"minecraft:absorption"},
    {Base:0.0f,Current:0.0f,DefaultMax:1.0f,DefaultMin:0.0f,Max:1.0f,Min:0.0f,Name:"minecraft:knockback_resistance"},
    {Base:0.25f,Current:0.25f,DefaultMax:3.4028234663852886e+38f,DefaultMin:0.0f,Max:3.4028234663852886e+38f,Min:0.0f,Name:"minecraft:movement"},
    {Base:0.019999999552965164f,Current:0.019999999552965164f,DefaultMax:3.4028234663852886e+38f,DefaultMin:0.0f,
    Max:3.4028234663852886e+38f,Min:0.0f,Name:"minecraft:underwater_movement"},{Base:0.019999999552965164f,Current:0.019999999552965164f,
    DefaultMax:3.4028234663852886e+38f,DefaultMin:0.0f,Max:3.4028234663852886e+38f,Min:0.0f,Name:"minecraft:lava_movement"},
    {Base:16.0f,Current:16.0f,DefaultMax:2048.0f,DefaultMin:0.0f,Max:2048.0f,Min:0.0f,Name:"minecraft:follow_range"},
    {Base:2.0f,Current:2.0f,DefaultMax:2.0f,DefaultMin:2.0f,Max:2.0f,Min:2.0f,Name:"minecraft:attack_damage"}],
    Chested:0b,Color:0b,Color2:0b,Dead:0b,DeathTime:0s,FallDistance:0.0f,HurtTime:0s,Invulnerable:0b,IsAngry:0b,IsAutonomous:0b,IsBaby:0b,
    IsEating:0b,IsGliding:0b,IsGlobal:0b,IsIllagerCaptain:0b,IsOrphaned:0b,IsOutOfControl:0b,IsPregnant:0b,IsRoaring:0b,IsScared:0b,IsStunned:0b,
    IsSwimming:0b,IsTamed:0b,IsTrusting:0b,LeasherID:-1l,Lifetime:270,LootDropped:1b,Mainhand:[{Count:0b,Damage:0s,Name:"",WasPickedUp:0b}],
    MarkVariant:0,NaturalSpawn:0b,Offhand:[{Count:0b,Damage:0s,Name:"",WasPickedUp:0b}],OnGround:1b,OwnerNew:-1l,Persistent:1b,
    PortalCooldown:0,Pos:[0.5f,-59.0f,0.5f],Rotation:[0.0f,0.0f],Saddled:0b,Sheared:0b,ShowBottom:0b,Sitting:0b,SkinID:0,
    SpawnedByNight:0b,Strength:0,StrengthMax:0,Surface:0b,Tags:[],TargetID:-1l,TradeExperience:0,TradeTier:0,UniqueID:-51539607540l,
    Variant:0,canPickupItems:1b,definitions:[],expDropEnabled:1b,hasSetCanPickupItems:1b,identifier:"",internalComponents:{},Health:5s,Age:-1s,
    Item:{Name:"minecraft:sand",Count:1b,Damage:0s}}"""
    Snbt = """{Air:300s,expDropEnabled:1b,hasSetCanPickupItems:1b,identifier:"",internalComponents:{},Health:5s,Age:-1s,
    Item:{Name:"minecraft:sand",Count:1b,Damage:0s}}"""
    NBTdata = nbt.read_from_snbt_file(io.StringIO(Snbt)).get_tag()
    NBTdata["UniqueID"] = nbt.TAG_Long(random.randint(-51539607540, 51539607540))
    NBTdata["identifier"] = nbt.TAG_String(id if id.startswith("minecraft:") else f"minecraft:{id}")
    NBTdata["Pos"] = nbt.TAG_List(array.array("f", pos), type=nbt.TAG_Float.type)
    if isinstance(name, str) : NBTdata["CustomName"] = nbt.TAG_String(name)

    return NBTdata



class Codecs :
    """
    编解码器类
    ---------------------------------
    * 通过 Codecs.XXXX 调用指定的编解码器
    ---------------------------------
    * 可用类 BDX: 解析/生成 bdx 文件的编解码器
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
    * 可用类 FunctionCommand: 生成 函数命令 zip文件的编码器
    * 可用类 TextCommand: 生成 文本命令 txt文件的编码器
    """

    class CodecsBase(abc.ABC) :

        def __init__(self, Common, IgnoreAir:bool=True):
            from . import CommonStructure
            self.Common:CommonStructure = Common
            self.IgnoreAir:bool = IgnoreAir

        @abc.abstractmethod
        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]) :
            raise NotImplementedError()

        @abc.abstractmethod
        def encode(self, Writer:Union[str, io.BufferedIOBase]) :
            raise NotImplementedError()

    class BDX(CodecsBase) :

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
                
                ContainerNbt = GenerateContainerNBT(block.name)
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

                ContainerNbt = GenerateContainerNBT(block.name)
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
                
                if block_index < 0 : continue
                if IgnoreAir and self.block_palette[block_index].name == "minecraft:air" : continue
                if index in self.block_nbt : append_function(
                    PlaceBlockWithNBTData(2*block_index, 2*block_index+1, self.block_nbt[index]) )
                else : append_function( PlaceBlockWithBlockStates(2*block_index, 2*block_index+1) )

            BDX.save_as(Writer)

    class MCSTRUCTURE(CodecsBase) :

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

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]):
            from .C_API import codecs_parser_schematic
            SCHMATIC = StructureSCHEMATIC.Schematic.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__( SCHMATIC.size )

            RunTimeBlock = StructureSCHEMATIC.RuntimeID_to_Block
            BlockPaletteArray = array.array("H", b"\x00\x00"*65536)
            codecs_parser_schematic(SCHMATIC.block_index, SCHMATIC.block_data, 
                StructureObject.block_index, BlockPaletteArray, SCHMATIC.size)

            BlockList = [None] * max(BlockPaletteArray)
            for block_id, block_index in enumerate(BlockPaletteArray) :
                if not block_index : continue
                BlockList[block_index-1] = Block(RunTimeBlock[block_id >> 8], block_id & 255)
            StructureObject.block_palette.__init__( [Block("minecraft:air")] + BlockList )

        def encode(self, Writer:Union[str, io.BufferedIOBase]):
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

        def operation_structure(self, Schma_File:StructureSCHEM.Schem_V1) :
            from .C_API import codecs_parser_schem
            StructureObject = self.Common
            StructureObject.__init__( Schma_File.size )

            blocks:List[Block] = [None] * len(Schma_File.block_palette)
            for index, block in Schma_File.block_palette.items() : blocks[index] = JE_Transfor_BE_Block(block)
            StructureObject.block_palette.__init__(blocks)

            NBTBlockBit = array.array("B", b"\x00"*len(StructureObject.block_palette))
            for index, block in enumerate(StructureObject.block_palette) : 
                if GenerateContainerNBT(block.name) : NBTBlockBit[index] = 1
                elif GenerateSignNBT(block.name) : NBTBlockBit[index] = 2
                elif GenerateCommandBlockNBT(block.name) : NBTBlockBit[index] = 3
            
            NBTDict = codecs_parser_schem(Schma_File.block_index, StructureObject.block_index,
                NBTBlockBit, Schma_File.size)
            for key, value in NBTDict.items() :
                block = StructureObject.block_palette[StructureObject.block_index[key]]
                if value == 1 : StructureObject.block_nbt[key] = GenerateContainerNBT(block.name)
                elif value == 2 : StructureObject.block_nbt[key] = GenerateSignNBT(block.name)
                elif value == 3 : StructureObject.block_nbt[key] = GenerateCommandBlockNBT(block.name)


            """
                O_X, O_Y, O_Z = Schma_File.size
                block_index, pos_x, pos_y, pos_z = 0, 0, 0, 0
                for index_data in Schma_File.block_index :
                    block_index |= 0b0111_1111 & index_data
                    if index_data >= 0 :
                        StructureObject.set_block(pos_x, pos_y, pos_z, block_index)
                        nbtdata = GenerateContainerNBT(blocks[block_index].name)
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

        def decode(self, Reader:Union[str, bytes, io.BufferedIOBase]):
            Schma_File = StructureSCHEM.Schem_V2.from_buffer(Reader)
            self.operation_structure(Schma_File)

    class MIANYANG_V1(CodecsBase) :

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
                    block_obj = Block(Struct1.block_palette[block[0]], block[1])
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    try : BlockJsonData = json.loads(block[-1])
                    except : continue
                    nbtstr = urllib.parse.unquote(BlockJsonData['blockCompleteNBT'])

                    node = nbt.NBT_Builder()
                    CommandBlockNbt = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(CommandMatch.search(nbtstr).group()),
                        CustomName = node.string(CustomNameMatch.search(nbtstr).group()),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(int( AutoMatch.search(nbtstr).group() )),
                        TickDelay = node.int(int( TickDelayMatch.search(nbtstr).group() )),
                        conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                        TrackOutput = node.byte(1),
                        Version = node.int(int( VersionMatch.search(nbtstr).group() )),
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
                    block_obj = Block(Struct1.block_palette[block[0]], block[1])
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    try : BlockJsonData = json.loads(block[-1])
                    except : continue
                    nbtstr = urllib.parse.unquote(BlockJsonData['blockCompleteNBT'])

                    if block_obj.name.endswith("command_block") : 
                        node = nbt.NBT_Builder()
                        CommandBlockNbt = node.compound(
                            id = node.string("CommandBlock"),
                            Command = node.string(CommandMatch.search(nbtstr).group()),
                            CustomName = node.string(CustomNameMatch.search(nbtstr).group()),
                            ExecuteOnFirstTick = node.byte(1),
                            auto = node.byte(int( AutoMatch.search(nbtstr).group() )),
                            TickDelay = node.int(int( TickDelayMatch.search(nbtstr).group() )),
                            conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                            TrackOutput = node.byte(1),
                            Version = node.int(int( VersionMatch.search(nbtstr).group() )),
                        ).build()
                        StructureObject.set_blockNBT(posx, posy, posz, CommandBlockNbt)
                    else :
                        try : nbtObj = nbt.read_from_snbt_file( io.StringIO(nbtstr) ).get_tag()
                        except : continue
                        if "Items" not in nbtObj : continue
                        StructureObject.set_blockNBT(posx, posy, posz, nbtObj)


            for entity in Struct1.entities :
                posx, posy, posz = entity[0]-PosStart[0], entity[1]-PosStart[1], entity[2]-PosStart[2]
                StructureObject.entity_nbt.append( GenerateEntity( entity[4], (posx, posy, posz), entity[3]) )

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
                    block_obj = Block(Struct1.block_palette[block[0]], block[1])
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    try : BlockJsonData = json.loads(block[-1])
                    except : continue
                    nbtstr = urllib.parse.unquote(BlockJsonData['blockCompleteNBT'])

                    if block_obj.name.endswith("command_block") : 
                        node = nbt.NBT_Builder()
                        CommandBlockNbt = node.compound(
                            id = node.string("CommandBlock"),
                            Command = node.string(CommandMatch.search(nbtstr).group()),
                            CustomName = node.string(CustomNameMatch.search(nbtstr).group()),
                            ExecuteOnFirstTick = node.byte(1),
                            auto = node.byte(int( AutoMatch.search(nbtstr).group() )),
                            TickDelay = node.int(int( TickDelayMatch.search(nbtstr).group() )),
                            conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                            TrackOutput = node.byte(1),
                            Version = node.int(int( VersionMatch.search(nbtstr).group() )),
                        ).build()
                        StructureObject.set_blockNBT(posx, posy, posz, CommandBlockNbt)
                    else :
                        try : nbtObj = nbt.read_from_snbt_file( io.StringIO(nbtstr) ).get_tag()
                        except : continue
                        if "Items" not in nbtObj : continue
                        StructureObject.set_blockNBT(posx, posy, posz, nbtObj)


            for entity in Struct1.entities :
                posx, posy, posz = entity[0]-PosStart[0], entity[1]-PosStart[1], entity[2]-PosStart[2]
                StructureObject.entity_nbt.append( GenerateEntity( entity[4], (posx, posy, posz), entity[3]) )

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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V1.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.__init__( Struct1.size )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = Struct1.origin[0], Struct1.origin[1], Struct1.origin[2]
            for block in Struct1.blocks :
                block_obj = Block(Struct1.block_palette[block["id"]], block.get("aux", 0))
                posx, posy, posz = block["p"][0] - O_X, block["p"][1] - O_Y, block["p"][2] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

                if "cmds" not in block : continue
                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(block["cmds"]["cmd"]),
                    CustomName = node.string(block["cmds"]["name"]),
                    ExecuteOnFirstTick = node.byte(1),
                    auto = node.byte(block["cmds"]["on"]),
                    TickDelay = node.int(block["cmds"]["tick"]),
                    TrackOutput = node.byte(block["cmds"]["should"]),
                    conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                    Version = node.int(38 if ExecuteTest.match(block["cmds"]["cmd"]) else 19),
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V2.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for block in Struct1.blocks :
                block_obj = Block(Struct1.block_palette[block["id"]], block.get("aux", 0))
                posx, posy, posz = block["p"][0] - O_X, block["p"][1] - O_Y, block["p"][2] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

                if "cmds" not in block : continue
                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(block["cmds"]["cmd"]),
                    CustomName = node.string(block["cmds"]["name"]),
                    ExecuteOnFirstTick = node.byte(1),
                    auto = node.byte(block["cmds"]["on"]),
                    TickDelay = node.int(block["cmds"]["tick"]),
                    TrackOutput = node.byte(block["cmds"]["should"]),
                    conditionalMode = node.byte(block_obj.states["conditional_bit"]),
                    Version = node.int(38 if ExecuteTest.match(block["cmds"]["cmd"]) else 19),
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
                    block_obj = Block(Struct1.block_palette[block[0]], block[1])
                    posx, posy, posz = block[2] + o_x, block[3] - o_y, block[4] + o_z
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    if block[5] != "nbt" : continue

                    NbtName = GetNbtID(block_obj.name)
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
                    block_obj = Block(Struct1.block_palette[block[0]], block[1])
                    posx, posy, posz = block[2] + o_x, block[3] - o_y, block[4] + o_z
                    StructureObject.set_block(posx, posy, posz, block_obj)

                    if block[-1].__class__ is not str : continue
                    if block[5] != "nbt" : continue

                    NbtName = GetNbtID(block_obj.name)
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
                if datatype != 1 : StructureObject.set_block(posx, posy, posz, Block(Struct1.block_palette[blockindex], datavar))
                Pointer += 6
                if datatype == 3 : continue

                blocknbt =  blockdata[Pointer]
                Pointer += 1
                if datatype == 1 :
                    node = nbt.NBT_Builder()
                    BlockData = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(blocknbt["cmd"]),
                        CustomName = node.string(blocknbt["name"]),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(blocknbt["auto"]),
                        TickDelay = node.int(blocknbt["delay"]),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(blocknbt["condition"]),
                        Version = node.int(38 if ExecuteTest.match(blocknbt["cmd"]) else 19),
                    ).build()
                    StructureObject.set_block(posx, posy, posz, Block(CommandBlockGangBan[datavar], blockindex))
                    StructureObject.set_blockNBT(posx, posy, posz, BlockData)
                elif datatype == 4 : 
                    Contanier = GenerateContainerNBT( Struct1.block_palette[blockindex] )
                    if Contanier is None : continue
                    for item in blocknbt :
                        if None in set(item.values()) : continue
                        itemID = item["ns"] if item["ns"].startswith("minecraft:") else "minecraft:" + item["ns"]
                        Contanier["Items"].append(nbt.TAG_Compound({
                            "Name": nbt.TAG_String(itemID),
                            "Count": nbt.TAG_Byte(item["num"]),
                            "Damage": nbt.TAG_Short(item["aux"]),
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
                    for Item in NBT_Object["Items"] :
                        data_list[-1].append({"ns":Item["Name"].value,
                        "aux":Item["Damage"].value,"num":Item["Count"].value,"slot":Item["Slot"].value})
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V6.from_buffer(Reader)
            if Struct1.size is not None :
                PosStart, PosEnd = [-1,-1,-1], Struct1.size
            else : PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            pos_cache, real_pos = [0, 0, 0], [0, 0, 0]
            TranslateReverse = {j:i for i,j in Translate["Item"].items()}
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
                        CustomName = node.string(block[-1]["name"]),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(block[-1]["auto"]),
                        TickDelay = node.int(block[-1]["delay"]),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(block[-1]["condition"]),
                        Version = node.int(38 if ExecuteTest.match(block[-1]["cmd"]) else 19),
                    ).build()
                    StructureObject.set_block(*real_pos, Block(CommandBlockGangBan[block[4]], block[3]))
                    StructureObject.set_blockNBT(*real_pos, BlockData)
                else : 
                    StructureObject.set_block(*real_pos, Block(Struct1.block_palette[block[3]], block[4]))
                    if block[-1].__class__ is list :
                        Contanier = GenerateContainerNBT( Struct1.block_palette[block[3]] )
                        if Contanier is None : continue
                        for item in block[-1] :
                            if None in set(item.values()) : continue
                            itemID = item["ns"] if item["ns"].startswith("minecraft:") else "minecraft:" + item["ns"]
                            Contanier["Items"].append(nbt.TAG_Compound({
                                "Name": nbt.TAG_String(itemID),
                                "Count": nbt.TAG_Byte(item["num"]),
                                "Damage": nbt.TAG_Short(item["aux"]),
                                "Slot": nbt.TAG_Byte(item["slot"]),
                                "Block": Block(itemID, 0).to_nbt()
                            }))
                        StructureObject.set_blockNBT(*real_pos, Contanier)

            for entity in Struct1.entities :
                entityNBT = GenerateEntity(entity[4], (entity[0]-PosStart[0], entity[1]-PosStart[1], entity[2]-PosStart[2]))
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
                    data_list[3], data_list[4] = Translate["Item"].get(ItemName, "石头"), "minecraft:item"
                else : 
                    EntityName = entity["identifier"].value.replace("minecraft:", "", 1)
                    data_list[3], data_list[4] = Translate["Entity"].get(EntityName, ""), entity["identifier"].value
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
                    for Item in NBT_Object["Items"] :
                        data_list[-1].append({"ns":Item["Name"].value,
                        "aux":Item["Damage"].value,"num":Item["Count"].value,"slot":Item["Slot"].value})
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V7.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            pos_cache = [0, 0, 0]
            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            TranslateReverse = {j:i for i,j in Translate["Item"].items()}
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
                        CustomName = node.string(block[-1]["name"]),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(block[-1]["auto"]),
                        TickDelay = node.int(block[-1]["delay"]),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(block[-1]["condition"]),
                        Version = node.int(38 if ExecuteTest.match(block[-1]["cmd"]) else 19),
                    ).build()
                    StructureObject.set_block(posx, posy, posz, Block(CommandBlockGangBan[block[4]], block[3]))
                    StructureObject.set_blockNBT(posx, posy, posz, BlockData)
                else : 
                    StructureObject.set_block(posx, posy, posz, Block(Struct1.block_palette[block[3]], block[4]))
                    if block[-1].__class__ is list :
                        Contanier = GenerateContainerNBT( Struct1.block_palette[block[3]] )
                        if Contanier is None : continue
                        for item in block[-1] :
                            if None in set(item.values()) : continue
                            itemID = item["ns"] if item["ns"].startswith("minecraft:") else "minecraft:" + item["ns"]
                            Contanier["Items"].append(nbt.TAG_Compound({
                                "Name": nbt.TAG_String(itemID),
                                "Count": nbt.TAG_Byte(item["num"]),
                                "Damage": nbt.TAG_Short(item["aux"]),
                                "Slot": nbt.TAG_Byte(item["slot"]),
                                "Block": Block(itemID, 0).to_nbt()
                            }))
                        StructureObject.set_blockNBT(posx, posy, posz, Contanier)

            for entity in Struct1.entities :
                entityNBT = GenerateEntity(entity[4], (entity[0], entity[1], entity[2]))
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
                    data_list[3], data_list[4] = Translate["Item"].get(ItemName, "石头"), "minecraft:item"
                else : 
                    EntityName = entity["identifier"].value.replace("minecraft:", "", 1)
                    data_list[3], data_list[4] = Translate["Entity"].get(EntityName, ""), entity["identifier"].value
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
                    for Item in NBT_Object["Items"] :
                        data_list[-1].append({"ns":Item["Name"].value,
                        "aux":Item["Damage"].value,"num":Item["Count"].value,"slot":Item["Slot"].value})
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.RunAway.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for block in Struct1.blocks :
                block_obj = Block(block["name"], block.get("aux", 0))
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.Kbdx.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            block_palette = {j:i for i,j in Struct1.block_palette.items()}

            for block in Struct1.blocks :
                block_obj = Block(block_palette[block[3]], block[4])
                posx, posy, posz = block[0] - O_X, block[1] - O_Y, block[2] - O_Z
                StructureObject.set_block(posx, posy, posz, block_obj)

            for snbt in Struct1.block_nbt :
                posx, posy, posz = snbt["x"] - O_X, snbt["y"] - O_Y, snbt["z"] - O_Z
                node = nbt.NBT_Builder()
                if snbt["id"].endswith("command_block") :
                    BlockData = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(snbt["Command"]),
                        CustomName = node.string(snbt["CustomName"]),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(not snbt["redstone"]),
                        TickDelay = node.int(snbt["TickDelay"]),
                        TrackOutput = node.byte(1),
                        conditionalMode = node.byte(snbt["isConditional"]),
                        Version = node.int(38 if ExecuteTest.match(snbt["Command"]) else 19),
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V1.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]

            for block in Struct1.blocks :
                block_obj = Block(block["name"], block.get("aux", 0))
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V2.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )


            def Command(x:int, y:int, z:int, block_id:str, data:Union[Dict[Literal["b", "e"], str], Tuple[str, int, int, str]]) :
                if data.__class__ is dict :
                    NBT_obj = nbt.read_from_snbt_file( io.StringIO(Nbtdata["e"]) )
                    StructureObject.set_blockNBT(x, y, z, NBT_obj.get_tag())
                else :
                    CommandBlockNBT = GenerateCommandBlockNBT("command_block")
                    if CommandBlockNBT is None : return None
                    CommandStr = data[0] if isinstance(data[0], str) else ""
                    CommandBlockNBT["Command"] = nbt.TAG_String(CommandStr)
                    CommandBlockNBT["TickDelay"] = nbt.TAG_Int(data[1])
                    CommandBlockNBT["auto"] = nbt.TAG_Byte(data[2])
                    CommandBlockNBT["CustomName"] = nbt.TAG_String(data[3])
                    CommandBlockNBT["Version"] = nbt.TAG_Int(38 if ExecuteTest.match(CommandStr) else 19)
                    StructureObject.set_blockNBT(x, y, z, CommandBlockNBT)

            def Container(x:int, y:int, z:int, block_id:str, data:Union[Dict[Literal["b", "e"], str], Dict[Literal["d"], List[dict]]]) :
                if "e" in data :
                    NBT_obj = nbt.read_from_snbt_file( io.StringIO(Nbtdata["e"]) )
                    StructureObject.set_blockNBT(x, y, z, NBT_obj.get_tag())
                else : 
                    ContanierNBT = GenerateContainerNBT( block_id )
                    if ContanierNBT is None : return None
                    for item in data.get("d", []) :
                        itemID = item["name"] if item["name"].startswith("minecraft:") else "minecraft:%s"%item["name"]
                        ContanierNBT["Items"].append(nbt.TAG_Compound({
                            "Name": nbt.TAG_String(itemID),
                            "Count": nbt.TAG_Byte(item["count"]),
                            "Damage": nbt.TAG_Short(item["damage"]),
                            "Slot": nbt.TAG_Byte(item["slot"]),
                            "Block": Block(itemID, 0).to_nbt()
                        }))
                    StructureObject.set_blockNBT(x, y, z, ContanierNBT)


            for chunk in Struct1.chunks :
                for data_obj in chunk["block"] :
                    if "en" in data_obj :
                        entity_id = data_obj["en"]
                        for posx,posy,posz in zip(data_obj["x"], data_obj["y"], data_obj["z"]) :
                            StructureObject.entity_nbt.append(GenerateEntity(entity_id, (posx, posy, posz)))
                    elif "n" in data_obj :
                        iter1 = data_obj.get("a", itertools.repeat(0))
                        if isinstance(iter1, int) : iter1 = itertools.repeat(iter1)
                        if "d" in data_obj : iter2 = data_obj["d"]
                        elif "c" in data_obj : iter2 = zip(data_obj["c"]["c"], data_obj["c"]["t"], data_obj["c"]["a"], data_obj["c"]["n"])
                        else : iter2 = itertools.repeat(None)
                        for posx,posy,posz,datavar,Nbtdata in zip(data_obj["x"], data_obj["y"], data_obj["z"], iter1, iter2) :
                            posx, posy, posz = posx-PosStart[0], posy-PosStart[1], posz-PosStart[2]
                            block_obj = Block(data_obj["n"], datavar)
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

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V3.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            def Container(id:str, data:List[Tuple[str, int, int, int]]) :
                ContanierNBT = GenerateContainerNBT( id )
                if ContanierNBT is None : return None
                for item in data :
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
                SignNBT = GenerateSignNBT(id)
                if SignNBT is None : return None
                
                SignNBT["FrontText"]["Text"] = nbt.TAG_String(data)
                return SignNBT

            def Command(id:str, data:Tuple[str, int, int, str]) :
                CommandBlockNBT = GenerateCommandBlockNBT(id)
                if CommandBlockNBT is None : return None
                CommandStr = data[0] if isinstance(data[0], str) else ""
                CommandBlockNBT["Command"] = nbt.TAG_String(CommandStr)
                CommandBlockNBT["auto"] = nbt.TAG_Byte(data[2])
                CommandBlockNBT["TickDelay"] = nbt.TAG_Int(data[1])
                CommandBlockNBT["CustomName"] = nbt.TAG_String(data[3])
                CommandBlockNBT["Version"] = nbt.TAG_Int(38 if ExecuteTest.match(CommandStr) else 19)
                return CommandBlockNBT

            for chunk in Struct1.chunks :
                chunk_x, chunk_z = chunk["startX"], chunk["startZ"]
                for data_obj in chunk["block"] :
                    id, datavar = data_obj[0], data_obj[1]
                    Pos1, Pos2, Pos3 = data_obj[2], data_obj[3], data_obj[4]
                    nbtdata = data_obj[5] if len(data_obj) > 5 else []

                    if id.__class__ is str :
                        StructureObject.entity_nbt.append( GenerateEntity(id, 
                        (chunk_x+Pos1, Pos2, chunk_z+Pos3), datavar) )
                    else :
                        block_obj = Block(Struct1.block_palette[id], datavar)
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

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.FuHong_V3()

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
                        NBT_Obj["auto"].value, NBT_Obj["TickDelay"].value, NBT_Obj["CustomName"].value ])
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
                        for item in NBT_Obj["Items"] : block_data_list[BlockHash][-1][-1].append(
                            [item["Name"].value, item["Damage"].value, item["Count"].value, item["Slot"].value]
                        )

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
            Struct1.save_as(Writer)

    class FUHONG_V4(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V4.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            def Container(id:str, data:List[Tuple[str, int, int, int]]) :
                ContanierNBT = GenerateContainerNBT( id )
                if ContanierNBT is None : return None
                for item in data :
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
                SignNBT = GenerateSignNBT(id)
                if SignNBT is None : return None
                SignNBT["FrontText"]["Text"] = nbt.TAG_String(data)
                return SignNBT

            def Command(id:str, data:Tuple[str, int, int, str]) :
                CommandBlockNBT = GenerateCommandBlockNBT(id)
                if CommandBlockNBT is None : return None
                CommandStr = data[0] if isinstance(data[0], str) else ""
                CommandBlockNBT["Command"] = nbt.TAG_String(CommandStr)
                CommandBlockNBT["auto"] = nbt.TAG_Byte(data[2])
                CommandBlockNBT["TickDelay"] = nbt.TAG_Int(data[1])
                CommandBlockNBT["CustomName"] = nbt.TAG_String(data[3])
                CommandBlockNBT["Version"] = nbt.TAG_Int(38 if ExecuteTest.match(CommandStr) else 19)
                return CommandBlockNBT

            for chunk in Struct1.chunks :
                for data_obj in chunk["block"] :
                    id, datavar = data_obj[0], data_obj[1]
                    Pos1, Pos2, Pos3 = data_obj[2], data_obj[3], data_obj[4]
                    nbtdata = data_obj[5] if len(data_obj) > 5 else []

                    if id.__class__ is str :
                        StructureObject.entity_nbt.append( GenerateEntity(id, 
                        (Pos1, Pos2, Pos3), datavar) )
                    else :
                        block_obj = Block(Struct1.block_palette[id], datavar)
                        nbt_iter = [None] * len(Pos1) ; nbt_iter[0:len(nbtdata)] = nbtdata
                        if block_obj.name.endswith("command_block") : NBTFunc = Command
                        elif block_obj.name.endswith("hanging_sign") : NBTFunc = Sign
                        elif block_obj.name.endswith("_sign") : NBTFunc = Sign
                        else : NBTFunc = Container

                        for posx,posy,posz,blockdata in zip(data_obj[2], data_obj[3], data_obj[4], nbt_iter) :
                            posx,posy,posz = posx-PosStart[0], posy-PosStart[1], posz-PosStart[2]
                            StructureObject.set_block(posx,posy,posz, block_obj)
                            if not blockdata : continue
                            NBT_obj = NBTFunc(block_obj.name, blockdata)
                            StructureObject.set_blockNBT(posx,posy,posz, NBT_obj)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.FuHong_V4()

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            ChunkCache:Dict[Tuple[int, int], list] = {}

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                chunk_pos = (posx//32*32, posz//32*32)
                if chunk_pos not in ChunkCache : ChunkCache[chunk_pos] = {"block":{}, "entity":[]}
                block_data_list = ChunkCache[chunk_pos]["block"]
                BlockHash = (BlockID, DataValue)
                if BlockHash not in block_data_list : 
                    block_data_list[BlockHash] = [block_index, DataValue, [], [], []]
                block_data_list[BlockHash][2].append( posx )
                block_data_list[BlockHash][3].append( posy )
                block_data_list[BlockHash][4].append( posz )

                if BlockID.endswith("command_block") : 
                    if block_data_list[BlockHash].__len__() < 6 : block_data_list[BlockHash].append([])
                    if index in self.block_nbt : 
                        NBT_Obj = self.block_nbt[index]
                        block_data_list[BlockHash][-1].append([NBT_Obj["Command"].value, 
                        NBT_Obj["auto"].value, NBT_Obj["TickDelay"].value, NBT_Obj["CustomName"].value ])
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
                        for item in NBT_Obj["Items"] : block_data_list[BlockHash][-1][-1].append(
                            [item["Name"].value, item["Damage"].value, item["Count"].value, item["Slot"].value]
                        )

            for entity in self.entity_nbt :
                EntityID = entity["identifier"].value
                EntityName = entity.get("CustomName", nbt.TAG_String()).value
                posx, posy, posz = entity["Pos"][0].value, entity["Pos"][1].value, entity["Pos"][2].value

                chunk_pos = (posx//32*32, posz//32*32)
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
            Struct1.save_as(Writer)

    class FUHONG_V5(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong_V5.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air") )

            def Container(id:str, data:List[Tuple[str, int, int, int]]) :
                ContanierNBT = GenerateContainerNBT( id )
                if ContanierNBT is None : return None
                for item in data :
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
                SignNBT = GenerateSignNBT(id)
                if SignNBT is None : return None
                SignNBT["FrontText"]["Text"] = nbt.TAG_String(data)
                return SignNBT

            def Command(id:str, data:Tuple[str, int, int, str]) :
                CommandBlockNBT = GenerateCommandBlockNBT(id)
                if CommandBlockNBT is None : return None
                CommandStr = data[0] if isinstance(data[0], str) else ""
                CommandBlockNBT["Command"] = nbt.TAG_String(CommandStr)
                CommandBlockNBT["auto"] = nbt.TAG_Byte(data[2])
                CommandBlockNBT["TickDelay"] = nbt.TAG_Int(data[1])
                CommandBlockNBT["CustomName"] = nbt.TAG_String(data[3])
                CommandBlockNBT["Version"] = nbt.TAG_Int(38 if ExecuteTest.match(CommandStr) else 19)
                return CommandBlockNBT

            for chunk in Struct1.chunks :
                for data_obj in chunk["block"] :
                    id, datavar = data_obj[0], data_obj[1]
                    Pos1, Pos2, Pos3 = data_obj[2], data_obj[3], data_obj[4]
                    nbtdata = data_obj[5] if len(data_obj) > 5 else []

                    if id.__class__ is str :
                        StructureObject.entity_nbt.append( GenerateEntity(id, 
                        (Pos1, Pos2, Pos3), datavar) )
                    else :
                        block_obj = Block(Struct1.block_palette[id], datavar)
                        nbt_iter = [None] * len(Pos1) ; nbt_iter[0:len(nbtdata)] = nbtdata
                        if block_obj.name.endswith("command_block") : NBTFunc = Command
                        elif block_obj.name.endswith("hanging_sign") : NBTFunc = Sign
                        elif block_obj.name.endswith("_sign") : NBTFunc = Sign
                        else : NBTFunc = Container

                        for posx,posy,posz,blockdata in zip(data_obj[2], data_obj[3], data_obj[4], nbt_iter) :
                            posx,posy,posz = posx-PosStart[0], posy-PosStart[1], posz-PosStart[2]
                            StructureObject.set_block(posx,posy,posz, block_obj)
                            if not blockdata : continue
                            NBT_obj = NBTFunc(block_obj.name, blockdata)
                            StructureObject.set_blockNBT(posx,posy,posz, NBT_obj)

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.FuHong_V5()

            Generator = zip(range(len(self.block_index)), self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) ))
            ChunkCache:Dict[Tuple[int, int], list] = {}

            for index, block_index, (posx, posy, posz) in Generator :
                if block_index < 0 : continue
                block:Block = self.block_palette[block_index]
                BlockID, BlockState, DataValue = block.name, block.states, block.dataValue[1]
                if IgnoreAir and BlockID == "minecraft:air" : continue

                chunk_pos = (posx//32*32, posz//32*32)
                if chunk_pos not in ChunkCache : ChunkCache[chunk_pos] = {"block":{}, "entity":[]}
                block_data_list = ChunkCache[chunk_pos]["block"]
                BlockHash = (BlockID, DataValue)
                if BlockHash not in block_data_list : 
                    block_data_list[BlockHash] = [block_index, DataValue, [], [], []]
                block_data_list[BlockHash][2].append( posx )
                block_data_list[BlockHash][3].append( posy )
                block_data_list[BlockHash][4].append( posz )

                if BlockID.endswith("command_block") : 
                    if block_data_list[BlockHash].__len__() < 6 : block_data_list[BlockHash].append([])
                    if index in self.block_nbt : 
                        NBT_Obj = self.block_nbt[index]
                        block_data_list[BlockHash][-1].append([NBT_Obj["Command"].value, 
                        NBT_Obj["auto"].value, NBT_Obj["TickDelay"].value, NBT_Obj["CustomName"].value ])
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
                        for item in NBT_Obj["Items"] : block_data_list[BlockHash][-1][-1].append(
                            [item["Name"].value, item["Damage"].value, item["Count"].value, item["Slot"].value]
                        )

            for entity in self.entity_nbt :
                EntityID = entity["identifier"].value
                EntityName = entity.get("CustomName", nbt.TAG_String()).value
                posx, posy, posz = entity["Pos"][0].value, entity["Pos"][1].value, entity["Pos"][2].value

                chunk_pos = (posx//32*32, posz//32*32)
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
            Struct1.save_as(Writer)

    class QINGXU_V1(CodecsBase) :

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

    class FunctionCommand(CodecsBase) :

        def generate_command(self) :
            IgnoreAir, self = self.IgnoreAir, self.Common
            can_setblock = [True] * len(self.block_index)
            size_x, size_y, size_z = self.size[0], self.size[1], self.size[2]
            block_string = [block.blockString for block in self.block_palette]

            #快速获取方块索引位置
            get_index = lambda x,y,z: (x * size_y + y) * size_z + z
            #评估分割区域体积
            def split_cuboid(L:int, H:int, W:int) :
                MAX_BLOCK_LIMIT = 32768
                a1 = math.ceil(math.sqrt(MAX_BLOCK_LIMIT / H))
                
                # 计算沿各维度的分割次数
                split_L = math.floor(L / math.ceil(L / a1))
                split_W = math.floor(W / math.ceil(W / a1))

                while 1 :
                    can_spread_x, can_spread_z = True, True

                    if split_L < size_x : 
                        if H*(split_L+1)*split_W <= MAX_BLOCK_LIMIT : split_L += 1
                        else : can_spread_x = False
                    else : can_spread_x = False

                    if split_W < size_z : 
                        if H*split_L*(split_W+1) <= MAX_BLOCK_LIMIT : split_W += 1
                        else : can_spread_z = False
                    else : can_spread_z = False

                    if not(can_spread_x or can_spread_z) : break

                return (split_L, H, split_W)
            #测试是否可填充
            def can_fill(x:int, y:int, z:int, block:int) -> bool:
                i = get_index(x, y, z)
                return can_setblock[i] and self.block_index[i] == block

            def process(x:int, y:int, z:int, b:int) :
                ex = x + 1
                while (ex < size_x) and can_fill(ex, y, z, b): ex += 1
                ez = z + 1
                while (ez < size_z) and all(can_fill(i, y, ez, b) for i in range(x, ex)): ez += 1
                ey = y + 1
                while (ey < size_y) and all(can_fill(i, ey, j, b) for i in range(x, ex) for j in range(z, ez)): ey += 1

                for xx in range(x, ex):
                    for yy in range(y, ey):
                        for zz in range(z, ez):
                            i = get_index(xx, yy, zz)
                            can_setblock[i] = False

                ex -= 1 ; ey -= 1 ; ez -= 1
                block_str = block_string[b]

                if x == ex and y == ey and z == ez : 
                    return f"setblock ~{x} ~{y} ~{z} {block_str}\n"
                elif (ex-x+1)*(ey-y+1)*(ez-z+1) <= 32768 :
                    return f"fill ~{x} ~{y} ~{z} ~{ex} ~{ey} ~{ez} {block_str}\n"
                else :
                    split_area = split_cuboid(ex-x+1, ey-y+1, ez-z+1)
                    range1 = range(x, ex+1, split_area[0])
                    range2 = range(y, ey+1, split_area[1])
                    range3 = range(z, ez+1, split_area[2])
                    strlist:List[str] = []
                    for xx, yy, zz in itertools.product(range1, range2, range3) :
                        min_x, min_y, min_z = min(xx+split_area[0]-1, ex), min(yy+split_area[1]-1, ey), min(zz+split_area[2]-1, ez)
                        strlist.append( f"fill ~{xx} ~{yy} ~{zz} ~{min_x} ~{min_y} ~{min_z} {block_str}\n" )
                    return strlist

            for x in range(size_x):
                for y in range(size_y):
                    for z in range(size_z):
                        current_block_pos = get_index(x, y, z)
                        block = self.block_index[current_block_pos]
                        if block < 0 : continue
                        if IgnoreAir and self.block_palette[block].name == "minecraft:air" : continue
                        if can_setblock[current_block_pos]: yield process(x, y, z, block)

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            raise RuntimeError(f"{Reader} 并不支持通过函数命令解析为结构")

        def encode(self, Writer):
            if isinstance(Writer, str) : 
                base_path = os.path.realpath(os.path.join(Writer, os.pardir))
                os.makedirs(base_path, exist_ok=True)
                _file = zipfile.ZipFile(Writer, "w")
            else : _file = zipfile.ZipFile(Writer, "w")
            
            __loop__ = ["scoreboard objectives add StructureLoader dummy",
            "scoreboard players add Time StructureLoader 1",
            "execute if score Time StructureLoader matches 5000.. run scoreboard objectives remove StructureLoader"
            "execute if score Time StructureLoader matches 5000.. run setblock ~ ~ ~ air"]
            
            __commands__, counter1 = [], 1
            for command in self.generate_command() :
                if command.__class__ is str : __commands__.append(command)
                else : __commands__.extend( command )

                if len(__commands__) < 5000 : continue
                with _file.open(f"StructureLoader/subchunk{counter1}.mcfunction", "w") as f :
                    f.write("".join( __commands__[0:5000] ).encode("utf-8"))
                loop_command = f"execute if score Time StructureLoader matches {counter1} run function StructureLoader/subchunk{counter1}.mcfunction"
                __loop__.insert(-2, loop_command)
                del __commands__[0:5000] ; counter1 += 1

            if __commands__ :
                with _file.open(f"StructureLoader/subchunk{counter1}.mcfunction", "w") as f : f.write("".join( __commands__ ).encode("utf-8"))
                loop_command = f"execute if score Time StructureLoader matches {counter1} run function StructureLoader/subchunk{counter1}.mcfunction"
                __loop__.insert(-2, loop_command)

            f = _file.open("StructureLoader/__loop__.mcfunction", "w")
            f.write("\n".join( __loop__ ).encode("utf-8"))
            f.close()

    class TextCommand(FunctionCommand) :
        
        def encode(self, Writer):
            if isinstance(Writer, str) : 
                base_path = os.path.realpath(os.path.join(Writer, os.pardir))
                os.makedirs(base_path, exist_ok=True)
                _file = open(Writer, "w+", encoding="utf-8")
            else : _file = Writer
            if not isinstance(_file, io.TextIOBase) : raise TypeError("buffer 参数需要文本缓冲区类型")

            for command in self.generate_command() :
                if command.__class__ is str : _file.write(f"/{command}")
                else : _file.write( "".join(f"/{i}" for i in command) )


