import sys
import pandas as pd
import matplotlib.pyplot as plt
import netplotbrain as npb

from scipy.io import loadmat
import statsmodels.api as sm

from matplotlib.colors import LinearSegmentedColormap

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/visualization')
from visual_utils import get_nodes_edges, get_nodes_from_atlas

###############################################################################
# Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H1'
atlas_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral'
strategy = "24HMP-8Phys-4GSR-Spike"
atlas_name = 'seitzman-set1'
thres = 0.1
###############################################################################

#general plotting settings
colors = ['#4daf4a', '#984ea3', '#f781bf', '#ffff33']
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
views=['L','S','P','L','S','P']
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

mapping =  {'pa mean': 'mean PA', 'na mean':'mean NA', 'stress mean': 'mean stress',
            'pain mean': 'mean pain', 'mean respiratory rate brpm': 'mean respiratory rate',
            'min respiratory rate brpm': 'min respiratory rate', 
            'max respiratory rate brpm': 'max respiratory rate', 'mean prv rmssd ms': 'mean HRV', 
            'min prv rmssd ms': 'min HRV', 'max prv rmssd ms': 'max HRV'}

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
ge = ge[ge['threshold']==thres]
pc = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='parti-coeff')
pc = pc[pc['threshold']==thres]
links = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='reg-links')

#case 1: only links are reported
if len(ge)==0 and len(pc)==0 and len(links)>0: 
    X = links["external factor"].nunique()
    external_factors = links["external factor"].unique()
    
    #create the layout first
    fig = plt.figure(figsize=(15, 7))
    grid_3d = plt.GridSpec(X, 3, wspace=-0.1, hspace=-0.1, left=0.05, right=0.95)
    axes_3d = []
    label_index = 0
    for row in range(X):
        for col in range(3):
            ax = fig.add_subplot(grid_3d[row, col], projection='3d')
            axes_3d.append(ax)
            if col == 0:  # Only label the leftmost axis
                ax.text2D(0.05, 0.95, labels[label_index], fontfamily='Arial', fontsize=16, fontweight='bold', transform=ax.transAxes)
                label_index += 1
    
    #now do the plotting 
    for row, factor in enumerate(external_factors):
        print(factor)
        factor_links = links[links["external factor"]==factor]
        nodes, edges = get_nodes_edges(factor_links)
        for col in range(3):
            ax = axes_3d[row * 3 + col]
            npb.plot(template='MNI152NLin2009cAsym',
                         template_style='glass', template_glass_maxalpha=0.25,
                         nodes=nodes, node_type='spheres', node_cmap=cmap, node_color='color',
                         edges=edges,edge_color={'negative':'b','positive':'r'}, edge_weights='weight', edge_widthscale=2,
                         view=views[col], node_colorlegend=False, fontcolor='k', title=None, fig=fig, ax=ax)
    
    plt.savefig(f'{path}/{hypo}_{strategy}_{atlas_name}.png')
    plt.show()

#case 2: PC and links are reported
if len(ge)==0 and len(pc)>0 and len(links)>0: 
    Y = links["external factor"].nunique()
    external_factors = links["external factor"].unique()
    
    X = pc["network"].nunique()
    networks = pc["network"].unique()
    
    #create the plot first
    fig = plt.figure(figsize=(15, 12))
    grid_3d = plt.GridSpec(Y, 3, wspace=-0.1, hspace=-0.1, left=0.01, right=0.75)
    grid_2d = plt.GridSpec(4, X, wspace=0.1, hspace=0.1, left=0.79, right=0.95)
    axes_3d, axes_2d = [],[]

    #Plot the links
    label_index=0
    for row in range(Y):
        for col in range(3):
            ax = fig.add_subplot(grid_3d[row, col], projection='3d')
            if col == 0:  # Only label the leftmost axis
                ax.text2D(0.05, 0.95, labels[label_index], fontfamily='Arial', fontsize=16, fontweight='bold', transform=ax.transAxes)
                label_index += 1
            axes_3d.append(ax)
    for row in range(4):
        if row == 0:
            ax2 = fig.add_subplot(grid_2d[row:2, 0], projection='3d')
            ax2.text2D(0.05, 0.95, labels[label_index], fontfamily='Arial', fontsize=16, fontweight='bold', transform=ax2.transAxes)
            label_index += 1
            axes_2d.append(ax2)
        elif row ==2:
            ax2 = fig.add_subplot(grid_2d[row, 0])
            ax2.text(-0.2, 1.1, labels[label_index], fontfamily='Arial', fontsize=16, fontweight='bold', transform=ax2.transAxes)
            label_index += 1
            axes_2d.append(ax2)
        else:
            ax2 = fig.add_subplot(grid_2d[row, 0])
            ax2.set_visible(False)
    
    for row, factor in enumerate(external_factors):
        print(factor)
        factor_links = links[links["external factor"]==factor]
        nodes, edges = get_nodes_edges(factor_links)
        for col in range(3):
            ax = axes_3d[row * 3 + col]
            npb.plot(template='MNI152NLin2009cAsym', template_style='glass', template_glass_maxalpha=0.2,
                     nodes=nodes, node_type='spheres', node_cmap=cmap, node_color='color',
                     edges=edges,edge_color={'negative':'b','positive':'r'}, edge_weights='weight', edge_widthscale=2,
                     view=views[col], node_colorlegend=False, fontcolor='k', title=None, fig=fig, ax=ax)
    #Plot the PC
    for row,net in enumerate(networks):
        print(net)
        ax = axes_2d[row]
        nodes_df = get_nodes_from_atlas(atlas_path, atlas_name, net)
        npb.plot(nodes=nodes_df, node_scale=50, node_alpha=0.9, node_color='k', title=None, fig=fig, ax=ax,
                 template='MNI152NLin2009cAsym', template_style='glass', template_glass_maxalpha=0.05)
        
        #now plot the network vs. external factor
        ax = axes_2d[2*row+1]
        brain2plot = pc["network"].iloc[row]
        y = pd.Series(brain_pc[:,network_mapping[brain2plot]-1], name='pc') #the indices were matlab-based that starts at 1
        x = beh[cols]
        data = pd.concat([y,x], axis=1)
        
        exog_i = (pc["external factor"].iloc[row]).replace(' ', '_')
        exog_others = list(set(cols) - set([exog_i]))
        sm.graphics.plot_partregress(endog='pc', exog_i=exog_i, exog_others=exog_others, data=data, obs_labels=False, ax=ax)
        ax.set_title('') 
        exog_i = exog_i.replace("_"," ")
        exog_i = mapping.get(exog_i, exog_i)
        ax.set_xlabel(f'e({exog_i} | X)')
        ax.set_ylabel('e(participation coefficient | X)')
        
    plt.savefig(f'{path}/{hypo}_{strategy}_{atlas_name}.png')
    plt.show()
        
        
#case 3: GE and links are reported
if len(ge)>0 and len(pc)==0 and len(links)>0: 
    Y = links["external factor"].nunique()
    external_factors = links["external factor"].unique()
    
    X = ge["network"].nunique()
    networks = ge["network"].unique()
    
    #create the plot first
    fig = plt.figure(figsize=(15, 12))
    grid_3d = plt.GridSpec(Y, 3, wspace=-0.1, hspace=-0.1, left=0.01, right=0.75)
    grid_2d = plt.GridSpec(4, X, wspace=0.1, hspace=0.1, left=0.79, right=0.95)
    axes_3d, axes_2d = [],[]

    #Plot the links
    label_index=0
    for row in range(Y):
        for col in range(3):
            ax = fig.add_subplot(grid_3d[row, col], projection='3d')
            if col == 0:  # Only label the leftmost axis
                ax.text2D(0.05, 0.95, labels[label_index], fontfamily='Arial', fontsize=16, fontweight='bold', transform=ax.transAxes)
                label_index += 1
            axes_3d.append(ax)
    for row in range(4):
        if row == 0:
            ax2 = fig.add_subplot(grid_2d[row:2, 0], projection='3d')
            ax2.text2D(0.05, 0.95, labels[label_index], fontfamily='Arial', fontsize=16, fontweight='bold', transform=ax2.transAxes)
            label_index += 1
            axes_2d.append(ax2)
        elif row ==2:
            ax2 = fig.add_subplot(grid_2d[row, 0])
            ax2.text(-0.2, 1.1, labels[label_index], fontfamily='Arial', fontsize=16, fontweight='bold', transform=ax2.transAxes)
            label_index += 1
            axes_2d.append(ax2)
        else:
            ax2 = fig.add_subplot(grid_2d[row, 0])
            ax2.set_visible(False)
    plt.show()
    
    for row, factor in enumerate(external_factors):
        print(factor)
        factor_links = links[links["external factor"]==factor]
        nodes, edges = get_nodes_edges(factor_links)
        for col in range(3):
            ax = axes_3d[row * 3 + col]
            npb.plot(template='MNI152NLin2009cAsym', template_style='glass', template_glass_maxalpha=0.2,
                     nodes=nodes, node_type='spheres', node_cmap=cmap, node_color='color',
                     edges=edges,edge_color={'negative':'b','positive':'r'}, edge_weights='weight', edge_widthscale=2,
                     view=views[col], node_colorlegend=False, fontcolor='k', title=None, fig=fig, ax=ax)
    #Plot the GE
    for row,net in enumerate(networks):
        print(net)
        ax = axes_2d[row]
        nodes_df = get_nodes_from_atlas(atlas_path, atlas_name, net)
        npb.plot(nodes=nodes_df, node_scale=50, node_alpha=0.9, node_color='k', title=None, fig=fig, ax=ax,
                 template='MNI152NLin2009cAsym', template_style='glass', template_glass_maxalpha=0.05)
        
        #now plot the network vs. external factor
        ax = axes_2d[2*row+1]
        brain2plot = ge["network"].iloc[row]
        y = pd.Series(brain_ge[:,network_mapping[brain2plot]-1], name='ge') #the indices were matlab-based that starts at 1
        x = beh[cols]
        data = pd.concat([y,x], axis=1)
        
        exog_i = (ge["external factor"].iloc[row]).replace(' ', '_')
        exog_others = list(set(cols) - set([exog_i]))
        sm.graphics.plot_partregress(endog='ge', exog_i=exog_i, exog_others=exog_others, data=data, obs_labels=False, ax=ax)
        ax.set_title('') 
        exog_i = exog_i.replace("_"," ")
        exog_i = mapping.get(exog_i, exog_i)
        ax.set_xlabel(f'e({exog_i} | X)')
        ax.set_ylabel('e(global efficiency | X)')
        
    plt.show()
    plt.savefig(f'{path}/{hypo}_{strategy}_{atlas_name}.png')
    
    