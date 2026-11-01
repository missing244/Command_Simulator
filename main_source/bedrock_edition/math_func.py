from . import np
import math
from typing import List, Literal, Union, Tuple



def mc_rotation_pos(distance:float, ry:float, rx:float):
    ry1 = -ry*math.pi/180
    rx1 = -rx*math.pi/180
    z = distance*math.cos(ry1)*math.cos(rx1)
    x = distance*math.sin(ry1)*math.cos(rx1)
    y = distance*math.sin(rx1)
    return [round(x, 6), round(y, 6), round(z, 6)]

def mc_rotation_base_vector(ry:float, rx:float):
    v1 = mc_rotation_pos(1, ry, rx)
    v2 = mc_rotation_pos(1, ry, rx-90)
    v3 = mc_rotation_pos(1, ry-90, 0)
    return [v3, v2, v1]



class Vector3:
    """三维向量，支持常用向量运算"""
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = np.float32(x)
        self.y = np.float32(y)
        self.z = np.float32(z)

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> 'Vector3':
        return self * scalar

    def __truediv__(self, scalar: float) -> 'Vector3':
        if scalar == 0: raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> 'Vector3':
        return Vector3(-self.x, -self.y, -self.z)


    def dot(self, other: 'Vector3') -> np.float32:
        """点积"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vector3') -> 'Vector3':
        """叉积"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self) -> np.float32:
        """模长"""
        return np.float32( math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2) )

    def length_squared(self) -> np.float32:
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def normalize(self) -> 'Vector3':
        """单位化"""
        length = self.length()
        if length == 0: raise ValueError("Cannot normalize a zero vector")
        return self / length

    def to_minecraft_rotation(self) -> Tuple[float, float]:
        """
        返回此方向向量对应的 Minecraft 旋转角 (yaw, pitch)，单位为度。
        与 mc_rotation_pos 相反，用于从方向向量反推视角角度。
        """
        # 避免零向量导致除零，返回默认水平朝向
        if self.length_squared() < 1e-12: return 0.0, 0.0

        v = self.normalize()

        # 俯仰角：asin(y)，注意 Minecraft 中向下为正，所以取负
        pitch = -math.degrees(math.asin(v.y))

        # 水平分量平方和，用于检测是否接近垂直（此时 yaw 无意义，设为 0）
        horizontal_sq = v.x * v.x + v.z * v.z
        if horizontal_sq < 1e-12: return 0.0, pitch

        # 偏航角：acos(z / sqrt(x^2+z^2))，再根据 x 的正负调整符号到 [-180, 180]
        yaw = math.degrees(math.acos(v.z / math.sqrt(horizontal_sq)))
        if v.x > 0: yaw = -yaw

        return yaw, pitch


    def __repr__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def __iter__(self) :
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, key) -> np.float32 :
        if key == 0 : return self.x
        if key == 1 : return self.y
        if key == 2 : return self.z

class Matrix4x4:
    """
    4x4 齐次变换矩阵，可用于平移、旋转、缩放等。
    内部存储为按行排列的 4×4 列表。
    """
    __slots__ = ('m',)

    def __init__(self, m: List[List[float]]):
        if len(m) != 4 or any(len(row) != 4 for row in m): raise ValueError("Matrix must be 4x4")
        self.m:List[List[np.float32]] = [list(row) for row in m]  # 深拷贝，防止外部修改
        for i in self.m :
            for j, k in enumerate(i) : i[j] = np.float32(k)

    @classmethod
    def identity(cls) -> 'Matrix4x4':
        return cls([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    @classmethod
    def translation(cls, x: float, y: float, z: float) -> 'Matrix4x4':
        return cls([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ])

    @classmethod
    def scale(cls, sx: float, sy: float, sz: float) -> 'Matrix4x4':
        return cls([
            [sx, 0,  0,  0],
            [0,  sy, 0,  0],
            [0,  0,  sz, 0],
            [0,  0,  0,  1]
        ])

    @classmethod
    def from_minecraft_rotation(cls, ry: float, rx: float) -> 'Matrix4x4':
        """根据 Minecraft 的旋转角度 (yaw, pitch) 创建旋转矩阵"""
        left, up, forward = mc_rotation_base_vector(ry, rx)
        return cls([
            [left[0], up[0], forward[0], 0],
            [left[1], up[1], forward[1], 0],
            [left[2], up[2], forward[2], 0],
            [0,        0,     0,          1]
        ])


    def __add__(self, other: 'Matrix4x4') -> 'Matrix4x4':
        """矩阵加法"""
        if not isinstance(other, Matrix4x4):
            raise TypeError("只能与另一个 Matrix4x4 相加")
        return Matrix4x4([
            [self.m[i][j] + other.m[i][j] for j in range(4)]
            for i in range(4)
        ])

    def __sub__(self, other: 'Matrix4x4') -> 'Matrix4x4':
        """矩阵减法"""
        if not isinstance(other, Matrix4x4):
            raise TypeError("只能与另一个 Matrix4x4 相减")
        return Matrix4x4([
            [self.m[i][j] - other.m[i][j] for j in range(4)]
            for i in range(4)
        ])

    def __mul__(self, vector: Vector3) -> Vector3:
        """
        矩阵乘以向量（隐式地将向量视为齐次坐标 (x,y,z,1)），
        执行线性变换（包含平移）。
        """
        x = vector.x
        y = vector.y
        z = vector.z
        w = self.m[3][0]*x + self.m[3][1]*y + self.m[3][2]*z + self.m[3][3]
        if w == 0: raise ZeroDivisionError("Homogeneous coordinate w is zero")
        new_x = self.m[0][0]*x + self.m[0][1]*y + self.m[0][2]*z + self.m[0][3]
        new_y = self.m[1][0]*x + self.m[1][1]*y + self.m[1][2]*z + self.m[1][3]
        new_z = self.m[2][0]*x + self.m[2][1]*y + self.m[2][2]*z + self.m[2][3]
        return Vector3(new_x / w, new_y / w, new_z / w)


    def transform_point(self, point: Vector3) -> Vector3:
        """变换点（考虑平移）"""
        return self * point

    def transform_vector(self, vector: Vector3) -> Vector3:
        """变换方向向量（忽略平移，即 w=0）"""
        x, y, z = vector.x, vector.y, vector.z
        new_x = self.m[0][0]*x + self.m[0][1]*y + self.m[0][2]*z
        new_y = self.m[1][0]*x + self.m[1][1]*y + self.m[1][2]*z
        new_z = self.m[2][0]*x + self.m[2][1]*y + self.m[2][2]*z
        return Vector3(new_x, new_y, new_z)


    def __repr__(self) -> str:
        rows = [", ".join(f"{val.value:.16f}" for val in row) for row in self.m]
        return "[" + "\n".join(rows) + "]"








