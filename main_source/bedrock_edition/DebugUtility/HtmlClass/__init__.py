import os, webbrowser, threading, time, json
from typing import List, Dict, Union, Literal, Tuple, Callable
BasePath = os.path.abspath(os.path.join(__file__, ".."))
WorldLoadHTML = open(os.path.join(BasePath, "WorldLoad.html"), "r", encoding="utf-8").read()
CommandLoadHTML = open(os.path.join(BasePath, "CommandLoad.html"), "r", encoding="utf-8").read()

def setTimeOut(sleep_time:float, func:Callable, *args1) :
    def time_out_func(sleep_time, func, *args1) :
        time.sleep(sleep_time)
        func(*args1)
    threading.Thread(target=time_out_func, args=(sleep_time,func, *args1)).start()


