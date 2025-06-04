import unittest
from parser import Parser
from lexer import Lexer
from AST import *
# Importa todas las clases AST necesarias


# code = "05 REM Este es un comentario\n06 END"

# p = Parser()  
# l = Lexer() 

# tokens = l.tokenize(code)

# ast = p.parse(tokens)

# print(ast)


# print(ast)
# print(type(ast))

class TestRem(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        
    def test_rem_statement(self):
        code = "05 REM Este es un comentario\n06 END"
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)

        
        
        # Verificar que el AST es una instancia de Program
        self.assertIsInstance(ast, Program, "El AST debe ser una instancia de Program")
        
        # Asegurar que el Program contiene exactamente dos comandos
        self.assertEqual(len(ast.cmds), 2, "El Program debería contener exactamente dos comandos")
        
        # Verificar que el primer comando es una instancia de Remark
        rem_command = ast.cmds[0]
        self.assertIsInstance(rem_command.comand, Remark, "El primer comando debería ser Remark")
        self.assertEqual(rem_command.comand.txt[3:].strip(), 'Este es un comentario', "El texto del comentario no coincide")
        
        # Verificar que el segundo comando es una instancia de End
        end_command = ast.cmds[1]
        self.assertIsInstance(end_command.comand, End, "El segundo comando debería ser End")




class TestGoto(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def test_goto_statement(self):
        code = '50 GOTO 200'
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        goto_command = ast.cmds[0].comand
        self.assertIsInstance(goto_command, Goto)
        self.assertEqual(goto_command.lineno.value, '200')



class TestForLoop(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def test_for_loop_statement(self):
        code = '40 FOR I = 1 TO 10'
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        for_command = ast.cmds[0].comand
        self.assertIsInstance(for_command, ForStmt)
        self.assertEqual(for_command.var.name, "I")
        self.assertEqual(for_command.low.value, '1')
        self.assertEqual(for_command.top.value, '10')


class TestIfStatement(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()


    def test_if_then_statement(self):
        code = '30 IF A = 10 THEN 100'
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        if_command = ast.cmds[0].comand
        self.assertIsInstance(if_command, IfStmt)
        self.assertIsInstance(if_command.relexpr, Logical)
        self.assertEqual(if_command.lineno, Number(value='100'))












if __name__ == '__main__':
    unittest.main()
