def GetPlatform() :
    import subprocess, typing, platform
    SoftwarePlatform: typing.Literal["windows_amd64", "android", "linux_amd64", "linux_arm64"] = None
    result = subprocess.run("getprop ro.build.version.release", shell=True, capture_output=True, text=True)
    system_info = platform.uname()
    system = system_info.system.lower()
    machine = system_info.machine.lower()

    if system == 'windows' and machine == "amd64": SoftwarePlatform = 'windows_amd64'
    elif system == 'android' : SoftwarePlatform = 'android'
    elif result.returncode == 0 : SoftwarePlatform = 'android'
    elif system == 'linux' and machine == "x86_64" : SoftwarePlatform = 'linux_amd64'
    elif system == 'linux' and machine == "aarch64" : SoftwarePlatform = 'linux_arm64'
    return SoftwarePlatform

def init() :
    import os, platform, sys, hashlib, re, zipfile, subprocess
    LinkCommand = "aarch64-linux-android-gcc -shared build/temp.linux-aarch64-3.9/fast_api.o -L%s -lpython%s.%s -o Linux_aarch64.pyd"
    py_dll_name = "MCBEWorld_C_API.%s"
    
    SysPlatfrom = GetPlatform()
    base_path = os.path.realpath( os.path.join(__file__, "..") )

    if SysPlatfrom == "windows_amd64" :
        target_path = os.path.join(base_path, py_dll_name % "pyd")
        target_abi = os.path.join(base_path, "ABI_File", "Win_amd64.pyd")
    elif SysPlatfrom == "android" : 
        zipfile1 = zipfile.ZipFile(os.path.join(base_path, "ABI_File", "Linux_aarch64.build"), "r")
        zipfile1.extractall( os.path.join(base_path, "ABI_File") )
        lib_path_re = re.compile("lib/python[0-9]\\.[0-9]{1,}$")
        for lib_path in sys.path :
            if lib_path_re.search(lib_path) : break
        lib_path = os.path.realpath( os.path.join(lib_path, "..") )
        subprocess.run(LinkCommand % (lib_path, sys.version_info.major, sys.version_info.minor), 
            shell=True, capture_output=True, text=True, cwd=os.path.join(base_path, "ABI_File"))
        for test_path in sys.path :
            if not test_path.endswith("site-packages") : continue
            else : break
        target_path = os.path.join(test_path, "Command_Simulator_C_API")
        target_abi = os.path.join(base_path, "ABI_File", "Linux_aarch64.pyd")
        os.makedirs( target_path, exist_ok=True )
        target_path = os.path.join(target_path, py_dll_name % "so")
    elif SysPlatfrom == "linux_amd64" :
        target_path = os.path.join(base_path, py_dll_name % "so")
        target_abi = os.path.join(base_path, "ABI_File", "Linux_x86_64.pyd")
    else : raise RuntimeError(f"未支持的系统{platform.uname()}")

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
    MCBEWorld_C_API.chunk_parser(block_use_bit, array1, bytes1)

def chunk_serialize(array1:array.array, block_count:int) -> bytes :
    """
    序列化区块数据
    """
    return MCBEWorld_C_API.chunk_serialize(block_count, array1)

def is_chunk_key(key_bytes:bytes, dimension:int) -> Union[Literal[False], tuple] :
    """
    序列化区块数据
    """
    return MCBEWorld_C_API.is_chunk_key(dimension, key_bytes)

def StructureOperatePosRange(startX:int, startZ:int, endX:int, endZ:int) -> \
    Iterable[Tuple[int, int, int, int]] :
    """
    根据坐标生成坐标迭代对象  
    (1, 1, 17, 17) -> (1, 1, 16, 16) (1, 16, 16, 17) (16, 1, 17, 16) (16, 16, 17, 17)
    """
    return MCBEWorld_C_API.StructureOperatePosRange(startX, startZ, endX, endZ)

def import_CommonStructure_to_chunk(startX:int, startY:int, startZ:int, SizeX:int, SizeY:int, SizeZ:int,
    chunkStartX:int, chunkStartY:int, chunkStartZ:int, chunkEndX:int, chunkEndY:int, chunkEndZ:int, 
    subchunk, blockindex:array.array, blockList:list, Array:array.array) :
    """
    将结构输出进区块对象中
    """
    MCBEWorld_C_API.CommonStructure_to_chunk(startX, startY, startZ, SizeX, SizeY, SizeZ,
        chunkStartX, chunkStartY, chunkStartZ, chunkEndX, chunkEndY, chunkEndZ, 
        subchunk, blockindex, blockList, Array)

def export_chunk_to_CommonStructure(startX:int, startY:int, startZ:int, SizeX:int, SizeY:int, SizeZ:int,
    chunkStartX:int, chunkStartY:int, chunkStartZ:int, chunkEndX:int, chunkEndY:int, chunkEndZ:int, 
    subchunk, blockindex:array.array, blockList:list, Array:array.array) :
    """
    将区块输出进结构对象中
    """
    MCBEWorld_C_API.chunk_to_CommonStructure(startX, startY, startZ, SizeX, SizeY, SizeZ,
        chunkStartX, chunkStartY, chunkStartZ, chunkEndX, chunkEndY, chunkEndZ, 
        subchunk, blockindex, blockList, Array)


