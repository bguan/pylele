#!/usr/bin/env python3

"""
    Pylele Bottom Assembly
"""

import os
from pylele_api import Shape
from pylele_base import LeleBase
from pylele_neck_joint import LeleNeckJoint
from pylele_texts import LeleTexts, pylele_texts_parser
from pylele_tail import LeleTail
from pylele_rim import LeleRim
from pylele_worm_key import LeleWormKey
from pylele_body import LeleBody
from pylele_spines import LeleSpines
from pylele_fretboard_spines import LeleFretboardSpines
from pylele_top_assembly import LeleTopAssembly
from pylele_neck_assembly import LeleNeckAssembly
from pylele_brace import LeleBrace
from pylele_chamber import LeleChamber
from pylele_tuners import LeleTuners

from pylele_fretboard_assembly import pylele_fretboard_assembly_parser
from pylele_worm import pylele_worm_parser

class LeleBottomAssembly(LeleBase):
    """ Pylele Body Bottom Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Body Bottom Assembly """

        nkJntCut = LeleNeckJoint(cli=self.cli, isCut=True).mv(-self.cfg.joinCutTol, 0, self.cfg.joinCutTol) \
            if self.cli.separate_neck else None
        txtCut = LeleTexts(cli=self.cli, isCut=True)
        tailCut = LeleTail(cli=self.cli, isCut=True) if self.cli.separate_end else None # if cfg.sepEnd else None
        rimCut = LeleRim(cli=self.cli, isCut=True) if self.cli.separate_top else None # if cfg.sepTop else None
        wormKeyCut = LeleWormKey(cli=self.cli, isCut=True) if self.cfg.isWorm else None

        chmCut = LeleChamber(cli=self.cli, isCut=True, cutters=[LeleBrace(cli=self.cli)])
        spCut = LeleSpines(cli=self.cli, isCut=True).mv(0, 0, self.cfg.joinCutTol)\
            if self.cfg.numStrs > 1 else None
        
        fbspCut = LeleFretboardSpines(cli=self.cli, isCut=True).mv(0, 0, -self.cfg.joinCutTol) \
            if self.cfg.sepFretbd or self.cfg.sepNeck or self.cfg.sepTop else None

        top = LeleTopAssembly(cli=self.cli)
        neck = LeleNeckAssembly(cli=self.cli)
        tnrsCut = LeleTuners(cli=self.cli, isCut=True)

        bodyJoiners = []
        bodyCutters = [txtCut, chmCut]

        if spCut is not None:
            bodyCutters.append(spCut)

        top.gen_full()
        if self.cli.separate_top:
            bodyCutters.append(rimCut)
            self.add_part(top)
        else:
            bodyJoiners.append(top)
            self.add_parts(top)

        neck.gen_full()
        if self.cli.separate_neck:
            bodyCutters.append(nkJntCut)
            self.add_part(neck)
        else:
            bodyJoiners.append(neck)
            self.add_parts(neck)

        if self.cli.separate_fretboard or self.cli.separate_top:
            bodyCutters.append(fbspCut)
        
        if tailCut is not None:
            bodyCutters.append(tailCut)
            self.add_part(tailCut)
        else:
            bodyCutters.append(tnrsCut)
            if self.cfg.isWorm:
                bodyCutters.append(wormKeyCut)

        body = LeleBody(cli=self.cli, joiners=bodyJoiners, cutters=bodyCutters)

        self.shape = body.gen_full()

        return self.shape
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser=pylele_fretboard_assembly_parser(parser=parser)
        parser=pylele_texts_parser(parser=parser)
        parser=pylele_worm_parser(parser=parser)
        return super().gen_parser( parser=parser )
    
def bottom_assembly_main(args=None):
    """ Generate Body Bottom Assembly """
    solid = LeleBottomAssembly(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_bottom_assembly():
    """ Test Bottom Assembly """

    component = 'bottom_assembly'
    tests = {
        'separate_bridge'    : ['-B'],
        'separate_top'       : ['-T'],
        'separate_neck'      : ['-N'],
        'separate_fretboard' : ['-F'],
        'separate_all'       : ['-F','-N','-T','-B','-NU','-FR','-D','G'],
        'gotoh_tuners'       : ['-t','gotoh'],
        'worm_tuners'        : ['-t','worm'],
        'big_worm_tuners'    : ['-t','bigWorm'],
    }

    for test,args in tests.items():
        for api in ['cadquery','blender']:
            print(f'# Test {component} {test} {api}')
            outdir = os.path.join('./test',component,test,api)
            args += [
                '-o', outdir,
                '-i', api
                     ]
            # print(args)
            bottom_assembly_main(args=args)

if __name__ == '__main__':
    bottom_assembly_main()
