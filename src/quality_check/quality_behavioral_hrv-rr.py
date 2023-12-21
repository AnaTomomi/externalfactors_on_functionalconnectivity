"""Visualizes the time of the day when the HRV and RR are mostly missing 

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
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
import matplotlib
import matplotlib.transforms as mtransforms

from matplotlib.colors import ListedColormap

path = '/m/cs/project/networks-pm/behavioral' #sys.argv[1]
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results' #sys.argv[2]

files = []
pattern   = '*device-embraceplus.csv'

for dir,_,_ in os.walk(path):
    files.extend(glob(os.path.join(dir,pattern))) 
print(f'checking data quality for {str(len(files))} files..................')

all_data = pd.DataFrame()

# Loop over the file list and concatenate each file's data into the all_data DataFrame
for file_path in files:
    df = pd.read_csv(file_path, parse_dates=['timestamp_iso'])
    all_data = pd.concat([all_data, df])

# Add a 'day' column and a 'time' column to the DataFrame
all_data['day'] = all_data['timestamp_iso'].dt.date
all_data['time'] = all_data['timestamp_iso'].dt.hour * 60 + all_data['timestamp_iso'].dt.minute

def plot_heatmap(data, column, ax):
    heatmap_data = data.pivot_table(index='day', columns='time', values=column,
                                    aggfunc=lambda x: 1 if pd.isna(x).any() else 0, fill_value=0)
    sns.heatmap(heatmap_data, cmap=ListedColormap(['black', 'white']), cbar=False, ax=ax)
    ax.set_xlabel('time (hours since midnight)')
    ax.set_ylabel('day')

fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
labels = ['A.', 'B.', 'C.']

plot_heatmap(all_data, 'prv_rmssd_ms', axs[1])
plot_heatmap(all_data, 'respiratory_rate_brpm', axs[2])
plot_heatmap(all_data, 'pulse_rate_bpm', axs[0])

xticks = [60 * hour for hour in range(24)]  # Every 60 minutes from 0 to 23 hours
xticklabels = [str(hour) for hour in range(24)]  # Labels from '0' to '23'

# Apply the defined x-ticks and labels to all subplots
for ax, label in zip(axs, labels):
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.axvline(x=480, color='blue', linestyle='--', lw=2)  # 08:00 AM line
    ax.axvline(x=1320, color='blue', linestyle='--', lw=2)  # 10:00 PM line
    ax.set_yticks([])  
    trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
    ax.text(0.0, 1.0, label, transform=ax.transAxes + trans, va='bottom')

plt.tight_layout()
plt.show()

plt.savefig(f'{savepath}/quality-hr_rr.pdf')