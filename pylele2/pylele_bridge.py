#!/usr/bin/env python3

"""
    Pylele Bridge
"""
import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape, Implementation
from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase
from pylele2.pylele_strings import LeleStrings


def pylele_bridge_parser(parser=None):
    """
    Pylele Bridge Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Pylele Bridge Configuration")

    parser.add_argument(
        "-bow",
        "--bridge_override_width",
        help="Override Bridge Width [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-bol",
        "--bridge_override_length",
        help="Override Bridge Length [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-boh",
        "--bridge_override_heigth",
        help="Override Bridge Heigth [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-bosr",
        "--bridge_override_string_radius",
        help="Override Bridge String Radius [mm]",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-bpiezo",
        "--bridge_piezo",
        help="Add space for a piezo microphone under the bridge",
        action="store_true",
    )
    parser.add_argument(
        "-bph",
        "--bridge_piezo_heigth",
        help="Bridge Piezo Heigth [mm]",
        type=float,
        default=1.5,
    )
    parser.add_argument(
        "-bpw",
        "--bridge_piezo_width",
        help="Bridge Piezo Width [mm]",
        type=float,
        default=2,
    )
    return parser


class LeleBridge(LeleBase):
    """Pylele Bridge Generator class"""

    def gen(self) -> Shape:
        """Generate Bridge"""
        fitTol = FIT_TOL
        scLen = float(self.cli.scale_length)

        if (
            hasattr(self.cli, "bridge_override_string_radius")
            and not self.cli.bridge_override_string_radius is None
        ):
            strRad = self.cli.bridge_override_string_radius
        else:
            strRad = self.cfg.STR_RAD

        if (
            hasattr(self.cli, "bridge_override_width")
            and not self.cli.bridge_override_width is None
        ):
            brdgWth = self.cli.bridge_override_width
        else:
            brdgWth = self.cfg.brdgWth + (2 * fitTol if self.isCut else 0)

        if (
            hasattr(self.cli, "bridge_override_length")
            and not self.cli.bridge_override_length is None
        ):
            brdgLen = self.cli.bridge_override_length
        else:
            brdgLen = self.cfg.brdgLen + (2 * fitTol if self.isCut else 0)

        if (
            hasattr(self.cli, "bridge_override_heigth")
            and not self.cli.bridge_override_heigth is None
        ):
            brdgHt = self.cli.bridge_override_heigth
            # strings will not move, so compensate z position for different heigth
            z_comp = brdgHt - 3.844291663553447  # + strRad
            brdgZ = self.cfg.brdgZ - z_comp
        else:
            brdgHt = self.cfg.brdgHt
            brdgZ = self.cfg.brdgZ

        if self.cli.implementation == Implementation.BLENDER and not self.isCut:
            # increase overlap when blender backend to force join
            brdgZ -= 1.5

        brdg = self.api.box(brdgLen, brdgWth, brdgHt).mv(
            scLen, 0, brdgZ + brdgHt / 2
        )

        if not self.isCut:
            cutRad = brdgLen / 2 - strRad
            cutHt = brdgHt - 2
            cutScaleZ = cutHt / cutRad

            frontCut = (
                self.api.cylinder_y(2 * brdgWth, cutRad)
                .scale(1, 1, cutScaleZ)
                .mv(scLen - cutRad - strRad, 0, brdgZ + brdgHt)
            )

            backCut = (
                self.api.cylinder_y(2 * brdgWth, cutRad)
                .scale(1, 1, cutScaleZ)
                .mv(scLen + cutRad + strRad, 0, brdgZ + brdgHt)
            )

            brdgTop = self.api.cylinder_y(brdgWth, strRad).mv(scLen, 0, brdgZ + brdgHt)

            brdg = brdg.cut(frontCut).cut(backCut).join(brdgTop)

            if self.cli.bridge_piezo:
                mic_cut = self.api.box(
                    self.cli.bridge_piezo_width, brdgWth, self.cli.bridge_piezo_heigth
                )
                mic_cut = mic_cut.mv(scLen, 0, brdgZ + self.cli.bridge_piezo_heigth / 2)
                brdg = brdg.cut(mic_cut)
        else:
            if self.cli.bridge_piezo:
                wire_rad = 2
                wire = self.api.cylinder_z(15, wire_rad).mv(
                    scLen, brdgWth / 2 - wire_rad, brdgZ
                )
                brdg = brdg.join(wire)

        # strings cut
        strings = LeleStrings(cli=self.cli, isCut=True)
        if not self.isCut and not self.cli.bridge_piezo:
            brdg = brdg.cut(strings.gen_full())

        return brdg

    def gen_parser(self, parser=None):
        """generate bridge parser"""
        parser = pylele_bridge_parser(parser=parser)
        return super().gen_parser(parser=parser)


def main(args=None):
    """Generate Bridge"""
    return main_maker(module_name=__name__, class_name="LeleBridge", args=args)


def test_bridge(self, apis=None):
    """Test Bridge"""
    tests = {
        "default" : [],
        "cut": ["-C"],
        "override_width": ["-bow", "100"],
        "override_length": ["-bol", "55"],
        "override_height": ["-boh", "3"],
        "override_string_radius": ["-bosr", "1.5"],
        "piezo": ["-bpiezo"],
        "cut_piezo": ["-C", "-bpiezo"],
    }
    test_loop(module=__name__, tests=tests, apis=apis)


def test_bridge_mock(self):
    """Test Bridge"""
    test_bridge(self, apis=["mock"])


if __name__ == "__main__":
    main()
