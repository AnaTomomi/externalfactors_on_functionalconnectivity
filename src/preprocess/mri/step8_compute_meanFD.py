"""
This script computes the mean framewise displacement 

@author: trianaa1
"""
import os
import pandas as pd

path = '/m/cs/scratch/networks-pm/pm_preprocessed'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri'

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
        mean_fd[task].append(df.loc[start_vol:end_vol].mean())

mean_fd = pd.DataFrame.from_dict(mean_fd)
mean_fd.index = 'sub-' + (mean_fd.index + 1).astype(str).str.zfill(2)

mean_fd.to_csv(f'{savepath}/sub-01_day-all_device-mri_meas-meanfd.csv')