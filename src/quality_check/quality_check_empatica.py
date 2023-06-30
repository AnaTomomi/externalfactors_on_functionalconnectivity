"""Computes the number of missing datapoints 

    Parameters
    ----------
    variable : str
        name of the variable to preprocess. It could be heart rate (hr), 
        temperature (temperature), electrodermal activity (electrodermal)
    path : str
        path where the raw data is stored
    savefile : str
        
    """
    
import os
import sys
import datetime as dt
import pandas as pd
import numpy as np

from glob import glob

path = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

files = []
pattern   = f'*device-embraceplus.csv'

for dir,_,_ in os.walk(path):
    files.extend(glob(os.path.join(dir,pattern))) 
print(f'checking data quality for {str(len(files))} files..................')

cols = ['pulse rate', 'pulse rate variability', 'breathing rate']
miss_df = pd.DataFrame(columns=cols)
for file in files:
    df = pd.read_csv(file)
    
    # Extract the day from the timestamp column
    day = pd.to_datetime(df['timestamp_iso']).dt.date[0]
    
    # Calculate the statistics
    loss_pr = df['pulse_rate_bpm'].isna().sum()
    loss_prv = df['prv_rmssd_ms'].isna().sum()
    loss_br = df['respiratory_rate_brpm'].isna().sum()

    # Create a temporary DataFrame to hold the current results
    temp_df = pd.DataFrame({'day': [day], 'pulse rate': [loss_pr], 
                            'pulse rate variability': [loss_prv], 'breathing rate': [loss_br]})
    
    # Concatenate the current results with the results DataFrame
    miss_df = pd.concat([miss_df, temp_df], ignore_index=True)

miss_df[cols] = miss_df[cols].apply(pd.to_numeric, errors='coerce')
miss_df['day'] = pd.to_datetime(miss_df['day'])
miss_df['day'] = miss_df['day'].dt.strftime('%d-%m-%Y')
miss_df.set_index('day', inplace=True)

#Compute this in percentages
miss_df = (miss_df/1440)*100

print(f'average data loss in percentage for empatica {miss_df.mean()}')

