#!/usr/bin/env python3

"""
    Pylele Top Assembly
"""

import os
from pylele_api import Shape
from pylele_config import FILLET_RAD, Implementation
from pylele_base import LeleBase
from pylele_bridge import LeleBridge
from pylele_guide import LeleGuide
from pylele_brace import LeleBrace
from pylele_chamber import LeleChamber
from pylele_fretboard_joint import LeleFretboardJoint
from pylele_tuners import LeleTuners
from pylele_soundhole import LeleSoundhole
from pylele_rim import LeleRim
from pylele_worm import WormConfig, pylele_worm_parser
from pylele_top import LeleTop
from pylele_fretboard_assembly import LeleFretboardAssembly, pylele_fretboard_assembly_parser, FretType, NutType

class LeleTopAssembly(LeleBase):
    """ Pylele Body Top Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Body Top Assembly """

        # gen bridge
        brdg = LeleBridge(cli=self.cli)

        # gen guide if using tuning pegs rather than worm drive
        guide = LeleGuide(cli=self.cli) if self.cfg.isPeg else None

        # gen body top
        chmCut = LeleChamber(cli=self.cli, isCut=True, cutters=[LeleBrace(cli=self.cli)])
        fbJntCut = LeleFretboardJoint(cli=self.cli, isCut=True).mv(-self.cfg.joinCutTol, 0, -self.cfg.joinCutTol) \
            if self.cli.separate_fretboard or self.cli.separate_neck else None
            # if cfg.sepFretbd or cfg.sepNeck else None
        tnrsCut = LeleTuners(cli=self.cli, isCut=True)
        topJoiners = []
        topCutters = [chmCut, tnrsCut, LeleSoundhole(cli=self.cli, isCut=True)]

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
            if self.cli.separate_bridge: # if cfg.sepBrdg:
                topCutters.append(LeleGuide(cli=self.cli, isCut=True))
            else:
                topJoiners.append(guide)

        topFillets = { FILLET_RAD: [(self.cfg.sndholeX, self.cfg.sndholeY, self.cfg.fretbdHt)] }
        # if self.cfg.isWorm and self.cfg.impl == Implementation.CAD_QUERY:
        if isinstance(self.cfg.tnrCfg,WormConfig) and self.cfg.impl == Implementation.CAD_QUERY:
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
        parser=pylele_worm_parser(parser=parser)
        return super().gen_parser( parser=parser )
    
def top_assembly_main(args=None):
    """ Generate Body Top Assembly """
    solid = LeleTopAssembly(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_top_assembly():
    """ Test Top Assembly """

    component = 'top_assembly'
    tests = {
        'cadquery'           : ['-i','cadquery'],
        'blender'            : ['-i','blender'],
        'separate_bridge'    : ['-B'],
        'separate_top'       : ['-T'],
        'separate_neck'      : ['-N'],
        'separate_fretboard' : ['-F'],
        'gotoh_tuners'       : ['-t','gotoh'],
        'worm_tuners'        : ['-t','worm'],
        'big_worm_tuners'    : ['-t','bigWorm'],
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        # print(args)
        top_assembly_main(args=args)

if __name__ == '__main__':
    top_assembly_main()
