#!/usr/bin/env python3

"""
    Pylele Fretboard Assembly
"""

import os
import argparse
from pylele_api import Shape
from pylele_base import LeleBase, LeleStrEnum
from pylele_config import Implementation, FILLET_RAD
from pylele_frets import LeleFrets
from pylele_nut import LeleNut, pylele_nut_parser, NutType
from pylele_fretboard_dots import LeleFretboardDots
from pylele_fretboard import LeleFretboard
from pylele_top import LeleTop
from pylele_fretboard_spines import LeleFretboardSpines
from pylele_fretboard_joint import LeleFretboardJoint

class FretType(LeleStrEnum):
    """ Pylele Fret Type """
    PRINT = 'print'
    NAIL = 'nail'

def pylele_fretboard_assembly_parser(parser = None):
    """
    Pylele Fretboard Assembly Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    parser = pylele_nut_parser(parser=parser)

    parser.add_argument("-ft", "--fret_type",
                    help="Fret Type",
                    type=FretType,
                    choices=list(FretType),
                    default=FretType.PRINT
                    )
    parser.add_argument("-NU", "--separate_nut",
                        help="Split nut from fretboard.",
                        action='store_true')
    return parser

def nut_is_cut(cli):
    """ Returns True if Nut is a cutter """
    if cli.separate_nut or \
       (cli.nut_type == NutType.ZEROFRET and cli.fret_type == FretType.NAIL):
        return True
    return False

def nut_is_join(cli):
    """ Returns True if Nut is a joiner """
    if not cli.separate_nut and (\
        cli.nut_type == NutType.NUT or \
        (cli.nut_type == NutType.ZEROFRET and cli.fret_type == FretType.PRINT) \
        ):
        return True
    return False

class LeleFretboardAssembly(LeleBase):
    """ Pylele Fretboard Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Fretboard Assembly """

        nut = LeleNut(cli=self.cli,isCut=nut_is_cut(self.cli))
        frets = LeleFrets(cli=self.cli)
        fdotsCut = LeleFretboardDots(isCut=True,cli=self.cli)
        topCut = LeleTop(isCut=True,cli=self.cli).mv(0, 0, -self.cfg.joinCutTol) if self.cfg.sepFretbd or self.cfg.sepNeck else None

        fbJoiners = []
        fbCutters = [fdotsCut]
        fbFillets = {}

        if self.cli.fret_type == FretType.PRINT:
            fbJoiners.append(frets)
        elif self.cli.fret_type == FretType.NAIL:
            fbCutters.append(frets)
        else:
            assert f'Unsupported FretType: {self.cli.fret_type} !'

        if nut_is_join(self.cli):
            fbJoiners.append(nut)
        elif nut_is_cut(self.cli):
            fbCutters.append(nut)

        if self.cfg.sepFretbd or self.cfg.sepNeck:
            fbCutters.insert(0, topCut)
            # blender mesh based edges can't handle curves
            if self.cfg.impl == Implementation.CAD_QUERY:
                fbFillets[FILLET_RAD] = [(self.cfg.fretbdLen, 0, .5*self.cfg.fretbdHt)]

        fretbd = LeleFretboard(joiners=fbJoiners,
                               cutters=fbCutters,
                               fillets=fbFillets,
                               cli=self.cli
                               )
        
        fretbd.gen_full()

        # Can't use joiners for fretbd joint & spines, as fbCutters will remove them 
        # as joins happen before cuts
        if self.cfg.sepFretbd or self.cfg.sepNeck:
            fretbd = fretbd \
            .join(LeleFretboardSpines(cli=self.cli)) \
            .join(LeleFretboardJoint(cli=self.cli))

        self.shape = fretbd.shape

        return self.shape
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_fretboard_assembly_parser(parser=parser) )

def fretboard_assembly_main(args=None):
    """ Generate Fretboard Assembly """
    solid = LeleFretboardAssembly(args=args)
    # solid.cli = solid.parse_args(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_fretboard_assembly():
    """ Test Fretboard Assembly """

    component = 'fretboard_assembly'
    tests = {
        'separate_fretboard' : ['-F'],
        'cadquery'           : ['-i','cadquery'],
        'blender'            : ['-i','blender'],
        'fret_nails'         : ['-ft', str(FretType.NAIL)],
        'zerofret'           : ['-nt', str(NutType.ZEROFRET)],
        'separate_nut'       : ['-NU'],
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        # print(args)
        fretboard_assembly_main(args=args)

if __name__ == '__main__':
    fretboard_assembly_main()
