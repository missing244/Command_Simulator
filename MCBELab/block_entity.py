from . import nbt
from typing import Union


ContainerNBT_ID = {"minecraft:chest": "Chest", "minecraft:trapped_chest": "Chest", 
"minecraft:lit_blast_furnace": "BlastFurnace", "minecraft:hopper": "Hopper", 
"minecraft:shulker_box": "ShulkerBox", "minecraft:undyed_shulker_box": "ShulkerBox", 
"minecraft:barrel": "Barrel", "minecraft:dispenser": "Dispenser", "minecraft:dropper": "Dropper", 
"minecraft:furnace": "Furnace", "minecraft:lit_furnace": "Furnace", "minecraft:smoker": "Smoker", 
"minecraft:lit_smoker": "Smoker", "minecraft:blast_furnace": "BlastFurnace", "minecraft:ender_chest":"EnderChest"}

def GenerateCommandBlockNBT(NBTid:str) -> nbt.TAG_Compound :
    node = nbt.NBT_Builder()
    return node.compound(
        id = node.string(NBTid),
        Command = node.string(""),
        CustomName = node.string(""),
        ExecuteOnFirstTick = node.byte(1),
        auto = node.byte(0),
        TickDelay = node.int(0),
        conditionalMode = node.byte(0),
        TrackOutput = node.byte(1),
        Version = node.int(19)
    ).build()

def GenerateContainerNBT(NBTid:str) -> nbt.TAG_Compound :
    node = nbt.NBT_Builder()
    return node.compound(
        Findable = node.byte(0),
        IsOpened = node.byte(0),
        isMovable = node.byte(1),
        id = node.string(NBTid),
        Items = node.list() 
    ).build()

def GenerateSignNBT(NBTid:str) -> nbt.TAG_Compound : 
    node = nbt.NBT_Builder()
    return node.compound(
        IsWaxed = node.byte(0),
        isMovable = node.byte(1),
        id = node.string(NBTid),
        BackText = node.compound(
            FilteredText = node.string(""),
            HideGlowOutline = node.byte(0),
            IgnoreLighting = node.byte(0),
            PersistFormatting = node.byte(1),
            SignTextColor = node.int(-16777216),
            Text = node.string(""),
            TextOwner = node.string("") ),
        FrontText = node.compound(
            FilteredText = node.string(""),
            HideGlowOutline = node.byte(0),
            IgnoreLighting = node.byte(0),
            PersistFormatting = node.byte(1),
            SignTextColor = node.int(-16777216),
            Text = node.string(""),
            TextOwner = node.string("") )
    ).build()

def GenerateBedNBT(NBTid:str) -> nbt.TAG_Compound  :
    node = nbt.NBT_Builder()
    return node.compound(
        color = node.byte(0),
        isMovable = node.byte(1),
        id = node.string(NBTid)
    ).build()

def GenerateBannerNBT(NBTid:str) -> nbt.TAG_Compound  :
    node = nbt.NBT_Builder()
    return node.compound(
        isMovable = node.byte(1),
        Type = node.int(0),
        Patterns = node.list(),
        Base = node.int(0),
        id = node.string(NBTid)
    ).build()


def GetNbtUID(id) :
    id = f"minecraft:{id}" if ":" not in id else id
    if id in ContainerNBT_ID : return 1
    elif id.endswith("command_block") : return 2
    elif id.endswith("hanging_sign") : return 3
    elif id.endswith("_sign") : return 4
    elif id.endswith("bed") : return 5
    elif id.endswith("_banner") : return 6
    elif id.endswith("_shelf") : return 7

def GetNbtID(id:str) :
    id = f"minecraft:{id}" if ":" not in id else id
    if id in ContainerNBT_ID : return ContainerNBT_ID[id]
    elif id.endswith("command_block") : return "CommandBlock"
    elif id.endswith("hanging_sign") : return "HangingSign"
    elif id.endswith("_sign") : return "Sign"
    elif id.endswith("bed") : return "Bed"
    elif id.endswith("_banner") : return "Banner"
    elif id.endswith("_shelf") : return "Shelf"

def GenerateBlockEntityNBT(id:str) :
    id = f"minecraft:{id}" if ":" not in id else id

    if id in ContainerNBT_ID : return GenerateContainerNBT( ContainerNBT_ID[id] )
    elif id.endswith("command_block") : return GenerateCommandBlockNBT("CommandBlock")
    elif id.endswith("hanging_sign") : return GenerateSignNBT("HangingSign")
    elif id.endswith("_sign") : return GenerateSignNBT("Sign")
    elif id.endswith("bed") : return GenerateBedNBT("Bed")
    elif id.endswith("_banner") : return GenerateBannerNBT("Banner")
    elif id.endswith("_shelf") : return GenerateContainerNBT("Shelf")
