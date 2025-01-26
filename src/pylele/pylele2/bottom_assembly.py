#!/usr/bin/env python3

"""
    Pylele Bottom Assembly
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.solid import main_maker, test_loop, Implementation
from pylele.pylele2.config import LeleBodyType
from b13d.api.constants import FIT_TOL
from b13d.api.core import Shape
from pylele.pylele2.base import LeleBase
from pylele.pylele2.neck_joint import LeleNeckJoint
from pylele.pylele2.texts import LeleTexts, pylele_texts_parser
from pylele.pylele2.tail import LeleTail
from pylele.pylele2.rim import LeleRim

from pylele.pylele2.body import LeleBody
from pylele.pylele2.spines import LeleSpines
from pylele.pylele2.fretboard_spines import LeleFretboardSpines
from pylele.pylele2.chamber import LeleChamber, pylele_chamber_parser
from pylele.pylele2.tuners import LeleTuners
from pylele.pylele2.fretboard_assembly import pylele_fretboard_assembly_parser
from pylele.pylele2.neck_assembly import LeleNeckAssembly
from pylele.pylele2.worm import pylele_worm_parser

class LeleBottomAssembly(LeleBase):
    """Pylele Body Bottom Assembly Generator class"""

    def gen(self) -> Shape:
        """ Generate Body Bottom Assembly """

        jcTol = self.api.tolerance()

        ## Body
        body = LeleBody(cli=self.cli)

        ## Chamber
        if not self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.HOLLOW]:
            body -= LeleChamber(cli=self.cli, isCut=True)

        ## Rim
        if self.cli.separate_top and not self.cli.body_type.is_solid():
            body -= LeleRim(cli=self.cli, isCut=True)

        ## Spines
        if self.cli.num_spines > 0:
            body -= LeleSpines(cli=self.cli, isCut=True).mv(0, 0, jcTol)

        ## Neck
        neck = LeleNeckAssembly(cli=self.cli, isCut=False)
        neck.gen_full()
        if self.cli.separate_neck:
            body -= LeleNeckAssembly(cli=self.cli, isCut=True)
            if not self.api.implementation == Implementation.BLENDER:
                # god knows why blender does not like this
                self.add_part(neck)
        else:
            body += neck.mv(jcTol, 0, 0)
            self.add_parts(neck.parts)

        ## Neck Joint
        if not self.cli.separate_neck:
            body -= LeleNeckJoint(cli=self.cli, isCut=True).mv(-jcTol, 0, jcTol)
                
        ## Fretboard Spines
        if  (self.cli.separate_fretboard or
            self.cli.separate_neck or
            self.cli.separate_top) and self.cli.num_spines > 0:
            body -= LeleFretboardSpines(cli=self.cli, isCut=True).mv(2*FIT_TOL, 0, 0)

        ## Tuners
        body -= LeleTuners(cli=self.cli, isCut=True)

        ## Tail, not ideal for non worm but possible
        if self.cli.separate_end:
            body -= LeleTail(cli=self.cli, isCut=True).mv(0, 0, jcTol)
            tail = LeleTail(cli=self.cli)
            self.add_part(tail)
        elif self.cli.body_type in [LeleBodyType.HOLLOW]:
            # join tail to body if flat hollow and not separate end
            body += LeleTail(cli=self.cli)

        ## Text (buggy for blender)
        if not self.cli.no_text:
            body -= LeleTexts(cli=self.cli, isCut=True)

        return body.gen_full()

    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser = pylele_fretboard_assembly_parser(parser=parser)
        parser = pylele_chamber_parser(parser=parser)
        parser = pylele_texts_parser(parser=parser)
        parser = pylele_worm_parser(parser=parser)
        return super().gen_parser(parser=parser)


def main(args=None):
    """Generate Body Bottom Assembly"""
    return main_maker(
        module_name="pylele.pylele2.bottom_assembly",
        class_name="LeleBottomAssembly",
        args=args,
    )


def test_bottom_assembly(self, apis=None):
    """Test Bottom Assembly"""

    tests = {
        "separate_top": ["-T","-X"],
        "separate_neck": ["-N","-X"],
        "separate_fretboard": ["-F","-X"],
        "text": ["-x", "TEST:30"],
    }

    refv = {
        'default': "467193",
        'travel' : '548386',
        'hollow' : '424951',
        'gourd'  : '504390',
        'flat'   : '913770',
        }
    test_body = {}
    for body in list(LeleBodyType):
        test_body[body] = ["-bt", body, "-t", "worm", "-e", "80", '-refv', refv[body]]

    test_loop(module=__name__, apis=apis, tests=tests | test_body)


def test_bottom_assembly_mock(self):
    """ Test Bottom Assembly Mock """
    test_bottom_assembly(self, apis=["mock"])

if __name__ == "__main__":
    main()
