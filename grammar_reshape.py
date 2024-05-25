
import grammar_ast
import lark

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ExprTransformer(lark.Transformer):
    def __init__(self, file_path=None):
        # is this where I wish to include the file output? if file is not None:
        if file is not None:
            with open(file_path, 'w'):
                write(".class: Main") # like wr
                # write(buffer)

    def program(self, e):
        log.debug("->program")
        classes, main_block = e # recall e is just the relevant data for initializing the proper node type.
        return grammar_ast.ProgramNode(classes, main_block)
    def INT(self, data):
        """ Data is the stored value passed as an argument. This must
        be an int. This is a terminal symbol, i.e., an int-const"""
        log.debug(f"Processing token INT with {data}")
        val = int(data.value)
        ast_node = grammar_ast.Int_literal(val)
        log.debug(f"Processed token into value {ast_node}")
        return ast_node

    def int(self, children):
        """int, unlike INT, is a non-terminal symbol, i.e., not an int-const. It has
        a single child, which will have been transformed by the INT method above."""
        log.debug(f"Processing 'int' with {children}")
        return children[0]

    def plus(self, e):
        log.debug("-> plus")
        left, right = e # left, right are the operands
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

    def ifstmt(self, e):
        """ifstmt production as referenced by grammar.lark"""
        log.debug("-> ifstmt")
        cond, thenpart, elspart = e
        return ast.IfStmtNode(cond, thenpart, elsepart)

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
