#!/usr/bin/env python3

"""
    Pylele Bottom Assembly
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_config import LeleBodyType
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
from pylele2.pylele_brace import LeleBrace
from pylele2.pylele_chamber import LeleChamber, pylele_chamber_parser
from pylele2.pylele_tuners import LeleTuners
from pylele2.pylele_fretboard_assembly import pylele_fretboard_assembly_parser
from pylele2.pylele_worm import pylele_worm_parser


class LeleBottomAssembly(LeleBase):
    """Pylele Body Bottom Assembly Generator class"""

    def gen(self) -> Shape:
        """Generate Body Bottom Assembly"""

        cutTol = self.api.getJoinCutTol()

        ## Initialize Joiners and Cutters
        bodyJoiners = []
        bodyCutters = []

        ## Chamber
        if not self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.HOLLOW]:
            chamber_cutters = []
            if not self.cli.body_type in [LeleBodyType.TRAVEL]:
                chamber_cutters.append(LeleBrace(cli=self.cli))
            bodyCutters.append(
                LeleChamber(cli=self.cli, isCut=True, cutters=chamber_cutters)
            )

        ## Spines
        if self.cli.num_strings > 1:
            bodyCutters.append(
                LeleSpines(cli=self.cli, isCut=True).mv(0, 0, self.api.getJoinCutTol())
            )

        ## Neck Joint
        if self.cli.separate_neck:
            bodyCutters.append(
                LeleNeckJoint(cli=self.cli, isCut=True).mv(-cutTol, 0, cutTol)
            )

        ## Fretboard Spines
        if (
            self.cli.separate_fretboard
            or self.cli.separate_neck
            or self.cli.separate_top
        ):
            bodyCutters.append(
                LeleFretboardSpines(cli=self.cli, isCut=True).mv(2 * FIT_TOL, 0, cutTol)
            )

        ## Tuners
        if not self.cli.separate_top or not self.cli.separate_end:
            tnrsCut = LeleTuners(cli=self.cli, isCut=True)
            bodyCutters.append(tnrsCut)

        ## Tail
        if TunerType[self.cli.tuner_type].value.is_worm():
            if self.cli.separate_end:
                bodyCutters.append(LeleTail(cli=self.cli, isCut=True))
            elif self.cli.body_type in [LeleBodyType.HOLLOW]:
                # join tail to body if flat hollow and not separate end
                bodyJoiners.append(LeleTail(cli=self.cli))

        ## Text
        if not self.cli.no_text:
            bodyCutters.append(LeleTexts(cli=self.cli, isCut=True))

        ## Body
        body = LeleBody(cli=self.cli, joiners=bodyJoiners, cutters=bodyCutters)

        self.shape = body.gen_full()

        return self.shape

    def gen_parser(self, parser=None):
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
        test_body[body] = ["-bt", body]

    test_loop(module=__name__, apis=apis, tests=tests | test_body)


def test_bottom_assembly_mock(self):
    """Test Bottom Assembly Mock"""
    test_bottom_assembly(self, apis=["mock"])


if __name__ == "__main__":
    main()
