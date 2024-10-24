#!/usr/bin/env python3

"""
    Pylele Tuners
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_solid import main_maker, test_loop
from pylele_config_common import TunerType
from pylele2.pylele_base import LeleBase
from pylele2.pylele_peg import LelePeg
from pylele2.pylele_worm import LeleWorm, pylele_worm_parser
from pylele2.pylele_worm_key import LeleWormKey


class LeleTuners(LeleBase):
    """Pylele Tuners Generator class"""

    def gen(self) -> Shape:
        """Generate Tuners"""

        tXYZs = self.cfg.tnrXYZs
        tnrs = None
        for txyz in tXYZs:
            tnr = (
                LelePeg(isCut=self.isCut, cli=self.cli)
                if TunerType[self.cli.tuner_type].value.is_peg()
                else (
                    LeleWorm(isCut=self.isCut, cli=self.cli)
                    if TunerType[self.cli.tuner_type].value.is_worm()
                    else None
                )
            )
            if not tnr is None:
                tnr = tnr.mv(txyz[0], txyz[1], txyz[2]).shape
                tnrs = tnr if tnrs is None else tnrs.join(tnr)

        if TunerType[self.cli.tuner_type].value.is_worm() and self.cli.worm_has_key:
            worm = LeleWormKey(cli=self.cli, isCut=self.isCut)
            worm.gen_full()
            tnrs = tnrs.join(worm.shape)

        return tnrs

    def gen_parser(self, parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser(parser=pylele_worm_parser(parser=parser))


def main(args=None):
    """Generate Tuners"""
    return main_maker(module_name=__name__, class_name="LeleTuners", args=args)


def test_tuners(self, apis=None):
    """Test Tuners"""
    tests = {
        "cut": ["-C"],
        "tail_end": ["-t", "worm", "-e", "90", "-E", "-wah", "-C"],
    }

    tests_tuners_type = {}
    for t in TunerType.list():
        tests_tuners_type[t] = ["-t", t]

    test_loop(module=__name__, tests=tests | tests_tuners_type, apis=apis)


def test_tuners_mock(self):
    """Test Tuners"""
    test_tuners(self, apis=["mock"])


if __name__ == "__main__":
    main()
