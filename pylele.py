import pylele_parts as pll
from pathlib import Path

"""
    Main Logic
"""

def main():
    cfg = pll.LeleConfig(
        pll.SOPRANO_SCALE_LEN, 
        sepTop=True, 
        sepFretbd=True, 
        sepNeck=True, 
        sepBrdg=True, 
        sepGuide=True, 
        flatWth=50,
    )

    # gen cuts
    chmCut = pll.Chamber(cfg, isCut=True).cut(pll.Brace(cfg))
    shCut = pll.Soundhole(cfg, isCut=True)
    spCut = pll.Spines(cfg, isCut=True)
    fbCut = pll.Fretboard(cfg, isCut=True)
    pegCut = pll.Peg(cfg, isCut=True).mv(
        cfg.scaleLen + cfg.bodyBackLen - cfg.pegCfg.majRad +.5, 
        0, 
        3 + .1*cfg.flatWth*cfg.TOP_RATIO
    )
    
    # gen fretbd
    fretbd = pll.Fretboard(cfg)
    frets = pll.Frets(cfg)
    fretbd = fretbd.join(frets)
    if cfg.sepFretbd or cfg.sepNeck:
        topCut = pll.Top(cfg, isCut=True)
        fretbd = fretbd.cut(topCut)

    # gen neck
    neck = pll.Neck(cfg)
    head = pll.Head(cfg)
    neck = neck.join(head)
    neck = neck.cut(spCut)
    if cfg.sepFretbd:
        fCut = pll.Frets(cfg, isCut=True)
        neck = neck.cut(fCut).cut(fbCut)
    elif cfg.sepNeck:
        neck = neck.join(fretbd)

    # gen bridge
    brdg = pll.Bridge(cfg)

    # gen guide
    guide = pll.Guide(cfg)

    # gen body top
    top = pll.Top(cfg)
    top = top.cut(chmCut).cut(shCut).cut(pegCut)

    if not cfg.sepFretbd and not cfg.sepNeck:
        top = top.join(fretbd)

    if cfg.sepBrdg:
        brdgCut = pll.Bridge(cfg, isCut=True)
        top = top.cut(brdgCut)
    else:
        top = top.join(brdg)

    if cfg.sepGuide:
        gdCut = pll.Guide(cfg, isCut=True)
        top = top.cut(gdCut)
    else:
        top = top.join(guide)

    # gen body bottom
    body = pll.Bottom(cfg)
    body = body.cut(chmCut).cut(pegCut).cut(spCut)

    if cfg.sepFretbd:
        body = body.cut(fCut).cut(fbCut)

    if not cfg.sepTop:
        body = body.join(top)

    if not cfg.sepNeck:
        body = body.join(neck)
    
    # if running in CQ-Editor
    global FRETBD, TOP, BODY, NECK, BRIDGE, GUIDE
    
    BODY = body.show()
    body.exportSTL(str(Path.home()/"Desktop"/"body.stl"))

    if cfg.sepFretbd:
        fretbd.exportSTL(str(Path.home()/"Desktop"/"fretbd.stl"))
        FRETBD = fretbd.show()

    if cfg.sepTop:
        TOP = top.show()
        top.exportSTL(str(Path.home()/"Desktop"/"top.stl"))

    if cfg.sepNeck:
        NECK = neck.show()
        neck.exportSTL(str(Path.home()/"Desktop"/"neck.stl"))

    if cfg.sepBrdg:
        BRIDGE = brdg.show()
        brdg.exportSTL(str(Path.home()/"Desktop"/"brdg.stl"))

    if cfg.sepGuide:
        GUIDE = guide.show()
        guide.exportSTL(str(Path.home()/"Desktop"/"guide.stl"))


if __name__ == '__main__' or __name__ == '__cq_main__':
    main()
