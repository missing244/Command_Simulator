import random, re, json, traceback
from urllib import request, parse

RedirectPattern = re.compile(r"https?://([^/]+)")
IframePattern = re.compile(r'<iframe\s+class="ifr2"\s+name="\d+"\s+src="([^"]+)"\s+frameborder="0"\s+scrolling="no"></iframe>')
SignPattern = re.compile(r"(?<!//)\s*wp_sign\s*=\s*'([^']+)'")
SignUrlPattern = re.compile(r"(?<!//)\s*url\s*:\s*'([^']+)'")
User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.%s.0" % random.randint(1000, 9999)
DownloadHeader = {
    "User-Agent": User_Agent,
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Microsoft Edge\";v=\"122\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "down_ip=1"
}

def fetch_direct_link(url:str) :
    try : redirect_url = RedirectPattern.search(url).group(1)
    except : return None

    request1 = request.Request(url, headers={"User-Agent": User_Agent})
    try : response1:str = request.urlopen(request1, timeout=5).read().decode("utf-8")
    except : print(url) ; print(traceback.format_exc().split("\n")[-2]) ; return None
    
    try : redirect_path = IframePattern.findall(response1)[0]
    except : return None

    request2 = request.Request(f"https://{redirect_url}{redirect_path}", headers={"User-Agent": User_Agent})
    try : response2:str = request.urlopen(request2, timeout=5).read().decode("utf-8")
    except : print(f"https://{redirect_url}{redirect_path}") ; print(traceback.format_exc().split("\n")[-2]) ; return None

    try : sign = SignPattern.search(response2).group(1)
    except : return None
    try : sign_url = SignUrlPattern.search(response2).group(1)
    except : return None

    data = parse.urlencode({'action': 'downprocess', 'signs': '?ctdf', 'sign': sign, 'websign': '', 
        'websignkey': 'bL27', 'ves': 1}).encode("utf-8")
    request3 = request.Request(f"https://{redirect_url}{sign_url}", headers= {"User-Agent": User_Agent,
        "Referer":redirect_path}, data=data)
    try : response3:str = request.urlopen(request3, timeout=5).read().decode("utf-8")
    except : print(f"https://{redirect_url}{sign_url}") ; print(traceback.format_exc().split("\n")[-2]) ; return None

    response3_json = json.loads(response3)
    full_url = response3_json['dom'] + "/file/" + response3_json['url']
    request4 = request.Request(full_url, headers= DownloadHeader)
    try : response4:bytes = request.urlopen(request4, timeout=10).read()
    except : print(full_url) ; print(traceback.format_exc().split("\n")[-2]) ; return None

    return response4
