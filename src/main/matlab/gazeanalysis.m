% Parses gaze hit processed csv file and filters fixations
gazefile = sprintf('data/test3_gazehits.csv');

outfile = sprintf('results/test3_gazeanalysis.csv');

% Get gaze data
fid1 = fopen(gazefile);
gazeDATA = textscan(fid1, '%s', 'delimiter', '\n');
gazedata = gazeDATA{1};

% Get gaze columns
gazen = textscan(gazedata{1}, '%s', 'delimiter', ',');
gazecol = gazen{1};
gazenColumns = floor(size(gazecol,1));

% Init field table
gazefield{1,1} = {'Frame'};
gazefield{1,2} = {'Time'};
gazefield{1,3} = {'M Gaze'};
gazefield{1,4} = {'P1 Gaze'};
gazefield{1,5} = {'P2 Gaze'};
gazefield{1,6} = {'M ASR'};
gazefield{1,7} = {'P1 ASR'};
gazefield{1,8} = {'P2 ASR'};

% Make first 6 lines NULL
for i = 2:6
    for j = 1:8
        gazefield{i,j} = {''};
    end
end

% Initiate gaze and fixations
placefixm = {''};
placefixp1 = {''};
placefixp2 = {''};

% Check if a fixation lasts at least 100ms (5 frames) and filter
for i = 7:(size(gazedata, 1) - 7)
    % Take gaze line
    gazelines(i) = textscan(gazedata{i}, '%s', 'delimiter', ',');
    d = gazelines{i};
    % Fix error where a few times last column is missing and put a zero
    if size(d,1) < 8
        d(8) = {''};
    end

    % Start counting after the first 5 frames
    fixationcounterm = 0;
    fixationcounterp1 = 0;
    fixationcounterp2 = 0;
    
    % Start after at least 5 frames have passed
    if i > 10
        for f = 1:4
            % Take previous gaze line
            previousd = gazelines{i-f};

            % Fix error where a few times last column is missing and put a zero
            if size(previousd,1) < 8
                previousd(8) = {''};
            end

            % Check within a fixation duration for gaze
            % Moderator gaze
            if strcmp(d(3),'') || strcmp(d(3),'P1') || strcmp(d(3),'P2') || strcmp(d(3),'O1') || strcmp(d(3),'O2') || strcmp(d(3),'O3') || strcmp(d(3),'O4') || strcmp(d(3),'O5') || strcmp(d(3),'O6') || strcmp(d(3),'O7') || strcmp(d(3),'O8')
                if strcmp(d(3),previousd(3))
                    fixationcounterm = fixationcounterm + 1;
                end
            end
            
            % P1 gaze
            if strcmp(d(4),'') || strcmp(d(4),'M') || strcmp(d(4),'P2') || strcmp(d(4),'O1') || strcmp(d(4),'O2') || strcmp(d(4),'O3') || strcmp(d(4),'O4') || strcmp(d(4),'O5') || strcmp(d(4),'O6') || strcmp(d(4),'O7') || strcmp(d(4),'O8')
                if strcmp(d(4),previousd(4))
                    fixationcounterp1 = fixationcounterp1 + 1;
                end
            end
            
            % P2 gaze
            if strcmp(d(5),'') || strcmp(d(5),'M') || strcmp(d(5),'P1') || strcmp(d(5),'O1') || strcmp(d(5),'O2') || strcmp(d(5),'O3') || strcmp(d(5),'O4') || strcmp(d(5),'O5') || strcmp(d(5),'O6') || strcmp(d(5),'O7') || strcmp(d(5),'O8')
                if strcmp(d(5),previousd(5))
                    fixationcounterp2 = fixationcounterp2 + 1;
                end
            end
        end

        % Check that the duration is at least 0.1s
        % Moderator gaze
        if fixationcounterm == 4
            placefixm = d(3);
        end
        
        % P1 gaze
        if fixationcounterp1 == 4
            placefixp1 = d(4);
        end
        
        % P2 gaze
        if fixationcounterp2 == 4
            placefixp2 = d(5);
        end
    end

    % Write to gazefield (only one frame every 5)
    fieldcounter = (i - 1) / 5;
    if floor(fieldcounter) == fieldcounter
        % First make all fields NULL
        for z = 1:8
            gazefield{fieldcounter,z} = {''};
        end
        
        % Put frame and time
        gazefield{fieldcounter,1} = int2str(fieldcounter - 1);
        gazefield{fieldcounter,2} = d(2);
    
%         % Put ASR
%         gazefield{fieldcounter,9} = d(9);
%         gazefield{fieldcounter,10} = d(10);
%         gazefield{fieldcounter,11} = d(11);
        
        % Put gaze fixations
        % Moderator gaze
        gazefield{fieldcounter,3} = placefixm;
        placefixm = {''};
        
        % P1 gaze
        gazefield{fieldcounter,4} = placefixp1;
        placefixp1 = {''};
        
        % P2 gaze
        gazefield{fieldcounter,5} = placefixp2;
        placefixp2 = {''};
    end

    % Display progress
    counter = i / 50;
    if floor(counter) == counter
        disp(counter)
    end
end

fclose(fid1);

% Write to csv
fid3 = fopen(outfile, 'wt');
for k = 1:size(gazefield, 1)
    for l = 1:8
        put = char(gazefield{k,l});
        fprintf(fid3, '%s,', put);
    end
    fprintf(fid3, '\n');
end
fclose(fid3);
