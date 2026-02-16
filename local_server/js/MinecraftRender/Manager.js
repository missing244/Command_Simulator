import {THREE, ChunkRenderObject, Structure} from "./__init__.js"
const PlantTexturePath = new URL('./MultiThread.js', import.meta.url).href
const MultiThread = new Worker(PlantTexturePath, {type: 'module'});
class ThreadEventsManager {

    constructor() {
        this.callbacks = {}

        MultiThread.onmessage = (/** @type {MessageEvent} */event) => {
            for (const [key, value] of Object.entries(this.callbacks)) value( event )
        }
    }

    subscribe(callback) {
        const key = crypto.randomUUID()
        this.callbacks[key] = callback
        return key
    }

    unsubscribe(uuid) {
        const exist = uuid in this.callbacks
        if (exist) delete this.callbacks[key]
        return exist
    }
}
const threadEventsManager = new ThreadEventsManager()



class DisplayManager {
    
    /**
     * 创建一个显示管理器
     * @param {THREE.WebGLRenderer} renderer - 渲染器
     * @param {THREE.PerspectiveCamera} camera - 透视摄像机
     * @param {Structure?} structObj - 需要显示的结构
     */
    constructor(renderer, camera, structObj=null) {
        this.camera = camera
        this.renderer = renderer
        this.structure = structObj
        
        const canvas = renderer.domElement;
		this.renderer.setPixelRatio(window.devicePixelRatio)
		this.renderer.setSize(canvas.innerWidth, canvas.innerHeight)

        /***   * @type {Record<String, ChunkRenderObject>} */
        this.chunk = {}
        this.scene = new THREE.Scene()
        this.renderDistance = 10
        this.uuid = crypto.randomUUID()

        const ComputeChunkRender = ( /** @type {MessageEvent} */event) => {
            if (event.data.uuid !== this.uuid) return null
            const element = event.data.pos
            const SceneChunkPosKey = `(${element.x},${element.y},${element.z})`
            const RenderObject = this.structure.getRenderObject(
                element.x, element.y, element.z, event.data.returnData)
            this.chunk[SceneChunkPosKey] = RenderObject
        }
        threadEventsManager.subscribe(ComputeChunkRender)
    }

    /**
     * 创建一个渲染回调函数
     * 用于绑定渲染更新事件
     */
    requestRender(){
        let renderRequested = false;
        const renderer = this.renderer
        const camera = this.camera
        const scene = this.scene
        const canvas = renderer.domElement

        const render = () => {
            renderRequested = undefined;
            const needUpdate = resizeRendererToDisplaySize(renderer)
            if (needUpdate) {
                camera.aspect = canvas.clientWidth / canvas.clientHeight;
                camera.updateProjectionMatrix();
            }
            this.flashRender()
            renderer.render( scene, camera );
        }
        const resizeRendererToDisplaySize = () => {
            const width = canvas.clientWidth;
            const height = canvas.clientHeight;
            const needResize = canvas.width !== width || canvas.height !== height;
            if ( needResize ) renderer.setSize( width, height, false );
            return needResize;
        }
        const requestRenderIfNotRequested = () => {
            if ( renderRequested ) return null
            renderRequested = true;
            requestAnimationFrame(render);
        }

        return requestRenderIfNotRequested
    }

    /**
     * 刷新渲染区块
     */
    flashRender(){
        if (!this.structure) return null
        const CameraX = this.camera.position.x
        const CameraY = this.camera.position.y
        const CameraZ = this.camera.position.z
        const CameraChunkX = Math.floor( CameraX / 16 )
        const CameraChunkZ = Math.floor( CameraZ / 16 )

        const LoopStartChunkX = (CameraChunkX - this.renderDistance) * 16
        const LoopStartChunkZ = (CameraChunkZ - this.renderDistance) * 16
        const LoopEndChunkX = (CameraChunkX + this.renderDistance) * 16
        const LoopEndChunkZ = (CameraChunkZ + this.renderDistance) * 16

        /***   * @type {Array<THREE.Vector3>} */
        const RenderChunkPos = [] 
        for (let x = LoopStartChunkX; x <= LoopEndChunkX; x+=16) {
            for (let z = LoopStartChunkZ; z <= LoopEndChunkZ; z+=16) {
                for (let y = 0; y < 384; y+=384) {
                    if (x < 0 || x >= this.structure.size[0]) continue
                    if (y < 0 || y >= this.structure.size[1]) continue
                    if (z < 0 || z >= this.structure.size[2]) continue
                    const chunkStart = new THREE.Vector3(x, 0, z)
                    const distanceX = Math.abs(x/16 - CameraChunkX)
                    const distanceZ = Math.abs(z/16 - CameraChunkZ)
                    const chunkDistance = Math.pow(distanceX*distanceX + distanceZ*distanceZ, 0.5)
                    if (chunkDistance > this.renderDistance) continue

                    RenderChunkPos.push(chunkStart)
                }
            }
        }

        const SceneChunkPosSet = new Set( Object.keys(this.chunk) )
        RenderChunkPos.forEach((element) => {
            const SceneChunkPosKey = `(${element.x},${element.y},${element.z})`

            if (SceneChunkPosSet.has(SceneChunkPosKey)) {
                if (!this.chunk[SceneChunkPosKey]) return null
                this.chunk[SceneChunkPosKey].addRender(this.scene)
            } else {
                this.chunk[SceneChunkPosKey] = null
                const SliceStart = [element.x-1, element.y-1, element.z-1]
                const SliceEnd = [element.x+16, element.y+384, element.z+16]
                const ArraySliceInfo = this.structure.getBlockIndexSlice(...SliceStart, ...SliceEnd)

                MultiThread.postMessage({type:"ComputeMeshData", uuid:this.uuid, 
                    pos:element, size:ArraySliceInfo.size,
                    requestStart:SliceStart, requestEnd:SliceEnd,
                    realStart:ArraySliceInfo.startPos, realEnd:ArraySliceInfo.endPos,
                    blockIndex:ArraySliceInfo.blockIndex, blockPalette:this.structure.blockPlatte}, 
                    [ArraySliceInfo.blockIndex.buffer])
            }
            SceneChunkPosSet.delete(SceneChunkPosKey)
        })

        SceneChunkPosSet.forEach( (item) => {
            if (!this.chunk[item]) return null
            this.chunk[item].removeRender(this.scene)
            //delete this.chunk[item]
        })
    }
}


export {DisplayManager}