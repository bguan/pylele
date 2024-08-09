#!/usr/bin/env python3

"""
    Pylele Body
"""

import os

from pylele_api import Shape
from pylele_base import LeleBase
class LeleBody(LeleBase):
    """ Pylele Body Generator class """

    def gen(self) -> Shape:
        """ Generate Body """
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.extMidBotTck
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyPath

        bot = self.api.genLineSplineRevolveX(bOrig, bPath, -180).scale(1, 1, botRat)

        if midTck > 0:
            bot = bot.mv(0, 0, -midTck)
            midR = self.api.genLineSplineExtrusionZ(bOrig, bPath, midTck)
            midL = midR.mirrorXZ()
            bot = bot.join(midL.mv(0, 0, -midTck)).join(midR.mv(0, 0, -midTck))

        self.shape = bot
        return bot

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
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        body_main(args=args)

if __name__ == '__main__':
    body_main()
