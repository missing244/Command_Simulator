import {THREE} from "./__init__.js"


const BlockTexturePath = new URL('./texture/blocks.png', import.meta.url).href
const BlockTexture = new THREE.TextureLoader().load(BlockTexturePath)
BlockTexture.minFilter = THREE.NearestMipmapNearestFilter
BlockTexture.magFilter = THREE.NearestFilter
const BlockMaterial = new THREE.MeshBasicMaterial({map:BlockTexture, transparent:true, alphaTest:0.6})

const PlantTexturePath = new URL('./texture/plants.png', import.meta.url).href
const PlantTexture = new THREE.TextureLoader().load(PlantTexturePath)
PlantTexture.minFilter = THREE.NearestMipmapNearestFilter
PlantTexture.magFilter = THREE.NearestFilter
const PlantMaterial = new THREE.MeshBasicMaterial({map:PlantTexture, transparent: true, side:THREE.DoubleSide, alphaTest:0.6})

const TransparentTexturePath = new URL('./texture/transparent.png', import.meta.url).href
const TransparentTexture = new THREE.TextureLoader().load(TransparentTexturePath)
TransparentTexture.minFilter = THREE.NearestMipmapNearestFilter
TransparentTexture.magFilter = THREE.NearestFilter
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

}


export {Block, ChunkRenderObject, Structure}

//
