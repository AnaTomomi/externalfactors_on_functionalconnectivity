%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script cuts the BIOPAC post-processed data according to the cuts   %
% defined for the NII files.                                              % 
% The cut files are in the 
%                                                                         %
%Author: ana.trianahoyos@aalto.fi                                         %
%created: 08.09.2021                                                      %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all
close all
clc

path = '/m/cs/project/networks-pm/mri/fast_prepro_bids';
savepath = '/m/cs/scratch/networks-pm/pm_preprocessed/';
sub = 'sub-07';
tasks = {'pvt', 'resting', 'movie', 'nback'}; %Tasks in the order they were taken in the scanner

for i=1:length(tasks)
    task = tasks{i};
    load(sprintf('%s/%s/func/%s_task-%s_device-biopac_downsampled.mat', path, sub, sub, task))
    disp(task)
    if strcmp(task,'pvt')
        downsampled_cut = downsampled_tr(:,6:1121);
        disp(size(downsampled_cut))
    elseif strcmp(task,'resting')
        downsampled_cut = downsampled_tr(:,6:1107);
        disp(size(downsampled_cut))
    elseif strcmp(task,'movie')
        downsampled_cut = downsampled_tr(:,6:1064);
        disp(size(downsampled_cut))
    elseif strcmp(task,'nback')
        downsampled_cut = downsampled_tr(:,6:619);
        disp(size(downsampled_cut))
    end
    
    save(sprintf('%s/%s/func/%s_task-%s_device-biopac_downsampledcut.mat', savepath, sub, sub, task), 'downsampled_cut');
end
