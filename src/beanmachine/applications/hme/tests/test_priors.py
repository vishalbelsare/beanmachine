# (c) Facebook, Inc. and its affiliates. Confidential and proprietary.

import pandas as pd
import pytest
from beanmachine.applications.hme import (
    HME,
    InferConfig,
    ModelConfig,
    MixtureConfig,
    PriorConfig,
    RegressionConfig,
)
from beanmachine.applications.hme.abstract_linear_model import AbstractLinearModel
from beanmachine.applications.hme.abstract_model import AbstractModel
from beanmachine.applications.hme.priors import ParamType, Distribution


class RealizedModel(AbstractModel):
    def build_graph(self):
        return super().build_graph()


class RealizedLinearModel(AbstractLinearModel):
    def build_graph(self):
        self.fixed_effects, self.random_effects = self.parse_formula(
            self.model_config.mean_regression.formula
        )
        self._set_priors()
        self._set_default_priors()
        self._customize_priors()

    def _add_observation_byrow(self, index, row, fere_i):
        return super()._add_observation_byrow(index, row, fere_i)


@pytest.mark.parametrize(
    "label",
    ["unknown"],
)
def test_paramtype_exception(label):
    with pytest.raises(
        ValueError, match="Unknown parameter type: '{s}'".format(s=label)
    ):
        ParamType.match_str(label)


@pytest.mark.parametrize(
    "label",
    ["unknown"],
)
def test_distribution_exception(label):
    with pytest.raises(
        ValueError, match="Unknown distribution type: '{s}'".format(s=label)
    ):
        Distribution.match_str(label)


@pytest.mark.parametrize(
    "prior_config",
    [
        PriorConfig("normal", {"mean": 0.0, "sigma": 1.0}),
        PriorConfig("t", {"scale": 1.0, "mean": 0.0, "degree-of-freedom": 2.0}),
    ],
)
def test_parameter_dict_exception(prior_config):
    model = RealizedModel(data=None, model_config=ModelConfig())
    with pytest.raises(ValueError):
        model._parse_fe_prior_config(prior_config, "test")


@pytest.mark.parametrize(
    "const_value, const_type, expected_dot",
    [
        (1.0, "pos_real", 'digraph "graph" {\n  N0[label="1"];\n}\n'),
        (-1.0, "real", 'digraph "graph" {\n  N0[label="-1"];\n}\n'),
        (1, "natural", 'digraph "graph" {\n  N0[label="1"];\n}\n'),
        (0.5, "prob", 'digraph "graph" {\n  N0[label="0.5"];\n}\n'),
    ],
)
def test_generate_const_node(const_value, const_type, expected_dot):
    model = RealizedModel(data=None, model_config=ModelConfig())
    model._generate_const_node(const_value, ParamType.match_str(const_type))
    assert model.g.to_dot() == expected_dot


@pytest.mark.parametrize(
    "prior_config, expected_dot",
    [
        (
            PriorConfig("normal", {"scale": 1.0, "mean": 0.0}),
            'digraph "graph" {\n  N0[label="0"];\n  N1[label="1"];\n  N2[label="Normal"];\n  N0 -> N2;\n  N1 -> N2;\n}\n',
        ),
        (
            PriorConfig("beta", {"alpha": 1.0, "beta": 1.0}),
            'digraph "graph" {\n  N0[label="1"];\n  N1[label="1"];\n  N2[label="Beta"];\n  N0 -> N2;\n  N1 -> N2;\n}\n',
        ),
        (
            PriorConfig("gamma", {"beta": 1.0, "alpha": 1.0}),
            'digraph "graph" {\n  N0[label="1"];\n  N1[label="1"];\n  N2[label="Gamma"];\n  N0 -> N2;\n  N1 -> N2;\n}\n',
        ),
        (
            PriorConfig("t", {"scale": 1.0, "mean": 0.0, "dof": 2.0}),
            'digraph "graph" {\n  N0[label="2"];\n  N1[label="0"];\n  N2[label="1"];\n  N3[label="StudentT"];\n  N0 -> N3;\n  N1 -> N3;\n  N2 -> N3;\n}\n',
        ),
    ],
)
def test_parse_fe_prior_config(prior_config, expected_dot):
    model = RealizedModel(data=None, model_config=ModelConfig())
    model._parse_fe_prior_config(prior_config, "test")
    assert model.g.to_dot() == expected_dot


def test_default_priors():
    model = RealizedLinearModel(
        data=None,
        model_config=ModelConfig(),
    )
    model._set_priors()
    model._set_default_priors()
    expected = {
        "fixed_effects": 8,
        "random_effects": (11, {"scale": 10}),
        "prob_h": 4,
        "prob_sign": 4,
    }
    assert model.default_priors == expected


@pytest.mark.parametrize(
    "priors_desc, expected",
    [
        (
            {
                "x1": PriorConfig("normal", {"mean": 0.0, "scale": 1.0}),
                "x2": PriorConfig("flat", {}),
                "group": PriorConfig(
                    "t",
                    {
                        "mean": PriorConfig("normal", {"mean": 2.0, "scale": 1.0}),
                        "dof": PriorConfig("half_cauchy", {"scale": 1.0}),
                        "scale": 1.0,
                    },
                ),
                "prob_h": PriorConfig("beta", {"beta": 1.0, "alpha": 1.0}),
                "prob_sign": PriorConfig("beta", {"alpha": 1.0, "beta": 1.0}),
            },
            {
                "x1": 14,
                "x2": 15,
                "group": (24, {"dof": 18, "mean": 22}),
                "prob_h": 27,
                "prob_sign": 30,
            },
        ),
    ],
)
def test_customize_priors(priors_desc, expected):
    model = RealizedLinearModel(
        data=None,
        model_config=ModelConfig(
            mean_regression=RegressionConfig(formula="y~1"),
            priors=priors_desc,
        ),
    )
    model.build_graph()
    assert model.customized_priors == expected


@pytest.mark.parametrize(
    "priors_desc, expected_dot",
    [
        (
            {
                "x1": PriorConfig("t", {"dof": 2.0, "scale": 1.0, "mean": 0.0}),
                "x2": PriorConfig("beta", {"alpha": 1.0, "beta": 1.0}),
            },
            (
                'digraph "graph" {\n  N0[label="0"];\n  N1[label="1"];\n  N2[label="2"];\n  N3[label="3"];\n  N4[label="Beta"];\n  '
                'N5[label="Gamma"];\n  N6[label="HalfCauchy"];\n  N7[label="distribution"];\n  N8[label="Normal"];\n  '
                'N9[label="StudentT"];\n  N10[label="~"];\n  N11[label="Normal"];\n  N12[label="2"];\n  N13[label="0"];\n  '
                'N14[label="1"];\n  N15[label="StudentT"];\n  N16[label="1"];\n  N17[label="1"];\n  N18[label="Beta"];\n  '
                'N19[label="~"];\n  N20[label="~"];\n  N0 -> N8;\n  N0 -> N9;\n  N0 -> N11;\n  N1 -> N4;\n  N1 -> N4;\n  '
                "N1 -> N5;\n  N1 -> N5;\n  N1 -> N6;\n  N1 -> N7;\n  N2 -> N8;\n  N3 -> N9;\n  N3 -> N9;\n  N7 -> N10;\n  "
                "N10 -> N11;\n  N12 -> N15;\n  N13 -> N15;\n  N14 -> N15;\n  N15 -> N19;\n  N16 -> N18;\n  N17 -> N18;\n  N18 -> N20;\n}\n"
            ),
        ),
        (
            {},
            (
                'digraph "graph" {\n  N0[label="0"];\n  N1[label="1"];\n  N2[label="2"];\n  N3[label="3"];\n  N4[label="Beta"];\n  '
                'N5[label="Gamma"];\n  N6[label="HalfCauchy"];\n  N7[label="distribution"];\n  N8[label="Normal"];\n  N9[label="StudentT"];\n  '
                'N10[label="~"];\n  N11[label="Normal"];\n  N12[label="~"];\n  N13[label="~"];\n  N0 -> N8;\n  N0 -> N9;\n  N0 -> N11;\n  '
                "N1 -> N4;\n  N1 -> N4;\n  N1 -> N5;\n  N1 -> N5;\n  N1 -> N6;\n  N1 -> N7;\n  N2 -> N8;\n  N3 -> N9;\n  N3 -> N9;\n  "
                "N7 -> N10;\n  N8 -> N12;\n  N8 -> N13;\n  N10 -> N11;\n}\n"
            ),
        ),
    ],
)
def test_initialize_fixed_effect_nodes(priors_desc, expected_dot):
    model = RealizedLinearModel(
        data=None,
        model_config=ModelConfig(
            mean_regression=RegressionConfig(formula="y~x1+x2"),
            priors=priors_desc,
        ),
    )
    model.build_graph()
    model._initialize_fixed_effect_nodes()
    assert model.g.to_dot() == expected_dot


@pytest.mark.parametrize(
    "priors_desc, expected_dot",
    [
        (
            {
                "group": PriorConfig(
                    "t",
                    {
                        "mean": PriorConfig("normal", {"mean": 2.0, "scale": 1.0}),
                        "dof": PriorConfig("half_normal", {"scale": 1.0}),
                        "scale": 1.0,
                    },
                ),
            },
            (
                'digraph "graph" {\n  N0[label="0"];\n  N1[label="1"];\n  N2[label="2"];\n  N3[label="3"];\n  N4[label="Beta"];\n  '
                'N5[label="Gamma"];\n  N6[label="HalfCauchy"];\n  N7[label="distribution"];\n  N8[label="Normal"];\n  '
                'N9[label="StudentT"];\n  N10[label="~"];\n  N11[label="Normal"];\n  N12[label="1"];\n  N13[label="distribution"];\n  '
                'N14[label="~"];\n  N15[label="2"];\n  N16[label="1"];\n  N17[label="Normal"];\n  N18[label="~"];\n  N19[label="1"];\n  '
                'N20[label="StudentT"];\n  N0 -> N8;\n  N0 -> N9;\n  N0 -> N11;\n  N1 -> N4;\n  N1 -> N4;\n  N1 -> N5;\n  N1 -> N5;\n  '
                "N1 -> N6;\n  N1 -> N7;\n  N2 -> N8;\n  N3 -> N9;\n  N3 -> N9;\n  N7 -> N10;\n  N10 -> N11;\n  N12 -> N13;\n  "
                "N13 -> N14;\n  N14 -> N20;\n  N15 -> N17;\n  N16 -> N17;\n  N17 -> N18;\n  N18 -> N20;\n  N19 -> N20;\n}\n"
            ),
        ),
        (
            {},
            (
                'digraph "graph" {\n  N0[label="0"];\n  N1[label="1"];\n  N2[label="2"];\n  N3[label="3"];\n  N4[label="Beta"];\n  '
                'N5[label="Gamma"];\n  N6[label="HalfCauchy"];\n  N7[label="distribution"];\n  N8[label="Normal"];\n  '
                'N9[label="StudentT"];\n  N10[label="~"];\n  N11[label="Normal"];\n  N0 -> N8;\n  N0 -> N9;\n  N0 -> N11;\n  '
                "N1 -> N4;\n  N1 -> N4;\n  N1 -> N5;\n  N1 -> N5;\n  N1 -> N6;\n  N1 -> N7;\n  N2 -> N8;\n  N3 -> N9;\n  N3 -> N9;\n  "
                "N7 -> N10;\n  N10 -> N11;\n}\n"
            ),
        ),
    ],
)
def test_initialize_random_effect_nodes(priors_desc, expected_dot):
    model = RealizedLinearModel(
        data=None,
        model_config=ModelConfig(
            mean_regression=RegressionConfig(formula="y~1+(1|group)"),
            priors=priors_desc,
        ),
    )
    model.build_graph()
    model._initialize_random_effect_nodes()
    assert model.g.to_dot() == expected_dot


@pytest.mark.parametrize(
    "mean_config, mixture_config, priors_desc, data, expected",
    [
        (
            RegressionConfig(
                distribution="normal",
                outcome="y",
                stderr="se",
                formula="~ 1+x1+x2+(1|team)+(1|group)",
                link="identity",
            ),
            MixtureConfig(use_null_mixture=True),
            {
                "x1": PriorConfig("normal", {"mean": 0.0, "scale": 1.0}),
                "group": PriorConfig(
                    "t",
                    {
                        "scale": 1.0,
                        "dof": PriorConfig("half_cauchy", {"scale": 1.0}),
                        "mean": PriorConfig("normal", {"mean": 2.0, "scale": 1.0}),
                    },
                ),
            },
            pd.DataFrame(
                {
                    "y": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                    "x1": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
                    "x2": [2.0, 1.1, 1.2, 1.3, 1.4, 1.5],
                    "se": [0.15] * 6,
                    "group": ["a"] * 3 + ["b"] * 3,
                    "team": ["x", "y"] * 3,
                }
            ),
            {
                "fixed_effect_Intercept",
                "fixed_effect_x1",
                "fixed_effect_x2",
                "re_group_dof",
                "re_group_mean",
                "re_team_scale",
                "re_value_group_a",
                "re_value_group_b",
                "re_value_team_x",
                "re_value_team_y",
            },
        ),
    ],
)
def test_queries(mean_config, mixture_config, priors_desc, data, expected):
    model = HME(
        data,
        ModelConfig(
            mean_regression=mean_config, mean_mixture=mixture_config, priors=priors_desc
        ),
    )
    post_samples, _ = model.infer(InferConfig(n_iter=100, n_warmup=100, seed=0))
    assert expected.issubset(post_samples.columns)
