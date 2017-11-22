function [gaze, mocap, maxStartTime, minEndTime] =  sync_gaze_and_mocap(gaze_syncfiles, gaze_masteraudio, mocap_syncfile, mocap_data, gaze_data, resampleFrameRate, nsec, gazesync_method, mocapsync_method)

% read gaze sync.
    nEyetrackers = size(gaze_syncfiles, 2);
    gaze_starttimes = zeros(nEyetrackers,1);
    gaze_ts = zeros(nEyetrackers,1); % timestamps the gaze data first frame
    
    % find the start and end times from the audio reference channel
    start_synctimes = zeros(nEyetrackers+1,1);
    end_synctimes = zeros(nEyetrackers+1,1);
    for i=1:nEyetrackers
        if (strcmp(gazesync_method, 'pulse'))
            [Xg,fsg] = audioread(gaze_syncfiles{i}{1});
            [Ng] = findtrigs(Xg,fsg);
            start_synctimes(i,1) = Ng(1);
            end_synctimes(i,1) = Ng(end);
            gaze_ts(i) = gaze_data{i}.syncpulse_ts(1);
        elseif (strcmp(gazesync_method, 'audio'))
            [T,L] = audiomatch(gaze_syncfiles{i}, gaze_masteraudio{i}, nsec);
            start_synctimes(i,1) = T(1);
            end_synctimes(i,1) = T(1)+L(end);
            gaze_ts(i) = gaze_data{i}.video_ts(1);
        elseif (strcmp(gazesync_method, 'clap'))
            [T,L] = audiomatch(gaze_masteraudio{i}, gaze_syncfiles{i}, nsec);
            [Xg,fsg] = audioread(gaze_masteraudio{i});
            [pks, inds] = findpeaks(Xg);
%             figure; plot(Xg)
            thres = 0.8;
            peaks = inds(pks>thres)/fsg;
            gaze_starttimes(i,1) = peaks(1)-T(1);
            start_synctimes(i,1) = peaks(1);
            end_synctimes(i,1) = T(1)+L(end);
            gaze_ts(i) = gaze_data{i}.video_ts(1);
        else
            error('erroneous sync method');
        end
    end

    % read mocap sync
    if (strcmp(mocapsync_method, 'pulse'))
        [Xm,fsm] = audioread(mocap_syncfile);
        [Nm] = findtrigs(Xm,fsm);
        start_synctimes(end,1) = Nm(1);
        end_synctimes(end,1) = Nm(end);
        mocap_start = Nm(1);
    elseif (strcmp(mocapsync_method, 'clap'))
        % the data should be trimmed on export
        mocap_start = max(start_synctimes);
        mocap_data.timestamps = mocap_data.timestamps-mocap_data.timestamps(1);
        end_synctimes(end,1) = mocap_start+mocap_data.timestamps(end);
    else
        error('erroneous sync method');
    end
    
    % Define min and max start times
    maxGazeStartTime = max(start_synctimes);
    maxStartTime = maxGazeStartTime;
    minEndTime = min(end_synctimes);
    length = (minEndTime-maxStartTime);

    % initialize resampled times
    deltatime = 1/resampleFrameRate;
    timesteps = 0:deltatime:length;

    for i=1:nEyetrackers
        %intelpolate the gaze data at discrecized time (plus offset)
        offset = maxStartTime-start_synctimes(i)+gaze_starttimes(i);
        gd = gaze_data{i};
        
        %fix because timestamps are not strictly monotoneous
        [tt, ii] = sort((gd.timestamps.left-gaze_ts(i))*1E-6);
        dd = gd.gazedata.left(ii,:);        
        gaze{i}.left = interp1(tt, dd, offset+timesteps);
        
        [tt, ii] = sort((gd.timestamps.right-gaze_ts(i))*1E-6);
        dd = gd.gazedata.right(ii,:);
        gaze{i}.right = interp1(tt, dd, offset+timesteps);

        [tt, ii] = sort((gd.timestamps.gp3-gaze_ts(i))*1E-6);
        dd = gd.gazedata.gp3(ii,:);
        bin = diff(tt)~=0;
        tt = tt(bin);
        dd = dd(bin,:);        
        gaze{i}.gp3 = interp1(tt, dd, offset+timesteps);
        
    end
    
    %intelpolate the mocap data at discrecized time (plus offset)
    offset = maxStartTime-mocap_start;
    tmp = interp1(mocap_data.timestamps, mocap_data.data, offset+timesteps);
    mocap = tmp;
    