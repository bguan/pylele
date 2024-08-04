#!/usr/bin/env python3

"""
    Pylele Peg
"""

import os

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import PegConfig, FIT_TOL

class LelePeg(LeleBase):
    """ Pylele Peg Generator class """

    def gen(self) -> Shape:
        """ Generate Peg """
        cutAdj = FIT_TOL if self.isCut else 0
        cfg: PegConfig = self.cfg.tnrCfg
        strRad = self.cfg.STR_RAD + cutAdj
        holeHt = cfg.holeHt
        majRad = cfg.majRad + cutAdj
        minRad = cfg.minRad + cutAdj
        midTck = cfg.midTck
        botLen = cfg.botLen
        btnRad = cfg.btnRad + cutAdj
        topCutTck = 100 if self.isCut else 2  # big value for cutting
        botCutTck = botLen - midTck/3 if self.isCut else 2

        top = self.api.genRodZ(topCutTck, majRad).mv(0, 0, topCutTck/2)

        if not self.isCut:
            stemHt = holeHt + 4*strRad
            stem = self.api.genRodZ(stemHt, minRad/2).mv(0, 0, stemHt/2)
            hole = self.api.genRodX(2*minRad, strRad).mv(0, 0, holeHt)
            stem = stem.cut(hole)
            top = top.join(stem)

        mid = self.api.genRodZ(midTck, minRad).mv(0, 0, -midTck/2)

        if self.isCut:
            btnConeTck = botLen - midTck - 2*cutAdj
            btn = self.api.genConeZ(btnConeTck, btnRad, majRad)\
                .mv(0, 0, -midTck - btnConeTck)
            bot = self.api.genRodZ(botCutTck, btnRad)\
                .mv(0, 0, -botLen - botCutTck/2 + 2*cutAdj)
            botEnd = self.api.genBall(btnRad)\
                .scale(1, 1, .5 if self.cfg.sepEnd else 1)\
                .mv(0, 0, -botLen - botCutTck)
            bot = bot.join(botEnd)
        else:
            bot = self.api.genRodZ(botCutTck, majRad)\
                .mv(0, 0, -midTck - botCutTck/2)
            stem = self.api.genRodZ(botLen, minRad/2)\
                .mv(0, 0, -midTck - botLen/2)
            bot = bot.join(stem)
            btn = self.api.genBox(btnRad*2, btnRad/2, btnRad)\
                .mv(0, 0, -midTck - botLen - botCutTck/2 + btnRad/2)

        peg = top.join(mid).join(btn).join(bot)

        self.shape = peg
        return peg
        

def peg_main(args = None):
    """ Generate Peg """
    solid = LelePeg(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_peg():
    """ Test Peg """

    component = 'peg'
    tests = {
        'cut'     : ['-C'],
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        peg_main(args=args)

if __name__ == '__main__':
    peg_main()
