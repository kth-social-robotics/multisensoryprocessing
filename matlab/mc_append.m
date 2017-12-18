function [D] = mc_append(DATA1, DATA2, idx)
%Adds DATA2 marker data to a the DATA1 dataset
[n,m,p]=size(DATA1);
if (nargin==2)
  idx=p+1;
end
[n2,m2,p2]=size(DATA2);
D=nan(n,m,p+p2);
D(:,:,1:idx-1) = DATA1(:,:,1:idx-1);
D(:,:,idx:(idx+p2-1)) = DATA2;
D(:,:,idx+p2:end) = DATA1(:,:,idx:end);
