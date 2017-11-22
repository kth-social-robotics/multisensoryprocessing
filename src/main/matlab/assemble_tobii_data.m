function [tobii_data] = assemble_tobii_data(gaze_data, tobiiRbg, frontLeft, frontRight, backLeft)
%Transforms tobii gaze vector from local (Tobii coordinate system) to world
%coordinate system
%   The method requires a setup with markers attached to the brim of the
%   glasses in the following configuration: Two markers on the upper front 
%   corner of the glasses, centered around the camera + one marker on the
%   back left brim.
% INPUT: 
%   gaze_local - 3D gaze data expressed in the local Tobii coordinate system. Can be 3D fixation points, gaze directions or other 3D data.
%   tobiiRgb - Rigid body data from optitrack system, i.e. position,
%   quaternion and marker data. Note: the data must not have any gaps at
%   the first frame. But I think this is fixed for now.
%   frontLeft, frontRight, backLeft - indices for the markers on the brim
% OUTPUT: tobii data struct containg world position and orientation
% of the tobii glasses coordinate system, as well as gaze data expressed in
% world coordinates.

    % Simple solution to fix the case of gaps on first frame, it just gets
    % the first frame with data
    i = 1;
    while isnan(tobiiRbg.quat(i,:))
        i = i + 1;
    end
    framenum = i;

    % Here it takes the framenum frame (in testrec1 this is 822)
    qq = tobiiRbg.quat(framenum,:);
    pp = tobiiRbg.pos(framenum,:);
    fl = world2localspace(tobiiRbg.rgbMarkers(framenum,:,frontLeft), qq, pp);
    fr = world2localspace(tobiiRbg.rgbMarkers(framenum,:,frontRight), qq, pp);
    bl = world2localspace(tobiiRbg.rgbMarkers(framenum,:,backLeft), qq, pp);

    % Here the camera angle is also defined
    [posOffset, rotOffset] = calc_tobii_offsets(fl, fr, bl);
    tobii_data.pos = local2worldspace(posOffset, tobiiRbg.quat, tobiiRbg.pos);
    tobii_data.quat = quatmultiply(tobiiRbg.quat, rotOffset);

    % Transform gaze and glasses to world space and export
    tobii_data.gaze3D_w = local2worldspace(gaze_data.gp3, tobii_data.quat, tobii_data.pos);
    tobii_data.gazeLeftDir_w = local2worldspace(gaze_data.left, tobii_data.quat, tobii_data.pos);
    tobii_data.gazeRightDir_w = local2worldspace(gaze_data.right, tobii_data.quat, tobii_data.pos);
    
    % Head pose from glasses. Define point 2 meters ahead of the glasses.
    head_pose = [0, 0, 2];
    tobii_data.headpose = local2worldspace(head_pose, tobii_data.quat, tobii_data.pos);
end
