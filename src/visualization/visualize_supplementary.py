"""
This script creates the visualizations for the supplementary analysis

To understand the thresholding, read https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Randomise/UserGuide

"""
import numpy as np
import glob
import nibabel as nib
from nilearn.plotting import plot_stat_map

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

###############################################################################
# Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/supplementary'
strategy = '24HMP-8Phys-Spike_HPF'
alpha = 0.05
###############################################################################

#Set common parameters for the plots
plt.rcParams['font.size'] = 14
plt.rcParams['font.family'] = 'Arial'

#set colors and graphics paramteres
positive_colors = ['#FFFFFF', '#FFFAB8', '#FFD978', '#FF9751', '#FF551A', '#FF0000']
negative_colors = [plt.cm.Greys(i) for i in np.linspace(0, 1, len(positive_colors))][::-1]
colors = negative_colors + positive_colors
custom_cmap = ListedColormap(colors)

# Values for the colorbar
values = [0, 1.5, 3.0, 4.5, 6.0, 7.5]
colors = ['#FFFFFF', '#FFFAB8', '#FFD978', '#FF9751', '#FF551A', '#FF0000']
cmap = plt.cm.colors.ListedColormap(colors)
norm = plt.cm.colors.BoundaryNorm(values, cmap.N)

#Check files with significant findings
files = sorted(glob.glob(path + f'/*_glm-second_{strategy}_tfce_corrp_tstat1.nii.gz', recursive=True))

thres = 1-alpha
significant = []
for file in files:
    pval_img = nib.load(file)
    pval_data = pval_img.get_fdata()
    if np.any(pval_data > 0.95):
        significant.append(file)

for file in significant:
    filename = file.split('/')[-1]
    parts = filename.split('_')
    
    #load the files
    tstat_img = nib.load(f'{path}/{parts[0]}_{parts[1]}_glm-second_{parts[3]}_HPF_tstat1.nii.gz')
    pval_img = nib.load(file)
    tstat_data = tstat_img.get_fdata()
    pval_data = pval_img.get_fdata()
    
    combined_data = tstat_data * (pval_data>thres)
    combined_img = nib.Nifti1Image(combined_data, tstat_img.affine)
    
    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_axes([0.05, 0.1, 0.8, 0.8])

    # Plotting the stat_map
    display = plot_stat_map(combined_img, colorbar=False, draw_cross=False, cmap=custom_cmap, symmetric_cbar=False, axes=ax1)
    display.annotate(size=16)

    # Define axis for the colorbar
    cax = fig.add_axes([0.9, 0.18, 0.02, 0.65])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="vertical")
    cb.set_label('T-statistic', rotation=270, labelpad=15)
    cb.set_ticks(values)

    plt.savefig(f'{path}/{parts[0]}_{parts[1]}_glm-second_{parts[3]}_HPF.pdf', dpi=300)
    
