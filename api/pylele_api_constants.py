from enum import Enum

FIT_TOL = .1
FILLET_RAD = .4

# Colors
class ColorEnum(Enum):
    """ Color Enumerator """
    CARBON = (32, 32, 32),
    GRAY = (128, 128, 128),
    LITE_GRAY = (192, 192, 192),
    DARK_GRAY = (64, 64, 64),
    ORANGE = (255, 165, 0),
    WHITE = (255, 255, 255)
