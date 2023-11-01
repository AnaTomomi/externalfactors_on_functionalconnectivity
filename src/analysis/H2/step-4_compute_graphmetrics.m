%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script computes the global efficiency and participation coefficient%
% according to the Seitzman et al. (2020) atlases.                        %
% Make sure to compute the information for the group atlas first!!!       %
%                                                                         %
% Author: ana.trianahoyos@aalto.fi                                        %
% Created: 19.10.2022                                                     %
% Modified: 01.11.2023 FIX: compute for binary, thresholded networks      %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all 
close all
clc

addpath(genpath('/m/cs/scratch/networks-pm/software/BCT'))
addpath(genpath('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/analysis'))

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/nback';
strategy = '24HMP-8Phys-4GSR-Spike_HPF';
atlas_name = 'seitzman-set1';
rho = 0.3;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Load the data
adj =  load(sprintf('%s/%s/reg-adj_%s_%s.mat', path, strategy, strategy, atlas_name));
adj = adj.conn;
n_subs = size(adj,2);
n_rois = size(adj{1,1},1);

% Step 1. Threshold the networks
thr_adj = {};
for j=1:n_subs
    a = adj{1,j};
    a_thr = threshold_network(a,rho); %threshold
    a_thr(a_thr>0)=1; %binarize the network
    thr_adj{1,j} = a_thr;
end

%compute the global efficiency and participation coefficient per network
%(as in Prischet et al 2020)

% Load the information about the community affiliation vector and keep only
% the preselected ROIs (DMN, fronto-parietal, cingulo opercular)
atlas_info = readtable(sprintf('%s/group_%s_info.xlsx',path, atlas_name));
atlas_info.index = (1:height(atlas_info))';
if strcmp(atlas_name,'seitzman-set1')
    % merge somatomotor Lateral and Dorsal into one
    for i = 1:n_rois
        if contains(atlas_info.netName{i}, 'Somatomotor')
            atlas_info.netName{i} = 'Somatomotor';
        end
    end
    networks = {'DefaultMode', 'FrontoParietal','Somatomotor'};
    comm = atlas_info.netWorkbenchLabel;
    comm(comm == 11) = 10; %merging somatomotors
else
    atlas_info = renamevars(atlas_info,"network","netName");
    atlas_info.netName = string(atlas_info.netName);
    % merge somatomotor Lateral and Dorsal into one
    for i = 1:n_rois
        if contains(atlas_info.netName{i}, '11')
            atlas_info.netName{i} = '10';
        end
    end
    networks = {'1', '3', '10'};
    comm = str2double(atlas_info.netName);
end

% compute the participation coefficient for the whole thresholded, binary 
% network 
pc = zeros(n_subs,n_rois);
for i=1:n_subs
    a = thr_adj{1,i};
    pc(i,:) = participation_coef(a,comm,0)'; %participation coefficient for all ROIs 
end

% Step 2: Select the corresponding columns from the pc matrix
net_num = size(networks,2);
effs = zeros(n_subs,net_num);
pcs = zeros(n_subs,net_num);
for net = 1:net_num
    filtered_rows = ismember(atlas_info.netName, {networks{1,net}});
    index_values = atlas_info(filtered_rows,"index").index;
    selected_pc = pc(:, index_values);
    
    % Step 3: Compute the PC mean across columns(nodes)
    pcs(:,net) = mean(selected_pc, 2);

    % Step 4: Compute the global efficiencies per networks
    for i = 1:n_subs
        a = thr_adj{i}(index_values, index_values);
        effs(i,net) = efficiency_bin(a,0); %0 for global efficiency
    end
end

%Save the data
save(sprintf('%s/%s/global-eff_%s_%s_thr-%s.mat', path,strategy, strategy, atlas_name,num2str(rho*100)),"effs")
save(sprintf('%s/%s/parti-coeff_%s_%s_thr-%s.mat', path,strategy, strategy, atlas_name,num2str(rho*100)),"pcs")