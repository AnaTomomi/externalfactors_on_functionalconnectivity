"""
Created on Tue May  2 17:32:22 2023

@author: trianaa1

This script visualize the FD for all the MRI tasks
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

################################ Modify these #################################
path = "/m/cs/scratch/networks-pm/pm_preprocessed"
tasks = ['pvt', 'resting', 'movie', 'nback']
savepath = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results"
###############################################################################

# List of sessions
sub_list = next(os.walk(path))[1]
ban_list = ['logs', 'sourcedata']
sub_list = [x for x in sub_list if x not in ban_list]
sub_list.sort()

# load FDs
task_fd = {}
for task in tasks:
    print(task)
    suf = f'task-{task}_desc-confounds_timeseries.tsv'
    fds = []
    for sub in sub_list:
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
    task_fd[task] = df

#Visualize the FDs alone
for task in tasks:
    print(task)
    fig, axs = plt.subplots(6, 5, figsize=(15, 18)) # Adjust grid size and figure size as needed
    axs = axs.ravel()  # Flatten the array of axes
    
    df = task_fd[task]
    for i, col in enumerate(df.columns):
        axs[i].plot(df[col])
        axs[i].axhline(y=0.2, color='r', linestyle='--')  # Adds horizontal line at y=0.2
        axs[i].axhline(y=0.5, color='g', linestyle='--')  # Adds horizontal line at y=0.5
        axs[i].set_title(f' session - {col}')
        axs[i].set_xlim([0, len(df)])  # Set x limits
        axs[i].set_ylim([0, 1.2])  # Set y limits
        axs[i].set_ylabel("framewise displacement")
        axs[i].set_xlabel("TR")
        
        if (i // 5) != 5:  # Hide xticks on all but the bottom subplots
            axs[i].set_xticks([])
            axs[i].set_xlabel("")
        
        if (i % 5) != 0:  # Hide yticks on all but the leftmost subplots
            axs[i].set_yticks([])
            axs[i].set_ylabel("")

    plt.tight_layout()  # Adjusts subplot params so that subplots do not overlap
    #plt.show()
    plt.savefig(f'{savepath}/{task}-fd.pdf')