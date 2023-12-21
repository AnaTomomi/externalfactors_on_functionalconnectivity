"""
This script checks for completeness of data. It requires all datasources and 
plots a heatmap where the % of completeness in each data source is shown. It 
also visualizes every Sunday, easing visual inspection. 

Input: path where all the preprocessed data is
Output: path where the figure will be saved

@author: trianaa1
"""

import sys
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib
import seaborn as sns

import matplotlib.dates as mdates


path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'#sys.argv[1]
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results' #sys.argv[2]
begin = '2023-01-01'
end = '2023-05-13'

def mask_data(df,col):
    df = df[col].notna().astype(int).to_frame()
    df[col] = df[col]*100
    df.rename(columns={col:"data"}, inplace=True)
    return df

#cognitive
pvt = pd.read_csv(f'{path}/cognitive/sub-01_day-all_device-presentation_test-pvt.csv', index_col=0)
nback = pd.read_csv(f'{path}/cognitive/sub-01_day-all_device-presentation_test-nback.csv', index_col=0)

pvt = mask_data(pvt,'mean_1_RT')
pvt.rename(columns={'data':'PVT'}, inplace=True)
nback = mask_data(nback,'median_RT_1')
nback.rename(columns={'data':'n-back'}, inplace=True)

#behavioral 
ring = pd.read_csv(f'{path}/behavioral/sub-01_day-all_device-oura.csv', index_col=0)
sleep = mask_data(ring,'total_sleep_duration')
sleep.rename(columns={'data':'sleep'}, inplace=True)
activity = mask_data(ring, 'Steps')
activity.rename(columns={'data':'activity'}, inplace=True)

ema = pd.read_csv(f'{path}/behavioral/sub-01_day-all_device-smartphone_sensor-ema_quality.csv',index_col=0)
ema = ema*100
bat = pd.read_csv(f'{path}/behavioral/sub-01_day-all_device-smartphone_sensor-battery_quality.csv',index_col=0)
bat = bat*100
bat.rename(columns={'battery_level':'smartphone'}, inplace=True)
loc = pd.read_csv(f'{path}/behavioral/sub-01_day-all_device-smartphone_sensor-all.csv')
loc['date'] = pd.to_datetime(loc['date'], utc=True).dt.tz_convert('Europe/Helsinki')
loc['date'] = loc['date'].dt.date
loc.set_index('date', inplace=True)
loc = mask_data(loc,'dist_total')
loc.rename(columns={'data':'GPS-based location'}, inplace=True)
loc.index = pd.to_datetime(loc.index)
loc.index = loc.index.strftime('%d-%m-%Y')

emp = pd.read_csv(f'{path}/behavioral/sub-01_day-all_device-embraceplus_quality.csv', index_col=0)
emp = emp[['pulse rate', 'pulse rate variability', 'breathing rate']]
emp = 100-emp
emp.rename(columns={'pulse rate':'heart rate', 'pulse rate variability':'heart rate variability'}, inplace=True)

#questionnaires
q = pd.read_excel(f'{path}/questionnaires/sub-01_day-all_device-questionnaire_score-initial.xlsx', sheet_name="pss")
q['date'] = pd.to_datetime(q['Unnamed: 0'], dayfirst=True, utc=True).dt.tz_convert('Europe/Helsinki')
q.set_index('date', inplace=True)
q.index = q.index.strftime('%d-%m-%Y')
q.drop(columns={'Unnamed: 0'}, inplace=True)
q = mask_data(q,0)
q.rename(columns={'data':'questionnaires'}, inplace=True)
q.replace(0, np.nan, inplace=True)

post_scan = pd.read_csv(f'{path}/questionnaires/sub-01_day-all_device-questionnaire_score-postscanner.csv', index_col=0)
post_scan = mask_data(post_scan,'pvt_engagement')
post_scan.replace(0, np.nan, inplace=True)

#fmri
eye = pd.read_csv(f'{path}/mri/sub-01_day-all_device-eyetracker.csv', index_col=0)
max_no = len(list(eye.columns))
eye['data'] = eye.notna().astype(int).sum(axis=1)
eye = ((eye['data']/max_no)*100).to_frame()

mri = pd.read_csv(f'{path}/mri/sub-01_day-all_device-mri.csv', index_col=0)
mri['date'] = pd.to_datetime(mri['date'], dayfirst=True).dt.strftime('%d-%m-%Y')
mri['fmriprep'] = np.where(mri['fmriprep'] == 'ok', 100, 0)
mri['biopac'] = np.where(mri['biopac'] == 'ok', 100, 75) #we know that only one biopac failed
mri = mri[['date', 'fmriprep', 'biopac']]

#Start merging for plotting
mri = mri.merge(eye, left_on='subject', right_on='subject')
mri.rename(columns={"data":"eye tracker"}, inplace=True)
mri = mri.merge(post_scan, left_on='subject', right_on='subject')
mri.rename(columns={"data":"post-scanner questions"}, inplace=True)
mri = mri.reset_index().set_index('date')
mri.drop(columns={'subject'},inplace=True)

data_frames = [pvt, nback, sleep, activity, ema, bat, loc, emp, q, mri]
df = pd.concat(data_frames, axis=1)
df.index = pd.to_datetime(df.index, dayfirst=True)
dates = pd.date_range(begin, end)
df = df[df.index.isin(dates)]

#plot the quality
cmap = plt.cm.YlGnBu
colors = np.linspace(0, 1, 10)
ten_colors = [cmap(color) for color in colors]
cmap_10 = mcolors.ListedColormap(ten_colors)

fig, ax = plt.subplots(figsize=(15,10))
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
sns.heatmap(df.T, cmap=cmap_10, ax=ax, linewidths=0, linecolor=None)

sundays = df[df.index.weekday == 6].index
for sunday in sundays:
    plt.axvline(df.index.get_loc(sunday), color='red', linestyle='--')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
plt.xticks(rotation=90) 
ax.tick_params(axis='both', which='major', labelsize=14)
ax.set_xlabel('time', fontsize=14)
ax.set_ylabel('data source', fontsize=14)

cbar = ax.collections[0].colorbar
cbar.set_label("% of collected data", rotation=90, labelpad=15, fontsize=14)
plt.tight_layout()
plt.savefig(f'{savepath}/quality_all.pdf')