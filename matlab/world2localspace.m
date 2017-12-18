function [ Pl ] = world2localspace(Pw, quat, pos)
%localspace_coords transforms data from world to localspace
%   Detailed explanation goes here
    Pl = nan(size(Pw));
    nMarkers = size(Pw,3);
    for j=1:nMarkers
        Pl (:,:,j)= quatrotate(quat,Pw(:,:,j)-pos);
    end
end

