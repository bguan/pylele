#!/usr/bin/env python3

"""
    Pylele Texts
"""

import os
import argparse

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import Fidelity, \
    DEFAULT_LABEL_FONT, DEFAULT_LABEL_SIZE, DEFAULT_LABEL_SIZE_BIG, DEFAULT_LABEL_SIZE_SMALL
from pylele_body import LeleBody, pylele_body_parser

def pylele_texts_parser(parser = None):
    """
    Pylele Texts Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    parser = pylele_body_parser(parser=parser)
    ## text options ######################################################

    parser.add_argument("-x", "--texts_size_font",
                        help="Comma-separated text[:size[:font]] tuples, "\
                            + "default Pylele:28:Arial,:8,'mind2form.com © 2024':8:Arial",
                        type=lambda x: [
                            (l[0], 10 if len(l) < 2 else int(l[1]),
                             'Arial' if len(l) < 3 else l[2])
                            for l in (tsfs.split(':') for tsfs in x.split(','))
                        ],
                        default=[
                            ('PYLELE', DEFAULT_LABEL_SIZE_BIG, DEFAULT_LABEL_FONT), 
                            ('', DEFAULT_LABEL_SIZE_SMALL, None), # for empty line
                            ('mind2form.com © 2024', DEFAULT_LABEL_SIZE, DEFAULT_LABEL_FONT),
                        ])
    
    return parser

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
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_texts_parser(parser=parser) )

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
