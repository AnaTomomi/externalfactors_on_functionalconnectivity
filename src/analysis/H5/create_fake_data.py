"""
This script generates the surrogate data for H5, H6, and H7. It already organizes
the data in lags.

author: @trianaa1
"""
import sys
import numpy as np
import pandas as pd
import pickle
from scipy.stats import zscore

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import get_behav_data, get_behav_data_15days

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
behav = get_behav_data(f'{path}/behavioral')

#z-score the data
standardized_data = zscore(behav)

# Seed for reproducibility
np.random.seed(0)

all_surrogate_behavs = []
for iteration in range(10000):
    surrogate_behav = pd.DataFrame()

    for col in behav.columns:
        # Step 1: Fourier Transform
        f_transform = np.fft.fft(standardized_data[col])
        amplitudes = np.abs(f_transform)
        phases = np.angle(f_transform)
        
        # Step 2: Phase Shuffling
        np.random.shuffle(phases[1:])  
        
        # Constructing surrogate Fourier spectrum
        surrogate_transform = amplitudes * np.exp(1j * phases)
        
        # Step 3: Inverse Fourier Transform
        surrogate_data = np.fft.ifft(surrogate_transform).real  
        
        # Assign surrogate_data to a column in surrogate_behav
        surrogate_behav[col] = surrogate_data
    
    surrogate_behav['date'] = behav.index
    surrogate_behav.set_index('date', inplace=True)
    lagged_df = get_behav_data_15days(f'{path}/behavioral', days=16, behav=surrogate_behav)
    all_surrogate_behavs.append(lagged_df)

with open(f'{path}/behavioral/surrogate_behav_data.pkl', 'wb') as file:
    pickle.dump(all_surrogate_behavs, file)