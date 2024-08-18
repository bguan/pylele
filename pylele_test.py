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

# solid parts
from parts.tube import test_tube
from parts.screw import test_screw

# ukulele parts
from pylele2.pylele_frets import test_frets
from pylele2.pylele_fretboard import test_fretboard
from pylele2.pylele_fretboard_dots import test_fretboard_dots
from pylele2.pylele_fretboard_spines import test_fretboard_spines
from pylele2.pylele_fretboard_joint import test_fretboard_joint
from pylele2.pylele_top import test_top
from pylele2.pylele_strings import test_strings
from pylele2.pylele_nut import test_nut
from pylele2.pylele_spines import test_spines
from pylele2.pylele_head import test_head
from pylele2.pylele_neck_joint import test_neck_joint
from pylele2.pylele_neck import test_neck
from pylele2.pylele_bridge import test_bridge
from pylele2.pylele_guide import test_guide
from pylele2.pylele_chamber import test_chamber
from pylele2.pylele_peg import test_peg
from pylele2.pylele_worm import test_worm
from pylele2.pylele_tuners import test_tuners
from pylele2.pylele_body import test_body
from pylele2.pylele_texts import test_texts
from pylele2.pylele_rim import test_rim
from pylele2.pylele_worm_key import test_worm_key
from pylele2.pylele_tail import test_tail
from pylele2.pylele_brace import test_brace
from pylele2.pylele_soundhole import test_soundhole

# assemblies
from pylele2.pylele_fretboard_assembly import test_fretboard_assembly
from pylele2.pylele_neck_assembly import test_neck_assembly
from pylele2.pylele_top_assembly import test_top_assembly
from pylele2.pylele_bottom_assembly import test_bottom_assembly

def make_api_path_and_filename(api_name,test_path=DEFAULT_TEST_DIR):
    """ Makes Test API folder and filename """
    out_path = os.path.join(Path.cwd(),test_path,api_name)

    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    assert os.path.isdir(out_path)

    outfname = os.path.join(out_path,api_name+'.stl')
    print(outfname)
    return outfname

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
    def test_cadquery_api(self):
        """ Test Cadquery API """
        test_api(module_name='api.cq_api',class_name='CQShapeAPI')

    def test_blender_api(self):
        """ Test Blender API """
        test_api(module_name='api.bpy_api',class_name='BlenderShapeAPI')
    
    ## Solid Parts
    def test_tube(self):
        """ Test Tube """
        test_tube()

    def test_screw(self):
        """ Test Screw """
        test_screw()

    ## Pylele Individual Parts
    
    def test_frets(self):
        """ Test Frets """
        test_frets()

    def test_fretboard(self):
        """ Test Fretboard """
        test_fretboard()

    def test_fretboard_dots(self):
        """ Test Fretboard Dots """
        test_fretboard_dots()

    def test_fretboard_spines(self):
        """ Test Fretboard Spines """
        test_fretboard_spines()

    def test_fretboard_joint(self):
        """ Test Fretboard Joint """
        test_fretboard_joint()

    def test_top(self):
        """ Test Top """
        test_top()

    def test_strings(self):
        """ Test Strings """
        test_strings()

    def test_nut(self):
        """ Test Nut """
        test_nut()

    def test_spines(self):
        """ Test Spines """
        test_spines()

    def test_head(self):
        """ Test Head """
        test_head()

    def test_neck_joint(self):
        """ Test Neck Joint """
        test_neck_joint()

    def test_neck(self):
        """ Test Neck """
        test_neck()

    def test_bridge(self):
        """ Test Bridge """
        test_bridge()

    def test_guide(self):
        """ Test Guide """
        test_guide()

    def test_chamber(self):
        """ Test Chamber """
        test_chamber()

    def test_peg(self):
        """ Test Peg """
        test_peg()

    def test_worm(self):
        """ Test Worm """
        test_worm()

    def test_tuners(self):
        """ Test Tuners """
        test_tuners()

    def test_body(self):
        """ Test Body """
        test_body()

    def test_texts(self):
        """ Test Texts """
        test_texts()

    def test_rim(self):
        """ Test Rim """
        test_rim()

    def test_worm_key(self):
        """ Test Worm Key """
        test_worm_key()

    def test_tail(self):
        """ Test Tail """
        test_tail()

    def test_brace(self):
        """ Test Brace """
        test_brace()

    def test_soundhole(self):
        """ Test Soundhole """
        test_soundhole()

    ## Assemblies

    def test_fretboard_assembly(self):
        """ Test Fretboard Assembly """
        test_fretboard_assembly()

    def test_neck_assembly(self):
        """ Test Neck Assembly """
        test_neck_assembly()

    def test_top_assembly(self):
        """ Test Top Assembly """
        test_top_assembly()

    def test_bottom_assembly(self):
        """ Test Bottom Assembly """
        test_bottom_assembly()

if __name__ == '__main__':
    unittest.main()
