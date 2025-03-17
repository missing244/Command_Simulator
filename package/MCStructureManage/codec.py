from . import nbt, Block
from . import StructureBDX, StructureMCS
from . import StructureRUNAWAY, StructureSCHEMATIC

from typing import Union,List,Dict,Tuple,Literal,TypedDict
import abc, re, os, io, json, array, itertools, urllib.parse, ctypes


class Codecs :
    """
    编解码器类
    ---------------------------------
    * 通过 Codecs.XXXX 调用指定的编解码器
    ---------------------------------
    * 可用类 BDX: 解析/生成 bdx 文件的编解码器
    * 可用类 MCSTRUCTURE: 解析/生成 mcstructure 文件的编解码器
    * 可用类 SCHEMATIC: 解析/生成 schematic 文件的编解码器
    * 可用类 MIANYANG: 解析/生成 绵阳 结构文件的编解码器
    * 可用类 GANGBAN_V1: 解析/生成 钢板 结构文件的编解码器
    * 可用类 GANGBAN_V2: 解析/生成 钢板 结构文件的编解码器
    * 可用类 GANGBAN_V3: 解析/生成 钢板 结构文件的编解码器
    * 可用类 RunAway: 解析/生成 跑路官方 结构文件的编解码器
    * 可用类 FUHONG: 解析/生成 FUHONG 结构文件的编解码器
    * 可用类 QINGXU: 解析/生成 情绪 结构文件的编解码器
    """

    class CodecsBase(abc.ABC) :

        def __init__(self, Common, IgnoreAir:bool=True):
            from . import CommonStructure
            self.Common:CommonStructure = Common
            self.IgnoreAir:bool = IgnoreAir

        @abc.abstractmethod
        def decode(self, Reader:Union[str, bytes, io.RawIOBase]) :
            raise NotImplementedError()

        @abc.abstractmethod
        def encode(self, Writer:Union[str, io.RawIOBase]) :
            raise NotImplementedError()

    class BDX(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.RawIOBase]) :
            CommandBlockID = ["minecraft:command_block", "minecraft:repeating_command_block", 
                "minecraft:chain_command_block"]
            BDX = StructureBDX.BDX_File.from_buffer(Reader)
            PosStart, PosEnd = BDX.get_volume()

            StructureObject = self.Common
            StructureObject.__init__( [j-i+1 for i,j in zip(PosStart, PosEnd)] )
            StructureObject.block_palette.append( Block("minecraft:air", {}) )

            BlockCount:int = 0
            ConstStr = BDX.const_str
            Blocks:Dict[str, Dict[Union[str,int], Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]]] ={}

            def RegisterBlock(BlockDict:dict, id:str, data_or_state:Union[str, int]) -> int :
                nonlocal BlockCount
                id = TransforNamespaceID(id)
                if id not in BlockDict : BlockDict[id] = {}
                if data_or_state not in BlockDict[id] :
                    if isinstance(data_or_state, str) : BlockStates = StringTransforBlockStates(id, data_or_state)
                    elif isinstance(data_or_state, int) : BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    BlockDict[id][data_or_state] = {"name": id, "states": BlockStates, "index": BlockCount+1 }
                    BlockCount += 1
                return BlockDict[id][data_or_state]

            def Operation_0x05(Oper: StructureBDX.OperationCode.PlaceBlockWithBlockStates1) -> int :
                Hash = RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                ConstStr[Oper.blockStatesConstantStringID])
                return Hash["index"]

            def Operation_0x07(Oper: StructureBDX.OperationCode.PlaceBlock) -> int :
                Hash= RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                Oper.blockData)
                return Hash["index"]

            def Operation_0x0d(Oper: StructureBDX.OperationCode.PlaceBlockWithBlockStates2) -> int :
                Hash = RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                Oper.blockStatesString)
                return Hash["index"]

            def Operation_0x1a(Oper: StructureBDX.OperationCode.SetCommandBlockData) -> Union[int, None] :
                BlockIndex = StructureObject.block_index[PosIndex]
                if BlockIndex < 1 : return None
                Block = Blocks[ list(Blocks.keys())[BlockIndex] ]
                if not CommandBlockIDTest.search(Block["name"]) : return None

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(Oper.command),
                        CustomName = node.string(Oper.customName),
                        ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                        auto = node.byte(int(not Oper.needsRedstone)),
                        TickDelay = node.int(Oper.tickdelay),
                        conditionalMode = node.byte(Oper.conditional),
                        TrackOutput = node.int(1),
                        Version = node.int(19),
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                if Block["name"] != CommandBlockID[Oper.mode] : 
                    Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Block["states"])
                    return Hash["index"]

            def Operation_0x1b(Oper: StructureBDX.OperationCode.PlaceBlockWithCommandBlockData) -> int :
                BlockID = ConstStr[Oper.blockConstantStringID]
                Hash = RegisterBlock(Blocks, BlockID, Oper.blockData)
                if not CommandBlockIDTest.search(BlockID) : return 

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(Oper.command),
                        CustomName = node.string(Oper.customName),
                        ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                        auto = node.byte(int(not Oper.needsRedstone)),
                        TickDelay = node.int(Oper.tickdelay),
                        conditionalMode = node.byte(Oper.conditional),
                        TrackOutput = node.int(1),
                        Version = node.int(19),
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                if BlockID != CommandBlockID[Oper.mode] : 
                    Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Oper.blockData)
                return Hash["index"]

            def Operation_0x20(Oper: StructureBDX.OperationCode.PlaceRuntimeBlock) -> int :
                BlockID, Data = GetRuntimeID(Oper.runtimeId)
                Hash = RegisterBlock(Blocks, BlockID, Data)
                return Hash["index"]

            def Operation_0x22(Oper: StructureBDX.OperationCode.PlaceRuntimeBlockWithCommandBlockData) -> int :
                BlockID, Data = GetRuntimeID(Oper.runtimeId)
                Hash = RegisterBlock(Blocks, BlockID, Data)
                if not CommandBlockIDTest.search(BlockID) : return Hash["index"]

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(Oper.command),
                        CustomName = node.string(Oper.customName),
                        ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                        auto = node.byte(int(not Oper.needsRedstone)),
                        TickDelay = node.int(Oper.tickdelay),
                        conditionalMode = node.byte(Oper.conditional),
                        TrackOutput = node.int(1),
                        Version = node.int(19),
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                if BlockID != CommandBlockID[Oper.mode] : 
                    Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Data)
                return Hash["index"]

            def Operation_0x24(Oper: StructureBDX.OperationCode.PlaceCommandBlockWithCommandBlockData) -> int :
                Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Oper.data)

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(Oper.command),
                    CustomName = node.string(Oper.customName),
                    ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                    auto = node.byte(int(not Oper.needsRedstone)),
                    conditionalMode = node.byte(Oper.conditional),
                    TickDelay = node.int(Oper.tickdelay),
                    TrackOutput = node.int(1),
                    Version = node.int(19),
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                return Hash["index"]

            def Operation_0x25(Oper: StructureBDX.OperationCode.PlaceRuntimeBlockWithChestData) -> int :
                BlockID, Data = GetRuntimeID(Oper.runtimeId)
                Hash = RegisterBlock(Blocks, BlockID, Data)

                if Hash["name"] not in BlockNBT_ID : return Hash["index"]
                node = nbt.NBT_Builder()
                ContainerNbt = node.compound(
                        id = node.string(BlockNBT_ID[Hash["name"]]),
                        Items = node.list(*[
                            node.compound(
                                Count = node.byte(Item["count"]),
                                Damage = node.short(Item["data"]),
                                Name = node.string(Item["name"]),
                                Slot = node.byte(Item["slotID"]),
                                tag = node.compound()
                            ) for Item in Oper.ChestData
                        ])
                ).build()
                StructureObject.block_nbt[PosIndex] = ContainerNbt

                return Hash["index"]

            def Operation_0x28(Oper: StructureBDX.OperationCode.PlaceBlockWithChestData) -> int :
                Hash = RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                Oper.blockData)

                if Hash["name"] not in BlockNBT_ID : return Hash["index"]
                node = nbt.NBT_Builder()
                ContainerNbt = node.compound(
                    id = node.string(BlockNBT_ID[Hash["name"]]),
                    Items = node.list(*[
                        node.compound(
                            Count = node.byte(Item["count"]),
                            Damage = node.short(Item["data"]),
                            Name = node.string(Item["name"]),
                            Slot = node.byte(Item["slotID"]),
                            tag = node.compound()
                        ) for Item in Oper.ChestData
                    ])
                ).build()
                StructureObject.block_nbt[PosIndex] = ContainerNbt

                return Hash["index"]

            def Operation_0x29(Oper: StructureBDX.OperationCode.PlaceBlockWithNBTData) -> int :
                Hash = RegisterBlock(Blocks, 
                    ConstStr[Oper.blockConstantStringID], 
                    ConstStr[Oper.blockStatesConstantStringID])

                StructureObject.block_nbt[PosIndex] = Oper.nbt

                return Hash["index"]

            StructX, StructY, StructZ = StructureObject.size[0], StructureObject.size[1], StructureObject.size[2]
            FUNCTION = {0x05:Operation_0x05, 0x07:Operation_0x07, 0x0d:Operation_0x0d,
            0x1a:Operation_0x1a, 0x1b:Operation_0x1b, 0x20:Operation_0x20, 0x21:Operation_0x20,
            0x22:Operation_0x22, 0x23:Operation_0x22, 0x24:Operation_0x24, 0x25:Operation_0x25,
            0x26:Operation_0x25, 0x28:Operation_0x28, 0x29:Operation_0x29}
            for PosX, PosY, PosZ, Oper in BDX.get_blocks() :
                if Oper.operation_code not in FUNCTION : continue
                PosIndex = (PosX-PosStart[0]) * StructY * StructZ + (PosY-PosStart[1]) * StructZ + (PosZ-PosStart[2])
                result = FUNCTION[Oper.operation_code](Oper)
                if result is None : continue
                StructureObject.block_index[PosIndex] = result

            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(BlockCount))
            for value1 in Blocks.values() : 
                for value2 in value1.values() :
                    StructureObject.block_palette[value2["index"]] = value2
                    del value2["index"]

        def encode(self, Writer:Union[str, io.RawIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            BDX = StructureBDX.BDX_File()
            CreateConstantString = StructureBDX.OperationCode.CreateConstantString
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
                append_function(CreateConstantString(Block["name"]))
                state_str = json.dumps(Block["states"], separators=(',', '='))
                state_str = f"[${ state_str[1:len(state_str)-1] }]"
                append_function(CreateConstantString(state_str))
            
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
                
                if IgnoreAir and self.block_palette[block_index]["name"] == "minecraft:air" : continue
                if index in self.block_nbt : append_function(PlaceBlockWithNBTData(
                    blockConstantStringID = 2*block_index,
                    blockStatesConstantStringID = 2*block_index+1,
                    nbt = self.block_nbt[index] ))
                else : append_function(PlaceBlockWithBlockStates(
                    blockConstantStringID = 2*block_index,
                    blockStatesConstantStringID = 2*block_index+1))

            BDX.save_as(Writer)

    class MCSTRUCTURE(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.RawIOBase]):
            MCS = StructureMCS.Mcstructure.from_buffer(Reader)
            
            StructureObject = self.Common
            StructureObject.size = MCS.size
            StructureObject.origin = MCS.origin
            StructureObject.block_index = MCS.block_index
            StructureObject.contain_index = MCS.contain_index
            StructureObject.block_palette = MCS.block_palette
            StructureObject.entity_nbt = MCS.entity_nbt
            StructureObject.block_nbt = MCS.block_nbt

            for key, value in StructureObject.block_nbt.items() :
                StructureObject.block_nbt[key] = value["block_entity_data"]

        def encode(self, Writer:Union[str, io.RawIOBase]):
            self = self.Common
            MCS = StructureMCS.Mcstructure()

            MCS.size = self.size
            MCS.origin = self.origin
            MCS.block_index = self.block_index
            MCS.contain_index = self.contain_index
            MCS.block_palette = self.block_palette
            MCS.entity_nbt = self.entity_nbt
            MCS.block_nbt = self.block_nbt.copy()

            for key, value in MCS.block_nbt.items() :
                a = nbt.TAG_Compound({"block_entity_data":value})
                MCS.block_nbt[key] = a
            MCS.save_as(Writer)

    class SCHEMATIC(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.RawIOBase]):
            SCHMATIC = StructureSCHEMATIC.Schematic.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.size = SCHMATIC.size
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * len(SCHMATIC.block_index))
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * len(SCHMATIC.block_index))
            
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] ={}
            def RegisterBlock(id_index:int, data_or_state:int) -> int :
                Hash = (id_index << 16) + data_or_state
                if Hash not in Blocks : 
                    id = StructureSCHEMATIC.RuntimeID_to_Block[id_index]
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks) }
                return Hash

            StructX, StructY, StructZ = StructureObject.size[0], StructureObject.size[1], StructureObject.size[2]
            PosIter = itertools.product(range(SCHMATIC.size[1]), range(SCHMATIC.size[2]), range(SCHMATIC.size[0]))
            for (posy, posz, posx), id_index, data in zip(PosIter, SCHMATIC.block_index, SCHMATIC.block_data) :
                blockHash = RegisterBlock(id_index, data)
                Index = posx * StructY * StructZ + posy * StructZ + posz
                StructureObject.block_index[Index] = Blocks[blockHash]["index"]

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex+1))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer:Union[str, io.RawIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            SCHMATIC = StructureSCHEMATIC.Schematic()
            for i in range(3) : 
                SCHMATIC.size[i] = self.size[i]
                SCHMATIC.origin[i] = self.origin[i]

            StructX, StructY, StructZ = self.size[0], self.size[1], self.size[2]
            SCHMATIC.block_index = array.array("B", b"\x00" * len(self.block_index))
            SCHMATIC.block_data = array.array("B", b"\x00" * len(self.block_index))

            RuntimeIDCache:Dict[int, Tuple[int, int]] = {}
            PosIter = itertools.product(range(self.size[0]), range(self.size[1]), range(self.size[2]))
            for (posx, posy, posz), id_index in zip(PosIter, self.block_index) :
                BlockID = self.block_palette[id_index]["name"]
                if BlockID not in StructureSCHEMATIC.Block_to_RuntimeID : continue
                Index = posy * StructZ * StructX + posz * StructX + posx

                BlockState = self.block_palette[id_index]["states"]
                if id_index not in RuntimeIDCache :
                    NumberID = StructureSCHEMATIC.Block_to_RuntimeID[BlockID]
                    Data = BlockStatesTransforDatavalue(BlockID, BlockState)
                    RuntimeIDCache[id_index] = (NumberID, Data)

                SCHMATIC.block_index[Index] = RuntimeIDCache[id_index][0]
                SCHMATIC.block_data[Index] = RuntimeIDCache[id_index][1]

            SCHMATIC.save_as(Writer)

    class MIANYANG(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.MianYang.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.size = array.array("i", [j-i+1 for i,j in zip(PosStart, PosEnd)])
            StructureObject.block_palette.append({"name":"minecraft:air", "states":{}})

            Volume = StructureObject.size[0] * StructureObject.size[1] * StructureObject.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * Volume)

            StructX, StructY, StructZ = StructureObject.size[0], StructureObject.size[1], StructureObject.size[2]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] = {}
            def RegisterBlock(id_index:int, data_or_state:int) -> int :
                Hash = (id_index << 16) + data_or_state
                if Hash not in Blocks : 
                    id = TransforNamespaceID(Struct1.block_palette[id_index])
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks)+1 }
                return Blocks[Hash]

            CommandMatch = re.compile('(?<=Command:").*(?=",CustomName)')
            CustomNameMatch = re.compile('(?<=CustomName:").*(?=",ExecuteOnFirstTick)')
            AutoMatch = re.compile('(?<=auto:)-?[0-9]+(?=b)')
            TickDelayMatch = re.compile('(?<=TickDelay:)-?[0-9]+(?=,)')
            VersionMatch = re.compile('(?<=Version:)-?[0-9]+(?=,)')
            for chunk in Struct1.chunks :
                o_x, o_z = chunk["startX"]-PosStart[0], chunk["startZ"]-PosStart[2]
                for block in chunk["blocks"] :
                    BlockHash = RegisterBlock(block[0], block[1])
                    block_index = BlockHash["index"]
                    posx, posy, posz = o_x + block[2], block[3] - PosStart[1], o_z + block[4]
                    Index = posx * StructY * StructZ + posy * StructZ + posz
                    StructureObject.block_index[Index] = block_index

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
                        conditionalMode = node.byte(BlockHash["states"]["conditional_bit"]),
                        TrackOutput = node.int(1),
                        Version = node.int(int( VersionMatch.search(nbtstr).group() )),
                    ).build()
                    StructureObject.block_nbt[Index] = CommandBlockNbt

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.MianYang()
            nbtstr = '{Command:"%s",CustomName:"%s",ExecuteOnFirstTick:0b,LPCommandMode:%s,' + \
                'LPCondionalMode:%sb,LPRedstoneMode:%sb,LastExecution:0l,LastOutput:"",' + \
                'LastOutputParams:[],SuccessCount:0,TickDelay:%s,TrackOutput:1b,' + \
                'Version:%s,auto:%sb,conditionMet:%sb,powered:0b}'
            LPCommandMode = {"minecraft:repeating_command_block":1, 
                "minecraft:chain_command_block":2, "minecraft:command_block":0}

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )

            Chunks:Dict[Tuple[int,int], dict] = {}
            for index, (id_index, (posx, posy, posz)) in Generator :
                BlockID = self.block_palette[id_index]["name"]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                BlockState = self.block_palette[id_index]["states"]
                Data = BlockStatesTransforDatavalue(BlockID, BlockState)

                realX, realY, realZ = o_x + posx, o_y + posy, o_z + posz
                chunk_pos = (realX//16*16, realZ//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = {
                    "startX":chunk_pos[0], "startZ":chunk_pos[1], "blocks":[]}
                
                chunk_block = [id_index, Data, realX-chunk_pos[0], realY, realZ-chunk_pos[1]]
                Chunks[chunk_pos]["blocks"].append(chunk_block)

                if index not in self.block_nbt : continue
                if not CommandBlockIDTest.search(BlockID) : continue

                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    name = node.string(BlockID),
                    states = node.compound(
                        conditional_bit=node.byte(BlockState["conditional_bit"]),
                        facing_direction=node.int(BlockState["facing_direction"])
                    ),
                    val = node.short(Data),
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
            Struct1.block_palette.extend(i["name"] for i in self.block_palette)
            Struct1.save_as(Writer)
 
    class GANGBAN_V1(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V1.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.size = array.array("i", [i for i in Struct1.size])
            StructureObject.block_palette.append({"name":"minecraft:air", "states":{}})

            Volume = Struct1.size[0] * Struct1.size[1] * Struct1.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * Volume)

            O_X, O_Y, O_Z = Struct1.origin[0], Struct1.origin[1], Struct1.origin[2]
            StructX, StructY, StructZ = Struct1.size[0], Struct1.size[1], Struct1.size[2]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] = {}
            def RegisterBlock(id_index:int, data_or_state:int) -> int :
                Hash = (id_index << 16) + data_or_state
                if Hash not in Blocks : 
                    id = TransforNamespaceID(Struct1.block_palette[id_index])
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks)+1 }
                return Hash

            for block in Struct1.blocks :
                BlockHash = RegisterBlock(block["id"], block.get("aux", 0))
                block_index = Blocks[BlockHash]["index"]
                posx, posy, posz = block["p"][0] - O_X, block["p"][1] - O_Y, block["p"][2] - O_Z
                Index = posx * StructY * StructZ + posy * StructZ + posz
                StructureObject.block_index[Index] = block_index

                if "cmds" not in block : continue
                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    id = node.string("CommandBlock"),
                    Command = node.string(block["cmds"]["cmd"]),
                    CustomName = node.string(block["cmds"]["name"]),
                    ExecuteOnFirstTick = node.byte(1),
                    auto = node.byte(block["cmds"]["on"]),
                    TickDelay = node.int(block["cmds"]["tick"]),
                    TrackOutput = node.int(block["cmds"]["should"]),
                    conditionalMode = node.byte(Blocks[BlockHash]["states"]["conditional_bit"]),
                    Version = node.int(19),
                ).build()
                StructureObject.block_nbt[Index] = BlockData

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V1()

            Struct1.size = self.size
            Struct1.origin = self.origin

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )
            CommandBlockGangBan = {"minecraft:repeating_command_block":"Repeating", 
                "minecraft:chain_command_block":"Chain", "minecraft:command_block":"Tick"}

            for index, (id_index, (posx, posy, posz)) in Generator :
                BlockID = self.block_palette[id_index]["name"]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                BlockState = self.block_palette[id_index]["states"]
                Data = BlockStatesTransforDatavalue(BlockID, BlockState)
                
                block = {"id":id_index, "aux":Data, "p":[o_x + posx, o_y + posy, o_z + posz]}
                Struct1.blocks.append(block)
                
                if index not in self.block_nbt : continue
                if not CommandBlockIDTest.search(BlockID) : continue
                block["cmds"] = {
                    "mode":CommandBlockGangBan[BlockID],
                    "condition":bool(BlockState["conditional_bit"]),
                    "cmd":self.block_nbt[index]["Command"].value,
                    "name":self.block_nbt[index]["CustomName"].value,
                    "tick":self.block_nbt[index]["TickDelay"].value,
                    "should":bool(self.block_nbt[index]["TrackOutput"]),
                    "on":bool(self.block_nbt[index]["auto"])
                }

            Struct1.block_palette.extend(i["name"] for i in self.block_palette)
            Struct1.save_as(Writer)

    class GANGBAN_V2(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V2.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.size = array.array("i", [j-i+1 for i,j in zip(PosStart, PosEnd)])
            StructureObject.block_palette.append({"name":"minecraft:air", "states":{}})

            Volume = StructureObject.size[0] * StructureObject.size[1] * StructureObject.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * Volume)

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            StructX, StructY, StructZ = StructureObject.size[0], StructureObject.size[1], StructureObject.size[2]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] = {}
            def RegisterBlock(id_index:int, data_or_state:int) -> int :
                Hash = (id_index << 16) + data_or_state
                if Hash not in Blocks : 
                    id = TransforNamespaceID(Struct1.block_palette[id_index])
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks)+1 }
                return Hash

            for chunk in Struct1.chunks :
                o_x, o_y, o_z = chunk["grids"]["x"]-O_X, O_Y, chunk["grids"]["z"]-O_Z
                for block in chunk["data"] :
                    BlockHash = RegisterBlock(block[0], block[1])
                    block_index = Blocks[BlockHash]["index"]
                    posx, posy, posz = block[2] + o_x, block[3] - o_y, block[4] + o_z
                    Index = posx * StructY * StructZ + posy * StructZ + posz
                    StructureObject.block_index[Index] = block_index

                    if block[-1].__class__ is not str : continue
                    if block[5] != "nbt" : continue
                    NbtName = GetNbtID( Blocks[BlockHash]["name"] )
                    if not NbtName : continue
                    StructureObject.block_nbt[Index] = nbt.read_from_snbt_file( io.StringIO(block[6]) ).get_tag()
                    StructureObject.block_nbt[Index]["id"] = nbt.TAG_String(NbtName)

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer:Union[str, io.TextIOBase]):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V2()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )

            Chunks:Dict[Tuple[int,int], dict] = {}
            for index, (id_index, (posx, posy, posz)) in Generator :
                BlockID = self.block_palette[id_index]["name"]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                BlockState = self.block_palette[id_index]["states"]
                Data = BlockStatesTransforDatavalue(BlockID, BlockState)

                realX, realY, realZ = o_x + posx, o_y + posy, o_z + posz
                chunk_pos = (realX//16*16, realZ//16*16)
                if chunk_pos not in Chunks : Chunks[chunk_pos] = {
                    "id":len(Chunks), "grids":{"x":chunk_pos[0], "z":chunk_pos[1],
                    "x1":chunk_pos[0]+16, "z1":chunk_pos[1]+16}, "data":[]}
                
                chunk_block = [id_index, Data, realX-chunk_pos[0], realY, realZ-chunk_pos[1]]
                Chunks[chunk_pos]["data"].append(chunk_block)

                if index not in self.block_nbt : continue

                node = nbt.NBT_Builder()
                BlockData = node.compound(
                    name = node.string(BlockID),
                    states = node.compound(**{
                        i:( node.byte(j) if 
                           isinstance(j, (bool, ctypes.c_byte)) 
                           else node.int(j)
                        ) for i,j in BlockState.items()
                    }),
                    val = node.short(Data),
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
                chunk_block.append(BlockSNbtIO1.getvalue()[3:])

            Struct1.chunks.extend(Chunks.values())
            Struct1.block_palette.extend(i["name"] for i in self.block_palette)
            Struct1.save_as(Writer)

    #未完成
    class GANGBAN_V3(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.GangBan_V3.from_buffer(Reader)

            StructureObject = self.Common
            StructureObject.size = array.array("i", [i for i in Struct1.size])
            StructureObject.block_palette.append({"name":"minecraft:air", "states":{}})

            Volume = Struct1.size[0] * Struct1.size[1] * Struct1.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * Volume)

            StructX, StructY, StructZ = Struct1.size[0], Struct1.size[1], Struct1.size[2]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] = {}
            def RegisterBlock(id_index:int, data_or_state:int) -> int :
                Hash = (id_index << 16) + data_or_state
                if Hash not in Blocks : 
                    id = TransforNamespaceID(Struct1.block_palette[id_index])
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks)+1 }
                return Hash

            pos_cache = [0, 0, 0]
            for block in Struct1.blocks :
                for i in range(3) : pos_cache[i] += block[i]
                BlockHash = RegisterBlock(block[3], block[4])
                block_index = Blocks[BlockHash]["index"]
                posx, posy, posz = pos_cache[0], pos_cache[1], pos_cache[2]
                Index = posx * StructY * StructZ + posy * StructZ + posz
                StructureObject.block_index[Index] = block_index

                if len(block) <= 5 : continue
                BlockEntity = block[5]

                node = nbt.NBT_Builder()
                if BlockEntity.__class__ is list : pass
                elif BlockEntity.__class__ is dict :
                    BlockData = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(BlockEntity["cmd"]),
                        CustomName = node.string(BlockEntity["name"]),
                        ExecuteOnFirstTick = node.byte(1),
                        auto = node.byte(BlockEntity["auto"]),
                        TickDelay = node.int(BlockEntity["delay"]),
                        TrackOutput = node.int(1),
                        conditionalMode = node.byte(Blocks[BlockHash]["states"]["conditional_bit"]),
                        Version = node.int(19),
                    ).build()
                StructureObject.block_nbt[Index] = BlockData

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.GangBan_V1()

            Struct1.size = self.size
            Struct1.origin = self.origin

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )
            CommandBlockGangBan = {"minecraft:repeating_command_block":"Repeating", 
                "minecraft:chain_command_block":"Chain", "minecraft:command_block":"Tick"}

            for index, (id_index, (posx, posy, posz)) in Generator :
                BlockID = self.block_palette[id_index]["name"]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                BlockState = self.block_palette[id_index]["states"]
                Data = BlockStatesTransforDatavalue(BlockID, BlockState)
                
                block = {"id":id_index, "aux":Data, "p":[o_x + posx, o_y + posy, o_z + posz]}
                Struct1.blocks.append(block)
                
                if index not in self.block_nbt : continue
                if not CommandBlockIDTest.search(BlockID) : continue
                block["cmds"] = {
                    "mode":CommandBlockGangBan[BlockID],
                    "condition":bool(BlockState["conditional_bit"]),
                    "cmd":self.block_nbt[index]["Command"].value,
                    "name":self.block_nbt[index]["CustomName"].value,
                    "tick":self.block_nbt[index]["TickDelay"].value,
                    "should":bool(self.block_nbt[index]["TrackOutput"]),
                    "on":bool(self.block_nbt[index]["auto"])
                }

            Struct1.block_palette.extend(i["name"] for i in self.block_palette)
            Struct1.save_as(Writer)

    class RUNAWAY(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.RunAway.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.size = array.array("i", [j-i+1 for i,j in zip(PosStart, PosEnd)])
            StructureObject.block_palette.append({"name":"minecraft:air", "states":{}})

            Volume = StructureObject.size[0] * StructureObject.size[1] * StructureObject.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * Volume)

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            StructX, StructY, StructZ = StructureObject.size[0], StructureObject.size[1], StructureObject.size[2]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] = {}
            def RegisterBlock(id:str, data_or_state:int) -> int :
                Hash = f"{id}:{data_or_state}"
                if Hash not in Blocks : 
                    id = TransforNamespaceID(id)
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks)+1 }
                return Hash

            for block in Struct1.blocks :
                BlockHash = RegisterBlock(block["name"], block.get("aux", 0))
                block_index = Blocks[BlockHash]["index"]
                posx, posy, posz = block["x"] - O_X, block["y"] - O_Y, block["z"] - O_Z
                Index = posx * StructY * StructZ + posy * StructZ + posz
                StructureObject.block_index[Index] = block_index

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.RunAway()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )

            for index, (id_index, (posx, posy, posz)) in Generator :
                BlockID = self.block_palette[id_index]["name"]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                BlockState = self.block_palette[id_index]["states"]
                Data = BlockStatesTransforDatavalue(BlockID, BlockState)
                block = {"name":BlockID, "aux":Data, "x":o_x + posx, "y":o_y + posy, "z":o_z + posz}
                Struct1.blocks.append(block)

            Struct1.save_as(Writer)

    class FUHONG(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.FuHong.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.size = array.array("i", [j-i+1 for i,j in zip(PosStart, PosEnd)])
            StructureObject.block_palette.append({"name":"minecraft:air", "states":{}})

            Volume = StructureObject.size[0] * StructureObject.size[1] * StructureObject.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * Volume)

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            StructX, StructY, StructZ = StructureObject.size[0], StructureObject.size[1], StructureObject.size[2]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] = {}
            def RegisterBlock(id:str, data_or_state:int) -> int :
                Hash = f"{id}:{data_or_state}"
                if Hash not in Blocks : 
                    id = TransforNamespaceID(id)
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks)+1 }
                return Hash

            for block in Struct1.blocks :
                BlockHash = RegisterBlock(block["name"], block.get("aux", 0))
                block_index = Blocks[BlockHash]["index"]
                posx, posy, posz = block["x"][0] - O_X, block["y"][0] - O_Y, block["z"][0] - O_Z
                Index = posx * StructY * StructZ + posy * StructZ + posz
                StructureObject.block_index[Index] = block_index

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.FuHong()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )

            for index, (id_index, (posx, posy, posz)) in Generator :
                BlockID = self.block_palette[id_index]["name"]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                BlockState = self.block_palette[id_index]["states"]
                Data = BlockStatesTransforDatavalue(BlockID, BlockState)
                block = {"name":BlockID, "aux":Data, "x":[o_x + posx], "y":[o_y + posy], "z":[o_z + posz]}
                Struct1.blocks.append(block)

            Struct1.save_as(Writer)

    class QINGXU(CodecsBase) :

        def decode(self, Reader:Union[str, bytes, io.IOBase]):
            Struct1 = StructureRUNAWAY.QingXu.from_buffer(Reader)
            PosStart, PosEnd = Struct1.get_volume()

            StructureObject = self.Common
            StructureObject.size = array.array("i", [j-i+1 for i,j in zip(PosStart, PosEnd)])

            Volume = StructureObject.size[0] * StructureObject.size[1] * StructureObject.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.contain_index = array.array("i", b"\xff\xff\xff\xff" * Volume)

            O_X, O_Y, O_Z = PosStart[0], PosStart[1], PosStart[2]
            StructX, StructY, StructZ = StructureObject.size[0], StructureObject.size[1], StructureObject.size[2]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] = {}
            def RegisterBlock(id:str) -> int :
                Hash = id
                if Hash not in Blocks : 
                    id = TransforNamespaceID(id)
                    BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                    Blocks[Hash] = {"name": id, "states": BlockStates, "index": len(Blocks) }
                return Hash

            for block in Struct1.blocks :
                BlockHash = RegisterBlock(block["Name"])
                block_index = Blocks[BlockHash]["index"]
                posx, posy, posz = block["x"] - O_X, block["y"] - O_Y, block["z"] - O_Z
                Index = posx * StructY * StructZ + posy * StructZ + posz
                StructureObject.block_index[Index] = block_index

            MaxIndex = max(block["index"] for block in Blocks.values()) + 1
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

        def encode(self, Writer):
            IgnoreAir, self = self.IgnoreAir, self.Common
            Struct1 = StructureRUNAWAY.QingXu()

            o_x, o_y, o_z = self.origin[0], self.origin[1], self.origin[2]
            Generator = enumerate( zip(self.block_index, itertools.product(
                range(self.size[0]), range(self.size[1]), range(self.size[2]) )) )

            for index, (id_index, (posx, posy, posz)) in Generator :
                BlockID = self.block_palette[id_index]["name"]
                if IgnoreAir and BlockID == "minecraft:air" : continue
                BlockState = self.block_palette[id_index]["states"]
                #Data = BlockStatesTransforDatavalue(BlockID, BlockState)
                block = {"Name":BlockID, "x":o_x + posx, "y":o_y + posy, "z":o_z + posz}
                Struct1.blocks.append(block)

            Struct1.save_as(Writer)

