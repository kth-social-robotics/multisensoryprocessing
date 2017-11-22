function mocapwrite_trc(filename, P, L, tstep, isNans2Zeros, stime, etime)
% TRC file format is a bit tricky. For use in Motion Builder
% gaps (nan values) are represented with a non-existing value
% in our previous releases, we used zeros in that case. set 
% isNans2Zeros to 1 if that behaviour is required
  if (nargin == 4)
      isNans2Zeros = 0;
  end
  if (isNans2Zeros)
      P = nans2zeros(P);
  end

  fid=fopen(filename,'w');
  fprintf(fid,'PathFileType,4,(X/Y/Z),C:\r\n');
  fprintf(fid,'DataRate,CameraRate,NumFrames,NumMarkers,Units,OrigDataRate,OrigDataStartFrame,OrigNumFrames,StartTime,EndTime\r\n');
  fps = round(1/tstep);
  nframes = size(P,1);
% nmarkers = size(P,3);
  nmarkers = 0;
  lables = '';
  nUnlabeled = size(P,3);
  for i = 1:length(L)
    str = strtrim(L{i});
    if size(str,2) >0
      if i>1 
          lables = sprintf('%s,,',lables);
      end
      lables = sprintf('%s,%s',lables,str);
      nmarkers = nmarkers+1;
      nUnlabeled = nUnlabeled-1;
    end
  end
  for i = 1:nUnlabeled
      lables = sprintf('%s,*Unnamed_%u',lables,i);
  end
  timestart = stime;
  timeend = etime;
  fprintf(fid,'%u,%u,%u,%u,m,%u,%u,%u,%f,%f\r\n', fps, fps, nframes, size(P,3), fps, 1, nframes, timestart, timeend);
  fprintf(fid,'Frame#,Time');
  fprintf(fid,'%s\r\n',lables);
  fprintf(fid,',,');
  for i = 1:size(P,3)
    fprintf(fid,'X%u,Y%u,Z%u,',i,i,i);
  end
  fprintf(fid,'\r\n\r\n');

  frame = 1:(size(P,1));
  time = tstep*frame;
  
  D = zeros(nframes,2+size(P,2)*size(P,3));

  D(:,1:2) = [frame' time'];
  
  for ch=1:size(P,3)
    D(:,(ch*3):(ch*3+2)) = P(:,:,ch);
  end	    
  
  for row=D'
    fprintf(fid,'%d,',row(1));
    str = sprintf('%f,',row(2:end-1));
    if (isNans2Zeros)
        fprintf(fid, str);
    else
      fprintf(fid, regexprep(str, 'NaN', ''));
    end
    str = sprintf('%f \n',row(end));
    fprintf(fid,regexprep(str, 'NaN', ''));
  end
  
  fclose(fid);
  