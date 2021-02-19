# Copyright (c) Facebook, Inc. and its affiliates.
"""Tests for bm_to_bmg.py"""
import unittest

import astor
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
from beanmachine.ppl.compiler.bm_to_bmg import (
    _bm_function_to_bmg_function,
    to_bmg,
    to_cpp,
    to_dot,
    to_python,
    to_python_raw,
)


# flake8 does not provide any mechanism to disable warnings in
# multi-line strings, so just turn it off for this file.
# flake8: noqa


def tidy(s: str) -> str:
    return "\n".join(c.strip() for c in s.strip().split("\n")).strip()


source2 = """
import beanmachine.ppl as bm
import torch
from torch import exp, log, tensor, neg
from torch.distributions import Bernoulli


@bm.random_variable
def x(n):
    return Bernoulli(probs=tensor(0.5) + log(input=exp(input=n * tensor(0.1))))


@bm.random_variable
def z():
    return Bernoulli(
        tensor(0.3) ** x(0) + x(0) / tensor(10.0) - neg(x(1) * tensor(0.4))
    )
"""

# In the medium term, we need to create a mechanism in BMG to represent
# "random variable with index".  This in particular will be necessary
# for scenarios like "Bernoulli(y(x())"; suppose x is a random variable
# either True and False and y(n) is a random variable that takes in True
# or False and produces a sample from 0.0 to 1.0. We do not have
# a way in BMG today to represent this because we require exactly as many
# sample nodes in the graph as there are samples in the program.
#
# However, because we do hoist the indices of x(0) and x(1) as nodes
# in the graph here, and because nodes are deduplicated, we end
# up doing the right thing when the indices are constants.

expected_raw_2 = """
from beanmachine.ppl.utils.memoize import memoize
from beanmachine.ppl.utils.probabilistic import probabilistic
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
_lifted_to_bmg: bool = True
bmg = BMGraphBuilder()
import torch
from torch import exp, log, tensor, neg
from torch.distributions import Bernoulli


@probabilistic(bmg)
@memoize
def x(n):
    a11 = 0.5
    r8 = [a11]
    a4 = bmg.handle_function(tensor, [*r8], {})
    a25 = 0.1
    r21 = [a25]
    a15 = bmg.handle_function(tensor, [*r21], {})
    a12 = bmg.handle_multiplication(n, a15)
    a9 = bmg.handle_function(exp, [], {**{'input': a12}})
    a6 = bmg.handle_function(log, [], {**{'input': a9}})
    a3 = bmg.handle_addition(a4, a6)
    r1 = bmg.handle_function(Bernoulli, [], {**{'probs': a3}})
    return bmg.handle_sample(r1)


@probabilistic(bmg)
@memoize
def z():
    a26 = 0.3
    r22 = [a26]
    a16 = bmg.handle_function(tensor, [*r22], {})
    a30 = 0
    r27 = [a30]
    a19 = bmg.handle_function(x, [*r27], {})
    a13 = bmg.handle_power(a16, a19)
    a31 = 0
    r28 = [a31]
    a20 = bmg.handle_function(x, [*r28], {})
    a34 = 10.0
    r32 = [a34]
    a23 = bmg.handle_function(tensor, [*r32], {})
    a17 = bmg.handle_division(a20, a23)
    a10 = bmg.handle_addition(a13, a17)
    a37 = 1
    r36 = [a37]
    a33 = bmg.handle_function(x, [*r36], {})
    a39 = 0.4
    r38 = [a39]
    a35 = bmg.handle_function(tensor, [*r38], {})
    a29 = bmg.handle_multiplication(a33, a35)
    r24 = [a29]
    a18 = bmg.handle_function(neg, [*r24], {})
    a14 = bmg.handle_negate(a18)
    a7 = bmg.handle_addition(a10, a14)
    r5 = [a7]
    r2 = bmg.handle_function(Bernoulli, [*r5], {})
    return bmg.handle_sample(r2)


roots = [z()]
"""

expected_dot_2 = """
digraph "graph" {
  N00[label=0.5];
  N01[label=Bernoulli];
  N02[label=Sample];
  N03[label=0.30000001192092896];
  N04[label="**"];
  N05[label=10.0];
  N06[label="/"];
  N07[label="+"];
  N08[label=0.6000000238418579];
  N09[label=Bernoulli];
  N10[label=Sample];
  N11[label=0.4000000059604645];
  N12[label="*"];
  N13[label="-"];
  N14[label="-"];
  N15[label="+"];
  N16[label=Bernoulli];
  N17[label=Sample];
  N01 -> N00[label=probability];
  N02 -> N01[label=operand];
  N04 -> N02[label=right];
  N04 -> N03[label=left];
  N06 -> N02[label=left];
  N06 -> N05[label=right];
  N07 -> N04[label=left];
  N07 -> N06[label=right];
  N09 -> N08[label=probability];
  N10 -> N09[label=operand];
  N12 -> N10[label=left];
  N12 -> N11[label=right];
  N13 -> N12[label=operand];
  N14 -> N13[label=operand];
  N15 -> N07[label=left];
  N15 -> N14[label=right];
  N16 -> N15[label=probability];
  N17 -> N16[label=operand];
}
"""


# Demonstrate that function calls work as expected when the
# function called is NOT a sample function.
source5 = """
import beanmachine.ppl as bm
import torch
from torch.distributions import Bernoulli

# NOTE NO RV HERE
def q(a, b):
  return (a + b) * 0.5

# NOTE NO RV HERE
def r(p):
  return Bernoulli(p)

@bm.random_variable
def x(n):
  return Bernoulli(0.5)

@bm.random_variable
def z():
  return r(q(x(0), x(1)))
"""

expected_raw_5 = """
from beanmachine.ppl.utils.memoize import memoize
from beanmachine.ppl.utils.probabilistic import probabilistic
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
_lifted_to_bmg: bool = True
bmg = BMGraphBuilder()
import beanmachine.ppl as bm
import torch
from torch.distributions import Bernoulli


def q(a, b):
    a5 = bmg.handle_addition(a, b)
    a6 = 0.5
    r1 = bmg.handle_multiplication(a5, a6)
    return r1


def r(p):
    r7 = [p]
    r12 = {}
    r2 = bmg.handle_function(Bernoulli, r7, r12)
    return r2


@probabilistic(bmg)
@memoize
def x(n):
    a10 = 0.5
    r8 = [a10]
    r13 = {}
    r3 = bmg.handle_function(Bernoulli, r8, r13)
    return bmg.handle_sample(r3)


@probabilistic(bmg)
@memoize
def z():
    a22 = 0
    r21 = [a22]
    r24 = {}
    a17 = bmg.handle_function(x, r21, r24)
    a16 = [a17]
    a25 = 1
    r23 = [a25]
    r26 = {}
    a20 = bmg.handle_function(x, r23, r26)
    a18 = [a20]
    r15 = bmg.handle_addition(a16, a18)
    r19 = {}
    a11 = bmg.handle_function(q, r15, r19)
    r9 = [a11]
    r14 = {}
    r4 = bmg.handle_function(r, r9, r14)
    return bmg.handle_sample(r4)


roots = [z()]"""

expected_dot_5 = """
digraph "graph" {
  N0[label=0.5];
  N1[label=Bernoulli];
  N2[label=Sample];
  N3[label=Sample];
  N4[label="+"];
  N5[label=0.5];
  N6[label="*"];
  N7[label=Bernoulli];
  N8[label=Sample];
  N1 -> N0[label=probability];
  N2 -> N1[label=operand];
  N3 -> N1[label=operand];
  N4 -> N2[label=left];
  N4 -> N3[label=right];
  N6 -> N4[label=left];
  N6 -> N5[label=right];
  N7 -> N6[label=probability];
  N8 -> N7[label=operand];
}
"""

# Here is a simple model where the argument to a sample is itself a sample.
# This illustrates how the graph must capture the possible control flows.
# Flip a fair coin y; use that to choose which unfair coin to use.
# Flip the unfair coin and use that to construct either a double-headed
# or double-tailed coin.
source6 = """
import beanmachine.ppl as bm
import torch
from torch.distributions import Bernoulli

# x(0) is Bern(0.25)
# x(1) is Bern(0.75)
@bm.random_variable
def x(n):
  return Bernoulli(n * 0.5 + 0.25)

@bm.random_variable
def y():
  return Bernoulli(0.5)

@bm.random_variable
def z():
  return Bernoulli(x(y()))
"""

expected_raw_6 = """
from beanmachine.ppl.utils.memoize import memoize
from beanmachine.ppl.utils.probabilistic import probabilistic
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
_lifted_to_bmg: bool = True
bmg = BMGraphBuilder()
import beanmachine.ppl as bm
import torch
from torch.distributions import Bernoulli


@probabilistic(bmg)
@memoize
def x(n):
    a14 = 0.5
    a10 = bmg.handle_multiplication(n, a14)
    a15 = 0.25
    a7 = bmg.handle_addition(a10, a15)
    r4 = [a7]
    r11 = {}
    r1 = bmg.handle_function(Bernoulli, r4, r11)
    return bmg.handle_sample(r1)


@probabilistic(bmg)
@memoize
def y():
    a8 = 0.5
    r5 = [a8]
    r12 = {}
    r2 = bmg.handle_function(Bernoulli, r5, r12)
    return bmg.handle_sample(r2)


@probabilistic(bmg)
@memoize
def z():
    r19 = []
    r20 = {}
    a17 = bmg.handle_function(y, r19, r20)
    r16 = [a17]
    r18 = {}
    a9 = bmg.handle_function(x, r16, r18)
    r6 = [a9]
    r13 = {}
    r3 = bmg.handle_function(Bernoulli, r6, r13)
    return bmg.handle_sample(r3)


roots = [y(), z()]
"""

expected_dot_6 = """
digraph "graph" {
  N00[label=0.5];
  N01[label=Bernoulli];
  N02[label=Sample];
  N03[label=0.25];
  N04[label=Bernoulli];
  N05[label=Sample];
  N06[label=0.0];
  N07[label=0.75];
  N08[label=Bernoulli];
  N09[label=Sample];
  N10[label=1.0];
  N11[label=map];
  N12[label=index];
  N13[label=Bernoulli];
  N14[label=Sample];
  N01 -> N00[label=probability];
  N02 -> N01[label=operand];
  N04 -> N03[label=probability];
  N05 -> N04[label=operand];
  N08 -> N07[label=probability];
  N09 -> N08[label=operand];
  N11 -> N05[label=1];
  N11 -> N06[label=0];
  N11 -> N09[label=3];
  N11 -> N10[label=2];
  N12 -> N02[label=right];
  N12 -> N11[label=left];
  N13 -> N12[label=probability];
  N14 -> N13[label=operand];
}
"""

# Neal's funnel
source7 = """
import beanmachine.ppl as bm
from torch.distributions import Normal
from torch import exp

@bm.random_variable
def X():
  return Normal(0.0, 3.0)

@bm.random_variable
def Y():
    return Normal(loc=0.0, scale=exp(X() * 0.5))
"""

expected_raw_7 = """
from beanmachine.ppl.utils.memoize import memoize
from beanmachine.ppl.utils.probabilistic import probabilistic
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
_lifted_to_bmg: bool = True
bmg = BMGraphBuilder()
from torch.distributions import Normal
from torch import exp


@probabilistic(bmg)
@memoize
def X():
    a9 = 0.0
    a7 = [a9]
    a12 = 3.0
    a10 = [a12]
    r5 = bmg.handle_addition(a7, a10)
    r1 = bmg.handle_function(Normal, [*r5], {})
    return bmg.handle_sample(r1)


@probabilistic(bmg)
@memoize
def Y():
    a3 = 0.0
    a11 = bmg.handle_function(X, [], {})
    a13 = 0.5
    a8 = bmg.handle_multiplication(a11, a13)
    r6 = [a8]
    a4 = bmg.handle_function(exp, [*r6], {})
    r2 = bmg.handle_function(Normal, [], {**{'loc': a3}, **{'scale': a4}})
    return bmg.handle_sample(r2)


roots = [X(), Y()]
"""

expected_dot_7 = """
digraph "graph" {
  N0[label=0.0];
  N1[label=3.0];
  N2[label=Normal];
  N3[label=Sample];
  N4[label=0.5];
  N5[label="*"];
  N6[label=Exp];
  N7[label=0.0];
  N8[label=Normal];
  N9[label=Sample];
  N2 -> N0[label=mu];
  N2 -> N1[label=sigma];
  N3 -> N2[label=operand];
  N5 -> N3[label=left];
  N5 -> N4[label=right];
  N6 -> N5[label=operand];
  N8 -> N6[label=sigma];
  N8 -> N7[label=mu];
  N9 -> N8[label=operand];
}
"""


# Testing support for calls with keyword args
source9 = """
import beanmachine.ppl as bm
from torch.distributions import Bernoulli

@bm.random_variable
def toss():
    return Bernoulli(probs=0.5)

# Notice that logits Bernoulli with constant argument is folded to
# probs Bernoulli...
@bm.random_variable
def toss2():
    return Bernoulli(logits=0.0)

# ...but we must make a distinction between logits and probs if the
# argument is a sample.
@bm.random_variable
def toss3():
    return Bernoulli(probs=toss())

@bm.random_variable
def toss4():
    return Bernoulli(logits=toss())
"""

expected_raw_9 = """
from beanmachine.ppl.utils.memoize import memoize
from beanmachine.ppl.utils.probabilistic import probabilistic
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
_lifted_to_bmg: bool = True
bmg = BMGraphBuilder()
from torch.distributions import Bernoulli


@probabilistic(bmg)
@memoize
def toss():
    a5 = 0.5
    r1 = bmg.handle_function(Bernoulli, [], {**{'probs': a5}})
    return bmg.handle_sample(r1)


@probabilistic(bmg)
@memoize
def toss2():
    a6 = 0.0
    r2 = bmg.handle_function(Bernoulli, [], {**{'logits': a6}})
    return bmg.handle_sample(r2)


@probabilistic(bmg)
@memoize
def toss3():
    a7 = bmg.handle_function(toss, [], {})
    r3 = bmg.handle_function(Bernoulli, [], {**{'probs': a7}})
    return bmg.handle_sample(r3)


@probabilistic(bmg)
@memoize
def toss4():
    a8 = bmg.handle_function(toss, [], {})
    r4 = bmg.handle_function(Bernoulli, [], {**{'logits': a8}})
    return bmg.handle_sample(r4)


roots = [toss(), toss2(), toss3(), toss4()]
"""

expected_dot_9 = """
digraph "graph" {
  N0[label=0.5];
  N1[label=Bernoulli];
  N2[label=Sample];
  N3[label=Sample];
  N4[label=Bernoulli];
  N5[label=Sample];
  N6[label="Bernoulli(logits)"];
  N7[label=Sample];
  N1 -> N0[label=probability];
  N2 -> N1[label=operand];
  N3 -> N1[label=operand];
  N4 -> N2[label=probability];
  N5 -> N4[label=operand];
  N6 -> N2[label=probability];
  N7 -> N6[label=operand];
}
"""

# Bayesian regression
source10 = """
import beanmachine.ppl as bm
from torch import tensor, zeros
from torch.distributions import Normal, Bernoulli
N = 3
K = 2
X = tensor([[1.0, 10, 20], [1.0, -100, -190], [1.0, -101, -192]])
intercept_scale = 0.9
coef_scale = [1.2, 2.3]

@bm.random_variable
def beta():
    return Normal(
        zeros((K + 1, 1)), tensor([intercept_scale] + coef_scale).view(K + 1, 1)
    )

@bm.random_variable
def y():
    return Bernoulli(logits=X.mm(beta()))
"""

expected_raw_10 = """
from beanmachine.ppl.utils.memoize import memoize
from beanmachine.ppl.utils.probabilistic import probabilistic
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
_lifted_to_bmg: bool = True
bmg = BMGraphBuilder()
from torch import tensor, zeros
from torch.distributions import Normal, Bernoulli
N = 3
K = 2
a9 = 1.0
a14 = 10
a19 = 20
a5 = [a9, a14, a19]
a15 = 1.0
a20 = -100
a24 = -190
a10 = [a15, a20, a24]
a21 = 1.0
a25 = -101
a29 = -192
a16 = [a21, a25, a29]
a1 = [a5, a10, a16]
X = bmg.handle_function(tensor, [a1], {})
intercept_scale = 0.9
a2 = 1.2
a6 = 2.3
coef_scale = [a2, a6]


@probabilistic(bmg)
@memoize
def beta():
    a11 = K + 1, 1
    a7 = bmg.handle_function(zeros, [a11], {})
    a30 = [intercept_scale]
    a26 = bmg.handle_addition(a30, coef_scale)
    a22 = bmg.handle_function(tensor, [a26], {})
    a17 = bmg.handle_dot_get(a22, 'view')
    a27 = 1
    a23 = bmg.handle_addition(K, a27)
    a28 = 1
    a12 = bmg.handle_function(a17, [a23, a28], {})
    r3 = bmg.handle_function(Normal, [a7, a12], {})
    return bmg.handle_sample(r3)


@probabilistic(bmg)
@memoize
def y():
    a13 = bmg.handle_dot_get(X, 'mm')
    a18 = bmg.handle_function(beta, [], {})
    a8 = bmg.handle_function(a13, [a18], {})
    r4 = bmg.handle_function(Bernoulli, [], {**{'logits': a8}})
    return bmg.handle_sample(r4)


roots = [beta(), y()]
"""

expected_dot_10 = """
digraph "graph" {
  N0[label="[[0.0],\\\\n[0.0],\\\\n[0.0]]"];
  N1[label="[[0.8999999761581421],\\\\n[1.2000000476837158],\\\\n[2.299999952316284]]"];
  N2[label=Normal];
  N3[label=Sample];
  N4[label="[[1.0,10.0,20.0],\\\\n[1.0,-100.0,-190.0],\\\\n[1.0,-101.0,-192.0]]"];
  N5[label="*"];
  N6[label="Bernoulli(logits)"];
  N7[label=Sample];
  N2 -> N0[label=mu];
  N2 -> N1[label=sigma];
  N3 -> N2[label=operand];
  N5 -> N3[label=right];
  N5 -> N4[label=left];
  N6 -> N5[label=probability];
  N7 -> N6[label=operand];
}
"""

# A sketch of a model for predicting if a new account is fake based on
# friend requests issued and accepted.
source11 = """
import beanmachine.ppl as bm
from torch import tensor
from torch.distributions import Bernoulli
FAKE_PRIOR = 0.001
# One entry per user
FAKE_REQ_PROB = tensor([0.01, 0.02, 0.03])
REAL_REQ_PROB = tensor([0.04, 0.05, 0.06])
REQ_PROB = [REAL_REQ_PROB, FAKE_REQ_PROB]
REAL_ACC_PROB = tensor([0.99, 0.50, 0.07])
@bm.random_variable
def is_fake(account):
  return Bernoulli(FAKE_PRIOR)
@bm.random_variable
def all_requests_sent(account):
  return Bernoulli(REQ_PROB[is_fake(account)])
@bm.random_variable
def all_requests_accepted(account):
  return Bernoulli(REAL_ACC_PROB * all_requests_sent(account))
_1 = 0
_2 = all_requests_accepted(_1)
"""

expected_raw_11 = """
import beanmachine.ppl as bm
from beanmachine.ppl.utils.memoize import memoize
from beanmachine.ppl.utils.probabilistic import probabilistic
from beanmachine.ppl.compiler.bm_graph_builder import BMGraphBuilder
_lifted_to_bmg: bool = True
bmg = BMGraphBuilder()
from torch import tensor
from torch.distributions import Bernoulli
FAKE_PRIOR = 0.001
a14 = 0.01
a19 = 0.02
a24 = 0.03
a8 = [a14, a19, a24]
r4 = [a8]
FAKE_REQ_PROB = bmg.handle_function(tensor, [*r4], {})
a15 = 0.04
a20 = 0.05
a25 = 0.06
a9 = [a15, a20, a25]
r5 = [a9]
REAL_REQ_PROB = bmg.handle_function(tensor, [*r5], {})
REQ_PROB = [REAL_REQ_PROB, FAKE_REQ_PROB]
a16 = 0.99
a21 = 0.5
a26 = 0.07
a10 = [a16, a21, a26]
r6 = [a10]
REAL_ACC_PROB = bmg.handle_function(tensor, [*r6], {})


@probabilistic(bmg)
@memoize
def is_fake(account):
    r11 = [FAKE_PRIOR]
    r1 = bmg.handle_function(Bernoulli, [*r11], {})
    return bmg.handle_sample(r1)


@probabilistic(bmg)
@memoize
def all_requests_sent(account):
    r27 = [account]
    a22 = bmg.handle_function(is_fake, [*r27], {})
    a17 = bmg.handle_index(REQ_PROB, a22)
    r12 = [a17]
    r2 = bmg.handle_function(Bernoulli, [*r12], {})
    return bmg.handle_sample(r2)


@probabilistic(bmg)
@memoize
def all_requests_accepted(account):
    r28 = [account]
    a23 = bmg.handle_function(all_requests_sent, [*r28], {})
    a18 = bmg.handle_multiplication(REAL_ACC_PROB, a23)
    r13 = [a18]
    r3 = bmg.handle_function(Bernoulli, [*r13], {})
    return bmg.handle_sample(r3)


_1 = 0
r7 = [_1]
_2 = bmg.handle_function(all_requests_accepted, [*r7], {})
roots = []
"""

expected_dot_11 = """
digraph "graph" {
  N00[label=0.0010000000474974513];
  N01[label=Bernoulli];
  N02[label=Sample];
  N03[label=0];
  N04[label="[0.03999999910593033,0.05000000074505806,0.05999999865889549]"];
  N05[label=1];
  N06[label="[0.009999999776482582,0.019999999552965164,0.029999999329447746]"];
  N07[label=map];
  N08[label=index];
  N09[label=Bernoulli];
  N10[label=Sample];
  N11[label="[0.9900000095367432,0.5,0.07000000029802322]"];
  N12[label="*"];
  N13[label=Bernoulli];
  N14[label=Sample];
  N01 -> N00[label=probability];
  N02 -> N01[label=operand];
  N07 -> N03[label=0];
  N07 -> N04[label=1];
  N07 -> N05[label=2];
  N07 -> N06[label=3];
  N08 -> N02[label=right];
  N08 -> N07[label=left];
  N09 -> N08[label=probability];
  N10 -> N09[label=operand];
  N12 -> N10[label=right];
  N12 -> N11[label=left];
  N13 -> N12[label=probability];
  N14 -> N13[label=operand];
}
"""

source12 = """
import beanmachine.ppl as bm
from torch.distributions import Normal, Uniform
@bm.random_variable
def theta_0():
    return Normal(0,1)

@bm.random_variable
def theta_1():
    return Normal(0,1)

@bm.random_variable
def error():
    return Uniform(0,1)

@bm.random_variable
def x(i):
    return Normal(0,1)

@bm.random_variable
def y(i):
    return Normal(theta_0() + theta_1() * x(i), error())

observations = [y(i) for i in range(3)] + [x(i) for i in range(3)]
"""

expected_dot_12 = """
digraph "graph" {
  N00[label=0.0];
  N01[label=1.0];
  N02[label=Normal];
  N03[label=Sample];
  N04[label=Sample];
  N05[label=Sample];
  N06[label="*"];
  N07[label="+"];
  N08[label=Uniform];
  N09[label=Sample];
  N10[label=Normal];
  N11[label=Sample];
  N12[label=Sample];
  N13[label="*"];
  N14[label="+"];
  N15[label=Normal];
  N16[label=Sample];
  N17[label=Sample];
  N18[label="*"];
  N19[label="+"];
  N20[label=Normal];
  N21[label=Sample];
  N02 -> N00[label=mu];
  N02 -> N01[label=sigma];
  N03 -> N02[label=operand];
  N04 -> N02[label=operand];
  N05 -> N02[label=operand];
  N06 -> N04[label=left];
  N06 -> N05[label=right];
  N07 -> N03[label=left];
  N07 -> N06[label=right];
  N08 -> N00[label=low];
  N08 -> N01[label=high];
  N09 -> N08[label=operand];
  N10 -> N07[label=mu];
  N10 -> N09[label=sigma];
  N11 -> N10[label=operand];
  N12 -> N02[label=operand];
  N13 -> N04[label=left];
  N13 -> N12[label=right];
  N14 -> N03[label=left];
  N14 -> N13[label=right];
  N15 -> N09[label=sigma];
  N15 -> N14[label=mu];
  N16 -> N15[label=operand];
  N17 -> N02[label=operand];
  N18 -> N04[label=left];
  N18 -> N17[label=right];
  N19 -> N03[label=left];
  N19 -> N18[label=right];
  N20 -> N09[label=sigma];
  N20 -> N19[label=mu];
  N21 -> N20[label=operand];
}
"""

# Illustrate that we correctly generate the support for
# multidimensional Bernoulli distributions. Flip two coins,
# take their average, and use that to make a third coin:
source13 = """
import beanmachine.ppl as bm
import torch
from torch import tensor
from torch.distributions import Bernoulli

@bm.random_variable
def x(n):
  return Bernoulli(n.sum()*0.5)

@bm.random_variable
def y():
  return Bernoulli(tensor([0.5,0.5]))

@bm.random_variable
def z():
  return Bernoulli(x(y()))
"""

expected_dot_13 = """
digraph "graph" {
  N00[label="[0.5,0.5]"];
  N01[label=Bernoulli];
  N02[label=Sample];
  N03[label=0.0];
  N04[label=Bernoulli];
  N05[label=Sample];
  N06[label="[0.0,0.0]"];
  N07[label=0.5];
  N08[label=Bernoulli];
  N09[label=Sample];
  N10[label="[0.0,1.0]"];
  N11[label=Sample];
  N12[label="[1.0,0.0]"];
  N13[label=1.0];
  N14[label=Bernoulli];
  N15[label=Sample];
  N16[label="[1.0,1.0]"];
  N17[label=map];
  N18[label=index];
  N19[label=Bernoulli];
  N20[label=Sample];
  N01 -> N00[label=probability];
  N02 -> N01[label=operand];
  N04 -> N03[label=probability];
  N05 -> N04[label=operand];
  N08 -> N07[label=probability];
  N09 -> N08[label=operand];
  N11 -> N08[label=operand];
  N14 -> N13[label=probability];
  N15 -> N14[label=operand];
  N17 -> N05[label=1];
  N17 -> N06[label=0];
  N17 -> N09[label=3];
  N17 -> N10[label=2];
  N17 -> N11[label=5];
  N17 -> N12[label=4];
  N17 -> N15[label=7];
  N17 -> N16[label=6];
  N18 -> N02[label=right];
  N18 -> N17[label=left];
  N19 -> N18[label=probability];
  N20 -> N19[label=operand];
}
"""

# Simple example of categorical
source14 = """
import beanmachine.ppl as bm
import torch
from torch.distributions import Bernoulli, Categorical
from torch import tensor

@bm.random_variable
def x(n):
  if n == 0:
    return Bernoulli(0.5)
  if n == 1:
    return Categorical(tensor([1.0, 3.0, 4.0]))
  return Bernoulli(0.75)

@bm.random_variable
def y():
  return Categorical(tensor([2.0, 6.0, 8.0]))

@bm.random_variable
def z():
  p = x(y()) * 0.25
  return Bernoulli(p)
"""

expected_dot_14 = """
digraph "graph" {
  N00[label="[0.125,0.375,0.5]"];
  N01[label=Categorical];
  N02[label=Sample];
  N03[label=0.5];
  N04[label=Bernoulli];
  N05[label=Sample];
  N06[label=0];
  N07[label=Sample];
  N08[label=1];
  N09[label=0.75];
  N10[label=Bernoulli];
  N11[label=Sample];
  N12[label=2];
  N13[label=map];
  N14[label=index];
  N15[label=0.25];
  N16[label="*"];
  N17[label=Bernoulli];
  N18[label=Sample];
  N01 -> N00[label=probability];
  N02 -> N01[label=operand];
  N04 -> N03[label=probability];
  N05 -> N04[label=operand];
  N07 -> N01[label=operand];
  N10 -> N09[label=probability];
  N11 -> N10[label=operand];
  N13 -> N05[label=1];
  N13 -> N06[label=0];
  N13 -> N07[label=3];
  N13 -> N08[label=2];
  N13 -> N11[label=5];
  N13 -> N12[label=4];
  N14 -> N02[label=right];
  N14 -> N13[label=left];
  N16 -> N14[label=left];
  N16 -> N15[label=right];
  N17 -> N16[label=probability];
  N18 -> N17[label=operand];
}
"""

# Gaussian mixture model.  Suppose we have a mixture of k normal distributions
# each with standard deviation equal to 1, but different means. Our prior
# on means is that mu(0), ... mu(k) are normally distributed.
# To make samples y(0), ... from this distribution we first choose which
# mean we want with z(0), ..., use that to sample mu(z(0)) to get the mean,
# and then use that mean to sample from a normal distribution.
source15 = """
import beanmachine.ppl as bm
from torch import tensor
from torch.distributions import Categorical, Normal

@bm.random_variable
def mu(k):
    # Means of the components are normally distributed
    return Normal(0, 1)

@bm.random_variable
def z(i):
    # Choose a category, 0, 1 or 2 with ratio 1:3:4.
    return Categorical(tensor([1., 3., 4.]))

@bm.random_variable
def y(i):
    return Normal(mu(z(i)), 1)

y0 = y(0)
"""

expected_dot_15 = """
digraph "graph" {
  N00[label="[0.125,0.375,0.5]"];
  N01[label=Categorical];
  N02[label=Sample];
  N03[label=0.0];
  N04[label=1.0];
  N05[label=Normal];
  N06[label=Sample];
  N07[label=Sample];
  N08[label=Sample];
  N09[label=2];
  N10[label=map];
  N11[label=index];
  N12[label=1];
  N13[label=Normal];
  N14[label=Sample];
  N01 -> N00[label=probability];
  N02 -> N01[label=operand];
  N05 -> N03[label=mu];
  N05 -> N04[label=sigma];
  N06 -> N05[label=operand];
  N07 -> N05[label=operand];
  N08 -> N05[label=operand];
  N10 -> N03[label=0];
  N10 -> N04[label=2];
  N10 -> N06[label=1];
  N10 -> N07[label=3];
  N10 -> N08[label=5];
  N10 -> N09[label=4];
  N11 -> N02[label=right];
  N11 -> N10[label=left];
  N13 -> N11[label=mu];
  N13 -> N12[label=sigma];
  N14 -> N13[label=operand];
}
"""


class CompilerTest(unittest.TestCase):
    def disabled_test_to_python_raw_2(self) -> None:
        self.maxDiff = None
        observed = to_python_raw(source2)
        self.assertEqual(observed.strip(), expected_raw_2.strip())

    def test_to_python_raw_5(self) -> None:
        self.maxDiff = None
        observed = to_python_raw(source5)
        self.assertEqual(observed.strip(), expected_raw_5.strip())

    def test_to_python_raw_6(self) -> None:
        self.maxDiff = None
        observed = to_python_raw(source6)
        self.assertEqual(observed.strip(), expected_raw_6.strip())

    def disabled_test_to_python_raw_7(self) -> None:
        # TODO: This crashes the compiler; figure out why
        self.maxDiff = None
        observed = to_python_raw(source7)
        self.assertEqual(observed.strip(), expected_raw_7.strip())

    def disabled_test_to_python_raw_9(self) -> None:
        # TODO: Enable this test when named arguments are fixed.
        self.maxDiff = None
        observed = to_python_raw(source9)
        self.assertEqual(observed.strip(), expected_raw_9.strip())

    def disabled_test_to_python_raw_10(self) -> None:
        # TODO: Enable this test when we support compilation of
        # TODO: vectorized models.
        self.maxDiff = None
        observed = to_python_raw(source10)
        self.assertEqual(observed.strip(), expected_raw_10.strip())

    def disabled_test_to_python_raw_11(self) -> None:
        # TODO: Enable this test when we support compilation of
        # TODO: vectorized models.
        self.maxDiff = None
        observed = to_python_raw(source11)
        self.assertEqual(observed.strip(), expected_raw_11.strip())

    def disabled_test_to_dot_2(self) -> None:
        self.maxDiff = None
        observed = to_dot(source2)
        self.assertEqual(observed.strip(), expected_dot_2.strip())

    def test_to_dot_5(self) -> None:
        self.maxDiff = None
        observed = to_dot(source5)
        self.assertEqual(observed.strip(), expected_dot_5.strip())

    def test_to_dot_6(self) -> None:
        self.maxDiff = None
        observed = to_dot(source6)
        self.assertEqual(observed.strip(), expected_dot_6.strip())

    def disabled_test_to_dot_7(self) -> None:
        # TODO: This crashes the compiler; figure out why
        self.maxDiff = None
        observed = to_dot(source7)
        self.assertEqual(observed.strip(), expected_dot_7.strip())

    def disabled_test_to_dot_9(self) -> None:
        # TODO: Enable this test when named arguments are fixed.
        self.maxDiff = None
        observed = to_dot(source9)
        self.assertEqual(observed.strip(), expected_dot_9.strip())

    def disabled_test_to_dot_10(self) -> None:
        # TODO: This crashes; something is broken with matrix multiplication.
        self.maxDiff = None
        observed = to_dot(source10)
        self.assertEqual(observed.strip(), expected_dot_10.strip())

    def test_to_dot_11(self) -> None:
        self.maxDiff = None
        observed = to_dot(source11)
        self.assertEqual(observed.strip(), expected_dot_11.strip())

    def disabled_test_to_dot_12(self) -> None:
        # TODO: This crashes the compiler; figure out why
        self.maxDiff = None
        observed = to_dot(source12)
        self.assertEqual(observed.strip(), expected_dot_12.strip())

    def test_to_dot_13(self) -> None:
        self.maxDiff = None
        observed = to_dot(source13)
        self.assertEqual(observed.strip(), expected_dot_13.strip())

    def test_to_dot_14(self) -> None:
        self.maxDiff = None
        observed = to_dot(source14)
        self.assertEqual(observed.strip(), expected_dot_14.strip())

    def test_to_dot_15(self) -> None:
        self.maxDiff = None
        observed = to_dot(source15)
        self.assertEqual(observed.strip(), expected_dot_15.strip())
