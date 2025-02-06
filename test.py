from main import *
from emit import *
from parse import *
import sys


def main():
    print("My very own compiler")
    
    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], "r") as inputFile:
        source = inputFile.read()
    #Initialize lexer and parser
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)
    
    parser.program() #starts parser
    emitter.writeFile() # Write the output to file.
    print("Compiling completed")
    
main()
