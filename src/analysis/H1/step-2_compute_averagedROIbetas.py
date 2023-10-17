"""
This script computes the averaged-ROI beta-series for the task data. It also 
applies the Fisher transform, regresses the mean FD and saves the matrices. 

@author: trianaa1
"""

import glob, os, sys
import numpy as np
import pandas as pd
from scipy.io import savemat, loadmat

from sklearn.linear_model import LinearRegression

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import list2mat, compute_groupmasks, compute_averagedbetas

###############################################################################
# Input variables: modify these accordingly
fmriprep_path = '/m/cs/scratch/networks-pm/pm_preprocessed/'
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/pvt'
task = 'pvt'
contrast = 'OK' #'twoback', 'OK'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'
atlas_name = 'seitzman-set2'
vol_size = [91,109,91]
###############################################################################

# 1. compute the group mask according to the atlas we select
group_atlas = compute_groupmasks(conn_path, fmriprep_path, task, vol_size, atlas_name)

# 2. compute the averaged-ROI timeseries
roi_ts_file = compute_averagedbetas(conn_path, contrast, task, strategy, group_atlas)

# 3. load the files in case 1 and 2 are pre-computed
all_ts = loadmat(roi_ts_file)['rs_ts'][0]
all_ts = [pd.DataFrame(ts) for ts in all_ts]

# 4. Compute the adjacency matrices and apply Fisher transform
con = [ts.corr(method='pearson') for ts in all_ts]
for df in con:
    np.fill_diagonal(df.values,0) #set diagonal values to zero to avoid self-loops
fisher = [np.arctanh(matrix.values) for matrix in con]

# 6. regress mean FD for all links
fd_path = '/'.join(conn_path.rsplit('/', 2)[:-2])
mean_fd = pd.read_csv(f'{fd_path}/sub-01_day-all_device-mri_meas-meanfd.csv')[task]

clf = LinearRegression(fit_intercept=True)
x = np.array(mean_fd).reshape(-1,1)

regressed = [np.zeros_like(matrix) for matrix in fisher]
idx = np.triu_indices(len(fisher[0]),1) #gets two lists of indexes, idx[0] = rows and idx[1] = columns
idx = np.stack((idx[0], idx[1]), axis=1)
for ind in range(len(idx)):
    i = idx[ind,0]
    j = idx[ind,1]
    y = []
    for matrix in fisher:
        y.append(matrix[i][j]) #organize link i-j for the different days (subjects)
    y = np.array(y)
    #Regress the mean FD from the links
    clf.fit(x,y)
    betas = clf.coef_
    regressed_links = y-np.dot(x,betas)-np.ones(len(y))*clf.intercept_
    for sub, link in enumerate(regressed_links):
        regressed[sub][i][j] = link #re-organize links into matrices
                
#Inverse Fisher
inv_fisher = [np.tanh(matrix) for matrix in regressed]
conn = list2mat(inv_fisher)

#Save the connectivity matrices
conn_file = f'{conn_path}/{strategy}/reg-adj_{contrast}_{strategy}_{atlas_name}.mat'
savemat(conn_file, {'conn':conn})