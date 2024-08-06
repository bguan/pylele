#!/usr/bin/env python3

"""
    Pylele Tail
"""

import os
from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL

class LeleTail(LeleBase):
    """ Pylele Tail Generator class """

    def gen(self) -> Shape:
        """ Generate Tail """
        assert self.cli.separate_end

        cfg = self.cfg
        joinTol = cfg.joinCutTol
        cutAdj = (FIT_TOL + 2*joinTol) if self.isCut else 0

        # this assertion should be verified
        assert self.cli.end_flat_width > 4.0 + 2*cutAdj, 'end_flat_width too small! %f, should be larger than %f' % (self.cli.end_flat_width, 4+2*cutAdj)        

        tailX = cfg.tailX
        chmBackX = cfg.scaleLen + cfg.chmBack
        tailLen = tailX - chmBackX + 2*cutAdj
        endWth = cfg.endWth + 2*cutAdj
        botRat = cfg.BOT_RATIO
        midBotTck = cfg.extMidBotTck + 2*cutAdj
        rimWth = cfg.rimWth+ 2*cutAdj
        
        top = None
        if midBotTck > 0:
            extTop = self.api.genBox(10 if self.isCut else rimWth, endWth, midBotTck)\
                .mv(tailX + (5 - rimWth if self.isCut else -rimWth/2), 0, -midBotTck/2)
            inrTop = self.api.genBox(2*tailLen, endWth -2*rimWth, midBotTck)\
                .mv(tailX -rimWth -tailLen, 0, -midBotTck/2)
            top = extTop.join(inrTop)
        
        extBot = self.api.genRodX(10 if self.isCut else rimWth, endWth/2).scale(1, 1, botRat)\
            .mv(tailX + (5 - rimWth if self.isCut else -rimWth/2), 0, -midBotTck)
        inrBot = self.api.genRodX(2*tailLen, endWth/2 - rimWth).scale(1, 1, botRat)\
            .mv(tailX - rimWth -tailLen, 0, -midBotTck)
        topCut = self.api.genBox(2000, 2000, 2000).mv(0,0,1000)
        bot = extBot.join(inrBot).cut(topCut)
        if top is None:
            tail = bot
        else:
            tail = top.join(bot)

        self.shape = tail
        return tail

def tail_main(args=None):
    """ Generate tail """
    solid = LeleTail(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_tail():
    """ Test Tail """

    component = 'tail'
    tests = {
        'cut'     : ['-E','-e','10','-C'],
        'cadquery': ['-E','-e','4.3','-i','cadquery'],
        'blender' : ['-E','-e','4.3','-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        tail_main(args=args)


if __name__ == '__main__':
    tail_main()
