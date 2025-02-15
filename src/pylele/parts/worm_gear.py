#!/usr/bin/env python3

"""
    Worm Gear (using solipython)
    Modeled after "Guitar Tuners that actually work"
    https://www.thingiverse.com/thing:6099101
    That I have reworked here
    https://www.thingiverse.com/thing:6664561
"""

from solid2.extensions.bosl2.gears import worm_gear, worm, enveloping_worm, worm_gear_thickness, worm_dist

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
        self.modulus = 1.5
        self.circ_pitch = 3      # The circular pitch, the distance between teeth centers around the pitch circle. Default: 5
        self.worm_diam = 10
        self.worm_starts = 1
        self.teeth = 14          # The number of teeth in the mated worm gear.
        self.pressure_angle = 25 # 32

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
        self.drive_h = self.worm_diam + self.gear_teeth
        self.drive_teeth_l = 0.98

        # drive cylindrical extension
        self.disk_h = (self.gear_diam - self.drive_h + 2)/2

        # cut tolerance
        self.cut_tolerance = 0.3

        self.tol = self.cut_tolerance if self.isCut else 0

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-g", "--gear_disable", help="Disable Generation of gear", action="store_true")
        parser.add_argument("-d", "--drive_disable", help="Disable Generation of gear", action="store_true")
        return parser

    def gen(self) -> Shape:
        assert self.isCut or (self.cli.implementation in [Implementation.SOLID2, Implementation.MOCK])
        
        if self.cli.gear_disable:
            gear = None
        else:
            gear = self.gen_gear()

        if self.cli.drive_disable:
            return gear
        else:
            drive = self.gen_drive()
            return drive + gear

    def gen_gear(self) -> Shape:
        """ Generate Gear """

        ## gear
        if self.isCut:
            gear = self.api.cylinder_z(
                    self.worm_diam-2*self.worm_drive_teeth,
                    self.gear_diam/2 + self.gear_teeth
                    )
        else:
            gear = self.api.genShape(
                    solid=worm_gear(circ_pitch=self.circ_pitch,
                                    teeth=self.teeth,
                                    worm_diam=self.worm_diam,
                                    worm_starts=self.worm_starts,
                                    pressure_angle=self.pressure_angle,
                                    # mod = self.modulus,
                                    spin = 19,
                                    worm_arc = 59
                                    )
                )
            if False:
                gear_h = worm_gear_thickness(
                    circ_pitch=self.circ_pitch,
                    teeth=self.teeth,
                    worm_diam=self.worm_diam,
                )

        # shaft
        shaft = self.api.cylinder_z(l=self.shaft_h, rad=self.shaft_diam/2 + self.tol)

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

        return gear

    def gen_drive(self) -> Shape:
        """ Generate Drive """

        ## drive
        if self.isCut:
            drive = self.api.cylinder_z(self.drive_h+2*self.tol,
                                        rad=self.worm_diam/2+self.drive_teeth_l+self.tol
                                        )
        else:

            if True:
                bworm = worm(circ_pitch=self.circ_pitch,
                                d=self.worm_diam,
                                starts=self.worm_starts,
                                l=self.drive_h,
                                pressure_angle=self.pressure_angle,
                                mod = self.modulus
                                )
            else:
                # bworm = enveloping_worm(circ_pitch=8, mate_teeth=45, d=30, _fn=72)
                bworm = enveloping_worm(circ_pitch=self.circ_pitch,
                                        mate_teeth=self.teeth,
                                        d=self.worm_diam,
                                        pressure_angle=self.pressure_angle)
                # bworm = enveloping_worm(
                                # circ_pitch=self.circ_pitch,
                                # d=self.worm_diam,
                                # starts=self.worm_starts,
                                # l=self.drive_h,
                                # pressure_angle=self.pressure_angle,
                                # mod = self.modulus,
                                # mate_teeth = 0.5
                #                )
                

            drive = self.api.genShape(
                    solid=bworm
                )
                
        # drive cylindrical extension
        disk_low = self.api.cylinder_z(l=self.disk_h+self.tol, rad=self.worm_diam/2+self.tol)
        disk_high = disk_low.dup()
        disk_low  <<= (0,0,-(self.drive_h+self.disk_h)/2)
        disk_high <<= (0,0, (self.drive_h+self.disk_h)/2)
        drive += disk_low + disk_high

        # drive extension
        drive_ext = self.api.cylinder_z(l=self.drive_h+2*self.disk_h+2*20*self.tol + 2*2,
                                        rad=self.hex_hole/2+2+2*self.tol
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
        dist = worm_dist(circ_pitch=self.circ_pitch,
                    d=self.worm_diam,
                    starts=self.worm_starts,
                    teeth=self.teeth, 
                    # [profile_shift],
                    pressure_angle=self.pressure_angle
                    )
        # drive = drive.rotate_x(90).mv((self.gear_diam+self.worm_diam)/2,0,0)
        drive = drive.rotate_x(90).mv(dist,0,0)
        
        return drive

def main(args=None):
    """ Generate a Tube """
    return main_maker(module_name=__name__,
                class_name='WormGear',
                args=args)

def test_worm_gear(self,apis=[Implementation.SOLID2]):
    """ Test worm gear """
    tests = {'default':[],
             'cut'    :['-C']}
    test_loop(module=__name__,apis=apis, tests=tests)

def test_worm_gear_mock(self):
    """ Test worm gear """
    test_loop(module=__name__,apis=[Implementation.MOCK])

if __name__ == '__main__':
    main(args=sys.argv[1:]+['-i',Implementation.SOLID2])
