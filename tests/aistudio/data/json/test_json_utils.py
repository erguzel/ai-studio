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

from aistudio.data.json.json_utils import *

df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()


rep = Reporter('some report title','otherinfo')

rep = (
    rep.addelm('somemore')
    .addkvp(key1 = 'value1')
    .addkvp(otherobject = Reporter('modelinfo').addkvp(alpha=3.3,beta = -0.002))
)
print(rep.__dict__)

