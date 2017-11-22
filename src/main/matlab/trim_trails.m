function [ Pout ] = trim_trails(P, npre, npost)
%   Removes data before and after gaps
%   P - data
Pout=P;
[N,dummy,M] = size(P);
for mi=1:M
    bin = isnan(P(:,1,mi));
    iv = bin2interv(bin);
    for ivi=1:size(iv,1)
        st = iv(ivi,1)-npre;
        if st<1
            st=1;
        end
        en = iv(ivi,2)+npost;
        if en>N
            en=N;
        end
        Pout(st:en,:,mi) = nan(en-st+1,3);
    end
end

