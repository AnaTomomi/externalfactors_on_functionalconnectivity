"""
This script summarizes the significant results for H4 organizing them and 
matching the results with the node coordinates and different scrubbing schemes

"""
import os
import json
import glob
import pandas as pd

from nltools.stats import fdr
from statsmodels.stats.multitest import fdrcorrection

###############################################################################
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H4'
conn_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie'
atlas_name = 'seitzman-set1'

strategies = ['24HMP-8Phys-Spike', '24HMP-8Phys-4GSR-Spike']
scrub = ['scrub-hard', 'scrub-soft']
###############################################################################

def get_results(file):
    ''' reads the r and p values from the files for each Mantel test. It returns
    the correlation value and the corrected p-value.
    
    Parameters
    ----------
    file: str
    
    Returns
    -------
    r: dict
    q: tuple
    '''
    with open(os.path.join(path,file), 'r') as f:
        result = json.load(f)
    r = result[0]
    p = result[1]
    q = fdrcorrection(pd.Series(p).values)
    return r,q

def check_results_movie(files):
    ''' loads each json file where the p-values are stored and performs the 
    Benjamin and Hochberg correction. It returns a list of files with significant
    results. 
    
    Parameters
    ----------
    files: list
    
    Returns
    -------
    answer: list
    '''
    answer = []
    for file in files:
        folder, file_name = os.path.split(file)
        with open(file, 'r') as f:
            result = json.load(f)
        p = result[1]
        q = fdr(pd.Series(p).values)
        if q>-1:
            answer.append(file_name)
    return answer

###############################################################################

# Check if there are any significant results
files = sorted(glob.glob(path + f'/mantel*hard*.json', recursive=True))
hard = check_results_movie(files)

files = sorted(glob.glob(path + f'/mantel*soft*.json', recursive=True))
soft = check_results_movie(files)

# Removing duplicate results in the stability table


# Check the stability of results
df = pd.DataFrame(columns=['behavior','ROI', 'model', 'strategy', 'parcel', 'scrub', 'r', 'p'])

for file in hard:
    var = file.split("_")
    r, q = get_results(file)
    rois = [index for index, value in enumerate(q[0]) if value]
    
    for roi in rois:
        #get the actual roi
        real_roi = list(r.keys())[roi]
        
        #Add first the significant result
        if len(var)==10:
            df = df.append({'behavior':"_".join([var[4],var[5]]),'ROI': roi, 'model':var[0][7:], 'strategy': var[1], 
                            'parcel': var[3],'scrub':"_".join([var[7],var[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        elif len(var)==11: 
            df = df.append({'behavior':"-".join([var[4],var[5]]),'ROI': roi, 'model':var[0][7:], 'strategy': var[1], 
                        'parcel': var[3],'scrub': "_".join([var[8],var[10]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        else: 
            df = df.append({'behavior':"-".join([var[4],var[5]]),'ROI': roi, 'model':var[0][7:], 'strategy': var[1], 
                        'parcel': var[3],'scrub':"_".join([var[6],var[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        
        #now add the other counterparts
        #first the different scrubs
        var_other = var.copy()
        if var_other[4]=='sleep-total':
            var_other[7] = 'scrub-soft'
        elif var_other[5] == 'prv':
            var_other[8] = 'scrub-soft'
        else:
            var_other[6] = 'scrub-soft'
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
        if len(var)==10:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                            'strategy': var_other[1], 'parcel': var_other[3],
                            'scrub':"_".join([var_other[7],var_other[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        elif len(var)==11:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                        'strategy': var_other[1], 'parcel': var_other[3],
                        'scrub':"_".join([var_other[8],var_other[10]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        else:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                        'strategy': var_other[1], 'parcel': var_other[3],
                        'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        
        var_other[-1] = 'per-0.1.json'
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
        if len(var)==10:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                            'strategy': var_other[1], 'parcel': var_other[3],
                            'scrub':"_".join([var_other[7],var_other[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        elif len(var)==11:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                        'strategy': var_other[1], 'parcel': var_other[3],
                        'scrub':"_".join([var_other[8],var_other[10]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        else: 
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:],
                        'strategy': var_other[1], 'parcel': var_other[3],
                        'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        #and then the strategy
        other = [s for s in strategies if s not in var][0]
        var_other = var.copy()
        var_other[1] = other
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
        if len(var)==10:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                            'strategy': var_other[1], 'parcel': var_other[3],
                            'scrub':"_".join([var_other[7],var_other[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        elif len(var)==11:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                        'strategy': var_other[1], 'parcel': var_other[3],
                        'scrub':"_".join([var_other[8],var_other[10]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        else: 
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                        'strategy': var_other[1],'parcel': var_other[3],
                        'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
    
for file in soft:
    var = file.split("_")
    r, q = get_results(file)
    rois = [index for index, value in enumerate(q[0]) if value]
    
    for roi in rois:
        #Add first the significant result
        if len(var)==11:
            df = df.append({'behavior':"_".join([var[4],var[5]]),'ROI': roi, 'model':var[0][7:], 'strategy': var[1], 
                            'parcel': var[3],'scrub':"_".join([var[8],var[10]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        elif len(var)==10:
            df = df.append({'behavior':"_".join([var[4],var[5]]),'ROI': roi, 'model':var[0][7:], 'strategy': var[1], 
                            'parcel': var[3],'scrub':"_".join([var[7],var[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        else:
            df = df.append({'behavior':"_".join([var[4],var[5]]),'ROI': roi, 'model':var[0][7:], 'strategy': var[1], 
                        'parcel': var[3],'scrub':"_".join([var[6],var[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        
        #now add the other counterparts
        #first the different scrubs
        var_other = var.copy()
        if var[-1] == 'per-0.1.json':
            var_other[-1] = 'per-0.05.json'
        else:
            var_other[-1] = 'per-0.1.json'
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
        if len(var)==11:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                            'parcel': var_other[3],'scrub':"_".join([var_other[8],var_other[10]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
            var_other[8] = 'scrub-hard'
        elif len(var)==10:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                            'parcel': var_other[3],'scrub':"_".join([var_other[7],var_other[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
            var_other[7] = 'scrub-hard'
        else:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                        'parcel': var_other[3],'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
            var_other[6] = 'scrub-hard'
            
        var_other[-1] = 'per-0.05.json'
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
        if len(var)==11:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                            'parcel': var_other[3],'scrub':"_".join([var_other[8],var_other[10]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        elif len(var)==10:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                            'parcel': var_other[3],'scrub':"_".join([var_other[7],var_other[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        else:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                        'parcel': var_other[3],'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        
        #and then the strategy
        other = [s for s in strategies if s not in var][0]
        var_other = var.copy()
        var_other[1] = other
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
        if len(var)==11:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                            'parcel': var_other[3],'scrub':"_".join([var_other[8],var_other[10]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        elif len(var)==10:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                            'parcel': var_other[3],'scrub':"_".join([var_other[7],var_other[9]])[6:-5], 
                            'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        else:
            df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var_other[0][7:], 'strategy': var_other[1], 
                        'parcel': var_other[3],'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)


#Include the ROI information for seitzman set-1
group_atlas = f'{conn_path}/group_mask_{atlas_name}.nii'
atlas_info = pd.read_excel(f'{conn_path}/group_seitzman-set1_info.xlsx')
atlas_info = atlas_info[atlas_info['netName'].isin(['DefaultMode', 'FrontoParietal', 'Salience'])]
selected_rois = atlas_info.index.to_list()
atlas_info.reset_index(inplace=True)
set1 = df[df['parcel'] == 'seitzman-set1']
set1 = set1.merge(atlas_info[['roi', 'x', 'y', 'z', 'netName']], 
                                left_on='ROI', right_index=True, how='left')
set1.rename(columns={'netName':'network'},inplace=True)

#Include the ROI information for seitzman set-2
atlas_info = pd.read_excel(f'{conn_path}/group_seitzman-set2_info.xlsx')
atlas_info = atlas_info[atlas_info['network'].isin([1,3,8])]
selected_rois = atlas_info.index.to_list()
atlas_info.reset_index(inplace=True)
network_mapping = {1:'DefaultMode',3:'FrontoParietal', 8:'Salience'}
atlas_info['network'] = atlas_info['network'].replace(network_mapping)
atlas_info.rename(columns={'gordon':'roi'},inplace=True)
set2 = df[df['parcel'] == 'seitzman-set2']
set2 = set2.merge(atlas_info[['roi', 'x', 'y', 'z', 'network']], 
                                left_on='ROI', right_index=True, how='left')

merged_df = pd.concat([set1, set2], axis=0).reset_index(drop=True)
merged_df = merged_df[['behavior', 'model', 'strategy', 'parcel', 'scrub', 'r', 'p',
                       'x', 'y', 'z', 'network']]

merged_df.to_excel(f'{path}/H4_stability.xlsx',index=False)

df = merged_df[merged_df.scrub=='soft_per-0.05']
df.drop(columns=["scrub"],inplace=True)
df.sort_values(by=['behavior', 'strategy', 'parcel'],inplace=True)
df = df[df.p<0.05]
df.drop_duplicates(inplace=True)
df.to_excel(f'{path}/H4_finaltable.xlsx',index=False)