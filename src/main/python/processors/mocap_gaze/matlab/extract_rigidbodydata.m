function rgbdata = extract_rigidbodydata(DATA, Labels, rgbName)

    tmp = DATA(:,strcmp(Labels,rgbName));

    % rigid body position
    rgbdata.pos = tmp(:,5:7);

    % rigid body orientation
    rgbdata.quat = tmp(:,[4 1 2 3]);

    % rigid body markers
    rgbmarkers_bin = strncmp(Labels,sprintf('%s_', rgbName),length(rgbName)+1);
    rgbMarkerNames = unique(Labels(rgbmarkers_bin))';
    nRgbMarkers = size(rgbMarkerNames,2);    
    rgbdata.rgbMarkers = nan(size(DATA,1), 3, nRgbMarkers);
    rgbdata.rgbMarkernames = rgbMarkerNames;
    rgbdata.name = rgbName;
    for j=1:nRgbMarkers
        tmp = DATA(:,strcmp(Labels,rgbMarkerNames{j}));
        rgbdata.rgbMarkers(:,:,j)= tmp(:,1:3);
    end
        