from . import operation as OperationCode
from typing import Union,Literal,List
import io,brotli,os,sys,traceback

from .function import get_operation
from .operation import match_string_bytes


"""
sys.path.append(os.path.realpath(os.path.join(__file__, os.pardir)))

文档 https://github.com/LNSSPsd/PhoenixBuilder/blob/main/docs/bdump/bdump-cn.md
"""



class BXDFileReadError(Exception): pass
class BXDFileDecodeError(Exception): pass

class BXDFileClosed(Exception): pass



class BDX_File :

    """
    BDX_File 是一个解析 bdx文件 的需要实例化的类\n
    支持读取与新写入两种模式\n
    ---------------------------------\n
    实例化参数 file : 字符串路径 / 字节数组 / 字节流\n
    实例化参数 mode : rb(读取) 与 wb(创建空白文件写入)\n
    ---------------------------------\n
    可用属性 author : 作者名，必须为字符串\n
    可用属性 operation_list : 储存操作码的列表，在 operation.py 内写明了所有支持的操作码\n
    ---------------------------------\n
    可用方法 save_as : 将文件保存至 save_path 的路径\n
    可用方法 close : 关闭文件并释放所有内存数据\n
    """


    def __init__(self, file:Union[str,bytes,io.BytesIO],mode:Literal["rb","wb"] = "rb") -> None:
        if mode not in ["rb","wb"] : raise ValueError("mode 只支持 'rb' 和 'wb' ")

        if isinstance(file,str) : self._file = open(file,mode)
        elif isinstance(file,bytes) : self._file = io.BytesIO(file)
        else : self._file = file
        
        self.author = ""
        self.operation_list : List[Union[OperationCode.CreateConstantString,OperationCode.PlaceBlockWithBlockStates1,
            OperationCode.AddInt16ZValue0,OperationCode.PlaceBlock,OperationCode.AddZValue0,OperationCode.NOP,
            OperationCode.AddInt32ZValue0,OperationCode.PlaceBlockWithBlockStates2,OperationCode.AddXValue,
            OperationCode.SubtractXValue,OperationCode.AddYValue,OperationCode.SubtractYValue,OperationCode.AddZValue,
            OperationCode.SubtractZValue,OperationCode.AddInt16XValue,OperationCode.AddInt32XValue,OperationCode.AddInt16YValue,
            OperationCode.AddInt32YValue,OperationCode.AddInt16ZValue,OperationCode.AddInt32ZValue,OperationCode.SetCommandBlockData,
            OperationCode.PlaceBlockWithCommandBlockData,OperationCode.AddInt8XValue,OperationCode.AddInt8YValue,OperationCode.AddInt8ZValue,
            OperationCode.UseRuntimeIDPool,OperationCode.PlaceRuntimeBlock,OperationCode.placeBlockWithRuntimeId,
            OperationCode.PlaceRuntimeBlockWithCommandBlockData,OperationCode.PlaceRuntimeBlockWithCommandBlockDataAndUint32RuntimeID,
            OperationCode.PlaceCommandBlockWithCommandBlockData,OperationCode.PlaceRuntimeBlockWithChestData,
            OperationCode.PlaceRuntimeBlockWithChestDataAndUint32RuntimeID,OperationCode.AssignDebugData,OperationCode.PlaceBlockWithChestData,
            OperationCode.PlaceBlockWithNBTData,OperationCode.Terminate]] = []

        self.__closed = False
        self.__mode = mode
        if mode == "rb" : self.__init2__()

    def __init2__(self) :
        if self._file.read(3) != b'BD@' : raise BXDFileReadError("不是bdx数据文件")
        bdx_code = io.BytesIO(brotli.decompress(self._file.read()))
        #print(bdx_code.getvalue()[0:100])
        if bdx_code.read(4) != b'BDX\0' : raise BXDFileReadError("不是bdx数据文件")
        self.author = match_string_bytes(bdx_code).decode("utf-8")
        try :
            while 1 : 
                a = bdx_code.read(1)
                if len(a) == 0 : break
                b = get_operation(a).from_bytes(bdx_code)
                self.operation_list.append(b)
                if isinstance(b,OperationCode.Terminate) : break
        except Exception as e :
            #print(len(bdx_code.getvalue()),bdx_code.tell(),bdx_code.getvalue()[bdx_code.tell()-1:])
            #traceback.print_exc()
            raise e

    def closed_test(self) :
        if self.__closed : raise BXDFileClosed("BXDFile 已被关闭")


    def save_as(self,save_path:str=None) :
        Writer1 = io.BytesIO(b"")
        Writer1.write(b'BDX\0')
        Writer1.write(self.author.encode("utf-8"))
        Writer1.write(b'\0')
        if len(self.operation_list) == 0 or isinstance(self.operation_list[-1],OperationCode.Terminate) :
            self.operation_list.append(OperationCode.Terminate())
        for i in self.operation_list : Writer1.write(i.to_bytes())

        if self.__mode == "rb" or isinstance(self._file,io.BytesIO) :
            Writer2 = open(save_path,'wb')
            Writer2.write(b"BD@")
            Writer2.write(brotli.compress(Writer1.getvalue(),quality=6))
            Writer1.close() ; Writer2.close()
        else :
            self._file.write(b"BD@")
            self._file.write(brotli.compress(Writer1.getvalue(),quality=6))
            Writer1.close()

    def close(self) :
        if self.__mode == "wb" : self.save_as()
        self.closed_test()
        self.__closed = True
        self.operation_list.clear()
        self._file.close()




if __name__ == "__main__" :

    if 1 :
        #a = BDX_File("test_file\snowball.bdx")
        #b = BDX_File("test_file\甩锅.bdx")
        c = BDX_File("test1.bdx")
        #a.save_as("a.bdx")
        for i in c.operation_list[-1:] : print(i)
        exit()

    if 0 :
        all_string_pool = [
            '["facing_direction": 0]',
            '["facing_direction": 1]',
            '["facing_direction": 2]',
            '["facing_direction": 3]',
            '["facing_direction": 4]',
            '["facing_direction": 5]'
        ]

        a = BDX_File("test1.bdx","wb")
        a.author = ""

        b = open("pos.txt","r",encoding="utf-8")
        b = b.read().split('\n')

        a.operation_list.append(
            OperationCode.PlaceCommandBlockWithCommandBlockData(1,0,
            'tellraw @p {"rawtext":[{"text":"需要添加标签并设置以下计分板分数\n标签：main_pos\n计分板：RotationX\n计分板：RotationY\n计分板：RotationZ"}]}',
            needsRedstone=True)
        )
        a.operation_list.append(OperationCode.AddZValue())

        for i in b :
            if i.replace(" ","") == "" : continue
            a.operation_list.append(
                OperationCode.PlaceCommandBlockWithCommandBlockData(
                    1, 0 if id(i) == id(b[0]) else 2, i, needsRedstone= True if id(i) == id(b[0]) else False)
            )
            a.operation_list.append(OperationCode.AddYValue())
        a.operation_list.append(OperationCode.Terminate())
        a.close()
        exit()

    for i in os.listdir("input")  :
        print(i)
        a = BDX_File(os.path.join("input",i))
        #a.save_as("a.bdx")
        #print(len(a.operation_list))
        #print(a.operation_list[1000:1660])
        #print(a.operation_list[-2])
        a.save_as(os.path.join("output",i))
        #for i in a.operation_list[0:100] : print(i)







