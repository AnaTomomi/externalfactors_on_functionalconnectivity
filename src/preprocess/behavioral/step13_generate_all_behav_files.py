"""
Automatically create all the behavioral files

@author: trianaa1
"""
import pandas as pd
import sys, os

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data, get_behav_data_15days, get_behav_data_tasks, get_behav_data_movie

behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral/'

#select the days
scan_days = pd.read_csv(os.path.join(f'{behav_path.rsplit("/", 2)[0]}/mri','sub-01_day-all_device-mri.csv'), header=0)
scan_days = scan_days[['date']]
scan_days['date'] = pd.to_datetime(scan_days['date'], format='%d/%m/%y')

#Create the behavioral data for pvt
behav = get_behav_data_tasks(behav_path, lag=1)
behav.to_excel(f'{behav_path}/sub-01_day-lag1_task_pvt.xlsx',index=False)

#Create the behavioral data for rs
sleep = get_behav_data_movie(behav_path, variable='sleep', lag=1)
mood = get_behav_data_movie(behav_path, variable='mood', lag=1)
phys = get_behav_data_movie(behav_path, variable='phys', lag=1)

sleep.index = pd.RangeIndex(start=0, stop=30, step=1)
mood.index = pd.RangeIndex(start=0, stop=30, step=1)
phys.index = pd.RangeIndex(start=0, stop=30, step=1)

behav = pd.concat([sleep, mood, phys], axis=1, join='inner')
behav.to_excel(f'{behav_path}/sub-01_day-lag1_task_movie.xlsx',index=False)

#Generate the lagged data
lagged = get_behav_data_15days(behav_path, days=16, behav=None)
lagged.to_excel(f'{behav_path}/sub-01_day-lag-all_task_all.xlsx',index=True)

#all data 
all_data = get_behav_data(behav_path)
all_data.to_excel(f'{behav_path}/sub-01_day-all_device-all.xlsx',index=True)