"""Re-order the smartphone files and name it following the pre-established criteria
    This script will unify the different measurements splitted in several files 
    into one dataframe that includes all days. The dataframe is stored as a csv 
    file. 
    
    The input should be done in the following order:

    Parameters
    ----------
    path : str
        path where the raw data is stored
    savepath : str
        path where the unified dataframe will be stored
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
all_data =[]
for index, row in df.iterrows():
    file = f'{path}/AwareESM.{row["folder"]}.csv'
    if os.path.isfile(file):
        data = pd.read_csv(file)
        data['date'] = pd.to_datetime(data['time_asked'],unit='s').dt.tz_localize('UTC').dt.tz_convert('Europe/Helsinki')
        #data['date'] = data['date'].dt.strftime('%d-%m-%Y %H:%M')
        
        data.set_index("date", inplace=True)
        data.drop(columns=['user', 'device', 'time', 'time_asked', 'type', 
               'instructions', 'submit', 'notification_timeout'], inplace=True)
        all_data.append(data)
    print(f'{row["folder"]} done!')
    
big_df = pd.concat(all_data)
big_df.sort_index(inplace=True)

big_df.to_csv(f'{savepath}/sub-01_day-all_device-smartphone_sensor-ema.csv')