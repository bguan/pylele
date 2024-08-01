#!/usr/bin/env python3

"""
    Pylele Fretboard Assembly
"""

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import Implementation, FILLET_RAD
from pylele_frets import LeleFrets
from pylele_fretboard_dots import LeleFretboardDots
from pylele_fretboard import LeleFretboard
from pylele_top import LeleTop
from pylele_strings import LeleStrings
from pylele_fretboard_spines import LeleFretboardSpines
class LeleFretboardAssembly(LeleBase):
    """ Pylele Fretboard Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Fretboard Assembly """

        strCuts = LeleStrings(isCut=True) # use by others too
        frets = LeleFrets()
        fdotsCut = LeleFretboardDots(isCut=True)
        topCut = LeleTop(isCut=True).mv(0, 0, -self.cfg.joinCutTol) if self.cfg.sepFretbd or self.cfg.sepNeck else None

        fbJoiners = [frets]
        fbCutters = [fdotsCut, strCuts]
        fbFillets = {}

        if self.cfg.sepFretbd or self.cfg.sepNeck:
            fbCutters.insert(0, topCut)
            # blender mesh based edges can't handle curves
            if self.cfg.impl == Implementation.CAD_QUERY:
                fbFillets[FILLET_RAD] = [(self.cfg.fretbdLen, 0, .5*self.cfg.fretbdHt)]

        fretbd = LeleFretboard(joiners=fbJoiners,
                               cutters=fbCutters,
                               fillets=fbFillets)
        
        fretbd.gen_full()

        # Can't use joiners for fretbd joint & spines, as fbCutters will remove them 
        # as joins happen before cuts
        if self.cfg.sepFretbd or self.cfg.sepNeck:
            fretbd = fretbd \
            .join(LeleFretboardSpines(isCut=False)) # \
            # .join(FretbdJoint(cfg, isCut=False))

        self.shape = fretbd.shape

        return self.shape

def fretboard_assembly_main():
    """ Generate Fretboard Assembly """
    solid = LeleFretboardAssembly()
    solid.export_configuration()
    solid.exportSTL()
    return solid

if __name__ == '__main__':
    fretboard_assembly_main()
