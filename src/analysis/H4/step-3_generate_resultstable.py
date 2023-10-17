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

