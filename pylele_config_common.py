"""
    Pylele Config Common between Pylele1 and Pylele2
"""

from enum import IntEnum

SEMI_RATIO = 2**(1/12)

class LeleScaleEnum(IntEnum):
    """ Enumerator for Scale Length Names """
    SOPRANO = 330
    CONCERT = 370
    TENOR   = 430

def type_scale_len(length: int):
    """ Returns scale length in mm
        input is a string either representing mm
        or LeleScaleEnum member
    """
    ulen = length.upper()
    if ulen in LeleScaleEnum._member_names_:
        return LeleScaleEnum[ulen].value
    return literal_eval(len)

# Tuner config

class TunerConfig:
    """ Tuner Configuration """
    def __init__(
        self,
        holeHt: float = 8,
        code: str = '?',
    ):
        self.holeHt = holeHt
        self.code = code

    def minGap(self) -> float:
        pass

    def tailAllow(self) -> float:
        pass
