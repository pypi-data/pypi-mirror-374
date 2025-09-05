# -*- coding: utf-8 -*-
# Copyright FMR LLC <opensource@fidelity.com>
# SPDX-License-Identifier: Apache-2.0

from typing import NoReturn, Tuple

import pandas as pd
import numpy as np

from scipy.special import rel_entr
from feature.base import _BaseSupervisedSelector
from feature.utils import Num, check_true


class _KL_Divergence(_BaseSupervisedSelector):

    def __init__(self, seed: int, num_features: Num, num_bins: Num = 100):
        super().__init__(seed)

        self.num_features = num_features  # this could be int or float
        self.num_bins = num_bins

    def fit(self, X: pd.DataFrame, y: pd.Series) -> NoReturn:

        label_categories = np.unique(y)
        check_true(len(label_categories) == 2, TypeError("Only binary labels are supported for KL Divergence"))
        input_dimension = X.shape[1]
        
        kl_mat = np.zeros((input_dimension, 1))
        X = X.values
        
        class_one_idx = np.where(y == label_categories[0])[0]
        class_two_idx = np.where(y == label_categories[1])[0]
        
        for i in range(input_dimension):
            
            # Create two distributions, one for the positive label and one for the negative label
            f1 = np.histogram(X[class_one_idx, i], bins = self.num_bins)[0]
            f2 = np.histogram(X[class_two_idx, i], bins = self.num_bins)[0]
            
            # Normalize the distributions to be between 0 and 1
            f1 = f1 / np.sum(f1)
            f2 = f2 / np.sum(f2)
        
            # KL Divergence is not symmetric, so we calculate divergence in both directions 
            kl = rel_entr(f1, f2)
            kl_reversed = rel_entr(f2, f1)
            
            # The relative entropy function returns KL(P || Q) = np.inf when P == 0 and Q != 0. 
            kl[kl == np.inf] = 9999
            kl_reversed[kl_reversed == np.inf] = 9999
            
            # The final score is the combination of KL divergence in both directions. 
            # This could possibly be a flag in a future version to determine which direction to apply KL Divergence
            # in if bidirectional is not desired. 
            kl_mat[i] = np.sum(kl) + np.sum(kl_reversed)

        scores_ = kl_mat.flatten()
        
        self.scores_ = scores_ # This is used by the statistical.py fit function. 
        self.abs_scores = scores_ 

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:

        # Select top-k from data based on abs_scores and num_features
        return self.get_top_k(data, self.abs_scores)
