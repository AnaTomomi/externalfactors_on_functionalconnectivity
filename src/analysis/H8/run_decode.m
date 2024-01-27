function run_decode(x,winsize,stepsize,prctokeep,folderout)
load sphoutMAT
addpath(genpath('/scratch/work/eglerean/isctest/external'))
mask = load_nii('/scratch/cs/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/movie/group_mask_mult.nii');

N=30;
% let's fix the slide
%for x = 1:91
%x=45;
%x=52;
load ISCout2/memMaps.mat

out=zeros(109,91,30);
T=1059;

for y=1:109
    %y=45;
	%y=21;
    for z=1:91
        
        %z=45;
		%z=38;
		if(mask.img(x,y,z)==0) continue;end
       	disp(num2str([x y z]))
        % get the coordinates to obtain the sphere
        list=sphout{x,y,z};
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
        decVec = decode_success(data,winsize,stepsize,prctokeep);
        out(y,z,:)=decVec;
    end
end
disp(['Saving ' folderout '/' num2str(x) '.mat'])
save([folderout '/' num2str(x) '.mat'],'out','-v7.3')

end
