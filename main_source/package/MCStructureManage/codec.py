from . import nbt,TypeCheckList,StructureBDX,StructureMCS
from typing import Union,List,Dict,Tuple,Literal,TypedDict
import abc, re, os, io, json, array, itertools
CurrentPath = os.path.realpath(os.path.join(__file__, os.pardir))
BlockDataToState = json.load(fp=open(os.path.join(CurrentPath, "blockstate.json"), "r", encoding="utf-8"))
CommandBlockIDTest = re.compile("command_block$")

NamespaceTest = re.compile("^minecraft:")
def TransforNamespaceID(s:str) :
    if NamespaceTest.search(s) : return s
    else : return f"minecraft:{s}"

SpaceMatch = re.compile('[ ]{0,}')
KeyMatch   = re.compile('"(\\\\.|[^\\\\"]){0,}"')
EqualMatch = re.compile('=|:')
ValueMatch = re.compile('"(\\\\.|[^\\\\"]){0,}"|true|false|[0-9]+')
NextMatch  = re.compile(',')
def StringTransforBlockStates(s:str) :
    index = SpaceMatch.match(s).end()
    if s[index] != "[" : return {}
    else : index += 1

    StateSave = {}
    while index < len(s) :
        index = SpaceMatch.match(s, pos=index).end()
        KEY = KeyMatch.match(s, index)
        if KEY is None : break
        else : index = KEY.end()

        index = SpaceMatch.match(s, pos=index).end()
        EQUAL = EqualMatch.match(s, index)
        if EQUAL is None : break
        else : index = EQUAL.end()

        index = SpaceMatch.match(s, pos=index).end()
        VALUE = ValueMatch.match(s, index)
        if VALUE is None : break
        else : index = VALUE.end()
        
        StateSave[json.loads(KEY.group())] = json.loads(VALUE.group())

        index = SpaceMatch.match(s, pos=index).end()
        if s[index] == "," : index += 1
        else : break
    
    return dict( sorted(StateSave.items()) )

def DatavalueTransforBlockStates(id:str, v:int) :
    BLOCK_ID = TransforNamespaceID(id)
    if BLOCK_ID not in BlockDataToState : return {}

    STATES:dict = BlockDataToState[BLOCK_ID].get(bin(v), None)
    if STATES is None : STATES = BlockDataToState[BLOCK_ID]["default"]
    return dict( sorted(STATES.items()) )

def GetRuntimeID(runtime:int) -> Tuple[str, int] :
    return StructureBDX.RunTimeID_117[runtime]

BlockNBT_ID = {"minecraft:chest": "Chest", "minecraft:trapped_chest": "Chest", 
"minecraft:lit_blast_furnace": "BlastFurnace", "minecraft:hopper": "Hopper", 
"minecraft:white_shulker_box": "ShulkerBox", "minecraft:undyed_shulker_box": "ShulkerBox", 
"minecraft:barrel": "Barrel", "minecraft:dispenser": "Dispenser", "minecraft:dropper": "Dropper", 
"minecraft:furnace": "Furnace", "minecraft:lit_furnace": "Furnace", "minecraft:smoker": "Smoker", 
"minecraft:lit_smoker": "Smoker", "minecraft:blast_furnace": "BlastFurnace"}


class Decoder :

    class DecodeBase(abc.ABCMeta) :

        def __init__(self, Common):
            from . import CommonStructure
            self.Common:CommonStructure = Common

        def decode(self, Reader:Union[str, bytes, io.RawIOBase]) :
            raise NotImplementedError()

    class BDX(DecodeBase) :

        def decode(self, Reader:Union[str, bytes, io.RawIOBase]) :
            CommandBlockID = ["minecraft:command_block", "minecraft:repeating_command_block", 
                "minecraft:chain_command_block"]
            BDX = StructureBDX.BDX_File.from_buffer(Reader)
            PosStart, PosEnd = BDX.get_volume()

            StructureObject = self.Common
            StructureObject.size = array.array("i", [j-i+1 for i,j in zip(PosStart, PosEnd)])
            StructureObject.block_palette.append({"name":"minecraft:air", "states":{}})

            Volume = StructureObject.size[0] * StructureObject.size[1] * StructureObject.size[2]
            StructureObject.block_index = array.array("i", b"\x00\x00\x00\x00" * Volume)
            StructureObject.water_log = array.array("i", b"\xff\xff\xff\xff" * Volume)

            PosXChange = set(StructureBDX.PosX_Change_OperationCode)
            PosYChange = set(StructureBDX.PosY_Change_OperationCode)
            PosZChange = set(StructureBDX.PosZ_Change_OperationCode)
            PosX, PosY, PosZ = 0, 0, 0
            ConstStr = [Oper.string for _, Oper in BDX.filter(lambda e: e.operation_code == 0x01)]
            Blocks:Dict[int, Dict[Literal['name', 'states', 'index'], Union[str, dict, int]]] ={}

            def RegisterBlock(BlockDict:dict, id:str, data_or_state:Union[str, int, dict]) -> int :
                if isinstance(data_or_state, str) : BlockStates = StringTransforBlockStates(data_or_state)
                elif isinstance(data_or_state, int) : BlockStates = DatavalueTransforBlockStates(id, data_or_state)
                else : BlockStates = data_or_state
                Hash = hash(id) + hash( json.dumps(data_or_state) )
                if Hash not in BlockDict : BlockDict[Hash] = {"name": TransforNamespaceID(id), 
                    "states": BlockStates, "index": len(BlockDict)+1 }
                return Hash

            def Operation_0x05(Oper: StructureBDX.OperationCode.PlaceBlockWithBlockStates1) -> int :
                Hash = RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                ConstStr[Oper.blockStatesConstantStringID])
                return Blocks[Hash]["index"]

            def Operation_0x07(Oper: StructureBDX.OperationCode.PlaceBlock) -> int :
                Hash= RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                Oper.blockData)
                return Blocks[Hash]["index"]

            def Operation_0x0d(Oper: StructureBDX.OperationCode.PlaceBlockWithBlockStates2) -> int :
                Hash = RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                Oper.blockStatesString)
                return Blocks[Hash]["index"]

            def Operation_0x1a(Oper: StructureBDX.OperationCode.SetCommandBlockData) -> Union[int, None] :
                BlockIndex = StructureObject.block_index[PosIndex]
                if BlockIndex < 1 : return None
                Block = Blocks[ list(Blocks.keys())[BlockIndex] ]
                if not CommandBlockIDTest.search(Block["name"]) : return None

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    block_entity_data = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(Oper.command),
                        CustomName = node.string(Oper.customName),
                        ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                        auto = node.byte(int(not Oper.needsRedstone)),
                        conditionalMode = node.byte(0),
                        TickDelay = node.int(Oper.tickdelay),
                        TrackOutput = node.int(1),
                        Version = node.int(19),
                    )
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                if Block["name"] != CommandBlockID[Oper.mode] : 
                    Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Block["states"])
                    return Blocks[Hash]["index"]

            def Operation_0x1b(Oper: StructureBDX.OperationCode.PlaceBlockWithCommandBlockData) -> int :
                BlockID = ConstStr[Oper.blockConstantStringID]
                Hash = RegisterBlock(Blocks, BlockID, Oper.blockData)
                if not CommandBlockIDTest.search(BlockID) : return Blocks[Hash]["index"]

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    block_entity_data = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(Oper.command),
                        CustomName = node.string(Oper.customName),
                        ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                        auto = node.byte(int(not Oper.needsRedstone)),
                        conditionalMode = node.byte(0),
                        TickDelay = node.int(Oper.tickdelay),
                        TrackOutput = node.int(1),
                        Version = node.int(19),
                    )
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                if BlockID != CommandBlockID[Oper.mode] : 
                    Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Oper.blockData)
                return Blocks[Hash]["index"]

            def Operation_0x20(Oper: StructureBDX.OperationCode.PlaceRuntimeBlock) -> int :
                BlockID, Data = GetRuntimeID(Oper.runtimeId)
                Hash = RegisterBlock(Blocks, BlockID, Data)
                return Blocks[Hash]["index"]

            def Operation_0x22(Oper: StructureBDX.OperationCode.PlaceRuntimeBlockWithCommandBlockData) -> int :
                BlockID, Data = GetRuntimeID(Oper.runtimeId)
                Hash = RegisterBlock(Blocks, BlockID, Data)
                if not CommandBlockIDTest.search(BlockID) : return Blocks[Hash]["index"]

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    block_entity_data = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(Oper.command),
                        CustomName = node.string(Oper.customName),
                        ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                        auto = node.byte(int(not Oper.needsRedstone)),
                        conditionalMode = node.byte(0),
                        TickDelay = node.int(Oper.tickdelay),
                        TrackOutput = node.int(1),
                        Version = node.int(19),
                    )
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                if BlockID != CommandBlockID[Oper.mode] : 
                    Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Data)
                return Blocks[Hash]["index"]

            def Operation_0x24(Oper: StructureBDX.OperationCode.PlaceCommandBlockWithCommandBlockData) -> int :
                Hash = RegisterBlock(Blocks, CommandBlockID[Oper.mode], Oper.data)

                node = nbt.NBT_Builder()
                CommandBlockNbt = node.compound(
                    block_entity_data = node.compound(
                        id = node.string("CommandBlock"),
                        Command = node.string(Oper.command),
                        CustomName = node.string(Oper.customName),
                        ExecuteOnFirstTick = node.byte(int(Oper.executeOnFirstTick)),
                        auto = node.byte(int(not Oper.needsRedstone)),
                        conditionalMode = node.byte(0),
                        TickDelay = node.int(Oper.tickdelay),
                        TrackOutput = node.int(1),
                        Version = node.int(19),
                    )
                ).build()
                StructureObject.block_nbt[PosIndex] = CommandBlockNbt

                return Blocks[Hash]["index"]

            def Operation_0x25(Oper: StructureBDX.OperationCode.PlaceRuntimeBlockWithChestData) -> int :
                BlockID, Data = GetRuntimeID(Oper.runtimeId)
                Hash = RegisterBlock(Blocks, BlockID, Data)

                if Blocks[Hash]["name"] not in BlockNBT_ID : return Blocks[Hash]["index"]
                node = nbt.NBT_Builder()
                ContainerNbt = node.compound(
                    block_entity_data = node.compound(
                        id = node.string(BlockNBT_ID[Blocks[Hash]["name"]]),
                        Items = node.list(*[
                            node.compound(
                                Count = node.byte(Item["count"]),
                                Damage = node.short(Item["data"]),
                                Name = node.string(Item["name"]),
                                Slot = node.byte(Item["slotID"]),
                                tag = node.compound()
                            ) for Item in Oper.ChestData
                        ])
                    )
                ).build()
                StructureObject.block_nbt[PosIndex] = ContainerNbt

                return Blocks[Hash]["index"]

            def Operation_0x28(Oper: StructureBDX.OperationCode.PlaceBlockWithChestData) -> int :
                Hash = RegisterBlock(Blocks, 
                ConstStr[Oper.blockConstantStringID], 
                Oper.blockData)

                if Blocks[Hash]["name"] not in BlockNBT_ID : return Blocks[Hash]["index"]
                node = nbt.NBT_Builder()
                ContainerNbt = node.compound(
                    block_entity_data = node.compound(
                        id = node.string(BlockNBT_ID[Blocks[Hash]["name"]]),
                        Items = node.list(*[
                            node.compound(
                                Count = node.byte(Item["count"]),
                                Damage = node.short(Item["data"]),
                                Name = node.string(Item["name"]),
                                Slot = node.byte(Item["slotID"]),
                                tag = node.compound()
                            ) for Item in Oper.ChestData
                        ])
                    )
                ).build()
                StructureObject.block_nbt[PosIndex] = ContainerNbt

                return Blocks[Hash]["index"]

            def Operation_0x29(Oper: StructureBDX.OperationCode.PlaceBlockWithNBTData) -> int :
                Hash = RegisterBlock(Blocks, 
                    ConstStr[Oper.blockConstantStringID], 
                    ConstStr[Oper.blockStatesConstantStringID])

                a = nbt.TAG_Compound()
                a["block_entity_data"] = Oper.nbt
                StructureObject.block_nbt[PosIndex] = a

                return Blocks[Hash]["index"]

            FUNCTION = {0x05:Operation_0x05, 0x07:Operation_0x07, 0x0d:Operation_0x0d,
            0x1a:Operation_0x1a, 0x1b:Operation_0x1b, 0x20:Operation_0x20, 0x21:Operation_0x20,
            0x22:Operation_0x22, 0x23:Operation_0x22, 0x24:Operation_0x24, 0x25:Operation_0x25,
            0x26:Operation_0x25, 0x28:Operation_0x28, 0x29:Operation_0x29}
            for Oper in BDX.operation_list :
                OperClass = Oper.__class__
                if OperClass in PosXChange : PosX += Oper.value ; continue
                elif OperClass in PosYChange : PosY += Oper.value ; continue
                elif OperClass in PosZChange : PosZ += Oper.value ; continue

                if Oper.operation_code not in FUNCTION : continue
                PosIndex = StructureObject.__pos_to_index__(
                    PosX-PosStart[0], PosY-PosStart[1], PosZ-PosStart[2])
                result = FUNCTION[Oper.operation_code](Oper)
                if result is None : continue
                StructureObject.block_index[PosIndex] = result

            MaxIndex = max(block["index"] for block in Blocks.values())
            super(TypeCheckList, StructureObject.block_palette).extend(None for i in range(MaxIndex))
            for value in Blocks.values() : 
                StructureObject.block_palette[value["index"]] = value
                del value["index"]

    class MCSTRUCTURE(DecodeBase) :

        def decode(self, Reader:Union[str, bytes, io.RawIOBase]):
            MCS = StructureMCS.Mcstructure.from_buffer(Reader)
            
            StructureObject = self.Common
            StructureObject.size = MCS.size
            StructureObject.origin = MCS.origin
            StructureObject.block_index = MCS.block_index
            StructureObject.water_log = MCS.water_log
            StructureObject.block_palette = MCS.block_palette
            StructureObject.entity_nbt = MCS.entity_nbt
            StructureObject.block_nbt = MCS.block_nbt


class Encoder :

    class EncodeBase(abc.ABCMeta) :

        def __init__(self, Common):
            from . import CommonStructure
            self.Common:CommonStructure = Common

        def encode(self, Writer:Union[str, io.RawIOBase]) :
            raise NotImplementedError()

    class BDX(EncodeBase) :

        def encode(self, Writer:Union[str, io.RawIOBase]):
            self = self.Common
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

                if index in self.block_nbt : append_function(PlaceBlockWithNBTData(
                    blockConstantStringID = 2*block_index,
                    blockStatesConstantStringID = 2*block_index+1,
                    nbt = self.block_nbt[index]["block_entity_data"] ))
                else : append_function(PlaceBlockWithBlockStates(
                    blockConstantStringID = 2*block_index,
                    blockStatesConstantStringID = 2*block_index+1))

            BDX.save_as(Writer)

    class MCSTRUCTURE(EncodeBase) :

        def encode(self, Writer:Union[str, io.RawIOBase]):
            self = self.Common
            MCS = StructureMCS.Mcstructure()

            MCS.size = self.size
            MCS.origin = self.origin
            MCS.block_index = self.block_index
            MCS.water_log = self.water_log
            MCS.block_palette = self.block_palette
            MCS.entity_nbt = self.entity_nbt
            MCS.block_nbt = self.block_nbt

            MCS.save_as(Writer)



