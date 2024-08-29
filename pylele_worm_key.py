#!/usr/bin/env python3

"""
    Pylele Worm Key
"""

import os
from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL, Implementation, WormConfig, FILLET_RAD

class LeleWormKey(LeleBase):
    """ Pylele Worm Key Generator class """

    def gen(self) -> Shape:
        """ Generate Worm Key """
        isBlender = self.cfg.impl == Implementation.BLENDER
        joinTol = self.cfg.joinCutTol
        tailX = self.cfg.tailX
        txyzs = self.cfg.tnrXYZs
        assert isinstance(self.cfg.tnrCfg,WormConfig)
        wcfg: WormConfig = self.cfg.tnrCfg
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        btnHt = wcfg.buttonHt + 2*cutAdj
        btnWth = wcfg.buttonWth + 2*cutAdj
        btnTck = wcfg.buttonTck + 2*cutAdj
        kbHt = wcfg.buttonKeybaseHt + 2*cutAdj
        kbRad = wcfg.buttonKeybaseRad + cutAdj
        kyRad = wcfg.buttonKeyRad + cutAdj
        kyLen = wcfg.buttonKeyLen + 2*cutAdj

        key = self.api.genPolyRodX(kyLen, kyRad, 6).mv(joinTol -kyLen/2 -kbHt -btnHt, 0, 0)
        base = self.api.genPolyRodX(kbHt, kbRad, 36) if isBlender else self.api.genRodX(kbHt, kbRad)
        base = base.mv(-kbHt/2 -btnHt, 0, 0)
        btn = self.api.genBox(100 if self.isCut else btnHt, btnTck, btnWth)\
            .mv(50 -btnHt if self.isCut else -btnHt/2, 0, 0)
        
        if self.isCut:
            btnExtCut = self.api.genRodX(100 if self.isCut else btnHt, btnWth/2)\
                .scale(1, .5, 1)\
                .mv(50 -btnHt if self.isCut else -btnHt/2, btnTck/2, 0)
            btn = btn.join(btnExtCut)
        else:
            btn = btn.filletByNearestEdges([], FILLET_RAD)

        btn = btn.join(base).join(key)
        maxTnrY = max([y for _, y, _ in txyzs])
        btn = btn.mv(tailX - joinTol, maxTnrY + btnTck -1, -1 -btnWth/2)
        self.shape = btn
        return btn

def worm_key_main(args=None):
    """ Generate Worm Key """
    solid = LeleWormKey(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_worm_key():
    """ Test Worm Key """

    component = 'worm_key'
    tests = {
        'cut'     : ['-t','worm','-C'],
        'cadquery': ['-t','worm','-i','cadquery'],
        'blender' : ['-t','worm','-i','blender'],
        'trimesh' : ['-t','worm','-i','trimesh'],
        'big_worm': ['-t','bigWorm'],
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        worm_key_main(args=args)


if __name__ == '__main__':
    worm_key_main()
