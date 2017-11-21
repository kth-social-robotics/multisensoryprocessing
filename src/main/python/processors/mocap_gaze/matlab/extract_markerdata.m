function P = extract_markerdata(CSVDATA, labels, types, markerNames)
    % extract marker data from cvs data structure

    nMarkers = length(markerNames);
    P = nan(size(CSVDATA,1), 3, nMarkers);
    for j=1:nMarkers
        markers_bin = strcmp(types,'Marker');
        lbls_bin = strcmp(labels,markerNames{j});
        if sum(lbls_bin) == 0
            disp(sprintf('could not find marker: %s', markerNames{j}));
        end
        tmp = CSVDATA(:,markers_bin & lbls_bin);
        P(:,:,j)= tmp;
    end
