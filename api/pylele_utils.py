import math

def radians(deg: float = 0) -> float:
    return deg * math.pi / 180


def degrees(rad: float = 0) -> float:
    return rad*180 / math.pi

def accumDiv(x: float, n: int, div: float) -> float:
    return 0 if n <= 0 else x + accumDiv(x / div, n - 1, div)
