clear all 
close all
clc

addpath(genpath('/m/cs/scratch/networks-pm/software/BCT'))

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs';
strategy = '24HMP-8Phys-Spike_HPF';
atlas_name = 'seitzman-set2';

adj =  load(sprintf('%s/%s/reg-adj_%s_%s.mat', path, strategy, strategy, atlas_name));
adj = adj.conn;

% keep only the preselected ROIs (DMN, fronto-parietal, cingulo opercular)
atlas_info = readtable(sprintf('%s/group_%s_info.xlsx',path, atlas_name));
atlas_info.index = (1:height(atlas_info))';
if strcmp(atlas_name,'seitzman-set1')
    networks = {'DefaultMode', 'FrontoParietal', 'CinguloOpercular'};
    preselection = ismember(atlas_info.netName, networks);
    atlas_selection = atlas_info(preselection, :);
else
    networks = [1, 3, 9];
    preselection = ismember(atlas_info.network, networks);
    atlas_selection = atlas_info(preselection, :);
end

%select the subnetworks
idx = atlas_selection.index;
sub_adj = cell(size(adj));
for i = 1:length(adj)
    sub_adj{i} = adj{i}(idx, idx);
end

%Put the links into columns
n_subs = length(sub_adj);
n_rois = size(atlas_selection,1);
n_links = (n_rois*(n_rois-1))/2;

links = zeros(n_subs,n_links); 
for i = 1:n_subs
    upper_tri = triu(sub_adj{i}, 1);% Extract upper triangle without the diagonal
    links(i, :) = upper_tri(upper_tri ~= 0)';
end

%Save the data
save(sprintf('%s/%s/reg-links_%s_%s.mat', path,strategy, strategy, atlas_name),"links")