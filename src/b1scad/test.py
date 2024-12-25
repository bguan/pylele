#!/usr/bin/env python3

"""
    B1scad Tests
"""

import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from b1scad.scad2py import scad2py

class B1scadTestMethods(unittest.TestCase):
    """Pylele Test Class"""
    def test_all_scad(self):
        scaddir = "./b1scad/scad"
        for idx in range(3):
            fname = f"model{idx:02}.scad"
            fullfile = os.path.join(scaddir,fname)
            print(fullfile)
            scad2py(fullfile)

def test_main():
    """ Launch all tests """
    unittest.main()

if __name__ == "__main__":
    test_main()
