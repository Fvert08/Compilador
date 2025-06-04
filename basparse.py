from rich import print
import sly

from baslex    import Lexer
from basast    import *
from basrender import DotRender

class Parser(sly.Parser):
    print("\n--Parser--\n")
    debugfile = 'parse.txt'
    expeced_shift_reduce = 3                                                                        

    tokens = Lexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', '^'),
        ('right', UMINUS),
    )

    @_(" { statement } ")
    def program(self, p):
        lines = {}  # Inicializamos un diccionario para almacenar las líneas del programa
        for cmd in p.statement:
            lines[int(cmd.lineno)] = cmd.comand  # Convertimos el número de línea a entero y almacenamos el comando
        return Program(lines)

    # @_("statement") # type: ignore
    # def program(self, p):
    #     lines, stmt = p.statement
    #     return Program({ lines: stmt })
    
    # @_("program statement ") # type: ignore
    # def program(self, p):
    #     lines, stmt = p.statement
    #     p.program [lines] = stmt
    #     return p.program
    
    @_("error")
    def program(self, p):
        raise SyntaxError("Programa Malformado")
    
    @_("INTEGER command NEWLINE")
    def statement(self, p):
        return Command(p.INTEGER, p.command)
    
    # @_("command")
    # def command(self, p):
    #     return p.command
    
    # @_("command ':' command")
    # def command(self, p):
    #     return p.command + [p.command]

    # @_("INTEGER", "FLOAT")
    # def statement(self, p):
    #     return Number(p[0])
    
    # @_("STRING")
    # def statement(self, p):
    #     return String(p.STRING)

    @_("INTEGER error")
    def statement(self, p):
        print(f"Error {p.error}")
        raise SyntaxError("Error en comando")
    

    @_("RESTORE")
    def command(self, p):
        return Restore()
    
    #-----------------------------------------------------------------------------------------------------------------------------------------LET
        
    @_("LET variable '=' expr")
    def command(self, p):
        # print(f"LET variable '=' expr\n p.variable: {p.variable} p.expr: {p.expr}\n")
        # input()
        return Let(p.variable, p.expr)
    
    #--------------- Atento por si la comento, porque una STRING puedo hacer que sea una expresion y ahorrarme esta regla.
    @_("LET variable '=' STRING")
    def command(self, p):
        return Let(p.variable, p.STRING)

    @_("STRING '+' STRING")
    def expr(self, p):
        return Binary('+', p.STRING0, p.STRING1)
    

    # --- CASO:  "" + I$           #testEliza1.bas (Solución de tener un token STRING y justo despues un NEWLINE sin contexto alguno) |   PARECE NO generar conflicto con test4
    @_("STRING '+' variable")
    def expr(self, p):
        return Binary('+', p.STRING, p.variable)

    # --- CASO:  I$ + ""            #testEliza1.bas (LET I$ = I$ + "-") (Solución de tener un token STRING y justo despues un NEWLINE sin contexto alguno)  |       ERROR CON TEST4 (LET I = I + 2 ) sumar entero por la derecha
    @_("variable '+' STRING")
    def expr(self, p):
        return Binary('+', p.variable, p.STRING)  # IDENT( p.ID ) , p.STRING <-- propuesta
    

    # --- CASO:  I$ + I$           #testEliza3.bas (Sumar 2 variables, ya sean de cadena o numericas) (Fijarme en el caso de I + I del test4, funciona correctamnete, pero con caso de LET I = I + 2 HAY ERROR)  ERROR CON TEST4
    @_("variable '+' variable ")
    def expr(self, p):
        return Binary('+', p.variable0, p.variable1)
    
    # --- CASO:  I$ + 2           #test4.bas (Sumar entero por la derecha)  |   ERROR CON TEST4, fijemonos que en el AST no lo genera como un Number si no como un 2 simplemente.
    @_("variable '+' INTEGER")
    def expr(self, p):
        return Binary('+', p.variable, Number(p.INTEGER))
    
    
    @_("LET variable '=' error")
    def command(self, p):
        print(f"ERROR EN LET variable '=' expr\n p.variable: {p.variable} p.expr: {p.error}\n")
        input()        
        raise SyntaxError("Error de expresion en LET")
 #-----------------------------------------------------------------------------------------------------------------------------------------LET

    #------READ
    
    @_("READ varlist")
    def command(self, p):
        return Read(p.varlist)
    
    @_("READ error")
    def command(self, p):
        raise SystemError("Lista de variables malformada en READ")
    
    #------DATA
    
    @_("DATA datalist")
    def command(self, p):
        return Data(p.datalist)
    

    @_("number { ',' number }")
    def datalist(self, p):
        return [p.number0] + p.number1
    

    @_("STRING { ',' STRING }")
    def datalist(self, p):
        return [p.STRING0] + p.STRING1
    
    @_("DATA error")
    def command(self, p):
        raise SyntaxError("Lista de numeros malformada en DATA")
    
    #------INPUT
    
    @_("INPUT [ STRING ',' ] varlist")#type:ignore
    def command(self, p):
        return Input(p.STRING, p.varlist)
    
    @_("INPUT error")
    def command(self, p):
        raise SyntaxError("Lista de variables malformada en INPUT")
    
    #------PRINT

    @_("PRINT plist [ optend ]")
    def command(self, p):
        return Print(p.plist, p.optend)
    
    @_("PRINT error")
    def command(self, p):
        raise SyntaxError("Declaración PRINT malformada")
    
    @_("PRINT")
    def command(self, p):
        return Print([])
    
    @_("','", "';'")
    def optend(self, p):
        return p[0]
    
    #------GOTO

    @_("GOTO INTEGER")
    def command(self, p):
        return Goto(Number(p.INTEGER))
    
    @_("GOTO error")
    def command(self, p):
        raise SystemError("Número de línea no válido en GOTO")
    
    #------IF

    @_("IF relexpr THEN INTEGER")
    def command(self, p):
        return IfStmt(p.relexpr, Number(p.INTEGER))
    
    #caso IF MID(I$,L,1) <> "'" THEN 240
    @_("IF STRING relexpr THEN INTEGER")
    def command(self, p):
        return IfStmt(p.relexpr, Number(p.INTEGER))
    
    @_("IF error THEN INTEGER")
    def command(self, p):
        print("p", p)
        print("p.error", p.error)
        input("\n\n")
        raise SystemError("Error en expresión relacional en IF")
    
    @_("IF relexpr THEN error")
    def command(self, p):
        print("Número de línea no válido en THEN") #print y no raise para que no se detenga el programa
    
    #------FOR

    @_("FOR ID '=' expr TO expr optstep")
    def command(self, p):
        return ForStmt(Variable(p.ID), p.expr0, p.expr1, p.optstep)
    
    @_("FOR ID '=' error TO expr optstep")
    def command(self, p):
        raise SystemError("Error en expresión de inicio en FOR")
    
    @_("FOR ID '=' expr TO error optstep")
    def command(self, p):
        raise SystemError("Error en expresión de fin en FOR")
    
    @_("FOR ID '=' expr TO expr error")
    def command(self, p):
        raise SystemError("Error en expresión de paso en FOR")
    
    #Optional STEP in FOR statement

    @_("STEP expr")
    def optstep(self, p):
        return p.expr
    
    @_("empty")
    def optstep(self, p):
        return None
    
    #------NEXT

    @_("NEXT ID")
    def command(self, p):
        return Next(Variable(p.ID))
    
    @_("NEXT error")
    def command(self, p):
        raise SystemError("NEXT malformaddo")
    
    #------END

    @_("END")
    def command(self, p):
        return End()
    
    #------REM

    @_("REM")
    def command(self, p):
        return Remark(p.REM[3:])
    
    #------STOP

    @_("STOP")
    def command(self, p):
        return Stop()
    
    #------DEF FN

    @_("DEF FN '(' ID ')' '=' expr")
    def command(self, p):
        return Function(p.FN, Variable(p.ID), p.expr)
    
    @_("DEF FN '(' ID ')' '=' error")
    def command(self, p):
        raise SystemError("Error en expresión en DEF")
    
    @_("DEF FN '(' error ')' '=' expr")
    def command(self, p):
        raise SystemError("Error de argumentos en DEF")
    
    #------GOSUB

    @_("GOSUB INTEGER")
    def command(self, p):
        return Gosub(Number(p.INTEGER))
    
    @_("GOSUB error")
    def command(self, p):
        raise SystemError("Número de línea no válido en GOSUB")
    
    #------RETURN

    @_("RETURN")
    def command(self, p):
        return Return()
    
    #------DIM

    @_("DIM dimlist")
    def command(self, p):
        return Dim(p.dimlist)
    
    @_("DIM error")
    def command(self, p):
        raise SystemError("Error en lista de variables en DIM")
    
    #List of variables supplied to DIM statement

    @_("dimitem { ',' dimitem }")
    def dimlist(self, p):
        return [p.dimitem0] + p.dimitem1

    #DIM items

    @_("ID '(' INTEGER ')'")
    def dimitem(self, p):
        return (p.ID, p.INTEGER, 0)
    
    @_("ID '(' INTEGER ',' INTEGER ')'")
    def dimitem(self, p):
        return (p.ID, p.INTEGER0, p.INTEGER1)
    
    # caso C$(n) = "string"
    @_("ID '(' INTEGER ')' '=' STRING")
    def command(self, p):
        return Let(Variable(p.ID, Number(p.INTEGER)), p.STRING)
    
    #ARITHMETHIC EXPRESSIONS

    @_("expr '+' expr",
       "expr '-' expr",
       "expr '*' expr",
       "expr '/' expr",
       "expr '^' expr")
    def expr(self, p):
        return Binary(p[1], p.expr0, p.expr1)
    
    @_("INTEGER", "FLOAT")
    def expr(self, p):
        # print(f"INTEGER o FLOAT: {p[0]}")
        # print(f"p: {p}")
        # print(f"p[0]: {p[0]}")
        return Number(p[0])
    


    
    # @_("BTLIN '(' expr ')'")
    # def expr(self, p):
    #     return Bltin(p.BLTIN, p.expr)
    
    
    # @_("BLTIN '(' expr ')'")
    # def expr(self, p):
    #     return Bltin(p.BLTIN, p.expr)
    
    
    @_("BLTIN '(' [ exprlist ]  ')'")
    def expr(self, p):
        return Bltin(p.BLTIN, p.exprlist)
    
    #caso BTLIN con string 
    @_("BLTIN '(' STRING ')'")
    def expr(self, p):
        return Bltin(p.BLTIN, String(p.STRING))
    
    @_("expr")  
    def exprlist(self, p):
        return [p.expr]
    
    @_("exprlist ',' expr")  
    def exprlist(self, p):
        return p.exprlist + [p.expr]

    # @_("BLTIN '(' [ expr ] ')'")#type:ignore
    # def expr(self, p):
    #     return Bltinfn(p.BLTIN, p.expr)
    
    @_("'(' expr ')'")
    def expr(self, p):
        return p.expr
    
    @_("'-' expr %prec UMINUS")
    def expr(self, p):
        return Unary(p[0], p.expr)
    

    @_("variable")#type:ignore
    def expr(self, p):
        return p.variable
    
    @_("expr LT expr",
         "expr LE expr",
         "expr = expr",
         "expr NE expr",
         "expr GE expr",
         "expr GT expr")
    def relexpr(self, p):
        return Binary(p[1], p.expr0, p.expr1)
    
    @_("STRING LT STRING",
         "STRING LE STRING",
         "STRING = STRING",
         "STRING NE STRING",
         "STRING GE STRING",
         "STRING GT STRING")
    def relexpr(self, p):
        print(f"Operación completa: {p.STRING0} {p[1]} {p.STRING1}")
        return Binary(p[1], String(p.STRING0), String(p.STRING1))
    

    #variables

    @_("ID")
    def variable(self, p):
        return Variable(p.ID)
    
    @_("ID '(' expr ')'")
    def variable(self, p):
        return Variable(p.ID, p.expr)
    
    @_("ID '(' expr ',' expr ')'")
    def variable(self, p):
        return Variable(p.ID, p.expr0, p.expr1)
    
    #builds a list of variable targets as a python list

    @_("variable { ',' variable }")
    def varlist(self, p):
        return [p.variable0] + p.variable1
    
    #builds a list of numbers as a python list



    @_("INTEGER")#type:ignore
    def number(self, p):
        return Number(p.INTEGER)

    @_("FLOAT")#type:ignore
    def number(self, p):
        return Number(p.FLOAT)
    
    @_("STRING")
    def pitem(self, p):
        return String(p.STRING)
    
    @_("expr")
    def pitem(self, p):
        return p.expr
    
    @_("STRING expr")
    def pitem(self, p):
        return String(p.STRING, p.expr)
    

    
    #A number. May be an integeger or a float

    # @_("INTEGER", "FLOAT")
    # def number(self, p):
    #     return Number(p[0])
    
    @_("'-' INTEGER", "'-' FLOAT")
    def number(self, p):
        return Unary(p[0], Number(p[1]))
    
    #List of targets for a print statement
    #Returns a lsit of tuples (label, expr)

    @_("plist ',' pitem ")# type: ignore
    def plist(self, p):
        return p.plist + [p.pitem]

    @_("pitem") # type: ignore
    def plist(self, p):
        return [p.pitem]
    #Empty

    @_("")
    def empty(self, p):
        pass

    def error(self, p):
        lineno = p.lineno if p else 'EOF'
        value  = p.value if p else 'EOF'
        if self.context: 
            self.context.error(lineno, f"Error de sintaxis en {value}")
        else:
            print(f"Linea {lineno}: Error de sintaxis en {value}")

    def __init__(self, context = None):
        self.context = context

def parse(txt):
    l = Lexer()
    p = Parser()

    try: 
        ast = p.parse(l.tokenize(txt))
        print("tokens: ", l.tokenize(txt))
        for token in l.tokenize(txt):
            #Si el token es NEWLINE
            if token.type == 'NEWLINE':
                print("\n")
            print(token)
        print("\n\nAST:")
        print(ast)
        
        # print("\n\nDOT:")
        # dot = DotRender().render(ast)
        # print(dot)
    except SyntaxError as e:
        print(e)
        

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python basparse.py filename")
        exit(1)

    parse(open(sys.argv[1]).read())

