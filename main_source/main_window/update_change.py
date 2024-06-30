import main_source.package.file_operation as file_IO
import os

OLD_NBT_PATH = os.path.join("main_source", "package", "python_nbt")
if file_IO.is_dir(OLD_NBT_PATH) : file_IO.delete_all_file(OLD_NBT_PATH)