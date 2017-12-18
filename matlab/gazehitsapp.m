% Parses processed csv files and reproduces csv of gaze hits
furniturefile = sprintf('data/app/furniture.csv');

% Rec files
furniturecsvcol = 140 + 1;
appfile = sprintf('../../Documents/Data/Baby Robot/Data/rec15/app/rec15_final.csv');
asrfile = sprintf('../../Documents/Data/Baby Robot/Data/rec15/asr/rec15.csv');
mocapfile = sprintf('../../Documents/Data/Baby Robot/Data/rec15/output/rec15_data.csv');

% Result
outfile = sprintf('data/results/rec15_gazehits.csv');

% Get app data
fid1 = fopen(appfile);
appDATA = textscan(fid1, '%s', 'delimiter', '\n');
appdata = appDATA{1};

% Get app columns
appn = textscan(appdata{1}, '%s', 'delimiter', ',');
appcol = appn{1};
appnColumns = floor(size(appcol,1));

% Get furniture data
fid2 = fopen(furniturefile);
furnitureDATA = textscan(fid2, '%s', 'delimiter', '\n');
furnituredata = furnitureDATA{1};

% Get furniture columns
furnituren = textscan(furnituredata{1}, '%s', 'delimiter', ';');
furniturecol = furnituren{1};
furniturenColumns = floor(size(furniturecol,1));

% Get asr data
fid3 = fopen(asrfile);
asrDATA = textscan(fid3, '%s', 'delimiter', '\n');
asrdata = asrDATA{1};

% Get asr columns
asrn = textscan(asrdata{1}, '%s', 'delimiter', ',');
asrcol = asrn{1};
asrnColumns = floor(size(asrcol,1));

% Get mocap data
fid4 = fopen(mocapfile);
mocapDATA = textscan(fid4, '%s', 'delimiter', '\n');
mocapdata = mocapDATA{1};

% Get mocap columns
mocapn = textscan(mocapdata{1}, '%s', 'delimiter', ',');
mocapcol = mocapn{1};
mocapnColumns = floor(size(mocapcol,1));

% Init field table
mocapfield{1,1} = {'Frame'};
mocapfield{1,2} = {'Time'};
mocapfield{1,3} = {'M Gaze'};
mocapfield{1,4} = {'P1 Gaze'};
mocapfield{1,5} = {'P2 Gaze'};
mocapfield{1,6} = {'M Room'};
mocapfield{1,7} = {'P1 Room'};
mocapfield{1,8} = {'P2 Room'};
mocapfield{1,9} = {'M ASR'};
mocapfield{1,10} = {'P1 ASR'};
mocapfield{1,11} = {'P2 ASR'};

% Make first 6 lines NULL
for i = 2:6
    for j = 1:11
        mocapfield{i,j} = {''};
    end
end

% Define screen coordinates
%screen_up_left = {-0.474992, 0.029005, 0.888369};
%screen_up_right = {-0.477954, 0.027106, -0.051085};
%screen_down_left = {0.052582, 0.030279, 0.889596};
%screen_down_right = {0.051298, 0.026969, -0.049968};
screenplane = createPlane([-0.049968 0 0.051298], [0.889596 0.00331 0.052582], [-0.051085 0.000137 -0.477954]);

% Room coordinates
% x1 = 1, x2 = 2, y1 = 3, y2 = 4
room{1,1} = 45;
room{1,2} = 214;
room{1,3} = 147;
room{1,4} = 573;
room{2,1} = 225;
room{2,2} = 334;
room{2,3} = 144;
room{2,4} = 295;
room{3,1} = 346;
room{3,2} = 513;
room{3,3} = 146;
room{3,4} = 294;
room{4,1} = 226;
room{4,2} = 454;
room{4,3} = 305;
room{4,4} = 514;
room{5,1} = 464;
room{5,2} = 633;
room{5,3} = 304;
room{5,4} = 574;
room{6,1} = 526;
room{6,2} = 755;
room{6,3} = 84;
room{6,4} = 212;
room{7,1} = 765;
room{7,2} = 874;
room{7,3} = 84;
room{7,4} = 213;
room{8,1} = 886;
room{8,2} = 1054;
room{8,3} = 86;
room{8,4} = 233;
room{9,1} = 645;
room{9,2} = 1233;
room{9,3} = 245;
room{9,4} = 574;

% Define a threshold around head mid point (20cm)
head_radius = 0.2;
    
% Define a threshold around objects (for now 150px), switch with probability
object_threshold = 150;
    
% Define a threshold around the screen (for now 15cm)
screen_threshold = 0.15;

% Define a threshold around room (for now 100px)
room_threshold = 100;

% Initiate asr and app
asrd = {'', '', '', '', ''};
appd = {'', '', '', '', ''};

% First check if gaze intersects with human or with screen and then find if it is close to objects
%for i = 7:50006
for i = 7:(size(mocapdata, 1) - 7)
    % Init gaze and furpoints
    gazepoint = [0,0];
    shopfurpoint = [0,0];
    furpoint = [0,0];
    
    mocaplines(i) = textscan(mocapdata{i}, '%s', 'delimiter', ',');
    
    % First make all fields NULL
    for z = 1:11
        mocapfield{i,z} = {''};
    end
    
    % Take mocap line
    d = mocaplines{i};

    % Fix error where a few times last gp3 is missing and put a zero
    if size(d,1) == 151
        d(152) = {'0'};
    end

    % Put frame and time
    mocapfield{i,1} = d(1);
    mocapfield{i,2} = d(2);

    % Get glasses
    % Get Moderator glasses position
    glasses_mod_left = {d(93), d(94), d(95)};
    glasses_mod_right = {d(90), d(91), d(92)};
    gmx = (str2double(d{93,1}) + str2double(d{90,1})) / 2;
    gmy = (str2double(d{94,1}) + str2double(d{91,1})) / 2;
    gmz = (str2double(d{95,1}) + str2double(d{92,1})) / 2;
    %glasses_mod_mid = {gmx, gmy, gmz};

    % Get P1 glasses position
    glasses_p1_left = {d(123), d(124), d(125)};
    glasses_p1_right = {d(114), d(115), d(116)};
    gp1x = (str2double(d{123,1}) + str2double(d{114,1})) / 2;
    gp1y = (str2double(d{124,1}) + str2double(d{115,1})) / 2;
    gp1z = (str2double(d{125,1}) + str2double(d{116,1})) / 2;
    %glasses_p1_mid = {gp1x, gp1y, gp1z};

    % Get P2 glasses position
    glasses_p2_left = {d(102), d(103), d(104)};
    glasses_p2_right = {d(105), d(106), d(107)};
    gp2x = (str2double(d{102,1}) + str2double(d{105,1})) / 2;
    gp2y = (str2double(d{103,1}) + str2double(d{106,1})) / 2;
    gp2z = (str2double(d{104,1}) + str2double(d{107,1})) / 2;
    %glasses_p2_mid = {gp2x, gp2y, gp2z};

    % Get gaze
    % Get Moderator gaze position
    gpmx = str2double(d(132));
    gpmy = str2double(d(133));
    gpmz = str2double(d(134));
    %gaze_mod = {gpmx, gpmy, gpmz};

    % Get P1 gaze position
    gpp1x = str2double(d(150));
    gpp1y = str2double(d(151));
    gpp1z = str2double(d(152));
    %gaze_p1 = {gpp1x, gpp1y, gpp1z};

    % Get P2 gaze position
    gpp2x = str2double(d(141));
    gpp2y = str2double(d(142));
    gpp2z = str2double(d(143));
    %gaze_p2 = {gpp2x, gpp2y, gpp2z};

    % Plot identified markers
    % Define sphere and plot
    %[x,y,z] = sphere;
    %figure;
    %mocap_centre = surf(x*0.01, y*0.01, z*0.01);
    %hold on;

    % All z are minus
    % Glasses
    %glasses_m = surf(x*0.15 + gmx, y*0.15 - gmz, z*0.15 + gmy);
    %glasses_p1 = surf(x*0.15 + gp1x, y*0.15 - gp1z, z*0.15 + gp1y);
    %glasses_p2 = surf(x*0.15 + gp2x, y*0.15 - gp2z, z*0.15 + gp2y);

    % Gaze
    %gaze_m = surf(x*0.05 + gpmx, y*0.05 - gpmz, z*0.05 + gpmy);
    %gaze_p1 = surf(x*0.05 + gpp1x, y*0.05 - gpp1z, z*0.05 + gpp1y);
    %gaze_p2 = surf(x*0.05 + gpp2x, y*0.05 - gpp2z, z*0.05 + gpp2y);

    % Gaze lines
    %line_m = line([gmx gpmx], [-gmz -gpmz], [gmy gpmy]);
    %line_p1 = line([gp1x gpp1x], [-gp1z -gpp1z], [gp1y gpp1y]);
    %line_p2 = line([gp2x gpp2x], [-gp2z -gpp2z], [gp2y gpp2y]);

    % Screen (z (second []) is minus)
    %screen = patch([-0.477954 -0.474992 0.052582 0.051298], [0.051085 -0.888369 -0.889596 0.049968], [0.027106 0.029005 0.030279 0.026969], [0 0 0 0]);

    % Coordinate limits
    %xlim([-4 4]);
    %ylim([-4 4]);
    %zlim([-2 2]);

    % Get gaze vectors
    gaze_vecm = [gpmx, gpmz, gpmy];
    gaze_vecp1 = [gpp1x, gpp1z, gpp1y];
    gaze_vecp2 = [gpp2x, gpp2z, gpp2y];

    % Get glasses positions
    glassesm = [gmx, gmz, gmy];
    glassesp1 = [gp1x, gp1z, gp1y];
    glassesp2 = [gp2x, gp2z, gp2y];

    % Get screen and app line
    appi = i / 12;
    if (i == 1) || (floor(appi) == appi)
        applines(appi + 6) = textscan(appdata{appi + 6}, '%s', 'delimiter', ',');
        appd = applines{appi + 6};
    end

    % Moderator
    % Calculate hits for moderator to P1
    dist_p1m = calc_norm(glassesp1-glassesm);
    collision_ang_p1m = atan(head_radius./dist_p1m);
    gaze_ang_p1m = calc_angle(gaze_vecm-glassesm, glassesp1-glassesm);
    gaze_hits_p1m = gaze_ang_p1m <= collision_ang_p1m;

    % Calculate hits for moderator to P2
    dist_p2m = calc_norm(glassesp2-glassesm);
    collision_ang_p2m = atan(head_radius./dist_p2m);
    gaze_ang_p2m = calc_angle(gaze_vecm-glassesm, glassesp2-glassesm);
    gaze_hits_p2m = gaze_ang_p2m <= collision_ang_p2m;

    % Calculate hits for moderator to screen
    % Create 3d line from points
    m_gazeline = createLine3d([gmz gmy gmx], [gpmz gpmy gpmx]);
    screen_hits_m = intersectLinePlane(m_gazeline, screenplane);
    %if ((screen_hits_m(1) >= -0.05 - screen_threshold) && (screen_hits_m(1) <= 0.88 + screen_threshold) && ((screen_hits_m(3) >= -0.47 - screen_threshold) && (screen_hits_m(3) <= 0.05 + screen_threshold)))
    if ((screen_hits_m(1) >= -0.05) && (screen_hits_m(1) <= 0.88) && ((screen_hits_m(3) >= -0.47) && (screen_hits_m(3) <= 0.05)))
        % Convert x and y to pixels
        m_pixel_x = ((screen_hits_m(1) + 0.05) / 0.93) * 1280;
        % For moderator inverse x
        m_pixel_x = abs(m_pixel_x - 1280);
        m_pixel_y = ((screen_hits_m(3) + 0.47) / 0.52) * 720;

        % Initiate field
        %mocapfield{i,3} = 'screen';
        %mocapfield{i,6} = 'screen';
        mocapfield{i,3} = '';
        mocapfield{i,6} = '';

        % Check what screen/room/object it currently is and update field
        switch appd{5}
            case 'black'
                % App has not started yet (black screen)
                %mocapfield{i,3} = 'black';
                %mocapfield{i,6} = 'black';
                mocapfield{i,3} = '';
                mocapfield{i,6} = '';

            case 'shop: bathroom'
                % Check objects by looking at relevant furniture line
                for furi = 2:35
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [m_pixel_x,m_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,3}, '')
                            mocapfield{i,3} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,3} = strcat(mocapfield{i,3}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,6} = 'shop: bathroom';
            case 'shop: bedroom'
                % Check objects by looking at relevant furniture line
                for furi = 36:51
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [m_pixel_x,m_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,3}, '')
                            mocapfield{i,3} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,3} = strcat(mocapfield{i,3}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,6} = 'shop: bedroom';
            case 'shop: kitchen'
                % Check objects by looking at relevant furniture line
                for furi = 52:75
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [m_pixel_x,m_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,3}, '')
                            mocapfield{i,3} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,3} = strcat(mocapfield{i,3}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,6} = 'shop: kitchen';
            case 'shop: living room'
                % Check objects by looking at relevant furniture line
                for furi = 76:99
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [m_pixel_x,m_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,3}, '')
                            mocapfield{i,3} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,3} = strcat(mocapfield{i,3}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,6} = 'shop: living room';
            case 'shop: misc'
                % Check objects by looking at relevant furniture line
                for furi = 100:126
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [m_pixel_x,m_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,3}, '')
                            mocapfield{i,3} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,3} = strcat(mocapfield{i,3}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,6} = 'shop: misc';
            case 'shop: rugs'
                % Check objects by looking at relevant furniture line
                for furi = 127:141
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [m_pixel_x,m_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,3}, '')
                            mocapfield{i,3} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,3} = strcat(mocapfield{i,3}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,6} = 'shop: rugs';

            case 'flat'
                % Check objects in appline
                a = 6;
                while a < furniturecsvcol % Change step for case where there is more furniture (or less) than 170
                    if strcmp(appd{a}, 'NULL') == 0
                        % Check distance closer than threshold
                        gazepoint = [m_pixel_x,m_pixel_y];
                        furpoint = [str2num(appd{a+1}),str2num(appd{a+2})];
                        dist = norm(gazepoint - furpoint);
                        % Write and append all objects
                        if dist <= object_threshold
                            if strcmp(mocapfield{i,3}, '')
                                mocapfield{i,3} = strcat('|', num2str(appd{a}), '@', num2str(fix(dist)), '|');
                            else
                                mocapfield{i,3} = strcat(mocapfield{i,3}, strcat(num2str(appd{a}), '@', num2str(fix(dist)), '|'));
                            end
                        end
                    end
                    a = a + 5;
                end

                % Check room
                for r = 1:9
                    if (m_pixel_x >= room{r,1}) && (m_pixel_x <= room{r,2}) && (m_pixel_y >= room{r,3}) && (m_pixel_y <= room{r,4})
                        mocapfield{i,6} = int2str(r);
                    end
                end
        end
    end

    % Write human values for Moderator
    if gaze_hits_p1m == 1
        mocapfield{i,3} = 'P1';
    end
    if gaze_hits_p2m == 1
        mocapfield{i,3} = 'P2';
    end

    % P1
    % Calculate hits for P1 to moderator
    dist_mp1 = calc_norm(glassesm-glassesp1);
    collision_ang_mp1 = atan(head_radius./dist_mp1);
    gaze_ang_mp1 = calc_angle(gaze_vecp1-glassesp1, glassesm-glassesp1);
    gaze_hits_mp1 = gaze_ang_mp1 <= collision_ang_mp1;

    % Calculate hits for P1 to P2
    dist_p2p1 = calc_norm(glassesp2-glassesp1);
    collision_ang_p2p1 = atan(head_radius./dist_p2p1);
    gaze_ang_p2p1 = calc_angle(gaze_vecp1-glassesp1, glassesp2-glassesp1);
    gaze_hits_p2p1 = gaze_ang_p2p1 <= collision_ang_p2p1;

    % Calculate hits for P1 to screen
    % Create 3d line from points
    p1_gazeline = createLine3d([gp1z gp1y gp1x], [gpp1z gpp1y gpp1x]);
    screen_hits_p1 = intersectLinePlane(p1_gazeline, screenplane);
    %if ((screen_hits_p1(1) >= -0.05 - screen_threshold) && (screen_hits_p1(1) <= 0.88 + screen_threshold) && ((screen_hits_p1(3) >= -0.47 - screen_threshold) && (screen_hits_p1(3) <= 0.05 + screen_threshold)))
    if ((screen_hits_p1(1) >= -0.05) && (screen_hits_p1(1) <= 0.88) && ((screen_hits_p1(3) >= -0.47) && (screen_hits_p1(3) <= 0.05)))
        % Convert x and y to pixels
        p1_pixel_x = ((screen_hits_p1(1) + 0.05) / 0.93) * 1280;
        % For moderator inverse x
        p1_pixel_x = abs(p1_pixel_x - 1280);
        p1_pixel_y = ((screen_hits_p1(3) + 0.47) / 0.52) * 720;

        % Initiate field
        %mocapfield{i,4} = 'screen';
        %mocapfield{i,7} = 'screen';
        mocapfield{i,4} = '';
        mocapfield{i,7} = '';

        % Check what screen/room/object it currently is and update field
        switch appd{5}
            case 'black'
                % App has not started yet (black screen)
                %mocapfield{i,4} = 'black';
                %mocapfield{i,7} = 'black';
                mocapfield{i,4} = '';
                mocapfield{i,7} = '';

            case 'shop: bathroom'
                % Check objects by looking at relevant furniture line
                for furi = 2:35
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p1_pixel_x,p1_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,4}, '')
                            mocapfield{i,4} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,4} = strcat(mocapfield{i,4}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,7} = 'shop: bathroom';
            case 'shop: bedroom'
                % Check objects by looking at relevant furniture line
                for furi = 36:51
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p1_pixel_x,p1_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,4}, '')
                            mocapfield{i,4} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,4} = strcat(mocapfield{i,4}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,7} = 'shop: bedroom';
            case 'shop: kitchen'
                % Check objects by looking at relevant furniture line
                for furi = 52:75
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p1_pixel_x,p1_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,4}, '')
                            mocapfield{i,4} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,4} = strcat(mocapfield{i,4}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,7} = 'shop: kitchen';
            case 'shop: living room'
                % Check objects by looking at relevant furniture line
                for furi = 76:99
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p1_pixel_x,p1_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,4}, '')
                            mocapfield{i,4} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,4} = strcat(mocapfield{i,4}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,7} = 'shop: living room';
            case 'shop: misc'
                % Check objects by looking at relevant furniture line
                for furi = 100:126
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p1_pixel_x,p1_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,4}, '')
                            mocapfield{i,4} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,4} = strcat(mocapfield{i,4}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,7} = 'shop: misc';
            case 'shop: rugs'
                % Check objects by looking at relevant furniture line
                for furi = 127:141
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p1_pixel_x,p1_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,4}, '')
                            mocapfield{i,4} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,4} = strcat(mocapfield{i,4}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,7} = 'shop: rugs';

            case 'flat'
                % Check objects in appline
                a = 6;
                while a < furniturecsvcol % Change step for case where there is more furniture (or less) than 170
                    if strcmp(appd{a}, 'NULL') == 0
                        % Check distance closer than threshold
                        gazepoint = [p1_pixel_x,p1_pixel_y];
                        furpoint = [str2num(appd{a+1}),str2num(appd{a+2})];
                        dist = norm(gazepoint - furpoint);
                        % Write and append all objects
                        if dist <= object_threshold
                            if strcmp(mocapfield{i,4}, '')
                                mocapfield{i,4} = strcat('|', num2str(appd{a}), '@', num2str(fix(dist)), '|');
                            else
                                mocapfield{i,4} = strcat(mocapfield{i,4}, strcat(num2str(appd{a}), '@', num2str(fix(dist)), '|'));
                            end
                        end
                    end
                    a = a + 5;
                end

                % Check room
                for r = 1:9
                    if (p1_pixel_x >= room{r,1}) && (p1_pixel_x <= room{r,2}) && (p1_pixel_y >= room{r,3}) && (p1_pixel_y <= room{r,4})
                        mocapfield{i,7} = int2str(r);
                    end
                end
        end
    end
    
    % Write human values for P1
    if gaze_hits_mp1 == 1
        mocapfield{i,4} = 'M';
    end
    if gaze_hits_p2p1 == 1
        mocapfield{i,4} = 'P2';
    end

    % P2
    % Calculate hits for P2 to moderator
    dist_mp2 = calc_norm(glassesm-glassesp2);
    collision_ang_mp2 = atan(head_radius./dist_mp2);
    gaze_ang_mp2 = calc_angle(gaze_vecp2-glassesp2, glassesm-glassesp2);
    gaze_hits_mp2 = gaze_ang_mp2 <= collision_ang_mp2;

    % Calculate hits for P2 to P1
    dist_p1p2 = calc_norm(glassesp1-glassesp2);
    collision_ang_p1p2 = atan(head_radius./dist_p1p2);
    gaze_ang_p1p2 = calc_angle(gaze_vecp2-glassesp2, glassesp1-glassesp2);
    gaze_hits_p1p2 = gaze_ang_p1p2 <= collision_ang_p1p2;

    % Calculate hits for P2 to screen
    % Create 3d line from points
    p2_gazeline = createLine3d([gp2z gp2y gp2x], [gpp2z gpp2y gpp2x]);
    screen_hits_p2 = intersectLinePlane(p2_gazeline, screenplane);
    %if ((screen_hits_p2(1) >= -0.05 - screen_threshold) && (screen_hits_p2(1) <= 0.88 + screen_threshold) && ((screen_hits_p2(3) >= -0.47 - screen_threshold) && (screen_hits_p2(3) <= 0.05 + screen_threshold)))
    if ((screen_hits_p2(1) >= -0.05) && (screen_hits_p2(1) <= 0.88) && ((screen_hits_p2(3) >= -0.47) && (screen_hits_p2(3) <= 0.05)))
        % Convert x and y to pixels
        p2_pixel_x = ((screen_hits_p2(1) + 0.05) / 0.93) * 1280;
        % For moderator inverse x
        p2_pixel_x = abs(p2_pixel_x - 1280);
        p2_pixel_y = ((screen_hits_p2(3) + 0.47) / 0.52) * 720;

        % Initiate field
        %mocapfield{i,5} = 'screen';
        %mocapfield{i,8} = 'screen';
        mocapfield{i,5} = '';
        mocapfield{i,8} = '';

        % Check what screen/room/object it currently is and update field
        switch appd{5}
            case 'black'
                % App has not started yet (black screen)
                %mocapfield{i,5} = 'black';
                %mocapfield{i,8} = 'black';
                mocapfield{i,5} = '';
                mocapfield{i,8} = '';

            case 'shop: bathroom'
                % Check objects by looking at relevant furniture line
                for furi = 2:35
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p2_pixel_x,p2_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,5}, '')
                            mocapfield{i,5} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,5} = strcat(mocapfield{i,5}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,8} = 'shop: bathroom';
            case 'shop: bedroom'
                % Check objects by looking at relevant furniture line
                for furi = 36:51
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p2_pixel_x,p2_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,5}, '')
                            mocapfield{i,5} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,5} = strcat(mocapfield{i,5}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,8} = 'shop: bedroom';
            case 'shop: kitchen'
                % Check objects by looking at relevant furniture line
                for furi = 52:75
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p2_pixel_x,p2_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,5}, '')
                            mocapfield{i,5} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,5} = strcat(mocapfield{i,5}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,8} = 'shop: kitchen';
            case 'shop: living room'
                % Check objects by looking at relevant furniture line
                for furi = 76:99
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p2_pixel_x,p2_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,5}, '')
                            mocapfield{i,5} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,5} = strcat(mocapfield{i,5}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,8} = 'shop: living room';
            case 'shop: misc'
                % Check objects by looking at relevant furniture line
                for furi = 100:126
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p2_pixel_x,p2_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,5}, '')
                            mocapfield{i,5} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,5} = strcat(mocapfield{i,5}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,8} = 'shop: misc';
            case 'shop: rugs'
                % Check objects by looking at relevant furniture line
                for furi = 127:141
                    furlines(furi) = textscan(furnituredata{furi}, '%s', 'delimiter', ';');
                    furd = furlines{furi};

                    % Check distance closer than threshold
                    gazepoint = [p2_pixel_x,p2_pixel_y];
                    shopfurpoint = [str2num(furd{9}),str2num(furd{10})];
                    dist = norm(gazepoint - shopfurpoint);
                    % Write and append all objects
                    if dist <= object_threshold
                        if strcmp(mocapfield{i,5}, '')
                            mocapfield{i,5} = strcat('|', num2str(furd{1}), '@', num2str(fix(dist)), '|');
                        else
                            mocapfield{i,5} = strcat(mocapfield{i,5}, strcat(num2str(furd{1}), '@', num2str(fix(dist)), '|'));
                        end
                    end
                end
                % Write location
                mocapfield{i,8} = 'shop: rugs';

            case 'flat'
                % Check objects in appline
                a = 6;
                while a < furniturecsvcol % Change step for case where there is more furniture (or less) than 170
                    if strcmp(appd{a}, 'NULL') == 0
                        % Check distance closer than threshold
                        gazepoint = [p2_pixel_x,p2_pixel_y];
                        furpoint = [str2num(appd{a+1}),str2num(appd{a+2})];
                        dist = norm(gazepoint - furpoint);
                        % Write and append all objects
                        if dist <= object_threshold
                            if strcmp(mocapfield{i,5}, '')
                                mocapfield{i,5} = strcat('|', num2str(appd{a}), '@', num2str(fix(dist)), '|');
                            else
                                mocapfield{i,5} = strcat(mocapfield{i,5}, strcat(num2str(appd{a}), '@', num2str(fix(dist)), '|'));
                            end
                        end
                    end
                    a = a + 5;
                end

                % Check room
                for r = 1:9
                    if (p2_pixel_x >= room{r,1}) && (p2_pixel_x <= room{r,2}) && (p2_pixel_y >= room{r,3}) && (p2_pixel_y <= room{r,4})
                        mocapfield{i,8} = int2str(r);
                    end
                end
        end
    end
    
    % Write human values for P2
    if gaze_hits_mp2 == 1
        mocapfield{i,5} = 'M';
    end
    if gaze_hits_p1p2 == 1
        mocapfield{i,5} = 'P1';
    end

    % Add ASR for all three participants
    asri = i / 12;
    if (i == 1) || (floor(asri) == asri)
        asrlines(asri + 6) = textscan(asrdata{asri + 6}, '%s', 'delimiter', ',');
        asrd = asrlines{asri + 6};

        % Fix error where last utterance is empty and put a space
        if size(asrd,1) < 5
            asrd(5) = {''};
        end
    end

    % Put asr in fields
    mocapfield{i,9} = asrd(5);
    mocapfield{i,10} = asrd(3);
    mocapfield{i,11} = asrd(4);
    
    % Display progress
    counter = i / 120;
    if floor(counter) == counter
        disp(counter)
    end
end

fclose(fid1);
fclose(fid2);
fclose(fid3);
fclose(fid4);

% Write to csv
fid5 = fopen(outfile, 'wt');
for k = 1:size(mocapfield, 1)
    for l = 1:11
        put = char(mocapfield{k,l});
        fprintf(fid5, '%s,', put);
    end
    fprintf(fid5, '\n');
end
fclose(fid5);
