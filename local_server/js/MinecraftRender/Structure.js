import {THREE} from "./__init__.js"


const BlockTexturePath = new URL('./texture/blocks.png', import.meta.url).href
const BlockTexture = new THREE.TextureLoader().load(BlockTexturePath)
// 合并面用 fract 重复采样，格子边界处 uv 会跳变；
// 如果保留 mipmap，GPU 会在边界选到低层级，混入相邻图集的透明像素，
// 再被 alphaTest 丢掉，看起来就是每个方块之间有一条透明细线。
// 这里直接关掉 mipmap，保证每个格子只采样自己的 16x16 小图。
BlockTexture.minFilter = THREE.NearestFilter
BlockTexture.generateMipmaps = false
BlockTexture.magFilter = THREE.NearestFilter
const BlockMaterial = new THREE.MeshBasicMaterial({map:BlockTexture, transparent:true, alphaTest:0.6})

const PlantTexturePath = new URL('./texture/plants.png', import.meta.url).href
const PlantTexture = new THREE.TextureLoader().load(PlantTexturePath)
PlantTexture.minFilter = THREE.NearestMipmapNearestFilter
PlantTexture.magFilter = THREE.NearestFilter
const PlantMaterial = new THREE.MeshBasicMaterial({map:PlantTexture, transparent: true, side:THREE.DoubleSide, alphaTest:0.6})

const TransparentTexturePath = new URL('./texture/transparent.png', import.meta.url).href
const TransparentTexture = new THREE.TextureLoader().load(TransparentTexturePath)
// 透明合并面同样用 fract 重复采样，也需要关闭 mipmap，避免格子边界混入相邻透明图块。
TransparentTexture.minFilter = THREE.NearestFilter
TransparentTexture.generateMipmaps = false
TransparentTexture.magFilter = THREE.NearestFilter
const TransparentMaterial = new THREE.MeshBasicMaterial({map: TransparentTexture, transparent: true, depthWrite:false, depthTest: true})

/**
 * 让 single / transparent 材质支持合并面 UV。
 * 合并面把图集列号/行号写到 uv 整数部分，把 0..w/0..h 的局部坐标写到小数部分。
 * 这里用 floor/fract 解码，再用 fract(local) 在当前 16x16 小图内重复采样。
 */
const addMergedUvDecode = (material, atlasWidth, atlasHeight) => {
    material.onBeforeCompile = (shader) => {
        shader.uniforms.uAtlasSize = { value: new THREE.Vector2(atlasWidth, atlasHeight) }

        shader.vertexShader = `
attribute float aAO;
varying float vAO;
varying vec2 vMergedUv;
` + shader.vertexShader.replace(
            '#include <begin_vertex>',
            `#include <begin_vertex>
            vMergedUv = uv;
            vAO = aAO;`
        )

        shader.fragmentShader = `
uniform vec2 uAtlasSize;
varying float vAO;
varying vec2 vMergedUv;
` + shader.fragmentShader.replace(
            '#include <map_fragment>',
            `#ifdef USE_MAP
            vec2 atlasUv;
            if (vMergedUv.x > 2.0) {
                vec2 tile = floor(vMergedUv) - vec2(10.0);
                vec2 local = fract(vMergedUv) * 1024.0;
                vec2 tileLocal = fract(local);
                atlasUv = (tile * 16.0 + tileLocal * 16.0) / uAtlasSize;
            } else {
                atlasUv = vUv;
            }
            vec4 sampledDiffuseColor = texture2D( map, atlasUv );
            diffuseColor *= sampledDiffuseColor;
            diffuseColor.rgb *= vAO;
            #endif`
        )
    }
    material.customProgramCacheKey = () => `MergedUvDecode-${atlasWidth}x${atlasHeight}`
}

addMergedUvDecode(BlockMaterial, 256 * 16, 64 * 16)
addMergedUvDecode(TransparentMaterial, 256 * 16, 16 * 16)



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
        if (!this.isEnable) return null
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
        if (!this.isEnable) return null
        if (!this.isRender) return null
        if (this.singleMesh) scene.remove(this.singleMesh)
        if (this.doubleMesh) scene.remove(this.doubleMesh)
        if (this.transparentMesh) scene.remove(this.transparentMesh)
        this.isRender = false
    }

    /**
     * 为场景永久删除区块渲染
     * @param {THREE.Scene} scene - 场景对象
     */
    disableRender(scene) {
        if (!this.isEnable) return null
        this.removeRender(scene)
        if (this.singleMesh) this.singleMesh.geometry.dispose()
        if (this.doubleMesh) this.doubleMesh.geometry.dispose()
        if (this.transparentMesh) this.transparentMesh.geometry.dispose()
        this.isEnable = false
    }

}

class BlockIndexArray {

    /**
     * 创建一个数组索引对象
     * @param {Number} size - 包含了x,y,z大小的数组
     */
    constructor(size) {
        this.indexs = []
        this.data_length = 1024 * 1024 * 512
        const DataLength = this.data_length

        for (let i = 0; i < size; i += DataLength) {
            const ArraySize = Math.min(DataLength, size-i)
            this.indexs.push(new Uint16Array(ArraySize))
        }
    }

    get length() {
        let total = 0;
        for (const arr of this.indexs) total += arr.length;
        return total;
    }

    getIndex(index) {
        const remainder = index % this.data_length;
        const quotient = (index - remainder) / this.data_length;
        return this.indexs[quotient][remainder]
    }
    setIndex(index, value) {
        const remainder = index % this.data_length;
        const quotient = (index - remainder) / this.data_length;
        this.indexs[quotient][remainder] = value
    }
    batchUpdate(array, offset=0){
        const remainder = offset % this.data_length;
        const quotient = (offset - remainder) / this.data_length;
        this.indexs[quotient].set(array, remainder)
    }
    subarray(startIndex, endIndex){
        const remainder1 = startIndex % this.data_length;
        const quotient1 = (startIndex - remainder1) / this.data_length;
        const remainder2 = endIndex % this.data_length;
        const quotient2 = (endIndex - remainder2) / this.data_length;
        if (quotient1 === quotient2) {
            return this.indexs[quotient1].subarray(remainder1, remainder2)
        } else {
            const view1 = this.indexs[quotient1].subarray(remainder1, this.data_length)
            const view2 = this.indexs[quotient2].subarray(0, remainder2)
            const combined = new Uint16Array(view1.length + view2.length);
            combined.set(view1, 0);
            combined.set(view2, view1.length);
            return combined;
        }
    }
    /**
     * 用同一个值填充整个（或指定区间的）BlockIndexArray
     * 语义等价于 Uint16Array.prototype.fill，但跨所有分块。
     * @param {Number} value       填充值
     * @param {Number} [start=0]   起始索引（支持负数，从末尾数）
     * @param {Number} [end]       结束索引（不含，支持负数；默认到末尾）
     * @returns {BlockIndexArray}  this
     */
    fill(value, start = 0, end = undefined) {
        const total = this.length;
        if (end === undefined) end = total;

        // 归一化负索引 / 越界索引（和原生 fill 行为一致）
        start = start < 0 ? Math.max(0, total + start) : Math.min(start, total);
        end   = end   < 0 ? Math.max(0, total + end)   : Math.min(end,   total);

        if (start >= end) return this;   // 空区间，什么都不做

        // 逐分块填充，只处理与 [start, end) 有交集的分块
        let blockStart = 0;
        for (const arr of this.indexs) {
            const blockEnd = blockStart + arr.length;

            if (blockEnd <= start) {          // 这个分块完全在区间左边
                blockStart = blockEnd;
                continue;
            }
            if (blockStart >= end) break;     // 后面分块都在区间右边

            const localStart = Math.max(0, start - blockStart);
            const localEnd   = Math.min(arr.length, end - blockStart);
            arr.fill(value, localStart, localEnd);

            blockStart = blockEnd;
        }

        return this;
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
        /*** 方块映射数组，按x,y,z顺序排序 * @type {BlockIndexArray} */
        this.blockIndex = new BlockIndexArray(this.size[0] * this.size[1] * this.size[2])
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
    reset(size, blockPalette=null) {
        /*** 结构长宽高[x,y,z] * @type {Array<Number>} */
        this.size = size.map( (i) => Math.floor(i) )
        /*** 方块映射数组，按x,y,z顺序排序 * @type {BlockIndexArray} */
        this.blockIndex = new BlockIndexArray(this.size[0] * this.size[1] * this.size[2]) 
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
        return this.blockIndex.getIndex(voxelOffset)
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
                const block = this.blockPlatte[v0]
                if (block.__hash__ == v.__hash__) break
            }
            if (v0 >= this.blockPlatte.length) this.blockPlatte.push(v)
            this.blockIndex.setIndex(voxelOffset, v0)
        } else this.blockIndex.setIndex(voxelOffset, v)
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
        const BlockDict = this.blockPlatte[ this.blockIndex.getIndex(voxelOffset) ]
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
     * 获取渲染对象
     * @param {Number} startX - x坐标
     * @param {Number} startY - y坐标
     * @param {Number} startZ - z坐标
     */
    getRenderObject(startX, startY, startZ, 
        {single_positions, single_uvs, single_indices, single_ao,
        double_positions, double_uvs, double_indices,
        transparent_positions, transparent_uvs, transparent_indices, transparent_ao }){
        // 兼容旧版 Worker：没有 AO 时默认全 1.0
        if (!single_ao || single_ao.length !== single_positions.length / 3) {
            single_ao = new Float32Array(single_positions.length / 3).fill(1)
        }
        if (!transparent_ao || transparent_ao.length !== transparent_positions.length / 3) {
            transparent_ao = new Float32Array(transparent_positions.length / 3).fill(1)
        }
        const RenderObject = new ChunkRenderObject()
        RenderObject.origin[0] = startX
        RenderObject.origin[1] = startY
        RenderObject.origin[2] = startZ

        if (single_positions.length) {
            const geometry = new THREE.BufferGeometry()
            geometry.setAttribute( 'position', new THREE.BufferAttribute(single_positions, 3))
            geometry.setAttribute( 'uv', new THREE.BufferAttribute(single_uvs, 2))
            geometry.setAttribute( 'aAO', new THREE.BufferAttribute(single_ao, 1))
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
            geometry.setAttribute( 'aAO', new THREE.BufferAttribute(transparent_ao, 1))
            geometry.setIndex(new THREE.Uint32BufferAttribute(transparent_indices, 1))
            const MeshObject = new THREE.Mesh(geometry, TransparentMaterial)
            MeshObject.renderOrder = 1000
            MeshObject.position.set(startX, startY, startZ)
            RenderObject.transparentMesh = MeshObject
        }

        return RenderObject
    }

}


export {Block, AirBlock, ChunkRenderObject, Structure}

//
