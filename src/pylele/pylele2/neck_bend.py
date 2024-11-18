#!/usr/bin/env python3

"""
    Pylele Neck Bend
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.api.core import Shape
from pylele.api.solid import main_maker, test_loop
from pylele.pylele2.config import LeleBodyType
from pylele.pylele2.base import LeleBase


class LeleNeckBend(LeleBase):
    """Pylele Neck Generator class"""

    def gen(self) -> Shape:
        """Generate Neck Bend"""
        assert self.cli.body_type in [
            LeleBodyType.FLAT,
            LeleBodyType.HOLLOW,
            LeleBodyType.TRAVEL,
        ]

        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth

        neck_profile = self.api.cylinder_z(self.cli.flat_body_thickness, nkWth / 2).mv(
            nkLen, 0, -self.cli.flat_body_thickness / 2
        )
        neck_cutter = self.api.box(
            nkWth / 2, nkWth, self.cli.flat_body_thickness
        ).mv(nkLen + nkWth / 4, 0, -self.cli.flat_body_thickness / 2)
        neck_profile = neck_profile.cut(neck_cutter)

        bot = (
            self.api.sphere_quadrant(nkWth / 2, False, True)
            .scale(1, 1, self.cfg.TOP_RATIO)
            .mv(nkLen, 0, -self.cli.flat_body_thickness + self.api.tolerance())
        )
        return neck_profile.join(bot)


def main(args=None):
    """Generate Neck"""
    return main_maker(
        module_name=__name__,
        class_name="LeleNeckBend",
        args=args,
    )


def test_neck_bend(self, apis=None):
    """Test Neck Bend"""
    tests = {"default": ["-bt", LeleBodyType.FLAT, '-refv','19986']}
    test_loop(module=__name__, apis=apis, tests=tests)


def test_neck_bend_mock(self):
    """Test Neck"""
    test_neck_bend(self, apis=["mock"])


if __name__ == "__main__":
    main()
