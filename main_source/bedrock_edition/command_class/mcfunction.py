import os,json,re,zlib
from typing import List,Tuple,Dict
from .. import RunTime,FileOperation
from . import Command_Tokenizer_Compiler

MCFUNCTION_FILE = re.compile("\\u002emcfunction$")
MCFUNCTION_COMMAND_ERROR_START = re.compile("[ ]{0,}/")


mcfunction_encoding_error:List[str] = []
mcfunction_syntax_error:Dict[str, List[Tuple[int,List[int],str,str]]] = {} #lines version command error_msg


def get_function_error() :
    return {
        "encoding_error" : mcfunction_encoding_error.copy(),
        "syntax_error" : mcfunction_syntax_error.copy(),
    }


def Function_Compiler(_game:RunTime.minecraft_thread) :
    mcfunction_encoding_error.clear() ; mcfunction_syntax_error.clear()

    bp_path = os.path.join("save_world",_game.world_name,'behavior_packs')
    for bp_name in os.listdir(bp_path) :
        if not FileOperation.is_dir( os.path.join(bp_path, bp_name) ) : continue
        bp_manifest_path = os.path.join(bp_path, bp_name, 'manifest.json')
        if not FileOperation.is_file( bp_manifest_path ) : continue

        try : manifest_content = json.load(fp=open(bp_manifest_path, "r", encoding="utf-8"))
        except : continue

        try : manifest_content['header']['min_engine_version']
        except : mcfunction_version = [1,18,0]
        else : mcfunction_version = manifest_content['header']['min_engine_version']
        
        bp_function_path = os.path.join(bp_path, bp_name, 'functions', "")
        Function_Checker(_game, mcfunction_version, bp_function_path)

def Function_Checker(_game:RunTime.minecraft_thread, version:List[int], mcfunction_path:str) :
    function_save = _game.minecraft_ident.functions

    for file_path in FileOperation.file_in_path(mcfunction_path) :
        if MCFUNCTION_FILE.search(file_path) is None : continue
        mcfunc_path = file_path.replace(mcfunction_path, "", 1)
        file_content = FileOperation.read_a_file(file_path)
        if isinstance(file_content, tuple) : mcfunction_encoding_error.append(file_path) ; continue

        file_crc32 = zlib.crc32(file_content.encode("utf-8"))
        if mcfunc_path in function_save and file_crc32 == function_save[mcfunc_path]["crc32"] : continue

        for lines,function_command_str in enumerate(file_content.split("\n")) :
            if MCFUNCTION_COMMAND_ERROR_START.match(function_command_str) :
                mcfunction_syntax_error[mcfunc_path].append( (lines+1, version, function_command_str, "mcfunction命令不能以/开头") )
                continue

            func_object = Command_Tokenizer_Compiler(_game, function_command_str, version)
            if isinstance(func_object, tuple) : 
                if mcfunc_path not in mcfunction_syntax_error : mcfunction_syntax_error[mcfunc_path] = []
                mcfunction_syntax_error[mcfunc_path].append( (lines+1, version, function_command_str, func_object[0]) )
                continue
            
            if mcfunc_path not in function_save : function_save[mcfunc_path] = {"crc32":file_crc32, "command":[]}
            function_save[mcfunc_path]["command"].append( (function_command_str, func_object) )
