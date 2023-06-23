import scipy.stats as stats
import numpy as np

def get_outlier_percentileofscore(data, percentile = [25.0,75.0]):
    """
    Returns the percentiles of scores of lower and upper outlier boundry data points as 1.5 * IQR according to given percentiles.
    """
    lower_bound,upper_bound = get_outlier_bounds(data,percentile)
    ranges = stats.percentileofscore(data, [lower_bound, upper_bound])

    return ranges
    
def get_outlier_bounds(data, percentile = [25.0,75.0]):
    """
    Returns the lower and upper points of (1.5 * IQR) defined by given percentiles
    """
    q1, q3 = np.percentile(data, percentile)
    iqr = q3-q1
    
    # Get the lower and upper bounds
    lower_bound = q1 - (1.5 * iqr) 
    upper_bound = q3 + (1.5 * iqr)

    lower_bound = lower_bound if lower_bound >= min(data) else min(data)
    upper_bound = upper_bound if upper_bound <= max(data) else max(data)


    return lower_bound,upper_bound