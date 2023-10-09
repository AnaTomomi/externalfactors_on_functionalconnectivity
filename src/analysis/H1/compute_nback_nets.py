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
conn = list2mat(net)

conn_file = f'{conn_path}/{strategy}/reg-adj_{strategy}_{atlas_name}.mat'
savemat(conn_file, {'conn':conn})