def init() :
    import os, platform, sys, hashlib
    py_dll_name = "MCBEWorld_C_API.%s"
    
    system_info = platform.uname()
    py_version = (sys.version_info.major, sys.version_info.minor)
    base_path = os.path.realpath( os.path.join(__file__, "..") )
    if system_info.system.lower() == 'windows' and system_info.machine.lower() == "amd64" :
        target_path = os.path.join(base_path, py_dll_name % "pyd")
        target_abi = os.path.join(base_path, "ABI_File", "amd64.pyd")
    elif system_info.system.lower() == 'linux' and system_info.machine.lower() == "aarch64" : 
        target_path = "/data/user/0/ru.iiec.pydroid3/files/aarch64-linux-android/lib/python%s.%s/site-packages/Command_Simulator_C_API" % py_version
        target_abi = os.path.join(base_path, "ABI_File", "aarch64.pyd")
        os.makedirs( target_path, exist_ok=True )
        target_path = os.path.join(target_path, py_dll_name % "so")
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
from typing import List

def cycle_xor(bytes1:bytes, bytes2:bytes) -> bytes : 
    """
    bytes2 对 bytes1 进行循环异或
    """
    return MCBEWorld_C_API.cycle_xor(bytes1, bytes2)

def chunk_parser(bytes1:bytes, block_use_bit:int) -> List[int] : 
    """
    解析区块数据
    """
    return MCBEWorld_C_API.chunk_parser(bytes1, block_use_bit)

def chunk_serialize(list1:List[int], block_count:int) -> bytes :
    """
    序列化区块数据
    """
    return MCBEWorld_C_API.chunk_serialize(list1, block_count)



