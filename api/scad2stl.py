#!/usr/bin/env python3

""" Converts a .scad file into a .stl mesh """

import sys
import os
from packaging import version

OPENSCAD='openscad'

def openscad_version():
    """ Returns openscad version """
    tmplog='log.txt'
    cmdstr = f'{OPENSCAD} -v 2>&1 | cat > {tmplog}'
    os.system(cmdstr)

    assert os.path.isfile(tmplog), f'ERROR: file {tmplog} does not exist!'

    with open(tmplog, encoding='utf-8') as f:
        lines = f.readlines()

    # print(f'<{lines}>')
    ans = lines[0].split()
    assert len(ans)==3, f'Missing arguments in openscad version output <{ans}>'

    ver=ans[2]
    # print(ver)

    # remove temporary file
    os.system(f'rm {tmplog}')

    return ver

def openscad_manifold_ok() -> bool:
    """ check manifold available """
    # https://github.com/openscad/openscad/issues/391#issuecomment-1718145488
    ver = openscad_version()
    # print(ver)
    if version.parse(ver) > version.parse("2023.09"):
        return True
    return False

def openscad_manifold_opt() -> str:
    """ generate manifold option enable, if available """
    if openscad_manifold_ok():
        return '--enable=manifold'
    return ''

def scad2stl(infile) -> str:
    """ Converts a .stl mesh into a .glb """
    assert os.path.isfile(infile), f'File {infile} does not exist!!!'

    fname, fext = os.path.splitext(infile)
    assert fext=='.scad'
    fout = fname+'.stl'

    manifold = openscad_manifold_opt()
    cmdstr = f'{OPENSCAD} {manifold} -o {fout} {infile}'
    os.system(cmdstr)

    assert os.path.isfile(fout), f'ERROR: file {fout} does not exist!'
    return fout

if __name__ == '__main__':
    scad2stl(sys.argv[1])
