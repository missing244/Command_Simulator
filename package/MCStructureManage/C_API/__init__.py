def init() :
    import os, platform, sys, hashlib, re
    py_dll_name = "MCBEStructure_C_API.%s"
    
    system_info = platform.uname()
    base_path = os.path.realpath( os.path.join(__file__, "..") )
    system = system_info.system.lower()
    machine = system_info.machine.lower()

    if system == 'windows' and machine == "amd64" :
        target_path = os.path.join(base_path, py_dll_name % "pyd")
        target_abi = os.path.join(base_path, "ABI_File", "Win_amd64.pyd")
    elif system == 'linux' and machine == "aarch64" : 
        for test_path in sys.path :
            if not test_path.endswith("site-packages") : continue
            else : break
        target_path = os.path.join(test_path, "Command_Simulator_C_API")
        target_abi = os.path.join(base_path, "ABI_File", "Linux_aarch64.so")
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

try : from . import MCBEStructure_C_API
except : import Command_Simulator_C_API.MCBEStructure_C_API as MCBEStructure_C_API
from typing import List

def fuhong_v5_decrypt(bytes1:bytes) -> str : 
    """
    fuhong_v5 解密函数
    """
    return MCBEStructure_C_API.fuhong_v5_decrypt(bytes1)

def fuhong_v5_encrypt(str1:str) -> bytes : 
    """
    fuhong_v5 加密函数
    """
    return MCBEStructure_C_API.fuhong_v5_encrypt(str1)