import os, subprocess, platform, io, shutil, traceback
from typing import List,Tuple,Literal,Union,Generator,Any

def GetPlatform() :
  result = subprocess.run("getprop ro.build.version.release", shell=True, capture_output=True, text=True)
  system_info = platform.uname()
  if system_info.system.lower() == 'windows' : return 'windows'
  elif system_info.system.lower() == 'android' : return 'android'
  elif result.returncode == 0 : return 'android'
  elif system_info.system.lower() == 'linux' and system_info.machine == "x86_64" : return 'linux_amd64'
  elif system_info.system.lower() == 'linux' and system_info.machine == "aarch64" : return 'linux_arm64'




def move_all_file(src_dir:str, dst_dir:str):
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"源目录不存在: {src_dir}")

    os.makedirs(dst_dir, exist_ok=True)
    shutil.move(src_dir, dst_dir)

def copy_all_file(copy_path:str, target_path:str):
    os.makedirs(target_path, exist_ok=True)

    for item in os.listdir(copy_path):
        src_path = os.path.join(copy_path, item)
        dst_path = os.path.join(target_path, item)
        
        if os.path.isdir(src_path) : copy_all_file(src_path, dst_path)
        else: shutil.copy2(src_path, dst_path)

def write_a_file(path:str, data:Union[str,bytes], mode:Literal["w+","wb"]="w+"):
    base_path = os.path.realpath(os.path.join(path, os.pardir))
    os.makedirs(base_path, exist_ok=True)
    if mode == "w+" : file2 = open(path, "w+", encoding='utf-8')
    elif mode == "wb" : file2 = open(path, "wb" )
    file2.write(data)
    file2.close()

def read_a_file(path:str, mode:Literal["read","readlines","readbyte"]="read"):
    if not os.path.isfile(path) : return None
    try :
        if mode == "read" :
            file2 = open(path, "r", encoding='utf-8')
            text1 = file2.read()
        elif mode == "readlines" :
            file2 = open(path, "r", encoding='utf-8')
            text1 = file2.readlines()
        elif mode == "readbyte" :
            file2 = open(path, "rb")
            text1 = file2.read()
    except UnicodeDecodeError :
        file2.close()
        return None
    else : return text1

def delete_all_file(path:str):
    if os.path.exists(path) : shutil.rmtree(path)

def file_in_path(path:str) -> Generator[str, Any, Any]:
    """获取该路径下的所有文件路径"""
    for base, _, file_list in os.walk(path) :
        for obj3 in file_list : yield os.path.join( base, obj3 )



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
                if os.path.isdir( file_path ) : yield (path_type, "dir", os.path.join(local_path, file_name) )
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


