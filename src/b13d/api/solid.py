#!/usr/bin/env python3

"""
    Abstract Base and Concrete Classes for all Pylele Solid objects
"""

from __future__ import annotations

import datetime
import importlib
import platform
import time
import trimesh
from json_tricks import dumps

from pathlib import Path
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from copy import deepcopy

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
                
from b13d.api.core import ShapeAPI, Shape, Fidelity, Implementation, StringEnum, supported_apis
from b13d.api.constants import ColorEnum, FIT_TOL, FILLET_RAD, DEFAULT_BUILD_DIR, DEFAULT_TEST_DIR, ColorEnum
from b13d.api.utils import make_or_exist_path
from b13d.conversion.scad2stl import scad2stl_parser

def main_maker(module_name, class_name, args=None):
    """Generate a main function for a Solid instance"""
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    solid = class_(args=args)
    solid.export_args()  # includes export_configuration for LeleBase
    out_fname = solid.export_stl()
    return solid, out_fname

def test_iteration(module, component, test, api, args=None):
    """Helper to generate a testcase launching the main function in a module"""
    mod = importlib.import_module(module)

    if args is None:
        largs = []
    else:
        largs = deepcopy(args)

    print(f'#### Test {component} {test} {api}')
    outdir = os.path.join(DEFAULT_TEST_DIR,component,test,api)
    largs += [
        '-o', outdir,
        '-i', api,
        '-odoff', # do not append date
        '-stlc' # enable stl volume analysis during test
                ]
    print(largs)
    mod.main(args=largs)
    pass


def test_loop(module, apis=None, tests=None):  # ,component):
    """loop over a list of tests"""

    # generate a default testcase if not specified
    if tests is None:
        tests = {
            "default": [],
        }

    if apis is None:
        apis = supported_apis()

    test_count = 0
    for test,args in tests.items():
        for api in apis:
            try:
                test_iteration(
                            module=module,
                            component=module,
                            test=f'{test_count:02d}_{test}',
                            api=api,
                            args=args,
                            )
            except:
                assert False, f'module: {module}, test: {test}, api: {api},\nargs:{args}'
            
        test_count += 1


class PrettyPrintDict(dict):
    """A class to print all entries of a dict"""

    def __init__(self, dictdata):
        self.dict = dictdata

    def __repr__(self):
        properties = "\n".join(f"{key}={value!r}" for key, value in self.dict.items())
        return properties


def export_dict2text(outpath, fname, dictdata, fmt='.txt') -> str:
    """save info in input dictionary to output file"""

    if isinstance(dictdata, Namespace):
        dictdata = vars(dictdata)

    if isinstance(dictdata, dict) and fmt=='.txt':
        dictdata = PrettyPrintDict(dictdata)

    out_fname = os.path.join(outpath, fname+fmt)
    print(out_fname)
    with open(out_fname, "w", encoding="UTF8") as f:
        if fmt=='.txt':
            f.write(repr(dictdata))
        elif fmt=='.json':
            f.write( dumps( dictdata, indent=4 ) )
        else:
            assert fmt in ['.txt','.json'], f'ERROR: export format {fmt} not supported!'

    assert os.path.isfile(out_fname)

def volume_match_reference(
    volume: float,
    reference: float,
    tolerance: float = 0.1,
) -> bool:
    """True if volume matches reference within tolerance"""

    if reference is None:
        return True

    if abs(volume - reference) <= abs(reference * tolerance):
        return True

    return False

def stl_report_metrics(out_fname: str) -> dict:
    assert os.path.isfile(out_fname), f"File {out_fname} does not exist!!!"
    mesh = trimesh.load_mesh(out_fname)
    # assert mesh.is_watertight
    print(f"mesh_volume: {mesh.volume}")
    print(f"mesh.convex_hull.volume: {mesh.convex_hull.volume}")
    print(f"mesh.bounding_box: {mesh.bounding_box.extents}")
    # mesh.show() does not work
    rpt = {}
    rpt["volume"] = mesh.volume
    rpt["convex_hull_volume"] = mesh.convex_hull.volume
    rpt["bounding_box_x"] = mesh.bounding_box.extents[0]
    rpt["bounding_box_y"] = mesh.bounding_box.extents[1]
    rpt["bounding_box_z"] = mesh.bounding_box.extents[2]
    return rpt

def stl_check_volume(
    out_fname: str,
    check_en: bool = True,
    reference_volume: float = None,
    reference_volume_tolerance: float = 10
) -> dict:
    """Check the volume of an .stl mesh against a reference value"""
    rpt = {}
    if check_en:
        rpt = stl_report_metrics(out_fname)
        rpt['pass'] = volume_match_reference(
            volume=rpt['volume'],
            reference=reference_volume,
            tolerance=reference_volume_tolerance/100
        )

        if not rpt['pass']:
            print(
                f'## WARNING!!! volume: {rpt["volume"]}, reference: {reference_volume}'
                )

    return rpt

def solid_operand(joiner)->ShapeAPI:
    """ returns a ShapeAPI compatible operand """
    if joiner is None:
        return joiner
    if isinstance(joiner,Solid):
        joiner.gen_full()
        return joiner.shape
    if isinstance(joiner, ShapeAPI):
        return joiner

def lele_solid_parser(parser=None):
    """
    Solid Command Line Interface
    """
    if parser is None:
        parser = ArgumentParser(description="Solid Configuration")

    ## options ######################################################
    parser.add_argument(
        "-i",
        "--implementation",
        help="Underlying engine implementation",
        type=Implementation,
        choices=list(Implementation),
        default=Implementation.MANIFOLD,
    )
    parser.add_argument(
        "-f",
        "--fidelity",
        help="Mesh fidelity for smoothness, default low",
        type=Fidelity,
        choices=list(Fidelity),
        default=Fidelity.LOW,
    )
    parser.add_argument(
        "-c",
        "--color",
        help="Color.",
        type=str,
        choices=ColorEnum._member_names_,
        default=ColorEnum.ORANGE,
    )
    parser.add_argument(
        "-o",
        "--outdir",
        help="Output directory.",
        type=str,
        default=DEFAULT_BUILD_DIR,
    )
    parser.add_argument(
        "-odoff",
        "--outdir_date_off",
        help="Disable appending name to output directory",
        action="store_true",
    )
    parser.add_argument(
        "-C",
        "--is_cut",
        help="This solid is a cutting.",
        action="store_true",
    )
    parser.add_argument(
        "-stlc",
        "--stl_check_en",
        help="Calculate output mesh volume for report",
        action="store_true",
    )
    parser.add_argument(
        "-refv",
        "--reference_volume",
        help="Reference volume in mm2. If specified, generate assertion "
        + "if volume of generated .stl file differs from the reference",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-refvt",
        "--reference_volume_tolerance",
        help="Reference volume tolerance in percentage",
        type=float,
        default=10,
    )
    parser.add_argument(
        "-S",
        "--split",
        help="Split in half",
        action="store_true",
    )

    parser = scad2stl_parser(parser=parser)

    return parser


class Solid(ABC):
    """
    Pylele Generic Solid Body
    """

    cli          : Namespace = None
    isCut        : bool = False
    outdir       : str = ''
    fileNameBase : str = ''
    api          : ShapeAPI = None
    shape        : Shape = None
    parts        : list = None

    def __init__(
        self,
        isCut: bool = False,
        args=None,
        cli=None,
    ):
        if cli is None:
            self.cli = self.parse_args(args=args)
        else:
            self.cli = cli

        self.isCut = self.cli.is_cut or isCut
        self.outdir = self.cli.outdir

        self.fileNameBase = self.__class__.__name__
        if self.isCut:
            self.fileNameBase += '_cut'

    @abstractmethod
    def gen(self) -> Shape:
        """Generate Shape"""
        # self.shape =  ...
        pass

    def has_shape(self) -> bool:
        """Return True if Solid has Shape attribute"""
        if not hasattr(self, "shape") or self.shape is None:
            return False
        return True

    def check_has_shape(self):
        """Assert if Solid does not have shape attribute"""
        assert self.has_shape()
        assert isinstance(self.shape, Shape)

    def has_api(self) -> bool:
        """Return True if Solid has api attribute"""
        if not hasattr(self, "api") or self.api is None:
            return False
        return True

    def check_has_api(self):
        """Assert if Solid does not have api attribute"""
        assert self.has_api()
        assert isinstance(self.api, ShapeAPI)

    def has_parts(self) -> bool:
        """Return True if Solid is an assembly with a list of parts attribute"""
        if hasattr(self, "parts") and isinstance(self.parts, list):
            return True
        return False

    def get_parts(self) -> list:
        """Returns the parts lists of an assembly"""
        if self.has_parts():
            return self.parts
        return []

    def add_part(self, part):
        """Add a solid part to the parts list of this assembly"""
        assert isinstance(part, Solid)

        if self.has_parts():
            self.parts.append(part)
        else:
            self.parts = [part]

        if part.has_parts():
            self.parts.append(part.parts)

    def add_parts(self, parts):
        """Add a list of solid parts to the parts list of this assembly"""
        assert isinstance(parts, list) or isinstance(parts, Solid), print(parts)

        if isinstance(parts, Solid):
            if parts.has_parts():
                parts = parts.parts
            else:
                print("# Warning: Solid has no parts!")

        if self.has_parts():
            self.parts += parts
        else:
            self.parts = parts

    def gen_full(self):
        """ Generate shape if attribute not present """
        if not self.has_shape():
            print(f"# Shape missing: Generating {self.fileNameBase}... ")

            if not self.has_api():
                print(f"# Shape missing API: Configuring {self.fileNameBase}... ")
                self.configure()
                self.check_has_api()
                print(f"# Done configuring API! {self.fileNameBase}")

            self.shape = self.gen()
            print(f"# Done generating shape! {self.fileNameBase}")
        self.check_has_shape()
        return self.shape

    def gen_parser(self, parser=None):
        """
        Solid Command Line Interface
        """
        return lele_solid_parser(parser=parser)

    def parse_args(self, args=None):
        """Parse Command Line Arguments"""
        return self.gen_parser().parse_args(args=args)

    def configure(self):
        """Configure Solid, and save self.cli"""
        self.api:ShapeAPI = self.cli.implementation.get_api(self.cli.fidelity)
        self.check_has_api()
        if self.cli.implementation == Implementation.SOLID2:
            self.api.setCommand(self.cli.openscad)
            self.api.setImplicit(self.cli.implicit)

    def cut(self, cutter: Solid) -> Solid:
        """ Cut solid with other shape """
        self.gen_full()
        self.shape = self.shape.cut(
            solid_operand(cutter)
        )
        return self

    def intersection(self, intersector: Solid) -> Solid:
        """ Intersect solid with other shape """
        self.gen_full()
        self.shape = self.shape.intersection(
            solid_operand(intersector)
        )
        return self

    def _make_out_path(self):
        """Generate an output directory"""
        main_out_path = os.path.join(Path.cwd(), self.outdir)
        make_or_exist_path(main_out_path)

        outfname = self.fileNameBase
        if not self.cli.outdir_date_off:
            outfname += (
                (datetime.datetime.now().strftime("-%y%m%d-%H%M%S-"))
                + self.cli.implementation.code()
                + self.cli.fidelity.code()
            )
        out_path = os.path.join(main_out_path, outfname)
        make_or_exist_path(out_path)
        return out_path

    def export_args(self):
        """Export Pylele Solid input arguments"""
        export_dict2text(
            outpath=self._make_out_path(),
            fname=self.fileNameBase + "_args",
            dictdata=self.cli,
            fmt='.json'
        )

    def export_stl(
        self,
        out_path=None,
        report_en=True,
    ) -> str:
        """Generate .stl output file"""
        if out_path is None:
            out_path = self._make_out_path()
        out_fname = os.path.join(out_path, self.fileNameBase + ".stl")
        print(f"Output File: {out_fname}")

        start_time = time.time()
        self.gen_full()

        self.api.export_stl(self.shape, out_fname)

        # potential timing issues with generating STL files
        retry = 0
        timeout = 1
        while retry < 3 and not os.path.isfile(out_fname):
            print(
                f"Failed to detect stl file {out_fname}, retry after {timeout} seconds..."
            )
            time.sleep(timeout)
            timeout *= 2
            retry += 1

        assert os.path.isfile(out_fname), f"Failed to generate stl file {out_fname}"

        if self.has_parts():
            # this is an assembly, generate other parts
            for part in self.parts:
                if isinstance(part, Solid):
                    part.export_stl(out_path=out_path)
                else:
                    print(
                        f"# WARNING: Cannot export .stl of class {part} in assembly {self}"
                    )
        # checks
        rpt = stl_check_volume(
            out_fname=out_fname,
            check_en=self.cli.stl_check_en
            and not self.cli.implementation == Implementation.MOCK,
            reference_volume=self.cli.reference_volume,
            reference_volume_tolerance=self.cli.reference_volume_tolerance,
        )

        end_time = time.time()
        # get the execution time
        render_time = end_time - start_time
        print(f"Rendering time: {render_time} [s]")
        rpt["render_time"] = render_time
        rpt['stl_file_size'] = os.path.getsize(out_fname)
        rpt["datetime"] = datetime.datetime.now().strftime("%y-%m-%d/%H:%M:%S")
        rpt |= platform.uname()._asdict()

        if report_en:
            export_dict2text(
                outpath=out_path, fname=self.fileNameBase + "_rpt", dictdata=rpt,fmt='.json'
            )

        return out_fname

    def fillet(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> Solid:
        """ Apply fillet to solid """
        self.gen_full()
        try:
            self.shape = self.shape.fillet(nearestPts, rad)
        except:
            print(f'WARNING: fillet failed at point {nearestPts}, with radius {rad}!')
        return self

    def half(self) -> Solid:
        """Cut solid in half to create a sectioned view"""
        # assert self.has_shape(), f'# Cannot half {self.fileNameBase} because main shape has not been generated yet!'
        self.gen_full()
        self.shape = self.shape.half()
        return self

    def join(self, joiner: Solid) -> Solid:
        """ Join solid with other solid """

        self.gen_full()
        self.shape = self.shape.join(
            solid_operand(joiner)
        )
        return self

    def mirror(self) -> Solid:
        """Mirror solid along XZ axis"""
        # assert self.has_shape(), f'# Cannot mirror {self.fileNameBase} because main shape has not been generated yet!'
        self.gen_full()
        mirror = self.shape.mirror()
        return mirror

    def mv(self, x: float, y: float, z: float) -> Solid:
        """Move solid in direction specified"""
        # assert self.has_shape(), f'# Cannot mv {self.fileNameBase} because main shape has not been generated yet!'
        self.gen_full()
        self.shape = self.shape.mv(x, y, z)
        return self

    def __add__(self, operand):
        """ Join using + """
        return self.join(operand)

    def __sub__(self, operand):
        """ cut using - """
        return self.cut(operand)

    def __and__(self, operand):
        """ cut using - """
        return self.intersection(operand)

    def __mul__(self, operand: tuple[float, float, float] = (1,1,1)) -> Shape:
        """ scale using * """
        if operand is None:
            return self
        return self.shape.scale(*operand)

    def __lshift__(self, operand: tuple[float, float, float] = (0,0,0)) -> Shape:
        """ move using << """
        if operand is None:
            return self
        return self.mv(*operand)

if __name__ == '__main__':
    prs = lele_solid_parser()
    print(prs.parse_args())
