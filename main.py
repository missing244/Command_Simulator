#!/usr/bin/python
# -*- coding: UTF-8 -*-

#原生模块加载与设置
import tkinter, ssl, time, threading, traceback
import os, re, math
ssl._create_default_https_context = ssl._create_unverified_context

import main_source.main_window.start_up as start_up             #更新后需要更改的文件
import main_source.main_window.constant as app_constants        #导入APP常量
import main_source.main_window.windows  as app_windows          #导入主界面模块


if __name__ == '__main__' : #启用软件前的加载项目

    def listen_cmd_input() :
        while app_constants.debug_testing : 
            text1 = input(">>> ")
            aaaa = globals()
            a_11 = time.time()
            try : compile(text1,"","eval")
            except Exception as e : 
                try : exec(text1, aaaa, aaaa)
                except : traceback.print_exc()
            else :
                try : print(eval(text1, aaaa, aaaa))
                except : traceback.print_exc()
            print('时间：%s' % str(time.time() - a_11))
    threading.Thread(target=listen_cmd_input, daemon=True).start()

    debug_windows = app_windows.control_windows()
    debug_windows.window.mainloop()
# //[a-zA-Z \\+->:_.'\\",~0-9()]{0,}   update_pack\bedrock_edition\**\**\**.json

debug_windows.window_exit()
Overworld = debug_windows.game_process.DimensionManager.get_dimension("overworld")
BP = debug_windows.game_process.SimulatorModule.BlockPermutation
Overworld.get_block((0, -60, 0))
debug_windows.game_process.OnlinePlayer[3].Inventory.__dict__
debug_windows.game_process.OnlinePlayer[3].get_component("minecraft:health")
debug_windows.game_process.CommandManager.CompileData
