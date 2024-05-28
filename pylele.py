import os
import sys
from pathlib import Path
from pylele_parts import *

"""
    Main Logic of Pylele, assembling the parts together
"""


def main():
    cfg = LeleConfig(
        SOPRANO_SCALE_LEN,
        action = 3,
        numStrs = 4,
        nutStrGap = 9.5,
        sepTop = True,
        sepFretbd = True,
        sepNeck = True,
        sepBrdg = False,
        flatWth = 50,
        chmTck = 3,
        chmLift = 2,
        txt1 = "元琴",
        fontSize1 = 48,
        txt1Font = "Arial Unicode MS",
        txt2 = "mind2form.com © 2024",
        fontSize2 = 9,
        txt2Font = "Arial",
        half=False,
        tnrCfg=WORM_TUNER_CFG,
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
    main()
