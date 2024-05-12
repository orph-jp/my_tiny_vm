"""Abstract syntax representation of a sequence of tokens (pattern)"""
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ASTNode:
    """Abstract base class for abstract sequence of patterns"""
    def __init__(self):
        this_class = self.__class__.__name__
        if this_class == "ASTNode":
            raise NotImplementedError("ASTNode is an abstract class and should not be instantiated")
        else:
            raise NotImplementedError(f"{this_class} is missing a constructor method")

    def walk(self, visit_state, pre_visit: Callable=ignore, post_visit:Callable=ignore):
        pre_visit(self, visit_state)
        for child in flatten(self.children):
            log.debug(f"Visiting ASTNode of class {child.__class__.__name__}")
            try:
                child.walk(visit_state, pre_visit, post_visit)
            except Exception as e:
                log.error(f"Failed walking {self.__class__.__name__} to {child.__class__.__name__}")
        post_visit(self, visit_state)

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

class MethodCallNode(ASTNode):
    """This class classifies nodes that result from source code that
    specifies a method call. Subsequently the .asm will look similar to the following:"""
    def __init__(self, name: str, receiver: ASTNode, actuals: list[ASTNode]):
        super().__init__()
        self.name = name
        self.receiver = receiver
        self.actuals = actuals
        if self.actuals == [ None ]:
            self.actuals = []
        self.children = [ self.receiver ] + self.actuals # must be the same as .extend()

    def __str__(self):
        actuals = ",".join(str(actual) for actual in self.actuals)
        return f"{self.receiver}.{self.name}({actuals})"

    def dot_label(self) -> str:
        return f"Method Call|{self.name}"

    def r_eval(self, buffer: list[str]):
        for actual in self.actuals:
            actual.r_eval(buffer)
        self.receiver.r_eval(buffer)

class BareExprNode(ASTNode):
    def __init__(self, expr, ASTNode):
        super().__init__()
        self.expr = expr
        self.children = [ expr ] 
    
    def __str__(self):
        return str(self.expr) + "// bare expression"
            
class AssignmentNode(ASTNode):
    def __init__(self, lhs, decl_type, rhs):
        self.decl_type = decl_type
        self.lhs = lhs
        self.rhs = rhs
        self.children = [self.rhs]

    def __str__(self):
        if self.decl_type is None:
            return f"{self.lhs} = {self.rhs};"
        else:
            return f"{self.lhs}: {self.decl_type} = {self.rhs};"

    def gen_code(self, buffer: list[str]):
        """Evaluate rhs, store in lhs"""
        buffer += self.rhs.r_eval()
        buffer.append(f"store {self.lhs}")

class VariableRefNode(ASTNode):
    """Reference to a variable, i.e., x in this.x"""
    def __init__(self, name: str):
        assert isinstance(name, str)


class Sum(ASTNode):
    pass


class Int(Sum):
    """Leaves of a sum are integer literals."""
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

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
    """A sequence of sums. We could represent it in a treelike manner
    to better match a left-recursive grammar, but we'll instead represent
    it as a list of sums to illustrate how we can apply a lark transformer
    to reshape it"""

    def __init__(self):
        self.sums: list[Sum] = []

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
