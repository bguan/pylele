#!/usr/bin/env python3

"""
    Pylele Top Assembly
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape
from api.pylele_solid import Implementation
from pylele2.pylele_base import LeleBase, test_loop,main_maker, FILLET_RAD, LeleScaleEnum, LeleBodyType
from pylele2.pylele_bridge import LeleBridge
from pylele2.pylele_guide import LeleGuide
from pylele2.pylele_brace import LeleBrace
from pylele2.pylele_chamber import LeleChamber, pylele_chamber_parser
from pylele2.pylele_fretboard_joint import LeleFretboardJoint
from pylele2.pylele_tuners import LeleTuners
from pylele2.pylele_soundhole import LeleSoundhole
from pylele2.pylele_rim import LeleRim
from pylele2.pylele_worm import WormConfig, pylele_worm_parser
from pylele2.pylele_top import LeleTop
from pylele2.pylele_fretboard_assembly import LeleFretboardAssembly, pylele_fretboard_assembly_parser

class LeleTopAssembly(LeleBase):
    """ Pylele Body Top Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Body Top Assembly """

        # gen bridge
        brdg = LeleBridge(cli=self.cli)

        # gen guide if using tuning pegs rather than worm drive
        guide = LeleGuide(cli=self.cli) if self.cfg.tnrCfg.is_peg() else None

        # gen body top
        chmCut = LeleChamber(cli=self.cli, isCut=True, cutters=[LeleBrace(cli=self.cli)])
        fbJntCut = LeleFretboardJoint(cli=self.cli, isCut=True).mv(-self.api.getJoinCutTol(), 0, -self.api.getJoinCutTol()) \
            if self.cli.separate_fretboard or self.cli.separate_neck else None
        tnrsCut = LeleTuners(cli=self.cli, isCut=True)
        topJoiners = []
        topCutters = [tnrsCut]
                
        if not self.cli.body_type==LeleBodyType.FLAT:
            topCutters += [chmCut, LeleSoundhole(cli=self.cli, isCut=True)]

        if self.cli.separate_top: # if cfg.sepTop:
            topJoiners.append(LeleRim(cli=self.cli, isCut=False))

        if self.cli.separate_fretboard or self.cli.separate_neck: # if cfg.sepFretbd or cfg.sepNeck:
            topCutters.append(fbJntCut)
        
        if not self.cli.separate_fretboard and not self.cli.separate_neck: # if not cfg.sepFretbd and not cfg.sepNeck:
            fretbd = LeleFretboardAssembly(cli=self.cli)
            topJoiners.append(fretbd)

        if self.cli.separate_bridge: # cfg.sepBrdg:
            topCutters.append(LeleBridge(cli=self.cli, isCut=True))
            self.add_part(brdg)
        else:
            topJoiners.append(brdg)

        if not guide is None:
            if self.cli.separate_guide: # if cfg.sepBrdg:
                topCutters.append(LeleGuide(cli=self.cli, isCut=True))
                self.add_part(guide)
            else:
                topJoiners.append(guide)

        topFillets = { FILLET_RAD: [(self.cfg.sndholeX, self.cfg.sndholeY, self.cfg.fretbdHt)] }
        if isinstance(self.cfg.tnrCfg,WormConfig) and self.cli.implementation == Implementation.CAD_QUERY and \
            not self.cli.body_type == LeleBodyType.FLAT:
            wcfg: WormConfig = self.cfg.tnrCfg
            topFillets[wcfg.slitWth] = [
                (xyz[0] - wcfg.slitLen, xyz[1], xyz[2] + wcfg.holeHt)
                for xyz in self.cfg.tnrXYZs
            ]

        top = LeleTop(cli=self.cli, joiners=topJoiners, cutters=topCutters, fillets=topFillets)

        self.shape = top.gen_full()

        return self.shape
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser=pylele_fretboard_assembly_parser(parser=parser)
        parser=pylele_chamber_parser(parser=parser)
        parser=pylele_worm_parser(parser=parser)
        return super().gen_parser( parser=parser )
    
def main(args=None):
    """ Generate Body Top Assembly """
    return main_maker(module_name=__name__,
                    class_name='LeleTopAssembly',
                    args=args)

def test_top_assembly(self, apis = None):
    """ Test Top Assembly """    

    test_scale_len = {}
    for sl in list(LeleScaleEnum):
        test_scale_len[sl.name] = ['-s',sl.name]

    tests = {
            'separate_bridge'    : ['-B'],
            'separate_guide'     : ['-G'],
            'separate_top'       : ['-T'],
            'separate_neck'      : ['-N'],
            'separate_fretboard' : ['-F'],
            'gotoh_tuners'       : ['-t','gotoh'],
            'worm_tuners'        : ['-t','worm'],
            'big_worm_tuners'    : ['-t','bigWorm'],
        }

    tests_all = tests | test_scale_len
    test_loop(module=__name__,tests=tests_all,apis=apis)

def test_top_assembly_mock(self):
    """ Test Top Assembly """    
    test_top_assembly(self, apis=['mock'])

if __name__ == '__main__':
    main()
