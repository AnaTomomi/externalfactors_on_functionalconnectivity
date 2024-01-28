function run_decode(x,winsize,stepsize,prctokeep,ISCfile,folderout)
disp('# preparing files')
load sphoutMAT_v2
addpath(genpath('/scratch/work/eglerean/isctest/external'))
mask = load_nii('/scratch/cs/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie/group_mask_mult.nii');

N=30;
% let's fix the slide
%for x = 1:91
%x=45;
%x=52;
%load ISCout2/memMaps.mat
load([ISCfile '/memMaps.mat'])

out=zeros(109,91,30);
T=1059;
disp(['# compute starts for slice x = ' num2str(x)])
for y=1:109
    %y=45;
	%y=21;
	disp(['## y = ' num2str(y)])
    for z=1:91
        %z=45;
		%z=38;
		if(mask.img(x,y,z)==0) continue;end
        % get the coordinates to obtain the sphere
        list=sphout{x,y,z};
		lbefore=size(list);
		% check if any in the sphere is outside the mask
		%if(any(mask.img(sub2ind(size(mask.img),list(:,1),list(:,2),list(:,3))) == 0))
		%	continue;
		%end
		% the previous approach removes too much from the cortex, let's consider a different approach where we keep those coordinates that are in the mask
		inmask=mask.img(sub2ind(size(mask.img),list(:,1),list(:,2),list(:,3))); 
		listtemp=list;
		list=listtemp(find(inmask==1),:); % let's make the list smaller
		lafter=size(list)
		disp(['List of sphere coordinates before masking: ' num2str(lbefore) ' and after: ' num2str(lafter)])
		if (lafter(1)==0)
			continue
		end

       	disp(['### loading data for ' num2str([x y z])])
        tic
        S=size(list,1);
        data=zeros(T,S,N);
        for n=1:N
            subname=['fMRIpreproc' num2str(n)];
            for s=1:S
                thisx=list(s,1);
                thisy=list(s,2);
                thisz=list(s,3);
                
                data(:,s,n)=zscore(double(memMaps.origMap.Session1.(subname).Data(thisx).tyz(:,thisy,thisz)));

            end

        end
		% trim data
		data=data(48:1019,:,:);
		toc
		disp('### decoding')
		tic
        decVec = decode_success_par(data,winsize,stepsize,prctokeep);
        out(y,z,:)=decVec;
		toc
    end
end
disp(['# Saving ' folderout '/' num2str(x) '.mat'])
save([folderout '/' num2str(x) '.mat'],'out','-v7.3')

end
