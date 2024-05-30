"""Read a sequence of sums,
parse with lark to form concrete synatax tree,
transform to form abstract syntax tree"""

import sys
import lark
import grammar_ast
import grammar_reshape

def main():
    # Open up the grammar file to create a parser
    gram_file = open("grammar_alt.lark", "r")
    parser = lark.Lark(gram_file, parser="lalr")

    # Open an example file for reading
    src_file = open("examples/EXGrammar.txt", "r")
    src_text = "".join(src_file.readlines())
    concete = parser.parse(src_text)
    print("Parse tree (concrete syntax):")
    print(concrete.pretty())
    

    # TODO: Include the file to write in the initialization of the transformer
    transformer = grammar_reshape.ExprTransformer()
    ast: grammar_ast.ASTNode = transformer.transform(concrete)
    buffer = [] # create buffer contains asm instructions
    ast.gen_code(buffer) # gen_code on root node
    print("\n".join(buffer)) 
    print(ast)
    print(f"as {repr(ast)}")
 
if __name__ == '__main__':
    main()
