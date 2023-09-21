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
comm = size(adj{1,1},1);
eff = zeros(n_subs,1);
pc = zeros(n_subs,comm);
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