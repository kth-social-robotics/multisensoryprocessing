function [data] = mocapgaze(tobii_device, gp3, pos, quat, rgbMarkers)
if (strcmp(tobii_device, 'tobii_glasses1'))
    % Values
    gd.left = [0, 0, 0];
    gd.right = [0, 0, 0];

    tobii_rgbdata.pos = pos;
    tobii_rgbdata.quat = quat;
    tobii_rgbdata.rgbMarkers = rgbMarkers;
    tobii_rgbdata.rgbMarkernames = ['glasses1_1', 'glasses1_2', 'glasses1_3', 'glasses1_4'];
    tobii_rgbdata.name = ['glasses1'];

    % Calculate a transform from rigidbody coordinates to tobii glasses
    % coordinates, assuming there are 2 markers on the front, and 2 markers
    % at the back
    front_left_marker = 2;
    front_right_marker = 4;
    back_left_marker = 1;
    back_right_marker = 3;
elseif (strcmp(tobii_device, 'tobii_glasses2'))
    % Values
    gd.left = [0, 0, 0];
    gd.right = [0, 0, 0];

    tobii_rgbdata.pos = pos;
    tobii_rgbdata.quat = quat;
    tobii_rgbdata.rgbMarkers = rgbMarkers;
    tobii_rgbdata.rgbMarkernames = ['glasses2_1', 'glasses2_2', 'glasses2_3', 'glasses2_4'];
    tobii_rgbdata.name = ['glasses2'];

    % Calculate a transform from rigidbody coordinates to tobii glasses
    % coordinates, assuming there are 2 markers on the front, and 2 markers
    % at the back
    front_left_marker = 3;
    front_right_marker = 2;
    back_left_marker = 4;
    back_right_marker = 1;
end

% Normalise gp3
ggp3 = gp3 * 0.001;

% Clamp the gaze target as this seem to be unreliable
gd.gp3 = clamp_magnitude(ggp3, 2, Inf);

% Assemble tobii data. Only 3 markers are used, the forth (back right) is
% not necessary as it is only used for robustness. The back left marker is
% positioned always at the same place for all glasses, while the back right
% position varies.
tobii_data = assemble_tobii_data(gd, tobii_rgbdata, front_left_marker, front_right_marker, back_left_marker);

% Remove nan cases of gp3 and put 0
if (isnan(tobii_data.gaze3D_w))
    tobii_data.gaze3D_w = [0, 0, 0];
end

% Trim errors
Pgaze = trim_trails(matrix2points([tobii_data.gazeLeftDir_w, tobii_data.gazeRightDir_w, tobii_data.gaze3D_w, tobii_data.headpose]), 10, 10);

%disp(tobii_data.gaze3D_w)
% Smooth gaze data. 10 is 200ms.
Pgaze_sm = mocap_smooth(Pgaze, 10, 'moving');
data = Pgaze_sm;
