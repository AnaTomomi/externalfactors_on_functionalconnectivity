"""
This script organizes the ring data, convertig the timestamps to DD-MM-YYYY format

@author: trianaa1
"""
import sys
import pandas as pd

file = "/m/cs/project/networks-pm/behavioral/sub-01_day-all_device-oura.csv"
savefile = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral/sub-01_day-all_device-oura.csv"

df = pd.read_csv(file, index_col=0)
df.sort_index(inplace=True)
df.index = pd.to_datetime(df.index).strftime('%d-%m-%Y')

df = df.loc['01-01-2023':'13-05-2023']

df.to_csv(savefile)