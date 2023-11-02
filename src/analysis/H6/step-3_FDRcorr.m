%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script corrects the obtained results for multiple comparisons using%
% the Benjamin and Hochberg approach                                      %
%                                                                         %
% Author: ana.trianahoyos@aalto.fi                                        %
% Created: 17.10.2023                                                     %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all
close all
clc

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H6';
strategy = '24HMP-8Phys-Spike_HPF';
atlas_name = 'seitzman-set1';
to_correct = 'parti-coeff'; %'parti-coeff' or 'global-eff'
thres = 0.1;
lags = 16;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

variables = {'total_sleep_duration','awake_time','restless_sleep', 'steps', 'inactive_time'};

filepath = sprintf('%s/%s_%s_%s_thr-%s.mat', path, to_correct, strategy, atlas_name, num2str(thres*100));
data = load(filepath);

%Start the multiple comparison correction
num_fields = numel(fieldnames(data));

%organize the data in a variables, lags, nodes array
org_data = zeros(size(variables,2), lags, num_fields);
for i = 0:(num_fields-1)
    fieldname = strcat('net_', string(i));
    org_data(:, :, i+1) = getfield(data, fieldname);
end

%with lag independence
data_BH = zeros(size(org_data));
for i=1:length(variables)
    for j=1:lags
        pvals = squeeze(org_data(i,j,:));
        qvals_bh =  mafdr(pvals, 'BHFDR', 'True');
        data_BH(i,j,:) = qvals_bh;
    end
end

savefile = sprintf('%s/%s_%s_%s_thr-%s_BHcorrected.mat', path, to_correct, strategy, atlas_name, num2str(thres*100));
save(savefile, 'data_BH')