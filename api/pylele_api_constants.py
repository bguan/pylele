
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import LeleStrEnum

FIT_TOL = .1
FILLET_RAD = .4

# Colors
WHITE = (255, 255, 255)
LITE_GRAY = (192, 192, 192)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
CARBON = (32, 32, 32)

class ColorEnum(LeleStrEnum):
    """ Color Enumerator """
    CARBON = CARBON,
    GRAY = GRAY,
    LITE_GRAY = LITE_GRAY,
    DARK_GRAY = DARK_GRAY,
    ORANGE = ORANGE,
    WHITE = WHITE
