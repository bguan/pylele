"""
    Pylele Config Common between Pylele1 and Pylele2
"""

from enum import IntEnum, Enum
from ast import literal_eval
from abc import ABC, abstractmethod

SEMI_RATIO = 2**(1/12)

class LeleScaleEnum(IntEnum):
    """ Enumerator for Scale Length Names """

    # https://ukeplanet.com/ukulele-sizes-the-ultimate-guide/
    
    SOPRANINO = 280
    TRAVEL    = 330
    SOPRANO   = 350
    CONCERT   = 380
    TENOR     = 430
    GUITAR    = 650

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

class TunerConfig(ABC):
    """ Tuner Configuration """
    def __init__(
        self,
        code: str = '?',
    ):
        self.code = code

    @abstractmethod
    def minGap(self) -> float:
        ...

    @abstractmethod
    def dims(self) -> tuple[float, float, float, float, float, float]:
        """
        (left, right, front, back, top, bottom)
        """
        ...

    @abstractmethod
    def tailAllow(self) -> float:
        ...

    @abstractmethod
    def strHt(self) -> float:
        """
        string height above tuner at 0
        """
        ...

    @abstractmethod
    def is_peg(self) -> bool:
        ...

    @abstractmethod
    def is_worm(self) -> bool:
        ...

    def __repr__(self):
        properties = '\n'.join(f"{key}={value!r}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}\n\n{properties}"

# Tuner config

class PegConfig(TunerConfig):

    STEM_ABOVE_HOLE: float = 4

    """ Peg Configuration """
    def __init__(
        self,
        majRad: float = 8,
        minRad: float = 4,
        botLen: float = 15,
        btnRad: float = 11.5,
        midTck: float = 10,
        holeHt: float = 8,
        tailAdj: float = -5,
        topCutTck: float = 100,
        code: str = 'P',
    ):
        super().__init__(code = code)
        self.holeHt = holeHt
        self.majRad = majRad
        self.minRad = minRad
        self.botLen = botLen
        self.btnRad = btnRad
        self.midTck = midTck
        self.tailAdj = tailAdj
        self.topCutTck = topCutTck

    def minGap(self) -> float:
        return 2*max(self.majRad, self.btnRad) + .5

    def dims(self) -> tuple[float, float, float, float, float, float]:
        maxRad = max(self.majRad, self.btnRad)
        return (
            maxRad,                             # front
            maxRad + self.tailAdj,              # back
            self.majRad,                        # left
            self.majRad,                        # right
            self.holeHt + self.STEM_ABOVE_HOLE, # top
            self.midTck + self.botLen,          # bottom
        )

    def is_peg(self) -> bool:
        return True

    def is_worm(self) -> bool:
        return False

    def strHt(self) -> float:
        return self.holeHt

    def tailAllow(self):
        (_, back, _, _, _, _) = self.dims()
        return back

class WormConfig(TunerConfig):

    """ Worm Configuration """
    def __init__(
        self,
        slitHt: float = 31,
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
        tailAdj: float = 0,
        buttonTck: float = 9.5,
        buttonWth: float = 16,
        buttonHt: float = 8,
        buttonKeyLen: float = 6,
        buttonKeyRad: float = 2.25,
        buttonKeybaseRad: float = 3.8,
        buttonKeybaseHt: float = 3,
        code: str = 'W',
    ):
        super().__init__(code = code)
        self.slitHt = slitHt
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
        self.tailAdj = tailAdj
        self.buttonTck = buttonTck
        self.buttonWth = buttonWth
        self.buttonHt = buttonHt
        self.buttonKeyRad = buttonKeyRad
        self.buttonKeyLen = buttonKeyLen
        self.buttonKeybaseRad = buttonKeybaseRad
        self.buttonKeybaseHt = buttonKeybaseHt

    def minGap(self) -> float:
        return self.diskTck + self.axleLen + self.gapAdj

    def dims(self) -> tuple[float, float, float, float, float, float]:
        halfX = max(self.diskRad, self.slitLen/2, self.driveLen/2)
        return (
            halfX,                              # front
            halfX + self.tailAdj,               # back
            max(self.driveRad, self.diskTck/2)
            + self.diskTck/2 + self.axleLen/2,  # left
            self.axleLen/2,                     # right
            self.slitHt - 2*self.axleRad,       # top
            self.diskRad,                       # bottom
        )

    def is_peg(self) -> bool:
        return False

    def is_worm(self) -> bool:
        return True

    def strHt(self) -> float:
        return self.slitHt - 2*self.axleRad

    def tailAllow(self):
        (front, back, _, _, _, _) = self.dims()
        return (front + back) / 2

class TurnaroundConfig(WormConfig):
    def __init__(
        self,
        slitHt: float = 31,
        slitLen: float = 10,
        slitWth: float = 3,
        diskTck: float = 5,
        diskRad: float = 7.7,
        axleRad: float = 3,
        axleLen: float = 8,
        driveRad: float = 0,
        driveLen: float = 0,
        driveOffset: float = 0,
        gapAdj: float = 1,
        tailAdj: float = 0,
        buttonTck: float = 9.5,
        buttonWth: float = 16,
        buttonHt: float = 8,
        buttonKeyLen: float = 6,
        buttonKeyRad: float = 2.25,
        buttonKeybaseRad: float = 3.8,
        buttonKeybaseHt: float = 3,
        code: str = 'T',
        peg_config = PegConfig(topCutTck=25)
    ):
        super().__init__(code = code)
        self.slitHt = slitHt
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
        self.tailAdj = tailAdj
        self.buttonTck = buttonTck
        self.buttonWth = buttonWth
        self.buttonHt = buttonHt
        self.buttonKeyRad = buttonKeyRad
        self.buttonKeyLen = buttonKeyLen
        self.buttonKeybaseRad = buttonKeybaseRad
        self.buttonKeybaseHt = buttonKeybaseHt
        self.peg_config = peg_config

FRICTION_PEG_CFG = PegConfig()
GOTOH_PEG_CFG = PegConfig(
    majRad=7.7,
    minRad=4.8,
    botLen=15,
    btnRad=9.5,
    midTck=11,
    holeHt=10,
    tailAdj=-2,
    code = 'G',
)
PEG_90 = PegConfig(
    majRad=7.7,
    minRad=3.3,
    botLen=9,
    btnRad=9.5,
    midTck=11,
    holeHt=10,
    tailAdj=-2,
    code = 'P',
)
WORM_TUNER_CFG = WormConfig()
BIGWORM_TUNER_CFG = WormConfig(
    slitHt=43,
    slitLen=10,
    diskTck=5 * 1.5,
    diskRad=7.7 * 1.5,
    axleRad=3 * 1.5,
    axleLen=6 * 1.5,
    driveRad=4 * 1.5,
    driveLen=14 * 1.5,
    driveOffset=9.75 * 1.5,
    gapAdj=1 * 1.5,
    tailAdj=0,
    code = 'B',
)

TURNAROUND_CFG = TurnaroundConfig()

class TunerType(Enum):
    """ Tuner Type Enumerator """
    FRICTION = FRICTION_PEG_CFG
    GOTOH = GOTOH_PEG_CFG
    WORM = WORM_TUNER_CFG
    BIGWORM = BIGWORM_TUNER_CFG
    TURNAROUND = TURNAROUND_CFG

    def list()->list:
        """ Return List of enumerated names """
        return TunerType._member_names_
