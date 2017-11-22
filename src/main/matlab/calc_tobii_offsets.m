function [ posOffset, rotOffset ] = calc_tobii_offsets(front_left_marker, front_right_marker, back_left_marker)
%UNTITLED5 Calculates a transform from rigidbody coordinates to
% tobii glasses coordinates, assuming there are 2 markers on the
% front, centered around the origin of the tobii coordinate system, and 1 marker at the back left brim
%   INPUT: marker positions in the local (rigid body) coordinate system
%   OUTPUT: position and rotation offset 
    % new axis
    xDir = front_left_marker-front_right_marker;
    zDir = front_left_marker-back_left_marker;
    yDir = cross(zDir, xDir);

    % translation and rotation
    posOffset = 0.5*(front_left_marker+front_right_marker);
    rotMtx = calc_rotation_matrix(xDir,yDir);

    % tilt the coordinate system a fixed angle around x for final
    % alignment
    angOffset = 0.40;
    rotOffset = dcm2quat(vrrotvec2mat([-1 0 0 angOffset])*rotMtx');

end
