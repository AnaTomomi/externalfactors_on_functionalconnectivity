function detrend(subject, task, strategy)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script applies the required steps for detrending fmri after fmriprep%
% It also regress signals from the BIOPAC after being preprocessed with    %
% drifter.                                                                 % 
%                                                                          %                                                                          %
%Author: ana.trianahoyos@aalto.fi                                          %
%created: 06.02.2023                                                       %
%modified: 07.03.2023                                                      %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath(genpath('/m/cs/scratch/networks-pm/software/bramila/bramila'));
addpath('/m/cs/scratch/networks-pm/software/NIFTI');
addpath(genpath('/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/src/preprocess/mri'));

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Modify this part only
path = '/m/cs/scratch/networks-pm/pm_preprocessed';
savepath = '/m/cs/scratch/networks-pm/pm_denoise';
tr = 0.594;
include_biopac = 1; %0:no, 1:yes

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
fprintf('Starting denoise for %s, %s with strategy %s...\n', subject, task, strategy)
nii_path = sprintf('%s/%s/func/%s_task-%s_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii',path, subject, subject, task);
nii = load_nii(nii_path);
fprintf('Reading nii file %s \n',nii_path)

mask_path = sprintf('%s/%s/func/%s_task-%s_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii', path, subject, subject, task);
mask = load_nii(mask_path);
fprintf('Reading mask file %s \n', mask_path)

confound_path = sprintf('%s/%s/func/%s_task-%s_desc-confounds_timeseries.tsv', path, subject, subject, task);
[confounds, confounds_name, ~] = tsvread(confound_path);
fprintf('Loading confounds %s \n', confound_path)
if include_biopac
    fprintf('loading %s/%s/func/%s_task-%s_device-biopac_downsampledcut.mat',path,subject,subject,task)
    load(sprintf('%s/%s/func/%s_task-%s_device-biopac_downsampledcut.mat',path,subject,subject,task));
end

disp('Choose the confounds... \n')
friston = {'trans_x';'trans_y';'trans_z';'rot_x';'rot_y';'rot_z';'trans_x_derivative1';'trans_y_derivative1';'trans_z_derivative1';'trans_x_power2';...
    'trans_y_power2';'trans_z_power2';'trans_x_derivative1_power2';'trans_y_derivative1_power2';'trans_z_derivative1_power2';'rot_x_derivative1';...
    'rot_y_derivative1';'rot_z_derivative1';'rot_x_power2';'rot_y_power2';'rot_z_power2';'rot_x_derivative1_power2';'rot_y_derivative1_power2';...
    'rot_z_derivative1_power2'};
phys8 = {'csf';'csf_derivative1';'csf_power2';'csf_derivative1_power2';'white_matter';'white_matter_derivative1';'white_matter_power2';'white_matter_derivative1_power2'};
gs = {'global_signal';'global_signal_derivative1';'global_signal_derivative1_power2';'global_signal_power2'};
motion = confounds_name(find(contains(confounds_name,'motion_outlier')))';
ica = confounds_name(find(contains(confounds_name,'aroma_motion')))';
if strcmp(strategy, '24HMP-8Phys')
    con = {friston,phys8};
end
if strcmp(strategy, '24HMP-8Phys-4GSR')
    con = {friston,phys8,gs};
end
if strcmp(strategy, '24HMP-8Phys-Spike')
    con = {friston,phys8,motion};
end
if strcmp(strategy, '24HMP-8Phys-4GSR-Spike')
    con = {friston,phys8,gs,motion};
end
if strcmp(strategy, 'ICA-AROMA-8Phys')
    con = {ica,phys8};
end
if strcmp(strategy, 'ICA-AROMA-8Phys-4GSR')
    con = {ica,phys8,gs};
end

strategy_confounds = cat(1, con{:});

%include the heart and breathing rate
for i=1:size(strategy_confounds,1)
    idx(i) = find(strcmp(confounds_name, strategy_confounds{i}));
end
if include_biopac
    confounds = horzcat(confounds(2:end,idx),downsampled_cut');
else
    confounds = horzcat(confounds(2:end,idx));
end
confounds(isnan(confounds))=0;

% First step: mask the data
disp('Masking the data... \n')

cfg.vol=double(nii.img);
cfg.mask=double(mask.img);

cfg.vol = bramila_maskdata(cfg);

% Second step: detrend the fMRI data
disp('Detrending the image with SG... \n')
cfg.detrend_type='Savitzky-Golay';
cfg.TR=tr;
cfg.write=0;
cfg.outfile=sprintf('%s/%s/%s_task-%s_SGdetrend.nii',savepath, subject, subject, task);
if ~isfile(cfg.outfile)
    cfg.vol = bramila_detrend(cfg);
    nii.hdr.dime.bitpix=64;
    nii.hdr.dime.datatype=64;
    nii.img = double(cfg.vol);
    nii.hdr.dime.cal_max=1000;
    nii.hdr.dime.cal_min=0;
    siz = size(cfg.vol);
    if length(siz)==4
        nii.hdr.dime.dim(1)=4;
        nii.hdr.dime.dim(5)=siz(4);
    end
    if ~exist(sprintf('%s/%s',savepath, subject),'dir')
        mkdir(sprintf('%s/%s',savepath, subject),'dir')
    end
    save_nii(nii,cfg.outfile);
else
    sg = load_nii(cfg.outfile);
    cfg.vol = double(sg.img);
end

% Third step: detrend the confounds
disp('Detrending the confounds...')
tempdata = confounds;
SGlen=round(240/cfg.TR);
if(mod(SGlen,2)==0) SGlen=SGlen-1; end % it needs to be odd
trend=sgolayfilt(tempdata,3,SGlen);
T=size(tempdata,1);
for v=1:size(tempdata,2) % for each confound
    if(var(trend(:,v))==0) continue; end
    if(var(tempdata(:,v))==0) continue; end
    [aa bb res]=regress(tempdata(:,v),[trend(:,v)  ones(T,1)]);
    tempdata(:,v)=res;
end	  
confounds=tempdata;
csvwrite(sprintf('%s/%s/%s_task-%s_detrended-confounds-%s.csv',savepath, subject, subject, task, strategy),confounds)

fprintf('Detrend complete for %s, %s, %s \n', subject, task, strategy)
    
end
