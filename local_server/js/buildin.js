function setLocalStorage(key, value, ttl) {
    const now = new Date();
    // ttl 为过期时间，单位为毫秒
    const item = {
        value: value,
        expiry: now.getTime() + ttl * 1000 * 60,
    };
    localStorage.setItem(key, JSON.stringify(item));
}

// 获取带有过期时间的 localStorage 数据
function getLocalStorage(key) {
    const itemStr = localStorage.getItem(key);
    if (!itemStr) return null;
    const item = JSON.parse(itemStr);
    const now = new Date();
    if (now.getTime() > item.expiry) {
        localStorage.removeItem(key);
        return null;
    }
    return item.value;
}


class post_to_server{
    constructor(){
        this.xhr = new XMLHttpRequest();
        this.xhr.timeout = 20000;
        this.xhr.ontimeout = function(){
            alert("服务器请求已超时，请重新请求");
        }
    }
    open_and_post(json_data){
        this.xhr.open('POST', 'http://localhost:32323');
        this.xhr.send(JSON.stringify(json_data));
    }
    set_response_callback(success_func,faild_func,end_func){
        this.xhr.onreadystatechange = () => {
            if (this.xhr.readyState == 4) {
                if (this.xhr.status == 200) {
                    success_func(this.xhr.responseText)// 执行回调函数 
                }
                else faild_func();
                if (end_func) end_func()
            }
        };
    }
}