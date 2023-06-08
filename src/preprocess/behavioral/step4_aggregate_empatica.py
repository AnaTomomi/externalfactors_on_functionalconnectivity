"""Preprocess empatica data. Reads all empatica data splitted in days, 
    aggregates them by day, and saves them in the given savepath.
    
    The input should be done in the following order:

    Parameters
    ----------
    path : str
        path where the raw data is stored
    savefile : str
        
    """
    
import os
import sys
import datetime as dt
import pandas as pd

path = sys.argv[1]
savepath = sys.argv[2]

#Select the empatica files
all_files = os.listdir(path)
csv_files = [f for f in all_files if f.endswith('device-embraceplus.csv')]

dataframes = []
for file_name in csv_files:
    df = pd.read_csv(os.path.join(path,file_name), index_col="timestamp_iso", parse_dates=True)
    dataframes.append(df)
big_df = pd.concat(dataframes)

# Sort the DataFrame by the index (timestamp_iso)
big_df.sort_index(inplace=True)

#Compute the basic statistics
big_df.drop(columns=['missing_value_reason','wearing_detection_percentage','sleep_detection_stage'],inplace=True)

df_min = big_df.resample('1D').min()
df_max = big_df.resample('1D').max()
df_mean = big_df.resample('1D').mean()
df_median = big_df.resample('1D').median()
df_std = big_df.resample('1D').std()

df_min.columns = [f'min_{col}' for col in df_min.columns]
df_max.columns = [f'max_{col}' for col in df_max.columns]
df_mean.columns = [f'mean_{col}' for col in df_mean.columns]
df_median.columns = [f'median_{col}' for col in df_median.columns]
df_std.columns = [f'std_{col}' for col in df_std.columns]

#merge the two DataFrames together
df_merged = pd.concat([df_min, df_max, df_mean, df_median, df_std], axis=1)

#save the dataframe
df_merged.to_csv(f'{savepath}/sub-01_day-all_device-embraceplus.csv')