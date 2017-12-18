function [N] = findtrigs(X,fs)

range=max(X)-min(X);
dX=diff(X);

eX=find(abs(dX)>.1*range);
lastt = -1e10;
timeout=fs*.005;
res=[];
sres=[];
zz=[];
for t=eX'
    if (t-lastt)>timeout
        res(end+1)=t;
        % sres(end+1)=sign(X(t+round(fs/48)));
        lastt=t;
%        zz=[zz X(t:t+timeout)];
    end
end

        
N=res/fs;
% S=sres;

   
    