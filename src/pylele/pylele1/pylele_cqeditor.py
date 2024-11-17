#!/usr/bin/env python3

import os
from pathlib import Path
from random import randint
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.constants import FILLET_RAD
from api.utils import make_or_exist_path
from pylele1.pylele_parts import Strings, Tuners, Spines, WormKey
from pylele1.pylele_config import Implementation, LeleConfig, TunerType, ModelLabel
from pylele1.pylele_assemble import assemble

"""
    Main Logic of Pylele when launched from CQEditor
"""


def cqeditor_main():
    cfg = LeleConfig(
        split=False,
        scaleLen=330,
        endWth=90,
        chmLift=1,
        impl=Implementation.CADQUERY,
        tnrType=TunerType.WORM,
        modelLbl=ModelLabel.LONG,
        sepEnd=True,
        sepTop=True,
        sepNeck=True,
        sepFretbd=True,
        sepBrdg=True,
    )
    strs = Strings(cfg, isCut=False)
    tnrs = Tuners(cfg, isCut=False)
    tnrs.fillet([], FILLET_RAD)
    sps = None if cfg.numStrs < 2 else Spines(cfg, isCut=False)
    parts = assemble(cfg)
    parts.extend([strs, tnrs])
    if not sps is None:
        parts.append(sps)
    for p in parts:
        if cfg.split and not isinstance(p, WormKey):
            p = p.half()
        color = (
            (randint(0, 255), randint(0, 255), randint(0, 255))
            if p.color is None
            else p.color.value
        )

        if 'show_object' in globals():
            # show_object() is dynamically injected by CQ-Editor
            show_object(  # type: ignore
                p.show(),
                name=p.name,
                options={"color": color},
            )
        else:
            out_path = Path("build")
            make_or_exist_path(out_path)
            p.export_stl(str(out_path / f"{p.name}"))


if __name__ in ["__main__", "__cq_main__"]:
    cqeditor_main()
