#!/usr/bin/env python3

"""
    Pylele turnaround
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.config_common import TunerType, WormConfig
from b13d.api.core import Shape, Implementation
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from b13d.parts.torus import Torus
from b13d.parts.tube import Tube
from pylele.pylele2.worm import LeleWorm

class LeleTurnaround(LeleWorm):
    """Pylele turnaround Generator class"""

    def gen(self) -> Shape:
        """Generate turnaround"""

        c = self.worm_config()

        # Note: Origin is middle of slit, near tip of axle

        ## Axle
        axlX = 0
        axlY = 0 # -0.5
        axlZ = 0

        axl = self.api.cylinder_y(c.axlLen, c.axlRad).mv(axlX, axlY, axlZ)
        if self.isCut:
            axl += self.api.box(100, c.axlLen, 2 * c.axlRad).mv(
                50 + axlX, axlY, axlZ
            )
            if self.cli.worm_axle_hole:
                axl += self.api.cylinder_y(100.0, self.cli.worm_axle_hole_radius).mv(
                    axlX, axlY, axlZ
                )
        turnaround = axl

        ## Disk
        dskX = axlX
        dskY = axlY # axlY - c.axlLen / 2 - c.dskTck / 2
        dskZ = axlZ
        if self.cli.implementation == Implementation.BLENDER:
            dskY = axlY -0.25

        if self.isCut:
            dsk = self.api.cylinder_y(c.dskTck, c.dskRad).mv(dskX, dskY, dskZ)
            dsk += self.api.box(100, c.dskTck, 2 * c.dskRad).mv(
                50 + dskX, dskY, dskZ
            )
        else:
            dsk = self.api.cylinder_rounded_y(c.dskTck, c.dskRad, 1/8).mv(dskX, dskY, dskZ)
        turnaround += dsk

        ## String holder torus
        if not self.isCut:
            str_rad = 0.75
            if False:
                torus = Tube(
                    args = [
                    "-H", f"{2*str_rad}",
                    "-in", f"{2*c.dskRad-2*str_rad}",
                    "-out", f"{2*c.dskRad+str_rad}",
                    "-i", self.cli.implementation
                    ]
                ).gen_full().rotate_z(90)
            else:
                torus = Torus( args = [
                    "-r1", f"{str_rad}",
                    "-r2", f"{c.dskRad}",
                    "-i", self.cli.implementation
                    ]
                ).gen_full()
            turnaround -= torus

        ## Slit
        if self.isCut:
            # upper vertical slit
            slit = self.api.box(c.sltLen, c.sltWth, c.sltHt)\
                .mv(c.sltLen/2 - c.front, 0, c.sltHt/2 - 2*c.axlRad)
            # upper diagonal slit
            slit += self.api.regpoly_extrusion_y(c.sltWth, c.sltWth * 2, 4)\
                .mv(-c.front, 0, c.sltHt - 2*c.axlRad) # dx was -c.sltLen/2
            # lower vertical slit
            slit += self.api.box(c.sltLen, c.sltWth, c.sltHt)\
                .mv(c.sltLen/2 - c.front, 0, -c.sltHt/2 + 2*c.axlRad)
            # upper diagonal slit
            slit += self.api.regpoly_extrusion_y(c.sltWth, c.sltWth * 2, 4)\
                .mv(-c.front, 0, -c.sltHt + 2*c.axlRad)
            turnaround += slit

        return turnaround

def main(args=None):
    """Generate turnaround"""
    return main_maker(module_name=__name__, class_name="LeleTurnaround", args=args)

def test_turnaround(self, apis=None):
    """Test turnaround"""

    tests = {
        "default":[],
        "cut" : "-C"
        }
    test_loop(module=__name__, tests=tests, apis=apis)

def test_turnaround_mock(self):
    """Test turnaround"""
    test_turnaround(self, apis=["mock"])


if __name__ == "__main__":
    main()
