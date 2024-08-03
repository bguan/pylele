#!/usr/bin/env python3

"""
    Pylele Strings
"""

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL, Fidelity

class LeleStrings(LeleBase):
    """ Pylele Strings Generator class """

    def gen(self) -> Shape:
        """ Generate Strings """

        if self.isCut:
            origFidel = self.cfg.fidelity
            self.api.setFidelity(Fidelity.MEDIUM)

        cutAdj = FIT_TOL if self.isCut else 0
        srad = self.cfg.STR_RAD + cutAdj
        paths = self.cfg.stringPaths

        strs = None
        for p in paths:
            str = self.api.genCirclePolySweep(srad, p)
            strs = str if strs == None else strs.join(str)

        if self.isCut:
            self.api.setFidelity(origFidel)

        self.shape = strs

        return strs

        pass

def strings_main():
    """ Generate Strings """
    solid = LeleStrings()
    solid.export_configuration()
    solid.exportSTL()
    return solid

if __name__ == '__main__':
    strings_main()
