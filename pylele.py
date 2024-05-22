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
        numStrs=4,
        sepTop=True,
        sepFretbd=True,
        sepNeck=False,
        sepBrdg=False,
        sepGuide=False,
        flatWth=40,
    )

    # gen cuts
    chmCut = Chamber(cfg, isCut=True).cut(Brace(cfg))
    shCut = Soundhole(cfg, isCut=True)
    spCut = Spines(cfg, isCut=True)
    fbCut = Fretboard(cfg, isCut=True)
    fCut = Frets(cfg, isCut=True)
    pegsCut = Pegs(cfg, isCut=True)

    # gen fretbd
    fretbd = Fretboard(cfg)
    frets = Frets(cfg)
    fretbd = fretbd.join(frets)
    if cfg.sepFretbd or cfg.sepNeck:
        topCut = Top(cfg, isCut=True)
        fretbd = fretbd.cut(topCut)

    # gen neck
    neck = Neck(cfg)
    head = Head(cfg)
    neck = neck.join(head)
    neck = neck.cut(spCut)
    if cfg.sepFretbd or cfg.sepTop:
        neck = neck.cut(fCut).cut(fbCut)
    elif cfg.sepNeck:
        neck = neck.join(fretbd)

    # gen bridge
    brdg = Bridge(cfg)

    # gen guide
    guide = Guide(cfg)

    # gen body top
    top = Top(cfg)
    top = top.cut(chmCut).cut(shCut).cut(pegsCut)

    if not cfg.sepFretbd and not cfg.sepNeck:
        top = top.join(fretbd)

    if cfg.sepBrdg:
        brdgCut = Bridge(cfg, isCut=True)
        top = top.cut(brdgCut)
    else:
        top = top.join(brdg)

    if cfg.sepGuide:
        gdCut = Guide(cfg, isCut=True)
        top = top.cut(gdCut)
    else:
        top = top.join(guide)

    # gen body bottom
    body = Bottom(cfg)
    body = body.cut(chmCut).cut(pegsCut).cut(spCut)

    if cfg.sepFretbd or cfg.sepTop:
        body = body.cut(fCut).cut(fbCut)

    if not cfg.sepTop:
        body = body.join(top)

    if not cfg.sepNeck:
        body = body.join(neck)

    expDir = Path.cwd()/"build"
    if not expDir.exists():
        expDir.mkdir()
    elif not expDir.is_dir():
        print("Cannot export to non directory: %s" % expDir, file=sys.stderr)
        sys.exit(os.EX_SOFTWARE)

    # if running in CQ-Editor
    global FRETBD, TOP, BODY, NECK, BRIDGE, GUIDE

    BODY = body.show()
    body.exportSTL(str(expDir/"body.stl"))

    if cfg.sepFretbd:
        fretbd.exportSTL(str(expDir/"fretbd.stl"))
        FRETBD = fretbd.show()

    if cfg.sepTop:
        TOP = top.show()
        top.exportSTL(str(expDir/"top.stl"))

    if cfg.sepNeck:
        NECK = neck.show()
        neck.exportSTL(str(expDir/"neck.stl"))

    if cfg.sepBrdg:
        BRIDGE = brdg.show()
        brdg.exportSTL(str(expDir/"brdg.stl"))

    if cfg.sepGuide:
        GUIDE = guide.show()
        guide.exportSTL(str(expDir/"guide.stl"))


if __name__ == '__main__' or __name__ == '__cq_main__':
    main()
