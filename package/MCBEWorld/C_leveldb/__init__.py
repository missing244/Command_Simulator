def GetPlatform() :
    import subprocess, typing, platform
    SoftwarePlatform: typing.Literal["windows_amd64", "android", "linux_amd64", "linux_arm64"] = None
    try : subprocess.run("getprop ro.build.version.release")
    except : SysTest = False
    else : SysTest = True
    del SysTest
    system_info = platform.uname()
    system = system_info.system.lower()
    machine = system_info.machine.lower()

    if system == 'windows' and machine == "amd64": SoftwarePlatform = 'windows_amd64'
    elif system == 'android' : SoftwarePlatform = 'android'
    elif SysTest is True : SoftwarePlatform = 'android'
    elif system == 'linux' and machine == "x86_64" : SoftwarePlatform = 'linux_amd64'
    elif system == 'linux' and machine == "aarch64" : SoftwarePlatform = 'linux_arm64'
    return SoftwarePlatform

def init() :
    import os, platform, sys, hashlib, re, zipfile, subprocess
    LinkCommand = "aarch64-linux-android-c++ -shared build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/builder.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/c.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/db_impl.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/db_iter.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/dbformat.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/filename.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/log_reader.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/log_writer.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/memtable.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/repair.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/table_cache.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/version_edit.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/version_set.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/write_batch.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/zlib_compressor.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/db/zstd_compressor.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/port/port_posix.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/port/port_posix_sse.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/block.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/block_builder.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/filter_block.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/format.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/iterator.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/merger.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/table.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/table_builder.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/table/two_level_iterator.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/arena.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/bloom.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/cache.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/coding.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/comparator.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/crc32c.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/env.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/env_posix.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/filter_policy.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/hash.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/histogram.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/logging.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/options.o build/temp.linux-aarch64-3.9/./leveldb-mcpe/util/status.o build/temp.linux-aarch64-3.9/./src/leveldb/_leveldb.o -L%s -lz -lpython%s.%s -o Linux_aarch64.pyd"
    py_dll_name = "_leveldb.%s"
    
    SysPlatfrom = GetPlatform()
    py_version = (sys.version_info.major, sys.version_info.minor)
    base_path = os.path.realpath( os.path.join(__file__, "..") )

    if SysPlatfrom == "windows_amd64" :
        target_path = os.path.join(base_path, py_dll_name % "pyd")
        target_abi = os.path.join(base_path, "ABI_File", "Win_amd64%s.pyd" % 
           ("" if py_version > (3, 8) else "_cp38") )
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


try : from . import _leveldb
except : import Command_Simulator_C_API._leveldb as _leveldb

LevelDB = _leveldb.LevelDB
LevelDBException = _leveldb.LevelDBException
LevelDBEncrypted = _leveldb.LevelDBEncrypted
LevelDBIteratorException = _leveldb.LevelDBIteratorException
Iterator = _leveldb.Iterator

# __version__ = _version.get_versions()["version"]
__version__ = "0.0.1a"


