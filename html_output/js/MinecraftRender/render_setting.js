export const FaceDefine = {
    "north": {
        dir: [0, 0, -1], corners: [
          { pos:[1, 0, 0], uv:[0, 0] }, { pos:[0, 0, 0], uv:[16, 0] },
          { pos:[1, 1, 0], uv:[0, 16] }, { pos:[0, 1, 0], uv:[16, 16] },
        ]
    },
    "south": {
        dir: [0, 0, 1], corners: [
          { pos:[0, 0, 1], uv:[0, 0] }, { pos:[1, 0, 1], uv:[16, 0] },
          { pos:[0, 1, 1], uv:[0, 16] }, { pos:[1, 1, 1], uv:[16, 16] },
        ]
    },
    "west": {
        dir: [-1, 0, 0], corners: [
          { pos:[0, 1, 0], uv:[0, 16] }, { pos:[0, 0, 0], uv:[0, 0] },
          { pos:[0, 1, 1], uv:[16, 16] }, { pos:[0, 0, 1], uv:[16, 0] }
        ]
    },
    "east": {
        dir: [1, 0, 0], corners: [
          { pos:[1, 1, 1], uv:[0, 16] }, { pos:[1, 0, 1], uv:[0, 0] },
          { pos:[1, 1, 0], uv:[16, 16] }, { pos:[1, 0, 0], uv:[16, 0] },
        ]
    },
    "top": {
        dir: [0, 1, 0], corners: [
          { pos:[0, 1, 1], uv:[16, 16] }, { pos:[1, 1, 1], uv:[0, 16] },
          { pos:[0, 1, 0], uv:[16, 0] }, { pos:[1, 1, 0], uv:[0, 0] },
        ]
    },
    "bottom": {
        dir: [0, -1, 0], corners: [
          { pos:[1, 0, 1], uv:[16, 0] }, { pos:[0, 0, 1], uv:[0, 0] },
          { pos:[1, 0, 0], uv:[16, 16] }, { pos:[0, 0, 0], uv:[0, 16] },
        ]
    }
}

export const ModelDefine = {
    "same_6": {"north": 0, "south": 0, "west": 0, "east": 0, "top": 0, "bottom": 0},   //6面相同
    "same_4": {"north": 0, "south": 0, "west": 0, "east": 0, "top": 1, "bottom": 2},   //4面相同
    "same_4-2": {"north": 0, "south": 0, "west": 0, "east": 0, "top": 1, "bottom": 1}, //4-2面相同
    "same_1": {"north": 0, "south": 1, "west": 2, "east": 3, "top": 4, "bottom": 5}    //6面都不相同
}