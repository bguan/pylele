"""
    Pylele Config Common between Pylele1 and Pylele2
"""

from enum import IntEnum, Enum
from ast import literal_eval

SEMI_RATIO = 2**(1/12)

class LeleScaleEnum(IntEnum):
    """ Enumerator for Scale Length Names """
    SOPRANO = 330
    CONCERT = 370
    TENOR   = 430

    def type(length:str)->int:
        """ Returns scale length in mm
        input is a string either representing mm
        or LeleScaleEnum member
        """
        ulen = length.upper()
        if ulen in LeleScaleEnum.list():
            return LeleScaleEnum[ulen].value
        return literal_eval(ulen)

    def list()->list:
        """ Return List of enumerated names """
        return LeleScaleEnum._member_names_

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

    def is_peg(self) -> bool:
        pass

    def is_worm(self) -> bool:
        pass

# Tuner config

class PegConfig(TunerConfig):
    """ Peg Configuration """
    def __init__(
        self,
        majRad: float = 8,
        minRad: float = 4,
        botLen: float = 15,
        btnRad: float = 11.5,
        midTck: float = 10,
        holeHt: float = 8,
        code: str = 'P',
    ):
        super().__init__(holeHt, code = code)
        self.majRad = majRad
        self.minRad = minRad
        self.botLen = botLen
        self.btnRad = btnRad
        self.midTck = midTck

    def minGap(self) -> float:
        return 2*max(self.majRad, self.btnRad) + .5

    def tailAllow(self) -> float:
        return self.majRad + self.btnRad - 1.5
    
    def is_peg(self) -> bool:
        return True

    def is_worm(self) -> bool:
        return False

class WormConfig(TunerConfig):
    """ Worm Configuration """
    def __init__(
        self,
        holeHt: float = 23,
        slitLen: float = 10,
        slitWth: float = 3,
        diskTck: float = 5,
        diskRad: float = 7.7,
        axleRad: float = 3,
        axleLen: float = 6,  # original worm tuner has 8mm axle
        driveRad: float = 4,
        driveLen: float = 14,
        driveOffset: float = 9.75,
        gapAdj: float = 1,
        buttonTck: float = 9.5,
        buttonWth: float = 16,
        buttonHt: float = 8,
        buttonKeyLen: float = 6,
        buttonKeyRad: float = 2.25,
        buttonKeybaseRad: float = 3.8,
        buttonKeybaseHt: float = 3,
        code: str = 'W',
    ):
        super().__init__(holeHt, code = code)
        self.slitLen = slitLen
        self.slitWth = slitWth
        self.diskTck = diskTck
        self.diskRad = diskRad
        self.axleRad = axleRad
        self.axleLen = axleLen
        self.driveRad = driveRad
        self.driveLen = driveLen
        self.driveOffset = driveOffset
        self.gapAdj = gapAdj
        self.buttonTck = buttonTck
        self.buttonWth = buttonWth
        self.buttonHt = buttonHt
        self.buttonKeyRad = buttonKeyRad
        self.buttonKeyLen = buttonKeyLen
        self.buttonKeybaseRad = buttonKeybaseRad
        self.buttonKeybaseHt = buttonKeybaseHt

    def minGap(self) -> float:
        return self.diskTck + self.axleLen + self.gapAdj

    def tailAllow(self) -> float:
        return self.driveLen
    
    def __repr__(self):
        properties = '\n'.join(f"{key}={value!r}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}\n\n{properties}"
    
    def is_peg(self) -> bool:
        return False

    def is_worm(self) -> bool:
        return True

FRICTION_PEG_CFG = PegConfig()
GOTOH_PEG_CFG = PegConfig(
    majRad=7.7,
    minRad=4.8,
    botLen=15,
    btnRad=9.5,
    midTck=11,
    holeHt=10,
    code = 'G',
)
WORM_TUNER_CFG = WormConfig()
BIGWORM_TUNER_CFG = WormConfig(
    holeHt=30,
    slitLen=10,
    diskTck=5 * 1.5,
    diskRad=7.7 * 1.5,
    axleRad=3 * 1.5,
    axleLen=7,
    driveRad=4 * 1.5,
    driveLen=14 * 1.5,
    driveOffset=9.75 * 1.5,
    gapAdj=1.5,
    code = 'B',
)

class TunerType(Enum):
    """ Tuner Type Enumerator """
    FRICTION = FRICTION_PEG_CFG
    GOTOH = GOTOH_PEG_CFG
    WORM = WORM_TUNER_CFG
    BIGWORM = BIGWORM_TUNER_CFG

    def list()->list:
        """ Return List of enumerated names """
        return TunerType._member_names_
