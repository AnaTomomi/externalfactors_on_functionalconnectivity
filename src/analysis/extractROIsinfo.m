clear all
close all
clc

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/pvt';
atlas_name = 'seitzman-set1';
atlas = niftiread(sprintf('%s/group_mask_%s.nii',path,atlas_name));

%get the ROIs labels
if strcmp(atlas_name, 'seitzman-set1')
    rois_names = readtable('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/300MNI_Power.xlsx');
else
    rois_names = readtable('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman-gordon.xlsx');
end

%get the unique ROIs
rois = round(unique(atlas(:)));
if strcmp(atlas_name, 'seitzman-set1')
    group_rois = rois_names(ismember(rois_names.roi, rois), :);
else
    group_rois = rois_names(ismember(rois_names.gordon, rois), :);
end

writetable(group_rois, sprintf('%s/group_%s_info.xlsx',path,atlas_name))
