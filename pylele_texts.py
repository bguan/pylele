#!/usr/bin/env python3

"""
    Pylele Texts
"""

import os

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import Fidelity
from pylele_body import LeleBody

class LeleTexts(LeleBase):
    """ Pylele Texts Generator class """

    def gen(self) -> Shape:
        """ Generate Texts """
        origFidel = self.api.fidelity
        self.api.setFidelity(Fidelity.HIGH)

        scLen = self.cfg.scaleLen
        backRat = self.cfg.CHM_BACK_RATIO
        dep = self.cfg.EMBOSS_DEP

        if False:
            tsf = self.cfg.txtSzFonts
        else:
            tsf = self.cli.texts_size_font

        txtTck = self.cfg.TEXT_TCK
        bodyWth = self.cfg.bodyWth
        botRat = self.cfg.BOT_RATIO
        midBotTck = self.cfg.extMidBotTck
        cutTol = self.cfg.joinCutTol

        txtZ = -botRat * bodyWth/2 - midBotTck - 2
        allHt = sum([1.2*size for _, size, _ in tsf])
        tx = 1.05*scLen - allHt/(1+backRat)
        ls: Shape = None
        # print(tsf)
        for txt, sz, fnt in tsf:
            if not txt is None and not fnt is None:
                l = self.api.genTextZ(txt, sz, txtTck, fnt) \
                    .rotateZ(90).mirrorXZ().mv(tx + sz/2, 0, txtZ)
                ls = l if ls is None else ls.join(l)
            tx += sz
        botCut = LeleBody(cli=self.cli, isCut=True).mv(0, 0, cutTol)

        txtCut = ls.cut(botCut.shape).mv(0, 0, dep)
        self.api.setFidelity(origFidel)
        return txtCut

def texts_main(args = None):
    """ Generate texts """
    solid = LeleTexts(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_texts():
    """ Test texts """

    component = 'texts'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        texts_main(args=args)

if __name__ == '__main__':
    texts_main()
