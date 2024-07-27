import * as THREE from "../three.module.js";
import * as BlockDefine from "./block_define.js"
import * as RenderSetting from "./render_setting.js"

const AirDict = {id: "minecraft:air", "state": {}}
export function print(obj) {console.log(obj)}

const Block_Texture = new THREE.TextureLoader().load("picture/render/blocks.png");
Block_Texture.magFilter = THREE.NearestFilter; Block_Texture.minFilter = THREE.NearestFilter;
const Block_Material = new THREE.MeshBasicMaterial({map: Block_Texture, transparent: true});

const Plant_Texture = new THREE.TextureLoader().load("picture/render/plants.png");
Plant_Texture.magFilter = THREE.NearestFilter; Plant_Texture.minFilter = THREE.NearestFilter;
const Plant_Material = new THREE.MeshBasicMaterial({map: Plant_Texture, transparent: true, side:THREE.DoubleSide});


export class BlockChunk {

  constructor( options ) {
    this.cellSizeX = options.cellSizeX;
    this.cellSizeY = options.cellSizeY;
    this.cellSizeZ = options.cellSizeZ;
    this.cellSliceSize = this.cellSizeY * this.cellSizeZ;

    this.TextureWidth = options.TextureWidth;
    this.TextureHeight = options.TextureHeight;
    this.tileSize = options.tileSize;

    this.cell = new Uint16Array(this.cellSizeX * this.cellSizeY * this.cellSizeZ)
    this.blockMap = options.blockMap
  }

  computeVoxelOffset( x, y, z ) {
    return x * this.cellSliceSize + y * this.cellSizeZ + z
  }
  setVoxel( x, y, z, v ) {
    const voxelOffset = this.computeVoxelOffset( x, y, z )
    this.cell[voxelOffset] = v
  }
  getVoxel( x, y, z ) {
    if (x < 0 || x >= this.cellSizeX) return AirDict
    if (y < 0 || y >= this.cellSizeY) return AirDict
    if (z < 0 || z >= this.cellSizeZ) return AirDict
    const voxelOffset = this.computeVoxelOffset( x, y, z )
    const BlockDict = this.blockMap[ this.cell[voxelOffset] ]
    return BlockDict
  }

  generateGeometryDataForCell() {
    const { tileSize, TextureWidth, TextureHeight } = this
    const positions = []; const normals = []; const uvs = []; const indices = []

    for ( let x = 0; x < this.cellSizeY; ++x ) {
      for ( let y = 0; y < this.cellSizeZ; ++y ) {
        for ( let z = 0; z < this.cellSizeX; ++z ) {
          const Block = this.getVoxel(x, y, z)
          if (Block.id === "minecraft:air") continue

          const BlockRenderData = BlockDefine.QueryBlockRender(Block)
          const uvOrignX = BlockRenderData["index"] * tileSize
          const uvOrignY = 0

          for (const face_name in RenderSetting.ModelDefine[BlockRenderData.model]) {
            const uvMode = RenderSetting.ModelDefine[BlockRenderData.model][face_name]
            let uvPosX = uvOrignX ; let uvPosY = uvOrignY
            if (uvMode instanceof Array) {uvPosX += uvMode[0] ; uvPosY += uvMode[1]}
            else {uvPosY = uvMode * tileSize}

            const {dir, corners} = RenderSetting.FaceDefine[face_name]
            const NeighborBlock = this.getVoxel(x+dir[0], y+dir[1], z+dir[2])
            if ( !(NeighborBlock.id === "minecraft:air" || BlockDefine.QueryBlockRender(NeighborBlock)
              .transmitting)) continue

            const ndx = Math.floor(positions.length / 3)
            for ( const { pos, uv } of corners ) {
              positions.push( pos[0]+x, pos[1]+y, pos[2]+z )
              normals.push( ...dir )
              uvs.push( (uvPosX+uv[0])/TextureWidth, (uvPosY+uv[1])/TextureHeight )
            }
            indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
          }
        }
      }
    }
    print(positions);
    print(normals);
    print(uvs);
    print(indices);
    return {positions, normals, uvs, indices};
  }

  generateMesh(){
    const { positions, normals, uvs, indices } = this.generateGeometryDataForCell();
    const geometry = new THREE.BufferGeometry();
    
    geometry.setAttribute( 'position', new THREE.BufferAttribute(new Float32Array(positions), 3));
    geometry.setAttribute( 'normal', new THREE.BufferAttribute(new Float32Array(normals), 3));
    geometry.setAttribute( 'uv', new THREE.BufferAttribute(new Float32Array(uvs), 2));
    geometry.setIndex(indices);
    const mesh = new THREE.Mesh(geometry, Block_Material);
    return mesh;
  }
}


