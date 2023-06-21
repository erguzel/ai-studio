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

fig = pu.multi_plot(
    plotparam=pu.PlotParam(data = df, y='pickups'),
    features=[
            'temp',
            'week_day',
            ],

    designparams=
    [
        pu.TransformParam(
            so.Dots(alpha=0.2),so.Agg('mean'),color = 'borough',pointsize = 'month' , y = 'dew_point_temperature'
        ),
        pu.TransformParam(
              so.Area(),so.Agg()
         ),
       # pu.TransformParam(
       #     so.Bar(),so.Agg()
       # )
    ],
    #layerparams=[
    #    pu.argsbase(
    #        pu.TransformParam(so.Line(),so.PolyFit(order = 4), y = 'dew_point_temperature')
    #    )
    #],
    updateparams= [
        pu.argsbase(pu.LabelParam(y = 'dew_pt_temp')),
        #pu.argsbase(pu.FacetParam(col='is_holiday'),pu.LabelParam(col = '{}'.format)),
        #pu.argsbase(pu.LabelParam(x = 'foo',y = 'bar'))
        ],
    wrap=3,
    figsize=(16,5)
    )