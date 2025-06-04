import sys 
from baslex import Lexer
from basparse import Parser
from basast import *
from interp import Interpreter
from rich import print


'''
True
False
'''
debugMode = True

class Visitor: 
    def visit(self, node, *args, **kwargs):
        methodName = 'visit_' + node.__class__.__name__
        visitor = getattr(self, methodName, self.undefinedVisitor)
        return visitor(node, *args, **kwargs)

    def undefinedVisitor(self, node, *args, **kwargs):
        print(f'\n[red]-- No existe método visit para: [green]{node.__class__.__name__}[red] -- \n')
        raise Exception(f'No existe el método: visit_{node.__class__.__name__}')

class CodeGenerator(Visitor):
    def __init__(self):
        self.code = []
        self.loop_stack = []  # Stack to handle nested loops
        self.program = []
        self.lineNoRun = [] #lista de lineas que no ejecutaran por el if

    # Este método NO es llamado por algún otro método.
    def visit_Program(self, node: Program ,specificLine=None):
        if specificLine:
            debugMode and print("\n[green]Visité Program con la línea específica:", specificLine)
            self.visit(node[specificLine.value])
            self.lineNoRun.append(specificLine.value)

        else:
            debugMode and print("[green]\n      EMPIEZA EL PROGRAMA\n")
            self.program = node.lines
            for line in node.lines:
                if line in self.lineNoRun:
                    self.code.append(('ENDIF',))
                    continue
                debugMode and print("\n[purple]--Analizando instrucción:", node.lines[line])
                self.visit(node.lines[line])
                
    # Este método NO es llamado por algún otro método.
    def visit_Let(self, node: Let):
        debugMode and print("\n[green]Visité Let")
        self.visit(node.expr)
        self.code.append(('GLOBAL_SET', node.var.name))

    # Este método puede ser llamado en: visit_Let
    def visit_Binary(self, node: Binary):
        debugMode and print("\n[green]Visité Binary")
        self.visit(node.left)
        self.visit(node.right)
        if node.op == '+':
            self.code.append(('ADDI',))
        elif node.op == '-':
            self.code.append(('SUBI',))
        elif node.op == '*':
            self.code.append(('MULI',))
        elif node.op == '/':
            self.code.append(('DIVI',))
        elif node.op == '^':
            self.code.append(('POWI',))
        elif node.op == '<':
            self.code.append(('LTI',))
        elif node.op == '>':
            self.code.append(('GTI',))
        elif node.op == '<=':
            self.code.append(('LTEI',))
        elif node.op == '>=':
            self.code.append(('GTEI',))
        elif node.op == '<>':
            self.code.append(('NEI',))
        elif node.op == '=':
            self.code.append(('EQI',))
        else:
            print(f'[red]Operador desconocido: {node.op}')
            raise Exception(f'Operador desconocido: {node.op}')

    def visit_Remark(self, node: Remark):
        debugMode and print("\n[green]Visité Remark")
        pass

    # Este método puede ser llamado en: visit_Binary, visit_Variable, visit_Let
    def visit_Number(self, node: Number):
        debugMode and print("\n[green]Visité Number")
        if isinstance(node.value, int):
            self.code.append(('CONSTI', node.value))
        else:
            self.code.append(('CONSTF', node.value))

    def visit_String(self, node: String):
        debugMode and print("\n[green]Visité String")
        if isinstance(node.value, str):
            self.code.append(('CONSTI', node.value))
        else:
            self.code.append(('CONSTF', node.value))

    def visit_str(self, node: String):
        debugMode and print("\n[green]Visité String")
        if isinstance(node, str):
            self.code.append(('CONSTI', node))
        else:
            self.code.append(('CONSTF', node))

    def visit_ForStmt(self, node: ForStmt):
        debugMode and print("\n[green]Visité ForStmt")
        self.visit(node.low)
        self.visit_VariableSet(node.var)
        self.code.append(('LOOP',))
        self.visit(node.var)
        self.visit(node.top)
        if node.step:
            self.visit(node.step)
        self.code.append(('LTI',))
        self.code.append(('CBREAK',))

    def visit_IfStmt(self, node: IfStmt):
        debugMode and print("\n[green]Visité IfStmt")
        self.visit(node.relexpr)
        self.code.append(('IF',))
        self.visit_Program(self.program, node.lineno)
        self.code.append(('ELSE',))

    def visit_Goto(self, node: Goto):
        debugMode and print("\n[green]Visité Goto")
        self.code.append(('GOTO', node.lineno.value))

    def visit_Unary(self, node: Unary):
        debugMode and print("\n[green]Visité Unary")
        self.visit(node.expr)
        self.code.append(('NEG',))

    def visit_Input(self, node: Input):
        debugMode and print("\n[green]Visité Input")
        #espera que el usuario ingrese un valor
        print("Ingrese un valor:")
        value = input()
        if '.' in value:
            self.code.append(('CONSTF', float(value)))
        else:
            self.code.append(('CONSTI', int(value)))
        self.code.append(('GLOBAL_SET', node.varlist[0].name))

    # def visit_Next(self, node: Next):
    #     debugMode and print("\n[green]Visité Next")
    #     # self.visit(node.var)
    #     #se le suma 1 a la variable
    #     self.code.append(('CONSTI', 1))
    #     self.code.append(('ADDI',))
    #     self.visit_VariableSet(node.var)
    #     self.code.append(('CONTINUE',))
    #     self.code.append(('ENDLOOP',))


    # Este método NO es llamado por algún otro método. 
    def visit_Print(self, node: Print):
        debugMode and print("\n[green]Visité print")
        for item in node.plist:
            self.visit(item)
            if isinstance(item, Number):
                if isinstance(item.value, int):
                    self.code.append(('PRINTI',))
                else:
                    self.code.append(('PRINTF',))
            elif isinstance(item, String):
                self.code.append(('PRINTI',))
            elif isinstance(item, Variable):
                self.code.append(('PRINTI',))
            elif isinstance(item, Binary):
                self.code.append(('PRINTI',))
                
    def visit_list(self, node: list):
        debugMode and print("\n[green]Visité list")
        for item in node:
            self.visit(item)

    # Este método puede ser llamado en: visit_Print, visit_Let, visit_Binary
    def visit_Variable(self, node: Variable):
        debugMode and print("\n[green]Visité Variable")
        self.code.append(('GLOBAL_GET', node.name))

    def visit_VariableSet(self, node: Variable):
        debugMode and print("\n[green]Visité VariableSet")
        self.code.append(('GLOBAL_SET', node.name))

    def visit_ForStmt(self, node: ForStmt):
        debugMode and print("\n[green]Visité ForStmt")
        # Initialize the loop variable
        self.visit(node.low)
        self.code.append(('GLOBAL_SET', node.var.name))
        # Record the start of the loop
        loop_start = len(self.code)
        self.code.append(('LOOP',))
        self.loop_stack.append((loop_start, node))

    def visit_Next(self, node: Next):
        debugMode and print("\n[green]Visité Next")
        # print("Next", node.var.name)
        # print("Next", self.loop_stack)
        #busca en loop_stack el loop que corresponde a la variable
        for loop_start, for_node in reversed(self.loop_stack):
            if for_node.var.name == node.var.name:
                break
        else:
            raise Exception(f'No se encontró el bucle para la variable {node.var.name}')
        # Increment the loop variable by the step value
        self.code.append(('GLOBAL_GET', for_node.var.name))
        if for_node.step:
            self.visit(for_node.step)
        else:
            self.code.append(('CONSTI', 1))  # Default step is 1
        self.code.append(('ADDI',))
        # print("Next", for_node.var.name)
        self.code.append(('GLOBAL_SET', for_node.var.name))
        # Check if the loop variable is within the bounds
        self.code.append(('GLOBAL_GET', for_node.var.name))
        self.visit(for_node.top)
        self.code.append(('GTI',))
        self.code.append(('CBREAK',))
        self.code.append(('CONTINUE',))
        self.code.append(('ENDLOOP',))
        self.loop_stack.append((loop_start, for_node))

    def visit_Data(self, node: Data):
        debugMode and print("\n[green]Visité Data")
        dataCount = len(node.nlist)
        #hace un ciclo para recorrer la lista de datos desde dataCount-1 hasta 0
        for i in range(dataCount-1, -1, -1):
            self.visit(node.nlist[i])

    def visit_Read(self, node: Read):
        debugMode and print("\n[green]Visité Read")
        #en este nodo , cambia Variable por VariableSet
        #ej de nodo:Read(vlist=[Variable(name='N0', dim1=None, dim2=None), Variable(name='P0', dim1=None, dim2=None)])
        for item in node.vlist:
            self.visit_VariableSet(item)

    def visit_End(self, node: End):
        debugMode and print("\n[green]Visité End")
        self.code.append(('END',))

def main():
    if len(sys.argv) != 2:
        print('\n[red]ERROR\n[green]uso: basIntermediateCode.py basicCode.bas\n')
        sys.exit(1)
    
    lexer = Lexer()
    parser = Parser()
    interp = Interpreter()
    visitor = CodeGenerator()

    text = open(sys.argv[1]).read()

    tokens = lexer.tokenize(text)
    ast = parser.parse(tokens)
    visitor.visit(ast)
    print("[yellow]\n\nCódigo Intermedio:\n")
    print(visitor.code)
    print("\n[yellow]Fin del código intermedio\n")
    
    name = "main"
    interp.add_function(name, [], visitor.code)
    interp.execute(name)

if __name__ == '__main__':
    main()
