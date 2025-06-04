from dataclasses import dataclass
from multimethod import multimeta
from typing import List, Dict

#---------------------visitor pattern---------------------------------------------------------------#

class Visitor(metaclass=multimeta):
    # def visit(self, node, *args, **kwargs):
    #     meth = self.multimethod(node.__class__)
    #     return meth(self, node, *args, **kwargs)
    pass

@dataclass
class Node:
    def accept(self, v:Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)

@dataclass
class Statement(Node):
    # def accept(self, v:Visitor, *args, **kwargs):
    #     return v.visit(self, *args, **kwargs)
    pass

@dataclass
class Expression(Node):
    # def accept(self, v:Visitor, *args, **kwargs):
    #     return v.visit(self, *args, **kwargs)
    pass

#---------------------------------------------------------------------------------------------------#

@dataclass
class Program(Statement):
    lines: Dict[int, Statement]

    def __setitem__(self, key, value):
        self.lines[key] = value

@dataclass
class Command(Statement):
    lineno: int
    comand: Statement

@dataclass
class Let(Statement):
    var: Expression
    expr: Expression

@dataclass
class Read(Statement):
    vlist: List[Expression]

@dataclass
class Data(Statement):
    nlist: List[Expression]
 
@dataclass
class Print(Statement):
    plist: List[Expression]
    optend: str = None

@dataclass
class Input(Statement):
    string: str
    varlist: List[Expression]

@dataclass
class Goto(Statement):
    lineno: Expression

@dataclass
class IfStmt(Statement):
    relexpr: Expression
    lineno: Expression

@dataclass
class ForStmt(Statement):
    var: Expression
    low: Expression
    top: Expression
    step: Expression = None

@dataclass
class Next(Statement):
    var: Expression

@dataclass
class Remark(Statement):
    rem: str

@dataclass
class End(Statement):
    txt : str = 'End'

@dataclass
class Stop(Statement):
    pass

@dataclass
class Function(Statement):
    func: str
    param: Expression
    expr: Expression

@dataclass
class Gosub(Statement):
    lineno: Expression

@dataclass
class Return(Statement):
    expr: Expression = None

# @dataclass
# class Dim(Statement):
#     dimlist: Expression
@dataclass
class Dim(Statement):
    dimlist : List[Expression]

# --- Expression
@dataclass
class Bltin(Expression):
    name: str
    expr: list[Expression]

@dataclass
class Variable(Expression):
    name: str
    dim1 : Expression = None
    dim2 : Expression = None

@dataclass
class Unary(Expression):
    op: str
    expr: Expression

@dataclass
class Binary(Expression):
    op: str
    left: Expression
    right: Expression

class Logical(Binary):
    pass

@dataclass
class Literal(Expression):
    # value : int | float | str

    # def __str__(self):
    #     return str(self.value)
    pass

@dataclass
class Number(Literal):
    value : int | float

@dataclass
class String(Literal):
    value: str
    expr: Expression = None
    
@dataclass
class Array(Expression):
    name : str
    dim1 : Expression
    dim2 : Expression = None

@dataclass
class Restore(Statement):
    pass

@dataclass
class Def(Statement):
    fname : str
    ident : str
    expr  : Expression

@dataclass
class Group(Expression):
    expr : Expression
