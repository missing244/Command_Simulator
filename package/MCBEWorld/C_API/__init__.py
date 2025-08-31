def init() :
    import os, platform, sys, hashlib, re
    py_dll_name = "MCBEWorld_C_API.%s"
    
    system_info = platform.uname()
    system = system_info.system.lower()
    machine = system_info.machine.lower()
    base_path = os.path.realpath( os.path.join(__file__, "..") )

    if system == 'windows' and machine == "amd64" :
        target_path = os.path.join(base_path, py_dll_name % "pyd")
        target_abi = os.path.join(base_path, "ABI_File", "Win_amd64.pyd")
    elif system == 'linux' and machine == "aarch64" : 
        for test_path in sys.path :
            if not test_path.endswith("site-packages") : continue
            else : break
        target_path = os.path.join(test_path, "Command_Simulator_C_API")
        target_abi = os.path.join(base_path, "ABI_File", "Linux_aarch64.pyd")
        os.makedirs( target_path, exist_ok=True )
        target_path = os.path.join(target_path, py_dll_name % "so")
    elif system == 'linux' and machine == "x86_64" :
        target_path = os.path.join(base_path, py_dll_name % "so")
        target_abi = os.path.join(base_path, "ABI_File", "Linux_x86_64.pyd")
    else : raise RuntimeError(f"未支持的系统{system_info}")

    if os.path.isfile(target_path) : 
        with open(target_abi, "rb") as f1 : data1 = f1.read()
        with open(target_path, "rb") as f2 : data2 = f2.read()
        if hashlib.md5(data1).digest() == hashlib.md5(data2).digest() : return None

    with open(target_abi, "rb") as f1 :
        with open(target_path, "wb") as f2 : f2.write( f1.read() )
init()

try : from . import MCBEWorld_C_API
except : import Command_Simulator_C_API.MCBEWorld_C_API as MCBEWorld_C_API
from typing import Tuple, Union, Literal, Iterable, Any
import array

def cycle_xor(bytes1:bytes, bytes2:bytes) -> bytes : 
    """
    bytes2 对 bytes1 进行循环异或
    """
    return MCBEWorld_C_API.cycle_xor(bytes1, bytes2)

def chunk_parser(bytes1:bytes, array1:array.array, block_use_bit:int) -> None : 
    """
    解析区块数据
    """
    MCBEWorld_C_API.chunk_parser(bytes1, array1, block_use_bit)

def chunk_serialize(array1:array.array, block_count:int) -> bytes :
    """
    序列化区块数据
    """
    return MCBEWorld_C_API.chunk_serialize(array1, block_count)

def is_chunk_key(key_bytes:bytes, dimension:int) -> Union[Literal[False], tuple] :
    """
    序列化区块数据
    """
    return MCBEWorld_C_API.is_chunk_key(key_bytes, dimension)

def StructureOperatePosRange(startX:int, startZ:int, endX:int, endZ:int) -> \
    Iterable[Tuple[int, int, int, int]] :
    """
    根据坐标生成坐标迭代对象  
    (1, 1, 17, 17) -> (1, 1, 16, 16) (1, 16, 16, 17) (16, 1, 17, 16) (16, 16, 17, 17)
    """
    return MCBEWorld_C_API.StructureOperatePosRange(startX, startZ, endX, endZ)

def import_CommonStructure_to_chunk(startX:int, startY:int, startZ:int, endX:int, 
    endY:int, endZ:int, subchunk, blockindex:array.array, blockHashTable:dict) :
    """
    将结构输出进区块对象中
    """
    MCBEWorld_C_API.CommonStructure_to_chunk(startX, startY, startZ,
        endX, endY, endZ, subchunk, blockindex, blockHashTable)


