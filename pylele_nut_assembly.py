#!/usr/bin/env python3

"""
    Pylele Nut Assembly
"""

import os
import argparse
from pylele_api import Shape
from pylele_base import LeleBase, LeleStrEnum
from pylele_nut import LeleNut
from pylele_strings import LeleStrings

class NutType(LeleStrEnum):
    """ Nut Type """
    NUT = 'nut'
    ZEROFRET = 'zerofret'

def pylele_nut_assembly_parser(parser = None):
    """
    Pylele Nut Assembly Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    parser.add_argument("-nt", "--nut_type",
                    help="Nut Type",
                    type=NutType,
                    choices=list(NutType),
                    default=NutType.NUT
                    )
    return parser
class LeleNutAssembly(LeleBase):
    """ Pylele Nut Assembly Generator class """

    def gen(self) -> Shape:
        """ Generate Nut Assembly """

        cutters = []
        if not self.cli.nut_type == NutType.ZEROFRET and not self.isCut:
            cutters.append( LeleStrings(isCut=True,cli=self.cli) )

        nut = LeleNut(
                        cutters=cutters,
                        cli=self.cli
                        )
        
        nut.gen_full()
        self.shape = nut.shape
        return self.shape
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_nut_assembly_parser(parser=parser) )

def nut_assembly_main(args=None):
    """ Generate Nut Assembly """
    solid = LeleNutAssembly(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_nut_assembly():
    """ Test Nut Assembly """

    component = 'nut_assembly'
    tests = {
        'separate_fretboard' : ['-F'],
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender'],
        'zerofret': ['-nt', str(NutType.ZEROFRET)],
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        # print(args)
        nut_assembly_main(args=args)

if __name__ == '__main__':
    nut_assembly_main()
