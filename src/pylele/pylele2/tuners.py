#!/usr/bin/env python3

"""
    Pylele Tuners
"""

from math import ceil

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.solid import main_maker, test_loop
from pylele.config_common import TunerType
from pylele.pylele2.base import LeleBase
from pylele.pylele2.peg import LelePeg
from pylele.pylele2.worm import LeleWorm, pylele_worm_parser
from pylele.pylele2.worm_key import LeleWormKey
from pylele.pylele2.turnaround import LeleTurnaround


class LeleTuners(LeleBase):
    """Pylele Tuners Generator class"""

    def is_peg(self):
        tuners = TunerType[self.cli.tuner_type].value
        return tuners.is_peg()

    def is_worm(self):
        tuners = TunerType[self.cli.tuner_type].value
        return tuners.is_worm()
    
    def gen(self) -> Shape:
        """Generate Tuners"""

        tnrs = None
        for txyz in self.cfg.tnrXYZs:
            if self.is_peg():
                tnr = LelePeg(isCut=self.isCut, cli=self.cli).gen_full()
            else: # if tuners.is_worm():
                if self.cli.tuner_type == TunerType.TURNAROUND.name:
                    tnr = LeleTurnaround(isCut=self.isCut, cli=self.cli).gen_full()
                else:
                    tnr = LeleWorm(isCut=self.isCut, cli=self.cli).gen_full()
            # if not tnr is None:
            tnr = tnr.mv(txyz[0], txyz[1], txyz[2])
            tnrs = tnr + tnrs

        # generate pegs for turnaround
        if self.cli.tuner_type == TunerType.TURNAROUND.name:
            ta_tnr = None
            for i in range(ceil(self.cli.num_strings/2)):
                tnr = LelePeg(isCut=self.isCut, cli=self.cli).gen_full()
                peg_cfg = TunerType[self.cli.tuner_type].value.peg_config
                tnr <<= (0,0,peg_cfg.botLen)
                tnr.rotate_x(90).mv(self.cli.scale_length - 35 * (1 + i),
                                    self.cfg.bodyWth/2,
                                    -self.cli.flat_body_thickness/2)
                ta_tnr = tnr + ta_tnr
            ta_tnr += ta_tnr.mirror_and_join()
            tnrs += ta_tnr

        if self.is_worm() and self.cli.worm_has_key:
            tnrs += LeleWormKey(cli=self.cli,isCut=self.isCut).gen_full()

        return tnrs

    def worm_fillet(self, top):
        """ Apply fillet to worm cut """
        assert self.isCut
        assert self.is_worm()

        # disabled for now to try slit back slope
        # tnr = LeleWorm(isCut=self.isCut, cli=self.cli)
        # # tnr._gen_full_if_no_shape()
        # tuners = tnr.worm_config()

        # for xyz in self.cfg.tnrXYZs:
        #     top = top.fillet(
        #         nearestPts=[
        #             (xyz[0] - tuners.sltLen, xyz[1], xyz[2] + tuners.strHt())
        #         ],
        #         rad = tuners.sltWth
        #         )
        return top

    def gen_parser(self,parser=None):
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
