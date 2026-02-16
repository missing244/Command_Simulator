/*
    Minecraft 3D 渲染器
    Constant.js      -> 声明一系列全局常量
    BlockDefine.js   -> 定义方块渲染映射，方块ID升级
    RenderDefine.js  -> 定义3D模型，面坐标与uv信息
    Structure.js     -> 定义通用方块对象，结构对象
    Manager.js       -> 定义显示管理器
    ——————————————————————————————————————————————————
    可导出常量
    Block : 通用方块对象（Structure对象的BlockPalette使用
    Structure : 通用结构对象
    ChunkRenderObject : 区块渲染对象
    DisplayManager : 显示管理器
*/


import * as THREE from "../three.module.js"
import {Block, ChunkRenderObject, Structure} from "./Structure.js";
import {DisplayManager} from "./Manager.js";

export {THREE, Block, ChunkRenderObject, Structure, DisplayManager}