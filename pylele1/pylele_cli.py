#!/usr/bin/env python3

import argparse

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from ast import literal_eval
from api.pylele_api import Implementation, Fidelity
from pylele1.pylele_config import LeleScaleEnum, type_scale_len, \
    DEFAULT_LABEL_SIZE, \
    DEFAULT_LABEL_FONT, DEFAULT_LABEL_SIZE_BIG, DEFAULT_LABEL_SIZE_SMALL, \
    ModelLabel, TunerType

def parseCLI():
    """
    Pylele Command Line Interface
    """
    parser = argparse.ArgumentParser(description='Pylele Configuration')

    ## Numeric config options ###########################################
    parser.add_argument("-s", "--scale_length", 
                        help=f"Scale Length [mm], or {LeleScaleEnum._member_names_}, default: {LeleScaleEnum.SOPRANO.value}",
                        type=type_scale_len, default=LeleScaleEnum.SOPRANO)
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

    parser.add_argument("-t", "--tuner_type", help=f"Type of tuners, default; {TunerType.FRICTION.name}",
                        type=str.upper, choices=TunerType._member_names_, default=TunerType.FRICTION.name)

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
    
    ## other options ######################################################

    parser.add_argument("-i", "--implementation", help="Underlying engine implementation, default cadquery",
                        type=Implementation, choices=list(Implementation), default='cadquery')
    
    parser.add_argument("-f", "--fidelity", help="Mesh fidelity for smoothness, default low",
                        type=Fidelity, choices=list(Fidelity), default='low')
    
    ## parse arguments ##########################################################
    
    return parser.parse_args()


if __name__ == '__main__':
    print(parseCLI())