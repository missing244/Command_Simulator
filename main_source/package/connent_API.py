import re,time,random,json,threading,traceback
from urllib import parse,request
from typing import Union,List
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data1 = ''

    def handle_data(self, data):
        self.data1 = data

parser = MyHTMLParser()



request_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54'}
qq_share_re_search = (re.compile('<script type="text/javascript">window.syncData = '), re.compile(';</script>'))


class AES_mode:

    MIX_C  = [[0x2, 0x3, 0x1, 0x1], [0x1, 0x2, 0x3, 0x1], [0x1, 0x1, 0x2, 0x3], [0x3, 0x1, 0x1, 0x2]]
    I_MIXC = [[0xe, 0xb, 0xd, 0x9], [0x9, 0xe, 0xb, 0xd], [0xd, 0x9, 0xe, 0xb], [0xb, 0xd, 0x9, 0xe]]
    RCon   = [0x01000000, 0x02000000, 0x04000000, 0x08000000, 0x10000000, 0x20000000, 0x40000000, 0x80000000, 0x1B000000, 0x36000000]

    S_BOX = [[0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76],
             [0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0],
             [0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15],
             [0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75],
             [0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84],
             [0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF],
             [0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8],
             [0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2],
             [0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73],
             [0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB],
             [0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79],
             [0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08],
             [0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A],
             [0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E],
             [0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF],
             [0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16]]

    I_SBOX = [[0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB],
              [0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB],
              [0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E],
              [0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25],
              [0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92],
              [0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84],
              [0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06],
              [0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B],
              [0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73],
              [0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E],
              [0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B],
              [0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4],
              [0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F],
              [0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF],
              [0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61],
              [0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D]]

    def SubBytes(self, State):
        # 字节替换
        return [self.S_BOX[i][j] for i, j in
               [(_ >> 4, _ & 0xF) for _ in State]]

    def SubBytes_Inv(self, State):
        # 字节逆替换
        return [self.I_SBOX[i][j] for i, j in
               [(_ >> 4, _ & 0xF) for _ in State]]

    def ShiftRows(self, S):
        # 行移位
        return [S[ 0], S[ 5], S[10], S[15],
                S[ 4], S[ 9], S[14], S[ 3],
                S[ 8], S[13], S[ 2], S[ 7],
                S[12], S[ 1], S[ 6], S[11]]

    def ShiftRows_Inv(self, S):
        # 逆行移位
        return [S[ 0], S[13], S[10], S[ 7],
                S[ 4], S[ 1], S[14], S[11],
                S[ 8], S[ 5], S[ 2], S[15],
                S[12], S[ 9], S[ 6], S[ 3]]

    def MixColumns(self, State):
        # 列混合
        return self.Matrix_Mul(self.MIX_C, State)

    def MixColumns_Inv(self, State):
        # 逆列混合
        return self.Matrix_Mul(self.I_MIXC, State)

    def RotWord(self, _4byte_block):
        # 用于生成轮密钥的字移位
        return ((_4byte_block & 0xffffff) << 8) + (_4byte_block >> 24)

    def SubWord(self, _4byte_block):
        # 用于生成密钥的字节替换
        result = 0
        for position in range(4):
            i = _4byte_block >> position * 8 + 4 & 0xf
            j = _4byte_block >> position * 8 & 0xf
            result ^= self.S_BOX[i][j] << position * 8
        return result

    def mod(self, poly, mod = 0b100011011):
        # poly模多项式mod
        while poly.bit_length() > 8:
            poly ^= mod << poly.bit_length() - 9
        return poly

    def mul(self, poly1, poly2):
        # 多项式相乘
        result = 0
        for index in range(poly2.bit_length()):
            if poly2 & 1 << index:
                result ^= poly1 << index
        return result

    def Matrix_Mul(self, M1, M2):  # M1 = MIX_C  M2 = State
        # 用于列混合的矩阵相乘
        M = [0] * 16
        for row in range(4):
            for col in range(4):
                for Round in range(4):
                    M[row + col*4] ^= self.mul(M1[row][Round], M2[Round+col*4])
                M[row + col*4] = self.mod(M[row + col*4])
        return M

    def round_key_generator(self, _16bytes_key):
        # 轮密钥产生
        w = [_16bytes_key >> 96,
             _16bytes_key >> 64 & 0xFFFFFFFF,
             _16bytes_key >> 32 & 0xFFFFFFFF,
             _16bytes_key & 0xFFFFFFFF] + [0]*40
        for i in range(4, 44):
            temp = w[i-1]
            if not i % 4:
                temp = self.SubWord(self.RotWord(temp)) ^ self.RCon[i//4-1]
            w[i] = w[i-4] ^ temp
        return [self.num_2_16bytes(
                    sum([w[4 * i] << 96, w[4*i+1] << 64,
                         w[4*i+2] << 32, w[4*i+3]])
                    ) for i in range(11)]

    def AddRoundKey(self, State, RoundKeys, index):
        # 异或轮密钥
        return self._16bytes_xor(State, RoundKeys[index])

    def _16bytes_xor(self, _16bytes_1, _16bytes_2):
        return [_16bytes_1[i] ^ _16bytes_2[i] for i in range(16)]

    def _16bytes2num(cls, _16bytes):
        # 16字节转数字
        return int.from_bytes(_16bytes, byteorder = 'big')

    def num_2_16bytes(cls, num):
        # 数字转16字节
        return num.to_bytes(16, byteorder = 'big')

    def encrypt(self, plaintext_list, RoundKeys):
        State = plaintext_list
        State = self.AddRoundKey(State, RoundKeys, 0)
        for Round in range(1, 10):
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.MixColumns(State)
            State = self.AddRoundKey(State, RoundKeys, Round)
        State = self.SubBytes(State)
        State = self.ShiftRows(State)
        State = self.AddRoundKey(State, RoundKeys, 10)
        return State

    def decrypt(self, ciphertext_list, RoundKeys,vi):
        State = ciphertext_list
        State = self.AddRoundKey(State, RoundKeys, 10)
        for Round in range(1, 10):
            State = self.ShiftRows_Inv(State)
            State = self.SubBytes_Inv(State)
            State = self.AddRoundKey(State, RoundKeys, 10-Round)
            State = self.MixColumns_Inv(State)
        State = self.ShiftRows_Inv(State)
        State = self.SubBytes_Inv(State)
        State = self.AddRoundKey(State, RoundKeys, 0)
        return self._16bytes_xor(State,vi)

class js_execute :

    def toNumber(str1) :
        list1 = []
        for i in range(16) :
            list1.append(eval("0x" + str1[2*i : 2*i+2]))
        return bytearray(list1)

    def toHex(byte1):
        str1 = ""
        for i in byte1 :
            str1 += ("000" + hex(i).replace("0x",""))[-2:]
        return str1

    def decode(http_str):
        if "<script type=\"text/javascript\" src=\"/aes.js\" >" in http_str :
            re_1 = re.search("a=toNumbers\\(\"[0123456789abcdef]+\"",http_str)
            re_2 = re.search("b=toNumbers\\(\"[0123456789abcdef]+\"",http_str)
            re_3 = re.search("c=toNumbers\\(\"[0123456789abcdef]+\"",http_str)
            a1 = eval("0x" + http_str[re_1.start():re_1.end()].replace("a=toNumbers(","").replace("\"",""))
            b1 = js_execute.toNumber(http_str[re_2.start():re_2.end()].replace("b=toNumbers(","").replace("\"",""))
            c1 = js_execute.toNumber(http_str[re_3.start():re_3.end()].replace("c=toNumbers(","").replace("\"",""))
            return "__test=" + js_execute.cbc_decode(c1,a1,b1)
        else :
            re_1 = re.search("document.cookie=[\"\w_=]+",http_str)
            return http_str[re_1.start():re_1.end()].split("\"")[1]

    def cbc_decode(text1,key,vi):
        cipher = AES_mode()
        key = cipher.round_key_generator(key)
        d = cipher.decrypt(text1,key,vi)
        return js_execute.toHex(d)


def request_API_url(url:Union[str,List[str]],post_data:dict = None,cookie_data:str = None) -> bytes: 
    """产生异常\n这个函数一定要运行于多线程"""
    if cookie_data : request_headers["cookie"] = cookie_data
    if post_data != None : post_data = parse.urlencode(post_data).encode('utf-8')
    if isinstance(url,str) : url = [url]
    
    for url1 in url :
        for times1 in range(2) :
            req1 = request.Request(url1, headers=request_headers, data = post_data)
            response2:bytes = request.urlopen(req1,timeout=4).read()
            if (b'<script type="text/javascript" src="/aes.js" ></script>' in response2) :
                request_headers["cookie"] = js_execute.decode(response2.decode("utf-8")) ; time.sleep(0.25)
            else : return response2

def request_url_without_error(url:Union[str,List[str]],post_data:dict = None,cookie_data:str = None) -> Union[None,bytes] : 
    """不产生异常,这个函数一定要运行于多线程"""
    if cookie_data : request_headers["cookie"] = cookie_data
    if post_data != None : post_data = parse.urlencode(post_data).encode('utf-8')
    if isinstance(url,str) : url = [url]
    
    for url1 in url :
        for times1 in range(2) :
            req1 = request.Request(url1, headers=request_headers, data = post_data)
            try : response2:bytes = request.urlopen(req1,timeout=4).read()
            except : response2 = None; print(url1) ; traceback.print_exc() ; continue
            else :
                if (b'<script type="text/javascript" src="/aes.js" ></script>' in response2) :
                    request_headers["cookie"] = js_execute.decode(response2.decode("utf-8")) ; time.sleep(0.25)
                else : return response2
    

def transfor_qq_share(a:str) -> str :
    b = qq_share_re_search[0].search(a)
    if b == None : return None
    c = qq_share_re_search[1].search(a[b.end():])
    if c == None : return None
    parser.feed(json.loads(a[b.end():b.end()+c.start()])['shareData']['html_content'])
    return parser.data1



TEST_BAIDU_URL = "https://www.baidu.com"
APP_INFO_URL = "https://sharechain.qq.com/a28ff773d6d07e3830dc7bf54cc7a079"

AUTO_LOGIN = ["https://command.infinityfreeapp.com/app_login.php?i=1","https://commandsimulatorapi.great-site.net/app_login.php?i=1"]
MANUAL_LOGIN = ["https://command.infinityfreeapp.com/manual_login.php?i=1","https://commandsimulatorapi.great-site.net/manual_login.php?i=1"]
UPDATE_EXPAND_PACK = ["https://command.infinityfreeapp.com/expand_buy.php?i=1","https://commandsimulatorapi.great-site.net/expand_buy.php?i=1"]
APP_TEST = ["https://command.infinityfreeapp.com/get_app_test.php?i=1","https://commandsimulatorapi.great-site.net/get_app_test.php?i=1"]

UPDATE_BE_ID = "https://ca.projectxero.top/idlist/data/beta/vanilla.zip"
UPDATE_BE_RESOURES = "https://missing244.github.io/cs-main/cs-things/be_resource.tar"
BLOCK_TEXTURE_DOWNLOAD = "https://z4a.net/images/2023/10/01/block_texture.png"



def get_online_api(json1:dict) :
    global AUTO_LOGIN,MANUAL_LOGIN,UPDATE_EXPAND_PACK,APP_TEST

    if "AUTO_LOGIN" in json1 : AUTO_LOGIN = json1['AUTO_LOGIN']
    if "MANUAL_LOGIN" in json1 : MANUAL_LOGIN = json1['MANUAL_LOGIN']
    if "UPDATE_EXPAND_PACK" in json1 : UPDATE_EXPAND_PACK = json1['UPDATE_EXPAND_PACK']
    if "APP_TEST" in json1 : APP_TEST = json1['APP_TEST']

