%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script generates the parcellation sets based on Seitzman (2020).   %
% It is necessary to generate set 1 before making set 2.                  %
%                                                                         %
% Author: ana.trianahoyos@aalto.fi                                        %
% Created: 19.10.2022                                                     %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all
close all
clc

addpath(genpath('/m/nbe/scratch/braindata/shared/toolboxes/bramila/bramila'));
addpath('/m/nbe/scratch/braindata/shared/toolboxes/NIFTI');

%set1 = readtable('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/ROIs_300inVol_MNI_allInfo.txt');
set1 = readtable('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/300MNI_Power.xlsx');
set2 = readtable('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman-gordon.xlsx');
gordon = readtable('/m/cs/scratch/networks-pm/atlas/Gordon-parcels/Parcels.xlsx');

set1 = table2struct(set1);
set2 = table2struct(set2);
gordon = table2struct(gordon);

set = 2; %1: generate seitzman set 1, 2: generate seitzman set 2
gordon_nii = load_nii('/m/cs/scratch/networks-pm/atlas/Gordon-parcels/Parcels_MNI_222.nii');
    
if set==1
    %Create the spheres for set 1
    gordon_nii.img = zeros(size(gordon_nii.img)); %empty the volume
    
    %Create the map for those spheres whose radius is 5mm
    ids_5mm = find([set1.radiusmm]==5);
    ids_4mm = find([set1.radiusmm]==4);
    set1_5mm = set1(ids_5mm);
    set1_4mm = set1(ids_4mm);
   
    cfg.imsize = size(gordon_nii.img);
    
    %Create the set for ROIs of 5mm
    no = size(set1_5mm,1);
    cfg_5mm.roi = zeros(no,3);
    cfg_5mm.labels={};
    cfg_5mm.radius = 2.5;
    for i=1:no
        cfg_5mm.roi(i,1) = set1_5mm(i).x;
        cfg_5mm.roi(i,2) = set1_5mm(i).y;
        cfg_5mm.roi(i,3) = set1_5mm(i).z;
        cfg_5mm.labels(i,1) = {sprintf('roi-%s',num2str(ids_5mm(i)))};
    end

    cfg_5mm.roi = round(cfg_5mm.roi);
    new_rois_5mm = bramila_makeRoiStruct(cfg_5mm);
    
    %Create the set for ROIs of 4mm
    no = size(set1_4mm,1);
    cfg_4mm.roi = zeros(no,3);
    cfg_4mm.labels={};
    cfg_4mm.radius = 2;
    for i=1:no
        cfg_4mm.roi(i,1) = set1_4mm(i).x;
        cfg_4mm.roi(i,2) = set1_4mm(i).y;
        cfg_4mm.roi(i,3) = set1_4mm(i).z;
        cfg_4mm.labels(i,1) = {sprintf('roi-%s',num2str(ids_4mm(i)))};
    end

    cfg_4mm.roi = round(cfg_4mm.roi);
    new_rois_4mm = bramila_makeRoiStruct(cfg_4mm);

    %Bring the two structures together
    new_rois = [struct2table(new_rois_5mm);struct2table(new_rois_4mm)];
    new_rois = table2struct(new_rois);
    
    %Delete any possible overlap
    comb = combvec([1:1:300],[1:1:300])';
    check_no = size(comb,1);
    for i=1:check_no
        if comb(i,1)~=comb(i,2)
            map = new_rois(comb(i,1)).map;
            map2 = new_rois(comb(i,2)).map;
            [id,~] = ismember(map,map2,'rows'); %repeated elements in map2
            [id2,~] = ismember(map2,map,'rows'); %repeated elements in map
            map2 = map2(~id2,:);
            map = map(~id,:);
            new_rois(comb(i,1)).map = map;
            new_rois(comb(i,2)).map = map2;
        end
        disp(i)
        clear map; clear map2; clear id2; clear id;
    end
    
    
    for i=1:300
        map = new_rois(i).map;
        map_voxels = size(map,1);
        value = extract(new_rois(i).label,digitsPattern);
        value = str2num(value{1,1});
        for j=1:map_voxels
            gordon_nii.img(map(j,1),map(j,2),map(j,3))=value;
        end
    end

    save_nii(gordon_nii, '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set1.nii')
    save('/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set1_struct.mat','new_rois')
end

if set==2
    parcel_no = size(set2,1);
    gordon_no = size(gordon,1);
        
    % Find the 34 subcortical and 27 cerebellar ROIs from Seitzman
    anatomicalLabelsToFind = {'hippocampus', 'amygdala', 'basalGanglia', 'thalamus', 'cerebellum'};
    rois2add = set1(arrayfun(@(x) any(strcmp(x.AnatomicalLabels, anatomicalLabelsToFind)), set1));
    
    %Create the set for the selected ROIs
    no = size(rois2add,1);
    cfg.roi = zeros(no,3);
    cfg.labels={};
    cfg.radius = 2;
    roi_num = 334; %start the new roi labels from 334 since Gordon has 333 ROIs
    for i=1:no
        cfg.roi(i,1) = rois2add(i).x;
        cfg.roi(i,2) = rois2add(i).y;
        cfg.roi(i,3) = rois2add(i).z;
        cfg.labels(i,1) = {sprintf('roi-%s',num2str(roi_num))};
        roi_num = roi_num+1;
    end

    cfg.roi = round(cfg.roi);
    new_rois = bramila_makeRoiStruct(cfg);

    % Combine spheres and parcels
    rois_add_no = size(rois2add,1);
    for i=1:rois_add_no
        map = new_rois(i).map;
        map_voxels = size(map,1);
        value = 333+i;
        for j=1:map_voxels
            gordon_nii.img(map(j,1),map(j,2),map(j,3))=value;
        end
    end

    save_nii(gordon_nii, '/m/cs/scratch/networks-pm/atlas/300_ROI_Set/seitzman_set2.nii')

end
