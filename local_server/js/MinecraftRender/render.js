import * as THREE from "../three.module.js"
import * as RenderSetting from "./render_setting.js"
import * as BlockDefine from "./block_define.js"

const WaterTest = {"minecraft:water":null, "minecraft:flowing_water":null}
const LavaTest = {"minecraft:lava":null, "minecraft:flowing_water":null}
const CopperGrateTest = {
  "minecraft:copper_grate":null, "minecraft:exposed_copper_grate":null, 
  "minecraft:exposed_copper_grate":null, "minecraft:oxidized_copper_grate":null, 
  "minecraft:waxed_copper_grate":null, "minecraft:waxed_exposed_copper_grate":null, 
  "minecraft:waxed_exposed_copper_grate":null, "minecraft:waxed_oxidized_copper_grate":null}
const AirTypeTest = new Set(["minecraft:air", "minecraft:light_block_0", "minecraft:light_block_1",
  "minecraft:light_block_2", "minecraft:light_block_3", "minecraft:light_block_4", "minecraft:light_block_5",
  "minecraft:light_block_6", "minecraft:light_block_7", "minecraft:light_block_8", "minecraft:light_block_9",
  "minecraft:light_block_10", "minecraft:light_block_11", "minecraft:light_block_12", "minecraft:light_block_13",
  "minecraft:light_block_14", "minecraft:light_block_15"])
const AirDict = {name: "minecraft:air", states: {}}
const ConnectTest = [
  {direction:[0, 0, -1], axes:[0, 1, 0], angle:0, name:"north"}, 
  {direction:[0, 0, 1], axes:[0, 1, 0], angle:Math.PI, name:"south"}, 
  {direction:[-1, 0, 0], axes:[0, 1, 0], angle:Math.PI/2, name:"west"}, 
  {direction:[1, 0, 0], axes:[0, 1, 0], angle:-Math.PI/2, name:"east"}, 
  {direction:[0, -1, 0], axes:[1, 0, 0], angle:-Math.PI/2, name:"top"}, 
  {direction:[0, 1, 0], axes:[1, 0, 0], angle:Math.PI/2, name:"bottom"}]
export function print(obj) {console.log(obj)}

const Block_Texture = new THREE.TextureLoader().load("picture/render/blocks.png");
Block_Texture.magFilter = THREE.NearestFilter
Block_Texture.minFilter = THREE.NearestFilter
const Block_Material = new THREE.MeshBasicMaterial({map: Block_Texture, transparent: true, alphaTest: 0.1})

const Plant_Texture = new THREE.TextureLoader().load("picture/render/double_side.png");
Plant_Texture.magFilter = THREE.NearestFilter
Plant_Texture.minFilter = THREE.NearestFilter
const Plant_Material = new THREE.MeshBasicMaterial({map: Plant_Texture, transparent: true, side:THREE.DoubleSide, alphaTest: 0.1});

const Transparent_Texture = new THREE.TextureLoader().load("picture/render/transparent.png");
Transparent_Texture.magFilter = THREE.NearestFilter
Transparent_Texture.minFilter = THREE.NearestFilter
const Transparent_Material = new THREE.MeshBasicMaterial({map: Transparent_Texture, transparent: true, depthWrite: false});



class State {
  constructor(){
    this.facing_direction1_test = new RegExp("(button|amethyst_bud|amethyst_cluster)$", "m")
    this.facing_direction3_test = new RegExp("(hopper)$", "m")
    this.stairs_test = new RegExp("stairs$", "m")
    this.trapdoor_test = new RegExp("trapdoor$", "m")
    this.glazed_terracotta_test = new RegExp("glazed_terracotta$", "m")
    this.functional_rail_test = new RegExp("(activator_rail|detector_rail|golden_rail)$", "m")

    this.FacingDirection_1 = {
      0: [{rotate_axis:[1,0,0], angle:0}], 1: [{rotate_axis:[1,0,0], angle:Math.PI}], 
      2: [{rotate_axis:[1,0,0], angle:Math.PI/2}], 3: [{rotate_axis:[1,0,0], angle:-Math.PI/2}], 
      4: [{rotate_axis:[0,1,0], angle:Math.PI/2}, {rotate_axis:[0,0,1], angle:-Math.PI/2}], 
      5: [{rotate_axis:[0,1,0], angle:Math.PI/2}, {rotate_axis:[0,0,1], angle:Math.PI/2}]
    }
    this.FacingDirection_2 = {
      0: {rotate_axis:[0,-1,0], angle:0}, 1: {rotate_axis:[0,-1,0], angle:0}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI}, 3: {rotate_axis:[0,-1,0], angle:0},
      4: {rotate_axis:[0,-1,0], angle:Math.PI/2}, 5: {rotate_axis:[0,-1,0], angle:-Math.PI/2},
    }
    this.Direction_1 = {
      0: {rotate_axis:[0,-1,0], angle:0}, 1: {rotate_axis:[0,-1,0], angle:Math.PI/2}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI}, 3: {rotate_axis:[0,-1,0], angle:3*Math.PI/2},
    }
    this.Direction_2 = {
      0: {rotate_axis:[0,-1,0], angle:0}, 1: {rotate_axis:[0,-1,0], angle:Math.PI}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI/2}, 3: {rotate_axis:[0,-1,0], angle:-Math.PI/2},
    }
    this.WeirdoDirection = {
      0: {rotate_axis:[0,-1,0], angle:0, facing:[-1,0,0]}, 1: {rotate_axis:[0,-1,0], angle:Math.PI, facing:[1,0,0]}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI/2, facing:[0,0,-1]}, 3: {rotate_axis:[0,-1,0], angle:-Math.PI/2, facing:[0,0,1]},
    }
    this.BlockFace = {down: 0, up: 1, north: 2, south: 3, west: 4, east: 5}
    this.CardinalDirection = {north: 0, east: 1, south: 2, west: 3}
    this.PillarAxis = {
      x:{rotate_axis:[0,0,-1], angle:Math.PI/2}, y:{rotate_axis:[0,-1,0], angle:0}, 
      z:{rotate_axis:[1,0,0], angle:Math.PI/2}}
    this.Orientation = {
      down_east:{rotate_axis:[0,0,-1], angle:Math.PI/2},
      down_north:{rotate_axis:[0,0,-1], angle:Math.PI/2},
      down_south:{rotate_axis:[0,0,-1], angle:Math.PI/2},
      down_west:{rotate_axis:[0,0,-1], angle:Math.PI/2},
      up_east:{rotate_axis:[0,0,-1], angle:-Math.PI/2},
      up_north:{rotate_axis:[0,0,-1], angle:-Math.PI/2},
      up_south:{rotate_axis:[0,0,-1], angle:-Math.PI/2},
      up_west:{rotate_axis:[0,0,-1], angle:-Math.PI/2},
      east_up:{rotate_axis:[0,-1,0], angle:Math.PI/2},
      north_up:{rotate_axis:[0,-1,0], angle:0},
      south_up:{rotate_axis:[0,-1,0], angle:-Math.PI},
      west_up:{rotate_axis:[0,-1,0], angle:Math.PI/2}
    }
  }


  __State_Pos_Transfor__(Block, pos) {
    if (!Object.keys(Block.states).length) return pos

    let new_pos = pos
    if (this.stairs_test.test(Block.name)) {
      new_pos = this.BlockState_For_Stairs(new_pos, Block.states) ; return new_pos }
    else if (this.functional_rail_test.test(Block.name) && "rail_direction" in Block.states) {
      new_pos = this.BlockState_For_FunctionalRail(new_pos, Block.states["rail_direction"]) ; return new_pos }
    else if (this.facing_direction1_test.test(Block.name) && "facing_direction" in Block.states) {
      new_pos = this.BlockState_FacingDirection_1(new_pos, Block.states["facing_direction"]) ; return new_pos }
    else if (this.facing_direction3_test.test(Block.name) && "facing_direction" in Block.states) {
      new_pos = this.BlockState_FacingDirection_3(new_pos, Block.states["facing_direction"]) ; return new_pos }
    else if (this.trapdoor_test.test(Block.name) && "direction" in Block.states) {
      new_pos = this.BlockState_Direction_2(new_pos, Block.states["direction"]) ; return new_pos }

    if ("facing_direction" in Block.states) 
      new_pos = this.BlockState_FacingDirection_2(new_pos, Block.states["facing_direction"])
    if ("direction" in Block.states || "coral_direction" in Block.states) 
      new_pos = this.BlockState_Direction_1(new_pos, Block.states["direction"])
    if ("minecraft:vertical_half" in Block.states) 
      new_pos = this.BlockState_VerticalHalf(new_pos, Block.states["minecraft:vertical_half"])
    if ("ground_sign_direction" in Block.states)
      new_pos = this.BlockState_GroundSignDirection(new_pos, Block.states["ground_sign_direction"])
    if ("upside_down_bit" in Block.states)
      new_pos = this.BlockState_UpsideDownBit(new_pos, Block.states["upside_down_bit"])
    if ("minecraft:block_face" in Block.states)
      new_pos = this.BlockState_BlockFace(new_pos, Block.states["minecraft:block_face"])
    if ("minecraft:cardinal_direction" in Block.states)
      new_pos = this.BlockState_CardinalDirection(new_pos, Block.states["minecraft:cardinal_direction"])
    if ("pillar_axis" in Block.states)
      new_pos = this.BlockState_PillarAxis(new_pos, Block.states["pillar_axis"])
    if ("orientation" in Block.states)
      new_pos = this.BlockState_Orientation(new_pos, Block.states["orientation"])


    return new_pos
  }
  __State_Disable_Rerden__(Block, direction) {
    if ("multi_face_direction_bits" in Block.states) 
      return this.BlockState_MultiFaceDirectionBits(direction, Block.states["multi_face_direction_bits"])
    else return true
  }


  __Rodrigues_rotate__(pos, rotate_axis, angle) {
    if (angle === 0) return pos

    const c1 = Math.cos(angle) ; const c2 = Math.sin(angle)
    const c3 = (1 - c1) * (pos[0]*rotate_axis[0] + pos[1]*rotate_axis[1] + pos[2]*rotate_axis[2])
    const cross = [ 
      rotate_axis[1] * pos[2] - rotate_axis[2] * pos[1],
      rotate_axis[2] * pos[0] - rotate_axis[0] * pos[2],
      rotate_axis[0] * pos[1] - rotate_axis[1] * pos[0]]

    return [ 
      c1*pos[0] + c3*rotate_axis[0] + c2*cross[0], 
      c1*pos[1] + c3*rotate_axis[1] + c2*cross[1], 
      c1*pos[2] + c3*rotate_axis[2] + c2*cross[2] ]
  }


  BlockState_CardinalDirection(pos, State){
    return this.BlockState_Direction_1(pos, this.CardinalDirection[State])
  }
  BlockState_BlockFace(pos, State){
    return this.BlockState_FacingDirection_1(pos, this.BlockFace[State])
  }
  BlockState_FacingDirection_1(pos, State) {
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    const FacingRotate = this.FacingDirection_1[State]
    FacingRotate.forEach(element => {
      result = this.__Rodrigues_rotate__(result, element.rotate_axis, element.angle)
    })
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }
  BlockState_FacingDirection_2(pos, State) {
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    const FacingRotate = this.FacingDirection_2[State]
    result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }
  BlockState_FacingDirection_3(pos, State) {
    if (pos[0] != 0.375 && pos[0] != 0.625) return pos
    if (State == 1) State = 0

    let result = [pos[0] - 0.5, pos[1] - 0.375, pos[2] - 0.5]
    const FacingRotate = this.FacingDirection_1[State]
    FacingRotate.forEach(element => {
      result = this.__Rodrigues_rotate__(result, element.rotate_axis, element.angle)
    })
    result[0] += 0.5 ; result[1] += 0.375 ; result[2] += 0.5

    if (State > 0) {
      let dir = [0, -2/16, 0]
      FacingRotate.forEach(element => {
        dir = this.__Rodrigues_rotate__(dir, element.rotate_axis, element.angle)
      })
      result[0] += dir[0] ; result[1] += dir[1] ; result[2] += dir[2]
    }
    return result
  }
  BlockState_Direction_1(pos, State) {
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    const FacingRotate = this.Direction_1[State]
    result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }
  BlockState_Direction_2(pos, State) {
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    const FacingRotate = this.Direction_2[State]
    result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }
  BlockState_VerticalHalf(pos, State) {
    if (State === "top" || State === true) return [pos[0], pos[1]+0.5, pos[2]]
    else return pos
  }
  BlockState_For_Stairs(pos, StateDict) {
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    const Rotate = this.WeirdoDirection[ StateDict["weirdo_direction"] ]
    result = this.__Rodrigues_rotate__(result, Rotate.rotate_axis, Rotate.angle)
    if (StateDict["upside_down_bit"]) result = this.__Rodrigues_rotate__(result, Rotate.facing, Math.PI)
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }
  BlockState_GroundSignDirection(pos, State) {
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    result = this.__Rodrigues_rotate__(result, [0,-1,0], State*Math.PI/8)
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }
  BlockState_UpsideDownBit(pos, State){
    if (State) return [pos[0], pos[1]+13/16, pos[2]]
    else return pos
  }
  BlockState_For_FunctionalRail(pos, State){
    let new_pos = [pos[0], pos[1], pos[2]]
    let angle = 0

    if (State === 1) angle = Math.PI/2
    else if (State > 1) {
      if (!new_pos[2]) new_pos[1] = 1
      if (State === 2) angle = Math.PI/2
      else if (State === 3) angle = -Math.PI/2
      else if (State === 5) angle = Math.PI
    }

    new_pos[0] -= 0.5 ; new_pos[1] -= 0.5 ; new_pos[2] -= 0.5
    new_pos = this.__Rodrigues_rotate__(new_pos, [0,-1,0], angle)
    new_pos[0] += 0.5 ; new_pos[1] += 0.5 ; new_pos[2] += 0.5

    return new_pos
  }
  BlockState_PillarAxis(pos, State){
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    const FacingRotate = this.PillarAxis[State]
    result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }
  BlockState_Orientation(pos, State){
    let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
    const FacingRotate = this.Orientation[State]
    result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
    result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
    return result
  }

  BlockState_MultiFaceDirectionBits(direction, State){
    State = State ? State : 63
    if (direction[1] < 0 && (State & 0b000001)) return true 
    else if (direction[1] > 0 && (State & 0b000010)) return true 
    else if (direction[2] < 0 && (State & 0b000100)) return true 
    else if (direction[2] > 0 && (State & 0b001000)) return true 
    else if (direction[0] < 0 && (State & 0b010000)) return true 
    else if (direction[0] > 0 && (State & 0b100000)) return true 
    else return false
  }
}
const BlockStateOperation = new State()


export class BlockChunk {

  constructor( options ) {
    this.cellSizeX = options.cellSizeX;
    this.cellSizeY = options.cellSizeY;
    this.cellSizeZ = options.cellSizeZ;
    this.cellSliceSize = this.cellSizeY * this.cellSizeZ;

    this.SingleTextureWidth = 200*16;
    this.SingleTextureHeight = 50*16;
    this.DoubleTextureWidth = 200*16;
    this.DoubleTextureHeight = 16*16;
    this.TransparentTextureWidth = 50*16;
    this.TransparentTextureHeight = 6*16;
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


  __renderConnent__(x, y, z, Block, BlockRenderData, positions, uvs, indices, TextureWidth, TextureHeight){
    const { tileSize } = this

    //生成连接处
    if ( !BlockRenderData.connect ) return null
    ConnectTest.forEach((element) => {
      const {direction, axes, angle, name} = element
      const NeighborBlock = this.getVoxel(x+direction[0], y+direction[1], z+direction[2])
      if ( AirTypeTest.has(NeighborBlock.name) ) return null
      const NeighborBlockData = BlockDefine.QueryBlockRender(NeighborBlock)
      const ConnectInfo = RenderSetting.ConnectionDefine[BlockRenderData.connect]
      if (ConnectInfo.id_test instanceof Set && !ConnectInfo.id_test.has(NeighborBlock.name)) return null
      if (ConnectInfo.id_test instanceof RegExp && !ConnectInfo.id_test.test(NeighborBlock.name) && 
      (NeighborBlockData.flawed || BlockRenderData.fluid)) return null

      let ConnectModelName = undefined
      if (ConnectInfo.custom) ConnectModelName = ConnectInfo[name]
      else ConnectModelName = ConnectInfo.model
      if (!ConnectModelName) return null

      if (!ConnectInfo.up_down && direction[1] !== 0) return null
      for (const face_name in RenderSetting.ModelDefine[ConnectModelName]) {
        const uvMode = RenderSetting.ModelDefine[ConnectModelName][face_name]
        const uvPosX = (BlockRenderData["index"] % 200) * tileSize
        const uvPosY = Math.floor(BlockRenderData["index"] / 200) * 160 + uvMode * tileSize

        //生成模型部分
        const {corners} = RenderSetting.FaceDefine[face_name]
        const ndx = Math.floor(positions.length / 3)
        for ( const { pos, uv } of corners ) {
          let New_Pos = [pos[0]-0.5, pos[1]-0.5, pos[2]-0.5]
          if (!ConnectInfo.custom) New_Pos = BlockStateOperation.__Rodrigues_rotate__(New_Pos, axes, angle)
          for (let i = 0; i < 3; i++) New_Pos[i] += 0.5

          positions.push( New_Pos[0]+x, New_Pos[1]+y, New_Pos[2]+z )
          uvs.push( (uvPosX+uv[0])/TextureWidth, (uvPosY+uv[1])/TextureHeight )
        }
      indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
      }
    })
  }


  renderFluid(x, y, z, BlockID, positions, uvs, indices){
    const { tileSize, TransparentTextureWidth, TransparentTextureHeight} = this
    const FluidRenderData = RenderSetting.BlockDefine[BlockID]
    const UpBlock = this.getVoxel(x, y+1, z)
    const UPBlockData = BlockDefine.QueryBlockRender(UpBlock)
    const UpBlockIsNotFluid = AirTypeTest.has(UpBlock.name) || !(UpBlock.name === BlockID || UPBlockData.water_log)

    //遍历需要渲染的每一个面
    for (const face_name in RenderSetting.ModelDefine[FluidRenderData.model]) {
      const uvMode = RenderSetting.ModelDefine[FluidRenderData.model][face_name]
      const uvPosX = (FluidRenderData["index"] % 200) * tileSize
      const uvPosY = Math.floor(FluidRenderData["index"] / 200) * 160 + tileSize * uvMode

      const {dir, corners} = RenderSetting.FaceDefine[face_name]
      const NeighborBlock = this.getVoxel(x+dir[0], y+dir[1], z+dir[2])
      const NeighborBlockData = BlockDefine.QueryBlockRender(NeighborBlock)

      if (!(AirTypeTest.has(NeighborBlock.name) || 
        (!(BlockID.name in CopperGrateTest) && NeighborBlock.name in CopperGrateTest) ||
        (!NeighborBlockData.flawed && NeighborBlockData.transparent) || 
        (NeighborBlockData.flawed && !NeighborBlockData.water_log) || 
        (UpBlockIsNotFluid && dir[1] > 0)) ) continue

      //生成模型部分
      const ndx = Math.floor(positions.length / 3)
      for ( const { pos, uv } of corners ) {
        positions.push( pos[0]+x, pos[1]+y+((!UpBlockIsNotFluid && pos[1]>0) ? 0.125 : 0) , pos[2]+z )
        uvs.push( (uvPosX+uv[0])/TransparentTextureWidth, (uvPosY+uv[1])/TransparentTextureHeight )
      }
      indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
    }
  }
  renderTransparentBlock(x, y, z, Block, BlockRenderData, positions, uvs, indices){
    const { tileSize, TransparentTextureWidth, TransparentTextureHeight} = this

    //遍历需要渲染的每一个面
    for (const face_name in RenderSetting.ModelDefine[BlockRenderData.model]) {
      const {dir, corners} = RenderSetting.FaceDefine[face_name]

      if (!BlockRenderData.flawed) {
        let New_Pos = [dir[0], dir[1], dir[2]]
        if (Object.keys(Block.states).length) {
          for (let index = 0; index < 3; index++) New_Pos[index] += 0.5
          New_Pos = BlockStateOperation.__State_Pos_Transfor__(Block, New_Pos)
          for (let index = 0; index < New_Pos.length; index++) New_Pos[index] = Math.round(New_Pos[index]-0.5)
        }
        const NeighborBlock = this.getVoxel(x+New_Pos[0], y+New_Pos[1], z+New_Pos[2])
        const NeighborBlockData = BlockDefine.QueryBlockRender(NeighborBlock)
        if (!(AirTypeTest.has(NeighborBlock.name) || (!(Block.name in CopperGrateTest) && NeighborBlock.name in CopperGrateTest) ||
        NeighborBlockData.flawed || NeighborBlockData.transmitting)) continue
      } else if (BlockRenderData.connect) {
        const NeighborBlock = this.getVoxel(x+dir[0], y+dir[1], z+dir[2])
        const NeighborBlockData = BlockDefine.QueryBlockRender(NeighborBlock)
        const ConnectInfo = RenderSetting.ConnectionDefine[BlockRenderData.connect]
        if (ConnectInfo["id_test"].test(NeighborBlock.name) || (NeighborBlockData && !NeighborBlockData.flawed)) continue
      }

      const uvMode = RenderSetting.ModelDefine[BlockRenderData.model][face_name]
      const uvPosX = (BlockRenderData["index"] % 200) * tileSize
      const uvPosY = Math.floor(BlockRenderData["index"] / 200) * 160 + tileSize * uvMode
      //生成模型部分
      const ndx = Math.floor(positions.length / 3)
      for ( const { pos, uv } of corners ) {
        const New_Pos = BlockStateOperation.__State_Pos_Transfor__(Block, pos)
        positions.push( New_Pos[0]+x, New_Pos[1]+y, New_Pos[2]+z )
        uvs.push( (uvPosX+uv[0])/TransparentTextureWidth, (uvPosY+uv[1])/TransparentTextureHeight )
      }
      indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
    }

    this.__renderConnent__(x, y, z, Block, BlockRenderData, positions, uvs, indices,
      TransparentTextureWidth, TransparentTextureHeight)
  }
  renderSingleSideBlock(x, y, z, Block, BlockRenderData, positions, uvs, indices){
    const { tileSize, SingleTextureWidth, SingleTextureHeight} = this

    //遍历需要渲染的每一个面
    for (const face_name in RenderSetting.ModelDefine[BlockRenderData.model]) {
      const {dir, corners} = RenderSetting.FaceDefine[face_name]

      if (!BlockRenderData.flawed) {
        let New_Pos = [dir[0], dir[1], dir[2]]
        if (Object.keys(Block.states).length) {
          for (let index = 0; index < 3; index++) New_Pos[index] += 0.5
          New_Pos = BlockStateOperation.__State_Pos_Transfor__(Block, New_Pos)
          for (let index = 0; index < New_Pos.length; index++) New_Pos[index] = Math.round(New_Pos[index]-0.5)
        }
        const NeighborBlock = this.getVoxel(x+New_Pos[0], y+New_Pos[1], z+New_Pos[2])
        const NeighborBlockData = BlockDefine.QueryBlockRender(NeighborBlock)
        if (!(AirTypeTest.has(NeighborBlock.name) || (!(Block.name in CopperGrateTest) && NeighborBlock.name in CopperGrateTest) ||
        NeighborBlockData.flawed || NeighborBlockData.transmitting || NeighborBlockData.transparent)) continue
      }

      const uvMode = RenderSetting.ModelDefine[BlockRenderData.model][face_name]
      const uvPosX = (BlockRenderData["index"] % 200) * tileSize
      const uvPosY = Math.floor(BlockRenderData["index"] / 200) * 160 + tileSize * uvMode
      //生成模型部分
      const ndx = Math.floor(positions.length / 3)
      for ( const { pos, uv } of corners ) {
        const New_Pos = BlockStateOperation.__State_Pos_Transfor__(Block, pos)
        positions.push( New_Pos[0]+x, New_Pos[1]+y, New_Pos[2]+z )
        uvs.push( (uvPosX+uv[0])/SingleTextureWidth, (uvPosY+uv[1])/SingleTextureHeight )
      }
      indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
    }

    this.__renderConnent__(x, y, z, Block, BlockRenderData, positions, uvs, indices,
      SingleTextureWidth, SingleTextureHeight)
  }
  renderDoubleSideBlock(x, y, z, Block, BlockRenderData, positions, uvs, indices){
    const { tileSize, DoubleTextureWidth, DoubleTextureHeight} = this

    //遍历需要渲染的每一个面
    for (const face_name in RenderSetting.ModelDefine[BlockRenderData.model]) {
      const {dir, corners} = RenderSetting.FaceDefine[face_name]
      if (!BlockStateOperation.__State_Disable_Rerden__(Block, dir)) continue

      if (!BlockRenderData.flawed) {
        const NeighborBlock = this.getVoxel(x+dir[0], y+dir[1], z+dir[2])
        const NeighborBlockData = BlockDefine.QueryBlockRender(NeighborBlock)
        if ( !(AirTypeTest.has(NeighborBlock.name) || NeighborBlockData.transmitting)) continue
      }

      const uvMode = RenderSetting.ModelDefine[BlockRenderData.model][face_name]
      const uvPosX = (BlockRenderData["index"] % 200) * tileSize
      const uvPosY = Math.floor(BlockRenderData["index"] / 200) * 160 + uvMode * tileSize
      //生成模型部分
      const ndx = Math.floor(positions.length / 3)
      for ( const { pos, uv } of corners ) {
        const New_Pos = BlockStateOperation.__State_Pos_Transfor__(Block, pos)

        positions.push( New_Pos[0]+x, New_Pos[1]+y, New_Pos[2]+z )
        uvs.push( (uvPosX+uv[0])/DoubleTextureWidth, (uvPosY+uv[1])/DoubleTextureHeight )
      }
      indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3)
    }

    this.__renderConnent__(x, y, z, Block, BlockRenderData, positions, uvs, indices,
      DoubleTextureWidth, DoubleTextureHeight)
  }


  generateGeometryDataForCell(Orign_x, Orign_z) {
    const single_positions = []; const single_uvs = []; const single_indices = []
    const double_positions = []; const double_uvs = []; const double_indices = []
    const transparent_positions = []; const transparent_uvs = []; const transparent_indices = []

    const LoopEndPos = [Orign_x + 100, Orign_z + 100]
    for ( let x = Orign_x; x < LoopEndPos[0]; ++x ) {
      for ( let y = 0; y < this.cellSizeY; ++y ) {
        for ( let z = Orign_z; z < LoopEndPos[1]; ++z ) {
          const Block = this.getVoxel(x, y, z)
          if (AirTypeTest.has(Block.name)) continue

          const BlockRenderData = BlockDefine.QueryBlockRender(Block)
          if (BlockRenderData === null) continue

          //根据方块选择单面渲染模式还是双面渲染模式
          if (BlockRenderData.transparent && !BlockRenderData.fluid) this.renderTransparentBlock(x, y, z, 
            Block, BlockRenderData, transparent_positions, transparent_uvs, transparent_indices)
          else if (BlockRenderData.double_side) this.renderDoubleSideBlock(x, y, z, Block, BlockRenderData, 
            double_positions, double_uvs, double_indices)
          else this.renderSingleSideBlock(x, y, z, Block, BlockRenderData, single_positions, 
            single_uvs, single_indices)
          
          if (BlockRenderData.water_log || Block.name in WaterTest) this.renderFluid(x, y, z, 
            "minecraft:water", transparent_positions, transparent_uvs, transparent_indices)
          if (Block.name in LavaTest) this.renderFluid(x, y, z, 
            "minecraft:lava", single_positions, single_uvs, single_indices)
        }
      }
    }

    return {
      single_positions, single_uvs, single_indices, 
      double_positions, double_uvs, double_indices,
      transparent_positions, transparent_uvs, transparent_indices
    }
  }
  generateMeshList() {
    const MeshList = []
    const StartTimeStamp = new Date().getTime()

    try { 
      for ( let x = 0; x < this.cellSizeX; x+=100 ) {
      for ( let z = 0; z < this.cellSizeZ; z+=100 ) {
        const { 
          single_positions, single_uvs, single_indices, 
          double_positions, double_uvs, double_indices,
          transparent_positions, transparent_uvs, transparent_indices 
        } = this.generateGeometryDataForCell(x, z)
          
        if (single_positions.length) {
          const geometry = new THREE.BufferGeometry()
          geometry.setAttribute( 'position', new THREE.BufferAttribute(new Float32Array(single_positions), 3))
          geometry.setAttribute( 'uv', new THREE.BufferAttribute(new Float32Array(single_uvs), 2))
          geometry.setIndex(single_indices)
          MeshList.push(new THREE.Mesh(geometry, Block_Material))
        }
        if (double_positions.length) {
          const geometry = new THREE.BufferGeometry()
          geometry.setAttribute( 'position', new THREE.BufferAttribute(new Float32Array(double_positions), 3))
          geometry.setAttribute( 'uv', new THREE.BufferAttribute(new Float32Array(double_uvs), 2))
          geometry.setIndex(double_indices)
          MeshList.push(new THREE.Mesh(geometry, Plant_Material))
        }
        if (transparent_positions.length) {
          const geometry = new THREE.BufferGeometry()
          geometry.setAttribute( 'position', new THREE.BufferAttribute(new Float32Array(transparent_positions), 3))
          geometry.setAttribute( 'uv', new THREE.BufferAttribute(new Float32Array(transparent_uvs), 2))
          geometry.setIndex(transparent_indices)
          MeshList.push(new THREE.Mesh(geometry, Transparent_Material))
        }

        if (new Date().getTime() >= StartTimeStamp + 30000) {
          alert( "区块构建超时，已强制停止构建" )
          return MeshList
        }
    }}} catch (error) {
      alert(`区块构建错误，错误信息：\n${error.stack}`)
    }

    return MeshList;
  }
}


