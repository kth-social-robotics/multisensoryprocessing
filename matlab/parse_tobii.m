function [timestamps, gazedata, syncpulse_ts, video_ts] = parse_tobii(filename)
  fid=fopen(filename)
  C=textscan(fid, '%s');
  fclose(fid);
  
  json_strs = C{1};
  nrows = size(json_strs,1);
  timestamps.left = nan(nrows,1);
  gazedata.left = nan(nrows,3);
  timestamps.right = nan(nrows,1);
  gazedata.right = nan(nrows,3);
  syncpulse_ts = [];
  video_ts = [];

  pc = 0;
  idx_l=1;
  idx_r=1;
  idx_p=1;
  for i = 1:nrows
      curr = floor(100*i/nrows);
      if curr>pc
          disp (sprintf('%u percent done', curr));
          pc=curr;
      end
      v = JSON.parse(json_strs{i});
      if isfield(v,'dir') && v.sig == 1
          syncpulse_ts = [syncpulse_ts; v.ts];
      end
      if isfield(v,'vts')
          video_ts = [video_ts; v.ts];
      end
      if isfield(v,'gp3')
          timestamps.gp3(idx_p)=v.ts;
          gazedata.gp3(idx_p,:) = cell2mat(v.gp3)*0.001;
          idx_p=idx_p+1;
      end
      if isfield(v,'gd')
          if strcmp(v.eye, 'left')
              timestamps.left(idx_l)=v.ts;
              gazedata.left(idx_l,:) = cell2mat(v.gd);
              idx_l=idx_l+1;
          elseif strcmp(v.eye, 'right')
              timestamps.right(idx_r)=v.ts;
              gazedata.right(idx_r,:) = cell2mat(v.gd);
              idx_r=idx_r+1;
          end
      end
  end
timestamps.left = timestamps.left(1:idx_l-1);
timestamps.right = timestamps.right(1:idx_r-1);
gazedata.left = gazedata.left(1:idx_l-1,:);
gazedata.right = gazedata.right(1:idx_r-1,:);

nn=calc_norm(gazedata.left);
bin = nn==0;
gazedata.left(bin,:)=nan(sum(bin),3);

nn=calc_norm(gazedata.right);
bin = nn==0;
gazedata.right(bin,:)=nan(sum(bin),3);

nn=calc_norm(gazedata.gp3);
bin = nn==0;
gazedata.gp3(bin,:)=nan(sum(bin),3);
