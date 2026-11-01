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
        const single_positions = []; const single_uvs = []; const single_indices = []; const single_ao = []
        const double_positions = []; const double_uvs = []; const double_indices = []
        const transparent_positions = []; const transparent_uvs = []; const transparent_indices = []; const transparent_ao = []

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

                for (const pos_uv of FaceData.corners) {pos_uv.pos = TransFunc(pos_uv.pos, block.states)}
                blockGeometryArray[ArrayLastIndex][face_name] = FaceData
            }
        })

        /**
         * 合并 single / transparent 两组面。
         * 不新增几何缓冲、不改函数输入输出，只往已有的
         * single_positions/single_uvs/single_indices 和
         * transparent_positions/transparent_uvs/transparent_indices 写入。
         *
         * UV 编码（复用现有 uv 属性，不新增顶点属性）：
         *   uv.x 整数部分 = 图集列号 + UV_ENCODE_OFFSET
         *   uv.y 整数部分 = 图集行号 * 10 + uvMode + UV_ENCODE_OFFSET
         *   uv.x/uv.y 小数部分 = 面内 0..w / 0..h 的局部坐标 / UV_ENCODE_SCALE
         * 片元 shader 用 floor/fract 解码，并用 fract(local) 在 16x16 小图内重复采样。
         *
         * @returns {Array<Object|null>} 非 null 的调色板索引由本函数渲染
         */
        const greedyMesherBuild = () => {
            const DIRECTIONS = [
                [1, 0, 0], [-1, 0, 0],
                [0, 1, 0], [0, -1, 0],
                [0, 0, 1], [0, 0, -1]
            ]
            const TILE = this.tileSize
            const ATLAS_COLS = 256
            const ROW_STRIDE_TILES = 10
            const ENCODE_OFFSET = 10
            const ENCODE_SCALE = 1024
            const size = this.size

            const renderMin = [
                Math.max(0, startX), Math.max(0, startY), Math.max(0, startZ)
            ]
            const renderMax = [
                Math.min(size[0] - 1, endX),
                Math.min(size[1] - 1, endY),
                Math.min(size[2] - 1, endZ)
            ]

            const cubeInfoArray = new Array(blockPlatte.length).fill(null)
            if (renderMin[0] > renderMax[0] ||
                renderMin[1] > renderMax[1] ||
                renderMin[2] > renderMax[2]) return cubeInfoArray

            const directionKey = (dir) => `${dir[0]},${dir[1]},${dir[2]}`
            const isUnitAxis = (vec) => {
                let count = 0
                for (let i = 0; i < 3; i++) {
                    if (vec[i] === 0) continue
                    if (Math.abs(vec[i]) !== 1) return false
                    count++
                }
                return count === 1
            }
            const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
            const snapUnit = (v) => {
                if (Math.abs(v) < 1e-4) return 0
                if (Math.abs(v - 1) < 1e-4) return 1
                return v
            }

            // ---------- AO 采样 ----------
            // 不透明、非流体、非双面植物才算遮挡物；玻璃/水/植物不产生 AO。
            const isOccluder = (blockId) => {
                if (airTestArray[blockId]) return false
                const rd = renderDataArray[blockId]
                if (!rd) return false
                return !rd.transparent && !rd.fluid && !rd.double_side
            }

            // 返回一个面的 4 个角 AO（0..3，3 最亮）：
            //   side1/side2/corner 分别对应面外侧一层的两边和斜角
            const faceAO = (x, y, z, dir, u, v) => {
                const corners = Object.create(null)
                let uniform = true
                let level = -1
                const base = [x + dir[0], y + dir[1], z + dir[2]]

                for (const sv of [-1, 1]) {
                    for (const su of [-1, 1]) {
                        const s1 = [base[0], base[1], base[2]]; s1[u] += su
                        const s2 = [base[0], base[1], base[2]]; s2[v] += sv
                        const cn = [base[0], base[1], base[2]]; cn[u] += su; cn[v] += sv

                        const s1o = isOccluder(this.getBlockIndex(s1[0], s1[1], s1[2])) ? 1 : 0
                        const s2o = isOccluder(this.getBlockIndex(s2[0], s2[1], s2[2])) ? 1 : 0
                        const cno = isOccluder(this.getBlockIndex(cn[0], cn[1], cn[2])) ? 1 : 0

                        const value = (s1o && s2o) ? 0 : 3 - (s1o + s2o + cno)
                        corners[`${su},${sv}`] = value

                        if (level < 0) level = value
                        else if (value !== level) uniform = false
                    }
                }

                return { corners, uniform, level }
            }

            // ---------- 1. 找出可合并的完整方块（single / transparent） ----------
            for (let id = 0; id < blockPlatte.length; id++) {
                if (airTestArray[id]) continue
                const renderData = renderDataArray[id]
                if (!renderData) continue
                if (renderData.flawed || renderData.fluid || renderData.double_side ||
                    renderData.connect || renderData.transmitting || renderData.water_log) continue

                const kind = renderData.transparent ? 'transparent' : 'single'
                const geometry = blockGeometryArray[id]
                const model = blockModelArray[id]
                if (!geometry || !model) continue
                const faceNames = Object.keys(geometry)
                if (faceNames.length !== 6) continue

                const faces = Object.create(null)
                const usedDirections = new Set()
                let valid = true

                for (const faceName of faceNames) {
                    const faceData = geometry[faceName]
                    const uvMode = model[faceName]
                    if (!faceData || !faceData.corners || faceData.corners.length !== 4 ||
                        typeof uvMode !== 'number') { valid = false; break }

                    const dir = faceData.dir.map((v) => Math.round(v))
                    if (!isUnitAxis(dir)) { valid = false; break }
                    const dirKey = directionKey(dir)
                    if (usedDirections.has(dirKey)) { valid = false; break }
                    usedDirections.add(dirKey)

                    const corners = faceData.corners
                    const p0 = corners[0].pos.map(snapUnit)
                    const p1 = corners[1].pos.map(snapUnit)
                    const p2 = corners[2].pos.map(snapUnit)
                    const p3 = corners[3].pos.map(snapUnit)
                    if (![...p0, ...p1, ...p2, ...p3].every((v) => v === 0 || v === 1)) {
                        valid = false; break
                    }

                    // 只合并完整 16x16 图块的面，避免处理子矩形 UV
                    let tileUMin = Infinity, tileUMax = -Infinity
                    let tileVMin = Infinity, tileVMax = -Infinity
                    for (const corner of corners) {
                        tileUMin = Math.min(tileUMin, corner.uv[0])
                        tileUMax = Math.max(tileUMax, corner.uv[0])
                        tileVMin = Math.min(tileVMin, corner.uv[1])
                        tileVMax = Math.max(tileVMax, corner.uv[1])
                    }
                    if (Math.abs(tileUMin) > 1e-6 || Math.abs(tileUMax - TILE) > 1e-6 ||
                        Math.abs(tileVMin) > 1e-6 || Math.abs(tileVMax - TILE) > 1e-6) {
                        valid = false; break
                    }

                    const uVec = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
                    const vVec = [p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]]
                    if (!isUnitAxis(uVec) || !isUnitAxis(vVec) || dot(uVec, vVec) !== 0) {
                        valid = false; break
                    }
                    if (p3[0] !== p0[0] + uVec[0] + vVec[0] ||
                        p3[1] !== p0[1] + uVec[1] + vVec[1] ||
                        p3[2] !== p0[2] + uVec[2] + vVec[2]) { valid = false; break }

                    const axis = dir[0] !== 0 ? 0 : (dir[1] !== 0 ? 1 : 2)
                    const boundary = dir[axis] > 0 ? 1 : 0
                    if (p0[axis] !== boundary) { valid = false; break }

                    // 顶点顺序必须与法线一致，否则合并后会被背面剔除
                    const cross = [
                        uVec[1] * vVec[2] - uVec[2] * vVec[1],
                        uVec[2] * vVec[0] - uVec[0] * vVec[2],
                        uVec[0] * vVec[1] - uVec[1] * vVec[0]
                    ]
                    if (cross[0] !== dir[0] || cross[1] !== dir[1] || cross[2] !== dir[2]) {
                        valid = false; break
                    }

                    const du = [
                        corners[1].uv[0] - corners[0].uv[0],
                        corners[1].uv[1] - corners[0].uv[1]
                    ]
                    const dv = [
                        corners[2].uv[0] - corners[0].uv[0],
                        corners[2].uv[1] - corners[0].uv[1]
                    ]
                    const texUAxis = du[0] !== 0 ? 0 : (du[1] !== 0 ? 1 : -1)
                    const texVAxis = dv[0] !== 0 ? 0 : (dv[1] !== 0 ? 1 : -1)
                    if (texUAxis < 0 || texVAxis < 0 || texUAxis === texVAxis) {
                        valid = false; break
                    }

                    // 纹理 U/V 在几何上的实际增长方向（含正负号）
                    const uvBaseVec = texUAxis === 0 ? uVec : vVec
                    const uvSign = texUAxis === 0 ? Math.sign(du[0]) : Math.sign(dv[0])
                    const uvVec = [
                        uvBaseVec[0] * uvSign,
                        uvBaseVec[1] * uvSign,
                        uvBaseVec[2] * uvSign
                    ]

                    const vvBaseVec = texVAxis === 1 ? vVec : uVec
                    const vvSign = texVAxis === 1 ? Math.sign(dv[1]) : Math.sign(du[1])
                    const vvVec = [
                        vvBaseVec[0] * vvSign,
                        vvBaseVec[1] * vvSign,
                        vvBaseVec[2] * vvSign
                    ]
                    if (!isUnitAxis(uvVec) || !isUnitAxis(vvVec) || dot(uvVec, vvVec) !== 0) {
                        valid = false; break
                    }

                    faces[dirKey] = {
                        origin: p0,
                        uVec, vVec, uvVec, vvVec,
                        tileCol: renderData.index % ATLAS_COLS,
                        tileRowMode: Math.floor(renderData.index / ATLAS_COLS) * ROW_STRIDE_TILES + uvMode
                    }
                }

                if (!valid || usedDirections.size !== 6) continue
                cubeInfoArray[id] = { kind, faces }
            }

            // ---------- 2. 六个方向分别构建 mask 并贪心合并 ----------
            for (const dir of DIRECTIONS) {
                const axis = dir[0] !== 0 ? 0 : (dir[1] !== 0 ? 1 : 2)
                const u = (axis + 1) % 3
                const v = (axis + 2) % 3
                const uCount = renderMax[u] - renderMin[u] + 1
                const vCount = renderMax[v] - renderMin[v] + 1
                const dirKey = directionKey(dir)
                const planeOffset = dir[axis] > 0 ? 1 : 0

                for (let slice = renderMin[axis]; slice <= renderMax[axis]; slice++) {
                    const mask = new Array(uCount * vCount).fill(null)

                    // 2.1 当前切片上每个格子是否需要渲染该方向的面
                    for (let j = 0; j < vCount; j++) {
                        for (let i = 0; i < uCount; i++) {
                            const pos = [0, 0, 0]
                            pos[axis] = slice
                            pos[u] = renderMin[u] + i
                            pos[v] = renderMin[v] + j

                            const id = this.getBlockIndex(pos[0], pos[1], pos[2])
                            const info = cubeInfoArray[id]
                            if (!info) continue
                            const face = info.faces[dirKey]
                            if (!face) continue

                            const neighborId = this.getBlockIndex(
                                pos[0] + dir[0], pos[1] + dir[1], pos[2] + dir[2])
                            const neighbor = blockPlatte[neighborId]
                            const neighborData = renderDataArray[neighborId]

                            let visible
                            if (info.kind === 'single') {
                                visible =
                                    Constant.AirTypes.has(neighbor.identifier) ||
                                    (!Constant.CopperGrateTypes.has(blockPlatte[id].identifier) &&
                                        Constant.CopperGrateTypes.has(neighbor.identifier)) ||
                                    (neighborData && neighborData.transmitting) ||
                                    (neighborData && (neighborData.flawed || neighborData.transparent))
                            } else {
                                visible =
                                    Constant.AirTypes.has(neighbor.identifier) ||
                                    Constant.CopperGrateTypes.has(neighbor.identifier) ||
                                    (neighborData && neighborData.flawed) ||
                                    (neighborData && neighborData.transmitting)
                            }

                            if (!visible) continue

                            const ao = faceAO(pos[0], pos[1], pos[2], dir, u, v)
                            mask[j * uCount + i] = {
                                id, face, kind: info.kind,
                                uniform: ao.uniform,
                                aoLevel: ao.level,
                                aoCorners: ao.corners
                            }
                        }
                    }

                    // 2.2 在 mask 上找最大的同 id 矩形
                    for (let j = 0; j < vCount; j++) {
                        for (let i = 0; i < uCount;) {
                            const cell = mask[j * uCount + i]
                            if (!cell) { i++; continue }

                            // 真实版 AO：只有 4 个角 AO 完全一致的面才允许合并；
                            // AO 不均匀的面保持 1x1，逐角写入 AO，避免把墙角明暗插值掉。
                            let w = 1
                            if (cell.uniform) {
                                while (i + w < uCount) {
                                    const next = mask[j * uCount + i + w]
                                    if (!next || next.id !== cell.id ||
                                        !next.uniform || next.aoLevel !== cell.aoLevel) break
                                    w++
                                }
                            }

                            let h = 1
                            if (cell.uniform) {
                                while (j + h < vCount) {
                                    let rowMatches = true
                                    for (let k = 0; k < w; k++) {
                                        const next = mask[(j + h) * uCount + i + k]
                                        if (!next || next.id !== cell.id ||
                                            !next.uniform || next.aoLevel !== cell.aoLevel) {
                                            rowMatches = false; break
                                        }
                                    }
                                    if (!rowMatches) break
                                    h++
                                }
                            }

                            // 合并矩形在方块边界上的四个角
                            const plane = slice + planeOffset
                            const cornerAt = (offsetU, offsetV) => {
                                const p = [0, 0, 0]
                                p[axis] = plane
                                p[u] = renderMin[u] + i + offsetU
                                p[v] = renderMin[v] + j + offsetV
                                return p
                            }
                            const p00 = cornerAt(0, 0)
                            const p10 = cornerAt(w, 0)
                            const p01 = cornerAt(0, h)
                            const p11 = cornerAt(w, h)

                            const face = cell.face
                            const ref = [0, 0, 0]
                            ref[axis] = slice
                            ref[u] = renderMin[u] + i
                            ref[v] = renderMin[v] + j
                            ref[0] += face.origin[0]
                            ref[1] += face.origin[1]
                            ref[2] += face.origin[2]

                            // 几何顶点顺序按 uVec/vVec 排序，保证三角形绕序正确
                            const faceUVOf = (p) => {
                                const dx = p[0] - ref[0]
                                const dy = p[1] - ref[1]
                                const dz = p[2] - ref[2]
                                return [
                                    Math.round(dx * face.uVec[0] + dy * face.uVec[1] + dz * face.uVec[2]),
                                    Math.round(dx * face.vVec[0] + dy * face.vVec[1] + dz * face.vVec[2])
                                ]
                            }
                            const rectCorners = [
                                { pos: p00, faceUV: faceUVOf(p00), mu: i, mv: j },
                                { pos: p10, faceUV: faceUVOf(p10), mu: i + w, mv: j },
                                { pos: p01, faceUV: faceUVOf(p01), mu: i, mv: j + h },
                                { pos: p11, faceUV: faceUVOf(p11), mu: i + w, mv: j + h }
                            ]

                            const faceUMin = Math.min(...rectCorners.map((c) => c.faceUV[0]))
                            const faceUMax = Math.max(...rectCorners.map((c) => c.faceUV[0]))
                            const faceVMin = Math.min(...rectCorners.map((c) => c.faceUV[1]))
                            const faceVMax = Math.max(...rectCorners.map((c) => c.faceUV[1]))

                            const cornerMap = new Map()
                            for (const corner of rectCorners) {
                                cornerMap.set(`${corner.faceUV[0]},${corner.faceUV[1]}`, corner)
                            }
                            const c00 = cornerMap.get(`${faceUMin},${faceVMin}`)
                            const c10 = cornerMap.get(`${faceUMax},${faceVMin}`)
                            const c01 = cornerMap.get(`${faceUMin},${faceVMax}`)
                            const c11 = cornerMap.get(`${faceUMax},${faceVMax}`)
                            if (!c00 || !c10 || !c01 || !c11) {
                                for (let l = 0; l < h; l++) {
                                    for (let k = 0; k < w; k++) {
                                        mask[(j + l) * uCount + i + k] = null
                                    }
                                }
                                i += w
                                continue
                            }

                            // 纹理 U/V 方向上的 0..w / 0..h 局部坐标
                            const localUVOf = (p) => {
                                const dx = p[0] - ref[0]
                                const dy = p[1] - ref[1]
                                const dz = p[2] - ref[2]
                                return [
                                    Math.round(dx * face.uvVec[0] + dy * face.uvVec[1] + dz * face.uvVec[2]),
                                    Math.round(dx * face.vvVec[0] + dy * face.vvVec[1] + dz * face.vvVec[2])
                                ]
                            }
                            for (const corner of rectCorners) {
                                corner.local = localUVOf(corner.pos)
                            }
                            const localUMin = Math.min(...rectCorners.map((c) => c.local[0]))
                            const localUMax = Math.max(...rectCorners.map((c) => c.local[0]))
                            const localVMin = Math.min(...rectCorners.map((c) => c.local[1]))
                            const localVMax = Math.max(...rectCorners.map((c) => c.local[1]))
                            const repeatU = localUMax - localUMin
                            const repeatV = localVMax - localVMin
                            if (!((repeatU === w && repeatV === h) ||
                                (repeatU === h && repeatV === w))) {
                                for (let l = 0; l < h; l++) {
                                    for (let k = 0; k < w; k++) {
                                        mask[(j + l) * uCount + i + k] = null
                                    }
                                }
                                i += w
                                continue
                            }

                            const targetPositions = cell.kind === 'transparent'
                                ? transparent_positions : single_positions
                            const targetUvs = cell.kind === 'transparent'
                                ? transparent_uvs : single_uvs
                            const targetIndices = cell.kind === 'transparent'
                                ? transparent_indices : single_indices
                            const targetAO = cell.kind === 'transparent'
                                ? transparent_ao : single_ao
                            const uniformAO = 0.55 + cell.aoLevel * 0.15

                            const ndx = targetPositions.length / 3
                            for (const corner of [c00, c10, c01, c11]) {
                                const localU = corner.local[0] - localUMin
                                const localV = corner.local[1] - localVMin
                                targetPositions.push(
                                    corner.pos[0] - startX,
                                    corner.pos[1] - startY,
                                    corner.pos[2] - startZ
                                )
                                targetUvs.push(
                                    face.tileCol + ENCODE_OFFSET + localU / ENCODE_SCALE,
                                    face.tileRowMode + ENCODE_OFFSET + localV / ENCODE_SCALE
                                )

                                if (cell.uniform) {
                                    targetAO.push(uniformAO)
                                } else {
                                    // 非均匀 AO 一定保持 1x1，按这个角在 mask 上的位置取 AO
                                    const su = corner.mu === i ? -1 : 1
                                    const sv = corner.mv === j ? -1 : 1
                                    const level = cell.aoCorners[`${su},${sv}`]
                                    targetAO.push(0.55 + level * 0.15)
                                }
                            }
                            targetIndices.push(ndx, ndx + 1, ndx + 2, ndx + 2, ndx + 1, ndx + 3)

                            for (let l = 0; l < h; l++) {
                                for (let k = 0; k < w; k++) {
                                    mask[(j + l) * uCount + i + k] = null
                                }
                            }
                            i += w
                        }
                    }
                }
            }

            return cubeInfoArray
        }

        const greedyInfoArray = greedyMesherBuild()

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
                    if (greedyInfoArray[BlockIndex]) continue
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
        // 非合并的 single/transparent 面没有 AO，补 1.0，保证 AO 与顶点一一对应
        while (single_ao.length < single_positions.length / 3) single_ao.push(1.0)
        while (transparent_ao.length < transparent_positions.length / 3) transparent_ao.push(1.0)

        return {
            single_positions: new Float32Array(single_positions), 
            single_uvs: new Float32Array(single_uvs), 
            single_indices: new Uint32Array(single_indices),
            single_ao: new Float32Array(single_ao),
            double_positions: new Float32Array(double_positions), 
            double_uvs: new Float32Array(double_uvs), 
            double_indices: new Uint32Array(double_indices),
            transparent_positions: new Float32Array(transparent_positions), 
            transparent_uvs: new Float32Array(transparent_uvs), 
            transparent_indices: new Uint32Array(transparent_indices),
            transparent_ao: new Float32Array(transparent_ao)
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
            returnValue.single_positions.buffer, returnValue.single_uvs.buffer,
            returnValue.single_indices.buffer, returnValue.single_ao.buffer,
            returnValue.double_positions.buffer, returnValue.double_uvs.buffer, returnValue.double_indices.buffer,
            returnValue.transparent_positions.buffer, returnValue.transparent_uvs.buffer,
            returnValue.transparent_indices.buffer, returnValue.transparent_ao.buffer];
        result = {type:"ComputeMeshData", uuid:e.data.uuid, pos:e.data.pos, returnData:returnValue}
    }
    self.postMessage(result, transferables);
}