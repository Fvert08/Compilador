# basrender.py
from graphviz import Digraph
from typing import Union
from AST import *

class DotRender(Visitor):
    print("\n--DotRender--\n")
    node_default = {
        'shape' : 'box',
        'color' : 'silver',
        'style' : 'filled',
    }
    edge_defaults = {
        'arrowhead' : 'none',
    }
    color = 'forestgreen'

    def __init__(self):
        self.dot = Digraph('AST')
        self.dot.attr('node', **self.node_default)
        self.dot.attr('edge', **self.edge_defaults)
        self.program = False
        self.seq = 0

    def __repr__(self):
        return self.dot.source
    
    def __str__(self):
        return self.dot.source
    
    @classmethod
    def render(cls, model):
        dot = cls()
        model.accept(dot)
        return dot.dot
    
    def name(self):
        self.seq += 1
        return f'node{self.seq:02d}'
    
    #Statements

    def visit(self, n:Program):
        print("Visité Program")
        name = self.name()
        self.dot.node(name, label='Program')
        for lineno, stmt in n.lines.items():
            self.dot.edge(name, stmt.accept(self, lineno))
        return name

    
    def visit(self, n:Command):
        print("Visité Command")
        name = self.name()
        self.dot.node(name, label=f'command\n{n.lineno}')
        print(f'Numero de linea analizada {n.lineno}')
        self.dot.edge(name, n.comand.accept(self,n.lineno))
        return name
    
    def visit(self, n:Remark,lineno):
        print("Visité Remark")
        name = self.name()
        self.dot.node(name, label=f'{lineno} REM')
        self.dot.edge(name, n.rem)
        return name
    
    def visit(self, n:Print, lineno):
        print("Visité Print")
        name = self.name()
        self.dot.node(name, label=f'{lineno} PRINT')
        for pitem in n.plist:
            self.dot.edge(name, pitem.accept(self))
        return name
    
    def visit(self, n:ForStmt, lineno):
        print("Visité ForStmt")
        name = self.name()
        self.dot.node(name, label=f'{lineno} FOR')
        print('despues de node')
        self.dot.edge(name, n.var.accept(self))
        print('despues de var')
        self.dot.edge(name, n.low.accept(self))
        self.dot.edge(name, n.top.accept(self))
        if n.step:
            self.dot.edge(name, n.step.accept(self))
        return name
    
    def visit(self, n:IfStmt, lineno):
        print("Visité IfStmt")
        name = self.name()
        self.dot.node(name, label=f'{lineno} IF')
        self.dot.edge(name, n.relexpr.accept(self))
        self.dot.edge(name, n.lineno.accept(self))
        return name
    
    def visit(self, n:Let, lineno):
        print("Visité Let")
        name = self.name()
        self.dot.node(name, label=f'{lineno} LET')
        if isinstance(n.var, str):
            self.dot.edge(name, n.var)
        else:
            self.dot.edge(name, n.var.accept(self))
        if isinstance(n.expr, str):
            self.dot.edge(name, n.expr)
        else:
            self.dot.edge(name, n.expr.accept(self))

        # self.dot.edge(name, n.var.accept(self))
        # self.dot.edge(name, n.expr.accept(self))
        return name
    
    def visit(self, n:Next, lineno):
        print("Visité Next")
        name = self.name()
        self.dot.node(name, label=f'{lineno} NEXT')
        self.dot.edge(name, n.var.accept(self))
        return name
    
    def visit(self, n:End,lineno):
        print("Visite End")
        name = self.name()
        self.dot.node(name, label='END')
        return name
    
    def visit(self, n:Goto, lineno):
        print("Visité Goto")
        name = self.name()
        self.dot.node(name, label=f'{lineno} GOTO')
        self.dot.edge(name, n.lineno.accept(self))
        return name
    
    def visit(self, n:Read, lineno):
        print("Visité Read")
        name = self.name()
        self.dot.node(name, label=f'{lineno} READ')
        for var in n.vlist:
            self.dot.edge(name, var.accept(self))
        return name 
    
    def visit(self, n:Data, lineno):
        print("Visité Data")
        name = self.name()
        self.dot.node(name, label=f'{lineno} DATA')
        for num in n.nlist:
            self.dot.edge(name, num.accept(self))
        return name
    
    #Expressions

    def visit(self, n:Binary):
        print("Visité Binary")
        name = self.name()
        self.dot.node(name, label=f'{n.op}', shape='circle', color=self.color)
        #si se recivbe un string, se debe de hacer un edge a la expresion
        if isinstance(n.left, str):
            self.dot.edge(name, n.left)
        else:
            self.dot.edge(name, n.left.accept(self))
        if isinstance(n.right, str):
            self.dot.edge(name, n.right)
        else:
            self.dot.edge(name, n.right.accept(self))
        # self.dot.edge(name, n.left.accept(self))
        # self.dot.edge(name, n.right.accept(self))
        # self.dot.edge(name, n.left)
        # self.dot.edge(name, n.right)
        return name
    
    def visit(self, n:Unary):
        print("Visité Unary")
        name = self.name()
        self.dot.node(name, label=f'{n.op}', shape='circle', color=self.color)
        self.dot.edge(name, n.expr.accept(self))
        return name
    
    #Funciones con palabras reservadas. (SIN, COS, TAN, ATN, EXP, ABS, LOG, SQR, RND, INT)
    def visit(self, n:Bltin):
        print("Visité Bltin")
        name = self.name()
        self.dot.node(name, label=f'{n.name}')
        self.dot.edge(name, n.expr.accept(self))
        return name
    
    def visit(self, n:Variable):
        print("Visité Variable")
        name = self.name()  
        self.dot.node(name, label=f'{n.name}')
        return name

    def visit(self, n:Number):
        print("Visité Number")
        name = self.name()
        self.dot.node(name, label=f'{n.value}')
        return name
    
    def visit(self, n:String):
        print("Visité String")
        name = self.name()
        self.dot.node(name, label=f'String\nvalue: {n.value}')
        if n.expr:
            self.dot.edge(name, n.expr, label='expr')
        return name
    

    #Statement nos permite determinar el error del nodo que nos hace falta
    def visit(self, n:Statement, lineno):
        name = self.name()
        print(f'{lineno} {n.__class__.__name__}')
        return name
    
    #Nodo que nos hace falta. 
    def visit(self, n:Expression):
        name = self.name()
        print(f'{n.__class__.__name__}')
        return name
    