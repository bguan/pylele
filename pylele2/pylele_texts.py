#!/usr/bin/env python3

"""
    Pylele Texts
"""

import os
import argparse
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape, Fidelity
from pylele2.pylele_base import LeleBase, test_loop, main_maker
from pylele2.pylele_body import LeleBody, pylele_body_parser

DEFAULT_LABEL_SIZE = 9
DEFAULT_LABEL_SIZE_BIG = 24
DEFAULT_LABEL_SIZE_SMALL = 6
DEFAULT_LABEL_FONT = 'Verdana'

def pylele_texts_parser(parser = None):
    """
    Pylele Texts Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    # parser = pylele_body_parser(parser=parser)
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

    parser.add_argument("-txt", "--text_en",
                        help="Enable Generation of Text emboss",
                        action='store_true')

    return parser

class LeleTexts(LeleBase):
    """ Pylele Texts Generator class """

    def gen(self) -> Shape:
        """ Generate Texts """
        assert self.cli.text_en

        if self.isCut:
            origFidel = self.api.fidelity
            self.api.setFidelity(Fidelity.LOW)

        scLen = self.cli.scale_length
        backRat = self.cfg.CHM_BACK_RATIO
        dep = self.cfg.EMBOSS_DEP

        tsf = self.cli.texts_size_font

        txtTck = self.cfg.TEXT_TCK
        bodyWth = self.cfg.bodyWth
        botRat = self.cfg.BOT_RATIO
        midBotTck = self.cfg.extMidBotTck
        cutTol = self.api.getJoinCutTol()

        txtZ = -botRat * bodyWth/2 - midBotTck - 2
        allHt = sum([1.2*size for _, size, _ in tsf])
        tx = 1.05*scLen - allHt/(1+backRat)
        ls: Shape = None
        for txt, sz, fnt in tsf:
            if not txt is None and not fnt is None:
                # orig impl uses mirrorXZ() instead of rotateX(180)
                # but Blender text mirroring can lead to weird output
                l = self.api.genTextZ(txt, sz, txtTck, fnt) \
                    .rotateZ(90).rotateX(180).mv(tx + sz/2, 0, txtZ +txtTck)
                ls = l if ls is None else ls.join(l)
            tx += sz
        botCut = LeleBody(cli=self.cli, isCut=True).mv(0, 0, cutTol)

        txtCut = ls.cut(botCut.shape).mv(0, 0, dep)
        if self.isCut:
            self.api.setFidelity(origFidel)
        return txtCut

    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_texts_parser(parser=parser) )

def main(args = None):
    """ Generate texts """
    return main_maker(module_name=__name__,
                    class_name='LeleTexts',
                    args=args)

def test_texts(self,apis=None):
    """ Test texts """
    tests = {
        'default': ['-txt']
    }
    test_loop(module=__name__,apis=apis,tests=tests)

def test_texts_mock(self):
    """ Test texts """
    test_texts(self,apis=['mock'])

if __name__ == '__main__':
    main(sys.argv[1:]+['-txt'])