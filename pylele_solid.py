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

from pylele_api import ShapeAPI, Shape
from pylele_config import Fidelity, Implementation, CARBON, GRAY, LITE_GRAY,DARK_GRAY, ORANGE, WHITE

COLORS = {
    'carbon': CARBON, 
    'gray': GRAY, 
    'lite_gray' : LITE_GRAY,
    'dark_gray' : DARK_GRAY, 
    'orange' : ORANGE, 
    'white': WHITE
}

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
                        type=Implementation, choices=list(Implementation), default=Implementation.BLENDER)
    parser.add_argument("-f", "--fidelity", help="Mesh fidelity for smoothness, default low",
                        type=Fidelity, choices=list(Fidelity), default=Fidelity.LOW)
    parser.add_argument("-c", "--color", help="Color.", type=str,
                        choices = COLORS.keys(), default = COLORS['white']
                        )
    parser.add_argument("-o", "--outdir", help="Output directory.", type=str,default='build')
    parser.add_argument("-C", "--is_cut",
                    help="This solid is a cutting.",
                    action='store_true')

    return parser

class LeleSolid(ABC):
    @abstractmethod
    def gen(self) -> Shape:
        """ Generate Shape """
        pass

    def gen_parser(self,parser=None):
        """
        LeleSolid Command Line Interface
        """
        return lele_solid_parser(parser=parser)

    def parse_args(self):
        """ Parse Command Line Arguments """
        return self.gen_parser().parse_args()

    def __init__(self,
        joiners: list[LeleSolid] = [],
        cutters: list[LeleSolid] = [],
        fillets: dict[float, list[tuple[float, float, float]]] = {},
    ):
        cfg = self.parse_args()

        self.isCut = cfg.is_cut
        self.color = cfg.color
        self.api = ShapeAPI.get(cfg.implementation, cfg.fidelity)
        self.outdir = cfg.outdir

        self.joiners = joiners
        self.cutters = cutters
        self.fileNameBase = self.__class__.__name__

        self.shape = self.gen()
    
        for j in self.joiners:
            self.shape = self.shape.join(j.shape)
        for c in self.cutters:
            self.shape = self.shape.cut(c.shape)
        for rad in fillets:
            self.shape = self.shape.filletByNearestEdges(fillets[rad], rad)
        
        return cfg
    
    def cut(self, cutter: LeleSolid) -> LeleSolid:
        self.shape = self.shape.cut(cutter.shape)
        return self

    def _make_out_path(self):
        main_out_path = os.path.join(Path.cwd(),self.outdir)
        make_or_exist_path(main_out_path)
        
        out_path = os.path.join(main_out_path, self.fileNameBase+(datetime.datetime.now().strftime("-%y%m%d-%H%M")))
        #os.makedirs(out_path)
        make_or_exist_path(out_path)
        return out_path
        
    def exportSTL(self) -> None:
        out_fname = os.path.join(self._make_out_path(),self.fileNameBase + '.stl')
        print(f'Output File: {out_fname}')
        self.api.exportSTL(self.shape, out_fname)
    
    def filletByNearestEdges(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> LeleSolid:
        self.shape = self.shape.filletByNearestEdges(nearestPts, rad)
        return self

    def half(self) -> LeleSolid:
        self.shape = self.shape.half()
        return self

    def join(self, joiner: LeleSolid) -> LeleSolid:
        self.shape = self.shape.join(joiner.shape)
        return self

    def mirrorXZ(self) -> LeleSolid:
        mirror = self.shape.mirrorXZ()
        return mirror

    def mv(self, x: float, y: float, z: float) -> LeleSolid:
        self.shape = self.shape.mv(x, y, z)
        return self

    def show(self):
        return self.shape.show()

if __name__ == '__main__':
    prs = lele_solid_parser()
    print(prs.parse_args())
