"""
This script reads organizes the scores given in the post-scanner scores. 

Inputs: file  

Outputs: csv file 

@author: trianaa1
"""

import os, glob, sys
import pandas as pd
import numpy as np

file = "/m/cs/archive/networks-pm/behavioral/questionnaires/post-scanner.xlsx"
save_file = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/questionnaires/sub-01_day-all_device-questionnaire_score-postscanner.csv"

df = pd.read_excel(file, header=3)
df = df.set_index('question').transpose()

# Rename columns
df.columns = df.columns.map({
    'During this session, I felt engaged on the PVT task': 'pvt_engagement',
    'During this session, I felt engaged on the resting state task': 'resting_engagement',
    'During this session, I felt engaged on the movie task': 'movie_engagement',
    'During this session, I felt engaged on the nback task': 'nback_engagement',
    'What were you thinking during the resting state task?': 'resting_thoughts',
    'What were you thinking during the movie task?': 'movie_thoughts',
    'During the session, I felt discomfort': 'discomfort',
    'During the session, I felt drowsy': 'drowsiness'
})

#drop the first column and set to numeric what can be numeric
df.drop(["id"], inplace=True)
df.index = pd.to_datetime(df.index, format='%d.%m.%Y')
df.insert(0, "subject", ["sub-" + str(i).zfill(2) for i in range(1, len(df) + 1)])
for col in ['pvt_engagement', 'resting_engagement', 'movie_engagement', 'nback_engagement', 'discomfort', 'drowsiness']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df.set_index('subject', inplace=True)

df.to_csv(save_file)