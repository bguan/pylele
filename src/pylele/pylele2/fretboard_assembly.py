#!/usr/bin/env python3

"""
    Pylele Fretboard Assembly
"""

import os
import argparse
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape, Implementation
from b13d.api.constants import FILLET_RAD
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase
from pylele.pylele2.frets import LeleFrets, pylele_frets_parser, FretType
from pylele.pylele2.nut import LeleNut, pylele_nut_parser, NutType
from pylele.pylele2.fretboard_dots import LeleFretboardDots, pylele_dots_parser
from pylele.pylele2.fretboard import LeleFretboard
from pylele.pylele2.top import LeleTop
from pylele.pylele2.fretboard_spines import LeleFretboardSpines
from pylele.pylele2.fretboard_joint import LeleFretboardJoint
from pylele.pylele2.body import LeleBody

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

        jcTol = self.api.tolerance()

        fretbd = LeleFretboard( cli=self.cli )

        ## dots
        if self.cli.separate_dots:
            fdotsCut = LeleFretboardDots(isCut=True,cli=self.cli)
            fretbd -= fdotsCut
            fdots   = LeleFretboardDots(cli=self.cli)
            if self.cli.all:
                fdots <<= (0, 0, self.cli.all_distance)
                fretbd += fdots
            else:
                self.add_part(fdots)

        ## frets
        frets = LeleFrets(cli=self.cli)
        if self.cli.separate_frets:
            fretbd -= frets
            if self.cli.all:
                frets <<= (0, 0, self.cli.all_distance)
                fretbd += frets
            else:
                self.add_part(frets)
        else:
            fretbd += frets

        ## nut
        nut = LeleNut(cli=self.cli,isCut=self.cli.separate_nut)
        if self.cli.separate_nut:
            fretbd -= nut
            if self.cli.all:
                nut <<= (0, 0, self.cli.all_distance)
                fretbd += nut
            else:
                self.add_part(nut)
        else:
            fretbd += nut

        if (self.cli.separate_fretboard or self.cli.separate_top) and self.cli.num_spines > 0:
            fretbd += LeleFretboardSpines(cli=self.cli).mv(0, 0, jcTol)

        if self.cli.separate_fretboard or self.cli.separate_neck:
            fretbd += LeleFretboardJoint(cli=self.cli).mv(-jcTol, 0, 0)
            # fretbd -= LeleTop(isCut=True,cli=self.cli).mv(0, 0, -jcTol)
            # fretbd -= LeleBody(isCut=True,cli=self.cli)

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
        'fret_round'         : ['-ft', str(FretType.ROUND), '-refv','40518'],
        'fret_wire'          : ['-ft', str(FretType.WIRE), '-FR'],
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
