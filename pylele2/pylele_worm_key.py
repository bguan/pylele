#!/usr/bin/env python3

"""
    Pylele Worm Key
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape, Implementation
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL, FILLET_RAD, TunerType
from pylele2.pylele_worm import WormConfig
from parts.rounded_box import RoundedBox

class LeleWormKey(LeleBase):
    """Pylele Worm Key Generator class"""

    def gen(self) -> Shape:
        """Generate Worm Key"""
        isBlender = self.cli.implementation == Implementation.BLENDER
        joinTol = self.api.getJoinCutTol()
        tailX = self.cfg.tailX
        txyzs = self.cfg.tnrXYZs
        assert TunerType[self.cli.tuner_type].value.is_worm()
        wcfg: WormConfig = TunerType[self.cli.tuner_type].value
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        btnHt = wcfg.buttonHt + 2 * cutAdj
        btnWth = wcfg.buttonWth + 2 * cutAdj
        btnTck = wcfg.buttonTck + 2 * cutAdj
        kbHt = wcfg.buttonKeybaseHt + 2 * cutAdj
        kbRad = wcfg.buttonKeybaseRad + cutAdj
        kyRad = wcfg.buttonKeyRad + cutAdj
        kyLen = wcfg.buttonKeyLen + 2 * cutAdj

        key = self.api.genPolyRodX(kyLen, kyRad, 6).mv(joinTol -kyLen/2 -kbHt -btnHt, 0, 0)
        base = self.api.genPolyRodX(kbHt, kbRad, 36) if isBlender else self.api.genRodX(kbHt, kbRad)
        base = base.mv(-kbHt/2 -btnHt, 0, 0)

        if self.isCut:
            btn = self.api.genBox(100, btnTck, btnWth)\
                .mv(50 -btnHt, 0, 0)
            btn += self.api.genRodX(100 if self.isCut else btnHt, btnWth/2)\
                .scale(1, .5, 1)\
                .mv(50 -btnHt, btnTck/2, 0)
        else:
            box = RoundedBox(args=['-x', f'{btnHt}',
                                   '-y', f'{btnTck}',
                                   '-z', f'{btnWth}',
                                   '-i', self.cli.implementation]
                                   )\
                .mv(-btnHt/2, 0, 0)
            btn = box.gen_full()

        btn += base + key
        maxTnrY = max([y for _, y, _ in txyzs])
        btn = btn.mv(tailX - joinTol, maxTnrY + btnTck -1, -1 -btnWth/2)
        return btn


def main(args=None):
    """Generate Worm Key"""
    return main_maker(module_name=__name__, class_name="LeleWormKey", args=args)


def test_worm_key(self, apis=None):
    """Test Worm Key"""
    tests = {
        "cut": ["-t", "worm", "-C"],
        "big_worm": ["-t", "bigWorm"],
    }
    test_loop(module=__name__, tests=tests, apis=apis)


def test_worm_key_mock(self):
    """Test Worm Key"""
    test_worm_key(self, apis=["mock"])


if __name__ == "__main__":
    main()
