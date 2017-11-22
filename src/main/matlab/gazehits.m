function [data] = gazehits(jsonfile)
% Parses processed json file and reproduces gaze hits

% Define a threshold around head mid point (20cm)
head_radius = 0.2;

% Define a threshold around the object (10cm)
object_radius = 0.1;

% % First check if gaze intersects with human or with object
% for i = 7:(size(mocapdata, 1) - 7)
%     % Init gaze and furpoints
%     gazepoint = [0,0];
%     
%     mocaplines(i) = textscan(mocapdata{i}, '%s', 'delimiter', ',');
%     
%     % First make all fields NULL
%     for z = 1:8
%         mocapfield{i,z} = {''};
%     end
%     
%     % Take mocap line
%     d = mocaplines{i};
% 
%     % Fix error where a few times last gp3/headpose is missing and put a zero
%     if size(d,1) == 168
%         d(169) = {'0'};
%     end
% 
%     % Put frame and time
%     mocapfield{i,1} = d(1);
%     mocapfield{i,2} = d(2);
% 
%     % Get glasses
%     % Get Moderator glasses position
%     glasses_mod_left = {d(9), d(10), d(11)};
%     glasses_mod_right = {d(6), d(7), d(8)};
%     gmx = (str2double(d{9,1}) + str2double(d{6,1})) / 2;
%     gmy = (str2double(d{10,1}) + str2double(d{7,1})) / 2;
%     gmz = (str2double(d{11,1}) + str2double(d{8,1})) / 2;
%     %glasses_mod_mid = {gmx, gmy, gmz};
% 
%     % Get P1 glasses position
%     glasses_p1_left = {d(21), d(22), d(23)};
%     glasses_p1_right = {d(15), d(16), d(17)};
%     gp1x = (str2double(d{21,1}) + str2double(d{15,1})) / 2;
%     gp1y = (str2double(d{22,1}) + str2double(d{16,1})) / 2;
%     gp1z = (str2double(d{23,1}) + str2double(d{17,1})) / 2;
%     %glasses_p1_mid = {gp1x, gp1y, gp1z};
% 
%     % Get P2 glasses position
%     glasses_p2_left = {d(27), d(28), d(29)};
%     glasses_p2_right = {d(30), d(31), d(32)};
%     gp2x = (str2double(d{27,1}) + str2double(d{30,1})) / 2;
%     gp2y = (str2double(d{28,1}) + str2double(d{31,1})) / 2;
%     gp2z = (str2double(d{29,1}) + str2double(d{32,1})) / 2;
%     %glasses_p2_mid = {gp2x, gp2y, gp2z};
% 
%     % Get gaze
%     % Get Moderator gaze position
%     gpmx = str2double(d(141));
%     gpmy = str2double(d(142));
%     gpmz = str2double(d(143));
%     %gaze_mod = {gpmx, gpmy, gpmz};
% 
%     % Get P1 gaze position
%     gpp1x = str2double(d(153));
%     gpp1y = str2double(d(154));
%     gpp1z = str2double(d(155));
%     %gaze_p1 = {gpp1x, gpp1y, gpp1z};
% 
%     % Get P2 gaze position
%     gpp2x = str2double(d(165));
%     gpp2y = str2double(d(166));
%     gpp2z = str2double(d(167));
%     %gaze_p2 = {gpp2x, gpp2y, gpp2z};
% 
%     % Get gaze vectors
%     gaze_vecm = [gpmx, gpmz, gpmy];
%     gaze_vecp1 = [gpp1x, gpp1z, gpp1y];
%     gaze_vecp2 = [gpp2x, gpp2z, gpp2y];
% 
%     % Get glasses positions
%     glassesm = [gmx, gmz, gmy];
%     glassesp1 = [gp1x, gp1z, gp1y];
%     glassesp2 = [gp2x, gp2z, gp2y];
%     
%     % Get objects
%     % Get object 1 position
%     object_1_left = {d(45), d(46), d(47)};
%     object_1_right = {d(39), d(40), d(41)};
%     o1x = (str2double(d{45,1}) + str2double(d{39,1})) / 2;
%     o1y = (str2double(d{46,1}) + str2double(d{40,1})) / 2;
%     o1z = (str2double(d{47,1}) + str2double(d{41,1})) / 2;
%     
%     % Get object 2 position
%     object_2_left = {d(60), d(61), d(62)};
%     object_2_right = {d(57), d(58), d(59)};
%     o2x = (str2double(d{60,1}) + str2double(d{57,1})) / 2;
%     o2y = (str2double(d{61,1}) + str2double(d{58,1})) / 2;
%     o2z = (str2double(d{62,1}) + str2double(d{59,1})) / 2;
%     
%     % Get object 3 position
%     object_3_left = {d(66), d(67), d(68)};
%     object_2_right = {d(72), d(73), d(74)};
%     o3x = (str2double(d{66,1}) + str2double(d{72,1})) / 2;
%     o3y = (str2double(d{67,1}) + str2double(d{73,1})) / 2;
%     o3z = (str2double(d{68,1}) + str2double(d{74,1})) / 2;
%     
%     % Get object 4 position
%     object_4_left = {d(81), d(82), d(83)};
%     object_4_right = {d(75), d(76), d(77)};
%     o4x = (str2double(d{81,1}) + str2double(d{75,1})) / 2;
%     o4y = (str2double(d{82,1}) + str2double(d{76,1})) / 2;
%     o4z = (str2double(d{83,1}) + str2double(d{77,1})) / 2;
%     
%     % Get object 5 position
%     object_5_left = {d(90), d(91), d(92)};
%     object_5_right = {d(93), d(94), d(95)};
%     o5x = (str2double(d{90,1}) + str2double(d{93,1})) / 2;
%     o5y = (str2double(d{91,1}) + str2double(d{94,1})) / 2;
%     o5z = (str2double(d{92,1}) + str2double(d{95,1})) / 2;
%     
%     % Get object 6 position
%     object_6_left = {d(102), d(103), d(104)};
%     object_6_right = {d(108), d(109), d(110)};
%     o6x = (str2double(d{102,1}) + str2double(d{108,1})) / 2;
%     o6y = (str2double(d{103,1}) + str2double(d{109,1})) / 2;
%     o6z = (str2double(d{104,1}) + str2double(d{110,1})) / 2;
%     
%     % Get object 7 position
%     object_7_left = {d(114), d(115), d(116)};
%     object_7_right = {d(111), d(112), d(113)};
%     o7x = (str2double(d{114,1}) + str2double(d{111,1})) / 2;
%     o7y = (str2double(d{115,1}) + str2double(d{112,1})) / 2;
%     o7z = (str2double(d{116,1}) + str2double(d{113,1})) / 2;
%     
%     % Get object 8 position
%     object_8_left = {d(123), d(124), d(125)};
%     object_8_right = {d(129), d(130), d(131)};
%     o8x = (str2double(d{123,1}) + str2double(d{129,1})) / 2;
%     o8y = (str2double(d{124,1}) + str2double(d{130,1})) / 2;
%     o8z = (str2double(d{125,1}) + str2double(d{131,1})) / 2;
%     
%     % Get objects positions
%     object1 = [o1x, o1z, o1y];
%     object2 = [o2x, o2z, o2y];
%     object3 = [o3x, o3z, o3y];
%     object4 = [o4x, o4z, o4y];
%     object5 = [o5x, o5z, o5y];
%     object6 = [o6x, o6z, o6y];
%     object7 = [o7x, o7z, o7y];
%     object8 = [o8x, o8z, o8y];
% 
%     % Moderator
%     % Calculate hits for moderator to P1
%     dist_p1m = calc_norm(glassesp1-glassesm);
%     collision_ang_p1m = atan(head_radius./dist_p1m);
%     gaze_ang_p1m = calc_angle(gaze_vecm-glassesm, glassesp1-glassesm);
%     gaze_hits_p1m = gaze_ang_p1m <= collision_ang_p1m;
% 
%     % Calculate hits for moderator to P2
%     dist_p2m = calc_norm(glassesp2-glassesm);
%     collision_ang_p2m = atan(head_radius./dist_p2m);
%     gaze_ang_p2m = calc_angle(gaze_vecm-glassesm, glassesp2-glassesm);
%     gaze_hits_p2m = gaze_ang_p2m <= collision_ang_p2m;
% 
%     % Write human values for Moderator
%     if gaze_hits_p1m == 1
%         mocapfield{i,3} = 'P1';
%     end
%     if gaze_hits_p2m == 1
%         mocapfield{i,3} = 'P2';
%     end
%     
%     % Calculate hits for moderator to O1
%     dist_o1m = calc_norm(object1-glassesm);
%     collision_ang_o1m = atan(object_radius./dist_o1m);
%     gaze_ang_o1m = calc_angle(gaze_vecm-glassesm, object1-glassesm);
%     gaze_hits_o1m = gaze_ang_o1m <= collision_ang_o1m;
%     
%     % Calculate hits for moderator to O2
%     dist_o2m = calc_norm(object2-glassesm);
%     collision_ang_o2m = atan(object_radius./dist_o2m);
%     gaze_ang_o2m = calc_angle(gaze_vecm-glassesm, object2-glassesm);
%     gaze_hits_o2m = gaze_ang_o2m <= collision_ang_o2m;
%     
%     % Calculate hits for moderator to O3
%     dist_o3m = calc_norm(object3-glassesm);
%     collision_ang_o3m = atan(object_radius./dist_o3m);
%     gaze_ang_o3m = calc_angle(gaze_vecm-glassesm, object3-glassesm);
%     gaze_hits_o3m = gaze_ang_o3m <= collision_ang_o3m;
%     
%     % Calculate hits for moderator to O4
%     dist_o4m = calc_norm(object4-glassesm);
%     collision_ang_o4m = atan(object_radius./dist_o4m);
%     gaze_ang_o4m = calc_angle(gaze_vecm-glassesm, object4-glassesm);
%     gaze_hits_o4m = gaze_ang_o4m <= collision_ang_o4m;
%     
%     % Calculate hits for moderator to O5
%     dist_o5m = calc_norm(object5-glassesm);
%     collision_ang_o5m = atan(object_radius./dist_o5m);
%     gaze_ang_o5m = calc_angle(gaze_vecm-glassesm, object5-glassesm);
%     gaze_hits_o5m = gaze_ang_o5m <= collision_ang_o5m;
%     
%     % Calculate hits for moderator to O6
%     dist_o6m = calc_norm(object6-glassesm);
%     collision_ang_o6m = atan(object_radius./dist_o6m);
%     gaze_ang_o6m = calc_angle(gaze_vecm-glassesm, object6-glassesm);
%     gaze_hits_o6m = gaze_ang_o6m <= collision_ang_o6m;
%     
%     % Calculate hits for moderator to O7
%     dist_o7m = calc_norm(object7-glassesm);
%     collision_ang_o7m = atan(object_radius./dist_o7m);
%     gaze_ang_o7m = calc_angle(gaze_vecm-glassesm, object7-glassesm);
%     gaze_hits_o7m = gaze_ang_o7m <= collision_ang_o7m;
%     
%     % Calculate hits for moderator to O8
%     dist_o8m = calc_norm(object8-glassesm);
%     collision_ang_o8m = atan(object_radius./dist_o8m);
%     gaze_ang_o8m = calc_angle(gaze_vecm-glassesm, object8-glassesm);
%     gaze_hits_o8m = gaze_ang_o8m <= collision_ang_o8m;
%     
%     % Write object values for Moderator
%     if gaze_hits_o1m == 1
%         mocapfield{i,3} = 'O1';
%     end
%     if gaze_hits_o2m == 1
%         mocapfield{i,3} = 'O2';
%     end
%     if gaze_hits_o3m == 1
%         mocapfield{i,3} = 'O3';
%     end
%     if gaze_hits_o4m == 1
%         mocapfield{i,3} = 'O4';
%     end
%     if gaze_hits_o5m == 1
%         mocapfield{i,3} = 'O5';
%     end
%     if gaze_hits_o6m == 1
%         mocapfield{i,3} = 'O6';
%     end
%     if gaze_hits_o7m == 1
%         mocapfield{i,3} = 'O7';
%     end
%     if gaze_hits_o8m == 1
%         mocapfield{i,3} = 'O8';
%     end
% 
%     % P1
%     % Calculate hits for P1 to moderator
%     dist_mp1 = calc_norm(glassesm-glassesp1);
%     collision_ang_mp1 = atan(head_radius./dist_mp1);
%     gaze_ang_mp1 = calc_angle(gaze_vecp1-glassesp1, glassesm-glassesp1);
%     gaze_hits_mp1 = gaze_ang_mp1 <= collision_ang_mp1;
% 
%     % Calculate hits for P1 to P2
%     dist_p2p1 = calc_norm(glassesp2-glassesp1);
%     collision_ang_p2p1 = atan(head_radius./dist_p2p1);
%     gaze_ang_p2p1 = calc_angle(gaze_vecp1-glassesp1, glassesp2-glassesp1);
%     gaze_hits_p2p1 = gaze_ang_p2p1 <= collision_ang_p2p1;
%     
%     % Write human values for P1
%     if gaze_hits_mp1 == 1
%         mocapfield{i,4} = 'M';
%     end
%     if gaze_hits_p2p1 == 1
%         mocapfield{i,4} = 'P2';
%     end
%     
%     % Calculate hits for P1 to O1
%     dist_o1p1 = calc_norm(object1-glassesp1);
%     collision_ang_o1p1 = atan(object_radius./dist_o1p1);
%     gaze_ang_o1p1 = calc_angle(gaze_vecp1-glassesp1, object1-glassesp1);
%     gaze_hits_o1p1 = gaze_ang_o1p1 <= collision_ang_o1p1;
%     
%     % Calculate hits for P1 to O2
%     dist_o2p1 = calc_norm(object2-glassesp1);
%     collision_ang_o2p1 = atan(object_radius./dist_o2p1);
%     gaze_ang_o2p1 = calc_angle(gaze_vecp1-glassesp1, object2-glassesp1);
%     gaze_hits_o2p1 = gaze_ang_o2p1 <= collision_ang_o2p1;
%     
%     % Calculate hits for P1 to O3
%     dist_o3p1 = calc_norm(object3-glassesp1);
%     collision_ang_o3p1 = atan(object_radius./dist_o3p1);
%     gaze_ang_o3p1 = calc_angle(gaze_vecp1-glassesp1, object3-glassesp1);
%     gaze_hits_o3p1 = gaze_ang_o3p1 <= collision_ang_o3p1;
%     
%     % Calculate hits for P1 to O4
%     dist_o4p1 = calc_norm(object4-glassesp1);
%     collision_ang_o4p1 = atan(object_radius./dist_o4p1);
%     gaze_ang_o4p1 = calc_angle(gaze_vecp1-glassesp1, object4-glassesp1);
%     gaze_hits_o4p1 = gaze_ang_o4p1 <= collision_ang_o4p1;
%     
%     % Calculate hits for P1 to O5
%     dist_o5p1 = calc_norm(object5-glassesp1);
%     collision_ang_o5p1 = atan(object_radius./dist_o5p1);
%     gaze_ang_o5p1 = calc_angle(gaze_vecp1-glassesp1, object5-glassesp1);
%     gaze_hits_o5p1 = gaze_ang_o5p1 <= collision_ang_o5p1;
%     
%     % Calculate hits for P1 to O6
%     dist_o6p1 = calc_norm(object6-glassesp1);
%     collision_ang_o6p1 = atan(object_radius./dist_o6p1);
%     gaze_ang_o6p1 = calc_angle(gaze_vecp1-glassesp1, object6-glassesp1);
%     gaze_hits_o6p1 = gaze_ang_o6p1 <= collision_ang_o6p1;
%     
%     % Calculate hits for P1 to O7
%     dist_o7p1 = calc_norm(object7-glassesp1);
%     collision_ang_o7p1 = atan(object_radius./dist_o7p1);
%     gaze_ang_o7p1 = calc_angle(gaze_vecp1-glassesp1, object7-glassesp1);
%     gaze_hits_o7p1 = gaze_ang_o7p1 <= collision_ang_o7p1;
%     
%     % Calculate hits for P1 to O8
%     dist_o8p1 = calc_norm(object8-glassesp1);
%     collision_ang_o8p1 = atan(object_radius./dist_o8p1);
%     gaze_ang_o8p1 = calc_angle(gaze_vecp1-glassesp1, object8-glassesp1);
%     gaze_hits_o8p1 = gaze_ang_o8p1 <= collision_ang_o8p1;
%     
%     % Write object values for P1
%     if gaze_hits_o1p1 == 1
%         mocapfield{i,4} = 'O1';
%     end
%     if gaze_hits_o2p1 == 1
%         mocapfield{i,4} = 'O2';
%     end
%     if gaze_hits_o3p1 == 1
%         mocapfield{i,4} = 'O3';
%     end
%     if gaze_hits_o4p1 == 1
%         mocapfield{i,4} = 'O4';
%     end
%     if gaze_hits_o5p1 == 1
%         mocapfield{i,4} = 'O5';
%     end
%     if gaze_hits_o6p1 == 1
%         mocapfield{i,4} = 'O6';
%     end
%     if gaze_hits_o7p1 == 1
%         mocapfield{i,4} = 'O7';
%     end
%     if gaze_hits_o8p1 == 1
%         mocapfield{i,4} = 'O8';
%     end
% 
%     % P2
%     % Calculate hits for P2 to moderator
%     dist_mp2 = calc_norm(glassesm-glassesp2);
%     collision_ang_mp2 = atan(head_radius./dist_mp2);
%     gaze_ang_mp2 = calc_angle(gaze_vecp2-glassesp2, glassesm-glassesp2);
%     gaze_hits_mp2 = gaze_ang_mp2 <= collision_ang_mp2;
% 
%     % Calculate hits for P2 to P1
%     dist_p1p2 = calc_norm(glassesp1-glassesp2);
%     collision_ang_p1p2 = atan(head_radius./dist_p1p2);
%     gaze_ang_p1p2 = calc_angle(gaze_vecp2-glassesp2, glassesp1-glassesp2);
%     gaze_hits_p1p2 = gaze_ang_p1p2 <= collision_ang_p1p2;
%     
%     % Write human values for P2
%     if gaze_hits_mp2 == 1
%         mocapfield{i,5} = 'M';
%     end
%     if gaze_hits_p1p2 == 1
%         mocapfield{i,5} = 'P1';
%     end
%     
%     % Calculate hits for P2 to O1
%     dist_o1p2 = calc_norm(object1-glassesp2);
%     collision_ang_o1p2 = atan(object_radius./dist_o1p2);
%     gaze_ang_o1p2 = calc_angle(gaze_vecp2-glassesp2, object1-glassesp2);
%     gaze_hits_o1p2 = gaze_ang_o1p2 <= collision_ang_o1p2;
%     
%     % Calculate hits for P2 to O2
%     dist_o2p2 = calc_norm(object2-glassesp2);
%     collision_ang_o2p2 = atan(object_radius./dist_o2p2);
%     gaze_ang_o2p2 = calc_angle(gaze_vecp2-glassesp2, object2-glassesp2);
%     gaze_hits_o2p2 = gaze_ang_o2p2 <= collision_ang_o2p2;
%     
%     % Calculate hits for P2 to O3
%     dist_o3p2 = calc_norm(object3-glassesp2);
%     collision_ang_o3p2 = atan(object_radius./dist_o3p2);
%     gaze_ang_o3p2 = calc_angle(gaze_vecp2-glassesp2, object3-glassesp2);
%     gaze_hits_o3p2 = gaze_ang_o3p2 <= collision_ang_o3p2;
%     
%     % Calculate hits for P2 to O4
%     dist_o4p2 = calc_norm(object4-glassesp2);
%     collision_ang_o4p2 = atan(object_radius./dist_o4p2);
%     gaze_ang_o4p2 = calc_angle(gaze_vecp2-glassesp2, object4-glassesp2);
%     gaze_hits_o4p2 = gaze_ang_o4p2 <= collision_ang_o4p2;
%     
%     % Calculate hits for P2 to O5
%     dist_o5p2 = calc_norm(object5-glassesp2);
%     collision_ang_o5p2 = atan(object_radius./dist_o5p2);
%     gaze_ang_o5p2 = calc_angle(gaze_vecp2-glassesp2, object5-glassesp2);
%     gaze_hits_o5p2 = gaze_ang_o5p2 <= collision_ang_o5p2;
%     
%     % Calculate hits for P2 to O6
%     dist_o6p2 = calc_norm(object6-glassesp2);
%     collision_ang_o6p2 = atan(object_radius./dist_o6p2);
%     gaze_ang_o6p2 = calc_angle(gaze_vecp2-glassesp2, object6-glassesp2);
%     gaze_hits_o6p2 = gaze_ang_o6p2 <= collision_ang_o6p2;
%     
%     % Calculate hits for P2 to O7
%     dist_o7p2 = calc_norm(object7-glassesp2);
%     collision_ang_o7p2 = atan(object_radius./dist_o7p2);
%     gaze_ang_o7p2 = calc_angle(gaze_vecp2-glassesp2, object7-glassesp2);
%     gaze_hits_o7p2 = gaze_ang_o7p2 <= collision_ang_o7p2;
%     
%     % Calculate hits for P2 to O8
%     dist_o8p2 = calc_norm(object8-glassesp2);
%     collision_ang_o8p2 = atan(object_radius./dist_o8p2);
%     gaze_ang_o8p2 = calc_angle(gaze_vecp2-glassesp2, object8-glassesp2);
%     gaze_hits_o8p2 = gaze_ang_o8p2 <= collision_ang_o8p2;
%     
%     % Write object values for P2
%     if gaze_hits_o1p2 == 1
%         mocapfield{i,5} = 'O1';
%     end
%     if gaze_hits_o2p2 == 1
%         mocapfield{i,5} = 'O2';
%     end
%     if gaze_hits_o3p2 == 1
%         mocapfield{i,5} = 'O3';
%     end
%     if gaze_hits_o4p2 == 1
%         mocapfield{i,5} = 'O4';
%     end
%     if gaze_hits_o5p2 == 1
%         mocapfield{i,5} = 'O5';
%     end
%     if gaze_hits_o6p2 == 1
%         mocapfield{i,5} = 'O6';
%     end
%     if gaze_hits_o7p2 == 1
%         mocapfield{i,5} = 'O7';
%     end
%     if gaze_hits_o8p2 == 1
%         mocapfield{i,5} = 'O8';
%     end
% 
%     % Add ASR for all three participants
% %     asri = i / 12;
% %     if (i == 1) || (floor(asri) == asri)
% %         asrlines(asri + 6) = textscan(asrdata{asri + 6}, '%s', 'delimiter', ',');
% %         asrd = asrlines{asri + 6};
% % 
% %         % Fix error where last utterance is empty and put a space
% %         if size(asrd,1) < 5
% %             asrd(5) = {''};
% %         end
% %     end
% 
%     % Put asr in fields
% %     mocapfield{i,9} = asrd(5);
% %     mocapfield{i,10} = asrd(3);
% %     mocapfield{i,11} = asrd(4);
%     
%     % Display progress
%     counter = i / 50;
%     if floor(counter) == counter
%         disp(counter)
%     end
% end
% 
% %fclose(fid3);
% fclose(fid4);
% 
% % Write to csv
% fid5 = fopen(outfile, 'wt');
% for k = 1:size(mocapfield, 1)
%     for l = 1:8
%         put = char(mocapfield{k,l});
%         fprintf(fid5, '%s,', put);
%     end
%     fprintf(fid5, '\n');
% end
% fclose(fid5);
disp(jsonfile);
data = jsonfile;