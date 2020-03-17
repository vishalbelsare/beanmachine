# Copyright (c) Facebook, Inc. and its affiliates.
# from beanmachine.graph import Graph
"""A builder for the BeanMachine Graph language"""

import math
from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Callable, Dict, List

import torch

# TODO: For reasons unknown, Pyre is unable to find type information about
# TODO: beanmachine.graph from beanmachine.ppl.  I'll figure out why later;
# TODO: for now, we'll just turn off error checking in this mModuleNotFoundError
# pyre-ignore-all-errors
from beanmachine.graph import AtomicType, DistributionType, Graph, OperatorType
from beanmachine.ppl.utils.dotbuilder import DotBuilder
from beanmachine.ppl.utils.memoize import memoize
from torch import Tensor
from torch.distributions import Bernoulli


builtin_function_or_method = type(abs)


class BMGNode(ABC):
    children: List["BMGNode"]
    edges: List[str]

    def __init__(self, children: List["BMGNode"]):
        self.children = children

    @abstractmethod
    def node_type(self) -> Any:
        pass

    @abstractmethod
    def label(self) -> str:
        pass

    @abstractmethod
    def _add_to_graph(self, g: Graph, d: Dict["BMGNode", int]) -> int:
        pass

    @abstractmethod
    def _to_python(self, d: Dict["BMGNode", int]) -> str:
        pass

    @abstractmethod
    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        pass

    @abstractmethod
    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        pass


known_tensor_instance_functions = [
    "add",
    "div",
    "exp",
    "float",
    "log",
    "logical_not",
    "mul",
    "neg",
    "pow",
]


class KnownFunction:
    receiver: BMGNode
    function: Any

    def __init__(self, receiver: BMGNode, function: Any) -> None:
        self.receiver = receiver
        self.function = function


class ConstantNode(BMGNode, metaclass=ABCMeta):
    edges = []
    value: Any

    def __init__(self):
        BMGNode.__init__(self, [])

    @abstractmethod
    def _value_to_cpp(self) -> str:
        pass

    @abstractmethod
    def _value_to_python(self) -> str:
        pass

    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        n = d[self]
        v = self._value_to_cpp()
        return f"uint n{n} = g.add_constant({v});"

    def _to_python(self, d: Dict["BMGNode", int]) -> str:
        n = d[self]
        v = self._value_to_python()
        return f"n{n} = g.add_constant({v})"


class BooleanNode(ConstantNode):
    value: bool

    def __init__(self, value: bool):
        ConstantNode.__init__(self)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def node_type(self) -> Any:
        return bool

    def label(self) -> str:
        return str(self.value)

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        return g.add_constant(bool(self.value))

    def _value_to_python(self) -> str:
        return str(bool(self.value))

    def _value_to_cpp(self) -> str:
        return str(bool(self.value)).lower()

    def __bool__(self) -> bool:
        return self.value


class RealNode(ConstantNode):
    value: float

    def __init__(self, value: float):
        ConstantNode.__init__(self)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    # TODO: We may need to represent "positive real" and "real between 0 and 1"
    # TODO: in the type system; how are we to do that?
    def node_type(self) -> Any:
        return float

    def label(self) -> str:
        return str(self.value)

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        return g.add_constant(float(self.value))

    def _value_to_python(self) -> str:
        return str(float(self.value))

    def _value_to_cpp(self) -> str:
        return str(float(self.value))

    def __bool__(self) -> bool:
        return bool(self.value)


class ListNode(BMGNode):
    # TODO: A list node does not appear in the final graph at this time; it
    # TODO: is useful when constructing the final graph from a BM program that
    # TODO: uses lists. Consider if we want a list type in the graph.
    def __init__(self, children: List[BMGNode]):
        BMGNode.__init__(self, children)
        self.edges = [str(x) for x in range(len(children))]

    # TODO: Determine the list type by observing the types of the members.
    def node_type(self) -> Any:
        return List[Any]

    def label(self) -> str:
        return "list"

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        # TODO: list nodes are not currently part of the graph
        return -1

    def _to_python(self, d: Dict[BMGNode, int]) -> str:
        # TODO: list nodes are not currently part of the graph
        return ""

    def _to_cpp(self, d: Dict[BMGNode, int]) -> str:
        # TODO: list nodes are not currently part of the graph
        return ""

    def __getitem__(self, key) -> BMGNode:
        if not isinstance(key, RealNode):
            raise ValueError(
                "BeanMachine list must be indexed with a known numeric value"
            )
        return self.children[int(key.value)]


class TensorNode(ConstantNode):
    value: Tensor

    def __init__(self, value: Tensor):
        ConstantNode.__init__(self)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    def _tensor_to_python(t: Tensor) -> str:
        if len(t.shape) == 0:
            return str(t.item())
        return "[" + ",".join(TensorNode._tensor_to_python(c) for c in t) + "]"

    @staticmethod
    def _tensor_to_label(t: Tensor) -> str:
        length = len(t.shape)
        if length == 0 or length == 1:
            return TensorNode._tensor_to_python(t)
        return "[" + ",\\n".join(TensorNode._tensor_to_label(c) for c in t) + "]"

    # TODO: Do tensor types need to describe their shape and contents?
    def node_type(self) -> Any:
        return Tensor

    def label(self) -> str:
        return TensorNode._tensor_to_label(self.value)

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        return g.add_constant(self.value)

    def _value_to_python(self) -> str:
        t = TensorNode._tensor_to_python(self.value)
        return f"tensor({t})"

    def _value_to_cpp(self) -> str:
        values = ",".join(str(element) for element in self.value.storage())
        dims = ",".join(str(dim) for dim in self.value.shape)
        return f"torch::from_blob((float[]){{{values}}}, {{{dims}}})"

    def __bool__(self) -> bool:
        return bool(self.value)


class DistributionNode(BMGNode, metaclass=ABCMeta):
    def __init__(self, children: List[BMGNode]):
        BMGNode.__init__(self, children)

    @abstractmethod
    def sample_type(self) -> Any:
        pass


class BernoulliNode(DistributionNode):
    edges = ["probability"]

    def __init__(self, probability: BMGNode):
        DistributionNode.__init__(self, [probability])

    def probability(self) -> BMGNode:
        return self.children[0]

    # TODO: Do we need a generic type for "distribution of X"?
    def node_type(self) -> Any:
        return Bernoulli

    def sample_type(self) -> Any:
        return self.probability().node_type()

    def label(self) -> str:
        return "Bernoulli"

    def __str__(self) -> str:
        return "Bernoulli(" + str(self.probability()) + ")"

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        return g.add_distribution(
            DistributionType.BERNOULLI, AtomicType.BOOLEAN, [d[self.probability()]]
        )

    def _to_python(self, d: Dict["BMGNode", int]) -> str:
        return (
            f"n{d[self]} = g.add_distribution(graph.DistributionType.BERNOULLI, "
            + f"graph.AtomicType.BOOLEAN, [n{d[self.probability()]}])"
        )

    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        return (
            f"uint n{d[self]} = g.add_distribution(\n"
            + "  graph::DistributionType::BERNOULLI,\n"
            + "  graph::AtomicType::BOOLEAN,\n"
            + f"  std::vector<uint>({{n{d[self.probability()]}}}));"
        )


class OperatorNode(BMGNode, metaclass=ABCMeta):
    def __init__(self, children: List[BMGNode]):
        BMGNode.__init__(self, children)


class BinaryOperatorNode(OperatorNode, metaclass=ABCMeta):
    edges = ["left", "right"]
    operator_type: OperatorType

    def __init__(self, left: BMGNode, right: BMGNode):
        OperatorNode.__init__(self, [left, right])

    # TODO: Improve this
    def node_type(self) -> Any:
        if self.left().node_type() == Tensor or self.right().node_type() == Tensor:
            return Tensor
        return float

    def left(self) -> BMGNode:
        return self.children[0]

    def right(self) -> BMGNode:
        return self.children[1]

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        return g.add_operator(self.operator_type, [d[self.left()], d[self.right()]])

    def _to_python(self, d: Dict["BMGNode", int]) -> str:
        n = d[self]
        ot = self.operator_type
        left = d[self.left()]
        right = d[self.right()]
        return f"n{n} = g.add_operator(graph.{ot}, [n{left}, n{right}])"

    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        ot = str(self.operator_type).replace(".", "::")
        left = d[self.left()]
        right = d[self.right()]
        return (
            f"uint n{d[self]} = g.add_operator(\n"
            + f"  graph::{ot}, std::vector<uint>({{n{left}, n{right}}}));"
        )


class AdditionNode(BinaryOperatorNode):
    operator_type = OperatorType.ADD

    def __init__(self, left: BMGNode, right: BMGNode):
        BinaryOperatorNode.__init__(self, left, right)

    def label(self) -> str:
        return "+"

    def __str__(self) -> str:
        return "(" + str(self.left()) + "+" + str(self.right()) + ")"


class MultiplicationNode(BinaryOperatorNode):
    operator_type = OperatorType.MULTIPLY

    def __init__(self, left: BMGNode, right: BMGNode):
        BinaryOperatorNode.__init__(self, left, right)

    def label(self) -> str:
        return "*"

    def __str__(self) -> str:
        return "(" + str(self.left()) + "*" + str(self.right()) + ")"


class DivisionNode(BinaryOperatorNode):
    # TODO: We haven't added division to the C++ implementation of BMG yet.
    # TODO: When we do, update this.
    operator_type = OperatorType.MULTIPLY  # TODO

    def __init__(self, left: BMGNode, right: BMGNode):
        BinaryOperatorNode.__init__(self, left, right)

    def label(self) -> str:
        return "/"

    def __str__(self) -> str:
        return "(" + str(self.left()) + "/" + str(self.right()) + ")"


class PowerNode(BinaryOperatorNode):
    # TODO: We haven't added power to the C++ implementation of BMG yet.
    # TODO: When we do, update this.
    operator_type = OperatorType.MULTIPLY  # TODO

    def __init__(self, left: BMGNode, right: BMGNode):
        BinaryOperatorNode.__init__(self, left, right)

    def label(self) -> str:
        return "**"

    def __str__(self) -> str:
        return "(" + str(self.left()) + "**" + str(self.right()) + ")"


class UnaryOperatorNode(OperatorNode, metaclass=ABCMeta):
    edges = ["operand"]
    operator_type: OperatorType

    def __init__(self, operand: BMGNode):
        OperatorNode.__init__(self, [operand])

    # TODO: Improve this
    def node_type(self) -> Any:
        return self.operand().node_type()

    def operand(self) -> BMGNode:
        return self.children[0]

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        return g.add_operator(self.operator_type, [d[self.operand()]])

    def _to_python(self, d: Dict[BMGNode, int]) -> str:
        n = d[self]
        o = d[self.operand()]
        ot = str(self.operator_type)
        return f"n{n} = g.add_operator(graph.{ot}, [n{o}])"

    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        n = d[self]
        o = d[self.operand()]
        # Since OperatorType is not actually an enum, there is no
        # name attribute to use.
        ot = str(self.operator_type).replace(".", "::")
        return (
            f"uint n{n} = g.add_operator(\n"
            + f"  graph::{ot}, std::vector<uint>({{n{o}}}));"
        )


class NegateNode(UnaryOperatorNode):
    operator_type = OperatorType.NEGATE

    def __init__(self, operand: BMGNode):
        UnaryOperatorNode.__init__(self, operand)

    def label(self) -> str:
        return "-"

    def __str__(self) -> str:
        return "-" + str(self.operand())


class NotNode(UnaryOperatorNode):
    # TODO: We do not support NOT in BMG yet; when we do, update this.
    operator_type = OperatorType.NEGATE  # TODO

    def __init__(self, operand: BMGNode):
        UnaryOperatorNode.__init__(self, operand)

    def node_type(self) -> Any:
        return bool

    def label(self) -> str:
        return "not"

    def __str__(self) -> str:
        return "not " + str(self.operand())


class ToRealNode(UnaryOperatorNode):
    operator_type = OperatorType.TO_REAL

    def __init__(self, operand: BMGNode):
        UnaryOperatorNode.__init__(self, operand)

    def node_type(self) -> Any:
        return float

    def label(self) -> str:
        return "ToReal"

    def __str__(self) -> str:
        return "ToReal(" + str(self.operand()) + ")"


class ToTensorNode(UnaryOperatorNode):
    operator_type = OperatorType.TO_TENSOR

    def __init__(self, operand: BMGNode):
        UnaryOperatorNode.__init__(self, operand)

    def label(self) -> str:
        return "ToTensor"

    def __str__(self) -> str:
        return "ToTensor(" + str(self.operand()) + ")"


class ExpNode(UnaryOperatorNode):
    operator_type = OperatorType.EXP

    def __init__(self, operand: BMGNode):
        UnaryOperatorNode.__init__(self, operand)

    def label(self) -> str:
        return "Exp"

    def __str__(self) -> str:
        return "Exp(" + str(self.operand()) + ")"


class LogNode(UnaryOperatorNode):
    # TODO: We do not support LOG in BMG yet; when we do, update this:
    operator_type = OperatorType.EXP  # TODO

    def __init__(self, operand: BMGNode):
        UnaryOperatorNode.__init__(self, operand)

    def label(self) -> str:
        return "Log"

    def __str__(self) -> str:
        return "Log(" + str(self.operand()) + ")"


class SampleNode(UnaryOperatorNode):
    operator_type = OperatorType.SAMPLE

    def __init__(self, operand: DistributionNode):
        UnaryOperatorNode.__init__(self, operand)

    def node_type(self) -> Any:
        return self.operand().sample_type()

    def operand(self) -> DistributionNode:
        c = self.children[0]
        assert isinstance(c, DistributionNode)
        return c

    def label(self) -> str:
        return "Sample"

    def __str__(self) -> str:
        return "Sample(" + str(self.operand()) + ")"


class Observation(BMGNode):
    edges = ["operand", "value"]

    def __init__(self, observed: SampleNode, value: ConstantNode):
        BMGNode.__init__(self, [observed, value])

    def observed(self) -> SampleNode:
        c = self.children[0]
        assert isinstance(c, SampleNode)
        return c

    def value(self) -> ConstantNode:
        c = self.children[1]
        assert isinstance(c, ConstantNode)
        return c

    def node_type(self) -> Any:
        return type(self.value())

    def label(self) -> str:
        return "Observation"

    def __str__(self) -> str:
        return str(self.observed()) + "=" + str(self.value())

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        v = self.value().value
        g.observe(d[self.observed()], v)
        return -1

    def _to_python(self, d: Dict["BMGNode", int]) -> str:
        v = self.value().value
        return f"g.observe(n{d[self.observed()]}, {v})"

    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        v = self.value()._value_to_cpp()
        return f"g.observe([n{d[self.observed()]}], {v});"


class Query(BMGNode):
    edges = ["operator"]

    def __init__(self, operator: OperatorNode):
        BMGNode.__init__(self, [operator])

    def operator(self) -> OperatorNode:
        c = self.children[0]
        assert isinstance(c, OperatorNode)
        return c

    def node_type(self) -> Any:
        return self.operator().node_type()

    def label(self) -> str:
        return "Query"

    def __str__(self) -> str:
        return "Query(" + str(self.operator()) + ")"

    def _add_to_graph(self, g: Graph, d: Dict[BMGNode, int]) -> int:
        g.query(d[self.operator()])
        return -1

    def _to_python(self, d: Dict["BMGNode", int]) -> str:
        return f"g.query(n{d[self.operator()]})"

    def _to_cpp(self, d: Dict["BMGNode", int]) -> str:
        return f"g.query(n{d[self.operator()]});"


class BMGraphBuilder:

    # Note that Python 3.7 guarantees that dictionaries maintain insertion order.
    nodes: Dict[BMGNode, int]

    def __init__(self):
        self.nodes = {}

    def remove_orphans(self, roots: List[BMGNode]) -> None:
        self.nodes = {}
        for root in roots:
            self.add_node(root)

    def add_node(self, node: BMGNode) -> None:
        # Maintain the invariant that children are always before parents
        # in the list.
        # TODO: If we are ever in a situation where we need to make nodes
        # TODO: and then add the edges later, we'll have to instead do
        # TODO: a deterministic topo sort.
        if node not in self.nodes:
            for child in node.children:
                self.add_node(child)
            self.nodes[node] = len(self.nodes)

    def add_constant(self, value: Any) -> ConstantNode:
        if isinstance(value, bool):
            return self.add_boolean(value)
        if isinstance(value, int):
            return self.add_real(value)
        if isinstance(value, float):
            return self.add_real(value)
        if isinstance(value, Tensor):
            return self.add_tensor(value)
        raise TypeError("value must be a bool, real or tensor")

    @memoize
    def add_real(self, value: float) -> RealNode:
        node = RealNode(value)
        self.add_node(node)
        return node

    @memoize
    def add_boolean(self, value: bool) -> BooleanNode:
        node = BooleanNode(value)
        self.add_node(node)
        return node

    @memoize
    def add_tensor(self, value: Tensor) -> TensorNode:
        node = TensorNode(value)
        self.add_node(node)
        return node

    @memoize
    def add_bernoulli(self, probability: BMGNode) -> BernoulliNode:
        node = BernoulliNode(probability)
        self.add_node(node)
        return node

    def handle_bernoulli(self, probability: Any) -> BernoulliNode:
        if not isinstance(probability, BMGNode):
            probability = self.add_constant(probability)
        return self.add_bernoulli(probability)

    @memoize
    def add_addition(self, left: BMGNode, right: BMGNode) -> BMGNode:
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return self.add_constant(left.value + right.value)
        node = AdditionNode(left, right)
        self.add_node(node)
        return node

    def handle_addition(self, left: Any, right: Any) -> Any:
        if (not isinstance(left, BMGNode)) and (not isinstance(right, BMGNode)):
            return left + right
        if not isinstance(left, BMGNode):
            left = self.add_constant(left)
        if not isinstance(right, BMGNode):
            right = self.add_constant(right)
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return left.value + right.value
        return self.add_addition(left, right)

    @memoize
    def add_multiplication(self, left: BMGNode, right: BMGNode) -> BMGNode:
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return self.add_constant(left.value * right.value)
        node = MultiplicationNode(left, right)
        self.add_node(node)
        return node

    def handle_multiplication(self, left: Any, right: Any) -> Any:
        if (not isinstance(left, BMGNode)) and (not isinstance(right, BMGNode)):
            return left * right
        if not isinstance(left, BMGNode):
            left = self.add_constant(left)
        if not isinstance(right, BMGNode):
            right = self.add_constant(right)
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return left.value * right.value
        return self.add_multiplication(left, right)

    @memoize
    def add_division(self, left: BMGNode, right: BMGNode) -> BMGNode:
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return self.add_constant(left.value / right.value)
        node = DivisionNode(left, right)
        self.add_node(node)
        return node

    # TODO: Do we need to represent both integer and float division?
    def handle_division(self, left: Any, right: Any) -> Any:
        if (not isinstance(left, BMGNode)) and (not isinstance(right, BMGNode)):
            return left / right
        if not isinstance(left, BMGNode):
            left = self.add_constant(left)
        if not isinstance(right, BMGNode):
            right = self.add_constant(right)
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return left.value / right.value
        return self.add_division(left, right)

    @memoize
    def add_power(self, left: BMGNode, right: BMGNode) -> BMGNode:
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return self.add_constant(left.value ** right.value)
        node = PowerNode(left, right)
        self.add_node(node)
        return node

    def handle_power(self, left: Any, right: Any) -> Any:
        if (not isinstance(left, BMGNode)) and (not isinstance(right, BMGNode)):
            return left ** right
        if not isinstance(left, BMGNode):
            left = self.add_constant(left)
        if not isinstance(right, BMGNode):
            right = self.add_constant(right)
        if isinstance(left, ConstantNode) and isinstance(right, ConstantNode):
            return left.value ** right.value
        return self.add_power(left, right)

    @memoize
    def add_negate(self, operand: BMGNode) -> BMGNode:
        if isinstance(operand, ConstantNode):
            return self.add_constant(-operand.value)
        node = NegateNode(operand)
        self.add_node(node)
        return node

    def handle_negate(self, operand: Any) -> Any:
        if not isinstance(operand, BMGNode):
            return -operand
        if isinstance(operand, ConstantNode):
            return -operand.value
        return self.add_negate(operand)

    # TODO: What should the result of NOT on a tensor be?
    # TODO: Should it be legal at all in the graph?
    # TODO: In Python, (not tensor(x)) is equal to (not x).
    # TODO: It is NOT equal to (tensor(not x)), which is what
    # TODO: you might expect.
    @memoize
    def add_not(self, operand: BMGNode) -> BMGNode:
        if isinstance(operand, ConstantNode):
            return self.add_constant(not operand.value)
        node = NotNode(operand)
        self.add_node(node)
        return node

    def handle_not(self, operand: Any) -> Any:
        if not isinstance(operand, BMGNode):
            return not operand
        if isinstance(operand, ConstantNode):
            return not operand.value
        return self.add_not(operand)

    @memoize
    def add_to_real(self, operand: BMGNode) -> ToRealNode:
        if isinstance(operand, RealNode):
            return operand
        if isinstance(operand, ConstantNode):
            return self.add_real(float(operand.value))
        node = ToRealNode(operand)
        self.add_node(node)
        return node

    def handle_to_real(self, operand: Any) -> Any:
        if not isinstance(operand, BMGNode):
            return float(operand)
        if isinstance(operand, ConstantNode):
            return float(operand.value)
        return self.add_to_real(operand)

    @memoize
    def add_to_tensor(self, operand: BMGNode) -> ToTensorNode:
        node = ToTensorNode(operand)
        self.add_node(node)
        return node

    @memoize
    def add_exp(self, operand: BMGNode) -> ExpNode:
        if isinstance(operand, TensorNode):
            return self.add_constant(torch.exp(operand.value))
        if isinstance(operand, ConstantNode):
            return self.add_constant(math.exp(operand.value))
        node = ExpNode(operand)
        self.add_node(node)
        return node

    def handle_exp(self, operand: Any) -> Any:
        if isinstance(operand, Tensor):
            return torch.exp(operand)
        if isinstance(operand, TensorNode):
            return torch.exp(operand.value)
        if not isinstance(operand, BMGNode):
            return math.exp(operand)
        if isinstance(operand, ConstantNode):
            return math.exp(operand.value)
        return self.add_exp(operand)

    @memoize
    def add_log(self, operand: BMGNode) -> ExpNode:
        if isinstance(operand, TensorNode):
            return self.add_constant(torch.log(operand.value))
        if isinstance(operand, ConstantNode):
            return self.add_constant(math.log(operand.value))
        node = LogNode(operand)
        self.add_node(node)
        return node

    def handle_log(self, operand: Any) -> Any:
        if isinstance(operand, Tensor):
            return torch.log(operand)
        if isinstance(operand, TensorNode):
            return torch.log(operand.value)
        if not isinstance(operand, BMGNode):
            return math.log(operand)
        if isinstance(operand, ConstantNode):
            return math.log(operand.value)
        return self.add_log(operand)

    # TODO: We will need to handle functions with named parameters and
    # starred parameters.
    # TODO: Add the other operators
    def handle_function(self, function: Any, arguments: List[Any]) -> Any:  # noqa
        if isinstance(function, KnownFunction):
            f = function.function
            args = [function.receiver] + arguments
        elif (
            isinstance(function, builtin_function_or_method)
            and isinstance(function.__self__, Tensor)
            and function.__name__ in known_tensor_instance_functions
        ):
            f = getattr(Tensor, function.__name__)
            args = [function.__self__] + arguments
        elif isinstance(function, Callable):
            f = function
            args = arguments
        else:
            raise ValueError(
                f"Function {function} is not supported by Bean Machine Graph."
            )
        if not any(isinstance(arg, BMGNode) for arg in args):
            return f(*args)
        if (f is torch.add) and len(args) == 2:
            return self.handle_addition(args[0], args[1])
        if (f is torch.Tensor.add) and len(args) == 2:
            return self.handle_addition(args[0], args[1])
        if (f is torch.div) and len(args) == 2:
            return self.handle_division(args[0], args[1])
        if (f is torch.Tensor.div) and len(args) == 2:
            return self.handle_division(args[0], args[1])
        # Note that torch.float is not a function.
        if (f is torch.Tensor.float) and len(args) == 1:
            return self.handle_to_real(args[0])
        if (f is torch.logical_not) and len(args) == 1:
            return self.handle_not(args[0])
        if (f is torch.Tensor.logical_not) and len(args) == 1:
            return self.handle_not(args[0])
        if (f is torch.mul) and len(args) == 2:
            return self.handle_multiplication(args[0], args[1])
        if (f is torch.Tensor.mul) and len(args) == 2:
            return self.handle_multiplication(args[0], args[1])
        if (f is torch.neg) and len(args) == 1:
            return self.handle_negate(args[0])
        if (f is torch.Tensor.neg) and len(args) == 1:
            return self.handle_negate(args[0])
        if (f is torch.pow) and len(args) == 2:
            return self.handle_power(args[0], args[1])
        if (f is torch.Tensor.pow) and len(args) == 2:
            return self.handle_power(args[0], args[1])
        if (f is torch.log) and len(args) == 1:
            return self.handle_log(args[0])
        if (f is torch.Tensor.log) and len(args) == 1:
            return self.handle_log(args[0])
        if (f is math.log) and len(args) == 1:
            return self.handle_log(args[0])
        if (f is torch.exp) and len(args) == 1:
            return self.handle_exp(args[0])
        if (f is torch.Tensor.exp) and len(args) == 1:
            return self.handle_exp(args[0])
        if (f is math.exp) and len(args) == 1:
            return self.handle_exp(args[0])
        if (f is Bernoulli) and len(args) == 1:
            return self.handle_bernoulli(args[0])
        raise ValueError(f"Function {f} is not supported by Bean Machine Graph.")

    # TODO: Do NOT memoize add_list; if we eventually add a list node to the
    # TODO: underlying graph, revisit this decision.
    def add_list(self, elements: List[BMGNode]) -> ExpNode:
        node = ListNode(elements)
        self.add_node(node)
        return node

    # Do NOT memoize add_sample; each sample node must be unique
    def add_sample(self, operand: DistributionNode) -> SampleNode:
        node = SampleNode(operand)
        self.add_node(node)
        return node

    def handle_sample(self, operand: Any) -> SampleNode:
        if isinstance(operand, DistributionNode):
            return self.add_sample(operand)
        if isinstance(operand, Bernoulli):
            b = self.handle_bernoulli(operand.probs)
            return self.add_sample(b)
        raise ValueError(
            f"Operand {str(operand)} is not a valid target for a sample operation."
        )

    def handle_dot_get(self, operand: Any, name: str) -> Any:
        # If we have x = foo.bar, foo must not be a sample; we have no way of
        # representing the "get the value of an attribute" operation in BMG.
        # However, suppose foo is a distribution of tensors; we do wish to support
        # operations such as:
        # x = foo.exp
        # y = x()
        # and have y be a graph that applies an EXP node to the SAMPLE node for foo.
        # This will require some cooperation between handling dots and handling
        # functions.

        # TODO: There are a great many more pure instance functions on tensors;
        # TODO: which do we wish to support?

        if isinstance(operand, BMGNode):
            if operand.node_type() == Tensor:
                if name in known_tensor_instance_functions:
                    return KnownFunction(operand, getattr(Tensor, name))
            raise ValueError(
                f"Fetching the value of attribute {name} is not "
                + "supported in Bean Machine Graph."
            )
        return getattr(operand, name)

    def handle_dot_set(self, operand: Any, name: str, value: Any) -> None:
        # If we have foo.bar = x, foo must not be a sample; we have no way of
        # representing the "set the value of an attribute" operation in BMG.
        if isinstance(operand, BMGNode):
            raise ValueError(
                f"Setting the value of attribute {name} is not "
                + "supported in Bean Machine Graph."
            )
        setattr(operand, name, value)

    def add_observation(self, observed: SampleNode, value: ConstantNode) -> Observation:
        node = Observation(observed, value)
        self.add_node(node)
        return node

    def add_query(self, operator: OperatorNode) -> Query:
        node = Query(operator)
        self.add_node(node)
        return node

    def to_dot(self) -> str:
        db = DotBuilder()
        for node, index in self.nodes.items():
            n = "N" + str(index)
            db.with_node(n, node.label())
            for (child, label) in zip(node.children, node.edges):
                db.with_edge(n, "N" + str(self.nodes[child]), label)
        return str(db)

    def to_bmg(self) -> Graph:
        g = Graph()
        d: Dict[BMGNode, int] = {}
        for node in self.nodes:
            d[node] = node._add_to_graph(g, d)
        return g

    def to_python(self) -> str:
        header = """from beanmachine import graph
from torch import tensor
g = graph.Graph()
"""
        return header + "\n".join(n._to_python(self.nodes) for n in self.nodes)

    def to_cpp(self) -> str:
        return "graph::Graph g;\n" + "\n".join(
            n._to_cpp(self.nodes) for n in self.nodes
        )
