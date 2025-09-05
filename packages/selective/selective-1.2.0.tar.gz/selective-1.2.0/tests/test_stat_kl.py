# -*- coding: utf-8 -*-
# Copyright FMR LLC <opensource@fidelity.com>
# SPDX-License-Identifier: Apache-2.0

from sklearn.datasets import fetch_california_housing, load_iris
from feature.utils import get_data_label
from feature.selector import Selective, SelectionMethod
from tests.test_base import BaseTest


class TestKL(BaseTest):

    def test_kl_regress_invalid(self):
        data, label = get_data_label(fetch_california_housing())
        data = data.drop(columns=["Latitude", "Longitude", "Population"])

        method = SelectionMethod.Statistical(num_features=3, method="kl_divergence")
        selector = Selective(method)
        with self.assertRaises(TypeError):
            selector.fit(data, label)

    def test_kl_regress_top_percentile_invalid(self):
        data, label = get_data_label(fetch_california_housing())
        data = data.drop(columns=["Latitude", "Longitude", "Population"])

        method = SelectionMethod.Statistical(num_features=0.6, method="kl_divergence")
        selector = Selective(method)
        with self.assertRaises(TypeError):
            selector.fit(data, label)

    def test_kl_classif_top_k(self):
        data, label = get_data_label(load_iris())
        
        # Only Binary Data Is Supported by KL Divergence
        data = data[(label == 0) | (label == 1)]
        label = label[(label == 0) | (label == 1)]
        
        method = SelectionMethod.Statistical(num_features=2, method="kl_divergence")
        selector = Selective(method)
        selector.fit(data, label)
        subset = selector.transform(data)

        # Reduced columns
        self.assertEqual(subset.shape[1], 2)
        self.assertListEqual(list(subset.columns), ['sepal length (cm)', 'petal length (cm)'])

    def test_kl_classif_top_percentile(self):
        data, label = get_data_label(load_iris())
        
        # Only Binary Data Is Supported by KL Divergence
        data = data[(label == 0) | (label == 1)]
        label = label[(label == 0) | (label == 1)]
        
        method = SelectionMethod.Statistical(num_features=0.5, method="kl_divergence")
        selector = Selective(method)
        selector.fit(data, label)
        subset = selector.transform(data)

        # Reduced columns
        self.assertEqual(subset.shape[1], 2)
        self.assertListEqual(list(subset.columns), ['sepal length (cm)', 'petal length (cm)'])

    def test_kl_classif_top_percentile_all(self):
        data, label = get_data_label(load_iris())

        # Only Binary Data Is Supported by KL Divergence
        data = data[(label == 0) | (label == 1)]
        label = label[(label == 0) | (label == 1)]
        
        method = SelectionMethod.Statistical(num_features=1.0, method="kl_divergence")
        selector = Selective(method)
        selector.fit(data, label)
        subset = selector.transform(data)

        # Reduced columns
        self.assertEqual(subset.shape[1], 4)
        self.assertListEqual(list(subset.columns),
                             ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'])

    def test_kl_classif_top_k_all(self):
        data, label = get_data_label(load_iris())

        # Only Binary Data Is Supported by KL Divergence
        data = data[(label == 0) | (label == 1)]
        label = label[(label == 0) | (label == 1)]

        method = SelectionMethod.Statistical(num_features=4, method="kl_divergence")
        selector = Selective(method)
        selector.fit(data, label)
        subset = selector.transform(data)

        # Reduced columns
        self.assertEqual(subset.shape[1], 4)
        self.assertListEqual(list(subset.columns),
                             ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'])