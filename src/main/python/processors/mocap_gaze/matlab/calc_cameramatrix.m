% calculates camera calibration from synced video and mocap data

markerset = 'Alejandro';
markers = {'HeadFront', 'LShoulderTop', 'RShoulderTop', 'RWristIn', 'RWristOut', 'RElbowOut', 'LHandOut'}
%markers = {'RWristIn', 'LElbowOut', 'LShoulderTop', 'RShoulderTop', 'Chest', 'HeadFront', 'LKneeOut', 'RT2', 'RI2', 'LM2'}
video_framerate = 25;
mocap_framerate = 120;
mocap_file = 'C:\Users\Simon\Documents\mimebot\FB_FRUST_RELAX\mocap\cut.trc';
%mocap_file = 'D:\processed\FB_FRUST_RELAX\mocap\mocap_final.trc';
[PP, L, H, t] = mocapread_trc(mocap_file);

inds = find_markerindices(L, add_markerprefix(markers, markerset));
worldPoints = [];
screenPoints = [];
for i = 1:length(markers)
    %A = dlmread(sprintf('C:\\tmp\\tr_zed_left_0448_%s.csv', markers{i}));
    A = dlmread(sprintf('C:\\Users\\Simon\\Documents\\mimebot\\FB_FRUST_RELAX\\video_overlay\\%s.csv', markers{i}));
    frameNos = round(A(:,3)*mocap_framerate/video_framerate);
    worldPoints = [worldPoints; PP(frameNos,:,inds(i))];
    screenPoints = [screenPoints;A(:,1:2)];
end
[Pc, K, R, T] = get_camera_matrix(screenPoints', worldPoints');
[yaw, pitch, roll] = dcm2angle(R);
eul = [yaw, pitch, roll]*180/pi
