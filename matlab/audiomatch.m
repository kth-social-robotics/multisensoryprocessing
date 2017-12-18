function [T, L]=audiomatch2(afile,bfile,nsec, xfile)
% [T, L] = audiomatch2(afile,bfile,xfile,nsec)
%
% Find best alignment between two audio files
%
% afile, bfile:  files (sampling rate: even multiple of 8khz)
% nsec: length of segment to match (longer means more accurate but
% slower)
%
% outputs
% T: time offset between a and b
% L: length of overlapping sound


fs=8000;

% read wavs and resample...

disp('reading file a');
[Ain,fs0]=audioread(afile);
%[Ain,fs0]=wavread(afile);
A=mean(Ain,2);
disp('decimating file a');
A=decimate(A,fs0/fs);

disp('reading file b');
[Bin,fs0]=audioread(bfile);
%[Bin,fs0]=wavread(bfile);
B=mean(Bin,2);
disp('decimating file b');
B=decimate(B,fs0/fs);


% find energy peak in first half of file B
wins = 4;
startfrac = 0.2;
endfrac = 0.5;
disp('looking for suitable section to match');
blen = length(B);
Bmid = B(round(blen*startfrac):round(blen*endfrac));
Eb = decimate(Bmid.^2,(fs*wins));
[m,i]=max(Eb);
t1 = i*wins + blen*startfrac/fs

Bseg = B(round(t1*fs):round((t1+nsec)*fs));
T = amatch(A,Bseg,fs) -t1
T = T(1);

if (T<0)  
  bi = round(-T*fs)   
  A2 = A;
  B2 = B(bi:end);
else
  ai = round(T*fs)   
  A2 = A(ai:end);
  B2 = B;
end

size(A2)
size(B2)
minlen  = min(length(A2),length(B2))
X = [A2(1:minlen) B2(1:minlen)];
L = minlen/fs;

if nargin>3
    audiowrite(xfile,X,fs);
%wavwrite(X,fs,xfile);
    dlmwrite(sprintf('%s.offset',bfile),T);
end
