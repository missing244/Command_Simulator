# 蓝奏云直链解析脚本
# 作者：笨蛋ovo
# https://github.com/liuran001/Lanzou_DirectLink_sh
__version__ = (1, 0, 0)

import random
from urllib import request

IP_ADDRESSES = [
    "218", "218", "66", "66", "218", "218", "60", "60", "202", "204", "66", "66", "66", "59", "61", "60", "222", "221", "66", "59",
    "60", "60", "66", "218", "218", "62", "63", "64", "66", "66", "122", "211"
]
URL_DOMAINS = [
    "wwa.lanzoux.com",
    "wwa.lanzoup.com",
    "wwa.lanzouw.com",
    "wwa.lanzouy.com"
]

def get_random_ip():
    ip1 = random.choice(IP_ADDRESSES)
    ip2 = random.randint(60, 255)
    ip3 = random.randint(60, 255)
    ip4 = random.randint(60, 255)
    return f"{ip1}.{ip2}.{ip3}.{ip4}"

random_ip = get_random_ip()
referer_url = random.choice(URL_DOMAINS)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.%s' % random.randint(15, 55),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'X-Forwarded-For': random_ip,
    'Referer': referer_url,
}

def fetch(url: str, headers: dict, data: dict = None, method: str = 'GET') -> str:
    if method.upper() == 'GET': request_obj = request.Request(url, headers=headers, method="GET", unverifiable=True)
    elif method.upper() == 'POST': request_obj = request.Request(url, headers=headers, data=data, method='POST', unverifiable=True)
    else : raise ValueError(f"Unsupported HTTP method: {method}")
    try : response = request.urlopen(request_obj, timeout=3)
    except : return None
    else : return response.read().decode("utf-8", "ignore")

def fetch_direct_link(url: str, pwd: str = None) :
    fileid = url.split('/')[-1]

    for domain in URL_DOMAINS:
        base_url = f"https://{domain}/tp/{fileid}"
        html = fetch(base_url, headers=HEADERS)

        if pwd:
            postsign = html.split('var vidksek')[1].split("'")[1]
            rawdownurl_response = fetch(
                f"https://{domain}/ajaxm.php",
                headers=HEADERS,
                data={
                    'action': 'downprocess',
                    'sign': postsign,
                    'p': pwd
                },
                method="POST",
            )

            if rawdownurl_response:
                dom = rawdownurl_response.split('dom')[1].split('"')[2].replace('\\', '')
                url = rawdownurl_response.split('url')[1].split('"')[2].replace('\\', '')
                downurl = dom + '/file/' + url
            else:
                print(f"Error: Could not get a response from 'https://{domain}/ajaxm.php'")
                continue
        else:
            tedomain = html.split('var vkjxld')[1].split("'")[1]
            domianload = html.split('var hyggid')[1].split("'")[1]
            downurl = tedomain + domianload

        directlink = request.Request(downurl, headers=HEADERS, method="HEAD", unverifiable=True)
        try : directlink_response = request.urlopen(directlink, timeout=3)
        except : continue
        file_bytes:bytes = directlink_response.read()
        if file_bytes : return file_bytes

    return None

