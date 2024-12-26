#!/usr/bin/env python3

""" converts scad to ast """

# scad_parser.py
from __future__ import annotations
from sly import Lexer

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from pylele.api.utils import gen_scad_foo

class OpenSCADLexer(Lexer):
    tokens = (
        CUBE, SPHERE, CYLINDER, 
        TRANSLATE, ROTATE, SCALE, UNION, DIFFERENCE, HULL,
        LBRACE, RBRACE, LPAREN, RPAREN, LSQUARE, RSQUARE, COMMA, SEMICOLON,
        NUMBER,
        IDENTIFIER, SFN, EQU,
    )
    ignore = ' \t\n'

    # Token definitions
    CUBE = r'cube'
    SPHERE = r'sphere'
    CYLINDER = r'cylinder'
    UNION = r'union'
    DIFFERENCE = r'difference'
    TRANSLATE = r'translate'
    ROTATE = r'rotate'
    SCALE = r'scale'
    HULL = r'hull'

    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    SFN = r'\$fn'
    NUMBER = r'[+-]?\d+(\.\d+)?'

    LBRACE = r'\{'
    RBRACE = r'\}'
    LPAREN = r'\('
    RPAREN = r'\)'
    LSQUARE = r'\['
    RSQUARE = r'\]'
    COMMA = r','
    SEMICOLON = r';'
    EQU = r'='

    ignore_comment = r'//.*'
    ignore_newline = r'\n+'

    def NUMBER(self, t):
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t
    
    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

# Modify parser to output Python file
def scad2ast(infname: str, view: bool = True):

    assert os.path.exists(infname), f'File not found: {infname}'
    with open(infname, 'r', encoding='utf8') as f:
        code = f.read()

        lexer = OpenSCADLexer()
        ast = lexer.tokenize(code)
        
        if view:
            print('AST:')
            for tok in ast:
                print('\t type=%r, value=%r' % (tok.type, tok.value))
            print('AST END')
            ast = lexer.tokenize(code)
        
        return ast

# Example usage:
if __name__ == "__main__":
    if len(sys.argv)<2:
        infname = "model.scad"
        print(f'Unspecified input file, generate default {infname}')
        gen_scad_foo(infname, module_en=False)
    else:
        infname = sys.argv[1]
    
    ast = scad2ast(infname)
