# WebGL渲染器
一个处于实验性阶段的半成品WebGL渲染
## 渲染器介绍
* WebGL MC渲染器现处于实验性阶段。
* 渲染器实现了近70%方块的材质与模型。
* 渲染器支持多线程区块渲染，默认启用渲染距离以优化性能。
## 如何配置
* 将js文件夹完整拷贝
* 注意js文件夹内部文件不可随意改变位置
* 需要搭建http本地服务器才能正常运行
## HTML代码
```html
<!DOCTYPE html>
<html>

	<head>
		<title>可视化模型</title>
    <meta name="viewport" charset="utf-8" content="width=device-width, initial-scale=1.0" />
	</head>

  <body>
		<div id="masterDOM" style="position: fixed; left: 0; top: 0; width: 100vw; height: 100vh; overflow: hidden;">
		<canvas id="threejs" style="width: 100%; height: 100%;"></canvas>
		</div> 
  </body>

   <script type="module">
   //一些JS代码
   </script>

</html>
```
## JS代码
```javascript
import * as THREE from "./js/three.module.js";
import {FirstPersonControls} from './js/FirstPersonControls.js';
import {Block, Structure, DisplayManager} from "./js/MinecraftRender/__init__.js";


const masterDOM = document.querySelector( '#masterDOM' ) //获取画布父类DOM对象
const canvas = document.querySelector( '#threejs' )      //获取画布DOM对象

//创建WebGL对象，透视相机对象，第一人称交互逻辑，显示逻辑
const renderer = new THREE.WebGLRenderer( {antialias: true, canvas} )
const camera = new THREE.PerspectiveCamera( 75, canvas.innerWidth/canvas.innerHeight, 0.1, 2000 );
const controls = new FirstPersonControls(masterDOM, camera, canvas);
const displayManager = new DisplayManager(renderer, camera)

displayManager.scene.add(new THREE.AxesHelper(390));            //在3D场景中添加坐标轴
displayManager.scene.add(new THREE.AmbientLight(0xfaffff));     //在3D场景中添加柔和白光
displayManager.scene.background = new THREE.Color('lightblue'); //在3D场景中设置背景颜色
displayManager.renderDistance = 8                               //在3D场景中设置摄像渲染距离

controls.addEventListener( 'change', displayManager.requestRender() )  //订阅第一人称交互事件并更新渲染信息
setInterval(() => controls.dispatchEvent( {type: 'change'} ), 1000);   //定时触发一次交互事件并更新渲染

//在3D场景中设置摄像头参数
camera.position.x = 1
camera.position.y = StructureObject.size[1]*1.2 + 20;
camera.position.z = -1
camera.lookAt(2, 0, 2);

//配置结构内部数据
const StructureObject = new Structure([3, 3, 3])
StructureObject.blockPlatte.push( new Block("air", {}) )
StructureObject.blockPlatte.push( new Block("bedrock", {}) )
StructureObject.blockPlatte.push( new Block("stone", {}) )
StructureObject.blockIndex.fill(1, 0, 9)
StructureObject.blockIndex.fill(2, 9, 18)
StructureObject.blockIndex.fill(3, 18, 27)

//将结构绑定到渲染控制上
displayManager.structure = StructureObject
```
