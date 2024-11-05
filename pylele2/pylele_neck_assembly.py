#!/usr/bin/env python3

"""
    Pylele Neck Assembly
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_config import LeleBodyType
from pylele2.pylele_base import LeleBase
from pylele2.pylele_fretboard_assembly import (
    LeleFretboardAssembly,
    pylele_fretboard_assembly_parser,
    FretType,
    NutType,
)
from pylele2.pylele_fretboard_spines import LeleFretboardSpines
from pylele2.pylele_head import LeleHead
from pylele2.pylele_neck_joint import LeleNeckJoint
from pylele2.pylele_neck import LeleNeck
from pylele2.pylele_neck_bend import LeleNeckBend
from pylele2.pylele_spines import LeleSpines


class LeleNeckAssembly(LeleBase):
    """Pylele Neck Assembly Generator class"""

    def gen(self) -> Shape:
        """Generate Neck Assembly"""

        jcTol = self.api.getJoinCutTol()

        ## Neck
        neck = LeleNeck(cli=self.cli)

        ## Head
        neck += LeleHead(cli=self.cli).mv(jcTol,0,0)

        ## Fretboard, only part of neck assembly if separate fretboard or separate neck
        ## if only separate top, fretboard is joined to top!
        if (self.cli.separate_fretboard or self.cli.separate_neck or not self.cli.separate_top):
            fretbd = LeleFretboardAssembly(cli=self.cli)
            fretbd.gen_full()
            if self.cli.separate_fretboard:
                self.add_part(fretbd)
            else:
                neck += fretbd.mv(max(0.01, jcTol), 0, -jcTol) # HACK cadquery bug needs this
                self.add_parts(fretbd.get_parts())

        ## Neck Joint
        if self.cli.separate_neck:
            neck += LeleNeckJoint(cli=self.cli, isCut=False).mv(0, 0, -jcTol)

        ## Fretboard Spines, needed as fbspines in Fretboard assembly and not in Fretboad
        if (self.cli.separate_fretboard or self.cli.separate_top) \
            and self.cli.num_spines > 0:
            neck -= LeleFretboardSpines(cli=self.cli, isCut=True)

        ## Spines
        if self.cli.num_spines > 0:
            neck -= LeleSpines(cli=self.cli, isCut=True)

        ## Neck Bend
        if self.cli.body_type in [
            LeleBodyType.FLAT,
            LeleBodyType.HOLLOW,
            LeleBodyType.TRAVEL
        ]:
            neck += LeleNeckBend(cli=self.cli)

        return neck.gen_full()

    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser(
            parser=pylele_fretboard_assembly_parser(parser=parser)
        )


def main(args=None):
    """Generate Neck Assembly"""
    return main_maker(module_name=__name__, class_name="LeleNeckAssembly", args=args)


def test_neck_assembly(self, apis=None):
    """Test Neck Assembly"""

    tests = {
        'fret_wire'          : ['-ft', str(FretType.WIRE)],
        'zerofret'           : ['-nt', str(NutType.ZEROFRET)],
        'separate_neck'      : ['-N'],
        'separate_fretboard' : ['-F'],
        'separate_nut'       : ['-NU'],
        'separate_frets'     : ['-FR'],
        'separate_all'       : ['-N','-FR','-NU','-F'],
        'flat_body'          : ['-bt',LeleBodyType.FLAT]
    }

    test_loop(module=__name__, tests=tests, apis=apis)


def test_neck_assembly_mock(self):
    """Test Neck Assembly"""
    test_neck_assembly(self, apis=["mock"])


if __name__ == "__main__":
    main()
