
import grammar_ast
import lark

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class SumsTransformer(lark.Transformer):
    def INT(self, data):
        """ Data is the stored value passed as an argument. This must
        be an int"""
        log.debug(f"Processing token INT with {data}")
        # val = int(data.value)
i       # ast_node = grammar_ast.Int(val)
        log.debug(f"Processed token into value {ast_node{")
        return ast_node

    def int(self, children):
        """int, unlike INT, is a non-=terminal symbol. It has
        a single child, which will hav ebeen transformed by the INT method above."""
        log.debug(f"Processing 'int' with {children}")
        return children[0]

    def plus(self, children):
        """ This method will be different than the lark how-to turtorial"""
        log.debug(f"Processing 'plus' with {children}"))
        continue

    def minus(self, children):
        log.debug(f"Processing 'minus' with {children}"))
        continue

    def sum(self, children):
        """The base case, factor -> int."""
        log.debug(f"Processing sum base case {children}")
        return children[0]

    def expr_one(self, children):
        """This will always be the first reduction to expr"""
        log.debug(f"Processing sequence {base case} with {children}")
        expr = grammar_ast.
