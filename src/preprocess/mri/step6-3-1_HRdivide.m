%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script breaks the BIOPAC full session into the number of runs/tasks%
% that it has. For example, if there have been two runs in one scanner    % 
% session.                                                                % 
%                                                                         %
%Author: ana.trianahoyos@aalto.fi                                         %
%created: 02.03.2021                                                      %
%modified:07.09.2021 include naming structure similar to bids             %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all
close all
clc

drifterpath = '/m/cs/archive/networks-pm/mri/20230206';
sub = 'sub-07';
savepath = sprintf('/m/cs/project/networks-pm/mri/fast_prepro_bids/%s', sub);
task = {'pvt', 'resting', 'movie', 'nback'}; %Tasks in the order they were taken in the scanner
day = '037';

%%%%%%%%% Do not modify from here on %%%%%%%%%%%%%%%%
drifterfile = sprintf('%s/sub-01_day-%s_device-biopac.mat',drifterpath,day);

if ~isfile(drifterfile)
    error('File does not exist. Please check the folder and file')
end

%refdata
refdata=load(drifterfile);
data = refdata.data; 

%plot the data to see what it looks like
temp=refdata.data(:,7);
dtemp=diff(temp);
unique(diff(find(dtemp==5)))
plot(temp)

%divide the intervals
interval_no = size(task,2);
for i=1:interval_no
    ids = find(temp==5);
    d = diff(find(temp==5)); %find the indices where there is been an interruption
    if i<interval_no
        inter_end = ids(find(d>10000,1,'first'));
    else
        inter_end = find(temp==5,1,'last');
    end
    inter_init = find(temp, 1, 'first');
    b = data(inter_init:inter_end,:);
    temp = temp(inter_end+1:end);
    data = data(inter_end+1:end,:);
    
    savefile = sprintf('%s/func/%s_task-%s_device-biopac.mat',savepath, sub, task{i});
    save(savefile, 'b');
end
