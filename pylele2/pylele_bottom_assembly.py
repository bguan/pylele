#!/usr/bin/env python3

"""
    Pylele Bottom Assembly
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_config import LeleBodyType, Implementation
from pylele_config_common import TunerType
from api.pylele_api_constants import FIT_TOL
from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase
from pylele2.pylele_neck_joint import LeleNeckJoint
from pylele2.pylele_texts import LeleTexts, pylele_texts_parser
from pylele2.pylele_tail import LeleTail

from pylele2.pylele_body import LeleBody
from pylele2.pylele_spines import LeleSpines
from pylele2.pylele_fretboard_spines import LeleFretboardSpines
from pylele2.pylele_chamber import LeleChamber, pylele_chamber_parser
from pylele2.pylele_tuners import LeleTuners
from pylele2.pylele_fretboard_assembly import pylele_fretboard_assembly_parser
from pylele2.pylele_neck_assembly import LeleNeckAssembly
from pylele2.pylele_worm import pylele_worm_parser
from pylele2.pylele_neck_bend import LeleNeckBend


class LeleBottomAssembly(LeleBase):
    """Pylele Body Bottom Assembly Generator class"""

    def gen(self) -> Shape:
        """ Generate Body Bottom Assembly """

        jcTol = self.api.getJoinCutTol()

        ## Body
        body = LeleBody(cli=self.cli)

        ## Text
        if not self.cli.no_text:
            body -= LeleTexts(cli=self.cli, isCut=True)

        ## Chamber
        chamber = None
        if not self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.HOLLOW]:
            chamber = LeleChamber(cli=self.cli, isCut=True)
            body -= chamber

        ## Spines
        spines = None
        if self.cli.num_strings > 1:
            spines = LeleSpines(cli=self.cli, isCut=True).mv(0, 0, jcTol)
            body -= spines

        ## Neck
        neck = LeleNeckAssembly(cli=self.cli, isCut=False)
        neck.gen_full()
        if self.cli.separate_neck:
            self.add_part(neck)
        else:
            body += neck.mv(jcTol, 0, 0)
            if neck.has_parts():
                self.add_parts(neck.parts)

        ## Neck Joint
        if self.cli.separate_neck:
            body -= LeleNeckJoint(cli=self.cli, isCut=True).mv(-jcTol, 0, jcTol)

        ## Neck Bend
        if self.cli.body_type in [
            LeleBodyType.FLAT,
            LeleBodyType.HOLLOW,
            LeleBodyType.TRAVEL
        ]:
            if self.cli.implementation == Implementation.CAD_QUERY and self.cli.body_type == LeleBodyType.FLAT:
                print('# WARNING: not generating neck bend, because does not work with cadquery and flat body')
            else:
                body += LeleNeckBend(cli=self.cli)

        ## Fretboard Spines
        if (self.cli.separate_fretboard or
            self.cli.separate_neck or
            self.cli.separate_top) and self.cli.num_spines > 0:
            body -= LeleFretboardSpines(cli=self.cli, isCut=True).mv(2*FIT_TOL, 0, 0)

        ## Tuners
        tuners = LeleTuners(cli=self.cli, isCut=True)
        if not self.cli.separate_end:
            body -= tuners

        ## Tail
        # if TunerType[self.cli.tuner_type].value.is_worm(): not ideal for non worm but possible
        if self.cli.separate_end:
            body -= LeleTail(cli=self.cli, isCut=True).mv(0, 0, jcTol)
            tail = LeleTail(cli=self.cli)
            tail -= tuners
            if spines is not None:
                tail -= spines
            if chamber is not None:
                tail -= chamber
            self.add_part(tail)
        elif self.cli.body_type in [LeleBodyType.HOLLOW]:
            # join tail to body if flat hollow and not separate end
            body += LeleTail(cli=self.cli)

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
        module_name="pylele2.pylele_bottom_assembly",
        class_name="LeleBottomAssembly",
        args=args,
    )


def test_bottom_assembly(self, apis=None):
    """Test Bottom Assembly"""

    tests = {
        "default": [],
        "separate_top": ["-T"],
        "separate_neck": ["-N"],
        "separate_fretboard": ["-F"],
        "text": ["-x", "TEST:30"],
    }

    test_body = {}
    for body in list(LeleBodyType):
        test_body[body] = ["-bt", body, "-t", "worm", "-e", "80"]

    test_loop(module=__name__, apis=apis, tests=tests | test_body)


def test_bottom_assembly_mock(self):
    """ Test Bottom Assembly Mock """
    test_bottom_assembly(self, apis=["mock"])

if __name__ == "__main__":
    main()
