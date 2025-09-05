import numpy as np
import pandas as pd
import itertools
from typing import List, Tuple


class CPCV:
    """
    Combinatorial Purged Cross-Validation (CPCV) with Embargo for Time Series Data.

    This module provides train-test splits for time series datasets while preventing
    data leakage through purging and embargoing, following Lopez de Prado (2018).

    Example Usage:
    ```python
    from cpcv import CPCV
    import pandas as pd

    df = pd.DataFrame({'feature': range(100)})
    cpcv = CPCV(n_folds=5, test_size=1, embargo_pct=0.1)
    splits = cpcv.split(df)

    for train, test in splits:
        print(train.shape, test.shape)
    ```
    """

    def __init__(
        self,
        n_folds: int,
        test_size: int,
        embargo_pct: float = 0.0,
    ):
        """
        Combinatorial Purged Cross-Validation (CPCV) with Embargo.

        Parameters
        ----------
        n_folds : int
            Number of folds to split the data into. Must be at least 2.
        test_size : int
            Number of folds to use as test set in each combination. Must be >=1 and < n_folds.
        embargo_pct : float, optional
            Fraction of test set length to embargo on each side [0.0, 1.0). Default is 0.0 (no embargo).
        """
        if n_folds < 2:
            raise ValueError("n_folds must be at least 2.")
        if not 0.0 <= embargo_pct < 1.0:
            raise ValueError("embargo_pct must be in [0.0, 1.0).")
        if test_size < 1 or test_size >= n_folds:
            raise ValueError("test_size must be >=1 and < n_folds.")

        self.n_folds = n_folds
        self.test_size = test_size
        self.embargo_pct = embargo_pct

    def split(self, df: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Generate CPCV train-test splits.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame to split. Must have at least n_folds rows.

        Returns
        -------
        List of train-test tuples : List[Tuple[pd.DataFrame, pd.DataFrame]]
            List of (Train, Test) splits as DataFrames.
        """
        n_samples = len(df)
        if n_samples == 0:
            raise ValueError("Input DataFrame is empty.")
        if n_samples < self.n_folds:
            raise ValueError("Number of samples must be at least equal to n_folds.")

        fold_size = n_samples // self.n_folds

        # define folds as index ranges
        folds = [
            np.arange(i * fold_size, (i + 1) * fold_size) for i in range(self.n_folds)
        ]

        # handle remainder
        remainder = n_samples % self.n_folds
        if remainder > 0:
            folds[-1] = np.arange((self.n_folds - 1) * fold_size, n_samples)

        splits = []
        for test_comb in itertools.combinations(range(self.n_folds), self.test_size):
            test_idx = np.concatenate([folds[i] for i in test_comb])

            embargo_size = int(len(test_idx) * self.embargo_pct)
            if embargo_size > 0:
                min_test, max_test = test_idx.min(), test_idx.max()
                embargo_start = max(0, min_test - embargo_size)
                embargo_end = min(n_samples, max_test + embargo_size)
                embargo_idx = np.arange(embargo_start, embargo_end)
            else:
                embargo_idx = np.array([], dtype=int)

            train_idx = np.setdiff1d(
                np.arange(n_samples), np.union1d(test_idx, embargo_idx)
            )

            # Sanity check: no overlap
            assert len(np.intersect1d(train_idx, test_idx)) == 0, (
                "Train and test overlap!"
            )

            splits.append((df.iloc[train_idx].copy(), df.iloc[test_idx].copy()))

        return splits
