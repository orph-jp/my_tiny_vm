"""Read a sequence of sums,
parse with lark to form confret esynatax tree,
transforn to form abstract syntax tree"""

import sys
import lark
import grammar_ast
import grammar_reshape

def main():
    # Open up the grammar file to create a parser
    gram_file = open("grammar.lark", "r")
    parser = lark.Lark(gram_file, parser="lalr")

    # Open an example file for reading
    src_file = open("examples/EXGrammar.txt", "r")
    src_text = "".join(src_file.readlines())
    concete = parser.parse(src_text)
    print("Parse tree (concrete syntax):")
    print(concrete.pretty())

    transformer = grammar_reshape.ExprTransformer()
    ast = transformer.transform(concrete)
    print(ast)
    print(f"as {repr(ast)}")

if __name__ == '__main__':
    main()
