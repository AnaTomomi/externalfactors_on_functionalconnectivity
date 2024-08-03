clear all
close all

HPC=0;
% roi definition file
if (HPC==1)
    roifile="/scratch/cs/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie/group_seitzman-set1_info.xlsx";
else
    % working on local computer
    roifile="\cs\networks-pm\effects_externalfactors_on_functionalconnectivity\data\mri\conn_matrix\movie\group_seitzman-set1_info.xlsx";
end

roitable=readtable(roifile);
roidata=table2array(roitable(:,1:4));
rois_to_run=[98 195 204];
% get xyz coordinates of the centroid of the three chosen ROIs
xyz=[];
labels={};
for r=1:size(roidata,1)
    roi=roidata(r,1);
    if(ismember(roi,rois_to_run))
        labels=[labels; roitable.Power{r}];
        xyz=[xyz; round(roidata(r,2:4)/2)*2]; % make sure it's in 2mm space
    end
end

% convert MNI to volume indexes
cfg.type='MNI';
cfg.coordinates = xyz;
cfg.imgsize = [91 109 91];  
[x,y,z] = bramila_MNI(cfg);

%% compute the leave 20% out for the chosen ROIs
winsize=25;
stepsize=1;
prctokeep=0.8;
ISCfile='ISCout1';
folderoutpre='rois/roi';
for r=1:3
    folderout=[folderoutpre num2str(rois_to_run(r))];
	disp(folderout)
    mkdir(folderout)
    run_decode_xyz([x(r) y(r) z(r)],winsize,stepsize,prctokeep,ISCfile,folderout)
end

%% plot the result and compare it with leave one out approach
nii=load_nii('niis/decoder_24HMP-8Phys-Spike_HPF_TRw25_step-1_subjects-1.nii');

%%
close all
for r=1:3
    datal20o=load(['rois/roi' num2str(rois_to_run(r)) '/' num2str(x(r)) '_' num2str(y(r)) '_' num2str(z(r)) '_0.8.mat' ]);
    datal1o=squeeze(nii.img(x(r),y(r),z(r),:));
    subplot(3,1,r)
    h=boxchart(datal20o.decVec');
    set(h,'MarkerSize',2)
    set(h,'WhiskerLineColor',3*[.25 .25 .25])
    hold on
    plot(datal1o,'ok-','MarkerFaceColor',[0 0 0],'MarkerSize',4)
    med=median(datal20o.decVec')';
    plot(med,'or-','MarkerFaceColor','red','MarkerSize',4)
    [rrr ppp]=corr(med,datal1o);
    %axis([0.5 30.5 0 0.1])
    title(['ROI ' num2str(rois_to_run(r)) ' ' labels{r} ' (MNI: ' num2str(xyz(r,1)) ',' num2str(xyz(r,2)) ',' num2str(xyz(r,3)) '); Corr(loo,median) = ' num2str(rrr,2) ' (p = ' num2str(ppp,2) ')' ])
    ylabel('Decoder accuracy')
    
        xlabel('Sessions')
    
end



