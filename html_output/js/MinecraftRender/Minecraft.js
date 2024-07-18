import * as THREE from "../three.module.js";

function print(obj) {console.log(obj)}

const Block_Texture = new THREE.TextureLoader().load("picture/block_texture.png");
Block_Texture.magFilter = THREE.NearestFilter; Block_Texture.minFilter = THREE.NearestFilter;
const Block_Material = new THREE.MeshBasicMaterial({map: Block_Texture, transparent: true});

const ModelType = {
  "same_4": [ //4面相同
    { // left
      uvRow: 0, dir:[-1, 0, 0], render:false,
      corners: [
        { pos:[0, 1, 0], uv:[0, 1] }, { pos:[0, 0, 0], uv:[0, 0] },
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[0, 0, 1], uv:[1, 0] }
      ]
    },
    { // right
      uvRow: 0, dir:[1, 0, 0], render:false,
      corners: [
        { pos:[1, 1, 1], uv:[0, 1] }, { pos:[1, 0, 1], uv:[0, 0] },
        { pos:[1, 1, 0], uv:[1, 1] }, { pos:[1, 0, 0], uv:[1, 0] },
      ]
    },
    { // top
      uvRow: 1, dir:[0, 1, 0], render:false,
      corners: [
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[1, 1, 1], uv:[0, 1] },
        { pos:[0, 1, 0], uv:[1, 0] }, { pos:[1, 1, 0], uv:[0, 0] },
      ]
    },
    { // bottom
      uvRow: 2, dir:[0, -1, 0], render:false,
      corners: [
        { pos:[1, 0, 1], uv:[1, 0] }, { pos:[0, 0, 1], uv:[0, 0] },
        { pos:[1, 0, 0], uv:[1, 1] }, { pos:[0, 0, 0], uv:[0, 1] },
      ]
    },
    { // back
      uvRow: 0, dir:[0, 0, -1], render:false,
      corners: [
        { pos:[1, 0, 0], uv:[0, 0], }, { pos:[0, 0, 0], uv:[1, 0] },
        { pos:[1, 1, 0], uv:[0, 1], }, { pos:[0, 1, 0], uv:[1, 1] },
      ]
    },
    { // front
      uvRow: 0, dir: [0, 0, 1], render:false,
      corners: [
        { pos:[0, 0, 1], uv:[0, 0], }, { pos:[1, 0, 1], uv:[1, 0] },
        { pos:[0, 1, 1], uv:[0, 1], }, { pos:[1, 1, 1], uv:[1, 1] },
      ]
    }
  ],
  "same_4-2": [ //4-2面相同
    { // left
      uvRow: 0, dir:[-1, 0, 0], render:false,
      corners: [
        { pos:[0, 1, 0], uv:[0, 1] }, { pos:[0, 0, 0], uv:[0, 0] },
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[0, 0, 1], uv:[1, 0] }
      ]
    },
    { // right
      uvRow: 0, dir:[1, 0, 0], render:false,
      corners: [
        { pos:[1, 1, 1], uv:[0, 1] }, { pos:[1, 0, 1], uv:[0, 0] },
        { pos:[1, 1, 0], uv:[1, 1] }, { pos:[1, 0, 0], uv:[1, 0] },
      ]
    },
    { // top
      uvRow: 1, dir:[0, 1, 0], render:false,
      corners: [
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[1, 1, 1], uv:[0, 1] },
        { pos:[0, 1, 0], uv:[1, 0] }, { pos:[1, 1, 0], uv:[0, 0] },
      ]
    },
    { // bottom
      uvRow: 1, dir:[0, -1, 0], render:false,
      corners: [
        { pos:[1, 0, 1], uv:[1, 0] }, { pos:[0, 0, 1], uv:[0, 0] },
        { pos:[1, 0, 0], uv:[1, 1] }, { pos:[0, 0, 0], uv:[0, 1] },
      ]
    },
    { // back
      uvRow: 0, dir:[0, 0, -1], render:false,
      corners: [
        { pos:[1, 0, 0], uv:[0, 0], }, { pos:[0, 0, 0], uv:[1, 0] },
        { pos:[1, 1, 0], uv:[0, 1], }, { pos:[0, 1, 0], uv:[1, 1] },
      ]
    },
    { // front
      uvRow: 0, dir: [0, 0, 1], render:false,
      corners: [
        { pos:[0, 0, 1], uv:[0, 0], }, { pos:[1, 0, 1], uv:[1, 0] },
        { pos:[0, 1, 1], uv:[0, 1], }, { pos:[1, 1, 1], uv:[1, 1] },
      ]
    }
  ],
  "same_6": [ //4面相同
    { // left
      uvRow: 0, dir:[-1, 0, 0], render:false,
      corners: [
        { pos:[0, 1, 0], uv:[0, 1] }, { pos:[0, 0, 0], uv:[0, 0] },
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[0, 0, 1], uv:[1, 0] }
      ]
    },
    { // right
      uvRow: 0, dir:[1, 0, 0], render:false,
      corners: [
        { pos:[1, 1, 1], uv:[0, 1] }, { pos:[1, 0, 1], uv:[0, 0] },
        { pos:[1, 1, 0], uv:[1, 1] }, { pos:[1, 0, 0], uv:[1, 0] },
      ]
    },
    { // top
      uvRow: 0, dir:[0, 1, 0], render:false,
      corners: [
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[1, 1, 1], uv:[0, 1] },
        { pos:[0, 1, 0], uv:[1, 0] }, { pos:[1, 1, 0], uv:[0, 0] },
      ]
    },
    { // bottom
      uvRow: 0, dir:[0, -1, 0], render:false,
      corners: [
        { pos:[1, 0, 1], uv:[1, 0] }, { pos:[0, 0, 1], uv:[0, 0] },
        { pos:[1, 0, 0], uv:[1, 1] }, { pos:[0, 0, 0], uv:[0, 1] },
      ]
    },
    { // back
      uvRow: 0, dir:[0, 0, -1], render:false,
      corners: [
        { pos:[1, 0, 0], uv:[0, 0], }, { pos:[0, 0, 0], uv:[1, 0] },
        { pos:[1, 1, 0], uv:[0, 1], }, { pos:[0, 1, 0], uv:[1, 1] },
      ]
    },
    { // front
      uvRow: 0, dir: [0, 0, 1], render:false,
      corners: [
        { pos:[0, 0, 1], uv:[0, 0], }, { pos:[1, 0, 1], uv:[1, 0] },
        { pos:[0, 1, 1], uv:[0, 1], }, { pos:[1, 1, 1], uv:[1, 1] },
      ]
    }
  ],
  "same_1": [ //4面相同
    { // left
      uvRow: 0, dir:[-1, 0, 0], render:false,
      corners: [
        { pos:[0, 1, 0], uv:[0, 1] }, { pos:[0, 0, 0], uv:[0, 0] },
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[0, 0, 1], uv:[1, 0] }
      ]
    },
    { // right
      uvRow: 1, dir:[1, 0, 0], render:false,
      corners: [
        { pos:[1, 1, 1], uv:[0, 1] }, { pos:[1, 0, 1], uv:[0, 0] },
        { pos:[1, 1, 0], uv:[1, 1] }, { pos:[1, 0, 0], uv:[1, 0] },
      ]
    },
    { // top
      uvRow: 2, dir:[0, 1, 0], render:false,
      corners: [
        { pos:[0, 1, 1], uv:[1, 1] }, { pos:[1, 1, 1], uv:[0, 1] },
        { pos:[0, 1, 0], uv:[1, 0] }, { pos:[1, 1, 0], uv:[0, 0] },
      ]
    },
    { // bottom
      uvRow: 3, dir:[0, -1, 0], render:false,
      corners: [
        { pos:[1, 0, 1], uv:[1, 0] }, { pos:[0, 0, 1], uv:[0, 0] },
        { pos:[1, 0, 0], uv:[1, 1] }, { pos:[0, 0, 0], uv:[0, 1] },
      ]
    },
    { // back
      uvRow: 4, dir:[0, 0, -1], render:false,
      corners: [
        { pos:[1, 0, 0], uv:[0, 0], }, { pos:[0, 0, 0], uv:[1, 0] },
        { pos:[1, 1, 0], uv:[0, 1], }, { pos:[0, 1, 0], uv:[1, 1] },
      ]
    },
    { // front
      uvRow: 5, dir: [0, 0, 1], render:false,
      corners: [
        { pos:[0, 0, 1], uv:[0, 0], }, { pos:[1, 0, 1], uv:[1, 0] },
        { pos:[0, 1, 1], uv:[0, 1], }, { pos:[1, 1, 1], uv:[1, 1] },
      ]
    }
  ]
}
const BlocksDefinition = {
  "minecraft:stone": {"transmite":false, "index": 0, "model":"same_6"}
}
const BlockIDTransfor = {}

function QueryBlockRender(Blcok) {

}





export class VoxelWorld {

  constructor( options ) {
    this.cellSizeX = options.cellSizeX;
    this.cellSizeY = options.cellSizeY;
    this.cellSizeZ = options.cellSizeZ;
    this.tileSize = options.tileSize;
    this.tileTextureWidth = options.tileTextureWidth;
    this.tileTextureHeight = options.tileTextureHeight;
    this.cellSliceSize = this.cellSizeX * this.cellSizeZ;
    this.cell = new Uint16Array(this.cellSizeX * this.cellSizeY * this.cellSizeZ)
    this.blockmap = options.blockmap
  }

  computeVoxelOffset( x, y, z ) {
    return y * this.cellSliceSize + z * this.cellSizeX + x
  }

  setVoxel( x, y, z, v ) {
    const voxelOffset = this.computeVoxelOffset( x, y, z )
    this.cell[voxelOffset] = v
  }

  getVoxel( x, y, z ) {
    const voxelOffset = this.computeVoxelOffset( x, y, z )
    return this.cell[voxelOffset];
  }

  generateGeometryDataForCell() {
    const { tileSize, tileTextureWidth, tileTextureHeight } = this
    const positions = []; const normals = []; const uvs = []; const indices = []

    for ( let y = 0; y < this.cellSizeY; ++y ) {
      for ( let z = 0; z < this.cellSizeZ; ++z ) {
        for ( let x = 0; x < this.cellSizeX; ++x ) {
          const blockindex = this.getVoxel(x, y, z)
          if (!blockindex) continue

          // voxel 0 is sky (empty) so for UVs we start at 0
          const render_data = QueryBlockRender()
          const uvVoxel = render_data["index"]

          for ( const {dir, corners, uvRow} of uv_data ) {
              const neighbor = this.getVoxel(x + dir[0], x + dir[1], x + dir[2]);
              if ( !neighbor ) {
                const ndx = Math.floor(positions.length / 3)
                for ( const { pos, uv } of corners ) {
                  positions.push( pos[0]+x, pos[1]+y, pos[2]+z )
                  normals.push( ...dir )
                  uvs.push(
                    (uvVoxel + uv[0]) * tileSize / tileTextureWidth,
                    1 - (uvRow + 1 - uv[1]) * tileSize / tileTextureHeight )
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
              }
          }
        }
      }
    }
    return {positions, normals, uvs, indices};
  }
}


export function Generate_Chunk(world){
  const { positions, normals, uvs, indices } = world.generateGeometryDataForCell( 0, 0, 0 );
  const geometry = new THREE.BufferGeometry();
  
  geometry.setAttribute( 'position', new THREE.BufferAttribute(new Float32Array(positions), 3));
  geometry.setAttribute( 'normal', new THREE.BufferAttribute(new Float32Array(normals), 4));
  geometry.setAttribute( 'uv', new THREE.BufferAttribute(new Float32Array(uvs), 2));
  geometry.setIndex(indices);
  const mesh = new THREE.Mesh(geometry, Block_Material);
  return mesh;
}



