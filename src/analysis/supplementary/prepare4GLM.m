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
first_level = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/supplementary';
mask_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix';
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/glm';
task = 'nback';
strategy = '24HMP-8Phys-Spike_HPF';

%read the data
variables = xlsread(sprintf('%s/behavioral/sub-01_day-lag1_task_pvt.xlsx', path));
names = {'sleep_duration', 'awake_time', 'restless_sleep', 'sleep_efficiency', 'sleep_latency', 'steps', 'inactive_time'};
meanFD = readmatrix(sprintf('%s/mri/sub-01_day-all_device-mri_meas-meanfd.csv', path));
intercept = ones(size(variables,1),1);

if strcmp(task,'pvt')
    variables = variables(:,1:5); %Only take the sleep variables
    meanFD = meanFD(:,2);
elseif strcmp(task,'nback')
    meanFD = meanFD(:,5);
end

for i=1:size(variables,2)
    designmatrix = [intercept, variables(:,i), meanFD];
    design_matrix_file = sprintf('%s/%s_%s_design.txt',savepath, task, names{i});
    design_matrix_fslfile = sprintf('%s/%s_%s_design.mat',savepath, task, names{i});
    save(design_matrix_file, 'designmatrix', '-ASCII','-append');
end

%BEWARE: After running this code, someone needs to manually open the files,
%paste them in a text editor and re-save them as txt. Sorry, no way around
%it :(




