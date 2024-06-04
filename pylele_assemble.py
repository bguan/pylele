from pylele_parts import *

"""
    Assembling the parts together
"""


def assemble(cfg: LeleConfig) -> list[LelePart]:

    parts = []

    # gen cuts
    chmCut = Chamber(cfg, isCut=True).cut(Brace(cfg))
    spCut = Spines(cfg, isCut=True)
    fbCut = Fretboard(cfg, isCut=True) if cfg.sepFretbd or cfg.sepTop else None
    fCut = Frets(cfg, isCut=True) if cfg.sepFretbd or cfg.sepTop else None
    tnrsCut = Tuners(cfg, isCut=True)
    strCuts = Strings(cfg, isCut=True)

    # gen fretbd
    fbCutters = [strCuts, FretboardDots(cfg, isCut=True)]
    fbFillets = {}
    if cfg.sepFretbd or cfg.sepNeck:
        fbCutters.append(Top(cfg, isCut=True))
        fbFillets[FILLET_RAD] = [(cfg.fretbdLen - 1, 0, cfg.FRETBD_TCK)]
    fretbd = Fretboard(cfg, False, [Frets(cfg)], fbCutters, fbFillets)

    # gen neck
    neckJoiners = [Head(cfg)]
    neckCutters = [spCut, strCuts]
    neckFillets = {}
    if cfg.sepNeck and not cfg.sepFretbd:
        neckJoiners.append(fretbd)
    if cfg.sepFretbd or cfg.sepTop:
        neckCutters.extend([fCut, fbCut])
    neck = Neck(cfg, False, neckJoiners, neckCutters, neckFillets)

    # gen bridge
    brdg = Bridge(cfg, cutters=[strCuts])

    # gen guide if using tuning pegs rather than worm drive
    guide = Guide(cfg) if cfg.isPeg else None

    # gen body top
    topJoiners = []
    topCutters = [chmCut, tnrsCut, Soundhole(cfg, isCut=True)]

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
    bodyCutters = [chmCut, tnrsCut, spCut, Texts(cfg, isCut=True)]

    if cfg.sepFretbd or cfg.sepTop:
        bodyCutters.extend([fCut, fbCut])

    if not cfg.sepTop:
        bodyJoiners.append(top)

    if not cfg.sepNeck:
        bodyJoiners.append(neck)

    body = Bottom(cfg, False, bodyJoiners, bodyCutters, {})

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
