#!/usr/bin/env python3

"""
    Pylele Fretboard
"""

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL

class LeleFretboard(LeleBase):
    """ Pylele Fretboard Generator class """

    def gen(self) -> Shape:
        """ Generate Fretboard """

        cutAdj = FIT_TOL if self.isCut else 0
        fbLen = self.cfg.fretbdLen + 2*cutAdj
        fbWth = self.cfg.fretbdWth + 2*cutAdj
        fbTck = self.cfg.FRETBD_TCK + 2*cutAdj
        fbHt = self.cfg.fretbdHt + 2*cutAdj
        riseAng = self.cfg.fretbdRiseAng

        path = self.cfg.fbCutPath if self.isCut else self.cfg.fbPath
        fretbd = self.api.genPolyExtrusionZ(path, fbHt)

        if self.isCut:
            fretbd = fretbd.mv(0, 0, -self.cfg.joinCutTol)
        else:
            topCut = self.api.genBox(fbLen * 2, fbWth, fbHt)\
                .rotateY(-riseAng)\
                .mv(0, 0, fbTck + fbHt/2)
            fretbd = fretbd.cut(topCut)
            fretbd = fretbd.filletByNearestEdges([(fbLen, 0, fbHt)], fbTck/2)

        self.shape = fretbd
        return fretbd

def fretboard_main():
    """ Generate Fretboard """
    solid = LeleFretboard()
    solid.export_configuration()
    solid.exportSTL()
    return solid

if __name__ == '__main__':
    fretboard_main()
