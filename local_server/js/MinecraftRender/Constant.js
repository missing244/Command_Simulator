const WaterTypes = new Set( ["minecraft:water", "minecraft:flowing_water"] )
const LavaTypes = new Set( ["minecraft:lava", "minecraft:flowing_lava"] )
const AirTypes = new Set( ["minecraft:air", , "minecraft:light_block", "minecraft:light_block_0", "minecraft:light_block_1",
    "minecraft:light_block_2", "minecraft:light_block_3", "minecraft:light_block_4", "minecraft:light_block_5",
    "minecraft:light_block_6", "minecraft:light_block_7", "minecraft:light_block_8", "minecraft:light_block_9",
    "minecraft:light_block_10", "minecraft:light_block_11", "minecraft:light_block_12", "minecraft:light_block_13",
    "minecraft:light_block_14", "minecraft:light_block_15", "minecraft:moving_block", "minecraft:piston_arm_collision",
    "minecraft:skull", "minecraft:skeleton_skull", "minecraft:wither_skeleton_skull", "minecraft:zombie_head",
    "minecraft:player_head", "minecraft:creeper_head", "minecraft:dragon_head", "minecraft:piglin_head", 
    "minecraft:standing_banner", "minecraft:sticky_piston_arm_collision"])
const CopperGrateTypes = new Set( ["minecraft:copper_grate", "minecraft:exposed_copper_grate", 
    "minecraft:exposed_copper_grate", "minecraft:oxidized_copper_grate", "minecraft:waxed_copper_grate", 
    "minecraft:waxed_exposed_copper_grate", "minecraft:waxed_exposed_copper_grate", "minecraft:waxed_oxidized_copper_grate"] )
const ConnectTest = [
    {direction:[0, 0, -1], axes:[0, 1, 0], angle:0, name:"north"}, 
    {direction:[0, 0, 1], axes:[0, 1, 0], angle:Math.PI, name:"south"}, 
    {direction:[-1, 0, 0], axes:[0, 1, 0], angle:Math.PI/2, name:"west"}, 
    {direction:[1, 0, 0], axes:[0, 1, 0], angle:-Math.PI/2, name:"east"}, 
    {direction:[0, -1, 0], axes:[1, 0, 0], angle:-Math.PI/2, name:"top"}, 
    {direction:[0, 1, 0], axes:[1, 0, 0], angle:Math.PI/2, name:"bottom"} ]



class BlockStateChangePos {
    //方块旋转参数
    static FacingDirection_1 = {
      0: [{rotate_axis:[1,0,0], angle:0}], 
      1: [{rotate_axis:[1,0,0], angle:Math.PI}], 
      2: [{rotate_axis:[1,0,0], angle:Math.PI/2}], 
      3: [{rotate_axis:[1,0,0], angle:-Math.PI/2}], 
      4: [{rotate_axis:[0,1,0], angle:Math.PI/2}, {rotate_axis:[0,0,1], angle:-Math.PI/2}], 
      5: [{rotate_axis:[0,1,0], angle:Math.PI/2}, {rotate_axis:[0,0,1], angle:Math.PI/2}]
    }
    static FacingDirection_2 = {
      0: {rotate_axis:[0,-1,0], angle:0}, 
      1: {rotate_axis:[0,-1,0], angle:0}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI}, 
      3: {rotate_axis:[0,-1,0], angle:0},
      4: {rotate_axis:[0,-1,0], angle:Math.PI/2}, 
      5: {rotate_axis:[0,-1,0], angle:-Math.PI/2},
    }
    static Direction_1 = {
      0: {rotate_axis:[0,-1,0], angle:0}, 
      1: {rotate_axis:[0,-1,0], angle:Math.PI/2}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI}, 
      3: {rotate_axis:[0,-1,0], angle:-Math.PI/2},
    }
    static Direction_2 = {
      0: {rotate_axis:[0,-1,0], angle:0}, 
      1: {rotate_axis:[0,-1,0], angle:Math.PI}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI/2}, 
      3: {rotate_axis:[0,-1,0], angle:-Math.PI/2},
    }
    static WeirdoDirection = {
      0: {rotate_axis:[0,-1,0], angle:0, facing:[-1,0,0]}, 
      1: {rotate_axis:[0,-1,0], angle:Math.PI, facing:[1,0,0]}, 
      2: {rotate_axis:[0,-1,0], angle:Math.PI/2, facing:[0,0,-1]}, 
      3: {rotate_axis:[0,-1,0], angle:-Math.PI/2, facing:[0,0,1]},
    }
    static PortalAxis = {
      "z": {rotate_axis:[0,1,0], angle:0}, 
      "x": {rotate_axis:[0,1,0], angle:Math.PI/2}, 
      "unknown": {rotate_axis:[0,1,0], angle:Math.PI/2}
    }
    static BlockFace = {down: 0, up: 1, north: 2, south: 3, west: 4, east: 5}
    static CardinalDirection = {north: 2, east: 3, south: 0, west: 1}
    static LeverDirection = {down_east_west: 0, down_north_south: 0, up_north_south: 1, up_east_west: 1,
        north: 2, south: 3, west: 4, east: 5}
    static PillarAxis = { 
        x:{rotate_axis:[0,0,-1], angle:Math.PI/2}, 
        y:{rotate_axis:[0,-1,0], angle:0}, 
        z:{rotate_axis:[1,0,0], angle:Math.PI/2}
    }
    static Orientation = {
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

    //方块ID测试
    static facing_direction1_test = new RegExp("(button|amethyst_bud|amethyst_cluster|lightning_rod|observer|piston|command_block|frame|end_rod)$", "m")
    static facing_direction3_test = new RegExp("(hopper)$", "m")
    static stairs_test = new RegExp("stairs$", "m")
    static trapdoor_test = new RegExp("trapdoor$", "m")
    static glazed_terracotta_test = new RegExp("glazed_terracotta$", "m")
    static functional_rail_test = new RegExp("(rail)$", "m")
    static lantern_test = new RegExp("lantern$", "m")

    //3D旋转函数
    static __Rodrigues_rotate__(pos, rotate_axis, angle) {
        if (angle === 0) return pos

        const c1 = Math.cos(angle) ; const c2 = Math.sin(angle)
        const c3 = (1 - c1) * (pos[0]*rotate_axis[0] + pos[1]*rotate_axis[1] + pos[2]*rotate_axis[2])
        const cross = [ 
            rotate_axis[1] * pos[2] - rotate_axis[2] * pos[1],
            rotate_axis[2] * pos[0] - rotate_axis[0] * pos[2],
            rotate_axis[0] * pos[1] - rotate_axis[1] * pos[0] ]

        return [ 
            c1*pos[0] + c3*rotate_axis[0] + c2*cross[0], 
            c1*pos[1] + c3*rotate_axis[1] + c2*cross[1], 
            c1*pos[2] + c3*rotate_axis[2] + c2*cross[2] ]
    }

    //方块坐标变换函数
    static BlockState_For_Stairs(pos, StateDict, NoPosDelta=false) {
        let State1 = "weirdo_direction" in StateDict ? StateDict["weirdo_direction"] : 0
        let State2 = "upside_down_bit" in StateDict ? StateDict["upside_down_bit"] : (
            "minecraft:vertical_half" in StateDict ? StateDict["minecraft:vertical_half"] : false )
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        const Rotate = this.WeirdoDirection[State1]
        result = this.__Rodrigues_rotate__(result, Rotate.rotate_axis, Rotate.angle)
        if (State2 === true || State2 === "top") result = this.__Rodrigues_rotate__(result, Rotate.facing, Math.PI)
        result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
        return result
    }
    static BlockState_For_FunctionalRail(pos, StateDict, NoPosDelta=false){
        let rail_direction = "rail_direction" in StateDict ? StateDict["rail_direction"] : 0
        let new_pos = [pos[0], pos[1], pos[2]]
        let angle = 0

        if (rail_direction === 1) angle = Math.PI/2
        else if (rail_direction >= 2 && rail_direction <= 5) {
            if (!new_pos[2]) new_pos[1] = 1
            if (rail_direction === 2) angle = Math.PI/2
            else if (rail_direction === 3) angle = -Math.PI/2
            else if (rail_direction === 5) angle = Math.PI
        } else if (rail_direction >= 6 && rail_direction <= 9) {
            if (rail_direction === 7) angle = Math.PI/2
            else if (rail_direction === 8) angle = Math.PI
            else if (rail_direction === 9) angle = -Math.PI/2
        }

        new_pos[0] -= 0.5 ; new_pos[1] -= 0.5 ; new_pos[2] -= 0.5
        new_pos = this.__Rodrigues_rotate__(new_pos, [0,-1,0], angle)
        new_pos[0] += 0.5 ; new_pos[1] += 0.5 ; new_pos[2] += 0.5

        return new_pos
    }
    static BlockState_For_Trapdoor(pos, StateDict, NoPosDelta=false) {
        let State1 = "direction" in StateDict ? StateDict["direction"] : 0
        let State2 = "upside_down_bit" in StateDict ? StateDict["upside_down_bit"] : (
            "minecraft:vertical_half" in StateDict ? StateDict["minecraft:vertical_half"] : false )
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        const FacingRotate = this.Direction_2[State1]
        result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
        result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
        if (State2 === true || State2 === "top") result[1] += 13/16
        return result
    }
    static BlockState_For_Lantern(pos, StateDict, NoPosDelta=false) {
        let State = "hanging" in StateDict ? StateDict["hanging"] : false
        if (State) return [pos[0], pos[1]+7/16, pos[2]]
        else return pos
    }
    static BlockState_For_PointedDripstone(pos, StateDict, NoPosDelta=false) {
        let State = "hanging" in StateDict ? StateDict["hanging"] : true
        if (!State) {
            let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
            result = this.__Rodrigues_rotate__(result, [0,0,1], Math.PI)
            result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
            return result
        } else return pos
    }
    static BlockState_For_SnowLayer(pos, StateDict, NoPosDelta=false) {
        let State = "height" in StateDict ? StateDict["height"] : 0
        if (State) {
            if (pos[1] > 0) return [pos[0], (2/16)*(State+1), pos[2]]
            else return pos
        } else return pos
    }
    static BlockState_FacingDirection_1(pos, StateDict, NoPosDelta=false) {
        let facing_direction = "facing_direction" in StateDict ? StateDict["facing_direction"] : 0
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        if (NoPosDelta) result = [pos[0], pos[1], pos[2]]
        const FacingRotate = this.FacingDirection_1[facing_direction]
        FacingRotate.forEach(element => {
            result = this.__Rodrigues_rotate__(result, element.rotate_axis, element.angle)
        })
        if (!NoPosDelta) {result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5}
        return result
    }
    static BlockState_FacingDirection_2(pos, StateDict, NoPosDelta=false) {
        let facing_direction = "facing_direction" in StateDict ? StateDict["facing_direction"] : 0
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        if (NoPosDelta) result = [pos[0], pos[1], pos[2]]
        const FacingRotate = this.FacingDirection_2[facing_direction]
        result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
        if (!NoPosDelta) {result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5}
        return result
    }
    static BlockState_FacingDirection_3(pos, StateDict, NoPosDelta=false) {
        let facing_direction = "facing_direction" in StateDict ? StateDict["facing_direction"] : 0
        if (pos[0] != 0.375 && pos[0] != 0.625) return pos
        if (facing_direction == 1) facing_direction = 0

        let result = [pos[0] - 0.5, pos[1] - 0.375, pos[2] - 0.5]
        const FacingRotate = this.FacingDirection_1[facing_direction]
        FacingRotate.forEach(element => {
            result = this.__Rodrigues_rotate__(result, element.rotate_axis, element.angle)
        })
        result[0] += 0.5 ; result[1] += 0.375 ; result[2] += 0.5

        if (facing_direction > 0) {
            let dir = [0, -2/16, 0]
            FacingRotate.forEach(element => {
                dir = this.__Rodrigues_rotate__(dir, element.rotate_axis, element.angle)
            })
            result[0] += dir[0] ; result[1] += dir[1] ; result[2] += dir[2]
        }
        return result
    }
    static BlockState_Direction_1(pos, StateDict, NoPosDelta=false) {
        let direction = "direction" in StateDict ? StateDict["direction"] : 0
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        if (NoPosDelta) result = [pos[0], pos[1], pos[2]]
        const FacingRotate = this.Direction_1[direction]
        result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
        if (!NoPosDelta) {result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5}
        return result
    }
    static BlockState_PortalAxis(pos, StateDict, NoPosDelta=false) {
        let direction = "portal_axis" in StateDict ? StateDict["portal_axis"] : "unknown"
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        const FacingRotate = this.PortalAxis[direction]
        result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
        result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5
        return result
    }
    static BlockState_VerticalHalf(pos, StateDict, NoPosDelta=false) {
        let State = "top_slot_bit" in StateDict ? StateDict["top_slot_bit"] : (
            "minecraft:vertical_half" in StateDict ? StateDict["minecraft:vertical_half"] : false )
        if (State === "top" || State === true) return [pos[0], pos[1]+0.5, pos[2]]
        else return pos
    }
    static BlockState_GroundSignDirection(pos, StateDict, NoPosDelta=false) {
        let State = "ground_sign_direction" in StateDict ? StateDict["ground_sign_direction"] : 0
        let result = [pos[0] - 0.5, pos[1], pos[2] - 0.5]
        result = this.__Rodrigues_rotate__(result, [0,-1,0], State*Math.PI/8)
        result[0] += 0.5 ; result[2] += 0.5
        return result
    }
    static BlockState_BlockFace(pos, StateDict, NoPosDelta=false) {
        let State = "minecraft:block_face" in StateDict ? StateDict["minecraft:block_face"] : "up"
        return this.BlockState_FacingDirection_1(pos, {"facing_direction":this.BlockFace[State]}, NoPosDelta)
    }
    static BlockState_CardinalDirection(pos, StateDict, NoPosDelta=false) {
        let State = "minecraft:cardinal_direction" in StateDict ? StateDict["minecraft:cardinal_direction"] : "south"
        return this.BlockState_Direction_1(pos, {"direction":this.CardinalDirection[State]}, NoPosDelta)
    }
    static BlockState_LeverDirection(pos, StateDict, NoPosDelta=false) {
        let State = "lever_direction" in StateDict ? StateDict["lever_direction"] : "down_east_west"
        return this.BlockState_FacingDirection_1(pos, {"direction":this.LeverDirection[State]})
    }
    static BlockState_PillarAxis(pos, StateDict, NoPosDelta=false) {
        let State = "pillar_axis" in StateDict ? StateDict["pillar_axis"] : "y"
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        if (NoPosDelta) result = [pos[0], pos[1], pos[2]]
        const FacingRotate = this.PillarAxis[State]
        result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
        if (!NoPosDelta) {result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5}
        return result
    }
    static BlockState_Orientation(pos, StateDict, NoPosDelta=false) {
        let State = "orientation" in StateDict ? StateDict["orientation"] : "down_east"
        let result = [pos[0] - 0.5, pos[1] - 0.5, pos[2] - 0.5]
        if (NoPosDelta) result = [pos[0], pos[1], pos[2]]
        const FacingRotate = this.Orientation[State]
        result = this.__Rodrigues_rotate__(result, FacingRotate.rotate_axis, FacingRotate.angle)
        if (!NoPosDelta) {result[0] += 0.5 ; result[1] += 0.5 ; result[2] += 0.5}
        return result
    }
    static BlockState_TorchFacingDirection(pos, StateDict, NoPosDelta=false) {
        let State = "torch_facing_direction" in StateDict ? StateDict["torch_facing_direction"] : "top"
        if (State !== "unknown" && State !== "top") {
            let result = [pos[0], pos[1], pos[2]]
            result[0] -= 0.5 ; result[2] -= 0.5
            result = this.__Rodrigues_rotate__(result, [0,0,-1], Math.PI/6)
            result[1] += 1/8 ; result[2] -= 0.5
            if (State == "west") { 
                result[2] += 1
            } else if (State == "east") {
                result = this.__Rodrigues_rotate__(result, [0,-1,0], Math.PI)
                result[0] += 1
            } else if (State == "north") {
                result = this.__Rodrigues_rotate__(result, [0,-1,0], Math.PI/2)
            } else if (State == "south") {
                result = this.__Rodrigues_rotate__(result, [0,-1,0], -Math.PI/2)
                result[0] += 1; result[2] += 1
            } 
            return result
        } else return pos
    }

    //方块坐标变换选取
    static getStatesToChangeCoordinatesFunction(blockObject) {
        const FunctionList = this.getChangeCoordinatesFunctionList(blockObject)
        if (FunctionList.length) {
            return (pos, StateDict, NoPosDelta=false) => {
                FunctionList.forEach( (func) => {pos = func(pos, StateDict, NoPosDelta)})
                return pos
            } 
        } else return null
    }
    static getChangeCoordinatesFunctionList(blockObject) {
        const BlockID = blockObject.identifier
        const BlockState = blockObject.states
        if (Object.keys( BlockState ).length == 0) return []

        if (this.stairs_test.test(BlockID)) 
            return [this.BlockState_For_Stairs.bind(this)]
        else if (this.functional_rail_test.test(BlockID))
            return [this.BlockState_For_FunctionalRail.bind(this)]
        else if (this.facing_direction1_test.test(BlockID)) 
            return [this.BlockState_FacingDirection_1.bind(this)]
        else if (this.facing_direction3_test.test(BlockID)) 
            return [this.BlockState_FacingDirection_3.bind(this)]
        else if (this.trapdoor_test.test(BlockID)) 
            return [this.BlockState_For_Trapdoor.bind(this)]
        else if (this.lantern_test.test(BlockID)) 
            return [this.BlockState_For_Lantern.bind(this)]
        else if (BlockID === "minecraft:pointed_dripstone") 
            return [this.BlockState_For_PointedDripstone.bind(this)]
        else if (BlockID === "minecraft:snow_layer") 
            return [this.BlockState_For_SnowLayer.bind(this)]


        const FunctionArray = []

        if ("facing_direction" in BlockState) 
            FunctionArray.push( this.BlockState_FacingDirection_2.bind(this) )
        if ("direction" in BlockState || "coral_direction" in BlockState) 
            FunctionArray.push( this.BlockState_Direction_1.bind(this) )
        if (!BlockID.endsWith("double_slab") && (("minecraft:vertical_half" in BlockState) || 
            ("top_slot_bit" in BlockState)))
            FunctionArray.push( this.BlockState_VerticalHalf.bind(this) )
        if ("ground_sign_direction" in BlockState)
            FunctionArray.push( this.BlockState_GroundSignDirection.bind(this) )
        if ("minecraft:block_face" in BlockState)
            FunctionArray.push( this.BlockState_BlockFace.bind(this) )
        if ("minecraft:cardinal_direction" in BlockState)
            FunctionArray.push( this.BlockState_CardinalDirection.bind(this) )
        if ("lever_direction" in BlockState)
            FunctionArray.push( this.BlockState_LeverDirection.bind(this) )
        if ("pillar_axis" in BlockState)
            FunctionArray.push( this.BlockState_PillarAxis.bind(this) )
        if ("portal_axis" in BlockState)
            FunctionArray.push( this.BlockState_PortalAxis.bind(this) )
        if ("orientation" in BlockState)
            FunctionArray.push( this.BlockState_Orientation.bind(this) )
        if ("torch_facing_direction" in BlockState)
            FunctionArray.push( this.BlockState_TorchFacingDirection.bind(this) )

        return FunctionArray
    }


    static __State_Disable_Rerden__(StateDict, direction) {
        if ("multi_face_direction_bits" in StateDict) {
            let State = StateDict["multi_face_direction_bits"]
            State = State ? State : 63
            if (direction[1] < 0 && (State & 0b000001)) return true 
            else if (direction[1] > 0 && (State & 0b000010)) return true 
            else if (direction[2] < 0 && (State & 0b000100)) return true 
            else if (direction[2] > 0 && (State & 0b001000)) return true 
            else if (direction[0] < 0 && (State & 0b010000)) return true 
            else if (direction[0] > 0 && (State & 0b100000)) return true 
            else return false
        } else return true
    }



}


export {WaterTypes, LavaTypes, AirTypes, CopperGrateTypes}
export {BlockStateChangePos, ConnectTest}
