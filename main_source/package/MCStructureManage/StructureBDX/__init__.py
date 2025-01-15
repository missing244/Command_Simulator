"""
    bdx文件解析模块
    ---------------------------------
    * 可用对象 BDX_File
    * 可用模块 OperationCode
    ---------------------------------
    * 可用变量 RunTimeID_117: 1.17版本的方块枚举列表，用于RunTimeID操作码索引指向的本列表数据
    * 可用变量 Support_OperationCode: 所有支持的操作，可用于isinstance判断
    * 可用变量 PosX_Change_OperationCode: 会改变X坐标的类型列表，可用于isinstance判断
    * 可用变量 PosY_Change_OperationCode: 会改变Y坐标的类型列表，可用于isinstance判断
    * 可用变量 PosZ_Change_OperationCode: 会改变Z坐标的类型列表，可用于isinstance判断
    * 可用变量 PosAddOne_OperationCode: 只会对坐标+1的类型列表，可用于isinstance判断
    * 可用变量 PosRemoveOne_OperationCode: 只会对坐标-1的类型列表，可用于isinstance判断
    * 可用变量 CommandBlockData_OperationCode: 储存了CommandBlock的信息的类型列表，可用于isinstance判断
    * 可用变量 Possible_CommandBlockData_OperationCode: 该对象可能储存了CommandBlock的信息，需要特别判断NBT内部的方块ID，可用于isinstance判断
    ---------------------------------
    * 文档 https://github.com/bouldev/PhoenixBuilder/blob/main/docs/bdump/bdump-cn.md
"""

from .object import BDX_File
from . import operation as OperationCode

#所有支持的操作，可用于isinstance判断
Support_OperationCode = (
    OperationCode.CreateConstantString, OperationCode.PlaceBlockWithBlockStates1,
    OperationCode.AddInt16ZValue0, OperationCode.PlaceBlock, OperationCode.AddZValue0,
    OperationCode.NOP, OperationCode.AddInt32ZValue0, OperationCode.PlaceBlockWithBlockStates2,
    OperationCode.AddXValue, OperationCode.SubtractXValue, OperationCode.AddYValue,
    OperationCode.SubtractYValue, OperationCode.AddZValue, OperationCode.SubtractZValue,
    OperationCode.AddInt16XValue, OperationCode.AddInt32XValue, OperationCode.AddInt16YValue,
    OperationCode.AddInt32YValue, OperationCode.AddInt16ZValue, OperationCode.AddInt32ZValue,
    OperationCode.SetCommandBlockData, OperationCode.PlaceBlockWithCommandBlockData,
    OperationCode.AddInt8XValue, OperationCode.AddInt8YValue, OperationCode.AddInt8ZValue,
    OperationCode.UseRuntimeIDPool, OperationCode.PlaceRuntimeBlock,
    OperationCode.placeBlockWithRuntimeId, OperationCode.PlaceRuntimeBlockWithCommandBlockData,
    OperationCode.PlaceRuntimeBlockWithCommandBlockDataAndUint32RuntimeID,
    OperationCode.PlaceCommandBlockWithCommandBlockData, 
    OperationCode.PlaceRuntimeBlockWithChestData, 
    OperationCode.PlaceRuntimeBlockWithChestDataAndUint32RuntimeID,
    OperationCode.AssignDebugData, OperationCode.PlaceBlockWithChestData,
    OperationCode.PlaceBlockWithNBTData, OperationCode.Terminate
)
#这些对象会改变X坐标，可用于isinstance判断
PosX_Change_OperationCode = (OperationCode.AddXValue, OperationCode.SubtractXValue, 
OperationCode.AddInt8XValue, OperationCode.AddInt16XValue, OperationCode.AddInt32XValue)
#这些对象会改变Y坐标，可用于isinstance判断
PosY_Change_OperationCode = (OperationCode.AddYValue, OperationCode.SubtractYValue, 
OperationCode.AddInt8YValue, OperationCode.AddInt16YValue, OperationCode.AddInt32YValue)
#这些对象会改变Z坐标，可用于isinstance判断
PosZ_Change_OperationCode = (OperationCode.AddZValue, OperationCode.SubtractZValue, 
OperationCode.AddInt8ZValue, OperationCode.AddInt16ZValue, OperationCode.AddInt32ZValue, 
OperationCode.AddInt16ZValue0, OperationCode.AddZValue0, OperationCode.AddInt32ZValue0)

#这些对象只会对坐标+1，可用于isinstance判断
PosAddOne_OperationCode = (OperationCode.AddXValue, OperationCode.AddYValue, 
OperationCode.AddZValue, OperationCode.AddZValue0)
#这些对象只会对坐标-1，可用于isinstance判断
PosRemoveOne_OperationCode = (OperationCode.SubtractXValue, 
OperationCode.SubtractYValue, OperationCode.SubtractZValue)
#这些对象储存了CommandBlock的信息，可用于isinstance判断
CommandBlockData_OperationCode = (
    OperationCode.SetCommandBlockData, 
    OperationCode.PlaceBlockWithCommandBlockData, 
    OperationCode.PlaceRuntimeBlockWithCommandBlockData, 
    OperationCode.PlaceRuntimeBlockWithCommandBlockDataAndUint32RuntimeID,
    OperationCode.PlaceCommandBlockWithCommandBlockData)
#该对象可能储存了CommandBlock的信息，需要特别判断NBT内部的方块ID，可用于isinstance判断
Possible_CommandBlockData_OperationCode = OperationCode.PlaceBlockWithNBTData

#1.17版本的方块枚举列表，用于RunTimeID操作码索引指向的本列表数据
from .object import RunTimeID_117