function [T,S] = amatch(A,B,fs,varargin)
% T = amatch(A,B,fs)
% Find best match (time alignment) between two sounds. 
% A, B are 1 ch. audio vectors with sampling rate fs
% T is offset in seconds for B relative to A for best match
% [T,S] = amatch(A,B,fs)
% also returns S, the 'matching strength' for the best match
%
% options:
%   'fftsize' - fftlength in samples (32)
%   'winlen'  - spectrogram window length in seconds (0.02)
%   'plot'    - display matching plot (0)

WINLEN = 0.02;
NFFT = 32;
PLOT = 0;

for i=1:2:length(varargin)
    
    if strcmp(varargin{i},'fftsize')
        NFFT = varargin{i+1}
    elseif strcmp(varargin{i},'winlen')
        WINLEN=varargin{i+1}
    elseif strcmp(varargin{i},'plot')
        PLOT=varargin{i+1}
    else
        varargin{i}
        error('unknown option')
    end
end


if length(B) > length(A)
    M = -amatch(B,A,fs,'fftsize',NFFT,'winlen',WINLEN);
    return
end


NW=round(fs*WINLEN);
NOVERLAP=round(NW*0.5);
frameshift = (NW-NOVERLAP)/fs;
disp(sprintf('input a: %f s',length(A)/fs))
disp(sprintf('input b: %f s',length(B)/fs))
eps=1e-3;
SA=log(abs(spectrogram(A,NW,NOVERLAP,NFFT))+eps);
SB=log(abs(spectrogram(B,NW,NOVERLAP,NFFT))+eps);

SA2 = imextendedmax(SA,1);
SB2 = imextendedmax(SB,1);

[nr,nc] = size(SB);

SA2 = [zeros(nr,nc) SA2 zeros(nr,nc)];
offset = nc*frameshift;

f = filter2(SB2,SA2,'valid');
f2 = medfilt1(f,15);
f=f-f2;

if (PLOT)
    hold off
    plot((0:length(f)-1)*frameshift-offset,f)
    xlabel('s');
    hold on
    ax=axis;
    plot([0 0],ax(3:4),'r')
end
[m,mi]=sort(f,'descend');

M=(mi'-1)*frameshift-offset;
prc = prctile(f,[1 10 50 90 100]);

S = (prc(5)-prc(3))/(prc(4)-prc(2))
T=M(1);
