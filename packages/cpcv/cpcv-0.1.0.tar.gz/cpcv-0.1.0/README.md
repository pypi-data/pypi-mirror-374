# Combinatorial Purged Cross-Validation with Embargo for Time Series Data

CPCV with Embargo prevents leakage in time series cross-validation by purging overlapping periods and applying an embargo around test folds.

## Installation

```bash
pip install git+https://github.com/yosri-bh/cpcv-train-test-data-split-module.git
```

or

```bash
pip install cpcv
```

## Usage

```python
import pandas as pd
from cpcv import CPCV

df = pd.DataFrame({'feature': range(100)})
cpcv = CPCV(n_folds=5, test_size=1, embargo_pct=0.1)
splits = cpcv.split(df)

for train, test in splits:
    print(train.shape, test.shape)
```

## Connect with Me

Thank you for visiting my GitHub profile! Feel free to reach out if you have any questions or opportunities to collaborate. Let's connect and explore new possibilities together:

[![GitHub](https://img.shields.io/badge/GitHub-Yosri--Ben--Halima-black?logo=github)](https://github.com/Yosri-Ben-Halima)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Yosri%20Ben%20Halima-blue?logo=linkedin)](https://www.linkedin.com/in/yosri-benhalima/)
[![Facebook](https://img.shields.io/badge/Facebook-@Yosry%20Ben%20Hlima-navy?logo=facebook)](https://www.facebook.com/NottherealYxsry)
[![Instagram](https://img.shields.io/badge/Instagram-@yosrybh-orange?logo=instagram)](https://www.instagram.com/yosrybh/)
[![Email](https://img.shields.io/badge/Email-yosri.benhalima@ept.ucar.tn-white?logo=gmail)](mailto:yosri.benhalima@ept.ucar.tn)
[![Personal Web Page](https://img.shields.io/badge/Personal%20Web%20Page-Visit%20Now-green?logo=googlechrome)](https://personal-web-page-yosribenhlima.streamlit.app/)
[![Google Drive](https://img.shields.io/badge/My%20Resume-Click%20Here-red?logo=googledrive&logoColor=white)](https://drive.google.com/file/d/18xB1tlZUBWz5URSli_9kewEFZwZPz235/view?usp=sharing)
[![PyPI](https://img.shields.io/badge/PyPI-yosri--ben--halima-pink?logo=pypi)](https://pypi.org/user/yosri-ben-halima/)
