#!/usr/bin/env python3

"""
Converts a .svg file to .dxf
"""

import sys
import os

def svg2dxf_wrapper(infile, outfile='') -> str:
    """ Converts an  into a binary """
    assert os.path.isfile(infile), f"ERROR: Input File {infile} does not exist!"

    if outfile=='':
        fname,fext = os.path.splitext(infile)
        outfile = f'{fname}.dxf'

    cmdstr = f'svg2dxf {infile} -o {outfile}'
    os.system(cmdstr)
    assert os.path.isfile(outfile), f"ERROR: Output File {outfile} does not exist!"
    return outfile

if __name__ == '__main__':
    svg2dxf_wrapper(sys.argv[1])
