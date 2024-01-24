%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The script prepares the design.mat and design.con files needed to run   %
% FSL randomise
% 
% (1)https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/GLM#Single-Group_Average_with_Additional_Covariate
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all
close all
clc

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data';
first_level = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/decoder';
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/decoder';
task = 'movie';
strategy = '24HMP-8Phys-Spike_HPF';

%read the data
data = readtable(sprintf('%s/behavioral/sub-01_day-lag-all_task_all.xlsx', path));
baseVarNames = {'total_sleep_duration', 'awake_time', 'restless_sleep', 'pa_mean', 'pa_std', 'na_mean', ...
        'stress_mean','pain_mean','mean_respiratory_rate_brpm','min_respiratory_rate_brpm',...
        'max_respiratory_rate_brpm','mean_prv_rmssd_ms','min_prv_rmssd_ms','max_prv_rmssd_ms'};
allColNames = data.Properties.VariableNames;
selectedCols = {};
for i = 1:length(baseVarNames)
    idx = startsWith(allColNames, [baseVarNames{i}, '']);
    selectedCols = [selectedCols, allColNames(idx)];
end

meanFD = readmatrix(sprintf('%s/mri/sub-01_day-all_device-mri_meas-meanfd.csv', path));
meanFD = meanFD(:,3);
intercept = ones(size(meanFD,1),1);

for i = 1:length(selectedCols)
    variable = data.(selectedCols{i});
    designmatrix = [variable, meanFD];
    design_matrix_file = sprintf('%s/%s_%s_design.txt',savepath, task, selectedCols{i});
    dlmwrite(design_matrix_file,designmatrix,'delimiter',' ','precision',12);
end