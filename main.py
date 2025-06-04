'''
usage: basic.py [-h] [-v] [-u] [-a] [-s] [-n] [-g] [-t] [--tabs] [r] [-p] [-w] [-o] [-i]

Compiler for BASIC DARTMOUTH 64

positional arguments:
  input              BASIC program file to compile

optional arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit
  -u, --upper        Convert keywords to uppercase
  -a, --array-base   Set the array base to 1
  -s, --slicing      Enable slicing
  -n, --no-run       Do not run the program
  -g, --go-next      Go to the next line after a GOTO
  -t, --trace        Enable tracing of lines
  --tabs             Use tabs for indentation
  -r, --random       Seed for random number generator
  -p, --print-stats  Print statistics
  -w, --write-stats  Write statistics to a file
  -o, --output       redirects the print output to a file
  -i, --input-file   redirects the input to a file
'''
from contextlib import redirect_stdout
import argparse
import time

from rich import print
from checker_errman_typesys import Context


def parse_args():
    cli = argparse.ArgumentParser(
        prog='basic.py',
        description='Compiler for BASIC programs'
    )

    cli.add_argument(
        '-v', '--version',
        action='version',
        version='1.4v (2024-06-04)')

    fgroup = cli.add_argument_group('Formatting options')

    fgroup.add_argument(
        'input',
        type=str,
        nargs='?',
        help='BASIC program file to compile')

    # mutex = fgroup.add_mutually_exclusive_group()

    # mutex.add_argument(
    #     '-l', '--lex',
    #     action='store_true',
    #     default=False,
    #     help='Store output of lexer')

    # mutex.add_argument(
    #     '-a', '--ast',
    #     action='store',
    #     dest='style',
    #     choices=['dot', 'txt'],
    #     help='Generate AST graph as DOT format')

    # ----------

    cli.add_argument(
        '-u', '--upper',
        action='store_true',
        help='Convert keywords to uppercase')

    cli.add_argument(
        '-ab', '--array-base',
        action='store_true',
        help='Set the array base to 1')

    # cli.add_argument(
    #     '-s', '--slicing',
    #     action='store_true',
    #     help='Enable slicing')

    cli.add_argument(
        '-n', '--no-run',
        action='store_true',
        help='Do not run the program')

    # cli.add_argument(
    #     '-g', '--go-next',
    #     action='store_true',
    #     help='Go to the next line after a GOTO')

    cli.add_argument(
        '-t', '--trace',
        action='store_true',
        help='Enable tracing')

    cli.add_argument(
        '--tabs',
        action='store_true',
        help='Use tabs for indentation')

    # cli.add_argument(
    #     '-r', '--random',
    #     action='store',
    #     help='Seed for random number generator')

    cli.add_argument(
        '-p', '--print-stats',
        action='store_true',
        help='Print statistics')

    cli.add_argument(
        '-w', '--write-stats',
        action='store_true',
        help='Write statistics to a file')

    cli.add_argument(
        '-o', '--output',
        action='store',
        help='Output file')

    cli.add_argument(
        '-i', '--input-file',
        action='store',
        help='Input file')

    return cli.parse_args()


if __name__ == '__main__':
    print("\n--Main--\n")
    args = parse_args()
    context = Context()  # Create a new context object to store the program information and state of the compiler

    if args.input:
        fname = args.input

    with open(fname, encoding='utf-8') as file:
        source = file.read()

    # if args.lex:
    #     flex = fname.split('.')[0] + '.lex'
    #     print(f'print lexer: {flex}')
    #     with open(flex, 'w', encoding='utf-8') as fout:
    #         with redirect_stdout(fout):
    #             context.print_tokens(source)  # --------------- método sin definir en bascontext.py

    # elif args.style:
    #     base = fname.split('.')[0]

    #     fast = base + '.' + args.style
    #     print(f'print ast: {fast}')
    #     with open(fast, 'w') as fout:
    #         with redirect_stdout(fout):
    #             context.print_ast(source, args.style)  # --------------- método sin definir en bascontext.py

    if args.upper:
        print("Me imprimo en mayúsculas")
        print("[green]\n\n-- START --\n[/green]")
        context.parse(source)
        context.runUpper(True)
        print("[green]\n\n-- END --\n[/green]")

    elif args.array_base:
        print("Establezco la base de los arrays en 1")
        print("[green]\n\n-- START --\n[/green]")
        context.parse(source)
        context.runArrayBase(True)
        print("[green]\n\n-- END --\n[/green]")

    elif args.print_stats:
        print("Imprimo estadísticas")
        print("[green]\n\n-- START --\n[/green]")
        
        # Comienza a contar el tiempo en segundos
        start_time = time.time()
        
        context.parse(source)
        context.runWithStats(True)
        
        # Termina de contar el tiempo en segundos
        end_time = time.time()
        elapsed_time = end_time - start_time
    
        print("[green]\n\n-- END --\n[/green]")
        # Imprime las estadísticas
        print(f"Tiempo transcurrido: {elapsed_time:.2f} segundos")

    elif args.write_stats:
        print("Escribiendo estadísticas en el archivo stats.txt")
        
        # Abre el archivo stats.txt en modo de escritura
        with open('stats.txt', 'w') as fout:
            fout.write("[green]\n\n-- START --\n[/green]\n")
            
            # Comienza a contar el tiempo en segundos
            start_time = time.time()
            
            context.parse(source)
            context.runWithStats(True)
            
            # Termina de contar el tiempo en segundos
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Escribe el tiempo transcurrido en segundos en el archivo
            fout.write(f"Tiempo transcurrido: {elapsed_time:.2f} segundos\n\n")
            
            # Escribe las estadísticas en el archivo
            fout.write(f"Tiempo transcurrido: {elapsed_time:.2f} segundos")
            
            fout.write("[green]\n\n-- END --\n[/green]\n")
        
        print("Las estadísticas han sido escritas en el archivo stats.txt")

    elif args.no_run:
        context.parse(source)
        context.noRun(True)
        print("[green]\n\n-- Analisis completado --\n[/green]")

    elif args.output:
        with open(args.output, 'w') as fout:
            # Redirige la salida estándar al archivo de salida
            with redirect_stdout(fout):
                context.parse(source)
                context.run()
        print("[green]\n\n-- Archivo de salida generado --\n[/green]")

    elif args.input_file:
        with open(args.input_file, 'w') as fout:
            # muestra los inputs en el archivo de entrada
            with redirect_stdout(fout):
                context.parse(source)
                context.run()
        print("[green]\n\n-- Archivo de entrada generado --\n[/green]")

    elif args.trace:
        print("seguimiento al número de líneas")
        print("[green]\n\n-- START --\n[/green]")
        context.parse(source)
        context.runWithTrace(True)
        print("[green]\n\n-- END --\n[/green]")

    elif args.tabs:
        print("Usando tabulaciones para la identación")
        print("[green]\n\n-- ingrese el numero de espacios de tabulación --\n[/green]")
        num_tabs = int(input())
        context.parse(source)
        context.runWithTabs(num_tabs)
        print("[green]\n\n-- END --\n[/green]")

    else:
        print("[green]\n\n-- START --\n[/green]")
        context.parse(source)
        context.run()
        print("\n\n\n\n")
