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

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data

###############################################################################
# Change this only!
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results'
###############################################################################

# Set the font properties
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 14


behav = get_behav_data(behav_path)
cols = ['total_sleep_duration', 'awake_time', 'restless_sleep', 'steps', 
        'inactive_time', 'pa_mean', 'pa_std', 'na_mean', 'stress_mean',
        'pain_mean', 'mean_respiratory_rate_brpm', 'min_respiratory_rate_brpm',
        'max_respiratory_rate_brpm', 'mean_prv_rmssd_ms', 'min_prv_rmssd_ms',
        'max_prv_rmssd_ms', 'std_prv_rmssd_ms']
selected_behav = behav[cols]
selected_behav.rename(columns={"total_sleep_duration": "sleep duration", 
    "awake_time": "awake time", "restless_sleep": "restless sleep", 
    "inactive_time":"inactive time", "pa_mean":"mean positive affect", 
    "pa_std": "std positive affect", "na_mean": "mean negative affect", 
    "stress_mean": "mean stress", "pain_mean": "mean pain level",
    "mean_respiratory_rate_brpm":"mean respiratory rate",
    "min_respiratory_rate_brpm":"minimum respiratory rate", 
    "max_respiratory_rate_brpm":"maximum respiratory rate", 
    "mean_prv_rmssd_ms":"mean heart rate variability", 
    "min_prv_rmssd_ms":"minimum heart rate variability",
    "max_prv_rmssd_ms":"maximum heart rate variability",
    "std_prv_rmssd_ms":"std heart rate variability"}, inplace=True)


#Lags
nrows = 4
ncols = 5

fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(20, 15))
fig.subplots_adjust(hspace = 0.5, wspace=.5)

# Remove the unnecessary subplot axes in the first row.
for col in [0, 3, 4]:
    fig.delaxes(axs[0, col])

# Set the positions for the subplots based on your recap.
positions = [
    (0,1), (0,2),
    (1,0), (1,1), (1,2), (1,3), (1,4),
    (2,0), (2,1), (2,2), (2,3), (2,4),
    (3,0), (3,1), (3,2), (3,3), (3,4)
]

for i, column in enumerate(selected_behav.columns):
    row, col = positions[i]
    ax = axs[row, col]
    data_acf = acf(selected_behav[column].dropna(), nlags=15, alpha=0.05)
    ax.bar(range(len(data_acf[0])), data_acf[0], width=0.5, color='black', align='center')
    ax.axhline(y=0, color='black')
    ax.axhline(y=-1.96/np.sqrt(len(selected_behav[column].dropna())), linestyle='--', color='blue')
    ax.axhline(y=1.96/np.sqrt(len(selected_behav[column].dropna())), linestyle='--', color='blue')
    ax.set_ylim(-0.2, 1)
    ax.set_title(column)
    ax.grid(False)
    
    # Adjust ylabels and yticks for subplots that are not in the first column.
    if col != 0 and (row, col) != (0, 1):
        ax.set_ylabel('')
        ax.set_yticklabels([])
    else:
        ax.set_ylabel('ACF')
    
    # Adjust xlabels and xticks for subplots that are not in the last row.
    if row != 3:
        ax.set_xlabel('')
        ax.set_xticklabels([])
    else:
        ax.set_xlabel('Lag')

plt.tight_layout()
plt.show()