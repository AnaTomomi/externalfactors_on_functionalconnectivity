function decVec = decode_success_par_new(data,winsize,stepsize,prctokeep,seed)
%% test
%close all
%T=969;
%sig=zscore(cumsum(randn(T,18)));
%data=0.5*randn(T,18,32)+repmat(sig,1,1,32);
%winsize=25;
%stepsize=25;
%prctokeep=1;

%
    % data is in format time x space x subjects
    % winsize is a number of length of window
    % step size is the sliding size
    % prctokeep is how many we use in the leave one out
    sz=size(data);
    T=sz(1);
    S=sz(2);
    N=sz(3);
    if prctokeep == 1
        decVec = zeros(N,1); % for each subject, for this voxel
    else
        decVec = zeros(N,100);
    end


    % qc: check that for every space we have data
    for s=1:S
        temp=var(squeeze(data(:,s,:)));
        if(any(temp==0))
			disp('Skipping')
            return 
        end
    end

    % if we are here, we have data for each voxel and for each subject
    parfor n=1:N
		%disp(['Parloop ' num2str(n)])
        % for the subject we are considering, let's separate the subject
        % data from the training data
        datathis=data(:,:,n);
        dataothers=data;
        dataothers(:,:,n)=[];
		Nleft=size(dataothers,3);
		iter=1;
		if(prctokeep < 1)
			iter=100;
			perms=nchoosek([1:Nleft],ceil(Nleft*prctokeep));
			temp=randperm(length(perms));
			perms=perms(temp(1:100),:);
		end
		dectemp=zeros(iter,1);
		for i=1:iter
			if (prctokeep == 1)
				meandataothers=mean(dataothers,3); % average N-1 subjects
			else
				meandataothers=mean(dataothers(:,:,perms(i,:)),3); % average N-1 subjects
			end
			windatathis=[];
			windataothers=[];
			tID=1;
			for t=1:stepsize:T
				if(T-t<winsize)
					continue
				end
				temp=datathis(t:t+winsize-1,:,:);
				temp=temp(:); % get rid of space
				windatathis(:,tID)=temp; % for this time window, we have subejct data
				temp=meandataothers(t:t+winsize-1,:,:);
				temp=temp(:); % get rid of space
				windataothers(:,tID)=temp; % for this time window, we have data for others
				tID=tID+1;
			end
			corrmat=corr([windatathis windataothers]);
			% let's look at the top block for the cross corr
			decodedata=corrmat(1:(tID-1),tID:end);
			dectemp(i) = decode_findbest(decodedata);
		end
		decVec(n,:)=dectemp;
		%disp('debug saving')
  		%save(['debug/' num2str(n) '.mat'],'-v7.3')       
    end
%figure(1)
%stem(decVec)
%hold on
