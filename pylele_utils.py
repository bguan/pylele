from math import inf, sqrt, sin, cos, atan2, pi
from pathlib import Path
from typing import Callable, Union

def radians(deg: float = 0) -> float:
    return deg * pi / 180


def degrees(rad: float = 0) -> float:
    return rad*180 / pi

def dimXY(
    start: tuple[float, float],
    path: list[tuple[float, float] | list[tuple[float, ...]]],
) -> tuple[float, float]:
    # Initialize min and max values
    min_x = max_x = start[0]
    min_y = max_y = start[1]
    for p_or_s in path:
        if isinstance(p_or_s, tuple) or len(p_or_s) == 1:
            x, y = p_or_s
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
        elif isinstance(p_or_s, list):
            for p in p_or_s:
                x, y = p[0], p[1]
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
    # Calculate spans and returns
    span_x = max_x - min_x
    span_y = max_y - min_y
    return (span_x, span_y)


def pathLen(
    path: list[tuple[float, ...]],
) -> float:
    acclen = 0

    lastX, lastY = path[0][0], path[0][1]
    for p in path[1:]:
        x, y = p[0], p[1]
        dx = x - lastX
        dy = y - lastY
        acclen += sqrt(dx**2 + dy**2)
        lastX, lastY = x, y

    return acclen

def pathBounds(
    path: list[tuple[float, ...]],
) -> tuple[tuple[float, float], tuple[float, float]]:
    x0, y0 = path[0][0], path[0][1]
    minX, minY, maxX, maxY = x0, y0, x0, y0

    for p in path[1:]:
        x, y = p[0], p[1]
        minX = x if x < minX else minX
        minY = y if y < minY else minY
        maxX = x if x > maxX else maxX
        maxY = y if y > maxY else maxY

    return ((minX, minY), (maxX, maxY))

def encureClosed2DPath(path: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if path[0][0] != path[-1][0] or path[0][1] != path[-1][1]:
        path.append(path[0])
    return path

def frange(start:float, stop:float, step:float):
    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1

def bezierSegment(p0, p1, p2, p3, num_points=50) -> list[tuple[float, float]]:
    """
    Generate points along a cubic Bézier curve.
    p0, p1, p2, p3 are the control points.
    """
    curve_points = []
    for t in frange(0., 1., 1./num_points):
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        curve_points.append((x, y))
    return curve_points

def superGradient(dy: float, dx: float) -> float:
    if dy == 0:
        return 0
    elif dx == 0:
        return inf if dy > 0 else -inf
    else:
        return dy/dx

def descreteBezierChain(
    xyGradPrePost: list[tuple[float, ...]],
    segsByLenFunc: Callable[[float], float],
) -> list[tuple[float, float]]:
    """
    Generate a chain of cubic Bézier curves from a list of points with directional derivatives.

    Parameters:
    xyGradPrePost (list[tuple[float, float, ...]]): 
        A list of points with optionalgradient, and pre/post expressed as ratio of span length.
        If no gradient is given, its computed from next point
        if no pre-control span length ratio is given, .5 is assumed.
        if no post-control span length ratio is given, .5 is assumed.
    segsByLenFunc (Callable[[float], float]): 
        A function that determines the number of segments for a given length.

    Returns:
    list[tuple[float, float]]: A list of points that make up the Bézier curves.

    Notes:
    Using x0, y0, grad0, ctrlLen0 from ratio against span length, x1, y1, to compute dx0, dy0.

    dy0/dx0 = grad0  so  dy0 = grad0 * dx0
    dx0^2 + dy0^2 = ctrlLen0^2  so  dy0 = sqrt(ctrlLen0^2 - dx0^2)

    ==> grad0 * dx0 = sqrt(ctrlLen0^2 - dx0^2)
    ==> grad0^2 * dx0^2 = ctrlLen0^2 - dx0^2
    ==> grad0^2 * dx0^2 + dx0^2 = ctrlLen0^2
    ==> (grad0^2 + 1) * dx0^2 = ctrlLen^2
    ==> dx0 = sqrt(ctrlLen^2 / (grad^2 + 1))

    Similarly, using x1, y1, grad1, ctrlLen1 from ratio against span length, x0, y0, to get dx1, dy1.
    """

    if len(xyGradPrePost) <= 0:
        return []
    elif len(xyGradPrePost) == 1:
        x0, y0 = xyGradPrePost[0][0:2]
        return [(x0, y0)]

    res:list[tuple[float, float]] = []
    prevX, prevY = xyGradPrePost[0][0:2]
    x1, y1 = xyGradPrePost[1][0:2]
    prevGrad = superGradient(x1-prevX, y1-prevY) if len(xyGradPrePost[0]) < 3 \
        else xyGradPrePost[0][2] 
    prevPreRatio = .5 if len(xyGradPrePost[0]) < 4 else xyGradPrePost[0][3]
    prevPostRatio = .5 if len(xyGradPrePost[0]) < 5 else xyGradPrePost[0][4]
    for i, xygpp in enumerate(xyGradPrePost):
        if i == 0:
            continue # skip first point
        curX, curY = xygpp[0:2]
        if len(xygpp) >= 3:
            curGrad = xygpp[2]
        elif i < len(xyGradPrePost) - 1:
            nextX, nextY = xyGradPrePost[i+1][0:2]
            curGrad = superGradient(nextX-curX, nextY-curY)
        else:
            curGrad = prevGrad
        curPreRatio = .5 if len(xygpp) < 4 else xygpp[3]
        curPostRatio = .5 if len(xygpp) < 5 else xygpp[4]
        spanLen = sqrt((curX - prevX)**2 + (curY - prevY)**2)
        segs = segsByLenFunc(spanLen)
        prevCtrlLen = prevPostRatio * spanLen
        prevDX = 0 if prevGrad == inf or prevGrad == -inf else sqrt(prevCtrlLen**2 / (prevGrad**2 + 1))
        prevDY = sqrt(prevCtrlLen**2 - prevDX**2)
        prevCtrlX = prevX + prevDX * ( 1 if curX >= prevX else -1)
        prevCtrlY = prevY + prevDY * ( 1 if curY >= prevY else -1)
        curCtrlLen = curPreRatio * spanLen
        curDX = 0 if curGrad == inf or curGrad == -inf else sqrt(curCtrlLen**2 / (curGrad**2 + 1))
        curDY = sqrt(curCtrlLen**2 - curDX**2)
        curCtrlX = curX - curDX * ( 1 if curX >= prevX else -1)
        curCtrlY = curY - curDY * ( 1 if curY >= prevY else -1)
        curvePts = bezierSegment(
            (prevX, prevY), (prevCtrlX, prevCtrlY), (curCtrlX, curCtrlY), (curX, curY), segs,
        )
        res.extend(curvePts)
        prevX, prevY, prevGrad, prevPreRatio, prevPostRatio = \
            curX, curY, curGrad, curPreRatio, curPostRatio
    return res


def simplifyLineSpline(
        start: tuple[float, float], 
        path: list[tuple[float, float] | list[tuple[float, ...]]],
) -> list[tuple[float, float]]:
    res = [ start ]
    for p in path:
        if isinstance(p, tuple):
            pt: tuple[float, float] = p
            res.append(pt)
        else:
            spline: list[tuple[float, ...]] = p
            res.extend([(spt[0], spt[1]) for spt in spline])
    return res

def isPathCounterClockwise(path2D: list[tuple[float, float]]) -> bool:
    """
    based on top answers that can handle edge cases of non convex path:
    https://stackoverflow.com/questions/1165647
    
    Sum over the edges, (x2 - x1)(y2 + y1). 
    If the result is positive the curve is counter-clockwise, 
    if it's negative the curve is clockwise. 
    """
    accSum  = 0
    for i, (x, y) in enumerate(path2D):
        nextPt = path2D[i+1] if i < len(path2D) - 1 else path2D[0]
        nextX, nextY = nextPt
        accSum += (nextX - x)*(nextY + y)
    return accSum > 0

def ensureFileExtn(path: Union[str, Path], extn: str) -> str:
    strpath = str(path)
    return strpath if strpath.endswith(extn) else strpath+extn