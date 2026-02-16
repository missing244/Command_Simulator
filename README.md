# 命令模拟器
命令模拟器是一款提供Minecraft基岩版**命令检查**与**命令模拟**的Python辅助程序。
## 主体功能
* 终端命令：通过终端控制命令运行，实现可控命令调试；
* 命令方块文件：低代码风格构建区分模块的命令方块组；
* 命令方块渲染：命令方块文件可渲染在MC中等效的命令方块链样式；
* 模拟命令方块运行：命令模拟器支持模拟命令方块的运行；
* 模拟函数命令运行：命令模拟器支持模拟函数命令的运行；
* 命令反馈文件：命令运行可生成反馈文件供玩家检查命令运行中产生的影响。
## 附加功能
* 基岩版全部字符的查询与复制
* 基岩版方块、物品等ID快速查询
* 适用于手动导入命令的小窗口命令复制
* 结构文件的解析支持（包括RunAway）
* 存档文件的解析支持（LevelDB）
* 3D世界预览器（测试）
## 拓展包功能
* execute与方块状态语法升级
* 基岩版指令语法自动补全与提示
* 按照预设模板快速生成同类命令
* 基岩版rawtext json富文本编辑器
* 基岩版websocket服务器
* 可视化命令效果调试
## 依赖软件
### Android
* [MT管理器](https://mt2.cn/download/)
* [Pydroid 3](https://wwop.lanzoup.com/iA8rP39i20jc)，蓝奏云密码1234
### Windows 7-8
* [Python 3.8.0](https://wwop.lanzoul.com/ijGLp2wl7exa)，蓝奏云密码1234，如已安装3.8以上版本请忽略
### Windows 10-11
* [Python 3.9.2](https://wwop.lanzoul.com/isS760vu6rvg)，蓝奏云密码1234，如已安装3.8以上版本请忽略
## 安装方法
* 根据系统完成依赖软件的安装
* 将本仓库文件下载到本地
* Windows系统：将下载的文件进行解压，双击windows启动.bat启动
* Android系统：通过MT管理器，将下载的文件移动到/storage/emulated/0/Android/data/ru.iiec.pydroid3/files/路径下进行解压，然后通过Pydroid 3打开main.py文件启动。[寻找main.py文件教程](https://github.com/missing244/Command_Simulator/blob/main/%E5%90%AF%E5%8A%A8%E6%96%B9%E6%B3%95.jpg)
## 可二次开发的第三方模块
* **MCCommandParser**：实现了Minecraft基岩版命令的语法检查，通过树结构构造语法解析的拆词器
* **MCBELab**：实现了将方块实体格式转换至MCBE1.18.30内部数据的兼容
* **MCBEWorld**：实现了MCBE的LevelDB存档格式读写操作的模块
* **MCStructureManage**：实现了Minecraft基岩版流通的结构文件的解析与转换
* **python_nbt**：实现了NBT数据的序列化与反序列化
## 致谢名单
* **CBerJun**：设计命令方块运行的核心代码，命令高亮检查拓展包
* **long-or**：设计无第三方模块的NBT数据的序列化与反序列化模块
* **Ethanout**：工具运行测试，BUG汇集与汇报
