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

path = "/m/cs/scratch/networks-pm/pm_preprocessed"
suf = "task-movie_desc-confounds_timeseries.tsv"
savepath = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results"

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

thr = 0.5
cmap = sns.color_palette("Greys", as_cmap=True)
cmap.set_bad(color='red')

# Visualize the data quality with hard threshold
fds = df.copy()
fds = fds.where(fds < thr) # For hard scrub
fds.loc[fds.isnull().any(axis=1),:] = np.nan # For hard scrub
discarded_volumes = (fds["sub-01"].isna().sum()/len(fds))*100

fig, axs = plt.subplots(1,1,figsize=(10, 10))
sns.heatmap(fds.T, cmap=cmap, vmin=0, vmax=thr, xticklabels=False, yticklabels=True, ax=axs)
axs.set_ylabel("session")
axs.set_xlabel("TR")
axs.set_title(f'discarded volumes: {str(discarded_volumes)}%')

#plt.show()
plt.savefig(f'{savepath}/movie-quality.pdf')
