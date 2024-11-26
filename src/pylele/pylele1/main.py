#!/usr/bin/env python3

import datetime
import os
from pathlib import Path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.pylele1.parts import WormKey, export_best_multiparts
from pylele.pylele1.config import LeleConfig, TunerType
from pylele.pylele1.cli import parseCLI
from pylele.pylele1.assemble import assemble

"""
    Main Logic of Pylele
"""


def pylele_main():

    # parse inputs
    cli = parseCLI()

    # generate configurations
    cfg = LeleConfig(
        scaleLen=cli.scale_length,
        action=cli.action,
        numStrs=cli.num_strings,
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
        noTxt=cli.no_text,
        txtSzFonts=cli.texts_size_font,
        modelLbl=cli.model_label,
        split=cli.split,
        tnrType=TunerType[cli.tuner_type],
        fidelity=cli.fidelity,
        impl=cli.implementation,
    )

    expDir = Path(cli.outdir)
    if not expDir.exists():
        expDir.mkdir()
    elif not expDir.is_dir():
        print(
            "Cannot export to non directory: %s" % expDir,
            file=sys.stderr,
        )
        sys.exit(os.EX_SOFTWARE)

    expDir = expDir / (
        datetime.datetime.now().strftime("%y%m%d-%H%M-") + cfg.genModelStr()
    )
    if not expDir.exists():
        expDir.mkdir()

    with open(expDir / "config.txt", "w") as f:
        f.write(repr(cfg))

    parts = assemble(cfg)

    for p in parts:
        if cfg.split and not isinstance(p, WormKey):
            p = p.half()
        p.export_stl(str(expDir / f"{p.name}"))

    model = cfg.genModelStr(inclDate=True)
    export_best_multiparts(parts, model, expDir / f"{model}")


if __name__ == "__main__":
    pylele_main()
