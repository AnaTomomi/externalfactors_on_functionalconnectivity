import pandas as pd
import os


datapath = "/u/68/trianaa1/unix/trianaa1/protocol/data/pilot_i/nback/s1/"
os.chdir(datapath)

def get_dual_data(stim2back):
    count=1
    for key in stim2back["DD1"]:
        print(key)
        stat = stim2back["DD1"][key].groupby([" change_correct "]).size().to_frame().T
        if count==1:
            stats = stat
        else:
            stats = pd.concat([stats,stat])
        count = count+1
    stats = stats.rename(columns={"0": "wrong", "1": "correct", "5":"missing"})
    stats = stats.reset_index()
    stats = stats.drop(columns=["index"])
    stats["days"] = range(1,len(stats)+1)
    return stats

twoback = []
for file in os.listdir(datapath):
    if file.endswith("_2back_OnlyNovels_fMRI_rawdata.txt"):
        twoback.append(file)
twoback.sort()

oneback = []
for file in os.listdir(datapath):
    if file.endswith("_OnlyNovels_fMRI_rawdata.txt"):
        if not file.endswith("_2back_OnlyNovels_fMRI_rawdata.txt"):
            oneback.append(file)
oneback.sort()

#Organize the data in dictionaries
table_names = ["DD1"]
days2back = dict()
for file in twoback:
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    groups = content[1].isin(table_names).cumsum()
    tables = dict()
    for k,g in content.groupby(groups):
        df = g.iloc[1:]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        tables[g.iloc[0,1]] = df
    days2back[int(file[-36:-34])] = tables
    print(file)

days1back = dict()
for file in oneback:
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    groups = content[1].isin(table_names).cumsum()
    tables = dict()
    for k,g in content.groupby(groups):
        df = g.iloc[1:]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        tables[g.iloc[0,1]] = df
    days1back[int(file[-30:-28])] = tables
    print(file)
    
#Flip the info to store per stimuli
stim2back = dict()
for name in table_names:
    stim2back[name] = dict()
    for key in days2back:
        stim2back[name][key] = days2back[key][name]
        print(key, name)

stim1back = dict()
for name in table_names:
    stim1back[name] = dict()
    for key in days1back:
        stim1back[name][key] = days1back[key][name]
        print(key, name) 
