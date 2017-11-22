% ************************************************************************* %
% ToolboxDemo.m
%
% Author: Tim Holmes
% Institution: Royal Holloway, University of London % Date: July 2nd, 2010
% Version: 1.0
%
% Demonstration script containing examples of all calls to the Tobii
% Toolbox v1.1 - please note, this same script WILL work with v1.0, with
% the GetTetTime call (see in line comments). %
% Before running this script it is essential that the installation
% instructions in the Tobii Toolbox User Documentation v1.1 have been
% completed. In particular, the Tobii Toolbox must be unzipped to a
% directory and that path included in the Matlab paths and the Tobii SDK
% v2.4.12 or higher must be installed on the same machine as Matlab. %
% This script is structured as follows: %
% 1. Initialisation and connection to the Tobii Eye-tracker % 2. Calibration of a participant
% 3. Display of a stimulus
% 4. Initiate eye-tracking
% 5. Get raw eye-movement data from Tobii Eye-tracker
% 6. Produce crude fixation plot
%
% *************************************************************************

warning off all;

% ************************************************************************* %
% 1. Initialisation and connection to the Tobii Eye-tracker %
% *************************************************************************

fixationduration = 6; %100/(1000/120) i.e. 100ms window/duration of a single row on the 120Hz file, use 6 for 60Hz (binocular)
fixationhrange = 0.029; %+/- 0.5 degree as a percentage of the screen size (standard T120 monitor with 57cm viewing distance)
fixationvrange = 0.037; %+/- 0.5 degree as a percentage of the screen size (standard T120 monitor with 57cm viewing distance)
fixation(1,1:6) =0;

%get path info
path = input('enter path for input/output files (easiest to use Tobii Toolbox path for demo): ','s');

%Call to Tobii Toolbox to connect to eye-tracker
tobiiserver = input('Tobii server name? e.g. TT120-205-92200620.local: ','s'); ConnectTo(tobiiserver);

% ************************************************************************* %
% 2. Calibration of a participant
%
% *************************************************************************

calibrationpoints = input('How many calibration points? (2,5 or 9): ','s');
TrackStatus; %Call to Tobii Toolbox to display the SDK GUI to confirm detection of both eyes
trackstatus = input('Ready to calibrate?: ','s');
while trackstatus == 'N' || trackstatus == 'N'
trackstatus = input('Ready to calibrate?: ','s'); end;
EndTrackStatus; %Call to Tobii Toolbox to clear the GUI Calibrate(str2double(calibrationpoints)); %Call to Tobii Toolbox to perform calibration
calibrated = input('Recalibration needed (Y/N)?: ','s');
while calibrated == 'Y' || calibrated == 'y'
ReCalibration; %Call to Tobii Toolbox to perform recalibration of unsuccesful points
calibrated = input('Recalibration needed?: ','s'); end;
ClearPlot; %Call to Tobii Toolbox to remove the calibration results plot from the screen

% ************************************************************************* %
% 3. Display of a stimulus
%
% For the demo this simply reads and display a bitmap of the Tobii logo.
% Any method for generation and display of stimuli availble to Matlab could
% be inserted here, for example using Psychtoolbox or Cogent %
% *************************************************************************

A=imread(strcat(path,'\TobiiLogo.bmp')); imagesc(A);
axis off;
axis image;
set(1,'MenuBar','none');
a=get(1,'Position');
set(1,'Position',[40 40 40+(2*a(3)) 40+(2*a(4))]);

% ************************************************************************* %
% 4. Initiate eye-tracking
%
% *************************************************************************

starttime = GetTetTime; %Call to Tobii Toolbox to capture the TTime (timestamp from the Tobii Eye-tracker)

%Start the eyetracking
trackfile = strcat(path,'\tobiidata.csv');
TrackStart(0,trackfile); %Call to Tobii Toolbox to commence tracking without displaying the fixation location on screen and return raw data in trackfile
pause(5); %Track gaze for 5 seconds
TrackStop; %Call to Tobii Toolbox to end tracking

% ************************************************************************* %
% 5. Get raw eye-movement data from Tobii Eye-tracker %
% *************************************************************************

DATA = csvread(trackfile);

% ************************************************************************* %
% 6. Produce crude fixation plot
%
% Now you have the raw data from the eye-tracker in Matlab matrix DATA, you
% can proceed with any kind of analysis you wish. The following code is a
% fairly unsophisticated fixation point analysis and plot and is included
% merely for illustration of how you might proceed. Details of the
% structure and format of entries in DATA are given in Appendix A of the % Tobii SDK Developer's Guide.
%
% *************************************************************************

trackstarttime = DATA(1,8)+(DATA(1,9)/1000000);

%calculate the average x and y gaze coordinates from the left and right eye %positions from Tobii
DATA(:,17)=0;
DATA(:,18)=0.5*(DATA(:,3)+DATA(:,10)); DATA(:,19)=0.5*(DATA(:,4)+DATA(:,11));

%set the fixation indicator as follows:
%if the gaze position (x,y) over a rolling 100ms window does not change by more than fixationhrange and fixationvrange then considered to be part of a single fixation
for efi = fixationduration:size(DATA,1)
if sum([sum(DATA(1+efi-fixationduration:efi,9)),sum((DATA(1+efi- fixationduration:efi,16)))]) == 0 %if all rows of tracked data have Tobii validity indicator of 0
if max(DATA(1+efi-fixationduration:efi,18)) - min(DATA(1+efi- fixationduration:efi,18))<= fixationhrange %if gaze x remains within spatial range
if max(DATA(1+efi-fixationduration:efi,19)) - min(DATA(1+efi- fixationduration:efi,19))<= fixationvrange %if gaze y remains within spatial range
DATA(1+efi-fixationduration:efi,17) = 1; end;
end;
end;
end;

%count the fixations, their average centre coordinates and duration
fixationcount = 0;
fixok = 0;
for efi = fixationduration:size(DATA,1)
    if DATA(efi,17) == 1
        if DATA(efi-1,17) == 0;
if fixationcount > 0; %first time thru?
    FIX(fixationcount,1) = fixatedx/timepoints;
    FIX(fixationcount,2) = fixatedy/timepoints;
    FIX(fixationcount,3) = fixationlength;
    fixok = 1;
            end;
            fixatedx = 0;
            fixatedy = 0;
            fixationlength = 0;
            timepoints = 0;
            fixationcount = fixationcount + 1;
end;
fixatedx = fixatedx + DATA(efi,18); fixatedy = fixatedy + DATA(efi,19); fixationlength = fixationlength + 1000/60; timepoints = timepoints + 1;
end; end;
if DATA(efi-1,17) == 1; %ends on a fixation?
    FIX(fixationcount,1) = fixatedx/timepoints;
    FIX(fixationcount,2) = fixatedy/timepoints;
    FIX(fixationcount,3) = fixationlength;
    fixok = 1;
end;
%produce simple scatter plot of the fixation centres with circles sized to %match the fixation duration at that point
if fixok == 0
    disp('NO FIXATIONS DETECTED');
else
FIX(:,1) = 1-FIX(:,1); %flips x-coordinates to match plot axis
FIX(:,2) = 1-FIX(:,2); %flips y-coordinates to match plot axis
scatter (FIX(:,1),FIX(:,2),FIX(:,3));
axis([0 1 0 1]);
end;

%write out the analysed file
csvwrite(strcat(path,'\fixations.csv'),DATA);
% ************************************************************************* %
% END
%
% *************************************************************************
