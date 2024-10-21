#!/usr/bin/env python3

""" Converts a .scad file into a .stl mesh """

import sys
import os
import argparse
from packaging import version

OPENSCAD='openscad --export-format binstl'
IMPLICITCAD='~/.cabal/bin/extopenscad'

def scad2stl_parser(parser=None):
    """
    scad2stl Command Line Interface
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='scad2stl configuration')

    ## options ######################################################
    parser.add_argument("-os", "--openscad", help="openscad executable command (ignored when --implicit is selected).",
                         type=str,default=OPENSCAD)
    parser.add_argument("--implicit",
                    help="Use implicitCAD (extopenscad) as solidpython2 backend",
                    action='store_true')
    return parser


def openscad_version(command=OPENSCAD):
    """ Returns openscad version """
    tmplog='log.txt'
    cmdstr = f'{command} -v 2>&1 | cat > {tmplog}'
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

def openscad_manifold_ok(command=OPENSCAD) -> bool:
    """ check manifold available """
    # https://github.com/openscad/openscad/issues/391#issuecomment-1718145488
    ver = openscad_version(command)
    # print(ver)
    if version.parse(ver) > version.parse("2023.09"):
        return True
    return False

def openscad_manifold_opt(command=OPENSCAD) -> str:
    """ generate manifold option enable, if available """
    if command==IMPLICITCAD:
        return ''
    if openscad_manifold_ok(command):
        return '--enable=manifold'
    return ''

def scad2stl(infile, command=OPENSCAD, implicit = False) -> str:
    """ Converts a .stl mesh into a .glb """
    assert os.path.isfile(infile), f'File {infile} does not exist!!!'

    fname, fext = os.path.splitext(infile)
    assert fext=='.scad'
    fout = fname+'.stl'

    if implicit:
        command = IMPLICITCAD

    manifold = openscad_manifold_opt(command=command)
    cmdstr = f'{command} {manifold} -o {fout} {infile}'
    os.system(cmdstr)

    assert os.path.isfile(fout), f'ERROR: file {fout} does not exist!'
    return fout

def scad2stl_main(args:list) -> None:
    parser = scad2stl_parser()
    cli = parser.parse_args(args=args[1:])
    scad2stl(args[0],implicit=cli.implicit,command=cli.openscad)

if __name__ == '__main__':
    scad2stl_main(sys.argv[1:])
