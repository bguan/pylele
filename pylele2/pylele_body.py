#!/usr/bin/env python3

"""
    Pylele Body
"""

import os
import argparse

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, LeleStrEnum, TunerType, test_loop, main_maker, LeleBodyType, DEFAULT_FLAT_BODY_THICKNESS

def pylele_body_parser(parser = None):
    """
    Pylele Body Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    return parser
class LeleBody(LeleBase):
    """ Pylele Body Generator class """

    def gen(self) -> Shape:
        """ Generate Body """
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.extMidBotTck
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyPath

        if self.cli.body_type == LeleBodyType.GOURD:
            # Gourd body
            bot = self.api.genLineSplineRevolveX(bOrig, bPath, -180).scale(1, 1, botRat)

            if midTck > 0:
                # Generates flat middle section of body
                bot = bot.mv(0, 0, -midTck)
                midR = self.api.genLineSplineExtrusionZ(bOrig, bPath, midTck)
                midL = midR.mirrorXZ()
                bot = bot.join(midL.mv(0, 0, -midTck)).join(midR.mv(0, 0, -midTck))

        elif self.cli.body_type == LeleBodyType.FLAT:
            # Flat body
            midR = self.api.genLineSplineExtrusionZ(bOrig, bPath, -self.cli.flat_body_thickness)
            midL = midR.mirrorXZ()
            bot = midR.join(midL)
        else:
            assert self.cli.body_type in list(LeleBodyType), f'Unsupported Body Type {self.cli.body_type}'

        self.shape = bot
        return bot
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser=pylele_body_parser( parser=parser )
        return super().gen_parser( parser=parser )

def main(args = None):
    """ Generate body """
    return main_maker(module_name=__name__,
                      class_name='LeleBody',
                      args=args)

## Cadquery and blender
TESTS_ALL = {
    'tail_end'           : ['-t',TunerType.WORM.name,'-e','60','-E'],
}
## flat body only works with cadquery at the moment
TESTS_CQ = {
    'flat_body'          : ['-bt',str(LeleBodyType.FLAT),'-fbt','50'],
    'flat_body_worm'     : ['-bt',str(LeleBodyType.FLAT),'-t',TunerType.WORM.name,'-e','60','-E'],
}

def test_body(self):
    """ Test body """   
    test_loop(module=__name__,
              apis = ['cadquery','blender'],
              tests = TESTS_ALL)
    test_loop(module=__name__,
              apis = ['cadquery'],
              tests = TESTS_CQ)

def test_body_mock(self):
    """ Test body """   
    test_loop(module=__name__,
              apis = ['mock'],
              tests = TESTS_ALL | TESTS_CQ)

if __name__ == '__main__':
    main()
