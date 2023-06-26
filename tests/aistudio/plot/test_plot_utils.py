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


aa = pu.multi_histogram(
    plotparam=pu.PlotParam(data = df, x = 'pickups'),
    features=tpargsbase('pickups','temp'),
    showoutlierrange=True,
    histvars= pu.TransformParam(so.Area(),so.Hist()).addelm('masterparam')
)


#sns.set_theme(palette='pastel',color_codes=True)

"""
ll = pu.multi_plot(
    plotparam=pu.PlotParam(data = df, y = 'pickups'),
    features=argsbase('borough','week_day'),
    designparams= pu.TransformParam(so.Bar(),so.Agg()).setmasterparam(True),
    updateparams = argsbase(pu.LayoutParam(size=(2,2))).setmasterparam(True)

)
"""

"""
pu.multi_plot(
    plotparam=pu.PlotParam(data = df, x = 'borough'),
    features=argsbase('pickups','temp','show_depth_inc'),
    designparams= argsbase(
            pu.TransformParam(so.Dot(),so.Agg(),pointsize = 'visibility'),
            pu.TransformParam(so.Band(),so.Agg()),
            pu.TransformParam(so.Area(),so.Perc())
        ),
    layerparams=argsbase(
        None,
        argsbase(
            pu.TransformParam(so.Line(),so.Agg('count'),color = 'is_holiday'),
            pu.TransformParam(so.Dash(),so.KDE(),marker = 'week_day')
        ),
        None,   
    )
)
"""

"""
hs = pu.multi_histogram(
    plotparam= pu.PlotParam(data = df, x = 'pickups'),
    features=argsbase('temp'),
)
"""


"""
bx = pu.multi_boxplot(
    pu.PlotParam(data = df, x = 'pickups'),
    features=argsbase('temp','dew_point_temperature','sea_level_pressure'),
    showkde=True,
    showhistogram=True,
    #histvars=pu.argsbase(None,pu.TransformParam(so.Bars(color='k'),so.Hist('density'))),
    histvars = pu.argsbase(
        None,
        pu.TransformParam(so.Bars(color='k'),so.Hist('density')),    
    ),
    kdevars = pu.argsbase(
        None,
        pu.TransformParam(so.Area(),so.KDE(cut=0,bw_adjust=2)) 
    ),
    #kdevars=pu.TransformParam(so.Area(),so.KDE(cut=0,bw_adjust=2)).setmasterparam(True),
    updateparams = argsbase(pu.FacetParam(col = 'is_holiday')).setmasterparam(True),
    boxplotvars = argsbase(
        None,
        kwargsbase(
            dotvars = kwargsbase(alpha = 0.09,pointsize = 4),
            jittervars = kwargsbase(width = 1),
            meanvars = kwargsbase(color = 'magenta',linestyle = '*'),
            dotview = True
        )
    )  
)
"""