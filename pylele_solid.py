#!/usr/bin/env python3

"""
    Abstract Base and Concrete Classes for all Gugulele Solid objects
"""

from __future__ import annotations

import os
import argparse
import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum

from pylele_api import ShapeAPI, Shape
from pylele_config import Fidelity, Implementation, CARBON, GRAY, LITE_GRAY,DARK_GRAY, ORANGE, WHITE

class ColorEnum(Enum):
    """ Color Enumerator """
    CARBON = CARBON,
    GRAY = GRAY,
    LITE_GRAY = LITE_GRAY,
    DARK_GRAY = DARK_GRAY,
    ORANGE = ORANGE,
    WHITE = WHITE

def make_or_exist_path(out_path):
    """ Check a directory exist, and generate if not """

    if not os.path.isdir(out_path):
        # Path.mkdir(out_path)
        os.makedirs(out_path)

    assert os.path.isdir(out_path), f"Cannot export to non directory: {out_path}"

def lele_solid_parser(parser=None):
    """
    LeleSolid Command Line Interface
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='LeleSolid Configuration')

    ## options ######################################################
    parser.add_argument("-i", "--implementation", help="Underlying engine implementation, default cadquery",
                        type=Implementation, choices=list(Implementation), default=Implementation.CAD_QUERY)
    parser.add_argument("-f", "--fidelity", help="Mesh fidelity for smoothness, default low",
                        type=Fidelity, choices=list(Fidelity), default=Fidelity.LOW)
    parser.add_argument("-c", "--color", help="Color.", type=str,
                        choices = ColorEnum._member_names_, default = 'ORANGE'
                        )
    parser.add_argument("-o", "--outdir", help="Output directory.", type=str,default='build')
    parser.add_argument("-C", "--is_cut",
                    help="This solid is a cutting.",
                    action='store_true')

    return parser

class LeleSolid(ABC):
    """
    Pylele Generic Solid Body
    """

    @abstractmethod
    def gen(self) -> Shape:
        """ Generate Shape """
        # self.shape =  ...
        pass

    def has_shape(self) -> bool:
        """ Return True if Solid has Shape attribute """
        if not hasattr(self, 'shape') or self.shape is None:
            return False
        return True
    
    def check_has_shape(self):
        """ Assert if Solid does not have shape attribute """
        assert self.has_shape()
        assert isinstance(self.shape,Shape)

    def has_api(self) -> bool:
        """ Return True if Solid has api attribute """
        if not hasattr(self, 'api') or self.api is None:
            return False
        return True
    
    def check_has_api(self):
        """ Assert if Solid does not have api attribute """
        assert self.has_api()
        assert isinstance(self.api, ShapeAPI)

    def has_parts(self) -> bool:
        """ Return True if Solid is an assembly with a list of parts attribute """
        if hasattr(self, 'parts') and not self.shape is None:
            return True
        return False
    
    def add_part(self,part):
        """ Add a solid part to the parts list of this assembly """
        assert isinstance(part, LeleSolid)

        if self.has_parts():
            self.parts.append(part)
        else:
            self.parts = [part]

    def add_parts(self,parts):
        """ Add a list of solid parts to the parts list of this assembly """
        assert isinstance(parts, list)

        if self.has_parts():
            self.parts += parts
        else:
            self.parts = parts

    def _gen_if_no_shape(self):
        """ Generate shape if attribute not present """
        if not self.has_shape():
            print(f'# Shape missing: Generating {self.fileNameBase}... ')

            if not self.has_api():
                print(f'# Shape missing API: Configuring {self.fileNameBase}... ')
                self.configure()
                self.check_has_api()
                print(f'# Done configuring API! {self.fileNameBase}')

            self.shape = self.gen()
            print(f'# Done generating shape! {self.fileNameBase}')
        self.check_has_shape()

    def gen_full(self):
        """ Generate full shape including joiners, cutters, and fillets """
        # generate self.shape
        self._gen_if_no_shape()
    
        for j in self.joiners:
            if not j.has_shape():
                print(f'# Warning: joiner {j} has no shape!')
                j.gen_full()
            self.shape = self.shape.join(j.shape)

        for c in self.cutters:
            if not c.has_shape():
                print(f'# Warning: cutter {c} has no shape!')
                c.gen_full()
            self.shape = self.shape.cut(c.shape)

        for rad in self.fillets.keys():
            # try:
            self.shape = self.shape.filletByNearestEdges(nearestPts=self.fillets[rad], rad=rad)
            # except:
            # print(f'# WARNING: Failed Fillet in {self.fileNameBase} on nearest edges {self.fillets[rad]}, with radius {rad}')
        
        return self.shape
    
    def _gen_full_if_no_shape(self):
        """ Generate full shape including joiners, cutters, and fillets, if shape is not already present """
        if not self.has_shape():
            self.gen_full()
        self.check_has_shape()

    def gen_parser(self,parser=None):
        """
        LeleSolid Command Line Interface
        """
        return lele_solid_parser(parser=parser)

    def parse_args(self, args=None):
        """ Parse Command Line Arguments """
        return self.gen_parser().parse_args(args=args)

    def __init__(self,
        isCut: bool = False,
        joiners: list[LeleSolid] = [],
        cutters: list[LeleSolid] = [],
        fillets: dict[float, list[tuple[float, float, float]]] = {},
        args=None,
        cli=None
    ):
        if cli is None:
            self.cli = self.parse_args(args=args)
        else:
            self.cli = cli

        self.isCut = self.cli.is_cut or isCut
        self.color = ColorEnum[self.cli.color]
        self.outdir = self.cli.outdir

        self.joiners = joiners
        self.cutters = cutters
        self.fillets = fillets
        self.fileNameBase = self.__class__.__name__

        return self.cli
    
    def configure(self):
        """ Configure Solid, and save self.cli """
        self.api = ShapeAPI.get(self.cli.implementation, self.cli.fidelity)
        self.check_has_api()

    def cut(self, cutter: LeleSolid) -> LeleSolid:
        """ Cut solid with other shape """
        # assert self.has_shape(), f'# Cannot cut {self.fileNameBase} because main shape has not been generated yet! '
        self._gen_full_if_no_shape()
        cutter._gen_full_if_no_shape()
        self.shape = self.shape.cut(cutter.shape)
        return self

    def _make_out_path(self):
        """ Generate an output directory """
        main_out_path = os.path.join(Path.cwd(),self.outdir)
        make_or_exist_path(main_out_path)
        
        out_path = os.path.join(main_out_path, self.fileNameBase+(datetime.datetime.now().strftime("-%y%m%d-%H%M")))
        make_or_exist_path(out_path)
        return out_path
    
    def export_args(self):
        """ Export Pylele Solid input arguments """
        out_fname = os.path.join(self._make_out_path(),self.fileNameBase + '_args.txt')
        with open(out_fname, 'w', encoding='UTF8') as f:
            f.write(repr(self.cli))
        assert os.path.isfile(out_fname)
        
    def exportSTL(self, out_path=None) -> None:
        """ Generate .stl output file """
        if out_path is None:
            out_path = self._make_out_path()
        out_fname = os.path.join(out_path,self.fileNameBase + '.stl')
        print(f'Output File: {out_fname}')

        self._gen_full_if_no_shape()

        self.api.exportSTL(self.shape, out_fname)
        assert os.path.isfile(out_fname)

        if self.has_parts():
            # this is an assembly, generate other parts
            for part in self.parts:
                assert isinstance(part,LeleSolid)
                part.exportSTL(out_path=out_path)
    
    def filletByNearestEdges(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> LeleSolid:
        """ Apply fillet to solid """
        self._gen_full_if_no_shape()
        self.shape = self.shape.filletByNearestEdges(nearestPts, rad)
        return self

    def half(self) -> LeleSolid:
        """ Cut solid in half to create a sectioned view """
        # assert self.has_shape(), f'# Cannot half {self.fileNameBase} because main shape has not been generated yet!'
        self._gen_full_if_no_shape()
        self.shape = self.shape.half()
        return self

    def join(self, joiner: LeleSolid) -> LeleSolid:
        """ Join solid with other solid """
        # assert self.has_shape(), f'# Cannot join {self.fileNameBase} because main shape has not been generated yet!'
        self._gen_full_if_no_shape()
        joiner._gen_full_if_no_shape()
        self.shape = self.shape.join(joiner.shape)
        return self

    def mirrorXZ(self) -> LeleSolid:
        """ Mirror solid along XZ axis """
        # assert self.has_shape(), f'# Cannot mirror {self.fileNameBase} because main shape has not been generated yet!'
        self._gen_full_if_no_shape()
        mirror = self.shape.mirrorXZ()
        return mirror

    def mv(self, x: float, y: float, z: float) -> LeleSolid:
        """ Move solid in direction specified """
        # assert self.has_shape(), f'# Cannot mv {self.fileNameBase} because main shape has not been generated yet!'
        self._gen_full_if_no_shape()
        self.shape = self.shape.mv(x, y, z)
        return self

    def show(self):
        """ Show solid """
        self._gen_full_if_no_shape()
        return self.shape.show()

if __name__ == '__main__':
    prs = lele_solid_parser()
    print(prs.parse_args())
