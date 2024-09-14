from enum import Enum

FIT_TOL = .1
FILLET_RAD = .4

DEFAULT_TEST_DIR='test'
DEFAULT_BUILD_DIR='build'

# Colors
class ColorEnum(Enum):
    """ Color Enumerator """
    BLACK = (1, 1, 1),
    CARBON = (32, 32, 32),
    GRAY = (128, 128, 128),
    LITE_GRAY = (192, 192, 192),
    DARK_GRAY = (64, 64, 64),
    ORANGE = (250, 100, 0),
    WHITE = (250, 250, 250)
