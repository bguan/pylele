#!/usr/bin/env python3

from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.misc.bezierTools import approximateQuadraticArcLength, quadraticPointAtT
from math import ceil, inf, sqrt, pi
import os
from pathlib import Path
import sys
from typing import Callable, Union
import time

def radians(deg: float = 0) -> float:
    return deg * pi / 180


def degrees(rad: float = 0) -> float:
    return rad * 180 / pi


def accumDiv(x: float, n: int, div: float) -> float:
    return 0 if n <= 0 else x + accumDiv(x / div, n - 1, div)


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


def pathBoundsArea(path: list[tuple[float, ...]]) -> float:
    (minX, minY), (maxX, maxY) = pathBounds(path)
    return (maxX - minX) * (maxY - minY)


def ensureClosed2DPath(path: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if path[0][0] != path[-1][0] or path[0][1] != path[-1][1]:
        path.append(path[0])
    return path


def frange(start: float, stop: float, step: float):
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
    for t in frange(0.0, 1.0, 1.0 / num_points):
        x = (
            (1 - t) ** 3 * p0[0]
            + 3 * (1 - t) ** 2 * t * p1[0]
            + 3 * (1 - t) * t**2 * p2[0]
            + t**3 * p3[0]
        )
        y = (
            (1 - t) ** 3 * p0[1]
            + 3 * (1 - t) ** 2 * t * p1[1]
            + 3 * (1 - t) * t**2 * p2[1]
            + t**3 * p3[1]
        )
        curve_points.append((x, y))
    return curve_points


def superGradient(dy: float, dx: float) -> float:
    if dy == 0:
        return 0
    elif dx == 0:
        return inf if dy > 0 else -inf
    else:
        return dy / dx


def descreteBezierChain(
    xyGradPrePost: list[tuple[float, ...]],
    segsByLenFunc: Callable[[float], float] = None,
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

    res: list[tuple[float, float]] = []
    prevX, prevY = xyGradPrePost[0][0:2]
    x1, y1 = xyGradPrePost[1][0:2]
    prevGrad = (
        superGradient(x1 - prevX, y1 - prevY)
        if len(xyGradPrePost[0]) < 3
        else xyGradPrePost[0][2]
    )
    prevPreRatio = 0.5 if len(xyGradPrePost[0]) < 4 else xyGradPrePost[0][3]
    prevPostRatio = 0.5 if len(xyGradPrePost[0]) < 5 else xyGradPrePost[0][4]
    for i, xygpp in enumerate(xyGradPrePost):
        if i == 0:
            continue  # skip first point
        curX, curY = xygpp[0:2]
        if len(xygpp) >= 3:
            curGrad = xygpp[2]
        elif i < len(xyGradPrePost) - 1:
            nextX, nextY = xyGradPrePost[i + 1][0:2]
            curGrad = superGradient(nextX - curX, nextY - curY)
        else:
            curGrad = prevGrad
        curPreRatio = 0.5 if len(xygpp) < 4 else xygpp[3]
        curPostRatio = 0.5 if len(xygpp) < 5 else xygpp[4]
        spanLen = sqrt((curX - prevX) ** 2 + (curY - prevY) ** 2)
        segs = spanLen if segsByLenFunc is None else segsByLenFunc(spanLen)
        prevCtrlLen = prevPostRatio * spanLen
        prevDX = (
            0
            if prevGrad == inf or prevGrad == -inf
            else sqrt(prevCtrlLen**2 / (prevGrad**2 + 1))
        )
        prevDY = sqrt(prevCtrlLen**2 - prevDX**2)
        prevCtrlX = prevX + prevDX * (1 if curX >= prevX else -1)
        prevCtrlY = prevY + prevDY * (1 if curY >= prevY else -1)
        curCtrlLen = curPreRatio * spanLen
        curDX = (
            0
            if curGrad == inf or curGrad == -inf
            else sqrt(curCtrlLen**2 / (curGrad**2 + 1))
        )
        curDY = sqrt(curCtrlLen**2 - curDX**2)
        curCtrlX = curX - curDX * (1 if curX >= prevX else -1)
        curCtrlY = curY - curDY * (1 if curY >= prevY else -1)
        curvePts = bezierSegment(
            (prevX, prevY),
            (prevCtrlX, prevCtrlY),
            (curCtrlX, curCtrlY),
            (curX, curY),
            segs,
        )
        res.extend(curvePts)
        prevX, prevY, prevGrad, prevPreRatio, prevPostRatio = (
            curX,
            curY,
            curGrad,
            curPreRatio,
            curPostRatio,
        )
    return res


# draw mix of straight lines from pt to pt, draw spline when given list of (x,y,dx,dy)
# use template pattern with optional supplied function to draw lines/curves
def lineSplineXY(
    start: tuple[float, float],
    path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
    segsByLenFunc: Callable[[float], float] = None,
    initFunc: Callable[[tuple[float, float]], any] = None,
    lineToFunc: Callable[[any, tuple[float, float]], any] = None,
    curveThruFunc: Callable[[any, list[tuple[float, float]]], any] = None,
    wrapUpFunc: Callable[[any], any] = None,
) -> any:
    result = [start] if initFunc is None else initFunc(start)

    for p_or_s in path:
        if isinstance(p_or_s, tuple):
            # a point so draw line
            lastX, lastY = p_or_s
            if lineToFunc is None:
                result.append((lastX, lastY))
            else:
                result = lineToFunc(result, (lastX, lastY))
        elif isinstance(p_or_s, list):
            # a list of points and gradients/tangents to trace spline thru
            spline: list[tuple[float, ...]] = p_or_s
            x1, y1 = spline[0][0:2]
            # insert first point if diff from last
            if lastX != x1 or lastY != y1:
                dx0 = x1 - lastX
                dy0 = y1 - lastY
                grad0 = superGradient(dy=dy0, dx=dx0)
                spline.insert(0, (lastX, lastY, grad0, 0, 0.5))
            curvePts = descreteBezierChain(spline, segsByLenFunc)
            if curveThruFunc is None:
                result.extend(curvePts)
            else:
                result = curveThruFunc(result, curvePts)
            lastX, lastY = spline[-1][0:2]
            if (lastX, lastY) != curvePts[-1]:
                if lineToFunc is None:
                    result.append((lastX, lastY))
                else:
                    result = lineToFunc(result, (lastX, lastY))

    return ensureClosed2DPath(result) if wrapUpFunc is None else wrapUpFunc(result)


def simplifyLineSpline(
    start: tuple[float, float],
    path: list[tuple[float, float] | list[tuple[float, ...]]],
) -> list[tuple[float, float]]:
    res = [start]
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
    accSum = 0
    for i, (x, y) in enumerate(path2D):
        nextPt = path2D[i + 1] if i < len(path2D) - 1 else path2D[0]
        nextX, nextY = nextPt
        accSum += (nextX - x) * (nextY + y)
    return accSum > 0

def file_replace_extension(path: str, ext: str):
    """ Replace the extension of a file path with a new extension """
    basefname, _ = os.path.splitext(path)
    return basefname + ext

def file_ensure_extension(path: Union[str, Path], extn: str) -> str:
    strpath = str(path)
    return strpath if strpath.endswith(extn) else strpath + extn

def make_or_exist_path(out_path) -> None:
    """Check a directory exist, and generate if not"""

    if not os.path.isdir(out_path):
        # Path.mkdir(out_path)
        os.makedirs(out_path)

    assert os.path.isdir(out_path), f"Cannot export to non directory: {out_path}"


def gen_stl_foo(outpath: str, bin_en=True) -> str:
    """generate an .stl file"""

    stlstr = """
        solid dart
        facet normal 0.00000E+000 0.00000E+000 -1.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 1.00000E+000 2.50000E-001 1.00000E+000
            endloop
        endfacet
        facet normal 0.00000E+000 0.00000E+000 -1.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
            endloop
        endfacet
        facet normal 8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 6.10000E+001 2.50000E-001 1.00000E+000
            endloop
        endfacet
        facet normal 8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
            endloop
        endfacet
        facet normal -8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
            endloop
        endfacet
        facet normal -8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 1.00000E+000 2.50000E-001 1.00000E+000
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
            endloop
        endfacet
        facet normal 3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
                vertex 1.00000E+000 2.50000E-001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
            endloop
        endfacet
        facet normal 3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
            endloop
        endfacet
        facet normal -3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
            endloop
        endfacet
        facet normal -3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 1.00000E+000
            endloop
        endfacet
        facet normal 0.00000E+000 0.00000E+000 1.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
            endloop
        endfacet
        facet normal 0.00000E+000 0.00000E+000 1.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
            endloop
        endfacet
        endsolid dart
        """

    # generate directory if it does not exist
    fparts = os.path.split(outpath)
    dirname = fparts[0]
    print(dirname)
    make_or_exist_path(dirname)

    fout = file_ensure_extension(outpath, ".stl")

    # write output file
    with open(fout, "w", encoding="UTF8") as f:
        f.write(stlstr)

    # check output file exists
    assert os.path.isfile(fout)
    return fout


def gen_scad_foo(outpath: str, module_en=True) -> str:
    """generate a .scad file"""

    if module_en:
        stlstr = """
        module box(w,h,d){
            cube([w,h,d]);
        }
        """
    else:
        stlstr = """
        difference {
            cube(20);
            translate(5, 5, 5) sphere(8);
        }
        """

    # generate directory if it does not exist
    fparts = os.path.split(outpath)
    dirname = fparts[0]
    
    if not dirname=="":
        print(dirname)
        make_or_exist_path(dirname)

    fout = file_ensure_extension(outpath, ".scad")

    # write output file
    with open(fout, "w", encoding="UTF8") as f:
        f.write(stlstr)

    # check output file exists
    assert os.path.isfile(fout)
    return fout


def gen_svg_foo(outpath: str) -> str:
    """generate a .svg file"""

    stlstr = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE svg>
        <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <!-- A red circle -->
        <circle cx="100" cy="100" r="50" fill="red" />
        </svg>
        """

    # generate directory if it does not exist
    fparts = os.path.split(outpath)
    dirname = fparts[0]
    print(dirname)
    make_or_exist_path(dirname)

    fout = file_ensure_extension(outpath, ".svg")

    # write output file
    with open(fout, "w", encoding="UTF8") as f:
        f.write(stlstr)

    # check output file exists
    assert os.path.isfile(fout)
    return fout

def gen_step_foo(outpath: str) -> str:
    """generate a .step file"""

    stlstr = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Open CASCADE Model'),'2;1');
FILE_NAME('Open CASCADE Shape Model','2025-01-05T00:38:39',('Author'),(
    'Open CASCADE'),'Open CASCADE STEP processor 7.7','Open CASCADE 7.7'
,'Unknown');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1 = APPLICATION_PROTOCOL_DEFINITION('international standard',
'automotive_design',2000,#2);
#2 = APPLICATION_CONTEXT(
'core data for automotive mechanical design processes');
#3 = SHAPE_DEFINITION_REPRESENTATION(#4,#10);
#4 = PRODUCT_DEFINITION_SHAPE('','',#5);
#5 = PRODUCT_DEFINITION('design','',#6,#9);
#6 = PRODUCT_DEFINITION_FORMATION('','',#7);
#7 = PRODUCT('Open CASCADE STEP translator 7.7 2',
'Open CASCADE STEP translator 7.7 2','',(#8));
#8 = PRODUCT_CONTEXT('',#2,'mechanical');
#9 = PRODUCT_DEFINITION_CONTEXT('part definition',#2,'design');
#10 = ADVANCED_BREP_SHAPE_REPRESENTATION('',(#11,#15),#27);
#11 = AXIS2_PLACEMENT_3D('',#12,#13,#14);
#12 = CARTESIAN_POINT('',(0.,0.,0.));
#13 = DIRECTION('',(0.,0.,1.));
#14 = DIRECTION('',(1.,0.,-0.));
#15 = MANIFOLD_SOLID_BREP('',#16);
#16 = CLOSED_SHELL('',(#17));
#17 = ADVANCED_FACE('',(#18),#22,.T.);
#18 = FACE_BOUND('',#19,.T.);
#19 = VERTEX_LOOP('',#20);
#20 = VERTEX_POINT('',#21);
#21 = CARTESIAN_POINT('',(6.123233995737E-16,-1.499759782662E-31,-10.));
#22 = SPHERICAL_SURFACE('',#23,10.);
#23 = AXIS2_PLACEMENT_3D('',#24,#25,#26);
#24 = CARTESIAN_POINT('',(0.,0.,0.));
#25 = DIRECTION('',(0.,0.,1.));
#26 = DIRECTION('',(1.,0.,0.));
#27 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) 
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#31)) GLOBAL_UNIT_ASSIGNED_CONTEXT(
(#28,#29,#30)) REPRESENTATION_CONTEXT('Context #1',
'3D Context with UNIT and UNCERTAINTY') );
#28 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );
#29 = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );
#30 = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );
#31 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#28,
'distance_accuracy_value','confusion accuracy');
#32 = PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(#7));
ENDSEC;
END-ISO-10303-21;
        """

    # generate directory if it does not exist
    fparts = os.path.split(outpath)
    dirname = fparts[0]
    print(dirname)
    make_or_exist_path(dirname)

    fout = file_ensure_extension(outpath, ".step")

    # write output file
    with open(fout, "w", encoding="UTF8") as f:
        f.write(stlstr)

    # check output file exists
    assert os.path.isfile(fout)
    return fout

def getFontname2FilepathMap() -> dict[str, str]:

    font2path: dict[str, str] = {}

    # Define directories to search for fonts
    if sys.platform == "win32":
        font_dirs = [os.path.join(os.environ["WINDIR"], "Fonts")]
    elif sys.platform == "darwin":
        font_dirs = [
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
        ]
    else:  # Assume Linux or other UNIX-like system
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
        ]

    def list_fonts(directory):
        fonts = []

        # Helper function to get the string by its name ID
        def get_name(font: TTFont, nameID: int):
            name_record = font["name"].getName(
                nameID=nameID, platformID=3, platEncID=1
            )
            if name_record is None:
                name_record = font["name"].getName(
                    nameID=nameID, platformID=1, platEncID=0
                )
            return name_record.toStr() if name_record else "Unknown"

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith((".ttf", ".otf")):
                    font_path = os.path.join(root, file)
                    try:
                        font = TTFont(font_path)
                        # Get the Font Family Name (name ID 1)
                        family = get_name(font, 1)
                        # Get the Font Subfamily Name (Style) (name ID 2)
                        style = get_name(font, 2)

                        font_name = (
                            family
                            if style == "Normal" or style == "Regular"
                            else family + " " + style
                        )
                        fonts.append((font_name, font_path))
                    except Exception as e:
                        print(f"Error reading {font_path}: {e}")
        return fonts

    # Collect fonts from all directories
    all_fonts = []
    for directory in font_dirs:
        if os.path.exists(directory):
            all_fonts.extend(list_fonts(directory))

    # Print the font names and paths
    for name, path in all_fonts:
        # print(f"Font: {name}, Path: {path}")
        font2path[name] = path

    return font2path


def textToGlyphsPaths(
    font_path: str,
    text: str,
    font_size: float = 24, # in points
    translate: tuple[float, float]=(0, 0),
    dimToSegs: Callable[[float], float] = lambda x: 36*x,
) -> list[list[tuple[float, float]]]:

    class PathExtractor(BasePen):
        def __init__(self, glyphSet):
            super().__init__(glyphSet)
            self.paths = []

        def _moveTo(self, p0):
            self.current_path = [("moveTo", p0)]

        def _lineTo(self, p1):
            self.current_path.append(("lineTo", p1))

        def _curveToOne(self, p1, p2, p3):
            self.current_path.append(("curveTo", p1, p2, p3))

        def _closePath(self):
            self.current_path.append(("closePath",))
            self.paths.append(self.current_path)
            self.current_path = []

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font["cmap"].getBestCmap()
    units_per_em = font['head'].unitsPerEm

    # Simplistic approach: assume ASCII and get glyph names
    glyph_names = []
    for char in text:
        code_point = ord(char)
        glyph_name = cmap.get(code_point)
        if glyph_name:
            glyph_names.append(glyph_name)
        else:
            print(f"Character '{char}' not found in the font.")
            glyph_names.append(".notdef")

    def pointsToFontScale(pts: float) -> float:
        pts_per_inch = 72
        resolution = 72
        return pts * resolution / ( pts_per_inch * units_per_em )

    scale = pointsToFontScale(font_size)

    # Initialize variables for positioning
    current_x = 0
    glyphs_paths = []

    for glyph_name in glyph_names:
        glyph = glyph_set[glyph_name]
        extractor = PathExtractor(glyph_set)
        glyph.draw(extractor)
        # Apply transformations (scaling and translation)
        transformed_paths = []
        for path in extractor.paths:
            transformed_path = []
            assert path[0][0] == "moveTo"
            start: tuple[float, float] = None
            for i, cmd in enumerate(path):
                if cmd[0] == "moveTo":
                    p = (
                        cmd[1][0] * scale + current_x + translate[0],
                        cmd[1][1] * scale + translate[1],
                    )
                    if i == 0:
                        start = p
                    transformed_path.append(p)
                elif cmd[0] == "lineTo":
                    p = (
                        cmd[1][0] * scale + current_x + translate[0],
                        cmd[1][1] * scale + translate[1],
                    )
                    transformed_path.append(p)
                elif cmd[0] == "curveTo":
                    p1 = (
                        cmd[1][0] * scale + current_x + translate[0],
                        cmd[1][1] * scale + translate[1],
                    )
                    p2 = (
                        cmd[2][0] * scale + current_x + translate[0],
                        cmd[2][1] * scale + translate[1],
                    )
                    p3 = (
                        cmd[3][0] * scale + current_x + translate[0],
                        cmd[3][1] * scale + translate[1],
                    )
                    dim = approximateQuadraticArcLength(p1, p2, p3)
                    numSegs = ceil(dimToSegs(dim))
                    for t in frange(0., 1., 1./numSegs):
                        transformed_path.append(quadraticPointAtT(p1, p2, p3, t))
                    transformed_path.append(p3)
                elif cmd[0] == "closePath":
                    assert i == len(path) - 1
                    if transformed_path[-1] != start:
                        transformed_path.append(start)
            transformed_paths.append(transformed_path)
        glyphs_paths.append(transformed_paths)

        # Advance current_x based on glyph's advance width
        advance_width = glyph.width * scale
        current_x += advance_width

    return glyphs_paths

def snake2camel(word):
    """Convert snake_case to CamelCase"""
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case/28774760#28774760
    return ''.join(x.capitalize() or '_' for x in word.split('_'))

def camel2snake(word):
    """Convert CamelCase to snake_case"""
    # https://stackoverflow.com/a/28774760/7094647
    snake = "".join(["_"+c.lower() if c.isupper() else c for c in s])
    return snake[1:] if snake.startswith("_") else snake

def distance(p0, p1):
    """ Calculates distance in multidimensional space """

    assert len(p0) == len(p1)
    # assert len(p1) == 3

    square_sum = 0
    for i in range(len(p0)):
        square_sum  += (p0[i] - p1[i])**2

    return sqrt( square_sum )

def wait_assert_file_exist(fname, timeout=1, nretry=10):
    """ Wait a bit for a file, assert if not available after timeout """

    retry = 0
    while retry < nretry and not os.path.isfile(fname):
        print(
            f"Failed to detect file {fname}, retry after {timeout} seconds..."
        )
        time.sleep(timeout)
        timeout *= 2
        retry += 1
        if os.path.isfile(fname):
            break

    assert os.path.isfile(fname), f"Failed to detect file {fname}"