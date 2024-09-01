#!/usr/bin/env python3

"""
    Pylele Bottom Assembly
"""

import os

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, LeleBodyType, TunerType
from pylele2.pylele_neck_joint import LeleNeckJoint
from pylele2.pylele_texts import LeleTexts, pylele_texts_parser
from pylele2.pylele_tail import LeleTail
from pylele2.pylele_rim import LeleRim
from pylele2.pylele_worm_key import LeleWormKey
from pylele2.pylele_body import LeleBody
from pylele2.pylele_spines import LeleSpines
from pylele2.pylele_fretboard_spines import LeleFretboardSpines
from pylele2.pylele_top_assembly import LeleTopAssembly
from pylele2.pylele_neck_assembly import LeleNeckAssembly
from pylele2.pylele_brace import LeleBrace
from pylele2.pylele_chamber import LeleChamber, pylele_chamber_parser
from pylele2.pylele_tuners import LeleTuners
from pylele2.pylele_fretboard_assembly import pylele_fretboard_assembly_parser
from pylele2.pylele_worm import pylele_worm_parser
from pylele2.pylele_config import CONFIGURATIONS

class LeleBottomAssembly(LeleBase):
    """ Pylele Body Bottom Assembly Generator class """

    def gen_tail(self,is_cut = False, cutters=[]) -> Shape:
        """ generate tail """
        tail = LeleTail(cli=self.cli, isCut=is_cut)
        for cut in cutters:
            if not cut is None:
                tail = tail.cut(cut)
        return tail

    def gen(self) -> Shape:
        """ Generate Body Bottom Assembly """

        ## Initialize Joiners and Cutters
        bodyJoiners = []
        bodyCutters = [LeleTexts(cli=self.cli, isCut=True)]

        ## Chamber
        if not self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.HOLLOW]:
            chamber_cutters = []
            if not self.cli.body_type in [LeleBodyType.TRAVEL]:
                chamber_cutters.append(LeleBrace(cli=self.cli))
            bodyCutters.append(
                LeleChamber(cli=self.cli, isCut=True, cutters=chamber_cutters)
            )

        ## Spines
        if self.cli.num_strings > 1:
            bodyCutters.append(
                LeleSpines(cli=self.cli, isCut=True).mv(0, 0, self.api.getJoinCutTol())
            )
            
        ## Top
        top = LeleTopAssembly(cli=self.cli)
        top.gen_full()
        if self.cli.separate_top:
            bodyCutters.append(LeleRim(cli=self.cli, isCut=True))
            self.add_part(top)
        else:
            bodyJoiners.append(top)
            self.add_parts(top)

        ## Neck
        neck = LeleNeckAssembly(cli=self.cli)
        neck.gen_full()
        if self.cli.separate_neck:
            bodyCutters.append(
                LeleNeckJoint(cli=self.cli, isCut=True)\
                .mv(-self.api.getJoinCutTol(), 0, self.api.getJoinCutTol())
                )
            self.add_part(neck)
        else:
            bodyJoiners.append(neck)
            self.add_parts(neck)

        if self.cli.separate_fretboard or self.cli.separate_neck or self.cli.separate_top:
            bodyCutters.append(
                LeleFretboardSpines(cli=self.cli, isCut=True).mv(0, 0, -self.api.getJoinCutTol())
            )

        ## Tuners
        tnrsCut = LeleTuners(cli=self.cli, isCut=True)
        bodyCutters.append(tnrsCut)

        ## Worm Key
        wormKeyCut = None
        if TunerType[self.cli.tuner_type].value.is_worm() and self.cli.worm_has_key:
            wormKeyCut = LeleWormKey(cli=self.cli, isCut=True)
            bodyCutters.append(wormKeyCut)

        ## Tail
        tail_cutters = [tnrsCut,wormKeyCut]
        if self.cli.separate_end:
            tailCut = self.gen_tail(cutters=tail_cutters,is_cut=True)
            self.add_part(tailCut)
            bodyCutters.append(tailCut)
        elif self.cli.body_type in [LeleBodyType.HOLLOW]:
            # join tail to body if flat hollow and not separate end
            bodyJoiners.append(
                self.gen_tail(cutters=tail_cutters,is_cut=False)
            )
        ## Body
        body = LeleBody(cli=self.cli, joiners=bodyJoiners, cutters=bodyCutters)

        self.shape = body.gen_full()

        return self.shape
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser=pylele_fretboard_assembly_parser(parser=parser)
        parser=pylele_chamber_parser(parser=parser)
        parser=pylele_texts_parser(parser=parser)
        parser=pylele_worm_parser(parser=parser)
        return super().gen_parser( parser=parser )
    
def main(args=None):
    """ Generate Body Bottom Assembly """
    return main_maker(
        module_name='pylele2.pylele_bottom_assembly',
        # module_name=__name__,
                      class_name='LeleBottomAssembly',
                      args=args)


def test_bottom_assembly(self,apis=['cadquery']):
    """ Test Bottom Assembly """

    tests = {
        'separate_bridge'    : ['-B'],
        'separate_top'       : ['-T'],
        'separate_neck'      : ['-N'],
        'separate_fretboard' : ['-F'],
        'separate_all'       : ['-F','-N','-T','-B','-NU','-FR','-D','-G'],
        'gotoh_tuners'       : ['-t','gotoh'],
        'worm_tuners'        : ['-t','worm'],
        'worm_key'           : ['-t','worm','-whk'],
        'big_worm_tuners'    : ['-t','bigWorm'],
    }

    test_loop(module=__name__,
              apis=apis,
              tests=tests|CONFIGURATIONS
              )

def test_bottom_assembly_mock(self):
    """ Test Bottom Assembly Mock """
    test_bottom_assembly(self,apis=['mock'])

if __name__ == '__main__':
    main()
