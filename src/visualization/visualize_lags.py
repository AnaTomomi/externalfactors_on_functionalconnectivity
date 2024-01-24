"""
This script summarizes the significant results for global efficiency and participation
coefficients, organizing them and matching the results with the node coordinates for H7

"""
import sys
import numpy as np
from scipy.io import loadmat

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis')
from utils import compute_real_corr

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/visualization')
from visual_utils import format_data

###############################################################################
# Change this!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H6'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data'
atlas_name = 'seitzman-set1'
strategy = '24HMP-8Phys-Spike_HPF'
thres = ['thr-10', 'thr-20', 'thr-30']
alpha = 0.05
lag_no = 16
###############################################################################

#Set the font and colormap properties for all plots
mpl.rc('font', family='Arial', size=14)
colors = ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0',
          '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f']
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
norm = BoundaryNorm([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1], cmap.N)

#Define names and variables according to the hypothesis to plot
hypo = path[-2:]
if hypo=='H7':
    task = 'rs'
    variables = ['total_sleep_duration','awake_time','restless_sleep','pa_mean','pa_std', 
             'na_mean','stress_mean','pain_mean','mean_respiratory_rate_brpm', 
             'min_respiratory_rate_brpm','max_respiratory_rate_brpm','mean_prv_rmssd_ms',
             'min_prv_rmssd_ms','max_prv_rmssd_ms']
    network_mapping = {1: 'default mode',2: 'fronto parietal',3: 'cingulo opercular'}
    ef = ['total sleep duration','awake time','restless sleep','mean positive affect',
      'std positive affect','mean neagtive affect','mean stress level','mean pain level',
      'mean respiratory rate', 'minimum respiratory rate','maximum respiratory rate',
      'mean heart rate variability', 'minimum heart rate variability',
      'maximum heart rate variability']
    labels = ['A', 'B', 'C', 'D', 'E', 'F']  
    t1 = 1.05
    n_net = len(network_mapping)
elif hypo=='H6':
    task = 'nback'
    variables = ['total_sleep_duration','awake_time','restless_sleep','steps', 'inactive_time']
    network_mapping = {1: 'default mode',2: 'fronto parietal',3: 'somatomotor'}
    ef = [var.replace('_', ' ') for var in variables]
    labels = ['A', 'B', 'C', 'D', 'E', 'F']  
    t1 = 1.15
    n_net = len(network_mapping)
elif hypo=='H5':
    task = 'pvt'
    variables = ['total_sleep_duration','awake_time','restless_sleep']
    network_mapping = {1: 'default mode',2: 'fronto parietal', 3:'cingulo opercular', 4:'somatomotor'}
    ef = [var.replace('_', ' ') for var in variables]
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  
    t1 = 1.15
    n_net = len(network_mapping)
else:
    print('No hypothesis found!')
    
#compute the real correlation for the participation coefficientes
for thr in thres:
    print(thr)
    #Compute the correlation values for global efficiency
    pc = loadmat(f'{behav_path}/mri/conn_matrix/{task}/{strategy}/global-eff_{strategy}_{atlas_name}_{thr}')['effs']
    real_corr_values = compute_real_corr(behav_path, variables, pc, lag_no)

    #Select the significant p-values for global efficiency
    data = loadmat(f'{path}/global-eff_{strategy}_{atlas_name}_{thr}_BHcorrected.mat')['data_BH']
    data = format_data(data, variables)
    
    #Start plotting
    X = len(real_corr_values)  # Number of DataFrames in the list
    fig, axes = plt.subplots(X, 2, figsize=(10, 5*X))  # Adjust figsize 
    
    for i, (df_pc, df_data) in enumerate(zip(real_corr_values, data)):
        # Select values from pc[i] where corresponding p-values in data[i] are < 0.05
        annotations = np.where(df_data < 0.05, '*', '')
        
        #plot the correlation values with a * where there is significance     
        sns.heatmap(df_pc, cmap=cmap, norm=norm, annot=annotations, fmt='', 
                    annot_kws={'size': 12, 'color':'k'}, cbar=False, ax=axes[i, 0], square=True)
        
        axes[i, 0].set_ylabel(network_mapping[i+1], fontweight='bold')
        axes[i, 0].set_yticks(np.arange(len(ef)) + 0.5)  # Position ticks at the center of the heatmap cells
        axes[i, 0].set_yticklabels(ef, rotation=0)
        if i < X-1:
            axes[i, 0].set_xticks([])
            axes[i, 0].set_xlabel('')
        else:
            axes[i, 0].set_xlabel('lag')
            axes[i, 0].set_xticklabels(range(1,16,1), rotation=0) 
    
    #Compute the correlation values for participation coefficient
    pc = loadmat(f'{behav_path}/mri/conn_matrix/{task}/{strategy}/parti-coeff_{strategy}_{atlas_name}_{thr}')['pcs']
    real_corr_values = compute_real_corr(behav_path, variables, pc, lag_no)

    #Select the significant p-values for global efficiency
    data = loadmat(f'{path}/parti-coeff_{strategy}_{atlas_name}_{thr}_BHcorrected.mat')['data_BH']
    data = format_data(data, variables)
    
    #Continue plotting    
    for i, (df_pc, df_data) in enumerate(zip(real_corr_values, data)):
        # Select values from pc[i] where corresponding p-values in data[i] are < 0.05
        annotations = np.where(df_data < 0.05, '*', '')
        
        #plot the correlation values with a * where there is significance     
        sns.heatmap(df_pc, cmap=cmap, norm=norm, annot=annotations, fmt='', 
                    annot_kws={'size': 12, 'color':'k'}, cbar=False, ax=axes[i, 1], square=True)
        
        axes[i, 1].set_yticks([])
        if i < X-1:
            axes[i, 1].set_xticks([])
            axes[i, 1].set_xlabel('')
        else:
            axes[i, 1].set_xlabel('lag')
            axes[i, 1].set_xticklabels(range(1,16,1), rotation=0) 
    
    # Add the colorbar 
    cbar_ax_bwr = fig.add_axes([0.35, 0.095, 0.58, 0.01])
    cbar_bwr = plt.colorbar(cm.ScalarMappable(cmap=cmap, norm=norm), cax=cbar_ax_bwr, orientation='horizontal')
    cbar_bwr.set_ticks([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])
    cbar_bwr.set_ticklabels(['-1', '-0.8', '-0.6', '-0.4', '-0.2', '0', '0.2', '0.4', '0.6', '0.8', '1'])
    cbar_bwr.set_label('correlation')

    # Add the labels and right size
    plt.tight_layout(rect=[0, 0.1, 1, 1], pad=2)  # Adjusts subplot params, leaving space for the colorbars
    
    for i, label in enumerate(labels):
        if i<n_net:
            axes[i, 0].text(0.05, t1, label, transform=axes[i, 0].transAxes, 
                        fontsize=16, fontname='Arial', fontweight='bold', va='center', ha='right')
        else:
            axes[i-n_net, 1].text(0.05, t1, label, transform=axes[i-n_net, 1].transAxes, 
                        fontsize=16, fontname='Arial', fontweight='bold', va='center', ha='right')
    plt.show()
        
    savefile = f'{path}/{hypo}_{strategy}_{atlas_name}_{thr}.pdf'
    plt.savefig(savefile, dpi=300)