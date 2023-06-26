
import pandas as pd

import aistudio.runtime.runtime_utils as ru
from aistudio.abstraction.base_types import *
df_original = pd.read_pickle('examples/dscienc-cstudy/Uber-Pickups-Weather/bin.upw-clear.df.pkl')
df = df_original.copy()


#limitobjects=pu.Limit(x=(0, 4), y=(-1, 6))


#limitobjects = ru.param_itemize(param_s=limitobjects,maxlength = 3, expectedtypes = pu.Limit, defaultvalue = None)


var1 = ru.kwargsbase()
var2 = ru.tpargsbase()
var3 = ru.argskwargssbase()



print(ru.type_checker(var1,ru.kwargsbase))
print(ru.type_checker(var2,ru.tpargsbase))
print(ru.type_checker(var3,ru.tpargsbase))