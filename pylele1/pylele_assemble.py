#!/usr/bin/env python3


import os
import sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from pylele1.pylele_config import FILLET_RAD, Fidelity, Implementation, LeleConfig, TunerType, WormConfig
from pylele1.pylele_parts import LelePart, Body, Brace, Bridge, Chamber, \
    Fretboard, FretboardDots, FretboardSpines, Frets, FretbdJoint, \
    Guide, Head, Neck, NeckJoint, Rim, \
    Soundhole, Spines, Strings, Texts, TailEnd, Top, Tuners, WormKey
from api.pylele_api_constants import DEFAULT_TEST_DIR

"""
    Assembling the parts together
"""
def assemble(cfg: LeleConfig) -> list[LelePart]:

    parts = []

    # gen fretbd
    strCuts = Strings(cfg, isCut=True) # use by others too
    topCut = Top(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol) if cfg.sepFretbd or cfg.sepNeck else None
    frets = Frets(cfg)
    fdotsCut = FretboardDots(cfg, isCut=True)
    fbJoiners = [frets]
    fbCutters = [fdotsCut, strCuts]
    fbFillets = {}
    if cfg.sepFretbd or cfg.sepNeck:
        fbCutters.insert(0, topCut)
        fbFillets[FILLET_RAD] = [(cfg.fretbdLen, 0, .5*cfg.fretbdHt)]
    fretbd = Fretboard(cfg, False, fbJoiners, fbCutters, fbFillets)

    # Can't use joiners for fretbd joint & spines, as fbCutters will remove them
    # as joins happen before cuts
    if cfg.sepFretbd or cfg.sepNeck:
        fretbd = fretbd \
            .join(FretboardSpines(cfg, isCut=False)) \
            .join(FretbdJoint(cfg, isCut=False))

    # gen neck
    neckJoiners = [Head(cfg).mv(cfg.joinCutTol, 0, 0)]
    neckCutters = [strCuts]

    if cfg.numStrs > 1:
        spCut = Spines(cfg, isCut=True)
        neckCutters.append(spCut)

    if cfg.sepFretbd:
        fbCut = Fretboard(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
        neckCutters.append(fbCut)

    if cfg.sepNeck:
        neckJoiners.append(NeckJoint(cfg, isCut=False).mv(-cfg.joinCutTol, 0, 0))

    if cfg.sepNeck and not cfg.sepFretbd:
        neckJoiners.append(fretbd)

    if cfg.sepFretbd or cfg.sepTop:
        fbspCut = FretboardSpines(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
        f0Cut = Frets(cfg, isCut=True)
        neckCutters.extend([fbspCut, f0Cut])

    # neckCutters.append(strCuts)
    neck = Neck(cfg, False, neckJoiners, neckCutters)

    # gen bridge
    brdg = Bridge(cfg, cutters=[strCuts])

    # gen guide if using tuning pegs rather than worm drive
    guide = Guide(cfg) if cfg.tnrCfg.is_peg() else None

    # gen body top
    chmCut = Chamber(cfg, isCut=True, cutters=[Brace(cfg)])
    tnrsCut = Tuners(cfg, isCut=True)
    wormKeyCut = None if not cfg.tnrCfg.is_worm() else WormKey(cfg, isCut=True)
    topJoiners = []
    topCutters = [chmCut, tnrsCut, Soundhole(cfg, isCut=True)]

    if cfg.sepTop:
        topJoiners.append(Rim(cfg, isCut=False))

    if cfg.sepFretbd or cfg.sepNeck:
        fbJntCut = FretbdJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, -cfg.joinCutTol)
        topCutters.append(fbJntCut)

    if not cfg.sepFretbd and not cfg.sepNeck:
        topJoiners.append(fretbd)

    if cfg.sepBrdg:
        topCutters.append(Bridge(cfg, isCut=True))
    else:
        topJoiners.append(brdg)

    if not guide is None:
        if cfg.sepBrdg:
            topCutters.append(Guide(cfg, isCut=True))
        else:
            topJoiners.append(guide)

    topFillets = { FILLET_RAD: [(cfg.sndholeX, cfg.sndholeY, cfg.fretbdHt)] }
    if cfg.tnrCfg.is_worm() and cfg.impl == Implementation.CAD_QUERY:
        wcfg: WormConfig = cfg.tnrCfg
        topFillets[wcfg.slitWth] = [
            (xyz[0] - wcfg.slitLen, xyz[1], xyz[2] + wcfg.holeHt)
            for xyz in cfg.tnrXYZs
        ]

    top = Top(cfg, False, topJoiners, topCutters, topFillets)

    # gen body bottom
    txtCut = Texts(cfg, isCut=True)
    tailCut = TailEnd(cfg, isCut=True) if cfg.sepEnd else None

    bodyJoiners = []
    bodyCutters = [chmCut]

    if txtCut is not None:
        bodyCutters.append(txtCut)

    if not spCut is None:
        bodyCutters.append(spCut)

    if cfg.sepTop:
        rimCut = Rim(cfg, isCut=True)
        bodyCutters.append(rimCut)
    else:
        bodyJoiners.append(top.mv(0, 0, -0.01)) # HACK: cadquery would fail text cut without the mv

    if cfg.sepNeck:
        nkJntCut = NeckJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, cfg.joinCutTol)
        bodyCutters.append(nkJntCut)
    else:
        bodyJoiners.append(neck.mv(cfg.joinCutTol, 0,0))

    if cfg.sepFretbd or cfg.sepTop:
        bodyCutters.append(fbspCut)

    if cfg.sepEnd:
        tailCut = TailEnd(cfg, isCut=True)
        bodyCutters.append(tailCut)
    else:
        bodyCutters.append(tnrsCut)
        if cfg.tnrCfg.is_worm():
            bodyCutters.append(wormKeyCut)

    body = Body(cfg, False, bodyJoiners, bodyCutters)
    parts.append(body)

    if cfg.sepFretbd:
        parts.append(fretbd)

    if cfg.sepTop:
        parts.append(top)

    if cfg.sepNeck:
        parts.append(neck)

    if cfg.sepBrdg:
        parts.append(brdg)

    if not guide is None and cfg.sepBrdg:
        parts.append(guide)

    if cfg.sepEnd:
        tailCutters = [tnrsCut, chmCut, spCut]
        if cfg.sepTop:
            tailCutters.append(rimCut)
        if cfg.tnrCfg.is_worm():
            tailCutters.append(wormKeyCut)
        tail = TailEnd(cfg, isCut=False, joiners=[], cutters=tailCutters)
        parts.append(tail)

    if cfg.tnrCfg.is_worm():
        parts.append(WormKey(cfg, isCut=False))

    return parts

def test(cfg: LeleConfig):

    expDir = Path.cwd()/DEFAULT_TEST_DIR
    if not expDir.exists():
        expDir.mkdir()
    elif not expDir.is_dir():
        print("Cannot export to non directory: %s" % expDir, file=sys.stderr)
        sys.exit(os.EX_SOFTWARE)
    implCode = cfg.impl.code()
    fidelCode = cfg.fidelity.code()

    with open(expDir / f"{implCode}{fidelCode}-config.txt", 'w') as f:
        f.write(repr(cfg))

    strCuts = Strings(cfg, isCut=True).mv(0, 0, cfg.joinCutTol)

    frets = Frets(cfg)
    fbsp = FretboardSpines(cfg, isCut=False).mv(0, 0, cfg.joinCutTol)
    fbJnt = FretbdJoint(cfg, isCut=False)
    topCut = Top(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
    fdotsCut = FretboardDots(cfg, isCut=True)
    fretbd = Fretboard(
        cfg,
        False,
        [frets, fbsp],
        [topCut, fdotsCut, strCuts],
    ).join(fbJnt)
    fretbd.exportSTL(os.path.join(DEFAULT_TEST_DIR,f"{fretbd.fileNameBase}"))

    head = Head(cfg)
    fbCut = Fretboard(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
    spCut = Spines(cfg, isCut=True)
    fbspCut = FretboardSpines(cfg, isCut=True).mv(0, 0, -cfg.joinCutTol)
    f0Cut = Frets(cfg, isCut=True)
    nkJnt = NeckJoint(cfg, isCut=False)

    neck = Neck(cfg, False, [head, nkJnt], [spCut, fbCut, f0Cut, strCuts, fbspCut])
    neck.exportSTL(os.path.join(DEFAULT_TEST_DIR,f"{neck.fileNameBase}"))

    brdg = Bridge(cfg, isCut=False, cutters=[strCuts])
    rim = Rim(cfg, isCut=False)
    chmCut = Chamber(cfg, isCut=True, cutters=[Brace(cfg)])
    tnrsCut = Tuners(cfg, isCut=True)
    fbJntCut = FretbdJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, -cfg.joinCutTol)
    shCut = Soundhole(cfg, isCut=True)
    topFillets = {}
    if cfg.tnrCfg.is_worm() and cfg.impl == Implementation.CAD_QUERY:
        wcfg: WormConfig = cfg.tnrCfg
        topFillets[wcfg.slitWth] = [
            (wx - wcfg.slitLen/2, wy, cfg.brdgZ) for wx, wy, _ in cfg.tnrXYZs
        ]

    topJoins = [brdg, rim]
    if cfg.tnrCfg.is_peg():
        topJoins.append(Guide(cfg, False))
    top = Top(cfg,
        joiners=topJoins,
        cutters=[fbJntCut, tnrsCut, shCut, chmCut],
        fillets=topFillets,
    )
    top.exportSTL(os.path.join(DEFAULT_TEST_DIR,f"{top.fileNameBase}"))

    rimCut = Rim(cfg, isCut=True)
    txtCut = Texts(cfg, isCut=True)
    txtCut.exportSTL(os.path.join(DEFAULT_TEST_DIR,f"{txtCut.fileNameBase}"))

    nkJntCut = NeckJoint(cfg, isCut=True).mv(-cfg.joinCutTol, 0, cfg.joinCutTol)
    bodyCuts = [topCut, nkJntCut, spCut, tnrsCut, chmCut, rimCut, txtCut]
    if cfg.tnrCfg.is_worm():
        wkCut = WormKey(cfg, isCut=True)
        bodyCuts.append(wkCut)
        wkey = WormKey(cfg, isCut=False)
        wkey.exportSTL(os.path.join(DEFAULT_TEST_DIR,f"{wkey.fileNameBase}"))

    body = Body(cfg, cutters=bodyCuts)
    body.exportSTL(os.path.join(DEFAULT_TEST_DIR,f"{body.fileNameBase}"))


if __name__ == "__main__":
    cfg = LeleConfig(
        impl=Implementation.TRIMESH,
        fidelity=Fidelity.LOW,
        sepFretbd=True,
        sepNeck=True,
        sepTop=True,
    )
    test(cfg)