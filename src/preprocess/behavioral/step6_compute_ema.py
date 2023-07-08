"""Compute the negative and positive affect per day based on the EMA answers. 
    The script also stores relevant information about menstruation and weight.
    
    The input should be done in the following order:

    Parameters
    ----------
    file : str
        path where the EMA answers file is stored
    savepath : str
        path where the processed data will be stored
    """

import os
import sys
import pandas as pd

#file = sys.argv[1]
#savepath = sys.argv[2]

file = "/m/cs/project/networks-pm/behavioral/sub-01_day-all_device-smartphone_sensor-AwareESM.csv"
savepath = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral"

df = pd.read_csv(file, index_col="date", parse_dates=True)

# Drop the nans of unanswered questions
df.dropna(inplace=True)

# Change 'Yes' to 1 and 'No' to 0 in the answer column, but only if the 'yes' and 'no' are alone
df.loc[df['answer'] == 'Yes', 'answer'] = 1
df.loc[df['answer'] == 'No', 'answer'] = 0

# Change the ids from morning and evening so that their PANAS IDs match the daily's.
id_map = {"pm_06": "dq_01", "pm_07": "dq_02", "pm_08": "dq_03", "pm_09": "dq_04", 
          "pm_10": "dq_05", "pm_11": "dq_06", "pm_12": "dq_07", "pm_13": "dq_08", 
          "pm_14": "dq_09", "pm_15": "dq_10", "pm_16": "dq_11", "pm_17": "dq_12", 
          "am_04": "dq_01", "am_05": "dq_02", "am_06": "dq_03", "am_07": "dq_04", 
          "am_08": "dq_05", "am_09": "dq_06", "am_10": "dq_07", "am_11": "dq_08", 
          "am_12": "dq_09", "am_13": "dq_10", "am_14": "dq_11", "am_15": "dq_12"}

df['id'] = df['id'].map(id_map).fillna(df['id'])

# Separate the dataframe into two
string_q = ['dq_13', 'pm_01', 'pm_02', 'pm_03']
df_strings = df[df['id'].isin(string_q)]
df = df[~df['id'].isin(string_q)]

# Convert answer to numbers
df["answer"] = pd.to_numeric(df["answer"], errors='coerce')

# the nans of the pm_05 to 1 because they come from a string saying how many hours the subject has exercised
df.loc[(df['id'] == 'pm_05') & (df['answer'].isna()), 'answer'] = 1

# Fix the date index and change the date to 'YYYY-MM-DD HH:MM' format
df.reset_index(inplace=True)
df['date'] = df['date'].apply(lambda x: x.replace(tzinfo=None))
df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M')

df.set_index('date', inplace=True)

# Define id lists
pa_ids = ['dq_01', 'dq_02', 'dq_03', 'dq_04', 'dq_05']
na_ids = ['dq_06', 'dq_07', 'dq_08', 'dq_09', 'dq_10']
sleep_ids = ['am_01', 'am_02', 'am_03']
pain_id = ['dq_12']
stress_id = ['dq_11']
menstruation_id = ['pm_18']
substance_id = ['pm_04']
exercise_id = ['pm_05']

# Reverse the am_02 score so that when we compute the sleep index, it is maximum when there were no nightmares
df.loc[df['id'] == 'am_02', 'answer'] = 1 - df.loc[df['id'] == 'am_02', 'answer']

#make some new dataframes for storing the information 
affect, sleep, night = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Compute scores per time asked
affect['pa'] = df.loc[df['id'].isin(pa_ids), 'answer'].groupby('date').sum()
affect['na'] = df.loc[df['id'].isin(na_ids), 'answer'].groupby('date').sum()
affect['stress'] = df.loc[df['id'].isin(stress_id), 'answer'].groupby('date').sum()
affect['pain'] = df.loc[df['id'].isin(pain_id), 'answer'].groupby('date').sum()
affect.dropna(inplace=True) #drop if there are nans because it means the survey was not completed in its entirety

sleep['sleep'] = df.loc[df['id'].isin(sleep_ids), 'answer'].groupby('date').sum()

night['menstruation'] = df.loc[df['id'].isin(menstruation_id), 'answer'].groupby('date').sum()
night['substance'] = df.loc[df['id'].isin(substance_id), 'answer'].groupby('date').sum()
night['exercise'] = df.loc[df['id'].isin(exercise_id), 'answer'].groupby('date').sum()

# Convert all date index to YYYY-MM-DD format
affect.index = pd.to_datetime(affect.index)
affect.index = affect.index.strftime('%Y-%m-%d')
sleep.index = pd.to_datetime(sleep.index)
sleep.index = sleep.index.strftime('%Y-%m-%d')
night.index = pd.to_datetime(night.index)
night.index = night.index.strftime('%Y-%m-%d')

# Compute the scores for the PA and NA
aggregations = {'pa': ['mean', 'median', 'min', 'max', 'std'],
                'na': ['mean', 'median', 'min', 'max', 'std'],
                'stress': ['mean', 'median', 'min', 'max', 'std'],
                'pain': ['mean', 'median', 'min', 'max', 'std']}

df_agg = affect.groupby('date').agg(aggregations)
df_agg.columns = ['_'.join(col) for col in df_agg.columns]

#now merge with the other dataframes
df = pd.merge(df_agg, night, on='date', how='outer')
df = pd.merge(df, sleep, on='date', how='outer')

# and fill the nans
df = df.fillna(df.mean())

# Now on to the string part. First, let's convert the time into the YYYY-MM-DD format
df_strings.reset_index(inplace=True)
df_strings['date'] = df_strings['date'].apply(lambda x: x.replace(tzinfo=None))
df_strings['date'] = df_strings['date'].dt.strftime('%Y-%m-%d')

# Let's move to the alcohol and coffee
df_pm = df_strings[df_strings['id'].isin(['pm_02', 'pm_03'])].copy()
df_pm['answer'] = df_pm['answer'].apply(lambda x: min(map(int, x.split('-'))) if '-' in str(x) else pd.to_numeric(x, errors='coerce'))

df_pm = df_pm.pivot(index='date', columns='id', values='answer')
df_pm = df_pm.rename(columns={'pm_02': 'alcohol', 'pm_03': 'coffee-tea'})

# let's separate the weight
categories = {
    'Yes. Written text': 1,
    'Yes. In person': 2,
    'Yes. Video meeting': 3,
    'Yes. Written text, Yes. In person': 4,
    'Yes. Written text, Yes. Video meeting': 5,
    'Yes. In person, Yes. Video meeting': 6,
    'Yes. Written text, Yes. In person, Yes. Video meeting': 7,
    'Yes. Written text, Yes. Video meeting, Yes. In person': 7,
    'Yes. Video meeting, Yes. In person, Yes. Written text': 7,
    'No.': 0
}

df_social = df_strings[df_strings['id'] == 'pm_01'].copy()
df_social['answer'] = df_social['answer'].map(categories)
df_social = df_social.pivot(index='date', columns='id', values='answer')
df_social = df_social.rename(columns={'pm_01': 'social'})

# now let's fix the weight and other string
df_text = df_strings[df_strings['id']=='dq_13']
df_weight = df_text[df_text['answer'].str.contains('kg')]
df_weight['weight'] = df_weight['answer'].apply(lambda x: float(x.split('kg')[0]))
df_weight.set_index('date', inplace=True)
df_weight = df_weight['weight']

# and finally the strings
df_string = df_text[~df_text['answer'].str.contains('kg')]
df_string = df_string.groupby(['date'])['answer'].apply(', '.join)

#merge all dataframes
df = pd.merge(df, df_pm, on='date', how='outer')
df = pd.merge(df, df_social, on='date', how='outer')
df = pd.merge(df, df_weight, on='date', how='outer')
df = pd.merge(df, df_string, on='date', how='outer')

# and save
df.to_csv(f'{savepath}/sub-01_day-all_device-smartphone_sensor-EMA_.csv')