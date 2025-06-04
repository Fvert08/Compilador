import sys
import math
import random

from typing import Dict, Union
from basast import *
from rich import print

class BasicExit(BaseException):
  pass

class BasicContinue(Exception):
  pass


def _is_truthy(value):
  if value is None:
    return False
  elif isinstance(value, bool):
    return value
  else:
    return True

class Interpreter(Visitor):
  # Inicializa el interprete. prog es un Node
  # que contiene mapeo (line,statement)
  def __init__(self, prog, verbose=False, sym=False, upper=False, array_base=False, stats=False,no_run=False,trace=False, numTabs=0):
    self.prog    = prog
    self.verbose = verbose
    self.sym =  sym
    self.upper = upper
    self.array_base = array_base
    self.stats = stats
    self.no_run = no_run
    self.trace = trace
    self.numTabs = numTabs

    self.functions = {           # Built-in function table
      'SIN': lambda x: math.sin(x),
      'COS': lambda x: math.cos(x),
      'TAN': lambda x: math.tan(x),
      'ATN': lambda x: math.atan(x),
      'EXP': lambda x: math.exp(x),
      'ABS': lambda x: abs(x),
      'LOG': lambda x: math.log(x),
      'SQR': lambda x: math.sqrt(x),
      'INT': lambda x: int(x),
      'RND': lambda x: random.random(),
      'TAB': lambda x: ' '*x,
      'LEFT': lambda x, y: x[:y],
      'MID': lambda x, y, z: x[y:y+z],
      'RIGHT': lambda x, y: x[-y:],
      'LEN': lambda x: len(x),
      'CHR': lambda x: chr(x)
    }

    self.vars = {}       # Aquí se almacenan las variables


  @classmethod
  def interpret(cls, prog:Dict[int, Statement], verbose=False, sym=False, upper=False,array_base=False, stats=False,no_run=False,trace=False, numTabs=0):
    basic = cls(prog, verbose, sym, upper, array_base, stats,no_run,trace, numTabs)

    try:
      basic.run()
    except BasicExit:
      pass
    
    if sym:
      basic.run(True)

  def error(self, message):
    # sys.stderr.write(message)
    print("\n\n[red]" + message + "\n\n")
    raise BasicExit()

  def _check_numeric_operands(self, instr, left, right):
    if isinstance(left,  Union[int,float]) and isinstance(right, Union[int,float]):
      return True
    else:
      self.error(f"{instr.op} OPERANDS MUST BE NUMBERS")

  def _check_numeric_operand(self, instr, value):
    if isinstance(value, Union[int,float]):
      return True
    else:
      self.error(f"{instr.op} operand must be a number")

  # print methods (view: Norvig)
  def print_string(self, s) -> None:
    '''
    Print a string, keeping track of column, 
    and advancing to newline if at or beyond
    column 80.
    '''
    if self.upper:  # Verificar si se debe imprimir en mayúsculas
      s = s.upper()
    print(s, end='')
    self.column += len(s)
    if self.column >= 80:
      self.newline()

    if self.trace:
      #imprime la linea de código que se está ejecutando, la linea la extrae del diccionario de instrucciones
      print(f"\n\n[yellow]Línea de código ejecutada[/yellow]\n")
      print(self.prog.lines[self.stat[self.pc]])

  def pad(self, width) -> None:
    '''
    Pad out to the column that is the next
    multiple of width
    '''
    while self.column % width != 0:
      self.print_string(' ')
  
  def newline(self):
    print(); self.column = 0

  # Collect all data statements
  def collect_data(self):
    self.data = []
    for lineno in self.stat:
      if isinstance(self.prog.lines[lineno], Data):
        self.data += self.prog.lines[lineno].nlist
    self.dc = 0 # Initialize the data counter

  # Check for end statements
  def check_end(self):
    has_end = False
    for lineno in self.stat:
      if isinstance(self.prog.lines[lineno], End) and not has_end:
        has_end = lineno
    if not has_end:
      self.error("NO END INSTRUCTION")
    elif has_end != lineno:
      self.error("END IS NOT LAST")

  # Check loops
  def check_loops(self):
    for pc in range(len(self.stat)):
      lineno = self.stat[pc]
      if isinstance(self.prog.lines[lineno], ForStmt):
        forinst = self.prog.lines[lineno]
        loopvar = forinst.var
        for i in range(pc + 1, len(self.stat)):
          if isinstance(self.prog.lines[self.stat[i]], Next):
            nextvar = self.prog.lines[self.stat[i]].var
            if nextvar != loopvar:
              continue
            self.loopend[pc] = i
            break
        else:
          self.error(f"FOR WITHOUT NEXT AT LINE {self.stat[pc]}")

  # Change the current line number
  def goto(self, lineno):
    #si lineno es int no le pasa el value
    lineNum = lineno.value if isinstance(lineno, Number) else lineno

    if not lineNum in self.stat:
      self.error(f"UNDEFINED LINE NUMBER {lineno} AT LINE {self.stat[self.pc]}")
    self.pc = self.stat.index(lineNum)


  # Run it
  def run(self, sym=False):
    print("\n\n[yellow]Ejecutando el programa[/yellow]\n")
    # self.vars   = {}       # All variables (the symbol table)
    self.lists  = {}       # List variables
    self.tables = {}       # Tables
    self.loops  = []       # Currently active loops
    self.loopend = {}      # Mapping saying where loops end
    self.gosub  = None     # Gosub return point (if any)
    self.column = 0        # Print coñumn control

    self.stat = list(self.prog.lines)
    self.stat.sort()
    self.pc = 0                  # Current program counter

    # Processing prior to running

    self.collect_data()          # Collect all of the data statements
    self.check_end()
    self.check_loops()


    while True:
      line  = self.stat[self.pc]
      instr = self.prog.lines[line]

      try:
        if self.no_run:
          if not instr.__class__.__name__ == "Print":
            instr.accept(self)
        else:
            instr.accept(self)
        if self.verbose:
          print(f"LINE {line}: {instr}")

      except BasicContinue as e:
        continue
        
      self.pc += 1
      # Print the symbol table  
      if sym:
          print("\n\n[yellow]Tabla de símbolos[/yellow]\n")
          print(self.vars)
        
  # --- Assignment

  def assign(self, target, value):
    var = target.name
    dim1 = target.dim1
    dim2 = target.dim2
    lineno = self.stat[self.pc]

    if not dim1 and not dim2:
      if isinstance(value, str):
        self.vars[var] = value
      else:
        self.vars[var] = value.accept(self)
    elif dim1 and not dim2:
      # List assignment
      x = dim1.accept(self)
      if not var in self.lists:
        self.lists[var] = [0] * 10
        print(self.lists)

      if x > len(self.lists[var]):
        self.error(f"DIMENSION TOO LARGE AT LINE {lineno}")
      if isinstance(value, str):
        self.lists[var][x - 1] = value
      else:
        self.lists[var][x - 1] = value.accept(self)
    
    elif dim1 and dim2:
      x = dim1.accept(self)
      y = dim2.accept(self)
      if not var in self.tables:
        temp = [0] * 10
        v = []
        for i in range(10):
          v.append(temp[:])
        self.tables[var] = v
      # Variable already exists
      if x > len(self.tables[var]) or y > len(self.tables[var][0]):
        self.error("DIMENSION TOO LARGE AT LINE {lineno}")
      self.tables[var][x - 1][y - 1] = value.accept(self)
  
  # --- Statement

  def visit(self, instr:Remark):
    pass

  def visit(self, instr:Restore):
    self.dc = 0

  def visit(self, instr:Let):
    var   = instr.var
    value = instr.expr
    self.assign(var, value)

  def visit(self, instr:Read):
    for target in instr.vlist:
      if self.dc >= len(self.data):
        # No more data.  Program ends
        raise BasicExit()
      value = self.data[self.dc]
      self.assign(target, value)
      self.dc += 1

  def visit(self, instr:Data):
    pass

  # TODO: variable type
  def visit(self, instr:Input):
    label = instr.string
    if label:
      sys.stdout.write(label)

    for variable in instr.varlist:
      print(f"input para [green]{variable.name}: ", end = '')
      value = input()
      if variable.name[-1] == '$':
        value = String(value)
      else:
        try:
          value = Number(int(value))
        except ValueError:
          try: 
            value = Number(float(value))
          except ValueError:
            #mostrar por consola al usuario que hay un error y que debe de ingresar un valor numerico
            self.error(f"ERROR: Debe de ingresar un valor numerico para la variable [green]{variable.name}")        
      self.assign(variable, value)
      
  # TODO: %.8g for numeric data. etc
  def visit(self, instr:Print):
    items = instr.plist
    for pitem in items:
      if not pitem: continue
      if isinstance(pitem, Node):
        pitem = pitem.accept(self)
      if pitem == ',':   self.pad(100)
      elif pitem == ';': self.pad(0)
      elif isinstance(pitem, str):
        self.print_string(pitem)
      else:
        self.print_string(f'{pitem:g}')
    if instr.optend == ',':
      if self.numTabs != 0:
        self.pad(self.numTabs)
      else:
        self.pad(3)
    elif instr.optend == ';':
      #no hace salto de linea ni tabulación
      pass
    else:
      self.newline()
    
  def visit(self, instr:Goto):
    newline = instr.lineno
    self.goto(newline)
    raise BasicContinue()

  def visit(self, instr:IfStmt):
    relexpr = instr.relexpr
    newline = instr.lineno
    if _is_truthy(relexpr.accept(self)):
       # si después del if hay una instrucción next, se hace self.pc = self.loops[-2][0] para que se ejecute el next
      # if self.prog.lines[self.stat[self.pc + 1]].__class__.__name__ == "Next":
      #   # print(f"Next: {self.prog.lines[self.stat[self.pc + 1]].__class__.__name__}")
      #   #guarda una bandera para saber si se ejecutó un if antes del next
      #   #si la condición del if es verdadera, se ejecuta el next
      #   self.if_next = True
      self.goto(newline)
      raise BasicContinue()
    # else:
    #   self.if_next = False

  def visit(self, instr:ForStmt):
    loopvar = instr.var
    initval = instr.low
    finval  = instr.top
    stepval = instr.step

    # Check to see if this is a new loop
    if not self.loops or self.loops[-1][0] != self.pc:
      # Looks like a new loop. Make the initial assignment
      newvalue = initval
      self.assign(loopvar, initval)
      if not stepval:
        stepval = Number(1)
      stepval = stepval.accept(self)    # Evaluate step here
      self.loops.append((self.pc, stepval))
    else:
      # print("en el else")
      # It's a repeat of the previous loop
      # Update the value of the loop variable according to the
      # step
      stepval = Number(self.loops[-1][1])
      newvalue = Binary('+', loopvar, stepval)

      relop = '>=' if self.loops[-1][1] < 0 else '<='
      if not _is_truthy(Logical(relop, newvalue, finval).accept(self)):
        # Loop is done. Jump to the NEXT
        self.pc = self.loopend[self.pc]
        self.loops.pop()
      else:
        self.assign(loopvar, newvalue)
          
  def visit(self, instr:Next):
    lineno = self.stat[self.pc]

    # print(f"Next: {lineno}")
    # print(f"Loops: {self.loops}")
    # print(f"PC: {self.pc}")
    # print(f"Loopend: {self.loopend}")
    # print(f"Stat: {self.stat}")
    # print(instr.var)
    # print(self.prog.lines[self.stat[self.pc]])
    # print(self.loops[-2][0])
    # print(f"Programa: {self.prog.lines}")
    # print(f"xd:{self.prog.lines[self.stat[self.pc - 1]].__class__.__name__}")

    if not self.loops:
      print(f"NEXT WITHOUT FOR AT LINE {lineno}")
      return
    nextvar = instr.var
    # si antes del next hay un if, se hace self.pc = self.loops[-2][0] para que se ejecute el if
    # if self.prog.lines[self.stat[self.pc - 1]].__class__.__name__ == "IfStmt":
    #   self.pc = self.loops[-2][0]
    # else:
    #si self.if_next es True, se ejecutó un if antes del next, por lo que se hace self.pc = self.loops[-2][0] para que se ejecute el next
    # if self.if_next:
    #   self.if_next = False
    #   self.pc = self.loops[-1][0]
    # else:
    self.pc = self.loops[-1][0]
    loopinst = self.prog.lines[self.stat[self.pc]]
    forvar = loopinst.var

    # print(f"Nextvar: {nextvar}")
    # print(f"Forvar: {forvar}")

    if nextvar != forvar:
      print(f"NEXT DOESN'T MATCH FOR AT LINE {lineno}")
      return
    raise BasicContinue()

  def visit(self, instr:Union[End, Stop]):
    raise BasicExit()
  
  def visit(self, instr:Number):
    return instr.value

  def visit(self, instr:Def):
    fname = instr.fname
    pname = instr.ident
    expr  = instr.expr

    def eval_func(pvalue, name=pname, self=self, expr=expr):
      self.assign(pname, pvalue)
      return expr.accept(self)

    self.functions[fname] = eval_func

  def visit(self, instr:Gosub):
    newline = instr.lineno
    lineno  = self.stat[self.pc]
    if self.gosub:
      print(f"ALREADY IN A SUBROUTINE AT LINE {lineno}")
      return
    self.gosub = self.stat[self.pc]
    self.goto(newline)
    raise BasicContinue()

  def visit(self, instr:Return):
    lineno = self.stat[self.pc]
    if not self.gosub:
      print(f"RETURN WITHOUT A GOSUB AT LINE {lineno}")
      return
    self.goto(self.gosub)
    self.gosub = None

  def visit(self, instr:Dim):
      for dimitem in instr.dimlist:
        vname = instr.dimlist[0][0]
        dim1 = instr.dimlist[0][1]
        dim2 = instr.dimlist[0][2]
        if not dim2:
          # Single dimension variable
          x = dim1
          self.lists[vname] = [0] * x
        else:
          # Double dimension variable
          x = dim1
          y = dim2
          temp = [0] * y
          v = []
          for i in range(x):
            v.append(temp[:])
          self.tables[vname] = v
  # def visit(self, instr:Dim):
  #   dimitem = instr.dimlist
  #   for dimitem in instr.dimlist:
  #     vname = dimitem.name
  #     dim1 = dimitem.dim1
  #     dim2 = dimitem.dim2
  #     if not dim2:
  #       # Single dimension variable
  #       x = dim1.accept(self)
  #       if self.array_base:
  #         self.lists[vname] = [0] * (x + 1)  # Comienza en 1
  #       else:
  #         self.lists[vname] = [0] * x  # Comienza en 0
  #     else:
  #       # Double dimension variable
  #       x = dim1.accept(self)
  #       y = dim2.accept(self)
  #       if self.array_base:
  #         temp = [0] * (y + 1)
  #         v = []
  #         for i in range(x + 1):
  #           v.append(temp[:])
  #         self.tables[vname] = v
  #       else:
  #         temp = [0] * y
  #         v = []
  #         for i in range(x):
  #           v.append(temp[:])
  #         self.tables[vname] = v

# --- Expression
  def visit(self, instr:String):
    return instr.value

  def visit(self, instr:Group):
    return instr.expr.accept(self)

  def visit(self, instr:Bltin):
    name = instr.name
    if isinstance(instr.expr, list):
      expr = [expr.accept(self) for expr in instr.expr]
      return self.functions[name](*expr)
    else:
      if isinstance(instr.expr, str):
        return self.functions[name](instr.expr)
      else:
        return self.functions[name](instr.expr.accept(self))
      

  # def visit(self, instr:Call):
  #   name = instr.fname
  #   expr = instr.expr
  #   return self.functions[name](expr)

  def visit(self, instr:Variable):
    var, dim1, dim2 = instr.name, instr.dim1, instr.dim2
    lineno = self.stat[self.pc]
    if not dim1 and not dim2:
      if var in self.vars:
        return self.vars[var]
      else:
        self.error(f"UNDEFINED VARIABLE '{var}' AT LINE {lineno}")
  
    # A list evaluation
    if var in self.lists:
      x = dim1.accept(self)
      if x < 1 or x > len(self.lists[var]):
        self.error(f'LIST INDEX OUT OF BOUNDS AT LINE {lineno}')
      return self.lists[var][x - 1]
      
    if dim1 and dim2:
      if var in self.tables:
        x = dim1.accept(self)
        y = dim2.accept(self)
        # print(dim1)
        # print(dim2)
        # print(f"X: {x}")
        # print(f"Y: {y}")
        if self.array_base:
          num = 0
        else:
          num = 1
        if x < num or x > len(self.tables[var]) or y < num or y > len(self.tables[var][0]):
          self.error(f'TABLE INDEX OUT OUT BOUNDS AT LINE {lineno}')
        return self.tables[var][x - 1][y - 1]

    self.error(f'UNDEFINED VARIABLE {var} AT LINE {lineno}')

  def visit(self, instr:Union[Binary,Logical]):
    if isinstance(instr.left, str):
      left = instr.left
    else:
      left = instr.left.accept(self)
    if isinstance(instr.right, str):
        right = instr.right
    else:
        right = instr.right.accept(self)
    if instr.op == '+':
      (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(instr, left, right)
      return left + right
    elif instr.op == '-':
      self._check_numeric_operands(instr, left, right)
      return left - right
    elif instr.op == '*':
      self._check_numeric_operands(instr, left, right)            
      return left * right
    elif instr.op == '/':
      self._check_numeric_operands(instr, left, right)            
      return left / right
    elif instr.op == '^':
      self._check_numeric_operands(instr, left, right)            
      return math.pow(left, right)
    elif instr.op == '=':
      return left == right
    elif instr.op == '<>':
      return left != right
    elif instr.op == '<':
      self._check_numeric_operands(instr, left, right)            
      return left < right
    elif instr.op == '>':
      self._check_numeric_operands(instr, left, right)            
      return left > right
    elif instr.op == '<=':
      self._check_numeric_operands(instr, left, right)            
      return left <= right
    elif instr.op == '>=':
      self._check_numeric_operands(instr, left, right)            
      return left >= right
    else:
      self.error(f"BAD OPERATOR {instr.op}")
  
  def visit(self, instr:Unary):
    value = instr.expr.accept(self)
    if instr.op == '-':
      self._check_numeric_operand(instr, value)
      return - value

  def visit(self, instr:Literal):
    return instr.value
  
  def visit(self, instr:Node):
    lineno = self.stat[self.pc]
    print(lineno, instr.__class__.__name__)

  #------------------------------------

  def stats(self):
    return f"Programa ejecutado con éxito\n"
  


  



    