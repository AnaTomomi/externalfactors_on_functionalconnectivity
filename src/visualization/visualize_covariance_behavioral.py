"""
This scripts only 
"""
import sys
import numpy as np
import pandas as pd
import seaborn as sns

from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import acf
import statsmodels.api as sm

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data

###############################################################################
# Change this only!
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral'
mri_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results'
###############################################################################

# Set the font properties
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 14

# load the z-scored data
behav = pd.read_excel(f'{behav_path}/sub-01_day-lag1_task_movie.xlsx')

#covariance matrix
corr = behav.corr(method='spearman')

#plot
colors = ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0',
          '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f']
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
norm = BoundaryNorm([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1], cmap.N)
annotations = np.where(abs(corr) > 0.7, '*', '')

plt.figure(figsize=(12, 10))
ax = sns.heatmap(corr, cmap=cmap, norm=norm, annot=annotations, fmt='', 
                 annot_kws={'size': 12}, 
                 cbar_kws={"ticks": [-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1]})
plt.tight_layout()
plt.savefig(f'{savepath}/quality-regressors.pdf')
