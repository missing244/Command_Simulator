def init() :
    import os, platform, sys
    test1, test2 = False, False

    try : from . import MCBEWorld_C_API
    except : pass
    else : return None
    try : import Command_Simulator_C_API.MCBEWorld_C_API as MCBEWorld_C_API
    except : pass
    else : return None

    py_dll_name = "MCBEWorld_C_API.%s"
    
    system_info = platform.uname()
    py_version = (sys.version_info.major, sys.version_info.minor)
    base_path = os.path.realpath( os.path.join(__file__, "..") )
    if system_info.system.lower() == 'windows' :
        target_path = os.path.join(base_path, py_dll_name % "pyd")
        target_abi = os.path.join(base_path, "ABI_File", "amd64.pyd")
    elif system_info.system.lower() == 'linux' and system_info.machine == "aarch64" : 
        target_path = "/data/user/0/ru.iiec.pydroid3/files/aarch64-linux-android/lib/python%s.%s/site-packages/Command_Simulator_C_API" % py_version
        target_abi = os.path.join(base_path, "ABI_File", "aarch64.pyd")
        os.makedirs( target_path, exist_ok=True )
        target_path = os.path.join(target_path, py_dll_name % "os")
    else : raise RuntimeError(f"未支持的系统{system_info}")

    with open(target_abi, "rb") as f1 :
        with open(target_path, "wb") as f2 : f2.write( f1.read() )
init()

try : from . import MCBEWorld_C_API
except : import Command_Simulator_C_API.MCBEWorld_C_API as MCBEWorld_C_API

def cycle_xor(bytes1:bytes, bytes2:bytes) -> bytes : 
    """
    bytes2 对 bytes1 进行循环异或
    """
    return MCBEWorld_C_API.cycle_xor(bytes1, bytes2)