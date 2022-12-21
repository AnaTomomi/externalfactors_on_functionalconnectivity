import os
import datetime as dt
import pandas as pd

path = '/u/68/trianaa1/unix/Downloads/ses1'

def read_empatica(variable, savepath):
    """Preprocess empatica data. Reads all empatica data splitted in sessions, 
    organizes, and saves them in the given savepath

    Parameters
    ----------
    variable : str
        name of the variable to preprocess. It could be heart rate (hr), 
        temperature (temperature), electrodermal activity (electrodermal)
    savepath : str
        path where the preprocessed data will be saved

    Returns
    -------
    data : dataframe
        a dataframe with the organized data by timestamps according to the 
        sampling frequency
    """
    files = []
    for file in os.listdir(path):
        if file.endswith(variable+'.csv'):
            files.append(file)

    df = []
    for file in files:
        data = pd.read_csv(f'{path}/{file}', header=None)
        start_time = data.iloc[0,0]
        sample_rate = 1/data.iloc[1,0]
        data = data.iloc[2:]
    
        start_time = dt.datetime.fromtimestamp(start_time)
        freq=f'{str(int(sample_rate))}S'    
        data["time"] = pd.date_range(start=start_time, periods=len(data),freq=freq)
        data.set_index("time", inplace=True)
        data.rename(columns={0:'data'}, inplace=True)
    
        df.append(data)
    
    data = pd.concat(df)
    data = data.sort_index()
    data.to_csv(savepath)
    return data