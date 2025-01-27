#!/usr/bin/env python3

"""
    Pylele Tests
"""

import unittest

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from b13d.api.core import test_api, DEFAULT_TEST_DIR
from b13d.api.utils import make_or_exist_path
from b13d.test import test_report, test_main

TEST_NAME="pylele2"

class PyleleTestMethods(unittest.TestCase):
    """Pylele Test Class"""

    ## Solid Parts
    from pylele.parts.tunable_saddle import test_tunable_saddle, test_tunable_saddle_mock
    from pylele.parts.tunable_bridge import test_tunable_bridge, test_tunable_bridge_mock

    ## Pylele Individual Parts
    from pylele.pylele2.frets import test_frets, test_frets_mock
    from pylele.pylele2.fretboard import test_fretboard, test_fretboard_mock
    from pylele.pylele2.fretboard_dots import (
        test_fretboard_dots,
        test_fretboard_dots_mock,
    )
    from pylele.pylele2.fretboard_spines import (
        test_fretboard_spines,
        test_fretboard_spines_mock,
    )
    from pylele.pylele2.fretboard_joint import (
        test_fretboard_joint,
        test_fretboard_joint_mock,
    )
    from pylele.pylele2.top import test_top, test_top_mock
    from pylele.pylele2.strings import test_strings, test_strings_mock
    from pylele.pylele2.nut import test_nut, test_nut_mock
    from pylele.pylele2.spines import test_spines, test_spines_mock
    from pylele.pylele2.head import test_head, test_head_mock
    from pylele.pylele2.neck_joint import test_neck_joint, test_neck_joint_mock
    from pylele.pylele2.neck import test_neck, test_neck_mock
    from pylele.pylele2.bridge import test_bridge, test_bridge_mock
    from pylele.pylele2.guide import test_guide, test_guide_mock
    from pylele.pylele2.chamber import test_chamber, test_chamber_mock
    from pylele.pylele2.peg import test_peg, test_peg_mock
    from pylele.pylele2.worm import test_worm, test_worm_mock
    from pylele.pylele2.turnaround import test_turnaround,test_turnaround_mock
    from pylele.pylele2.tuners import test_tuners, test_tuners_mock
    from pylele.pylele2.body import test_body, test_body_mock
    from pylele.pylele2.texts import test_texts, test_texts_mock
    from pylele.pylele2.rim import test_rim, test_rim_mock
    from pylele.pylele2.worm_key import test_worm_key, test_worm_key_mock
    from pylele.pylele2.tail import test_tail, test_tail_mock
    from pylele.pylele2.brace import test_brace, test_brace_mock
    from pylele.pylele2.soundhole import test_soundhole, test_soundhole_mock

    ## Assemblies
    from pylele.pylele2.fretboard_assembly import (
        test_fretboard_assembly,
        test_fretboard_assembly_mock,
    )
    from pylele.pylele2.neck_assembly import test_neck_assembly, test_neck_assembly_mock
    from pylele.pylele2.bridge_assembly import test_bridge_assembly, test_bridge_assembly_mock
    from pylele.pylele2.top_assembly import test_top_assembly, test_top_assembly_mock
    from pylele.pylele2.bottom_assembly import (
        test_bottom_assembly,
        test_bottom_assembly_mock,
    )
    from pylele.pylele2.all_assembly import test_all_assembly, test_all_assembly_mock

    def test_zz_report(self):
        """ Generate Test Report """
        test_report(name=TEST_NAME)

if __name__ == "__main__":
    test_main(TEST_NAME)
