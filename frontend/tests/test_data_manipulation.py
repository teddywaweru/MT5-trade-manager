import sys
sys.path.insert(1, 'FX_MT4_app')
import backend.data_manipulation as data_manipulation
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'open': np.random.rand(100),
    'high': np.random.rand(100),
    'low': np.random.rand(100),
    'close': np.random.rand(100),
    'spread': np.random.rand(100),
    'real_volume': np.random.rand(100),
})

dm = data_manipulation.DataManipulation(data)

def test_data_columns():
    assert list(data.columns) == ['open','high','low','close','spread','real_volume']


def test_data_cols_after_transform():
    assert list(dm.data_df.columns) == ['open','high','low','close','atr']