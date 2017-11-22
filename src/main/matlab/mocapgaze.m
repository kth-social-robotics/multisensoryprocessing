function [data] = mocapgaze(gp3, pos, quat, rgbMarkers)
% Values
gd1.left = [0, 0, 0];
gd1.right = [0, 0, 0];

tobii_rgbdata1.pos = pos;
tobii_rgbdata1.quat = quat;
tobii_rgbdata1.rgbMarkers = rgbMarkers;
tobii_rgbdata1.rgbMarkernames = ['glasses1_1', 'glasses1_2', 'glasses1_3', 'glasses1_4'];
tobii_rgbdata1.name = ['glasses1'];

% Calculate a transform from rigidbody coordinates to tobii glasses
% coordinates, assuming there are 2 markers on the front, and 2 markers
% at the back
front_left_marker1 = 3;
front_right_marker1 = 4;
back_left_marker1 = 2;
back_right_marker1 = 1;

% Normalise gp3
ggp3 = gp3 * 0.001;

% Clamp the gaze target as this seem to be unreliable
gd1.gp3 = clamp_magnitude(ggp3, 2, Inf);

% Assemble tobii data. Only 3 markers are used, the forth (back right) is
% not necessary as it is only used for robustness. The back left marker is
% positioned always at the same place for all glasses, while the back right
% position varies.
tobii_data1 = assemble_tobii_data(gd1, tobii_rgbdata1, front_left_marker1, front_right_marker1, back_left_marker1);

% Remove nan cases of gp3 and put 0
if (isnan(tobii_data1.gaze3D_w))
    tobii_data1.gaze3D_w = [0, 0, 0];
end

% Trim errors
Pgaze1 = trim_trails(matrix2points([tobii_data1.gazeLeftDir_w, tobii_data1.gazeRightDir_w, tobii_data1.gaze3D_w, tobii_data1.headpose]), 10, 10);

%disp(tobii_data1.gaze3D_w)
% Smooth gaze data. 10 is 200ms.
Pgaze_sm1 = mocap_smooth(Pgaze1, 10, 'moving');
data = Pgaze_sm1;
