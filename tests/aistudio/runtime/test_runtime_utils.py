import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so
import aistudio.runtime.runtime_utils as ru
import aistudio.plot.plot_utils as pu
import exchelp.exception_helper as eh

df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()


limitobjects=pu.Limit(x=(0, 4), y=(-1, 6))


limitobjects = ru.param_itemize(param_s=limitobjects,maxlength = 3, expectedtypes = pu.Limit, defaultvalue = None)

for k in limitobjects:
    print(k)