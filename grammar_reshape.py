import grammar_ast_alt
import lark

import logging
log = logging.getLogger('name')
log.setLevel(logging.DEBUG)
log.debug("hello")

class QuackTransformer(lark.Transformer):
    """The grammar generates derivations which are then, via this class,
    creating node types inheriting from grammar_ast.ASTNode"""
    """
    def __init__(self, file_path=None):
        # is this where I wish to include the file output? if file is not None:
        if file_path is not None:
            with open(file_path, 'w'):
                self.write_to_buffer(".class: Main") # like wr
                # write(buffer)
        else:
            with open("/out.asm", 'w'):
                self.write_to_buffer(".class: Main") # like wr
    """
    def program(self, e):
        log.debug("->program")
        print(str(e))
        # classes, main_block = e # recall e is just the relevant data for initializing the proper node type.
        # return grammar_ast_alt.ProgramNode(classes, main_block)

    def clazz(self, e):
        log.debug("->clazz")
        name, formals, superclass, constructor, methods = e
        # print(str(name), str(formals), str(superclass), str(constructor), str(methods) )
        grammar_ast_alt.ClassNode(name, formals, superclass, methods, constructor)

    def assign_vars(self, e):
        """NOTE: e passed into buffer may be only 2 variables, in the case that there is no decl_type"""
        """Later, this may need to be handled by checking if the variable is already assigned previously to
        a constNode of the same type."""
        log.debug("-> assignment")
        left, decl_type, rhs = (e[0], None, e[1]) if len(e) == 2 else e
        grammar_ast_alt.AssignmentNode(left, decl_type, rhs)

    def INT(self, data):
        """ Data is the stored value passed as an argument. This must
        be an int. This is a terminal symbol, i.e., an int-const"""
        log.debug(f"Processing token INT with {data}")
        val = int(data.value)
        ast_node = grammar_ast_alt.Int_literal(val)
        log.debug(f"Processed token into value {ast_node}")
        return ast_node

    def int(self, children):
        """int, unlike INT, is a non-terminal symbol, i.e., not an int-const. It has
        a single child, which will have been transformed by the INT method above."""
        log.debug(f"Processing 'int' with {children}")
        return children[0]

    """SECTION: Here are the transformer methods for mathematical operators"""

    def plus(self, e):
        log.debug("-> plus")
        left, right = e # left, right are the operands
        return grammar_ast_alt.MethodNode("PLUS", left, [ right ])

    def minus(self, e):
        log.debug("-> minus")
        left, right = e
        log.debug(e)
        return grammar_ast_alt.MethodNode("MINUS", left, [ right ])

    def times(self, e):
        log.debug("-> times")
        left, right = e
        log.debug(e) # bug point
        return grammar_ast_alt.MethodNode("TIMES", left, [ right ])

    def divide(self, e):
        log.debug("-> divide")
        left, right = e
        return grammar_ast_alt.MethodNode("DIVIDE", left, [ right ])

    def sum(self, children):
        """The base case, factor -> int."""
        log.debug(f"Processing sum base case {children}")
        return children[0]

    """SECTION: Here are the transformer methods for various built-in methods"""

    def method(self, e):
        """Method class"""
        log.debug("-> method")
        name, receiver, actuals = e
        return grammar_ast_alt.MethodNode(name, receiver, actuals)

    def ifstmt(self, e):
        """ifstmt derivation as referenced by grammar.lark. I have chosen
        not to have this be in the form a method call.= and be in a seperate
        class entirely."""
        log.debug("-> ifstmt")
        cond, thenpart, elspart = e
        return grammar_ast_alt.IfStmtNode(cond, thenpart, elsepart)

    def cond(self, e):
        """cond production as  referenced by grammar.lark
        e must therefore already be a grammar_ast.ASTNode"""
        log.debug("-> cond")
        return e

    def whilestmt(self, e):
        """While statement"""
        log.debug("-> while")
        cond, thenpart = e
        # return grammar_ast_alt.WhileNode(cond, thenpart)

    def cond_and(self, e):
        log.debug("-> cond_and")
        left, right = e
        return grammar_ast_alt.MethodNode("BOOL_AND", left, [ right ])

    def cond_or(self, e):
        log.debug("-> cond_or")
        left, right = e
        return grammar_ast_alt.MethodNode("BOOL_OR", left, [ right ])

    def bool_lt(self, e):
        log.debug("-> bool_lt")
        left, right = e
        return grammar_ast_alt.MethodNode("BOOL_LT", left [ right ])

    def bool_gt(self, e):
        log.debug("-> bool_gt")
        left, right = e
        return grammar_ast_alt.MethodNode("BOOL_GT", left [ right ])

    def bool_leq(self, e):
        log.debug("-> bool_leq")
        left, right = e
        return grammar_ast_alt.MethodNode("BOOL_LEQ", left [ right ])

    def bool_geq(self, e):
        log.debug("-> bool_geq")
        left, right = e
        return grammar_ast_alt.MethodNode("BOOL_GEQ", left [ right ])

    def bool_eq(self, e):
        log.debug("-> bool_eq")
        left, right = e
        return grammar_ast_alt.MethodNode("BOOL_EQ", left [ right ])

    """SECTION: Here are the transformer methods distinguishing between recursive or non-recursive classification"""
    def expr_one(self, children):
        """This will always be the first reduction to expr"""
        log.debug(f"Processing exp (base case) with {children}")
        expr = grammar_ast_alt.Expr()
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
