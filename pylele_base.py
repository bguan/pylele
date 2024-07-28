#!/usr/bin/env python3

"""
    Pylele Base Element
"""

import argparse
from pylele_solid import LeleSolid
from pylele_config import LeleConfig, TunerType, ModelLabel, \
    SOPRANO_SCALE_LEN, DEFAULT_LABEL_FONT, DEFAULT_LABEL_SIZE, DEFAULT_LABEL_SIZE_BIG, DEFAULT_LABEL_SIZE_SMALL


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

    parser.add_argument("-d", "--dot_frets",
                        help="Comma-separated fret[:dots] pairs, default 3,5:2,7,10,12:3,15,17:2,19,22",
                        type=lambda d: {
                            int(l[0]): 1 if len(l) < 2 else int(l[1])
                            for l in (fns.split(':') for fns in d.split(','))
                        },
                        default={3: 1, 5: 2, 7: 1, 10: 1, 12: 3, 15: 1, 17: 2, 19: 1, 22: 1})

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

    parser.add_argument("-m", "--model_label", help="Model labeling choices, default short",
                        type=ModelLabel, choices=list(ModelLabel), default='short')
    
    return parser

class LeleBase(LeleSolid):
    """ Base element for Ukulele Parts """

    def __init__(self,
        joiners: list[LeleSolid] = [],
        cutters: list[LeleSolid] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        """ Initialization Method for Base ukuelele element """

        super().__init__(joiners, cutters, fillets)

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
            fret2Dots=self.cli.dot_frets,
            txtSzFonts=self.cli.texts_size_font,
            modelLbl=self.cli.model_label,
            half=self.cli.half,
            tnrType=self.cli.tuner_type,
            fidelity=self.cli.fidelity,
            impl=self.cli.implementation,
        )

        super().gen_full()

    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser( parser=pylele_base_parser(parser=parser) )

