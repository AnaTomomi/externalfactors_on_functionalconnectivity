import sys
import pandas as pd
import string
import matplotlib.pyplot as plt
import netplotbrain as npb

from scipy.io import loadmat
import statsmodels.api as sm

from matplotlib.colors import LinearSegmentedColormap

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/visualization')
from visual_utils import get_nodes_edges, plot_connectome, get_nodes_from_atlas

###############################################################################
# Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H2'
atlas_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral'
strategy = "24HMP-8Phys-Spike"
atlas_name = 'seitzman-set1'
###############################################################################

#general plotting settings
colors = ['#4daf4a', '#984ea3', '#f781bf', '#ffff33']
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
views=['L','S','R','P','L','S','R','P']

#set the atlas and behavioral info
hypo = path[-2:]
if hypo=='H1':
    beh = pd.read_excel(f'{behav_path}/sub-01_day-lag1_task_pvt.xlsx')
    brain_ge = loadmat(f'{atlas_path}/pvt/{strategy}_HPF/global-eff_{strategy}_HPF_{atlas_name}_thr-10.mat')['effs']
    brain_pc = loadmat(f'{atlas_path}/pvt/{strategy}_HPF/parti-coeff_{strategy}_HPF_{atlas_name}_thr-10.mat')['pcs']
    network_mapping = {'default mode': 1,'fronto parietal': 2,'cingulo opercular':3, 'somatomotor':4}
    cols = ['total_sleep_duration', 'awake_time', 'restless_sleep']
elif hypo=='H2':
    beh = pd.read_excel(f'{behav_path}/sub-01_day-lag1_task_pvt.xlsx')
    brain_ge = loadmat(f'{atlas_path}/nback/{strategy}_HPF/global-eff_{strategy}_HPF_{atlas_name}_thr-10.mat')['effs']
    brain_pc = loadmat(f'{atlas_path}/nback/{strategy}_HPF/parti-coeff_{strategy}_HPF_{atlas_name}_thr-10.mat')['pcs']
    network_mapping = {'default mode':1, 'fronto parietal':2, 'somatomotor':3}
    cols = ['total_sleep_duration', 'awake_time', 'restless_sleep','steps', 'inactive_time']
elif hypo=='H3':
    beh = pd.read_excel(f'{behav_path}/sub-01_day-lag1_task_rs.xlsx')
    brain_ge = loadmat(f'{atlas_path}/rs/{strategy}_HPF/global-eff_{strategy}_HPF_{atlas_name}_thr-10.mat')['effs']
    brain_pc = loadmat(f'{atlas_path}/rs/{strategy}_HPF/parti-coeff_{strategy}_HPF_{atlas_name}_thr-10.mat')['pcs']
    network_mapping = {'default mode':1, 'fronto parietal':2, 'cingulo opercular':3}
    cols = ['total_sleep_duration','awake_time','restless_sleep','pa_mean','pa_std','na_mean','stress_mean',
            'pain_mean','mean_respiratory_rate_brpm','min_respiratory_rate_brpm','max_respiratory_rate_brpm',
            'mean_prv_rmssd_ms','min_prv_rmssd_ms','max_prv_rmssd_ms']
    
# Read the data
ge = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='global-eff')
pc = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='parti-coeff')
links = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='reg-links')

#case 1: only links are reported
if len(ge)==0 and len(pc)==0 and len(links)>0: 
    X = links["external factor"].nunique()
    external_factors = links["external factor"].unique()
    
    #create the layout first
    fig = plt.figure(figsize=(15, 7))
    grid_3d = plt.GridSpec(X, 4, wspace=-0.1, hspace=-0.1, left=0.05, right=0.95)
    axes_3d = []
    for row in range(X):
        for col in range(4):
            ax = fig.add_subplot(grid_3d[row, col], projection='3d')
            axes_3d.append(ax)
    
    #now do the plotting 
    for row, factor in enumerate(external_factors):
        factor_links = links[links["external factor"]==factor]
        nodes, edges = get_nodes_edges(factor_links)
        for col in range(4):
            ax = axes_3d[row * 4 + col]
            npb.plot(template='MNI152NLin2009cAsym',
                         template_style='glass', template_glass_maxalpha=0.05,
                         nodes=nodes, node_type='spheres', node_cmap=cmap, node_color='community',
                         edges=edges,edge_color={'negative':'b','positive':'r'}, edge_weights='weight', edge_widthscale=2,
                         view=views[col], node_colorlegend=False, fontcolor='k', title=None, fig=fig, ax=ax)
    for i in range(X):
        label = string.ascii_uppercase[i]
        leftmost_plot_position = fig.get_axes()[i * 4].get_position()
        fig.text(0.02, leftmost_plot_position.y0 + 0.5, label, fontsize=16, ha='left', va='top')
    plt.show()
    plt.savefig(f'{path}/{hypo}_{strategy}_{atlas_name}.pdf', dpi=300)

#case 2: PC and links are reported
if len(ge)==0 and len(pc)>0 and len(links)>0: 
    Y = links["external factor"].nunique()
    external_factors = links["external factor"].unique()
    
    X = pc["network"].nunique()
    networks = pc["network"].unique()
    
    fig = plt.figure(figsize=(12, 8))
    # First grid space with 4 columns and Y rows for plotting the links
    grid1 = plt.GridSpec(Y, 4, fig, left=0.05, right=0.7, hspace=-0.2, wspace=0.2)        
    
    for i, factor in enumerate(external_factors):
        factor_links = links[links["external factor"]==factor]
        nodes, edges = get_nodes_edges(factor_links)
        for j in range(4):
            ax = fig.add_subplot(grid1[i, j], projection='3d')
            npb.plot(template='MNI152NLin2009cAsym', template_style='glass', template_glass_maxalpha=0.01,
                     nodes=nodes, node_type='spheres', node_cmap=cmap, node_color='community',
                     edges=edges,edge_color={'negative':'b','positive':'r'}, edge_weights='weight', edge_widthscale=2,
                     view=views[j], node_colorlegend=False, fontcolor='k', title=None, fig=fig, ax=ax)
            
    # Second grid space with 1 column and X*2 rows for plotting the PCs
    grid2 = plt.GridSpec(X * 2, 1, fig, left=0.8, right=0.95, hspace=-0.2)
    for i,net in enumerate(networks):
        #plot the network
        ax = fig.add_subplot(grid2[i*2, 0], projection='3d')
        nodes_df = get_nodes_from_atlas(atlas_path, atlas_name, net)
        npb.plot(nodes=nodes_df, template='MNI152NLin2009cAsym', title=None, fig=fig, ax=ax)
        
        #now plot the network vs. external factor
        ax = fig.add_subplot(grid2[i*2+1, 0])
        brain2plot = pc["network"].iloc[i]
        y = pd.Series(brain_pc[:,network_mapping[brain2plot]-1], name='pc') #the indices were matlab-based that starts at 1
        x = beh[cols]
        data = pd.concat([y,x], axis=1)
        
        exog_i = (pc["external factor"].iloc[i]).replace(' ', '_')
        exog_others = list(set(cols) - set([exog_i]))
        sm.graphics.plot_partregress(endog='pc', exog_i=exog_i, exog_others=exog_others, data=data, obs_labels=False, ax=ax)
        ax.set_title('') 
        ax.set_xlabel(f'e({exog_i.replace("_"," ")} | X)')
        ax.set_ylabel('e(participation coefficient | X)')
        
        ax.set_aspect('equal')
    
    plt.show()
    plt.savefig(f'{path}/{hypo}_{strategy}_{atlas_name}.pdf', dpi=300)
        
        
        
    
    