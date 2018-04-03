% ASSIGN THE CORRECT VALUES OF THE MARKERS FOR THE GLASSES AND HANDS
% ASSIGN OBJECTS

function [data] = gazehits(jsonfile, agent, glasses_num, gloves_num, targets_num, tables_num)
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
mocapfield{2} = {''}; % P2
mocapfield{3} = {''}; % P3

% Table positions or angles
% if strcmp(agent, 'yumi')
%     mocapfield{3} = [0, 0, 0]; % P1
%     mocapfield{4} = [0, 0, 0]; % P2
% elseif strcmp(agent, 'furhat')
% Angles to targets
mocapfield{4} = zeros(targets_num); % P1
mocapfield{5} = zeros(targets_num); % P2
mocapfield{6} = zeros(targets_num); % P3
%end

% Pointing Targets labels and angles for P1
mocapfield{7} = {''}; % Label (both hands)
mocapfield{8} = {''}; % Angle HL
mocapfield{9} = {''}; % Angle HR

% Pointing Targets labels and angles for P2
mocapfield{10} = {''}; % Label (both hands)
mocapfield{11} = {''}; % Angle HL
mocapfield{12} = {''}; % Angle HR

% Head Targets labels and angles
mocapfield{13} = {''}; % Label P1
mocapfield{14} = {''}; % Label P2
mocapfield{15} = {''}; % Label P3
mocapfield{16} = {''}; % Angle P1
mocapfield{17} = {''}; % Angle P2
mocapfield{18} = {''}; % Angle P3

% Initialise gaze hits
gaze_hits_p2p1 = 0;
gaze_hits_p3p1 = 0;
gaze_hits_fp1 = 0;
gaze_hits_cp1 = 0;
gaze_hits_sp1 = 0;
gaze_hits_p1p2 = 0;
gaze_hits_p3p2 = 0;
gaze_hits_fp2 = 0;
gaze_hits_cp2 = 0;
gaze_hits_sp2 = 0;
gaze_hits_p1p3 = 0;
gaze_hits_p2p3 = 0;
gaze_hits_fp3 = 0;
gaze_hits_cp3 = 0;
gaze_hits_sp3 = 0;

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

if isfield(jsonfile, 'mocap_glasses2')
    % Get P2 glasses position (LEFT AND RIGHT MARKERS)
    gp2x = (jsonfile.mocap_glasses2.marker1.x + jsonfile.mocap_glasses2.marker4.x) / 2;
    gp2y = (jsonfile.mocap_glasses2.marker1.y + jsonfile.mocap_glasses2.marker4.y) / 2;
    gp2z = (jsonfile.mocap_glasses2.marker1.z + jsonfile.mocap_glasses2.marker4.z) / 2;
    glassesp2 = [gp2x, gp2z, gp2y];
end

if isfield(jsonfile, 'tobii_glasses2')
    if isfield(jsonfile.tobii_glasses2, 'gp3_3d')
        % Get P2 gaze position
        gpp2x = jsonfile.tobii_glasses2.gp3_3d.x;
        gpp2y = jsonfile.tobii_glasses2.gp3_3d.y;
        gpp2z = jsonfile.tobii_glasses2.gp3_3d.z;

        % Get gaze vectors
        gaze_vecp2 = [gpp2x, gpp2z, gpp2y];
    end
    
    if isfield(jsonfile.tobii_glasses2, 'headpose')
        % Get P2 head position
        ghp2x = jsonfile.tobii_glasses2.headpose.x;
        ghp2y = jsonfile.tobii_glasses2.headpose.y;
        ghp2z = jsonfile.tobii_glasses2.headpose.z;

        % Get head vectors
        head_vecp2 = [ghp2x, ghp2z, ghp2y];
    end
end

if isfield(jsonfile, 'mocap_glasses3')
    % Get P3 glasses position (LEFT AND RIGHT MARKERS)
    gp3x = (jsonfile.mocap_glasses3.marker3.x + jsonfile.mocap_glasses3.marker2.x) / 2;
    gp3y = (jsonfile.mocap_glasses3.marker3.y + jsonfile.mocap_glasses3.marker2.y) / 2;
    gp3z = (jsonfile.mocap_glasses3.marker3.z + jsonfile.mocap_glasses3.marker2.z) / 2;
    glassesp3 = [gp3x, gp3z, gp3y];
end

if isfield(jsonfile, 'tobii_glasses3')
    if isfield(jsonfile.tobii_glasses3, 'gp3_3d')
        % Get P3 gaze position
        gpp3x = jsonfile.tobii_glasses3.gp3_3d.x;
        gpp3y = jsonfile.tobii_glasses3.gp3_3d.y;
        gpp3z = jsonfile.tobii_glasses3.gp3_3d.z;

        % Get gaze vectors
        gaze_vecp3 = [gpp3x, gpp3z, gpp3y];
    end
    
    if isfield(jsonfile.tobii_glasses3, 'headpose')
        % Get P3 head position
        ghp3x = jsonfile.tobii_glasses3.headpose.x;
        ghp3y = jsonfile.tobii_glasses3.headpose.y;
        ghp3z = jsonfile.tobii_glasses3.headpose.z;

        % Get head vectors
        head_vecp3 = [ghp3x, ghp3z, ghp3y];
    end
end

% Hands 1L (get back marker for center and front marker for 'gp3'
if isfield(jsonfile, 'mocap_hand1l')
    % Get back marker position
    hp1lx = jsonfile.mocap_hand1l.marker3.x;
    hp1ly = jsonfile.mocap_hand1l.marker3.y;
    hp1lz = jsonfile.mocap_hand1l.marker3.z;
    handlp1 = [hp1lx, hp1lz, hp1ly];

    % Get front marker position
    hpp1lx = jsonfile.mocap_hand1l.marker4.x;
    hpp1ly = jsonfile.mocap_hand1l.marker4.y;
    hpp1lz = jsonfile.mocap_hand1l.marker4.z;
    pointl_vecp1 = [hpp1lx, hpp1lz, hpp1ly];
end

% Hands 1R (get back marker for center and front marker for 'gp3'
if isfield(jsonfile, 'mocap_hand1r')
    % Get back marker position
    hp1rx = jsonfile.mocap_hand1r.marker2.x;
    hp1ry = jsonfile.mocap_hand1r.marker2.y;
    hp1rz = jsonfile.mocap_hand1r.marker2.z;
    handrp1 = [hp1rx, hp1rz, hp1ry];

    % Get front marker position
    hpp1rx = jsonfile.mocap_hand1r.marker1.x;
    hpp1ry = jsonfile.mocap_hand1r.marker1.y;
    hpp1rz = jsonfile.mocap_hand1r.marker1.z;
    pointr_vecp1 = [hpp1rx, hpp1rz, hpp1ry];
end

% Hands 2L (get back marker for center and front marker for 'gp3'
if isfield(jsonfile, 'mocap_hand2l')
    % Get back marker position
    hp2lx = jsonfile.mocap_hand2l.marker4.x;
    hp2ly = jsonfile.mocap_hand2l.marker4.y;
    hp2lz = jsonfile.mocap_hand2l.marker4.z;
    handlp2 = [hp2lx, hp2lz, hp2ly];

    % Get front marker position
    hpp2lx = jsonfile.mocap_hand2l.marker2.x;
    hpp2ly = jsonfile.mocap_hand2l.marker2.y;
    hpp2lz = jsonfile.mocap_hand2l.marker2.z;
    pointl_vecp2 = [hpp2lx, hpp2lz, hpp2ly];
end

% Hands 2R (get back marker for center and front marker for 'gp3'
if isfield(jsonfile, 'mocap_hand2r')
    % Get back marker position
    hp2rx = jsonfile.mocap_hand2r.marker2.x;
    hp2ry = jsonfile.mocap_hand2r.marker2.y;
    hp2rz = jsonfile.mocap_hand2r.marker2.z;
    handrp2 = [hp2rx, hp2rz, hp2ry];

    % Get front marker position
    hpp2rx = jsonfile.mocap_hand2r.marker1.x;
    hpp2ry = jsonfile.mocap_hand2r.marker1.y;
    hpp2rz = jsonfile.mocap_hand2r.marker1.z;
    pointr_vecp2 = [hpp2rx, hpp2rz, hpp2ry];
end

% % Get tables
% % Get table 1 position
% if isfield(jsonfile, 'mocap_table1')
%     t1x = jsonfile.mocap_table1.position.x;
%     t1y = jsonfile.mocap_table1.position.y;
%     t1z = jsonfile.mocap_table1.position.z;
%     table1 = [t1x, t1z, t1y];
% end

% Get furhat and calibration and screen
% Get furhat position
if isfield(jsonfile, 'mocap_furhat')
    fx = jsonfile.mocap_furhat.position.x;
    fy = jsonfile.mocap_furhat.position.y + 0.20; % Add 20cm to furhat
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

% Get screen position
if isfield(jsonfile, 'mocap_screen')
    sx = jsonfile.mocap_screen.position.x;
    sy = jsonfile.mocap_screen.position.y;
    sz = jsonfile.mocap_screen.position.z;
    screen = [sx, sz, sy];
end

% Get objects
% Get object 1 position
if isfield(jsonfile, 'mocap_target1')
    o1x = jsonfile.mocap_target1.position.x;
    o1y = jsonfile.mocap_target1.position.y;
    o1z = jsonfile.mocap_target1.position.z;
    object{1} = [o1x, o1z, o1y];
end

% Get object 2 position
if isfield(jsonfile, 'mocap_target2')
    o2x = jsonfile.mocap_target2.position.x;
    o2y = jsonfile.mocap_target2.position.y;
    o2z = jsonfile.mocap_target2.position.z;
    object{2} = [o2x, o2z, o2y];
end

% Get object 3 position
if isfield(jsonfile, 'mocap_target3')
    o3x = jsonfile.mocap_target3.position.x;
    o3y = jsonfile.mocap_target3.position.y;
    o3z = jsonfile.mocap_target3.position.z;
    object{3} = [o3x, o3z, o3y];
end

% Get object 4 position
if isfield(jsonfile, 'mocap_target4')
    o4x = jsonfile.mocap_target4.position.x;
    o4y = jsonfile.mocap_target4.position.y;
    o4z = jsonfile.mocap_target4.position.z;
    object{4} = [o4x, o4z, o4y];
end

% Get object 5 position
if isfield(jsonfile, 'mocap_target5')
    o5x = jsonfile.mocap_target5.position.x;
    o5y = jsonfile.mocap_target5.position.y;
    o5z = jsonfile.mocap_target5.position.z;
    object{5} = [o5x, o5z, o5y];
end

% Get object 6 position
if isfield(jsonfile, 'mocap_target6')
    o6x = jsonfile.mocap_target6.position.x;
    o6y = jsonfile.mocap_target6.position.y;
    o6z = jsonfile.mocap_target6.position.z;
    object{6} = [o6x, o6z, o6y];
end

% Get object 7 position
if isfield(jsonfile, 'mocap_target7')
    o7x = jsonfile.mocap_target7.position.x;
    o7y = jsonfile.mocap_target7.position.y;
    o7z = jsonfile.mocap_target7.position.z;
    object{7} = [o7x, o7z, o7y];
end

% Get object 8 position
if isfield(jsonfile, 'mocap_target8')
    o8x = jsonfile.mocap_target8.position.x;
    o8y = jsonfile.mocap_target8.position.y;
    o8z = jsonfile.mocap_target8.position.z;
    object{8} = [o8x, o8z, o8y];
end

% Get object 9 position
if isfield(jsonfile, 'mocap_target9')
    o9x = jsonfile.mocap_target9.position.x;
    o9y = jsonfile.mocap_target9.position.y;
    o9z = jsonfile.mocap_target9.position.z;
    object{9} = [o9x, o9z, o9y];
end

% Get object 10 position
if isfield(jsonfile, 'mocap_target10')
    o10x = jsonfile.mocap_target10.position.x;
    o10y = jsonfile.mocap_target10.position.y;
    o10z = jsonfile.mocap_target10.position.z;
    object{10} = [o10x, o10z, o10y];
end

% Get object 11 position
if isfield(jsonfile, 'mocap_target11')
    o11x = jsonfile.mocap_target11.position.x;
    o11y = jsonfile.mocap_target11.position.y;
    o11z = jsonfile.mocap_target11.position.z;
    object{11} = [o11x, o11z, o11y];
end

% Get object 12 position
if isfield(jsonfile, 'mocap_target12')
    o12x = jsonfile.mocap_target12.position.x;
    o12y = jsonfile.mocap_target12.position.y;
    o12z = jsonfile.mocap_target12.position.z;
    object{12} = [o12x, o12z, o12y];
end

% Get object 13 position
if isfield(jsonfile, 'mocap_target13')
    o13x = jsonfile.mocap_target13.position.x;
    o13y = jsonfile.mocap_target13.position.y;
    o13z = jsonfile.mocap_target13.position.z;
    object{13} = [o13x, o13z, o13y];
end

% Get object 14 position
if isfield(jsonfile, 'mocap_target14')
    o14x = jsonfile.mocap_target14.position.x;
    o14y = jsonfile.mocap_target14.position.y;
    o14z = jsonfile.mocap_target14.position.z;
    object{14} = [o14x, o14z, o14y];
end

% if strcmp(agent, 'yumi')
%     % Get table marker properties
%     table1marker1x = jsonfile.mocap_table1.marker1.x;
%     table1marker1y = jsonfile.mocap_table1.marker1.y;
%     table1marker1z = jsonfile.mocap_table1.marker1.z;
%     table1marker2x = jsonfile.mocap_table1.marker2.x;
%     table1marker2y = jsonfile.mocap_table1.marker2.y;
%     table1marker2z = jsonfile.mocap_table1.marker2.z;
%     table1marker3x = jsonfile.mocap_table1.marker3.x;
%     table1marker3y = jsonfile.mocap_table1.marker3.y;
%     table1marker3z = jsonfile.mocap_table1.marker3.z;
% end

% P1
if isfield(jsonfile, 'tobii_glasses1') & isfield(jsonfile, 'mocap_glasses1')
    % Calculate hits for P1 to P2
    if isfield(jsonfile, 'mocap_glasses2')
        dist_p2p1 = calc_norm(glassesp2-glassesp1);
        collision_ang_p2p1 = atan(head_radius./dist_p2p1);
        gaze_ang_p2p1 = calc_angle(gaze_vecp1-glassesp1, glassesp2-glassesp1);
        gaze_hits_p2p1 = gaze_ang_p2p1 <= collision_ang_p2p1;

        % Write human values for P1
        if gaze_hits_p2p1 == 1
            mocapfield{1} = 'P2';
        end
    end
    
    % Calculate hits for P1 to P3
    if isfield(jsonfile, 'mocap_glasses3')
        dist_p3p1 = calc_norm(glassesp3-glassesp1);
        collision_ang_p3p1 = atan(head_radius./dist_p3p1);
        gaze_ang_p3p1 = calc_angle(gaze_vecp1-glassesp1, glassesp3-glassesp1);
        gaze_hits_p3p1 = gaze_ang_p3p1 <= collision_ang_p3p1;

        % Write human values for P1
        if gaze_hits_p3p1 == 1
            mocapfield{1} = 'P3';
        end
    end
    
%     % Calculate hits for P1 to Table 1
%     if isfield(jsonfile, 'mocap_table1')
%         dist_t1p1 = calc_norm(table1-glassesp1);
%         collision_ang_t1p1 = atan(object_radius./dist_t1p1);
%         gaze_ang_t1p1 = calc_angle(gaze_vecp1-glassesp1, table1-glassesp1);
%         gaze_hits_t1p1 = gaze_ang_t1p1 <= collision_ang_t1p1;
%     end

%     % Calculate intersection points for P1 to Table 1
%     if strcmp(agent, 'yumi')
%         tableplane = createPlane([table1marker1x table1marker1y table1marker1z], [table1marker2x table1marker2y table1marker2z], [table1marker3x table1marker3y table1marker3z]);
%         p1_gazeline = createLine3d([gp1z gp1y gp1x], [gpp1z gpp1y gpp1x]);
%         table_hits_p1 = intersectLinePlane(p1_gazeline, tableplane);
% 
%         % Write table position values for P1
%         mocapfield{3} = table_hits_p1;
%     end

%     % Write table values for P1
%     if gaze_hits_t1p1 == 1
%         mocapfield{1} = 'Tab1';
%     end

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
    
    % Calculate hits for P1 to screen
    if isfield(jsonfile, 'mocap_screen')
        dist_sp1 = calc_norm(screen-glassesp1);
        collision_ang_sp1 = atan(object_radius./dist_sp1);
        gaze_ang_sp1 = calc_angle(gaze_vecp1-glassesp1, screen-glassesp1);
        gaze_hits_sp1 = gaze_ang_sp1 <= collision_ang_sp1;
    end

    % Write furhat and calibration and screen values for P1
    if gaze_hits_fp1 == 1
        mocapfield{1} = 'Furhat';
    end
    if gaze_hits_cp1 == 1
        mocapfield{1} = 'Calibration';
    end
    if gaze_hits_sp1 == 1
        mocapfield{1} = 'Screen';
    end

    % Calculate hits for P1 to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            dist_op1{i} = calc_norm(object{i}-glassesp1);
            collision_ang_op1{i} = atan(object_radius./dist_op1{i});
            gaze_ang_op1{i} = calc_angle(gaze_vecp1-glassesp1, object{i}-glassesp1);
            gaze_hits_op1{i} = gaze_ang_op1{i} <= collision_ang_op1{i};

            if gaze_hits_op1{i} == 1
                mocapfield{1} = strcat('T', int2str(i));
            end
        end
    end
    
    % Calculate head hits for P1 to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            hdist_op1{i} = calc_norm(object{i}-glassesp1);
            hcollision_ang_op1{i} = atan(object_radius./hdist_op1{i});
            head_ang_op1{i} = calc_angle(head_vecp1-glassesp1, object{i}-glassesp1);
            head_hits_op1{i} = head_ang_op1{i} <= hcollision_ang_op1{i};

            if head_hits_op1{i} == 1
                mocapfield{13} = strcat('T', int2str(i));
            end
        end
    end

    % Pointing HL
    % Calculate pointing hits for P1L to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            pldist_op1{i} = calc_norm(object{i}-handlp1);
            plcollision_ang_op1{i} = atan(pobject_radius./pldist_op1{i});
            pointl_ang_op1{i} = calc_angle(pointl_vecp1-handlp1, object{i}-handlp1);
            pointl_hits_op1{i} = pointl_ang_op1{i} <= plcollision_ang_op1{i};

            if pointl_hits_op1{i} == 1
                mocapfield{7} = strcat('T', int2str(i));
            end
        end
    end

    % Pointing HR
    % Calculate pointing hits for P1R to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            prdist_op1{i} = calc_norm(object{i}-handrp1);
            prcollision_ang_op1{i} = atan(pobject_radius./prdist_op1{i});
            pointr_ang_op1{i} = calc_angle(pointr_vecp1-handrp1, object{i}-handrp1);
            pointr_hits_op1{i} = pointr_ang_op1{i} <= prcollision_ang_op1{i};

            if pointr_hits_op1{i} == 1
                mocapfield{7} = strcat('T', int2str(i));
            end
        end
    end
    
    % Export gaze and pointing angles (revert to probability)
    mocapfield{4} = {};
    mocapfield{8} = {};
    mocapfield{9} = {};
    mocapfield{16} = {};
    for i = 1:14
        mocapfield{4} = [mocapfield{4}, (-gaze_ang_op1{i} / pi) + 1];
        mocapfield{8} = [mocapfield{8}, (-pointl_ang_op1{i} / pi) + 1];
        mocapfield{9} = [mocapfield{9}, (-pointr_ang_op1{i} / pi) + 1];
        mocapfield{16} = [mocapfield{16}, (-head_ang_op1{i} / pi) + 1];
    end
end

% P2
if isfield(jsonfile, 'tobii_glasses2') & isfield(jsonfile, 'mocap_glasses2')
    % Calculate hits for P2 to P1
    if isfield(jsonfile, 'mocap_glasses1')
        dist_p1p2 = calc_norm(glassesp1-glassesp2);
        collision_ang_p1p2 = atan(head_radius./dist_p1p2);
        gaze_ang_p1p2 = calc_angle(gaze_vecp2-glassesp2, glassesp1-glassesp2);
        gaze_hits_p1p2 = gaze_ang_p1p2 <= collision_ang_p1p2;

        % Write human values for P2
        if gaze_hits_p1p2 == 1
            mocapfield{2} = 'P1';
        end
    end
    
    % Calculate hits for P2 to P3
    if isfield(jsonfile, 'mocap_glasses3')
        dist_p3p2 = calc_norm(glassesp3-glassesp2);
        collision_ang_p3p2 = atan(head_radius./dist_p3p2);
        gaze_ang_p3p2 = calc_angle(gaze_vecp2-glassesp2, glassesp3-glassesp2);
        gaze_hits_p3p2 = gaze_ang_p3p2 <= collision_ang_p3p2;

        % Write human values for P2
        if gaze_hits_p3p2 == 1
            mocapfield{2} = 'P3';
        end
    end

    % Calculate hits for P2 to Furhat
    if isfield(jsonfile, 'mocap_furhat')
        dist_fp2 = calc_norm(furhat-glassesp2);
        collision_ang_fp2 = atan(object_radius./dist_fp2);
        gaze_ang_fp2 = calc_angle(gaze_vecp2-glassesp2, furhat-glassesp2);
        gaze_hits_fp2 = gaze_ang_fp2 <= collision_ang_fp2;
    end

    % Calculate hits for P2 to calibration
    if isfield(jsonfile, 'mocap_calibration')
        dist_cp2 = calc_norm(calibration-glassesp2);
        collision_ang_cp2 = atan(object_radius./dist_cp2);
        gaze_ang_cp2 = calc_angle(gaze_vecp2-glassesp2, calibration-glassesp2);
        gaze_hits_cp2 = gaze_ang_cp2 <= collision_ang_cp2;
    end
    
    % Calculate hits for P2 to screen
    if isfield(jsonfile, 'mocap_screen')
        dist_sp2 = calc_norm(screen-glassesp2);
        collision_ang_sp2 = atan(object_radius./dist_sp2);
        gaze_ang_sp2 = calc_angle(gaze_vecp2-glassesp2, screen-glassesp2);
        gaze_hits_sp2 = gaze_ang_sp2 <= collision_ang_sp2;
    end

    % Write furhat and calibration values for P2
    if gaze_hits_fp2 == 1
        mocapfield{2} = 'Furhat';
    end
    if gaze_hits_cp2 == 1
        mocapfield{2} = 'Calibration';
    end
    if gaze_hits_sp2 == 1
        mocapfield{2} = 'Screen';
    end
    
    % Calculate hits for P2 to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            dist_op2{i} = calc_norm(object{i}-glassesp2);
            collision_ang_op2{i} = atan(object_radius./dist_op2{i});
            gaze_ang_op2{i} = calc_angle(gaze_vecp2-glassesp2, object{i}-glassesp2);
            gaze_hits_op2{i} = gaze_ang_op2{i} <= collision_ang_op2{i};

            if gaze_hits_op2{i} == 1
                mocapfield{2} = strcat('T', int2str(i));
            end
        end
    end
    
    % Calculate head hits for P2 to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            hdist_op2{i} = calc_norm(object{i}-glassesp2);
            hcollision_ang_op2{i} = atan(object_radius./hdist_op2{i});
            head_ang_op2{i} = calc_angle(head_vecp2-glassesp2, object{i}-glassesp2);
            head_hits_op2{i} = head_ang_op2{i} <= hcollision_ang_op2{i};

            if head_hits_op2{i} == 1
                mocapfield{14} = strcat('T', int2str(i));
            end
        end
    end

    % Pointing HL
    % Calculate pointing hits for P2L to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            pldist_op2{i} = calc_norm(object{i}-handlp2);
            plcollision_ang_op2{i} = atan(pobject_radius./pldist_op2{i});
            pointl_ang_op2{i} = calc_angle(pointl_vecp2-handlp2, object{i}-handlp2);
            pointl_hits_op2{i} = pointl_ang_op2{i} <= plcollision_ang_op2{i};

            if pointl_hits_op2{i} == 1
                mocapfield{10} = strcat('T', int2str(i));
            end
        end
    end

    % Pointing HR
    % Calculate pointing hits for P2R to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            prdist_op2{i} = calc_norm(object{i}-handrp2);
            prcollision_ang_op2{i} = atan(pobject_radius./prdist_op2{i});
            pointr_ang_op2{i} = calc_angle(pointr_vecp2-handrp2, object{i}-handrp2);
            pointr_hits_op2{i} = pointr_ang_op2{i} <= prcollision_ang_op2{i};

            if pointr_hits_op2{i} == 1
                mocapfield{10} = strcat('T', int2str(i));
            end
        end
    end

    % Export gaze and pointing angles (revert to probability)
    mocapfield{5} = {};
    mocapfield{11} = {};
    mocapfield{12} = {};
    mocapfield{17} = {};
    for i = 1:14
        mocapfield{5} = [mocapfield{5}, (-gaze_ang_op2{i} / pi) + 1];
        mocapfield{11} = [mocapfield{11}, (-pointl_ang_op2{i} / pi) + 1];
        mocapfield{12} = [mocapfield{12}, (-pointr_ang_op2{i} / pi) + 1];
        mocapfield{17} = [mocapfield{17}, (-head_ang_op2{i} / pi) + 1];
    end
end

% P3
if isfield(jsonfile, 'tobii_glasses3') & isfield(jsonfile, 'mocap_glasses3')
    % Calculate hits for P3 to P1
    if isfield(jsonfile, 'mocap_glasses1')
        dist_p1p3 = calc_norm(glassesp1-glassesp3);
        collision_ang_p1p3 = atan(head_radius./dist_p1p3);
        gaze_ang_p1p3 = calc_angle(gaze_vecp3-glassesp3, glassesp1-glassesp3);
        gaze_hits_p1p3 = gaze_ang_p1p3 <= collision_ang_p1p3;

        % Write human values for P3
        if gaze_hits_p1p3 == 1
            mocapfield{3} = 'P1';
        end
    end
    
    % Calculate hits for P3 to P2
    if isfield(jsonfile, 'mocap_glasses2')
        dist_p2p3 = calc_norm(glassesp2-glassesp3);
        collision_ang_p2p3 = atan(head_radius./dist_p2p3);
        gaze_ang_p2p3 = calc_angle(gaze_vecp3-glassesp3, glassesp2-glassesp3);
        gaze_hits_p2p3 = gaze_ang_p2p3 <= collision_ang_p2p3;

        % Write human values for P3
        if gaze_hits_p2p3 == 1
            mocapfield{3} = 'P2';
        end
    end

    % Calculate hits for P3 to Furhat
    if isfield(jsonfile, 'mocap_furhat')
        dist_fp3 = calc_norm(furhat-glassesp3);
        collision_ang_fp3 = atan(object_radius./dist_fp3);
        gaze_ang_fp3 = calc_angle(gaze_vecp3-glassesp3, furhat-glassesp3);
        gaze_hits_fp3 = gaze_ang_fp3 <= collision_ang_fp3;
    end

    % Calculate hits for P3 to calibration
    if isfield(jsonfile, 'mocap_calibration')
        dist_cp3 = calc_norm(calibration-glassesp3);
        collision_ang_cp3 = atan(object_radius./dist_cp3);
        gaze_ang_cp3 = calc_angle(gaze_vecp3-glassesp3, calibration-glassesp3);
        gaze_hits_cp3 = gaze_ang_cp3 <= collision_ang_cp3;
    end
    
    % Calculate hits for P3 to screen
    if isfield(jsonfile, 'mocap_screen')
        dist_sp3 = calc_norm(screen-glassesp3);
        collision_ang_sp3 = atan(object_radius./dist_sp3);
        gaze_ang_sp3 = calc_angle(gaze_vecp3-glassesp3, screen-glassesp3);
        gaze_hits_sp3 = gaze_ang_sp3 <= collision_ang_sp3;
    end

    % Write furhat and calibration values for P3
    if gaze_hits_fp3 == 1
        mocapfield{3} = 'Furhat';
    end
    if gaze_hits_cp3 == 1
        mocapfield{3} = 'Calibration';
    end
    if gaze_hits_sp3 == 1
        mocapfield{3} = 'Screen';
    end
    
    % Calculate hits for P3 to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            dist_op3{i} = calc_norm(object{i}-glassesp3);
            collision_ang_op3{i} = atan(object_radius./dist_op3{i});
            gaze_ang_op3{i} = calc_angle(gaze_vecp3-glassesp3, object{i}-glassesp3);
            gaze_hits_op3{i} = gaze_ang_op3{i} <= collision_ang_op3{i};

            if gaze_hits_op3{i} == 1
                mocapfield{3} = strcat('T', int2str(i));
            end
        end
    end
    
    % Calculate head hits for P3 to Objects
    for i = 1:14
        if isfield(jsonfile, strcat('mocap_target', int2str(i)))
            hdist_op3{i} = calc_norm(object{i}-glassesp3);
            hcollision_ang_op3{i} = atan(object_radius./hdist_op3{i});
            head_ang_op3{i} = calc_angle(head_vecp3-glassesp3, object{i}-glassesp3);
            head_hits_op3{i} = head_ang_op3{i} <= hcollision_ang_op3{i};

            if head_hits_op3{i} == 1
                mocapfield{15} = strcat('T', int2str(i));
            end
        end
    end

    % Export gaze angles (revert to probability)
    mocapfield{6} = {};
    mocapfield{18} = {};
    for i = 1:14
        mocapfield{6} = [mocapfield{6}, (-gaze_ang_op3{i} / pi) + 1];
        mocapfield{18} = [mocapfield{18}, (-head_ang_op3{i} / pi) + 1];
    end
end

data = mocapfield;
