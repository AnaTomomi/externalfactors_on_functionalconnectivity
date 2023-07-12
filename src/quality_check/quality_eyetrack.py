#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script generates two plots to check the data quality for the eye-tracking 
data. The first plot is a distribution of the fixation duration. According to 
Mahanama et al. 2022, the duration of fixation in one point typically lasts 
between 30 and 300 ms, and may be longer depending on the cognitive load. 

The second plot is a lineplot for the eye's position in the x-axis. This is only
generated for the resting-state task, as it is the task of interest where we will
use the eye-tracker as a regressor. Therefore, we want to make sure the data is 
reliably collected. 

Mahanama et al., 2022: https://doi.org/10.3389/fcomp.2021.733531

Input:  root_dir: path where the eye-tracker data is stored in csv format
        save_dir: path where the plots will be stored
Output: PDFs

@author: trianaa1
"""

import os, sys
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns

root_dir = sys.argv[1]
save_dir = sys.argv[2]

subjects = [os.path.basename(f.path) for f in os.scandir(root_dir) if f.is_dir()]
subjects = sorted(subjects)
tasks = ['pvt', 'resting', 'movie', 'nback']


fixation = {}
fix_pos = {}
for subject in subjects:
    fixation[subject] = []
    fix_pos[subject] = []
    for task in tasks:
        df = pd.read_csv(f'{root_dir}/{subject}/func/{subject}_task-{task}_device-eyetrack.csv', index_col=0)
        
        fix = df.loc[df['EVENT']=='fix','FIX_DURATION']
        pos = df.loc[df['EVENT']=='fix', ['FIX_X','FIX_Y']]
        
        fixation[subject].append(fix)
        fix_pos[subject].append(pos)

#plot the fixation duration
fig, axs = plt.subplots(6,5,figsize=(15,15))  # replace with your actual figure and axes
axs = axs.flatten()

for i, (key, series_list) in enumerate(fixation.items()):
    df = pd.concat(series_list, axis=1)
    df.columns = ['pvt', 'resting', 'movie', 'n-back'] 

    #sns.kdeplot(data=df, ax=axs[i], fill=True, legend=False)
    for column in df.columns:
        sns.histplot(data=df, x=column, ax=axs[i], bins=15, 
                     kde=False, label=column, multiple="stack", alpha=0.5,
                     edgecolor=None) # you can adjust the number of bins
    
    axs[i].set_title(key.replace('sub', 'ses'))
    axs[i].axvline(30, color='black',linestyle='--') #average fixation duration
    axs[i].axvline(300, color='black',linestyle='--') #average fixation duration
    axs[i].set_xlim([0, 1500])  # Set x limits
    #axs[i].set_ylim([0, 0.005])  # Set y limits
    axs[i].set_ylabel("count")
    axs[i].set_xlabel("duration (ms)")        
    
    if (i // 5) != 5:  # Hide xticks on all but the bottom subplots
        axs[i].set_xticks([])
        axs[i].set_xlabel("")
    
    if (i % 5) != 0:  # Hide yticks on all but the leftmost subplots
        #axs[i].set_yticks([])
        axs[i].set_ylabel("")
        
legend_handles = [mlines.Line2D([], [], color=sns.color_palette()[i], label=tasks[i]) for i in range(4)]
fig.legend(handles=legend_handles, loc='upper center', ncol=5)

plt.savefig(f'{save_dir}/quality-eyetracker_meas-fixdur_style-histogram.pdf')

#plot the x and y position for the resting state, where we will use the eye-tracker info
keys = list(fix_pos.keys())
values = list(fix_pos.values())

fig, axes = plt.subplots(6, 5, figsize=(15,15))
axes = axes.flatten()
base_fontsize = 10
for idx, (key, value_list) in enumerate(zip(keys, values)):
    data = value_list[1]['FIX_X'] # Get the second dataframe (index 1) and column 'FIX_X'
        
    if idx==2 or idx==8:
        sns.lineplot(ax=axes[idx], data=data, color='red')
        axes[idx].tick_params(axis='x', colors='red')
    else:
        sns.lineplot(ax=axes[idx], data=data)
    
    axes[idx].set_title(key.replace('sub', 'ses'))
    axes[idx].set_ylabel("eye x-position")
    axes[idx].set_xlabel("time")  
    axes[idx].set_ylim([-1000, 2000]) 
    
    if (idx // 5) != 5: 
        axes[idx].set_xlabel("")
    
    if (idx % 5) != 0: 
        axes[idx].set_yticks([])
        axes[idx].set_ylabel("")

plt.tight_layout()
plt.subplots_adjust(hspace = 0.7, wspace=0.3)
plt.savefig(f'{save_dir}/quality-eyetracker_task-resting_meas-fixpos_style-lineplot.pdf')