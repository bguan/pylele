#!/usr/bin/env python3

import argparse
import sys
from pylele_config import *

TUNER_TYPES = {
    'friction': FRICTION_PEG_CFG,
    'gotoh': GOTOH_PEG_CFG,
    'worm': WORM_TUNER_CFG,
    'bigWorm': BIGWORM_TUNER_CFG,
}


def parseCLI():
    """
    Pylele Command Line Interface
    """
    parser = argparse.ArgumentParser(description='Pylele Configuration')

    ## Numeric config options ###########################################
    parser.add_argument("-s", "--scale_len", help="Scale Length [mm]",
                        type=int, default=SOPRANO_SCALE_LEN)
    parser.add_argument("-n", "--nstrings", help="Number of strings",
                        type=int, default=4)
    parser.add_argument("-a", "--action", help="Strings action [mm]",
                        type=float, default=2)
    parser.add_argument("-g", "--nut_string_gap", help="Nut to String gap [mm]",
                        type=float, default=9)
    parser.add_argument("-e", "--end_flat_width", help="Flat width at tail end [mm]",
                        type=float, default=40)

    ## Chamber config options ###########################################

    parser.add_argument("-w", "--wall_thickness", help="Chamber Wall Thickness [mm]",
                        type=float, default=4)
    parser.add_argument("-l", "--chamber_lift", help="Chamber Lift [mm]",
                        type=float, default=2)
    parser.add_argument("-r", "--chamber_rotate", help="Chamber Rotation/Pitch [deg]",
                        type=float, default=-0.5)

    ## Non-Numeric config options #######################################

    parser.add_argument("-t", "--tuners_type", help="Type of tuners",
                        type=str, default='worm', choices=TUNER_TYPES.keys())

    parser.add_argument("-d", "--dot_frets",
                        help="Comma-separated fret[:dots] pairs, e.g. 3,5:2,7,10,12:3",
                        type=lambda d: {
                            int(l[0]): 1 if len(l) < 2 else int(l[1])
                            for l in (fns.split(':') for fns in d.split(','))
                        },
                        default={3: 1, 5: 2, 7: 1, 10: 1, 12: 3, 15: 1, 17: 2, 19: 1, 22: 1, 24: 3})

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
                        help="Comma-separated text[:size[:font]] tuples. "\
                            + "e.g. Love:36,'Summer 2024':12:Times",
                        type=lambda x: [
                            (l[0], 10 if len(l) < 2 else int(l[1]),
                             'Arial' if len(l) < 3 else l[2])
                            for l in (tsfs.split(':') for tsfs in x.split(','))
                        ],
                        default=[
                            ('PYLELE', DEFAULT_LABEL_SIZE_BIG, DEFAULT_LABEL_FONT), 
                            ('', DEFAULT_LABEL_SIZE_SMALL, None), # for empty line
                            ('mind2form.com © 2024', DEFAULT_LABEL_SIZE_SMALL, DEFAULT_LABEL_FONT),
                        ])

    parser.add_argument("-X", "--no_model_text",
                        help="Do not add model text to label",
                        action='store_true')
    
    return parser.parse_args()


if __name__ == '__main__':
    print(parseCLI(sys.argv[1:]))
