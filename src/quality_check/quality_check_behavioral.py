import sys
sys.path.insert(0, "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/quality_check")

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.transforms as mtransforms
import matplotlib

import quality_utils as qu

######################### Pepare paths #######################################

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral'
begin = '2023-01-01' 
end = '2023-05-13' 

#Smartring sleep
data = pd.read_csv(f'{path}/sub-01_day-all_device-oura.csv')
dates_d = pd.to_datetime(data["date"], infer_datetime_format=True)
data.columns = data.columns.str.replace('_',' ')
df1 = data["Total Sleep Duration"].to_frame()
df1.index = dates_d
df1 = df1.loc[begin:end]
df1.rename(columns={"Total Sleep Duration":" sleep duration"}, inplace=True)
df1.sort_index(inplace=True)

#smartring activity
df2 = data["Steps"].to_frame()
df2.index = dates_d
df2 = df2.loc[begin:end]
df2.rename(columns={"Steps":" steps"}, inplace=True)
df2.sort_index(inplace=True)

#smartphone ESM
df3 = pd.read_csv(f'{path}/sub-01_day-all_device-smartphone_sensor-ema.csv')
df3.set_index(pd.to_datetime(df3["date"], infer_datetime_format=True), inplace=True)
df3 = df3["pa_mean"].to_frame()
df3 = df3.loc[begin:end]
df3.rename(columns={"pa_mean":"positive affect"}, inplace=True)

#empatica HR
data = pd.read_csv(f'{path}/sub-01_day-all_device-embraceplus.csv')
data.rename(columns={"timestamp_iso":"date", "mean_pulse_rate_bpm":"pulse rate (bpm)",
                    "mean_respiratory_rate_brpm":"respiration rate (bpm)"}, inplace=True)
data.set_index(pd.to_datetime(data["date"], infer_datetime_format=True), inplace=True)
df4 = data["pulse rate (bpm)"].to_frame()
df4 = df4.loc[begin:end]

#empatica BR
df5 = data["respiration rate (bpm)"].to_frame()
df5 = df5.loc[begin:end]

#Hourly binned
df4 = prepare_data(f'{path}/sub-01_sensor-battery.csv', begin, end, column='battery_level')
df4.rename(columns={"battery_level":" battery \n level"}, inplace=True)
df5 = prepare_data(f'{path}/sub-01_sensor-light.csv', begin, end, column='double_light_lux')
df5.rename(columns={"double_light_lux":" light \n intensity"}, inplace=True)
df6 = prepare_data(f'{path}/sub-01_sensor-wifi.csv', begin, end, column='rssi')
df6.rename(columns={"rssi":" wifi signal \n intensity"}, inplace=True)
df7 = prepare_data(f'{path}/sub-01_sensor-location.csv', begin, end, column='double_latitude')
df7[df7>0] = 1
df7.rename(columns={"double_latitude":" location \n data"}, inplace=True)

dfs = [df1, df2, df3, df4, df5, df6, df7]
label = ['A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.']

#two graphs
fig, axes = plt.subplots(nrows=7, ncols=1, sharex=True, figsize=(9,9))
form = md.DateFormatter("%d-%m")
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
dates_d = df1.index

for i, df in enumerate(dfs): 
    indices = find_missing(df)
    percent = find_missing_percent(df)
    trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
    axes[i].text(0.0, 1.0, label[i], transform=axes[i].transAxes + trans, va='bottom')
    for v in df.columns.tolist():
        axes[i].plot(df[v], label=v, color='black', linewidth=2)
    axes[i].set_ylabel(df.columns[0].lower())
    axes[i].set_title(f'missing data={percent}%', loc="right", fontsize=14)
    axes[i].xaxis.grid(b=True, which='major', color='black', linestyle='--', alpha=1) #add xaxis gridlines
    highlight_datetimes(indices, axes[i])
axes[0].set_xlim(min(dates_d), max(dates_d))
axes[0].xaxis.set_major_formatter(form)
axes[6].set_xlabel('dates (DD-MM)')
fig.align_ylabels(axes)
fig.tight_layout()
plt.show()
plt.savefig('/u/68/trianaa1/unix/trianaa1/protocol/results/pilot_iii/sensor_missing.pdf')

##############################################################################