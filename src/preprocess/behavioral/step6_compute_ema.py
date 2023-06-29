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

file = "/m/cs/project/networks-pm/behavioral/sub-01_day-all_device-smartphone_sensor-ema.csv"
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
df["answer"] = pd.to_numeric(df["answer"])

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

# Reverse the am_02 score
df.loc[df['id'] == 'am_02', 'answer'] = 1 - df.loc[df['id'] == 'am_02', 'answer']

# Compute scores per time asked
df['pa'] = df.loc[df['id'].isin(pa_ids), 'answer'].groupby('date').sum()
df['na'] = df.loc[df['id'].isin(na_ids), 'answer'].groupby('date').sum()
df['sleep'] = df.loc[df['id'].isin(sleep_ids), 'answer'].groupby('date').sum()
df['pain'] = df.loc[df['id'].isin(pain_id), 'answer'].groupby('date').sum()
df['stress'] = df.loc[df['id'].isin(stress_id), 'answer'].groupby('date').sum()
df['menstruation'] = df.loc[df['id'].isin(menstruation_id), 'answer'].groupby('date').sum()
df['substance'] = df.loc[df['id'].isin(substance_id), 'answer'].groupby('date').sum()
df['exercise'] = df.loc[df['id'].isin(exercise_id), 'answer'].groupby('date').sum()

# Compute the values per day 
df.index = pd.to_datetime(df.index)
df.index = df.index.strftime('%Y-%m-%d')

selected_ids = ["am_01", "dq_01", "pm_04", "pm_18", "pm_05"]
df = df[df['id'].isin(selected_ids)]
df.drop(columns=['answer', 'title'],inplace=True)

scores = df.groupby([df.index, "id"]).median()
scores.reset_index(inplace=True)
scores = scores[scores["id"]=='dq_01']
scores.set_index("date", inplace=True)
scores.drop(columns=["id"], inplace=True)

# Fill in the gaps with the mean, according to the registered report
scores.fillna(round(scores.mean()), inplace=True)

# Now on to the string-based replies
