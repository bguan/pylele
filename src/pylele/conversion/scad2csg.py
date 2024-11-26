#!/usr/bin/env python3

""" Converts a .scad file into a .csg representation """

import sys
import os

OPENSCAD='openscad'

def scad2csg(infile, command=OPENSCAD) -> str:
    """ Converts a .scad mesh into a .csg """
    assert os.path.isfile(infile), f'File {infile} does not exist!!!'

    fname, fext = os.path.splitext(infile)
    assert fext=='.scad'
    fout = fname+'.csg'

    cmdstr = f'{command} -o {fout} {infile}'
    os.system(cmdstr)

    assert os.path.isfile(fout), f'ERROR: file {fout} does not exist!'
    return fout

if __name__ == '__main__':
    scad2csg(sys.argv[1])
