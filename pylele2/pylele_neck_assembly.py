#!/usr/bin/env python3

"""
    Pylele Neck Assembly
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, LeleBodyType
from pylele2.pylele_spines import LeleSpines
from pylele2.pylele_fretboard_spines import LeleFretboardSpines
from pylele2.pylele_head import LeleHead
from pylele2.pylele_neck_joint import LeleNeckJoint
from pylele2.pylele_neck import LeleNeck
from pylele2.pylele_fretboard import LeleFretboard
from pylele2.pylele_fretboard_assembly import LeleFretboardAssembly, pylele_fretboard_assembly_parser, FretType, NutType
from pylele2.pylele_neck_bend import LeleNeckBend

class LeleNeckAssembly(LeleBase):
    """ Pylele Neck Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Neck Assembly """

        jtol = self.api.getJoinCutTol()

        neckJoiners = [LeleHead(cli=self.cli).mv(jtol,0,0)]
        neckCutters = []

        ## Fretboard
        fretbd = LeleFretboardAssembly(cli=self.cli)
        fretbd.gen_full()
        self.add_parts(fretbd.get_parts())

        if self.cli.separate_fretboard:
            fbCut = LeleFretboard(cli=self.cli, isCut=True)\
                .mv(0, 0, -jtol)
            neckCutters.append(fbCut)
            self.add_part(fretbd)
        else:
            if not self.cli.separate_top:
                neckJoiners.append(fretbd)

        ## Spines
        if self.cli.num_strings > 1:
            neckCutters.append(LeleSpines(cli=self.cli, isCut=True).mv(0, 0, self.api.getJoinCutTol()))

        ## Neck Join
        # if self.cli.separate_neck:
        #    neckJoiners.append(LeleNeckJoint(cli=self.cli, isCut=False))

        ## Neck Bend
        # if self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.HOLLOW, LeleBodyType.TRAVEL]:
        #    neckJoiners.append(LeleNeckBend(cli=self.cli))

        ## Fretboard Spines
        if self.cli.separate_fretboard or self.cli.separate_top or self.cli.separate_neck:
            neckCutters.append(
                LeleFretboardSpines(cli=self.cli, isCut=True).mv(0, 0, -self.api.getJoinCutTol())
                            )
        ## Neck
        self.shape = LeleNeck(cli=self.cli,
                        joiners=neckJoiners,
                        cutters=neckCutters)
        
        return self.shape.gen_full()
    
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

def test_neck_assembly(self, apis=None):
    """ Test Neck Assembly """

    tests = {
        'fret_nails'         : ['-ft', str(FretType.NAIL)],
        'zerofret'           : ['-nt', str(NutType.ZEROFRET)],
        'separate_neck'      : ['-N'],
        'separate_fretboard' : ['-F'],
        'separate_nut'       : ['-NU'],
        'separate_frets'     : ['-FR'],
        'separate_all'       : ['-N','-FR','-NU','-F'],
        'flat_body'          : ['-bt',LeleBodyType.FLAT]
    }

    test_loop(module=__name__,tests=tests,apis=apis)

def test_neck_assembly_mock(self):
    """ Test Neck Assembly """
    test_neck_assembly(self,apis=['mock'])

if __name__ == '__main__':
    main()
