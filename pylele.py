#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from pylele_parts import *
from pylele_assemble import *
from pylele_cli import parseCLI, TUNER_TYPES

"""
    Main Logic of Pylele
"""

def pylele_main():

    # parse inputs
    cli = parseCLI()

    # generate configurations
    cfg = LeleConfig(
        scaleLen=cli.scale_len,
        action=cli.action,
        numStrs=cli.nstrings,
        nutStrGap=cli.nut_string_gap,
        sepTop=cli.separate_top,
        sepFretbd=cli.separate_fretboard,
        sepNeck=cli.separate_neck,
        sepBrdg=cli.separate_bridge,
        sepEnd=cli.separate_end,
        endWth=cli.end_flat_width,
        wallTck=cli.wall_thickness,
        chmLift=cli.chamber_lift,
        chmRot=cli.chamber_rotate,
        fret2Dots=cli.dot_frets,
        txtSzFonts=cli.texts_size_font,
        noModelTxt=cli.no_model_text,
        half=cli.half,
        tnrCfg=TUNER_TYPES[cli.tuners_type]
    )

    parts = assemble(cfg)

    expDir = Path.cwd()/"build"
    if not expDir.exists():
        expDir.mkdir()
    elif not expDir.is_dir():
        print("Cannot export to non directory: %s" % expDir, file=sys.stderr)
        sys.exit(os.EX_SOFTWARE)

    # if running in CQ-Editor
    global FRETBD, TOP, BODY, NECK, BRIDGE, GUIDE, STRINGS, TUNERS
    strs = Strings(cfg, isCut=False)
    tnrs = Tuners(cfg, isCut=False)

    if cfg.half:
        strs = strs.half()
        tnrs = tnrs.half()

    STRINGS = strs.show()
    TUNERS = tnrs.show()

    for p in parts:
        if cfg.half:
            p = p.half()
        if isinstance(p, Bottom):
            BODY = p.show()
            p.exportSTL(str(expDir/"body.stl"))
        elif isinstance(p, Top):
            TOP = p.show()
            p.exportSTL(str(expDir/"top.stl"))
        elif isinstance(p, Fretboard):
            FRETBD = p.show()
            p.exportSTL(str(expDir/"fretbd.stl"))
        elif isinstance(p, Neck):
            NECK = p.show()
            p.exportSTL(str(expDir/"neck.stl"))
        elif isinstance(p, Bridge):
            BRIDGE = p.show()
            p.exportSTL(str(expDir/"brdg.stl"))
        elif isinstance(p, Guide):
            GUIDE = p.show()
            p.exportSTL(str(expDir/"guide.stl"))

if __name__ == '__main__' or __name__ == '__cq_main__':
    pylele_main()