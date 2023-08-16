"""
This script checks for data missing patterns in the preprocessed cognitive data, 
i.e. PVT and n-back scores


Input: path where all the preprocessed data is
Output: path where the figure will be saved

@author: trianaa1
"""

import sys
sys.path.insert(0, "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/quality_check")

import pandas as pd

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

#PVT 
data = pd.read_csv(f'{path}/sub-01_day-all_device-presentation_test-pvt.csv')
data.rename(columns={"mean":"mean RT (ms)"}, inplace=True)
data.set_index(pd.to_datetime(data["date"], dayfirst=True, infer_datetime_format=True), inplace=True)
data = data.loc[begin:end]
data.sort_index(inplace=True)

df1 = data["mean RT (ms)"].to_frame()

#N-back
data = pd.read_csv(f'{path}/sub-01_day-all_device-presentation_test-nback.csv')
data.rename(columns={"mean_RT_1":"mean RT (ms)"}, inplace=True)
data.set_index(pd.to_datetime(data["date"], dayfirst=True, infer_datetime_format=True), inplace=True)
data = data.loc[begin:end]

df2 = data["mean RT (ms)"].to_frame()

dfs = [df1, df2]
label = ['A.', 'B.']

#two graphs
fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8,4))
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
    axes[i].set_ylabel(df.columns[0])
    axes[i].set_title(f'missing data={percent}%', loc="right", fontsize=12)
    qu.highlight_datetimes(df, indices, axes[i])
axes[0].set_xlim(min(dates_d), max(dates_d))
axes[0].xaxis.set_major_formatter(form)
axes[1].set_xlabel('dates (DD-MM)')
fig.align_ylabels(axes)
fig.tight_layout()
plt.show()
plt.savefig(f'{savepath}/quality_cognitive.pdf')

##############################################################################