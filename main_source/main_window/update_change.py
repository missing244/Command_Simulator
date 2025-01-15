import main_source.package.file_operation as file_IO
import os, sys

OLD_NBT_PATH = os.path.join("main_source", "package", "python_nbt.py")
if file_IO.is_file(OLD_NBT_PATH) : os.remove(OLD_NBT_PATH)

OLD_BDX_PATH = os.path.join("main_source", "package", "python_bdx")
if file_IO.is_dir(OLD_BDX_PATH) : os.remove(OLD_BDX_PATH)