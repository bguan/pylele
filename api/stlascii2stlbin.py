#!/usr/bin/env python3

""" 
Converts a .stl file from ascii to binary format 
Uses stl2bin tool included with numpy-stl
"""

import sys
import os

def stl_is_bin(fname) -> bool:
    """ Returns True if .scl in ascii format """
    with open(fname, "r",encoding='utf-8') as fp:
        retval=fp.readline().find("solid") > -1
        fp.close()
    return retval

def stlascii2stlbin(infile,outfile='') -> str:
    """ Converts an ASCII .stl into a binary """
    assert os.path.isfile(infile), f"ERROR: Input File {infile} does not exist!"

    if not stl_is_bin(infile):
        if outfile=='':
            fname,fext = os.path.splitext(infile)
            outfile = f'{fname}_bin{fext}'

        cmdstr = f'stl2bin {infile} {outfile}'
        os.system(cmdstr)
        assert os.path.isfile(outfile), f"ERROR: Output File {outfile} does not exist!"
        return outfile
    
    # else
    print(f'WARNING: .stl {infile} is already in binary format!')
    return infile

if __name__ == '__main__':
    stlascii2stlbin(sys.argv[1])
