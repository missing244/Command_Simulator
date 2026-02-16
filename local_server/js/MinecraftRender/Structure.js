import {THREE} from "./__init__.js"
import * as Constant from "./Constant.js"
import * as BlockDefine from "./BlockDefine.js"
import * as RenderDefine from "./RenderDefine.js"


const BlockTexturePath = new URL('./texture/blocks.png', import.meta.url).href
const BlockTexture = new THREE.TextureLoader().load(BlockTexturePath)
BlockTexture.magFilter = THREE.NearestFilter
BlockTexture.minFilter = THREE.NearestFilter
const BlockMaterial = new THREE.MeshBasicMaterial({map:BlockTexture, transparent:true, alphaTest:0.1})

const PlantTexturePath = new URL('./texture/plants.png', import.meta.url).href
const PlantTexture = new THREE.TextureLoader().load(PlantTexturePath)
PlantTexture.magFilter = THREE.NearestFilter
PlantTexture.minFilter = THREE.NearestFilter
const PlantMaterial = new THREE.MeshBasicMaterial({map:PlantTexture, transparent: true, side:THREE.DoubleSide, alphaTest:0.1})

const TransparentTexturePath = new URL('./texture/transparent.png', import.meta.url).href
const TransparentTexture = new THREE.TextureLoader().load(TransparentTexturePath)
TransparentTexture.magFilter = THREE.NearestFilter
TransparentTexture.minFilter = THREE.NearestFilter
const TransparentMaterial = new THREE.MeshBasicMaterial({map: TransparentTexture, transparent: true, depthWrite:false, depthTest: true})



class Block {
    /**
     * 创建一个方块实例
     * @param {String} id - 方块英文ID
     * @param {Object} states - 键值对Dict[str, Union[str, int, bool]]
     */
    constructor(id, states={}) {
        if (typeof id !== "string") throw new Error("方块对象id传参不正确")
        if (states.constructor !== Object) throw new Error("方块对象states传参不正确")

        /*** 方块唯一英文标识符 * @type {String} */
        this.identifier = id.startsWith("minecraft:") ? id : "minecraft:"+id
        /*** 方块状态 * @type {Object} */
        this.states = { ...states }
        /*** 只读哈希 * @type {Number} */
        this.__hash__ = this.__murmurHash3__()

    }

    /**
     * 判断方块实例是否相等
     * @param {Block} other - 方块
     */
    equal(other){
        if (other.constructor !== Block) return false
        return this.__hash__ === other.__hash__
    }

    /**
     * 计算方块实例的哈希摘要
     * @param {String} key - 方块英文ID
     * @param {Number} seed - 种子
     */
    __murmurHash3__(seed = 0) {
        let StatesStr = ""
        let KeySort = Object.keys( this.states ).sort()
        KeySort.forEach( (item) => {StatesStr = StatesStr + item + ":" + this.states[item] + ","})

        let key = this.identifier + `[${StatesStr}]`
        let h1 = seed;
        const c1 = 0xcc9e2d51, c2 = 0x1b873593;
        const length = key.length;
        
        for (let i = 0; i < length; i++) {
            let k1 = key.charCodeAt(i);
            k1 = Math.imul(k1, c1);
            k1 = (k1 << 15) | (k1 >>> 17);
            k1 = Math.imul(k1, c2);
            
            h1 ^= k1;
            h1 = (h1 << 13) | (h1 >>> 19);
            h1 = Math.imul(h1, 5) + 0xe6546b64;
        }
        
        // 最终混合
        h1 ^= length;
        h1 ^= h1 >>> 16;
        h1 = Math.imul(h1, 0x85ebca6b);
        h1 ^= h1 >>> 13;
        h1 = Math.imul(h1, 0xc2b2ae35);
        h1 ^= h1 >>> 16;
        
        return h1 >>> 0; // 转换为无符号32位整数
    }
}
const AirBlock = new Block("air")

class ChunkRenderObject {

    constructor() {
        this.isRender = false
        this.isEnable = true

        /*** 区块起始位置 * @type {Array<number>} */
        this.origin = [0, 0, 0]
        /*** Mesh对象 * @type {THREE.Mesh} */
        this.singleMesh = null
        /*** Mesh对象 * @type {THREE.Mesh} */
        this.doubleMesh = null
        /*** Mesh对象 * @type {THREE.Mesh} */
        this.transparentMesh = null
    }

    /**
     * 为场景添加区块渲染
     * @param {THREE.Scene} scene - 场景对象
     */
    addRender(scene) {
        if (this.isRender) return null
        if (this.singleMesh) scene.add(this.singleMesh)
        if (this.doubleMesh) scene.add(this.doubleMesh)
        if (this.transparentMesh) scene.add(this.transparentMesh)
        this.isRender = true
    }

    /**
     * 为场景移除区块渲染
     * @param {THREE.Scene} scene - 场景对象
     */
    removeRender(scene) {
        if (!this.isRender) return null
        if (this.singleMesh) {
            //this.singleMesh.geometry.dispose()
            scene.remove(this.singleMesh)
        }
        if (this.doubleMesh) {
            //this.doubleMesh.geometry.dispose()
            scene.remove(this.doubleMesh)
        }
        if (this.transparentMesh) {
            //this.transparentMesh.geometry.dispose()
            scene.remove(this.transparentMesh)
        }
        this.isRender = false
    }

    /**
     * 为场景隐藏区块渲染
     * @param {THREE.Scene} scene - 场景对象
     */
    disableRender() {
        if (!this.isEnable) return null
        if (this.singleMesh) this.singleMesh.visible = false
        if (this.doubleMesh) this.doubleMesh.visible = false
        if (this.transparentMesh) this.transparentMesh.visible = false
        this.isEnable = false
    }

    /**
     * 为场景显示区块渲染
     * @param {THREE.Scene} scene - 场景对象
     */
    enableRender() {
        if (this.isEnable) return null
        if (this.singleMesh) this.singleMesh.visible = true
        if (this.doubleMesh) this.doubleMesh.visible = true
        if (this.transparentMesh) this.transparentMesh.visible = true
        this.isEnable = true
    }
}

class Structure {

    /**
     * 创建一个结构对象
     * @param {Array<Number>} size - 包含了x,y,z大小的数组
     */
    constructor(size) {
        /*** 结构长宽高[x,y,z] * @type {Array<Number>} */
        this.size = size.map( (i) => Math.floor(i) )
        /*** 方块映射数组，按x,y,z顺序排序 * @type {Uint16Array} */
        this.blockIndex = new Uint16Array(this.size[0] * this.size[1] * this.size[2])
        /*** 方块调色板 * @type {Array<Block>} */
        this.blockPlatte = new Array()

        this.sliceSize = this.size[1] * this.size[2]
        this.tileSize = 16
        this.SingleTextureWidth = 256*16
        this.SingleTextureHeight = 64*16
        this.DoubleTextureWidth = 256*16
        this.DoubleTextureHeight = 16*16
        this.TransparentTextureWidth = 256*16
        this.TransparentTextureHeight = 16*16
    }

    /**
     * 重置结构对象
     * @param {Array<Number>} size - 包含了x,y,z大小的数组
     */
    reset(size, blockIndex=null, blockPalette=null) {
        /*** 结构长宽高[x,y,z] * @type {Array<Number>} */
        this.size = size.map( (i) => Math.floor(i) )
        /*** 方块映射数组，按x,y,z顺序排序 * @type {Uint16Array} */
        this.blockIndex = blockIndex ? blockIndex : new Uint16Array(this.size[0] * this.size[1] * this.size[2]) 
        /*** 方块调色板 * @type {Array<Block>} */
        this.blockPlatte = blockPalette ? blockPalette : new Array()
        this.sliceSize = this.size[1] * this.size[2]

        return this
    }

    
    /**
     * 获取一维数组偏量
     * @param {Number} x - x坐标
     * @param {Number} y - y坐标
     * @param {Number} z - z坐标
     */
    getOffset( x, y, z ) {
        return x * this.sliceSize + y * this.size[2] + z
    }
    /**
     * 获取一维数组值
     * @param {Number} x - x坐标
     * @param {Number} y - y坐标
     * @param {Number} z - z坐标
     */
    getBlockIndex( x, y, z ) {
        if (x < 0 || x >= this.size[0]) return this.blockPlatte.length
        if (y < 0 || y >= this.size[1]) return this.blockPlatte.length
        if (z < 0 || z >= this.size[2]) return this.blockPlatte.length
        const voxelOffset = x * this.sliceSize + y * this.size[2] + z
        return this.blockIndex[voxelOffset]
    }
    /**
     * 设置方块
     * @param {Number} x - x坐标
     * @param {Number} y - y坐标
     * @param {Number} z - z坐标
     * @param {Number|Block} v - 方块对象或索引数值
     */
    setBlock( x, y, z, v ) {
        if (x < 0 || x >= this.size[0]) throw Error("x坐标超过结构有效范围")
        if (y < 0 || y >= this.size[1]) throw Error("y坐标超过结构有效范围")
        if (z < 0 || z >= this.size[2]) throw Error("z坐标超过结构有效范围")
        const voxelOffset = x * this.sliceSize + y * this.size[2] + z
        if (v instanceof Block) {
            let v0 = 0
            for (v0 = 0; v0 < this.blockPlatte.length; v0++) {
                const block = this.blockPlatte[index]
                if (block.__hash__ == v.__hash__) break
            }
            if (v0 >= this.blockPlatte.length) this.blockPlatte.push(v)
            this.blockIndex[voxelOffset] = v0
        } else { this.blockIndex[voxelOffset] = v }
    }
    /**
     * 获取方块
     * @param {Number} x - x坐标
     * @param {Number} y - y坐标
     * @param {Number} z - z坐标
     */
    getBlock( x, y, z ) {
        if (x < 0 || x >= this.size[0]) return AirBlock
        if (y < 0 || y >= this.size[1]) return AirBlock
        if (z < 0 || z >= this.size[2]) return AirBlock
        const voxelOffset = x * this.sliceSize + y * this.size[2] + z
        const BlockDict = this.blockPlatte[ this.blockIndex[voxelOffset] ]
        return BlockDict
    }


    /**
     * 获取方块索引数组的切片
     * @param {Number} startX - x坐标
     * @param {Number} startY - y坐标
     * @param {Number} startZ - z坐标
     * @param {Number} endX - x坐标
     * @param {Number} endY - y坐标
     * @param {Number} endZ - z坐标
     */
    getBlockIndexSlice(startX, startY, startZ, endX, endY, endZ) {
        if (endX < startX) [startX, endX] = [endX, startX]
        if (endY < startY) [startY, endY] = [endY, startY]
        if (endZ < startZ) [startZ, endZ] = [endZ, startZ]
        startX = Math.max(0, Math.min(startX, this.size[0]-1))
        startY = Math.max(0, Math.min(startY, this.size[1]-1))
        startZ = Math.max(0, Math.min(startZ, this.size[2]-1))
        endX = Math.max(0, Math.min(endX, this.size[0]-1))
        endY = Math.max(0, Math.min(endY, this.size[1]-1))
        endZ = Math.max(0, Math.min(endZ, this.size[2]-1))
        const sliceChunkSize = [endX-startX+1, endY-startY+1, endZ-startZ+1]
        const result = new Uint16Array(sliceChunkSize[0] * sliceChunkSize[1] * sliceChunkSize[2]);
        const sliceZLength = this.size[2]

        let writeOffset = 0
        for (let x = startX; x <= endX; x++) {
            let readOffset = this.getOffset(x, startY, startZ)
            for (let y = startY; y <= endY; y++) {
                const rowStartOffset = readOffset
                const rowEndOffset = readOffset + sliceChunkSize[2]
                const sliceZMemoryView = this.blockIndex.subarray(rowStartOffset, rowEndOffset)
                result.set(sliceZMemoryView, writeOffset)

                readOffset += sliceZLength
                writeOffset += sliceChunkSize[2]
            }
        }

        return {startPos:[startX, startY, startZ], endPos:[endX, endY, endZ], 
            size:sliceChunkSize, blockIndex:result};
    }


    /**
     * 获取渲染数据列表
     * @param {Number} startX - x坐标
     * @param {Number} startY - y坐标
     * @param {Number} startZ - z坐标
     * @param {Number} endX - x坐标
     * @param {Number} endY - y坐标
     * @param {Number} endZ - z坐标
     */
    getRenderData(startX, startY, startZ, endX, endY, endZ) {
        if (endX < startX) [startX, endX] = [endX, startX]
        if (endY < startY) [startY, endY] = [endY, startY]
        if (endZ < startZ) [startZ, endZ] = [endZ, startZ]
        const single_positions = []; const single_uvs = []; const single_indices = []
        const double_positions = []; const double_uvs = []; const double_indices = []
        const transparent_positions = []; const transparent_uvs = []; const transparent_indices = []

        const sizeX = this.size[0]; const sizeY = this.size[1]; const sizeZ = this.size[2]
        const blockPlatte = new Array(...this.blockPlatte)
        const airTestArray = []             //储存方块是否是空气类，元素数量与方块调色板一致
        const renderDataArray = []          //储存方块指向的渲染数据，元素数量与方块调色板一致
        const coordinateFunctionArray = []  //储存方块坐标变换函数，元素数量与方块调色板一致
        //console.log(renderDataArray)
        //console.log(coordinateFunctionArray)

        blockPlatte.push(AirBlock)
        blockPlatte.forEach( (block) => {
            airTestArray.push( Constant.AirTypes.has(block.identifier) )
            renderDataArray.push( BlockDefine.QueryBlockRender(block) ) 
            coordinateFunctionArray.push( Constant.BlockStateChangePos.
                getStatesToChangeCoordinatesFunction(block) ) 
        })

        const __renderConnent__ = (x, y, z, BlockRenderData, positions, uvs, indices, TextureWidth, TextureHeight) => {
            const { tileSize } = this

            //生成连接处
            Constant.ConnectTest.forEach((element) => {
                const {direction, axes, angle, name} = element
                const NeighborBlockIndex = this.getBlockIndex(x+direction[0], y+direction[1], z+direction[2])
                const NeighborBlock = blockPlatte[NeighborBlockIndex]
                const NeighborBlockData = renderDataArray[NeighborBlockIndex]
                if ( Constant.AirTypes.has(NeighborBlock.identifier) ) return null
                const ConnectInfo = RenderDefine.ConnectionDefine[BlockRenderData.connect]
                if (ConnectInfo.id_test instanceof Set && !ConnectInfo.id_test.has(NeighborBlock.identifier)) return null
                if (ConnectInfo.id_test instanceof RegExp && !ConnectInfo.id_test.test(NeighborBlock.identifier) && 
                (!NeighborBlockData || NeighborBlockData.flawed || BlockRenderData.fluid)) return null

                let ConnectModelName = undefined
                if (ConnectInfo.custom) ConnectModelName = ConnectInfo[name]
                else ConnectModelName = ConnectInfo.model
                if (!ConnectModelName) return null

                if (!ConnectInfo.up_down && direction[1] !== 0) return null
                for (const face_name in RenderDefine.ModelDefine[ConnectModelName]) {
                    const uvMode = RenderDefine.ModelDefine[ConnectModelName][face_name]
                    const uvPosX = (BlockRenderData["index"] % 256) * tileSize
                    const uvPosY = Math.floor(BlockRenderData["index"] / 256) * 160 + uvMode * tileSize

                    //生成模型部分
                    const {corners} = RenderDefine.FaceDefine[face_name]
                    const ndx = Math.floor(positions.length / 3)
                    for ( const { pos, uv } of corners ) {
                        let New_Pos = [pos[0]-0.5, pos[1]-0.5, pos[2]-0.5]
                        if (!ConnectInfo.custom) New_Pos = Constant.BlockStateChangePos.__Rodrigues_rotate__(New_Pos, axes, angle)
                        New_Pos[0] += 0.5 ; New_Pos[1] += 0.5 ; New_Pos[2] += 0.5

                        positions.push( New_Pos[0]+x-startX, New_Pos[1]+y-startY, New_Pos[2]+z-startZ )
                        uvs.push( (uvPosX+uv[0])/TextureWidth, (uvPosY+uv[1])/TextureHeight )
                    }
                    indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
                }
            })
        }
        const renderFluid = (x, y, z, BlockID, TextureWidth, TextureHeight, positions, uvs, indices) => {
            const { tileSize } = this
            const FluidRenderData = BlockDefine.BlockDefine[BlockID]
            const UpBlockIndex = this.getBlockIndex(x, y+1, z)
            const UpBlock = blockPlatte[UpBlockIndex]
            const UPBlockData = renderDataArray[UpBlockIndex]
            const UpBlockIsNotFluid = Constant.AirTypes.has(UpBlock.identifier) || !(UpBlock.identifier === BlockID || UPBlockData.water_log)

            //遍历需要渲染的每一个面
            for (const face_name in RenderDefine.ModelDefine[FluidRenderData.model]) {
                const uvMode = RenderDefine.ModelDefine[FluidRenderData.model][face_name]
                const uvPosX = (FluidRenderData["index"] % 256) * tileSize
                const uvPosY = Math.floor(FluidRenderData["index"] / 256) * 160 + tileSize * uvMode

                const {dir, corners} = RenderDefine.FaceDefine[face_name]
                const NeighborBlockIndex = this.getBlockIndex(x+dir[0], y+dir[1], z+dir[2])
                const NeighborBlock = blockPlatte[NeighborBlockIndex]
                const NeighborBlockData = renderDataArray[NeighborBlockIndex]

                if (!(Constant.AirTypes.has(NeighborBlock.identifier) || 
                    Constant.CopperGrateTypes.has(NeighborBlock.identifier) ||
                    (NeighborBlockData && NeighborBlockData.flawed && !NeighborBlockData.water_log) ||
                    (UpBlockIsNotFluid && dir[1] > 0)) ) continue

                //生成模型部分
                const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                    //console.log(positions)
                    positions.push( pos[0]+x-startX, pos[1]+y+((!UpBlockIsNotFluid && pos[1]>0) ? 0.125 : 0)-startY , pos[2]+z-startZ )
                    uvs.push( (uvPosX+uv[0])/TextureWidth, (uvPosY+uv[1])/TextureHeight )
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
            }
        }
        const renderTransparent = (x, y, z, Block, BlockRenderData, BlockPosTransFunc, positions, uvs, indices) => {
            const { tileSize, TransparentTextureWidth, TransparentTextureHeight} = this

            //遍历需要渲染的每一个面
            for (const face_name in RenderDefine.ModelDefine[BlockRenderData.model]) {
                const {dir, corners} = RenderDefine.FaceDefine[face_name]

                if (!BlockRenderData.flawed) {
                    const NeighborBlockIndex = this.getBlockIndex(x+dir[0], y+dir[1], z+dir[2])
                    const NeighborBlock = blockPlatte[NeighborBlockIndex]
                    const NeighborBlockData = renderDataArray[NeighborBlockIndex]
                    if (! ( Constant.AirTypes.has(NeighborBlock.identifier) ||
                            Constant.CopperGrateTypes.has(NeighborBlock.identifier) ||
                            (NeighborBlockData && NeighborBlockData.flawed) || 
                            (NeighborBlockData && NeighborBlockData.transmitting) ) ) continue
                    //满足以上条件需渲染方块面   相邻方块空气、铜栅格、不完整、透光
                } else if (BlockRenderData.connect) {
                    const NeighborBlockIndex = this.getBlockIndex(x+dir[0], y+dir[1], z+dir[2])
                    const NeighborBlock = blockPlatte[NeighborBlockIndex]
                    const NeighborBlockData = renderDataArray[NeighborBlockIndex]
                    const ConnectInfo = RenderDefine.ConnectionDefine[BlockRenderData.connect]
                    if (ConnectInfo["id_test"].test(NeighborBlock.identifier) || (NeighborBlockData && !NeighborBlockData.flawed)) continue
                    //满足以上条件需渲染连接方块面   相邻方块是同ID类、方块是实心完整方块
                }

                const uvMode = RenderDefine.ModelDefine[BlockRenderData.model][face_name]
                const uvPosX = (BlockRenderData["index"] % 256) * tileSize
                const uvPosY = Math.floor(BlockRenderData["index"] / 256) * 160 + tileSize * uvMode
                //生成模型部分
                const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                    const New_Pos = BlockPosTransFunc ? BlockPosTransFunc(pos, Block.states) : pos
                    positions.push( New_Pos[0]+x-startX, New_Pos[1]+y-startY, New_Pos[2]+z-startZ )
                    uvs.push( (uvPosX+uv[0])/TransparentTextureWidth, (uvPosY+uv[1])/TransparentTextureHeight )
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
            }

            if ( BlockRenderData.connect ) __renderConnent__(
                x, y, z, BlockRenderData, 
                positions, uvs, indices,
                TransparentTextureWidth, TransparentTextureHeight)
        }
        const renderDoubleSide = (x, y, z, Block, BlockRenderData, BlockPosTransFunc, positions, uvs, indices) => {
            const { tileSize, DoubleTextureWidth, DoubleTextureHeight} = this
            
            //遍历需要渲染的每一个面
            for (const face_name in RenderDefine.ModelDefine[BlockRenderData.model]) {
                const {dir, corners} = RenderDefine.FaceDefine[face_name]
                if (!Constant.BlockStateChangePos.__State_Disable_Rerden__(Block.states, dir)) continue

                if (!BlockRenderData.flawed) {
                    const NeighborBlockIndex = this.getBlockIndex(x+dir[0], y+dir[1], z+dir[2])
                    const NeighborBlock = blockPlatte[NeighborBlockIndex]
                    const NeighborBlockData = renderDataArray[NeighborBlockIndex]
                    if ( !(
                        Constant.AirTypes.has(NeighborBlock.identifier) || 
                        (NeighborBlockData && NeighborBlockData.flawed)
                        (NeighborBlockData && NeighborBlockData.transmitting)
                    )) continue
                    //满足以上条件需渲染方块面   相邻方块空气、不完整、透光
                }

                const uvMode = RenderDefine.ModelDefine[BlockRenderData.model][face_name]
                const uvPosX = (BlockRenderData["index"] % 256) * tileSize
                const uvPosY = Math.floor(BlockRenderData["index"] / 256) * 160 + uvMode * tileSize
                //生成模型部分
                const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                    const New_Pos = BlockPosTransFunc ? BlockPosTransFunc(pos, Block.states) : pos
                    positions.push( New_Pos[0]+x-startX, New_Pos[1]+y-startY, New_Pos[2]+z-startZ )
                    uvs.push( (uvPosX+uv[0])/DoubleTextureWidth, (uvPosY+uv[1])/DoubleTextureHeight )
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
            }

            if ( BlockRenderData.connect ) __renderConnent__(
                x, y, z, BlockRenderData, 
                positions, uvs, indices,
                DoubleTextureWidth, DoubleTextureHeight)
        }
        const renderSingleSide = (x, y, z, Block, BlockRenderData, BlockPosTransFunc, positions, uvs, indices) => {
            const { tileSize, SingleTextureWidth, SingleTextureHeight} = this

            //遍历需要渲染的每一个面
            for (const face_name in RenderDefine.ModelDefine[BlockRenderData.model]) {
            const {dir, corners} = RenderDefine.FaceDefine[face_name]

            if (!BlockRenderData.flawed) {
                let New_Pos = BlockPosTransFunc ? BlockPosTransFunc(dir, Block.states, true) : dir
                for (let index = 0; index < New_Pos.length; index++) New_Pos[index] = Math.round(New_Pos[index])
                const NeighborBlockIndex = this.getBlockIndex(x+New_Pos[0], y+New_Pos[1], z+New_Pos[2])
                const NeighborBlock = blockPlatte[NeighborBlockIndex]
                const NeighborBlockData = renderDataArray[NeighborBlockIndex]
                if (!(
                    Constant.AirTypes.has(NeighborBlock.identifier) || 
                    (!Constant.CopperGrateTypes.has(Block.identifier) && Constant.CopperGrateTypes.has(NeighborBlock.identifier)) ||
                    (NeighborBlockData && ( !BlockRenderData.transmitting && NeighborBlockData.transmitting)) ||
                    (NeighborBlockData && ( NeighborBlockData.flawed || NeighborBlockData.transparent)
                    ))
                ) continue
                //满足以上条件需渲染方块面   相邻方块空气、铜栅格、不完整、透光、透明
            }

            const uvMode = RenderDefine.ModelDefine[BlockRenderData.model][face_name]
            const uvPosX = (BlockRenderData["index"] % 256) * tileSize
            const uvPosY = Math.floor(BlockRenderData["index"] / 256) * 160 + tileSize * uvMode
            //生成模型部分
            const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                    const New_Pos = BlockPosTransFunc ? BlockPosTransFunc(pos, Block.states) : pos
                    positions.push( New_Pos[0]+x-startX, New_Pos[1]+y-startY, New_Pos[2]+z-startZ )
                    uvs.push( (uvPosX+uv[0])/SingleTextureWidth, (uvPosY+uv[1])/SingleTextureHeight )
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
            }

            if ( BlockRenderData.connect ) __renderConnent__(
                x, y, z, BlockRenderData, 
                positions, uvs, indices,
                SingleTextureWidth, SingleTextureHeight)
        }


        for ( let x = startX; x <= endX && x < sizeX; x++ ) {
            for ( let y = startY; y <= endY && y < sizeY; y++ ) {
                for ( let z = startZ; z <= endZ && z < sizeZ; z++ ) {
                    const BlockIndex = this.blockIndex[this.getOffset(x, y, z)]
                    const BlockAirTest = airTestArray[BlockIndex]
                    const BlockRenderData = renderDataArray[BlockIndex]
                    if (BlockAirTest) continue
                    if (!BlockRenderData) continue
                    const Block = blockPlatte[BlockIndex]
                    const BlockPosTransFunc = coordinateFunctionArray[BlockIndex]

                    //根据方块选择单面渲染模式还是双面渲染模式
                    if (Constant.LavaTypes.has(Block.identifier)) renderFluid(x, y, z, 
                        "minecraft:lava", this.SingleTextureWidth, this.SingleTextureHeight, 
                        single_positions, single_uvs, single_indices)
                    else if (BlockRenderData.transparent && !BlockRenderData.fluid) 
                        renderTransparent(x, y, z, 
                        Block, BlockRenderData, BlockPosTransFunc, 
                        transparent_positions, transparent_uvs, transparent_indices)
                    else if (BlockRenderData.double_side && !BlockRenderData.fluid) 
                        renderDoubleSide(x, y, z, 
                        Block, BlockRenderData, BlockPosTransFunc, 
                        double_positions, double_uvs, double_indices)
                    else if (!BlockRenderData.fluid) renderSingleSide(x, y, z, 
                        Block, BlockRenderData, BlockPosTransFunc, 
                        single_positions, single_uvs, single_indices)

                    if (BlockRenderData.water_log || Constant.WaterTypes.has(Block.identifier)) renderFluid(x, y, z, 
                        "minecraft:water", this.TransparentTextureWidth, this.TransparentTextureHeight, 
                        transparent_positions, transparent_uvs, transparent_indices)
                }
            }
        }
        return {
            single_positions: new Float32Array(single_positions), 
            single_uvs: new Float32Array(single_uvs), 
            single_indices: new Uint32Array(single_indices),
            double_positions: new Float32Array(double_positions), 
            double_uvs: new Float32Array(double_uvs), 
            double_indices: new Uint32Array(double_indices),
            transparent_positions: new Float32Array(transparent_positions), 
            transparent_uvs: new Float32Array(transparent_uvs), 
            transparent_indices: new Uint32Array(transparent_indices)
        }
    }
    /**
     * 获取渲染对象
     * @param {Number} startX - x坐标
     * @param {Number} startY - y坐标
     * @param {Number} startZ - z坐标
     */
    getRenderObject(startX, startY, startZ, 
        {single_positions, single_uvs, single_indices,
        double_positions, double_uvs, double_indices,
        transparent_positions, transparent_uvs, transparent_indices }){
        const RenderObject = new ChunkRenderObject()
        RenderObject.origin[0] = startX
        RenderObject.origin[1] = startY
        RenderObject.origin[2] = startZ

        if (single_positions.length) {
            const geometry = new THREE.BufferGeometry()
            geometry.setAttribute( 'position', new THREE.BufferAttribute(single_positions, 3))
            geometry.setAttribute( 'uv', new THREE.BufferAttribute(single_uvs, 2))
            geometry.setIndex(new THREE.Uint32BufferAttribute(single_indices, 1))
            const MeshObject = new THREE.Mesh(geometry, BlockMaterial)
            MeshObject.renderOrder = 0
            MeshObject.position.set(startX, startY, startZ)
            RenderObject.singleMesh = MeshObject
            
        }
        if (double_positions.length) {
            const geometry = new THREE.BufferGeometry()
            geometry.setAttribute( 'position', new THREE.BufferAttribute(double_positions, 3))
            geometry.setAttribute( 'uv', new THREE.BufferAttribute(double_uvs, 2))
            geometry.setIndex(new THREE.Uint32BufferAttribute(double_indices, 1))
            const MeshObject = new THREE.Mesh(geometry, PlantMaterial)
            MeshObject.renderOrder = 500
            MeshObject.position.set(startX, startY, startZ)
            RenderObject.doubleMesh = MeshObject
        }
        if (transparent_positions.length) {
            const geometry = new THREE.BufferGeometry()
            geometry.setAttribute( 'position', new THREE.BufferAttribute(transparent_positions, 3))
            geometry.setAttribute( 'uv', new THREE.BufferAttribute(transparent_uvs, 2))
            geometry.setIndex(new THREE.Uint32BufferAttribute(transparent_indices, 1))
            const MeshObject = new THREE.Mesh(geometry, TransparentMaterial)
            MeshObject.renderOrder = 1000
            MeshObject.position.set(startX, startY, startZ)
            RenderObject.transparentMesh = MeshObject
        }

        return RenderObject
    }
    /**
     * 获取渲染对象
     * @param {Number} startX - x坐标
     * @param {Number} startY - y坐标
     * @param {Number} startZ - z坐标
     * @param {Number} endX - x坐标
     * @param {Number} endY - y坐标
     * @param {Number} endZ - z坐标
     */
    getChunkRender(startX, startY, startZ, endX, endY, endZ) {
        if (endX < startX) [startX, endX] = [endX, startX]
        if (endY < startY) [startY, endY] = [endY, startY]
        if (endZ < startZ) [startZ, endZ] = [endZ, startZ]
        const RenderData = this.getRenderData(startX, startY, startZ, endX, endY, endZ)
        const RenderObject = this.getRenderObject(startX, startY, startZ, RenderData)
        return RenderObject
    }

}


export {Block, ChunkRenderObject, Structure}

//
