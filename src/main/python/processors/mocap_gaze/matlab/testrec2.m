% Process performance capture data from a setup containing fulldata mocap
% (processed by motive), and gaze data from tobii glasses
 
% File names and directories
% Mocap
mocapfile = sprintf('../data/testrec2/mocap/mocap.csv');
 
% Tobii
gazefiles = {sprintf('../data/testrec2/gaze/gaze.json')};
 
% Microphones
audiofile = {sprintf('../data/testrec2/audio/mic.wav')};
 
% Sync
mocap_syncfile = sprintf('../data/testrec2/audio/mocap-sync.wav');
audio_tobii = {sprintf('../data/testrec2/audio/tobii-sync.wav')};
 
% Output
mocapoutfile = sprintf('../data/testrec2/output/mocap.trc');
mocapoutcsvfile = sprintf('../data/testrec2/output/mocap.csv');
 
% Parse performance data
[DATA, labels, types, t] = mocapread_csv2matrix(mocapfile);
mocap_data.timestamps = t;
mocap_data.data = DATA;
 
% Parse gaze data
nEyetrackers = 1;
for i=1:nEyetrackers
    [timestamps, gazedata, syncpulse_ts, video_ts] = parse_tobii(gazefiles{i});
    gaze_data{i}.timestamps = timestamps;
    gaze_data{i}.gazedata = gazedata;
    gaze_data{i}.syncpulse_ts = syncpulse_ts;
    gaze_data{i}.video_ts = video_ts;
end
 
% Check time syncing
[gaze, mocap] = sync_gaze_and_mocap(audio_tobii, audiofile, mocap_syncfile, mocap_data, gaze_data, 120, 20, 'pulse', 'pulse');
 
% Extract rigid body data
tobii_rgbName = 'Glasses';
tobii_rgbdata = extract_rigidbodydata(mocap, labels, tobii_rgbName);
 
% Calculate a transform from rigidbody coordinates to tobii glasses
% coordinates, assuming there are 2 markers on the front, and 2 markers
% at the back
front_left_marker = 1;
front_right_marker = 4;
back_left_marker = 2;
back_right_marker = 3;
 
% Transform markers to rigid body coordinates
gd = gaze{1};
 
% Clamp the gaze target as this seem to be unreliable
gd.gp3 = clamp_magnitude(gd.gp3, 2, Inf);
% Assemble tobii data. Only 3 markers are used, the forth (back right) is
% not necessary as it is only used for robustness. The back left marker is
% positioned always at the same place for all glasses, while the back right
% position varies.
tobii_data = assemble_tobii_data(gd, tobii_rgbdata, front_left_marker, front_right_marker, back_left_marker);
 
% Trim errors and smooth gaze data
Pgaze = trim_trails(matrix2points([tobii_data.gazeLeftDir_w, tobii_data.gazeRightDir_w, tobii_data.gaze3D_w]), 10, 10);
Pgaze_sm = mocap_smooth(Pgaze, 100, 'moving');
 
[Plabeled, outlabels] = extract_labeledmarkers(mocap, labels, types);
Ptot = mc_append(Plabeled, Pgaze_sm);
%outlbls = [outlabels, {'gaze_left', 'gaze_right', 'gaze_target'}];
% Manual labelling
%outlbls = [{'gaze_target:marker1', 'gaze_target:marker2', 'gaze_target:marker3', 'tobii_glasses_3:mark1', 'tobii_glasses_3:mark2', 'tobii_glasses_3:mark3', 'gaze_left', 'gaze_right', 'gaze_target'}];
outlbls = [{'glasses_3:m1a', 'glasses_3:m2a', 'glasses_3:m3a', 'glasses_3:m4a', 'hand_l1:m1b', 'hand_l1:m2b', 'hand_l1:m3b', 'hand_l1:m4b', 'hand_r1:m1c', 'hand_r1:m2c', 'hand_r1:m3c', 'hand_r1:m4c', 'screen:m1d', 'screen:m2d', 'screen:m3d', 'screen:m4d', 'gaze_left', 'gaze_right', 'gaze_target'}];
mocapwrite_trc(mocapoutfile, Ptot, outlbls, 1/120, 0);
mocapwrite_trc(mocapoutcsvfile, Ptot, outlbls, 1/120, 0);
 
%pseudocode from annotate_gaze.m
% for each tobii glasses
%     for each target point
%         
%         %calcalute delta position
%         Pij = target position (pt2) - tobii position
%         gaze_vec = gaze target position (gp3) - tobii position
%         
%         error_radius = 0.2;
%         dist_ij = calc_norm(Pij);
%         thres_ang = atan(error_radius./dist_ij);
%         gaze_to_target_ang = calc_angle(gaze_vec, Pij);
%         
%         gaze_hits = gaze_to_target_ang<=tres_ang;
%         write_annotation(bin2interv(gaze_hits, nFrames), 'gaze', fileName);
% 
%     end
% end