#!/usr/bin/env python3

"""
    Pylele Base Element
"""

import os
import argparse
from enum import Enum

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_solid import LeleSolid, test_iteration, test_loop, main_maker, \
    FIT_TOL, FILLET_RAD, LeleStrEnum, export_dict2text
from pylele2.pylele_config import LeleConfig, TunerType, PegConfig, WormConfig, LeleBodyType, \
    LeleScaleEnum, SEMI_RATIO, DEFAULT_FLAT_BODY_THICKNESS, pylele_config_parser


def pylele_base_parser(parser = None):
    """
    Pylele Base Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')
    parser = pylele_config_parser(parser)
    return parser

class LeleBase(LeleSolid):
    """ Base element for Ukulele Parts """

    def __init__(self,
        isCut: bool = False,
        joiners: list[LeleSolid] = [],
        cutters: list[LeleSolid] = [],
        fillets: dict[tuple[float, float, float], float] = {},
        args = None,
        cli = None
    ):
        """ Initialization Method for Base ukuelele element """

        super().__init__(isCut=isCut,
                         joiners=joiners, 
                         cutters=cutters,
                         fillets=fillets,
                         args = args,
                         cli=cli
                         )

    def configure(self):

        # generate ukulele configuration
        self.cfg = LeleConfig(cli=self.cli)

        super().configure()
        # super().gen_full()

    def export_args(self):
        super().export_args()
        self.export_configuration()
    
    def has_configuration(self):
        """ True if pylele has configuration class """
        if not hasattr(self, 'cfg') or self.cfg is None:
            return False
        return isinstance(self.cfg,LeleConfig)

    def configure_if_hasnt(self):
        """ Geneate Pylele Configuration if not available """
        if not self.has_configuration():
            self.configure()

    def export_configuration(self):
        """ Export Pylele Configuration """

        self.configure_if_hasnt()
        export_dict2text(outpath=self._make_out_path(),
                         fname=self.fileNameBase + '_cfg.txt',
                         dictdata=self.cfg)

    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_base_parser(parser=parser) )
    
    def exportSTL(self,out_path=None) -> None:
        """ Generate .stl output file """
        self.configure_if_hasnt()
        return super().exportSTL(out_path=out_path)

    def gen_full(self):
        """ Generate full shape including joiners, cutters and fillets """
        self.configure_if_hasnt()
        return super().gen_full()
