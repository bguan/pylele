#!/usr/bin/env python3

"""
    Pylele Base Element
"""

import os
import argparse
from enum import Enum
from pylele_solid import LeleSolid
from pylele_config import LeleConfig, TunerType, SOPRANO_SCALE_LEN

class LeleStrEnum(Enum):
    """ Pylele Enumerator for String Types """
    def __str__(self):
        return self.value

def pylele_base_parser(parser = None):
    """
    Pylele Base Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    ## Numeric config options ###########################################
    parser.add_argument("-s", "--scale_length", help="Scale Length [mm], default 330",
                        type=int, default=SOPRANO_SCALE_LEN)
    parser.add_argument("-n", "--num_strings", help="Number of strings, default 4",
                        type=int, default=4)
    parser.add_argument("-a", "--action", help="Strings action [mm], default 2",
                        type=float, default=2)
    parser.add_argument("-g", "--nut_string_gap", help="Nut to String gap [mm], default 9",
                        type=float, default=9)
    parser.add_argument("-e", "--end_flat_width", help="Flat width at tail end [mm], default 0",
                        type=float, default=0)

    ## Chamber config options ###########################################

    parser.add_argument("-w", "--wall_thickness", help="Chamber Wall Thickness [mm], default 4",
                        type=float, default=4)
    parser.add_argument("-l", "--chamber_lift", help="Chamber Lift [mm], default 1",
                        type=float, default=1)
    parser.add_argument("-r", "--chamber_rotate", help="Chamber Rotation/Pitch [deg], default -.5°",
                        type=float, default=-.5)

    ## Non-Numeric config options #######################################

    parser.add_argument("-t", "--tuner_type", help="Type of tuners, default friction",
                        type=TunerType, choices=list(TunerType), default='friction')

    ## Cut options ######################################################

    parser.add_argument("-T", "--separate_top",
                        help="Split body top from body back.",
                        action='store_true')
    parser.add_argument("-N", "--separate_neck",
                        help="Split neck from body.",
                        action='store_true')
    parser.add_argument("-F", "--separate_fretboard",
                        help="Split fretboard from neck back.",
                        action='store_true')
    parser.add_argument("-B", "--separate_bridge",
                        help="Split bridge from body.",
                        action='store_true')
    parser.add_argument("-E", "--separate_end",
                        help="Split end block from body.",
                        action='store_true')
    parser.add_argument("-H", "--half",
                        help="Half Split",
                        action='store_true')

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
        self.cfg = LeleConfig(
            scaleLen=self.cli.scale_length,
            action=self.cli.action,
            numStrs=self.cli.num_strings,
            nutStrGap=self.cli.nut_string_gap,
            sepTop=self.cli.separate_top,
            sepFretbd=self.cli.separate_fretboard,
            sepNeck=self.cli.separate_neck,
            sepBrdg=self.cli.separate_bridge,
            sepEnd=self.cli.separate_end,
            endWth=self.cli.end_flat_width,
            wallTck=self.cli.wall_thickness,
            chmLift=self.cli.chamber_lift,
            chmRot=self.cli.chamber_rotate,
            # fret2Dots=self.cli.dot_frets,
            # txtSzFonts=self.cli.texts_size_font,
            # modelLbl=self.cli.model_label,
            half=self.cli.half,
            tnrType=self.cli.tuner_type,
            fidelity=self.cli.fidelity,
            impl=self.cli.implementation,
        )

        super().configure()
        # super().gen_full()

    def has_configuration(self):
        """ True if pylele has configuration class """
        if not hasattr(self, 'cfg') or self.cfg is None:
            return False
        return isinstance(self.cfg,LeleConfig)

    def export_configuration(self):
        """ Export Pylele Configuration """

        if not self.has_configuration():
            self.configure()

        out_fname = os.path.join(self._make_out_path(),self.fileNameBase + '_cfg.txt')
        with open(out_fname, 'w', encoding='UTF8') as f:
            f.write(repr(self.cfg))
        assert os.path.isfile(out_fname)

    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_base_parser(parser=parser) )
    
    def exportSTL(self,out_path=None) -> None:
        """ Generate .stl output file """
        if not self.has_configuration():
            self.configure()
        return super().exportSTL(out_path=out_path)

    def gen_full(self):
        """ Generate full shape including joiners, cutters and fillets """
        if not self.has_configuration():
            self.configure()
        return super().gen_full()
