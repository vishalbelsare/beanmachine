# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from typing import Dict

import beanmachine.ppl as bm
import beanmachine.ppl.diagnostics.common_statistics as common_statistics
import numpy as np
import pandas as pd
import torch
import torch.distributions as dist
from beanmachine.ppl.diagnostics.diagnostics import Diagnostics
from statsmodels.tsa.stattools import acf


diri_dis = dist.Dirichlet(
    torch.tensor([[1.0, 2.0, 3.0], [2.0, 1.0, 3.0], [2.0, 3.0, 1.0]])
)

beta_dis = dist.Beta(torch.tensor([1.0, 2.0, 3.0]), torch.tensor([9.0, 8.0, 7.0]))

normal_dis = dist.Normal(torch.tensor([0.0, 1.0, 2.0]), torch.tensor([0.5, 1.0, 1.5]))


@bm.random_variable
def diri(i, j):
    return diri_dis


@bm.random_variable
def beta(i):
    return beta_dis


@bm.random_variable
def normal():
    return normal_dis


@bm.random_variable
def foo():
    return dist.Normal(0, 1)


@bm.random_variable
def bar():
    return dist.Normal(torch.randn(3, 1, 2), torch.ones(3, 1, 2))


def dist_summary_stats() -> Dict[str, torch.tensor]:
    exact_mean = {
        "beta": beta_dis.mean.reshape(-1),
        "diri": diri_dis.mean.reshape(-1),
        "normal": normal_dis.mean.reshape(-1),
    }

    exact_std = {
        "beta": torch.sqrt(beta_dis.variance.reshape(-1)),
        "diri": torch.sqrt(diri_dis.variance.reshape(-1)),
        "normal": torch.sqrt(normal_dis.variance.reshape(-1)),
    }
    exact_CI_2_5 = {"normal": normal_dis.mean - 1.96 * torch.sqrt(normal_dis.variance)}
    exact_CI_50 = {"normal": normal_dis.mean}
    exact_CI_97_5 = {"normal": normal_dis.mean + 1.96 * torch.sqrt(normal_dis.variance)}

    exact_stats = {
        "avg": exact_mean,
        "std": exact_std,
        "2.5%": exact_CI_2_5,
        "50%": exact_CI_50,
        "97.5%": exact_CI_97_5,
    }

    return exact_stats


class DiagnosticsTest(unittest.TestCase):
    def test_basic_diagnostics(self):
        def _inference_evaulation(summary: pd.DataFrame):
            exact_stats = dist_summary_stats()

            for col in summary.columns:
                if not (col in exact_stats):
                    continue
                for dis, res in exact_stats[col].items():
                    query_res = summary.loc[summary.index.str.contains(f"^{dis}")]
                    for i, val in enumerate(query_res[col].values):
                        self.assertAlmostEqual(
                            val,
                            res[i].item(),
                            msg=f"query {query_res.index[i]} for {col}",
                            delta=0.5,
                        )

        def _test_plot_object(diag, query, query_samples):
            plot_object = diag.plot([query])
            trace_object = diag.trace([query])
            index = 0
            num_samples = query_samples[0].numel()
            # test the trace plot over the first chain of beta(0)
            for i in range(num_samples):
                assert all(
                    a == b
                    for a, b in zip(
                        plot_object[0]["data"][index]["y"], query_samples[:, i]
                    )
                ), f"plot object for {diag._stringify_query(query)} is not correct"

                assert all(
                    a == b
                    for a, b in zip(
                        trace_object[0]["data"][index]["y"], query_samples[:, i]
                    )
                ), f"trace object for {diag._stringify_query(query)} {i} is not correct"

                index += 2

        def _test_autocorr_object(diag, query, query_samples):
            autocorr_object = diag.autocorr([query])
            index = 0
            num_samples = query_samples[0].numel()
            # test the autocorr results over the first chain of beta(0)
            for i in range(num_samples):
                expected_acf = acf(
                    query_samples[:, i].detach().numpy(),
                    True,
                    nlags=num_samples - 1,
                    fft=False,
                )
                for ns in range(num_samples):
                    self.assertAlmostEqual(
                        autocorr_object[0]["data"][index]["y"][ns],
                        expected_acf[ns],
                        msg=f"autocorr data for {diag._stringify_query(query)}\
                              is not correct",
                        delta=0.3,
                    )
                index += 1

        np.random.seed(123)
        torch.manual_seed(123)
        mh = bm.SingleSiteAncestralMetropolisHastings()
        query_list = [beta(0), diri(1, 5), normal()]
        num_chains = 2
        samples = mh.infer(query_list, {}, 200, num_chains)

        out_df = Diagnostics(samples).summary()
        _inference_evaulation(out_df)

        out_df = Diagnostics(samples).summary([diri(1, 5), beta(0)])
        _inference_evaulation(out_df)

        out_df = Diagnostics(samples).summary(query_list=[diri(1, 5)], chain=1)
        _inference_evaulation(out_df)

        self.assertRaises(ValueError, Diagnostics(samples).summary, [diri(1, 3)])
        self.assertRaises(ValueError, Diagnostics(samples).summary, [diri(1, 5), foo()])

        query = beta(0)
        query_samples = samples[query][0]
        _test_plot_object(Diagnostics(samples), query, query_samples)
        _test_autocorr_object(Diagnostics(samples), query, query_samples)

    def test_r_hat_one_chain(self):
        mh = bm.SingleSiteAncestralMetropolisHastings()
        samples = mh.infer([normal()], {}, 5, 1)
        diagnostics = Diagnostics(samples)
        with self.assertWarns(UserWarning):
            results = diagnostics.split_r_hat([normal()])
        self.assertTrue(results.empty)

    def test_r_hat_column(self):
        mh = bm.SingleSiteAncestralMetropolisHastings()
        samples = mh.infer([normal()], {}, 5, 2)
        diagnostics = Diagnostics(samples)

        out_df = diagnostics.summary()
        self.assertTrue("r_hat" in out_df.columns)

        out_df = diagnostics.summary(chain=0)
        self.assertTrue("r_hat" not in out_df.columns)

    def test_r_hat_no_column(self):
        mh = bm.SingleSiteAncestralMetropolisHastings()
        samples = mh.infer([normal()], {}, 5, 1)
        out_df = Diagnostics(samples).summary()
        self.assertTrue("r_hat" not in out_df.columns)

    def test_r_hat(self):
        samples = torch.tensor([[0.0, 1.0, 2.0, 3.0], [4.0, 5.0, 6.0, 7.0]])
        self.assertAlmostEqual(common_statistics.r_hat(samples), 2.3558, delta=0.001)
        self.assertAlmostEqual(
            common_statistics.split_r_hat(samples), 3.7193, delta=0.001
        )

    def test_r_hat_additional_dimension(self):
        samples = torch.tensor(
            [
                [[0.0, 2.0], [2.0, 4.0], [4.0, 8.0], [6.0, 0.0]],
                [[8.0, 12.0], [10.0, 6.0], [12.0, 1.0], [14.0, 2.0]],
                [[16.0, -5.0], [18.0, 4.0], [20.0, 2.0], [22.0, 4.0]],
            ]
        )
        dim1, dim2 = common_statistics.r_hat(samples)
        self.assertAlmostEqual(dim1, 3.2171, delta=0.001)
        self.assertAlmostEqual(dim2, 0.9849, delta=0.001)
        dim1, dim2 = common_statistics.split_r_hat(samples)
        self.assertAlmostEqual(dim1, 5.3385, delta=0.001)
        self.assertAlmostEqual(dim2, 1.0687, delta=0.001)

    def test_effective_sample_size(self):
        samples = torch.tensor(
            [[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]], dtype=torch.double
        )
        n_eff = common_statistics.effective_sample_size(samples)
        self.assertAlmostEqual(n_eff, 2.6114, delta=0.001)

    def test_effective_sample_size_additional_dimension(self):
        samples = torch.tensor(
            [
                [[0.0, 2.0], [2.0, 4.0], [4.0, 8.0], [6.0, 0.0]],
                [[8.0, 12.0], [10.0, 6.0], [12.0, 1.0], [14.0, 2.0]],
                [[16.0, -5.0], [18.0, 4.0], [20.0, 2.0], [22.0, 4.0]],
            ]
        )
        dim1, dim2 = common_statistics.effective_sample_size(samples)
        self.assertAlmostEqual(dim1, 1.9605, delta=0.001)
        self.assertAlmostEqual(dim2, 15.1438, delta=0.001)

    def test_effective_sample_size_columns(self):
        mh = bm.SingleSiteAncestralMetropolisHastings()
        samples = mh.infer([normal()], {}, 5, 2)
        out_df = Diagnostics(samples).summary()
        self.assertTrue("n_eff" in out_df.columns)

    def test_singleton_dims(self):
        mh = bm.SingleSiteAncestralMetropolisHastings()
        obs = {bar(): torch.ones(3, 1, 2)}
        samples = mh.infer([bar()], obs, 5, 2)
        diagnostics = Diagnostics(samples)
        out_df = diagnostics.summary()
        self.assertTrue("r_hat" in out_df.columns)
