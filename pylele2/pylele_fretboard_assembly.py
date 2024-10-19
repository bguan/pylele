#!/usr/bin/env python3

"""
    Pylele Fretboard Assembly
"""

import os
import argparse
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape, Implementation
from api.pylele_api_constants import FILLET_RAD
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase
from pylele2.pylele_frets import LeleFrets, pylele_frets_parser, FretType
from pylele2.pylele_nut import LeleNut, pylele_nut_parser, NutType
from pylele2.pylele_fretboard_dots import LeleFretboardDots, pylele_dots_parser
from pylele2.pylele_fretboard import LeleFretboard
from pylele2.pylele_top import LeleTop
from pylele2.pylele_fretboard_spines import LeleFretboardSpines
from pylele2.pylele_fretboard_joint import LeleFretboardJoint


def pylele_fretboard_assembly_parser(parser=None):
    """
    Pylele Fretboard Assembly Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Pylele Configuration")

    parser = pylele_nut_parser(parser=parser)
    parser = pylele_dots_parser(parser=parser)
    parser = pylele_frets_parser(parser=parser)
    parser.add_argument(
        "-NU", "--separate_nut", help="Split nut from fretboard.", action="store_true"
    )
    parser.add_argument(
        "-FR",
        "--separate_frets",
        help="Split frets from fretboard.",
        action="store_true",
    )
    parser.add_argument(
        "-D", "--separate_dots", help="Split dots from fretboard.", action="store_true"
    )
    return parser

class LeleFretboardAssembly(LeleBase):
    """Pylele Fretboard Assembly Generator class"""

    def gen(self) -> Shape:
        """ Generate Fretboard Assembly """
        
        fretbd = LeleFretboard( cli=self.cli )

        ## dots
        if self.cli.separate_dots:
            fdotsCut = LeleFretboardDots(isCut=True,cli=self.cli)
            fretbd -= fdotsCut
            self.add_part(fdotsCut)

        ## frets
        frets = LeleFrets(cli=self.cli)
        if self.cli.separate_frets:
            fretbd -= frets
            self.add_part(frets)
        else:
            fretbd += frets

        ## nut
        nut = LeleNut(cli=self.cli,isCut=self.cli.separate_nut)
        if self.cli.separate_nut:
            fretbd -= nut
            self.add_part(nut)
        else:
            fretbd += nut

        if self.cli.separate_fretboard or self.cli.separate_neck:
            fretbd -= LeleTop(isCut=True,cli=self.cli).mv(0, 0, -self.api.getJoinCutTol())
            fretbd += LeleFretboardJoint(cli=self.cli)
            if self.cli.num_spines > 0:
                fretbd += LeleFretboardSpines(cli=self.cli)
        
        return fretbd.gen_full()
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser(
            parser=pylele_fretboard_assembly_parser(parser=parser)
        )


def main(args=None):
    """Generate Fretboard Assembly"""
    return main_maker(
        module_name=__name__, class_name="LeleFretboardAssembly", args=args
    )


def test_fretboard_assembly(self, apis=None):
    """Test Fretboard Assembly"""
    tests = {
        'separate_fretboard' : ['-F'],
        'fret_round'         : ['-ft', str(FretType.ROUND)],
        'fret_wire'          : ['-ft', str(FretType.WIRE)],
        'zerofret'           : ['-nt', str(NutType.ZEROFRET)],
        'separate_nut'       : ['-NU'],
        'separate_frets'     : ['-FR'],
        'separate_dots'      : ['-D'],
        }
    for nspines in range(4):
        tests[f'nspines{nspines}'] = ['-F','-nsp',f'{nspines}']
    test_loop(module=__name__,tests=tests,apis=apis)

def test_fretboard_assembly_mock(self):
    """Test Fretboard Assembly"""
    test_fretboard_assembly(self, apis=["mock"])


if __name__ == "__main__":
    main()
