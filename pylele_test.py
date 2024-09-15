#!/usr/bin/env python3

"""
    Pylele Tests
"""

import os
import unittest
import importlib
from pathlib import Path

# api
from api.pylele_api import Fidelity
from api.pylele_solid import DEFAULT_TEST_DIR

def make_api_path_and_filename(api_name,test_path=DEFAULT_TEST_DIR):
    """ Makes Test API folder and filename """
    out_path = Path.cwd() / test_path / api_name

    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    assert os.path.isdir(out_path)

    # outfname = os.path.join(out_path,api_name+'.stl')
    # print(outfname)
    return out_path

def test_api(module_name,class_name):
    """ Test a Shape API """
    module = importlib.import_module(module_name)
    outfname = make_api_path_and_filename(module_name)
    class_ = getattr(module, class_name)
    api = class_(Fidelity.LOW)
    api.test(outfname)
class PyleleTestMethods(unittest.TestCase):
    """ Pylele Test Class """

    ## API
    def test_mock_api(self):
        """ Test Mock API """
        test_api(module_name='api.mock_api',class_name='MockShapeAPI')
    
    def test_cadquery_api(self):
        """ Test Cadquery API """
        test_api(module_name='api.cq_api',class_name='CQShapeAPI')

    def test_blender_api(self):
        """ Test Blender API """
        test_api(module_name='api.bpy_api',class_name='BlenderShapeAPI')
    
    def test_trimesh_api(self):
        """ Test Trimesh API """
        test_api(module_name='api.tm_api',class_name='TMShapeAPI')

    def test_solid2_api(self):
        """ Test SolidPython2 API """
        test_api(module_name='api.sp2_api',class_name='Sp2ShapeAPI')

    ## Solid Parts
    from parts.tube import test_tube, test_tube_mock
    from parts.screw import test_screw, test_screw_mock

    ## Pylele Individual Parts
    from pylele2.pylele_frets import test_frets, test_frets_mock
    from pylele2.pylele_fretboard import test_fretboard, test_fretboard_mock
    from pylele2.pylele_fretboard_dots import test_fretboard_dots, test_fretboard_dots_mock
    from pylele2.pylele_fretboard_spines import test_fretboard_spines, test_fretboard_spines_mock
    from pylele2.pylele_fretboard_joint import test_fretboard_joint, test_fretboard_joint_mock
    from pylele2.pylele_top import test_top, test_top_mock
    from pylele2.pylele_strings import test_strings, test_strings_mock
    from pylele2.pylele_nut import test_nut, test_nut_mock
    from pylele2.pylele_spines import test_spines, test_spines_mock
    from pylele2.pylele_head import test_head, test_head_mock
    from pylele2.pylele_neck_joint import test_neck_joint, test_neck_joint_mock
    from pylele2.pylele_neck import test_neck, test_neck_mock
    from pylele2.pylele_bridge import test_bridge, test_bridge_mock
    from pylele2.pylele_guide import test_guide, test_guide_mock
    from pylele2.pylele_chamber import test_chamber, test_chamber_mock
    from pylele2.pylele_peg import test_peg, test_peg_mock
    from pylele2.pylele_worm import test_worm, test_worm_mock
    from pylele2.pylele_tuners import test_tuners, test_tuners_mock
    from pylele2.pylele_body import test_body,test_body_mock
    from pylele2.pylele_texts import test_texts, test_texts_mock
    from pylele2.pylele_rim import test_rim, test_rim_mock
    from pylele2.pylele_worm_key import test_worm_key, test_worm_key_mock
    from pylele2.pylele_tail import test_tail, test_tail_mock
    from pylele2.pylele_brace import test_brace, test_brace_mock
    from pylele2.pylele_soundhole import test_soundhole, test_soundhole_mock
    from pylele2.pylele_neck_bend import test_neck_bend, test_neck_bend_mock

    ## Assemblies
    from pylele2.pylele_fretboard_assembly import test_fretboard_assembly, test_fretboard_assembly_mock
    from pylele2.pylele_neck_assembly import test_neck_assembly, test_neck_assembly_mock
    from pylele2.pylele_top_assembly import test_top_assembly, test_top_assembly_mock
    from pylele2.pylele_bottom_assembly import test_bottom_assembly, test_bottom_assembly_mock
    from pylele2.pylele_all_assembly import test_all_assembly, test_all_assembly_mock

if __name__ == '__main__':
    unittest.main()
