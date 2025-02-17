#!/usr/bin/env python3

"""
    Pylele Peg 90 degrees
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from pylele.config_common import PegConfig, TunerType, PEG_90_CFG
from pylele.pylele2.base import LeleBase

class LelePeg90(LeleBase):
    """Pylele Peg 90 Degree Generator class"""

    def gen(self) -> Shape:
        """Generate Peg"""
        cutAdj = FIT_TOL if self.isCut else 0
        if TunerType[self.cli.tuner_type].value.is_peg():
            cfg: PegConfig = PEG_90_CFG # TunerType[self.cli.tuner_type].value
        elif TunerType[self.cli.tuner_type] in [TunerType.TURNAROUND, TunerType.TURNAROUND90] :
            cfg: PegConfig = TunerType[self.cli.tuner_type].value.peg_config
        else:
            assert f"Unsupported Peg for tuner type {self.cli.tuner_type}"
        joinTol = 2 * self.cfg.tolerance
        strRad = self.cfg.STR_RAD + cutAdj
        holeHt = cfg.holeHt
        majRad = cfg.majRad + cutAdj
        minRad = cfg.minRad + cutAdj
        midTck = cfg.midTck
        botLen = cfg.botLen
        btnRad = cfg.btnRad + cutAdj

        mid = self.api.cylinder_z(midTck + joinTol, minRad).mv(0, 0, -midTck / 2)

        stemHt = holeHt + 4 * strRad
        
        # top stem
        top  = self.api.cylinder_z(stemHt + joinTol, minRad / 2).mv(0, 0, stemHt / 2)
        # top stem hole
        top  -= self.api.cylinder_x(2 * minRad, strRad).mv(0, 0, holeHt)

        bot = self.api.cylinder_z(botLen + joinTol, majRad).mv(
            0, 0, -midTck - botLen / 2
        )

        stem_rad = 4
        bot_square = self.api.box(majRad+2*stem_rad,2*majRad,botLen)
        bot_square <<= (0,majRad,-midTck - botLen/2)

        stem_ht = 10
        hstem = self.api.cylinder_x(stem_ht, stem_rad)
        hstem <<= (majRad+stem_ht/2,majRad+stem_rad,-midTck - botLen/2)

        # handle
        btn = self.api.box(btnRad * 2, btnRad / 2, btnRad)\
            .rotate_x(90).rotate_z(90)
        btn <<= (majRad+stem_ht + btnRad/2,
                    majRad+stem_rad,
                    -midTck - botLen/2)

        return top + mid + bot + bot_square + hstem + btn

def main(args=None):
    """Generate Peg 90"""
    return main_maker(module_name=__name__, class_name="LelePeg90", args=args)

def test_peg90(self, apis=None):
    """Test Peg 90"""

    tests = {
        "default": [],
    }
    test_loop(module=__name__, tests=tests, apis=apis)


def test_peg90_mock(self):
    """Test Peg 90"""
    test_peg90(self, apis=["mock"])


if __name__ == "__main__":
    main()
