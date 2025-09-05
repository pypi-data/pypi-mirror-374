from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

from ..algebra import element_type, query_property, return_type
from ..finch_assembly import AssemblyNode
from ..symbolic import Context, FType, Term, TermTree, literal_repr
from ..util import qual_str


@dataclass(eq=True, frozen=True)
class NotationNode(Term, ABC):
    """
    NotationNode

    Base class for all Finch Notation nodes
    """

    @classmethod
    def head(cls):
        """Returns the head of the node."""
        return cls

    @classmethod
    def make_term(cls, head, *children):
        return head.from_children(*children)

    @classmethod
    def from_children(cls, *children):
        return cls(*children)

    def __str__(self):
        """Returns a string representation of the node."""
        ctx = NotationPrinterContext()
        res = ctx(self)
        return res if res is not None else ctx.emit()


@dataclass(eq=True, frozen=True)
class NotationTree(NotationNode, TermTree):
    @property
    @abstractmethod
    def children(self) -> list[NotationNode]:  # type: ignore[override]
        ...


class NotationExpression(NotationNode):
    """
    Notation AST expression base class.
    """

    @property
    @abstractmethod
    def result_format(self) -> Any:
        """
        Get the type of the expression.
        """
        ...


@dataclass(eq=True, frozen=True)
class Literal(NotationExpression):
    """
    Notation AST expression for the literal value `val`.
    """

    val: Any

    @property
    def result_format(self):
        return type(self.val)

    def __repr__(self) -> str:
        return literal_repr(type(self).__name__, asdict(self))


@dataclass(eq=True, frozen=True)
class Value(NotationExpression):
    """
    Notation AST expression for host code `val` expected to evaluate to a value of
    type `type_`.
    """

    ex: AssemblyNode
    type_: Any

    @property
    def result_format(self):
        return self.type_

    def __repr__(self) -> str:
        return literal_repr(type(self).__name__, asdict(self))


@dataclass(eq=True, frozen=True)
class Variable(NotationExpression):
    """
    Notation AST expression for a variable named `name`.

    Attributes:
        name: The name of the variable.
        type_: The type of the variable.
    """

    name: str
    type_: Any = None

    @property
    def result_format(self):
        return self.type_

    def __repr__(self) -> str:
        return literal_repr(type(self).__name__, asdict(self))


@dataclass(eq=True, frozen=True)
class Call(NotationTree, NotationExpression):
    """
    Notation AST expression for the result of calling the function `op` on
    `args...`.
    """

    op: Literal
    args: tuple[NotationNode, ...]

    @property
    def result_format(self):
        arg_types = [a.result_format for a in self.args]
        return return_type(self.op.val, *arg_types)

    @classmethod
    def from_children(cls, op, *args):
        return cls(op, args)

    @property
    def children(self):
        return [self.op, *self.args]


class AccessMode(NotationNode):
    """
    Notation AST node representing the access mode of a tensor.
    """


class AccessFType(FType):
    obj: Any

    def __init__(self, obj: Any):
        self.obj = obj

    def __eq__(self, other):
        if not isinstance(other, AccessFType):
            return False
        return self.obj == other.obj

    def __hash__(self):
        return hash(self.obj)

    @property
    def element_type(self):
        """
        Returns the element type of the access ftype.
        """
        return element_type(self.obj)


@dataclass(eq=True, frozen=True)
class Access(NotationTree, NotationExpression):
    """
    Notation AST expression representing the value of tensor `tns` at the indices
    `idx...`.
    """

    tns: NotationNode
    mode: AccessMode
    idxs: tuple[NotationNode, ...]

    @property
    def result_format(self):
        if len(self.idxs) == 0:
            return self.tns.result_format
        return AccessFType(self.tns.result_format)

    @classmethod
    def from_children(cls, tns, mode, *idxs):
        return cls(tns, mode, idxs)

    @property
    def children(self):
        return [self.tns, self.mode, *self.idxs]


@dataclass(eq=True, frozen=True)
class Read(AccessMode):
    """
    Notation AST node representing a read-only access mode for a tensor.
    This mode allows reading the value of a tensor without modifying it.
    """

    @property
    def children(self):
        return []


@dataclass(eq=True, frozen=True)
class Update(AccessMode, NotationTree):
    """
    Notation AST node representing an update access mode for a tensor.  This
    mode allows reading and modifying the value of a tensor.  Increment
    operations are allowed in this mode, and will use the update operation `op`
    to increment `ref` with `val` as `ref = op(ref, val)`.  To overwrite the
    value of a tensor, use the ops `algebra.overwrite` or `algebra.InitWrite`.
    Attributes:
        op: The operation used to update the value of the tensor.
    """

    op: NotationNode

    @property
    def children(self):
        return [self.op]


@dataclass(eq=True, frozen=True)
class Increment(NotationTree):
    """
    Notation AST statement that updates the value `lhs` using `rhs`.
    """

    lhs: NotationNode
    rhs: NotationNode

    @property
    def children(self):
        return [self.lhs, self.rhs]


@dataclass(eq=True, frozen=True)
class Unwrap(NotationTree):
    """
    Notation AST statement that unwraps the scalar value from a 0-dimensional
    tensor `arg`.
    """

    arg: NotationNode

    @property
    def children(self):
        return [self.arg]

    def result_format(self):
        """
        Returns the type of the unwrapped value.
        """
        return element_type(self.arg.result_format)


@dataclass(eq=True, frozen=True)
class Cached(NotationTree, NotationExpression):
    """
    Notation AST expression `arg`, equivalent to the quoted expression `ref`.

    Often used after the compiler caches the computation `ref` into a variable
    `arg`, but we still wish to refer to the original expression to prove
    properties about it.
    """

    arg: NotationNode
    ref: NotationNode

    @property
    def result_format(self):
        return self.arg.result_format

    @property
    def children(self):
        return [self.arg, self.ref]


@dataclass(eq=True, frozen=True)
class Loop(NotationTree):
    """
    Notation AST statement that runs `body` for each value of `idx` in `ext`.
    """

    idx: NotationNode
    ext: NotationNode
    body: NotationNode

    @property
    def children(self):
        return [self.idx, self.ext, self.body]


@dataclass(eq=True, frozen=True)
class If(NotationTree):
    """
    Notation AST statement that only executes `body` if `cond` is true.
    """

    cond: NotationNode
    body: NotationNode

    @property
    def children(self):
        return [self.cond, self.body]


@dataclass(eq=True, frozen=True)
class IfElse(NotationTree):
    """
    Notation AST statement that executes `then_body` if `cond` is true, otherwise
    executes `else_body`.
    """

    cond: NotationNode
    then_body: NotationNode
    else_body: NotationNode

    @property
    def children(self):
        return [self.cond, self.then_body, self.else_body]


@dataclass(eq=True, frozen=True)
class Assign(NotationTree):
    """
    Notation AST statement that defines `lhs` as having the value `rhs`.
    """

    lhs: NotationNode
    rhs: NotationNode

    @property
    def children(self):
        return [self.lhs, self.rhs]


@dataclass(eq=True, frozen=True)
class Stack(NotationExpression):
    """
    A logical AST expression representing an object using a set `obj` of
    expressions, variables, and literals in the target language.

    Attributes:
        obj: The object referencing symbolic variables defined in the target language.
        type: The type of the symbolic object.
    """

    obj: Any
    type: Any

    @property
    def result_format(self):
        """Returns the type of the expression."""
        return self.type


@dataclass(eq=True, frozen=True)
class Slot(NotationExpression):
    """
    Represents a register to a symbolic object. Using a register in an
    expression creates a copy of the object.

    Attributes:
        name: The name of the symbolic object to register.
        type: The type of the symbolic object.
    """

    name: str
    type: Any

    @property
    def result_format(self):
        """Returns the type of the expression."""
        return self.type

    def __repr__(self) -> str:
        return literal_repr(type(self).__name__, asdict(self))


@dataclass(eq=True, frozen=True)
class Unpack(NotationTree):
    """
    Attempts to convert `rhs` into a symbolic, which can be registerd with
    `lhs`. The original object must not be accessed or modified until the
    corresponding `Repack` node is reached.

    Attributes:
        lhs: The symbolic object to write to.
        rhs: The original object to read from.
    """

    lhs: Slot
    rhs: NotationExpression

    @property
    def children(self):
        """Returns the children of the node."""
        return [self.lhs, self.rhs]


@dataclass(eq=True, frozen=True)
class Repack(NotationTree):
    """
    Registers updates from a symbolic object `val` with the original
    object `obj`. The original object may now be accessed and modified.

    Attributes:
        slot: The symbolic object to read from.
        obj: The original object to write to.
    """

    val: Slot
    obj: NotationExpression

    @property
    def children(self):
        """Returns the children of the node."""
        return [self.val, self.obj]


@dataclass(eq=True, frozen=True)
class Declare(NotationTree, NotationExpression):
    """
    Notation AST statement that declares `tns` with an initial value `init` reduced
    with `op` in the current scope.
    """

    tns: NotationNode
    init: NotationNode
    op: NotationNode
    shape: tuple[NotationNode, ...]

    @property
    def children(self):
        return [self.tns, self.init, self.op, *self.shape]

    @classmethod
    def from_children(cls, tns, init, op, *shape):
        """
        Creates a Declare node from its children.
        """
        return cls(tns, init, op, shape)

    @property
    def result_format(self):
        """
        Returns the type of the declared tensor.
        """
        return query_property(
            self.tns.result_format,
            "declare",
            "return_type",
            self.op.result_format,
            *[s.result_format for s in self.shape],
        )


@dataclass(eq=True, frozen=True)
class Freeze(NotationTree, NotationExpression):
    """
    Notation AST statement that freezes `tns` in the current scope after
    modifications with `op`.
    """

    tns: NotationNode
    op: NotationNode

    @property
    def children(self):
        return [self.tns, self.op]

    @property
    def result_format(self):
        """
        Returns the type of the frozen tensor.
        """
        return query_property(
            self.tns.result_format,
            "freeze",
            "return_type",
            self.op.result_format,
        )


@dataclass(eq=True, frozen=True)
class Thaw(NotationTree, NotationExpression):
    """
    Notation AST statement that thaws `tns` in the current scope, moving the tensor
    from read-only mode to update-only mode with a reduction operator `op`.
    """

    tns: NotationNode
    op: NotationNode

    @property
    def children(self):
        return [self.tns, self.op]

    @property
    def result_format(self):
        """
        Returns the type of the thawed tensor.
        """
        return query_property(
            self.tns.result_format,
            "thaw",
            "return_type",
            self.op.result_format,
        )


@dataclass(eq=True, frozen=True)
class Block(NotationTree):
    """
    Notation AST statement that executes each of its arguments in turn.
    """

    bodies: tuple[NotationNode, ...]

    @classmethod
    def from_children(cls, *bodies):
        return cls(bodies)

    @property
    def children(self):
        return list(self.bodies)


@dataclass(eq=True, frozen=True)
class Function(NotationTree):
    """
    Represents a logical AST statement that defines a function `fun` on the
    arguments `args...`.

    Attributes:
        name: The name of the function to define as a variable typed with the
            return type of this function.
        args: The arguments to the function.
        body: The body of the function. If it does not contain a return statement,
            the function returns the value of `body`.
    """

    name: Variable
    args: tuple[Variable, ...]
    body: NotationNode

    @property
    def children(self):
        """Returns the children of the node."""
        return [self.name, *self.args, self.body]

    @classmethod
    def from_children(cls, name, *args_body):
        """Creates a term with the given head and arguments."""
        *args, body = args_body
        return cls(name, tuple(args), body)


@dataclass(eq=True, frozen=True)
class Return(NotationTree):
    """
    Notation AST statement that returns the value of `val` from the current
    function.
    """

    val: NotationNode

    @property
    def children(self):
        """Returns the children of the node."""
        return [self.val]

    @classmethod
    def from_children(cls, val):
        return cls(val)


@dataclass(eq=True, frozen=True)
class Module(NotationTree):
    """
    Represents a group of functions. This is the toplevel translation unit for
    FinchNotation.

    Attributes:
        funcs: The functions defined in the module.
    """

    funcs: tuple[NotationNode, ...]

    @property
    def children(self):
        """Returns the children of the node."""
        return [*self.funcs]

    @classmethod
    def from_children(cls, *funcs):
        return cls(funcs)


class NotationPrinterContext(Context):
    def __init__(self, tab="    ", indent=0):
        super().__init__()
        self.tab = tab
        self.indent = indent

    @property
    def feed(self) -> str:
        return self.tab * self.indent

    def emit(self):
        return "\n".join([*self.preamble, *self.epilogue])

    def block(self) -> NotationPrinterContext:
        blk = super().block()
        blk.indent = self.indent
        blk.tab = self.tab
        return blk

    def subblock(self):
        blk = self.block()
        blk.indent = self.indent + 1
        return blk

    def __call__(self, prgm: NotationNode):
        feed = self.feed
        match prgm:
            case Literal(value):
                return qual_str(value)
            case Variable(name, _):
                return str(name)
            case Value(name, _):
                return str(name)
            case Slot(name, _):
                return str(name)
            case Stack(obj, _):
                return str(obj)
            case Call(f, args):
                return f"{self(f)}({', '.join(self(arg) for arg in args)})"
            case Unwrap(tns):
                return f"unwrap({self(tns)})"
            case Assign(Variable(var_n, var_t), val):
                self.exec(f"{feed}{var_n}: {qual_str(var_t)} = {self(val)}")
                return None
            case Access(tns, mode, idxs):
                tns_e = self(tns)
                idxs_e = [self(idx) for idx in idxs]
                match mode:
                    case Read():
                        return f"read({tns_e}, {idxs_e})"
                    case Update(op):
                        op_e = self(op)
                        return f"update({tns_e}, {idxs_e}, {op_e})"
                    case _:
                        raise NotImplementedError(f"Unrecognized access mode: {mode}")
                return None
            case Increment(tns, val):
                tns_e = self(tns)
                val_e = self(val)
                self.exec(f"{feed}increment({tns_e}, {val_e})")
                return None
            case Block(bodies):
                ctx_2 = self.block()
                for body in bodies:
                    ctx_2(body)
                self.exec(ctx_2.emit())
                return None
            case Loop(idx, ext, body):
                idx_e = self(idx)
                ext_e = self(ext)
                ctx_2 = self.subblock()
                ctx_2(body)
                body_code = ctx_2.emit()
                self.exec(f"{feed}loop({idx_e}, {ext_e}):\n{body_code}")
                return None
            case Declare(tns, init, op, shape):
                shape_e = [self(s) for s in shape]
                self.exec(
                    f"{feed}declare({self(tns)}, {self(init)}, {self(op)}, {shape_e})"
                )
                return None
            case Freeze(tns, op):
                self.exec(f"{feed}freeze({self(tns)}, {self(op)})")
                return None
            case Thaw(tns, op):
                return f"thaw({self(tns)}, {self(op)})"
            case Unpack(Slot(var_n, var_t), val):
                self.exec(f"{feed}{var_n}: {qual_str(var_t)} = unpack({self(val)})")
                return None
            case Repack(Slot(var_n, var_t), obj):
                self.exec(f"{feed}repack({var_n}, {self(obj)})")
                return None
            case If(cond, body):
                cond_code = self(cond)
                ctx_2 = self.subblock()
                ctx_2(body)
                body_code = ctx_2.emit()
                self.exec(f"{feed}if {cond_code}:\n{body_code}")
                return None
            case IfElse(cond, body, else_body):
                cond_code = self(cond)
                ctx_2 = self.subblock()
                ctx_2(body)
                body_code = ctx_2.emit()
                ctx_3 = self.subblock()
                ctx_3(else_body)
                else_body_code = ctx_3.emit()
                self.exec(
                    f"{feed}if {cond_code}:\n{body_code}\n{feed}else:\n{else_body_code}"
                )
                return None
            case Function(Variable(func_n, ret_t), args, body):
                ctx_2 = self.subblock()
                arg_decls = []
                for arg in args:
                    match arg:
                        case Variable(name, t):
                            arg_decls.append(f"{name}: {qual_str(t)}")
                        case _:
                            raise NotImplementedError(
                                f"Unrecognized argument type: {arg}"
                            )
                ctx_2(body)
                body_code = ctx_2.emit()
                feed = self.feed
                self.exec(
                    f"{feed}def {func_n}({', '.join(arg_decls)}) -> "
                    f"{qual_str(ret_t)}:\n"
                    f"{body_code}\n"
                )
                return None
            case Return(value):
                self.exec(f"{feed}return {self(value)}")
                return None
            case Module(funcs):
                for func in funcs:
                    if not isinstance(func, Function):
                        raise NotImplementedError(
                            f"Unrecognized function type: {type(func)}"
                        )
                    self(func)
                return None
            case _:
                raise NotImplementedError(
                    f"Unrecognized notation node type: {type(prgm)}"
                )
