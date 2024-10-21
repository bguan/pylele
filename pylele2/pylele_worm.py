#!/usr/bin/env python3

"""
    Pylele Worm
"""

import os
import argparse
import sys

from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
from pylele_config_common import TunerType

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase


def default_or_alternate(def_val, alt_val=None):
    """Override default value with alternate value, if available"""
    if alt_val is None:
        return def_val
    return alt_val


def pylele_worm_parser(parser=None):
    """
    Pylele Worm Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Pylele Worm Configuration")

    parser.add_argument(
        "-whh",
        "--worm_hole_heigth",
        help="Worm Hole Heigth [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wsl",
        "--worm_slit_length",
        help="Worm Slit Length [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wsw",
        "--worm_slit_width",
        help="Worm Slit Width [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wdit",
        "--worm_disk_thickness",
        help="Worm Disk Thickness [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wdir",
        "--worm_disk_radius",
        help="Worm Disk Radius [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-war",
        "--worm_axle_radius",
        help="Worm Axle Radius [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wal",
        "--worm_axle_length",
        help="Worm Axle Length [mm]",
        type=float,
        default=None,  # original worm tuner has 8mm axle
    )
    parser.add_argument(
        "-wdrr",
        "--worm_drive_radius",
        help="Worm Drive Radius [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wdrl",
        "--worm_drive_length",
        help="Worm Drive Length [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wdro",
        "--worm_drive_offset",
        help="Worm Drive Offser [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wga",
        "--worm_gap_adjust",
        help="Worm Gap Adjust [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wbt",
        "--worm_button_thickness",
        help="Worm Button Thickness [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wbw",
        "--worm_button_width",
        help="Worm Button Width [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wbh",
        "--worm_button_heigth",
        help="Worm Button heigth [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wbkl",
        "--worm_button_key_length",
        help="Worm Button Key Length [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wbkr",
        "--worm_button_key_radius",
        help="Worm Button Key Radius [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wbkbr",
        "--worm_button_key_base_radius",
        help="Worm Button Key Base Radius [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wbkbh",
        "--worm_button_key_base_heigth",
        help="Worm Button Key Base Heigth [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-wah",
        "--worm_axle_hole",
        help="Create Hole for worm gear axle.",
        action="store_true",
    )
    parser.add_argument(
        "-wahr",
        "--worm_axle_hole_radius",
        help="Worm Axle Radius [mm]",
        type=float,
        default=1.5,
    )
    parser.add_argument(
        "-whk",
        "--worm_has_key",
        help="Create Hole for worm key.",
        action="store_true",
    )
    return parser


class LeleWorm(LeleBase):
    """Pylele Worm Generator class"""

    def worm_config(self):
        """ worm configuration """
        tnrCfg = TunerType[self.cli.tuner_type].value
        assert tnrCfg.is_worm()

        cutAdj = FIT_TOL if self.isCut else 0
        c = WormConfig()
        c.sltLen = default_or_alternate(tnrCfg.slitLen,self.cli.worm_slit_length)
        c.sltWth = default_or_alternate(tnrCfg.slitWth,self.cli.worm_slit_width)
        c.drvRad = default_or_alternate(tnrCfg.driveRad + cutAdj,self.cli.worm_drive_radius)
        c.dskRad = default_or_alternate(tnrCfg.diskRad + cutAdj,self.cli.worm_disk_radius)
        c.dskTck = default_or_alternate(tnrCfg.diskTck + 2*cutAdj,self.cli.worm_disk_thickness)
        c.axlRad = default_or_alternate(tnrCfg.axleRad + cutAdj,self.cli.worm_axle_radius)
        c.axlLen = default_or_alternate(tnrCfg.axleLen + 2*cutAdj,self.cli.worm_axle_length)
        c.offset = default_or_alternate(tnrCfg.driveOffset,self.cli.worm_drive_offset)
        c.drvLen = default_or_alternate(tnrCfg.driveLen + 2*cutAdj,self.cli.worm_drive_length)

        return c
    
    def gen(self) -> Shape:
        """ Generate Worm """

        c = self.worm_config()

        # Note: Origin is middle of slit, near tip of axle

        ## Axle
        axlX = 0
        axlY = -0.5  # sltWth/2 -axlLen/2
        axlZ = 0
        
        axl = self.api.genRodY(c.axlLen, c.axlRad).mv(axlX, axlY, axlZ)
        if self.isCut:
            axl += self.api.genBox(100, c.axlLen, 2*c.axlRad)\
                .mv(50 + axlX, axlY, axlZ)
            if self.cli.worm_axle_hole:
                axl += self.api.genRodY(100.0, self.cli.worm_axle_hole_radius)\
                    .mv(axlX, axlY, axlZ)
        ## Disk
        dskX = axlX
        dskY = axlY - c.axlLen/2 - c.dskTck/2
        dskZ = axlZ
        
        dsk = self.api.genRodY(c.dskTck, c.dskRad).mv(dskX, dskY, dskZ)
        if self.isCut:
            dsk += self.api.genBox(
                100, c.dskTck, 2*c.dskRad).mv(50 + dskX, dskY, dskZ)

        ## Drive
        drvX = dskX
        drvY = dskY
        drvZ = dskZ + c.offset
        drv = self.api.genRodX(c.drvLen, c.drvRad).mv(drvX, drvY, drvZ)
        if self.isCut:
            drv += self.api.genRodX(100, c.drvRad).mv(50 + drvX, drvY, drvZ)

        worm = axl + dsk + drv

        ## Slit
        if self.isCut:
            (front, _, _, _, _, _) = (
                tnrCfg.dims()
            )  # enable open back slit w/o long slit front
            slit = self.api.genBox(sltLen, sltWth, 100).mv(
                sltLen / 2 - front, 0, 50 - 2 * axlRad
            )
            worm = worm.join(slit)

        self.shape = worm
        return worm

    def gen_parser(self, parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser(parser=pylele_worm_parser(parser=parser))


def main(args=None):
    """Generate Worm"""
    return main_maker(module_name=__name__, class_name="LeleWorm", args=args)


def test_worm(self, apis=None):
    """Test Worm"""

    tests = {
        "worm": ["-t", TunerType.WORM.name, "-wah"],
        "bigworm": ["-t", TunerType.BIGWORM.name, "-wah"],
    }
    test_loop(module=__name__, tests=tests, apis=apis)


def test_worm_mock(self):
    """Test Worm"""
    test_worm(self, apis=["mock"])


if __name__ == "__main__":
    main()
