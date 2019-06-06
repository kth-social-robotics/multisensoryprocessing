% ASSIGN THE CORRECT VALUES OF THE MARKERS FOR THE GLASSES AND HANDS
% ASSIGN OBJECTS

function [data] = gazehits(jsonfile, targets_num)
% Parses processed json file and reproduces gaze hits and angles

% Define a threshold around head mid point (20cm)
head_radius = 0.2;

% Define a threshold around the object (10cm) - Gaze
object_radius = 0.1;

% Define a threshold around the object (15cm) - Pointing
pobject_radius = 0.15;

% Check if gaze intersects with human or with object
% First make all fields NULL
% Gaze Targets
mocapfield{1} = {''}; % P1

% Angles to targets
mocapfield{4} = zeros(targets_num + 2); % P1

% Pointing Targets labels and angles for P1
mocapfield{7} = {''}; % Label (both hands)
mocapfield{8} = {''}; % Angle HL
mocapfield{9} = {''}; % Angle HR

% Head Targets labels and angles
mocapfield{13} = {''}; % Label P1
mocapfield{16} = {''}; % Angle P1

% Initialise gaze hits
gaze_hits_fp1 = 0;
gaze_hits_cp1 = 0;

% Check that tobii glasses 1 exist
if isfield(jsonfile, 'mocap_glasses1')
    % Get P1 glasses position (LEFT AND RIGHT MARKERS)
    gp1x = (jsonfile.mocap_glasses1.marker3.x + jsonfile.mocap_glasses1.marker2.x) / 2;
    gp1y = (jsonfile.mocap_glasses1.marker3.y + jsonfile.mocap_glasses1.marker2.y) / 2;
    gp1z = (jsonfile.mocap_glasses1.marker3.z + jsonfile.mocap_glasses1.marker2.z) / 2;
    glassesp1 = [gp1x, gp1z, gp1y];
end

if isfield(jsonfile, 'tobii_glasses1')
    if isfield(jsonfile.tobii_glasses1, 'gp3_3d')
        % Get P1 gaze position
        gpp1x = jsonfile.tobii_glasses1.gp3_3d.x;
        gpp1y = jsonfile.tobii_glasses1.gp3_3d.y;
        gpp1z = jsonfile.tobii_glasses1.gp3_3d.z;

        % Get gaze vectors
        gaze_vecp1 = [gpp1x, gpp1z, gpp1y];
    end
    
    if isfield(jsonfile.tobii_glasses1, 'headpose')
        % Get P1 head position
        ghp1x = jsonfile.tobii_glasses1.headpose.x;
        ghp1y = jsonfile.tobii_glasses1.headpose.y;
        ghp1z = jsonfile.tobii_glasses1.headpose.z;

        % Get head vectors
        head_vecp1 = [ghp1x, ghp1z, ghp1y];
    end
end

% Hands 1L (get back marker for center and front marker for 'gp3'
if isfield(jsonfile, 'mocap_hand1l')
    % Get back marker position
    hp1lx = jsonfile.mocap_hand1l.marker4.x;
    hp1ly = jsonfile.mocap_hand1l.marker4.y;
    hp1lz = jsonfile.mocap_hand1l.marker4.z;
    handlp1 = [hp1lx, hp1lz, hp1ly];

    % Get front marker position
    hpp1lx = jsonfile.mocap_hand1l.marker1.x;
    hpp1ly = jsonfile.mocap_hand1l.marker1.y;
    hpp1lz = jsonfile.mocap_hand1l.marker1.z;
    pointl_vecp1 = [hpp1lx, hpp1lz, hpp1ly];
end

% Hands 1R (get back marker for center and front marker for 'gp3'
if isfield(jsonfile, 'mocap_hand1r')
    % Get back marker position
    hp1rx = jsonfile.mocap_hand1r.marker4.x;
    hp1ry = jsonfile.mocap_hand1r.marker4.y;
    hp1rz = jsonfile.mocap_hand1r.marker4.z;
    handrp1 = [hp1rx, hp1rz, hp1ry];

    % Get front marker position
    hpp1rx = jsonfile.mocap_hand1r.marker2.x;
    hpp1ry = jsonfile.mocap_hand1r.marker2.y;
    hpp1rz = jsonfile.mocap_hand1r.marker2.z;
    pointr_vecp1 = [hpp1rx, hpp1rz, hpp1ry];
end

% Get furhat and calibration and screen
% Get furhat position
if isfield(jsonfile, 'mocap_furhat')
    fx = jsonfile.mocap_furhat.position.x;
    fy = jsonfile.mocap_furhat.position.y + 0.15; % Add 15cm to furhat
    fz = jsonfile.mocap_furhat.position.z;
    furhat = [fx, fz, fy];
end

% Get calibration position
if isfield(jsonfile, 'mocap_calibration')
    cx = jsonfile.mocap_calibration.position.x;
    cy = jsonfile.mocap_calibration.position.y;
    cz = jsonfile.mocap_calibration.position.z;
    calibration = [cx, cz, cy];
end

% Get objects
% Get object 1 position
if isfield(jsonfile, 'mocap_target1')
    o1x = jsonfile.mocap_target1.position.x;
    o1y = jsonfile.mocap_target1.position.y;
    o1z = jsonfile.mocap_target1.position.z;
    object{1} = [o1x, o1z, o1y];
end

% % Get object 2 position
% if isfield(jsonfile, 'mocap_target2')
%     o2x = jsonfile.mocap_target2.position.x;
%     o2y = jsonfile.mocap_target2.position.y;
%     o2z = jsonfile.mocap_target2.position.z;
%     object{2} = [o2x, o2z, o2y];
% end
% 
% % Get object 3 position
% if isfield(jsonfile, 'mocap_target3')
%     o3x = jsonfile.mocap_target3.position.x;
%     o3y = jsonfile.mocap_target3.position.y;
%     o3z = jsonfile.mocap_target3.position.z;
%     object{3} = [o3x, o3z, o3y];
% end
% 
% % Get object 4 position
% if isfield(jsonfile, 'mocap_target4')
%     o4x = jsonfile.mocap_target4.position.x;
%     o4y = jsonfile.mocap_target4.position.y;
%     o4z = jsonfile.mocap_target4.position.z;
%     object{4} = [o4x, o4z, o4y];
% end
% 
% % Get object 5 position
% if isfield(jsonfile, 'mocap_target5')
%     o5x = jsonfile.mocap_target5.position.x;
%     o5y = jsonfile.mocap_target5.position.y;
%     o5z = jsonfile.mocap_target5.position.z;
%     object{5} = [o5x, o5z, o5y];
% end
% 
% % Get object 6 position
% if isfield(jsonfile, 'mocap_target6')
%     o6x = jsonfile.mocap_target6.position.x;
%     o6y = jsonfile.mocap_target6.position.y;
%     o6z = jsonfile.mocap_target6.position.z;
%     object{6} = [o6x, o6z, o6y];
% end
% 
% % Get object 7 position
% if isfield(jsonfile, 'mocap_target7')
%     o7x = jsonfile.mocap_target7.position.x;
%     o7y = jsonfile.mocap_target7.position.y;
%     o7z = jsonfile.mocap_target7.position.z;
%     object{7} = [o7x, o7z, o7y];
% end
% 
% % Get object 8 position
% if isfield(jsonfile, 'mocap_target8')
%     o8x = jsonfile.mocap_target8.position.x;
%     o8y = jsonfile.mocap_target8.position.y;
%     o8z = jsonfile.mocap_target8.position.z;
%     object{8} = [o8x, o8z, o8y];
% end
% 
% % Get object 9 position
% if isfield(jsonfile, 'mocap_target9')
%     o9x = jsonfile.mocap_target9.position.x;
%     o9y = jsonfile.mocap_target9.position.y;
%     o9z = jsonfile.mocap_target9.position.z;
%     object{9} = [o9x, o9z, o9y];
% end
% 
% % Get object 10 position
% if isfield(jsonfile, 'mocap_target10')
%     o10x = jsonfile.mocap_target10.position.x;
%     o10y = jsonfile.mocap_target10.position.y;
%     o10z = jsonfile.mocap_target10.position.z;
%     object{10} = [o10x, o10z, o10y];
% end
% 
% % Get object 11 position
% if isfield(jsonfile, 'mocap_target11')
%     o11x = jsonfile.mocap_target11.position.x;
%     o11y = jsonfile.mocap_target11.position.y;
%     o11z = jsonfile.mocap_target11.position.z;
%     object{11} = [o11x, o11z, o11y];
% end
% 
% % Get object 12 position
% if isfield(jsonfile, 'mocap_target12')
%     o12x = jsonfile.mocap_target12.position.x;
%     o12y = jsonfile.mocap_target12.position.y;
%     o12z = jsonfile.mocap_target12.position.z;
%     object{12} = [o12x, o12z, o12y];
% end
% 
% % Get object 13 position
% if isfield(jsonfile, 'mocap_target13')
%     o13x = jsonfile.mocap_target13.position.x;
%     o13y = jsonfile.mocap_target13.position.y;
%     o13z = jsonfile.mocap_target13.position.z;
%     object{13} = [o13x, o13z, o13y];
% end
% 
% % Get object 14 position
% if isfield(jsonfile, 'mocap_target14')
%     o14x = jsonfile.mocap_target14.position.x;
%     o14y = jsonfile.mocap_target14.position.y;
%     o14z = jsonfile.mocap_target14.position.z;
%     object{14} = [o14x, o14z, o14y];
% end

% P1
if isfield(jsonfile, 'tobii_glasses1') & isfield(jsonfile, 'mocap_glasses1')
    % Calculate hits for P1 to Furhat
    if isfield(jsonfile, 'mocap_furhat')
        dist_fp1 = calc_norm(furhat-glassesp1);
        collision_ang_fp1 = atan(object_radius./dist_fp1);
        gaze_ang_fp1 = calc_angle(gaze_vecp1-glassesp1, furhat-glassesp1);
        gaze_hits_fp1 = gaze_ang_fp1 <= collision_ang_fp1;
    end

    % Calculate hits for P1 to calibration
    if isfield(jsonfile, 'mocap_calibration')
        dist_cp1 = calc_norm(calibration-glassesp1);
        collision_ang_cp1 = atan(object_radius./dist_cp1);
        gaze_ang_cp1 = calc_angle(gaze_vecp1-glassesp1, calibration-glassesp1);
        gaze_hits_cp1 = gaze_ang_cp1 <= collision_ang_cp1;
    end
    
    % Write furhat and calibration values for P1
    if gaze_hits_fp1 == 1
        mocapfield{1} = 'Furhat';
    end
    if gaze_hits_cp1 == 1
        mocapfield{1} = 'Calibration';
    end

    % Calculate hits for P1 to Objects
    %for i = 1:14
    i = 1; % REMOVE IF MORE THAN 1 OBJECTS
    if isfield(jsonfile, strcat('mocap_target', int2str(i)))
        dist_op1{i} = calc_norm(object{i}-glassesp1);
        collision_ang_op1{i} = atan(object_radius./dist_op1{i});
        gaze_ang_op1{i} = calc_angle(gaze_vecp1-glassesp1, object{i}-glassesp1);
        gaze_hits_op1{i} = gaze_ang_op1{i} <= collision_ang_op1{i};

        if gaze_hits_op1{i} == 1
            mocapfield{1} = strcat('T', int2str(i));
        end
    end
    %end
    
    % Calculate head hits for P1 to Objects
    %for i = 1:14
    i = 1; % REMOVE IF MORE THAN 1 OBJECTS
    if isfield(jsonfile, strcat('mocap_target', int2str(i)))
        hdist_op1{i} = calc_norm(object{i}-glassesp1);
        hcollision_ang_op1{i} = atan(object_radius./hdist_op1{i});
        head_ang_op1{i} = calc_angle(head_vecp1-glassesp1, object{i}-glassesp1);
        head_hits_op1{i} = head_ang_op1{i} <= hcollision_ang_op1{i};

        if head_hits_op1{i} == 1
            mocapfield{13} = strcat('T', int2str(i));
        end
    end
    %end

    % Pointing HL
    % Calculate pointing hits for P1L to Objects
    %for i = 1:14
    i = 1; % REMOVE IF MORE THAN 1 OBJECTS
    if isfield(jsonfile, strcat('mocap_target', int2str(i)))
        pldist_op1{i} = calc_norm(object{i}-handlp1);
        plcollision_ang_op1{i} = atan(pobject_radius./pldist_op1{i});
        pointl_ang_op1{i} = calc_angle(pointl_vecp1-handlp1, object{i}-handlp1);
        pointl_hits_op1{i} = pointl_ang_op1{i} <= plcollision_ang_op1{i};

        if pointl_hits_op1{i} == 1
            mocapfield{7} = strcat('T', int2str(i));
        end
    end
    %end

    % Pointing HR
    % Calculate pointing hits for P1R to Objects
    %for i = 1:14
    i = 1; % REMOVE IF MORE THAN 1 OBJECTS
    if isfield(jsonfile, strcat('mocap_target', int2str(i)))
        prdist_op1{i} = calc_norm(object{i}-handrp1);
        prcollision_ang_op1{i} = atan(pobject_radius./prdist_op1{i});
        pointr_ang_op1{i} = calc_angle(pointr_vecp1-handrp1, object{i}-handrp1);
        pointr_hits_op1{i} = pointr_ang_op1{i} <= prcollision_ang_op1{i};

        if pointr_hits_op1{i} == 1
            mocapfield{7} = strcat('T', int2str(i));
        end
    end
    %end
    
    % Export gaze and pointing angles (revert to probability)
    mocapfield{4} = {};
    mocapfield{8} = {};
    mocapfield{9} = {};
    mocapfield{16} = {};

    %for i = 1:14
    i = 1; % REMOVE IF MORE THAN 1 OBJECTS
    mocapfield{4} = [mocapfield{4}, (-gaze_ang_op1{i} / pi) + 1];
    mocapfield{8} = [mocapfield{8}, (-pointl_ang_op1{i} / pi) + 1];
    mocapfield{9} = [mocapfield{9}, (-pointr_ang_op1{i} / pi) + 1];
    mocapfield{16} = [mocapfield{16}, (-head_ang_op1{i} / pi) + 1];
    %end
end

data = mocapfield;
