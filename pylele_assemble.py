from pylele_config import FILLET_RAD, LeleConfig, WormConfig
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

    spCut = Spines(cfg, isCut=True) if cfg.numStrs > 1 else None
    fbspCut = FretboardSpines(cfg, isCut=True) \
        if cfg.sepFretbd or cfg.sepNeck or cfg.sepTop else None
    fbCut = Fretboard(cfg, isCut=True) if cfg.sepFretbd or cfg.sepTop else None
    fCut = Frets(cfg, isCut=True) \
        if cfg.sepFretbd or cfg.sepTop else None
    fbJntCut = FretbdJoint(cfg, isCut=True) \
        if cfg.sepFretbd or cfg.sepNeck else None
    nkJntCut = NeckJoint(cfg, isCut=True) if cfg.sepNeck else None
    tnrsCut = Tuners(cfg, isCut=True)
    strCuts = Strings(cfg, isCut=True)
    txtCut = Texts(cfg, isCut=True)
    tailCut = TailEnd(cfg, isCut=True) if cfg.sepEnd else None
    rimCut = Rim(cfg, isCut=True) if cfg.sepTop else None

    # gen fretbd
    fbJoiners = [Frets(cfg)]
    fbCutters = [strCuts, FretboardDots(cfg, isCut=True)]
    fbFillets = {} #cfg.FRETBD_TCK: [(cfg.fretbdLen, 0, cfg.fretbdHt)]}
    if cfg.sepFretbd or cfg.sepNeck:
        fbCutters.append(Top(cfg, isCut=True).mv(0, 0,-cfg.joinCutTol))
        fbFillets[FILLET_RAD] = [(cfg.fretbdLen, 0, cfg.FRETBD_TCK)]
    fretbd = Fretboard(cfg, False, fbJoiners, fbCutters, fbFillets)
    # Can't use joiners for fretbd joint & spines, as fbCutters will remove them 
    # as joins happen before cuts
    if cfg.sepFretbd or cfg.sepNeck:
        fretbd = fretbd.join(FretbdJoint(cfg, isCut=False).mv(-cfg.joinCutTol, 0, 0))\
            .join(FretboardSpines(cfg, isCut=False).mv(0, 0, cfg.joinCutTol))

    # gen neck
    neckJoiners = [Head(cfg).mv(cfg.joinCutTol, 0, 0)]
    neckCutters = [strCuts] if spCut is None else [spCut.mv(0, 0, -cfg.joinCutTol), strCuts]
    if cfg.sepNeck: 
        neckJoiners.append(NeckJoint(cfg, isCut=False))
        if not cfg.sepFretbd:
            neckJoiners.append(fretbd)

    if cfg.sepFretbd or cfg.sepTop:
        neckCutters.extend([
            fCut.mv(cfg.joinCutTol, 0, -cfg.joinCutTol),
            fbCut.mv(cfg.joinCutTol, 0, -cfg.joinCutTol),
            fbspCut.mv(cfg.joinCutTol, 0, -cfg.joinCutTol),
        ])
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
        topCutters.append(fbJntCut.mv(-cfg.joinCutTol, 0, 0))
    
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
        bodyCutters.append(nkJntCut.mv(-cfg.joinCutTol, 0, 0))
    else:
        bodyJoiners.append(neck)

    if cfg.sepFretbd or cfg.sepTop:
        bodyCutters.append(fbspCut)
    
    if tailCut is not None:
        bodyCutters.append(tailCut)
    else:
        bodyCutters.append(tnrsCut)
        if cfg.isWorm:
            bodyCutters.append(WormKey(cfg, isCut=True))

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
            tailCutters.append(WormKey(cfg, isCut=True))
        tail = TailEnd(cfg, isCut=False, joiners=[], cutters=tailCutters)
        parts.append(tail)

    if cfg.isWorm:
        parts.append(WormKey(cfg, isCut=True))

    return parts

def test(cfg: LeleConfig) -> list[LelePart]:
    parts = []

    frets = Frets(cfg)
    fretbd = Fretboard(cfg, False, [frets])
    parts.append(fretbd)

    head = Head(cfg).mv(cfg.joinCutTol, 0, 0)
    neck = Neck(cfg, False, [head])
    parts.append(neck)

    brdg = Bridge(cfg)
    chm = Chamber(cfg)
    top = Top(cfg, joiners=[brdg], cutters=[chm])
    parts.append(top)

    body = Body(cfg, cutters=[chm])
    parts.append(body)

    return parts