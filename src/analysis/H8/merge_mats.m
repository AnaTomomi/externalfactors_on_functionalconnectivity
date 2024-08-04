clear all
close all
addpath(genpath('/scratch/work/eglerean/isctest/external'))

iscfolder={
	'ISCout1'
	'ISCout2'
};

option={
	'decoder_24HMP-8Phys-Spike_HPF_TRw25_step-' %2_subjects-1.nii'
	'decoder_24HMP-8Phys-Spike-4GSR_HPF_TRw25_step-' %2_subjects-1.nii'
};

steps=[1 2 4];
perc=[1];

for c=1:2
	iscdata=iscfolder{c};
	condition=option{c};
	for s=1:length(steps)
		step=steps(s);
		for p=1:length(perc)
			percento=perc(p);
			% initialize output data
			out=zeros(91,109,91,30);
			infoldername=['decode_' iscdata '_25_' num2str(step) '_' num2str(percento)];
			disp(['>> Processing ' infoldername]);
			err=0;
			for n=1:91
				if (isfile([infoldername '/' num2str(n) '.mat']))
					temp=load([infoldername '/' num2str(n) '.mat']);
					out(n,:,:,:)=temp.out;
				else
					disp([infoldername ' is missing file ' num2str(n) ])
					err=1;
				end
			end
			outfile=[condition num2str(step) '_subjects-' num2str(p)];
			if(err == 0)
				niifile=['niis/' outfile '.nii'];
				disp(['>> Storing the nii file in ' niifile])
				refimg=make_nii(out,[2 2 2]);
				save_nii(refimg,niifile)
				nii=bramila_fixOriginator(niifile);
				save_nii(nii,niifile)
			else
				disp(['>> Not storing ' outfile  ' because of missing slices'])
			end
		end
	end
end

