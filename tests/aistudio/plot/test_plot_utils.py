import os
import sys
print(os.getcwd())
sys.path.insert(1,os.getcwd())


import pytest 

import src.aistudio.plot.plot_utils as pu



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
import aistudio.plot.plot_utils as pu
from aistudio.abstraction.base_types import *

df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()


fig = pu.multi_boxplot(
    plotparam=pu.PlotParam(data = df, x = 'pickups'),
    features=argsbase('temp','dew_point_temperature','snow_depth_inc'),
    updateparams=argsbase(pu.FacetParam(col='is_holiday')).setmasterparam(True)
)