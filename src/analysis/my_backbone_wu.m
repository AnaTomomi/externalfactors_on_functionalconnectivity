function  [CIJtree,CIJclus] = my_backbone_wu(CIJ,avgdeg)
%This is a modification of the original Brain Connectivity Toolbox function
%to allow the computation of only minimum spanning trees with an average
%degree of 0
%BACKBONE_WU        Backbone
%
%   [CIJtree,CIJclus] = backbone_wu(CIJ,avgdeg)
%
%   The network backbone contains the dominant connections in the network
%   and may be used to aid network visualization. This function computes
%   the backbone of a given weighted and undirected connection matrix CIJ, 
%   using a minimum-spanning-tree based algorithm.
%
%   input:      CIJ,    connection/adjacency matrix (weighted, undirected)
%            avgdeg,    desired average degree of backbone
%   output: 
%           CIJtree,    connection matrix of the minimum spanning tree of CIJ
%           CIJclus,    connection matrix of the minimum spanning tree plus
%                       strongest connections up to an average degree 'avgdeg'
%
%   NOTE: nodes with zero strength are discarded.
%   NOTE: CIJclus will have a total average degree exactly equal to 
%         (or very close to) 'avgdeg'.
%   NOTE: 'avgdeg' backfill is handled slightly differently than in Hagmann
%         et al 2008.
%
%   Reference: Hidalgo et al. (2007) Science 317, 482.
%              Hagmann et al. (2008) PLoS Biol
%
%   Olaf Sporns, Indiana University, 2007/2008/2010/2012

N = size(CIJ,1);
CIJtree = zeros(N);

% find strongest edge (note if multiple edges are tied, only use first one)
[i,j,s] = find(max(max(CIJ))==CIJ);
im = [i(1) i(2)];
jm = [j(1) j(2)];

% copy into tree graph
CIJtree(im,jm) = CIJ(im,jm);

in=zeros(1,N);
in(1:2)=im;
%in = im;
out = setdiff(1:N,in);
    

    
% repeat N-2 times
for n=1:N-2
    % find strongest link between 'in' and 'out',ignore tied ranks
    [i,j,s] = find(max(max(CIJ(in(1:1+n),out)))==CIJ(in(1:1+n),out));
    im = in(i(1));
    jm = out(j(1));
    
    % copy into tree graph
    CIJtree(im,jm) = CIJ(im,jm); CIJtree(jm,im) = CIJ(jm,im);
    %in = [in jm];
    in(2+n)=jm;
    %out = setdiff(1:N,in);
    out=1:N;
    out(in(1:(2+n)))=[];
end;


if(avgdeg==0)
	CIJclus=0;
else
    % now add connections back, with the total number of added connections 
    % determined by the desired 'avgdeg'
    CIJnotintree = CIJ.*~CIJtree;
    [a,b] = sort(nonzeros(CIJnotintree),'descend');
    cutoff = avgdeg*N - 2*(N-1);
    thr = a(cutoff);
    CIJclus = CIJtree + CIJnotintree.*(CIJnotintree>=thr);
end
