#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 22:59:11 2023

@author: trianaa1
"""
import os
import json
import glob
import pandas as pd

from nltools.stats import fdr
from statsmodels.stats.multitest import fdrcorrection

###############################################################################
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H4'

strategies = ['24HMP-8Phys-Spike', '24HMP-8Phys-4GSR-Spike']
scrub = ['scrub-hard', 'scrub-soft']
###############################################################################

def get_results(file):
    with open(os.path.join(path,file), 'r') as f:
        result = json.load(f)
    r = result[0]
    p = result[1]
    q = fdrcorrection(pd.Series(p).values)
    return r,q

def check_results_movie(files):
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
        df = df.append({'behavior':"_".join([var[4],var[5]]),'ROI': roi, 'model':var[0][7:], 'strategy': var[1], 
                        'parcel': var[3],'scrub':"_".join([var[6],var[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        
        #now add the other counterparts
        #first the different scrubs
        var_other = var.copy()
        var_other[6] = 'scrub-soft'
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
        df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                        'strategy': var_other[1], 'parcel': var_other[3],
                        'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        
        var_other[-1] = 'per-0.1.json'
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
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
        
        df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:],
                        'strategy': var_other[1], 'parcel': var_other[3],
                        'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)
        
        var_other[6] = 'scrub-hard'
        var_other[-1] = 'per-0.05.json'
        other_file = "_".join(var_other)
        r, q = get_results(other_file)
        
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
        
        df = df.append({'behavior':"_".join([var_other[4],var_other[5]]),'ROI': roi, 'model':var[0][7:], 
                        'strategy': var_other[1],'parcel': var_other[3],
                        'scrub':"_".join([var_other[6],var_other[8]])[6:-5], 
                        'r': pd.Series(r).values[roi],'p': q[1][roi]}, ignore_index=True)

df.to_csv(f'{path}/stability.csv')