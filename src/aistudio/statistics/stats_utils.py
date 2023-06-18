import scipy.stats as stats
import numpy as np

def get_outlier_range(data,percentile = [25,75]):
    """
    Get the range of outliers in a dataset.
    
    Parameters
    ----------
    data : array-like
        The dataset.
    
    Returns
    -------
    outlier_range : tuple
        The range of outliers in the dataset.
    """
    
    # Get the quartiles
    q1, q3 = np.percentile(data, percentile)
    iqr = q3-q1
    
    # Get the lower and upper bounds
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    
    ranges = stats.percentileofscore(data, [lower_bound, upper_bound])

    return ranges
    
