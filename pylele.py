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
        modelLbl=cli.model_label,
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
    for p in parts:
        if cfg.half:
            p = p.half()
        p.exportSTL(str(expDir/"{p.fileNameBase}.stl"))

if __name__ == '__main__':
    pylele_main()
elif __name__ == '__cq_main__':
    cfg = LeleConfig(sepTop=True, sepFretbd=True, tnrCfg=WORM_TUNER_CFG)
    strs = Strings(cfg, isCut=False)
    tnrs = Tuners(cfg, isCut=False)
    if cfg.half:
        strs = strs.half()
        tnrs = tnrs.half()
    parts = assemble(cfg)
    parts.extend([strs, tnrs])
    for p in parts:
        if cfg.half:
            p = p.half()
        show_object(p.show(), name=p.fileNameBase, options={'color':p.color}) # type: ignore
