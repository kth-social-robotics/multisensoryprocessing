function [ Pw ] = local2worldspace(Pl, quat, pos)
%localspace_coords transforms data from world to localspace
%   Detailed explanation goes here
    if size(Pl,1) == 1 && size(quat,1) > 1
        Pl = repmat(Pl, size(quat,1), 1);
    end
    Pw = nan(size(Pl));
    nMarkers = size(Pw,3);
    for j=1:nMarkers
        Pw (:,:,j)= quatrotate(quatinv(quat), Pl(:,:,j)) + pos;
    end
end

