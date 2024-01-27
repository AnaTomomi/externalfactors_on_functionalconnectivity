addpath(genpath('external'))

baseimg=zeros(91,109,91);
cfg.type='MNI';
cfg.coordinates=[0 0 0];
cfg.imgsize=[91 109 91];
[xorig yorig zorig]=bramila_MNI(cfg); 

% sphere is x^2+y^2+z^2=r^2
r=10;
for x=1:91
    for y=1:109
        for z=1:91
            cfg.type='space';
            cfg.coordinates=[x y z];
            cfg.imgsize=[91 109 91];
            [xmm ymm zmm]=bramila_MNI(cfg);
            val=xmm.^2 +ymm.^2 +zmm.^2;
            if(val <= r.^2)
                baseimg(x,y,z)=1;
            end
        end
    end
end

mask=load_nii('MNI152_T1_2mm_brain_mask.nii');
[sphIDsx sphIDsy sphIDsz]=ind2sub(size(baseimg),find(baseimg));
sphIDs=[sphIDsx sphIDsy sphIDsz];

for x=1:91
	disp(num2str(x))
    for y=1:109
        for z=1:91
            %if(mask.img(x,y,z)==1)
                temp=zeros(size(baseimg));
                xd=x-xorig;
                yd=y-yorig;
                zd=z-zorig;
                thissphIDs=[sphIDs(:,1)+repmat(xd,size(sphIDs,1),1) sphIDs(:,2)+repmat(yd,size(sphIDs,1),1) sphIDs(:,3)+repmat(zd,size(sphIDs,1),1)];
                %for tID=1:size(thissphIDs,1)
                %    temp(thissphIDs(tID,1),thissphIDs(tID,2),thissphIDs(tID,3))=1;
                %end
                %error('stop')
                sphout{x,y,z}=thissphIDs;
            %end
        end
    end
end
save('sphoutMAT_v2.mat','sphout','-v7.3');


