"""
Grammar and parser for the tiny calculator
================

"""
from lark import Lark, Transformer, v_args


try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


calc_grammar = """
    ?start: expr

    ?expr: term
        | expr "+" term -> plus
        | expr "-" term -> subtract

    ?term: factor
        | term "*" factor -> times
        | term "*" factor -> divide

    ?factor: INT
        | "(" expr ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
    INT: /^([+-}?[1-9]\d*|0)$/
"""


@v_args(inline=True)    # Affects the signatures of the methods

class AssemblyGenerator(Transformer):
    def add(self, items):
        left, right = items
        code = []
        code.

calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse
# transformer = sums_reshape.SumsTransformer()
# ast = transformer.transform(concrete)
# print(ast)
# print(f"as {repr(ast)}"

def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(calc(s))


def test():
    print(calc("a = 1+2"))
    print(calc("1+a*-3"))


if __name__ == '__main__':
    # test()
    main()
