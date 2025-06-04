# coding: utf-8
from rich import print
import sly
import re
import sys

class Lexer(sly.Lexer):
    print("\n--Lexer--\n")
    # #ignorar mayusculas y minusculas
    reflags = re.IGNORECASE

    tokens = {
        # keywords
        "LET", "READ", "DATA", "PRINT", "GOTO", "IF",
        "THEN", "FOR", "NEXT", "TO", "STEP", "END",
        "STOP", "DEF", "GOSUB", "DIM", "REM", "RETURN",
        "RESTORE",  # Actualizado aquí
        # "RUN", "LIST", "NEW",

        # operadores de relacion
        "LT", "LE", "GT", "GE", "NE",

        # identificador
        "ID",
        
        # otros

        'FLOAT', 'INTEGER', 'STRING', 'FN',  # Actualizado aquí
        'INPUT', 'BLTIN', 'NEWLINE',
    }

    literals = '+-*/^()=:,;'

    ignore = ' \t\r'

    @_(r'\n+') # type: ignore
    def NEWLINE(self, t):
        self.lineno += 1
        t.value = ''
        return t

    REM    = r'REM.*'
    LET    = r'LET' 
    READ   = r'READ'
    DATA   = r'DATA'
    PRINT  = r'PRINT'
    GOTO   = r'GO ?TO'
    IF     = r'IF'
    THEN   = r'THEN'
    FOR    = r'FOR'
    NEXT   = r'NEXT'
    TO     = r'TO'
    STEP   = r'STEP'
    END    = r'END'
    STOP   = r'STOP'
    DEF    = r'DEF'
    GOSUB  = r'GOSUB'
    DIM    = r'DIM'
    RETURN = r'RETURN'
    INPUT  = r'INPUT'
    BLTIN  = r'SIN|COS|TAN|ATN|EXP|ABS|LOG|SQR|RND|INT|TAB|DEG|PI|TIME|LEFT|MID|RIGHT|LEN|CHR'
    RESTORE = r'RESTORE'

    # Identificador
    # ID = r'[A-Za-z][A-Za-z0-9_]*\$?'
    ID = r'(?![Ff][Nn])[A-Za-z][0-9]?\$?'
    # Para nombres de funciones, si se necesitan reglas especiales, ajustar aquí
    FN = r'FN[A-Z]'
    
    
    
    
    # Números flotantes y enteros
    # FLOAT  = r'\d+\.\d+'
    # INTEGER = r'\d+(?!\.\d)'
    # Otros tokens
    # STRING  = r'"[^"]*"'
    NE = r'<>'
    LE = r'<='
    # LT = r'<+(?!>)'  # r'<'  # r'<+(?!>)'
    LT = r'<'
    GE = r'>='
    GT = r'>+(?!<)'

    def error(self, t):
        print(f"Línea {t.lineno}: [red]caracter ilegal '{t.value[0]}'[/red]")
        self.index += 1

    @_(r'(\d+\.\d+|\.\d+)([eE][+-]?\d+)?') # type: ignore
    def FLOAT(self, t):
        t.value = float(t.value)    
        return t
	
    @_(r'\d+') # type: ignore
    def INTEGER(self, t):
        t.value = int(t.value)
        return t
	
    @_(r'"[^"]*"') # type: ignore
    def STRING (self, t):
        t.value = t.value[1:-1]
        return t

#----------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('uso: baslex.py filename')
        sys.exit(1)
    lex = Lexer()    
    data = open(sys.argv[1]).read()
 
 
    for tok in lex.tokenize(data):
        if tok.type == 'NEWLINE':
            print("\n")
        print(tok)
