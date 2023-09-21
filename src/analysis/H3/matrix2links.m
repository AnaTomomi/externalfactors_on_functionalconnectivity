clear all 
close all
clc

addpath(genpath('/m/cs/scratch/networks-pm/software/BCT'))

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs';
strategy = '24HMP-8Phys-Spike_HPF';
atlas_name = 'seitzman-set1';

adj =  load(sprintf('%s/%s/reg-adj_%s_%s.mat', path, strategy, strategy, atlas_name));
adj = adj.conn;

n_subs = size(adj,2);
n_rois = size(adj{1,1},1);
n_links = (n_rois*(n_rois-1))/2;
links = zeros(n_subs,n_links);
for i=1:n_subs
    mat = adj{1,i};
    links(i,:) = nonzeros(triu(mat));
end

%Save the data
save(sprintf('%s/%s/global-eff_%s_%s.mat', path,strategy, strategy, atlas_name),"eff")
save(sprintf('%s/%s/parti-coeff_%s_%s.mat', path,strategy, strategy, atlas_name),"pc")