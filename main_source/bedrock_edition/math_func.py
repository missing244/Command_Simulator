from . import np
import math
from typing import List,Literal


def vector_add(v1:List[float], v2:List[float]) :
    return [v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2]]

def vector_remove(v1:List[float], v2:List[float]) :
    return [v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2]]

def vector_number_product(v1:List[float], value1:float) :
    return [v1[0]*value1, v1[1]*value1, v1[2]*value1]

def vector_number_div(v1:List[float], value1:float) :
    return [v1[0]*value1, v1[1]*value1, v1[2]*value1]

def vector_unit(v1:List[float]) :
    value1 = sum([v1[0]**2, v1[1]**2, v1[2]**2]) ** 0.5
    return [v1[0]/value1, v1[1]/value1, v1[2]/value1]

def vector_dot_product(v1:List[float], v2:List[float]) :
    return sum([v1[0]*v2[0], v1[1]*v2[1], v1[2]*v2[2]])

def vector_cross_product(v1:List[float], v2:List[float]) :
    x = v1[1] * v2[2] - v1[2] * v2[1]
    y = -(v1[0] * v2[2] - v1[2] * v2[0])
    z = v1[0] * v2[1] - v1[1] * v2[0]
    return [x,y,z]

def mc_rotation_pos(distance:float, ry:float, rx:float):
    ry1 = -ry*math.pi/180
    rx1 = -rx*math.pi/180
    z = distance*math.cos(ry1)*math.cos(rx1)
    x = distance*math.sin(ry1)*math.cos(rx1)
    y = distance*math.sin(rx1)
    return [x,y,z]

def mc_rotation_base_vector(ry:float, rx:float):
    v1 = mc_rotation_pos(1,ry,rx)
    v2 = mc_rotation_pos(1,ry,rx-90)
    v3 = mc_rotation_pos(1,ry-90,0)
    return [v3,v2,v1]

def vector_transform(vector:List[float], base_vector:List[List[float]]) :
    v1 = [0,0,0]
    for i in range(3) :
        v1 = vector_add(v1,vector_number_product(base_vector[i],vector[i]))
    return v1
    
def mitrax_transform(trans_vector:List[float],base_vector:List[List[float]]) :
    result:List[float] = []
    for i in range(3) :
        v1 = vector_transform(trans_vector[i],base_vector)
        result.append(v1)
    return result
    

def mc_point2level(point_value:int):
    a,b,c = 1,6,-point_value
    x1 = (-b + (b * b - 4 * a * c)**0.5) / (2 * a)
    x2 = (-b - (b * b - 4 * a * c)**0.5) / (2 * a)
    if 0 <= x1 < 17 : return int(x1)
    elif 0 <= x2 < 17 : return int(x2)
        
    a,b,c = 2.5,-40.5,-point_value+360
    x1 = (-b + (b * b - 4 * a * c)**0.5) / (2 * a)
    x2 = (-b - (b * b - 4 * a * c)**0.5) / (2 * a)
    if 17 <= x1 < 32 : return int(x1)
    elif 17 <= x2 < 32 : return int(x2)

    a,b,c = 4.5,-162.5,-point_value+2220
    x1 = (-b + (b * b - 4 * a * c)**0.5) / (2 * a)
    x2 = (-b - (b * b - 4 * a * c)**0.5) / (2 * a)
    if 32 <= x1 : return int(x1)
    elif 32 <= x2 : return int(x2)
        
def mc_next_levelup(level_value:int):
    if 0 <= level_value <= 15 : return (2 * level_value + 7)
    elif 16 <= level_value <= 30 : return (5 * level_value - 38)
    elif 31 <= level_value : return (9 * level_value - 158)
    
def mc_level2point(level_value:int): 
    if 0 <= level_value < 17 : a,b,c = 1,6,0
    if 17 <= level_value < 32 : a,b,c = 2.5,-40.5,360
    if 32 <= level_value : a,b,c = 4.5,-162.5,2220
    return a * level_value * level_value + b * level_value + c
    

def normal_distribution(x:float) -> float :
    return 1 - pow(math.e, 6*x*x*-1)


def rotation_angle(pos1:List[float], pos2:List[float]):
    v1 = [pos2[0]-pos1[0], pos2[1]-pos1[1], pos2[2]-pos1[2]]
    if sum(v1) < 0.0000001 : return (0.0, 0.0)

    v3 = vector_unit(v1)
    rx = math.asin(v3[1]) / math.pi * 180 * -1
    if sum((v3[0],v3[2])) < 0.0000001 : return (0.0, rx)
    
    ry = math.acos( v3[2] / ((v3[0] ** 2 + v3[2] ** 2) ** 0.5) )
    ry = ry / math.pi * 180 * (-1 if v1[0] > 0 else 1)
    return (ry,rx)
    
def rotate_compute(rotate_start:float, rotate_offset:str, mode:Literal["rx","ry"]="ry", can_outside_limit:bool=False) -> np.float32 :
    rotate_max = 180 if mode == "ry" else 90
    if rotate_offset[0] != "~" : rotate_value = np.float32(rotate_offset)
    if len(rotate_offset) == 1 : rotate_value = np.float32(rotate_start)
    else : rotate_value = rotate_start + float(rotate_offset[1:])

    if mode == "ry" : 
        rotate_value -= math.ceil(rotate_value / 360) * 360.0
        if rotate_value > 180 : rotate_value -= 360
        elif rotate_value < -180 : rotate_value += 360
        return np.float32(rotate_value)
    else : 
        if not can_outside_limit : 
            if rotate_value > 90 : return np.float32(90.0)
            if rotate_value < -90 : return np.float32(-90.0)
        else : return np.float32(rotate_value)

def mc_pos_compute(origin:List[float], pos_offset:List[str], rotate:List[float]):
    pos_result = list(origin)

    if pos_offset[0][0] == pos_offset[1][0] == pos_offset[2][0] == "^" :
        base1 = mc_rotation_base_vector(rotate[0],rotate[1])
        for i in range(3) :
            number1 = np.float32(pos_offset[i][1:]) if len(pos_offset[i][1:]) else 0
            pos_result[0] += number1 * base1[i][0]
            pos_result[1] += number1 * base1[i][1]
            pos_result[2] += number1 * base1[i][2]
        return pos_result
    else :
        for i in range(3) :
            if pos_offset[i][0] == "~" and len(pos_offset[i][1:]) == 0 : continue
            elif pos_offset[i][0] == "~" : pos_result[i] += np.float32(pos_offset[i][1:])
            elif "."  in pos_offset[i] : pos_result[i] = np.float32(pos_offset[i])
            else : pos_result[i] = np.float32(pos_offset[i]) + 0.5
        return pos_result


def version_compare(version1:List[int], version2:List[int]) :
    version_int1 = version1[0] * 1000000 + version1[1] * 1000 + version1[2]
    version_int2 = version2[0] * 1000000 + version2[1] * 1000 + version2[2]
    if version_int1 > version_int2 : return 1
    elif version_int1 < version_int2 : return -1
    else : return 0



