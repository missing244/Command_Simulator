import * as THREE from "./three.module.js";



export function print(obj) {console.log(obj)}


const block_texture = new THREE.TextureLoader().load("picture/block_texture.png");
block_texture.magFilter = THREE.NearestFilter; block_texture.minFilter = THREE.NearestFilter;
export const block_material = new THREE.MeshBasicMaterial({map: block_texture,transparent: true});


const block_index = {
  "minecraft:stone": "same_6",
  "minecraft:dirt": "same_6",
  "minecraft:grass": "same_4",
  "minecraft:cobblestone": "same_6",
  "minecraft:planks": "same_6",
  "minecraft:bedrock": "same_6",
  "minecraft:flowing_water": "same_4_2",
  "minecraft:water": "same_4_2",
  "minecraft:flowing_lava": "same_4_2",
  "minecraft:lava": "same_4_2",
  "minecraft:sand": "same_6",
  "minecraft:gravel": "same_6",
  "minecraft:gold_ore": "same_6",
  "minecraft:iron_ore": "same_6",
  "minecraft:coal_ore": "same_6",
  "minecraft:log": "same_4_2",
  "minecraft:stripped_oak_log": "same_4_2",
  "minecraft:stripped_birch_log": "same_4_2",
  "minecraft:stripped_dark_oak_log": "same_4_2",
  "minecraft:stripped_acacia_log": "same_4_2",
  "minecraft:stripped_jungle_log": "same_4_2",
  "minecraft:stripped_spruce_log": "same_4_2",
  "minecraft:leaves": "same_6",
  "minecraft:sponge": "same_6",
  "minecraft:glass": "same_6",
  "minecraft:lapis_ore": "same_6",
  "minecraft:lapis_block": "same_6",
  "minecraft:sandstone": "same_4",
  "minecraft:noteblock": "same_6",
  "minecraft:jukebox": "same_4",
  "minecraft:sticky_piston": "same_4",
  "minecraft:piston": "same_4",
  "minecraft:wool": "same_6",
  "minecraft:gold_block": "same_6",
  "minecraft:iron_block": "same_6",
  "minecraft:coral_block": "same_6",
  "minecraft:brick_block": "same_6",
  "minecraft:tnt": "same_4",
  "minecraft:bookshelf": "same_4_2",
  "minecraft:mossy_cobblestone": "same_6",
  "minecraft:obsidian": "same_6",
  "minecraft:mob_spawner": "same_6",
  "minecraft:chest": "same_1",
  "minecraft:diamond_ore": "same_6",
  "minecraft:diamond_block": "same_6",
  "minecraft:crafting_table": "same_1",
  "minecraft:farmland": "same_4",
  "minecraft:furnace": "same_1",
  "minecraft:redstone_ore": "same_6",
  "minecraft:snow_layer": "same_6",
  "minecraft:ice": "same_6",
  "minecraft:snow": "same_6",
  "minecraft:clay": "same_6",
  "minecraft:dried_kelp_block": "same_1",
  "minecraft:pumpkin": "same_4_2",
  "minecraft:carved_pumpkin": "same_1",
  "minecraft:netherrack": "same_6",
  "minecraft:magma": "same_6",
  "minecraft:soul_sand": "same_6",
  "minecraft:glowstone": "same_6",
  "minecraft:portal": "same_6",
  "minecraft:lit_pumpkin": "same_1",
  "minecraft:barrier": "same_6",
  "minecraft:stonebrick": "same_6",
  "minecraft:melon_block": "same_4_2",
  "minecraft:mycelium": "same_4",
  "minecraft:cauldron": "same_4",
  "minecraft:end_stone": "same_6",
  "minecraft:end_bricks": "same_6",
  "minecraft:redstone_lamp": "same_6",
  "minecraft:lit_redstone_lamp": "same_6",
  "minecraft:emerald_ore": "same_6",
  "minecraft:emerald_block": "same_6",
  "minecraft:nether_brick": "same_6",
  "minecraft:red_nether_brick": "same_6",
  "minecraft:nether_wart_block": "same_6",
  "minecraft:trapped_chest": "same_1",
  "minecraft:redstone_block": "same_6",
  "minecraft:structure_block": "same_6",
  "minecraft:jigsaw": "same_1",
  "minecraft:structure_void": "same_6",
  "minecraft:quartz_ore": "same_6",
  "minecraft:bone_block": "same_4_2",
  "minecraft:quartz_block": "same_4",
  "minecraft:purpur_block": "same_6",
  "minecraft:chorus_plant": "same_6",
  "minecraft:chorus_flower": "same_6",
  "minecraft:stained_hardened_clay": "same_6",
  "minecraft:leaves2": "same_6",
  "minecraft:slime": "same_6",
  "minecraft:hay_block": "same_4_2",
  "minecraft:hardened_clay": "same_6",
  "minecraft:coal_block": "same_6",
  "minecraft:packed_ice": "same_6",
  "minecraft:blue_ice": "same_6",
  "minecraft:dragon_egg": "same_6",
  "minecraft:red_sandstone": "same_4",
  "minecraft:grass_path": "same_4",
  "minecraft:podzol": "same_4",
  "minecraft:glowingobsidian": "same_6",
  "minecraft:observer": "same_1",
  "minecraft:fire": "same_6",
  "minecraft:prismarine": "same_6",
  "minecraft:seaLantern": "same_6",
  "minecraft:ender_chest": "same_1",
  "minecraft:stained_glass": "same_6",
  "minecraft:shulker_box": "same_6",
  "minecraft:undyed_shulker_box": "same_6",
  "minecraft:command_block": "same_4",
  "minecraft:repeating_command_block": "same_4",
  "minecraft:chain_command_block": "same_4",
  "minecraft:concrete": "same_6",
  "minecraft:concretePowder": "same_6",
  "minecraft:black_glazed_terracotta": "same_6",
  "minecraft:blue_glazed_terracotta": "same_6",
  "minecraft:brown_glazed_terracotta": "same_6",
  "minecraft:cyan_glazed_terracotta": "same_6",
  "minecraft:gray_glazed_terracotta": "same_6",
  "minecraft:green_glazed_terracotta": "same_6",
  "minecraft:light_blue_glazed_terracotta": "same_6",
  "minecraft:lime_glazed_terracotta": "same_6",
  "minecraft:magenta_glazed_terracotta": "same_6",
  "minecraft:orange_glazed_terracotta": "same_6",
  "minecraft:pink_glazed_terracotta": "same_6",
  "minecraft:purple_glazed_terracotta": "same_6",
  "minecraft:red_glazed_terracotta": "same_6",
  "minecraft:silver_glazed_terracotta": "same_6",
  "minecraft:white_glazed_terracotta": "same_6",
  "minecraft:yellow_glazed_terracotta": "same_6",
  "minecraft:frosted_ice": "same_6",
  "minecraft:smooth_stone": "same_6",
  "minecraft:barrel": "same_1",
  "minecraft:smithing_table": "same_1",
  "minecraft:smoker": "same_1",
  "minecraft:lit_smoker": "same_1",
  "minecraft:blast_furnace": "same_1",
  "minecraft:lit_blast_furnace": "same_1",
  "minecraft:cartography_table": "same_1",
  "minecraft:loom": "same_1",
  "minecraft:composter": "same_4",
  "minecraft:allow": "same_6",
  "minecraft:deny": "same_6",
  "minecraft:border_block": "same_6",
  "minecraft:bee_nest": "same_1",
  "minecraft:beehive": "same_1",
  "minecraft:honey_block": "same_4",
  "minecraft:honeycomb_block": "same_6",
  "minecraft:lodestone": "same_4_2",
  "minecraft:warped_wart_block": "same_6",
  "minecraft:stripped_crimson_stem": "same_4_2",
  "minecraft:stripped_warped_stem": "same_4_2",
  "minecraft:crimson_hyphae": "same_6",
  "minecraft:warped_hyphae": "same_6",
  "minecraft:stripped_crimson_hyphae": "same_6",
  "minecraft:stripped_warped_hyphae": "same_6",
  "minecraft:shroomlight": "same_6",
  "minecraft:crimson_nylium": "same_4",
  "minecraft:warped_nylium": "same_4",
  "minecraft:basalt": "same_4_2",
  "minecraft:polished_basalt": "same_4_2",
  "minecraft:soul_soil": "same_6",
  "minecraft:target": "same_4_2",
  "minecraft:netherite_block": "same_6",
  "minecraft:nether_gold_ore": "same_6",
  "minecraft:ancient_debris": "same_4_2",
  "minecraft:crimson_planks": "same_6",
  "minecraft:warped_planks": "same_6",
  "minecraft:blackstone": "same_4_2",
  "minecraft:polished_blackstone_bricks": "same_6",
  "minecraft:chiseled_polished_blackstone": "same_6",
  "minecraft:cracked_polished_blackstone_bricks": "same_6",
  "minecraft:gilded_blackstone": "same_6",
  "minecraft:honeycomb": "same_6",
  "minecraft:respawn_anchor": "same_4",
  "minecraft:crying_obsidian": "same_6",
  "minecraft:polished_blackstone": "same_6",
  "minecraft:polished_blackstone_pressure_plate": "same_6",
  "minecraft:polished_blackstone_wall": "same_6",
  "minecraft:chiseled_nether_bricks": "same_6",
  "minecraft:cracked_nether_bricks": "same_6",
  "minecraft:quartz_bricks": "same_6",
  "minecraft:powder_snow": "same_6",
  "minecraft:dirt_with_roots": "same_6",
  "minecraft:azalea_leaves": "same_6",
  "minecraft:azalea_leaves_flowered": "same_6",
  "minecraft:moss_block": "same_6",
  "minecraft:moss_carpet": "same_6",
  "minecraft:dripstone_block": "same_6",
  "minecraft:amethyst_block": "same_6",
  "minecraft:budding_amethyst": "same_6",
  "minecraft:tuff": "same_6",
  "minecraft:calcite": "same_6",
  "minecraft:tinted_glass": "same_6",
  "minecraft:smooth_basalt": "same_6",
  "minecraft:deepslate": "same_4_2",
  "minecraft:infested_deepslate": "same_4_2",
  "minecraft:cobbled_deepslate": "same_6",
  "minecraft:polished_deepslate": "same_6",
  "minecraft:deepslate_tiles": "same_6",
  "minecraft:deepslate_bricks": "same_6",
  "minecraft:chiseled_deepslate": "same_6",
  "minecraft:deepslate_lapis_ore": "same_6",
  "minecraft:deepslate_iron_ore": "same_6",
  "minecraft:deepslate_gold_ore": "same_6",
  "minecraft:deepslate_redstone_ore": "same_6",
  "minecraft:lit_deepslate_redstone_ore": "same_6",
  "minecraft:deepslate_diamond_ore": "same_6",
  "minecraft:deepslate_coal_ore": "same_6",
  "minecraft:deepslate_emerald_ore": "same_6",
  "minecraft:deepslate_copper_ore": "same_6",
  "minecraft:cracked_deepslate_tiles": "same_6",
  "minecraft:cracked_deepslate_bricks": "same_6",
  "minecraft:copper_ore": "same_6",
  "minecraft:copper_block": "same_6",
  "minecraft:exposed_copper": "same_6",
  "minecraft:weathered_copper": "same_6",
  "minecraft:oxidized_copper": "same_6",
  "minecraft:waxed_copper": "same_6",
  "minecraft:waxed_exposed_copper": "same_6",
  "minecraft:waxed_weathered_copper": "same_6",
  "minecraft:waxed_oxidized_copper": "same_6",
  "minecraft:cut_copper": "same_6",
  "minecraft:exposed_cut_copper": "same_6",
  "minecraft:weathered_cut_copper": "same_6",
  "minecraft:oxidized_cut_copper": "same_6",
  "minecraft:waxed_cut_copper": "same_6",
  "minecraft:waxed_exposed_cut_copper": "same_6",
  "minecraft:waxed_weathered_cut_copper": "same_6",
  "minecraft:waxed_oxidized_cut_copper": "same_6",
  "minecraft:raw_copper_block": "same_6",
  "minecraft:raw_iron_block": "same_6",
  "minecraft:raw_gold_block": "same_6",
  "minecraft:mangrove_roots": "same_4_2",
  "minecraft:muddy_mangrove_roots": "same_4_2",
  "minecraft:mangrove_log": "same_4_2",
  "minecraft:stripped_mangrove_log": "same_4_2",
  "minecraft:mangrove_planks": "same_6",
  "minecraft:mangrove_wood": "same_6",
  "minecraft:stripped_mangrove_wood": "same_6",
  "minecraft:sculk_sensor": "same_4",
  "minecraft:sculk": "same_6",
  "minecraft:sculk_catalyst": "same_4",
  "minecraft:sculk_shrieker": "same_4",
  "minecraft:pearlescent_froglight": "same_4_2",
  "minecraft:verdant_froglight": "same_4_2",
  "minecraft:ochre_froglight": "same_4_2",
  "minecraft:mud": "same_6",
  "minecraft:packed_mud": "same_6",
  "minecraft:mud_bricks": "same_6",
  "minecraft:reinforced_deepslate": "same_4",
  "minecraft:white_wool": "same_6",
  "minecraft:orange_wool": "same_6",
  "minecraft:magenta_wool": "same_6",
  "minecraft:light_blue_wool": "same_6",
  "minecraft:yellow_wool": "same_6",
  "minecraft:lime_wool": "same_6",
  "minecraft:pink_wool": "same_6",
  "minecraft:gray_wool": "same_6",
  "minecraft:light_gray_wool": "same_6",
  "minecraft:cyan_wool": "same_6",
  "minecraft:purple_wool": "same_6",
  "minecraft:blue_wool": "same_6",
  "minecraft:brown_wool": "same_6",
  "minecraft:green_wool": "same_6",
  "minecraft:red_wool": "same_6",
  "minecraft:black_wool": "same_6",
  "minecraft:oak_log": "same_4_2",
  "minecraft:spruce_log": "same_4_2",
  "minecraft:birch_log": "same_4_2",
  "minecraft:jungle_log": "same_4_2",
  "minecraft:acacia_log": "same_4_2",
  "minecraft:bamboo_mosaic": "same_6",
  "minecraft:bamboo_block": "same_4_2",
  "minecraft:stripped_bamboo_block": "same_4_2",
  "minecraft:bamboo_planks": "same_6",
  "minecraft:chiseled_bookshelf": "same_1",
  "minecraft:suspicious_sand": "same_6",
  "minecraft:suspicious_gravel": "same_6",
  "minecraft:cherry_log": "same_4_2",
  "minecraft:cherry_planks": "same_6",
  "minecraft:cherry_wood": "same_6",
  "minecraft:stripped_cherry_log": "same_4_2",
  "minecraft:stripped_cherry_wood": "same_6",
  "minecraft:cherry_leaves": "same_6",
  "minecraft:calibrated_sculk_sensor": "same_1",
  "minecraft:white_concrete": "same_6",
  "minecraft:orange_concrete": "same_6",
  "minecraft:magenta_concrete": "same_6",
  "minecraft:light_blue_concrete": "same_6",
  "minecraft:yellow_concrete": "same_6",
  "minecraft:lime_concrete": "same_6",
  "minecraft:pink_concrete": "same_6",
  "minecraft:gray_concrete": "same_6",
  "minecraft:light_gray_concrete": "same_6",
  "minecraft:cyan_concrete": "same_6",
  "minecraft:purple_concrete": "same_6",
  "minecraft:blue_concrete": "same_6",
  "minecraft:brown_concrete": "same_6",
  "minecraft:green_concrete": "same_6",
  "minecraft:red_concrete": "same_6",
  "minecraft:black_concrete": "same_6"
}
const list_of_block_index = Object.keys(block_index)
const list_of_block_index_map = {}
list_of_block_index.forEach( function(a) {list_of_block_index_map[a] = Object.keys(block_index).indexOf(a) + 1} )
console.log(list_of_block_index_map)


function mc_rotation_pos(distance,ry,rx) {
  const ry1 = -ry * Math.PI / 180
  const rx1 = -rx * Math.PI / 180
  const z = distance * Math.cos(ry1) * Math.cos(rx1)
  const x = distance * Math.sin(ry1) * Math.cos(rx1)
  const y = distance * Math.sin(rx1)
  return [x,y,z]
}

function mc_rotation_base_vector(ry,rx) {
  const v1 = mc_rotation_pos(1.5,ry,rx)
  const v2 = mc_rotation_pos(1.5,ry,rx-90)
  const v3 = mc_rotation_pos(1.5,ry-90,0)
  return [v3,v2,v1]
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
    this.cell = new Uint16Array(this.cellSizeX * this.cellSizeY * this.cellSizeZ);
    this.blockMap = options.blockMap
  }

  computeVoxelOffset( x, y, z ) {
    //const voxelX = THREE.MathUtils.euclideanModulo(x, this.cellSizeX) | 0;
    //const voxelY = THREE.MathUtils.euclideanModulo(y, this.cellSizeY) | 0;
    //const voxelZ = THREE.MathUtils.euclideanModulo(z, this.cellSizeZ) | 0;
    //console.log([voxelX,voxelY,voxelZ,this.cellSizeX,this.cellSizeY,this.cellSizeZ])
    return y * this.cellSliceSize + z * this.cellSizeX + x;
  }

  getCellForVoxel( x, y, z ) {
    const cellX = Math.floor( x / this.cellSizeX );
    const cellY = Math.floor( y / this.cellSizeY );
    const cellZ = Math.floor( z / this.cellSizeZ );
    if ( cellX !== 0 || cellY !== 0 || cellZ !== 0 ) return null;
    return this.cell;
  }

  setVoxel( x, y, z, v ) {
    const cell = this.getCellForVoxel( x, y, z );
    if ( !cell ) return; // TODO: add a new cell?
    const voxelOffset = this.computeVoxelOffset( x, y, z );
    if (list_of_block_index.includes(this.blockMap[v])) cell[voxelOffset] = list_of_block_index_map[this.blockMap[v]]
    else cell[voxelOffset] = 0
  }

  getVoxel( x, y, z ) {
    const cell = this.getCellForVoxel( x, y, z );
    if ( !cell ) return 0;
    const voxelOffset = this.computeVoxelOffset( x, y, z );
    return cell[voxelOffset];
  }

  generateGeometryDataForCell( cellX, cellY, cellZ ) {
    const { tileSize, tileTextureWidth, tileTextureHeight } = this;
    const positions = []; const normals = []; const uvs = []; const indices = [];
    const startX = cellX * this.cellSizeX;
    const startY = cellY * this.cellSizeY;
    const startZ = cellZ * this.cellSizeZ;

    for ( let y = 0; y < this.cellSizeY; ++ y ) {
      const voxelY = startY + y;
      for ( let z = 0; z < this.cellSizeZ; ++ z ) {
        const voxelZ = startZ + z;
        for ( let x = 0; x < this.cellSizeX; ++ x ) {
          const voxelX = startX + x;
          const voxel = this.getVoxel(voxelX, voxelY, voxelZ);
          if ( voxel ) {
            // voxel 0 is sky (empty) so for UVs we start at 0
            const uvVoxel = voxel - 1; let uv_data = null;
            // There is a voxel here but do we need faces for it?
            if      (block_index[list_of_block_index[uvVoxel]] == "same_6") uv_data = VoxelWorld.same_6
            else if (block_index[list_of_block_index[uvVoxel]] == "same_4") uv_data = VoxelWorld.same_4
            else if (block_index[list_of_block_index[uvVoxel]] == "same_4_2") uv_data = VoxelWorld.same_4_2
            else if (block_index[list_of_block_index[uvVoxel]] == "same_1") uv_data = VoxelWorld.same_1

            for ( const {dir, corners, uvRow} of uv_data ) {
              const neighbor = this.getVoxel(voxelX + dir[0], voxelY + dir[1], voxelZ + dir[2]);
              if ( ! neighbor ) {
                // this voxel has no neighbor in this direction so we need a face.
                const ndx = Math.floor(positions.length / 3);
                for ( const { pos, uv } of corners ) {
                  positions.push( pos[0]+x, pos[1]+y, pos[2]+z );
                  normals.push( ...dir );
                  uvs.push(
                    (uvVoxel + uv[0]) * tileSize / tileTextureWidth,
                    1 - ( uvRow + 1 - uv[1] ) * tileSize / tileTextureHeight );
                }
                indices.push(ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3);
              }
            }
          }
        }
      }
    }
    return {positions, normals, uvs, indices};
  }
}


//4面相同
VoxelWorld.same_4 = [
  { // left
    uvRow: 0,
    dir: [ - 1, 0, 0, ],
    corners: [
      { pos: [ 0, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 1 ], uv: [ 1, 0 ], },
    ],
  },
  { // right
    uvRow: 0,
    dir: [ 1, 0, 0, ],
    corners: [
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 1, 1 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 0 ], },
    ],
  },
  { // bottom
    uvRow: 2,
    dir: [ 0, - 1, 0, ],
    corners: [
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 1 ], },
    ],
  },
  { // top
    uvRow: 1,
    dir: [ 0, 1, 0, ],
    corners: [
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 0 ], },
    ],
  },
  { // back
    uvRow: 0,
    dir: [ 0, 0, - 1, ],
    corners: [
      { pos: [ 1, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 0, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 1 ], },
    ],
  },
  { // front
    uvRow: 0,
    dir: [ 0, 0, 1, ],
    corners: [
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 1, 1 ], },
    ],
  },
];

//4,2面相同 原木
VoxelWorld.same_4_2 = [
  { // left
    uvRow: 0,
    dir: [ - 1, 0, 0, ],
    corners: [
      { pos: [ 0, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 1 ], uv: [ 1, 0 ], },
    ],
  },
  { // right
    uvRow: 0,
    dir: [ 1, 0, 0, ],
    corners: [
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 1, 1 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 0 ], },
    ],
  },
  { // bottom
    uvRow: 1,
    dir: [ 0, - 1, 0, ],
    corners: [
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 1 ], },
    ],
  },
  { // top
    uvRow: 1,
    dir: [ 0, 1, 0, ],
    corners: [
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 0 ], },
    ],
  },
  { // back
    uvRow: 0,
    dir: [ 0, 0, - 1, ],
    corners: [
      { pos: [ 1, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 0, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 1 ], },
    ],
  },
  { // front
    uvRow: 0,
    dir: [ 0, 0, 1, ],
    corners: [
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 1, 1 ], },
    ],
  },
];

//6面相同
VoxelWorld.same_6 = [
  { // left
    uvRow: 0,
    dir: [ - 1, 0, 0, ],
    corners: [
      { pos: [ 0, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 1 ], uv: [ 1, 0 ], },
    ],
  },
  { // right
    uvRow: 0,
    dir: [ 1, 0, 0, ],
    corners: [
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 1, 1 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 0 ], },
    ],
  },
  { // bottom
    uvRow: 0,
    dir: [ 0, - 1, 0, ],
    corners: [
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 1 ], },
    ],
  },
  { // top
    uvRow: 0,
    dir: [ 0, 1, 0, ],
    corners: [
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 0 ], },
    ],
  },
  { // back
    uvRow: 0,
    dir: [ 0, 0, - 1, ],
    corners: [
      { pos: [ 1, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 0, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 1 ], },
    ],
  },
  { // front
    uvRow: 0,
    dir: [ 0, 0, 1, ],
    corners: [
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 1, 1 ], },
    ],
  },
];

//没有面相同
VoxelWorld.same_1 = [
  { // left
    uvRow: 0,
    dir: [ - 1, 0, 0, ],
    corners: [
      { pos: [ 0, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 1 ], uv: [ 1, 0 ], },
    ],
  },
  { // right
    uvRow: 1,
    dir: [ 1, 0, 0, ],
    corners: [
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 1, 1 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 0 ], },
    ],
  },
  { // bottom
    uvRow: 3,
    dir: [ 0, - 1, 0, ],
    corners: [
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 0 ], uv: [ 1, 1 ], },
      { pos: [ 0, 0, 0 ], uv: [ 0, 1 ], },
    ],
  },
  { // top
    uvRow: 2,
    dir: [ 0, 1, 0, ],
    corners: [
      { pos: [ 0, 1, 1 ], uv: [ 1, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 0 ], },
    ],
  },
  { // back
    uvRow: 4,
    dir: [ 0, 0, - 1, ],
    corners: [
      { pos: [ 1, 0, 0 ], uv: [ 0, 0 ], },
      { pos: [ 0, 0, 0 ], uv: [ 1, 0 ], },
      { pos: [ 1, 1, 0 ], uv: [ 0, 1 ], },
      { pos: [ 0, 1, 0 ], uv: [ 1, 1 ], },
    ],
  },
  { // front
    uvRow: 5,
    dir: [ 0, 0, 1, ],
    corners: [
      { pos: [ 0, 0, 1 ], uv: [ 0, 0 ], },
      { pos: [ 1, 0, 1 ], uv: [ 1, 0 ], },
      { pos: [ 0, 1, 1 ], uv: [ 0, 1 ], },
      { pos: [ 1, 1, 1 ], uv: [ 1, 1 ], },
    ],
  },
];



export function generate_3d_chunk(world){
  const { positions, normals, uvs, indices } = world.generateGeometryDataForCell( 0, 0, 0 );
  const geometry = new THREE.BufferGeometry();

  const positionNumComponents = 3; const normalNumComponents = 3; const uvNumComponents = 2;
  geometry.setAttribute( 'position', new THREE.BufferAttribute(new Float32Array(positions), positionNumComponents));
  geometry.setAttribute( 'normal', new THREE.BufferAttribute(new Float32Array(normals), normalNumComponents));
  geometry.setAttribute( 'uv', new THREE.BufferAttribute(new Float32Array(uvs), uvNumComponents));
  geometry.setIndex(indices);
  const mesh = new THREE.Mesh(geometry, block_material);
  return mesh;
}


export function generate_3d_entity(startx,startz,entities){
  const geometry1 = new THREE.BoxGeometry(0.5, 0.5, 0.5)
  const BoxMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const color = new THREE.Color(entities.color);

  // 创建一个InstancedMesh对象
  const mesh1 = new THREE.InstancedMesh(geometry1, BoxMaterial, entities.entity.length);
  const vertices1 = []; const vertices2 = []; const vertices3 = [];

// 循环设置每个实例的变换矩阵
  for (let i = 0; i < mesh1.count; i++) {
    const matrix = new THREE.Matrix4();
    const obj1 = entities.entity[i]
    obj1.Pos[0].value -= startx
    obj1.Pos[2].value -= startz
    //console.log(obj1.Pos);
    matrix.setPosition(obj1.Pos[0].value, obj1.Pos[1].value+64, obj1.Pos[2].value);
    mesh1.setMatrixAt(i, matrix);
    mesh1.setColorAt(i, color);

    vertices1.push(obj1.Pos[0].value); vertices1.push(obj1.Pos[1].value+64); vertices1.push(obj1.Pos[2].value);
    vertices2.push(obj1.Pos[0].value); vertices2.push(obj1.Pos[1].value+64); vertices2.push(obj1.Pos[2].value);
    vertices3.push(obj1.Pos[0].value); vertices3.push(obj1.Pos[1].value+64); vertices3.push(obj1.Pos[2].value);

    const rotation_vector = mc_rotation_base_vector(obj1.Rotation[0].value , obj1.Rotation[1].value)
    vertices1.push(obj1.Pos[0].value + rotation_vector[0][0]); 
    vertices1.push(obj1.Pos[1].value+ 64 + rotation_vector[0][1]); 
    vertices1.push(obj1.Pos[2].value + rotation_vector[0][2]);

    vertices2.push(obj1.Pos[0].value + rotation_vector[1][0]); 
    vertices2.push(obj1.Pos[1].value+ 64 + rotation_vector[1][1]); 
    vertices2.push(obj1.Pos[2].value + rotation_vector[1][2]);

    vertices3.push(obj1.Pos[0].value + rotation_vector[2][0]); 
    vertices3.push(obj1.Pos[1].value + 64 + rotation_vector[2][1]); 
    vertices3.push(obj1.Pos[2].value + rotation_vector[2][2]);
  }
  
  const geometry_line1 = new THREE.BufferGeometry();
  const LineMaterial1 = new THREE.LineBasicMaterial({ color: 0xff0000 });
  geometry_line1.setAttribute('position', new THREE.Float32BufferAttribute(vertices1, 3));
  const line1 = new THREE.LineSegments(geometry_line1, LineMaterial1);

  const geometry_line2 = new THREE.BufferGeometry();
  const LineMaterial2 = new THREE.LineBasicMaterial({ color: 0x00ff00 });
  geometry_line2.setAttribute('position', new THREE.Float32BufferAttribute(vertices2, 3));
  const line2 = new THREE.LineSegments(geometry_line2, LineMaterial2);

  const geometry_line3 = new THREE.BufferGeometry();
  const LineMaterial3 = new THREE.LineBasicMaterial({ color: 0x0000ff });
  geometry_line3.setAttribute('position', new THREE.Float32BufferAttribute(vertices3, 3));
  const line3 = new THREE.LineSegments(geometry_line3, LineMaterial3);
  // 将InstancedMesh对象添加到场景中
  return [mesh1,line1,line2,line3];
}


export function generate_3d_particle(startx,startz,area_x,area_z,particle_data){
  const geometry1 = new THREE.SphereGeometry(0.2,32,32)
  const BoxMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const new_particle_list = []
  Object.keys(particle_data).forEach((items1) => {
    particle_data[items1].forEach((items2) =>{
      let x = items2.pos[0].value - startx
      let z = items2.pos[2].value - startz
      if ((x >= 0 && x < area_x) && (z >= 0 && z < area_z)) {
        items2.pos[0].value = x
        items2.pos[2].value = z
        new_particle_list.push(items2)
      }
    })
  })

  // 创建一个InstancedMesh对象
  const mesh1 = new THREE.InstancedMesh(geometry1, BoxMaterial, new_particle_list.length);
  for (let i = 0; i < mesh1.count; i++) {
    const matrix = new THREE.Matrix4();
    matrix.setPosition(
      new_particle_list[i].pos[0].value,
      new_particle_list[i].pos[1].value + 64,
      new_particle_list[i].pos[2].value);
    mesh1.setMatrixAt(i, matrix);
  }
  return mesh1
}
