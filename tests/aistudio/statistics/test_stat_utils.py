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
from aistudio.abstraction.base_types import *
import aistudio.statistics.stats_utils as su

df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()

d,u = su.get_outlier_boundpairs(df['pickups'],tuplargs([25,75,100])).args[0]
print(d,u)

l,u = su.get_outlier_percentileofscores(df['pickups'],tuplargs([25,75,100])).args[0]
print(l,u)


