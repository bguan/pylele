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

class LeleBottomAssembly(LeleBase):
    """ Pylele Body Bottom Assembly Generator class """

    def gen_tail(self,is_cut = False ,cutters=[]) -> Shape:
        """ generate tail """
        tailCut = LeleTail(cli=self.cli, isCut=is_cut)
        for cut in cutters:
            if not cut is None:
                tailCut = tailCut.cut(cut)
        return tailCut

    def gen(self) -> Shape:
        """ Generate Body Bottom Assembly """

        txtCut = LeleTexts(cli=self.cli, isCut=True)
        top = LeleTopAssembly(cli=self.cli)
        neck = LeleNeckAssembly(cli=self.cli)
        tnrsCut = LeleTuners(cli=self.cli, isCut=True)

        bodyJoiners = []
        bodyCutters = [txtCut]

        if not self.cli.body_type in [LeleBodyType.FLAT , LeleBodyType.FLAT_HOLLOW]:
            chmCut = LeleChamber(cli=self.cli, isCut=True, cutters=[LeleBrace(cli=self.cli)])
            bodyCutters += [chmCut]

        if self.cli.num_strings > 1:
            spCut = LeleSpines(cli=self.cli, isCut=True).mv(0, 0, self.api.getJoinCutTol())
            bodyCutters.append(spCut)

        top.gen_full()
        if self.cli.separate_top:
            rimCut = LeleRim(cli=self.cli, isCut=True)
            bodyCutters.append(rimCut)
            self.add_part(top)
        else:
            bodyJoiners.append(top)
            self.add_parts(top)

        neck.gen_full()
        if self.cli.separate_neck:
            nkJntCut = LeleNeckJoint(cli=self.cli, isCut=True).mv(-self.api.getJoinCutTol(), 0, self.api.getJoinCutTol())
            bodyCutters.append(nkJntCut)
            self.add_part(neck)
        else:
            bodyJoiners.append(neck)
            self.add_parts(neck)

        if self.cli.separate_fretboard or self.cli.separate_top:
            fbspCut = LeleFretboardSpines(cli=self.cli, isCut=True).mv(0, 0, -self.api.getJoinCutTol()) \
            if self.cli.separate_fretboard or self.cli.separate_neck or self.cli.separate_top else None
            bodyCutters.append(fbspCut)

        bodyCutters.append(tnrsCut)

        

        if TunerType[self.cli.tuner_type].value.is_worm() and self.cli.worm_has_key:
            wormKeyCut = LeleWormKey(cli=self.cli, isCut=True)
            bodyCutters.append(wormKeyCut)
        else:
            wormKeyCut = None

        ## add tail
        tail_cutters = [tnrsCut,wormKeyCut]
        if self.cli.separate_end:
            tailCut = self.gen_tail(cutters=tail_cutters,is_cut=True)
            self.add_part(tailCut)
            bodyCutters.append(tailCut)
        elif self.cli.body_type==LeleBodyType.FLAT_HOLLOW:
            # join tail to body if flat hollow and not separate end
            tailCut = self.gen_tail(cutters=tail_cutters,is_cut=False)
            bodyJoiners.append(tailCut)
        
        ## body
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


TESTS = {
    'separate_bridge'    : ['-B'],
    'separate_top'       : ['-T'],
    'separate_neck'      : ['-N'],
    'separate_fretboard' : ['-F'],
    'separate_all'       : ['-F','-N','-T','-B','-NU','-FR','-D','-G'],
    'gotoh_tuners'       : ['-t','gotoh'],
    'worm_tuners'        : ['-t','worm'],
    'worm_key'           : ['-t','worm','-whk'],
    'big_worm_tuners'    : ['-t','bigWorm'],
    'tail_end'           : ['-t','worm','-e','60','-E','-wah'],
}

TESTS_CQ = {
        'flat'          : ['-t',   'worm','-e','80','-E','-wah', '-bt', LeleBodyType.FLAT,'-wsl','35'],
        'flat_bigworm'  : ['-t','bigworm','-e','80','-E','-wah', '-bt', LeleBodyType.FLAT,'-wsl','45','-fbt','35'],
        'flat_hollow_bigworm' : ['-t','bigworm','-e','80','-E','-wah', '-bt', LeleBodyType.FLAT_HOLLOW,'-wsl','45','-fbt','35'],
        'flat_hollow_bigworm_notail' : ['-t','bigworm','-e','80','-wah', '-bt', LeleBodyType.FLAT_HOLLOW,'-wsl','45','-fbt','35']
    }

def test_bottom_assembly(self):
    """ Test Bottom Assembly """

    """
    test_loop(module=__name__,
              apis=['cadquery','blender'],
              tests=TESTS
              )
    """

    # flat body only works with cadquery at the moment    
    test_loop(module=__name__,
              apis=['cadquery'],
              tests=TESTS|TESTS_CQ
              )

def test_bottom_assembly_mock(self):
    """ Test Bottom Assembly """
    test_loop(module=__name__,
              apis=['mock'],
              tests=TESTS | TESTS_CQ
              )

if __name__ == '__main__':
    main()
