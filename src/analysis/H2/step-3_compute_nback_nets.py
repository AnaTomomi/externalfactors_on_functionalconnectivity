'''Since the n-back has 1 and 2-back events and the beta series are computed on 
the events type, then we have one network for 1-back and another for 2-back. 
Following the GLM contrasts, the final networks are obtained from substracting 
the 1-back adjecency matrix from the 2-back adjacency matrix. This script 
computes this substraction. 

@author: trianaa1
'''

import sys
import pandas as pd
from scipy.io import savemat, loadmat

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import list2mat

###############################################################################
# Input variables: modify these accordingly
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/nback'
strategy = '24HMP-8Phys-4GSR-Spike_HPF'
atlas_name = 'seitzman-set1'
###############################################################################

oneback = loadmat(f'{conn_path}/{strategy}/reg-adj_oneback_{strategy}_{atlas_name}.mat')['conn'][0]
oneback = [pd.DataFrame(ts) for ts in oneback]

twoback = loadmat(f'{conn_path}/{strategy}/reg-adj_twoback_{strategy}_{atlas_name}.mat')['conn'][0]
twoback = [pd.DataFrame(ts) for ts in twoback]

net=[]
for ob, tb in zip(oneback, twoback):
    net.append(tb - ob)
net = [network.to_numpy() for network in net]
conn = list2mat(net)

conn_file = f'{conn_path}/{strategy}/reg-adj_{strategy}_{atlas_name}.mat'
savemat(conn_file, {'conn':conn})