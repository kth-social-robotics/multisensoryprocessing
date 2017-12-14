function [data] = gazehits(jsonfile)
% Parses processed json file and reproduces gaze hits

% Define a threshold around head mid point (20cm)
head_radius = 0.2;

% Define a threshold around the object (10cm)
object_radius = 0.1;

% Check if gaze intersects with human or with object
% First make all fields NULL
mocapfield{1} = {''};

% Check that tobii glasses exist
if isfield(jsonfile, 'tobii_glasses1') & isfield(jsonfile, 'mocap_glasses1') & isfield(jsonfile, 'mocap_target1') & isfield(jsonfile, 'mocap_target2')
    % Get glasses
    % Get P1 glasses position
    glasses_p1_left = jsonfile.mocap_glasses1.marker1;
    glasses_p1_right = jsonfile.mocap_glasses1.marker3;
    gp1x = (jsonfile.mocap_glasses1.marker3.x + jsonfile.mocap_glasses1.marker4.x) / 2;
    gp1y = (jsonfile.mocap_glasses1.marker3.y + jsonfile.mocap_glasses1.marker4.y) / 2;
    gp1z = (jsonfile.mocap_glasses1.marker3.z + jsonfile.mocap_glasses1.marker4.z) / 2;

    % Get gaze
    % Get P1 gaze position
    gpp1x = jsonfile.tobii_glasses1.gp3_3d.x;
    gpp1y = jsonfile.tobii_glasses1.gp3_3d.y;
    gpp1z = jsonfile.tobii_glasses1.gp3_3d.z;

    % Get gaze vectors
    gaze_vecp1 = [gpp1x, gpp1z, gpp1y];

    % Get glasses positions
    glassesp1 = [gp1x, gp1z, gp1y];

    % Get objects
    % Get object 1 position
    o1x = jsonfile.mocap_target1.position.x;
    o1y = jsonfile.mocap_target1.position.y;
    o1z = jsonfile.mocap_target1.position.z;

    % Get object 2 position
    o2x = jsonfile.mocap_target2.position.x;
    o2y = jsonfile.mocap_target2.position.y;
    o2z = jsonfile.mocap_target2.position.z;

    % Get objects positions
    object1 = [o1x, o1z, o1y];
    object2 = [o2x, o2z, o2y];

    % P1
%     % Calculate hits for P1 to P2
%     dist_p2p1 = calc_norm(glassesp2-glassesp1);
%     collision_ang_p2p1 = atan(head_radius./dist_p2p1);
%     gaze_ang_p2p1 = calc_angle(gaze_vecp1-glassesp1, glassesp2-glassesp1);
%     gaze_hits_p2p1 = gaze_ang_p2p1 <= collision_ang_p2p1;
%     
%     % Write human values for P1
%     if gaze_hits_p2p1 == 1
%         mocapfield{i,4} = 'P2';
%     end

    % Calculate hits for P1 to O1
    dist_o1p1 = calc_norm(object1-glassesp1);
    collision_ang_o1p1 = atan(object_radius./dist_o1p1);
    gaze_ang_o1p1 = calc_angle(gaze_vecp1-glassesp1, object1-glassesp1);
    gaze_hits_o1p1 = gaze_ang_o1p1 <= collision_ang_o1p1;

    % Calculate hits for P1 to O2
    dist_o2p1 = calc_norm(object2-glassesp1);
    collision_ang_o2p1 = atan(object_radius./dist_o2p1);
    gaze_ang_o2p1 = calc_angle(gaze_vecp1-glassesp1, object2-glassesp1);
    gaze_hits_o2p1 = gaze_ang_o2p1 <= collision_ang_o2p1;

    % Write object values for P1
    if gaze_hits_o1p1 == 1
        mocapfield{1} = 'O1';
    end
    if gaze_hits_o2p1 == 1
        mocapfield{1} = 'O2';
    end
end

data = mocapfield;
