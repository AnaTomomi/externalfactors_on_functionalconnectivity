"""
This script computes the exact volumes where the sequences need to be cut

@author: trianaa1
"""

import os, re
import pandas as pd

path ="/m/cs/archive/networks-pm/cognitive"
days = pd.read_csv(f'/m/cs/project/networks-pm/mri/fast_prepro_bids/participants.tsv',sep='\t')
tr = 0.594

tasks = {'pvt':[1116,'Instruction screen present','End screen present'], 
         'resting':[1102, 'sync', 'last'], 
         'movie':[1059,'sync','video1','last'], 
         'nback':[614, 'dual_block','end']}

#Select the MRI sessions
files = [f for f in os.listdir(path) if f.endswith('.log')]
files.sort()

filtered_files = []
for file in files:
    day = int(re.search('day-(\d+)', file).group(1))
    if day in days['day'].values:
        filtered_files.append(file)

cuts = pd.DataFrame(columns=['subject','task','low_cut','high_cut'])
for file in filtered_files:
    df = pd.read_csv(os.path.join(path,file), sep='\t', skiprows=[0,1,2])
    task = re.search('task-+([\w]+)\.log', file).group(1)
    sub = file[0:6]
    
    #Take into account that we have discarded the first 5 volumes
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    df['Time'] = df['Time']/10
    mri_pulse_time = df[df['Code'] == 'MRI pulse received']['Time'].iloc[0]
    df['Time'] = round(df['Time']-mri_pulse_time)-(5*(tr*1000))
    
    # Filtering the 5 volumes cut at the beginning.
    #This is exactly how the image is input to fmriprep
    df = df[(df['Time'] >= 0)]
        
    if task =='movie':
        movie_start = df.loc[df['Code'].shift(-1) == 'video1', 'Time'].iloc[0]
        movie_end = df.loc[df['Code'].shift(1) == 'last', 'Time'].iloc[0]
        df = df[df["Event Type"]=="Pulse"]
        df.reset_index(inplace=True)
        
        #select the movie segment only
        df = df[(df['Time'] > movie_start) & (df['Time'] < movie_end)]
        cut = pd.DataFrame([{'subject': sub, 'task':task, 'low_cut':df.index[0], 'high_cut':df.index[-1]}])
        cuts = pd.concat([cuts, cut], ignore_index=True)
        
    elif task.lower() =='nback':
        # the cut was so minimal that there are only 3 TRs outside the task, let's leave it as it is
        df = df[df["Event Type"]=="Pulse"]
        df.reset_index(inplace=True)
        cut = pd.DataFrame([{'subject': sub, 'task':task, 'low_cut':df.index[0], 'high_cut':df.index[-1]}])
        cuts = pd.concat([cuts, cut], ignore_index=True)
    
    elif task =='pvt':
        for i in range(len(df) - 1):
            if df['Trial'].iloc[i] == '4' and df['Trial'].iloc[i + 1] != '4':
                pvt_start = df.iloc[i-1]['Time']
        pvt_end =  df.loc[df['Code'].shift(1) == 'End screen present', 'Time'].iloc[0]
        df = df[df["Event Type"]=="Pulse"]
        df.reset_index(inplace=True)
        
        #select the pvt segment only
        df = df[(df['Time'] > pvt_start) & (df['Time'] < pvt_end)]
        cut = pd.DataFrame([{'subject': sub, 'task':task, 'low_cut':df.index[0], 'high_cut':df.index[-1]}])
        cuts = pd.concat([cuts, cut], ignore_index=True)
        
    elif task=='resting':
        rest_start = df.loc[df['Code'].shift(-1) == 'sync', 'Time'].iloc[0]
        rest_end = df.loc[df['Code'].shift(1) == 'last', 'Time'].iloc[0]
        df = df[df["Event Type"]=="Pulse"]
        df.reset_index(inplace=True)
        
        #select the movie segment only
        df = df[(df['Time'] > rest_start) & (df['Time'] < rest_end)]
        cut = pd.DataFrame([{'subject': sub, 'task':task, 'low_cut':df.index[0], 'high_cut':df.index[-1]}])
        cuts = pd.concat([cuts, cut], ignore_index=True)
        
    else:
        print("task not supported")  
