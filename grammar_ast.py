"""Abstract syntax representation of a sequence of tokens (pattern)"""
from typing import List
from collections.abc import Callable
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

LB = '}'
RB = '{'

class ASTNode:
    """Abstract base class for abstract sequence of patterns"""
    def __init__(self):
        this_class = self.__class__.__name__
        self.children = []
        if this_class == "ASTNode":
            raise NotImplementedError("ASTNode is an abstract class and should not be instantiated")
        else:
            raise NotImplementedError(f"{this_class} is missing a constructor method")

    def walk(self, visit_state, pre_visit:Callable=ignore, post_visit:Callable=ignore): 
        """NOTE: Normally here, the method calls for pre_vist and post_visit are to be ignored as they
        are overwritten in method_table_vist, which does take action in a few nodes."""
        pre_visit(self, visit_state)
        for child in flatten(self.children):
            log.debug(f"Visiting ASTNode of class {child.__class__.__name__}")
            try:
                child.walk(visit_state, pre_visit, post_visit)
            except Exception as e:
                log.error(f"Failed walking {self.__class__.__name__} to {child.__class__.__name__}")
        post_visit(self, visit_state)

    def post_visit(self, visit_state):
        """For tree, traverse left subtree (recursive call), then traverse right subtree. Then visit root"""
        pass

    def pre_visit(self, visit_state):
        """For tree, visit root, then traverse left subtree (recursive call), then traverse right subtree."""
        pass

    def ignore(self):
        pass

    # Gather method signatures onto the stack
    def method_table_visit(self, visit_state: dict):
        ignore(self, visit_state)

    def r_eval(self, buffer: list[str]):
        """Evaluate for value, i.e., generate code that will
        result in evaluating an expression of some kind for a value.
        Always increases stack depth by 1."""
        raise NotImplementedError(f"r_eval not implemented for node type {self.__class__.__name__}") # because this is called by self.__class__.__name__ instance and will redirected to Abstract class

    def c_eval(self, true_branch: str, false_branch: str, buffer: list[str]):
        """ Code generation method for control flow evaluation. 
        Branches = labels (used in .asm). When evaluated, serves as a go-to, in some sense,
        but rather a 'fall through'"""
        raise NotImplementedError(f"c_eval not implemented for node type {self.__class__.__name__}")

    def gen_code(self, buffer: list[str]):
        """Gen_code is code generation method that does not alter the depth of the 
        stack, unlike c_eval and r_eval."""
        raise NotImplementedError(f"No gen_code method for class {self.__class__.__name__}")

    def dot_id(self) -> str:
        """ Python;s built-in 'id' functiopn lets us create unique IDs"""
        return f"node_{id(self)}" # So for instance, Node_4

    def dot_label(self) -> str:
        """Returns the class as a node label.
        Override to palce other attributes within this tag."""
        return self.__class__.__name__

    def to_dot(self, buffer: list[str]):
        """Add relevant dot code to this node"""
        this_node = self.dot_id()
        buffer.append(f'{this_node}[label="{LB}{self.dot_label()}{RB}"]') # where LB is left
        # branch and RB is the right branch
        for child in flatten(self.children):
            buffer.append(f"{this_node} -> {child.dot_id()};")
            child.to_dot(buffer)

class ProgramNode(ASTNode):
    """The root node of every abstract syntax tree::"""
    def __init__(self, classes: List[ASTNode],  main_block: ASTNode):
        super().__init__() # as always, initialize the super class
        self.classes = classes 
        main_class = ClassNode("$Main", [], "Obj", [], main_block) # main is a class, in essence. Obj is default parent class.
        self.classes.append(main_class) # so it becomes the first entry into self.classes
        self.children = self.classes # descendants of the main class is everything else in the tree--append just main now

    def __str__(self) -> str:
        return "\n".join([str(c) for c in self.classes]) # returns a string seperated by newline of all classes

    def gen_code(self, buffer: list[str]):
        for clazz in self.classes:
            clazz.gen_code(buffer) # this will be .class <var>:Obj

class ClassNode(ASTNode):
    """Class ::= class_signature, class_body, constructor (args are formals), superclass"""
    def __init__(self, class_sig: str, constructor_args: List[ASTNode], superclass: str, methods: List[ASTNode], block: ASTNode): 
        super().__init__()
        self.class_sig = class_sig
        self.constructor = MethodNode("$constructor", constructor_args, "Nothing", block)
        self.methods = methods
        self.methods.insert(0, self.constructor) # design choice to have constructor be the first method        
    def __str__(self):
        """First we must join the seperate elements before python's iterative magic can produce the string representation  """
        constargs = ", ".join([str(arg) for arg in self.constructor.actuals]) # str(arg) will do the ASTNode str repr.
        method = "\n".join(f"{method}\n" for method in self.methods)
        return f""" class {self.name}({constargs}){LB}
            {methods} /* statements as a constructor */ {self.constructor} {RB}
            /* end class {self.class_sig} */"""
        # TODO: Reverse-engineer the corresponding parameter classes and methods
        # TODO: Make sure this is correct

    # TODO: method_table_visit
class MethodNode(ASTNode):
    """This class classifies nodes that result from source code that
    specifies a method call. Subsequently the .asm will look similar to the following:"""
    def __init__(self, name: str, receiver: ASTNode, actuals: list[ASTNode]):
        """For reference: the formal is the actual variable1 used in parameters in the method def.
        Return is the object that is returned by the method.
        Receiver is the actual instance of the class that has called the method.
        Actuals is the actual value or variable passed in to the method when it is called.
        """
        super().__init__()
        self.name = name
        self.receiver = receiver
        self.actuals = actuals
        if self.actuals == [ None ]:
            self.actuals = []
        self.children = [ self.receiver ] + self.actuals # must be the same as .extend()

    def __str__(self):
        actuals_str = ",".join(str(actual) for actual in self.actuals)
        return f"Method Call|{self.name}"

    def dot_label(self) -> str:
        return f"Method Call|{self.name}"

    def r_eval(self, buffer: list[str]):
        for actual in self.actuals:
            actual.r_eval(buffer)
        self.receiver.r_eval(buffer)
        buffer.append(f"call Int:{self.name}")

class BareExprNode(ASTNode):
    def __init__(self, expr: ASTNode):
        super().__init__()
        self.expr = expr
        self.children = [ expr ] 
    
    def __str__(self):
        return str(self.expr) + "// bare expression"

    def gen_code(self, buffer: list[str]):
        self.expr.r_eval(buffer)
        buffer.append("pop") # pop from the call stack the evaluated expr
            
class AssignmentNode(ASTNode):
    """An assignment node is for instance int x = 3."""
    def __init__(self, lhs, decl_type, rhs):
        super().__init__()
        self.decl_type = decl_type
        self.lhs = lhs
        self.rhs = rhs
        self.children = [self.rhs]

    def __str__(self):
        if self.decl_type is None: # e.g. var_1 = 20; 
            return f"{self.lhs} = {self.rhs};"
        else:
            return f"{self.lhs}: {self.decl_type} = {self.rhs};"

    def gen_code(self, buffer: list[str]):
        """Evaluate rhs, store in lhs"""
        buffer += self.rhs.r_eval() # this will store each character as one new entry at the end of the list based on __repr__
                                    # of rhs type (in r_eval).
        buffer.append(f"store {self.lhs}") # i.e. "store Int:x" 

    def gather_locals_visit(self, visit_state: set):
        """For an assignment x = exp, x may be a new local variable"""
        log.debug(f"{self.__class__.__name__}Gathering variable {self.lhs}")
        visit_state.add(self.lhs)

class FieldRefNode(ASTNode):
    """Reference to a variable, i.e., x in this.x"""
    def __init__(self, name: str):
        assert isinstance(name, str)
    """TODO: How to generate code and .PRINT method? Do we need this?""" 

class BooleanExprNode(ASTNode):
    """Stores a boolean expression"""
    def __init__(self, cond):
        self.cond = cond

    def __str__(self):
        return f"{self.cond}"

class Sum(ASTNode):
    pass


class Int_literal(Sum):
    """Leaves of a sum are integer literals."""
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

class Str_literal(ASTNode):
    """String node"""
    def __init__(self, string: str):
        self.chars = string

    def __str__(self):
        return f"{self.chars}"

    def __repr__(self):
        return repr(self.chars)

class BinOp(Sum):
    """Represents addition or subtraction"""
    def __init__(self, op: str, left: Sum, right: Sum):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left} {self.op} {self.right})" 

    def __repr__(self) -> str:
        clazz = self.__class__.__name__
        return f"{clazz}({repr(self.left)}, {repr(self.right)})"

class Plus(BinOp):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__('+', left, right)

class Minus(BinOp):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__('-', left, right)

class Times(BinOp):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__('*', left, right)

class Divide(BinOp):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__('/', left, right)

class Expr(ASTNode):
    """An expresion is the left or right hand side of a traditional statement, and preceeds a non-terminal
    in the derivation of the grammar"""

    def __init__(self, side: str):
        self.sums: list[Sum] = []
        self.side = side

    def append(self, sum: Sum):
        self.sums.append(sum)

    def __str__(self) -> str:
        el_strs = ", ".join(str(e) for e in self.sums)
        return f"[{el_strs}]"

    def __repr__(self):
        return f"seq({repr(self.sums)})"

def smoke_test_sums():
    sum1 = Plus(1, Minus(2, 3))
    sum2 = Minus(2, 1)
    expr = Expr()
    expr.append(sum1)
    expr.append(sum2)
    print(expr)

if __name__ == "__main__":
    smoke_test_sums()
