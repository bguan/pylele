#!/usr/bin/env python3

import argparse
import sys
from pylele_config import SOPRANO_SCALE_LEN, FRICTION_PEG_CFG, WORM_TUNER_CFG

TUNER_TYPES = {
    'friction': FRICTION_PEG_CFG,
    'worm': WORM_TUNER_CFG,
}

def pylele_cli():  # pylint: disable=W0102
    """
    Pylele Command Line Interface
    """
    parser = argparse.ArgumentParser(description='Pylele Configuration')
    
    ## Numeric config options ###########################################
    parser.add_argument("-scale", "--scale_len", help="Scale Length [mm]",
                        type=int, default=SOPRANO_SCALE_LEN)
    parser.add_argument("-nstrings", "--nstrings", help="Number of strings",
                        type=int, default=4)
    parser.add_argument("-action", "--action", help="Strings action [mm]",
                        type=float, default=2)
    parser.add_argument("-nut_str_gap", "--nut_string_gap", help="Nut to String gap [mm]",
                        type=float, default=9.5)
    parser.add_argument("-flat_width", "--flat_width", help="Flat width [mm]",
                        type=float, default=50)
    parser.add_argument("-dot_rad", "--dot_radius", help="Fretboard dots radius [mm]",
                        type=float, default=1.5)

    ## Chamber config options ###########################################

    parser.add_argument("-chm_tck", "--chamber_thickness", help="Chamber Thickness [mm]",
                        type=float, default=4)
    parser.add_argument("-chm_lift", "--chamber_lift", help="Chamber Lift [mm]",
                        type=float, default=2)
    parser.add_argument("-chm_tilt", "--chamber_tilt", help="Chamber Tilt [deg]",
                        type=float, default=-0.53)

    ## Non-Numeric config options #######################################

    parser.add_argument("-tuners", "--tuners_type", help="Type of tuners",
                        type=str, default='worm', choices=TUNER_TYPES.keys())

    """
    parser.add_argument("-dot_frets", "--dot_frets", help="Dotted frets",
                        type=dict[int, int],
                        default={ 3:1, 5:2, 7:1, 10:1, 12:3, 15:1, 17:2, 19:1, 22:1, 24:3 }
                        )
    """
    ## Cut options ######################################################

    parser.add_argument("-sep_top", "--separate_top",
                        help="Split body top from body back.",
                        action='store_true')
    parser.add_argument("-sep_neck", "--separate_neck",
                        help="Split neck from body.",
                        action='store_true')
    parser.add_argument("-sep_fretbd", "--separate_fretboard",
                        help="Split fretboard from neck back.",
                        action='store_true')
    parser.add_argument("-sep_brdg", "--separate_bridge",
                        help="Split bridge from body.",
                        action='store_true')
    parser.add_argument("-half", "--half",
                        help="Half Split",
                        action='store_true')
    
    ## text options ######################################################

    parser.add_argument("-txt1", "--text1", help="Text #1",
                        type=str, default='PYLELE')
    parser.add_argument("-txt1_font", "--text1_font", help="Text #1 font",
                        type=str, default='Arial')
    parser.add_argument("-txt1_size", "--text1_size", help="Text #1 font size",
                        type=float, default=20)

    parser.add_argument("-txt2", "--text2", help="Text #2",
                        type=str, default='mind2form.com © 2024')
    parser.add_argument("-txt2_font", "--text2_font", help="Text #2 font",
                        type=str, default='Arial')
    parser.add_argument("-txt2_size", "--text2_size", help="Text #2 font size",
                        type=float, default=10)

    return parser.parse_args()
                     
if __name__ == '__main__':
    print(pylele_cli(sys.argv[1:]))
