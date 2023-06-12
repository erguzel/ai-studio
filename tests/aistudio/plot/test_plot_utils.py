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

df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()
cont_vars = ['pickups', 'visibility', 'temp','dew_point_temperature','sea_level_pressure','snow_depth_inc','liquid_precipitation_1h','liquid_precipitation_6h','liquid_precipitation_24h']

p,f = pu.so_boxplots(
    data =df,
    numerics=cont_vars,
    griddimensions=(3,3),
    figsize=(14,12),
    vertical=False,
    viewmodes='band'
)

p.show()