#!/usr/bin/env python3

"""
    Pylele Top Assembly
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.config import LeleBodyType
from pylele.config_common import LeleScaleEnum
from pylele.pylele2.base import LeleBase
from pylele.pylele2.bridge_assembly import LeleBridgeAssembly, pylele_bridge_assembly_parser
from pylele.pylele2.guide import LeleGuide
from pylele.pylele2.brace import LeleBrace
from pylele.pylele2.chamber import LeleChamber, pylele_chamber_parser
from pylele.pylele2.fretboard_joint import LeleFretboardJoint
from pylele.pylele2.tuners import LeleTuners
from pylele.pylele2.soundhole import LeleSoundhole
from pylele.pylele2.rim import LeleRim
from pylele.pylele2.worm import pylele_worm_parser
from pylele.pylele2.top import LeleTop
from pylele.pylele2.fretboard_assembly import (
    LeleFretboardAssembly,
    pylele_fretboard_assembly_parser,
)
from pylele.pylele2.fretboard import LeleFretboard
from pylele.pylele2.worm_key import LeleWormKey

class LeleTopAssembly(LeleBase):
    """Pylele Body Top Assembly Generator class"""

    def gen(self) -> Shape:
        """Generate Body Top Assembly"""

        jcTol = self.api.tolerance()

        # top
        top = LeleTop(cli=self.cli)

        # tuners
        tuners = LeleTuners(cli=self.cli, isCut=True)
        top -= tuners

        if tuners.is_worm():
            # fillet worm tuners slit
            top = tuners.worm_fillet(top)

            if self.cli.worm_has_key:
                self.add_part(LeleWormKey(cli=self.cli))

        elif tuners.is_peg():
            # gen guide if using tuning pegs
            guide = LeleGuide(cli=self.cli)
            if self.cli.separate_guide:
                top -= LeleGuide(cli=self.cli, isCut=True)
                self.add_part(guide)
            else:
                top +=guide

        if self.cli.separate_top: # and self.cli.body_type in [LeleBodyType.GOURD]:
            top += LeleRim(cli=self.cli, isCut=False)

        if self.cli.separate_top and not self.cli.separate_fretboard and not self.cli.separate_neck:
            fretbd = LeleFretboardAssembly(cli=self.cli)
            fretbd.gen_full()
            top += fretbd.mv(max(0.01, jcTol), 0, 0) # HACK cadquery bug needs this
            if fretbd.has_parts():
                self.add_parts(top.parts)

        if not self.cli.body_type.is_solid():
            # soundhole
            sh  = LeleSoundhole(cli=self.cli, isCut=True)
            top -= sh
            top = sh.fillet(top)

        if self.cli.separate_fretboard or self.cli.separate_neck:
            top -= LeleFretboardJoint(cli=self.cli, isCut=True)\
                .mv(-self.api.tolerance(), 0, -self.api.tolerance())
            top -= LeleFretboard(cli=self.cli, isCut=True)

        # gen bridge
        brdg = LeleBridgeAssembly(cli=self.cli)
        if self.cli.separate_bridge:
            top -= LeleBridgeAssembly(cli=self.cli, isCut=True)
            self.add_part(brdg)
        else:
            top += brdg

        if self.cli.body_type in [LeleBodyType.GOURD, LeleBodyType.TRAVEL]:
            chm = LeleChamber(cli=self.cli,isCut=True)
            # cut Brace from chamber
            if not self.cli.body_type.is_solid():
                chm -= LeleBrace(cli=self.cli)
            top -= chm

        return top.gen_full()

    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser = pylele_fretboard_assembly_parser(parser=parser)
        parser = pylele_chamber_parser(parser=parser)
        parser = pylele_worm_parser(parser=parser)
        parser = pylele_bridge_assembly_parser(parser=parser)
        return super().gen_parser(parser=parser)


def main(args=None):
    """Generate Body Top Assembly"""
    return main_maker(module_name=__name__, class_name="LeleTopAssembly", args=args)


def test_top_assembly(self, apis=None):
    """Test Top Assembly"""

    test_scale_len = {}
    for sl in list(LeleScaleEnum):
        test_scale_len[sl.name] = ["-s", sl.name]

    tests = {
        "default": [],
        "separate_bridge": ["-B"],
        "separate_guide": ["-G"],
        "separate_top": ["-T"],
        "separate_neck": ["-N"],
        "separate_fretboard": ["-F"],
        # "gotoh_tuners": ["-t", "gotoh"],
        "worm_tuners": ["-t", "worm"],
        "big_worm_tuners": ["-t", "bigWorm"],
        "bridge_piezo": ["-bpiezo", "-B"],
    }

    tests_all = tests | test_scale_len
    test_loop(module=__name__, tests=tests_all, apis=apis)


def test_top_assembly_mock(self):
    """Test Top Assembly"""
    test_top_assembly(self, apis=["mock"])


if __name__ == "__main__":
    main()
