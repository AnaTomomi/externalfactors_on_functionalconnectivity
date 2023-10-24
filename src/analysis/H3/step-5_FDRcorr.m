%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script corrects the obtained results for multiple comparisons using%
% the Benjamin and Hochberg approach                                      %
%                                                                         %
% Author: ana.trianahoyos@aalto.fi                                        %
% Created: 19.10.2022                                                     %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all
close all
clc

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Change this only!
path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3';
strategy = '24HMP-8Phys-4GSR-Spike_HPF';
atlas_name = 'seitzman-set2';
atlas_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs';
to_correct = 'reg-links'; %'reg-links' or 'parti-coeff'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if strcmp(atlas_name,'seitzman-set1')
    matrixSize = 130;
else
    matrixSize = 141;
end

filepath = sprintf('%s/%s_%s_%s.csv', path, to_correct, strategy, atlas_name);
data = readtable(filepath);

data = data(~contains(data.Var1, 'Intercept'), :); % Filter out the intercept
data = data(:,[1,3,9]); %select only the needed columns
data.Var1 = regexprep(data.Var1, '\d+$', ''); %set the same variable names for all
totest = unstack(data, 'p_values','Var1'); % Pivot the table

%Start the multiple comparison correction
data_BH = totest;
colNamesToIterate = totest.Properties.VariableNames(2:end);
if strcmp(to_correct,'parti-coeff')
    for colName = colNamesToIterate
        pvals = totest.(colName{1});
        if max(pvals)>1
            fprintf('%s pval over 1', colName{1})
        end
        qvals_bh =  mafdr(pvals, 'BHFDR', 'True');
        if any(qvals_bh<0.05)
            fprintf('result for %s \n',colName{1})
        end
        data_BH.(colName{1}) = qvals_bh;
    end
end

if strcmp(to_correct,'reg-links')
    [idx(:,1),idx(:,2)]= ind2sub([matrixSize, matrixSize], find(triu(ones(matrixSize), 1)==1));
    data_BH.('row') = idx(:,1);
    data_BH.('column') = idx(:,2);

    colNamesToIterate = totest.Properties.VariableNames(2:end);
    for colName = colNamesToIterate
        pvals = totest.(colName{1});
        if max(pvals)>1
            fprintf('%s pval over 1', colName{1})
        end
        qvals_bh =  mafdr(pvals, 'BHFDR', 'True');
        if any(qvals_bh<0.05)
            fprintf('result for %s \n',colName{1})
        end
        data_BH.(colName{1}) = qvals_bh;
    end

    % keep only the preselected ROIs (DMN, fronto-parietal, cingulo opercular)
    atlas_info = readtable(sprintf('%s/group_%s_info.xlsx',atlas_path, atlas_name));
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
    
    %map to original node numbers in the atlas parcellation 
    %(and it works!)
    num_rows_data_BH = height(data_BH);
    for i = 1:num_rows_data_BH
        % Get the current row and column values
        current_row = data_BH.row(i);
        current_column = data_BH.column(i);
        
        % Find the position of the current row and column in the
        % original atlas
        original_index_row = idx(current_row);
        original_index_column = idx(current_column);
        
        % Assign the original indexes back to the data_BH table
        data_BH.row(i) = original_index_row;
        data_BH.column(i) = original_index_column;
    end
end
writetable(data_BH, sprintf('%s/%s_%s_%s_BHcorrected.xlsx', path, to_correct, strategy, atlas_name))