% ASSIGN THE CORRECT VALUES OF THE MARKERS FOR THE GLASSES
% ASSIGN OBJECTS

function [data] = gazehits(jsonfile, agent, glasses_num, targets_num, tables_num)
% Parses processed json file and reproduces gaze hits

% Define a threshold around head mid point (20cm)
head_radius = 0.2;

% Define a threshold around the object (10cm)
object_radius = 0.1;

% Check if gaze intersects with human or with object
% First make all fields NULL
% Gaze Targets
mocapfield{1} = {''}; % P1
mocapfield{2} = {''}; % P2

% Table positions or angles
if strcmp(agent, 'yumi')
    mocapfield{3} = [0, 0, 0]; % P1
    mocapfield{4} = [0, 0, 0]; % P2
elseif strcmp(agent, 'furhat')
    % Angles to targets
    mocapfield{3} = zeros(targets_num); % P1
    mocapfield{4} = zeros(targets_num); % P2
end

% Check that tobii glasses 1 exist
if isfield(jsonfile, 'mocap_glasses1')
    % Get P1 glasses position
    gp1x = (jsonfile.mocap_glasses1.marker2.x + jsonfile.mocap_glasses1.marker4.x) / 2;
    gp1y = (jsonfile.mocap_glasses1.marker2.y + jsonfile.mocap_glasses1.marker4.y) / 2;
    gp1z = (jsonfile.mocap_glasses1.marker2.z + jsonfile.mocap_glasses1.marker4.z) / 2;
    glassesp1 = [gp1x, gp1z, gp1y];
end

if isfield(jsonfile, 'tobii_glasses1')
    % Get P1 gaze position
    gpp1x = jsonfile.tobii_glasses1.gp3_3d.x;
    gpp1y = jsonfile.tobii_glasses1.gp3_3d.y;
    gpp1z = jsonfile.tobii_glasses1.gp3_3d.z;

    % Get gaze vectors
    gaze_vecp1 = [gpp1x, gpp1z, gpp1y];
end

if isfield(jsonfile, 'mocap_glasses2')
    % Get P2 glasses position
    gp2x = (jsonfile.mocap_glasses2.marker3.x + jsonfile.mocap_glasses2.marker2.x) / 2;
    gp2y = (jsonfile.mocap_glasses2.marker3.y + jsonfile.mocap_glasses2.marker2.y) / 2;
    gp2z = (jsonfile.mocap_glasses2.marker3.z + jsonfile.mocap_glasses2.marker2.z) / 2;
    glassesp2 = [gp2x, gp2z, gp2y];
end

if isfield(jsonfile, 'tobii_glasses2')
    % Get P2 gaze position
    gpp2x = jsonfile.tobii_glasses2.gp3_3d.x;
    gpp2y = jsonfile.tobii_glasses2.gp3_3d.y;
    gpp2z = jsonfile.tobii_glasses2.gp3_3d.z;

    % Get gaze vectors
    gaze_vecp2 = [gpp2x, gpp2z, gpp2y];
end

% Get tables
% Get table 1 position
if isfield(jsonfile, 'mocap_table1')
    t1x = jsonfile.mocap_table1.position.x;
    t1y = jsonfile.mocap_table1.position.y;
    t1z = jsonfile.mocap_table1.position.z;
    table1 = [t1x, t1z, t1y];
end

% Get table 2 position
if isfield(jsonfile, 'mocap_table2')
    t2x = jsonfile.mocap_table2.position.x;
    t2y = jsonfile.mocap_table2.position.y;
    t2z = jsonfile.mocap_table2.position.z;
    table2 = [t2x, t2z, t2y];
end

% Get furhat and calibration
% Get furhat position
if isfield(jsonfile, 'mocap_furhat')
    fx = jsonfile.mocap_furhat.position.x;
    fy = jsonfile.mocap_furhat.position.y;
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
    object1 = [o1x, o1z, o1y];
end

% Get object 2 position
if isfield(jsonfile, 'mocap_target2')
    o2x = jsonfile.mocap_target2.position.x;
    o2y = jsonfile.mocap_target2.position.y;
    o2z = jsonfile.mocap_target2.position.z;
    object2 = [o2x, o2z, o2y];
end

% Get object 3 position
if isfield(jsonfile, 'mocap_target3')
    o3x = jsonfile.mocap_target3.position.x;
    o3y = jsonfile.mocap_target3.position.y;
    o3z = jsonfile.mocap_target3.position.z;
    object3 = [o3x, o3z, o3y];
end

% Get object 4 position
if isfield(jsonfile, 'mocap_target4')
    o4x = jsonfile.mocap_target4.position.x;
    o4y = jsonfile.mocap_target4.position.y;
    o4z = jsonfile.mocap_target4.position.z;
    object4 = [o4x, o4z, o4y];
end

% Get object 5 position
if isfield(jsonfile, 'mocap_target5')
    o5x = jsonfile.mocap_target5.position.x;
    o5y = jsonfile.mocap_target5.position.y;
    o5z = jsonfile.mocap_target5.position.z;
    object5 = [o5x, o5z, o5y];
end

if strcmp(agent, 'yumi')
    % Get table marker properties
    table1marker1x = jsonfile.mocap_table1.marker1.x;
    table1marker1y = jsonfile.mocap_table1.marker1.y;
    table1marker1z = jsonfile.mocap_table1.marker1.z;
    table1marker2x = jsonfile.mocap_table1.marker2.x;
    table1marker2y = jsonfile.mocap_table1.marker2.y;
    table1marker2z = jsonfile.mocap_table1.marker2.z;
    table1marker3x = jsonfile.mocap_table1.marker3.x;
    table1marker3y = jsonfile.mocap_table1.marker3.y;
    table1marker3z = jsonfile.mocap_table1.marker3.z;
end

% P1
if isfield(jsonfile, 'tobii_glasses1')
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

    % Calculate hits for P1 to Table 1
    if isfield(jsonfile, 'mocap_table1')
        dist_t1p1 = calc_norm(table1-glassesp1);
        collision_ang_t1p1 = atan(object_radius./dist_t1p1);
        gaze_ang_t1p1 = calc_angle(gaze_vecp1-glassesp1, table1-glassesp1);
        gaze_hits_t1p1 = gaze_ang_t1p1 <= collision_ang_t1p1;
    end

    % Calculate hits for P1 to Table 2
    if isfield(jsonfile, 'mocap_table2')
        dist_t2p1 = calc_norm(table2-glassesp1);
        collision_ang_t2p1 = atan(object_radius./dist_t2p1);
        gaze_ang_t2p1 = calc_angle(gaze_vecp1-glassesp1, table2-glassesp1);
        gaze_hits_t2p1 = gaze_ang_t2p1 <= collision_ang_t2p1;
    end

    % Calculate intersection points for P1 to Table 1
    if strcmp(agent, 'yumi')
        tableplane = createPlane([table1marker1x table1marker1y table1marker1z], [table1marker2x table1marker2y table1marker2z], [table1marker3x table1marker3y table1marker3z]);
        p1_gazeline = createLine3d([gp1z gp1y gp1x], [gpp1z gpp1y gpp1x]);
        table_hits_p1 = intersectLinePlane(p1_gazeline, tableplane);

        % Write table position values for P1
        mocapfield{3} = table_hits_p1;
    end

    % Write table values for P1
    if gaze_hits_t1p1 == 1
        mocapfield{1} = 'Tab1';
    end
    if gaze_hits_t2p1 == 1
        mocapfield{1} = 'Tab2';
    end

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

    % Calculate hits for P1 to O1
    if isfield(jsonfile, 'mocap_target1')
        dist_o1p1 = calc_norm(object1-glassesp1);
        collision_ang_o1p1 = atan(object_radius./dist_o1p1);
        gaze_ang_o1p1 = calc_angle(gaze_vecp1-glassesp1, object1-glassesp1);
        gaze_hits_o1p1 = gaze_ang_o1p1 <= collision_ang_o1p1;

        if gaze_hits_o1p1 == 1
            mocapfield{1} = 'T1';
        end
    end

    % Calculate hits for P1 to O2
    if isfield(jsonfile, 'mocap_target2')
        dist_o2p1 = calc_norm(object2-glassesp1);
        collision_ang_o2p1 = atan(object_radius./dist_o2p1);
        gaze_ang_o2p1 = calc_angle(gaze_vecp1-glassesp1, object2-glassesp1);
        gaze_hits_o2p1 = gaze_ang_o2p1 <= collision_ang_o2p1;

        if gaze_hits_o2p1 == 1
            mocapfield{1} = 'T2';
        end
    end

    % Calculate hits for P1 to O3
    if isfield(jsonfile, 'mocap_target3')
        dist_o3p1 = calc_norm(object3-glassesp1);
        collision_ang_o3p1 = atan(object_radius./dist_o3p1);
        gaze_ang_o3p1 = calc_angle(gaze_vecp1-glassesp1, object3-glassesp1);
        gaze_hits_o3p1 = gaze_ang_o3p1 <= collision_ang_o3p1;

        if gaze_hits_o3p1 == 1
            mocapfield{1} = 'T3';
        end
    end

    % Calculate hits for P1 to O4
    if isfield(jsonfile, 'mocap_target4')
        dist_o4p1 = calc_norm(object4-glassesp1);
        collision_ang_o4p1 = atan(object_radius./dist_o4p1);
        gaze_ang_o4p1 = calc_angle(gaze_vecp1-glassesp1, object4-glassesp1);
        gaze_hits_o4p1 = gaze_ang_o4p1 <= collision_ang_o4p1;

        if gaze_hits_o4p1 == 1
            mocapfield{1} = 'T4';
        end
    end

    % Calculate hits for P1 to O5
    if isfield(jsonfile, 'mocap_target5')
        dist_o5p1 = calc_norm(object5-glassesp1);
        collision_ang_o5p1 = atan(object_radius./dist_o5p1);
        gaze_ang_o5p1 = calc_angle(gaze_vecp1-glassesp1, object5-glassesp1);
        gaze_hits_o5p1 = gaze_ang_o5p1 <= collision_ang_o5p1;

        if gaze_hits_o5p1 == 1
            mocapfield{1} = 'T5';
        end
    end
end

% P2
if isfield(jsonfile, 'tobii_glasses2')
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

    % Calculate hits for P2 to Table 1
    if isfield(jsonfile, 'mocap_table1')
        dist_t1p2 = calc_norm(table1-glassesp2);
        collision_ang_t1p2 = atan(object_radius./dist_t1p2);
        gaze_ang_t1p2 = calc_angle(gaze_vecp2-glassesp2, table1-glassesp2);
        gaze_hits_t1p2 = gaze_ang_t1p2 <= collision_ang_t1p2;
    end

    % Calculate hits for P2 to Table 2
    if isfield(jsonfile, 'mocap_table2')
        dist_t2p2 = calc_norm(table2-glassesp2);
        collision_ang_t2p2 = atan(object_radius./dist_t2p2);
        gaze_ang_t2p2 = calc_angle(gaze_vecp2-glassesp2, table2-glassesp2);
        gaze_hits_t2p2 = gaze_ang_t2p2 <= collision_ang_t2p2;
    end

    % Calculate intersection points for P2 to Table 1
    if strcmp(agent, 'yumi')
        tableplane = createPlane([table1marker1x table1marker1y table1marker1z], [table1marker2x table1marker2y table1marker2z], [table1marker3x table1marker3y table1marker3z]);
        p2_gazeline = createLine3d([gp2z gp2y gp2x], [gpp2z gpp2y gpp2x]);
        table_hits_p2 = intersectLinePlane(p2_gazeline, tableplane);

        % Write table position values for P2
        mocapfield{4} = table_hits_p2;
    end

    % Write table values for P1
    if gaze_hits_t1p2 == 1
        mocapfield{2} = 'Tab1';
    end
    if gaze_hits_t2p2 == 1
        mocapfield{2} = 'Tab2';
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

    % Write furhat and calibration values for P2
    if gaze_hits_fp2 == 1
        mocapfield{2} = 'Furhat';
    end
    if gaze_hits_cp2 == 1
        mocapfield{2} = 'Calibration';
    end

    % Calculate hits for P2 to O1
    if isfield(jsonfile, 'mocap_target1')
        dist_o1p2 = calc_norm(object1-glassesp2);
        collision_ang_o1p2 = atan(object_radius./dist_o1p2);
        gaze_ang_o1p2 = calc_angle(gaze_vecp2-glassesp2, object1-glassesp2);
        gaze_hits_o1p2 = gaze_ang_o1p2 <= collision_ang_o1p2;

        if gaze_hits_o1p2 == 1
            mocapfield{2} = 'T1';
        end
    end

    % Calculate hits for P2 to O2
    if isfield(jsonfile, 'mocap_target2')
        dist_o2p2 = calc_norm(object2-glassesp2);
        collision_ang_o2p2 = atan(object_radius./dist_o2p2);
        gaze_ang_o2p2 = calc_angle(gaze_vecp2-glassesp2, object2-glassesp2);
        gaze_hits_o2p2 = gaze_ang_o2p2 <= collision_ang_o2p2;

        if gaze_hits_o2p2 == 1
            mocapfield{2} = 'T2';
        end
    end

    % Calculate hits for P2 to O3
    if isfield(jsonfile, 'mocap_target3')
        dist_o3p2 = calc_norm(object3-glassesp2);
        collision_ang_o3p2 = atan(object_radius./dist_o3p2);
        gaze_ang_o3p2 = calc_angle(gaze_vecp2-glassesp2, object3-glassesp2);
        gaze_hits_o3p2 = gaze_ang_o3p2 <= collision_ang_o3p2;

        if gaze_hits_o3p2 == 1
            mocapfield{2} = 'T3';
        end
    end

    % Calculate hits for P2 to O4
    if isfield(jsonfile, 'mocap_target4')
        dist_o4p2 = calc_norm(object4-glassesp2);
        collision_ang_o4p2 = atan(object_radius./dist_o4p2);
        gaze_ang_o4p2 = calc_angle(gaze_vecp2-glassesp2, object4-glassesp2);
        gaze_hits_o4p2 = gaze_ang_o4p2 <= collision_ang_o4p2;

        if gaze_hits_o4p2 == 1
            mocapfield{2} = 'T4';
        end
    end

    % Calculate hits for P2 to O5
    if isfield(jsonfile, 'mocap_target5')
        dist_o5p2 = calc_norm(object5-glassesp2);
        collision_ang_o5p2 = atan(object_radius./dist_o5p2);
        gaze_ang_o5p2 = calc_angle(gaze_vecp2-glassesp2, object5-glassesp2);
        gaze_hits_o5p2 = gaze_ang_o5p2 <= collision_ang_o5p2;

        if gaze_hits_o5p2 == 1
            mocapfield{2} = 'T5';
        end
    end
end

data = mocapfield;
