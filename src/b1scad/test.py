#!/usr/bin/env python3

"""
    B1scad Tests
"""

import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from b1scad.scad2py import scad2py
from pylele.conversion.scad2stl import scad2stl
from pylele.api.solid import stl_report_metrics, volume_match_reference

def stl_compare_volume(refstl, outstl):
    refrpt = stl_report_metrics(refstl)
    outrpt = stl_report_metrics(outstl)

    assert volume_match_reference(
            volume=outrpt['volume'],
            reference=refrpt['volume'],
        ), f"reference file: {refstl}\nout file: {outstl}\nreference volume: {refrpt['volume']}, volume: {outrpt['volume']}"
    
    pass

class B1scadTestMethods(unittest.TestCase):
    """Pylele Test Class"""
    def test_all_scad(self):
        scaddir = os.path.join(os.path.abspath(os.path.dirname(__file__)),"scad")
        for idx in range(11):
            fname = f"model{idx:02}"
            scadfname = f"{fname}.scad"
            fullscadfile = os.path.join(scaddir,scadfname)
            print(fullscadfile)

            # generate reference .stl file
            refstl = scad2stl(fullscadfile)

            # generate output .py and .stl file
            outpy, modelname = scad2py(fullscadfile, execute_en=True)
            outstl = os.path.join("./build",modelname,f'{modelname}.stl')
            stl_compare_volume(refstl, outstl)

def test_main():
    """ Launch all tests """
    unittest.main()

if __name__ == "__main__":
    test_main()
