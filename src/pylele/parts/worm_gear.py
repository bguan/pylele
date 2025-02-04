#!/usr/bin/env python3

"""
    Worm Gear (using solipython)
    Modeled after "Guitar Tuners that actually work"
    https://www.thingiverse.com/thing:6099101
    That I have reworked here
    https://www.thingiverse.com/thing:6664561
"""

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

    def configure(self):
        Solid.configure(self)
        
        # gear parameters
        self.modulus = 2
        self.worm_pitch = 3
        self.worm_diam = 10
        self.worm_starts = 1
        self.teeth = 15
        self.pressure_angle = 35

        # inferred parameters
        self.gear_diam = 14.6
        self.worm_drive_teeth = 1.43
        self.gear_teeth = 1.4

        # shaft parameters
        self.shaft_h = 10
        self.shaft_diam = 8

        # hex hole
        self.hex_hole = 4.3

        # string hole
        self.string_diam = 2

        # drive parameters
        self.drive_h = 10
        self.drive_teeth_l = 0.98

        # drive cylindrical extension
        self.disk_h = (self.gear_diam - self.drive_h + 2)/2

        # cut tolerance
        self.cut_tolerance = 0.3

    def gen(self) -> Shape:
        assert self.isCut or (self.cli.implementation in [Implementation.SOLID2, Implementation.MOCK])
        
        """
        Usage: As a Module

        worm_gear(circ_pitch, teeth, worm_diam, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=], [shaft_diam=]) [ATTACHMENTS];
        worm_gear(mod=, teeth=, worm_diam=, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=], [shaft_diam=]) [ATTACHMENTS];

        Usage: As a Function

        vnf = worm_gear(circ_pitch, teeth, worm_diam, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=]);
        vnf = worm_gear(mod=, teeth=, worm_diam=, [worm_starts=], [worm_arc=], [crowning=], [left_handed=], [pressure_angle=], [backlash=], [clearance=], [slices=])
        """

        tol = self.cut_tolerance if self.isCut else 0

        ## gear
        if self.isCut:
            gear = self.api.cylinder_z(
                    self.worm_diam-2*self.worm_drive_teeth,
                    self.gear_diam/2 + self.gear_teeth
                    )
        else:
            gear = self.api.genShape(
                    solid=worm_gear(pitch=self.worm_pitch,
                                    teeth=self.teeth,
                                    worm_diam=self.worm_diam,
                                    worm_starts=self.worm_starts,
                                    pressure_angle=self.pressure_angle,
                                    # modulus = modulus
                                    )
                ).rotate_z(5)
    
        # shaft
        shaft = self.api.cylinder_z(l=self.shaft_h, rad=self.shaft_diam/2 + tol)

        if not self.isCut:
            # string hole
            string_cut = self.api.cylinder_x(l=2*self.worm_diam, rad=self.string_diam/2)
            string_cut <<= (0,0,self.shaft_h/2-self.string_diam)
            shaft -= string_cut

            # torus to shape shaft
            torus_rad = self.shaft_diam/4
            torus = Torus(
                args = ['-i', self.cli.implementation,
                        '-r1', f'{torus_rad}',
                        '-r2', f'{self.shaft_diam/2+torus_rad/2}'
                        ]
            ).gen_full()
            torus = torus.rotate_x(90)
            torus <<= (0,0,self.shaft_h/2 - self.string_diam)
            shaft -= torus
            
        shaft <<= (0,0,self.shaft_h/2)
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
        if self.isCut:
            drive = self.api.cylinder_z(self.drive_h+2*tol,
                                        rad=self.worm_diam/2+self.drive_teeth_l+tol
                                        )
        else:
            drive = self.api.genShape(
                    solid=worm(pitch=self.worm_pitch,
                            d=self.worm_diam,
                            starts=self.worm_starts,
                            l=self.drive_h,
                            pressure_angle=self.pressure_angle,
                            # modulus = modulus
                            )
                )
                
        # drive cylindrical extension
        disk_low = self.api.cylinder_z(l=self.disk_h+tol, rad=self.worm_diam/2+tol)
        disk_high = disk_low.dup()
        disk_low  <<= (0,0,-(self.drive_h+self.disk_h)/2)
        disk_high <<= (0,0, (self.drive_h+self.disk_h)/2)
        drive += disk_low + disk_high

        # drive extension
        drive_ext = self.api.cylinder_z(l=self.drive_h+2*self.disk_h+2*20*tol + 2*2, 
                                        rad=self.hex_hole/2+2+2*tol
                                        )
        drive += drive_ext

        # hex key hole
        if not self.isCut:
            hex_cut = Pencil(
                args = ['-i', self.cli.implementation,
                        '-s', f'{self.hex_hole}',
                        '-d','0',
                        '-fh','0'
                        ]
            ).gen_full()
            drive -= hex_cut.rotate_y(90)
        
        # align drive with gear
        drive = drive.rotate_x(90).mv((self.gear_diam+self.worm_diam)/2,0,0)
        
        return drive + gear

def main(args=None):
    """ Generate a Tube """
    return main_maker(module_name=__name__,
                class_name='WormGear',
                args=args)

def test_worm_gear(self,apis=[Implementation.SOLID2]):
    """ Test worm gear """
    tests = {'default':None,
             'cut':['-C']}
    test_loop(module=__name__,apis=apis, tests=tests)

def test_worm_gear_mock(self):
    """ Test worm gear """
    test_loop(module=__name__,apis=[Implementation.MOCK])

if __name__ == '__main__':
    main(args=sys.argv[1:]+['-i',Implementation.SOLID2])
