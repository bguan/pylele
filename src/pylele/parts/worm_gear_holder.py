#!/usr/bin/env python3

"""
    Worm Gear (using solipython)
    Modeled after "Guitar Tuners that actually work"
    https://www.thingiverse.com/thing:6099101
    That I have reworked here
    https://www.thingiverse.com/thing:6664561
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker, Implementation
from b13d.api.core import Shape
from pylele.parts.worm_drive import WormDrive

class WormGearHolder(WormDrive):
    """ Generate Worm Gear Holder"""

    def configure(self):
        WormDrive.configure(self)

        self.wall_thickness = 1.4
        
        """
        self.holder_thickness = max([
            self.worm_diam-2*self.worm_drive_teeth, # from gear
            self.worm_diam/2+self.drive_teeth_l   , # from drive
        ]) + 2*self.wall_thickness + 2*self.cut_tolerance
        """
        self.holder_thickness = self.worm_diam + 2*self.wall_thickness + 2*self.cut_tolerance

        self.holder_width = 2*(self.gear_diam/2 + self.gear_teeth + self.wall_thickness)

    def gen(self) -> Shape:
        
        ## gear
        gear = self.api.cylinder_z(
            self.holder_thickness,
            rad = self.holder_width/2
            )
        
        ## join gear and drive
        """
        jx = self.gear_diam/2+self.disk_h
        joiner = self.api.box(
            jx,
            self.holder_width,
            self.holder_thickness,
        )
        joiner <<= (self.holder_width/2,0,0)
        gear += joiner
        """

        ## drive
        holder_x = self.worm_diam + 2*self.worm_drive_teeth + self.gear_diam/2 + self.wall_thickness
        drive = self.api.box(
            holder_x,
            self.holder_width,
            self.holder_thickness,
            )

        # align drive with gear
        drive = drive.mv(holder_x/2,0,0)

        # assemble holder
        holder = drive + gear
        if self.cli.implementation.has_hull():
            holder = holder.hull()

        # carve tuner hole
        holder -= WormDrive( args = [
            '-i', self.cli.implementation,
            '-g',
            '-C'
            ]
        ).gen_full()

        if True and self.cli.implementation == Implementation.SOLID2:
            holder += WormDrive( args = [
                '-i', self.cli.implementation,
                '-g'
                ]
            ).gen_full()

        return holder

def main(args=None):
    """ Generate a Tube """
    return main_maker(module_name=__name__,
                class_name='WormGearHolder',
                args=args)

def test_worm_gear_holder(self,apis=[Implementation.SOLID2]):
    """ Test worm gear """
    test_loop(module=__name__,apis=apis)

def test_worm_gear_holder_mock(self):
    """ Test worm gear holder """
    test_loop(module=__name__,apis=[Implementation.MOCK])

if __name__ == '__main__':
    main(args=sys.argv[1:]+['-i',Implementation.SOLID2])
    # main()

