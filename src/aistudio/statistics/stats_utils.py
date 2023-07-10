import scipy.stats as stats
from aistudio.abstraction.base_types import *
from aistudio.exception.exception_utils import *
from inspect import currentframe, getframeinfo

import numpy as np


def get_outlier_percentileofscores(data, percentiles:tuplargs = tuplargs([25.0,75.0]))->tuplargs:
    result = []
    for i,perc in enumerate(percentiles.args):
        if len(perc) !=2:
            (
               Interrupter('Only uppest and lowest percentile values are needed i.e. [25.0,75.0]',log=True,throw = True)
                .addkvps(filename = getframeinfo(currentframe()).filename)
                .addkvps(lineno = getframeinfo(currentframe()).lineno)
                .act() 
            )
        lower,upper = get_outlier_boundpairs(data,tuplargs(perc)).args[i]
        lowerdata,upperdata = stats.percentileofscore(data,[lower,upper])
        result.append([lowerdata,upperdata])
    
    return tuplargs(*result)
        
def get_outlier_boundpairs(data,percentiles:tuplargs=tuplargs([25.0,75.0]))->tuplargs:
    result = []
    for perc in percentiles.args:
        if len(perc) != 2:
            (
               Interrupter('Only uppest and lowest percentile values are needed i.e. [25.0,75.0]',log=True,throw = True)
                .addkvps(filename = getframeinfo(currentframe()).filename)
                .addkvps(lineno = getframeinfo(currentframe()).lineno)
                .act() 
            )
        q1,q3 = np.percentile(data,perc)
        iqr = q3-q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        lower_bound = lower_bound if lower_bound >= min(data) else min(data)
        upper_bound = upper_bound if upper_bound <= max(data) else max(data)
        result.append((lower_bound,upper_bound))
        
    return tuplargs(*result)


def get_outlier_bounds(data,percentile=[25,75]):
    if len(percentile) != 2:
        Interrupter('Only uppest and lowest percentile values are needed i.e. [25.0,75.0]',log=True,throw = True)\
        .addkvps(filename = getframeinfo(currentframe()).filename)\
        .addkvps(lineno = getframeinfo(currentframe()).lineno)\
        .act() 
        
    q1,q3 = np.percentile(data,percentile)
    iqr = q3-q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    lower_bound = lower_bound if lower_bound >= min(data) else min(data)
    upper_bound = upper_bound if upper_bound <= max(data) else max(data) 
    return (lower_bound,upper_bound)

def agg_lower_outlierbound(data):
    return get_outlier_bounds(data)[0]

def agg_upper_outlierbound(data):
    return get_outlier_bounds(data)[1]