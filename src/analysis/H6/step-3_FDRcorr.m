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

path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H6';
strategy = '24HMP-8Phys-4GSR-Spike_HPF';
atlas_name = 'seitzman-set2';
to_correct = 'parti-coeff'; %'global-eff' or 'parti-coeff'
lags = 16;

variables = {'total_sleep_duration','awake_time','restless_sleep', 'steps', 'inactive_time'};

filepath = sprintf('%s/%s_%s_%s.mat', path, to_correct, strategy, atlas_name);
data = load(filepath);

%Start the multiple comparison correction
if strcmp(to_correct, 'global-eff')
    data_BH = data;
    data_fdr = data;
    data = data.pvals;
    for i=1:size(data,1)
        pvals = data(i,:);
        if max(pvals)>1
            fprintf('%s pval over 1', i)
        end
        qvals_bh =  mafdr(pvals, 'BHFDR', 'True');
        if all(pvals(:))~=pvals(end)
            qvals = mafdr(pvals);
        else
            qvals = qvals_bh;
        end
    
        if any(qvals_bh<0.05)
            fprintf('result for %s \n',variables{i})
        end
    
        qvals_bh(qvals_bh > 0.05) = 0;
        qvals(qvals > 0.05) = 0;
        data_BH(i,:) = qvals_bh;
        data_fdr(i,:) = qvals;
    end
    data_BH = array2table(data_BH');
    data_BH.Properties.VariableNames = variables;
    data_fdr = array2table(data_fdr');
    data_fdr.Properties.VariableNames = variables;
end 

if strcmp(to_correct,'parti-coeff')
    num_fields = numel(fieldnames(data));

    %organize the data in a variables, lags, nodes array
    org_data = zeros(size(variables,2), lags, num_fields);
    for i = 0:(num_fields-1)
        fieldname = strcat('node_', string(i));
        org_data(:, :, i+1) = getfield(data, fieldname);
    end

    %with lag independence
    data_BH = zeros(size(org_data));
    for i=1:length(variables)
        for j=1:lags
            pvals = squeeze(org_data(i,j,:));
            qvals_bh =  mafdr(pvals, 'BHFDR', 'True');
            qvals_bh(qvals_bh > 0.05) = 0;
            data_BH(i,j,:) = qvals_bh;
        end
    end

end

save(sprintf('%s/%s_%s_%s_BHcorrected.xlsx', path, to_correct, strategy, atlas_name), 'data_BH')
