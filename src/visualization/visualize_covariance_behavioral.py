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
behav.columns = behav.columns.str.replace('_', ' ')
replacements = {r"\bpa\b": "positive affect", "na": "negative affect", "brpm": "",
                "rmssd ms": "", "prv": "heart rate variability", "min": "minimum",
                "max": "maximum"}
for old, new in replacements.items():
    behav.columns = behav.columns.str.replace(old, new, regex=False)
behav.columns = behav.columns.str.strip()
behav.rename(columns={'pa mean': 'mean positive affect', 'pa median': 'median positive affect',
                      'pa minimum':'minimum positive affect', 'pa maximum': 'maximum positive affect', 
                      'pa std':'std positive affect', 'negative affect mean':'mean negative affect',
                      'negative affect median': 'median negative affect', 
                      'negative affect minimum': 'minimum negative affect',
                      'negative affect maximum': 'maximum negative affect', 
                      'negative affect std': 'std negative affect', 'stress mean': 'mean stress level',
                      'stress median':'median stress level', 'stress minimum':'minimum stress level', 
                      'stress maximum':'maximum stress level', 'stress std':'std stress level',
                      'pain mean':'mean pain level', 'pain median':'median pain level', 
                      'pain minimum':'minimum pain level', 'pain maximum':'maximum pain level', 
                      'pain std': 'std pain level'}, inplace=True)

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
