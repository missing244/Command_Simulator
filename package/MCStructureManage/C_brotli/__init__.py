# Copyright 2016 The Brotli Authors. All rights reserved.
#
# Distributed under MIT license.
# See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

def init() :
    import os, platform, sys, hashlib, re
    py_dll_name = "_brotli.%s"
    
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

try : from . import _brotli
except : import Command_Simulator_C_API._brotli as _brotli




"""Functions to compress and decompress data using the Brotli library."""

# The library version.
version = __version__ = _brotli.__version__
# The compression mode.
MODE_GENERIC = _brotli.MODE_GENERIC
MODE_TEXT = _brotli.MODE_TEXT
MODE_FONT = _brotli.MODE_FONT

# Compress a byte string.
def compress(string:bytes, mode=MODE_GENERIC, quality=11, lgwin=22, lgblock=0) -> bytes:
    """Compress a byte string.

    Args:
      string (bytes): The input data.
      mode (int, optional): The compression mode can be MODE_GENERIC (default),
        MODE_TEXT (for UTF-8 format text input) or MODE_FONT (for WOFF 2.0).
      quality (int, optional): Controls the compression-speed vs compression-
        density tradeoff. The higher the quality, the slower the compression.
        Range is 0 to 11. Defaults to 11.
      lgwin (int, optional): Base 2 logarithm of the sliding window size. Range
        is 10 to 24. Defaults to 22.
      lgblock (int, optional): Base 2 logarithm of the maximum input block size.
        Range is 16 to 24. If set to 0, the value will be set based on the
        quality. Defaults to 0.

    Returns:
      The compressed byte string.

    Raises:
      brotli.error: If arguments are invalid, or compressor fails.
    """
    return _brotli.compress(string, mode=mode, quality=quality, lgwin=lgwin, lgblock=lgblock)

# Decompress a compressed byte string.
def decompress(bytes1:bytes) -> bytes:
    """Decompress a compressed byte string.
        Args:
          string (bytes): The compressed input data.
        Returns:
          string (bytes): The decompressed byte string.
        Raises:
          brotli.error: If decompressor fails.
    """
    return _brotli.decompress(bytes1)

# Raised if compression or decompression fails.
error = _brotli.error


