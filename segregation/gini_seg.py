"""
Gini Segregation Metrics
"""

__author__ = "Renan X. Cortes <renanc@ucr.edu> and Sergio J. Rey <sergio.rey@ucr.edu>"

import numpy as np
import pandas as pd

__all__ = ['Gini_Seg']


def _gini_seg(data, group_pop_var, total_pop_var):
    """
    Calculation of Gini Segregation index
    Parameters
    ----------
    data          : a pandas DataFrame
    
    group_pop_var : string
                    The name of variable in data that contains the population size of the group of interest
                    
    total_pop_var : string
                    The name of variable in data that contains the total population of the unit
    Attributes
    ----------
    statistic : float
                Gini Segregation Index
                
    core_data : a pandas DataFrame
                A pandas DataFrame that contains the columns used to perform the estimate. 
                
    Notes
    -----
    Based on Massey, Douglas S., and Nancy A. Denton. "The dimensions of residential segregation." Social forces 67.2 (1988): 281-315.
    """
    if((type(group_pop_var) is not str) or (type(total_pop_var) is not str)):
        raise TypeError('group_pop_var and total_pop_var must be strings')
    
    if ((group_pop_var not in data.columns) or (total_pop_var not in data.columns)):    
        raise ValueError('group_pop_var and total_pop_var must be variables of data')

    data = data.rename(columns={group_pop_var: 'group_pop_var', 
                                total_pop_var: 'total_pop_var'})
    
    if any(data.total_pop_var < data.group_pop_var):    
        raise ValueError('Group of interest population must equal or lower than the total population of the units.')
   
    T = data.total_pop_var.sum()
    P = data.group_pop_var.sum() / T
    
    # If a unit has zero population, the group of interest frequency is zero
    data = data.assign(ti = data.total_pop_var,
                       pi = np.where(data.total_pop_var == 0, 0, data.group_pop_var/data.total_pop_var))
    
    num = (np.matmul(np.array(data.ti)[np.newaxis].T, np.array(data.ti)[np.newaxis]) * abs(np.array(data.pi)[np.newaxis].T - np.array(data.pi)[np.newaxis])).sum()
    den = (2 * T**2 * P * (1-P))
    G = num / den
    
    core_data = data[['group_pop_var', 'total_pop_var']]
    
    return G, core_data


class Gini_Seg:
    """
    Classic Gini Segregation Index
    Parameters
    ----------
    data          : a pandas DataFrame
    
    group_pop_var : string
                    The name of variable in data that contains the population size of the group of interest
                    
    total_pop_var : string
                    The name of variable in data that contains the total population of the unit
    Attributes
    ----------
    statistic : float
                Gini Segregation Index
                
    core_data : a pandas DataFrame
                A pandas DataFrame that contains the columns used to perform the estimate. 
                
    Examples
    --------
    In this example, we will calculate the Gini Segregation Index (G) for the Riverside County using the census tract data of 2010.
    The group of interest is non-hispanic black people which is the variable nhblk10 in the dataset.
    
    Firstly, we need to read the data:
    
    >>> This example uses all census data that the user must provide your own copy of the external database.
    >>> A step-by-step procedure for downloading the data can be found here: https://github.com/spatialucr/osnap/tree/master/osnap/data.
    >>> After the user download the LTDB_Std_All_fullcount.zip and extract the files, the filepath might be something like presented below.
    >>> filepath = '~/data/std_2010_fullcount.csv'
    >>> census_2010 = pd.read_csv(filepath, encoding = "ISO-8859-1", sep = ",")
    
    Then, we filter only for the desired county (in this case, Riverside County):
    
    >>> df = census_2010.loc[census_2010.county == "Riverside County"][['pop10','nhblk10']]
    
    The value is estimated below.
    
    >>> gini_seg_index = Gini_Seg(df, 'nhblk10', 'pop10')
    >>> gini_seg_index.statistic
    0.44620350030600087
       
    Notes
    -----
    Based on Massey, Douglas S., and Nancy A. Denton. "The dimensions of residential segregation." Social forces 67.2 (1988): 281-315.
    """

    def __init__(self, data, group_pop_var, total_pop_var):
        
        aux = _gini_seg(data, group_pop_var, total_pop_var)

        self.statistic = aux[0]
        self.core_data = aux[1]
        self._function = _gini_seg