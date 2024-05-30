#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from pylele_parts import *
from pylele_cli import pylele_cli, TUNER_TYPES

"""
    Main Logic of Pylele, assembling the parts together
"""


def pylele_main():

    # parse inputs
    cli = pylele_cli()
    print(cli)

    # generate configurations
    cfg = LeleConfig(
        scaleLen = cli.scale_len, # SOPRANO_SCALE_LEN,
        action = cli.action,
        numStrs = cli.nstrings,
        nutStrGap = cli.nut_string_gap,
        sepTop = cli.separate_top,
        sepFretbd = cli.separate_fretboard,
        sepNeck = cli.separate_neck,
        sepBrdg = cli.separate_bridge,
        flatWth = cli.flat_width,
        chmTck = cli.chamber_thickness,
        chmLift = cli.chamber_lift,
        txt1 = cli.text1, # "元琴",
        fontSize1 = cli.text1_size, # 48,
        txt1Font = cli.text1_font, # "Arial Unicode MS",
        txt2 = cli.text2, # "mind2form.com © 2024",
        fontSize2 = cli.text2_size, # 9,
        txt2Font = cli.text2_font, # "Arial",
        half=cli.half,
        tnrCfg=TUNER_TYPES[cli.tuners_type] # WORM_TUNER_CFG,
    )

    # gen cuts
    chmCut = Chamber(cfg, isCut=True).cut(Brace(cfg))
    shCut = Soundhole(cfg, isCut=True)
    spCut = Spines(cfg, isCut=True)
    fbCut = Fretboard(cfg, isCut=True)
    fCut = Frets(cfg, isCut=True)
    tnrsCut = Tuners(cfg, isCut=True)
    strCuts = Strings(cfg, isCut=True)
    txtsCut = Texts(cfg, isCut=True)
    fbDotsCut = FretboardDots(cfg, isCut=True)

    # gen fretbd
    fretbd = Fretboard(cfg)
    frets = Frets(cfg)
    fretbd = fretbd.join(frets).cut(strCuts).cut(fbDotsCut)

    if cfg.sepFretbd or cfg.sepNeck:
        topCut = Top(cfg, isCut=True)
        fretbd = fretbd.cut(topCut).filletByNearestEdges(
            [(cfg.fretbdLen - 1, 0, cfg.FRETBD_TCK)], 
            FILLET_RAD,
        )

    # gen neck
    neck = Neck(cfg)
    head = Head(cfg)
    neck = neck.join(head)
    neck = neck.cut(spCut).cut(strCuts)
    if cfg.sepFretbd or cfg.sepTop:
        neck = neck.cut(fCut).cut(fbCut)
    elif cfg.sepNeck:
        neck = neck.join(fretbd)

    # gen bridge
    brdg = Bridge(cfg).cut(strCuts)

    # gen guide if using tuning pegs rather than worm drive
    guide = Guide(cfg) if isinstance(cfg.tnrCfg, PegConfig) else None

    # gen body top
    top = Top(cfg)

    if not cfg.sepFretbd:
        if cfg.sepNeck:
            neck = neck.join(fretbd)
        else:
            top = top.join(fretbd)

    if cfg.sepBrdg:
        brdgCut = Bridge(cfg, isCut=True)
        top = top.cut(brdgCut)
    else:
        top = top.join(brdg)

    if guide != None:
        if cfg.sepBrdg:
            gdCut = Guide(cfg, isCut=True)
            top = top.cut(gdCut)
        else:
            top = top.join(guide)

    top = top.cut(chmCut).cut(shCut).cut(tnrsCut)
    if cfg.isWorm:
        wcfg: WormConfig = cfg.tnrCfg
        top = top.filletByNearestEdges(
            [
                (xyz[0] -wcfg.slitLen, xyz[1], xyz[2] +wcfg.holeHt) 
                    for xyz in cfg.tnrXYZs
            ], 
            2*cfg.STR_RAD,
        )

    # gen body bottom
    body = Bottom(cfg)
    body = body.cut(chmCut).cut(tnrsCut).cut(spCut).cut(txtsCut)

    if cfg.sepFretbd or cfg.sepTop:
        body = body.cut(fCut).cut(fbCut)

    if not cfg.sepTop:
        body = body.join(top)

    if not cfg.sepNeck:
        body = body.join(neck)

    if cfg.split:
        body = body.half()

    expDir = Path.cwd()/"build"
    if not expDir.exists():
        expDir.mkdir()
    elif not expDir.is_dir():
        print("Cannot export to non directory: %s" % expDir, file=sys.stderr)
        sys.exit(os.EX_SOFTWARE)

    # if running in CQ-Editor
    global FRETBD, TOP, BODY, NECK, BRIDGE, GUIDE, STRINGS, TUNERS

    tnrs = Tuners(cfg, isCut=False)
    
    if cfg.split:
        strCuts = strCuts.half()
        tnrs = tnrs.half()
        
    STRINGS = strCuts.show()
    TUNERS = tnrs.show()

    BODY = body.show()
    body.exportSTL(str(expDir/"body.stl"))

    if cfg.sepFretbd:
        if cfg.split:
            fretbd = fretbd.half()
        fretbd.exportSTL(str(expDir/"fretbd.stl"))
        FRETBD = fretbd.show()

    if cfg.sepTop:
        if cfg.split:
            top = top.half()
        TOP = top.show()
        top.exportSTL(str(expDir/"top.stl"))

    if cfg.sepNeck:
        if cfg.split:
            neck = neck.half()
        NECK = neck.show()
        neck.exportSTL(str(expDir/"neck.stl"))

    if cfg.sepBrdg:
        if cfg.split:
            brdg = brdg.half()
        BRIDGE = brdg.show()
        brdg.exportSTL(str(expDir/"brdg.stl"))

    if guide != None and cfg.sepBrdg:
        if cfg.split:
            guide = guide.half()
        GUIDE = guide.show()
        guide.exportSTL(str(expDir/"guide.stl"))


if __name__ == '__main__' or __name__ == '__cq_main__':
    pylele_main()

