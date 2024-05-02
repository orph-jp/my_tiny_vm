
import grammar_ast
import lark

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ExprTransformer(lark.Transformer):
    def __init__(self, file=None):
        if file is not None:
            
    def INT(self, data):
        """ Data is the stored value passed as an argument. This must
        be an int"""
        log.debug(f"Processing token INT with {data}")
        val = int(data.value)
        ast_node = grammar_ast.Int(val)
        log.debug(f"Processed token into value {ast_node}")
        return ast_node

    def int(self, children):
        """int, unlike INT, is a non-=terminal symbol. It has
        a single child, which will hav ebeen transformed by the INT method above."""
        log.debug(f"Processing 'int' with {children}")
        return children[0]

    def plus(self, children):
        """ This method will be different than the lark how-to turtorial"""
        log.debug(f"Processing 'plus' with {children}")
        left, right = children
        return grammar_ast.Plus(left, right)

    def minus(self, children):
        log.debug(f"Processing 'minus' with {children}")
        left, right = children
        return grammar_ast.Minus(left, right)

    def times(self, children):
        log.debug(f"Processing 'times' with {children}")
        left, right = children
        return grammar_ast.Times(left, right)

    def minus(self, children):
        log.debug(f"Processing 'divide' with {children}")
        left, right = children
        return grammar_ast.Divide(left, right)

    def sum(self, children):
        """The base case, factor -> int."""
        log.debug(f"Processing sum base case {children}")
        return children[0]

    def expr_one(self, children):
        """This will always be the first reduction to expr"""
        log.debug(f"Processing exp (base case) with {children}")
        expr = grammar_ast.Expr()
        expr.append(children[0])
        log.debug(f"Exoression is now {expr}")
        return expr

    def expr_more(self, children):
        """This left-recursive production will always be reduced AFTER
        the base case has been reduced."""
        log.debug(f"Processing expr (recursive case) with {children}")
        expr, sum = children
        expr.append(sum)
        return expr
