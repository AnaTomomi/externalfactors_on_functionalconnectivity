roifile="/scratch/cs/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie/group_seitzman-set1_info.xlsx";
%roifile="\cs\networks-pm\effects_externalfactors_on_functionalconnectivity\data\mri\conn_matrix\movie\group_seitzman-set1_info.xlsx";
roitable=readtable(roifile);

roidata=table2array(roitable(:,1:4));
rois_to_run=[98 195 204];

xyz=[];
for r=1:size(roidata,1)
    roi=roidata(r,1);
    if(ismember(roi,rois_to_run))
        xyz=[xyz; round(roidata(r,2:4)/2)*2];
    end
end

cfg.type='MNI';
cfg.coordinates = xyz;
cfg.imgsize = [91 109 91];  
[x,y,z] = bramila_MNI(cfg);
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
