clear all 
close all
addpath(genpath('/m/nbe/scratch/braindata/eglerean/narrative/isctoolbox2'))


clabels={
 'movGSR6mm'
 'mov'
 'movGSR'
 'mov6mm'
}

for c=1:2
disp(['subjects' num2str(c) '.m'])
run(['subjects' num2str(c) '.m'])

for s=1:length(subjs)
	subjects_isc{1,s}=subjs{s};
end



outfolder=['/m/triton/scratch/work/eglerean/isctest/ISCout' num2str(c) '/'];

load('demoISCParams.mat')
Params.PublicParams.removeMemmaps=0;
Params.PublicParams.dataDescription=clabels{c+1};
Params.PublicParams.dataDestination=outfolder;
Params.PublicParams.subjectSource=subjects_isc;
Params.PublicParams.dataSize=[91 109 91 1059];
Params.PublicParams.calcStats=1;
Params.PublicParams.samplingFrequency=1/0.5940;
Params.PrivateParams.subjectDestination= [outfolder 'fMRIpreprocessed/'];
Params.PrivateParams.subjectFiltDestination= [outfolder 'fMRIfiltered/'];
Params.PrivateParams.resultsDestination= [outfolder 'results/'];
Params.PrivateParams.statsDestination= [outfolder 'stats/'];
Params.PrivateParams.PFDestination= [outfolder 'PF/'];
Params.PrivateParams.PFsessionDestination= [outfolder 'PFsession/'];
Params.PrivateParams.withinDestination= [outfolder 'within/'];
Params.PrivateParams.phaseDifDestination= [outfolder 'phase/'];
Params.PrivateParams.dataSize=[91 109 91 1059];
Params.PrivateParams.nrSubjects=length(subjs);
runAnalysis(Params)
clear Params
end
