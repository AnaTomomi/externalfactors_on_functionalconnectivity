"""Compute the aggregated scores for calls, battery, SMS, screen, and GPS.
    
    The input should be done in the following order:

    Parameters
    ----------
    file : str
        path where the smartphone answers files are stored
    savepath : str
        path where the processed data will be stored
    """

import os, sys
import pandas as pd
sys.path.insert(0, '/m/cs/scratch/networks/trianaa1/Paper3/niimpy/')

import warnings
warnings.filterwarnings("ignore")

import niimpy
import niimpy.preprocessing.communication as com
import niimpy.preprocessing.screen as sc
import niimpy.preprocessing.battery as bat
import niimpy.preprocessing.location as l


path = sys.argv[1]
savepath = sys.argv[2]

def get_location_resampled(df, rule):
    loc_feat = []
    for user in df['user'].unique():
        print(f'computing {user}')
        df2 = df.loc[df['user'] == user]
        df3 = df2.resample(rule)
        inds = df3.indices
        loc = {}
        columns = ['n_sps', 'n_static', 'n_moving', 'n_rare', 'n_home', 'max_dist_home', 'n_transitions',
                   'n_top1', 'n_top2', 'n_top3', 'n_top4', 'n_top5', 'entropy', 'normalized_entropy',
                   'dist_total', 'n_bins', 'speed_average', 'speed_variance', 'speed_max', 'variance',
                   'log_variance']
        for i, key in enumerate(inds.keys()):
            print(key)
            partial_df = df2.iloc[inds[key][0]:inds[key][-1],:]
            if not partial_df.empty and len(partial_df)>15:
                partial_res = l.extract_features_location(partial_df)
                columns = list(partial_res.columns)
                partial_res = partial_res.values.tolist()
                loc[key] = partial_res[0]
        loc_user = pd.DataFrame.from_dict(loc, orient='index', columns=columns)
        loc_user['user'] = user
        loc_user.reset_index(inplace=True)
        loc_user.set_index(['user', 'index'], inplace=True)
        loc_feat.append(loc_user)
    loc_people = pd.concat(loc_feat)
    return loc_people

all_files = os.listdir(path)
files = [f for f in all_files if 'device-smartphone' in f]
files = [f for f in files if 'ESM' not in f]

rule = "1D" #aggregate data per day

#Let's define the features we want to preprocess. This is based on the documentation
# of the niimpy module
call_features = {com.call_duration_total:{"resample_args":{"rule":rule}},
                     com.call_duration_mean:{"resample_args":{"rule":rule}},
                     com.call_duration_median:{"resample_args":{"rule":rule}},
                     com.call_duration_std:{"resample_args":{"rule":rule}},
                     com.call_count:{"resample_args":{"rule":rule}},
                     com.call_outgoing_incoming_ratio:{"resample_args":{"rule":rule}}}

screen_features = {sc.screen_count:{"resample_args":{"rule":rule}},
                     sc.screen_duration:{"resample_args":{"rule":rule}},
                     sc.screen_duration_min:{"resample_args":{"rule":rule}},
                     sc.screen_duration_max:{"resample_args":{"rule":rule}},
                     sc.screen_duration_median:{"resample_args":{"rule":rule}},
                     sc.screen_duration_mean:{"resample_args":{"rule":rule}},
                     sc.screen_duration_std:{"resample_args":{"rule":rule}}}

battery_features = {bat.battery_mean_level:{"resample_args":{"rule":rule}},
                     bat.battery_median_level:{"resample_args":{"rule":rule}},
                     bat.battery_std_level:{"resample_args":{"rule":rule}},
                     bat.battery_shutdown_time:{"resample_args":{"rule":rule}},
                     bat.battery_discharge:{"resample_args":{"rule":rule}}}

#Now let's compute the calls, screen, and battery info
for file in files:
    df = pd.read_csv(f'{path}/{file}', index_col=0)
    df['user'] = 'sub-01'
    df.index = pd.to_datetime(df.index, utc=True)
    df.index = df.index.tz_convert('Europe/Helsinki')
    if "Messages" in file and not df.empty:
        sms = com.sms_count(df, {"resample_args":{"rule":"1D"}})
        sms.reset_index(level='user', inplace=True)
        sms.drop(columns=['user'], inplace=True)
    elif "Calls" in file and not df.empty:
        call = com.extract_features_comms(df, features=call_features)
    elif "Battery" in file and not df.empty:
        df['device'] = 'smart'
        df['datetime'] = df.index
        battery = bat.extract_features_battery(df, battery_features)
        battery.reset_index(level='user', inplace=True)
        battery.drop(columns=['user'], inplace=True)
    elif "Screen" in file and not df.empty:
        bat = pd.read_csv(f'{path}/sub-01_day-all_device-smartphone_sensor-AwareBattery.csv', index_col=0)
        bat['user'] = 'sub-01'
        bat.index = pd.to_datetime(bat.index, utc=True)
        bat.index = bat.index.tz_convert('Europe/Helsinki')
        bat['device'] = 'smart'
        bat['datetime'] = bat.index
        df['device'] = 'smart'
        df['datetime'] = df.index
        screen = sc.extract_features_screen(df, bat, features=screen_features)
        screen.reset_index(level='user', inplace=True)
        screen.drop(columns=['user'], inplace=True)
    elif "Location" in file:
        loc_filter = l.filter_location(df,remove_disabled=False, remove_network=False, remove_zeros=True)
        loc_binned = niimpy.util.aggregate(loc_filter, freq='10T', method_numerical='median')
        loc_binned = loc_binned.reset_index(0).dropna()
        loc = get_location_resampled(loc_binned, '1D')
        loc.reset_index(level='user', inplace=True)
        loc.drop(columns=['user'], inplace=True)
    else:
        pass

df = pd.merge(sms, battery, on='date', how='outer')
df = pd.merge(df, screen, on='date', how='outer')

loc.reset_index(inplace=True)
loc.rename({'index': 'date'}, axis=1, inplace=True)
loc.set_index('date', inplace=True)
df = pd.merge(df, loc, on='date', how='outer')

df.sort_index(inplace=True)

df.to_csv(f'{savepath}/sub-01_day-all_device-smartphone_sensor-all.csv')