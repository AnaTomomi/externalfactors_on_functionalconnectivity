"""
This script checks for data missing patterns in the fMRI data


Input: path where all the preprocessed data is
Output: path where the figure will be saved

@author: trianaa1
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results'

fd = pd.read_csv(f'{path}/sub-01_day-all_device-mri_meas-meanfd.csv', index_col=0)
fd.rename(columns={"nback":"n-back"}, inplace=True)
eye = pd.read_csv(f'{path}/sub-01_day-all_device-eyetracker.csv', index_col=0)
eye.rename(columns={"nback":"n-back"}, inplace=True)
eye.index = eye.index.str.replace('sub-', '')

dfs = [fd.transpose(), eye.transpose()]

label = ['A.', 'B.']
clabels = ['average FD', '% microsleep']

#two graphs
fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(15,8))
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)

cmap = sns.color_palette("YlGnBu", as_cmap=True)
cmap.set_bad(color='black')

for i, df in enumerate(dfs): 
    ax = sns.heatmap(df, cmap=cmap, cbar=False, annot=False, vmin=0, mask=df.isnull(), linewidths=.5, ax=axes[i])
    trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
    axes[i].text(0.0, 1.0, label[i], transform=axes[i].transAxes + trans, va='bottom')
    axes[i].set_ylabel('task')
    cbar = fig.colorbar(ax.get_children()[0], ax=ax, orientation='vertical')
    cbar.set_label(clabels[i], size=14)
    plt.setp(axes[i].get_yticklabels(), rotation=0)

plt.savefig(f'{savepath}/quality-fmri_averages.pdf')