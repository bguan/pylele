#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api_constants import FILLET_RAD
from pylele1.pylele_config import LeleConfig, WormConfig
from pylele1.pylele_parts import (
    LelePart,
    Body,
    Brace,
    Bridge,
    Chamber,
    Fretboard,
    FretboardDots,
    FretboardSpines,
    Frets,
    FretbdJoint,
    Guide,
    Head,
    Neck,
    NeckJoint,
    Rim,
    Soundhole,
    Spines,
    Strings,
    Texts,
    TailEnd,
    Top,
    Tuners,
    WormKey,
)

"""
    Assembling the parts together
"""


def assemble(cfg: LeleConfig) -> list[LelePart]:

    jctol = cfg.joinCutTol
    parts = []

    # reusable cutters
    strCuts = Strings(cfg, isCut=True)
    spCut = None if cfg.numStrs <= 1 else Spines(cfg, isCut=True)
    chmCut = Chamber(cfg, isCut=True).cut(Brace(cfg))
    tnrsCut = Tuners(cfg, isCut=True)
    rimCut = Rim(cfg, isCut=True)
    fbspCut = (
        FretboardSpines(cfg, isCut=True)
        if cfg.sepFretbd or cfg.sepNeck or cfg.sepTop
        else None
    )

    # gen fretbd
    frets = Frets(cfg).cut(strCuts)
    fretbd = Fretboard(cfg).join(frets).cut(FretboardDots(cfg, isCut=True))
    if cfg.sepFretbd or cfg.sepNeck:
        fretbd = fretbd.cut(Top(cfg, isCut=True).mv(0, 0, -jctol))
    if cfg.sepFretbd or cfg.sepNeck:
        fretbd = fretbd.join(FretbdJoint(cfg, isCut=False))
    if cfg.sepFretbd or cfg.sepTop:
        fretbd = fretbd.join(FretboardSpines(cfg, isCut=False))

    # gen head
    f0cut = Frets(cfg, isCut=True, upToFret=0)
    head = Head(cfg).cut(strCuts).cut(f0cut)
    if spCut is not None:
        head = head.cut(spCut)

    # gen neck
    neck = Neck(cfg).join(head.mv(jctol, 0, 0))

    if cfg.sepNeck:
        neck = neck.join(NeckJoint(cfg, isCut=False).mv(-jctol, 0, 0))
    if spCut is not None:
        neck = neck.cut(spCut)
    if cfg.sepFretbd or cfg.sepTop:
        neck = neck.cut(fbspCut)
    if cfg.sepFretbd or cfg.sepTop:
        neck = neck.cut(Fretboard(cfg, isCut=True).mv(0, 0, -jctol))
    if cfg.sepNeck and not cfg.sepFretbd:
        neck = neck.join(fretbd)

    # gen bridge
    brdg = Bridge(cfg).cut(strCuts)

    # gen guide if using tuning pegs rather than worm drive
    guide = Guide(cfg) if cfg.tnrCfg.is_peg() else None

    # gen body top
    top = Top(cfg)

    if cfg.sepTop:
        top = top.join(Rim(cfg, isCut=False))

    top = top.cut(chmCut).cut(tnrsCut).cut(Soundhole(cfg))

    if cfg.sepFretbd or cfg.sepNeck:
        top = top.cut(FretbdJoint(cfg, isCut=True).mv(-jctol, 0, -jctol))

    if cfg.sepBrdg:
        top = top.cut(Bridge(cfg, isCut=True))
        if not guide is None:
            top = top.cut(Guide(cfg, isCut=True))
    else:
        top = top.join(brdg)
        if not guide is None:
            top = top.join(guide)

    if cfg.sepTop and not cfg.sepFretbd and not cfg.sepNeck:
        top = top.join(fretbd)

    # problematic edge selection?
    # top = top.filletByNearestEdges(
    #     [
    #         (cfg.sndholeX, cfg.sndholeY, cfg.brdgZ),
    #         (cfg.sndholeX, cfg.sndholeY, 0),
    #     ],
    #     FILLET_RAD,
    # )

    # if cfg.tnrCfg.is_worm():
    #     wcfg: WormConfig = cfg.tnrCfg
    #     top = top.filletByNearestEdges(
    #         [
    #             (xyz[0] - wcfg.slitLen, xyz[1], xyz[2] + wcfg.strHt())
    #             for xyz in cfg.tnrXYZs
    #         ],
    #         wcfg.slitWth,
    #     )

    # gen body bottom
    body = Body(cfg)

    if not cfg.noTxt:
        txtCut = Texts(cfg, isCut=True).mv(0, 0, -jctol).cut(body)
        body = body.cut(txtCut.mv(0, 0, cfg.EMBOSS_DEP))

    if not cfg.sepNeck:
        body = body.join(neck.mv(jctol, 0, 0))

    body = body.cut(chmCut)
    if spCut is not None:
        body = body.cut(spCut)
    if cfg.sepTop:
        body = body.cut(rimCut)

    if cfg.sepNeck:
        body = body.cut(NeckJoint(cfg, isCut=True).mv(-jctol, 0, jctol))
    elif cfg.sepFretbd or cfg.sepTop:
        body = body.cut(fbspCut)

    wormKeyCut = None if not cfg.tnrCfg.is_worm() else WormKey(cfg, isCut=True)

    if cfg.sepEnd:
        body = body.cut(TailEnd(cfg, isCut=True).mv(0, 0, jctol))
    else:
        body = body.cut(tnrsCut)
        if wormKeyCut is not None:
            body = body.cut(wormKeyCut)

    if not cfg.sepTop:
        if not cfg.sepFretbd and not cfg.sepNeck:
            # HACK mv needed for Cadquery sometimes
            top = top.join(fretbd.mv(0.01, 0, 0))
        body = body.join(top.mv(0, 0, -jctol))

    if cfg.sepEnd:
        tail = TailEnd(cfg, isCut=False).cut(tnrsCut).cut(chmCut)
        if spCut is not None:
            tail = tail.cut(spCut)
        if cfg.sepTop:
            tail = tail.cut(rimCut)
        if wormKeyCut is not None:
            tail = tail.cut(wormKeyCut)
        parts.append(tail)

    parts.append(body)

    if cfg.sepFretbd:
        parts.append(fretbd)

    if cfg.sepTop:
        parts.append(top)

    if cfg.sepNeck:
        parts.append(neck)

    if cfg.sepBrdg:
        parts.append(brdg)

    if guide is not None and cfg.sepBrdg:
        parts.append(guide)

    if cfg.tnrCfg.is_worm():
        parts.append(WormKey(cfg, isCut=False))

    return parts
