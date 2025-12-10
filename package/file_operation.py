__version__ = (1, 0, 0)

import os, subprocess, platform, io, shutil, sys
import builtins
import importlib.util
import importlib.machinery
from types import ModuleType
from pathlib import Path
from contextlib import contextmanager
from typing import List,Tuple,Literal,Union,Generator


def GetPlatform() :
  result = subprocess.run("getprop ro.build.version.release", shell=True, capture_output=True, text=True)
  system_info = platform.uname()
  if system_info.system.lower() == 'windows' : return 'windows'
  elif system_info.system.lower() == 'android' : return 'android'
  elif result.returncode == 0 : return 'android'
  elif system_info.system.lower() == 'linux' and system_info.machine == "x86_64" : return 'linux_amd64'
  elif system_info.system.lower() == 'linux' and system_info.machine == "aarch64" : return 'linux_arm64'


def is_file(path:str) :
    return os.path.exists(path) and os.path.isfile(path)

def is_dir(path:str) :
    return os.path.exists(path) and os.path.isdir(path)


def search_file(path1:str,condition_func=None) -> List[Tuple[Literal["file","dir"],str,str]]:
        """
        condition_func(base_path_name, file_name) -> 1/0
        """
        search_result = []
        search_file_list = list(os.walk(path1))
        for base_path_name,_,file_name_list in search_file_list :
            for file_name in file_name_list :
                if condition_func and not condition_func(base_path_name, file_name) : continue
                search_result.append( ("file", base_path_name, os.path.join(base_path_name, file_name)) )
            if len(file_name_list) == 0 : search_result.append( ("dir", base_path_name ) )
        return search_result

def force_write(path1:str,path2:str):
        file1 = open(path1,"rb")
        file2 = open(path2,"wb")
        file2.write(file1.read())
        file1.close()
        file2.close()

def move_all_file(start:str,end:str):
        file_or_dir_list = search_file(start)
        for file_or_dir in file_or_dir_list :
            end_path = file_or_dir[1].replace(start, end, 1)
            if file_or_dir[0] == "file" :
                os.makedirs(end_path, exist_ok=True)
                force_write(file_or_dir[2],file_or_dir[2].replace(start,end,1))
                os.remove(file_or_dir[2])
            else : os.makedirs(end_path, exist_ok=True)

            try : os.removedirs(file_or_dir[1])
            except : pass

def delete_all_file(path1:str):
    file1 = search_file(path1)
    for group1 in file1 :
        if group1[0] == "file" : os.remove(group1[2])
        try : os.removedirs(group1[1])
        except : pass

def copy_all_file(start:str,end:str):
        file1 = search_file(start)
        for group1 in file1 :
            text1 = group1[1].replace(start,end,1)
            if group1[0] == "file" :
                os.makedirs(text1,exist_ok=True)
                force_write(group1[2],group1[2].replace(start,end,1))
            else : os.makedirs(text1,exist_ok=True)

def write_a_file(path:str,data:Union[str,bytes],mode:Literal["w+","wb"]="w+"):
        base_path = os.path.realpath(os.path.join(path, os.pardir))
        os.makedirs(base_path, exist_ok=True)
        if mode == "w+" : file2 = open(path,"w+",encoding='utf-8')
        elif mode == "wb" : file2 = open(path,"wb")
        file2.write(data)
        file2.close()

def read_a_file(path:str,mode:Literal["read","readlines","readbyte"]="read"):
        if os.path.exists(path) and (not os.path.isfile(path)) : return None
        try :
            if mode == "read" :
                file2 = open(path,"r",encoding='utf-8')
                text1 = file2.read()
            elif mode == "readlines" :
                file2 = open(path,"r",encoding='utf-8')
                text1 = file2.readlines()
            elif mode == "readbyte" :
                file2 = open(path,"rb")
                text1 = file2.read()
        except UnicodeDecodeError :
            file2.close()
            return (path,)
        return text1

def file_in_path(path:str):
        rp_file_list = list( os.walk(path) )
        text_list_1 : List[str] = [ ]
        for base,_,file_list in rp_file_list :
            for obj3 in file_list : text_list_1.append( os.path.join( base, obj3 ) )
        return text_list_1



class PathSandBox :
    
    def __init__(self, sandboxName:str) :
        self.__platfrom = GetPlatform()
        self.internal_path = os.path.join("functionality", sandboxName)
        self.outside_path = os.path.join("/storage/emulated/0/Documents/Pydroid3/Command_Simulator", sandboxName)
        self.make_dir("all")
    
    def path_exist(self, path_type:Literal["internal", "outside", "all"], local_path:str) :
        if path_type == "internal" or path_type == "all" : 
            local_path_0 = os.path.join(self.internal_path, local_path)
            return os.path.exists( local_path_0 )
        elif path_type == "outside" or path_type == "all" : 
            local_path_0 = os.path.join(self.outside_path, local_path)
            return self.__platfrom == "android" and os.path.exists( local_path_0 )

    def delete_path(self, path_type:Literal["internal", "outside", "all"], local_path:str) :
        if path_type == "internal" or path_type == "all" :
            _path = os.path.join(self.internal_path, local_path)
            if os.path.isfile(_path) : os.remove(_path)
            elif os.path.isdir(_path) : delete_all_file(_path)
        if (path_type == "outside" or path_type == "all") and self.__platfrom == "android" : 
            _path = os.path.join(self.outside_path, local_path)
            if os.path.isfile(_path) : os.remove(_path)
            elif os.path.isdir(_path) : delete_all_file(_path)

    def list_dirs(self, path_type:Literal["internal", "outside", "all"], local_path:str) -> Generator[
        Tuple[Literal["internal", "outside"], Literal["file", "dir"], str], None, None] :
        list1, list2 = [], []
        if path_type == "internal" or path_type == "all" : list1.append("internal") ; list2.append(self.internal_path)
        elif path_type == "outside" or path_type == "all" : list1.append("outside") ; list2.append(self.outside_path)
        for path_type, path in zip( list1, list2 ) :
            local_path_0 = os.path.join(path, local_path)
            if not os.path.exists( local_path_0 ) : continue
            for file_name in os.listdir( local_path_0 ) :
                file_path = os.path.join(local_path_0, file_name)
                if is_dir( file_path ) : yield (path_type, "dir", os.path.join(local_path, file_name) )
                else : yield (path_type, "file", os.path.join(local_path, file_name) )

    def make_dir(self, path_type:Literal["internal", "outside", "all"], local_path:str="") :
        if path_type == "internal" or path_type == "all" :
            os.makedirs( os.path.join(self.internal_path, local_path), exist_ok=True)
        if (path_type == "outside" or path_type == "all") and self.__platfrom == "android" : 
            try : os.makedirs( os.path.join(self.outside_path, local_path), exist_ok=True)
            except : pass

    def file_operate(self, path_type:Literal["internal", "outside"], local_path:str, *arg, **karg) -> io.IOBase:
        if path_type == "internal" : return open( os.path.join(self.internal_path, local_path), *arg, **karg)
        elif path_type == "outside" : return open( os.path.join(self.outside_path, local_path), *arg, **karg)


