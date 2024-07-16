from pylele_config import FILLET_RAD, Fidelity, Implementation, LeleConfig, TunerType, WormConfig
from pylele_parts import LelePart, Body, Brace, Bridge, Chamber, \
    Fretboard, FretboardDots, FretboardSpines, Frets, FretbdJoint, \
    Guide, Head, Neck, NeckJoint, Rim, \
    Soundhole, Spines, Strings, Texts, TailEnd, Top, Tuners, WormKey

"""
    Assembling the parts together
"""
def assemble(cfg: LeleConfig) -> list[LelePart]:

    parts = []

    # gen cuts
    chmCut = Chamber(cfg, isCut=True, cutters=[Brace(cfg)])

    spCut = Spines(cfg, isCut=True).mv(0, 0, cfg.joinCutTol)\
        if cfg.numStrs > 1 else None
    fbspCut = FretboardSpines(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol) \
        if cfg.sepFretbd or cfg.sepNeck or cfg.sepTop else None
    fbCut = Fretboard(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol) if cfg.sepFretbd or cfg.sepTop else None
    f0Cut = Frets(cfg, isCut=True) \
        if cfg.sepFretbd or cfg.sepTop else None
    fbJntCut = FretbdJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, -cfg.joinCutTol) \
        if cfg.sepFretbd or cfg.sepNeck else None
    nkJntCut = NeckJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, cfg.joinCutTol) \
        if cfg.sepNeck else None
    tnrsCut = Tuners(cfg, isCut=True)
    strCuts = Strings(cfg, isCut=True)
    txtCut = Texts(cfg, isCut=True)
    tailCut = TailEnd(cfg, isCut=True) if cfg.sepEnd else None
    rimCut = Rim(cfg, isCut=True) if cfg.sepTop else None
    wormKeyCut = WormKey(cfg, isCut=True) if cfg.isWorm else None

    # gen fretbd
    fbJoiners = [Frets(cfg)]
    fbCutters = [strCuts, FretboardDots(cfg, isCut=True)]
    fbFillets = {}
    if cfg.sepFretbd or cfg.sepNeck:
        fbCutters.append(Top(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol))
        # blender mesh based edges can't handle curves
        if cfg.impl == Implementation.CAD_QUERY:
            fbFillets[FILLET_RAD] = [(cfg.fretbdLen, 0, .8*cfg.fretbdHt)]

    fretbd = Fretboard(cfg, False, fbJoiners, fbCutters, fbFillets)
    # Can't use joiners for fretbd joint & spines, as fbCutters will remove them 
    # as joins happen before cuts
    if cfg.sepFretbd or cfg.sepNeck:
        fretbd = fretbd.join(FretbdJoint(cfg, isCut=False).mv(-cfg.joinCutTol, 0, 0))\
            .join(FretboardSpines(cfg, isCut=False).mv(0, 0, cfg.joinCutTol))

    # gen neck
    neckJoiners = [Head(cfg)]
    neckCutters = []
    if cfg.sepFretbd:
        neckCutters.append(fbCut)
    neckCutters.append(spCut)
    if cfg.sepNeck: 
        neckJoiners.append(NeckJoint(cfg, isCut=False))
        if not cfg.sepFretbd:
            neckJoiners.append(fretbd)
    if cfg.sepFretbd or cfg.sepTop:
        neckCutters.extend([fbspCut, f0Cut])
    neckCutters.append(strCuts)
    neck = Neck(cfg, False, neckJoiners, neckCutters)

    # gen bridge
    brdg = Bridge(cfg, cutters=[strCuts])

    # gen guide if using tuning pegs rather than worm drive
    guide = Guide(cfg) if cfg.isPeg else None

    # gen body top
    topJoiners = []
    topCutters = [chmCut, tnrsCut, Soundhole(cfg, isCut=True)]

    if cfg.sepTop:
        topJoiners.append(Rim(cfg, isCut=False)) 

    if cfg.sepFretbd or cfg.sepNeck:
        topCutters.append(fbJntCut)
    
    if not cfg.sepFretbd and not cfg.sepNeck:
        topJoiners.append(fretbd)

    if cfg.sepBrdg:
        topCutters.append(Bridge(cfg, isCut=True))
    else:
        topJoiners.append(brdg)

    if guide != None:
        if cfg.sepBrdg:
            topCutters.append(Guide(cfg, isCut=True))
        else:
            topJoiners.append(guide)

    topFillets = { FILLET_RAD: [(cfg.sndholeX, cfg.sndholeY, cfg.fretbdHt)] }
    if cfg.isWorm:
        wcfg: WormConfig = cfg.tnrCfg
        topFillets[4*cfg.STR_RAD] = [
            (xyz[0] - wcfg.slitLen, xyz[1], xyz[2] + wcfg.holeHt)
            for xyz in cfg.tnrXYZs
        ]

    top = Top(cfg, False, topJoiners, topCutters, topFillets)

    # gen body bottom
    bodyJoiners = []
    bodyCutters = [chmCut, txtCut] 
    if spCut is not None:
        bodyCutters.append(spCut)

    if cfg.sepTop:
        bodyCutters.append(rimCut) 
    else:
        bodyJoiners.append(top)

    if cfg.sepNeck:
        bodyCutters.append(nkJntCut)
    else:
        bodyJoiners.append(neck)

    if cfg.sepFretbd or cfg.sepTop:
        bodyCutters.append(fbspCut)
    
    if tailCut is not None:
        bodyCutters.append(tailCut)
    else:
        bodyCutters.append(tnrsCut)
        if cfg.isWorm:
            bodyCutters.append(wormKeyCut)

    body = Body(cfg, False, bodyJoiners, bodyCutters, {})

    parts.append(body)
    if cfg.sepFretbd:
        parts.append(fretbd)

    if cfg.sepTop:
        parts.append(top)

    if cfg.sepNeck:
        parts.append(neck)

    if cfg.sepBrdg:
        parts.append(brdg)

    if guide != None and cfg.sepBrdg:
        parts.append(guide)

    if cfg.sepEnd:
        tailCutters = [tnrsCut, chmCut, spCut]
        if cfg.sepTop:
            tailCutters.append(rimCut) 
        if cfg.isWorm:
            tailCutters.append(wormKeyCut)
        tail = TailEnd(cfg, isCut=False, joiners=[], cutters=tailCutters)
        parts.append(tail)

    if cfg.isWorm:
        parts.append(WormKey(cfg, isCut=False))

    return parts

def test(cfg: LeleConfig):

    strCuts = Strings(cfg, isCut=True).mv(0, 0, cfg.joinCutTol)

    frets = Frets(cfg)
    fbsp = FretboardSpines(cfg, isCut=False)
    fbJnt = FretbdJoint(cfg, isCut=False)
    topCut = Top(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
    fdotsCut = FretboardDots(cfg, isCut=True)
    fretbd = Fretboard(
        cfg, 
        False, 
        [frets, fbsp], 
        [topCut, fdotsCut, strCuts],
    ).join(fbJnt)
    fretbd.exportSTL(f"build/{fretbd.fileNameBase}.stl")

    head = Head(cfg)
    fbCut = Fretboard(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
    spCut = Spines(cfg, isCut=True) #.mv(0, 0, cfg.joinCutTol)
    fbspCut = FretboardSpines(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
    f0Cut = Frets(cfg, isCut=True)
    nkJnt = NeckJoint(cfg, isCut=False)

    neck = Neck(cfg, False, [head, nkJnt], [spCut, fbCut, f0Cut, strCuts, fbspCut])
    neck.exportSTL(f"build/{neck.fileNameBase}.stl")

    brdg = Bridge(cfg, isCut=False, cutters=[strCuts])
    guide = Guide(cfg, isCut=False)
    rim = Rim(cfg, isCut=False)
    rimCut = Rim(cfg, isCut=True)
    chmCut = Chamber(cfg, isCut=True, cutters=[Brace(cfg)])
    tnrsCut = Tuners(cfg, isCut=True)
    fbJntCut = FretbdJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, -cfg.joinCutTol)
    shCut = Soundhole(cfg, isCut=True)
    top = Top(cfg, joiners=[rim, guide, brdg], cutters=[spCut, tnrsCut, shCut, fbJntCut, chmCut]) 
    top.exportSTL(f"build/{top.fileNameBase}.stl")

    wkCut = WormKey(cfg, isCut=True)
    wkey = WormKey(cfg, isCut=False)
    wkey.exportSTL(f"build/{wkey.fileNameBase}.stl")

    txtCut = Texts(cfg, isCut=True)
    nkJntCut = NeckJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, cfg.joinCutTol)
    body = Body(cfg, cutters=[topCut, nkJntCut, spCut, tnrsCut, txtCut, chmCut, rimCut, wkCut])
    body.exportSTL(f"build/{body.fileNameBase}.stl")


if __name__ == "__main__":
    cfg = LeleConfig(
        impl=Implementation.BLENDER, 
        fidelity=Fidelity.LOW, 
        tnrType=TunerType.WORM_TUNER,
        endWth=48, # or try 56 for HIGH, 48 for MEDIUM & LOW
    )
    test(cfg)