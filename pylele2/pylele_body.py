#!/usr/bin/env python3

"""
    Pylele Body
"""

import os
import argparse

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, LeleStrEnum

DEFAULT_FLAT_BODY_THICKNESS=20

class BodyType(LeleStrEnum):
    """ Body Type """
    GOURD = 'gourd'
    FLAT  = 'flat'

def pylele_body_parser(parser = None):
    """
    Pylele Body Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    parser.add_argument("-bt", "--body_type",
                    help="Body Type",
                    type=BodyType,
                    choices=list(BodyType),
                    default=BodyType.GOURD
                    )
    
    parser.add_argument("-fbt", "--flat_body_thickness", help=f"Body thickness [mm] when flat body, default {DEFAULT_FLAT_BODY_THICKNESS}",
                        type=float, default=DEFAULT_FLAT_BODY_THICKNESS)

    return parser
class LeleBody(LeleBase):
    """ Pylele Body Generator class """

    def gen(self) -> Shape:
        """ Generate Body """
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.extMidBotTck
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyPath

        if self.cli.body_type == BodyType.GOURD:
            # Gourd body
            bot = self.api.genLineSplineRevolveX(bOrig, bPath, -180).scale(1, 1, botRat)

            if midTck > 0:
                # Generates flat middle section of body
                bot = bot.mv(0, 0, -midTck)
                midR = self.api.genLineSplineExtrusionZ(bOrig, bPath, midTck)
                midL = midR.mirrorXZ()
                bot = bot.join(midL.mv(0, 0, -midTck)).join(midR.mv(0, 0, -midTck))

        elif self.cli.body_type == BodyType.FLAT:
            # Flat body
            midR = self.api.genLineSplineExtrusionZ(bOrig, bPath, -self.cli.flat_body_thickness)
            midL = midR.mirrorXZ()
            bot = midR.join(midL)
        else:
            assert self.cli.body_type in list(BodyType), f'Unsupported Body Type {self.cli.body_type}'

        self.shape = bot
        return bot
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser=pylele_body_parser( parser=parser )
        return super().gen_parser( parser=parser )

def body_main(args = None):
    """ Generate body """
    solid = LeleBody(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_body():
    """ Test body """

    component = 'body'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender'],
        'flat_body': ['-bt',str(BodyType.FLAT),'-fbt','50']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        body_main(args=args)

if __name__ == '__main__':
    body_main()
