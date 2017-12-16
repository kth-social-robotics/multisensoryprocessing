function [data] = gazehits(jsonfile)
% Parses processed json file and reproduces gaze hits

% Define a threshold around head mid point (20cm)
head_radius = 0.2;

% Define a threshold around the object (10cm)
object_radius = 0.1;

% Check if gaze intersects with human or with object
% First make all fields NULL
mocapfield{1} = {''};
mocapfield{2} = [0, 0, 0];

% Check that tobii glasses exist
if isfield(jsonfile, 'tobii_glasses1') & isfield(jsonfile, 'mocap_glasses1')
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
    % Get table 1 position
    t1x = jsonfile.mocap_table1.position.x;
    t1y = jsonfile.mocap_table1.position.y;
    t1z = jsonfile.mocap_table1.position.z;
    table1 = [t1x, t1z, t1y];
    
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

    % Calculate hits for P1 to Table 1
    dist_t1p1 = calc_norm(table1-glassesp1);
    collision_ang_t1p1 = atan(object_radius./dist_t1p1);
    gaze_ang_t1p1 = calc_angle(gaze_vecp1-glassesp1, table1-glassesp1);
    gaze_hits_t1p1 = gaze_ang_t1p1 <= collision_ang_t1p1;
    
    % Calculate intersection points for P1 to Table 1
    %table_hits_p1 = [0, 0, 0];
    tableplane = createPlane([table1marker1x table1marker1y table1marker1z], [table1marker2x table1marker2y table1marker2z], [table1marker3x table1marker3y table1marker3z]);
    p1_gazeline = createLine3d([gp1z gp1y gp1x], [gpp1z gpp1y gpp1x]);
    table_hits_p1 = intersectLinePlane(p1_gazeline, tableplane);
    
    % Write table values for P1
    if gaze_hits_t1p1 == 1
        mocapfield{1} = 'T1';
    end
    % Write table position values for P1
    mocapfield{2} = table_hits_p1;

    % Calculate hits for P1 to O1
    if isfield(jsonfile, 'mocap_target1')
        dist_o1p1 = calc_norm(object1-glassesp1);
        collision_ang_o1p1 = atan(object_radius./dist_o1p1);
        gaze_ang_o1p1 = calc_angle(gaze_vecp1-glassesp1, object1-glassesp1);
        gaze_hits_o1p1 = gaze_ang_o1p1 <= collision_ang_o1p1;
        
        if gaze_hits_o1p1 == 1
            mocapfield{1} = 'O1';
        end
    end
    
    % Calculate hits for P1 to O2
    if isfield(jsonfile, 'mocap_target2')
        dist_o2p1 = calc_norm(object2-glassesp1);
        collision_ang_o2p1 = atan(object_radius./dist_o2p1);
        gaze_ang_o2p1 = calc_angle(gaze_vecp1-glassesp1, object2-glassesp1);
        gaze_hits_o2p1 = gaze_ang_o2p1 <= collision_ang_o2p1;
        
        if gaze_hits_o2p1 == 1
            mocapfield{1} = 'O2';
        end
    end
end

data = mocapfield;
