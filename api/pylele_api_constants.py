#!/usr/bin/env python3
from enum import Enum

FIT_TOL = 0.1
FILLET_RAD = 0.4

DEFAULT_TEST_DIR = "test"
DEFAULT_BUILD_DIR = "build"


# Colors
class ColorEnum(Enum):
    """Color Enumerator"""

    BLACK = (0, 0, 0)
    CARBON = (16, 16, 16)
    GRAY = (128, 128, 128)
    LITE_GRAY = (160, 160, 160)
    DARK_GRAY = (32, 32, 32)
    ORANGE = (255, 64, 0)
    WHITE = (255, 255, 255)
