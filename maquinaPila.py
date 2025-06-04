def run_END(self):
    self.pc = len(self.code)  # Set the program counter to the end of the code, terminating the execution

# Add this function to the Interpreter class

import struct

class Interpreter:
    '''
    Ejecuta un intérprete del código intermedio generado para su compilador. 
    La idea de implementación es la siguiente. Dada una secuencia de tuplas 
    de instrucciones como:

       code = [
          ('CONSTI', 1),
          ('CONSTI', 2),
          ('ADDI',),
          ('PRINTI',)
          ...
       ]
   
    La clase ejecuta métodos self.run_opcode(args). Por ejemplo:

       self.run_CONSTI(1)
       self.run_CONSTI(2)
       self.run_ADDI()
       self.run_PRINTI()

    Sólo un recordatorio de que el código intermedio se basa en una máquina de pila.
    El intérprete necesita implementar la pila y la memoria para almacenar variables.
    '''
    def __init__(self):
        self.code = []
        self.pc = 0

        # Almacenamiento de variables
        self.globals = { }
        self.vars = { }

        # Pila frame stack
        self.frames = [ ]

        # La pila de operaciones
        self.stack = [ ]

        # Memoria
        self.memory = bytearray()

        # Rotulos flujo-control
        self.control = { }

        # Tabla de funciones
        self.functions = { }

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def add_function(self, name: str, argnames: list, code: list[tuple]):
        # muestra etiquetas de flujo de control
        control = { }
        levels = []
        for n, (inst, *args) in enumerate(code):
            if inst == 'IF':
                levels.append(n)
            elif inst == 'ELSE':
                control[levels[-1]] = n
                levels[-1] = n
            elif inst == 'ENDIF':
                control[levels[-1]] = n
                levels.pop()
            if inst == 'LOOP':
                levels.append(n)
            elif inst == 'CBREAK':
                levels.append(n)
            elif inst == 'ENDLOOP':
                control[n] = levels[-2]
                control[levels[-1]] = n
                levels.pop()
                levels.pop()
        self.functions[name] = (code, argnames, control)

    def execute(self, name:str):
        self.frames.append((self.code, self.pc, self.control, self.vars))
        self.code, argnames, self.control = self.functions[name]
        self.vars = { }

        # 
        for argname in argnames[::-1]:
            value = self.pop()
            self.vars[argname] = value

        self.pc = 0
        while self.pc < len(self.code):
            inst, *args = self.code[self.pc]
            getattr(self, f'run_{inst}')(*args)
            self.pc += 1
        self.code, self.pc, self.control, self.vars = self.frames.pop()

    # Interpreter opcodes
    def run_CONSTI(self, value):
        # print("CONSTI", value)
        self.push(value)
    run_CONSTF = run_CONSTI

    def run_ADDI(self):
        # print("ADDI")
        #si alguno de los dos operandos es string, concatena
        if type(self.stack[-1]) == str or type(self.stack[-2]) == str:
            self.push(str(self.pop()) + str(self.pop()))
        else:
            self.push(self.pop() + self.pop())
    run_ADDF = run_ADDI

    def run_SUBI(self):
        # print("SUBI")
        right = self.pop()
        left = self.pop()
        self.push(left-right)
    run_SUBF = run_SUBI

    def run_MULI(self):
        # print("MULI")
        self.push(self.pop() * self.pop())
    run_MULF = run_MULI

    def run_POWI(self):
        # print("POWI")
        right = self.pop()
        left = self.pop()
        self.push(left ** right)

    def run_DIVI(self):
        # print("DIVI")
        right = self.pop()
        left = self.pop()
        self.push(left // right)

    def run_DIVF(self):
        # print("DIVF")
        right = self.pop()
        left = self.pop()
        self.push(left / right)

    def run_ITOF(self):
        self.push(float(self.pop()))

    def run_FTOI(self):
        # print("FTOI")
        self.push(int(self.pop()))

    def run_PRINTI(self):
        # print("PRINTI", end=" ")
        print(self.pop())
    run_PRINTF = run_PRINTI

    def run_PRINTB(self):
        # print("PRINTB", end=" ")
        print(chr(self.pop()),end='')

    def run_LOCAL_GET(self, name):
        # print("LOCAL_GET", name)
        self.push(self.vars[name])

    def run_GLOBAL_GET(self, name):
        # print("GLOBAL_GET", name)
        self.push(self.globals[name])

    def run_LOCAL_SET(self, name):
        # print("LOCAL_SET", name)
        self.vars[name] = self.pop()

    def run_GLOBAL_SET(self, name):
        # print("GLOBAL_SET", name)
        self.globals[name] = self.pop()

    def run_LEI(self):
        # print("LEI")
        right = self.pop()
        left = self.pop()
        self.push(int(left <= right))

    run_LEF = run_LEI

    def run_LTI(self):
        # print("LTI")
        right = self.pop()
        left = self.pop()
        self.push(int(left < right))

    run_LTF = run_LTI

    def run_GEI(self):
        # print("GEI")
        right = self.pop()
        left = self.pop()
        self.push(int(left >= right))

    run_GEF = run_GEI

    def run_GTI(self):
        # print("GTI")
        right = self.pop()
        left = self.pop()
        self.push(int(left > right))

    run_GTF = run_GTI

    def run_EQI(self):
        # print("EQI")
        right = self.pop()
        left = self.pop()
        self.push(int(left == right))

    run_EQF = run_EQI

    def run_NEI(self):
        # print("NEI")
        right = self.pop()
        left = self.pop()
        self.push(int(left != right))

    run_NEF = run_NEI

    def run_ANDI(self):
        # print("ANDI")
        self.push(self.pop() & self.pop())

    def run_ORI(self):
        print("ORI")
        self.push(self.pop() | self.pop())

    def run_GROW(self):
        print("GROW")
        self.memory.extend(b'\x00'*self.pop())
        self.push(len(self.memory))

    def run_PEEKI(self):
        addr = self.pop()
        self.push(struct.unpack("<i", self.memory[addr:addr+4])[0])

    def run_PEEKF(self):
        addr = self.pop()
        self.push(struct.unpack("<d", self.memory[addr:addr+8])[0])

    def run_INPUTI(self):
        self.push(int(input()))

    def run_PEEKB(self):
        addr = self.pop()
        self.push(self.memory[addr])

    def run_POKEI(self):
        value = self.pop()
        addr = self.pop()
        self.memory[addr:addr+4] = struct.pack("<i", value)

    def run_POKEF(self):
        value = self.pop()
        addr = self.pop()
        self.memory[addr:addr+8] = struct.pack("<d", value)

    def run_POKEB(self):
        value = self.pop()
        addr = self.pop()
        self.memory[addr] = value

    def run_IF(self):
        if not self.pop():
            self.pc = self.control[self.pc]

    def run_ELSE(self):
        self.pc = self.control[self.pc]

    def run_ENDIF(self):
        pass

    def run_LOOP(self):
        # print("LOOP")
        pass

    def run_CBREAK(self):
        # print("CBREAK")
        if self.pop():
            # print(self.control)
            # print(self.pc)
            self.pc = self.control[self.pc]

    def run_ENDLOOP(self):
        # print("ENDLOOP")
        self.pc = self.control[self.pc]

    def run_GOTO(self,lino):
        self.pc = lino - 1

    def run_CALL(self, name):
        self.execute(name)

    def run_RET(self):
        self.pc = len(self.code)

    # def run_CONTINUE(self):
    #     print("CONTINUE")
    #     # Set the program counter to the start of the loop
    #     loop_start = None
    #     for addr, (inst, *args) in enumerate(self.code):
    #         if inst == 'LOOP':
    #             loop_start = addr
    #             break
    #     if loop_start is not None:
    #         self.pc = loop_start - 1  # Adjust because the pc will be incremented after this function

    def run_CONTINUE(self):
        self.pc = self.control[self.pc+1] - 1
            

    def run_END(self):
        self.pc = len(self.code)  # Set the program counter to the end of the code, terminating the execution

def run(module):
    interpreter = Interpreter()
    has_main = False
    for func in module.functions.values():
        argnames = func.parmnames
        interpreter.add_function(func.name, argnames, func.code)

    interpreter.execute('main')