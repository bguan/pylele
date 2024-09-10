#!/usr/bin/env python3

"""
    Pylele Strings
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape
from api.pylele_solid import Fidelity
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL

class LeleStrings(LeleBase):
    """ Pylele Strings Generator class """

    def gen(self) -> Shape:
        """ Generate Strings """

        if self.isCut:
            origFidel = self.cli.fidelity
            self.api.setFidelity(Fidelity.MEDIUM)

        cutAdj = FIT_TOL if self.isCut else 0
        srad = self.cfg.STR_RAD + cutAdj
        paths = self.cfg.stringPaths

        strs = None
        for p in paths:
            str = self.api.genCirclePolySweep(srad, p)
            strs = str if strs is None else strs.join(str)

        if self.isCut:
            self.api.setFidelity(origFidel)

        self.shape = strs

        return strs

        pass

def main(args=None):
    """ Generate Strings """
    return main_maker(module_name=__name__,
                    class_name='LeleStrings',
                    args=args)

def test_strings(self,apis=None):
    """ Test String """
    tests = {
        'cut'     : ['-C']
    }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_strings_mock(self):
    """ Test String """
    test_strings(self,apis=['mock'])
    
if __name__ == '__main__':
    main()
