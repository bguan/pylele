#!/usr/bin/env python3

"""
    Pylele All Assembly
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.api.core import Shape
from pylele.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase
from pylele.pylele2.texts import pylele_texts_parser
from pylele.pylele2.top_assembly import LeleTopAssembly
from pylele.pylele2.chamber import pylele_chamber_parser
from pylele.pylele2.fretboard_assembly import pylele_fretboard_assembly_parser
from pylele.pylele2.worm import pylele_worm_parser
from pylele.pylele2.config import CONFIGURATIONS
from pylele.pylele2.bottom_assembly import LeleBottomAssembly
from pylele.pylele2.bridge import pylele_bridge_parser


class LeleAllAssembly(LeleBase):
    """Pylele All Assembly Generator class"""

    def gen(self) -> Shape:
        """Generate Body Bottom Assembly"""

        jcTol = self.api.tolerance()

        ## Body
        body = LeleBottomAssembly(cli=self.cli)
        body.gen_full()
        if body.has_parts():
            self.add_parts(body.parts)

        ## Top
        top = LeleTopAssembly(cli=self.cli)
        top.gen_full()
        if self.cli.separate_top:
            self.add_part(top)
        else:
            body += top.mv(0, 0, -jcTol)
            if top.has_parts():
                self.add_parts(top.parts)

        return body.gen_full()

    def gen_parser(self,parser=None):
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
        module_name="pylele.pylele2.all_assembly",
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

    # reference volumes
    refv = {
        'default'        :  '529039',
        'worm'           :  '579205',
        'flat'           : '1078970',
        'hollow'         : '1053325',
        'travel'         :  '922530'
    }

    test_config = {}
    for key,config in CONFIGURATIONS.items():
        test_config[key] = config + ['-refv',refv[key]]
        
    test_loop(
        module=__name__,
        apis=apis,
        tests=tests | test_config,
    )


def test_all_assembly_mock(self):
    """Test Bottom Assembly Mock"""
    test_all_assembly(self, apis=["mock"])


if __name__ == "__main__":
    main()