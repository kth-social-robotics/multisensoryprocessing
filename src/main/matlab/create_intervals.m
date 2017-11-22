function [starts, ends, cnt] = create_intervals(IDX, maxdiff)
    % check if is in row or column format
    [n,m] = size(IDX);
    if n>0 && m>n
        % transpose to column format
        IDX=IDX';        
    end
    if maxdiff<1
        disp('error maxdiff ahould be >=1');
    end
    if (size(IDX,1) == 0)
        starts = [];
        ends = [];
        cnt = [];
        return
    end
    dIDX=diff(IDX);
    I = dIDX <= maxdiff;
    E = [1;find(~I)+1];
    starts = IDX(E);
    E2 = E-1;
    ends = [IDX(E2(2:end));IDX(end)];
    cnt = diff([E;length(IDX)+1]);
        
end

