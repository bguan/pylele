#!/usr/bin/env python3

"""
    Pylele Strings
"""

import os
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
            strs = str if strs is None else strs.join(str)

        if self.isCut:
            self.api.setFidelity(origFidel)

        self.shape = strs

        return strs

        pass

def strings_main(args=None):
    """ Generate Strings """
    solid = LeleStrings(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_strings():
    """ Test String """

    component = 'strings'

    tests = {
        'cut'     : ['-C'],
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        strings_main(args=args)

if __name__ == '__main__':
    strings_main()
