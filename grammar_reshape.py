
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

    def plus(self, e):
        log.debug("-> plus")
        left, right = e
        return grammar_ast.MethodCallNode("PLUS", left, [ right ])

    def minus(self, e):
        log.debug("-> minus")
        left, right = e
        return grammar_ast.MethodCallNode("MINUS", left, [ right ])

    def times(self, e):
        log.debug("-> times")
        left, right = e
        return grammar_ast.MethodCallNode("TIMES", left, [ right ])

    def divide(self, e):
        log.debug("-> divide")
        left, right = e
        return grammar_ast.MethodCallNode("DIVIDE", left, [ right ])

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
