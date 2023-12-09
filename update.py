from urllib import request
import tarfile,json,traceback,time,os,re,ssl,random,webbrowser
ssl._create_default_https_context = ssl._create_unverified_context
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._html_data = ''

    def handle_data(self, data:str):
        self._html_data = data

    def feed(self, data: str):
        super().feed(data)
        return self._html_data




user_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.%s.140 Safari/537.36 Edge/115.0.1901.%s'%(random.randint(100,900),random.randint(1000,5000))}

if os.path.exists("update.tar") and os.path.isfile("update.tar") :
    print("搜索到本地更新文件，正在自动更新.....")
    with tarfile.open("update.tar","r") as zip_file1 : zip_file1.extractall("")
    os.remove("update.tar")
    print("更新完成，安卓用户需要重新打开main.py文件")
    time.sleep(10)
    exit()



try : 
    print('正在获取更新信息.....')
    req1 = request.Request("https://sharechain.qq.com/bfc7fe2d0b016f0cb778d64ca90cad30", headers=user_headers)
    response1 = request.urlopen(req1,timeout=5).read().decode("utf-8")
    match_start = re.compile('window.syncData = ').search(response1)
    match_end = re.compile(';</script>').search(response1,pos=match_start.end())
    if not any([match_start],match_end) : raise Exception
    dowload_info_unparse = json.loads(response1[match_start.end():match_end.start()])['shareData']['html_content']
    dowload_info = json.loads( MyHTMLParser().feed(dowload_info_unparse) )
except : 
    print("更新失败，无法获取更新信息，请联系开发者解决")
    time.sleep(10)
    exit()
else :
    print("你将要更新：%s" % dowload_info['version'])
    download_url_list = response1['url']
    for index1,url2 in enumerate(download_url_list) :
        try :
            req2 = request.Request(url2, headers=user_headers)
            response2 = request.urlopen(req2,timeout=8).read()
        except : 
            if (index1 + 1) != len(download_url_list) : continue
            print("\n".join([
                "########################################################",
                "在线更新失败，你可以在蓝奏云中下载离线更新包。",
                "下载密码为 1234",
                "将离线更新包放置在本目录，重新运行本文件即可更新",
                "########################################################"
            ]))
            print("")
            for i in range(6,0,-1) : 
                print("%s秒后即将打开浏览器......",i) ; time.sleep(1)
            webbrowser.open(response1['offline_url'])
            break
        else :
            file1 = open("update.tar","wb")
            file1.write(response2)
            file1.close()
            with tarfile.open("update.tar","r") as zip_file1 : zip_file1.extractall("")
            print("更新完成，安卓用户需要重新打开main.py文件")
            os.remove("update.tar")
            time.sleep(10)
            break
