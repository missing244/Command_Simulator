import socket,re,threading,base64,hashlib,traceback,json,struct,uuid,io,time
import mc_websocket.constant as Constant

from mc_websocket.TypeClass import *
from typing import *


class WebSocket_Client : 
    """
    该类可以根据用户需要进行继承，推荐改写 init_hook 方法\n
    -----------------------------\n
    可改写方法 init_hook : 客户端连接时需要执行的代码\n
    -----------------------------\n
    可用属性 close : 关闭本client的socket连接\n
    可用方法 subscribe_event : 对client发送监听请求\n
    可用方法 unsubscribe_event : 对client发送取消监听请求\n
    可用方法 run_command : 对client发送运行命令的请求\n
    """

    def __init__(self,socket_io:socket.socket) -> None:
        self.client_socket_io:socket.socket = socket_io
        self.client_ip_port:Tuple[IPv4_String,Unsigned_Int16_Port] = socket_io.getpeername()
        self.connect_alive:bool = True
        threading.Thread(target=self.__process__).start()

    def __process__(self) :
        self.init_hook()
        self.__listen_receive__()
    
    def __listen_receive__(self) :
        while self.connect_alive :
            try : recv_data = self.client_socket_io.recv(1048576)
            except : return self.close()
            
            try :
                if len(recv_data) == 0 : return self.close()
                if recv_data[0] & 0b00001111 == 8 : return self.close()
                if recv_data[0] & 0b00001111 != 1 : continue
                data_list = self.__read_respones__(recv_data)
                if data_list : self.receive_msg_hook(data_list)
            except : pass
    
    def __read_respones__(self,respones:bytes) -> List[bytes] :
        if len(respones) < 3 : return None
        bytes_data = io.BytesIO(respones) ; data_list = []
        while 1 :
            mask_and_len = bytes_data.read(2)
            if len(mask_and_len) < 1 : break

            is_mask = mask_and_len[1] & 0b10000000 ; data_len = mask_and_len[1] & 0b01111111

            if data_len == 126 : data_len = int.from_bytes(bytes_data.read(2),'big',signed=False)
            elif data_len == 127 : data_len = int.from_bytes(bytes_data.read(4),'big',signed=False)
            if is_mask : mask_data = bytes_data.read(4)

            if not is_mask : data_list.append(bytes_data.read(data_len))
            else : 
                mask_bytes = bytes_data.read(data_len)
                data_list.append(bytes([(mask_bytes[i] ^ mask_data[i&3]) for i in range(data_len)]))
        return data_list

    def __send_data__(self,msg:str) :
        if not self.connect_alive : raise Exception("客户端%s连接已断开"%str(self.client_ip_port))
        data_bytes = [struct.pack('B',129),bytes(msg,encoding="utf-8")] ; msg_len = len(msg)
        if msg_len < 126 : data_bytes.insert(1,struct.pack('B',msg_len))
        elif msg_len < 32767 : data_bytes.insert(1,struct.pack('!BH',126,msg_len))
        elif msg_len < 2147483647 : data_bytes.insert(1,struct.pack('!BQ',127,msg_len))
        self.client_socket_io.send(b"".join(data_bytes))




    def close(self) -> None : 
        self.connect_alive = False
        self.client_socket_io.close()

    def init_hook(self) : pass

    def receive_msg_hook(self,msg_data:List[bytes]) : pass
    
    def subscribe_event(self,event_name:str) -> None :
        if event_name not in Constant.SUBSCRIBE_EVENT : raise Exception("%s不属于可订阅事件" % event_name)
        Constant.SUBSCRIBE_EVENT_JSON['body']['eventName'] = event_name
        Constant.SUBSCRIBE_EVENT_JSON['header']['requestId'] = str(uuid.uuid4())
        self.__send_data__(json.dumps(Constant.SUBSCRIBE_EVENT_JSON))

    def unsubscribe_event(self,event_name:str) -> None :
        if event_name not in Constant.SUBSCRIBE_EVENT : raise Exception("%s不属于可订阅事件" % event_name)
        Constant.UNSUBSCRIBE_EVENT_JSON['body']['eventName'] = event_name
        Constant.UNSUBSCRIBE_EVENT_JSON['header']['requestId'] = str(uuid.uuid4())
        self.__send_data__(json.dumps(Constant.UNSUBSCRIBE_EVENT_JSON))

    def run_command(self,command:str) -> UUID :
        Constant.RUN_COMMAND_JSON['body']['commandLine'] = command
        Constant.RUN_COMMAND_JSON['header']['requestId'] = str(uuid.uuid4())
        self.__send_data__(json.dumps(Constant.RUN_COMMAND_JSON))
        return Constant.RUN_COMMAND_JSON['header']['requestId']



class WebSocket_Server : 
    """
    实例化传参 ip, : IPv4格式的字符串\n
    实例化传参  : 2字节无符号整数\n
    可选实例化传参 ClientClassHook : 继承于WebSocket_Client的新类\n
    ------------------------------------\n
    可用属性 connenting_client : 正在连接的client列表\n
    可用方法 start_server : 开启ws服务端\n
    可用方法 stop_server : 关闭ws服务端\n
    """
    
    def __init__(self,ip:IPv4_String,port:Unsigned_Int16_Port,/,ClientClassHook:WebSocket_Client=WebSocket_Client) -> None:
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind((ip , port))
        self.tcp_server.listen(10)

        self.connenting_client:List[WebSocket_Client] = []
        self.__server_run = False
        self.__server_close = False
        self.__client_class = ClientClassHook

    def __memory_relese__(self) :
        while self.__server_run and (not self.__server_close) :
            for i in list(self.connenting_client) : 
                if not i.connect_alive : self.connenting_client.remove(i)
            time.sleep(5)
    

    def server_hand_shake(self,socket_io:socket.socket) -> None :
        recv_fata = socket_io.recv(32768)
        match_key = re.search("Sec-WebSocket-Key: [A-Za-z0-9+/]*={0,2}",recv_fata.decode("utf-8"))
        hash_text = match_key.group().replace("Sec-WebSocket-Key: ","") + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        hash_text = base64.b64encode(hashlib.sha1(bytes(hash_text, encoding='utf-8')).digest()).decode("utf-8")
        response = Constant.WEBSOCKET_HAND_SHAKE % hash_text
        socket_io.send(bytes(response.encode("utf-8")))

    def listen_client_connention(self) -> None :
        while self.__server_run :
            try : 
                client_address = self.tcp_server.accept()[0]
                self.server_hand_shake(client_address)
            except : 
                if "client_address" in locals() : client_address.close()
            else : self.connenting_client.append(self.__client_class(client_address))


    def start_server(self) -> None : 
        if self.__server_run : raise Exception("WS服务器已经在运行中了")
        if self.__server_close : raise Exception("WS服务器已经被关闭了")
        self.__server_run = True
        threading.Thread(target=self.listen_client_connention).start()
        threading.Thread(target=self.__memory_relese__).start()

    def stop_server(self) -> None : 
        if self.__server_close : raise Exception("WS服务器已经被关闭了了")
        self.__server_run = False
        self.__server_close = True
        for i in self.connenting_client : i.close()
        self.tcp_server.close()





__all__ = ["WebSocket_Server","WebSocket_Client"]




if __name__ == "__main__" : #请将该代码与mc_websocket文件夹处于同一路径下使用
        import random,time,mc_websocket
        ip,port = socket.gethostbyname(socket.gethostname()),random.randint(10000,60000)
        WS_Server = mc_websocket.WebSocket_Server(ip,port)
        WS_Server.start_server()
        print("/connect %s:%s"%(ip,port))
        while 1 : time.sleep(1) #保证线程运行，如果是UI控制则无需该操作