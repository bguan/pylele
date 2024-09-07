#!/usr/bin/env python3

""" Converts a .stl mesh into a .glb """

import sys
import os
import trimesh

def stl2glb(infile) -> str:
    """ Converts a .stl mesh into a .glb """
    assert os.path.isfile(infile), f'File {infile} does not exist!!!'
    mesh =  trimesh.load_mesh(infile)
    fname, fext = os.path.splitext(infile)
    assert fext=='.stl'
    out_fname = fname+'.glb'
    mesh.export(out_fname)
    assert os.path.isfile(out_fname), f'File {out_fname} does not exist!!!'
    return out_fname

if __name__ == '__main__':
    stl2glb(sys.argv[1])
