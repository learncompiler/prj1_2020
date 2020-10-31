import sys
import argparse

from .lex import lexing
from .parser import parsing
# from .ir import gen_ir
# from .asm import ir2asm


def parseArgs(argv):
    parser = argparse.ArgumentParser(description='MiniDecaf compiler')
    parser.add_argument('infile', type=str,
                        help='the input C file')
    parser.add_argument('outfile', type=str, nargs='?',
                        help='the output assembly file')
    parser.add_argument('-ir', action='store_true',
                        help='emit ir rather than asm')
    parser.add_argument('-ni', action='store_true',
                        help='emit result of name resulution')
    parser.add_argument('-ty', action='store_true',
                        help='emit type check information')
    parser.add_argument('-lex', action='store_true',
                        help='emit tokens produced by lexing')
    parser.add_argument('-parse', action='store_true',
                        help='emit cst produced by parsing (use `make cst` for graphical view)')
    parser.add_argument('-backtrace', action='store_true',
                        help='emit backtrace information (for debugging)')
    return parser.parse_args()


def print_lex(token_list):
    print('%-25s%s' % ('Token', 'Text'))
    print('-------------------------------')
    for token in token_list:
        print(token)


def print_ir(ir):
    print('\nglobal:\n', ir[0])
    for func in ir[1]:
        print('\n%s:' % func[0])
        for node in func[1]:
            print(node)


def main(argv):
    global args
    args = parseArgs(argv)
    code = open(args.infile, 'r').read()
    token_list = lexing(code)
    if args.lex:
        print_lex(token_list)
        return 0
    prog = parsing(token_list)
    s = prog.to_cpp()
    # print(s)
    open(args.outfile, 'w').write(s)
