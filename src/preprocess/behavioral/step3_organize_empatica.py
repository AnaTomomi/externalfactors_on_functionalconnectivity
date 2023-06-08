"""Re order the empatica files and name it using the pre-established convention.
    This script will unify the different measurements splitted in several files 
    into one dataframe per day. The dataframe is stored as a csv file. 
    
    The input should be done in the following order:

    Parameters
    ----------
    path : str
        path where the raw data is stored
    savepath : str
        path where the raw data is stored
    """

import os
import sys
import pandas as pd

path = sys.argv[1]
savepath = sys.argv[2]

#Create the dataframe with dates and day numbers
date_range = pd.date_range(start='2023-01-01', end='2023-05-14')
data = {'folder': date_range.strftime('%Y-%m-%d'), 
        'day': ['day-' + str(i).zfill(3) for i in range(1, len(date_range)+1)]}
df = pd.DataFrame(data)

#Now start moving the files and name them according to the convention
for index, row in df.iterrows():
    subfolder = f'{path}/{row["folder"]}/SUB01-3YK3H1511X/digital_biomarkers/aggregated_per_minute'
    if os.path.isdir(subfolder):
        files = [f for f in os.listdir(subfolder)]
        all_data =[]
        for file in files:
            data = pd.read_csv(f'{subfolder}/{file}')
            data.set_index("timestamp_iso", inplace=True)
            data.drop(columns=['timestamp_unix', 'participant_full_id'], inplace=True)
            all_data.append(data)
        data = all_data[0]
        for dataf in all_data[1:]:
            data = data.combine_first(dataf)
        data.to_csv(f'{savepath}/sub-01_{row["day"]}_device-embraceplus.csv')
    print(f'{row["folder"]} done!')