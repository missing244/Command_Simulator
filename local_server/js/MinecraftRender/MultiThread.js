import * as Constant from "./Constant.js"
import * as BlockDefine from "./BlockDefine.js"
import * as RenderDefine from "./RenderDefine.js"
const ChooseRealPos = (x, y, m) => x===y ? x+m : y


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
     * @param {Uint16Array} blockIndex - 包含了x,y,z大小的数组
     * @param {Array<Block>} blockPalette - 包含了x,y,z大小的数组
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
        const airTestArray = []              //储存方块是否是空气类，元素数量与方块调色板一致
        const renderDataArray = []           //储存方块指向的渲染数据，元素数量与方块调色板一致
        const blockModelArray = []           //储存方块模型面的UV变换结果，元素数量与方块调色板一致
        const blockGeometryArray = []        //储存方块模型加方块状态的变换结果，元素数量与方块调色板一致

        blockPlatte.push(AirBlock)
        blockPlatte.forEach( (block) => {
            const ArrayLastIndex = airTestArray.length

            airTestArray.push( Constant.AirTypes.has(block.identifier) )
            renderDataArray.push( BlockDefine.QueryBlockRender(block) ) 
            blockGeometryArray.push( {} ) 
            
            const TransFunc = Constant.BlockStateChangePos.getStatesToChangeCoordinatesFunction(block)
            const RenderModel = RenderDefine.ModelDefine[renderDataArray[ArrayLastIndex].model]
            blockModelArray.push( RenderModel ) 

            for (const face_name in RenderModel) {
                const FaceData = JSON.parse(JSON.stringify(RenderDefine.FaceDefine[face_name]))
                if (!TransFunc) {blockGeometryArray[ArrayLastIndex][face_name] = FaceData ; continue; }
                
                FaceData.dir = TransFunc(FaceData.dir, block.states, true)
                for (let index = 0; index < FaceData.dir.length; index++) FaceData.dir[index] = Math.round(FaceData.dir[index])
                if (!Constant.BlockStateChangePos.__State_Disable_Render__(block.states, FaceData.dir)) continue

                for (const pos_uv of FaceData.corners) {pos_uv.pos = TransFunc(pos_uv.pos, block.states, true)}
                blockGeometryArray[ArrayLastIndex][face_name] = FaceData
            }
        })

        const greedyMesherBuild = ({single, transparent, fluid}) => {
            const dims = [this.size[0], this.size[1], this.size[2]]
            const get = (x,y,z) => this.getBlockIndex(x,y,z)

            const pushFace = (buffer, verts, w, h, render) => {
                const ndx = buffer.pos.length / 3

                const tileSize = this.tileSize
                const texW = this.SingleTextureWidth
                const texH = this.SingleTextureHeight

                const uvPosX = (render.index % 256) * tileSize
                const uvPosY = Math.floor(render.index / 256) * 160

                const u0 = uvPosX / texW
                const v0 = uvPosY / texH
                const u1 = (uvPosX + tileSize * w) / texW
                const v1 = (uvPosY + tileSize * h) / texH

                for (let i=0;i<4;i++) {
                    const p = verts[i]
                    buffer.pos.push(p[0], p[1], p[2])
                }

                buffer.uv.push(
                    u0, v0,
                    u1, v0,
                    u1, v1,
                    u0, v1
                )

                buffer.ind.push(
                    ndx, ndx+1, ndx+2,
                    ndx, ndx+2, ndx+3
                )
            }

            // 6个方向
            for (let d = 0; d < 3; d++) {

                const mask = []
                const u = (d + 1) % 3
                const v = (d + 2) % 3

                const x = [0,0,0]
                const q = [0,0,0]
                q[d] = 1

                for (x[d] = -1; x[d] < dims[d]; ) {

                    // --- 构建mask ---
                    let n = 0

                    for (x[v]=0; x[v]<dims[v]; x[v]++) {
                        for (x[u]=0; x[u]<dims[u]; x[u]++) {

                            const a = (x[d] >= 0) ? get(x[0], x[1], x[2]) : -1
                            const b = (x[d] < dims[d]-1) ? get(x[0]+q[0], x[1]+q[1], x[2]+q[2]) : -1

                            let cell = null

                            if (a !== -1) {

                                const render = renderDataArray[a]

                                if (render?.fluid) {
                                    if (d === 1 && q[1] === 1) {
                                        const up = get(x[0],x[1]+1,x[2])
                                        if (up !== a) {
                                            cell = { id: a, type: "fluid" }
                                        }
                                    }
                                } else {
                                    if (b === -1 || b !== a) {
                                        if (render.transparent) {
                                            cell = { id: a, type: "transparent" }
                                        } else {
                                            cell = { id: a, type: "single" }
                                        }
                                    }
                                }
                            }

                            mask[n++] = cell
                        }
                    }

                    x[d]++

                    // --- Greedy 合并 ---
                    n = 0
                    for (let j=0; j<dims[v]; j++) {
                        for (let i=0; i<dims[u]; ) {

                            const cell = mask[n]
                            if (!cell) { i++; n++; continue }

                            let w
                            for (w=1; i+w<dims[u]; w++) {
                                const next = mask[n+w]
                                if (!next || next.id !== cell.id || next.type !== cell.type) break
                            }

                            let h
                            let done = false
                            for (h=1; j+h<dims[v]; h++) {
                                for (let k=0; k<w; k++) {
                                    const next = mask[n + k + h*dims[u]]
                                    if (!next || next.id !== cell.id || next.type !== cell.type) {
                                        done = true
                                        break
                                    }
                                }
                                if (done) break
                            }

                            // --- 生成面 ---
                            x[u] = i
                            x[v] = j

                            const du = [0,0,0]
                            const dv = [0,0,0]

                            du[u] = w
                            dv[v] = h

                            const verts = []

                            for (let m=0; m<4; m++) {
                                const pos = [x[0], x[1], x[2]]

                                if (m === 1 || m === 2) {
                                    pos[0]+=du[0]; pos[1]+=du[1]; pos[2]+=du[2]
                                }
                                if (m === 2 || m === 3) {
                                    pos[0]+=dv[0]; pos[1]+=dv[1]; pos[2]+=dv[2]
                                }

                                verts.push([
                                    pos[0]-startX,
                                    pos[1]-startY,
                                    pos[2]-startZ
                                ])
                            }

                            // 👉 根据材质选择buffer
                            let buffer
                            if (cell.type === "single") buffer = single
                            else if (cell.type === "transparent") buffer = transparent
                            else buffer = fluid

                            const render = renderDataArray[cell.id]
                            pushFace(buffer, verts, w, h, render)

                            // 清mask
                            for (let l=0; l<h; l++) {
                                for (let k=0; k<w; k++) {
                                    mask[n + k + l*dims[u]] = null
                                }
                            }

                            i += w
                            n += w
                        }
                    }
                }
            }
        }
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
        const renderTransparent = (x, y, z, Block, BlockRenderData, BlockModel, BlockGeometry, positions, uvs, indices) => {
            const { tileSize, TransparentTextureWidth, TransparentTextureHeight} = this

            //遍历需要渲染的每一个面
            for (const face_name in BlockModel) {
                const {dir, corners} = BlockGeometry[face_name]

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

                const uvMode = BlockModel[face_name]
                const uvPosX = (BlockRenderData["index"] % 256) * tileSize
                const uvPosY = Math.floor(BlockRenderData["index"] / 256) * 160 + tileSize * uvMode
                //生成模型部分
                const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                    positions.push( pos[0]+x-startX, pos[1]+y-startY, pos[2]+z-startZ )
                    uvs.push( (uvPosX+uv[0])/TransparentTextureWidth, (uvPosY+uv[1])/TransparentTextureHeight )
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
            }

            if ( BlockRenderData.connect ) __renderConnent__(
                x, y, z, BlockRenderData, 
                positions, uvs, indices,
                TransparentTextureWidth, TransparentTextureHeight)
        }
        const renderDoubleSide = (x, y, z, Block, BlockRenderData, BlockModel, BlockGeometry, positions, uvs, indices) => {
            const { tileSize, DoubleTextureWidth, DoubleTextureHeight} = this
            
            //遍历需要渲染的每一个面
            for (const face_name in BlockModel) {
                const {dir, corners} = BlockGeometry[face_name]

                if (!BlockRenderData.flawed) {
                    const NeighborBlockIndex = this.getBlockIndex(x+dir[0], y+dir[1], z+dir[2])
                    const NeighborBlock = blockPlatte[NeighborBlockIndex]
                    const NeighborBlockData = renderDataArray[NeighborBlockIndex]
                    if ( !(
                        Constant.AirTypes.has(NeighborBlock.identifier) || 
                        (NeighborBlockData && NeighborBlockData.flawed) || 
                        (NeighborBlockData && NeighborBlockData.transmitting)
                    )) continue
                    //满足以上条件需渲染方块面   相邻方块空气、不完整、透光
                }

                const uvMode = BlockModel[face_name]
                const uvPosX = (BlockRenderData["index"] % 256) * tileSize
                const uvPosY = Math.floor(BlockRenderData["index"] / 256) * 160 + uvMode * tileSize
                //生成模型部分
                const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                    positions.push( pos[0]+x-startX, pos[1]+y-startY, pos[2]+z-startZ )
                    uvs.push( (uvPosX+uv[0])/DoubleTextureWidth, (uvPosY+uv[1])/DoubleTextureHeight )
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
            }

            if ( BlockRenderData.connect ) __renderConnent__(
                x, y, z, BlockRenderData, 
                positions, uvs, indices,
                DoubleTextureWidth, DoubleTextureHeight)
        }
        const renderSingleSide = (x, y, z, Block, BlockRenderData, BlockModel, BlockGeometry, positions, uvs, indices) => {
            const { tileSize, SingleTextureWidth, SingleTextureHeight} = this

            //遍历需要渲染的每一个面
            for (const face_name in BlockModel) {
                const {dir, corners} = BlockGeometry[face_name]

                if (!BlockRenderData.flawed) {
                    const NeighborBlockIndex = this.getBlockIndex(x+dir[0], y+dir[1], z+dir[2])
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

                const uvMode = BlockModel[face_name]
                const uvPosX = (BlockRenderData["index"] % 256) * tileSize
                const uvPosY = Math.floor(BlockRenderData["index"] / 256) * 160 + tileSize * uvMode
                //生成模型部分
                const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                    positions.push( pos[0]+x-startX, pos[1]+y-startY, pos[2]+z-startZ )
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
                    const BlockRenderData = renderDataArray[BlockIndex]
                    if (airTestArray[BlockIndex]) continue
                    if (!BlockRenderData) continue
                    const Block = blockPlatte[BlockIndex]
                    const BlockModel = blockModelArray[BlockIndex]
                    const BlockGeometry = blockGeometryArray[BlockIndex]

                    //根据方块选择单面渲染模式还是双面渲染模式
                    if (Constant.LavaTypes.has(Block.identifier)) renderFluid(x, y, z, 
                        "minecraft:lava", this.SingleTextureWidth, this.SingleTextureHeight, 
                        single_positions, single_uvs, single_indices)
                    else if (BlockRenderData.transparent && !BlockRenderData.fluid) 
                        renderTransparent(x, y, z, Block,
                        BlockRenderData, BlockModel, BlockGeometry, 
                        transparent_positions, transparent_uvs, transparent_indices)
                    else if (BlockRenderData.double_side && !BlockRenderData.fluid) 
                        renderDoubleSide(x, y, z, Block,
                        BlockRenderData, BlockModel, BlockGeometry, 
                        double_positions, double_uvs, double_indices)
                    else if (!BlockRenderData.fluid) 
                        renderSingleSide(x, y, z, Block,
                        BlockRenderData, BlockModel, BlockGeometry, 
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
}


/**
 * 计算mesh信息
 * @param {Array<Number>} requestStart - 包含了x,y,z大小的数组
 * @param {Array<Number>} requestEnd - 包含了x,y,z大小的数组
 * @param {Array<Number>} realStart - 包含了x,y,z大小的数组
 * @param {Array<Number>} realEnd - 包含了x,y,z大小的数组
 * @param {Array<Number>} size - 包含了x,y,z大小的数组
 * @param {Uint16Array} blockIndex - 包含了x,y,z大小的数组
 * @param {Array<Record>} blockPalette - 包含了x,y,z大小的数组
 */
function ComputeMeshData(requestStart, requestEnd, realStart, realEnd, size, blockIndex, blockPalette) {
    const CommonStructure = new Structure([1, 1, 1])
    const BlockPalette = []
    blockPalette.forEach( (item) => BlockPalette.push(new Block(item.identifier, item.states)) )
    CommonStructure.reset(size, blockIndex, BlockPalette)

    let renderStartX = (requestStart[0] === realStart[0]) ? 1 : 0
    let renderStartY = (requestStart[1] === realStart[1]) ? 1 : 0
    let renderStartZ = (requestStart[2] === realStart[2]) ? 1 : 0
    let renderEndX = (requestEnd[0] === realEnd[0]) ? size[0]-2 : size[0]-1
    let renderEndY = (requestEnd[1] === realEnd[1]) ? size[1]-2 : size[1]-1
    let renderEndZ = (requestEnd[2] === realEnd[2]) ? size[2]-2 : size[2]-1
    const RenderData = CommonStructure.getRenderData(
        renderStartX, renderStartY, renderStartZ,
        renderEndX, renderEndY, renderEndZ)
    return RenderData
}



self.onmessage = function(e) {
    let result = null, transferables = null

    if (e.data.type === "ComputeMeshData") {
        //需要传参 {uuid, pos, size, requestStart, requestEnd, realStart, realEnd, chunkSize, blockIndex, blockPalette}
        const returnValue = ComputeMeshData( 
            e.data.requestStart, e.data.requestEnd, 
            e.data.realStart, e.data.realEnd,
            e.data.size, e.data.blockIndex, e.data.blockPalette)
        transferables = [ 
            returnValue.single_positions.buffer, returnValue.single_uvs.buffer, returnValue.single_indices.buffer,
            returnValue.double_positions.buffer, returnValue.double_uvs.buffer, returnValue.double_indices.buffer,
            returnValue.transparent_positions.buffer, returnValue.transparent_uvs.buffer, returnValue.transparent_indices.buffer];
        result = {type:"ComputeMeshData", uuid:e.data.uuid, pos:e.data.pos, returnData:returnValue}
    }
    self.postMessage(result, transferables);
}