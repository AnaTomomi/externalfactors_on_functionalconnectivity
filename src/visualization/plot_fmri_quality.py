"""
This script checks for data missing patterns in the fMRI data


Input: path where all the preprocessed data is
Output: path where the figure will be saved

@author: trianaa1
"""
import os
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
eye = eye*100
eye.rename_axis('session', inplace=True)

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
    axes[i].set_ylabel('session')

plt.savefig(f'{savepath}/quality-fmri_averages.pdf')

#Violin plots
path = '/m/cs/scratch/networks-pm/pm_preprocessed'

tasks = ['pvt', 'resting', 'movie', 'nback']
cuts = {'pvt':[54,1064],'resting':[47,1057],'movie':[47,1018],'nback':[0,624]}

#list the subjects
subjects = next(os.walk(path))[1]
ban_list = ['logs', 'sourcedata']
subjects = [x for x in subjects if x not in ban_list]
subjects.sort()

mean_fd = {}
for task in tasks:
    mean_fd[task] = []
    for subject in subjects:
        df = pd.read_csv(f'{path}/{subject}/func/{subject}_task-{task}_desc-confounds_timeseries.tsv', sep='\t')
        df = df['framewise_displacement']
        start_vol = cuts[task][0]
        end_vol = cuts[task][1]
        mean_fd[task].append(df.loc[start_vol:end_vol])
    mean_fd[task] = pd.concat(mean_fd[task], axis=1)
    mean_fd[task].columns = subjects
    mean_fd[task].columns = mean_fd[task].columns.str.replace('sub-', '')

fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(13,13))
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)

label = ['A.', 'B.', 'C.', 'D.']
for i, key in enumerate(mean_fd): 
    df = mean_fd[key]
    df.dropna(inplace=True)
    df_melted = df.melt(var_name='Session', value_name='Value')
    ax = sns.violinplot(x='Session',y='Value',data=df_melted,ax=axes[i])
    trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
    axes[i].text(0.0, 1.0, label[i], transform=axes[i].transAxes + trans, va='bottom')
    axes[i].set_ylim(0, 1.5)
    axes[i].set_ylabel('framewise \ndisplacement')
    if i != len(mean_fd) - 1:  # If not the last subplot, clear the x-label
        axes[i].set_xlabel('')

axes[-1].set_xlabel('session')
plt.tight_layout()

plt.savefig(f'{savepath}/quality-fmri_violin.pdf')