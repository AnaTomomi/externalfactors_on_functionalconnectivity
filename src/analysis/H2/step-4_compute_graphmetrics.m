%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script computes the global efficiency and participation coefficient%
% according to the Seitzman et al. (2020) atlases.                        %
% Make sure to compute the information for the group atlas first!!!       %
%                                                                         %
% Author: ana.trianahoyos@aalto.fi                                        %
% Created: 19.10.2022                                                     %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


clear all 
close all
clc

addpath(genpath('/m/cs/scratch/networks-pm/software/BCT'))

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/nback';
strategy = '24HMP-8Phys-4GSR-Spike_HPF';
atlas_name = 'seitzman-set1';
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Load the data
adj =  load(sprintf('%s/%s/reg-adj_%s_%s.mat', path, strategy, strategy, atlas_name));
adj = adj.conn;

%Load the information about the community affiliation vector
atlas_info = readtable(sprintf('%s/group_%s_info.xlsx',path, atlas_name));
if strcmp(atlas_name,'seitzman-set1')
    comm = atlas_info.netWorkbenchLabel;
else
    comm = atlas_info.network;
end

%compute the global efficiency and participation coefficient
n_subs = size(adj,2);
n_rois = size(adj{1,1},1);
eff = zeros(n_subs,1);
pc = zeros(n_subs,n_rois);
for i=1:n_subs
    a = adj{1,i};
    a(a<=0) = 0; %discard negative correlations
    a = a+a'; %make the matrix simmetric
    eff(i,1) = efficiency_wei(a,0); %0 for global efficiency
    pc(i,:) = participation_coef(a,comm,0)'; %participation coefficient for all ROIs 
    disp(i)
end

%Save the data
save(sprintf('%s/%s/global-eff_%s_%s.mat', path,strategy, strategy, atlas_name),"eff")
save(sprintf('%s/%s/parti-coeff_%s_%s.mat', path,strategy, strategy, atlas_name),"pc")