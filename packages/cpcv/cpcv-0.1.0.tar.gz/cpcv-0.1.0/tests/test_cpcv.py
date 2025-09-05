import pandas as pd
from cpcv import CPCV


def test_split_sizes():
    df = pd.DataFrame({"a": range(100)})
    cpcv = CPCV(n_folds=5, test_size=1, embargo_pct=0.1)
    splits = cpcv.split(df)

    for train, test in splits:
        # Ensure train and test do not overlap
        assert set(train.index).isdisjoint(test.index)
        # Ensure all rows accounted for
        assert len(train) + len(test) <= len(df)
