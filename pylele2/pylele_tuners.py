#!/usr/bin/env python3

"""
    Pylele Tuners
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape, Fidelity
from pylele2.pylele_base import LeleBase, test_loop, main_maker
from pylele1.pylele_config import PegConfig, WormConfig
from pylele2.pylele_peg import LelePeg
from pylele2.pylele_worm import LeleWorm, pylele_worm_parser

class LeleTuners(LeleBase):
    """ Pylele Tuners Generator class """

    def gen(self) -> Shape:
        """ Generate Tuners """
        
        if self.isCut:
            origFidel = self.cfg.fidelity
            self.api.setFidelity(Fidelity.MEDIUM)

        tXYZs = self.cfg.tnrXYZs
        isPeg = isinstance(self.cfg.tnrCfg, PegConfig)
        isWorm = isinstance(self.cfg.tnrCfg, WormConfig)
        tnrs = None
        for txyz in tXYZs:
            tnr = LelePeg(isCut=self.isCut, cli=self.cli) if isPeg \
                else LeleWorm(isCut=self.isCut, cli=self.cli) if isWorm \
                else None
            if not tnr is None:
                tnr = tnr.mv(txyz[0], txyz[1], txyz[2]).shape
                tnrs = tnr if tnrs is None else tnrs.join(tnr)

        if self.isCut:
            self.api.setFidelity(origFidel)
        return tnrs
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_worm_parser(parser=parser) )

def main(args = None):
    """ Generate Tuners """
    return main_maker(module_name=__name__,
                    class_name='LeleTuners',
                    args=args)

def test_tuners():
    """ Test Tuners """
    tests = {
        'cut'     : ['-C'],
        'gotoh'   : ['-t','gotoh'],
        'worm'    : ['-t','worm'],
        'big_worm': ['-t','bigWorm'],
        'tail_end': ['-t','worm','-e','60','-E','-wah','-C']
    }
    test_loop(module=__name__,tests=tests)

if __name__ == '__main__':
    main()
