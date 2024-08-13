#!/usr/bin/env python3

"""
    Pylele Neck Assembly
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker
from pylele2.pylele_spines import LeleSpines
from pylele2.pylele_fretboard_spines import LeleFretboardSpines
from pylele2.pylele_head import LeleHead
from pylele2.pylele_neck_joint import LeleNeckJoint
from pylele2.pylele_neck import LeleNeck
from pylele2.pylele_fretboard import LeleFretboard
from pylele2.pylele_fretboard_assembly import LeleFretboardAssembly, pylele_fretboard_assembly_parser, FretType, NutType

class LeleNeckAssembly(LeleBase):
    """ Pylele Neck Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Neck Assembly """

        spCut = LeleSpines(cli=self.cli, isCut=True).mv(0, 0, self.cfg.joinCutTol)\
            if self.cfg.numStrs > 1 else None
        fbspCut = LeleFretboardSpines(cli=self.cli, isCut=True).mv(0, 0, -self.cfg.joinCutTol) \
            if self.cfg.sepFretbd or self.cfg.sepNeck or self.cfg.sepTop else None
        fbCut = LeleFretboard(cli=self.cli, isCut=True).mv(0, 0, -self.cfg.joinCutTol) if self.cfg.sepFretbd or self.cfg.sepTop else None
        fretbd = LeleFretboardAssembly(cli=self.cli)
        
        #f0Cut = Frets(cfg, isCut=True) \
        #    if cfg.sepFretbd or cfg.sepTop else None
        neckJoiners = [LeleHead(cli=self.cli)]
        neckCutters = []

        if self.cli.separate_fretboard:
            neckCutters.append(fbCut)
            self.add_part(fretbd)
        else:
            if not self.cli.separate_top:
                neckJoiners.append(fretbd)

        neckCutters.append(spCut)

        if self.cli.separate_neck:
            neckJoiners.append(LeleNeckJoint(cli=self.cli, isCut=False))

        if self.cli.separate_fretboard or self.cli.separate_top:
            neckCutters.extend([fbspCut])
        # neckCutters.append(strCuts)

        neck = LeleNeck(cli=self.cli,
                        joiners=neckJoiners,
                        cutters=neckCutters)
        
        fretbd.gen_full()
        self.add_parts(fretbd.get_parts())
        
        self.shape = neck.gen_full()
        return self.shape
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_fretboard_assembly_parser(parser=parser) )
    
def main(args=None):
    """ Generate Neck Assembly """
    return main_maker(module_name=__name__,
                    class_name='LeleNeckAssembly',
                    args=args)

def test_neck_assembly():
    """ Test Neck Assembly """

    tests = {
        'fret_nails'         : ['-ft', str(FretType.NAIL)],
        'zerofret'           : ['-nt', str(NutType.ZEROFRET)],
        'separate_neck'      : ['-N'],
        'separate_fretboard' : ['-F'],
        'separate_nut'       : ['-NU'],
        'separate_frets'     : ['-FR'],
        'separate_all'       : ['-N','-FR','-NU','-F'],
    }
    test_loop(module=__name__,tests=tests)

if __name__ == '__main__':
    main()
