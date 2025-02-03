#!/usr/bin/env python3

"""
    Worm Gear (using solipython)
    Modeled after "Guitar Tuners that actually work"
    https://www.thingiverse.com/thing:6099101
    That I have reworked here
    https://www.thingiverse.com/thing:6664561
"""

from solid2 import import_scad
from solid2.extensions.bosl2.gears import worm_gear, worm

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker, Implementation
from b13d.api.core import Shape
from b13d.parts.pencil import Pencil
from b13d.parts.torus import Torus

class WormGear(Solid):
    """ Generate Worm Gear """
    def gen(self) -> Shape:
        assert self.cli.implementation in [Implementation.SOLID2, Implementation.MOCK]
        
        """
        Usage: As a Module

        worm_gear(circ_pitch, teeth, worm_diam, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=], [shaft_diam=]) [ATTACHMENTS];
        worm_gear(mod=, teeth=, worm_diam=, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=], [shaft_diam=]) [ATTACHMENTS];

        Usage: As a Function

        vnf = worm_gear(circ_pitch, teeth, worm_diam, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=]);
        vnf = worm_gear(mod=, teeth=, worm_diam=, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=])
        """

        modulus = 2
        worm_pitch = 3
        worm_diam = 10
        worm_starts = 1
        teeth = 15
        pressure_angle = 35

        # inferred parameters
        gear_diam = 14.6
        worm_drive_teeth = 1.43
        gear_teeth = 1.4

        ## gear
        if self.isCut:
            gear = self.api.cylinder_z(worm_diam-2*worm_drive_teeth,
                                   gear_diam/2 + gear_teeth)
        else:
            gear = self.api.genShape(
                    solid=worm_gear(pitch=worm_pitch,
                                    teeth=teeth,
                                    worm_diam=worm_diam,
                                    worm_starts=worm_starts,
                                    pressure_angle=pressure_angle,
                                    # modulus = modulus
                                    )
                ).rotate_z(5)
    
        # shaft
        shaft_h = 10
        shaft_diam = 8
        shaft = self.api.cylinder_z(l=shaft_h, rad=shaft_diam/2)

        if not self.isCut:
            # string hole
            string_diam = 2
            string_cut = self.api.cylinder_x(l=2*worm_diam, rad=string_diam/2)
            string_cut <<= (0,0,shaft_h/2-string_diam)
            shaft -= string_cut

            # torus to shape shaft
            torus_rad = shaft_diam/4
            torus = Torus(
                args = ['-i', self.cli.implementation,
                        '-r1', f'{torus_rad}',
                        '-r2', f'{shaft_diam/2+torus_rad/2}'
                        ]
            ).gen_full()
            torus = torus.rotate_x(90)
            torus <<= (0,0,shaft_h/2 - string_diam)
            shaft -= torus
            
        shaft <<= (0,0,shaft_h/2)
        gear += shaft

        """    
        Usage: As a Module

        worm(circ_pitch, d, l, [starts=], [left_handed=], [pressure_angle=], [backlash=], [clearance=]);
        worm(mod=, d=, l=, [starts=], [left_handed=], [pressure_angle=], [backlash=], [clearance=]);

        Usage: As a Function

        vnf = worm(circ_pitch, d, l, [starts=], [left_handed=], [pressure_angle=], [backlash=], [clearance=]);
        vnf = worm(mod=, d=, l=, [starts=], [left_handed=], [pressure_angle=], [backlash=], [clearance=]);
        """

        ## drive
        drive_h = 10
        drive_teeth_l = 0.98
        if self.isCut:
            drive = self.api.cylinder_z(drive_h,rad=worm_diam/2+drive_teeth_l)
        else:
            drive = self.api.genShape(
                    solid=worm(pitch=worm_pitch,
                            d=worm_diam,
                            starts=worm_starts,
                            l=drive_h,
                            pressure_angle=pressure_angle,
                            # modulus = modulus
                            )
                )
                
        # drive cylindrical extension
        disk_h = (gear_diam - drive_h + 2)/2
        disk_low = self.api.cylinder_z(l=disk_h, rad=worm_diam/2)
        disk_high = disk_low.dup()
        disk_low  <<= (0,0,-(drive_h+disk_h)/2)
        disk_high <<= (0,0, (drive_h+disk_h)/2)
        drive += disk_low + disk_high

        if not self.isCut:
            # hex key hole
            hex_cut = Pencil(
                args = ['-i', self.cli.implementation,
                        '-s', '4.3',
                        '-d','0',
                        '-fh','0'
                        ]
            ).gen_full()
            drive -= hex_cut.rotate_y(90)
        
        # align drive with gear
        drive = drive.rotate_x(90).mv((gear_diam+worm_diam)/2,0,0)
        
        return drive + gear

def main(args=None):
    """ Generate a Tube """
    return main_maker(module_name=__name__,
                class_name='WormGear',
                args=args)

def test_worm_gear(self,apis=[Implementation.SOLID2]):
    """ Test worm gear """
    tests = {'default':[],
             'cut':['-C']}
    test_loop(module=__name__,apis=apis, tests=tests)

def test_worm_gear_mock(self):
    """ Test worm gear """
    test_loop(module=__name__,apis=[Implementation.MOCK])

if __name__ == '__main__':
    main(args=sys.argv[1:]+['-i',Implementation.SOLID2])
