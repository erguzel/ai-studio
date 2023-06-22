import os
import sys
print(os.getcwd())
sys.path.insert(1,os.getcwd())


import pytest 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
import aistudio.plot.plot_utils as pu
from aistudio.abstraction.base_types import *

df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()


bx = pu.multi_boxplot(
    pu.PlotParam(data = df, x = 'pickups'),
    features=argsbase('temp','dew_point_temperature','sea_level_pressure'),
    dotvars= pu.kwargsbase(alpha = 0.08,pointsize = 4).setmasterparam(True),
    jittervars= pu.argsbase(pu.kwargsbase(width = 1)),
    meanvars = pu.argsbase(pu.kwargsbase(color = 'cyan',linestyle = '--')),
    dotview = argsbase(True,True),
    showhistogram=True,
    histvars=pu.argsbase(None,pu.TransformParam(so.Bars(color='k'),so.Hist('density'))),
    kdevars=pu.TransformParam(so.Area(),so.KDE(cut=0,bw_adjust=2)).setmasterparam(True),
    showkde=True,
    updateparams = argsbase(pu.FacetParam(col = 'is_holiday')).setmasterparam(True)
)