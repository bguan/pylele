#!/usr/bin/env python3

"""
    Pylele Tests
"""

import unittest

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

# assemblies
from pylele_nut_assembly import test_nut_assembly
from pylele_fretboard_assembly import test_fretboard_assembly


class PyleleTestMethods(unittest.TestCase):
    """ Pylele Test Class """

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

    ## Assemblies

    def test_nut_assembly(self):
        """ Test Nut Assembly """
        test_nut_assembly()

    def test_fretboard_assembly(self):
        """ Test Fretboard Assembly """
        test_fretboard_assembly()
        
if __name__ == '__main__':
    unittest.main()