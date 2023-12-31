import * as THREE from "./three.module.js";


function load_texture(path_list1){
	for (let index = 0; index < path_list1.length; index++){
		const texture = new THREE.TextureLoader().load(path_list1[index]);
		texture.magFilter = THREE.NearestFilter;
		const material = new THREE.MeshLambertMaterial( {map: texture} );
		path_list1[index] = material
	}
}

const command_block = [
    'picture/block/command_block_side_mipmap.png','picture/block/command_block_side_mipmap.png',
    'picture/block/command_block_front_mipmap.png','picture/block/command_block_back_mipmap.png',
    'picture/block/command_block_side_mipmap.png','picture/block/command_block_side_mipmap.png'];
load_texture(command_block)

const command_block_condition = [
    'picture/block/command_block_conditional_mipmap.png','picture/block/command_block_conditional_mipmap.png',
    'picture/block/command_block_front_mipmap.png','picture/block/command_block_back_mipmap.png',
    'picture/block/command_block_conditional_mipmap.png','picture/block/command_block_conditional_mipmap.png'];
load_texture(command_block_condition)

const chain_command_block = [
    'picture/block/chain_command_block_side_mipmap.png','picture/block/chain_command_block_side_mipmap.png',
    'picture/block/chain_command_block_front_mipmap.png','picture/block/chain_command_block_back_mipmap.png',
    'picture/block/chain_command_block_side_mipmap.png','picture/block/chain_command_block_side_mipmap.png'];
load_texture(chain_command_block)
        
const chain_command_block_condition = [
    'picture/block/chain_command_block_conditional_mipmap.png','picture/block/chain_command_block_conditional_mipmap.png',
    'picture/block/chain_command_block_front_mipmap.png','picture/block/chain_command_block_back_mipmap.png',
    'picture/block/chain_command_block_conditional_mipmap.png','picture/block/chain_command_block_conditional_mipmap.png'];
load_texture(chain_command_block_condition)
        
const repeating_command_block = [
    'picture/block/repeating_command_block_side_mipmap.png','picture/block/repeating_command_block_side_mipmap.png',
    'picture/block/repeating_command_block_front_mipmap.png','picture/block/repeating_command_block_back_mipmap.png',
    'picture/block/repeating_command_block_side_mipmap.png','picture/block/repeating_command_block_side_mipmap.png'];
load_texture(repeating_command_block)
        
const repeating_command_block_condition = [
    'picture/block/repeating_command_block_conditional_mipmap.png','picture/block/repeating_command_block_conditional_mipmap.png',
    'picture/block/repeating_command_block_front_mipmap.png','picture/block/repeating_command_block_back_mipmap.png',
    'picture/block/repeating_command_block_conditional_mipmap.png','picture/block/repeating_command_block_conditional_mipmap.png'];
load_texture(repeating_command_block_condition)

function command_block_rotation(pos,facing){
	const matrix = new THREE.Matrix4()
	const position = new THREE.Vector3( pos[0], pos[1], pos[2] );
	if (facing == 0) matrix.compose(position,new THREE.Quaternion().setFromEuler(new THREE.Euler( 0,0,Math.PI )),new THREE.Vector3( 1, 1, 1 ))
	else if (facing == 1) matrix.compose(position,new THREE.Quaternion().setFromEuler(new THREE.Euler( 0,0,0 )),new THREE.Vector3( 1, 1, 1 ))
	else if (facing == 2) matrix.compose(position,new THREE.Quaternion().setFromEuler(new THREE.Euler( -Math.PI/2,0,0 )),new THREE.Vector3( 1, 1, 1 ))
	else if (facing == 3) matrix.compose(position,new THREE.Quaternion().setFromEuler(new THREE.Euler( Math.PI/2,0,0 )),new THREE.Vector3( 1, 1, 1 ))
	else if (facing == 4) matrix.compose(position,new THREE.Quaternion().setFromEuler(new THREE.Euler( 0,0,Math.PI/2 )),new THREE.Vector3( 1, 1, 1 ))
	else if (facing == 5) matrix.compose(position,new THREE.Quaternion().setFromEuler(new THREE.Euler( 0,0,-Math.PI/2 )),new THREE.Vector3( 1, 1, 1 ))
	return matrix
}



export function command_block_rander_system(cb_list){

	const cb_sort = {"command_block":[], "command_block_condition":[], "chain_command_block":[], "chain_command_block_condition":[],
					 "repeating_command_block":[], "repeating_command_block_condition":[]}

	for (let index = 0; index < cb_list.length; index++) {
		if (cb_list[index].conditional) cb_sort[cb_list[index].id + "_condition"].push(cb_list[index])
		else cb_sort[cb_list[index].id].push(cb_list[index])
	}
	console.log(cb_sort);

	const geometry_0 = new THREE.BoxGeometry(1, 1, 1);
	const mesh_0 = new THREE.InstancedMesh(geometry_0, command_block, cb_sort["command_block"].length);
	for (let index = 0; index < mesh_0.count; index++) {
		const cb_data = cb_sort["command_block"][index]
		mesh_0.setMatrixAt(index, command_block_rotation(cb_data.pos,cb_data.facing));
	}

	const geometry_1 = new THREE.BoxGeometry(1, 1, 1);
	const mesh_1 = new THREE.InstancedMesh(geometry_1, command_block_condition, cb_sort["command_block_condition"].length);
	for (let index = 0; index < mesh_1.count; index++) {
		const cb_data = cb_sort["command_block_condition"][index]
		mesh_1.setMatrixAt(index, command_block_rotation(cb_data.pos,cb_data.facing));
	}

	const geometry_2 = new THREE.BoxGeometry(1, 1, 1);
	const mesh_2 = new THREE.InstancedMesh(geometry_2, chain_command_block, cb_sort["chain_command_block"].length);
	for (let index = 0; index < mesh_2.count; index++) {
		const cb_data = cb_sort["chain_command_block"][index]
		mesh_2.setMatrixAt(index, command_block_rotation(cb_data.pos,cb_data.facing));
	}

	const geometry_3 = new THREE.BoxGeometry(1, 1, 1);
	const mesh_3 = new THREE.InstancedMesh(geometry_3, chain_command_block_condition, cb_sort["chain_command_block_condition"].length);
	for (let index = 0; index < mesh_3.count; index++) {
		const cb_data = cb_sort["chain_command_block_condition"][index]
		mesh_3.setMatrixAt(index, command_block_rotation(cb_data.pos,cb_data.facing));
	}

	const geometry_4 = new THREE.BoxGeometry(1, 1, 1);
	const mesh_4 = new THREE.InstancedMesh(geometry_4, repeating_command_block, cb_sort["repeating_command_block"].length);
	for (let index = 0; index < mesh_4.count; index++) {
		const cb_data = cb_sort["repeating_command_block"][index]
		mesh_4.setMatrixAt(index, command_block_rotation(cb_data.pos,cb_data.facing));
	}

	const geometry_5 = new THREE.BoxGeometry(1, 1, 1);
	const mesh_5 = new THREE.InstancedMesh(geometry_5, repeating_command_block_condition, cb_sort["repeating_command_block_condition"].length);
	for (let index = 0; index < mesh_5.count; index++) {
		const cb_data = cb_sort["repeating_command_block_condition"][index]
		mesh_5.setMatrixAt(index, command_block_rotation(cb_data.pos,cb_data.facing));
	}

	return [mesh_0, mesh_1, mesh_2, mesh_3, mesh_4, mesh_5]
}