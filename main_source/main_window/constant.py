import os,uuid,platform,typing,subprocess
try : 
    import jnius
    if platform.system() == "Windows" : raise Exception
except : jnius = None

APP_VERSION = (3, 0, 0, 1) ; debug_testing = True
PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity') if jnius else None
Context = jnius.autoclass('android.content.Context') if jnius else None

def GetPlatform() :
  result = subprocess.run("getprop ro.build.version.release", shell=True, capture_output=True, text=True)
  system_info = platform.uname()
  if system_info.system.lower() == 'windows' : return 'windows'
  elif system_info.system.lower() == 'android' : return 'android'
  elif result.returncode == 0 : return 'android'
  elif system_info.system.lower() == 'linux' and system_info.machine == "x86_64" : return 'linux_amd64'
  elif system_info.system.lower() == 'linux' and system_info.machine == "aarch64" : return 'linux_arm64'
SoftwarePlatform: typing.Literal["windows", "android", "linux_amd64", "linux_arm64"] = GetPlatform()


world_config = {
  "normal_setting" : {
    "world_name" : "我的测试", #给你的世界起个名字
    "gamemode" : 1,#玩家模式——0为生存，1为创造，2为冒险，3为观察者
    "difficulty" : 2, #游戏难度——0为和平，1为简单，2为一般，3为困难
    "seed" : 124343354765 , #世界种子——支持字符串和整数两种类型
    "world_data_type" : "infinity", #be世界类型——可填 字符串infinity、flat
    "simulator_distance" : 4 , #模拟距离——允许输入4,6,8,10
  },
  "be_gamerule" : {
    "commandBlockOutput": True, "commandBlocksEnabled": True ,"doDaylightCycle": True ,"doEntityDrops": True,
    "doImmediateRespawn": False, "doInsomnia": True, "doMobLoot": True, "doMobSpawning": True, "doTileDrops": True,
    "doWeatherCycle": True, "drowningDamage": True, "fallDamage": True, "fireDamage": True, "freezeDamage": True, 
    "keepInventory": False, "doFireTick": True, "showTags" : True, "showCoordinates": True, "pvp" : True ,"tntExplodes" : True,
    "functionCommandLimit": 10000, #值需要在0-10000之间
    "maxCommandChainLength": 65536, #值需要在0-2147483647之间
    "randomTickSpeed": 1, #值需要在0-200之间
    "sendCommandFeedback": True, "showDeathMessages": True, "showBorderEffect": True,
    "mobGriefing": True, "naturalRegeneration": True, "respawnblocksexplode": True,
    "spawnRadius" : 5#值需要在0-12之间
  }
}