function [appstart, clap_start, clap_end] = get_starttimes(app_syncfile, audiofile, base)

    % Find the app start time from the audio reference channel
    [Xg,fsg] = audioread(app_syncfile);
    [Ng] = findtrigs(Xg,fsg);
    appstart = Ng(1);
    
    % Write audio file to check it is correct
    audiowrite(sprintf('%s/timing/app.wav', base), Xg(ceil((appstart - 1) * fsg):ceil((appstart + 1) * fsg)), fsg);    
    
    % Get first and last claps
    [Xg,fsg] = audioread(audiofile{1});
    Xg = Xg/max(Xg);
    [pks, inds] = findpeaks(Xg);
    thres = 0.8;
    peaks = inds(pks>thres)/fsg;
    %figure
    %plot(Xg)
    clap_start = peaks(1);
    clap_end = peaks(end);

    % Write audio files to check they are correct
    audiowrite(sprintf('%s/timing/clap1.wav', base), Xg(ceil((clap_start - 1) * fsg):ceil((clap_start + 1) * fsg)), fsg);
    audiowrite(sprintf('%s/timing/clap2.wav', base), Xg(ceil((clap_end - 1) * fsg):ceil((clap_end + 1) * fsg)), fsg);
    