# Copyright (c) Facebook, Inc. and its affiliates.

"""This module takes a Bean Machine Graph builder and makes a best
effort attempt to transform the accumulated graph to meet the
requirements of the BMG type system. All possible transformations
are made; if there are nodes that cannot be represented in BMG
or cannot be made to meet type requirements, an error report is
returned."""


import beanmachine.ppl.compiler.bmg_nodes as bn
import beanmachine.ppl.compiler.bmg_types as bt
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
from beanmachine.ppl.compiler.bmg_requirements import EdgeRequirements
from beanmachine.ppl.compiler.error_report import ErrorReport, Violation
from beanmachine.ppl.compiler.graph_labels import get_edge_labels
from beanmachine.ppl.compiler.lattice_typer import LatticeTyper


class RequirementsFixer:
    """This class takes a Bean Machine Graph builder and attempts to
    fix violations of BMG type system requirements.

    The basic idea is that every *edge* in the graph has a *requirement*, such as
    "the type of the input must be Probability".  We do a traversal of the input
    edges of every node in the graph; if the input node meets the requirement,
    it is unchanged. If it does not, then a new node that has the same semantics
    that meets the requirement is returned. If there is no such node then an
    error is added to the error report."""

    errors: ErrorReport
    bmg: BMGraphBuilder
    _typer: LatticeTyper
    _reqs: EdgeRequirements

    def __init__(self, bmg: BMGraphBuilder, typer: LatticeTyper) -> None:
        self.errors = ErrorReport()
        self.bmg = bmg
        self._typer = typer
        self._reqs = EdgeRequirements(typer)

    def _type_meets_requirement(self, t: bt.BMGLatticeType, r: bt.Requirement) -> bool:
        assert t != bt.Untypable
        if isinstance(r, bt.AnyRequirement):
            return True
        if isinstance(r, bt.UpperBound):
            return bt.supremum(t, r.bound) == r.bound
        if isinstance(r, bt.AlwaysMatrix):
            return t == r.bound
        return t == r

    def _node_meets_requirement(self, node: bn.BMGNode, r: bt.Requirement) -> bool:
        if isinstance(r, bt.AlwaysMatrix):
            return self._typer.is_matrix(node) and self._type_meets_requirement(
                self._typer[node], r.bound
            )
        return self._type_meets_requirement(self._typer[node], r)

    def _meet_constant_requirement(
        self,
        node: bn.ConstantNode,
        requirement: bt.Requirement,
        consumer: bn.BMGNode,
        edge: str,
    ) -> bn.BMGNode:
        # We have a constant node that either (1) is untyped, and therefore
        # needs to be replaced by an equivalent typed node, or (2) is typed
        # but is of the wrong type, and needs to be replaced by an equivalent
        # constant of a larger type.
        #
        # Obtain a type for the node. If the node meets an upper bound requirement
        # then it has a value that can be converted to the desired type.  If it
        # does not meet an UB requirement then there is no equivalent constant
        # node of the correct type and we give an error.
        it = self._typer[node]
        if self._type_meets_requirement(it, bt.upper_bound(requirement)):
            required_type = bt.requirement_to_type(requirement)
            if bt.must_be_matrix(requirement):
                assert isinstance(required_type, bt.BMGMatrixType)
                result = self.bmg.add_constant_of_matrix_type(node.value, required_type)
            else:
                result = self.bmg.add_constant_of_type(node.value, required_type)
            assert self._node_meets_requirement(result, requirement)
            return result

        # We cannot convert this node to any type that meets the requirement.
        # Add an error.
        self.errors.add_error(Violation(node, it, requirement, consumer, edge))
        return node

    def _convert_operator_to_atomic_type(
        self,
        node: bn.OperatorNode,
        requirement: bt.BMGLatticeType,
        consumer: bn.BMGNode,
        edge: str,
    ) -> bn.BMGNode:
        # We have been given a node which does not meet a requirement,
        # but it can be converted to a node which does meet the requirement
        # that has the same semantics. Start by confirming those preconditions.
        node_type = self._typer[node]
        assert node_type != requirement
        assert bt.is_convertible_to(node_type, requirement)

        # Converting anything to real or positive real is easy;
        # there's already a node for that so just insert it on the edge
        # whose requirement is not met, and the requirement will be met.

        if requirement == bt.Real:
            return self.bmg.add_to_real(node)
        if requirement == bt.PositiveReal:
            return self.bmg.add_to_positive_real(node)

        # We are not converting to real or positive real.
        # Our precondition is that the requirement is larger than
        # *something*, which means that it cannot be bool.
        # That means the requirement must be either natural or
        # probability. Verify this.

        assert requirement == bt.Natural or requirement == bt.Probability

        # Our precondition is that the requirement is larger than the
        # node type.

        assert node_type == bt.Boolean

        # There is no "to natural" or "to probability" but since we have
        # a bool in hand, we can use an if-then-else as a conversion.

        zero = self.bmg.add_constant_of_type(0.0, requirement)
        one = self.bmg.add_constant_of_type(1.0, requirement)
        return self.bmg.add_if_then_else(node, one, zero)

    def _convert_operator_to_matrix_type(
        self,
        node: bn.OperatorNode,
        requirement: bt.Requirement,
        consumer: bn.BMGNode,
        edge: str,
    ) -> bn.BMGNode:
        if isinstance(requirement, bt.AlwaysMatrix):
            requirement = requirement.bound
        assert isinstance(requirement, bt.BMGMatrixType)

        # We have been given a node which does not meet a requirement,
        # but it can be converted to a node which does meet the requirement
        # that has the same semantics. Start by confirming those preconditions.
        node_type = self._typer[node]
        assert node_type != requirement
        assert bt.is_convertible_to(node_type, requirement)

        # Converting anything to real matrix or positive real matrix is easy;
        # there's already a node for that so just insert it on the edge
        # whose requirement is not met, and the requirement will be met.

        # TODO: We do not yet handle the case where we are converting from, say,
        # an atomic probability to a 1x1 real matrix because in practice this
        # hasn't come up yet. If it does, detect it here and insert a TO_REAL
        # or TO_POS_REAL followed by a TO_MATRIX and create a test case that
        # illustrates the scenario.
        assert self._typer.is_matrix(node)

        if isinstance(requirement, bt.RealMatrix):
            return self.bmg.add_to_real_matrix(node)

        # TODO: We do not yet handle the case where we are converting from
        # a matrix of bools to a matrix of naturals or probabilities because
        # in practice this has not come up yet. If it does, we will need
        # to create TO_NATURAL_MATRIX and TO_PROB_MATRIX operators in BMG, or
        # come up with some other way to turn many bools into many naturals
        # or probabilities.
        assert isinstance(requirement, bt.PositiveRealMatrix)

        return self.bmg.add_to_positive_real_matrix(node)

    def _can_force_to_prob(
        self, inf_type: bt.BMGLatticeType, requirement: bt.Requirement
    ) -> bool:
        # Consider the graph created by a call like:
        #
        # Bernoulli(0.5 + some_beta() / 2)
        #
        # The inf types of the addends are both probability, but there is
        # no addition operator on probabilities; we will add these as
        # positive reals, and then get an error when we use it as the parameter
        # to a Bernoulli.  But you and I both know that this is a legal
        # probability.
        #
        # To work around this problem, if we have a *real* or *positive real* used
        # in a situation where a *probability* is required, we insert an explicit
        # "clamp this real to a probability" operation.
        #
        # TODO: We might want to restrict this. For example, if we have
        #
        # Bernoulli(some_normal())
        #
        # then it seems plausible that we ought to produce an error here rather than
        # clamping the result to a probability. We could allow this feature only
        # in situations where there was some operator other than a sample, for instance.
        #
        # TODO: We might want to build a warning mechanism that informs the developer
        # of the possibility that they've gotten something wrong here.
        return (
            requirement == bt.Probability
            or requirement == bt.upper_bound(bt.Probability)
        ) and (inf_type == bt.Real or inf_type == bt.PositiveReal)

    def _meet_operator_requirement(
        self,
        node: bn.OperatorNode,
        requirement: bt.Requirement,
        consumer: bn.BMGNode,
        edge: str,
    ) -> bn.BMGNode:
        # If the operator node already meets the requirement, we're done.
        assert not self._node_meets_requirement(node, requirement)

        # It does not meet the requirement. Can we convert this thing to a node
        # whose type does meet the requirement? The lattice type is the
        # smallest type that this node is convertible to, so if the lattice type
        # meets an upper bound requirement, then the conversion we want exists.

        node_type = self._typer[node]
        if self._type_meets_requirement(node_type, bt.upper_bound(requirement)):
            # If we got here then the node did NOT meet the requirement,
            # but its type DID meet an upper bound requirement, which
            # implies that the requirement was not an upper bound requirement.
            assert not isinstance(requirement, bt.UpperBound)

            # We definitely can meet the requirement by inserting some sort
            # of conversion logic. We have different helper methods for
            # the atomic type and matrix type cases.
            if bt.must_be_matrix(requirement):
                result = self._convert_operator_to_matrix_type(
                    node, requirement, consumer, edge
                )
            else:
                assert isinstance(requirement, bt.BMGLatticeType)
                result = self._convert_operator_to_atomic_type(
                    node, requirement, consumer, edge
                )
        elif self._can_force_to_prob(node_type, requirement):
            # We cannot make the node meet the requirement "implicitly". However
            # there is one situation where we can "explicitly" meet a requirement:
            # an operator of type real or positive real used as a probability.
            assert node_type == bt.Real or node_type == bt.PositiveReal
            assert self._node_meets_requirement(node, node_type)
            result = self.bmg.add_to_probability(node)
        else:
            # We have no way to make the conversion we need, so add an error.
            self.errors.add_error(
                Violation(node, node_type, requirement, consumer, edge)
            )
            return node

        assert self._node_meets_requirement(result, requirement)
        return result

    def meet_requirement(
        self,
        node: bn.BMGNode,
        requirement: bt.Requirement,
        consumer: bn.BMGNode,
        edge: str,
    ) -> bn.BMGNode:
        """The consumer node consumes the value of the input node. The consumer's
        requirement is given; the name of this edge is provided for error reporting."""

        # These lattice types should never be used as requirements.
        assert requirement not in {bt.Tensor, bt.One, bt.Zero, bt.Untypable}

        # There is never a requirement on these nodes because they only have
        # input edges.
        assert not isinstance(node, bn.Observation)
        assert not isinstance(node, bn.Query)
        assert not isinstance(node, bn.FactorNode)

        # If we have an untyped constant node we always need to replace it.
        if isinstance(node, bn.UntypedConstantNode):
            return self._meet_constant_requirement(node, requirement, consumer, edge)

        # If the node already meets the requirement, we're done.
        if self._node_meets_requirement(node, requirement):
            return node

        # In normal operation we should never insert a typed constant node
        # that is of the wrong type, but we have a few test cases in which
        # we do so explicitly. Regardless, it is not a problem to convert a
        # typed constant to the correct type.
        if isinstance(node, bn.ConstantNode):
            return self._meet_constant_requirement(node, requirement, consumer, edge)

        # A distribution's outgoing edges are only queries and their requirements
        # are always met, so we should have already returned. Therefore the only
        # remaining possibility is that we have an operator.
        assert isinstance(node, bn.OperatorNode)
        return self._meet_operator_requirement(node, requirement, consumer, edge)

    def fix_problems(self) -> None:
        nodes = self.bmg.all_ancestor_nodes()
        for node in nodes:
            requirements = self._reqs.requirements(node)
            # TODO: The edge labels used to visualize the graph in DOT
            # are not necessarily the best ones for displaying errors.
            # Consider fixing this.
            edges = get_edge_labels(node)
            node_was_updated = False
            for i in range(len(requirements)):
                new_input = self.meet_requirement(
                    node.inputs[i], requirements[i], node, edges[i]
                )
                if node.inputs[i] is not new_input:
                    node.inputs[i] = new_input
                    node_was_updated = True
            if node_was_updated:
                self._typer.update_type(node)