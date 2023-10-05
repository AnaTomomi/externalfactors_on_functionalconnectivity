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
savepath = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/glm';
task = 'pvt';

%read the data
variables = xlsread(sprintf('%s/behavioral/sub-01_day-lag1_task_pvt.xlsx', path));
meanFD = readmatrix(sprintf('%s/mri/sub-01_day-all_device-mri_meas-meanfd.csv', path));
intercept = ones(size(variables,1),1);

if strcmp(task,'pvt')
    variables = variables(:,1:5); %Only take the sleep variables
    meanFD = meanFD(:,2);
elseif strcmp(task,'nback')
    meanFD = meanFD(:,5);
end

designmatrix = [variables, meanFD];
designmatrix = designmatrix-mean(designmatrix); %demean the data according to (1)
designmatrix = [intercept, designmatrix];
save(sprintf('%s/design.mat',savepath), 'designmatrix', '-ASCII','-append');

contrast = zeros(1,size(designmatrix,2));
sleep_dur = contrast; awake = contrast; restless = contrast; efficiency = contrast; latency = contrast; 
sleep_dur(1,2) = 1;
awake(1,3) = 1;
restless(1,4) = 1;
efficiency(1,5) = 1;
latency(1,6) = 1;

%Save the files
save(sprintf('%s/sleep_duration.con',savepath), 'sleep_dur', '-ASCII','-append');
save(sprintf('%s/awake_time.con',savepath), 'awake', '-ASCII','-append');
save(sprintf('%s/restless_sleep.con',savepath), 'restless', '-ASCII','-append');
save(sprintf('%s/sleep_efficiency.con',savepath), 'efficiency', '-ASCII','-append');
save(sprintf('%s/sleep_latency.con',savepath), 'latency', '-ASCII','-append');

if strcmp(task,'nback')
    steps = contrast; inactive = contrast; 
    steps(1,7) = 1;
    inactive(1,8) = 1;

    save(sprintf('%s/steps.con',savepath), 'steps', '-ASCII','-append');
    save(sprintf('%s/inactive_time.con',savepath), 'inactive', '-ASCII','-append');
end

contrast(1,2:(size(contrast,2)-1))=1;
save(sprintf('%s/all_vars.con',savepath), 'contrast', '-ASCII','-append');
