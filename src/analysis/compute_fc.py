import glob, os
import pandas as pd
import numpy as np

from scipy.io import savemat

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/roi-ts'
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/adjacency_mat'


#Read/Make the time series
files = glob.glob(path + "/**/*.csv", recursive=True)


for file in files:
    head, tail = os.path.split(file)
    outfile = f'{savepath}/{tail[:-4]}.mat'
        
    if os.path.exists(outfile):
        print(f'Node time series file for {file} already exists!')
    else:
        print(f'Creating node time series for {file} in {outfile}')
        sub_data = pd.read_csv(file, header=None)
        con = sub_data.corr(method='pearson') #compute the FC matrices
        con = con.to_numpy()
        idx = np.tril_indices(len(con),0)
        con[idx] = 0
        conn = {'fc':con}
        savemat(outfile,conn)