#!/usr/bin/env python3

"""
    Pylele All Assembly
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase
from pylele2.pylele_texts import pylele_texts_parser
from pylele2.pylele_tail import LeleTail
from pylele2.pylele_rim import LeleRim
from pylele2.pylele_spines import LeleSpines
from pylele2.pylele_top_assembly import LeleTopAssembly
from pylele2.pylele_neck_assembly import LeleNeckAssembly
from pylele2.pylele_chamber import pylele_chamber_parser
from pylele2.pylele_fretboard_assembly import pylele_fretboard_assembly_parser
from pylele2.pylele_worm import pylele_worm_parser
from pylele2.pylele_config import CONFIGURATIONS
from pylele2.pylele_bottom_assembly import LeleBottomAssembly
from pylele2.pylele_bridge import pylele_bridge_parser


class LeleAllAssembly(LeleBase):
    """Pylele All Assembly Generator class"""

    def gen(self) -> Shape:
        """Generate Body Bottom Assembly"""

        joinTol = self.api.getJoinCutTol()

        ## Initialize Joiners and Cutters
        bodyJoiners = []
        bodyCutters = []

        ## Spines
        if self.cli.num_spines > 0:
            bodyCutters.append(
                LeleSpines(cli=self.cli, isCut=True).mv(0, 0, self.api.getJoinCutTol())
            )
            
        ## Top
        top = LeleTopAssembly(cli=self.cli).mv(0, 0, -joinTol)
        top.gen_full()
        if self.cli.separate_top:
            bodyCutters.append(LeleRim(cli=self.cli, isCut=True))
            self.add_part(top)
        else:
            bodyJoiners.append(top)
            if top.has_parts():
                self.add_parts(top.get_parts())

        ## Neck
        neck = LeleNeckAssembly(cli=self.cli).mv(-joinTol, 0, 0)
        neck.gen_full()
        if self.cli.separate_neck:
            self.add_part(neck)
        else:
            bodyJoiners.append(neck)
            if neck.has_parts():
                self.add_parts(neck.get_parts())

        ## Tail
        if self.cli.separate_end:
            self.add_part(LeleTail(cli=self.cli))

        ## Body
        self.shape = LeleBottomAssembly(
            cli=self.cli, joiners=bodyJoiners, cutters=bodyCutters
        )
        return self.shape.gen_full()

    def gen_parser(self, parser=None):
        """
        pylele Command Line Interface
        """
        parser = pylele_fretboard_assembly_parser(parser=parser)
        parser = pylele_chamber_parser(parser=parser)
        parser = pylele_texts_parser(parser=parser)
        parser = pylele_worm_parser(parser=parser)
        parser = pylele_bridge_parser(parser=parser)
        return super().gen_parser(parser=parser)


def main(args=None):
    """Generate Body Bottom Assembly"""
    return main_maker(
        module_name="pylele2.pylele_all_assembly",
        class_name="LeleAllAssembly",
        args=args,
    )


def test_all_assembly(self, apis=None):
    """Test All Assembly"""

    tests = {
        "separate_bridge": ["-B"],
        "separate_top": ["-T"],
        "separate_neck": ["-N"],
        "separate_fretboard": ["-F"],
        "separate_all": ["-F", "-N", "-T", "-B", "-NU", "-FR", "-D", "-G"],
        "gotoh_tuners": ["-t", "gotoh"],
    }

    test_loop(
        module=__name__,
        apis=apis,
        tests=tests | CONFIGURATIONS,
    )


def test_all_assembly_mock(self):
    """Test Bottom Assembly Mock"""
    test_all_assembly(self, apis=["mock"])


if __name__ == "__main__":
    main()
