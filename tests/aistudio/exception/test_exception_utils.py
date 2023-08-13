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


REPORT = JSNode(problem = JSNode(
    title = 'DATA_PATH',
    context = 'uber pickups across NY boroughs.',
    target = 'pickups',
    factors = ['temporal','seasonal','geographical']
    )
)

REPORT = REPORT.update(data = JSNode(
    shape = 'shape'
))

sdsd = REPORT.get_property('data')
sdsd = sdsd.adddata(a=2)
tt = type(sdsd)

print('asd')