import math

def radians(deg: float = 0) -> float:
    return deg * math.pi / 180


def degrees(rad: float = 0) -> float:
    return rad*180 / math.pi
