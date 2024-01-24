"""
This script creates the visualizations for the supplementary analysis

To understand the thresholding, read https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Randomise/UserGuide

"""
import numpy as np
import glob
import math
import string
import nibabel as nib
from nilearn.plotting import plot_stat_map

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

###############################################################################
# Change this only!
tr = '1TR-4GSR'
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H8'
strategy = '24HMP-8Phys-Spike_HPF'
alpha = 0.05
###############################################################################

# Function to extract the number before "_24HMP" from a file path
def extract_number(filepath):
    # Split the filepath and find the part with "_24HMP"
    parts = filepath.split('/')
    for part in parts:
        if "_24HMP" in part:
            # Find the position where "_24HMP" starts
            pos = part.find('_24HMP')
            # Extract the part of the string just before "_24HMP"
            num_part = part[:pos]
            # Extract the digits from that part of the string
            num = ''.join(filter(str.isdigit, num_part))
            # Return the number as an integer
            return int(num)
    return 0  # Return 0 if no number is found

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
files = sorted(glob.glob(path + f'/{tr}/*_tfce_corrp_tstat1.nii.gz', recursive=True))

thres = 1-alpha
significant = []
for file in files:
    pval_img = nib.load(file)
    pval_data = pval_img.get_fdata()
    if np.any(pval_data > 0.95):
        significant.append(file)
significant_sorted = sorted(significant, key=extract_number)

num_files = len(significant_sorted)
num_columns = 3
num_rows = math.ceil(num_files / num_columns)

fig, axes = plt.subplots(num_rows, num_columns, figsize=(5 * num_columns, 5 * num_rows))
plt.subplots_adjust(wspace=0.1, hspace=-0.1, left=0.03, right=0.98, top=1, bottom=0.05)
if num_rows * num_columns > num_files:
    axes[-1, -1].set_visible(False)
axes_flat = axes.flatten()

for ax, file, letter in zip(axes_flat, significant_sorted, string.ascii_uppercase):
    filename = file.split('/')[-1]
    print(filename)
    
    #load the files
    tstat_img = nib.load(f'{path}/{tr}/{filename[:-24]}tstat1.nii.gz')
    pval_img = nib.load(file)
    tstat_data = tstat_img.get_fdata()
    pval_data = pval_img.get_fdata()
    
    combined_data = tstat_data * (pval_data>thres)
    combined_img = nib.Nifti1Image(combined_data, tstat_img.affine)
    
    # Display the combined image
    display = plot_stat_map(combined_img, colorbar=False, draw_cross=False, 
                            cmap=custom_cmap, symmetric_cbar=False, annotate=False, axes=ax)
    ax.text(0.0, 0.8, letter, transform=ax.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')


# Define axis for the colorbar
cax = fig.add_axes([0.15, 0.1, 0.65, 0.02])
cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal")
cb.set_label('T-statistic', rotation=0, labelpad=15)
cb.set_ticks(values)

plt.savefig(f'{path}/{strategy}_{tr}.pdf', dpi=300)
    
