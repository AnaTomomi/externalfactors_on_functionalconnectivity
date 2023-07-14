"""
set of utility functions 

@author: trianaa1
"""
import os, glob
import pandas as pd
import numpy as np

from scipy.io import loadmat

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.transforms as mtransforms
import matplotlib

def find_missing(df):
    indices = list(np.where(df.isnull())[0])
    return indices

def find_missing_percent(df):
    return round(100*(len(list(np.where(df.isnull())[0]))/len(df)),2)

def highlight_datetimes(df, indices, ax):
    i = 0
    while i < len(indices):
        if indices[i] == 0:
            ax.axvspan(df.index[indices[i]], df.index[indices[i] + 1], facecolor='tomato', edgecolor='none')
        elif indices[i]==len(df)-1: #last index
            ax.axvspan(df.index[indices[i]-1], df.index[indices[i]], facecolor='tomato', edgecolor='none')
        else:
            ax.axvspan(df.index[indices[i]-1], df.index[indices[i] + 1], facecolor='tomato', edgecolor='none')
        i += 1
        

def create_linbins(start, end, n_bins):
    bins = np.linspace(start, end, n_bins)
    return bins
