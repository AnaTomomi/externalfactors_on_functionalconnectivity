import sys
import pandas as pd
import string
import matplotlib.pyplot as plt
import netplotbrain as npb

from matplotlib.colors import LinearSegmentedColormap

sys.path.append('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/visualization')
from visual_utils import get_nodes_edges

###############################################################################
# Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H2'
strategy = "24HMP-8Phys-Spike"
atlas_name = 'seitzman-set1'
###############################################################################

#general plotting settings
colors = ['#4daf4a', '#984ea3', '#f781bf', '#ffff33']
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)
views=['L','S','R','P']

hypo = path[-2:]
ge = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='global-eff')
pc = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='parti-coeff')
links = pd.read_excel(f'{path}/{strategy}_HPF_{atlas_name}_finaltable.xlsx', sheet_name='reg-links')

#case 1: only links are reported
if len(ge)==0 and len(pc)==0 and len(links)>0: 
    X = links["external factor"].nunique()
    external_factors = links["external factor"].unique()
    
    #start plotting
    fig = plt.figure(figsize=(10, X*5))
    for i, factor in enumerate(external_factors):
        factor_links = links[links["external factor"]==factor]
        nodes, edges = get_nodes_edges(factor_links)

        #plot 
        for j in range(4):
            ax = fig.add_subplot(X, 4, i*4+j+1, projection='3d')
            npb.plot(template='MNI152NLin2009cAsym',
                     template_style='glass', template_glass_maxalpha=0.05,
                     nodes=nodes, node_type='spheres', node_cmap=cmap, node_color='community',
                     edges=edges,edge_color={'negative':'b','positive':'r'}, edge_weights='weight', edge_widthscale=2,
                     view=views[j], fig=fig, ax=ax,
                     legend_tick_fontsize=14, legend_title_fontsize=14, font= 'Arial', fontcolor = 'k', node_colorlegend=False)
    for i in range(X):
        label = string.ascii_uppercase[i]
        leftmost_plot_position = fig.get_axes()[i * 4].get_position()
        fig.text(0.02, leftmost_plot_position.y0 + 0.27, label, fontsize=16, ha='left', va='top')

    plt.tight_layout()
    plt.show()
    plt.savefig(f'{path}/{hypo}_{strategy}_{atlas_name}.pdf', dpi=300)

#case 2: PC and links are reported
if len(ge)==0 and len(pc)>0 and len(links)>0: 
    Y = links["external factor"].nunique()
    external_factors = links["external factor"].unique()
    
    X = pc["network"].nunique()
    networks = pc["network"].unique()
    
    fig = plt.figure(figsize=(10, X*5))
    