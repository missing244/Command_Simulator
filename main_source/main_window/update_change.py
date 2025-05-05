import package.file_operation as file_IO
import os, sys

OLD_BDX_PATH = os.path.join("main_source", "package")
if file_IO.is_dir(OLD_BDX_PATH) : file_IO.delete_all_file(OLD_BDX_PATH)

OLD_LocalServer_PATH = os.path.join("html_output")
if file_IO.is_dir(OLD_LocalServer_PATH) : file_IO.delete_all_file(OLD_LocalServer_PATH)

OLD_Parser_PATH = os.path.join("main_source", "bedrock_edition", "command_class", "parser")
if file_IO.is_dir(OLD_Parser_PATH) : file_IO.delete_all_file(OLD_Parser_PATH)