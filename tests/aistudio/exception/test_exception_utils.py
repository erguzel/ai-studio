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
from aistudio.exception.exception_utils import *



df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()


int = Interrupter('some error occured','dont do stg',logit = True,throw = False)

int = int.addData(logit=True,bar = 'foo')

print(int.kwargs)