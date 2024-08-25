#!/usr/bin/env python3

"""
    Pylele Tail
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL, LeleBodyType

class LeleTail(LeleBase):
    """ Pylele Tail Generator class """

    def gen(self) -> Shape:
        """ Generate Tail """
        assert self.cli.separate_end

        cfg = self.cfg
        joinTol = self.api.getJoinCutTol() # cfg.joinCutTol
        cutAdj = (FIT_TOL + 2*joinTol) if self.isCut else 0

        # this assertion should be verified
        assert self.cli.end_flat_width > 4.0 + 2*cutAdj, 'end_flat_width too small! %f, should be larger than %f' % (self.cli.end_flat_width, 4+2*cutAdj)        

        tailX = cfg.tailX
        chmBackX = self.cli.scale_length + cfg.chmBack
        tailLen = tailX - chmBackX + 2*cutAdj
        endWth = self.cli.end_flat_width + 2*cutAdj
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
        
        if self.cli.body_type == LeleBodyType.FLAT:
            extBot = self.api.genBox(10 if self.isCut else rimWth, endWth, self.cli.flat_body_thickness)\
            .mv(tailX + (5 - rimWth if self.isCut else -rimWth), 0, -self.cli.flat_body_thickness/2)
            inrBot = self.api.genBox(2*tailLen, endWth - rimWth, self.cli.flat_body_thickness)\
            .mv(tailX - rimWth -tailLen, 0, -self.cli.flat_body_thickness/2)
        else:
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

def main(args=None):
    """ Generate tail """
    return main_maker(module_name=__name__,
                    class_name='LeleTail',
                    args=args)

def test_tail(self,apis=None):
    """ Test Tail """

    tests = {
        'cut'          : ['-E','-e','10','-C'],
        'separate_tail': ['-E','-e','4.3'],
    }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_tail_mock(self):
    """ Test Tail """
    test_tail(self,apis=['mock'])

if __name__ == '__main__':
    main()
