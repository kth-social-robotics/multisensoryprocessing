function [DATA,L,types,t]=mocapread_csv2matrix(filename)
    % reads mocap data in trc format
    % P is a [N x 3 x M] matrix where N is number of frames and M is number of markers
    % L is a string array of labels for the M markers
    % H is a cell array containing the full header (6 lines)
    fid=fopen(filename);
    if (fid<0) 
    disp(sprintf('Could not open file: %s', filename));
    end
    
    H1=textscan(fid,'%s',7,'delimiter','\n','whitespace','');%,'bufsize',16000);
    H=H1{1};

    nn=textscan(H{1},'%s','delimiter',',');
    info = nn{1};
    nframes = str2num(info{12});

    nn=textscan(H{3},'%s','delimiter',',');
    types=nn{1};
    types=types(3:end);
    
    nn=textscan(H{4},'%s','delimiter',',');
    L=nn{1};
    L=L(3:end);
    nColumns = floor(size(L,1));
    
    tmp = textscan(fid,'%s', 'delimiter','\n');%,'bufsize',16000);
    fclose(fid);
    DD = tmp{1};
    if isempty(DD{1})
        DD = DD(2:end);
    end
    t = nan(size(DD,1),1);
    DATA = nan(size(DD,1),nColumns);
    str = '%u%f';
    for i=1:nColumns
        str = sprintf('%s%s',str,'%f');
    end
    for i = 1:size(DATA,1)
        D = textscan(DD{i}, str, 'delimiter',',', 'emptyvalue',NaN, 'CollectOutput', 1);%,'bufsize',16000);
        t(i) = D{2}(1);
        DATA(i,:) = D{2}(2:end);
    end
    disp('D done')
%     col = 3;
%     for col = 1:nMarkers
%        P(:,k,j) = DDD(2 + (col-1)*3:4 + (col-1)*3, :);
%     end
%     t(i) = D{2};
