#!/usr/bin/env python3

"""
    Pylele Tests
"""

import os
import unittest
from pathlib import Path

# api
from pylele_config import Fidelity
from cq_api import CQShapeAPI
from bpy_api import BlenderShapeAPI

# parts
from pylele_frets import test_frets
from pylele_fretboard import test_fretboard
from pylele_fretboard_dots import test_fretboard_dots
from pylele_fretboard_spines import test_fretboard_spines
from pylele_fretboard_joint import test_fretboard_joint
from pylele_top import test_top
from pylele_strings import test_strings
from pylele_nut import test_nut
from pylele_spines import test_spines
from pylele_head import test_head
from pylele_neck_joint import test_neck_joint
from pylele_neck import test_neck
from pylele_bridge import test_bridge
from pylele_guide import test_guide
from pylele_chamber import test_chamber
from pylele_peg import test_peg
from pylele_worm import test_worm
from pylele_tuners import test_tuners
from pylele_body import test_body
from pylele_texts import test_texts
from pylele_rim import test_rim
from pylele_worm_key import test_worm_key
from pylele_tail import test_tail

# assemblies
from pylele_fretboard_assembly import test_fretboard_assembly
from pylele_neck_assembly import test_neck_assembly

def make_api_path_and_filename(api_name,test_path='./test'):
    """ Makes Test API folder and filename """
    out_path = os.path.join(Path.cwd(),test_path,api_name)

    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    assert os.path.isdir(out_path)

    outfname = os.path.join(out_path,api_name+'.stl')
    print(outfname)
    return outfname

class PyleleTestMethods(unittest.TestCase):
    """ Pylele Test Class """

    ## API
    def test_cadquery_api(self):
        """ Test Cadquery API """
        outfname = make_api_path_and_filename('cadquery_api')
        api = CQShapeAPI(Fidelity.LOW)
        api.test(outfname)

    def test_blender_api(self):
        """ Test Blender API """
        outfname = make_api_path_and_filename('blender_api')
        api = BlenderShapeAPI(Fidelity.LOW)
        api.test(outfname)

    ## Individual Parts
    
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

    ## Assemblies

    def test_fretboard_assembly(self):
        """ Test Fretboard Assembly """
        test_fretboard_assembly()

    def test_neck_assembly(self):
        """ Test Neck Assembly """
        test_neck_assembly()
        
if __name__ == '__main__':
    unittest.main()