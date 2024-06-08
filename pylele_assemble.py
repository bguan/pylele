from pylele_parts import *

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
    fCut = Frets(cfg, isCut=True) \
        if cfg.sepFretbd or cfg.sepTop else None
    fbJntCut = FretbdJoint(cfg, isCut=True) \
        if cfg.sepFretbd or cfg.sepNeck else None
    nkJntCut = NeckJoint(cfg, isCut=True) if cfg.sepNeck else None
    tnrsCut = Tuners(cfg, isCut=True)
    strCuts = Strings(cfg, isCut=True)
    txtCut = Texts(cfg, isCut=True)

    # gen fretbd
    fbJoiners = [Frets(cfg)]
    fbCutters = [strCuts, FretboardDots(cfg, isCut=True)]
    fbFillets = {}
    if cfg.sepFretbd or cfg.sepNeck:
        fbCutters.append(Top(cfg, isCut=True))
        fbFillets[FILLET_RAD] = [(cfg.fretbdLen - 1, 0, cfg.FRETBD_TCK)]
    fretbd = Fretboard(cfg, False, fbJoiners, fbCutters, fbFillets)
    # Can't use joiners for fretbd joint, as fbCutters would remove it 
    # as joins happen before cuts
    if cfg.sepFretbd or cfg.sepNeck:
        fretbd = fretbd.join(FretbdJoint(cfg, isCut=False))\
            .join(FretboardSpines(cfg, isCut=False))

    # gen neck
    neckJoiners = [Head(cfg)]
    neckCutters = [strCuts] if spCut is None else [spCut, strCuts]
    if cfg.sepNeck: 
        neckJoiners.append(NeckJoint(cfg, isCut=False))
        if not cfg.sepFretbd:
            neckJoiners.append(fretbd)

    if cfg.sepFretbd or cfg.sepTop:
        neckCutters.extend([fCut, fbspCut])
    neck = Neck(cfg, False, neckJoiners, neckCutters)

    # gen bridge
    brdg = Bridge(cfg, cutters=[strCuts])

    # gen guide if using tuning pegs rather than worm drive
    guide = Guide(cfg) if cfg.isPeg else None

    # gen body top
    topJoiners = []
    topCutters = [chmCut, tnrsCut, Soundhole(cfg, isCut=True)]

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

    topFillets = {}
    if cfg.isWorm:
        wcfg: WormConfig = cfg.tnrCfg
        topFillets[4*cfg.STR_RAD] = [
            (xyz[0] - wcfg.slitLen, xyz[1], xyz[2] + wcfg.holeHt)
            for xyz in cfg.tnrXYZs
        ]

    top = Top(cfg, False, topJoiners, topCutters, topFillets)

    # gen body bottom
    bodyJoiners = []
    bodyCutters = [chmCut, tnrsCut, txtCut] if spCut is None else [spCut, chmCut, tnrsCut, txtCut]

    if not cfg.sepTop:
        bodyJoiners.append(top)

    if cfg.sepNeck:
        bodyCutters.append(nkJntCut)
    else:
        bodyJoiners.append(neck)

    if cfg.sepFretbd or cfg.sepTop:
        bodyCutters.append(fbspCut)

    if cfg.isWorm:
        wcfg: WormConfig = cfg.tnrCfg
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

    return parts
