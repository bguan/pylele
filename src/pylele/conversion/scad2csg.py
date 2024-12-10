#!/usr/bin/env python3

""" Converts a .scad file into a .csg representation """

import sys
import os
import time

OPENSCAD='openscad'

def scad2csg(infile, command=OPENSCAD) -> str:
    """ Converts a .scad mesh into a .csg """
    assert os.path.isfile(infile), f'File {infile} does not exist!!!'

    inpath, baseinfile = os.path.split(infile)
    fname, fext = os.path.splitext(baseinfile)
    assert fext=='.scad'
    # for whatever reason openscad does not like to export .csg on a different directory
    fout = fname+'.csg'

    cmdstr = f'{command} -o {fout} {infile}'
    print(cmdstr)
    os.system(cmdstr)

    time.sleep(0.1) # wait for file to appear
    assert os.path.isfile(fout), f'ERROR: file {fout} does not exist!'

    # mv output file to input directory
    cmdstr = f'mv {fout} {inpath}'
    os.system(cmdstr)
    outfname = os.path.join(inpath,fout)
    assert os.path.isfile(outfname), f'ERROR: file {outfname} does not exist!'

    return outfname

if __name__ == '__main__':
    scad2csg(sys.argv[1])
