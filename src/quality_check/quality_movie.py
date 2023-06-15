#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  2 17:32:22 2023

@author: trianaa1

This script visualize the FD for the movie watching task
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def count_volumes(df, thr):
    """Counts the number of volumes over a threshold for each TR.

        Parameters
        ----------
        df : dataframe
            A dataframe containing the FD values as computed from fmriprep. 
            The rows should be the TR, the columns should be the subjects. 

        Returns
        ------
        df_copy : dataframe
            A dataframe indicating the number of volumes over the threshold for
            each timepoint TR.
        """
    df_copy = df.copy()
    mask = df_copy > thr  # Apply boolean mask over DataFrame
    df_copy['bad_vol'] = mask.sum(axis=1) # Count values that are True (i.e., exceed the threshold)

    return df_copy[['bad_vol']]
    
    

path = "/m/cs/scratch/networks-pm/pm_preprocessed"
suf = "task-movie_desc-confounds_timeseries.tsv"
savepath = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results"
thr = 0.2
percent = 0.1

# List of paths
sub_list = next(os.walk(path))[1]
ban_list = ['logs', 'sourcedata']
sub_list = [x for x in sub_list if x not in ban_list]
sub_list.sort()

# load FDs
fds = []
for sub in sub_list:
    print(sub)
    
    #read confound data from bids
    file_fd = f'{path}/{sub}/func/{sub}_{suf}'
    
    if os.path.isfile(file_fd):
        fd = pd.read_csv(file_fd, sep ='\t')
        fd = fd["framewise_displacement"]
        fd.rename(sub, inplace=True)
        fds.append(fd)

# merge all fds in order and save
df = pd.concat(fds, axis=1)
df.dropna(inplace=True) #at this point, only discards the first volume
df.columns = df.columns.str.replace('sub-', '') # change the column names

# count number of bad volumes per TR
bad_vol = count_volumes(df, thr)

# Visualize the data quality with hard threshold
fds = df.copy()
fds = fds.where(fds < thr) # For hard scrub
fds.loc[fds.isnull().any(axis=1),:] = np.nan # For hard scrub
discarded_volumes = (fds["01"].isna().sum()/len(fds))*100

#Visualize the data quality
cmap = sns.color_palette("Greys", as_cmap=True)
cmap.set_bad(color='red')

fig = plt.figure(figsize=(10, 10))
gs = gridspec.GridSpec(4, 1, figure=fig)

ax1 = fig.add_subplot(gs[:3, :])
sns.heatmap(fds.T, cmap=cmap, vmin=0, vmax=thr, xticklabels=False, yticklabels=True, ax=ax1)
ax1.set_ylabel("session")
ax1.set_xlabel("TR")
ax1.set_title(f'discarded volumes: {str(discarded_volumes)}%')

ax2 = fig.add_subplot(gs[3, :])
sns.lineplot(data=bad_vol, ax=ax2)
ax2.set_ylabel("number of af affected volumes")
ax2.set_xlabel("TR")

#plt.show()
plt.savefig(f'{savepath}/movie-quality_fd-{str(thr)}.pdf')

#Visualize the percent scrub 
fds = df.copy()
fds = fds.where((fds > thr).mean(axis=1) <= percent)
discarded_volumes = (fds["01"].isna().sum()/len(fds))*100

#Visualize the data quality
fig = plt.figure(figsize=(10, 10))
gs = gridspec.GridSpec(4, 1, figure=fig)

ax1 = fig.add_subplot(gs[:3, :])
sns.heatmap(fds.T, cmap=cmap, vmin=0, vmax=thr, xticklabels=False, yticklabels=True, ax=ax1)
ax1.set_ylabel("session")
ax1.set_xlabel("TR")
ax1.set_title(f'discarded volumes: {str(discarded_volumes)}%')

ax2 = fig.add_subplot(gs[3, :])
sns.lineplot(data=bad_vol, ax=ax2)
ax2.set_ylabel("number of af affected volumes")
ax2.set_xlabel("TR")

#plt.show()
plt.savefig(f'{savepath}/movie-quality_fd-{str(thr)}_per-{str(percent)}.pdf')