#!/usr/bin/env python3

"""
    Pylele Bridge
"""
import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape, Implementation
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL
from pylele2.pylele_strings import LeleStrings

def pylele_bridge_parser(parser = None):
    """
    Pylele Bridge Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Bridge Configuration')

    parser.add_argument("-bow", "--bridge_override_width",
                    help="Override Bridge Width [mm]",
                    type=float,
                    default=None
                    )
    parser.add_argument("-bol", "--bridge_override_length",
                    help="Override Bridge Length [mm]",
                    type=float,
                    default=None
                    )
    parser.add_argument("-boh", "--bridge_override_heigth",
                    help="Override Bridge Heigth [mm]",
                    type=float,
                    default=None
                    )
    parser.add_argument("-bosr", "--bridge_override_string_radius",
                    help="Override Bridge String Radius [mm]",
                    type=float,
                    default=None
                    )
    return parser

class LeleBridge(LeleBase):
    """ Pylele Bridge Generator class """

    def gen(self) -> Shape:
        """ Generate Bridge """
        fitTol = FIT_TOL
        scLen = self.cli.scale_length

        if hasattr(self.cli,'bridge_override_string_radius') and \
            not self.cli.bridge_override_string_radius is None:
            strRad = self.cli.bridge_override_string_radius
        else:
            strRad = self.cfg.STR_RAD

        if hasattr(self.cli,'bridge_override_width') and \
            not self.cli.bridge_override_width is None:
            brdgWth = self.cli.bridge_override_width
        else:
            brdgWth = self.cfg.brdgWth + (2*fitTol if self.isCut else 0)

        if hasattr(self.cli,'bridge_override_length') and \
            not self.cli.bridge_override_length is None:
            brdgLen = self.cli.bridge_override_length
        else:
            brdgLen = self.cfg.brdgLen + (2*fitTol if self.isCut else 0)

        if hasattr(self.cli,'bridge_override_heigth') and \
            not self.cli.bridge_override_heigth is None:
            brdgHt = self.cli.bridge_override_heigth
            # strings will not move, so compensate z position for different heigth
            z_comp = brdgHt - 3.844291663553447 # + strRad
            brdgZ = self.cfg.brdgZ - z_comp
        else:
            brdgHt = self.cfg.brdgHt
            brdgZ = self.cfg.brdgZ

        if self.cli.implementation == Implementation.BLENDER and not self.isCut:
            # increase overlap when blender backend to force join
            brdgZ -= 1.5

        brdg = self.api.genBox(brdgLen, brdgWth, brdgHt).mv(
            scLen, 0, brdgZ + brdgHt/2)
        if not self.isCut:
            cutRad = brdgLen/2 - strRad
            cutHt = brdgHt - 2
            cutScaleZ = cutHt/cutRad
            frontCut = self.api.genRodY(2*brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen - cutRad - strRad, 0, brdgZ + brdgHt)
            backCut = self.api.genRodY(2*brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen + cutRad + strRad, 0, brdgZ + brdgHt)
            brdgTop = self.api.genRodY(brdgWth, strRad).mv(scLen, 0, brdgZ + brdgHt)
            brdg = brdg.cut(frontCut).cut(backCut).join(brdgTop)

        # strings cut
        strings = LeleStrings(cli=self.cli,isCut=True)
        brdg.cut(strings.gen_full())

        self.shape = brdg
        return brdg
    
    def gen_parser(self, parser=None):
        """ generate bridge parser """
        parser=pylele_bridge_parser(parser=parser)
        return super().gen_parser(parser=parser)

def main(args = None):
    """ Generate Bridge """
    return main_maker(module_name=__name__,
                    class_name='LeleBridge',
                    args=args)

def test_bridge(self,apis=None):
    """ Test Bridge """
    tests = {
        'cut'     : ['-C'],
        'override_width' : ['-bow','100'],
        'override_length' : ['-bol','55'],
        'override_height' : ['-boh','3'],
        'override_string_radius' : ['-bosr','1.5'],
    }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_bridge_mock(self):
    """ Test Bridge """
    test_bridge(self,apis=['mock'])

if __name__ == '__main__':
    main()
