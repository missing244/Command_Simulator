import os
from typing import List,Tuple,Literal,Union


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
                if condition_func and not condition_func(base_path_name,file_name) : continue
                search_result.append( ("file", base_path_name, os.path.join(base_path_name,file_name)) )
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
        os.makedirs(base_path,exist_ok=True)
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
