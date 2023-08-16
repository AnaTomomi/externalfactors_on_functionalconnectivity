"""
This script checks for data missing patterns in the aggregated behavioral data, 
i.e. smartring, smartwatch, and smartphone


Input: path where all the preprocessed data is
Output: path where the figure will be saved

@author: trianaa1
"""


import sys
sys.path.insert(0, "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/quality_check")

import pandas as pd
import pytz

import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.transforms as mtransforms
import matplotlib

import quality_utils as qu

######################### Pepare paths #######################################

path = sys.argv[1]
savepath = sys.argv[2]
begin = '2023-01-01' 
end = '2023-05-13' 

#Smartring 
data = pd.read_csv(f'{path}/sub-01_day-all_device-oura.csv')
data.rename(columns={"Total Sleep Duration":"sleep \nduration", "Steps":"steps"}, inplace=True)
data.set_index(pd.to_datetime(data["date"], dayfirst=True), inplace=True)
data = data.loc[begin:end]
data.sort_index(inplace=True)

#smartring sleep
df1 = data["sleep \nduration"].to_frame()
df1 = df1/3600 #to hours

#smartring activity
df2 = data["steps"].to_frame()
df2 = df2/1000 #in k-steps

#smartphone ESM
df3 = pd.read_csv(f'{path}/sub-01_day-all_device-smartphone_sensor-ema.csv')
df3.set_index(pd.to_datetime(df3["date"], yearfirst=True), inplace=True)
df3 = df3["pa_mean"].to_frame()
df3 = df3.loc[begin:end]
df3.rename(columns={"pa_mean":"positive \naffect"}, inplace=True)

#empatica 
data = pd.read_csv(f'{path}/sub-01_day-all_device-embraceplus.csv')
data.rename(columns={"timestamp_iso":"date", "mean_pulse_rate_bpm":"pulse \nrate (bpm)",
                    "mean_respiratory_rate_brpm":"respiration \nrate (bpm)"}, inplace=True)
data.set_index(pd.to_datetime(data["date"]), inplace=True)
data = data.loc[begin:end]

# empatica HR
df4 = data["pulse \nrate (bpm)"].to_frame()

#empatica BR
df5 = data["respiration \nrate (bpm)"].to_frame()

#smartphone others
data = pd.read_csv(f'{path}/sub-01_day-all_device-smartphone_sensor-all.csv')
data.rename(columns={"battery_mean_level":"battery \nlevel (%)",
                    "dist_total":"GPS-based \ndistance (km)"}, inplace=True)
data.set_index(pd.to_datetime(data["date"]), inplace=True)
data = data.loc[pd.to_datetime(begin).tz_localize('Europe/Helsinki'):pd.to_datetime(end).tz_localize('Europe/Helsinki')]

#smartphone battery
df6 = data["battery \nlevel (%)"].to_frame()

#smartphone GPS
df7 = data["GPS-based \ndistance (km)"].to_frame()
df7 = df7/1000 #to km

dfs = [df1, df2, df3, df4, df5, df6, df7]
label = ['A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.']

#two graphs
fig, axes = plt.subplots(nrows=7, ncols=1, sharex=True, figsize=(9,9))
form = md.DateFormatter("%d-%m")
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
dates_d = df1.index

for i, df in enumerate(dfs): 
    indices = qu.find_missing(df)
    percent = qu.find_missing_percent(df)
    trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
    axes[i].text(0.0, 1.0, label[i], transform=axes[i].transAxes + trans, va='bottom')
    for v in df.columns.tolist():
        axes[i].plot(df[v], label=v, color='black', linewidth=2)
    axes[i].set_ylabel(df.columns[0].lower())
    axes[i].set_title(f'missing data={percent}%', loc="right", fontsize=12)
    qu.highlight_datetimes(df, indices, axes[i])
axes[0].set_xlim(min(dates_d), max(dates_d))
axes[0].xaxis.set_major_formatter(form)
axes[6].set_xlabel('dates (DD-MM)')
fig.align_ylabels(axes)
fig.tight_layout()
#plt.show()
plt.savefig(f'{savepath}/quality_behavioral.pdf')

##############################################################################