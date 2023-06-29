"""
Created on Tue May  2 17:32:22 2023

@author: trianaa1

This script visualize the preprocessed heart and respiration rate from the BIOPAC
"""

import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.colors import ListedColormap, BoundaryNorm
import seaborn as sns

from scipy.io import loadmat

################################ Modify these #################################
path = "/m/cs/scratch/networks-pm/pm_preprocessed"
tasks = ['pvt', 'resting', 'movie', 'nback']
savepath = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results"
###############################################################################

def get_averages(dc):
    #get the average signal
    avg_df = pd.DataFrame()

    for i in range(30):
        session_data = []
        for key in dc.keys():
            session_data.append(dc[key].iloc[:,i])
        session_df = pd.concat(session_data, axis=1)
        avg_df[i] = session_df.mean(axis=1, skipna=True)
    return avg_df

# List of sessions
sub_list = next(os.walk(path))[1]
ban_list = ['logs', 'sourcedata']
sub_list = [x for x in sub_list if x not in ban_list]
sub_list.sort()

# load heart and respiration rate
bio_heart, bio_breath  = {}, {}
for task in tasks:
    print(task)
    suf = f'task-{task}_device-biopac_downsampledcut.mat'
    heart, breath = [], []
    for sub in sub_list:
        file = f'{path}/{sub}/func/{sub}_{suf}'
        if os.path.isfile(file):
            data = loadmat(file)
            heart.append(data['downsampled_cut'][1,:])
            breath.append(data['downsampled_cut'][0,:])
        else:
            heart.append(np.zeros_like(heart[0]))
            breath.append(np.zeros_like(breath[0]))
    
    #set all data in dataframes
    data = np.transpose(heart)
    heart_df = pd.DataFrame(data, columns=sub_list)
    
    data = np.transpose(breath)
    breath_df = pd.DataFrame(data, columns=sub_list)
    
    heart_df.columns = heart_df.columns.str.replace('sub-', '') # change the column names
    breath_df.columns = breath_df.columns.str.replace('sub-', '') # change the column names
    bio_heart[task] = heart_df
    bio_breath[task] = breath_df

avg_heart = get_averages(bio_heart)
avg_breath = get_averages(bio_breath)

#Visualize per task

#Create the colormap
tableau_10 = [(78, 121, 167), (242, 142, 43), (225, 87, 89), (118, 183, 178)]
for i in range(len(tableau_10)):  
    r, g, b = tableau_10[i]  
    tableau_10[i] = (r / 255., g / 255., b / 255.)  
color_map = {key: color for key, color in zip(bio_heart.keys(), tableau_10)}

# Assuming axs is a flat list of your subplots
fig, axs = plt.subplots(6,5,figsize=(15,15))  # replace with your actual figure and axes
axs = axs.flatten()

for i in range(30):  # Iterate over each session
    for key in bio_heart.keys():  # Iterate over each task
        df = bio_heart[key]  # Get the DataFrame for the current task
        axs[i].plot(df.iloc[:, i], color=color_map[key], label=key, alpha=0.7) 
        axs[i].plot(avg_heart.iloc[:,i], color='k', label='average')
        axs[i].set_title(f'session {i+1}')  # Set the title for the subplot

        axs[i].set_xlim([0, 1120])  # Set x limits
        axs[i].set_ylim([30, 130])  # Set y limits
        axs[i].set_ylabel("heart rate (bpm)")
        axs[i].set_xlabel("TR")        
        
        if (i // 5) != 5:  # Hide xticks on all but the bottom subplots
            axs[i].set_xticks([])
            axs[i].set_xlabel("")
        
        if (i % 5) != 0:  # Hide yticks on all but the leftmost subplots
            axs[i].set_yticks([])
            axs[i].set_ylabel("")

lines = [mlines.Line2D([], [], color=color_map[key]) for key in bio_heart.keys()]
labels = list(bio_heart.keys())
fig.legend(lines, labels, loc='upper center', ncol=len(labels))
plt.savefig(f'{savepath}/quality-biopac_meas-hr_style-spaguetti.pdf')

# Assuming axs is a flat list of your subplots
fig, axs = plt.subplots(6,5,figsize=(15,15))  # replace with your actual figure and axes
axs = axs.flatten()

for i in range(30):  # Iterate over each session
    for key in bio_breath.keys():  # Iterate over each task
        df = bio_breath[key]  # Get the DataFrame for the current task
        axs[i].plot(df.iloc[:, i], color=color_map[key], label=key, alpha=0.7) 
        axs[i].plot(avg_breath.iloc[:,i], color='k', label='average')
        axs[i].set_title(f'session {i+1}')  # Set the title for the subplot

        axs[i].set_xlim([0, 1120])  # Set x limits
        axs[i].set_ylim([0, 30])  # Set y limits
        axs[i].set_ylabel("respiration \nrate (bpm)")
        axs[i].set_xlabel("TR")        
        
        if (i // 5) != 5:  # Hide xticks on all but the bottom subplots
            axs[i].set_xticks([])
            axs[i].set_xlabel("")
        
        if (i % 5) != 0:  # Hide yticks on all but the leftmost subplots
            axs[i].set_yticks([])
            axs[i].set_ylabel("")

lines = [mlines.Line2D([], [], color=color_map[key]) for key in bio_heart.keys()]
labels = list(bio_heart.keys())
fig.legend(lines, labels, loc='upper center', ncol=len(labels))
plt.savefig(f'{savepath}/quality-biopac_meas-breath_style-spaguetti.pdf')


#The same but for session, in heatmap forms
bounds = [0, 30, 50, 70, 90, 110, 130]
colors = ['#000000', '#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
cmap = ListedColormap(colors)
norm = BoundaryNorm(bounds, cmap.N)

fig, axs = plt.subplots(6,5,figsize=(15,15))  # replace with your actual figure and axes
axs = axs.flatten()

for i in range(30):
    session_data = []
    for key in bio_heart.keys():
        session_data.append(bio_heart[key].iloc[:,i])
    session_df = pd.concat(session_data, axis=1)
    session_df.columns = ['pvt','resting','movie','n-back']  
    
    if i // 5 == 5:
        sns.heatmap(session_df, cmap=cmap, norm=norm, ax=axs[i], xticklabels=True, yticklabels=False)
        axs[i].set_xlabel("session")
    else:
        sns.heatmap(session_df, cmap=cmap, norm=norm, ax=axs[i], xticklabels=False, yticklabels=False)
    
    if i % 5 == 0:
        axs[i].set_ylabel("TR")
plt.savefig(f'{savepath}/quality-biopac_meas-heart_style-heatmap.pdf')


fig, axs = plt.subplots(6,5,figsize=(15,15))  # replace with your actual figure and axes
axs = axs.flatten()

for i in range(30):
    session_data = []
    for key in bio_breath.keys():
        session_data.append(bio_breath[key].iloc[:,i])
    session_df = pd.concat(session_data, axis=1)
    session_df.columns = ['pvt','resting','movie','n-back']  
    
    if i // 5 == 5:
        sns.heatmap(session_df, cmap='autumn_r', ax=axs[i], xticklabels=True, yticklabels=False)
        axs[i].set_xlabel("session")
    else:
        sns.heatmap(session_df, cmap='autumn_r', ax=axs[i], xticklabels=False, yticklabels=False)
    
    if i % 5 == 0:
        axs[i].set_ylabel("TR")
plt.savefig(f'{savepath}/quality-biopac_meas-breath_style-heatmap.pdf')