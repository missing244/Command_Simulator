import random,traceback,base64,json,zlib,re
from urllib import request
from html.parser import HTMLParser
Info_URL = "https://sharechain.qq.com/a28ff773d6d07e3830dc7bf54cc7a079"
qq_share_re_search = (re.compile('<script type="text/javascript">window\\.syncData = '), re.compile(';</script>'))
user_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.%s.140 Safari/537.36 Edge/115.0.1901.%s'%(random.randint(100,900),random.randint(1000,5000))}


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._html_data = ''

    def handle_data(self, data:str):
        self._html_data = data

    def feed(self, data: str):
        super().feed(data)
        return self._html_data

parser = MyHTMLParser()
def transfor_qq_share(a:str) -> str :
    b = qq_share_re_search[0].search(a)
    if b is None : return None
    c = qq_share_re_search[1].search(a[b.end():])
    if c is None : return None
    parser.feed(json.loads(a[b.end():b.end()+c.start()])['shareData']['html_content'])
    return parser._html_data



Req1 = request.Request(Info_URL, headers=user_headers)
try : Info_Base64:bytes = request.urlopen(Req1, timeout=3).read().decode("utf-8")
except :
    print("错误：获取更新信息失败\n请重试 或 在命令模拟器中添加QQ群进行联系。\n\n\n")
    traceback.print_exc()
    exit()

Info = json.loads(zlib.decompress( base64.b64decode( transfor_qq_share(Info_Base64) ) ))
Code = zlib.decompress(base64.b64decode( Info["app_download"]["download_code"].encode("utf-8") )).decode("utf-8")
exec(Code)